#pragma once
#include <gtest/gtest.h>
#include "Company.h"
#include "Employee.h"
#include "Product.h"
#include "Order.h"
#include "Payment.h"
#include "Supplier.h"
#include "Customer.h"
#include "Transaction.h"

// Test the hireEmployee method
TEST(CompanyTest, HireEmployee) {
    Company company;
    Employee employee("John Doe", 30, "Developer", 50000.0);
    company.hireEmployee(employee);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    company.displayInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Name: John Doe, Age: 30\nPosition: Developer, Salary: 50000\n";

    EXPECT_EQ(output, expected_output);
}

// Test the addProduct method
TEST(CompanyTest, AddProduct) {
    Company company;
    Product product(1, "Laptop", 999.99, 10);
    company.addProduct(product);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    company.displayInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Product ID: 1, Name: Laptop, Price: 999.99, Quantity: 10\n";

    EXPECT_EQ(output, expected_output);
}

// Test the createOrder method
TEST(CompanyTest, CreateOrder) {
    Company company;
    std::vector<int> products = { 1, 2, 3 };
    Order order(1, 100, products);
    company.createOrder(order);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    company.displayInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Order ID: 1\nCustomer ID: 100\nProducts: 1 2 3 \nStatus: Pending\n";

    EXPECT_EQ(output, expected_output);
}

// Test the makePayment method
TEST(CompanyTest, MakePayment) {
    Company company;
    Payment payment(1, 1001, 250.75);
    company.makePayment(payment);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    company.displayInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Payment ID: 1\nOrder ID: 1001\nAmount: 250.75\nPayment Method: Unknown\nPayment Status: Pending\n";

    EXPECT_EQ(output, expected_output);
}


// Test the addTransaction method
TEST(CompanyTest, AddTransaction) {
    Company company;
    Transaction transaction(1, 1001, 2002, 500.75);
    company.addTransaction(transaction);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    company.displayInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Transaction ID: 1, From Account: 1001, To Account: 2002, Amount: 500.75\n";

    EXPECT_EQ(output, expected_output);
}
