
from fastapi import Depends, HTTPException, status
from core.dictionary.repository import DictionaryRepository
from core.morphology.analyzer import RussianMorphAnalyzer

# Singleton instances
_repo_instance = None
_morph_instance = None

def get_repository() -> DictionaryRepository:
    """Получение репозитория словаря"""
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = DictionaryRepository()
    return _repo_instance

def get_morph_analyzer() -> RussianMorphAnalyzer:
    """Получение морфологического анализатора"""
    global _morph_instance
    if _morph_instance is None:
        _morph_instance = RussianMorphAnalyzer()
    return _morph_instance

def validate_lemma(lemma: str, repo: DictionaryRepository = Depends(get_repository)):
    """Проверка существования леммы"""
    if not repo.get(lemma):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Лемма '{lemma}' не найдена"
        )
    return lemma