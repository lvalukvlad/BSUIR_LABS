import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq


class FFTAnalyzer:
    def __init__(self, signal_type='sin', frequency=5, duration=1.0, sampling_rate=1000):
        self.signal_type = signal_type.lower()
        self.frequency = frequency
        self.duration = duration
        self.sampling_rate = sampling_rate

        if self.signal_type not in ['sin', 'cos']:
            raise ValueError("Тип сигнала должен быть 'sin' или 'cos'")

    def generate_signal(self):
        t = np.linspace(0, self.duration, int(self.sampling_rate * self.duration), endpoint=False)

        if self.signal_type == 'sin':
            signal = np.sin(2 * np.pi * self.frequency * t)
        else:
            signal = np.cos(2 * np.pi * self.frequency * t)

        return t, signal

    def perform_fft(self, signal):
        fft_result = fft(signal)

        amplitudes = np.abs(fft_result) / len(signal) * 2
        amplitudes[0] /= 2

        freqs = fftfreq(len(signal), 1 / self.sampling_rate)

        positive_freq_mask = freqs >= 0
        positive_freqs = freqs[positive_freq_mask]
        positive_amplitudes = amplitudes[positive_freq_mask]

        return positive_freqs, positive_amplitudes, fft_result

    def find_peak_frequency(self, freqs, amplitudes):
        peak_idx = np.argmax(amplitudes)
        return freqs[peak_idx], amplitudes[peak_idx]

    def analyze(self):
        t, signal = self.generate_signal()

        freqs, amplitudes, fft_result = self.perform_fft(signal)

        peak_freq, peak_amp = self.find_peak_frequency(freqs, amplitudes)

        return t, signal, freqs, amplitudes, peak_freq, peak_amp

    def print_results(self, peak_freq, peak_amp):
        print("=" * 60)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА ФУРЬЕ")
        print("=" * 60)
        print(f"Тип сигнала: {self.signal_type}(2π*{self.frequency}*t)")
        print(f"Длительность: {self.duration} с")
        print(f"Частота дискретизации: {self.sampling_rate} Гц")
        print(f"Количество отсчетов: {int(self.sampling_rate * self.duration)}")
        print(f"Обнаруженная частота: {peak_freq:.6f} Гц")
        print(f"Ожидаемая частота: {self.frequency:.6f} Гц")
        print(f"Погрешность частоты: {abs(peak_freq - self.frequency):.6f} Гц")
        print(f"Амплитуда пика: {peak_amp:.6f}")
        print(f"Ожидаемая амплитуда: {1.0:.6f}")
        print(f"Погрешность амплитуды: {abs(peak_amp - 1.0):.6f}")

        frequency_error = abs(peak_freq - self.frequency)
        amplitude_error = abs(peak_amp - 1.0)

        print("\nПРОВЕРКА ТОЧНОСТИ:")
        if frequency_error < 0.1 and amplitude_error < 0.05:
            print("✓ Преобразование Фурье работает корректно!")
            print("✓ Частота определена точно")
            print("✓ Амплитуда определена точно")
        else:
            print("⚠ Возможны неточности в определении параметров")
            if frequency_error >= 0.1:
                print(f"⚠ Погрешность частоты ({frequency_error:.3f} Гц) выше допустимой")
            if amplitude_error >= 0.05:
                print(f"⚠ Погрешность амплитуды ({amplitude_error:.3f}) выше допустимой")

    def plot_results(self, t, signal, freqs, amplitudes, peak_freq, peak_amp):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        ax1.plot(t, signal)
        ax1.set_title(f'Исходный сигнал: {self.signal_type}(2π*{self.frequency}*t)')
        ax1.set_xlabel('Время [с]')
        ax1.set_ylabel('Амплитуда')
        ax1.grid(True)

        ax2.plot(freqs, amplitudes)
        ax2.set_title('Спектр Фурье')
        ax2.set_xlabel('Частота [Гц]')
        ax2.set_ylabel('Амплитуда')
        ax2.grid(True)
        ax2.set_xlim(0, max(freqs))

        ax2.axvline(x=peak_freq, color='r', linestyle='--',
                    label=f'Пик: {peak_freq:.2f} Гц, амплитуда: {peak_amp:.4f}')
        ax2.legend()

        plt.tight_layout()
        plt.show()


def example_sin():
    print("АНАЛИЗ СИНУСОИДАЛЬНОГО СИГНАЛА")
    print("-" * 40)

    analyzer = FFTAnalyzer(signal_type='sin', frequency=5, duration=2.0, sampling_rate=1000)

    t, signal, freqs, amplitudes, peak_freq, peak_amp = analyzer.analyze()

    analyzer.print_results(peak_freq, peak_amp)

    analyzer.plot_results(t, signal, freqs, amplitudes, peak_freq, peak_amp)


def example_cos():
    print("\n" + "=" * 60)
    print("АНАЛИЗ КОСИНУСОИДАЛЬНОГО СИГНАЛА")
    print("-" * 40)

    analyzer = FFTAnalyzer(signal_type='cos', frequency=10, duration=1.5, sampling_rate=2000)

    t, signal, freqs, amplitudes, peak_freq, peak_amp = analyzer.analyze()

    analyzer.print_results(peak_freq, peak_amp)

    analyzer.plot_results(t, signal, freqs, amplitudes, peak_freq, peak_amp)


def custom_analysis(signal_type, frequency, duration=1.0, sampling_rate=1000):
    print(f"\n" + "=" * 60)
    print(f"ПОЛЬЗОВАТЕЛЬСКИЙ АНАЛИЗ: {signal_type.upper()}({frequency} Гц)")
    print("-" * 40)

    try:
        analyzer = FFTAnalyzer(signal_type=signal_type, frequency=frequency,
                               duration=duration, sampling_rate=sampling_rate)

        t, signal, freqs, amplitudes, peak_freq, peak_amp = analyzer.analyze()
        analyzer.print_results(peak_freq, peak_amp)
        analyzer.plot_results(t, signal, freqs, amplitudes, peak_freq, peak_amp)

    except ValueError as e:
        print(f"Ошибка: {e}")


def interactive_menu():
    print("БЫСТРОЕ ПРЕОБРАЗОВАНИЕ ФУРЬЕ - МЕНЮ")
    print("=" * 40)
    print("1. Анализ синусоиды (5 Гц)")
    print("2. Анализ косинусоиды (10 Гц)")
    print("3. Пользовательский анализ")
    print("4. Все примеры")
    print("0. Выход")

    choice = input("\nВыберите опцию (0-4): ")

    if choice == '1':
        example_sin()
    elif choice == '2':
        example_cos()
    elif choice == '3':
        signal_type = input("Введите тип сигнала (sin/cos): ").strip().lower()
        frequency = float(input("Введите частоту (Гц): "))
        duration = float(input("Введите длительность (сек) [1.0]: ") or "1.0")
        sampling_rate = int(input("Введите частоту дискретизации (Гц) [1000]: ") or "1000")
        custom_analysis(signal_type, frequency, duration, sampling_rate)
    elif choice == '4':
        example_sin()
        example_cos()
    elif choice == '0':
        print("Выход из программы")
        return False
    else:
        print("Неверный выбор. Попробуйте снова.")

    return True


if __name__ == "__main__":
    print("Демонстрация быстрого преобразования Фурье")

    # Можно раскомментировать нужные варианты:

    # Вариант 1: Запуск конкретного примера
    # example_sin()
    # example_cos()

    # Вариант 2: Пользовательский анализ
    # custom_analysis('sin', 7, duration=2.0, sampling_rate=1500)

    # Вариант 3: Интерактивное меню
    while interactive_menu():
        pass

    # Вариант 4: Простой тест
    # analyzer = FFTAnalyzer(signal_type='sin', frequency=5)
    # t, signal, freqs, amplitudes, peak_freq, peak_amp = analyzer.analyze()
    # analyzer.print_results(peak_freq, peak_amp)
    # analyzer.plot_results(t, signal, freqs, amplitudes, peak_freq, peak_amp)