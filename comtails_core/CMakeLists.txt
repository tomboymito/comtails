cmake_minimum_required(VERSION 3.16)
project(comtails_core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

add_library(comtails_core STATIC
    src/core_cpu.cpp
)
target_include_directories(comtails_core PUBLIC include)

add_executable(comtails_core_tests
    tests/test_core_cpu.cpp
)
target_link_libraries(comtails_core_tests PRIVATE comtails_core)

enable_testing()
add_test(NAME comtails_core_tests COMMAND comtails_core_tests)

add_executable(comtails_core_bench_monte_carlo
    tools/benchmark_monte_carlo.cpp
)
target_link_libraries(comtails_core_bench_monte_carlo PRIVATE comtails_core)

add_executable(comtails_core_bench_parity_dataset
    tools/benchmark_parity_dataset.cpp
)
target_link_libraries(comtails_core_bench_parity_dataset PRIVATE comtails_core)

add_executable(comtails_core_check_parity_regression
    tools/check_parity_regression.cpp
)

add_executable(comtails_core_run_synthetic_tail
    tools/run_synthetic_tail.cpp
)
target_link_libraries(comtails_core_run_synthetic_tail PRIVATE comtails_core)
