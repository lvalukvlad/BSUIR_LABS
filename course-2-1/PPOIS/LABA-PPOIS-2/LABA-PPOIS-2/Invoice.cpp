#include "Invoice.h"
#include "Order.h"
#include "Product.h"
#include <iostream>

void Invoice::generateInvoice(const Order& order, const std::vector<Product>& products) {
    std::cout << "Generating invoice for order:" << std::endl;
    std::cout << order.getOrderDetails() << std::endl;

    double total = 0.0;
    for (const auto& product : products) {
        total += product.getPrice();
    }

    std::cout << "Total: " << total << std::endl;
}