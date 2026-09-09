#pragma once
#ifndef BIGINTEGER_H
#define BIGINTEGER_H

#include <vector>
#include <string>
#include <iostream>

class BigInteger {
private:
    std::vector<int> digits;
    bool isPositive;

    std::vector<int> addVectors(const std::vector<int>& a, const std::vector<int>& b) const;
    std::vector<int> subtractVectors(const std::vector<int>& a, const std::vector<int>& b) const;
    std::vector<int> multiplyVectors(const std::vector<int>& a, const std::vector<int>& b) const;
    std::vector<int> divideVectors(const std::vector<int>& a, const std::vector<int>& b) const;

public:
    BigInteger();
    BigInteger(const std::string& number);
    BigInteger(const std::vector<int>& digits, bool isPositive);
    BigInteger(const BigInteger& other);

    BigInteger& operator=(const BigInteger& other);

    operator int() const;

    BigInteger operator+(const BigInteger& other) const;
    BigInteger& operator+=(const BigInteger& other);
    BigInteger operator-(const BigInteger& other) const;
    BigInteger& operator-=(const BigInteger& other);
    BigInteger operator*(const BigInteger& other) const;
    BigInteger& operator*=(const BigInteger& other);
    BigInteger operator/(const BigInteger& other) const;
    BigInteger& operator/=(const BigInteger& other);

    BigInteger operator+(int other) const;
    BigInteger& operator+=(int other);
    BigInteger operator-(int other) const;
    BigInteger& operator-=(int other);
    BigInteger operator*(int other) const;
    BigInteger& operator*=(int other);
    BigInteger operator/(int other) const;
    BigInteger& operator/=(int other);

    BigInteger& operator++();
    BigInteger operator++(int);
    BigInteger& operator--();
    BigInteger operator--(int);

    bool operator==(const BigInteger& other) const;
    bool operator!=(const BigInteger& other) const;
    bool operator<(const BigInteger& other) const;
    bool operator<=(const BigInteger& other) const;
    bool operator>(const BigInteger& other) const;
    bool operator>=(const BigInteger& other) const;

    bool operator==(int other) const;
    bool operator!=(int other) const;
    bool operator<(int other) const;
    bool operator<=(int other) const;
    bool operator>(int other) const;
    bool operator>=(int other) const;

    friend std::ostream& operator<<(std::ostream& os, const BigInteger& number);
    friend std::istream& operator>>(std::istream& is, BigInteger& number);
};

#endif // BIGINTEGER_H