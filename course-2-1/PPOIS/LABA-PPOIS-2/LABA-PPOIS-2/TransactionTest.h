#pragma once
#include <gtest/gtest.h>
#include "Transaction.h"

// Test the constructor and getters
TEST(TransactionTest, ConstructorAndGetters) {
    Transaction transaction(1, 1001, 2002, 500.75);

    EXPECT_EQ(transaction.getTransactionID(), 1);
    EXPECT_EQ(transaction.getFromAccount(), 1001);
    EXPECT_EQ(transaction.getToAccount(), 2002);
    EXPECT_DOUBLE_EQ(transaction.getAmount(), 500.75);
}

// Test the process method
TEST(TransactionTest, Process) {
    Transaction transaction(1, 1001, 2002, 500.75);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    transaction.process();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Processing transaction ID: 1 from account 1001 to account 2002 amount: 500.75\n";

    EXPECT_EQ(output, expected_output);
}

// Test the displayInfo method
TEST(TransactionTest, DisplayInfo) {
    Transaction transaction(1, 1001, 2002, 500.75);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    transaction.displayInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Transaction ID: 1, From Account: 1001, To Account: 2002, Amount: 500.75\n";

    EXPECT_EQ(output, expected_output);
}