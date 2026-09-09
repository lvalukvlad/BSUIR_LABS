#include "D:/LABY/BSUIR/1laba_PPOIS/LongInt.h"
#include <iostream>
#include <string>

int main() {

    setlocale(LC_ALL, "russian");
    std::string input_first;
    std::cout << "введите первое длинное целое число:\t";
    std::getline(std::cin, input_first);
    LongInt first(input_first);
    std::cout << "вы ввели первое число, значение:\t" << first.getLong() << '\n';
    std::string input_second;
    std::cout << "введите второе длинное целое число:\t";
    std::getline(std::cin, input_second);
    LongInt second(input_second);
    std::cout << "вы ввели второе число, значение:\t" << second.getLong() << '\n';

    bool flagToMenageOperation{ true };
    int choice;
    do {
        std::cout << "\nChoose an operation:\n";
        std::cout << "1. Addition\n";
        std::cout << "2. Subtraction\n";
        std::cout << "3. Multiplication\n";
        std::cout << "4. Division\n";
        std::cout << "5. Exit\n";
        std::cout << "Enter your choice: ";
        std::cin >> choice;

        switch (choice) {
        case 1:
            std::cout << "Result: " << (first + second).getLong() << std::endl;
            break;
        case 2:
            std::cout << "Result: " << (first - second).getLong() << std::endl;
            break;
        case 3:
            std::cout << "Result: " << (first * second).getLong() << std::endl;
            break;
        case 4:
            std::cout << "Result: " << (first / second).getLong() << std::endl;
            break;
        case 5:
            std::cout << "Exiting the program..." << std::endl;
            break;
        default:
            std::cout << "Invalid choice. Please try again." << std::endl;
        }
    } while (choice != 5);

    return 0;
}