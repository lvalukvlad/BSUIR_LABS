from itertools import product

class Node:
    def __init__(self, value, children=None):
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        if not self.children:
            return self.value
        if len(self.children) == 1:
            return f"!{self.children[0]}"
        return f"({self.children[0]} {self.value} {self.children[1]})"

def tokenize(s: str) -> list:
    tokens = []
    i = 0
    while i < len(s):
        if s[i].isspace():
            i += 1
            continue
        if s[i] in '()':
            tokens.append(s[i])
            i += 1
        elif s[i] == '&':
            tokens.append('&')
            i += 1
        elif s[i] == '|':
            tokens.append('|')
            i += 1
        elif s[i] == '!':
            tokens.append('!')
            i += 1
        elif s[i] == '-' and i + 1 < len(s) and s[i + 1] == '>':
            tokens.append('->')
            i += 2
        elif s[i] == '~':
            tokens.append('~')
            i += 1
        elif s[i].isalpha() and s[i].isupper():
            tokens.append(s[i])
            i += 1
            if i < len(s) and s[i].isalpha():
                raise ValueError(f"Переменные должны быть однобуквенными: {s[i-1:i+1]}")
        else:
            raise ValueError(f"Недопустимый символ: {s[i]}")
    return tokens

def parse_formula_to_tree(s: str) -> Node:
    tokens = tokenize(s)
    if not tokens:
        raise ValueError("Пустая формула")
    node, pos = parse_equivalence(tokens, 0)
    if pos != len(tokens):
        raise ValueError("Некорректная структура формулы: лишние токены")
    return node

def parse_equivalence(tokens: list, pos: int) -> tuple:
    node, pos = parse_implication(tokens, pos)
    while pos < len(tokens) and tokens[pos] == '~':
        op = tokens[pos]
        pos += 1
        right, pos = parse_implication(tokens, pos)
        node = Node(op, [node, right])
    return node, pos

def parse_implication(tokens: list, pos: int) -> tuple:
    node, pos = parse_disjunction(tokens, pos)
    while pos < len(tokens) and tokens[pos] == '->':
        op = tokens[pos]
        pos += 1
        right, pos = parse_disjunction(tokens, pos)
        node = Node(op, [node, right])
    return node, pos

def parse_disjunction(tokens: list, pos: int) -> tuple:
    node, pos = parse_conjunction(tokens, pos)
    while pos < len(tokens) and tokens[pos] == '|':
        op = tokens[pos]
        pos += 1
        right, pos = parse_conjunction(tokens, pos)
        node = Node(op, [node, right])
    return node, pos

def parse_conjunction(tokens: list, pos: int) -> tuple:
    node, pos = parse_negation(tokens, pos)
    while pos < len(tokens) and tokens[pos] == '&':
        op = tokens[pos]
        pos += 1
        right, pos = parse_negation(tokens, pos)
        node = Node(op, [node, right])
    return node, pos

def parse_negation(tokens: list, pos: int) -> tuple:
    if pos < len(tokens) and tokens[pos] == '!':
        pos += 1
        node, pos = parse_negation(tokens, pos)
        return Node('!', [node]), pos
    return parse_atom(tokens, pos)

def parse_atom(tokens: list, pos: int) -> tuple:
    if pos >= len(tokens):
        raise ValueError("Некорректная структура формулы")
    token = tokens[pos]
    if token == '(':
        pos += 1
        node, pos = parse_equivalence(tokens, pos)
        if pos >= len(tokens) or tokens[pos] != ')':
            raise ValueError("Несбалансированные скобки")
        pos += 1
        return node, pos
    if is_atomic(token):
        pos += 1
        return Node(token), pos
    raise ValueError(f"Недопустимый токен: {token}")

def is_atomic(s: str) -> bool:
    return len(s) == 1 and s.isalpha() and s.isupper()

def evaluate(node: Node, variables: dict) -> bool:
    if is_atomic(node.value):
        result = variables.get(node.value, False)
        return result
    if node.value == '!':
        child_result = evaluate(node.children[0], variables)
        result = not child_result
        return result
    left_val = evaluate(node.children[0], variables)
    right_val = evaluate(node.children[1], variables)
    if node.value == '&':
        result = left_val and right_val
        return result
    if node.value == '|':
        result = left_val or right_val
        return result
    if node.value == '->':
        result = not left_val or right_val
        return result
    if node.value == '~':
        result = left_val == right_val
        return result
    raise ValueError(f"Неизвестная операция: {node.value}")

def get_variables(node: Node) -> set:
    variables = set()
    if is_atomic(node.value):
        variables.add(node.value)
    for child in node.children:
        variables.update(get_variables(child))
    return variables

def is_neutral(formula: str) -> bool:
    try:
        tree = parse_formula_to_tree(formula)
        variables = sorted(get_variables(tree))
        for values in product([True, False], repeat=len(variables)):
            var_dict = dict(zip(variables, values))
            result = evaluate(tree, var_dict)
            if not result:
                return False
        return True
    except ValueError:
        return False

def is_contradiction(formula: str) -> bool:
    try:
        tree = parse_formula_to_tree(formula)
        variables = sorted(get_variables(tree))
        for values in product([True, False], repeat=len(variables)):
            var_dict = dict(zip(variables, values))
            if evaluate(tree, var_dict):
                return False
        return True
    except ValueError:
        return False