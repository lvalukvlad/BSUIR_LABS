#pragma once
#include "Order.h"
#include "Product.h"
#include <vector>
#include <string>

class Invoice {
public:
    void generateInvoice(const Order& order, const std::vector<Product>& products); 
};