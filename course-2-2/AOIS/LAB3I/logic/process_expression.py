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

            if expr[i] in 'abcde':
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
    vars = [x for x in rpn_tokens if x[0] in 'abcde' or (len(x) > 1 and x[0] == '!' and x[1] in 'abcde')]

    return vars, rpn_tokens