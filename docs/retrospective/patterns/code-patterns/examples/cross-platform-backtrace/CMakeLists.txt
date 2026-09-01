cmake_minimum_required(VERSION 3.15)
project(backtrace-leak-demo VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

option(DEMO_ENABLE_BACKTRACE "Enable stack backtrace for leak diagnosis" ON)
option(DEMO_ENABLE_LOG "Enable debug logging" ON)

add_executable(leak_demo demo.cc)

target_include_directories(leak_demo PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

if(DEMO_ENABLE_BACKTRACE)
  target_compile_definitions(leak_demo PRIVATE DEMO_ENABLE_BACKTRACE)
endif()

if(DEMO_ENABLE_LOG)
  target_compile_definitions(leak_demo PRIVATE DEMO_ENABLE_LOG)
endif()

if(MSVC)
  target_compile_definitions(leak_demo PRIVATE
    WIN32_LEAN_AND_MEAN
    _CRT_SECURE_NO_WARNINGS
    NOMINMAX
  )
  target_compile_options(leak_demo PRIVATE /W3 /Zi)
  if(DEMO_ENABLE_BACKTRACE)
    target_link_libraries(leak_demo PRIVATE DbgHelp.lib)
  endif()
else()
  target_compile_options(leak_demo PRIVATE -Wall -Wextra -Wno-unused-parameter)
  target_link_libraries(leak_demo PRIVATE pthread)
endif()

message(STATUS "=== Backtrace Leak Demo Build Configuration ===")
message(STATUS "  Backtrace support: ${DEMO_ENABLE_BACKTRACE}")
message(STATUS "  Debug logging:    ${DEMO_ENABLE_LOG}")
message(STATUS "  Compiler:         ${CMAKE_CXX_COMPILER_ID}")
message(STATUS "===============================================")
