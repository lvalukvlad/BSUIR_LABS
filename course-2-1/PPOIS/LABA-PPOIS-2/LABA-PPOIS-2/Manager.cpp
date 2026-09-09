#include "Manager.h"

void Manager::displayInfo() const {
    Employee::displayInfo();
    std::cout << "Role: Manager" << std::endl;
}