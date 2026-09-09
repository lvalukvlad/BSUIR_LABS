import random


def is_prime(n):
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def mod_pow(base, exp, mod):
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod  # Умножение с модулем
        base = (base * base) % mod  # Квадрат с модулем
        exp //= 2
    return result


def is_primitive_root(g, p):
    if not is_prime(p):
        raise ValueError("P must be prime")
    phi = p - 1
    # Факторизация phi: 3876 = 2^2 * 3 * 17 * 19, простые делители: 2,3,17,19
    factors = [2, 3, 17, 19]
    for q in factors:
        if mod_pow(g, phi // q, p) == 1:
            return False
    return True


def find_primitive_root(p):
    g = 2
    while not is_primitive_root(g, p):
        g += 1
    return g


def main():
    p = 3877  # Вариант 11
    print(f"Проверка P={p}: простое? {is_prime(p)}")

    g = find_primitive_root(p)
    print(f"Примитивный корень g: {g}")

    a = random.randint(2, p - 2)  # Секрет Алисы
    b = random.randint(2, p - 2)  # Секрет Боба

    A = mod_pow(g, a, p)  # Алиса отправляет A Бобу
    B = mod_pow(g, b, p)  # Боб отправляет B Алисе

    K_alice = mod_pow(B, a, p)
    K_bob = mod_pow(A, b, p)

    print("\nСимуляция протокола:")
    print(f"Алиса: секрет a = {a}, вычисляет A = {g}^{a} mod {p} = {A}")
    print(f"Боб: секрет b = {b}, вычисляет B = {g}^{b} mod {p} = {B}")
    print(f"Алиса вычисляет K = {B}^{a} mod {p} = {K_alice}")
    print(f"Боб вычисляет K = {A}^{b} mod {p} = {K_bob}")
    print(f"Общий секрет совпадает: {K_alice == K_bob}")


if __name__ == "__main__":
    main()