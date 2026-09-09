import uuid
from pathlib import Path
from typing import Any
from datetime import datetime
import time

from sqlalchemy.orm import Session
from sqlalchemy import delete

from core.models import Document, Sentence, Token, SyntaxRelation, SessionLocal
from core.shared.parser.txt_parser import TxtParser
from core.shared.parser.rtf_parser import RtfParser
from core.shared.syntax.analyzer import (
    SyntaxAnalyzer,
    DependencyTreeBuilder,
    ConstituencyTreeBuilder,
)


class SyntaxManager:
    def __init__(self, data_dir: Path | str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.txt_parser = TxtParser()
        self.rtf_parser = RtfParser()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.dep_tree_builder = DependencyTreeBuilder(self.syntax_analyzer)
        self.const_tree_builder = ConstituencyTreeBuilder(self.syntax_analyzer)

    def _get_db(self) -> Session:
        return SessionLocal()

    def load_file(self, content: bytes, filename: str) -> Document:
        ext = filename.split(".")[-1].lower() if "." in filename else "txt"

        if ext == "rtf":
            text = self.rtf_parser.parse(content)
        else:
            text = self.txt_parser.parse(content)

        title = filename.rsplit(".", 1)[0] if "." in filename else filename

        doc = Document(
            id=str(uuid.uuid4()),
            title=title,
            content=text,
            source=filename,
            text_type="текст для синтаксического анализа",
            created_at=datetime.now(),
            word_count=len(text.split()),
            char_count=len(text),
        )

        return doc

    def add_document(self, doc: Document) -> Document:
        db = self._get_db()
        try:
            db.add(doc)
            db.commit()
            db.refresh(doc)
            return doc
        finally:
            db.close()

    def get_document(self, doc_id: str) -> Document | None:
        db = self._get_db()
        try:
            return db.query(Document).filter(Document.id == doc_id).first()
        finally:
            db.close()

    def get_all_documents(self) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            docs = db.query(Document).order_by(Document.created_at.desc()).all()
            return [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "word_count": doc.word_count,
                    "metadata": doc.to_dict()["metadata"],
                }
                for doc in docs
            ]
        finally:
            db.close()

    def update_document(self, doc_id: str, content: str) -> Document | None:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return None
            doc.content = content
            doc.word_count = len(content.split())
            doc.char_count = len(content)
            db.commit()
            db.refresh(doc)
            return doc
        finally:
            db.close()

    def delete_document(self, doc_id: str) -> bool:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return False
            db.delete(doc)
            db.commit()
            return True
        finally:
            db.close()

    def analyze_document(self, doc_id: str) -> list[dict[str, Any]]:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return []

            sentences = db.query(Sentence).filter(Sentence.document_id == doc_id).all()
            for sent in sentences:
                db.query(Token).filter(Token.sentence_id == sent.id).delete(
                    synchronize_session=False
                )
                db.query(SyntaxRelation).filter(
                    SyntaxRelation.sentence_id == sent.id
                ).delete(synchronize_session=False)
            db.query(Sentence).filter(Sentence.document_id == doc_id).delete(
                synchronize_session=False
            )
            db.commit()

            start_time = time.perf_counter()
            analysis = self.syntax_analyzer.analyze_text(doc.content)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            doc.analysis_time_ms = elapsed_ms
            db.commit()

            for sentence_data in analysis:
                sentence = Sentence(
                    document_id=doc_id,
                    sentence_index=sentence_data["sentence_index"],
                    sentence_text=sentence_data["sentence"],
                    created_at=datetime.now(),
                )
                db.add(sentence)
                db.flush()

                tokens_data = sentence_data.get("tokens", [])
                token_objects = []
                for token_data in tokens_data:
                    token = Token(
                        document_id=doc_id,
                        sentence_id=sentence.id,
                        token_index=token_data.get(
                            "token_index", token_data.get("position", 0)
                        ),
                        token_text=token_data.get("token", ""),
                        lemma=token_data.get("lemma", ""),
                        pos=token_data.get("pos", ""),
                        pos_name=token_data.get("pos_name", ""),
                        case=token_data.get("case", ""),
                        case_name=token_data.get("case_name", ""),
                        number=token_data.get("number", ""),
                        number_name=token_data.get("number_name", ""),
                        gender=token_data.get("gender", ""),
                        gender_name=token_data.get("gender_name", ""),
                        tense=token_data.get("tense", ""),
                        person=token_data.get("person", ""),
                        animacy=token_data.get("animacy", ""),
                        syntax_role=token_data.get("syntax_role", ""),
                        syntax_role_name=token_data.get("syntax_role_name", ""),
                        position=token_data.get("position", 0),
                    )
                    db.add(token)
                    token_objects.append(token)

                db.flush()

                relations = self.syntax_analyzer.detect_relations(token_objects)
                for rel in relations:
                    relation = SyntaxRelation(
                        sentence_id=sentence.id,
                        from_token_id=rel["from_token_id"],
                        to_token_id=rel["to_token_id"],
                        relation_type=rel["relation_type"],
                        relation_name=rel["relation_name"],
                        description=rel.get("description", ""),
                    )
                    db.add(relation)

            db.commit()

            return self.get_analysis(doc_id)
        finally:
            db.close()

    def get_analysis(self, doc_id: str) -> list[dict[str, Any]] | None:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return None

            sentences = (
                db.query(Sentence)
                .filter(Sentence.document_id == doc_id)
                .order_by(Sentence.sentence_index)
                .all()
            )

            result = []
            for sent in sentences:
                sent_dict = sent.to_dict()
                result.append(sent_dict)

            return result
        finally:
            db.close()

    def get_relations(self, doc_id: str) -> list[dict[str, Any]] | None:
        db = self._get_db()
        try:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if not doc:
                return None

            sentences = (
                db.query(Sentence)
                .filter(Sentence.document_id == doc_id)
                .order_by(Sentence.sentence_index)
                .all()
            )

            all_relations = []
            for sent in sentences:
                relations = (
                    db.query(SyntaxRelation)
                    .filter(SyntaxRelation.sentence_id == sent.id)
                    .all()
                )
                for rel in relations:
                    all_relations.append(
                        {
                            "sentence_index": sent.sentence_index,
                            "sentence_text": sent.sentence_text,
                            "relation": rel.to_dict(),
                        }
                    )

            return all_relations
        finally:
            db.close()

    def update_token_role(
        self,
        doc_id: str,
        sentence_id: int,
        token_id: int,
        syntax_role: str,
        syntax_role_name: str,
    ) -> bool:
        db = self._get_db()
        try:
            token = (
                db.query(Token)
                .filter(
                    Token.id == token_id,
                    Token.document_id == doc_id,
                    Token.sentence_id == sentence_id,
                )
                .first()
            )

            if not token:
                return False

            token.syntax_role = syntax_role
            token.syntax_role_name = syntax_role_name
            db.commit()
            return True
        finally:
            db.close()

    def get_dependency_tree(
        self, doc_id: str, sentence_index: int | None = None
    ) -> dict[str, Any]:
        analysis = self.get_analysis(doc_id)
        if not analysis:
            return {"error": "Документ не найден"}

        if sentence_index is not None:
            sentences = [s for s in analysis if s["sentence_index"] == sentence_index]
        else:
            sentences = analysis

        trees = []
        for sent in sentences:
            tree = self.dep_tree_builder.build_tree(sent)
            trees.append(
                {
                    "sentence_index": sent["sentence_index"],
                    "sentence_text": sent["sentence_text"],
                    "tree": tree.get("tree"),
                    "flat_representation": tree.get("flat_representation", []),
                    "root_token": tree.get("root_token"),
                }
            )

        return {"document_id": doc_id, "trees": trees}

    def get_constituency_tree(
        self, doc_id: str, sentence_index: int | None = None
    ) -> dict[str, Any]:
        analysis = self.get_analysis(doc_id)
        if not analysis:
            return {"error": "Документ не найден"}

        if sentence_index is not None:
            sentences = [s for s in analysis if s["sentence_index"] == sentence_index]
        else:
            sentences = analysis

        trees = []
        for sent in sentences:
            tree = self.const_tree_builder.build_tree(sent)
            trees.append(
                {
                    "sentence_index": sent["sentence_index"],
                    "sentence_text": sent["sentence_text"],
                    "tree": tree.get("tree"),
                    "linearized": tree.get("linearized", ""),
                }
            )

        return {"document_id": doc_id, "trees": trees}

    def analyze_text_trees(self, text: str) -> dict[str, Any]:
        analysis = self.syntax_analyzer.analyze_text(text)

        dependency_trees = []
        constituency_trees = []

        for sent_data in analysis:
            dep_tree = self.dep_tree_builder.build_tree(sent_data)
            const_tree = self.const_tree_builder.build_tree(sent_data)

            dependency_trees.append(
                {
                    "sentence_index": sent_data["sentence_index"],
                    "sentence_text": sent_data["sentence"],
                    "tree": dep_tree.get("tree"),
                    "flat_representation": dep_tree.get("flat_representation", []),
                    "root_token": dep_tree.get("root_token"),
                }
            )

            constituency_trees.append(
                {
                    "sentence_index": sent_data["sentence_index"],
                    "sentence_text": sent_data["sentence"],
                    "tree": const_tree.get("tree"),
                    "linearized": const_tree.get("linearized", ""),
                }
            )

        return {
            "text": text,
            "dependency_trees": dependency_trees,
            "constituency_trees": constituency_trees,
            "statistics": self.syntax_analyzer.get_statistics(analysis),
        }
