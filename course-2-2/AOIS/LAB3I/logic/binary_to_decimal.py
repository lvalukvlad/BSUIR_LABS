def binary_to_decimal(binary_str: str) -> int:
    decimal_number = 0
    power = len(binary_str) - 1

    for digit in binary_str:
        decimal_number += int(digit) * (2 ** power)
        power -= 1

    return decimal_number