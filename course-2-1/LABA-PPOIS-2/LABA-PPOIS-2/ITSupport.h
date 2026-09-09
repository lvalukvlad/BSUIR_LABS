#pragma once
#include "Employee.h"

class ITSupport : public virtual Employee { 
public:
    ITSupport(const std::string& name, int age, const std::string& position, double salary)
        : Person(name, age), Employee(name, age, position, salary) {} 

    void displayInfo() const;
};