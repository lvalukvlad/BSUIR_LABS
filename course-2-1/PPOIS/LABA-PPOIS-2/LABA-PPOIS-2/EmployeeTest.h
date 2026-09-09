#include <gtest/gtest.h>
#include <sstream>
#include "Employee.h"

class MockPerson : public Person {
public:
    MockPerson(const std::string& name, int age) : Person(name, age) {}

    void displayInfo() const override {
        std::cout << "Name: " << name << ", Age: " << age << std::endl;
    }
};

TEST(EmployeeTest, DisplayInfo) {
    MockPerson mock_person("John Doe", 30);
    Employee employee("Jane Smith", 40, "Manager", 75000.0);

    std::stringstream buffer;
    std::streambuf* old = std::cout.rdbuf(buffer.rdbuf());

    employee.displayInfo();

    std::cout.rdbuf(old);

    std::string output = buffer.str();
    std::string expected_output = "Name: Jane Smith, Age: 40\nPosition: Manager, Salary: 75000\n";

    EXPECT_EQ(output, expected_output);
}