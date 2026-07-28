/*!
 * \file demo.cc
 * \brief Executable demo for the cross-platform backtrace leak-diagnosis pattern.
 *
 * Demonstrates:
 *   1. Normal lifecycle - objects constructed and destroyed correctly
 *   2. Intentional leak detection via atomic live_count counter
 *   3. TRACE-level backtrace output showing where leaked objects were created
 *   4. get_backtrace() global API for ad-hoc stack dumps
 *   5. Graceful degradation when DEMO_ENABLE_BACKTRACE is OFF
 *
 * Build:
 *   mkdir build && cd build
 *   cmake .. -DDEMO_ENABLE_BACKTRACE=ON -DDEMO_ENABLE_LOG=ON
 *   cmake --build . --config Release
 *   ./leak_demo           # default WARN level - no backtrace output
 *   ./leak_demo --trace   # TRACE level - prints construction backtraces
 */

#include <cstdlib>
#include <cstring>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "backtrace.hpp"
#include "log.hpp"
#include "tracked_object.hpp"

// --- TrackedObject static member definition ---
std::atomic<int64_t> TrackedObject::live_count_{0};

// --- Example domain class deriving from TrackedObject ---
class Resource : public TrackedObject {
 public:
  explicit Resource(size_t sz, const std::string& name)
      : size_(sz), name_(name), data_(new char[sz]) {
    DEMO_MEM_LOG << "[ALLOC] Resource#" << id()
                 << " name='" << name_ << "' size=" << size_
                 << " ptr=" << static_cast<const void*>(data_);
    std::memset(data_, 0, sz);
  }

  ~Resource() override {
    DEMO_MEM_LOG << "[FREE] Resource#" << id()
                 << " name='" << name_ << "' size=" << size_
                 << " ptr=" << static_cast<const void*>(data_);
    delete[] data_;
  }

  size_t size() const { return size_; }
  const std::string& name() const { return name_; }

 private:
  size_t size_;
  std::string name_;
  char* data_;
};

// --- Factory functions that may leak (for demo purposes) ---
static std::unique_ptr<Resource> make_resource(size_t sz, const std::string& name) {
  return std::make_unique<Resource>(sz, name);
}

static Resource* allocate_leaking_resource(size_t sz, const std::string& name) {
  // BUG: returns raw pointer without ownership tracking, causing a leak
  return new Resource(sz, name);
}

static void do_work_normal() {
  DEMO_LOG_INFO() << "--- Normal lifecycle test ---";
  {
    auto r1 = make_resource(1024, "buffer-a");
    auto r2 = make_resource(2048, "buffer-b");
    DEMO_LOG_INFO() << "Inside scope, live_count=" << TrackedObject::live_count();
  }
  DEMO_LOG_INFO() << "After scope exit, live_count=" << TrackedObject::live_count();
}

static void do_work_with_leak() {
  DEMO_LOG_INFO() << "--- Intentional leak test ---";
  Resource* leaked = allocate_leaking_resource(4096, "leaked-buffer");
  DEMO_LOG_INFO() << "Allocated leaking resource ptr=" << leaked
                  << " live_count=" << TrackedObject::live_count();
  // Intentionally NOT deleting 'leaked' to simulate a bug
}

static void print_summary(const std::string& label) {
  int64_t n = TrackedObject::live_count();
  std::cout << "\n=== " << label << " ===\n";
  std::cout << "  live TrackedObjects: " << n;
  if (n > 0) {
    std::cout << "  *** POTENTIAL LEAK DETECTED ***";
  }
  std::cout << "\n\n";
}

int main(int argc, char* argv[]) {
  bool trace_mode = false;
  for (int i = 1; i < argc; ++i) {
    if (std::strcmp(argv[i], "--trace") == 0 || std::strcmp(argv[i], "-t") == 0) {
      trace_mode = true;
    }
  }

  std::cout << "=== Cross-Platform Backtrace Leak Diagnosis Demo ===\n";
  std::cout << "Build: backtrace="
#ifdef DEMO_ENABLE_BACKTRACE
            << "ON"
#else
            << "OFF"
#endif
            << ", logging="
#ifdef DEMO_ENABLE_LOG
            << "ON"
#else
            << "OFF"
#endif
            << "\n";

  if (trace_mode) {
    demo_log::EnableTrace();
    std::cout << "Log level: TRACE (construction backtraces enabled)\n";
  } else {
    std::cout << "Log level: WARN (default, use --trace to see backtraces)\n";
  }

  // 1. Show ad-hoc backtrace API
  std::cout << "\n--- Current call stack (via get_backtrace) ---\n";
  std::cout << backtrace::GetBacktrace(1);

  // 2. Normal lifecycle
  do_work_normal();
  print_summary("After normal lifecycle");

  // 3. Leak scenario
  do_work_with_leak();
  print_summary("After leaking allocation");

  // 4. Show how to diagnose: if live_count > 0 after cleanup,
  //    rerun with --trace to see construction backtraces in TRACE log.
  if (TrackedObject::live_count() > 0) {
    if (!trace_mode) {
      std::cout << ">>> Rerun with --trace to see where the leaked object was created. <<<\n";
    } else {
      std::cout << ">>> Check [TRACE] lines above for 'construction backtrace:' <<<\n";
      std::cout << ">>> The last construction backtrace that has NO matching     <<<\n";
      std::cout << ">>> destruction line is the leak source.                      <<<\n";
    }
  }

  // 5. Demonstrate Blob.construction_backtrace property
  {
    auto r = make_resource(512, "probe");
    std::cout << "\n--- Direct backtrace property access ---\n";
    std::cout << "Resource#" << r->id() << " ('" << r->name() << "')";
    std::cout << " construction_backtrace:\n" << r->construction_backtrace();
  }

  std::cout << "\n=== Demo finished ===\n";
  return TrackedObject::live_count() > 0 ? 1 : 0;
}
