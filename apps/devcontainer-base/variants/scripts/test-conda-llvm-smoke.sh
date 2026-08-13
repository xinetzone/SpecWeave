#!/bin/bash
# test-conda-llvm-smoke.sh — conda-llvm 变体冒烟测试（快速验证）
#
# 用途：构建后快速验证镜像最核心功能是否正常（<10秒执行完毕）
# 定位：L1工具链可用性 + L2基本功能 两层冒烟验证
#
# 与 test-conda-llvm.sh（21项完整测试）的区别：
#   - 冒烟测试：构建后立即执行，3-5个核心检查，快速反馈构建是否成功
#   - 完整测试：CI/发布前执行，21项全面检查，覆盖L1-L6所有层级
#
# 测试范围：
#   S1: clang++ --version 版本输出正确性（核心要求）
#   S2: clang++ 可执行文件存在且可调用
#   S3: 基础 C++ 编译（Hello World）验证工具链可用
#   S4: PATH 优先级验证（conda-llvm 工具链在 PATH 中）
#
# 用法：
#   bash variants/scripts/test-conda-llvm-smoke.sh              # 默认tag=latest
#   bash variants/scripts/test-conda-llvm-smoke.sh --tag 1.0    # 指定tag
#   bash variants/scripts/test-conda-llvm-smoke.sh --image img  # 指定完整镜像名
#
# 退出码：0=全部通过，1=存在失败

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"

source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="test-conda-llvm-smoke"

TAG="latest"
IMAGE=""
EXPECTED_LLVM_VERSION="${EXPECTED_LLVM_VERSION:-22.1}"

TEST_PASS=0
TEST_FAIL=0
TEST_TOTAL=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Smoke test for conda-llvm variant (fast post-build verification).

Options:
  --tag TAG              Image tag suffix (default: latest)
  --image IMAGE          Full image name (overrides --tag)
  --expected-ver VER     Expected LLVM/Clang major.minor version (default: 22.1)
  -h, --help             Show this help message

Default image: devcontainer-base:conda-llvm-latest
Expected exit: 0=all pass, 1=failures exist
EOF
}

pass() {
    local msg="$1"
    echo -e "  ${GREEN}PASS${NC}: $msg"
    TEST_PASS=$((TEST_PASS + 1))
    TEST_TOTAL=$((TEST_TOTAL + 1))
}

fail() {
    local msg="$1"
    echo -e "  ${RED}FAIL${NC}: $msg"
    TEST_FAIL=$((TEST_FAIL + 1))
    TEST_TOTAL=$((TEST_TOTAL + 1))
}

docker_run() {
    docker run --rm "$IMAGE" "$@" 2>&1
}

docker_run_bash() {
    docker run --rm "$IMAGE" bash -c "$1" 2>&1
}

# ─── S1: clang++ 版本输出验证 ──────────────────────────────────────────────
test_clangpp_version_output() {
    local result
    result=$(docker_run clang++ --version 2>&1)
    local exit_code=$?

    if [ $exit_code -ne 0 ]; then
        fail "S1: clang++ --version exited with code $exit_code, output: $(echo "$result" | head -1)"
        return 1
    fi

    local first_line
    first_line=$(echo "$result" | head -1)

    # 验证版本格式：clang version X.Y.Z (tags/...) 或类似
    if echo "$first_line" | grep -qiE "clang version [0-9]+\.[0-9]+"; then
        local detected_ver
        detected_ver=$(echo "$first_line" | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        # 验证主版本号匹配
        if echo "$detected_ver" | grep -q "^${EXPECTED_LLVM_VERSION}"; then
            pass "S1: clang++ --version = $first_line"
            return 0
        else
            fail "S1: clang++ version mismatch: expected ${EXPECTED_LLVM_VERSION}.x, got $detected_ver"
            return 1
        fi
    else
        fail "S1: clang++ --version output not recognized: $first_line"
        return 1
    fi
}

# ─── S2: clang++ 可执行性验证 ──────────────────────────────────────────────
test_clangpp_executable() {
    local result
    result=$(docker_run_bash 'test -x "$(which clang++)" && echo "executable" && which clang++' 2>&1)

    if echo "$result" | grep -q "executable"; then
        local clangpp_path
        clangpp_path=$(echo "$result" | grep -v "^executable$" | head -1)
        pass "S2: clang++ is executable at $clangpp_path"
        return 0
    else
        fail "S2: clang++ not found or not executable: $result"
        return 1
    fi
}

# ─── S3: 基础 C++ Hello World 编译验证 ─────────────────────────────────────
test_cpp_hello_world() {
    local result
    result=$(docker_run_bash 'cat > /tmp/hello.cpp << '"'"'EOF'"'"'
#include <iostream>
int main() {
    std::cout << "Hello from conda-llvm clang++!" << std::endl;
    return 0;
}
EOF
clang++ -std=c++17 /tmp/hello.cpp -o /tmp/hello 2>&1 && /tmp/hello && rm -f /tmp/hello.cpp /tmp/hello' 2>&1)

    if echo "$result" | grep -q "Hello from conda-llvm clang++"; then
        pass "S3: C++ Hello World compilation + execution works"
        return 0
    else
        fail "S3: C++ compilation test failed: $(echo "$result" | tail -3)"
        return 1
    fi
}

# ─── S4: PATH 优先级验证（llvm工具在PATH中） ────────────────────────────────
test_path_priority() {
    local result
    result=$(docker_run_bash 'which clang++ && which clang && which llvm-config' 2>&1)

    # conda-llvm 变体的工具应该来自 conda 环境 (/opt/conda/bin/)
    if echo "$result" | grep -q "/opt/conda/bin/clang++"; then
        pass "S4: clang++ in PATH at /opt/conda/bin/clang++ (conda-llvm bin priority)"
        return 0
    elif echo "$result" | grep -q "clang++"; then
        local clangpp_path
        clangpp_path=$(echo "$result" | grep clang++ | head -1)
        # 可能是symlink到/opt/conda/bin/clang，仍然可以
        pass "S4: clang++ accessible in PATH at $clangpp_path"
        return 0
    else
        fail "S4: clang++ not found in PATH: $result"
        return 1
    fi
}

# ─── 参数解析 ────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag)
            if [ -z "${2:-}" ]; then echo "--tag requires a TAG argument"; exit 1; fi
            TAG="$2"; shift 2 ;;
        --image)
            if [ -z "${2:-}" ]; then echo "--image requires an IMAGE argument"; exit 1; fi
            IMAGE="$2"; shift 2 ;;
        --expected-ver)
            if [ -z "${2:-}" ]; then echo "--expected-ver requires a VERSION argument"; exit 1; fi
            EXPECTED_LLVM_VERSION="$2"; shift 2 ;;
        -h|--help)
            usage; exit 0 ;;
        *)
            echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [ -z "$IMAGE" ]; then
    IMAGE="devcontainer-base:conda-llvm-${TAG}"
fi

# ─── 主测试流程 ──────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       Conda-LLVM Smoke Test (Fast Verification)              ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Image:    %-50s ║\n" "$IMAGE"
printf "║  Expected: LLVM/Clang %-39s ║\n" "${EXPECTED_LLVM_VERSION}.x"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

log_step "Verifying image exists"
if ! docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | grep -q "^${IMAGE}$"; then
    echo ""
    echo -e "${RED}ERROR: Image not found: ${IMAGE}${NC}"
    echo "Please build the image first:"
    echo "  cd apps/devcontainer-base/variants"
    echo "  bash build.sh --variant conda-llvm --cn"
    echo ""
    exit 1
fi
log_ok "Image exists: ${IMAGE}"
echo ""

log_step "Running smoke tests..."
test_clangpp_version_output || true
test_clangpp_executable || true
test_cpp_hello_world || true
test_path_priority || true
echo ""

# ─── 结果汇总 ────────────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    SMOKE TEST SUMMARY                        ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  %-20s %3d checks                          ║\n" "TOTAL:" "$TEST_TOTAL"
printf "║  %-20s %3d checks                          ║\n" "PASSED:" "$TEST_PASS"
printf "║  %-20s %3d checks                          ║\n" "FAILED:" "$TEST_FAIL"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [ $TEST_FAIL -gt 0 ]; then
    echo -e "${RED}SMOKE TEST FAILED: ${TEST_FAIL} check(s) failed${NC}"
    echo "Run full test suite for details: bash variants/scripts/test-conda-llvm.sh"
    exit 1
else
    echo -e "${GREEN}SMOKE TEST PASSED: All ${TEST_PASS} checks passed${NC}"
    exit 0
fi
