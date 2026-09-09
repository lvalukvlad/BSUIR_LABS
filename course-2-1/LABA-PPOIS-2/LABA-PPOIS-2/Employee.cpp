#include "Employee.h"

void Employee::displayInfo() const {
    Person::displayInfo();
    std::cout << "Position: " << position << ", Salary: " << salary << std::endl;
}