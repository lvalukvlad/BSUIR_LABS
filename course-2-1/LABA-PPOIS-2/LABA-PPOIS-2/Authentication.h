#pragma once
#include <string>
class Authentication {
private:
    std::string password;

public:
    void setPassword(const std::string& newPassword) {
        password = newPassword;
    }

    bool verifyPassword(const std::string& inputPassword) const {
        return password == inputPassword;
    }
};