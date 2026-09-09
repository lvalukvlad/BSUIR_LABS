import random
import math


def is_prime(n, k=20):
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1: continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1: break
        else:
            return False
    return True


def generate_prime(bits):
    while True:
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1
        if is_prime(p): return p


def mod_exp(base, exponent, modulus):
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent = exponent >> 1
    return result


def extended_gcd(a, b):
    if a == 0: return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    return gcd, x, x1


def mod_inverse(a, m):
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1: return None
    return (x % m + m) % m


def generate_rsa_keys(bits=1024):
    p = generate_prime(bits)
    q = generate_prime(bits)
    while p == q: q = generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    while math.gcd(e, phi) != 1:
        e = random.randint(3, phi - 1)
    d = mod_inverse(e, phi)
    return (e, n), (d, n), p, q


def save_to_file(filename, data):
    with open(filename, 'w') as f:
        f.write(str(data))


def read_from_file(filename):
    with open(filename, 'r') as f:
        return f.read().strip()


def create_test_data():
    test_messages = [str(random.randint(1000, 1000000)) for _ in range(10)]
    with open('test_data.txt', 'w') as f:
        for msg in test_messages:
            f.write(msg + '\n')
    print("Создано 10 тестовых сообщений в файле test_data.txt")


def main():
    print("RSA КРИПТОСИСТЕМА")
    try:
        with open('test_data.txt', 'r'):
            pass
    except FileNotFoundError:
        create_test_data()
    print("Генерация ключей RSA...")
    public_key, private_key, p, q = generate_rsa_keys(1024)
    save_to_file('public_key.txt', f"{public_key[0]},{public_key[1]}")
    save_to_file('private_key.txt', f"{private_key[0]},{private_key[1]}")

    print(f"Открытый ключ сохранен в public_key.txt")
    print(f"Закрытый ключ сохранен в private_key.txt")
    print(f"n = {public_key[1]}")
    with open('test_data.txt', 'r') as f:
        test_messages = [line.strip() for line in f.readlines()]

    print(f"\nЗагружено {len(test_messages)} тестовых сообщений:")
    for i, msg in enumerate(test_messages, 1):
        print(f"{i}: {msg}")
    while True:
        try:
            choice = int(input("\nВведите номер тестового сообщения (1-10) или 0 для выхода: "))
            if choice == 0:
                break
            if choice < 1 or choice > 10:
                print("Ошибка: введите число от 1 до 10")
                continue

            message = int(test_messages[choice - 1])
            print(f"\nТест сообщения {choice}")
            print(f"Исходное сообщение: {message}")

            encrypted = mod_exp(message, public_key[0], public_key[1])
            print(f"Зашифрованное: {encrypted}")
            save_to_file('encrypted.txt', encrypted)

            decrypted = mod_exp(encrypted, private_key[0], private_key[1])
            print(f"Расшифрованное: {decrypted}")

            signature = mod_exp(message, private_key[0], private_key[1])
            print(f"Цифровая подпись: {signature}")

            verified = mod_exp(signature, public_key[0], public_key[1])
            print(f"Проверка подписи: {verified}")

            if message == decrypted == verified:
                print("Все операции выполнены успешно!")
            else:
                print("Ошибка в работе алгоритма!")

        except ValueError:
            print("Ошибка: введите целое число")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()