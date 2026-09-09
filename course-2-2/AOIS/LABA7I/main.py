from typing import List
from generate_matrix import generate_matrix
from generate_matrix import print_matrix
from find_logos import find_logos
from find_column import find_column
from logical_operations import logical_operations
from arithmetic_operations import arithmetic_operations
from ordered_selection import ordered_selection

if __name__ == '__main__':
    choice: int = 1
    matrix = generate_matrix()
    while choice != 0:
        choice = int(input(r"""
                    1 - Сгенерировать матрицу;
                    2 - Считывание;
                    3 - Логические функции;
                    4 - Упорядоченная выборка;
                    5 - Арифметические операции;
                    0 - Выход;
                    """))
        if choice == 1:
            matrix = generate_matrix()
            print_matrix(matrix)
        if choice == 2:
            new_choice: int = int(input(
                        r"""
                        1 - Считывание столбца;
                        2 - Считывание слова;
                        """))
            if new_choice == 1:
                num: int = int(input('Введите номер столбца с 0 до 15: '))
                try:
                    if 0 <= num <= 15:
                        print(find_column(matrix, num))
                        continue
                    else:
                        print('Неправильно введено число')
                        continue
                except:
                    print('Ошибка: Считывание столбца')
                    continue
            if new_choice == 2:
                num: int = int(input('Введите номер слова с 0 до 15: '))
                try:
                    if 0 <= num <= 15:
                        print(find_logos(matrix, num))
                        continue
                    else:
                        print('Неправильно введено число')
                        continue
                except:
                    print('Ошибка: Считывание столбца')
                    continue
        if choice == 3:
            logos_1: List[int]
            logos_2: List[int]
            num: int = int(input('Введите номер слова с 0 до 15: '))
            try:
                if 0 <= num <= 15:
                    logos_1 = find_logos(matrix, num)
                    print(f'Логос-1 {logos_1}')
                else:
                    print('Неправильно введено число')
                    continue
            except:
                print('Ошибка: Логические функции logos_1')
                continue
            num: int = int(input('Введите номер слова с 0 до 15: '))
            try:
                if 0 <= num <= 15:
                    logos_2 = find_logos(matrix, num)
                    print(f'Логос-2 {logos_2}')
                else:
                    print('Неправильно введено число')
                    continue
            except:
                print('Ошибка: Логические функции logos_2')
                continue
            logical_operations(logos_1, logos_2)
        if choice == 4:
            ordered_selection(matrix)
        if choice == 5:
            num_1: int = 0
            num_2: int = 0
            num_3: int = 0
            logos: List[int] = [num_1, num_2, num_3]
            try:
                num_1: int = int(input('Введите цифру 0 или 1: '))
                num_2: int = int(input('Введите цифру 0 или 1: '))
                num_3: int = int(input('Введите цифру 0 или 1: '))
                if 0 <= num_1 <= 1 and 0 <= num_2 <= 1 and 0 <= num_3 <= 1:
                    logos[0] = num_1
                    logos[1] = num_2
                    logos[2] = num_3
                    arithmetic_operations(matrix, logos)
                    print(matrix)
                    print_matrix(matrix)
                else:
                    print('Неправильная цифра')
            except:
                print('Ошибка: Арифметические операции')
                continue