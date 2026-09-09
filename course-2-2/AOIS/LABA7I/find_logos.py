from typing import List


def find_logos(matrix, num) -> List[int]:
    RANGE = 16
    logos: List[int] = []
    for i in range(RANGE):
        row = num + i if num + i < RANGE else num + i - RANGE
        logos.append(matrix[row][num])
    return logos