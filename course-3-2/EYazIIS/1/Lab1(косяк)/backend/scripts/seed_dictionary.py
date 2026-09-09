#!/usr/bin/env python3
"""Наполнение словаря тестовыми данными"""

import sys

sys.path.insert(0, '.')

from core.dictionary.models import LemmaEntry, MorphRule
from core.dictionary.repository import DictionaryRepository


def seed():
    repo = DictionaryRepository()

    test_entries = [
        LemmaEntry(
            lemma="дом",
            stem="дом",
            pos="существительное",
            rules=[
                MorphRule(ending="", grammemes={"падеж": "именительный", "число": "ед", "род": "муж"}),
                MorphRule(ending="а", grammemes={"падеж": "родительный", "число": "ед", "род": "муж"}),
                MorphRule(ending="у", grammemes={"падеж": "дательный", "число": "ед", "род": "муж"}),
                MorphRule(ending="ом", grammemes={"падеж": "творительный", "число": "ед", "род": "муж"}),
                MorphRule(ending="е", grammemes={"падеж": "предложный", "число": "ед", "род": "муж"}),
                MorphRule(ending="а", grammemes={"падеж": "именительный", "число": "мн", "род": "муж"}),
                MorphRule(ending="ов", grammemes={"падеж": "родительный", "число": "мн", "род": "муж"}),
            ],
            frequency=0,
            meta="Тестовая запись"
        ),
        LemmaEntry(
            lemma="стол",
            stem="стол",
            pos="существительное",
            rules=[
                MorphRule(ending="", grammemes={"падеж": "именительный", "число": "ед", "род": "муж"}),
                MorphRule(ending="а", grammemes={"падеж": "родительный", "число": "ед", "род": "муж"}),
                MorphRule(ending="у", grammemes={"падеж": "дательный", "число": "ед", "род": "муж"}),
                MorphRule(ending="ом", grammemes={"падеж": "творительный", "число": "ед", "род": "муж"}),
                MorphRule(ending="е", grammemes={"падеж": "предложный", "число": "ед", "род": "муж"}),
            ],
            frequency=0,
            meta="Тестовая запись"
        ),
        LemmaEntry(
            lemma="книга",
            stem="книг",
            pos="существительное",
            rules=[
                MorphRule(ending="а", grammemes={"падеж": "именительный", "число": "ед", "род": "жен"}),
                MorphRule(ending="и", grammemes={"падеж": "родительный", "число": "ед", "род": "жен"}),
                MorphRule(ending="е", grammemes={"падеж": "дательный", "число": "ед", "род": "жен"}),
                MorphRule(ending="у", grammemes={"падеж": "винительный", "число": "ед", "род": "жен"}),
                MorphRule(ending="ой", grammemes={"падеж": "творительный", "число": "ед", "род": "жен"}),
                MorphRule(ending="е", grammemes={"падеж": "предложный", "число": "ед", "род": "жен"}),
            ],
            frequency=0,
            meta="Тестовая запись"
        ),
    ]

    for entry in test_entries:
        repo.save(entry)
        print(f"✓ Добавлено: {entry.lemma}")

    print(f"\nВсего записей: {len(repo.search())}")


if __name__ == "__main__":
    seed()