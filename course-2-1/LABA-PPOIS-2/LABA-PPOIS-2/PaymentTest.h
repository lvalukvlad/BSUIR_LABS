#include <gtest/gtest.h>
#include "Payment.h"

// Test the constructor
TEST(PaymentTest, Constructor) {
    Payment payment(1, 1001, 250.75);
    EXPECT_EQ(payment.getPaymentID(), 1);
    EXPECT_EQ(payment.getOrderID(), 1001);
    EXPECT_DOUBLE_EQ(payment.getAmount(), 250.75);
    EXPECT_EQ(payment.getPaymentMethod(), "Unknown");
    EXPECT_EQ(payment.getPaymentStatus(), "Pending");
}

// Test the setPaymentDetails method
TEST(PaymentTest, SetPaymentDetails) {
    Payment payment(1, 1001, 250.75);
    payment.setPaymentDetails(2, 1002, 300.50);
    EXPECT_EQ(payment.getPaymentID(), 2);
    EXPECT_EQ(payment.getOrderID(), 1002);
    EXPECT_DOUBLE_EQ(payment.getAmount(), 300.50);
}

// Test the processPayment method
TEST(PaymentTest, ProcessPayment) {
    Payment payment(1, 1001, 250.75);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    payment.processPayment();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    EXPECT_EQ(output, "Обработка платежа на сумму 250.75 для заказа 1001\n");
    EXPECT_EQ(payment.getPaymentStatus(), "Processed");
}

// Test the refundPayment method
TEST(PaymentTest, RefundPayment) {
    Payment payment(1, 1001, 250.75);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    payment.refundPayment();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    EXPECT_EQ(output, "Возврат платежа на сумму 250.75 для заказа 1001\n");
    EXPECT_EQ(payment.getPaymentStatus(), "Refunded");
}

// Test the displayPaymentInfo method
TEST(PaymentTest, DisplayPaymentInfo) {
    Payment payment(1, 1001, 250.75);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    payment.displayPaymentInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Payment ID: 1\nOrder ID: 1001\nAmount: 250.75\nPayment Method: Unknown\nPayment Status: Pending\n";
    EXPECT_EQ(output, expected_output);
}
