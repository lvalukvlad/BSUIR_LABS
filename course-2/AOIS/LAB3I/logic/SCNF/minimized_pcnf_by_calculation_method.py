from itertools import product

def truth_table_pcnf(expression, variables):
    table = []
    # Заменяем операторы для корректной работы eval()
    expression = expression.replace("!", "not ").replace("&", " and ").replace("|", " or ")

    for values in product([0, 1], repeat=len(variables)):
        env = {var: bool(val) for var, val in zip(variables, values)}
        result = eval(expression, {}, env)  # Теперь eval() понимает выражение
        if not result:  # Для СКНФ берем строки, где результат 0
            table.append(values)
    return table
def to_sknf(table, variables):
    terms = []
    for row in table:
        term = []
        for var, val in zip(variables, row):
            term.append(var if val == 0 else f"!{var}")
        terms.append(" | ".join(term))
    return " & ".join(f"({t})" for t in terms)

def minimize_sknf_by_calculation_method(expression_str):
    variables = sorted(set(filter(str.isalpha, expression_str)))
    table = truth_table_pcnf(expression_str, variables)
    sknf = to_sknf(table, variables)

    # Создание списка термов в строковом представлении
    terms = ["".join(str(int(v)) for v in row) for row in table]

    # Минимизация
    prime_implicants = set()
    while terms:
        new_terms = set()
        used = set()
        for i in range(len(terms)):
            for j in range(i + 1, len(terms)):
                diffs = [idx for idx in range(len(terms[i])) if terms[i][idx] != terms[j][idx]]
                if len(diffs) == 1:
                    index = diffs[0]
                    new_term = terms[i][:index] + "-" + terms[i][index + 1:]
                    new_terms.add(new_term)
                    used.add(terms[i])
                    used.add(terms[j])
        prime_implicants.update(set(terms) - used)
        terms = list(new_terms)

    minimized_terms = []
    for term in prime_implicants:
        minimized_terms.append(" | ".join(
            var if bit == "0" else f"!{var}" for var, bit in zip(variables, term) if bit != "-"
        ))

    minimized = " & ".join(f"({t})" for t in minimized_terms)
    print('СКНФ расчетным методом, стадии склеивания', sknf)
    return minimized