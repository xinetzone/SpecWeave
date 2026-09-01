// ffi_bridge.cc — Minimal FFI bridge example
//
// This file demonstrates how to expose SetLogLevel/GetLogLevel to the
// host language (Python/Rust/Go/etc.) via your FFI system.
// Replace TVM_FFI_STATIC_INIT_BLOCK with your FFI framework's
// registration mechanism (pybind11, cxx, PyO3, etc.).

#include "log.hpp"

// ── Cross-platform DLL export macro ──────────────────────
// Define MYPROJ_DLL_EXPORTS when building as a shared library
// on Windows to export symbols. On Linux/macOS all extern "C"
// symbols are exported by default.
#if defined(_WIN32) && defined(MYPROJ_DLL_EXPORTS)
#  define MYPROJ_API __declspec(dllexport)
#else
#  define MYPROJ_API
#endif

// ── Bridge functions (thin wrappers, no business logic) ──
extern "C" MYPROJ_API void myproj_set_log_level(int level) {
  using myproj::log::Level;
  if (level < 0) level = 0;
  if (level > 4) level = 4;
  myproj::log::SetLevel(static_cast<Level>(level));
}

extern "C" MYPROJ_API int myproj_get_log_level() {
  return static_cast<int>(myproj::log::GetLevel());
}

// ── Test trigger function (for validation scripts) ──────
// Emits one log message at each of the 5 levels.
// Call this from Python/ctypes to verify the full pipeline.
extern "C" MYPROJ_API void myproj_test_logs() {
  MYPROJ_LOG_TRACE() << "trace test message";
  MYPROJ_LOG_DEBUG() << "debug test message";
  MYPROJ_LOG_INFO()  << "info test message";
  MYPROJ_LOG_WARN()  << "warn test message";
  MYPROJ_LOG_ERROR() << "error test message";
}

// ── FFI registration (TVM FFI example) ──────────────────
// For pybind11, replace with:
//   m.def("set_log_level", &myproj_set_log_level);
//   m.def("get_log_level", &myproj_get_log_level);
//
// For PyO3, replace with:
//   #[pyfunction]
//   fn set_log_level(level: i32) { unsafe { myproj_set_log_level(level); } }

#ifdef TVM_FFI_STATIC_INIT_BLOCK_AVAILABLE
#include <tvm/ffi/function.h>
TVM_FFI_STATIC_INIT_BLOCK() {
  tvm::ffi::FunctionRegistry::Global("myproj.SetLogLevel")
      .set_body([](tvm::ffi::TVMArgs args, tvm::ffi::TVMRetValue* rv) {
        myproj_set_log_level(args[0].operator int());
      });
  tvm::ffi::FunctionRegistry::Global("myproj.GetLogLevel")
      .set_body([](tvm::ffi::TVMArgs args, tvm::ffi::TVMRetValue* rv) {
        *rv = myproj_get_log_level();
      });
}
#endif
