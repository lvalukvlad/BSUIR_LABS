cmake_minimum_required(VERSION 3.10)
project(search_module)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Поиск всех исходных файлов
file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

# Добавление библиотеки типа SHARED
add_library(search_module SHARED ${SOURCES})

# Линковка с библиотекой sc-memory
target_link_libraries(search_module PUBLIC sc-memory)

# Включение директорий с заголовочными файлами
target_include_directories(search_module PRIVATE 
    ${CMAKE_CURRENT_SOURCE_DIR}
    /home/ubuntuuser/ostis-web-platform/sc-machine/sc-memory/sc-memory/include
)