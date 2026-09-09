#include "Payment.h"

void Payment::setPaymentDetails(int paymentID, int orderID, double amount) {
    this->paymentID = paymentID;
    this->orderID = orderID;
    this->amount = amount;
}

int Payment::getPaymentID() const {
    return paymentID;
}

int Payment::getOrderID() const {
    return orderID;
}

double Payment::getAmount() const {
    return amount;
}

string Payment::getPaymentMethod() const {
    return paymentMethod;
}

string Payment::getPaymentStatus() const {
    return paymentStatus;
}

void Payment::processPayment() {
    cout << "Обработка платежа на сумму " << amount << " для заказа " << orderID << endl;
    paymentStatus = "Processed";
}

void Payment::refundPayment() {
    cout << "Возврат платежа на сумму " << amount << " для заказа " << orderID << endl;
    paymentStatus = "Refunded";
}

void Payment::displayPaymentInfo() const {
    cout << "Payment ID: " << paymentID << endl;
    cout << "Order ID: " << orderID << endl;
    cout << "Amount: " << amount << endl;
    cout << "Payment Method: " << paymentMethod << endl;
    cout << "Payment Status: " << paymentStatus << endl;
}