#pragma once
#include <string>
#include <iostream>

class Person {
public:
    std::string name;
    int age;
    Person() : name(""), age(0) {} 
    Person(const std::string& name, int age) : name(name), age(age) {}
    virtual void displayInfo() const;
};