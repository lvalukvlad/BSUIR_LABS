from cipher import ScytaleCipher
from security_analysis import ScytaleSecurityAnalysis

def main():
    cipher = ScytaleCipher()

    while True:
        print("\n" + "=" * 50)
        print("ШИФР СКИТАЛА")
        print("=" * 50)
        print("1. Зашифровать текст")
        print("2. Расшифровать текст")
        print("3. Атака полным перебором")
        print("4. Оценка криптографической стойкости")
        print("5. Демонстрация работы")
        print(f"6. Сменить язык (текущий: {'русский' if cipher.language == 'ru' else 'английский'})")
        print("7. Выход")

        choice = input("\nВыберите действие (1-7): ").strip()

        if choice == '1':
            text = input("Введите текст для шифрования: ")
            try:
                diameter = int(input("Введите ключ: "))
                if diameter <= 0:
                    raise ValueError("Ключ должен быть положительным!")
                encrypted, orig_len = cipher.encrypt(text, diameter)
                print(f"\nЗашифрованный текст: {encrypted}")
                print(f"Оригинальная длина: {orig_len}")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == '2':
            ciphertext = input("Введите текст для расшифрования: ")
            try:
                diameter = int(input("Введите ключ: "))
                if diameter <= 0:
                    raise ValueError("Ключ должен быть положительным!")
                orig_len_str = input("Введите оригинальную длину текста (если известна): ")
                orig_len = int(orig_len_str) if orig_len_str else None
                clean_ciphertext = cipher.clean_text(ciphertext)
                if not clean_ciphertext:
                    print("Ошибка: шифртекст не содержит букв алфавита!")
                    continue
                if clean_ciphertext != ciphertext:
                    print(f"Очищенный шифртекст: {clean_ciphertext}")
                decrypted = cipher.decrypt(clean_ciphertext, diameter, orig_len)
                print(f"\nРасшифрованный текст: {decrypted}")
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == '3':
            ciphertext = input("Введите текст для атаки: ")
            clean_ciphertext = cipher.clean_text(ciphertext)
            if not clean_ciphertext:
                print("Ошибка: шифртекст не содержит букв алфавита!")
                continue
            if clean_ciphertext != ciphertext:
                print(f"Очищенный шифртекст: {clean_ciphertext}")

            has_original = input("Есть ли у вас оригинальный текст для сравнения? (y/n): ").lower() == 'y'
            original_text = None
            original_len = None

            if has_original:
                original_text = input("Введите оригинальный текст: ")
            else:
                orig_len_str = input("Введите оригинальную длину текста (если известна): ")
                original_len = int(orig_len_str) if orig_len_str else None

            try:
                max_diameter = int(input("Максимальный ключ для перебора: ") or "20")
                if max_diameter <= 0:
                    raise ValueError("Максимальный ключ должен быть положительным!")
                results = cipher.brute_force_attack(clean_ciphertext, original_text, original_len, max_diameter)
                cipher.visualize_results(results)
            except ValueError as e:
                print(f"Ошибка: {e}")

        elif choice == '4':
            print("\nЗапуск анализа криптографической стойкости...")
            analyzer = ScytaleSecurityAnalysis()
            analyzer.full_security_assessment()

        elif choice == '5':
            from demo import demo_basic, demo_enhanced, demo_security_analysis
            print("\nЗапуск демонстрации...")
            demo_basic()
            demo_enhanced()
            demo_security_analysis()

        elif choice == '6':
            lang = input("Выберите язык (ru/en): ").lower()
            if lang not in ['ru', 'en', 'russian', 'english']:
                print("Ошибка: выберите 'ru' или 'en'!")
                continue
            cipher.set_language(lang)
            print(f"Язык изменен на: {'русский' if cipher.language == 'ru' else 'английский'}")

        elif choice == '7':
            print("Выход из программы...")
            break

        else:
            print("Неверный выбор! Попробуйте снова.")

if __name__ == "__main__":
    main()