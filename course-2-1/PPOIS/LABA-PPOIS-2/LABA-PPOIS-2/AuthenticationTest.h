#include <gtest/gtest.h>
#include "Authentication.h"

TEST(AuthenticationTest, SetAndVerifyPassword) {
    Authentication auth;
    auth.setPassword("correct_password");

    EXPECT_TRUE(auth.verifyPassword("correct_password"));
    EXPECT_FALSE(auth.verifyPassword("wrong_password"));
}

TEST(AuthenticationTest, VerifyEmptyPassword) {
    Authentication auth;
    auth.setPassword("");

    EXPECT_TRUE(auth.verifyPassword(""));
    EXPECT_FALSE(auth.verifyPassword("not_empty"));
}
