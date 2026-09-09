import json
import uuid
from datetime import datetime
from pathlib import Path

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, create_engine, event, func, inspect, select, text
from sqlalchemy.orm import Session, declarative_base, relationship, sessionmaker
from sqlalchemy.engine import Engine

Base = declarative_base()


@event.listens_for(Engine, "connect")
def _sqlite_pragma(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


class DialogSession(Base):
    __tablename__ = "dialog_sessions"

    id = Column(String(36), primary_key=True)
    title = Column(String(500), nullable=False, default="Диалог")
    context_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship(
        "DialogMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="DialogMessage.id",
    )


class DialogMessage(Base):
    __tablename__ = "dialog_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        String(36),
        ForeignKey("dialog_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    role = Column(String(16), nullable=False)
    content = Column(Text, nullable=False)
    intent = Column(String(64), default="")
    processing_time_ms = Column(Integer, default=0)
    sources_json = Column(Text, nullable=True)
    versions_json = Column(Text, nullable=True)
    edit_version = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("DialogSession", back_populates="messages")


_engine = None
_SessionLocal = None


def get_db_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "dialog.db"


def init_db():
    global _engine, _SessionLocal
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    _engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(_engine)
    _migrate_sqlite_schema(_engine)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    _seed_initial_session()


def _migrate_sqlite_schema(engine):
    insp = inspect(engine)
    if not insp.has_table("dialog_messages"):
        return
    cols = {c["name"] for c in insp.get_columns("dialog_messages")}
    if "sources_json" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE dialog_messages ADD COLUMN sources_json TEXT"))
    if "versions_json" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE dialog_messages ADD COLUMN versions_json TEXT"))
    if "edit_version" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE dialog_messages ADD COLUMN edit_version INTEGER DEFAULT 0"))


def _seed_initial_session():
    s = _SessionLocal()
    try:
        has_any = s.scalar(select(func.count()).select_from(DialogSession))
        if int(has_any or 0) == 0:
            s.add(
                DialogSession(
                    id=new_session_id(),
                    title="Диалог",
                    context_json="{}",
                )
            )
            s.commit()
    finally:
        s.close()


def get_engine():
    if _engine is None:
        init_db()
    return _engine


def get_session() -> Session:
    if _SessionLocal is None:
        init_db()
    return _SessionLocal()


def message_to_dict(m: DialogMessage) -> dict:
    out = {
        "id": m.id,
        "session_id": m.session_id,
        "role": m.role,
        "content": m.content,
        "intent": m.intent or "",
        "processing_time_ms": m.processing_time_ms or 0,
        "edit_version": m.edit_version or 0,
        "created_at": m.created_at.isoformat() if m.created_at else "",
        "updated_at": m.updated_at.isoformat() if m.updated_at else "",
    }
    if m.sources_json:
        try:
            out["sources"] = json.loads(m.sources_json)
        except json.JSONDecodeError:
            pass
    if m.versions_json:
        try:
            out["versions"] = json.loads(m.versions_json)
        except json.JSONDecodeError:
            pass
    return out


def session_to_dict(sess: DialogSession, message_count: int = 0) -> dict:
    ctx = {}
    try:
        ctx = json.loads(sess.context_json or "{}")
    except json.JSONDecodeError:
        ctx = {}
    return {
        "id": sess.id,
        "title": sess.title,
        "context": ctx,
        "message_count": message_count,
        "created_at": sess.created_at.isoformat() if sess.created_at else "",
        "updated_at": sess.updated_at.isoformat() if sess.updated_at else "",
    }


def new_session_id() -> str:
    return str(uuid.uuid4())
