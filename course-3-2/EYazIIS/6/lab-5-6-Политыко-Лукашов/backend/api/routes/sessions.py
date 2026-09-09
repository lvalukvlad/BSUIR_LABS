import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.models import (
    DialogMessage,
    DialogSession,
    get_session,
    new_session_id,
    session_to_dict,
)

router = APIRouter(prefix="/sessions", tags=["Сессии"])


def db():
    s = get_session()
    try:
        yield s
    finally:
        s.close()


class SessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=500)


class SessionPatch(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)


@router.get("")
def list_sessions(session: Session = Depends(db)):
    rows = session.scalars(
        select(DialogSession).order_by(DialogSession.updated_at.desc())
    ).all()
    out = []
    for r in rows:
        cnt = session.scalar(
            select(func.count()).select_from(DialogMessage).where(
                DialogMessage.session_id == r.id
            )
        )
        out.append(session_to_dict(r, int(cnt or 0)))
    return {"sessions": out}


@router.post("")
def create_session(body: SessionCreate, session: Session = Depends(db)):
    sid = new_session_id()
    title = (body.title or "").strip() or "Новый диалог"
    row = DialogSession(id=sid, title=title, context_json="{}")
    session.add(row)
    session.commit()
    session.refresh(row)
    return session_to_dict(row, 0)


@router.patch("/{session_id}")
def patch_session(
    session_id: str,
    body: SessionPatch,
    session: Session = Depends(db),
):
    row = session.get(DialogSession, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    row.title = body.title.strip()
    row.updated_at = datetime.utcnow()
    session.commit()
    cnt = session.scalar(
        select(func.count()).select_from(DialogMessage).where(
            DialogMessage.session_id == session_id
        )
    )
    return session_to_dict(row, int(cnt or 0))


@router.delete("/{session_id}")
def delete_session(session_id: str, session: Session = Depends(db)):
    row = session.get(DialogSession, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    session.delete(row)
    session.commit()
    remaining = session.scalar(select(func.count()).select_from(DialogSession))
    if int(remaining or 0) == 0:
        sid = new_session_id()
        session.add(
            DialogSession(
                id=sid,
                title="Новый диалог",
                context_json="{}",
            )
        )
        session.commit()
    return {"ok": True}


@router.post("/{session_id}/clear-context")
def clear_context(session_id: str, session: Session = Depends(db)):
    row = session.get(DialogSession, session_id)
    if not row:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    row.context_json = "{}"
    row.updated_at = datetime.utcnow()
    session.commit()
    return {"ok": True}
