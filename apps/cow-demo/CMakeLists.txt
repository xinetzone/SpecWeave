cmake_minimum_required(VERSION 3.14)
project(cow_demo LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# 可选：注释掉下面这行来测试编译期完全禁用COW（回退到浅共享模式）
# add_compile_definitions(COW_DISABLED_AT_COMPILE_TIME)

# 线程库（单元测试需要）
find_package(Threads REQUIRED)

# -----------------------------------------------------------------------------
# Demo 可执行文件（带彩色输出的7个场景演示）
# -----------------------------------------------------------------------------
add_executable(cow_demo
    src/main.cpp
)

target_include_directories(cow_demo PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

# MSVC 编译选项
if(MSVC)
    target_compile_options(cow_demo PRIVATE /W4 /permissive-)
else()
    target_compile_options(cow_demo PRIVATE -Wall -Wextra -Wpedantic)
endif()

# -----------------------------------------------------------------------------
# 单元测试可执行文件（静默模式，面向CI）
# -----------------------------------------------------------------------------
add_executable(cow_tests
    tests/test_cow_buffer.cpp
)

target_include_directories(cow_tests PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(cow_tests PRIVATE Threads::Threads)

if(MSVC)
    target_compile_options(cow_tests PRIVATE /W4 /permissive-)
else()
    target_compile_options(cow_tests PRIVATE -Wall -Wextra -Wpedantic)
endif()

# 注册到 CTest
enable_testing()
add_test(NAME cow_unit_tests COMMAND cow_tests)

message(STATUS "cow_demo: Zero-copy COW pattern demo")
message(STATUS "  C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Compiler: ${CMAKE_CXX_COMPILER_ID}")
message(STATUS "  Targets: cow_demo (demo), cow_tests (unit tests)")
