'''
Лабораторная работа №1
по дисциплине ЛОИС
Выполнена студентами группы 321701
Филиппов Руслан Михайлович, Политыко Илья Андреевич, Лукашов Владислав Андреевич
Вариант 1:
Реализовать прямой нечеткий логический вывод используя импликацию Геделя
'''

from functions import *
import os

if __name__ == '__main__':
    file = input('Введите имя файла: ')
    if not os.path.isfile(file):
        print(f'Файл {file} не найден!')
        exit()
    print('База знаний:')
    with open(file, 'r') as f:
        print(f.read())
    facts, rules = load_data(file)
    try:
        facts, rules = load_data(file)
        fact_sets = facts_to_dict_form(facts)
        print('\nОбработка правил:')
        for rule in rules:
            print(rule)
            process_rule(rule, fact_sets)
    except InvalidInput as e:
        print(f'Ошибка: {e}')
