// #include <gtest/gtest.h>
// #include "BigInteger.h"

// TEST(BigIntegerConstructor, DefaultConstructor) {
//     BigInteger a;
//     EXPECT_EQ(a, BigInteger("0"));
// }

// TEST(BigIntegerConstructor, StringConstructor) {
//     BigInteger a("123");
//     EXPECT_EQ(a, BigInteger("123"));
// }

// TEST(BigIntegerConstructor, NegativeStringConstructor) {
//     BigInteger a("-123");
//     EXPECT_EQ(a, BigInteger("-123"));
// }

// TEST(BigIntegerAddition, AddPositiveNumbers) {
//     BigInteger a("123");
//     BigInteger b("456");
//     EXPECT_EQ(a + b, BigInteger("579"));
// }

// TEST(BigIntegerAddition, AddNegativeNumbers) {
//     BigInteger a("-123");
//     BigInteger b("-456");
//     EXPECT_EQ(a + b, BigInteger("-579"));
// }

// TEST(BigIntegerSubtraction, SubtractPositiveNumbers) {
//     BigInteger a("456");
//     BigInteger b("123");
//     EXPECT_EQ(a - b, BigInteger("333"));
// }

// TEST(BigIntegerSubtraction, SubtractNegativeNumbers) {
//     BigInteger a("-456");
//     BigInteger b("-123");
//     EXPECT_EQ(a - b, BigInteger("-333"));
// }

// TEST(BigIntegerMultiplication, MultiplyPositiveNumbers) {
//     BigInteger a("123");
//     BigInteger b("456");
//     EXPECT_EQ(a * b, BigInteger("56088"));
// }

// TEST(BigIntegerMultiplication, MultiplyNegativeNumbers) {
//     BigInteger a("-123");
//     BigInteger b("-456");
//     EXPECT_EQ(a * b, BigInteger("56088"));
// }

// TEST(BigIntegerDivision, DividePositiveNumbers) {
//     BigInteger a("56088");
//     BigInteger b("456");
//     EXPECT_EQ(a / b, BigInteger("123"));
// }

// TEST(BigIntegerDivision, DivideNegativeNumbers) {
//     BigInteger a("-56088");
//     BigInteger b("-456");
//     EXPECT_EQ(a / b, BigInteger("123"));
// }

// int main(int argc, char **argv) {
//     ::testing::InitGoogleTest(&argc, argv);
//     return RUN_ALL_TESTS();
// }