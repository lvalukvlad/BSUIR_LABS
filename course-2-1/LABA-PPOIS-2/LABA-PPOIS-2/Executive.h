#pragma once
#include "Manager.h"
#include "ITSupport.h"

class Executive : public Manager, public ITSupport {
public:
    Executive(const std::string& name, int age, const std::string& position, double salary)
        : Person(name, age), Employee(name, age, position, salary), Manager(name, age, position, salary), ITSupport(name, age, position, salary) {}

    void displayInfo() const override;
};