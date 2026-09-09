#include <gtest/gtest.h>
#include "Manager.h"

// Mock Employee to avoid dependencies on actual Employee implementation
class MockEmployee : public Employee {
public:
    MockEmployee(const std::string& name, int age, const std::string& position, double salary)
        : Employee(name, age, position, salary) {}

    void displayInfo() const override {
        std::cout << "Mock Employee Info" << std::endl;
    }
};

