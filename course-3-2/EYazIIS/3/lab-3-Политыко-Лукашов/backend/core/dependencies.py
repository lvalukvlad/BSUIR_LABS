from pathlib import Path
from sqlalchemy.orm import Session
from core.models import init_db, get_db, Document, Sentence, Token, SyntaxRelation, engine
from core.corpus.manager import SyntaxManager


_syntax_manager: SyntaxManager | None = None


def get_syntax_manager() -> SyntaxManager:
    global _syntax_manager
    if _syntax_manager is None:
        data_dir = Path(__file__).parent.parent / 'data'
        _syntax_manager = SyntaxManager(data_dir)
    return _syntax_manager


def get_database() -> Session:
    return next(get_db())
