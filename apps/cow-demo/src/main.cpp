// =============================================================================
// Zero-copy COW Read-Write Separation Pattern - Demo & Test Cases
// 零拷贝COW读写分离模式 - 演示与测试用例
// =============================================================================

#include "cow_buffer.hpp"
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

using namespace cow_demo;

// =============================================================================
// 轻量级测试框架（零第三方依赖）
// =============================================================================

struct TestResult {
    std::string name;
    bool passed;
    std::string message;
};

static std::vector<TestResult> g_results;

#define TEST_CASE(name) \
    static bool Test_##name(); \
    static bool _reg_##name = (RegisterTest(#name, Test_##name), true); \
    static bool Test_##name()

#define EXPECT_TRUE(cond) \
    do { if (!(cond)) { \
        std::cerr << "  ✗ FAIL: " #cond " at " << __FILE__ << ":" << __LINE__ << "\n"; \
        return false; \
    }} while(0)

#define EXPECT_FALSE(cond) EXPECT_TRUE(!(cond))

#define EXPECT_EQ(a, b) \
    do { if (!((a) == (b))) { \
        std::cerr << "  ✗ FAIL: " #a " == " #b " at " << __FILE__ << ":" << __LINE__ \
                  << " (" << (a) << " != " << (b) << ")\n"; \
        return false; \
    }} while(0)

#define EXPECT_NE(a, b) \
    do { if ((a) == (b)) { \
        std::cerr << "  ✗ FAIL: " #a " != " #b " at " << __FILE__ << ":" << __LINE__ \
                  << " (both are " << (a) << ")\n"; \
        return false; \
    }} while(0)

#define EXPECT_PTR_EQ(a, b) \
    do { if ((const void*)(a) != (const void*)(b)) { \
        std::cerr << "  ✗ FAIL: " #a " == " #b " at " << __FILE__ << ":" << __LINE__ << "\n"; \
        return false; \
    }} while(0)

#define EXPECT_PTR_NE(a, b) \
    do { if ((const void*)(a) == (const void*)(b)) { \
        std::cerr << "  ✗ FAIL: " #a " != " #b " at " << __FILE__ << ":" << __LINE__ \
                  << " (both are " << (const void*)(a) << ")\n"; \
        return false; \
    }} while(0)

#define EXPECT_NEAR(a, b, tol) \
    do { if (std::fabs((a) - (b)) > (tol)) { \
        std::cerr << "  ✗ FAIL: |" #a " - " #b "| <= " #tol " at " << __FILE__ << ":" << __LINE__ \
                  << " (|" << (a) << " - " << (b) << "| = " << std::fabs((a)-(b)) << ")\n"; \
        return false; \
    }} while(0)

void RegisterTest(const char* name, bool (*func)());
int RunAllTests();

// =============================================================================
// 辅助函数
// =============================================================================

void PrintSeparator(const char* title) {
    std::cout << "\n";
    std::cout << "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n";
    std::cout << "┃  " << title << "\n";
    std::cout << "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n";
}

void PrintBuffer(const CowBuffer& buf, size_t n = 8) {
    const float* d = buf.raw_ptr();
    size_t show = std::min(n, buf.size());
    std::cout << "  📦 '" << buf.name() << "' [";
    for (size_t i = 0; i < show; i++) {
        if (i > 0) std::cout << ", ";
        std::cout << std::fixed << std::setprecision(1) << d[i];
    }
    if (buf.size() > show) std::cout << ", …";
    std::cout << "] refcnt=" << buf.use_count()
              << " size=" << buf.size()
              << " ptr=" << buf.raw_ptr() << "\n";
}

// =============================================================================
// 测试场景1：独占缓冲区读写（不触发COW）
// =============================================================================
TEST_CASE(ExclusiveAccess) {
    PrintSeparator("测试1: 独占访问 — 读写都不复制");

    CowBuffer a(8, "exclusive_buf");
    float* wptr = a.mutable_data();
    for (int i = 0; i < 8; i++) wptr[i] = static_cast<float>(i * 10);

    PrintBuffer(a);

    EXPECT_EQ(a.use_count(), 1);
    EXPECT_NEAR(a[0], 0.0f, 1e-6f);
    EXPECT_NEAR(a[7], 70.0f, 1e-6f);

    const void* ptr1 = a.raw_ptr();
    float* wptr2 = a.mutable_data();  // 第二次写入，独占状态仍不复制
    EXPECT_PTR_EQ(wptr2, ptr1);

    std::cout << "  ✓ 独占访问零复制，指针始终一致\n";
    return true;
}

// =============================================================================
// 测试场景2：const只读访问（永远不触发COW，零开销）
// =============================================================================
TEST_CASE(ConstAccess) {
    PrintSeparator("测试2: const只读访问 — 零开销永远不复制");

    CowBuffer a(8, "source");
    a.mutable_data()[0] = 42.0f;

    CowBuffer b(0, "reader");
    b.ShareFrom(a, false);

    const CowBuffer& const_b = b;
    const float* rptr = const_b.data();
    std::cout << "  🔍 const读取: b[0] = " << rptr[0] << "\n";
    std::cout << "  📊 use_count=" << const_b.use_count() << " (共享状态保持)\n";

    EXPECT_NEAR(rptr[0], 42.0f, 1e-6f);
    EXPECT_EQ(const_b.use_count(), 2);
    EXPECT_PTR_EQ(const_b.raw_ptr(), a.raw_ptr());

    std::cout << "  ✓ const访问零开销，use_count不变，不触发COW\n";
    return true;
}

// =============================================================================
// 测试场景3：N=1单消费者 identity直通
// =============================================================================
TEST_CASE(N1IdentityPassthrough) {
    PrintSeparator("测试3: N=1单消费者 — identity直通（in-place零拷贝）");

    CowBuffer source(8, "source_layer");
    for (int i = 0; i < 8; i++) source.mutable_data()[i] = 1.0f;

    std::cout << "  📌 共享前: source ptr=" << source.raw_ptr()
              << " refcnt=" << source.use_count() << "\n";

    CowBuffer output(0, "N=1_output");
    output.ShareFrom(source, /*identity=*/true);

    std::cout << "\n  写入前:\n";
    PrintBuffer(source);
    PrintBuffer(output);

    float* wptr = output.mutable_data();
    wptr[0] = 99.0f;

    std::cout << "\n  写入output[0]=99后:\n";
    PrintBuffer(source);
    PrintBuffer(output);

    EXPECT_NEAR(source[0], 99.0f, 1e-6f);
    EXPECT_NEAR(output[0], 99.0f, 1e-6f);
    EXPECT_PTR_EQ(source.raw_ptr(), output.raw_ptr());
    EXPECT_EQ(source.use_count(), 2);

    std::cout << "  ✓ N=1 identity直通：指针相同，in-place修改对源可见\n";
    return true;
}

// =============================================================================
// 测试场景4：N=2多消费者 — 写时自动COW隔离
// =============================================================================
TEST_CASE(N2MultiConsumerCOW) {
    PrintSeparator("测试4: N=2多消费者 — 写时COW自动隔离");

    CowBuffer source(8, "source_layer");
    for (int i = 0; i < 8; i++) source.mutable_data()[i] = 1.0f;

    CowBuffer out1(0, "output_1");
    CowBuffer out2(0, "output_2");
    out1.ShareFrom(source, false);
    out2.ShareFrom(source, false);

    std::cout << "  📊 共享后 use_count=" << source.use_count() << "\n";
    PrintBuffer(source);
    PrintBuffer(out1);
    PrintBuffer(out2);

    const void* src_ptr = source.raw_ptr();
    EXPECT_EQ(source.use_count(), 3);
    EXPECT_PTR_EQ(out1.raw_ptr(), src_ptr);
    EXPECT_PTR_EQ(out2.raw_ptr(), src_ptr);
    std::cout << "  🔗 三个缓冲区指向同一内存: " << src_ptr << "\n";

    std::cout << "\n  ✏️  out1写入88.8 — 触发COW!\n";
    float* w1 = out1.mutable_data();
    w1[0] = 88.8f;

    std::cout << "\n  写入后:\n";
    PrintBuffer(source);
    PrintBuffer(out1);
    PrintBuffer(out2);

    EXPECT_NEAR(source[0], 1.0f, 1e-6f);
    EXPECT_NEAR(out2[0], 1.0f, 1e-6f);
    EXPECT_NEAR(out1[0], 88.8f, 1e-6f);
    EXPECT_PTR_NE(out1.raw_ptr(), src_ptr);
    EXPECT_PTR_EQ(out2.raw_ptr(), src_ptr);

    std::cout << "  ✓ COW隔离生效：out1获私有副本，source/out2保持原数据\n";
    return true;
}

// =============================================================================
// 测试场景5：显式Unshare()强制断开共享
// =============================================================================
TEST_CASE(ExplicitUnshare) {
    PrintSeparator("测试5: 显式Unshare() — 强制断开共享");

    CowBuffer a(8, "owner");
    a.mutable_data()[0] = 100.0f;

    CowBuffer b(0, "borrower");
    b.ShareFrom(a, true);

    std::cout << "  📌 Unshare前: a.ptr=" << a.raw_ptr()
              << " b.ptr=" << b.raw_ptr() << "\n";
    EXPECT_PTR_EQ(a.raw_ptr(), b.raw_ptr());

    b.Unshare();

    std::cout << "  📌 Unshare后: a.ptr=" << a.raw_ptr()
              << " b.ptr=" << b.raw_ptr() << "\n";
    EXPECT_PTR_NE(a.raw_ptr(), b.raw_ptr());

    b.mutable_data()[0] = 200.0f;
    EXPECT_NEAR(a[0], 100.0f, 1e-6f);
    EXPECT_NEAR(b[0], 200.0f, 1e-6f);

    std::cout << "  ✓ Unshare强制复制，即使identity共享也断开\n";
    return true;
}

// =============================================================================
// 测试场景6：Resize改变元数据自动打断共享
// =============================================================================
TEST_CASE(ResizeBreaksSharing) {
    PrintSeparator("测试6: Resize元数据修改 — 自动打断共享");

    CowBuffer a(4, "original");
    for (int i = 0; i < 4; i++) a.mutable_data()[i] = static_cast<float>(i);

    CowBuffer b(0, "shared_view");
    b.ShareFrom(a, false);

    std::cout << "  📌 初始: size a=" << a.size() << " b=" << b.size()
              << " 同指针=" << (a.raw_ptr() == b.raw_ptr() ? "YES" : "NO") << "\n";
    EXPECT_EQ(a.size(), 4);
    EXPECT_PTR_EQ(a.raw_ptr(), b.raw_ptr());

    std::cout << "\n  ✏️  b.Resize(8)\n";
    b.Resize(8);

    std::cout << "  📌 Resize后: size a=" << a.size() << " b=" << b.size()
              << " 同指针=" << (a.raw_ptr() == b.raw_ptr() ? "YES" : "NO") << "\n";
    PrintBuffer(a);
    PrintBuffer(b);

    EXPECT_EQ(a.size(), 4);
    EXPECT_EQ(b.size(), 8);
    EXPECT_PTR_NE(a.raw_ptr(), b.raw_ptr());
    EXPECT_NEAR(b[0], 0.0f, 1e-6f);
    EXPECT_NEAR(b[1], 1.0f, 1e-6f);
    EXPECT_NEAR(b[3], 3.0f, 1e-6f);
    EXPECT_NEAR(b[4], 0.0f, 1e-6f);
    EXPECT_NEAR(b[7], 0.0f, 1e-6f);

    std::cout << "  ✓ Resize自动打断共享并扩展新空间，原数据保留+零填充\n";
    return true;
}

// =============================================================================
// 测试场景7：运行期开关 — 紧急回退演示
// =============================================================================
TEST_CASE(RuntimeSwitch) {
    PrintSeparator("测试7: 运行期开关 — 紧急回退A/B测试");

    SetCOWEnabled(true);

    CowBuffer source(8, "source");
    for (int i = 0; i < 8; i++) source.mutable_data()[i] = 5.0f;

    CowBuffer out1(0, "out1");
    CowBuffer out2(0, "out2");
    out1.ShareFrom(source, false);
    out2.ShareFrom(source, false);

    std::cout << "  🔘 COW状态: " << (IsCOWEnabled() ? "ENABLED" : "DISABLED") << "\n";
    std::cout << "  ⚠️  禁用COW（模拟线上紧急回退）\n";
    SetCOWEnabled(false);

    float* w1 = out1.mutable_data();
    w1[0] = 999.0f;

    std::cout << "\n  COW禁用时写入out1:\n";
    PrintBuffer(source);
    PrintBuffer(out1);
    PrintBuffer(out2);
    // COW禁用时，out1写入直接修改共享内存，source/out2看到污染值
    EXPECT_NEAR(source[0], 999.0f, 1e-6f);
    EXPECT_NEAR(out2[0], 999.0f, 1e-6f);
    std::cout << "  ⚠️  COW禁用：无隔离，写入污染所有共享方（预期回退行为）\n";

    std::cout << "\n  🔘 重新启用COW\n";
    SetCOWEnabled(true);

    CowBuffer out3(0, "out3");
    out3.ShareFrom(source, false);
    float* w3 = out3.mutable_data();
    w3[0] = 111.0f;
    std::cout << "\n  COW重新启用后写入out3:\n";
    std::cout << "  source[0] = " << source[0] << " (out3写入不影响source)\n";
    std::cout << "  out3[0]   = " << out3[0] << " (独立副本)\n";
    EXPECT_NEAR(source[0], 999.0f, 1e-6f);
    EXPECT_NEAR(out3[0], 111.0f, 1e-6f);
    EXPECT_PTR_NE(out3.raw_ptr(), source.raw_ptr());

    std::cout << "  ✓ 运行期开关工作正常，动态切换无需重编译\n";
    return true;
}

// =============================================================================
// 测试运行器实现
// =============================================================================

struct TestReg {
    const char* name;
    bool (*func)();
};

static std::vector<TestReg>& GetTests() {
    static std::vector<TestReg> tests;
    return tests;
}

void RegisterTest(const char* name, bool (*func)()) {
    GetTests().push_back({name, func});
}

int RunAllTests() {
    int passed = 0, failed = 0;
    std::cout << "\n";
    std::cout << "╔══════════════════════════════════════════════════════════════╗\n";
    std::cout << "║         Zero-copy COW Demo - Running " << GetTests().size() << " Tests          ║\n";
    std::cout << "╚══════════════════════════════════════════════════════════════╝\n";

    for (auto& t : GetTests()) {
        std::cout << "\n▶ [" << t.name << "] ";
        std::cout.flush();
        bool ok = false;
        try {
            ok = t.func();
        } catch (const std::exception& e) {
            std::cerr << "\n  💥 EXCEPTION: " << e.what() << "\n";
            ok = false;
        } catch (...) {
            std::cerr << "\n  💥 UNKNOWN EXCEPTION\n";
            ok = false;
        }
        if (ok) {
            passed++;
            std::cout << "\n  🟢 PASSED: " << t.name << "\n";
            g_results.push_back({t.name, true, ""});
        } else {
            failed++;
            std::cout << "\n  🔴 FAILED: " << t.name << "\n";
            g_results.push_back({t.name, false, "assertion failed"});
        }
    }

    std::cout << "\n";
    std::cout << "╔══════════════════════════════════════════════════════════════╗\n";
    std::cout << "║                       Test Summary                          ║\n";
    std::cout << "╠══════════════════════════════════════════════════════════════╣\n";
    printf("║  Total:  %2d   Passed: %2d   Failed: %2d                        ║\n",
           (int)GetTests().size(), passed, failed);
    std::cout << "╚══════════════════════════════════════════════════════════════╝\n";

    if (failed == 0) {
        std::cout << "\n🎉 所有测试通过！\n\n";
        std::cout << "模式5步法验证：\n";
        std::cout << "  1. ✓ const/non-const读写API分离（data() const vs mutable_data()）\n";
        std::cout << "  2. ✓ 引用计数O(1)零拷贝共享（ShareFrom仅指针赋值）\n";
        std::cout << "  3. ✓ 写时自动克隆（mutable_data()按需触发COW）\n";
        std::cout << "  4. ✓ N=1 identity直通 + N≥2 COW隔离分层策略\n";
        std::cout << "  5. ✓ 编译期宏 + 运行期原子开关双重回退\n";
    }

    return failed > 0 ? 1 : 0;
}

// =============================================================================
// 主函数
// =============================================================================
int main() {
    std::cout << "============================================================\n";
    std::cout << "  Zero-copy COW Read-Write Separation Pattern Demo\n";
    std::cout << "  零拷贝COW读写分离模式 - C++示例框架\n";
    std::cout << "============================================================\n";
    std::cout << "  COW Enabled: " << (IsCOWEnabled() ? "YES" : "NO") << "\n";
    std::cout << "  Log Level:   " << static_cast<int>(GetLogLevel())
              << " (0=silent 1=normal 2=verbose)\n";

    SetLogLevel(LogLevel::kNormal);  // demo模式用normal级别日志
    return RunAllTests();
}
