#pragma once
#include <string>
#include <iostream>

class Product {
private:
    int id;
    std::string name;
    double price;
    int quantity;

public:
    Product(int id, std::string name, double price, int quantity)
        : id(id), name(name), price(price), quantity(quantity) {}

    int getId() const { return id; }
    std::string getName() const { return name; }
    double getPrice() const { return price; }
    int getQuantity() const { return quantity; }

    void displayInfo() const;
};