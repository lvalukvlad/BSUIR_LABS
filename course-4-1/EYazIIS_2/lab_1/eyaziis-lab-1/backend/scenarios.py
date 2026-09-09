"""Проверочные сценарии работы системы.

Запуск: docker compose exec backend python scenarios.py
Скрипт последовательно проверяет предобработку текста, поиск, интеллектуальные
функции интерфейса и обработку ошибочных ситуаций, печатая результат каждого шага.
"""
from app.db import init_pool
from app.document_loader import UnsupportedFormatError, extract_text
from app.indexer import collection_stats, delete_document, index_document
from app.probabilistic import collection_size, rsj_weight
from app.query_assistant import analyze_query, correct_query, suggest
from app.search_service import search
from app.text_processing import normalize

PASSED = 0
FAILED = 0


def check(title: str, condition: bool, detail: str = "") -> None:
    global PASSED, FAILED
    mark = "OK  " if condition else "FAIL"
    if condition:
        PASSED += 1
    else:
        FAILED += 1
    print(f"[{mark}] {title}" + (f" -- {detail}" if detail else ""))


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    init_pool()

    section("1. Предобработка текста")
    lemmas = normalize("Локальные вычислительные сети объединяют компьютеры в здании")
    check("лемматизация и отсев стоп-слов", "сеть" in lemmas and "в" not in lemmas, str(lemmas))
    check("прилагательные приводятся к начальной форме", "локальный" in lemmas)

    section("2. Состояние индекса")
    stats = collection_stats()
    check("коллекция загружена", stats["documents"] == 18, f"документов: {stats['documents']}")
    check("словарь построен", stats["terms"] > 1000, f"терминов: {stats['terms']}")
    check("инвертированный индекс заполнен", stats["postings"] > 3000, f"постингов: {stats['postings']}")

    section("3. Веса вероятностной модели")
    n_docs, avgdl = collection_size()
    rare = rsj_weight(n_docs, 1)
    frequent = rsj_weight(n_docs, 15)
    check("редкий термин весит больше частого", rare > frequent, f"{rare:.3f} против {frequent:.3f}")
    check("средняя длина документа рассчитана", avgdl > 100, f"avgdl = {avgdl:.1f}")

    section("4. Поиск по запросам разной сложности")
    single = search("хоккей", top_k=10)
    check("однословный запрос находит документ", single["total"] >= 1,
          f"первый результат: {single['results'][0]['title'] if single['results'] else 'нет'}")

    multi = search("нейронные сети и машинное обучение", top_k=10)
    titles = [item["title"] for item in multi["results"]]
    check("многословный запрос ранжирует верно",
          titles and "Нейронные сети" in titles[0], f"топ: {titles[:2]}")

    empty = search("абракадабра кувырком заковыристо", top_k=10)
    check("запрос без совпадений даёт пустую выдачу", empty["total"] == 0)

    section("5. Интеллектуальные функции интерфейса")
    corrected, corrections = correct_query("нейроные сети")
    check("опечатка исправляется", len(corrections) > 0, f"{corrections}")

    analysis = analyze_query("ии в медицине")
    check("аббревиатура расширяется синонимами",
          "искусственный" in analysis["expanded"], f"{analysis['expanded']}")

    hints = suggest("нейр")
    check("автодополнение по префиксу работает", len(hints) > 0, f"{hints}")

    with_snippet = search("вторая мировая война", top_k=5)
    first = with_snippet["results"][0]
    check("сниппет содержит подсветку", "<mark>" in first["snippet"])
    check("возвращается список найденных слов запроса", len(first["matched_words"]) > 0,
          f"{first['matched_words'][:5]}")

    section("6. Загрузка документов")
    html = "<html><body><h1>Заголовок</h1><p>Сетевой протокол</p></body></html>"
    text = extract_text("test.html", html.encode("utf-8"))
    check("текст извлекается из HTML", "Сетевой протокол" in text, repr(text[:50]))

    try:
        extract_text("picture.png", b"\x89PNG")
        check("неподдерживаемый формат отклоняется", False)
    except UnsupportedFormatError:
        check("неподдерживаемый формат отклоняется", True)

    section("7. Индексация и удаление документа")
    doc_id = index_document(
        title="Временный документ о квантовых вычислениях",
        body="Квантовый компьютер использует кубиты и явление суперпозиции состояний.",
    )
    found = search("квантовый компьютер кубиты", top_k=5)
    check("новый документ становится доступен поиску",
          any(r["document_id"] == doc_id for r in found["results"]))
    check("документ удаляется из индекса", delete_document(doc_id))
    after = search("квантовый компьютер кубиты", top_k=5)
    check("после удаления документ не находится",
          all(r["document_id"] != doc_id for r in after["results"]))

    print(f"\nИтог: пройдено {PASSED}, не пройдено {FAILED}")


if __name__ == "__main__":
    main()
