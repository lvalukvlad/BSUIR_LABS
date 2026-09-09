
import uuid
from pathlib import Path
from typing import Any

from sqlalchemy import func

from core.models import Document, Token, SessionLocal, init_db
from core.shared.parser.txt_parser import TxtParser
from core.shared.parser.rtf_parser import RtfParser
from core.shared.parser.pdf_parser import PdfParser
from core.shared.parser.doc_parser import DocParser
from core.shared.parser.docx_parser import DocxParser
from core.shared.morphology.analyzer import MorphAnalyzer


class TextDocument:
    def __init__(
        self,
        doc_id: str,
        title: str,
        content: str,
        source: str = "",
        author: str = "",
        date: str = "",
        genre: str = "",
        text_type: str = ""
    ):
        self.id = doc_id
        self.title = title
        self.content = content
        self.source = source
        self.author = author
        self.date = date
        self.genre = genre
        self.text_type = text_type
        self.word_count = len(content.split())
        self.char_count = len(content)

    def to_dict(self) -> dict[str, Any]:
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
                'created_at': ''
            }
        }


class CorpusManager:
    def __init__(self, data_dir: Path | str):
        self.data_dir = Path(data_dir)
        
        init_db()
        
        self.txt_parser = TxtParser()
        self.rtf_parser = RtfParser()
        self.pdf_parser = PdfParser()
        self.doc_parser = DocParser()
        self.docx_parser = DocxParser()
        self.morph = MorphAnalyzer()

    def load_file(self, content: bytes, filename: str) -> TextDocument:
        ext = filename.split('.')[-1].lower() if '.' in filename else 'txt'
        
        if ext == 'rtf':
            text = self.rtf_parser.parse(content)
        elif ext == 'pdf':
            text = self.pdf_parser.parse(content)
        elif ext == 'doc':
            text = self.doc_parser.parse(content)
        elif ext == 'docx':
            text = self.docx_parser.parse(content)
        else:
            text = self.txt_parser.parse(content)
        
        title = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        doc = TextDocument(
            doc_id=str(uuid.uuid4()),
            title=title,
            content=text,
            source=filename,
            text_type='кулинарный текст'
        )
        
        return doc

    def add_document(self, doc: TextDocument):
        db = SessionLocal()
        try:
            db_doc = Document(
                id=doc.id,
                title=doc.title,
                content=doc.content,
                source=doc.source,
                author=doc.author,
                date=doc.date,
                genre=doc.genre,
                text_type=doc.text_type,
                word_count=doc.word_count,
                char_count=doc.char_count
            )
            db.add(db_doc)
            db.flush()

            analysis = self.morph.analyze_text(doc.content)
            for item in analysis:
                token = Token(
                    document_id=doc.id,
                    token=item['token'],
                    position=item['position'],
                    lemma=item['analysis']['lemma'],
                    pos=item['analysis']['pos'],
                    case=item['analysis']['grammemes'].get('падеж', ''),
                    number=item['analysis']['grammemes'].get('число', ''),
                    gender=item['analysis']['grammemes'].get('род', '')
                )
                db.add(token)
            
            db.commit()
        finally:
            db.close()

    def get_document(self, doc_id: str) -> TextDocument | None:
        db = SessionLocal()
        try:
            db_doc = db.query(Document).filter(Document.id == doc_id).first()
            if not db_doc:
                return None
            
            doc = TextDocument(
                doc_id=db_doc.id,
                title=db_doc.title,
                content=db_doc.content,
                source=db_doc.source,
                author=db_doc.author,
                date=db_doc.date,
                genre=db_doc.genre,
                text_type=db_doc.text_type
            )
            doc.word_count = db_doc.word_count
            doc.char_count = db_doc.char_count
            return doc
        finally:
            db.close()

    def get_all_documents(self) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            docs = db.query(Document).all()
            return [
                {
                    'id': doc.id,
                    'title': doc.title,
                    'word_count': doc.word_count,
                    'metadata': {
                        'source': doc.source,
                        'author': doc.author,
                        'date': doc.date,
                        'genre': doc.genre,
                        'text_type': doc.text_type,
                        'word_count': doc.word_count,
                        'char_count': doc.char_count,
                        'created_at': doc.created_at.isoformat() if doc.created_at else ''
                    }
                }
                for doc in docs
            ]
        finally:
            db.close()

    def update_document(self, doc_id: str, content: str) -> TextDocument | None:
        db = SessionLocal()
        try:
            db_doc = db.query(Document).filter(Document.id == doc_id).first()
            if not db_doc:
                return None
            
            db_doc.content = content
            db_doc.word_count = len(content.split())
            db_doc.char_count = len(content)
            
            db.query(Token).filter(Token.document_id == doc_id).delete()
            
            analysis = self.morph.analyze_text(content)
            for item in analysis:
                token = Token(
                    document_id=doc_id,
                    token=item['token'],
                    position=item['position'],
                    lemma=item['analysis']['lemma'],
                    pos=item['analysis']['pos'],
                    case=item['analysis']['grammemes'].get('падеж', ''),
                    number=item['analysis']['grammemes'].get('число', ''),
                    gender=item['analysis']['grammemes'].get('род', '')
                )
                db.add(token)
            
            db.commit()
            
            return self.get_document(doc_id)
        finally:
            db.close()

    def delete_document(self, doc_id: str) -> bool:
        db = SessionLocal()
        try:
            db_doc = db.query(Document).filter(Document.id == doc_id).first()
            if not db_doc:
                return False
            
            db.delete(db_doc)
            db.commit()
            return True
        finally:
            db.close()

    def analyze_document(self, doc_id: str) -> list[dict[str, Any]]:
        db = SessionLocal()
        try:
            tokens = db.query(Token).filter(Token.document_id == doc_id).all()
            return [token.to_dict() for token in tokens]
        finally:
            db.close()

    def get_lemmas(self, doc_id: str) -> dict[str, int]:
        db = SessionLocal()
        try:
            results = db.query(
                Token.lemma,
                func.count(Token.id).label('count')
            ).filter(Token.document_id == doc_id).group_by(Token.lemma).all()
            return {row.lemma: row.count for row in results}
        finally:
            db.close()

    def get_wordform_frequencies(self, doc_id: str | None = None) -> dict[str, int]:
        db = SessionLocal()
        try:
            query = db.query(
                func.lower(Token.token).label('token'),
                func.count(Token.id).label('count')
            )
            if doc_id:
                query = query.filter(Token.document_id == doc_id)
            results = query.group_by(func.lower(Token.token)).all()
            return {row.token: row.count for row in results}
        finally:
            db.close()

    def get_lemma_frequencies(self, doc_id: str | None = None) -> dict[str, int]:
        db = SessionLocal()
        try:
            query = db.query(
                Token.lemma,
                func.count(Token.id).label('count')
            )
            if doc_id:
                query = query.filter(Token.document_id == doc_id)
            results = query.group_by(Token.lemma).all()
            return {row.lemma: row.count for row in results}
        finally:
            db.close()

    def get_pos_statistics(self, doc_id: str | None = None) -> dict[str, int]:
        db = SessionLocal()
        try:
            query = db.query(
                Token.pos,
                func.count(Token.id).label('count')
            )
            if doc_id:
                query = query.filter(Token.document_id == doc_id)
            results = query.group_by(Token.pos).all()
            return {row.pos: row.count for row in results}
        finally:
            db.close()

    def get_grammar_statistics(self, doc_id: str | None = None) -> dict[str, dict[str, int]]:
        db = SessionLocal()
        try:
            case_stats: dict[str, int] = {}
            number_stats: dict[str, int] = {}
            gender_stats: dict[str, int] = {}
            
            query = db.query(Token)
            if doc_id:
                query = query.filter(Token.document_id == doc_id)
            
            tokens = query.all()
            for token in tokens:
                if token.case:
                    case_stats[token.case] = case_stats.get(token.case, 0) + 1
                if token.number:
                    number_stats[token.number] = number_stats.get(token.number, 0) + 1
                if token.gender:
                    gender_stats[token.gender] = gender_stats.get(token.gender, 0) + 1
            
            return {
                'падежи': case_stats,
                'числа': number_stats,
                'роды': gender_stats
            }
        finally:
            db.close()

    def search(self, query: str, doc_id: str | None = None) -> list[dict[str, Any]]:
        query_lower = query.lower()
        results = []
        
        if doc_id:
            docs = [self.get_document(doc_id)]
        else:
            docs = [self.get_document(d['id']) for d in self.get_all_documents()]
        
        for doc in docs:
            if not doc:
                continue
            
            content_lower = doc.content.lower()
            start = 0
            while True:
                pos = content_lower.find(query_lower, start)
                if pos == -1:
                    break
                
                context_start = max(0, pos - 50)
                context_end = min(len(doc.content), pos + len(query) + 50)
                
                results.append({
                    'document_id': doc.id,
                    'document_title': doc.title,
                    'position': pos,
                    'context': doc.content[context_start:context_end]
                })
                
                start = pos + 1
        
        return results

    def concordance(self, query: str, doc_id: str | None = None, context: int = 5) -> list[dict[str, Any]]:
        query_lower = query.lower()
        results = []
        
        if doc_id:
            docs = [self.get_document(doc_id)]
        else:
            docs = [self.get_document(d['id']) for d in self.get_all_documents()]
        
        for doc in docs:
            if not doc:
                continue
            
            words = doc.content.split()
            for i, word in enumerate(words):
                word_clean = word.lower().strip('.,!?;:"()[]')
                if word_clean == query_lower:
                    start = max(0, i - context)
                    end = min(len(words), i + context + 1)
                    
                    left = ' '.join(words[start:i])
                    center = words[i]
                    right = ' '.join(words[i+1:end])
                    
                    results.append({
                        'document_id': doc.id,
                        'document_title': doc.title,
                        'position': i,
                        'left': left,
                        'keyword': center,
                        'right': right,
                        'full_context': f"{left} {center} {right}"
                    })
        
        return results
