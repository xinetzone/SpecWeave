#pragma once
/*!
 * \file log.hpp
 * \brief Lightweight leveled logging with NullStream zero-overhead pattern.
 *
 * Levels: TRACE(0) < DEBUG(1) < INFO(2) < WARN(3) < ERROR(4)
 * TRACE is for leak-diagnosis backtraces; default level is WARN.
 * Compile with DEMO_ENABLE_LOG to enable TRACE/DEBUG/INFO at compile time.
 */

#include <iostream>
#include <sstream>
#include <string>

namespace demo_log {

enum class Level : int {
  TRACE = 0,
  DEBUG = 1,
  INFO  = 2,
  WARN  = 3,
  ERROR = 4
};

inline Level& CurrentLevel() {
  static Level level = Level::WARN;
  return level;
}

inline void SetLevel(Level lvl) { CurrentLevel() = lvl; }
inline Level GetLevel() { return CurrentLevel(); }

struct NullStream {
  template<typename T>
  NullStream& operator<<(const T&) { return *this; }
};

struct LogStream {
  Level level;
  std::ostringstream oss;

  LogStream(Level lvl, const char* tag) : level(lvl) {
    static const char* names[] = {"TRACE", "DEBUG", "INFO", "WARN", "ERROR"};
    oss << "[" << names[static_cast<int>(lvl)] << "] " << tag;
  }
  ~LogStream() {
    oss << "\n";
    std::cerr << oss.str();
  }
  template<typename T>
  LogStream& operator<<(const T& val) { oss << val; return *this; }
};

}  // namespace demo_log

#if defined(DEMO_ENABLE_LOG)

  #define DEMO_LOG(lvl, tag) \
    if (static_cast<int>(::demo_log::GetLevel()) <= static_cast<int>(lvl)) \
      ::demo_log::LogStream(lvl, tag)
  #define DEMO_LOG_TRACE()  DEMO_LOG(::demo_log::Level::TRACE, "")
  #define DEMO_LOG_DEBUG()  DEMO_LOG(::demo_log::Level::DEBUG, "")
  #define DEMO_LOG_INFO()   DEMO_LOG(::demo_log::Level::INFO, "")
  #define DEMO_LOG_WARN()   DEMO_LOG(::demo_log::Level::WARN, "")
  #define DEMO_LOG_ERROR()  DEMO_LOG(::demo_log::Level::ERROR, "")

  #define DEMO_MEM_LOG    DEMO_LOG_DEBUG() << "[MEM] "
  #define DEMO_OBJ_LOG    DEMO_LOG_DEBUG() << "[OBJ] "

#else

  #define DEMO_LOG(lvl, tag) ::demo_log::NullStream()
  #define DEMO_LOG_TRACE()  ::demo_log::NullStream()
  #define DEMO_LOG_DEBUG()  ::demo_log::NullStream()
  #define DEMO_LOG_INFO()   ::demo_log::NullStream()
  #define DEMO_LOG_WARN()   ::demo_log::NullStream()
  #define DEMO_LOG_ERROR()  ::demo_log::NullStream()
  #define DEMO_MEM_LOG      ::demo_log::NullStream()
  #define DEMO_OBJ_LOG      ::demo_log::NullStream()

#endif

namespace demo_log {
inline void EnableTrace() { SetLevel(Level::TRACE); }
inline void EnableDebug() { SetLevel(Level::DEBUG); }
inline void DisableDebug() { SetLevel(Level::WARN); }
}  // namespace demo_log
