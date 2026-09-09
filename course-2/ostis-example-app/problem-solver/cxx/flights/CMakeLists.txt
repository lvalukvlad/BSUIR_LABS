file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

include_directories(${CMAKE_CURRENT_LIST_DIR} ${SC_MEMORY_SRC} ${SC_KPM_SRC} ${INFERENCE_MODULE_PATH})

add_library (flights SHARED ${SOURCES})
target_link_libraries(flights sc-memory sc-agents-common inferenceModule)

sc_codegen_ex(flights ${CMAKE_CURRENT_LIST_DIR} ${CMAKE_CURRENT_LIST_DIR}/generated)
