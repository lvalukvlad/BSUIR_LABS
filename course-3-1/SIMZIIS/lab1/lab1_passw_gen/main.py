import random
import time
import string
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import itertools


class PasswordGenerator:
    def __init__(self):
        self.alphabet = string.ascii_lowercase
        self.measured_speed = None

    def generate_random_string(self, length):
        random.seed(int(datetime.now().timestamp() * 1000))
        result = []
        for _ in range(length):
            random_index = random.randint(0, len(self.alphabet) - 1)
            result.append(self.alphabet[random_index])
        return ''.join(result)

    def check_uniformity_distribution(self, s):
        freq = {char: 0 for char in self.alphabet}

        for char in s:
            if char in freq:
                freq[char] += 1

        plt.figure(figsize=(14, 6))
        chars = list(self.alphabet)
        counts = [freq[char] for char in chars]
        total_chars = len(s)

        # ИСПРАВЛЕНИЕ: Правильное вычисление процентов
        if total_chars > 0:
            percentages = [count / total_chars * 100 for count in counts]
            expected_percentage = 100 / len(self.alphabet)
        else:
            percentages = [0] * len(chars)
            expected_percentage = 0

        x_pos = np.arange(len(chars))
        bars = plt.bar(x_pos, percentages, alpha=0.7, color='skyblue', edgecolor='black')

        plt.axhline(y=expected_percentage, color='red', linestyle='--', linewidth=2,
                    label=f'Ожидаемая частота: {expected_percentage:.1f}%')
        plt.title('ВИЗУАЛИЗАЦИЯ ЧАСТОТНОГО РАСПРЕДЕЛЕНИЯ СИМВОЛОВ', fontsize=16, pad=20)
        plt.xlabel('Символы алфавита', fontsize=12)
        plt.ylabel('Частота встречаемости (%)', fontsize=12)  # ИСПРАВЛЕНИЕ: Добавлен %
        plt.xticks(x_pos, chars)
        plt.grid(axis='y', alpha=0.3)
        plt.legend()

        # ИСПРАВЛЕНИЕ: Исправлена переменная (count → percentage)
        for bar, percentage in zip(bars, percentages):
            if percentage > 0:
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                         f'{percentage:.1f}%', ha='center', va='bottom', fontsize=9)  # ИСПРАВЛЕНИЕ: форматирование
        plt.tight_layout()
        plt.savefig('distribution_plot.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("\n" + "=" * 60)
        print("АНАЛИЗ РАВНОМЕРНОСТИ РАСПРЕДЕЛЕНИЯ")
        print("=" * 60)
        total_deviation = 0
        valid_chars = 0  # ИСПРАВЛЕНИЕ: Счетчик валидных символов

        # ИСПРАВЛЕНИЕ: Правильный расчет отклонений
        expected = expected_percentage  # Ожидаемый процент
        print("Символ | Абсолютная | Относительная | Отклонение")
        print("       |  частота   |  частота (%)  |   от эталона")
        print("-------|------------|---------------|------------")

        for char in sorted(chars):
            count = freq[char]
            if total_chars > 0:
                relative_percentage = (count / total_chars) * 100
                # ИСПРАВЛЕНИЕ: Отклонение от ожидаемого процента
                deviation = abs(relative_percentage - expected)
            else:
                relative_percentage = 0
                deviation = 0

            if expected > 0:  # ИСПРАВЛЕНИЕ: Избегаем деления на ноль
                total_deviation += deviation
                valid_chars += 1

            status = "✓" if deviation < 2 else "⚠" if deviation < 5 else "✗"
            print(f"{char:6} | {count:10} | {relative_percentage:12.2f}% | {deviation:9.2f}% {status}")

        # ИСПРАВЛЕНИЕ: Правильное вычисление среднего отклонения
        if valid_chars > 0:
            avg_deviation = total_deviation / valid_chars
            print("=" * 60)
            print(f"Среднее отклонение от равномерного распределения: {avg_deviation:.2f}%")

            if avg_deviation < 2:
                print("✅ Распределение близко к равномерному")
            elif avg_deviation < 5:
                print("⚠️  Распределение умеренно неравномерное")
            else:
                print("❌ Распределение сильно неравномерно")
        else:
            print("Невозможно вычислить отклонение")

        return freq

    def measure_brute_force_time(self, password):
        start_time = time.time()
        attempts = 0

        for guess in itertools.product(self.alphabet, repeat=len(password)):
            attempts += 1
            if ''.join(guess) == password:
                break
        return time.time() - start_time, attempts

    def calculate_average_time_for_length(self, length, samples=3):
        times = []

        for _ in range(samples):
            password = self.generate_random_string(length)
            time_taken, attempts = self.measure_brute_force_time(password)
            times.append(time_taken)
        return sum(times) / len(times)

    def calculate_average_time_from_string(self, generated_string, sample_size=5):
        print(f"\n" + "=" * 70)
        print("ВЫЧИСЛЕНИЕ СРЕДНЕГО ВРЕМЕНИ ПОДБОРА ПАРОЛЕЙ ИЗ СТРОКИ")
        print("=" * 70)
        times = []
        attempts_list = []
        test_passwords = []
        n = len(generated_string)

        for i in range(sample_size):
            start_pos = i % max(1, n - 3)
            pwd_length = min(4, n - start_pos)
            test_password = generated_string[start_pos:start_pos + pwd_length]
            test_passwords.append(test_password)

        print("Тестируемые пароли:")
        for i, pwd in enumerate(test_passwords, 1):
            print(f"  {i}. '{pwd}' (длина: {len(pwd)})")

        for i, password in enumerate(test_passwords, 1):
            print(f"\n--- Тест {i}/{sample_size}: пароль '{password}' ---")
            time_taken, attempts = self.measure_brute_force_time(password)
            times.append(time_taken)
            attempts_list.append(attempts)
            print(f"   Попыток: {attempts:,}")
            print(f"   Время: {time_taken:.6f} сек")
        avg_time = sum(times) / len(times)
        avg_attempts = sum(attempts_list) / len(attempts_list)
        print("\n" + "=" * 70)
        print("РЕЗУЛЬТАТЫ: СРЕДНЕЕ ВРЕМЯ ПОДБОРА")
        print("=" * 70)
        print(f"Количество тестов: {sample_size}")
        print(f"Среднее время подбора: {avg_time:.6f} секунд")
        print(f"Среднее количество попыток: {avg_attempts:,.0f}")
        print(f"Минимальное время: {min(times):.6f} сек")
        print(f"Максимальное время: {max(times):.6f} сек")
        return avg_time, avg_attempts

    def build_time_vs_length_graph(self, max_length=6):
        print("\n" + "=" * 70)
        print("ПОСТРОЕНИЕ ГРАФИКА: СРЕДНЕЕ ВРЕМЯ ПОДБОРА vs ДЛИНА ПАРОЛЯ")
        print("=" * 70)
        lengths = []
        avg_times = []

        for length in range(1, max_length + 1):
            print(f"Измерение для длины {length}...")
            avg_time = self.calculate_average_time_for_length(length)
            lengths.append(length)
            avg_times.append(avg_time)
            print(f"Длина {length}: среднее время = {avg_time:.6f} сек")
        self.create_time_graph(lengths, avg_times)
        return lengths, avg_times

    def create_time_graph(self, lengths, avg_times):
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        plt.plot(lengths, avg_times, 'o-', linewidth=3, markersize=8,
                 color='blue', markerfacecolor='red')
        plt.title('ЗАВИСИМОСТЬ СРЕДНЕГО ВРЕМЕНИ ПОДБОРА ОТ ДЛИНЫ ПАРОЛЯ', fontsize=16)
        plt.xlabel('Длина пароля (символов)', fontsize=12)
        plt.ylabel('Среднее время подбора (секунды)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(lengths)

        for i, (length, time_val) in enumerate(zip(lengths, avg_times)):
            plt.annotate(f'{time_val:.6f} сек', (length, time_val),
                         textcoords="offset points", xytext=(0, 10),
                         ha='center', fontsize=9, bbox=dict(boxstyle="round,pad=0.3",
                                                            facecolor="yellow", alpha=0.7))
        plt.subplot(2, 1, 2)
        plt.plot(lengths, avg_times, 's-', linewidth=2, markersize=6,
                 color='green', markerfacecolor='orange')
        plt.yscale('log')
        plt.title('ЛОГАРИФМИЧЕСКАЯ ШКАЛА (экспоненциальный рост)', fontsize=14)
        plt.xlabel('Длина пароля (символов)', fontsize=12)
        plt.ylabel('Среднее время (логарифмическая шкала)', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xticks(lengths)
        plt.tight_layout()
        plt.savefig('time_vs_length_graph.png', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"\n✅ График сохранен в файл: time_vs_length_graph.png")

    def measure_attack_speed(self):
        print("Измерение скорости перебора...")
        test_password = "abc"
        start_time = time.time()
        attempts = 0

        for guess in itertools.product(self.alphabet, repeat=len(test_password)):
            attempts += 1
            if ''.join(guess) == test_password:
                break
        elapsed_time = time.time() - start_time
        self.measured_speed = attempts / elapsed_time
        print(f"⚡ Скорость перебора: {self.measured_speed:,.0f} паролей/сек")
        return self.measured_speed

    def get_detailed_recommendations(self):
        if self.measured_speed is None:
            self.measure_attack_speed()
        recommendations = [
            "=" * 80,
            "ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ ПО ВЫБОРУ ПАРОЛЯ",
            "=" * 80,
            "",
            "1. АНАЛИЗ АЛФАВИТА (латиница строчные)",
            "   " + "-" * 50,
            f"   • Текущий алфавит: {len(self.alphabet)} символов",
            "   • Слабый уровень защиты ❌",
            "   • Рекомендуется расширить алфавит:",
            "     - Заглавные буквы",
            "     - Цифры",
            "     - Спецсимволы",
            "",
            "2. ЦЕННОСТЬ ИНФОРМАЦИИ",
            "   " + "-" * 50,
            "   • Социальные сети: 12+ символов",
            "   • Email-аккаунты: 14+ символов",
            "   • Банковские системы: 16+ символов",
            "   • Криптокошельки: 20+ символов",
            "",
            "3. ПРОИЗВОДИТЕЛЬНОСТЬ АТАКУЮЩЕГО",
            "   " + "-" * 50,
            f"   • Ваш компьютер: {self.measured_speed:,.0f} паролей/сек",
            "   • Обычный ПК: 1-10 млн/сек",
            "   • GPU-кластер: до 1 млрд/сек",
            "   • Спецоборудование: до 100 млрд/сек",
            "",
            "4. ВРЕМЯ АТАКИ И РЕКОМЕНДАЦИИ",
            "   " + "-" * 50,
        ]

        for length in [8, 12, 16]:
            combinations = len(self.alphabet) ** length
            time_seconds = combinations / self.measured_speed

            if time_seconds < 60:
                time_str = f"{time_seconds:.1f} сек"
            elif time_seconds < 3600:
                time_str = f"{time_seconds / 60:.1f} мин"
            elif time_seconds < 86400:
                time_str = f"{time_seconds / 3600:.1f} час"
            else:
                time_str = f"{time_seconds / 86400:.1f} дней"

            recommendations.append(f"   • {length} символов: {time_str} ({combinations:,} комбинаций)")
        recommendations.extend([
            "",
            "5. ВЫВОДЫ И РЕКОМЕНДАЦИИ",
            "   " + "-" * 50,
            "   • Минимальная длина: 12 символов",
            "   • Используйте разные регистры букв",
            "   • Добавляйте цифры и специальные символы",
            "   • Включите двухфакторную аутентификацию",
            "   • Используйте менеджер паролей",
            "   • Не повторяйте пароли на разных сервисах",
            "",
            "=" * 80,
        ])
        return "\n".join(recommendations)


def main():
    print("=" * 80)
    print("ГЕНЕРАЦИЯ ПАРОЛЕЙ")
    print("Латиница, строчные буквы")
    print("=" * 80)
    generator = PasswordGenerator()

    try:
        length = int(input("Введите длину строки для генерации: "))
        if length <= 0:
            print("Ошибка: длина должна быть > 0")
            return

        print(f"\nГенерация строки длиной {length} символов...")
        generated_string = generator.generate_random_string(length)
        print(f"✅ Сгенерировано: '{generated_string}'")
        print("\n" + "=" * 60)
        print("ПРОВЕРКА РАВНОМЕРНОСТИ РАСПРЕДЕЛЕНИЯ СИМВОЛОВ")
        print("=" * 60)
        generator.check_uniformity_distribution(generated_string)
        print("✅ График распределения сохранен в distribution_plot.png")

        avg_time, avg_attempts = generator.calculate_average_time_from_string(generated_string)

        if length >= 3:
            lengths, avg_times = generator.build_time_vs_length_graph(
                max_length=min(6, length)
            )

        print("\n" + "=" * 80)
        print("ПРАКТИЧЕСКИЕ РЕКОМЕНДАЦИИ")
        print("=" * 80)
        print(generator.get_detailed_recommendations())
        print(f"Среднее время подбора: {avg_time:.6f} сек")

    except ValueError:
        print("Ошибка: введите целое число!")
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()