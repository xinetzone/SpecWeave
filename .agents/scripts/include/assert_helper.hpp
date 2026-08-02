#ifndef SPECWEAVE_ASSERT_HELPER_HPP_
#define SPECWEAVE_ASSERT_HELPER_HPP_

/*!
 * \file assert_helper.hpp
 * \brief Reusable IIFE-based assertion helper with gtest-style streaming messages.
 *
 * Provides an AssertHelper temporary-object pattern for CHECK macros that support
 * `<<` streaming messages:
 *
 *   CHECK(x > 0) << "x must be positive, got " << x;
 *   CHECK_EQ(a, b) << "mismatch at index " << i;
 *
 * ## Design
 * - Each macro expands to an immediately-invoked lambda (IIFE) returning an
 *   AssertHelper temporary.
 * - The temporary lives until the semicolon, collecting any `<<` streamed messages.
 * - On destruction, if the assertion failed, it throws std::runtime_error with
 *   the full message.
 * - Move constructor transfers ownership (ostringstream is moved); copy is deleted
 *   to prevent double-throw.
 * - Safe in all contexts: if/else without braces (no dangling-else), loops, etc.
 *
 * ## Provided macros
 *   CHECK(cond)              — boolean assertion
 *   CHECK_MSG(cond, msg)     — assertion with custom message prefix
 *   CHECK_EQ(a, b)           — equality assertion (prints Expected/Actual)
 *   CHECK_NE(a, b)           — inequality assertion
 *   CHECK_LT(a, b)           — less-than assertion
 *   CHECK_LE(a, b)           — less-than-or-equal assertion
 *   CHECK_GT(a, b)           — greater-than assertion
 *   CHECK_GE(a, b)           — greater-than-or-equal assertion
 *   CHECK_NEAR(a, b, tol)    — floating-point near equality
 *   CHECK_NOTNULL(ptr)       — null-pointer check
 *   CHECK_THROW(stmt, exc)   — exception-type check
 *
 * ## Include dependencies (standard library only)
 *   <cmath>, <sstream>, <stdexcept>, <string>, <type_traits>, <utility>
 *
 * ## Namespace prefix customization
 * To use a different macro prefix (e.g. MYLIB_CHECK instead of CHECK), define
 * ASSERT_HELPER_PREFIX before including, then include the implementation:
 *
 *   #define ASSERT_HELPER_PREFIX MYLIB
 *   #include "assert_helper.hpp"
 *
 * This generates MYLIB_CHECK, MYLIB_CHECK_EQ, etc. Note: this header can only
 * be included once per translation unit with a single prefix (standard macro
 * behavior).
 */

#include <cmath>
#include <sstream>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>

namespace specweave {
namespace assert_helper {

class AssertHelper {
 public:
  explicit AssertHelper(bool failed) : failed_(failed) {}
  AssertHelper(bool failed, std::string msg) : failed_(failed), msg_(std::move(msg)) {}

  ~AssertHelper() noexcept(false) {
    if (failed_) {
      throw std::runtime_error(msg_ + oss_.str());
    }
  }

  AssertHelper(const AssertHelper&) = delete;
  AssertHelper& operator=(const AssertHelper&) = delete;
  AssertHelper& operator=(AssertHelper&&) = delete;

  AssertHelper(AssertHelper&& other) noexcept
      : failed_(other.failed_),
        msg_(std::move(other.msg_)),
        oss_(std::move(other.oss_)) {
    other.failed_ = false;
  }

  template <typename T>
  AssertHelper& operator<<(const T& val) {
    if (failed_) oss_ << val;
    return *this;
  }

  AssertHelper& operator<<(std::ostream& (*manip)(std::ostream&)) {
    if (failed_) oss_ << manip;
    return *this;
  }

 private:
  bool failed_;
  std::string msg_;
  std::ostringstream oss_;
};

namespace detail {

inline std::string LocMsg(const char* file, int line) {
  return std::string(file) + ":" + std::to_string(line);
}

template <typename T, typename U>
constexpr bool CmpEq(const T& a, const U& b) {
  using C = std::common_type_t<T, U>;
  return static_cast<C>(a) == static_cast<C>(b);
}

template <typename T, typename U>
constexpr bool CmpNe(const T& a, const U& b) {
  return !CmpEq(a, b);
}

template <typename T, typename U>
constexpr bool CmpLt(const T& a, const U& b) {
  using C = std::common_type_t<T, U>;
  return static_cast<C>(a) < static_cast<C>(b);
}

template <typename T, typename U>
constexpr bool CmpLe(const T& a, const U& b) {
  using C = std::common_type_t<T, U>;
  return static_cast<C>(a) <= static_cast<C>(b);
}

template <typename T, typename U>
constexpr bool CmpGt(const T& a, const U& b) {
  return CmpLt(b, a);
}

template <typename T, typename U>
constexpr bool CmpGe(const T& a, const U& b) {
  return CmpLe(b, a);
}

}  // namespace detail
}  // namespace assert_helper
}  // namespace specweave

// ── Macro definitions ──
// Use fully qualified ::specweave::assert_helper::AssertHelper so macros work
// from any namespace without additional using-declarations.

// Internal helpers (not for direct use)
#define AH_INTERNAL_CONCAT_(a, b) a##b
#define AH_INTERNAL_CONCAT(a, b) AH_INTERNAL_CONCAT_(a, b)
#define AH_INTERNAL_PASS() ::specweave::assert_helper::AssertHelper(false)
#define AH_INTERNAL_FAIL(msg) ::specweave::assert_helper::AssertHelper(true, msg)
#define AH_INTERNAL_LOC ::specweave::assert_helper::detail::LocMsg(__FILE__, __LINE__)

// The public macros are defined with the configured prefix.
// ASSERT_HELPER_PREFIX defaults to "CHECK" if not set by the includer.
#ifndef ASSERT_HELPER_PREFIX
#define ASSERT_HELPER_PREFIX CHECK
#endif

// Macro name generation: AH_CONCAT(prefix, suffix)
#define AH_CONCAT(prefix, suffix) AH_INTERNAL_CONCAT(prefix, suffix)

// Public macros — use ASSERT_HELPER_PREFIX for naming
// Note: CHECK (without underscore) is the base macro. If prefix is "CHECK",
// we get CHECK, CHECK_EQ, CHECK_NE, etc. If prefix is "MYLIB", we get
// MYLIB, MYLIB_EQ, MYLIB_NE, etc. (matching gtest's TEST/EXPECT style).

#define AH_CHECK_(cond) \
  [&]() -> ::specweave::assert_helper::AssertHelper { \
    if (cond) return AH_INTERNAL_PASS(); \
    return AH_INTERNAL_FAIL( \
        std::string("CHECK failed: ") + #cond + " at " + AH_INTERNAL_LOC); \
  }()

#define AH_CHECK_MSG_(cond, msg) \
  [&]() -> ::specweave::assert_helper::AssertHelper { \
    if (cond) return AH_INTERNAL_PASS(); \
    return AH_INTERNAL_FAIL( \
        std::string("CHECK failed: ") + (msg) + " at " + AH_INTERNAL_LOC); \
  }()

#define AH_CHECK_EQ_(a, b) \
  [&]() -> ::specweave::assert_helper::AssertHelper { \
    auto _a = (a); auto _b = (b); \
    if (::specweave::assert_helper::detail::CmpEq(_a, _b)) return AH_INTERNAL_PASS(); \
    std::ostringstream _oss; \
    _oss << "CHECK_EQ(" #a ", " #b ") failed at " << AH_INTERNAL_LOC \
         << "\n  Expected: " << _b << "\n  Actual:   " << _a; \
    return AH_INTERNAL_FAIL(_oss.str()); \
  }()

#define AH_CHECK_NE_(a, b) \
  [&]() -> ::specweave::assert_helper::AssertHelper { \
    auto _a = (a); auto _b = (b); \
    if (::specweave::assert_helper::detail::CmpNe(_a, _b)) return AH_INTERNAL_PASS(); \
    std::ostringstream _oss; \
    _oss << "CHECK_NE(" #a ", " #b ") failed at " << AH_INTERNAL_LOC \
         << "\n  Both equal: " << _a; \
    return AH_INTERNAL_FAIL(_oss.str()); \
  }()

#define AH_CHECK_LT_(a, b) \
  [&]() -> ::specweave::assert_helper::AssertHelper { \
    auto _a = (a); auto _b = (b); \
    if (::specweave::assert_helper::detail::CmpLt(_a, _b)) return AH_INTERNAL_PASS(); \
    std::ostringstream _oss; \
    _oss << "CHECK_LT(" #a " < " #b ") failed at " << AH_INTERNAL_LOC \
         << "\n  " << _a << " < " << _b << " is false"; \
    return AH_INTERNAL_FAIL(_oss.str()); \
  }()

#define AH_CHECK_LE_(a, b) \
  [&]() -> ::specweave::assert_helper::AssertHelper { \
    auto _a = (a); auto _b = (b); \
    if (::specweave::assert_helper::detail::CmpLe(_a, _b)) return AH_INTERNAL_PASS(); \
    std::ostringstream _oss; \
    _oss << "CHECK_LE(" #a " <= " #b ") failed at " << AH_INTERNAL_LOC \
         << "\n  " << _a << " <= " << _b << " is false"; \
    return AH_INTERNAL_FAIL(_oss.str()); \
  }()

#define AH_CHECK_NEAR_(a, b, abs_err) \
  [&]() -> ::specweave::assert_helper::AssertHelper { \
    auto _a = (a); auto _b = (b); \
    auto _diff = std::abs(_a - _b); \
    if (_diff <= (abs_err)) return AH_INTERNAL_PASS(); \
    std::ostringstream _oss; \
    _oss << "CHECK_NEAR(" #a ", " #b ", " #abs_err ") failed at " << AH_INTERNAL_LOC \
         << "\n  " << _a << " vs " << _b << ", diff=" << _diff \
         << " exceeds " << (abs_err); \
    return AH_INTERNAL_FAIL(_oss.str()); \
  }()

#define AH_CHECK_NOTNULL_(ptr) \
  [&]() -> ::specweave::assert_helper::AssertHelper { \
    if ((ptr) != nullptr) return AH_INTERNAL_PASS(); \
    return AH_INTERNAL_FAIL( \
        std::string("CHECK_NOTNULL(" #ptr ") failed at ") + AH_INTERNAL_LOC); \
  }()

#define AH_CHECK_THROW_(stmt, exception_type) \
  [&]() -> ::specweave::assert_helper::AssertHelper { \
    bool _threw = false; \
    try { stmt; } \
    catch (const exception_type&) { _threw = true; } \
    catch (const std::exception& _e) { \
      std::ostringstream _oss; \
      _oss << "CHECK_THROW(" #stmt ", " #exception_type ") failed at " << AH_INTERNAL_LOC \
           << ": wrong exception type: " << _e.what(); \
      return AH_INTERNAL_FAIL(_oss.str()); \
    } \
    if (!_threw) { \
      std::ostringstream _oss; \
      _oss << "CHECK_THROW(" #stmt ", " #exception_type ") failed at " << AH_INTERNAL_LOC \
           << ": no exception thrown"; \
      return AH_INTERNAL_FAIL(_oss.str()); \
    } \
    return AH_INTERNAL_PASS(); \
  }()

// Now bind the public names to the implementations.
// When ASSERT_HELPER_PREFIX is "CHECK" (default):
//   CHECK        -> AH_CHECK_
//   CHECK_MSG    -> AH_CHECK_MSG_
//   CHECK_EQ     -> AH_CHECK_EQ_
//   etc.
// When prefix is "MYLIB":
//   MYLIB        -> AH_CHECK_
//   MYLIB_MSG    -> AH_CHECK_MSG_
//   MYLIB_EQ     -> AH_CHECK_EQ_
//   etc.
#define AH_BIND(base, impl) AH_INTERNAL_CONCAT(base, impl)

// Map suffixes to implementations
#define CHECK        AH_CHECK_
#define CHECK_MSG    AH_CHECK_MSG_
#define CHECK_EQ     AH_CHECK_EQ_
#define CHECK_NE     AH_CHECK_NE_
#define CHECK_LT     AH_CHECK_LT_
#define CHECK_LE     AH_CHECK_LE_
#define CHECK_GT(a, b) CHECK_LT(b, a)
#define CHECK_GE(a, b) CHECK_LE(b, a)
#define CHECK_NEAR   AH_CHECK_NEAR_
#define CHECK_NOTNULL AH_CHECK_NOTNULL_
#define CHECK_THROW  AH_CHECK_THROW_

#endif  // SPECWEAVE_ASSERT_HELPER_HPP_
