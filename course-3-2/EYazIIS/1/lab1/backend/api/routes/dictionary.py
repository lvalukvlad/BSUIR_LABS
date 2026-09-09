from fastapi import APIRouter, HTTPException, status, Query, Body, Path
from typing import Optional, List
from urllib.parse import unquote
import json

from core.dictionary.repository import DictionaryRepository
from core.dictionary.models import LemmaEntry, MorphRule

router = APIRouter(tags=["Словарь"])
repo = DictionaryRepository()


def _normalize_lemma(lemma: str) -> str:
    if not lemma:
        return ""
    return unquote(lemma).strip().lower()


@router.get("/dictionary")
def get_dictionary(
    search: Optional[str] = Query(None),
    pos: Optional[str] = Query(None),
    limit: Optional[int] = Query(None)
):
    if search:
        search = _normalize_lemma(search)
    if pos:
        pos = unquote(pos).strip()

    entries = repo.search(query=search or "", pos_filter=pos)
    if limit and limit > 0:
        entries = entries[:limit]

    return [e.to_dict() for e in entries]


@router.get("/dictionary-item")
def get_lemma(lemma: str = Query(..., description="Лемма для поиска")):
    lemma_clean = _normalize_lemma(lemma)
    entry = repo.get(lemma_clean)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma_clean}' не найдена"
        )
    return entry.to_dict()


@router.post("/dictionary", status_code=status.HTTP_201_CREATED)
def add_lemma(entry: LemmaEntry = Body(...)):
    if not entry.lemma or not entry.lemma.strip():
        raise HTTPException(400, detail="Поле 'lemma' обязательно")
    lemma = _normalize_lemma(entry.lemma).lower()

    if repo.get(lemma):
        raise HTTPException(409, detail=f"Лемма '{lemma}' уже существует")

    entry.lemma = lemma
    if not entry.stem:
        entry.stem = entry.lemma
    repo.save(entry)
    return entry.to_dict()

@router.put("/dictionary")
def update_lemma(
    lemma: str = Query(..., description="Лемма для обновления"),
    entry: LemmaEntry = Body(...)
):
    lemma_clean = _normalize_lemma(lemma)

    old_entry = repo.get(lemma_clean)
    if not old_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma_clean}' не найдена"
        )

    if entry.stem and entry.stem.strip():
        old_entry.stem = entry.stem.strip()

    if entry.pos and entry.pos.strip():
        old_entry.pos = entry.pos.strip()

    if entry.rules is not None and len(entry.rules) > 0:
        old_entry.rules = entry.rules

    if entry.meta is not None:
        old_entry.meta = entry.meta

    if entry.frequency is not None:
        old_entry.frequency = entry.frequency

    repo.save(old_entry)

    return old_entry.to_dict()


@router.delete("/dictionary")
def delete_lemma(lemma: str = Query(..., description="Лемма для удаления")):
    lemma_clean = _normalize_lemma(lemma)

    if not repo.delete(lemma_clean):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma_clean}' не найдена"
        )

    return {"success": True, "deleted": lemma_clean}


@router.get("/dictionary/export")
def export_dictionary(format: str = Query("json", description="Формат экспорта: json, txt")):
    entries = repo.all()
    
    if format == "txt":
        # Экспорт в текстовый формат для документирования
        lines = []
        lines.append("=" * 60)
        lines.append("СЛОВАРЬ ЕСТЕСТВЕННОГО ЯЗЫКА")
        lines.append("=" * 60)
        lines.append(f"Всего слов: {len(entries)}")
        lines.append("=" * 60)
        lines.append("")
        
        for entry in entries:
            lines.append(f"Лемма: {entry.lemma}")
            lines.append(f"  Основа: {entry.stem}")
            lines.append(f"  Часть речи: {entry.pos}")
            lines.append(f"  Частота: {entry.frequency}")
            if entry.rules:
                lines.append(f"  Правила словоизменения:")
                for rule in entry.rules:
                    grammemes_str = ", ".join([f"{k}={v}" for k, v in rule.grammemes.items()])
                    lines.append(f"    - окончание '{rule.ending}': {grammemes_str}")
            lines.append("")
        
        return {"format": "txt", "content": "\n".join(lines)}

    return {
        "format": "json", 
        "total": len(entries),
        "entries": [e.to_dict() for e in entries]
    }


@router.put("/dictionary/{lemma}/rules")
def update_rules(
    lemma: str = Path(..., description="Лемма"),
    rules: List[dict] = Body(..., description="Список правил")
):
    lemma_clean = _normalize_lemma(lemma)
    entry = repo.get(lemma_clean)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma_clean}' не найдена"
        )

    morph_rules = [MorphRule.from_dict(r) for r in rules]
    entry.rules = morph_rules
    repo.save(entry)

    return entry.to_dict()


@router.delete("/dictionary/{lemma}/rules/{rule_index}")
def delete_rule(
    lemma: str = Path(..., description="Лемма"),
    rule_index: int = Path(..., description="Индекс правила")
):
    lemma_clean = _normalize_lemma(lemma)
    entry = repo.get(lemma_clean)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma_clean}' не найдена"
        )

    if rule_index < 0 or rule_index >= len(entry.rules):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Правило с индексом {rule_index} не найдено"
        )

    deleted_rule = entry.rules.pop(rule_index)
    repo.save(entry)

    return {
        "success": True,
        "deleted": deleted_rule.to_dict(),
        "remaining_rules": len(entry.rules)
    }


@router.post("/dictionary/{lemma}/rules")
def add_rule(
    lemma: str = Path(..., description="Лемма"),
    rule: dict = Body(..., description="Новое правило")
):
    lemma_clean = _normalize_lemma(lemma)
    entry = repo.get(lemma_clean)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma_clean}' не найдена"
        )

    morph_rule = MorphRule.from_dict(rule)
    entry.rules.append(morph_rule)
    repo.save(entry)

    return {
        "success": True,
        "added": morph_rule.to_dict(),
        "total_rules": len(entry.rules)
    }