file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

add_library(svyazModule SHARED ${SOURCES})
target_link_libraries(svyazModule
    LINK_PRIVATE sc-memory
    LINK_PRIVATE sc-agents-common
)
target_include_directories(svyazModule
    PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}
)