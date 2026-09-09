#include "BigInteger.h"
#include "gtest/gtest.h"

TEST(BigIntegerConstructor_DefaultConstructor) {
    BigInteger a;
    EXPECT_EQ(a, BigInteger("0"));
}

TEST(BigIntegerConstructor_StringConstructor) {
    BigInteger a("123");
    EXPECT_EQ(a, BigInteger("123"));
}

TEST(BigIntegerConstructor_NegativeStringConstructor) {
    BigInteger a("-123");
    EXPECT_EQ(a, BigInteger("-123"));
}

TEST(BigIntegerConstructor_VectorConstructor) {
    std::vector<int> digits = { 3, 2, 1 };
    BigInteger a(digits, true);
    EXPECT_EQ(a, BigInteger("123"));
}

TEST(BigIntegerConstructor_CopyConstructor) {
    BigInteger a("123");
    BigInteger b(a);
    EXPECT_EQ(b, a);
}

TEST(BigIntegerAssignment_AssignmentOperator) {
    BigInteger a("123");
    BigInteger b;
    b = a;
    EXPECT_EQ(b, a);
}

TEST(BigIntegerConversion_ToInt) {
    BigInteger a("123");
    int b = a;
    EXPECT_EQ(b, 123);
}

TEST(BigIntegerAddition_AddPositiveNumbers) {
    BigInteger a("123");
    BigInteger b("456");
    EXPECT_EQ(a + b, BigInteger("579"));
}

TEST(BigIntegerAddition_AddNegativeNumbers) {
    BigInteger a("-123");
    BigInteger b("-456");
    EXPECT_EQ(a + b, BigInteger("-579"));
}

TEST(BigIntegerAddition_AddPositiveAndNegativeNumbers) {
    BigInteger a("123");
    BigInteger b("-456");
    EXPECT_EQ(a + b, BigInteger("-333"));
}

TEST(BigIntegerSubtraction_SubtractPositiveNumbers) {
    BigInteger a("456");
    BigInteger b("123");
    EXPECT_EQ(a - b, BigInteger("333"));
}

TEST(BigIntegerSubtraction_SubtractNegativeNumbers) {
    BigInteger a("-456");
    BigInteger b("-123");
    EXPECT_EQ(a - b, BigInteger("-333"));
}

TEST(BigIntegerSubtraction_SubtractPositiveAndNegativeNumbers) {
    BigInteger a("123");
    BigInteger b("-456");
    EXPECT_EQ(a - b, BigInteger("579"));
}

TEST(BigIntegerMultiplication_MultiplyPositiveNumbers) {
    BigInteger a("123");
    BigInteger b("456");
    EXPECT_EQ(a * b, BigInteger("56088"));
}

TEST(BigIntegerMultiplication_MultiplyNegativeNumbers) {
    BigInteger a("-123");
    BigInteger b("-456");
    EXPECT_EQ(a * b, BigInteger("56088"));
}

TEST(BigIntegerMultiplication_MultiplyPositiveAndNegativeNumbers) {
    BigInteger a("123");
    BigInteger b("-456");
    EXPECT_EQ(a * b, BigInteger("-56088"));
}

TEST(BigIntegerDivision_DividePositiveNumbers) {
    BigInteger a("56088");
    BigInteger b("456");
    EXPECT_EQ(a / b, BigInteger("123"));
}

TEST(BigIntegerDivision_DivideNegativeNumbers) {
    BigInteger a("-56088");
    BigInteger b("-456");
    EXPECT_EQ(a / b, BigInteger("123"));
}

TEST(BigIntegerDivision_DividePositiveAndNegativeNumbers) {
    BigInteger a("56088");
    BigInteger b("-456");
    EXPECT_EQ(a / b, BigInteger("-123"));
}

TEST(BigIntegerIncrementDecrement_PreIncrement) {
    BigInteger a("123");
    ++a;
    EXPECT_EQ(a, BigInteger("124"));
}

TEST(BigIntegerIncrementDecrement_PostIncrement) {
    BigInteger a("123");
    BigInteger b = a++;
    EXPECT_EQ(a, BigInteger("124"));
    EXPECT_EQ(b, BigInteger("123"));
}

TEST(BigIntegerIncrementDecrement_PreDecrement) {
    BigInteger a("123");
    --a;
    EXPECT_EQ(a, BigInteger("122"));
}

TEST(BigIntegerIncrementDecrement_PostDecrement) {
    BigInteger a("123");
    BigInteger b = a--;
    EXPECT_EQ(a, BigInteger("122"));
    EXPECT_EQ(b, BigInteger("123"));
}

TEST(BigIntegerComparison_CompareEqualNumbers) {
    BigInteger a("123");
    BigInteger b("123");
    EXPECT_TRUE(a == b);
    EXPECT_FALSE(!(a != b));
    EXPECT_FALSE(!(a < b));
    EXPECT_TRUE(a <= b);
    EXPECT_FALSE(!(a > b));
    EXPECT_TRUE(a >= b);
}

TEST(BigIntegerComparison_CompareDifferentNumbers) {
    BigInteger a("123");
    BigInteger b("456");
    EXPECT_FALSE(!(a == b));
    EXPECT_TRUE(a != b);
    EXPECT_TRUE(a < b);
    EXPECT_TRUE(a <= b);
    EXPECT_FALSE(!(a > b));
    EXPECT_FALSE(!(a >= b));
}

TEST(BigIntegerComparison_CompareWithInt) {
    BigInteger a("123");
    int b = 123;
    EXPECT_TRUE(a == b);
    EXPECT_FALSE(!(a != b));
    EXPECT_FALSE(!(a < b));
    EXPECT_TRUE(a <= b);
    EXPECT_FALSE(!(a > b));
    EXPECT_TRUE(a >= b);
}
TEST(BigIntegerAddition_AddInt) {
    BigInteger a("123");
    int b = 456;
    EXPECT_EQ(a + b, BigInteger("579"));
}

TEST(BigIntegerAddition_AddNegativeInt) {
    BigInteger a("123");
    int b = -456;
    EXPECT_EQ(a + b, BigInteger("-333"));
}

TEST(BigIntegerSubtraction_SubtractInt) {
    BigInteger a("456");
    int b = 123;
    EXPECT_EQ(a - b, BigInteger("333"));
}

TEST(BigIntegerSubtraction_SubtractNegativeInt) {
    BigInteger a("456");
    int b = -123;
    EXPECT_EQ(a - b, BigInteger("579"));
}

TEST(BigIntegerMultiplication_MultiplyInt) {
    BigInteger a("123");
    int b = 456;
    EXPECT_EQ(a * b, BigInteger("56088"));
}

TEST(BigIntegerMultiplication_MultiplyNegativeInt) {
    BigInteger a("123");
    int b = -456;
    EXPECT_EQ(a * b, BigInteger("-56088"));
}

TEST(BigIntegerDivision_DivideInt) {
    BigInteger a("56088");
    int b = 456;
    EXPECT_EQ(a / b, BigInteger("123"));
}

TEST(BigIntegerDivision_DivideNegativeInt) {
    BigInteger a("56088");
    int b = -456;
    EXPECT_EQ(a / b, BigInteger("-123"));
}

int main(int argc, char** argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}