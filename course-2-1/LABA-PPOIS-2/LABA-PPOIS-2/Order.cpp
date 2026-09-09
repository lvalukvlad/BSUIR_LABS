#include "Order.h"
#include "Product.h"

int Order::getOrderID() const {
    return orderID;
}

int Order::getCustomerID() const {
    return customerID;
}

vector<int> Order::getProductList() const {
    return productList;
}

string Order::getStatus() const {
    return status;
}

void Order::displayOrderDetails() const {
    cout << "Order ID: " << orderID << endl;
    cout << "Customer ID: " << customerID << endl;
    cout << "Products: ";
    for (const auto& product : productList) {
        cout << product << " ";
    }
    cout << endl;
    cout << "Status: " << status << endl;
}

string Order::getOrderDetails() const {
    string details = "Order ID: " + to_string(orderID) + "\n";
    details += "Customer ID: " + to_string(customerID) + "\n";
    details += "Products: ";
    for (const auto& product : productList) {
        details += to_string(product) + " ";
    }
    details += "\nStatus: " + status + "\n";
    return details;
}

double Order::calculateTotal(const vector<Product>& products) const {
    double total = 0.0;
    for (const auto& productID : productList) {
        for (const auto& product : products) {
            if (product.getId() == productID) {
                total += product.getPrice();
                break;
            }
        }
    }
    return total;
}