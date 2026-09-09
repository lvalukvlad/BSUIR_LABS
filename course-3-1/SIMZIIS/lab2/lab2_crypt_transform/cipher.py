import math
import string
import random
import hashlib


class ScytaleCipher:
    def __init__(self):
        self.alphabet_ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        self.alphabet_en = string.ascii_lowercase
        self.language = 'ru'

    def set_language(self, language):
        if language.lower() in ['ru', 'russian']:
            self.language = 'ru'
        elif language.lower() in ['en', 'english']:
            self.language = 'en'

    def clean_text(self, text):
        alphabet = self.alphabet_ru if self.language == 'ru' else self.alphabet_en
        return ''.join(char.lower() for char in text if char.lower() in alphabet)

    def encrypt(self, text, diameter):
        if not text:
            return "", 0

        clean_text = self.clean_text(text)
        original_len = len(clean_text)
        if original_len == 0:
            return "", 0

        rows = math.ceil(original_len / diameter)
        needed_len = rows * diameter
        padding_char = clean_text[-1] if clean_text else ('а' if self.language == 'ru' else 'a')
        padding = padding_char * (needed_len - original_len)
        padded_text = clean_text + padding

        encrypted = []
        for col in range(diameter):
            for row in range(rows):
                index = row * diameter + col
                encrypted.append(padded_text[index])

        return ''.join(encrypted), original_len

    def decrypt(self, ciphertext, diameter, original_len=None):
        if not ciphertext:
            return ""

        rows = math.ceil(len(ciphertext) / diameter)
        full_length = rows * diameter

        if len(ciphertext) < full_length:
            padding_char = ciphertext[-1] if ciphertext else ('а' if self.language == 'ru' else 'a')
            ciphertext = ciphertext + padding_char * (full_length - len(ciphertext))

        decrypted = [''] * full_length

        for col in range(diameter):
            for row in range(rows):
                cipher_index = col * rows + row
                text_index = row * diameter + col
                if cipher_index < len(ciphertext) and text_index < full_length:
                    decrypted[text_index] = ciphertext[cipher_index]

        result = ''.join(decrypted)
        if original_len is not None:
            return result[:original_len]
        return result

    def brute_force_attack(self, ciphertext, original_text=None, original_len=None, max_diameter=20):
        clean_ciphertext = self.clean_text(ciphertext)
        if not clean_ciphertext:
            return []

        len_ct = len(clean_ciphertext)
        results = []

        print(f"Перебираем ключи от 1 до {max_diameter}...")
        print(f"Длина текста: {len_ct} символов")

        for diameter in range(1, min(max_diameter + 1, len_ct + 1)):
            rows = math.ceil(len_ct / diameter)
            full_length = rows * diameter

            if len_ct < full_length:
                padding_char = clean_ciphertext[-1] if clean_ciphertext else ('а' if self.language == 'ru' else 'a')
                padded_ciphertext = clean_ciphertext + padding_char * (full_length - len_ct)
            else:
                padded_ciphertext = clean_ciphertext

            try:
                decrypted = self.decrypt(padded_ciphertext, diameter)
                similarity = 0

                if original_text:
                    clean_original = self.clean_text(original_text)
                    orig_len = len(clean_original)
                    decrypted_for_comparison = decrypted[:orig_len] if len(decrypted) >= orig_len else decrypted
                    if len(decrypted_for_comparison) == orig_len:
                        similarity = self._calculate_similarity(decrypted_for_comparison, clean_original)

                results.append((diameter, decrypted, similarity, full_length))

            except Exception as e:
                continue

        return results

    def _calculate_similarity(self, text1, text2):
        if len(text1) != len(text2):
            return 0
        matches = sum(1 for i in range(len(text1)) if text1[i] == text2[i])
        return matches / len(text1) if len(text1) > 0 else 0

    def visualize_results(self, results):
        print("\n" + "=" * 80)
        print("РЕЗУЛЬТАТЫ АТАКИ ПОЛНЫМ ПЕРЕБОРОМ")
        print("=" * 80)

        if not results:
            print("Ошибка: шифртекст не содержит букв алфавита!")
            return

        if any(similarity > 0 for _, _, similarity, _ in results):
            results.sort(key=lambda x: x[2], reverse=True)
            print("Наиболее вероятные ключи (с учётом схожести с оригиналом):")
        else:
            print("Все варианты расшифрования (визуальная проверка):")

        print(f"Всего результатов: {len(results)}")

        for diameter, text, similarity, full_length in results:
            print(f"\nКлюч (диаметр): {diameter}")
            print(f"Размер матрицы: {full_length // diameter}×{diameter}")
            if similarity > 0:
                print(f"Схожесть с оригиналом: {similarity:.2%}")
            print(f"Текст (длина {len(text)}): {text[:100]}{'...' if len(text) > 100 else ''}")


class EnhancedScytale:
    def __init__(self):
        self.alphabet_ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        self.alphabet_en = string.ascii_lowercase
        self.language = 'ru'

    def set_language(self, language):
        if language.lower() in ['ru', 'russian']:
            self.language = 'ru'
        elif language.lower() in ['en', 'english']:
            self.language = 'en'

    def clean_text(self, text):
        alphabet = self.alphabet_ru if self.language == 'ru' else self.alphabet_en
        return ''.join(char.lower() for char in text if char.lower() in alphabet)

    def _get_permutation(self, key, n):
        seed = int(hashlib.sha256(key.encode()).hexdigest(), 16) % (2 ** 32)
        random.seed(seed)
        perm = list(range(n))
        random.shuffle(perm)
        return perm

    def enhanced_encrypt(self, text, diameter, key, shift=0, reverse=False):
        if not text:
            return "", 0

        clean_text = self.clean_text(text)
        original_len = len(clean_text)
        if original_len == 0:
            return "", 0

        rows = math.ceil(original_len / diameter)
        needed_len = rows * diameter
        padding_char = clean_text[-1] if clean_text else ('а' if self.language == 'ru' else 'a')
        padded_text = clean_text + padding_char * (needed_len - original_len)

        shifted_text = padded_text[shift:] + padded_text[:shift]

        perm = self._get_permutation(key, diameter)
        if reverse:
            perm = list(reversed(perm))

        encrypted = []
        for j in perm:
            for row in range(rows):
                index = row * diameter + j
                encrypted.append(shifted_text[index])

        return ''.join(encrypted), original_len

    def enhanced_decrypt(self, ciphertext, diameter, key, original_len, shift=0, reverse=False):
        if not ciphertext:
            return ""

        clean_ciphertext = self.clean_text(ciphertext)
        rows = math.ceil(len(clean_ciphertext) / diameter)
        full_length = rows * diameter

        if len(clean_ciphertext) < full_length:
            padding_char = clean_ciphertext[-1] if clean_ciphertext else ('а' if self.language == 'ru' else 'a')
            clean_ciphertext = clean_ciphertext + padding_char * (full_length - len(clean_ciphertext))

        perm = self._get_permutation(key, diameter)
        if reverse:
            perm = list(reversed(perm))

        inv_perm = [0] * diameter
        for i, p in enumerate(perm):
            inv_perm[p] = i

        decrypted_shifted = [''] * full_length
        idx = 0
        for j in perm:
            for row in range(rows):
                if idx < len(clean_ciphertext):
                    text_index = row * diameter + j
                    if text_index < full_length:
                        decrypted_shifted[text_index] = clean_ciphertext[idx]
                    idx += 1

        shifted_text = ''.join(decrypted_shifted)
        unshifted = shifted_text[-shift:] + shifted_text[:-shift]

        return unshifted[:original_len]

    def multi_layer_encrypt(self, text, diameters, keys, shifts=None, reverses=None):
        if shifts is None:
            shifts = [0] * len(diameters)
        if reverses is None:
            reverses = [False] * len(diameters)

        encrypted = text
        original_len = len(self.clean_text(text))
        lengths = [original_len]  # Сохраняем длины для каждого слоя

        for i, diameter in enumerate(diameters):
            encrypted, layer_len = self.enhanced_encrypt(encrypted, diameter, keys[i], shifts[i], reverses[i])
            lengths.append(layer_len)

        return encrypted, original_len, lengths[1:]

    def multi_layer_decrypt(self, ciphertext, diameters, keys, original_len, shifts=None, reverses=None):
        if shifts is None:
            shifts = [0] * len(diameters)
        if reverses is None:
            reverses = [False] * len(diameters)

        decrypted = self.clean_text(ciphertext)

        for i in range(len(diameters) - 1, -1, -1):
            decrypted = self.enhanced_decrypt(decrypted, diameters[i], keys[i], original_len, shifts[i], reverses[i])

        return decrypted[:original_len]