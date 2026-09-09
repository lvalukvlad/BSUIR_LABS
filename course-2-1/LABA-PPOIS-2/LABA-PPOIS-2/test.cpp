#include <gtest/gtest.h>
#include "AuthenticationTest.h"
#include "EmployeeTest.h"
#include "ManagerTest.h"
#include "OrderTest.h"
#include "PaymentTest.h"
#include "PersonTest.h"
#include "ProductTest.h"
#include "TransactionTest.h"
#include "CompanyTest.h"

int main(int argc, char** argv) {
    system("chcp 1251");
    setlocale(LC_ALL, "RU");
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}

//OpenCppCoverage --sources LABA-PPOIS-2 -- .\x64\Debug\LABA-PPOIS-2.exe