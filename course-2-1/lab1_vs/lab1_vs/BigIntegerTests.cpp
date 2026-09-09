#include <gmock/gmock.h>
#include <gtest/gtest.h>
#include "BigInteger.h"

// Тесты для конструкторов
TEST(BigIntegerConstructor_DefaultConstructor) {
    BigInteger a;
    CHECK_EQUAL(a, BigInteger("0"));
}

TEST(BigIntegerConstructor_StringConstructor) {
    BigInteger a("123");
    CHECK_EQUAL(a, BigInteger("123"));
}

TEST(BigIntegerConstructor_NegativeStringConstructor) {
    BigInteger a("-123");
    CHECK_EQUAL(a, BigInteger("-123"));
}

TEST(BigIntegerConstructor_VectorConstructor) {
    std::vector<int> digits = { 3, 2, 1 };
    BigInteger a(digits, true);
    CHECK_EQUAL(a, BigInteger("123"));
}

TEST(BigIntegerConstructor_CopyConstructor) {
    BigInteger a("123");
    BigInteger b(a);
    CHECK_EQUAL(b, a);
}

// Тесты для операторов присваивания
TEST(BigIntegerAssignment_AssignmentOperator) {
    BigInteger a("123");
    BigInteger b;
    b = a;
    CHECK_EQUAL(b, a);
}

// Тесты для преобразования в int
TEST(BigIntegerConversion_ToInt) {
    BigInteger a("123");
    int b = a;
    CHECK_EQUAL(b, 123);
}

// Тесты для сложения
TEST(BigIntegerAddition_AddPositiveNumbers) {
    BigInteger a("123");
    BigInteger b("456");
    CHECK_EQUAL(a + b, BigInteger("579"));
}

TEST(BigIntegerAddition_AddNegativeNumbers) {
    BigInteger a("-123");
    BigInteger b("-456");
    CHECK_EQUAL(a + b, BigInteger("-579"));
}

TEST(BigIntegerAddition_AddPositiveAndNegativeNumbers) {
    BigInteger a("123");
    BigInteger b("-456");
    CHECK_EQUAL(a + b, BigInteger("-333"));
}

// Тесты для вычитания
TEST(BigIntegerSubtraction_SubtractPositiveNumbers) {
    BigInteger a("456");
    BigInteger b("123");
    CHECK_EQUAL(a - b, BigInteger("333"));
}

TEST(BigIntegerSubtraction_SubtractNegativeNumbers) {
    BigInteger a("-456");
    BigInteger b("-123");
    CHECK_EQUAL(a - b, BigInteger("-333"));
}

TEST(BigIntegerSubtraction_SubtractPositiveAndNegativeNumbers) {
    BigInteger a("123");
    BigInteger b("-456");
    CHECK_EQUAL(a - b, BigInteger("579"));
}

// Тесты для умножения
TEST(BigIntegerMultiplication_MultiplyPositiveNumbers) {
    BigInteger a("123");
    BigInteger b("456");
    CHECK_EQUAL(a * b, BigInteger("56088"));
}

TEST(BigIntegerMultiplication_MultiplyNegativeNumbers) {
    BigInteger a("-123");
    BigInteger b("-456");
    CHECK_EQUAL(a * b, BigInteger("56088"));
}

TEST(BigIntegerMultiplication_MultiplyPositiveAndNegativeNumbers) {
    BigInteger a("123");
    BigInteger b("-456");
    CHECK_EQUAL(a * b, BigInteger("-56088"));
}

// Тесты для деления
TEST(BigIntegerDivision_DividePositiveNumbers) {
    BigInteger a("56088");
    BigInteger b("456");
    CHECK_EQUAL(a / b, BigInteger("123"));
}

TEST(BigIntegerDivision_DivideNegativeNumbers) {
    BigInteger a("-56088");
    BigInteger b("-456");
    CHECK_EQUAL(a / b, BigInteger("123"));
}

TEST(BigIntegerDivision_DividePositiveAndNegativeNumbers) {
    BigInteger a("56088");
    BigInteger b("-456");
    CHECK_EQUAL(a / b, BigInteger("-123"));
}

// Тесты для инкремента и декремента
TEST(BigIntegerIncrementDecrement_PreIncrement) {
    BigInteger a("123");
    ++a;
    CHECK_EQUAL(a, BigInteger("124"));
}

TEST(BigIntegerIncrementDecrement_PostIncrement) {
    BigInteger a("123");
    BigInteger b = a++;
    CHECK_EQUAL(a, BigInteger("124"));
    CHECK_EQUAL(b, BigInteger("123"));
}

TEST(BigIntegerIncrementDecrement_PreDecrement) {
    BigInteger a("123");
    --a;
    CHECK_EQUAL(a, BigInteger("122"));
}

TEST(BigIntegerIncrementDecrement_PostDecrement) {
    BigInteger a("123");
    BigInteger b = a--;
    CHECK_EQUAL(a, BigInteger("122"));
    CHECK_EQUAL(b, BigInteger("123"));
}

// Тесты для сравнения
TEST(BigIntegerComparison_CompareEqualNumbers) {
    BigInteger a("123");
    BigInteger b("123");
    CHECK(a == b);
    CHECK(!(a != b));
    CHECK(!(a < b));
    CHECK(a <= b);
    CHECK(!(a > b));
    CHECK(a >= b);
}

TEST(BigIntegerComparison_CompareDifferentNumbers) {
    BigInteger a("123");
    BigInteger b("456");
    CHECK(!(a == b));
    CHECK(a != b);
    CHECK(a < b);
    CHECK(a <= b);
    CHECK(!(a > b));
    CHECK(!(a >= b));
}

TEST(BigIntegerComparison_CompareWithInt) {
    BigInteger a("123");
    int b = 123;
    CHECK(a == b);
    CHECK(!(a != b));
    CHECK(!(a < b));
    CHECK(a <= b);
    CHECK(!(a > b));
    CHECK(a >= b);
}

// Тесты для сложения с int
TEST(BigIntegerAddition_AddInt) {
    BigInteger a("123");
    int b = 456;
    CHECK_EQUAL(a + b, BigInteger("579"));
}

TEST(BigIntegerAddition_AddNegativeInt) {
    BigInteger a("123");
    int b = -456;
    CHECK_EQUAL(a + b, BigInteger("-333"));
}

// Тесты для вычитания с int
TEST(BigIntegerSubtraction_SubtractInt) {
    BigInteger a("456");
    int b = 123;
    CHECK_EQUAL(a - b, BigInteger("333"));
}

TEST(BigIntegerSubtraction_SubtractNegativeInt) {
    BigInteger a("456");
    int b = -123;
    CHECK_EQUAL(a - b, BigInteger("579"));
}

// Тесты для умножения с int
TEST(BigIntegerMultiplication_MultiplyInt) {
    BigInteger a("123");
    int b = 456;
    CHECK_EQUAL(a * b, BigInteger("56088"));
}

TEST(BigIntegerMultiplication_MultiplyNegativeInt) {
    BigInteger a("123");
    int b = -456;
    CHECK_EQUAL(a * b, BigInteger("-56088"));
}

// Тесты для деления с int
TEST(BigIntegerDivision_DivideInt) {
    BigInteger a("56088");
    int b = 456;
    CHECK_EQUAL(a / b, BigInteger("123"));
}

TEST(BigIntegerDivision_DivideNegativeInt) {
    BigInteger a("56088");
    int b = -456;
    CHECK_EQUAL(a / b, BigInteger("-123"));
}

int main(int argc, char** argv) {
    return UnitTest::RunAllTests();
}