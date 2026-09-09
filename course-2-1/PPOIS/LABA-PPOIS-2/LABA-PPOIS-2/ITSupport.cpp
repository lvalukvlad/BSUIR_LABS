#include "ITSupport.h"

void ITSupport::displayInfo() const {
    Employee::displayInfo();
    std::cout << "Role: IT Support" << std::endl;
}