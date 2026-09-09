from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
from pathlib import Path

Base = declarative_base()


class Document(Base):
    __tablename__ = 'documents'

    id = Column(String(36), primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(500), default='')
    author = Column(String(255), default='')
    date = Column(String(50), default='')
    genre = Column(String(255), default='')
    text_type = Column(String(255), default='')
    created_at = Column(DateTime, default=datetime.now)
    word_count = Column(Integer, default=0)
    char_count = Column(Integer, default=0)

    tokens = relationship('Token', back_populates='document', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'metadata': {
                'source': self.source,
                'author': self.author,
                'date': self.date,
                'genre': self.genre,
                'text_type': self.text_type,
                'word_count': self.word_count,
                'char_count': self.char_count,
                'created_at': self.created_at.isoformat() if self.created_at else ''
            }
        }


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    token = Column(String(500), nullable=False)
    position = Column(Integer, nullable=False)
    lemma = Column(String(500), nullable=False)
    pos = Column(String(50), nullable=False)
    case = Column(String(50), default='')
    number = Column(String(50), default='')
    gender = Column(String(50), default='')

    document = relationship('Document', back_populates='tokens')

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'token': self.token,
            'position': self.position,
            'analysis': {
                'lemma': self.lemma,
                'pos': self.pos,
                'grammemes': {
                    'падеж': self.case if self.case else '',
                    'число': self.number if self.number else '',
                    'род': self.gender if self.gender else ''
                }
            }
        }


DATABASE_PATH = Path(__file__).parent.parent / 'data' / 'corpus.db'
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f'sqlite:///{DATABASE_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
