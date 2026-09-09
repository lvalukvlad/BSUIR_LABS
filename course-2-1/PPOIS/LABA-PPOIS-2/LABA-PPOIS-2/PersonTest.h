#include <gtest/gtest.h>
#include "Person.h"

// Test the default constructor
TEST(PersonTest, DefaultConstructor) {
    Person person;
    EXPECT_EQ(person.name, ""); // name should be empty string
    EXPECT_EQ(person.age, 0);   // age should be 0
}

// Test the parameterized constructor
TEST(PersonTest, ParameterizedConstructor) {
    Person person("John Doe", 30);
    EXPECT_EQ(person.name, "John Doe"); // name should be "John Doe"
    EXPECT_EQ(person.age, 30);          // age should be 30
}

// Test the displayInfo method
TEST(PersonTest, DisplayInfo) {
    Person person("Jane Doe", 25);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    person.displayInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    EXPECT_EQ(output, "Name: Jane Doe, Age: 25\n");
}