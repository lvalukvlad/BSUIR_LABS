import itertools
import re
from functools import lru_cache


def parse_expression(expression: str):
    variables = sorted(set(re.findall(r'[a-zA-Z]', expression)))
    return variables


def generate_truth_table(variables):
    return list(itertools.product([0, 1], repeat=len(variables)))


def fix_expression_syntax(expression: str):
    expression = expression.replace('!', 'not ')
    expression = expression.replace('&', ' and ')
    expression = expression.replace('|', ' or ')
    return expression


def evaluate_expression(expression: str, variables: list, values: tuple):
    local_env = {var: val for var, val in zip(variables, values)}
    fixed_expr = fix_expression_syntax(expression)
    return eval(fixed_expr, {}, local_env)


def get_minterms(expression: str):
    variables = parse_expression(expression)
    truth_table = generate_truth_table(variables)
    minterms = [values for values in truth_table if evaluate_expression(expression, variables, values)]
    return variables, minterms


def gray_code(n):
    return [i ^ (i >> 1) for i in range(2 ** n)]


def print_karnaugh_map(terms, variables):
    n = len(variables)
    row_bits = n // 2
    col_bits = n - row_bits
    gray_rows = [format(i, f'0{row_bits}b') for i in gray_code(row_bits)]
    gray_cols = [format(i, f'0{col_bits}b') for i in gray_code(col_bits)]

    print("\nКарта Карно:")
    print("   " + " ".join(gray_cols))
    for r in gray_rows:
        row_values = []
        for c in gray_cols:
            term = tuple(int(b) for b in r + c)
            row_values.append('0' if term in terms else '1')
        print(r, " ".join(row_values))


def merge_terms(a, b):
    diff = [i for i in range(len(a)) if a[i] != b[i]]
    if len(diff) == 1:
        return tuple(a[i] if i not in diff else '-' for i in range(len(a)))
    return None


def minimize_karnaugh(terms, variables):
    groups = {i: [] for i in range(len(variables) + 1)}
    for term in terms:
        groups[sum(term)].append(term)

    prime_implicants = set()
    while True:
        next_groups = {i: [] for i in range(len(variables))}
        combined_terms = set()
        marked = set()

        keys = sorted(groups.keys())
        for i in keys:
            if i + 1 not in groups:
                continue
            for term1 in groups[i]:
                for term2 in groups[i + 1]:
                    merged = merge_terms(term1, term2)
                    if merged:
                        next_groups[i].append(merged)
                        combined_terms.add(merged)
                        marked.add(term1)
                        marked.add(term2)

        # Добавляем только те, которые не были объединены
        for group in groups.values():
            for term in group:
                if term not in marked:
                    prime_implicants.add(term)

        if not any(next_groups.values()):
            break
        # Удаляем дубликаты
        groups = {}
        for term in combined_terms:
            ones = sum(1 for x in term if x == 1)
            groups.setdefault(ones, []).append(term)

    essential_prime_implicants = find_essential_prime_implicants(prime_implicants, terms)
    additional_implicants = cover_remaining_terms(essential_prime_implicants, prime_implicants, terms)

    return essential_prime_implicants.union(additional_implicants)



def find_essential_prime_implicants(prime_implicants, terms):
    term_to_implicant = {term: set() for term in terms}
    for implicant in prime_implicants:
        for term in terms:
            if covers(implicant, term):
                term_to_implicant[term].add(implicant)

    essential = set()
    for term, implicants in term_to_implicant.items():
        if len(implicants) == 1:
            essential.add(next(iter(implicants)))

    return essential


def cover_remaining_terms(essential, prime_implicants, terms):
    uncovered_terms = {term for term in terms if not any(covers(implicant, term) for implicant in essential)}
    additional = set()

    while uncovered_terms:
        best_choice = None
        best_coverage = 0
        for implicant in prime_implicants:
            coverage = sum(1 for term in uncovered_terms if covers(implicant, term))
            if coverage > best_coverage:
                best_choice = implicant
                best_coverage = coverage

        if best_choice is None:
            break

        additional.add(best_choice)
        uncovered_terms -= {term for term in uncovered_terms if covers(best_choice, term)}

    return additional


def covers(implicant, term):
    return all(i == j or i == '-' for i, j in zip(implicant, term))


def minimize_sdnf(expression: str):
    variables, minterms = get_minterms(expression)
    minimized = minimize_karnaugh(minterms, variables)

    def term_to_sdnf(term):
        return "(" + " & ".join(
            f"{variables[i]}" if term[i] == 1 else f"!{variables[i]}" for i in range(len(term)) if term[i] != '-') + ")"

    return " | ".join(term_to_sdnf(term) for term in minimized)


def minimize_sdnf_by_spreadsheet_method(expr):
    variables, minterms = get_minterms(expr)
    print_karnaugh_map(minterms, variables)
    result = minimize_sdnf(expr)
    print(f"Минимизированная форма (СДНФ) табличным методом: {result}")
    return result