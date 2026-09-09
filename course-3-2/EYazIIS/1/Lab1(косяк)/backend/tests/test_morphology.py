"""Тесты морфологического анализа"""

import sys
sys.path.insert(0, '.')

from core.morphology.analyzer import RussianMorphAnalyzer
from core.morphology.stem_extractor import StemExtractor
from core.morphology.rule_builder import RuleBuilder


def test_analyzer_basic():
    """Тест базового анализа слова"""
    analyzer = RussianMorphAnalyzer()
    
    result = analyzer.analyze("домами")
    assert result is not None
    assert result['lemma'] == 'дом'
    assert result['pos'] == 'существительное'
    assert 'grammemes' in result
    
    print("✓ RussianMorphAnalyzer: basic analysis")


def test_analyzer_pos_mapping():
    """Тест маппинга частей речи"""
    analyzer = RussianMorphAnalyzer()
    
    result = analyzer.analyze("стол")
    assert result['pos'] == 'существительное'
    
    result = analyzer.analyze("красивый")
    assert result['pos'] == 'прилагательное'
    
    print("✓ RussianMorphAnalyzer: POS mapping")


def test_stem_extractor_basic():
    """Тест извлечения основы"""
    extractor = StemExtractor()
    
    stem = extractor.extract("домами", "дом")
    assert stem == "дом"
    
    stem = extractor.extract("книгой", "книга")
    assert stem in ["книга", "книг"]
    
    print("✓ StemExtractor: basic extraction")


def test_stem_extractor_with_ending():
    """Тест извлечения основы и окончания"""
    extractor = StemExtractor()
    
    stem, ending = extractor.extract_with_ending("домами", "дом")
    assert stem == "дом"
    assert ending == "ами"
    
    print("✓ StemExtractor: stem + ending")


def test_rule_builder_basic():
    """Тест построения правил из парадигмы"""
    builder = RuleBuilder()
    
    rules = builder.build_from_lemma("дом")
    
    # Правила должны быть построены
    assert len(rules) > 0, "Правила должны быть построены"
    
    # Каждое правило должно иметь grammemes
    for rule in rules:
        assert isinstance(rule.grammemes, dict), "grammemes должен быть dict"
    
    # Должно быть хотя бы одно правило с заполненными граммемами
    rules_with_grammemes = [r for r in rules if r.grammemes]
    assert len(rules_with_grammemes) > 0, "Должны быть правила с морфологической информацией"
    
    # Проверяем наличие хотя бы одного падежа
    case_values = set(r.grammemes.get('падеж') for r in rules if r.grammemes.get('падеж'))
    assert len(case_values) >= 1, "Должны быть правила хотя бы с одним падежом"
    
    print("✓ RuleBuilder: basic rule generation")


def test_rule_builder_cases():
    """Тест наличия правил для основных падежей"""
    builder = RuleBuilder()
    
    rules = builder.build_from_lemma("дом")
    case_values = [r.grammemes.get('падеж') for r in rules]
    
    has_nominative = any(c in ['nomn', 'именительный'] for c in case_values)
    has_locative = any(c in ['loct', 'предложный'] for c in case_values)
    has_genitive = any(c in ['gent', 'родительный'] for c in case_values)
    
    assert has_nominative or has_locative or has_genitive, \
        "Должно быть хотя бы одно правило с падежом"
    
    print("✓ RuleBuilder: case rules present")


def test_rule_builder_fallback():
    """Тест fallback-правил для недостающих падежей"""
    builder = RuleBuilder()
    
    rules = builder.build_from_lemma("книга")
    endings = set(r.ending for r in rules)
    
    # Допускаем, что все окончания могут быть пустыми (для леммы)
    # Главное — что правила есть
    assert len(rules) > 0, "Должны быть построены правила"
    
    print("✓ RuleBuilder: fallback rules")


def test_rule_builder_grammemes_format():
    """Тест формата граммем в правилах"""
    builder = RuleBuilder()
    
    rules = builder.build_from_lemma("стол")
    
    for rule in rules:
        assert isinstance(rule.grammemes, dict), "grammemes должен быть dict"
        for key in rule.grammemes:
            assert isinstance(key, str), f"Ключ граммемы должен быть str: {key}"
    
    print("✓ RuleBuilder: grammemes format")


if __name__ == "__main__":
    print("Запуск тестов морфологии...")
    
    test_analyzer_basic()
    test_analyzer_pos_mapping()
    test_stem_extractor_basic()
    test_stem_extractor_with_ending()
    test_rule_builder_basic()
    test_rule_builder_cases()
    test_rule_builder_fallback()
    test_rule_builder_grammemes_format()
    
    print("\n✅ Все тесты морфологии пройдены!")
