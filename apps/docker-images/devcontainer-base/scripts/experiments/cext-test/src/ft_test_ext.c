/*
 * ft_test_ext.c — Free-Threading C Extension Test Module
 * =============================================================================
 * A minimal C extension to verify:
 *   1. Compilation against Python 3.14t (cpython-314t ABI) works with cmake+ninja
 *   2. Module loads correctly on free-threading Python
 *   3. C extension functions execute without GIL crashes
 *   4. Multi-threaded concurrent calls are safe
 *
 * Build: cmake -G Ninja -B build && cmake --build build
 * Test:  python -c "import ft_test_ext; ft_test_ext.run_self_test()"
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdatomic.h>
#include <string.h>
#include <math.h>

/* If Py_GIL_DISABLED is defined, we're on free-threading Python */
#if !defined(Py_GIL_DISABLED)
#warning "Compiling without Py_GIL_DISABLED - this module targets free-threading Python 3.13t+"
#endif

/* ── Module state ─────────────────────────────────────────────── */
typedef struct {
    atomic_long counter;  /* Atomic counter for thread-safety testing */
} FtTestState;

/* ── 1. Simple computation: sum of squares (releases GIL) ─────── */
static PyObject*
ft_sum_of_squares(PyObject* self, PyObject* args)
{
    (void)self;
    long n;
    if (!PyArg_ParseTuple(args, "l", &n)) {
        return NULL;
    }
    if (n < 0) n = 0;
    if (n > 10000000) n = 10000000;

    long long result = 0;
    /* Release the GIL for CPU-bound work */
    Py_BEGIN_ALLOW_THREADS
    for (long i = 1; i <= n; i++) {
        result += (long long)i * i;
    }
    Py_END_ALLOW_THREADS

    return PyLong_FromLongLong(result);
}

/* ── 2. Thread-safe atomic counter (no GIL needed for atomic ops) ── */
static PyObject*
ft_atomic_increment(PyObject* self, PyObject* args)
{
    long amount = 1;
    if (!PyArg_ParseTuple(args, "|l", &amount)) {
        return NULL;
    }
    FtTestState* state = PyModule_GetState(self);
    if (!state) {
        PyErr_SetString(PyExc_RuntimeError, "Cannot get module state");
        return NULL;
    }
    long val = atomic_fetch_add_explicit(&state->counter, amount, memory_order_relaxed) + amount;
    return PyLong_FromLong(val);
}

static PyObject*
ft_atomic_get(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    FtTestState* state = PyModule_GetState(self);
    if (!state) {
        PyErr_SetString(PyExc_RuntimeError, "Cannot get module state");
        return NULL;
    }
    long val = atomic_load_explicit(&state->counter, memory_order_relaxed);
    return PyLong_FromLong(val);
}

static PyObject*
ft_atomic_reset(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    FtTestState* state = PyModule_GetState(self);
    if (!state) {
        PyErr_SetString(PyExc_RuntimeError, "Cannot get module state");
        return NULL;
    }
    atomic_store_explicit(&state->counter, 0, memory_order_relaxed);
    Py_RETURN_NONE;
}

/* ── 3. String processing (GIL-required Python object access) ─── */
static PyObject*
ft_string_repeat(PyObject* self, PyObject* args)
{
    (void)self;
    const char* s;
    Py_ssize_t count;
    if (!PyArg_ParseTuple(args, "sn", &s, &count)) {
        return NULL;
    }
    if (count < 0) count = 0;
    if (count > 10000) count = 10000;
    Py_ssize_t slen = strlen(s);
    Py_ssize_t buflen = slen * count + 1;
    char* buf = (char*)PyMem_Malloc(buflen);
    if (!buf) return PyErr_NoMemory();
    for (Py_ssize_t i = 0; i < count; i++) {
        memcpy(buf + i * slen, s, slen);
    }
    buf[buflen - 1] = '\0';
    PyObject* result = PyUnicode_FromString(buf);
    PyMem_Free(buf);
    return result;
}

/* ── 4. Get build info (compile-time vs runtime ABI check) ────── */
static PyObject*
ft_build_info(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    (void)self;
    PyObject* info = PyDict_New();
    if (!info) return NULL;

    /* Compile-time info */
    PyDict_SetItemString(info, "compile_python_version",
                         PyUnicode_FromString(PY_VERSION));
#ifdef Py_GIL_DISABLED
    PyDict_SetItemString(info, "compile_free_threading", Py_True);
#else
    PyDict_SetItemString(info, "compile_free_threading", Py_False);
#endif
#ifdef Py_DEBUG
    PyDict_SetItemString(info, "compile_debug", Py_True);
#else
    PyDict_SetItemString(info, "compile_debug", Py_False);
#endif

    /* Runtime info */
    PyObject* sys = PyImport_ImportModule("sys");
    if (sys) {
        PyObject* pyver = PyObject_GetAttrString(sys, "version");
        if (pyver) {
            PyDict_SetItemString(info, "runtime_python_version", pyver);
            Py_DECREF(pyver);
        }
        PyObject* gil = PyObject_GetAttrString(sys, "_is_gil_enabled");
        if (gil) {
            PyObject* res = PyObject_CallNoArgs(gil);
            if (res) {
                /* In free-threading build, _is_gil_enabled() returns False by default */
                PyDict_SetItemString(info, "runtime_gil_enabled", res);
                Py_DECREF(res);
            }
            Py_DECREF(gil);
        }
        Py_DECREF(sys);
    }

    /* SOABI from sysconfig */
    PyObject* sysconfig = PyImport_ImportModule("sysconfig");
    if (sysconfig) {
        PyObject* get_fn = PyObject_GetAttrString(sysconfig, "get_config_var");
        if (get_fn) {
            PyObject* soabi_args = PyTuple_Pack(1, PyUnicode_FromString("SOABI"));
            if (soabi_args) {
                PyObject* soabi = PyObject_CallObject(get_fn, soabi_args);
                if (soabi) {
                    PyDict_SetItemString(info, "soabi", soabi);
                    Py_DECREF(soabi);
                }
                Py_DECREF(soabi_args);
            }
            Py_DECREF(get_fn);
        }
        Py_DECREF(sysconfig);
    }

    return info;
}

/* ── 5. Self-test function ────────────────────────────────────── */
static PyObject*
ft_run_self_test(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    (void)self;
    int passed = 0;
    int total = 0;

#define CHECK(name, cond) do { \
    total++; \
    if (cond) { passed++; printf("  [PASS] %s\n", name); } \
    else { printf("  [FAIL] %s\n", name); } \
} while(0)

    printf("=== ft_test_ext Self-Test ===\n");

    /* Test 1: sum_of_squares correctness */
    PyObject* r = ft_sum_of_squares(self, Py_BuildValue("(l)", 100L));
    CHECK("sum_of_squares(100) correct",
          r && PyLong_Check(r) && PyLong_AsLongLong(r) == 338350LL);
    Py_XDECREF(r);

    /* Test 2: atomic counter */
    ft_atomic_reset(self, NULL);
    r = ft_atomic_increment(self, Py_BuildValue("(l)", 42L));
    CHECK("atomic_increment(42) returns 42",
          r && PyLong_AsLong(r) == 42);
    Py_XDECREF(r);
    r = ft_atomic_get(self, NULL);
    CHECK("atomic_get returns 42 after increment",
          r && PyLong_AsLong(r) == 42);
    Py_XDECREF(r);

    /* Test 3: string_repeat */
    r = ft_string_repeat(self, Py_BuildValue("(sn)", "ab", 3L));
    const char* rs = r ? PyUnicode_AsUTF8(r) : NULL;
    CHECK("string_repeat('ab', 3) == 'ababab'",
          rs && strcmp(rs, "ababab") == 0);
    Py_XDECREF(r);

    /* Test 4: build info */
    r = ft_build_info(self, NULL);
    CHECK("build_info returns dict",
          r && PyDict_Check(r));
    if (r && PyDict_Check(r)) {
        PyObject* soabi = PyDict_GetItemString(r, "soabi");
        CHECK("SOABI contains cpython-314t",
              soabi && PyUnicode_Check(soabi) &&
              strstr(PyUnicode_AsUTF8(soabi), "cpython-314t") != NULL);
        PyObject* ft = PyDict_GetItemString(r, "compile_free_threading");
        CHECK("compiled with free-threading support",
              ft && PyObject_IsTrue(ft));
    }
    Py_XDECREF(r);

    ft_atomic_reset(self, NULL);

    printf("\n  Result: %d/%d passed\n", passed, total);
    printf("==============================\n");

    if (passed == total) {
        Py_RETURN_TRUE;
    } else {
        Py_RETURN_FALSE;
    }
#undef CHECK
}

/* ── Multi-thread stress test (called from Python) ────────────── */
static PyObject*
ft_thread_stress(PyObject* self, PyObject* args)
{
    (void)self;
    long n_threads = 8;
    long n_iterations = 100000;
    if (!PyArg_ParseTuple(args, "|ll", &n_threads, &n_iterations)) {
        return NULL;
    }
    if (n_threads < 1) n_threads = 1;
    if (n_threads > 64) n_threads = 64;
    if (n_iterations < 1) n_iterations = 1;
    if (n_iterations > 10000000) n_iterations = 10000000;

    /* Use Python threading to run concurrent atomic increments */
    /* This tests that the GIL-disabled environment doesn't crash
       when multiple threads call C extension functions simultaneously */
    PyObject* threading = PyImport_ImportModule("threading");
    if (!threading) return NULL;
    PyObject* Thread = PyObject_GetAttrString(threading, "Thread");
    if (!Thread) { Py_DECREF(threading); return NULL; }

    ft_atomic_reset(self, NULL);

    /* Create a Python worker script */
    PyObject* worker_code = Py_CompileString(
        "import ft_test_ext\n"
        "def worker(n):\n"
        "    for _ in range(n):\n"
        "        ft_test_ext.atomic_increment(1)\n",
        "<stress_test>", Py_file_input);
    if (!worker_code) { Py_DECREF(Thread); Py_DECREF(threading); return NULL; }

    PyObject* worker_mod = PyImport_ExecCodeModule("_ft_stress_worker", worker_code);
    Py_DECREF(worker_code);
    if (!worker_mod) { Py_DECREF(Thread); Py_DECREF(threading); return NULL; }

    PyObject* worker_fn = PyObject_GetAttrString(worker_mod, "worker");
    if (!worker_fn) { Py_DECREF(worker_mod); Py_DECREF(Thread); Py_DECREF(threading); return NULL; }

    PyObject* threads = PyList_New(n_threads);
    for (long i = 0; i < n_threads; i++) {
        PyObject* t_args = PyTuple_Pack(1, PyLong_FromLong(n_iterations));
        PyObject* t_kwargs = Py_BuildValue("{s:O,s:O}", "target", worker_fn, "args", t_args);
        PyObject* t = PyObject_Call(Thread, PyTuple_New(0), t_kwargs);
        Py_XDECREF(t_args);
        Py_XDECREF(t_kwargs);
        if (!t) {
            Py_DECREF(threads); Py_DECREF(worker_fn);
            Py_DECREF(worker_mod); Py_DECREF(Thread); Py_DECREF(threading);
            return NULL;
        }
        PyList_SET_ITEM(threads, i, t);
    }

    /* Start all threads */
    for (long i = 0; i < n_threads; i++) {
        PyObject* t = PyList_GetItem(threads, i);
        PyObject* start = PyObject_GetAttrString(t, "start");
        if (start) { PyObject_CallNoArgs(start); Py_DECREF(start); }
    }
    /* Join all threads */
    for (long i = 0; i < n_threads; i++) {
        PyObject* t = PyList_GetItem(threads, i);
        PyObject* join = PyObject_GetAttrString(t, "join");
        if (join) { PyObject_CallNoArgs(join); Py_DECREF(join); }
    }

    long expected = n_threads * n_iterations;
    PyObject* final_val = ft_atomic_get(self, NULL);
    long actual = final_val ? PyLong_AsLong(final_val) : -1;
    Py_XDECREF(final_val);

    Py_DECREF(threads);
    Py_DECREF(worker_fn);
    Py_DECREF(worker_mod);
    Py_DECREF(Thread);
    Py_DECREF(threading);

    return Py_BuildValue("{s:l,s:l,s:l,s:O}",
        "threads", n_threads,
        "iterations_per_thread", n_iterations,
        "expected_total", expected,
        "actual_total", PyLong_FromLong(actual),
        "correct", (actual == expected) ? Py_True : Py_False
    );
}

/* ── Module definition ────────────────────────────────────────── */
static PyMethodDef FtTestMethods[] = {
    {"sum_of_squares", ft_sum_of_squares, METH_VARARGS,
     "sum_of_squares(n) -> int\nCompute sum of 1^2+2^2+...+n^2 (releases GIL)"},
    {"atomic_increment", ft_atomic_increment, METH_VARARGS,
     "atomic_increment([amount=1]) -> int\nThread-safe atomic counter increment"},
    {"atomic_get", ft_atomic_get, METH_NOARGS,
     "atomic_get() -> int\nGet current atomic counter value"},
    {"atomic_reset", ft_atomic_reset, METH_NOARGS,
     "atomic_reset() -> None\nReset atomic counter to 0"},
    {"string_repeat", ft_string_repeat, METH_VARARGS,
     "string_repeat(s, n) -> str\nRepeat string s n times"},
    {"build_info", ft_build_info, METH_NOARGS,
     "build_info() -> dict\nReturn compile-time and runtime build info"},
    {"run_self_test", ft_run_self_test, METH_NOARGS,
     "run_self_test() -> bool\nRun self-tests and return True if all pass"},
    {"thread_stress", ft_thread_stress, METH_VARARGS,
     "thread_stress([n_threads=8], [n_iter=100000]) -> dict\nMulti-threaded stress test"},
    {NULL, NULL, 0, NULL}
};

static int
ft_test_ext_exec(PyObject* module)
{
    FtTestState* state = PyModule_GetState(module);
    if (!state) return -1;
    atomic_init(&state->counter, 0);
    return 0;
}

static PyModuleDef_Slot FtTestSlots[] = {
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_exec, (void*)ft_test_ext_exec},
    {0, NULL}
};

static struct PyModuleDef ft_test_module = {
    PyModuleDef_HEAD_INIT,
    "ft_test_ext",
    "Free-Threading C Extension Test Module — built with cmake+ninja for Python 3.14t",
    sizeof(FtTestState),   /* m_size for per-module state */
    FtTestMethods,
    FtTestSlots,
    NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit_ft_test_ext(void)
{
    return PyModuleDef_Init(&ft_test_module);
}
