#include "Transaction.h"

int Transaction::getTransactionID() const {
    return transactionID;
}

int Transaction::getFromAccount() const {
    return fromAccount;
}

int Transaction::getToAccount() const {
    return toAccount;
}

double Transaction::getAmount() const {
    return amount;
}

void Transaction::process() const {
    std::cout << "Processing transaction ID: " << transactionID << " from account " << fromAccount << " to account " << toAccount << " amount: " << amount << std::endl;
}

void Transaction::displayInfo() const {
    std::cout << "Transaction ID: " << transactionID << ", From Account: " << fromAccount << ", To Account: " << toAccount << ", Amount: " << amount << std::endl;
}