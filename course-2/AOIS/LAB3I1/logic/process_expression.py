def process_expression(expression):
    def get_operator_priority(operator):
        priorities = {
            '!': 4,
            '&': 3,
            '|': 2,
            '->': 1,
            '~': 1,
            '(': 0
        }
        return priorities.get(operator, 0)

    def infix_to_rpn(expr):
        output = []
        operator_stack = []
        i = 0

        while i < len(expr):
            if expr[i].isspace():
                i += 1
                continue

            # Обработка переменных (включая отрицания)
            if expr[i] in 'abcde':
                # Проверяем отрицание перед переменной
                if i > 0 and expr[i - 1] == '!':
                    output.append(f"!{expr[i]}")
                else:
                    output.append(expr[i])
                i += 1
                continue

            if expr[i] == '!' and i + 1 < len(expr) and expr[i + 1] in 'abcde':
                output.append(f"!{expr[i + 1]}")
                i += 2
                continue

            if expr[i] == '(':
                operator_stack.append('(')
                i += 1
                continue

            if expr[i] == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                i += 1
                continue

            if expr[i] in '&|!->~':
                current_op = expr[i]
                if current_op == '-' and i + 1 < len(expr) and expr[i + 1] == '>':
                    current_op = '->'
                    i += 1

                while (operator_stack and operator_stack[-1] != '(' and
                       get_operator_priority(operator_stack[-1]) >= get_operator_priority(current_op)):
                    output.append(operator_stack.pop())

                operator_stack.append(current_op)
                i += 1
                continue

            i += 1

        while operator_stack:
            if operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            else:
                operator_stack.pop()

        return output

    rpn_tokens = infix_to_rpn(expression)
    # Убираем дублирование переменных с отрицаниями
    vars = []
    seen = set()
    for token in rpn_tokens:
        if token[0] in 'abcde' or (len(token) > 1 and token[0] == '!' and token[1] in 'abcde'):
            if token not in seen:
                vars.append(token)
                seen.add(token)

    return vars, rpn_tokens