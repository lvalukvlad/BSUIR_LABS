from typing import List


def addition_bin(a, b):
    result = [0] * 5
    carry = 0
    for i in range(3, -1, -1):
        total = a[i] + b[i] + carry
        result[i + 1] = total % 2
        carry = total // 2

    result[0] = carry

    return result


def arithmetic_operations(matrix, key) -> List[int]:
    print(matrix)
    V = 3
    A = 4
    B = 4
    S = 5
    columns: List[int] = []
    for element in range(len(matrix)):
        b: bool = True
        for i in range(len(key)):
            if matrix[i][element] != key[i]:
                b = False
        if b:
            columns.append(element)
    if len(columns) > 0:
        for element in columns:
            a: List[int] = []
            b: List[int] = []
            s: List[int] = []
            for i in range(V, V + A):
                a.append(matrix[i][element])
            print(a)
            for i in range(V + A, V + A + B):
                b.append(matrix[i][element])
            print(b)
            s = addition_bin(a, b)
            print(f"    {s}")
            start: int = V + A + B
            for i in range(S):
                matrix[start + i][element] = s[i]
    return matrix