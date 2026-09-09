#pragma once
#include <vector>
#include <string>
#include <iostream>
#include "Product.h"
using namespace std;

class Order {
private:
    int orderID;
    int customerID;
    vector<int> productList;
    string status;

public:
    Order(int id, int customerID, const vector<int>& products)
        : orderID(id), customerID(customerID), productList(products), status("Pending") {}

    int getOrderID() const;
    int getCustomerID() const;
    vector<int> getProductList() const;
    string getStatus() const;

    void displayOrderDetails() const;
    string getOrderDetails() const;
    double calculateTotal(const vector<Product>& products) const;
};