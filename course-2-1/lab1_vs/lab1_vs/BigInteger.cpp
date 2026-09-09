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
    for (size_t i = 0; i < maxSize; ++i) {
        int sum = carry;
        if (i < a.size()) sum += a[i];
        if (i < b.size()) sum += b[i];
        carry = sum / 10;
        result.push_back(sum % 10);
    }
    if (carry) result.push_back(carry);
    return result;
}

std::vector<int> BigInteger::subtractVectors(const std::vector<int>& a, const std::vector<int>& b) const {
    std::vector<int> result;
    int borrow = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        int diff = a[i] - borrow - (i < b.size() ? b[i] : 0);
        borrow = (diff < 0) ? 1 : 0;
        result.push_back((diff + 10) % 10);
    }
    while (result.size() > 1 && result.back() == 0) {
        result.pop_back();
    }
    return result;
}

std::vector<int> BigInteger::multiplyVectors(const std::vector<int>& a, const std::vector<int>& b) const {
    std::vector<int> result(a.size() + b.size(), 0);
    for (size_t i = 0; i < a.size(); ++i) {
        for (size_t j = 0; j < b.size(); ++j) {
            result[i + j] += a[i] * b[j];
            result[i + j + 1] += result[i + j] / 10;
            result[i + j] %= 10;
        }
    }
    while (result.size() > 1 && result.back() == 0) {
        result.pop_back();
    }
    return result;
}

std::vector<int> BigInteger::divideVectors(const std::vector<int>& a, const std::vector<int>& b) const {
    if (b == std::vector<int>{0}) {
        std::cerr << "Ошибка: Деление на ноль" << std::endl;
        return {};
    }
    std::vector<int> result;
    BigInteger dividend(a, true);
    BigInteger divisor(b, true);
    dividend.isPositive = true;
    divisor.isPositive = true;
    while (dividend >= divisor) {
        BigInteger temp = divisor;
        int count = 0;
        while (dividend >= temp) {
            temp = temp * 10;
            ++count;
        }
        temp = temp / 10;
        --count;
        dividend = dividend - temp;
        result.push_back(count);
    }
    std::reverse(result.begin(), result.end());
    return result;
}

BigInteger BigInteger::operator+(const BigInteger& other) const {
    BigInteger result;
    if (isPositive == other.isPositive) {
        result.digits = addVectors(digits, other.digits);
        result.isPositive = isPositive;
    }
    else {
        if (digits == other.digits) {
            return BigInteger("0");
        }
        if (digits > other.digits) {
            result.digits = subtractVectors(digits, other.digits);
            result.isPositive = isPositive;
        }
        else {
            result.digits = subtractVectors(other.digits, digits);
            result.isPositive = other.isPositive;
        }
    }
    return result;
}

BigInteger& BigInteger::operator+=(const BigInteger& other) {
    *this = *this + other;
    return *this;
}

BigInteger BigInteger::operator-(const BigInteger& other) const {
    BigInteger result;
    if (isPositive != other.isPositive) {
        result.digits = addVectors(digits, other.digits);
        result.isPositive = isPositive;
    }
    else {
        if (digits == other.digits) {
            return BigInteger("0");
        }
        if (digits > other.digits) {
            result.digits = subtractVectors(digits, other.digits);
            result.isPositive = isPositive;
        }
        else {
            result.digits = subtractVectors(other.digits, digits);
            result.isPositive = !isPositive;
        }
    }
    return result;
}

BigInteger& BigInteger::operator-=(const BigInteger& other) {
    *this = *this - other;
    return *this;
}

BigInteger BigInteger::operator*(const BigInteger& other) const {
    BigInteger result;
    result.digits = multiplyVectors(digits, other.digits);
    result.isPositive = (isPositive == other.isPositive);
    return result;
}

BigInteger& BigInteger::operator*=(const BigInteger& other) {
    *this = *this * other;
    return *this;
}

BigInteger BigInteger::operator/(const BigInteger& other) const {
    BigInteger result;
    result.digits = divideVectors(digits, other.digits);
    result.isPositive = (isPositive == other.isPositive);
    return result;
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
    return *this > BigInteger(std::to_string(other));
}

bool BigInteger::operator>=(int other) const {
    return *this >= BigInteger(std::to_string(other));
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