// =============================================================================
// CowBuffer Unit Tests (静默模式，面向CI/自动化验证)
// =============================================================================

#include "cow_buffer.hpp"
#include <atomic>
#include <cassert>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <thread>
#include <vector>

using namespace cow_demo;

static int g_tests_run = 0;
static int g_tests_passed = 0;
static int g_tests_failed = 0;

#define TEST(name) \
    static void Test_##name(); \
    struct Reg_##name { Reg_##name() { RegisterUnitTest(#name, Test_##name); } }; \
    static Reg_##name reg_##name; \
    static void Test_##name()

#define ASSERT_TRUE(cond) \
    do { if (!(cond)) { \
        std::fprintf(stderr, "  FAIL: %s:%d: " #cond "\n", __FILE__, __LINE__); \
        throw TestFailure(); \
    }} while(0)

#define ASSERT_FALSE(cond) ASSERT_TRUE(!(cond))
#define ASSERT_EQ(a, b) ASSERT_TRUE((a) == (b))
#define ASSERT_NE(a, b) ASSERT_TRUE((a) != (b))
#define ASSERT_NEAR(a, b, tol) ASSERT_TRUE(std::fabs((a)-(b)) <= (tol))
#define ASSERT_PTR_EQ(a, b) ASSERT_TRUE((const void*)(a) == (const void*)(b))
#define ASSERT_PTR_NE(a, b) ASSERT_TRUE((const void*)(a) != (const void*)(b))

struct TestFailure {};

struct UnitTestReg {
    const char* name;
    void (*func)();
};
static std::vector<UnitTestReg>& GetUnitTests() {
    static std::vector<UnitTestReg> tests;
    return tests;
}
void RegisterUnitTest(const char* name, void (*func)()) {
    GetUnitTests().push_back({name, func});
}

// =============================================================================
// 构造与基础操作
// =============================================================================

TEST(DefaultConstructor_IsEmpty) {
    CowBuffer buf;
    ASSERT_EQ(buf.size(), 0u);
    ASSERT_TRUE(buf.raw_ptr() == nullptr);
    ASSERT_EQ(buf.use_count(), 0);
    ASSERT_FALSE(buf.is_shared());
    ASSERT_FALSE(buf.is_identity_share());
}

TEST(SizedConstructor_ZeroInitialized) {
    CowBuffer buf(16, "test");
    ASSERT_EQ(buf.size(), 16u);
    ASSERT_TRUE(buf.raw_ptr() != nullptr);
    ASSERT_EQ(buf.use_count(), 1);
    for (size_t i = 0; i < 16; i++) {
        ASSERT_NEAR(buf[i], 0.0f, 1e-9f);
    }
}

TEST(MutableData_WriteAndReadBack) {
    CowBuffer buf(4, "buf");
    float* p = buf.mutable_data();
    p[0] = 1.5f; p[1] = -2.5f; p[2] = 3.14f; p[3] = 0.0f;
    ASSERT_NEAR(buf[0], 1.5f, 1e-6f);
    ASSERT_NEAR(buf[1], -2.5f, 1e-6f);
    ASSERT_NEAR(buf[2], 3.14f, 1e-6f);
    ASSERT_NEAR(buf[3], 0.0f, 1e-6f);
}

TEST(ConstData_ReturnsSamePointer) {
    CowBuffer buf(4, "buf");
    buf.mutable_data()[0] = 42.0f;
    const CowBuffer& cbuf = buf;
    const float* p = cbuf.data();
    ASSERT_NEAR(p[0], 42.0f, 1e-6f);
    ASSERT_PTR_EQ(p, buf.raw_ptr());
}

TEST(SetName_WorksCorrectly) {
    CowBuffer buf(4, "original");
    ASSERT_EQ(std::string(buf.name()), "original");
    buf.set_name("renamed");
    ASSERT_EQ(std::string(buf.name()), "renamed");
}

// =============================================================================
// 零拷贝共享
// =============================================================================

TEST(ShareFrom_ZeroCopyPointerEquality) {
    CowBuffer a(8, "a");
    CowBuffer b(0, "b");
    a.mutable_data()[0] = 7.0f;
    b.ShareFrom(a, false);
    ASSERT_PTR_EQ(b.raw_ptr(), a.raw_ptr());
    ASSERT_EQ(b.size(), a.size());
    ASSERT_NEAR(b[0], 7.0f, 1e-6f);
    ASSERT_EQ(a.use_count(), 2);
}

TEST(ShareFrom_ReplacesOldData) {
    CowBuffer a(4, "a");
    CowBuffer b(8, "b");  // b has its own data
    b.mutable_data()[0] = 99.0f;
    const void* old_b_ptr = b.raw_ptr();
    b.ShareFrom(a, false);
    ASSERT_PTR_NE(b.raw_ptr(), old_b_ptr);
    ASSERT_PTR_EQ(b.raw_ptr(), a.raw_ptr());
}

TEST(ShareFrom_MultipleConsumers_RefCountCorrect) {
    CowBuffer src(4, "src");
    CowBuffer o1(0, "o1"), o2(0, "o2"), o3(0, "o3");
    o1.ShareFrom(src, false);
    o2.ShareFrom(src, false);
    o3.ShareFrom(src, false);
    ASSERT_EQ(src.use_count(), 4);  // src + o1 + o2 + o3
    ASSERT_TRUE(src.is_shared());
}

TEST(ShareFrom_IdentityFlag_SetCorrectly) {
    CowBuffer a(4, "a");
    CowBuffer b(0, "b"), c(0, "c");
    b.ShareFrom(a, true);
    c.ShareFrom(a, false);
    ASSERT_TRUE(b.is_identity_share());
    ASSERT_FALSE(c.is_identity_share());
}

// =============================================================================
// COW 写时复制
// =============================================================================

TEST(COW_ExclusiveWrite_NoCopy) {
    CowBuffer buf(4, "buf");
    const void* orig = buf.raw_ptr();
    buf.mutable_data()[0] = 1.0f;
    ASSERT_PTR_EQ(buf.raw_ptr(), orig);  // exclusive: no copy
}

TEST(COW_N1Identity_NoCopy) {
    CowBuffer src(4, "src");
    CowBuffer out(0, "out");
    out.ShareFrom(src, true);
    const void* orig = out.raw_ptr();
    out.mutable_data()[0] = 5.0f;
    ASSERT_PTR_EQ(out.raw_ptr(), orig);  // identity passthrough: no copy
    ASSERT_NEAR(src[0], 5.0f, 1e-6f);   // in-place visible to source
}

TEST(COW_N2MultiConsumer_WriteTriggersCopy) {
    CowBuffer src(4, "src");
    src.mutable_data()[0] = 1.0f;
    CowBuffer o1(0, "o1"), o2(0, "o2");
    o1.ShareFrom(src, false);
    o2.ShareFrom(src, false);
    const void* src_ptr = src.raw_ptr();

    float* p1 = o1.mutable_data();
    p1[0] = 88.0f;

    ASSERT_PTR_NE(o1.raw_ptr(), src_ptr);    // o1 got a copy
    ASSERT_PTR_EQ(o2.raw_ptr(), src_ptr);    // o2 still shares
    ASSERT_PTR_EQ(src.raw_ptr(), src_ptr);   // src unchanged
    ASSERT_NEAR(src[0], 1.0f, 1e-6f);       // source not modified
    ASSERT_NEAR(o2[0], 1.0f, 1e-6f);        // o2 not modified
    ASSERT_NEAR(o1[0], 88.0f, 1e-6f);       // o1 has new value
}

TEST(COW_OwnerWrite_WhenShared_TriggersCopy) {
    CowBuffer src(4, "src");
    src.mutable_data()[0] = 3.0f;
    CowBuffer reader(0, "reader");
    reader.ShareFrom(src, false);
    const void* reader_ptr = reader.raw_ptr();

    // Owner writes while reader is sharing — src should COW
    float* sp = src.mutable_data();
    sp[0] = 77.0f;

    ASSERT_PTR_NE(src.raw_ptr(), reader_ptr);  // src got a copy
    ASSERT_NEAR(src[0], 77.0f, 1e-6f);
    ASSERT_NEAR(reader[0], 3.0f, 1e-6f);       // reader sees old value
}

TEST(COW_DataIntegrity_AfterClone) {
    CowBuffer src(8, "src");
    for (int i = 0; i < 8; i++) src.mutable_data()[i] = static_cast<float>(i);
    CowBuffer clone(0, "clone");
    clone.ShareFrom(src, false);
    clone.mutable_data()[0] = 999.0f;

    // Clone has modified [0], rest should be copied correctly
    ASSERT_NEAR(clone[0], 999.0f, 1e-6f);
    for (int i = 1; i < 8; i++) {
        ASSERT_NEAR(clone[i], static_cast<float>(i), 1e-6f);
    }
    // Source unchanged
    for (int i = 0; i < 8; i++) {
        ASSERT_NEAR(src[i], static_cast<float>(i), 1e-6f);
    }
}

TEST(COW_RefCount_AfterClone) {
    CowBuffer src(4, "src");
    CowBuffer o1(0, "o1"), o2(0, "o2");
    o1.ShareFrom(src, false);
    o2.ShareFrom(src, false);
    ASSERT_EQ(src.use_count(), 3);

    o1.mutable_data();  // trigger COW for o1
    ASSERT_EQ(src.use_count(), 2);   // src + o2
    ASSERT_EQ(o1.use_count(), 1);    // o1 now exclusive
    ASSERT_EQ(o2.use_count(), 2);   // o2 still with src
}

// =============================================================================
// 显式 Unshare
// =============================================================================

TEST(Unshare_Exclusive_NoEffect) {
    CowBuffer buf(4, "buf");
    const void* orig = buf.raw_ptr();
    buf.Unshare();
    ASSERT_PTR_EQ(buf.raw_ptr(), orig);
    ASSERT_EQ(buf.use_count(), 1);
}

TEST(Unshare_Shared_CreatesCopy) {
    CowBuffer a(4, "a");
    a.mutable_data()[0] = 100.0f;
    CowBuffer b(0, "b");
    b.ShareFrom(a, false);
    b.Unshare();
    ASSERT_PTR_NE(b.raw_ptr(), a.raw_ptr());
    ASSERT_EQ(b.use_count(), 1);
    ASSERT_EQ(a.use_count(), 1);
    b.mutable_data()[0] = 200.0f;
    ASSERT_NEAR(a[0], 100.0f, 1e-6f);
    ASSERT_NEAR(b[0], 200.0f, 1e-6f);
}

TEST(Unshare_IdentityShared_StillCopies) {
    CowBuffer a(4, "a");
    CowBuffer b(0, "b");
    b.ShareFrom(a, true);  // identity passthrough
    ASSERT_TRUE(b.is_identity_share());
    b.Unshare();
    ASSERT_FALSE(b.is_identity_share());
    ASSERT_PTR_NE(b.raw_ptr(), a.raw_ptr());
}

// =============================================================================
// Resize
// =============================================================================

TEST(Resize_SameSize_NoOp) {
    CowBuffer buf(4, "buf");
    const void* orig = buf.raw_ptr();
    buf.Resize(4);
    ASSERT_PTR_EQ(buf.raw_ptr(), orig);
    ASSERT_EQ(buf.size(), 4u);
}

TEST(Resize_Grow_PreservesExistingData) {
    CowBuffer buf(4, "buf");
    for (int i = 0; i < 4; i++) buf.mutable_data()[i] = static_cast<float>(i * 10);
    buf.Resize(8);
    ASSERT_EQ(buf.size(), 8u);
    for (int i = 0; i < 4; i++) {
        ASSERT_NEAR(buf[i], static_cast<float>(i * 10), 1e-6f);
    }
    for (int i = 4; i < 8; i++) {
        ASSERT_NEAR(buf[i], 0.0f, 1e-6f);  // new space zeroed
    }
}

TEST(Resize_Shrink_TruncatesData) {
    CowBuffer buf(8, "buf");
    for (int i = 0; i < 8; i++) buf.mutable_data()[i] = static_cast<float>(i);
    buf.Resize(3);
    ASSERT_EQ(buf.size(), 3u);
    ASSERT_NEAR(buf[0], 0.0f, 1e-6f);
    ASSERT_NEAR(buf[1], 1.0f, 1e-6f);
    ASSERT_NEAR(buf[2], 2.0f, 1e-6f);
}

TEST(Resize_Shared_BreaksShare) {
    CowBuffer a(4, "a");
    a.mutable_data()[0] = 5.0f;
    CowBuffer b(0, "b");
    b.ShareFrom(a, false);
    b.Resize(8);
    ASSERT_PTR_NE(b.raw_ptr(), a.raw_ptr());
    ASSERT_EQ(a.size(), 4u);
    ASSERT_EQ(b.size(), 8u);
    ASSERT_NEAR(a[0], 5.0f, 1e-6f);
    ASSERT_NEAR(b[0], 5.0f, 1e-6f);
    ASSERT_NEAR(b[4], 0.0f, 1e-6f);
}

TEST(Resize_FromZero_AllocatesNew) {
    CowBuffer buf;
    ASSERT_EQ(buf.size(), 0u);
    ASSERT_TRUE(buf.raw_ptr() == nullptr);
    buf.Resize(4);
    ASSERT_EQ(buf.size(), 4u);
    ASSERT_TRUE(buf.raw_ptr() != nullptr);
    for (size_t i = 0; i < 4; i++) {
        ASSERT_NEAR(buf[i], 0.0f, 1e-6f);
    }
}

// =============================================================================
// 运行时开关
// =============================================================================

TEST(RuntimeSwitch_Disabled_NoCOW) {
    SetCOWEnabled(true);
    CowBuffer src(4, "src");
    src.mutable_data()[0] = 1.0f;
    CowBuffer o1(0, "o1");
    o1.ShareFrom(src, false);

    SetCOWEnabled(false);
    const void* src_ptr = src.raw_ptr();
    o1.mutable_data()[0] = 99.0f;
    // COW disabled: o1 writes to shared memory
    ASSERT_PTR_EQ(o1.raw_ptr(), src_ptr);
    ASSERT_NEAR(src[0], 99.0f, 1e-6f);  // polluted!

    SetCOWEnabled(true);  // restore
}

TEST(RuntimeSwitch_ReEnabled_COWWorks) {
    SetCOWEnabled(false);
    SetCOWEnabled(true);
    CowBuffer src(4, "src");
    src.mutable_data()[0] = 1.0f;
    CowBuffer o1(0, "o1");
    o1.ShareFrom(src, false);
    o1.mutable_data()[0] = 55.0f;
    ASSERT_NEAR(src[0], 1.0f, 1e-6f);
    ASSERT_NEAR(o1[0], 55.0f, 1e-6f);
}

// =============================================================================
// 编译期开关（默认不定义，这里测试运行时路径）
// =============================================================================

TEST(CompileTimeSwitch_DefaultCOWEnabled) {
#ifndef COW_DISABLED_AT_COMPILE_TIME
    ASSERT_TRUE(IsCOWEnabled());
#else
    ASSERT_FALSE(IsCOWEnabled());
#endif
}

// =============================================================================
// 引用计数生命周期
// =============================================================================

TEST(RefCount_DestructorDecrements) {
    CowBuffer a(4, "a");
    {
        CowBuffer b(0, "b");
        b.ShareFrom(a, false);
        ASSERT_EQ(a.use_count(), 2);
    }
    ASSERT_EQ(a.use_count(), 1);
}

TEST(RefCount_ShareChain) {
    CowBuffer a(4, "a");
    CowBuffer b(0, "b"), c(0, "c"), d(0, "d");
    b.ShareFrom(a, false);
    c.ShareFrom(b, false);  // share from b, not directly from a
    d.ShareFrom(c, false);
    ASSERT_EQ(a.use_count(), 4);  // a=b=c=d all share same data
    ASSERT_PTR_EQ(a.raw_ptr(), d.raw_ptr());
}

// =============================================================================
// 线程安全（开关是原子的）
// =============================================================================

TEST(RuntimeSwitch_ThreadSafe) {
    SetCOWEnabled(true);
    std::atomic<bool> stop{false};
    std::atomic<int> success{0};

    auto writer = [&]() {
        while (!stop.load(std::memory_order_relaxed)) {
            CowBuffer buf(4, "tbuf");
            buf.mutable_data()[0] = 1.0f;
            success.fetch_add(1, std::memory_order_relaxed);
        }
    };

    auto toggler = [&]() {
        for (int i = 0; i < 100; i++) {
            SetCOWEnabled(i % 2 == 0);
        }
        stop.store(true, std::memory_order_relaxed);
    };

    std::thread t1(writer);
    std::thread t2(writer);
    std::thread t3(toggler);
    t1.join(); t2.join(); t3.join();
    SetCOWEnabled(true);
    ASSERT_TRUE(success.load() > 0);
}

// =============================================================================
// 空缓冲区边界
// =============================================================================

TEST(EmptyBuffer_MutableDataReturnsNull) {
    CowBuffer buf;
    ASSERT_TRUE(buf.mutable_data() == nullptr);
    ASSERT_TRUE(buf.data() == nullptr);
}

TEST(EmptyBuffer_ShareFromEmpty) {
    CowBuffer a;
    CowBuffer b(4, "b");
    b.ShareFrom(a, false);
    ASSERT_EQ(b.size(), 0u);
    ASSERT_TRUE(b.raw_ptr() == nullptr);
}

// =============================================================================
// 单元测试运行器
// =============================================================================

int RunUnitTests() {
    SetLogLevel(LogLevel::kSilent);
    SetCOWEnabled(true);

    std::printf("Running %zu unit tests (silent mode)...\n", GetUnitTests().size());
    auto& tests = GetUnitTests();

    for (auto& t : tests) {
        g_tests_run++;
        try {
            // Reset COW state before each test
            SetCOWEnabled(true);
            t.func();
            g_tests_passed++;
            std::printf("  [PASS] %s\n", t.name);
        } catch (const TestFailure&) {
            g_tests_failed++;
            std::printf("  [FAIL] %s\n", t.name);
        } catch (const std::exception& e) {
            g_tests_failed++;
            std::printf("  [FAIL] %s (exception: %s)\n", t.name, e.what());
        } catch (...) {
            g_tests_failed++;
            std::printf("  [FAIL] %s (unknown exception)\n", t.name);
        }
    }

    std::printf("\nUnit Test Results: %d/%d passed", g_tests_passed, g_tests_run);
    if (g_tests_failed > 0) {
        std::printf(" (%d FAILED)", g_tests_failed);
    }
    std::printf("\n");

    return g_tests_failed > 0 ? 1 : 0;
}

#ifndef COW_DEMO_UNIT_TESTS_ONLY
int main() {
    return RunUnitTests();
}
#endif
