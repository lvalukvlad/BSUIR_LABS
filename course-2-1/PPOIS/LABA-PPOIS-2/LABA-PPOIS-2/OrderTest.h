#include <gtest/gtest.h>
#include "Order.h"
#include "Product.h"

// Test the constructor and getters
TEST(OrderTest, ConstructorAndGetters) {
    std::vector<int> products = { 1, 2, 3 };
    Order order(1, 100, products);

    EXPECT_EQ(order.getOrderID(), 1);
    EXPECT_EQ(order.getCustomerID(), 100);
    EXPECT_EQ(order.getProductList(), products);
    EXPECT_EQ(order.getStatus(), "Pending");
}

// Test the displayOrderDetails method
TEST(OrderTest, DisplayOrderDetails) {
    std::vector<int> products = { 1, 2, 3 };
    Order order(1, 100, products);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    order.displayOrderDetails();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Order ID: 1\nCustomer ID: 100\nProducts: 1 2 3 \nStatus: Pending\n";

    EXPECT_EQ(output, expected_output);
}

// Test the getOrderDetails method
TEST(OrderTest, GetOrderDetails) {
    std::vector<int> products = { 1, 2, 3 };
    Order order(1, 100, products);

    std::string expected_details = "Order ID: 1\nCustomer ID: 100\nProducts: 1 2 3 \nStatus: Pending\n";
    EXPECT_EQ(order.getOrderDetails(), expected_details);
}

// Test the calculateTotal method
TEST(OrderTest, CalculateTotal) {
    std::vector<int> products = { 1, 2, 3 };
    Order order(1, 100, products);

    std::vector<Product> allProducts = {
        Product(1, "Product1", 10.0, 1),
        Product(2, "Product2", 20.0, 1),
        Product(3, "Product3", 30.0, 1)
    };

    EXPECT_DOUBLE_EQ(order.calculateTotal(allProducts), 60.0);
}
