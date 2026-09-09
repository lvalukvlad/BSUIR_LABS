from typing import List
from generate_matrix import print_matrix


def find_logos(column, num) -> List[int]:
    RANGE = 16
    logos: List[int] = []
    for i in range(RANGE):
        row = num + i if num + i < RANGE else num + i - RANGE
        logos.append(column[row])
    return logos


def reverse_matrix(matrix: List[List[int]]) -> List[List[int]]:
    new_matrix: List[List[int]] = []
    for element in range(len(matrix)):
        column: List[int] = []
        for i in range(len(matrix)):
            column.append(matrix[i][element])
        new_matrix.append(column)
    return new_matrix


def comparison_logos(max_column, column, index):
    logos: List[int] = find_logos(column, index)
    max_logos: List[int] = find_logos(max_column, index)
    for element in range(len(logos)):
        if logos[element] == max_logos[element]:
            continue
        if logos[element] > max_logos[element]:
            return True
        else:
            return False


def sort_matrix(matrix: List[List[int]]):
    new_matrix: List[List[int]] = reverse_matrix(matrix).copy()
    for element in range(len(matrix) - 1, 0, -1):
        max_column: List[int] = new_matrix[element].copy()
        for i in range(element):
            if comparison_logos(max_column, new_matrix[i], element):
                intermediate_column: List[int] = new_matrix[i]
                new_matrix[element] = intermediate_column
                new_matrix[i] = max_column
                max_column = intermediate_column.copy()
    return reverse_matrix(new_matrix)


def ordered_selection(matrix: List[List[int]]) -> List[List[int]]:
    print_matrix(matrix)
    result_matrix = sort_matrix(matrix)
    print('\n\n\n')
    print_matrix(result_matrix)
    return result_matrix