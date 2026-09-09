#pragma once
#include <string>
#include <iostream>

class BankAccount {
private:
    int accountNumber;
    double balance;

public:
    BankAccount(int accountNumber, double balance)
        : accountNumber(accountNumber), balance(balance) {}

    int getAccountNumber() const { return accountNumber; }
    double getBalance() const { return balance; }

    void deposit(double amount) {
        balance += amount;
    }

    void withdraw(double amount) {
        if (amount <= balance) {
            balance -= amount;
        }
        else {
            std::cout << "Insufficient funds" << std::endl;
        }
    }

    void displayInfo() const {
        std::cout << "Account Number: " << accountNumber << ", Balance: " << balance << std::endl;
    }
};