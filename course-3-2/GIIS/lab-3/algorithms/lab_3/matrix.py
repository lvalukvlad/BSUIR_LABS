from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


M_BEZIER = [
    [-1, 3, -3, 1],
    [3, -6, 3, 0],
    [-3, 3, 0, 0],
    [1, 0, 0, 0]
]

M_HERMITE = [
    [2, -3, 0, 1],
    [1, -2, 1, 0],
    [1, -1, 0, 0],
    [-2, 3, 0, 0]
]


def get_curve_matrix(name):
    if name == "Безье":
        return M_BEZIER
    elif name == "Эрмит":
        return M_HERMITE
    else:
        raise ValueError(f"Неизвестная кривая: {name}")


def multiply(A, B):
    rows_a = len(A)
    cols_a = len(A[0])
    rows_b = len(B)
    cols_b = len(B[0])

    if cols_a != rows_b:
        raise ValueError("Нельзя умножить матрицы: несовместимые размеры")

    result = [[0.0 for _ in range(cols_b)] for _ in range(rows_a)]

    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += A[i][k] * B[k][j]

    return result


def multiply_vector(M, v):
    result = []
    for row in M:
        val = sum(row[i] * v[i] for i in range(len(v)))
        result.append(val)
    return result


def inverse(M):
    n = len(M)
    if n != 4 or len(M[0]) != 4:
        raise ValueError("Инверсия поддерживается только для матриц 4x4")

    A = [row[:] for row in M]

    I = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    for i in range(n):
        pivot = A[i][i]
        if abs(pivot) < 1e-10:
            raise ValueError("Матрица вырожденная")

        for j in range(n):
            A[i][j] /= pivot
            I[i][j] /= pivot

        for k in range(n):
            if k != i:
                factor = A[k][i]
                for j in range(n):
                    A[k][j] -= factor * A[i][j]
                    I[k][j] -= factor * I[i][j]

    return I


def transpose(M):
    return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]
