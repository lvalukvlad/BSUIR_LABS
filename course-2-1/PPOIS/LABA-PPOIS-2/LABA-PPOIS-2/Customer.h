#pragma once
#include "Person.h"
#include <string>

class Customer : public Person {
private:
    std::string email;
    std::string phone;

public:
    Customer(const std::string& name, int age, const std::string& email, const std::string& phone)
        : Person(name, age), email(email), phone(phone) {}

    void displayInfo() const override {
        Person::displayInfo();
        std::cout << "Email: " << email << ", Phone: " << phone << std::endl;
    }
};