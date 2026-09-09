# Вариант: F4
# Лабораторная работа №1 по дисциплине Логические Основы Интеллектуальных Систем
# Выполнена студентом группы 321701 Лукашовым Владиславом Андреевичем
#
# 08.05.2025
#
# Задание:
#  Проверить, является ли формула сокращённого языка логики высказываний нейтральной
#
# Использованные источники:
# Справочная система по дисциплине ЛОИС
# Логические основы интеллектуальных систем. Практикум

from formula_processor import *

def read_formula_from_file(filename: str) -> str:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return "".join(line.strip() for line in file)
    except FileNotFoundError:
        print("Не удалось открыть файл.")
        return ""

def user_test():
    test_cases = [
        ("A | !A", True),           # Нейтральная
        ("A & !A", False),          # Противоречие
        ("A & B", False),           # Не нейтральная
        ("A | B", False),           # Не нейтральная
        ("A -> B", False),          # Не нейтральная
        ("A ~ B", False),           # Не нейтральная
        ("(A & B) | (!A & !B)", False),  # Не нейтральная
        ("A & (B | !B)", False),    # Не нейтральная
        ("(A -> B) & (B -> A)", False), # Не нейтральная
        ("!(A & B)", False),        # Не нейтральная
        ("A & (B -> C)", False),    # Не нейтральная
        ("(A | B) & !A", False),    # Не нейтральная
        ("A ~ !A", False),          # Не нейтральная
        ("(A -> B) | (B -> A)", True),  # Нейтральная
        ("(A & B) -> (A | B)", True)    # Нейтральная
    ]

    correct = 0
    for i, (formula, expected) in enumerate(test_cases, start=1):
        print(f"\nФормула #{i}: {formula}")
        while True:
            answer = input("Это нейтральная формула? (1 - да, 0 - нет): ").strip()
            if answer not in ("0", "1"):
                print("Некорректный ввод. Введите '1' или '0'.")
                continue
            user_answer = (answer == "1")
            break
        if user_answer == expected:
            print("Правильно!")
            correct += 1
        else:
            print(f"Неправильно. Формула {'нейтральная' if expected else 'не нейтральная'}.")
            if expected:
                print("Пояснение: Формула всегда истинна при любых значениях переменных.")
            else:
                if is_contradiction(formula):
                    print("Пояснение: Формула всегда ложна.")
                else:
                    print("Пояснение: Формула может быть истинной или ложной в зависимости от значений переменных.")
    print(f"\nВы ответили правильно на {correct} из {len(test_cases)} вопросов ({correct / len(test_cases) * 100:.1f}%).")

def main():
    while True:
        print("\nМеню:")
        print("1 - Ввод формулы")
        print("2 - Чтение формулы из файла")
        print("3 - Пройти тест на знание нейтральных формул")
        print("4 - Автор")
        print("0 - Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("Спасибо за использование программы!")
            break
        elif choice == "4":
            print("Лукашов Владислав Андреевич, группа 321701")
            continue
        elif choice == "3":
            user_test()
            continue
        elif choice not in ("1", "2"):
            print("Неверный выбор. Введите 0, 1, 2, 3 или 4.")
            continue

        if choice == "1":
            input_formula = input("Введите формулу (операторы: &, |, !, ->, ~): ").strip()
        else:  # choice == "2"
            filename = input("Введите имя файла: ").strip()
            input_formula = read_formula_from_file(filename)

        if not input_formula:
            print("Формула пуста.")
            continue

        try:
            if is_neutral(input_formula):
                print(f"Формула '{input_formula}' является нейтральной.")
            else:
                print(f"Формула '{input_formula}' не является нейтральной.")
                if is_contradiction(input_formula):
                    print("Пояснение: Формула является противоречием.")
                else:
                    print("Пояснение: Формула может быть истинной или ложной в зависимости от значений переменных.")
        except ValueError as e:
            print(f"Формула невалидна: {e}")
            print("Убедитесь, что формула содержит:")
            print("- Только допустимые символы (A-Z, &, |, !, ->, ~, (, ))")
            print("- Сбалансированные скобки")
            print("- Однобуквенные переменные (A, B, C, ...)")
            print("- Корректный синтаксис (например, (A & B), !(A -> B))")

if __name__ == "__main__":
    main()