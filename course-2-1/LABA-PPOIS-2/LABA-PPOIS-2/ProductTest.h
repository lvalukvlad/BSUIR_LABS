#include <gtest/gtest.h>
#include "Product.h"

// Test the constructor and getters
TEST(ProductTest, ConstructorAndGetters) {
    Product product(1, "Laptop", 999.99, 10);

    EXPECT_EQ(product.getId(), 1);
    EXPECT_EQ(product.getName(), "Laptop");
    EXPECT_DOUBLE_EQ(product.getPrice(), 999.99);
    EXPECT_EQ(product.getQuantity(), 10);
}

// Test the displayInfo method
TEST(ProductTest, DisplayInfo) {
    Product product(1, "Laptop", 999.99, 10);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    product.displayInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Product ID: 1, Name: Laptop, Price: 999.99, Quantity: 10\n";

    EXPECT_EQ(output, expected_output);
}
