from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, create_engine, UniqueConstraint, event
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Engine
from datetime import datetime
from pathlib import Path

Base = declarative_base()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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
    analysis_time_ms = Column(Integer, default=0)

    sentences = relationship('Sentence', back_populates='document', cascade='all, delete-orphan')

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
                'created_at': self.created_at.isoformat() if self.created_at else '',
                'analysis_time_ms': self.analysis_time_ms
            }
        }


class Sentence(Base):
    __tablename__ = 'sentences'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    sentence_index = Column(Integer, nullable=False)
    sentence_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    document = relationship('Document', back_populates='sentences')
    tokens = relationship(
        'Token',
        back_populates='sentence',
        cascade='all, delete-orphan',
        order_by='Token.token_index',
    )
    relations = relationship('SyntaxRelation', back_populates='sentence', cascade='all, delete-orphan')

    __table_args__ = (
        UniqueConstraint('document_id', 'sentence_index', name='uq_sentence_index'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'sentence_index': self.sentence_index,
            'sentence_text': self.sentence_text,
            'created_at': self.created_at.isoformat() if self.created_at else '',
            'tokens': [t.to_dict() for t in self.tokens],
            'relations': [r.to_dict() for r in self.relations]
        }


class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String(36), ForeignKey('documents.id', ondelete='CASCADE'), nullable=False)
    sentence_id = Column(Integer, ForeignKey('sentences.id', ondelete='CASCADE'), nullable=False)
    token_index = Column(Integer, nullable=False)
    token_text = Column(String(500), nullable=False)
    lemma = Column(String(500), default='')
    pos = Column(String(50), default='')
    pos_name = Column(String(100), default='')
    case = Column(String(50), default='')
    case_name = Column(String(100), default='')
    number = Column(String(50), default='')
    number_name = Column(String(100), default='')
    gender = Column(String(50), default='')
    gender_name = Column(String(100), default='')
    tense = Column(String(50), default='')
    person = Column(String(50), default='')
    animacy = Column(String(50), default='')
    syntax_role = Column(String(100), default='')
    syntax_role_name = Column(String(100), default='')
    position = Column(Integer, default=0)

    sentence = relationship('Sentence', back_populates='tokens')

    __table_args__ = (
        UniqueConstraint('sentence_id', 'token_index', name='uq_token_index'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'sentence_id': self.sentence_id,
            'token_index': self.token_index,
            'token_text': self.token_text,
            'lemma': self.lemma,
            'pos': self.pos,
            'pos_name': self.pos_name,
            'case': self.case,
            'case_name': self.case_name,
            'number': self.number,
            'number_name': self.number_name,
            'gender': self.gender,
            'gender_name': self.gender_name,
            'tense': self.tense,
            'person': self.person,
            'animacy': self.animacy,
            'syntax_role': self.syntax_role,
            'syntax_role_name': self.syntax_role_name,
            'position': self.position
        }


class SyntaxRelation(Base):
    __tablename__ = 'syntax_relations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id = Column(Integer, ForeignKey('sentences.id', ondelete='CASCADE'), nullable=False)
    from_token_id = Column(Integer, ForeignKey('tokens.id', ondelete='CASCADE'), nullable=False)
    to_token_id = Column(Integer, ForeignKey('tokens.id', ondelete='CASCADE'), nullable=False)
    relation_type = Column(String(50), nullable=False)
    relation_name = Column(String(100), nullable=False)
    description = Column(String(500), default='')
    created_at = Column(DateTime, default=datetime.now)

    sentence = relationship('Sentence', back_populates='relations')
    from_token = relationship('Token', foreign_keys=[from_token_id])
    to_token = relationship('Token', foreign_keys=[to_token_id])

    def to_dict(self):
        return {
            'id': self.id,
            'sentence_id': self.sentence_id,
            'from_token_id': self.from_token_id,
            'to_token_id': self.to_token_id,
            'from_token_text': self.from_token.token_text if self.from_token else '',
            'to_token_text': self.to_token.token_text if self.to_token else '',
            'relation_type': self.relation_type,
            'relation_name': self.relation_name,
            'description': self.description
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
