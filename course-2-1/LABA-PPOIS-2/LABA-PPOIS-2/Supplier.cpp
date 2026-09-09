#include "Supplier.h"

void Supplier::displayInfo() const {
    Person::displayInfo();
    std::cout << "Company: " << company << std::endl;
}