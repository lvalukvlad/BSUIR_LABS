#pragma once
#include "Employee.h"

class Manager : public virtual Employee { 
public:
    using Employee::Employee; 

    void displayInfo() const override;
};