#pragma once
#include <string>
#include <iostream>

class Transaction {
private:
    int transactionID;
    int fromAccount;
    int toAccount;
    double amount;

public:
    Transaction(int id, int from, int to, double amount)
        : transactionID(id), fromAccount(from), toAccount(to), amount(amount) {}

    int getTransactionID() const;
    int getFromAccount() const;
    int getToAccount() const;
    double getAmount() const;

    void process() const;
    void displayInfo() const;
};