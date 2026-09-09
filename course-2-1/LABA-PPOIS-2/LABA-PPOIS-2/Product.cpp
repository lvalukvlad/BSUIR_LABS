#include "Product.h"

void Product::displayInfo() const {
    std::cout << "Product ID: " << id << ", Name: " << name << ", Price: " << price << ", Quantity: " << quantity << std::endl;
}