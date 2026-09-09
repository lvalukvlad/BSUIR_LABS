cmake_minimum_required(VERSION 3.10)
project(lab1_vs)

set(CMAKE_CXX_STANDARD 17)

add_library(BigInteger src/BigInteger.cpp)

add_executable(LAB1 src/LAB1.cpp)
target_link_libraries(LAB1 BigInteger)

enable_testing()
add_subdirectory(tests)