import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from core.dialog.engine import generate_reply
from core.models import (
    DialogMessage,
    DialogSession,
    get_session,
    message_to_dict,
    new_session_id,
)

router = APIRouter(prefix="/dialog", tags=["Диалог"])

RESET_SESSION_CONTEXT_INTENTS = frozenset(
    {"greeting", "goodbye", "help", "emergency"}
)


def db():
    s = get_session()
    try:
        yield s
    finally:
        s.close()


class MessageIn(BaseModel):
    text: str = Field(..., min_length=0, max_length=8000)
    session_id: str | None = Field(default=None, max_length=36)

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str | None):
        if v is None:
            return v
        try:
            uuid.UUID(v)
        except ValueError as e:
            raise ValueError("session_id должен быть строкой UUID") from e
        return v


class MessagePatch(BaseModel):
    content: str = Field(..., min_length=1, max_length=8000)


def _merge_context(sess_row: DialogSession, patch: dict) -> None:
    cur = {}
    try:
        cur = json.loads(sess_row.context_json or "{}")
    except json.JSONDecodeError:
        cur = {}
    cur.update(patch)
    sess_row.context_json = json.dumps(cur, ensure_ascii=False)
    sess_row.updated_at = datetime.utcnow()


def _apply_context_update(context: dict, intent: str, patch: dict) -> dict:
    if intent in RESET_SESSION_CONTEXT_INTENTS:
        return {}
    out = dict(context)
    out.update(patch or {})
    return out


def _resolve_session_id(session: Session, provided: str | None) -> str:
    if provided:
        return provided
    newest = session.scalar(
        select(DialogSession.id).order_by(DialogSession.updated_at.desc()).limit(1)
    )
    if newest:
        return newest
    sid = new_session_id()
    session.add(DialogSession(id=sid, title="Новый диалог", context_json="{}"))
    session.commit()
    return sid


def _derive_context_before(
    session: Session,
    session_id: str,
    before_message_id: int,
) -> dict:
    ctx: dict = {}
    rows = session.scalars(
        select(DialogMessage)
        .where(
            DialogMessage.session_id == session_id,
            DialogMessage.id < before_message_id,
            DialogMessage.role == "user",
        )
        .order_by(DialogMessage.id.asc())
    ).all()
    for m in rows:
        r = generate_reply(m.content, ctx, allow_llm=False)
        ctx = _apply_context_update(ctx, r.intent, r.updated_context)
    return ctx


def _regenerate_assistant_for_user(
    session: Session,
    user_msg: DialogMessage,
    previous_user_content: str | None = None,
) -> None:
    ctx = _derive_context_before(session, user_msg.session_id, user_msg.id)
    result = generate_reply(user_msg.content, ctx)
    next_assistant = session.scalar(
        select(DialogMessage)
        .where(
            DialogMessage.session_id == user_msg.session_id,
            DialogMessage.id > user_msg.id,
            DialogMessage.role == "assistant",
        )
        .order_by(DialogMessage.id.asc())
        .limit(1)
    )
    if next_assistant is None:
        raise HTTPException(status_code=400, detail="Не найден связанный ответ ассистента")

    history = []
    if user_msg.versions_json:
        try:
            history = json.loads(user_msg.versions_json)
        except json.JSONDecodeError:
            history = []
    history.append(
        {
            "user": previous_user_content if previous_user_content is not None else user_msg.content,
            "assistant": next_assistant.content,
            "intent": next_assistant.intent,
            "processing_time_ms": next_assistant.processing_time_ms,
            "edited_at": datetime.utcnow().isoformat() + "Z",
        }
    )
    user_msg.versions_json = json.dumps(history, ensure_ascii=False)
    user_msg.edit_version = len(history)
    src_dump = json.dumps(result.sources, ensure_ascii=False) if result.sources else None
    next_assistant.content = result.reply
    next_assistant.intent = result.intent
    next_assistant.processing_time_ms = result.processing_time_ms
    next_assistant.sources_json = src_dump
    next_assistant.edit_version = user_msg.edit_version

    session.execute(
        delete(DialogMessage).where(
            DialogMessage.session_id == user_msg.session_id,
            DialogMessage.id > next_assistant.id,
        )
    )
    sess_row = session.get(DialogSession, user_msg.session_id)
    if sess_row:
        new_ctx = _apply_context_update(ctx, result.intent, result.updated_context)
        sess_row.context_json = json.dumps(new_ctx, ensure_ascii=False)
        sess_row.updated_at = datetime.utcnow()


@router.post("/reply")
def post_reply(body: MessageIn, session: Session = Depends(db)):
    user_text = body.text.strip()
    sid = _resolve_session_id(session, body.session_id)
    sess_row = session.get(DialogSession, sid)
    if not sess_row:
        raise HTTPException(status_code=404, detail="Сессия не найдена")

    user_messages_before = int(
        session.scalar(
            select(func.count())
            .select_from(DialogMessage)
            .where(DialogMessage.session_id == sid, DialogMessage.role == "user")
        )
        or 0
    )

    ctx = {}
    try:
        ctx = json.loads(sess_row.context_json or "{}")
    except json.JSONDecodeError:
        ctx = {}

    result = generate_reply(user_text, ctx)
    if result.intent in RESET_SESSION_CONTEXT_INTENTS:
        sess_row.context_json = "{}"
        sess_row.updated_at = datetime.utcnow()
    elif result.updated_context:
        _merge_context(sess_row, result.updated_context)

    um = DialogMessage(
        session_id=sid,
        role="user",
        content=user_text,
        intent="",
        processing_time_ms=0,
    )
    src_dump = (
        json.dumps(result.sources, ensure_ascii=False) if result.sources else None
    )
    am = DialogMessage(
        session_id=sid,
        role="assistant",
        content=result.reply,
        intent=result.intent,
        processing_time_ms=result.processing_time_ms,
        sources_json=src_dump,
    )
    session.add(um)
    session.add(am)
    if user_messages_before == 0 and sess_row.title.strip().lower() in {"диалог", "новый диалог"}:
        title = user_text[:56].strip()
        if len(user_text) > 56:
            title += "…"
        if title:
            sess_row.title = title
            sess_row.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(um)
    session.refresh(am)

    return {
        "user_message": message_to_dict(um),
        "assistant_message": message_to_dict(am),
        "intent": result.intent,
        "processing_time_ms": result.processing_time_ms,
        "sources": result.sources,
        "session_context": json.loads(sess_row.context_json or "{}"),
    }


@router.get("/history")
def get_history(
    session_id: str | None = Query(default=None),
    db_sess: Session = Depends(db),
):
    sid = _resolve_session_id(db_sess, session_id)
    rows = db_sess.scalars(
        select(DialogMessage)
        .where(DialogMessage.session_id == sid)
        .order_by(DialogMessage.id.asc())
    ).all()
    return {"messages": [message_to_dict(m) for m in rows], "session_id": sid}


@router.put("/messages/{msg_id}")
def patch_message(
    msg_id: int,
    body: MessagePatch,
    session: Session = Depends(db),
):
    m = session.get(DialogMessage, msg_id)
    if not m:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    if m.role != "user":
        raise HTTPException(
            status_code=403,
            detail="Можно редактировать только сообщения пользователя",
        )
    prev_content = m.content
    cleaned = body.content.strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="Текст сообщения не может быть пустым")
    m.content = cleaned
    _regenerate_assistant_for_user(session, m, previous_user_content=prev_content)
    session.commit()
    session.refresh(m)
    return message_to_dict(m)


@router.delete("/messages/{msg_id}")
def delete_message(msg_id: int, session: Session = Depends(db)):
    m = session.get(DialogMessage, msg_id)
    if not m:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    if m.role != "user":
        raise HTTPException(
            status_code=403,
            detail="Можно удалять только сообщения пользователя",
        )
    next_msg = session.scalar(
        select(DialogMessage)
        .where(
            DialogMessage.session_id == m.session_id,
            DialogMessage.id > m.id,
        )
        .order_by(DialogMessage.id.asc())
        .limit(1)
    )
    session.delete(m)
    if next_msg and next_msg.role == "assistant":
        session.delete(next_msg)
    sess_row = session.get(DialogSession, m.session_id)
    if sess_row:
        rows = session.scalars(
            select(DialogMessage)
            .where(
                DialogMessage.session_id == m.session_id,
                DialogMessage.role == "user",
            )
            .order_by(DialogMessage.id.asc())
        ).all()
        ctx: dict = {}
        for row in rows:
            result = generate_reply(row.content, ctx, allow_llm=False)
            ctx = _apply_context_update(ctx, result.intent, result.updated_context)
        sess_row.context_json = json.dumps(ctx, ensure_ascii=False)
        sess_row.updated_at = datetime.utcnow()
    session.commit()
    return {"ok": True, "id": msg_id}


@router.delete("/history")
def clear_history(session_id: str | None = Query(default=None), session: Session = Depends(db)):
    sid = _resolve_session_id(session, session_id)
    session.execute(delete(DialogMessage).where(DialogMessage.session_id == sid))
    sess_row = session.get(DialogSession, sid)
    if sess_row:
        sess_row.context_json = "{}"
        sess_row.updated_at = datetime.utcnow()
    session.commit()
    return {"ok": True, "session_id": sid}


@router.get("/export")
def export_dialog(session_id: str | None = Query(default=None), session: Session = Depends(db)):
    sid = _resolve_session_id(session, session_id)
    sess_row = session.get(DialogSession, sid)
    if not sess_row:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    rows = session.scalars(
        select(DialogMessage)
        .where(DialogMessage.session_id == sid)
        .order_by(DialogMessage.id.asc())
    ).all()
    ctx = {}
    try:
        ctx = json.loads(sess_row.context_json or "{}")
    except json.JSONDecodeError:
        pass
    return {
        "session_id": sid,
        "title": sess_row.title,
        "context": ctx,
        "messages": [message_to_dict(m) for m in rows],
        "exported_at": datetime.utcnow().isoformat() + "Z",
    }
