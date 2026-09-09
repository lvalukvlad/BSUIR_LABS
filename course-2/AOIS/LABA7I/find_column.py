from typing import List


def find_column(matrix, num) -> List[int]:
    RANGE = 16
    column: List[int] = []
    for i in range(RANGE):
        row = num + i if num + i < RANGE else num + i - RANGE
        column.append(matrix[i][row])
    return column