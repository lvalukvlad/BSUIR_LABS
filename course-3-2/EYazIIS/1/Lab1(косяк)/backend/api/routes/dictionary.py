"""Маршруты API для работы со словарём — ПОЛНОСТЬЮ РАБОЧАЯ ВЕРСИЯ"""

from fastapi import APIRouter, HTTPException, status, Query, Body
from typing import Optional, List
from urllib.parse import unquote

from core.dictionary.repository import DictionaryRepository
from core.dictionary.models import LemmaEntry, MorphRule

router = APIRouter(tags=["Словарь"])
repo = DictionaryRepository()


@router.get("/dictionary")
def get_dictionary(
    search: Optional[str] = Query(None),
    pos: Optional[str] = Query(None),
    limit: Optional[int] = Query(None)
):
    """Получение списка лемм с фильтрацией"""
    if search:
        search = unquote(search.strip())
    if pos:
        pos = unquote(pos.strip())

    entries = repo.search(query=search or "", pos_filter=pos)
    if limit and limit > 0:
        entries = entries[:limit]

    # 🔥 Возвращаем список dict, не объектов!
    return [e.to_dict() for e in entries]


@router.get("/dictionary-item")
def get_lemma(lemma: str = Query(..., description="Лемма для поиска")):
    """Получение одной леммы по точному совпадению"""
    lemma_clean = unquote(lemma).strip()
    entry = repo.get(lemma_clean)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma_clean}' не найдена"
        )

    # 🔥 Возвращаем dict, не объект!
    return entry.to_dict()


@router.post("/dictionary", status_code=status.HTTP_201_CREATED)
def add_lemma(entry: LemmaEntry = Body(...)):
    """Добавление новой леммы"""
    if not entry.lemma or not entry.lemma.strip():
        raise HTTPException(400, detail="Поле 'lemma' обязательно")

    lemma = entry.lemma.strip()

    if repo.get(lemma):
        raise HTTPException(409, detail=f"Лемма '{lemma}' уже существует")

    # Нормализуем
    entry.lemma = lemma
    if not entry.stem:
        entry.stem = entry.lemma

    repo.save(entry)

    # 🔥 Возвращаем dict!
    return entry.to_dict()


@router.put("/dictionary")  # ← КЛЮЧЕВОЕ: только query-параметр, не path!
def update_lemma(
    lemma: str = Query(..., description="Лемма для обновления"),
    entry: LemmaEntry = Body(...)
):
    """
    Обновление существующей леммы.

    Использование:
      PUT /api/dictionary?lemma=значение
      Body: {"lemma": "...", "stem": "...", "pos": "...", "rules": [...], "frequency": N}
    """
    from urllib.parse import unquote

    # Декодируем кириллицу из query-параметра
    lemma_clean = unquote(lemma).strip()

    # Проверяем существование
    old_entry = repo.get(lemma_clean)
    if not old_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma_clean}' не найдена"
        )

    # === Обновляем поля (только если переданы и не пустые) ===

    if entry.stem and entry.stem.strip():
        old_entry.stem = entry.stem.strip()

    if entry.pos and entry.pos.strip():
        old_entry.pos = entry.pos.strip()

    if entry.rules is not None and len(entry.rules) > 0:
        old_entry.rules = entry.rules

    if entry.meta is not None:
        old_entry.meta = entry.meta

    # frequency обновляем всегда, если передан (0 — валидное значение!)
    if entry.frequency is not None:
        old_entry.frequency = entry.frequency

    # === Сохраняем и ВОЗВРАЩАЕМ результат ===
    repo.save(old_entry)

    # 🔥🔥🔥 КЛЮЧЕВОЙ МОМЕНТ: явно возвращаем dict, не объект!
    return old_entry.to_dict()


@router.delete("/dictionary")
def delete_lemma(lemma: str = Query(..., description="Лемма для удаления")):
    """Удаление леммы"""
    from urllib.parse import unquote
    lemma_clean = unquote(lemma).strip()

    if not repo.delete(lemma_clean):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma_clean}' не найдена"
        )

    # 🔥 Возвращаем JSON, не пустой ответ!
    return {"success": True, "deleted": lemma_clean}