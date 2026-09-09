from typing import List


def f6(logos_1, logos_2) -> List[int]:
    logos_result: List[int] = []
    for i in range(len(logos_1)):
        if logos_1[i] == logos_2[i]:
            logos_result.append(0)
        else:
            logos_result.append(1)
    return logos_result


def f9(logos_1, logos_2) -> List[int]:
    logos_result: List[int] = []
    for i in range(len(logos_1)):
        if logos_1[i] == logos_2[i]:
            logos_result.append(1)
        else:
            logos_result.append(0)
    return logos_result


def f4(logos_1, logos_2) -> List[int]:
    logos_result: List[int] = []
    for i in range(len(logos_1)):
        if logos_1[i] == 0 and logos_2[i] == 1:
            logos_result.append(1)
        else:
            logos_result.append(0)
    return logos_result


def f11(logos_1, logos_2) -> List[int]:
    logos_result: List[int] = []
    for i in range(len(logos_1)):
        if logos_1[i] == 0 and logos_2[i] == 1:
            logos_result.append(0)
        else:
            logos_result.append(1)
    return logos_result


def logical_operations(logos_1, logos_2):
    print(f'f6 - {f6(logos_1, logos_2)}')
    print(f'f9 - {f9(logos_1, logos_2)}')
    print(f'f4 - {f4(logos_1, logos_2)}')
    print(f'f11 - {f11(logos_1, logos_2)}')