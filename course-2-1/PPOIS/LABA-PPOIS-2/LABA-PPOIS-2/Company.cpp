#include "Company.h"

void Company::hireEmployee(const Employee& employee) {
    employees.push_back(employee);
}

void Company::addProduct(const Product& product) {
    products.push_back(product);
}

void Company::createOrder(const Order& order) {
    orders.push_back(order);
}

void Company::processOrder(const Order& order) {
}

void Company::makePayment(const Payment& payment) {
    payments.push_back(payment);
}

void Company::addSupplier(const Supplier& supplier) {
    suppliers.push_back(supplier);
}

void Company::addCustomer(const Customer& customer) {
    customers.push_back(customer);
}

void Company::addTransaction(const Transaction& transaction) {
    transactions.push_back(transaction);
}

void Company::generateReport() const {
}

void Company::displayInfo() const {
    for (const auto& employee : employees) {
        employee.displayInfo();
    }
    for (const auto& product : products) {
        product.displayInfo();
    }
    for (const auto& order : orders) {
        order.displayOrderDetails();
    }
    for (const auto& payment : payments) {
        payment.displayPaymentInfo();
    }
    for (const auto& supplier : suppliers) {
        supplier.displayInfo();
    }
    for (const auto& customer : customers) {
        customer.displayInfo();
    }
    for (const auto& transaction : transactions) {
        transaction.displayInfo();
    }
}