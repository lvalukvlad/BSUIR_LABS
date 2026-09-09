'''
Лабораторная работа №1
по дисциплине ЛОИС
Выполнена студентами группы 321701
Филиппов Руслан Михайлович, Политыко Илья Андреевич, Лукашов Владислав Андреевич
Вариант 1:
Реализовать прямой нечёткий логический вывод используя импликацию Гёделя
'''

from prettytable import PrettyTable
import re

class InvalidInput(Exception):
    pass

def is_fact_valid(fact):
    pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9]*\([a-zA-Z][a-zA-Z0-9]*\)=\{(\([a-zA-Z][a-zA-Z0-9]*,[01](\.\d+)?\),)*(\([a-zA-Z][a-zA-Z0-9]*,[01](\.\d+)?\))?\}$')
    return bool(pattern.match(fact))

def get_fact_name(fact):
    pattern = r'^([a-zA-Z][a-zA-Z0-9]*\([a-zA-Z][a-zA-Z0-9]*\))=\{(.*)\}$'
    match = re.match(pattern, fact)
    if match:
        return match.group(1)
    return None

def get_fact_set(fact):
    pattern = r"^([a-zA-Z][a-zA-Z0-9]*\([a-zA-Z][a-zA-Z0-9]*\))=\{(.*)\}$"
    match = re.match(pattern, fact)
    if match:
        pairs_str = match.group(2)
        if not pairs_str:
            return tuple()
        pairs = [tuple(pair.split(",")) for pair in pairs_str[1:-1].split("),(")]
        return tuple(map(lambda x: (x[0], float(x[1])), pairs))
    return tuple()

def is_rule_valid(rule):
    pattern = re.compile(r"^[a-zA-Z][a-zA-Z0-9]*\([a-zA-Z][a-zA-Z0-9]*\)~>[a-zA-Z][a-zA-Z0-9]*\([a-zA-Z][a-zA-Z0-9]*\)$")
    return bool(pattern.match(rule))

def get_rule_impl(rule):
    parts = rule.split('~>', 1)
    if len(parts) == 2:
        return (parts[0], parts[1])
    return None

def load_data(file):
    with open(file, 'r') as f:
        facts, rules = (tuple(''.join(x.split()) for x in line.split('\n')) for line in f.read().split('\n\n'))
    for fact in facts:
        if not is_fact_valid(fact):
            raise InvalidInput(f'Факт {fact} введен неккоректно!')
    for rule in rules:
        if not is_rule_valid(rule):
            raise InvalidInput(f'Правило {rule} введено неккоректно!')
    return facts, rules

def facts_to_dict_form(facts):
    fact_sets = {}
    for fact in facts:
        name = get_fact_name(fact)
        pairs = get_fact_set(fact)
        fact_sets[name] = dict(pairs)
    return fact_sets

def fact_to_set_form(dict_form):
    if not dict_form:
        return {}
    set_form = '{'
    for var in dict_form:
        set_form += f'({var}, {dict_form[var]}), '
    set_form = set_form[:-2] + '}'
    return set_form

def process_rule(rule, fact_sets):
    impl = get_rule_impl(rule)
    fact1, fact2 = impl
    if fact1 not in fact_sets:
        raise InvalidInput(f'Факт {fact1} из правила {rule} не найден в базе знаний')
    if fact2 not in fact_sets:
        raise InvalidInput(f'Факт {fact2} из правила {rule} не найден в базе знаний')
    fact1_set = fact_sets[fact1]
    fact2_set = fact_sets[fact2]
    relation = compute_impl(fact1_set, fact2_set)
    print(f'Матрица импликации для {fact1} ~> {fact2}:')
    print_table(f'{fact1} ~> {fact2}', relation)
    result = f'{fact2} = {fact_to_set_form(conclusion(fact1_set, relation))}'
    print(f'Результат вывода для правила {rule}: {result}\n')

def t_norm(v1, v2):
    return min(v1, v2)

def gedel_impl(v1, v2):
    if v1 <= v2:
        return 1
    else:
        return v2

def compute_impl(set1, set2):
    relation = {}
    for i in set1:
        relation[i] = {}
        for j in set2:
            v1 = set1[i]
            v2 = set2[j]
            relation[i][j] = gedel_impl(v1, v2)
    return relation

def conclusion(set, relation):
    concl_set = {}
    for i in list(relation[list(relation.keys())[0]].keys()):
        values = []
        for j in relation:
            values.append(t_norm(set[j], relation[j][i]))
        concl_set[i] = max(values)
        print(f'{i}: max({values} = {concl_set[i]}')
    return concl_set

def print_table(name, table):
    pretty_table = PrettyTable()
    rows_names = list(table.keys())
    cols_names = [name, *list(table[rows_names[0]].keys())]
    pretty_table.field_names = cols_names
    for row_name in rows_names:
        pretty_table.add_row([row_name, *table[row_name].values()])
    print(pretty_table)