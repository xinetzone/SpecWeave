# =============================================================================
# CMakeLists.txt — Free-Threading C Extension Build (cmake + ninja)
# =============================================================================
# Targets Python 3.14t (cpython-314t ABI) with free-threading enabled.
# Usage:
#   cmake -G Ninja -B build -DCMAKE_BUILD_TYPE=Release
#   cmake --build build
# =============================================================================

cmake_minimum_required(VERSION 3.27...3.31)
project(ft_test_ext LANGUAGES C)

# ── Require out-of-source build ──
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR "In-source builds not allowed. Use: cmake -B build")
endif()

# ── Find Python (prefer free-threading 3.14) ──
# Explicitly use the Python from PATH (conda-activated env)
set(Python3_FIND_STRATEGY LOCATION)
set(Python3_FIND_IMPLEMENTATIONS CPython)
# Help cmake find the conda Python development files
if(DEFINED ENV{CONDA_PREFIX})
    set(Python3_ROOT_DIR "$ENV{CONDA_PREFIX}")
    set(Python3_INCLUDE_DIR "$ENV{CONDA_PREFIX}/include/python3.14t")
endif()
find_package(Python3 3.14 REQUIRED COMPONENTS Interpreter Development.Module)

# ── Verify free-threading ABI ──
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c
        "import sysconfig; import sys; ft=sysconfig.get_config_var('Py_GIL_DISABLED'); soabi=sysconfig.get_config_var('SOABI'); sys.exit(0 if ft==1 and 't' in soabi.split('-')[1] else 1)"
    RESULT_VARIABLE PYTHON_FT_CHECK
    OUTPUT_QUIET ERROR_QUIET
)
if(NOT PYTHON_FT_CHECK EQUAL 0)
    message(FATAL_ERROR
        "Python ${Python3_VERSION} at ${Python3_EXECUTABLE} is NOT a free-threading build.\n"
        "This project requires Python 3.13t+ (cpython-31Xt ABI, Py_GIL_DISABLED=1).\n"
        "Activate the 'main' conda env: conda activate main"
    )
endif()

# ── Get SOABI for correct file naming ──
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import sysconfig; print(sysconfig.get_config_var('SOABI'))"
    OUTPUT_VARIABLE PYTHON_SOABI
    OUTPUT_STRIP_TRAILING_WHITESPACE
)
message(STATUS "Python executable: ${Python3_EXECUTABLE}")
message(STATUS "Python version:    ${Python3_VERSION}")
message(STATUS "Python SOABI:      ${PYTHON_SOABI}")
message(STATUS "Free-threading:    YES (Py_GIL_DISABLED=1)")

# ── C extension module ──
python3_add_library(ft_test_ext MODULE src/ft_test_ext.c)

# ── Compiler flags ──
target_compile_options(ft_test_ext PRIVATE
    -O3
    -Wall -Wextra -Wpedantic
    -fno-semantic-interposition
)
target_compile_definitions(ft_test_ext PRIVATE Py_GIL_DISABLED=1)

# ── Set output suffix to match SOABI (Python expects cpython-314t-x86_64-linux-gnu.so) ──
set_target_properties(ft_test_ext PROPERTIES
    PREFIX ""
    SUFFIX ".${PYTHON_SOABI}.so"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

# ── Install/copy to project root for easy import ──
add_custom_command(TARGET ft_test_ext POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        "$<TARGET_FILE:ft_test_ext>"
        "${CMAKE_SOURCE_DIR}/ft_test_ext.so"
    COMMENT "Copying ft_test_ext.so to project root"
)

message(STATUS "")
message(STATUS "=== Build Configuration Summary ===")
message(STATUS "  Build type:       ${CMAKE_BUILD_TYPE}")
message(STATUS "  C compiler:       ${CMAKE_C_COMPILER}")
message(STATUS "  Output:           ${CMAKE_BINARY_DIR}/lib/ft_test_ext.${PYTHON_SOABI}.so")
message(STATUS "====================================")
