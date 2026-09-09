#pragma once
#include <string>
#include <iostream>
using namespace std;

class Payment {
private:
    int paymentID;
    int orderID;
    double amount;
    string paymentMethod;
    string paymentStatus;

public:
    Payment(int paymentID, int orderID, double amount)
        : paymentID(paymentID), orderID(orderID), amount(amount), paymentMethod("Unknown"), paymentStatus("Pending") {}

    void setPaymentDetails(int paymentID, int orderID, double amount);
    int getPaymentID() const;
    int getOrderID() const;
    double getAmount() const;
    string getPaymentMethod() const;
    string getPaymentStatus() const;

    void processPayment();
    void refundPayment();
    void displayPaymentInfo() const;
};