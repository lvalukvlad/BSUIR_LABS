from cipher import ScytaleCipher, EnhancedScytale
from security_analysis import demonstrate_security_analysis

def demo_basic():
    print("ДЕМОНСТРАЦИЯ ШИФРА СКИТАЛА")
    print("=" * 50)

    cipher = ScytaleCipher()
    original_text = "прилетаюседьмогоутра"
    diameter = 5

    print(f"Оригинальный текст: {original_text}")
    print(f"Ключ (диаметр): {diameter}")

    encrypted, orig_len = cipher.encrypt(original_text, diameter)
    print(f"Зашифрованный текст: {encrypted}")

    decrypted = cipher.decrypt(encrypted, diameter, orig_len)
    print(f"Расшифрованный текст: {decrypted}")

    print("\nАтака полным перебором:")
    results = cipher.brute_force_attack(encrypted, original_text, max_diameter=10)
    cipher.visualize_results(results)

def demo_enhanced():
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ УСОВЕРШЕНСТВОВАННОГО ШИФРА")
    print("=" * 50)

    enhanced = EnhancedScytale()
    text = "секретноесообщение"
    diameter = 5
    key = "mysecretkey"

    encrypted, orig_len = enhanced.enhanced_encrypt(text, diameter, key, shift=2, reverse=True)
    print(f"Зашифрованный (enhanced): {encrypted}")

    decrypted = enhanced.enhanced_decrypt(encrypted, diameter, key, orig_len, shift=2, reverse=True)
    print(f"Расшифрованный: {decrypted}")

    diameters = [3, 5, 4]
    keys = ["key1", "key2", "key3"]
    multi_enc, orig_len, _ = enhanced.multi_layer_encrypt(text, diameters, keys, shifts=[1, 2, 0], reverses=[False, True, False])
    print(f"Многослойное шифрование: {multi_enc}")

    multi_dec = enhanced.multi_layer_decrypt(multi_enc, diameters, keys, orig_len, shifts=[1, 2, 0], reverses=[False, True, False])
    print(f"Многослойное расшифрование: {multi_dec}")

def demo_security_analysis():
    print("\n" + "=" * 50)
    print("ДЕМОНСТРАЦИЯ АНАЛИЗА СТОЙКОСТИ")
    print("=" * 50)
    demonstrate_security_analysis()

if __name__ == "__main__":
    demo_basic()
    demo_enhanced()
    demo_security_analysis()