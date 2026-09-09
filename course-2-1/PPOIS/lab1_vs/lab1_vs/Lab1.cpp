#include <iostream>
#include "BigInteger.h"
#include <string>

int main() {
    setlocale(0, "");
    std::string input_num1;
    std::cout << "Введите первое длинное целое число:\t";
    std::getline(std::cin, input_num1);
    BigInteger num1(input_num1);
    std::cout << "Вы ввели первое число:\t" << num1 << '\n';
    std::string input_num2;
    std::cout << "Введите второе длинное целое число:\t";
    std::getline(std::cin, input_num2);
    BigInteger num2(input_num2);
    std::cout << "Вы ввели второе число:\t" << num2 << '\n';

    bool flagToMenageOperation{ true };
    int choice;
    do {
        std::cout << "\nВыберите операцию:\n";
        std::cout << "1. Сложение двух длинных целых\n";
        std::cout << "2. Сложение длинного целого с целым\n";
        std::cout << "3. Вычитание двух длинных целых\n";
        std::cout << "4. Вычитание из длинного целого целого\n";
        std::cout << "5. Произведение двух длинных целых\n";
        std::cout << "6. Произведение длинного целого и целого\n";
        std::cout << "7. Деление двух длинных целых\n";
        std::cout << "8. Деление длинного целого на целое\n";
        std::cout << "9. Пре- и постинкремент\n";
        std::cout << "10. Пре- и постдекремент\n";
        std::cout << "11. Сравнение двух длинных целых\n";
        std::cout << "12. Сравнение длинного целого с целым\n";
        std::cout << "13. Выход\n";
        std::cout << "Введите ваш выбор: ";
        std::cin >> choice;

        switch (choice) {
        case 1:
            std::cout << "Результат: " << (num1 + num2) << std::endl;
            break;
        case 2:
            std::cout << "Введите целое число: ";
            int intNum;
            std::cin >> intNum;
            std::cout << "Результат: " << (num1 + intNum) << std::endl;
            break;
        case 3:
            std::cout << "Результат: " << (num1 - num2) << std::endl;
            break;
        case 4:
            std::cout << "Введите целое число: ";
            std::cin >> intNum;
            std::cout << "Результат: " << (num1 - intNum) << std::endl;
            break;
        case 5:
            std::cout << "Результат: " << (num1 * num2) << std::endl;
            break;
        case 6:
            std::cout << "Введите целое число: ";
            std::cin >> intNum;
            std::cout << "Результат: " << (num1 * intNum) << std::endl;
            break;
        case 7:
            try {
                std::cout << "Результат: " << (num1 / num2) << std::endl;
            }
            catch (const std::invalid_argument& e) {
                std::cout << "Ошибка: " << e.what() << std::endl;
            }
            break;
        case 8:
            std::cout << "Введите целое число: ";
            std::cin >> intNum;
            try {
                std::cout << "Результат: " << (num1 / intNum) << std::endl;
            }
            catch (const std::invalid_argument& e) {
                std::cout << "Ошибка: " << e.what() << std::endl;
            }
            break;
        case 9:
            std::cout << "Преинкремент: " << ++num1 << std::endl;
            std::cout << "Постинкремент: " << num1++ << std::endl;
            std::cout << "После постинкремента: " << num1 << std::endl;
            break;
        case 10:
            std::cout << "Предекремент: " << --num1 << std::endl;
            std::cout << "Постдекремент: " << num1-- << std::endl;
            std::cout << "После постдекремента: " << num1 << std::endl;
            break;
        case 11:
            if (num1 < num2) {
                std::cout << num1 << " меньше " << num2 << std::endl;
            }
            else if (num1 > num2) {
                std::cout << num1 << " больше " << num2 << std::endl;
            }
            else {
                std::cout << num1 << " равно " << num2 << std::endl;
            }
            break;
        case 12:
            std::cout << "Введите целое число: ";
            std::cin >> intNum;
            if (num1 < intNum) {
                std::cout << num1 << " меньше " << intNum << std::endl;
            }
            else if (num1 > intNum) {
                std::cout << num1 << " больше " << intNum << std::endl;
            }
            else {
                std::cout << num1 << " равно " << intNum << std::endl;
            }
            break;
        case 13:
            std::cout << "Выход из программы..." << std::endl;
            flagToMenageOperation = false;
            break;
        default:
            std::cout << "Неверный выбор. Попробуйте снова." << std::endl;
        }
    } while (flagToMenageOperation);

    return 0;
}