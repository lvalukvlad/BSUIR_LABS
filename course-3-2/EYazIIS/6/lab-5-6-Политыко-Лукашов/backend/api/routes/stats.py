from fastapi import APIRouter
from sqlalchemy import func, select

from core.corpus.index import index_status
from core.models import DialogMessage, DialogSession, get_db_path, get_session

router = APIRouter(prefix="/stats", tags=["Статистика"])


@router.get("")
def statistics():
    session = get_session()
    try:
        msg_n = session.scalar(select(func.count()).select_from(DialogMessage)) or 0
        sess_n = session.scalar(select(func.count()).select_from(DialogSession)) or 0
    finally:
        session.close()
    idx = index_status()
    return {
        "messages_total": int(msg_n),
        "sessions_total": int(sess_n),
        "corpus_chunks": idx["chunk_count"],
        "corpus_indexed": idx["indexed"],
        "database_path": str(get_db_path()),
    }
