/*
 * ft_extension.c — Free-Threading Python C Extension Template
 * =============================================================================
 * A minimal but complete template for building Python 3.13t+ C extensions
 * that work safely in free-threading (no-GIL) mode.
 *
 * Features demonstrated:
 *   1. GIL-safe module declaration (Py_mod_gil slot)
 *   2. Atomic operations for thread-safe shared state (stdatomic.h)
 *   3. GIL release for CPU-bound work (Py_BEGIN_ALLOW_THREADS)
 *   4. Per-module state (m_size > 0) for thread safety
 *   5. Self-test and multi-thread stress test
 *
 * Build: see ../CMakeLists.txt
 * Usage:
 *   import ft_extension
 *   ft_extension.run_self_test()
 *   ft_extension.thread_stress(8, 100000)  # 8 threads × 100K iterations
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdatomic.h>
#include <string.h>
#include <math.h>

/* Free-threading build detection */
#if defined(Py_GIL_DISABLED)
#  define FT_BUILD 1
#else
#  define FT_BUILD 0
#  warning "Compiling without Py_GIL_DISABLED - this module targets free-threading Python 3.13t+"
#endif

/* ── Module state ─────────────────────────────────────────────── */
/*
 * IMPORTANT: Use per-module state (m_size > 0) instead of global variables
 * for thread safety in free-threading builds. Global variables shared across
 * sub-interpreters or multiple module instances cause data races.
 */
typedef struct {
    atomic_long counter;  /* Atomic counter - safe for concurrent access */
} ModuleState;

/* ── Example 1: CPU-bound computation (releases GIL) ─────────── */
/*
 * BEST PRACTICE: For CPU-heavy pure C computation (no Python API calls),
 * release the GIL with Py_BEGIN_ALLOW_THREADS / Py_END_ALLOW_THREADS.
 * This allows true parallel execution on multiple cores in free-threading mode.
 *
 * WARNING: Do NOT call ANY Python C API functions while the GIL is released!
 * No Py_XDECREF, no PyLong_From*, no PyObject_Call*, nothing. Only pure C.
 */
static PyObject*
ft_sum_of_squares(PyObject* self, PyObject* args)
{
    (void)self;  /* Suppress unused parameter warning */
    long n;
    if (!PyArg_ParseTuple(args, "l", &n)) {
        return NULL;
    }
    /* Clamp input to reasonable range */
    if (n < 0) n = 0;
    if (n > 10000000) n = 10000000;

    /*
     * Declare variables used across the GIL release boundary OUTSIDE
     * Py_BEGIN_ALLOW_THREADS. Variables declared inside the block are
     * not accessible after Py_END_ALLOW_THREADS.
     */
    long long result = 0;

    Py_BEGIN_ALLOW_THREADS
    /* ─── GIL released: pure C computation only ─── */
    for (long i = 1; i <= n; i++) {
        result += (long long)i * i;
    }
    Py_END_ALLOW_THREADS
    /* ─── GIL reacquired: safe to call Python API again ─── */

    return PyLong_FromLongLong(result);
}

/* ── Example 2: Thread-safe atomic counter ───────────────────── */
/*
 * BEST PRACTICE: Use C11 stdatomic.h for shared mutable state.
 * Atomic operations are guaranteed to be race-free without the GIL.
 * memory_order_relaxed is sufficient for simple counters (no ordering
 * constraints with other memory operations).
 */
static PyObject*
ft_atomic_increment(PyObject* self, PyObject* args)
{
    long amount = 1;
    if (!PyArg_ParseTuple(args, "|l", &amount)) {
        return NULL;
    }
    ModuleState* state = PyModule_GetState(self);
    if (!state) {
        PyErr_SetString(PyExc_RuntimeError, "Cannot get module state");
        return NULL;
    }
    /* atomic_fetch_add returns the OLD value; add amount to get new value */
    long old_val = atomic_fetch_add_explicit(&state->counter, amount,
                                             memory_order_relaxed);
    return PyLong_FromLong(old_val + amount);
}

static PyObject*
ft_atomic_get(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    ModuleState* state = PyModule_GetState(self);
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
    ModuleState* state = PyModule_GetState(self);
    if (!state) {
        PyErr_SetString(PyExc_RuntimeError, "Cannot get module state");
        return NULL;
    }
    atomic_store_explicit(&state->counter, 0, memory_order_relaxed);
    Py_RETURN_NONE;
}

/* ── Example 3: String processing (GIL required for Python objects) ── */
/*
 * NOTE: This function manipulates Python objects (PyUnicode_FromString,
 * PyMem_Malloc which may call Python's allocator), so it does NOT release
 * the GIL. In free-threading mode, multiple threads calling this will
 * still be serialized by the GIL (Python automatically re-acquires it
 * for functions that don't declare Py_MOD_GIL_NOT_USED compatibility...
 * but since we DO declare it, you MUST ensure thread safety yourself).
 */
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

/* ── Example 4: Build info (compile-time vs runtime ABI check) ── */
static PyObject*
ft_build_info(PyObject* self, PyObject* Py_UNUSED(ignored))
{
    (void)self;
    PyObject* info = PyDict_New();
    if (!info) return NULL;

    /* Compile-time info */
    /* NOTE: PY_VERSION (not Py_VERSION!) gives the version as a string like "3.14.0" */
    PyDict_SetItemString(info, "compile_python_version",
                         PyUnicode_FromString(PY_VERSION));
    PyDict_SetItemString(info, "compile_free_threading",
                         FT_BUILD ? Py_True : Py_False);
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
        /*
         * NOTE: sys._is_gil_enabled() returns True in ALL Python 3.13+ builds
         * by default. It only returns False when:
         *   1. Running on a free-threading build (Py_GIL_DISABLED=1)
         *   2. The GIL is actually disabled (PYTHON_GIL=0 env var, or
         *      all loaded modules declare Py_MOD_GIL_NOT_USED)
         * Do NOT use hasattr(sys, '_is_gil_enabled') to detect free-threading!
         * Use sysconfig.get_config_var('Py_GIL_DISABLED') instead.
         */
        PyObject* gil = PyObject_GetAttrString(sys, "_is_gil_enabled");
        if (gil) {
            PyObject* res = PyObject_CallNoArgs(gil);
            if (res) {
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
            PyObject* key = PyUnicode_FromString("SOABI");
            PyObject* soabi = PyObject_CallOneArg(get_fn, key);
            Py_XDECREF(key);
            if (soabi) {
                PyDict_SetItemString(info, "soabi", soabi);
                Py_DECREF(soabi);
            }
            Py_DECREF(get_fn);
        }
        Py_DECREF(sysconfig);
    }

    return info;
}

/* ── Self-test function ───────────────────────────────────────── */
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

    printf("=== ft_extension Self-Test ===\n");

    /* Test 1: sum_of_squares correctness */
    PyObject* r = ft_sum_of_squares(self, Py_BuildValue("(l)", 100L));
    CHECK("sum_of_squares(100) == 338350",
          r && PyLong_Check(r) && PyLong_AsLongLong(r) == 338350LL);
    Py_XDECREF(r);

    /* Test 2: atomic counter */
    ft_atomic_reset(self, NULL);
    r = ft_atomic_increment(self, Py_BuildValue("(l)", 42L));
    CHECK("atomic_increment(42) returns 42",
          r && PyLong_Check(r) && PyLong_AsLong(r) == 42);
    Py_XDECREF(r);
    r = ft_atomic_get(self, NULL);
    CHECK("atomic_get returns 42",
          r && PyLong_Check(r) && PyLong_AsLong(r) == 42);
    Py_XDECREF(r);

    /* Test 3: string_repeat */
    r = ft_string_repeat(self, Py_BuildValue("(sn)", "ab", 3L));
    const char* rs = r ? PyUnicode_AsUTF8(r) : NULL;
    CHECK("string_repeat('ab', 3) == 'ababab'",
          rs && strcmp(rs, "ababab") == 0);
    Py_XDECREF(r);

    /* Test 4: build info */
    r = ft_build_info(self, NULL);
    CHECK("build_info returns dict", r && PyDict_Check(r));
    if (r && PyDict_Check(r)) {
        PyObject* ft = PyDict_GetItemString(r, "compile_free_threading");
        CHECK("compiled for free-threading", ft && PyObject_IsTrue(ft));
    }
    Py_XDECREF(r);

    ft_atomic_reset(self, NULL);

    printf("\n  Result: %d/%d passed\n", passed, total);
    printf("==============================\n");

    return (passed == total) ? Py_True : Py_False;
#undef CHECK
}

/* ── Multi-thread stress test ────────────────────────────────── */
/*
 * This test verifies that concurrent calls from multiple Python threads
 * do not cause race conditions when using atomic operations.
 * In free-threading mode, threads run truly in parallel — if atomic
 * operations are not used, the final count will be wrong.
 */
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

    PyObject* threading = PyImport_ImportModule("threading");
    if (!threading) return NULL;
    PyObject* Thread = PyObject_GetAttrString(threading, "Thread");
    if (!Thread) { Py_DECREF(threading); return NULL; }

    ft_atomic_reset(self, NULL);

    /* Create worker function via Py_CompileString */
    /* NOTE: Use keyword arguments for Thread() — positional args are wrong! */
    PyObject* worker_code = Py_CompileString(
        "def worker(n):\n"
        "    for _ in range(n):\n"
        "        ft_extension.atomic_increment(1)\n",
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
        PyObject* t_kwargs = Py_BuildValue("{s:O,s:O}",
                                            "target", worker_fn,
                                            "args", t_args);
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

/* ── Module method table ─────────────────────────────────────── */
static PyMethodDef ModuleMethods[] = {
    {"sum_of_squares", ft_sum_of_squares, METH_VARARGS,
     "sum_of_squares(n) -> int\nCompute sum(1^2..n^2), releases GIL for parallelism"},
    {"atomic_increment", ft_atomic_increment, METH_VARARGS,
     "atomic_increment([amount=1]) -> int\nThread-safe atomic counter increment"},
    {"atomic_get", ft_atomic_get, METH_NOARGS,
     "atomic_get() -> int\nGet current counter value"},
    {"atomic_reset", ft_atomic_reset, METH_NOARGS,
     "atomic_reset() -> None\nReset counter to 0"},
    {"string_repeat", ft_string_repeat, METH_VARARGS,
     "string_repeat(s, n) -> str\nRepeat string s n times"},
    {"build_info", ft_build_info, METH_NOARGS,
     "build_info() -> dict\nCompile-time and runtime ABI info"},
    {"run_self_test", ft_run_self_test, METH_NOARGS,
     "run_self_test() -> bool\nRun self-tests, return True if all pass"},
    {"thread_stress", ft_thread_stress, METH_VARARGS,
     "thread_stress([threads=8], [iter=100000]) -> dict\nMulti-thread stress test"},
    {NULL, NULL, 0, NULL}
};

/* ── Module initialization ───────────────────────────────────── */
static int
module_exec(PyObject* module)
{
    ModuleState* state = PyModule_GetState(module);
    if (!state) return -1;
    atomic_init(&state->counter, 0);
    return 0;
}

/*
 * ─── CRITICAL: GIL declaration slot ───────────────────────────
 *
 * Py_mod_gil with Py_MOD_GIL_NOT_USED tells Python that this module
 * is safe to run without the GIL. Without this slot, Python will
 * automatically re-enable the GIL when this module is imported,
 * defeating the purpose of free-threading!
 *
 * This is the single most important thing to get right. If you forget
 * this slot, your module will work (serialized by GIL) but you won't
 * get any multi-threaded speedup.
 *
 * The (void*) cast is required to avoid ISO C warnings about converting
 * function pointers to object pointers.
 */
static PyModuleDef_Slot ModuleSlots[] = {
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {Py_mod_exec, (void*)module_exec},
    {0, NULL}
};

static struct PyModuleDef module_def = {
    PyModuleDef_HEAD_INIT,
    "ft_extension",                                       /* m_name */
    "Free-Threading C Extension Template for Python 3.13t+", /* m_doc */
    sizeof(ModuleState),                                  /* m_size: per-module state */
    ModuleMethods,                                        /* m_methods */
    ModuleSlots,                                          /* m_slots */
    NULL, NULL, NULL                                      /* m_traverse, m_clear, m_free */
};

PyMODINIT_FUNC
PyInit_ft_extension(void)
{
    return PyModuleDef_Init(&module_def);
}
