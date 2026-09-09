#include <iostream>
#include <vector>
#include <thread>
#include <cmath>
#include <fstream>
#include <mutex>
#include <unistd.h> // Для getpid()

#define PI 3.14159265358979323846

std::mutex mtx; // Для синхронизации вывода

// Структура данных для передачи в потоки
struct ThreadData {
    int index;
    int N;
    int n_terms;
    double result;
};

// Функция для расчета значения ряда Тейлора
void calculate_taylor_series(ThreadData& data) {
    double x = 2 * PI * data.index / data.N;
    double term = x; // Первый член ряда
    double sum = term; // Начальное значение суммы

    // Вычисление ряда Тейлора
    for (int i = 1; i < data.n_terms; ++i) {
        term *= -x * x / ((2 * i) * (2 * i + 1));
        sum += term;
    }

    data.result = sum;

    // Блокируем вывод для синхронизации
    std::lock_guard<std::mutex> lock(mtx);
    std::cout << "Thread " << std::this_thread::get_id() 
              << " (pid: " << getpid() << "): y[" << data.index 
              << "] = " << sum << std::endl;
}

int main() {
    int K, N, n_terms;

    // Ввод данных
    std::cout << "Enter K (number of points): ";
    std::cin >> K;
    std::cout << "Enter N (period divisor): ";
    std::cin >> N;
    std::cout << "Enter n (number of Taylor series terms): ";
    std::cin >> n_terms;

    std::vector<std::thread> threads;
    std::vector<ThreadData> thread_data(K);
    std::vector<double> y(K);

    // Создаем потоки для вычисления y[i]
    for (int i = 0; i < K; ++i) {
        thread_data[i] = {i, N, n_terms, 0.0};
        threads.emplace_back(calculate_taylor_series, std::ref(thread_data[i]));
    }

    // Ожидаем завершения потоков
    for (auto& th : threads) {
        th.join();
    }

    // Суммируем результаты и записываем в файл
    double sum = 0.0;
    std::ofstream file("results.txt");
    if (!file) {
        std::cerr << "Failed to open file for writing.\n";
        return 1;
    }

    file << "Index\tValue\n";
    for (int i = 0; i < K; ++i) {
        y[i] = thread_data[i].result;
        file << i << "\t" << y[i] << "\n";
        sum += y[i];
    }
    file << "Sum of all y[i]: " << sum << "\n";
    file.close();

    std::cout << "Results saved to 'results.txt'\n";

    return 0;
}
