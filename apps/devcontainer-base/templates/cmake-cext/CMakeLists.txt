# =============================================================================
# CMakeLists.txt — Free-Threading Python C Extension Template (cmake + ninja)
# =============================================================================
# Targets Python 3.13t+ (cpython-31Xt ABI) with free-threading enabled.
#
# Quick Start:
#   mkdir build && cd build
#   cmake -G Ninja -DCMAKE_BUILD_TYPE=Release ..
#   ninja -j$(nproc)
#   python -c "import <module_name>; <module_name>.run_self_test()"
#
# Variables (can be overridden via -D):
#   MODULE_NAME        - Name of the Python extension module (default: ft_extension)
#   PYTHON_TARGET_VER  - Minimum Python version (default: 3.13)
#   REQUIRE_FT         - Require free-threading build (default: ON)
# =============================================================================

cmake_minimum_required(VERSION 3.27...3.31)

# ── Configurable options ──
set(MODULE_NAME "ft_extension" CACHE STRING "Python extension module name")
set(PYTHON_TARGET_VER "3.13" CACHE STRING "Minimum Python version")
option(REQUIRE_FT "Require free-threading Python build" ON)

project(${MODULE_NAME} LANGUAGES C)

# ── Require out-of-source build ──
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_BINARY_DIR)
    message(FATAL_ERROR "In-source builds not allowed. Use: cmake -B build")
endif()

# ── Find Python (prefer free-threading build from conda env) ──
set(Python3_FIND_STRATEGY LOCATION)
set(Python3_FIND_IMPLEMENTATIONS CPython)

# Help cmake find conda Python development files
if(DEFINED ENV{CONDA_PREFIX})
    set(Python3_ROOT_DIR "$ENV{CONDA_PREFIX}")
    # Try common include paths for free-threading Python
    file(GLOB _PY_INCLUDE_CANDIDATES LIST_DIRECTORIES true
        "$ENV{CONDA_PREFIX}/include/python${PYTHON_TARGET_VER}t"
        "$ENV{CONDA_PREFIX}/include/python${PYTHON_TARGET_VER}*"
    )
    if(_PY_INCLUDE_CANDIDATES)
        list(GET _PY_INCLUDE_CANDIDATES 0 Python3_INCLUDE_DIR)
    endif()
endif()

find_package(Python3 ${PYTHON_TARGET_VER} REQUIRED COMPONENTS Interpreter Development.Module)

# ── Verify free-threading ABI (if required) ──
if(REQUIRE_FT)
    execute_process(
        COMMAND "${Python3_EXECUTABLE}" -c
            "import sysconfig; ft=sysconfig.get_config_var('Py_GIL_DISABLED'); soabi=sysconfig.get_config_var('SOABI') or ''; ver=soabi.split('-')[1] if '-' in soabi else ''; sys.exit(0 if ft==1 and ver.endswith('t') else 1)"
        RESULT_VARIABLE PYTHON_FT_CHECK
        OUTPUT_QUIET ERROR_QUIET
    )
    if(NOT PYTHON_FT_CHECK EQUAL 0)
        message(FATAL_ERROR
            "Python ${Python3_VERSION} at ${Python3_EXECUTABLE} is NOT a free-threading build.\n"
            "This template requires Python ${PYTHON_TARGET_VER}t+ (cpython-31Xt ABI, Py_GIL_DISABLED=1).\n"
            "If using conda: conda activate main (or your ft-enabled env)\n"
            "To disable this check: cmake -DREQUIRE_FT=OFF .."
        )
    endif()
endif()

# ── Get SOABI for correct file naming ──
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import sysconfig; print(sysconfig.get_config_var('SOABI') or 'abi3')"
    OUTPUT_VARIABLE PYTHON_SOABI
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

message(STATUS "")
message(STATUS "=== Python C Extension Build Configuration ===")
message(STATUS "  Module name:      ${MODULE_NAME}")
message(STATUS "  Python executable:${Python3_EXECUTABLE}")
message(STATUS "  Python version:   ${Python3_VERSION}")
message(STATUS "  Python SOABI:     ${PYTHON_SOABI}")
if(REQUIRE_FT)
    message(STATUS "  Free-threading:   YES (Py_GIL_DISABLED=1)")
endif()
message(STATUS "  Build type:       ${CMAKE_BUILD_TYPE}")
message(STATUS "  C compiler:       ${CMAKE_C_COMPILER}")
message(STATUS "==============================================")
message(STATUS "")

# ── C extension module ──
file(GLOB MODULE_SOURCES CONFIGURE_DEPENDS "src/*.c")
python3_add_library(${MODULE_NAME} MODULE ${MODULE_SOURCES})

# ── Compiler flags ──
target_compile_options(${MODULE_NAME} PRIVATE
    -O3
    -Wall -Wextra -Wpedantic
    -fno-semantic-interposition
)
if(REQUIRE_FT)
    target_compile_definitions(${MODULE_NAME} PRIVATE Py_GIL_DISABLED=1)
endif()

# ── Set output suffix to match SOABI ──
# Python expects: <module>.cpython-314t-x86_64-linux-gnu.so
set_target_properties(${MODULE_NAME} PROPERTIES
    PREFIX ""
    SUFFIX ".${PYTHON_SOABI}.so"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

# ── Post-build: copy to project root for easy import ──
add_custom_command(TARGET ${MODULE_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy
        "$<TARGET_FILE:${MODULE_NAME}>"
        "${CMAKE_SOURCE_DIR}/${MODULE_NAME}.so"
    COMMENT "Copying ${MODULE_NAME}.so to project root"
)

# ── CTest integration (optional) ──
enable_testing()
add_test(NAME self_test
    COMMAND "${Python3_EXECUTABLE}" -c "import ${MODULE_NAME}; assert ${MODULE_NAME}.run_self_test()"
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
)
