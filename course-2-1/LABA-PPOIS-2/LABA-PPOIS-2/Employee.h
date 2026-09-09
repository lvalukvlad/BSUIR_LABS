#pragma once
#include "Person.h"
#include <string>

class Employee : public virtual Person { 
private:
    std::string position;
    double salary;

public:
    Employee(std::string name, int age, std::string position, double salary)
        : Person(name, age), position(position), salary(salary) {}

    void displayInfo() const override;
};