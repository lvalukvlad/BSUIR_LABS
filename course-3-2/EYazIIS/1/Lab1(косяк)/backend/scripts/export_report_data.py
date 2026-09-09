#!/usr/bin/env python3
"""Экспорт данных для отчёта"""

import sys
import json

sys.path.insert(0, '.')

from core.dictionary.repository import DictionaryRepository


def export():
    repo = DictionaryRepository()
    entries = repo.search()

    report_data = {
        "total_lemmas": len(entries),
        "total_frequency": sum(e.frequency for e in entries),
        "parts_of_speech": {},
        "lemmas": [e.to_dict() for e in entries[:20]]  # первые 20 для примера
    }

    # Статистика по частям речи
    for entry in entries:
        pos = entry.pos
        report_data["parts_of_speech"][pos] = report_data["parts_of_speech"].get(pos, 0) + 1

    # Сохранение
    with open("docs/report_data.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"✓ Экспортировано {len(entries)} записей")
    print(f"✓ Части речи: {report_data['parts_of_speech']}")
    print("✓ Файл: docs/report_data.json")


if __name__ == "__main__":
    export()