from app.language_model import (
    FrequentWordsRecognizer,
    NeuralNetworkRecognizer,
    ShortWordsRecognizer,
    out_of_place_distance,
)
from app.text_processing import detect_language, lexemes, normalize

PASSED = 0
FAILED = 0


def check(title, condition, detail=""):
    global PASSED, FAILED
    mark = "OK  " if condition else "FAIL"
    if condition:
        PASSED += 1
    else:
        FAILED += 1
    print(f"[{mark}] {title}" + (f" -- {detail}" if detail else ""))


def section(title):
    print(f"\n=== {title} ===")


def main():
    section("1. Предобработка русского текста")
    lemmas = normalize("Локальные вычислительные сети объединяют компьютеры")
    check("лемматизация русских слов", any(item.startswith("сет") for item in lemmas), str(lemmas[:6]))

    section("2. Предобработка немецкого текста")
    de_lemmas = lexemes("Für die Größe der Lösung ist das Krankenhaus zuständig")
    check("немецкие умлауты не теряются", "für" in de_lemmas and "größe" in de_lemmas, str(de_lemmas[:8]))
    check("немецкий текст токенизируется", len(de_lemmas) > 0, str(de_lemmas[:5]))

    section("3. Обнаружение языка")
    check("русский текст обнаружен", detect_language("Привет мир") == "русский")
    check("немецкий текст обнаружен", detect_language("Hallo Welt") == "немецкий")

    section("4. Метод коротких слов")
    short = ShortWordsRecognizer()
    ru_texts = ["это тест для метода коротких слов " * 6]
    de_texts = ["das ist ein test für die erkennung " * 6]
    profiles = {
        "русский": short.build_profile(ru_texts),
        "немецкий": short.build_profile(de_texts),
    }
    result_mix = short.recognize("это для слов das ist ein", profiles)
    check("короткие слова видят оба языка", set(result_mix.get("languages") or []) == {"русский", "немецкий"}, str(result_mix))

    section("5. Метод частотных слов")
    freq = FrequentWordsRecognizer()
    long_ru = [" ".join(["привет", "мир", "тест", "текст"] * 50) for _ in range(5)]
    long_de = [" ".join(["hallo", "welt", "test", "text"] * 50) for _ in range(5)]
    profiles_f = {
        "русский": freq.build_profile(long_ru),
        "немецкий": freq.build_profile(long_de),
    }
    result_f = freq.recognize("привет мир текст", profiles_f)
    check("частотных слов распознаёт русский", "русский" in result_f.get("languages", []), str(result_f))

    section("6. Расстояние Out-of-Place")
    distance = out_of_place_distance(["а", "б", "в", "г", "д"], ["а", "г", "б", "д", "в"])
    check("OoP учитывает ранги, а не алфавит", distance == 6, f"distance={distance}")
    empty = out_of_place_distance([], ["а"])
    check("OoP для пустого профиля", empty == float("inf"))

    section("7. Нейросетевой метод")
    nn = NeuralNetworkRecognizer()
    nn.train(
        ["это русский текст про больницу и врача"] * 4
        + ["das ist ein deutscher text über krankenhaus und arzt"] * 4,
        ["русский"] * 4 + ["немецкий"] * 4,
    )
    result_nn = nn.recognize("врач осмотрел пациента в больнице")
    check("нейросеть распознаёт русский", "русский" in result_nn.get("languages", []), str(result_nn))

    print(f"\nИтог: пройдено {PASSED}, не пройдено {FAILED}")
    if FAILED:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
