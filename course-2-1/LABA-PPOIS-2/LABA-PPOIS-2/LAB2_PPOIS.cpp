#include "Company.h"
#include "Employee.h"
#include "Product.h"
#include "Order.h"
#include "Inventory.h"
#include "Supplier.h"
#include "Delivery.h"
#include "Payment.h"
#include "Invoice.h"
#include "Report.h"
#include "Warehouse.h"
#include "Sales.h"
#include "Marketing.h"
#include "Finance.h"
#include "HR.h"
#include "IT.h"
#include "Legal.h"
#include "RnD.h"
#include <iostream>

int main() {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");

    Company company;

    // Добавление сотрудников
    Employee emp1(1, "John Doe", "Manager", 50000, "john.doe@example.com");
    Employee emp2(2, "Jane Smith", "Developer", 60000, "jane.smith@example.com");
    company.hireEmployee(emp1);
    company.hireEmployee(emp2);

    // Добавление продуктов
    Product prod1(1, "Laptop", 1000, 10);
    Product prod2(2, "Smartphone", 500, 20);
    company.addProduct(prod1);
    company.addProduct(prod2);

    // Создание заказа
    Order order1(1, 1, { prod1.getId(), prod2.getId() });
    company.createOrder(order1);
    company.processOrder(order1);

    // Управление инвентарем
    company.manageInventory();

    // Генерация отчета
    company.generateReport();

    // Выполнение платежа
    Payment payment1(1, 1, 1500); // Изменяем вызов конструктора
    company.makePayment(payment1);

    // Доставка заказа
    Delivery delivery1(1, 1, "123 Main St");
    company.deliverOrder(delivery1);

    // Добавление поставщика
    Supplier supplier1(1, "Tech Supplies Inc.", "contact@techsupplies.com");
    company.addSupplier(supplier1);

    // Установка маркетинговой стратегии
    Marketing marketing1("Social Media Campaign", "Young Adults", 10000);
    company.setMarketingStrategy(marketing1);

    // Управление финансами
    Finance finance1(100000);
    company.manageFinance(finance1);

    // Соблюдение юридических норм
    Legal legal1("123", "Compliance Document", "2023-01-01", "2023-12-31");
    company.handleLegalCompliance(legal1);

    // Проведение исследований и разработок
    RnD rnd1;
    rnd1.addResearchProject("New Product Development", "Developing a new innovative product.");
    company.conductRnD(rnd1);

    // Управление кадрами
    HR hr1;
    hr1.hireEmployee(emp1);
    hr1.hireEmployee(emp2);
    company.manageHR(hr1);

    // Управление ИТ-ресурсами
    IT it1;
    it1.addHardwareResource("Server");
    it1.addSoftwareResource("CRM System");
    company.manageIT(it1);

    // Управление продажами
    Sales sales1(1);
    company.manageSales(sales1);

    // Управление складом
    Warehouse warehouse1(1, "Main Warehouse");
    company.manageWarehouse(warehouse1);

    std::cout << "Company operations completed successfully." << std::endl;

    return 0;
}