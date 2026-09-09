from logic.to_bin import to_bin
from logic.make_operation import make_operation


def rpn_check(rpn):
    stack = []
    for element in rpn:
        if isinstance(element, int):  # Проверка на числовое значение
            stack.append(element)
            continue
        if element == '!':
            if not stack:
                continue
            stack[-1] = 1 - stack[-1]
        else:
            if len(stack) < 2:
                continue
            b = stack.pop()
            a = stack.pop()
            res = make_operation(a, b, element)
            stack.append(res)
    return stack[0] if stack else 0


def table_create(exp: str, rpn: list, vars: list):
    # Получаем уникальные переменные без отрицаний в алфавитном порядке
    unique_vars = sorted(list({v.replace('!', '') for v in vars}))
    num_vars = len(unique_vars)
    vars_in_degree = 2 ** num_vars

    # Вывод заголовка таблицы
    print(" ".join(unique_vars) + " | F")
    print("-" * (len(unique_vars) * 2 + 3))

    index_form = []
    truth_table = []

    for i in range(vars_in_degree):
        bool_vars = to_bin(i, num_vars)
        bool_rpn = rpn.copy()

        # Заменяем переменные на их значения с учетом отрицаний
        for var in vars:
            clean_var = var.replace('!', '')
            val = bool_vars[unique_vars.index(clean_var)]
            if '!' in var:
                val = 1 - val
            bool_rpn = [val if x == var else x for x in bool_rpn]

        result = rpn_check(bool_rpn)
        truth_table.append((bool_vars.copy(), result))
        index_form.append(str(result))

        # Вывод строки таблицы истинности
        print(" ".join(map(str, bool_vars)) + f" | {result}")

    # Формируем СДНФ и СКНФ (в обратном порядке для соответствия индексной форме)
    pdnf_exp_list = []
    pcnf_exp_list = []
    pdnf_list = []
    pcnf_list = []

    for i, (bool_vars, result) in enumerate(truth_table):
        if result == 1:
            term = []
            for f in range(num_vars):
                term.append(f"{'' if bool_vars[f] else '!'}{unique_vars[f]}")
            pdnf_list.append(str(i))
            pdnf_exp_list.append('(' + '&'.join(term) + ')')
        else:
            term = []
            for f in range(num_vars):
                term.append(f"{'!' if bool_vars[f] else ''}{unique_vars[f]}")
            pcnf_list.append(str(i))
            pcnf_exp_list.append('(' + '|'.join(term) + ')')

    # Индексная форма должна быть в обратном порядке (от 111..1 до 000..0)
    correct_index_form = index_form[::-1]

    return {
        'index': ''.join(correct_index_form),  # Правильный порядок битов
        'pdnf': '(' + ', '.join(pdnf_list) + ')',
        'pcnf': '(' + ', '.join(pcnf_list) + ')',
        'pdnf_exp_list': '|'.join(pdnf_exp_list),
        'pcnf_exp_list': '&'.join(pcnf_exp_list),
        'truth_table': truth_table  # Для дополнительной проверки
    }