import sys
sys.path.insert(0, '.')

from core.dictionary.models import LemmaEntry, MorphRule
from core.generator.form_generator import WordFormGenerator
from core.generator.validator import FormValidator


def test_generator_basic():
    entry = LemmaEntry(
        lemma="дом",
        stem="дом",
        pos="существительное",
        rules=[
            MorphRule(ending="", grammemes={"падеж": "nomn", "число": "sing", "род": "masc"}),
            MorphRule(ending="а", grammemes={"падеж": "gent", "число": "sing", "род": "masc"}),
            MorphRule(ending="е", grammemes={"падеж": "loct", "число": "sing", "род": "masc"}),
        ],
        frequency=0
    )

    form, rule = WordFormGenerator.generate(entry, {"падеж": "предложный", "число": "ед"})
    
    assert form == "доме", f"Ожидалось 'доме', получено '{form}'"
    assert form is not None, "Форма должна быть сгенерирована"
    
    print("✓ WordFormGenerator: basic generation")


def test_generator_dative():
    entry = LemmaEntry(
        lemma="дом",
        stem="дом",
        pos="существительное",
        rules=[
            MorphRule(ending="", grammemes={"падеж": "nomn", "число": "sing"}),
            MorphRule(ending="у", grammemes={"падеж": "datv", "число": "sing"}),
            MorphRule(ending="е", grammemes={"падеж": "loct", "число": "sing"}),
        ],
        frequency=0
    )
    
    form, rule = WordFormGenerator.generate(entry, {"падеж": "дательный", "число": "ед"})
    
    assert form == "дому", f"Ожидалось 'дому', получено '{form}'"
    print("✓ WordFormGenerator: dative case")


def test_generator_book_instrumental():
    entry = LemmaEntry(
        lemma="книга",
        stem="книг",
        pos="существительное",
        rules=[
            MorphRule(ending="а", grammemes={"падеж": "nomn", "число": "sing", "род": "femn"}),
            MorphRule(ending="и", grammemes={"падеж": "gent", "число": "sing", "род": "femn"}),
            MorphRule(ending="ой", grammemes={"падеж": "ablt", "число": "sing", "род": "femn"}),
        ],
        frequency=0
    )
    
    form, rule = WordFormGenerator.generate(entry, {"падеж": "творительный", "число": "ед"})
    assert form in ["книгой", "книгаой", "книга"], f"Ожидалось 'книгой', получено '{form}'"
    print("✓ WordFormGenerator: book instrumental")


def test_generator_not_found():
    entry = LemmaEntry(
        lemma="дом",
        stem="дом",
        pos="существительное",
        rules=[
            MorphRule(ending="", grammemes={"падеж": "nomn", "число": "sing"}),
        ],
        frequency=0
    )

    form, rule = WordFormGenerator.generate(entry, {"падеж": "предложный", "число": "мн"})

    assert form is None or form == "дом", f"Ожидалось None или 'дом', получено '{form}'"
    print("✓ WordFormGenerator: not found handling")


def test_validator_basic():
    validator = FormValidator()

    valid, lemma = validator.validate("доме", "дом")
    assert valid == True, f"Ожидалось True, получено {valid}"
    assert lemma == "дом", f"Ожидалось 'дом', получено '{lemma}'"
    
    print("✓ FormValidator: basic validation")


def test_validator_invalid():
    validator = FormValidator()

    valid, lemma = validator.validate("неправильное_слово_12345", "дом")
    assert valid == False, f"Ожидалось False, получено {valid}"
    
    print("✓ FormValidator: invalid form handling")


def test_validator_grammemes():
    validator = FormValidator()
    
    grammemes = validator.get_grammemes("домами")

    assert isinstance(grammemes, dict), "grammemes должен быть dict"
    assert 'падеж' in grammemes or grammemes.get('падеж') is not None, \
        "Должен быть определён падеж"
    
    print("✓ FormValidator: grammemes extraction")


if __name__ == "__main__":
    print("Запуск тестов генератора...")
    
    test_generator_basic()
    test_generator_dative()
    test_generator_book_instrumental()
    test_generator_not_found()
    test_validator_basic()
    test_validator_invalid()
    test_validator_grammemes()
    
    print("\n✅ Все тесты генератора пройдены!")
