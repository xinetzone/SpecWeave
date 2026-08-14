// =============================================================================
// Zero-copy COW Read-Write Separation Pattern - C++ Example Framework
// 零拷贝COW读写分离模式 - C++示例框架
// =============================================================================
//
// 核心特性（对应模式5步法）：
//   1. const/non-const 编译期读写API分离
//   2. std::shared_ptr 引用计数O(1)零拷贝共享
//   3. mutable_data() 入口自动检测，写时克隆
//   4. identity_share 标志支持N=1单消费者in-place直通
//   5. 编译期宏 + 运行期原子开关双重回退机制
//
// 编译要求：C++17 及以上（零第三方依赖）
// =============================================================================

#ifndef COW_BUFFER_HPP_
#define COW_BUFFER_HPP_

#include <atomic>
#include <cstddef>
#include <cstring>
#include <iostream>
#include <memory>
#include <string>
#include <utility>

namespace cow_demo {

// -----------------------------------------------------------------------------
// 日志级别控制
// -----------------------------------------------------------------------------

enum class LogLevel {
    kSilent = 0,   // 静默模式（单元测试使用）
    kNormal = 1,   // 正常模式（仅关键事件：ALLOC/SHARE/COW/RESIZE/SWITCH/UNSHARE）
    kVerbose = 2   // 详细模式（所有事件：含READ/WRITE）
};

namespace detail {
inline std::atomic<int>& log_level() {
    static std::atomic<int> instance{static_cast<int>(LogLevel::kVerbose)};
    return instance;
}
inline std::atomic<bool>& cow_runtime_enabled() {
    static std::atomic<bool> instance{true};
    return instance;
}
}  // namespace detail

/// @brief 设置日志级别
inline void SetLogLevel(LogLevel level) {
    detail::log_level().store(static_cast<int>(level), std::memory_order_relaxed);
}

/// @brief 查询当前日志级别
inline LogLevel GetLogLevel() {
    return static_cast<LogLevel>(detail::log_level().load(std::memory_order_relaxed));
}

/// @brief 设置运行期COW开关状态（线程安全，无需重编译）
inline void SetCOWEnabled(bool enabled) {
    bool old = detail::cow_runtime_enabled().exchange(enabled, std::memory_order_relaxed);
    if (GetLogLevel() >= LogLevel::kNormal) {
        std::cout << "[COW-SWITCH] Runtime switch: " << (old ? "ENABLED" : "DISABLED")
                  << " -> " << (enabled ? "ENABLED" : "DISABLED") << std::endl;
    }
}

/// @brief 查询运行期COW开关状态
inline bool IsCOWEnabled() {
#ifndef COW_DISABLED_AT_COMPILE_TIME
    return detail::cow_runtime_enabled().load(std::memory_order_relaxed);
#else
    return false;
#endif
}

// 编译期开关：取消注释以下宏可完全移除COW代码，回退为总是浅共享
// #define COW_DISABLED_AT_COMPILE_TIME

// -----------------------------------------------------------------------------
// CowBuffer 核心类
// -----------------------------------------------------------------------------

/// @brief 支持零拷贝共享和写时复制(COW)的浮点缓冲区
///
/// 设计遵循"零拷贝COW读写分离模式"：
/// - 读操作（data() const）：零开销，永远不触发复制
/// - 写操作（mutable_data()）：共享时自动触发COW，获得私有副本
/// - 共享操作（ShareFrom()）：O(1)指针赋值，零拷贝
/// - N=1单消费者场景（identity share）：保持in-place直通，不触发COW
class CowBuffer {
public:
    /// @brief 构造空缓冲区
    CowBuffer() : size_(0), is_shared_(false), is_identity_share_(false) {}

    /// @brief 构造指定大小的缓冲区并初始化
    /// @param size 元素个数（float类型）
    /// @param name 可选名称，用于日志调试
    explicit CowBuffer(size_t size, std::string name = "")
        : size_(size), name_(std::move(name)), is_shared_(false), is_identity_share_(false) {
        data_ = std::shared_ptr<float[]>(new float[size_]);
        std::memset(data_.get(), 0, size_ * sizeof(float));
        if (GetLogLevel() >= LogLevel::kNormal) {
            std::cout << "[ALLOC] CowBuffer'" << name_ << "' created, size=" << size_
                      << ", ptr=" << data_.get() << std::endl;
        }
    }

    /// @brief 零拷贝共享另一个缓冲区的数据
    void ShareFrom(const CowBuffer& other, bool identity_pass_through = false) {
        data_.reset();
        data_ = other.data_;
        size_ = other.size_;
        is_shared_ = true;
        is_identity_share_ = identity_pass_through;

        if (GetLogLevel() >= LogLevel::kNormal) {
            std::cout << "[SHARE] CowBuffer'" << name_ << "' shares from '" << other.name_
                      << "', ptr=" << data_.get()
                      << ", use_count=" << data_.use_count()
                      << ", identity=" << (is_identity_share_ ? "YES" : "NO")
                      << " (zerocopy)" << std::endl;
        }
    }

    /// @brief 显式强制断开共享（深拷贝）
    void Unshare() {
        if (data_ && data_.use_count() > 1) {
            if (GetLogLevel() >= LogLevel::kNormal) {
                std::cout << "[UNSHARE] CowBuffer'" << name_
                          << "' explicit unshare, old_ptr=" << data_.get()
                          << ", use_count=" << data_.use_count() << std::endl;
            }
            TriggerCOW("explicit Unshare()");
        }
        is_shared_ = false;
        is_identity_share_ = false;
    }

    // -------------------------------------------------------------------------
    // 第一步：const/non-const 读写API分离
    // -------------------------------------------------------------------------

    /// @brief 获取只读数据指针（const版本，永远不触发COW，零开销）
    const float* data() const {
        if (data_ && GetLogLevel() >= LogLevel::kVerbose) {
            std::cout << "[READ]  CowBuffer'" << name_
                      << "' const access, ptr=" << data_.get()
                      << ", use_count=" << data_.use_count()
                      << " (nocopy)" << std::endl;
        }
        return data_ ? data_.get() : nullptr;
    }

    /// @brief 获取可写数据指针（non-const版本，按需触发COW）
    float* mutable_data() {
        if (!data_) {
            return nullptr;
        }

        bool needs_cow = false;
        const char* cow_reason = "exclusive (nocopy)";

        if (IsCOWEnabled()) {
            if (is_identity_share_) {
                cow_reason = "identity passthrough (nocopy)";
            } else if (data_.use_count() > 1) {
                needs_cow = true;
                cow_reason = "TRIGGER COW";
            }
        } else {
            cow_reason = "COW disabled (nocopy, UNSAFE for sharing)";
        }

        if (GetLogLevel() >= LogLevel::kVerbose) {
            std::cout << "[WRITE] CowBuffer'" << name_
                      << "' mutable access, ptr=" << data_.get()
                      << ", use_count=" << data_.use_count()
                      << " -> " << cow_reason << std::endl;
        }

        if (needs_cow) {
            TriggerCOW("mutable_data() write access");
        }

        return data_.get();
    }

    // -------------------------------------------------------------------------
    // 元数据操作
    // -------------------------------------------------------------------------

    /// @brief 改变缓冲区大小（会打断共享，重新分配内存）
    void Resize(size_t new_size) {
        if (new_size == size_) {
            return;
        }

        if (GetLogLevel() >= LogLevel::kNormal) {
            std::cout << "[RESIZE] CowBuffer'" << name_
                      << "' resize " << size_ << " -> " << new_size;
        }

        if (data_ && data_.use_count() > 1) {
            if (GetLogLevel() >= LogLevel::kNormal) {
                std::cout << " (breaking share)";
            }
            TriggerCOW("Resize() changes metadata");
        }
        if (GetLogLevel() >= LogLevel::kNormal) {
            std::cout << std::endl;
        }

        auto new_data = std::shared_ptr<float[]>(new float[new_size]);
        size_t copy_size = std::min(size_, new_size);
        if (data_ && copy_size > 0) {
            std::memcpy(new_data.get(), data_.get(), copy_size * sizeof(float));
        }
        if (new_size > size_) {
            std::memset(new_data.get() + size_, 0, (new_size - size_) * sizeof(float));
        }
        data_ = new_data;
        size_ = new_size;
        is_shared_ = false;
        is_identity_share_ = false;
    }

    // -------------------------------------------------------------------------
    // 辅助查询方法
    // -------------------------------------------------------------------------

    size_t size() const { return size_; }
    const std::string& name() const { return name_; }
    void set_name(const std::string& name) { name_ = name; }
    long use_count() const { return data_ ? data_.use_count() : 0; }
    bool is_shared() const { return data_ && data_.use_count() > 1; }
    bool is_identity_share() const { return is_identity_share_; }

    /// @brief 获取原始指针（无日志，用于内部比较和测试）
    const float* raw_ptr() const { return data_ ? data_.get() : nullptr; }

    /// @brief 便捷下标访问（const，只读，不触发COW，不打日志）
    float operator[](size_t idx) const {
        return data_ ? data_[idx] : 0.0f;
    }

private:
    void TriggerCOW(const char* reason) {
        size_t old_use_count = data_.use_count();
        const void* old_ptr = data_.get();

        auto new_data = std::shared_ptr<float[]>(new float[size_]);
        std::memcpy(new_data.get(), data_.get(), size_ * sizeof(float));
        data_ = new_data;
        is_shared_ = false;
        is_identity_share_ = false;

        if (GetLogLevel() >= LogLevel::kNormal) {
            std::cout << "  [COW] Cloned: reason=" << reason
                      << ", old_ptr=" << old_ptr << ", new_ptr=" << data_.get()
                      << ", size=" << size_
                      << ", old_use_count=" << old_use_count
                      << ", new_use_count=" << data_.use_count()
                      << std::endl;
        }
    }

    std::shared_ptr<float[]> data_;
    size_t size_;
    std::string name_;
    bool is_shared_;
    bool is_identity_share_;
};

}  // namespace cow_demo

#endif  // COW_BUFFER_HPP_
