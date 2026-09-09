#include "Executive.h"

void Executive::displayInfo() const {
    Manager::displayInfo();
    ITSupport::displayInfo();
    std::cout << "Role: Executive" << std::endl;
}