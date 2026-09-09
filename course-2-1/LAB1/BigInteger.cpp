#include "BigInteger.h"
#include <algorithm>
#include <iostream>

BigInteger::BigInteger() : isPositive(true) {}

BigInteger::BigInteger(const std::string& number) {
    if (number.empty()) {
        std::cerr << "Ошибка: Неверный числовой формат" << std::endl;
        return;
    }
    isPositive = (number[0] != '-');
    for (size_t i = (isPositive ? 0 : 1); i < number.size(); ++i) {
        if (!isdigit(number[i])) {
            std::cerr << "Ошибка: Неверный числовой формат" << std::endl;
            return;
        }
        digits.push_back(number[i] - '0');
    }
    std::reverse(digits.begin(), digits.end());
}

BigInteger::BigInteger(const std::vector<int>& digits, bool isPositive) : digits(digits), isPositive(isPositive) {}

BigInteger::BigInteger(const BigInteger& other) : digits(other.digits), isPositive(other.isPositive) {}

BigInteger& BigInteger::operator=(const BigInteger& other) {
    if (this != &other) {
        digits = other.digits;
        isPositive = other.isPositive;
    }
    return *this;
}

BigInteger::operator int() const {
    int result = 0;
    for (size_t i = 0; i < digits.size(); ++i) {
        result = result * 10 + digits[digits.size() - 1 - i];
    }
    return isPositive ? result : -result;
}

std::vector<int> BigInteger::addVectors(const std::vector<int>& a, const std::vector<int>& b) const {
    std::vector<int> result;
    int carry = 0;
    size_t maxSize = std::max(a.size(), b.size());
    for (size_t i = 0; i < maxSize || carry; ++i) {
        int sum = carry;
        if (i < a.size()) sum += a[i];
        if (i < b.size()) sum += b[i];
        result.push_back(sum % 10);
        carry = sum / 10;
    }
    return result;
}

std::vector<int> BigInteger::subtractVectors(const std::vector<int>& a, const std::vector<int>& b) const {
    std::vector<int> result;
    int borrow = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        int diff = a[i] - borrow - (i < b.size() ? b[i] : 0);
        if (diff < 0) {
            diff += 10;
            borrow = 1;
        } else {
            borrow = 0;
        }
        result.push_back(diff);
    }
    return result;
}

std::vector<int> BigInteger::multiplyVectors(const std::vector<int>& a, const std::vector<int>& b) const {
    std::vector<int> result(a.size() + b.size(), 0);
    for (size_t i = 0; i < a.size(); ++i) {
        for (size_t j = 0; j < b.size(); ++j) {
            result[i + j] += a[i] * b[j];
            if (result[i + j] >= 10) {
                result[i + j + 1] += result[i + j] / 10;
                result[i + j] %= 10;
            }
        }
    }
    while (result.size() > 1 && result.back() == 0) {
        result.pop_back();
    }
    return result;
}

std::vector<int> BigInteger::divideVectors(const std::vector<int>& a, const std::vector<int>& b) const {
    return std::vector<int>{0};
}

BigInteger BigInteger::operator+(const BigInteger& other) const {
    if (isPositive == other.isPositive) {
        return BigInteger(addVectors(digits, other.digits), isPositive);
    } else {
        if (isPositive) {
            return *this - BigInteger(other.digits, true);
        } else {
            return other - BigInteger(digits, true);
        }
    }
}

BigInteger& BigInteger::operator+=(const BigInteger& other) {
    *this = *this + other;
    return *this;
}

BigInteger BigInteger::operator-(const BigInteger& other) const {
    if (isPositive == other.isPositive) {
        if (*this >= other) {
            return BigInteger(subtractVectors(digits, other.digits), isPositive);
        } else {
            return BigInteger(subtractVectors(other.digits, digits), !isPositive);
        }
    } else {
        return *this + BigInteger(other.digits, !other.isPositive);
    }
}

BigInteger& BigInteger::operator-=(const BigInteger& other) {
    *this = *this - other;
    return *this;
}

BigInteger BigInteger::operator*(const BigInteger& other) const {
    return BigInteger(multiplyVectors(digits, other.digits), isPositive == other.isPositive);
}

BigInteger& BigInteger::operator*=(const BigInteger& other) {
    *this = *this * other;
    return *this;
}

BigInteger BigInteger::operator/(const BigInteger& other) const {
    return BigInteger(divideVectors(digits, other.digits), isPositive == other.isPositive);
}

BigInteger& BigInteger::operator/=(const BigInteger& other) {
    *this = *this / other;
    return *this;
}

BigInteger BigInteger::operator+(int other) const {
    return *this + BigInteger(std::to_string(other));
}

BigInteger& BigInteger::operator+=(int other) {
    *this = *this + other;
    return *this;
}

BigInteger BigInteger::operator-(int other) const {
    return *this - BigInteger(std::to_string(other));
}

BigInteger& BigInteger::operator-=(int other) {
    *this = *this - other;
    return *this;
}

BigInteger BigInteger::operator*(int other) const {
    return *this * BigInteger(std::to_string(other));
}

BigInteger& BigInteger::operator*=(int other) {
    *this = *this * other;
    return *this;
}

BigInteger BigInteger::operator/(int other) const {
    return *this / BigInteger(std::to_string(other));
}

BigInteger& BigInteger::operator/=(int other) {
    *this = *this / other;
    return *this;
}

BigInteger& BigInteger::operator++() {
    *this += 1;
    return *this;
}

BigInteger BigInteger::operator++(int) {
    BigInteger temp = *this;
    ++(*this);
    return temp;
}

BigInteger& BigInteger::operator--() {
    *this -= 1;
    return *this;
}

BigInteger BigInteger::operator--(int) {
    BigInteger temp = *this;
    --(*this);
    return temp;
}

bool BigInteger::operator==(const BigInteger& other) const {
    return isPositive == other.isPositive && digits == other.digits;
}

bool BigInteger::operator!=(const BigInteger& other) const {
    return !(*this == other);
}

bool BigInteger::operator<(const BigInteger& other) const {
    if (isPositive != other.isPositive) {
        return !isPositive;
    }
    if (digits.size() != other.digits.size()) {
        return isPositive ? digits.size() < other.digits.size() : digits.size() > other.digits.size();
    }
    for (size_t i = digits.size(); i-- > 0;) {
        if (digits[i] != other.digits[i]) {
            return isPositive ? digits[i] < other.digits[i] : digits[i] > other.digits[i];
        }
    }
    return false;
}

bool BigInteger::operator<=(const BigInteger& other) const {
    return *this < other || *this == other;
}

bool BigInteger::operator>(const BigInteger& other) const {
    return !(*this <= other);
}

bool BigInteger::operator>=(const BigInteger& other) const {
    return !(*this < other);
}

bool BigInteger::operator==(int other) const {
    return *this == BigInteger(std::to_string(other));
}

bool BigInteger::operator!=(int other) const {
    return !(*this == other);
}

bool BigInteger::operator<(int other) const {
    return *this < BigInteger(std::to_string(other));
}

bool BigInteger::operator<=(int other) const {
    return *this <= BigInteger(std::to_string(other));
}

bool BigInteger::operator>(int other) const {
    return !(*this <= other);
}

bool BigInteger::operator>=(int other) const {
    return !(*this < other);
}

std::ostream& operator<<(std::ostream& os, const BigInteger& number) {
    if (!number.isPositive) {
        os << '-';
    }
    for (size_t i = number.digits.size(); i-- > 0;) {
        os << number.digits[i];
    }
    return os;
}

std::istream& operator>>(std::istream& is, BigInteger& number) {
    std::string input;
    is >> input;
    number = BigInteger(input);
    return is;
}