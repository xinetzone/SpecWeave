#ifndef THREE_LAYER_LOGGING_LOG_HPP_
#define THREE_LAYER_LOGGING_LOG_HPP_

#include <cstring>
#include <iostream>
#include <sstream>
#include <string>

namespace myproj {
namespace log {

enum class Level {
  TRACE = 0,
  DEBUG = 1,
  INFO  = 2,
  WARN  = 3,
  ERROR = 4,
};

inline Level& CurrentLevel() {
  static Level level = Level::WARN;
  return level;
}

inline void SetLevel(Level level) { CurrentLevel() = level; }
inline Level GetLevel() { return CurrentLevel(); }

inline const char* LevelName(Level level) {
  switch (level) {
    case Level::TRACE: return "TRACE";
    case Level::DEBUG: return "DEBUG";
    case Level::INFO:  return "INFO";
    case Level::WARN:  return "WARN";
    case Level::ERROR: return "ERROR";
    default:           return "UNKNOWN";
  }
}

inline bool ShouldLog(Level level) {
#ifdef MYPROJ_ENABLE_DEBUG_LOG
  return static_cast<int>(level) >= static_cast<int>(CurrentLevel());
#else
  return static_cast<int>(level) >= static_cast<int>(Level::WARN);
#endif
}

class Logger {
 public:
  Logger(Level level, const char* file, int line, const char* func)
      : enabled_(ShouldLog(level)), level_(level) {
    if (enabled_) {
      const char* basename = std::strrchr(file, '\\');
      if (!basename) basename = std::strrchr(file, '/');
      basename = basename ? basename + 1 : file;
      buf_ << "[" << LevelName(level) << "] "
           << basename << ":" << line << " (" << func << ") ";
    }
  }

  ~Logger() {
    if (enabled_) {
      buf_ << "\n";
      if (level_ >= Level::ERROR) {
        std::cerr << buf_.str();
        std::cerr.flush();
      } else {
        std::cout << buf_.str();
        std::cout.flush();
      }
    }
  }

  template <typename T>
  Logger& operator<<(const T& value) {
    if (enabled_) buf_ << value;
    return *this;
  }

 private:
  bool enabled_;
  Level level_;
  std::ostringstream buf_;
};

}  // namespace log
}  // namespace myproj

// ── Level macros ──────────────────────────────────────────
#define MYPROJ_LOG(level) \
  ::myproj::log::Logger(level, __FILE__, __LINE__, __func__)

#define MYPROJ_LOG_TRACE() MYPROJ_LOG(::myproj::log::Level::TRACE)
#define MYPROJ_LOG_DEBUG() MYPROJ_LOG(::myproj::log::Level::DEBUG)
#define MYPROJ_LOG_INFO()  MYPROJ_LOG(::myproj::log::Level::INFO)
#define MYPROJ_LOG_WARN()  MYPROJ_LOG(::myproj::log::Level::WARN)
#define MYPROJ_LOG_ERROR() MYPROJ_LOG(::myproj::log::Level::ERROR)

// ── Component tag macros (customize for your project) ────
// Copy this pattern: define a DEBUG macro per component that
// prepends a [TAG] for easy grep filtering.
#define MYPROJ_MEM_LOG       MYPROJ_LOG_DEBUG() << "[MEM] "
#define MYPROJ_TENSOR_LOG    MYPROJ_LOG_DEBUG() << "[TENSOR] "
#define MYPROJ_NET_LOG       MYPROJ_LOG_DEBUG() << "[NET] "
#define MYPROJ_LAYER_LOG     MYPROJ_LOG_DEBUG() << "[LAYER] "

#endif  // THREE_LAYER_LOGGING_LOG_HPP_
