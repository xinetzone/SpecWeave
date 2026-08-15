#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"

source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="test-conda-llvm"
LOG_JSON_OUTPUT="/tmp/test-conda-llvm-events.jsonl"

TAG="latest"
IMAGE=""

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

Unit test script for conda-llvm variant.

Options:
  --tag TAG        Image tag suffix (default: latest)
  --image IMAGE    Full image name (overrides --tag)
  -h, --help       Show this help message

Default image: devcontainer-base:conda-llvm-latest
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

skip() {
    local msg="$1"
    echo -e "  ${YELLOW}SKIP${NC}: $msg"
}

docker_run() {
    docker run --rm "$IMAGE" "$@" 2>&1
}

docker_run_bash() {
    docker run --rm "$IMAGE" bash -c "$1" 2>&1
}

test_llvm_config_version() {
    local result
    result=$(docker_run llvm-config --version 2>&1)
    if echo "$result" | grep -q "22.1"; then
        pass "T1: llvm-config --version = $result"
        return 0
    else
        fail "T1: llvm-config --version expected 22.1.x, got: $result"
        return 1
    fi
}

test_clang_version() {
    local result
    result=$(docker_run clang --version 2>&1)
    if echo "$result" | grep -q "22.1"; then
        pass "T2: clang --version contains 22.1.x"
        return 0
    else
        fail "T2: clang --version expected 22.1.x, got: $(echo "$result" | head -1)"
        return 1
    fi
}

test_clangpp_version() {
    local result
    result=$(docker_run clang++ --version 2>&1)
    if echo "$result" | grep -q "22.1"; then
        pass "T3: clang++ --version contains 22.1.x"
        return 0
    else
        fail "T3: clang++ --version expected 22.1.x, got: $(echo "$result" | head -1)"
        return 1
    fi
}

test_cmake_version() {
    local result
    result=$(docker_run cmake --version 2>&1)
    local cmake_ver
    # 容器 entrypoint 会输出服务诊断日志，cmake --version 行混在其中，
    # 不能直接用 head -1（会取到日志行）。改为从完整输出中精确提取版本。
    cmake_ver=$(echo "$result" | grep -oE 'cmake version [0-9]+\.[0-9]+' | head -1 | awk '{print $3}')
    # conda-forge 现已提供 cmake 4.x；同时兼容 3.x，故匹配 ^[34]\.
    if echo "$cmake_ver" | grep -qE "^[34]\."; then
        pass "T4: cmake --version = $cmake_ver (>= 3.x)"
        return 0
    else
        fail "T4: cmake version expected >= 3.x, got: $cmake_ver"
        return 1
    fi
}

test_ninja_version() {
    local result
    result=$(docker_run ninja --version 2>&1)
    if [ -n "$result" ] && [ "$result" != "" ]; then
        pass "T5: ninja --version = $result"
        return 0
    else
        fail "T5: ninja not executable or no version output"
        return 1
    fi
}

test_make_version() {
    local result
    result=$(docker_run make --version 2>&1)
    if echo "$result" | grep -qi "GNU Make"; then
        pass "T6: make --version reports GNU Make"
        return 0
    else
        fail "T6: make expected GNU Make, got: $(echo "$result" | head -1)"
        return 1
    fi
}

test_cpp_hello_world() {
    local result
    result=$(docker_run_bash 'cat > /tmp/hello.cpp << EOF
#include <iostream>
int main() {
    std::cout << "Hello from LLVM/Clang!" << std::endl;
    return 0;
}
EOF
clang++ -std=c++17 /tmp/hello.cpp -o /tmp/hello 2>&1 && /tmp/hello && rm -f /tmp/hello.cpp /tmp/hello' 2>&1)
    if echo "$result" | grep -q "Hello from LLVM/Clang"; then
        pass "T7: C++ Hello World compilation and execution"
        return 0
    else
        fail "T7: C++ Hello World test failed, output: $result"
        return 1
    fi
}

test_cpp17_features() {
    local result
    result=$(docker_run_bash 'cat > /tmp/cpp17.cpp << EOF
#include <iostream>
#include <optional>
#include <string>
#include <tuple>

std::optional<std::string> get_greeting(bool present) {
    if (present) {
        return "C++17 works!";
    }
    return std::nullopt;
}

int main() {
    auto [msg, ok] = []() -> std::tuple<std::string, bool> {
        auto g = get_greeting(true);
        if (g) return {*g, true};
        return {"", false};
    }();
    if (ok) {
        std::cout << msg << std::endl;
        return 0;
    }
    return 1;
}
EOF
clang++ -std=c++17 /tmp/cpp17.cpp -o /tmp/cpp17 2>&1 && /tmp/cpp17 && rm -f /tmp/cpp17.cpp /tmp/cpp17' 2>&1)
    if echo "$result" | grep -q "C++17 works"; then
        pass "T8: C++17 features (std::optional, structured bindings)"
        return 0
    else
        fail "T8: C++17 features test failed, output: $result"
        return 1
    fi
}

test_cpp_optimization() {
    local result
    result=$(docker_run_bash 'cat > /tmp/opt_test.cpp << EOF
#include <iostream>
static inline int add(int a, int b) { return a + b; }
int main() {
    int sum = 0;
    for (int i = 0; i < 1000; i++) sum = add(sum, i);
    std::cout << sum << std::endl;
    return 0;
}
EOF
clang++ -O2 /tmp/opt_test.cpp -o /tmp/opt_test 2>&1 && /tmp/opt_test && rm -f /tmp/opt_test.cpp /tmp/opt_test' 2>&1)
    if echo "$result" | grep -q "499500"; then
        pass "T9: C++ -O2 optimization test (sum 0-999 = 499500)"
        return 0
    else
        fail "T9: C++ optimization test failed, output: $result"
        return 1
    fi
}

test_llvm_components() {
    local result
    result=$(docker_run llvm-config --components 2>&1)
    if echo "$result" | grep -q "core" && echo "$result" | grep -q "support"; then
        local comp_count
        comp_count=$(echo "$result" | wc -w)
        pass "T10: llvm-config --components lists core/support (${comp_count} components)"
        return 0
    else
        fail "T10: llvm-config --components missing core/support, got: $(echo "$result" | head -1)"
        return 1
    fi
}

test_llvm_includedir() {
    local result
    result=$(docker_run_bash 'incdir=$(llvm-config --includedir); test -d "$incdir" && echo "$incdir" && ls "$incdir" | head -3' 2>&1)
    if echo "$result" | grep -q "llvm" || [ -n "$result" ]; then
        pass "T11: llvm-config --includedir path exists: $(echo "$result" | head -1)"
        return 0
    else
        fail "T11: llvm include directory not found or empty"
        return 1
    fi
}

test_sshd_config() {
    local result
    result=$(docker_run_bash 'test -f /etc/ssh/sshd_config && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T12: SSH config file exists (/etc/ssh/sshd_config)"
        return 0
    else
        fail "T12: SSH config file not found"
        return 1
    fi
}

test_supervisord_config() {
    local result
    result=$(docker_run_bash 'test -f /etc/supervisord.conf && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T13: supervisord config exists (/etc/supervisord.conf)"
        return 0
    else
        fail "T13: supervisord config not found"
        return 1
    fi
}

test_jupyter_executable() {
    local rc
    docker run --rm "$IMAGE" bash -c 'test -x /opt/conda/envs/main/bin/jupyter' >/dev/null 2>&1
    rc=$?
    if [ "$rc" -eq 0 ]; then
        pass "T14: Jupyter executable exists (/opt/conda/envs/main/bin/jupyter)"
        return 0
    else
        fail "T14: Jupyter executable not found at /opt/conda/envs/main/bin/jupyter"
        return 1
    fi
}

test_docker_cli() {
    local result
    result=$(docker_run docker --version 2>&1)
    if echo "$result" | grep -qi "docker version"; then
        pass "T15: Docker CLI available: $(echo "$result" | head -1)"
        return 0
    else
        fail "T15: Docker CLI not available, got: $result"
        return 1
    fi
}

test_devuser_exists() {
    local result
    result=$(docker_run id devuser 2>&1)
    if echo "$result" | grep -q "uid="; then
        pass "T16: devuser exists: $result"
        return 0
    else
        fail "T16: devuser does not exist, got: $result"
        return 1
    fi
}

test_conda_version() {
    local result
    result=$(docker_run /opt/conda/bin/conda --version 2>&1)
    if echo "$result" | grep -q "conda"; then
        pass "T17: conda --version available: $result"
        return 0
    else
        fail "T17: conda not available, got: $result"
        return 1
    fi
}

test_conda_dir_exists() {
    local result
    result=$(docker_run_bash 'test -d /opt/conda && echo "exists"' 2>&1)
    if echo "$result" | grep -q "exists"; then
        pass "T18: /opt/conda directory exists"
        return 0
    else
        fail "T18: /opt/conda directory not found"
        return 1
    fi
}

test_conda_path_priority() {
    local result
    result=$(docker_run_bash 'which python' 2>&1)
    if echo "$result" | grep -q "/opt/conda/envs/main/bin/python"; then
        pass "T19: python points to conda main env: $result"
        return 0
    else
        fail "T19: python does not point to main env (expected /opt/conda/envs/main/bin/python), got: $result"
        return 1
    fi
}

test_venv_preserved() {
    local result
    result=$(docker_run_bash 'test ! -d /opt/venv && echo "VENV_REMOVED"' 2>&1)
    if echo "$result" | grep -q "VENV_REMOVED"; then
        pass "T20: /opt/venv removed (using conda only)"
        return 0
    else
        fail "T20: /opt/venv directory still exists (venv not removed)"
        return 1
    fi
}

test_condarc_exists() {
    local result
    result=$(docker_run_bash 'test -f /opt/conda/.condarc && cat /opt/conda/.condarc | head -5' 2>&1)
    if [ -n "$result" ] && ! echo "$result" | grep -q "No such file"; then
        pass "T21: .condarc configuration exists"
        return 0
    else
        fail "T21: .condarc not found or not readable"
        return 1
    fi
}

test_main_gil_disabled() {
    local result
    result=$(docker_run /opt/conda/envs/main/bin/python -c "import sys;print('FT_OK' if sys._is_gil_enabled() is False else 'GIL_UNEXPECTED_ENABLED')" 2>&1)
    if echo "$result" | grep -q "FT_OK"; then
        pass "T22: main env GIL disabled (free-threading guard, cp314t)"
        return 0
    else
        fail "T22: main env GIL not disabled or _is_gil_enabled API missing, output: $(echo "$result" | tail -3)"
        return 1
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag)
            if [ -z "$2" ]; then
                log_error "--tag requires a TAG argument"
                usage
                exit 1
            fi
            TAG="$2"
            shift 2
            ;;
        --image)
            if [ -z "$2" ]; then
                log_error "--image requires an IMAGE argument"
                usage
                exit 1
            fi
            IMAGE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

if [ -z "$IMAGE" ]; then
    IMAGE="devcontainer-base:conda-llvm-${TAG}"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       Conda-LLVM Variant Unit Test Suite                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
log_info "Testing image: ${IMAGE}"
echo ""

log_step "Verifying image exists"
if ! docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE}$"; then
    log_fatal "Image not found: ${IMAGE}. Please build it first."
fi
log_ok "Image exists: ${IMAGE}"
echo ""

log_step "1. Basic Toolchain Availability Tests"
test_llvm_config_version || true
test_clang_version || true
test_clangpp_version || true
test_cmake_version || true
test_ninja_version || true
test_make_version || true
echo ""

log_step "2. C++ Compilation Tests"
test_cpp_hello_world || true
test_cpp17_features || true
test_cpp_optimization || true
echo ""

log_step "3. LLVM Functionality Tests"
test_llvm_components || true
test_llvm_includedir || true
echo ""

log_step "4. Base Service Inheritance Tests"
test_sshd_config || true
test_supervisord_config || true
test_jupyter_executable || true
test_docker_cli || true
test_devuser_exists || true
echo ""

log_step "5. Conda Environment Tests"
test_conda_version || true
test_conda_dir_exists || true
test_conda_path_priority || true
test_venv_preserved || true
echo ""

log_step "6. Conda Mirror Configuration Tests"
test_condarc_exists || true
echo ""

log_step "7. Free-threading Guard Tests"
test_main_gil_disabled || true
echo ""

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                              ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  %-20s %3d tests                           ║\n" "TOTAL:" "$TEST_TOTAL"
printf "║  %-20s %3d tests                           ║\n" "PASSED:" "$TEST_PASS"
printf "║  %-20s %3d tests                           ║\n" "FAILED:" "$TEST_FAIL"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [ $TEST_FAIL -gt 0 ]; then
    echo -e "${RED}${TEST_FAIL} test(s) failed!${NC}"
    exit 1
else
    echo -e "${GREEN}All ${TEST_PASS} tests passed!${NC}"
    exit 0
fi
