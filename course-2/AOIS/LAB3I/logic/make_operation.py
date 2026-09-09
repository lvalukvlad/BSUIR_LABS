def make_operation(first: int, second: int, operation: str):
    if operation == '&':
        if first == 1 and second == 1:
            return 1
        return 0
    elif operation == '|':
        if first == 0 and second == 0:
            return 0
        return 1
    elif operation == '->':
        if first == 1 and second == 0:
            return 0
        return 1
    elif operation == '~':
        if first == second:
            return 1
        return 0
    else:
        return 0