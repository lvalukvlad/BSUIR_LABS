"""Тесты парсеров входных файлов"""

import sys
sys.path.insert(0, '.')

from core.parser.txt_parser import TxtParser
from core.parser.rtf_parser import RtfParser


def test_txt_parser_utf8():
    """Тест TXT-парсера: UTF-8 кодировка"""
    parser = TxtParser()
    content = "Привет мир".encode('utf-8')
    result = parser.parse(content)
    assert result == "Привет мир"
    print("✓ TxtParser UTF-8")


def test_txt_parser_cp1251():
    """Тест TXT-парсера: CP1251 кодировка"""
    parser = TxtParser()
    content = "Привет мир".encode('cp1251')
    result = parser.parse(content)
    assert result == "Привет мир"
    print("✓ TxtParser CP1251")


def test_txt_parser_auto_detect():
    """Тест автоопределения кодировки"""
    parser = TxtParser()
    # Смешанный контент
    content = "Дом дома дому.".encode('utf-8')
    result = parser.parse(content)
    assert "дом" in result.lower()
    print("✓ TxtParser auto-detect")


def test_rtf_parser_simple():
    """Тест RTF-парсера: простой документ"""
    parser = RtfParser()
    # RTF с ASCII-текстом (без кириллицы в bytes literal)
    rtf_content = b"{\\rtf1\\ansi Hello world.\\par}"
    result = parser.parse(rtf_content)
    assert "Hello" in result or "world" in result
    print("✓ RtfParser simple ASCII")


def test_rtf_parser_with_cyrillic():
    """Тест RTF-парсера: кириллица через encode"""
    parser = RtfParser()
    # Кириллица должна быть закодирована
    text = "{\\rtf1\\ansi Дом дома дому.\\par}"
    rtf_content = text.encode('utf-8')
    result = parser.parse(rtf_content)
    # После striprtf должен остаться текст
    assert "дом" in result.lower() or "Дом" in result
    print("✓ RtfParser with Cyrillic")


def test_rtf_parser_fallback():
    """Тест RTF-парсера: fallback при отсутствии striprtf"""
    parser = RtfParser()
    # Если striprtf не установлен, должен работать как TxtParser
    content = "Test text".encode('utf-8')
    result = parser.parse(content)
    assert "Test" in result or "text" in result
    print("✓ RtfParser fallback")


if __name__ == "__main__":
    print("Запуск тестов парсеров...")
    test_txt_parser_utf8()
    test_txt_parser_cp1251()
    test_txt_parser_auto_detect()
    test_rtf_parser_simple()
    test_rtf_parser_with_cyrillic()
    test_rtf_parser_fallback()
    print("\n✅ Все тесты парсеров пройдены!")