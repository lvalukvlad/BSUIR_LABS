#include "Company.h"
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
#include <iostream>

int main() {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");

    Company company;

    Employee emp1("John Doe", 30, "Manager", 50000);
    Employee emp2("Jane Smith", 28, "Developer", 60000);
    company.hireEmployee(emp1);
    company.hireEmployee(emp2);

    Product prod1(1, "Medicine A", 100, 50);
    Product prod2(2, "Medicine B", 200, 30);
    company.addProduct(prod1);
    company.addProduct(prod2);

    Order order1(1, 1, { prod1.getId(), prod2.getId() });
    company.createOrder(order1);
    company.processOrder(order1);

    Payment payment1(1, 1, 300);
    company.makePayment(payment1);

    Supplier supplier1("Supplier Inc.", 10, "Pharma Co.");
    company.addSupplier(supplier1);

    Customer customer1("Alice Johnson", 25, "alice@example.com", "123-456-7890");
    company.addCustomer(customer1);
    customer1.displayInfo();

    Transaction transaction1(1, 1001, 1002, 500.0);
    company.addTransaction(transaction1);
    transaction1.process();

    Authentication auth("user", "password123");
    bool isPasswordCorrect = auth.verifyPassword("password123");
    std::cout << "Password verification: " << (isPasswordCorrect ? "Correct" : "Incorrect") << std::endl;

    company.generateReport();

    company.displayInfo();

    std::cout << "Company operations completed successfully." << std::endl;

    return 0;
}