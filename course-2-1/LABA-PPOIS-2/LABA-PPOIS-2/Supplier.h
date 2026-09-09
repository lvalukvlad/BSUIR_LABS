#pragma once
#include "Person.h"
#include <string>

class Supplier : private Person {
private:
    std::string company;

public:
    Supplier(const std::string& name, int age, const std::string& company)
        : Person(name, age), company(company) {}

    void displayInfo() const;
};