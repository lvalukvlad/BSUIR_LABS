file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

add_library(tupik SHARED ${SOURCES})
target_link_libraries(tupik
    LINK_PRIVATE sc-memory
    LINK_PRIVATE sc-agents-common
)
target_include_directories(tupik
    PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
)