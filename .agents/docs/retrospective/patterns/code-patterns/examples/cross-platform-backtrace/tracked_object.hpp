#pragma once
/*!
 * \file tracked_object.hpp
 * \brief Example RAII base class demonstrating the cross-platform backtrace
 *        leak-diagnosis pattern: atomic counters + construction backtrace capture
 *        + TRACE-level destructor output.
 *
 * Derive from TrackedObject to get automatic instance counting and
 * leak-source backtraces in your own classes.
 */

#include <atomic>
#include <cstdint>
#include <string>

#include "backtrace.hpp"
#include "log.hpp"

class TrackedObject {
 public:
  TrackedObject() : id_(next_id()) {
    live_count_.fetch_add(1, std::memory_order_relaxed);
    construct_bt_ = backtrace::GetBacktrace(3);
    DEMO_OBJ_LOG << "[LIFECYCLE] TrackedObject#" << id_
                 << " constructed this=" << this
                 << " live=" << live_count();
  }

  virtual ~TrackedObject() {
    int64_t live_before = live_count_.fetch_sub(1, std::memory_order_relaxed);
    DEMO_OBJ_LOG << "[LIFECYCLE] TrackedObject#" << id_
                 << " destroyed this=" << this
                 << " live=" << (live_before - 1);
    DEMO_LOG_TRACE() << "[LIFECYCLE] TrackedObject#" << id_
                     << " construction backtrace:\n" << construct_bt_;
  }

  TrackedObject(const TrackedObject&) = delete;
  TrackedObject& operator=(const TrackedObject&) = delete;

  int64_t id() const { return id_; }
  const std::string& construction_backtrace() const { return construct_bt_; }

  static int64_t live_count() {
    return live_count_.load(std::memory_order_relaxed);
  }

 private:
  static int64_t next_id() {
    static std::atomic<int64_t> g_id{1};
    return g_id.fetch_add(1, std::memory_order_relaxed);
  }
  static std::atomic<int64_t> live_count_;

  int64_t id_;
  std::string construct_bt_;
};
