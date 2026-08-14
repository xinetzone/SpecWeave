#!/bin/bash
set -euo pipefail

# This script runs inside the container with conda already activated
mkdir -p /tmp/cext-build
cd /tmp/cext-build

# Create source files
mkdir -p src

cat > src/ft_extension.c << 'CEOF'
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdatomic.h>
#include <string.h>

#if defined(Py_GIL_DISABLED)
#  define FT_BUILD 1
#else
#  define FT_BUILD 0
#endif

typedef struct {
    atomic_long counter;
} ModuleState;

static PyObject*
ft_sum_of_squares(PyObject* self, PyObject* args)
{
    (void)self;
    long n;
    if (!PyArg_ParseTuple(args, "l", &n)) return NULL;
    if (n < 0) n = 0;
    if (n > 10000000) n = 10000000;
    long long result = 0;
    Py_BEGIN_ALLOW_THREADS
    for (long i = 1; i <= n; i++) result += (long long)i * i;
    Py_END_ALLOW_THREADS
    return PyLong_FromLongLong(result);
}

static PyObject*
ft_atomic_increment(PyObject* self, PyObject* args)
{
    long amount = 1;
    if (!PyArg_ParseTuple(args, "|l", &amount)) return NULL;
    ModuleState* state = PyModule_GetState(self);
    if (!state) { PyErr_SetString(PyExc_RuntimeError, "no state"); return NULL; }
    long old = atomic_fetch_add_explicit(&state->counter, amount, memory_order_relaxed);
    return PyLong_FromLong(old + amount);
}

static PyObject*
ft_atomic_get(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    ModuleState* state = PyModule_GetState(self);
    if (!state) { PyErr_SetString(PyExc_RuntimeError, "no state"); return NULL; }
    return PyLong_FromLong(atomic_load_explicit(&state->counter, memory_order_relaxed));
}

static PyObject*
ft_atomic_reset(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    ModuleState* state = PyModule_GetState(self);
    if (!state) { PyErr_SetString(PyExc_RuntimeError, "no state"); return NULL; }
    atomic_store_explicit(&state->counter, 0, memory_order_relaxed);
    Py_RETURN_NONE;
}

static PyObject*
ft_run_self_test(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    (void)self;
    int passed = 0, total = 0;
#define CHECK(name, cond) do { total++; if (cond) { passed++; printf("  [PASS] %s\n", name); } else { printf("  [FAIL] %s\n", name); } } while(0)
    printf("=== ft_extension Self-Test ===\n");
    PyObject* r = ft_sum_of_squares(self, Py_BuildValue("(l)", 100L));
    CHECK("sum_of_squares(100)==338350", r && PyLong_Check(r) && PyLong_AsLongLong(r) == 338350LL);
    Py_XDECREF(r);
    ft_atomic_reset(self, NULL);
    r = ft_atomic_increment(self, Py_BuildValue("(l)", 42L));
    CHECK("atomic_increment(42)==42", r && PyLong_Check(r) && PyLong_AsLong(r) == 42);
    Py_XDECREF(r);
    r = ft_atomic_get(self, NULL);
    CHECK("atomic_get==42", r && PyLong_Check(r) && PyLong_AsLong(r) == 42);
    Py_XDECREF(r);
    printf("\n  Result: %d/%d passed\n", passed, total);
    ft_atomic_reset(self, NULL);
    return (passed == total) ? Py_True : Py_False;
#undef CHECK
}

static PyObject*
ft_thread_stress(PyObject* self, PyObject* args)
{
    (void)self;
    long n_threads = 8, n_iterations = 100000;
    if (!PyArg_ParseTuple(args, "|ll", &n_threads, &n_iterations)) return NULL;
    if (n_threads < 1) n_threads = 1;
    if (n_threads > 64) n_threads = 64;
    if (n_iterations < 1) n_iterations = 1;
    PyObject* threading = PyImport_ImportModule("threading");
    if (!threading) return NULL;
    PyObject* Thread = PyObject_GetAttrString(threading, "Thread");
    if (!Thread) { Py_DECREF(threading); return NULL; }
    ft_atomic_reset(self, NULL);
    PyObject* worker_code = Py_CompileString(
        "import ft_extension\n"
        "def worker(n):\n"
        "    for _ in range(n):\n"
        "        ft_extension.atomic_increment(1)\n",
        "<stress>", Py_file_input);
    if (!worker_code) { Py_DECREF(Thread); Py_DECREF(threading); return NULL; }
    PyObject* worker_mod = PyImport_ExecCodeModule("_ft_worker", worker_code);
    Py_DECREF(worker_code);
    if (!worker_mod) { Py_DECREF(Thread); Py_DECREF(threading); return NULL; }
    PyObject* worker_fn = PyObject_GetAttrString(worker_mod, "worker");
    if (!worker_fn) { Py_DECREF(worker_mod); Py_DECREF(Thread); Py_DECREF(threading); return NULL; }
    PyObject* threads = PyList_New(n_threads);
    for (long i = 0; i < n_threads; i++) {
        PyObject* t_args = PyTuple_Pack(1, PyLong_FromLong(n_iterations));
        PyObject* t_kwargs = Py_BuildValue("{s:O,s:O}", "target", worker_fn, "args", t_args);
        PyObject* t = PyObject_Call(Thread, PyTuple_New(0), t_kwargs);
        Py_XDECREF(t_args); Py_XDECREF(t_kwargs);
        if (!t) { Py_DECREF(threads); Py_DECREF(worker_fn); Py_DECREF(worker_mod); Py_DECREF(Thread); Py_DECREF(threading); return NULL; }
        PyList_SET_ITEM(threads, i, t);
    }
    for (long i = 0; i < n_threads; i++) {
        PyObject* t = PyList_GetItem(threads, i);
        PyObject* start = PyObject_GetAttrString(t, "start");
        if (start) { PyObject_CallNoArgs(start); Py_DECREF(start); }
    }
    for (long i = 0; i < n_threads; i++) {
        PyObject* t = PyList_GetItem(threads, i);
        PyObject* join = PyObject_GetAttrString(t, "join");
        if (join) { PyObject_CallNoArgs(join); Py_DECREF(join); }
    }
    long expected = n_threads * n_iterations;
    PyObject* final_val = ft_atomic_get(self, NULL);
    long actual = final_val ? PyLong_AsLong(final_val) : -1;
    Py_XDECREF(final_val);
    Py_DECREF(threads); Py_DECREF(worker_fn); Py_DECREF(worker_mod); Py_DECREF(Thread); Py_DECREF(threading);
    return Py_BuildValue("{s:l,s:l,s:l,s:O,s:O}",
        "threads", n_threads, "iterations_per_thread", n_iterations,
        "expected_total", expected, "actual_total", PyLong_FromLong(actual),
        "correct", (actual == expected) ? Py_True : Py_False);
}

static PyMethodDef Methods[] = {
    {"sum_of_squares", ft_sum_of_squares, METH_VARARGS, "sum(n)"},
    {"atomic_increment", ft_atomic_increment, METH_VARARGS, "atomic increment"},
    {"atomic_get", ft_atomic_get, METH_NOARGS, "get counter"},
    {"atomic_reset", ft_atomic_reset, METH_NOARGS, "reset counter"},
    {"run_self_test", ft_run_self_test, METH_NOARGS, "self test"},
    {"thread_stress", ft_thread_stress, METH_VARARGS, "thread stress test"},
    {NULL, NULL, 0, NULL}
};

static int module_exec(PyObject* module) {
    ModuleState* state = PyModule_GetState(module);
    if (!state) return -1;
    atomic_init(&state->counter, 0);
    return 0;
}

static PyModuleDef_Slot Slots[] = {
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_exec, (void*)module_exec},
    {0, NULL}
};

static struct PyModuleDef def = {
    PyModuleDef_HEAD_INIT, "ft_extension", "Free-threading C extension template test",
    sizeof(ModuleState), Methods, Slots, NULL, NULL, NULL
};

PyMODINIT_FUNC PyInit_ft_extension(void) { return PyModuleDef_Init(&def); }
CEOF

cat > CMakeLists.txt << 'CMEOF'
cmake_minimum_required(VERSION 3.27)
project(ft_extension LANGUAGES C)
set(Python3_FIND_STRATEGY LOCATION)
set(Python3_FIND_IMPLEMENTATIONS CPython)
find_package(Python3 3.13 REQUIRED COMPONENTS Interpreter Development.Module)
execute_process(
    COMMAND "${Python3_EXECUTABLE}" -c "import sysconfig; ft=sysconfig.get_config_var('Py_GIL_DISABLED'); soabi=sysconfig.get_config_var('SOABI') or ''; ver=soabi.split('-')[1] if '-' in soabi else ''; sys.exit(0 if ft==1 and ver.endswith('t') else 1)"
    RESULT_VARIABLE IS_FT OUTPUT_QUIET ERROR_QUIET)
if(NOT IS_FT EQUAL 0)
    message(FATAL_ERROR "Not free-threading Python!")
endif()
execute_process(COMMAND "${Python3_EXECUTABLE}" -c "import sysconfig; print(sysconfig.get_config_var('SOABI'))"
    OUTPUT_VARIABLE PYTHON_SOABI OUTPUT_STRIP_TRAILING_WHITESPACE)
message(STATUS "Python: ${Python3_EXECUTABLE}, SOABI: ${PYTHON_SOABI}")
python3_add_library(ft_extension MODULE src/ft_extension.c)
target_compile_options(ft_extension PRIVATE -O3 -Wall -Wextra)
target_compile_definitions(ft_extension PRIVATE Py_GIL_DISABLED=1)
set_target_properties(ft_extension PROPERTIES PREFIX "" SUFFIX ".${PYTHON_SOABI}.so" LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
add_custom_command(TARGET ft_extension POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy "$<TARGET_FILE:ft_extension>" "${CMAKE_SOURCE_DIR}/ft_extension.so")
CMEOF

echo "=== Configuring with CMake + Ninja ==="
cmake -G Ninja -B build -DCMAKE_BUILD_TYPE=Release .

echo ""
echo "=== Building ==="
cmake --build build -j$(nproc)

echo ""
echo "=== Verifying output ==="
ls -la ft_extension.so

echo ""
echo "=== Checking Python ABI ==="
python -c "import sysconfig; print('SOABI:', sysconfig.get_config_var('SOABI')); print('FT:', sysconfig.get_config_var('Py_GIL_DISABLED'))"

echo ""
echo "=== Running self-test ==="
python -c "import ft_extension; assert ft_extension.run_self_test(), 'Self-test FAILED'"
echo "Self-test PASSED"

echo ""
echo "=== Running 8-thread stress test (100K iterations each) ==="
python -c "
import ft_extension
r = ft_extension.thread_stress(8, 100000)
print(f'Threads: {r[\"threads\"]}')
print(f'Iter/thread: {r[\"iterations_per_thread\"]}')
print(f'Expected: {r[\"expected_total\"]}')
print(f'Actual: {r[\"actual_total\"]}')
print(f'Correct: {r[\"correct\"]}')
assert r['correct'], f'RACE CONDITION! Expected {r[\"expected_total\"]}, got {r[\"actual_total\"]}'
print('Stress test PASSED')
"

echo ""
echo "=== All tests PASSED ==="
