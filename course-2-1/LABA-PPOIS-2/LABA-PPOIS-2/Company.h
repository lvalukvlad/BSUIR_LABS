#pragma once
#include "Employee.h"
#include "Manager.h"
#include "Supplier.h"
#include "ITSupport.h"
#include "Executive.h"
#include "Product.h"
#include "Order.h"
#include "Payment.h"
#include "Invoice.h"
#include "Customer.h"
#include "Transaction.h"
#include "Authentication.h"
#include <vector>
#include <string>

class Company {
private:
    std::vector<Employee> employees;
    std::vector<Product> products;
    std::vector<Order> orders;
    std::vector<Payment> payments;
    std::vector<Supplier> suppliers;
    std::vector<Customer> customers;
    std::vector<Transaction> transactions;

public:
    void hireEmployee(const Employee& employee);
    void addProduct(const Product& product);
    void createOrder(const Order& order);
    void processOrder(const Order& order);
    void makePayment(const Payment& payment);
    void addSupplier(const Supplier& supplier);
    void addCustomer(const Customer& customer);
    void addTransaction(const Transaction& transaction);
    void generateReport() const;
    void displayInfo() const;
};