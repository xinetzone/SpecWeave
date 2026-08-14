#!/bin/bash
# test-timer-parser.sh — [TIMER] 日志解析逻辑单元测试
#
# 用途：验证 build.sh 中 parse_timer_logs() 函数能正确从 docker build 日志中
#       提取 [TIMER] 标记的阶段名称和耗时。
#
# 测试策略：
#   1. 生成模拟 docker build 日志（包含真实的 [TIMER] 标记格式）
#   2. 从 build.sh 中提取 parse_timer_logs 函数
#   3. 对模拟日志执行解析
#   4. 验证解析结果是否与预期一致
#
# 用法：
#   bash variants/scripts/test-timer-parser.sh          # 运行所有测试
#   bash variants/scripts/test-timer-parser.sh -v       # 详细输出
#
# 不需要 Docker，可在任何有 bash 的环境运行。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_SH="${VARIANTS_DIR}/build.sh"

VERBOSE=0
[[ "${1:-}" == "-v" || "${1:-}" == "--verbose" ]] && VERBOSE=1

TEST_PASS=0
TEST_FAIL=0
TEST_TOTAL=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { if [[ $VERBOSE -eq 1 ]]; then echo -e "$@"; fi; }
pass() { echo -e "  ${GREEN}PASS${NC}: $1"; TEST_PASS=$((TEST_PASS+1)); TEST_TOTAL=$((TEST_TOTAL+1)); }
fail() { echo -e "  ${RED}FAIL${NC}: $1"; TEST_FAIL=$((TEST_FAIL+1)); TEST_TOTAL=$((TEST_TOTAL+1)); }
info() { echo -e "  ${BLUE}INFO${NC}: $1"; }

# ─── 从 build.sh 中提取 parse_timer_logs 函数 ────────────────────────────────
extract_parse_function() {
    # 使用 awk 提取从 "parse_timer_logs() {" 开始到下一个顶级 "}" 结束的函数体
    awk '
    /^parse_timer_logs\(\)/ { in_func=1; depth=0 }
    in_func {
        print
        # 统计花括号深度（忽略字符串内的花括号——对我们的函数足够）
        n_open = gsub(/\{/, "{")
        n_close = gsub(/\}/, "}")
        depth += n_open - n_close
        if (depth <= 0 && n_close > 0 && NR > 1) { exit }
    }
    ' "$BUILD_SH"
}

# ─── 生成模拟日志 ────────────────────────────────────────────────────────────
# 模拟 conda-llvm 变体构建时的真实 [TIMER] 输出格式
generate_mock_conda_llvm_log() {
    local logfile="$1"
    cat > "$logfile" << 'MOCKEOF'
#0 building with "default" instance using docker driver
#1 [internal] load build definition from Dockerfile
#1 transferring dockerfile: 3.82kB 0.0s done
#1 DONE 0.0s
#2 [internal] load metadata for docker.io/library/devcontainer-base:conda-latest
#2 DONE 0.0s

#3 [conda-llvm-add 1/4] FROM devcontainer-base:conda-latest
#3 CACHED

#4 [conda-llvm-add 2/4] RUN echo "" && ...
[TIMER] Conda-LLVM variant build started at 2026-08-07T12:00:00Z
[ACTION] Configuring conda channels for LLVM toolchain...
[OK] Conda channels configured
[ACTION] Creating build timer marker...
[OK] Build timer started
#4 2.3s done
[TIMER] Stage 1/4 (config+init) took 2s | LLVM variant cumulative: 2s

#5 [conda-llvm-add 3/4] RUN echo "" && ...
[ACTION] Installing LLVM/Clang toolchain via conda...
[ACTION] Installing: llvmdev=22.1.* clangdev=22.1.* clang=22.1.* lld=22.1.* lldb=22.1.* ...
[OK] LLVM/Clang installation complete
#5 45.7s done
[TIMER] Stage 2/4 (install toolchain) took 45s | LLVM variant cumulative: 47s

#6 [conda-llvm-add 4/4] RUN echo "" && ...
[ACTION] Creating clang/clang++ symlinks...
[OK] Symlinks created: clang++ -> clang, ld.lld -> lld
[ACTION] Writing activation script...
[OK] Activation script written
#6 3.1s done
[TIMER] Stage 3/4 (symlinks+init+verify) took 3s | LLVM variant cumulative: 50s

#7 [conda-llvm-add 4/4] RUN echo "" && ... (Stage 4/4)
[ACTION] Writing build metadata to /etc/devcontainer-variant-conda-llvm-build-info...
[OK] Build metadata written
[ACTION] Running cleanup...
[OK] Cleanup complete
[VALIDATE 1/9] bash -n /etc/profile.d/conda-llvm-init.sh...
[OK] conda-llvm-init.sh bash syntax valid
[VALIDATE 2/9] llvm-config available and version matches...
[OK] llvm-config executable
22.1.8
[VALIDATE 3/9] clang/clang++ available...
[OK] clang executable
clang version 22.1.8
[OK] clang++ executable
[VALIDATE 4/9] cmake available...
[OK] cmake executable
cmake version 3.31.6
[VALIDATE 9/9] devuser can access LLVM tools...
[OK] devuser can access LLVM toolchain
[VALIDATE] All validation checks completed
[OK] C++ compilation test passed
[TIMER] Stage 4/4 (metadata+final verify) took 8s | LLVM variant cumulative: 58s
╔══════════════════════════════════════════════════════════════╗
║   BUILD TIMING SUMMARY (Conda-LLVM Variant - 4 Add Stages) ║
╠══════════════════════════════════════════════════════════════╣
║  Stage 1/4  channel config + init         2s               ║
║  Stage 2/4  LLVM toolchain install       45s               ║
║  Stage 3/4  symlinks+init script          3s               ║
║  Stage 4/4  metadata+final verify         8s               ║
╠══════════════════════════════════════════════════════════════╣
║  CONDA-LLVM VARIANT TOTAL (add-on)       58s               ║
╚══════════════════════════════════════════════════════════════╝
#7 DONE 8.2s
[TIMER] Build duration: 58s
MOCKEOF
}

# 模拟 conda 变体构建日志
generate_mock_conda_log() {
    local logfile="$1"
    cat > "$logfile" << 'MOCKEOF'
#0 building with "default" instance using docker driver
#1 [internal] load build definition from Dockerfile
#1 DONE 0.0s
[TIMER] Conda variant build started at 2026-08-07T11:50:00Z
[ACTION] Checking system package availability...
[OK] System packages available
[TIMER] Stage 1/5 (system check) took 1s | Variant cumulative: 1s
[ACTION] Installing Miniconda3...
[OK] Miniconda3 installed
[TIMER] Stage 2/5 (Miniconda install) took 35s | Variant cumulative: 36s
[ACTION] Configuring conda/pip mirrors...
[OK] Mirror configuration complete
[TIMER] Stage 3/5 (mirror config) took 4s | Variant cumulative: 40s
[ACTION] Writing activation script and setting permissions...
[OK] Activation script and permissions set
[TIMER] Stage 4/5 (activation+perms) took 2s | Variant cumulative: 42s
[ACTION] Writing build metadata...
[OK] Build metadata written
[VALIDATE 1/7] bash -n /etc/profile.d/conda-init.sh...
[OK] conda-init.sh bash syntax valid
[VALIDATE 7/7] devuser can read conda directory...
[OK] devuser can access conda
[TIMER] Stage 5/5 (metadata+final verify) took 10s | Variant cumulative: 52s
╔══════════════════════════════════════════════════════════════╗
║     BUILD TIMING SUMMARY (Conda Variant - 5 Add Stages)    ║
╠══════════════════════════════════════════════════════════════╣
║  Stage 1/5  system packages check         1s               ║
║  Stage 2/5  Miniconda3 install           35s               ║
║  Stage 3/5  conda/pip mirror config       4s               ║
║  Stage 4/5  activation script+perms       2s               ║
║  Stage 5/5  metadata+final verify        10s               ║
╠══════════════════════════════════════════════════════════════╣
║  VARIANT TOTAL (add-on layers)           52s               ║
╚══════════════════════════════════════════════════════════════╝
#7 DONE 10.1s
[TIMER] Build duration: 52s
MOCKEOF
}

# 生成包含各种边缘情况的日志
generate_mock_edge_cases_log() {
    local logfile="$1"
    cat > "$logfile" << 'MOCKEOF'
# random build output
[TIMER] Test variant build started at 2026-08-07T10:00:00Z
some noise output here
[TIMER] Stage 1/3 (quick stage) took 0s | cumulative: 0s
[TIMER] Stage 2/3 (normal stage) took 120s | cumulative: 120s
[TIMER] Stage 3/3 (long stage) took 3600s | cumulative: 3720s
more noise
[WARNING] something unexpected
╔══════════════════════════════════════════════════════════════╗
║  BUILD TIMING SUMMARY (not parseable as [TIMER] line)       ║
╚══════════════════════════════════════════════════════════════╝
MOCKEOF
}

# ─── 运行解析并返回结果 ──────────────────────────────────────────────────────
run_parser() {
    local logfile="$1"
    local func_def
    func_def=$(extract_parse_function)

    if [[ -z "$func_def" ]]; then
        echo "ERROR: Failed to extract parse_timer_logs from build.sh"
        return 1
    fi

    # 在子shell中加载函数（含log函数stub）并执行
    bash -c "
# Stub functions for logging library calls within parse_timer_logs
log_step() { :; }
log_warn() { echo \"[WARN] \$*\" >&2; }
log_info() { :; }
log_ok()   { :; }
$func_def
parse_timer_logs '$logfile' 'test-variant'
" 2>&1
}

# ─── 测试用例 ────────────────────────────────────────────────────────────────
TMPDIR_TEST=$(mktemp -d)
trap 'rm -rf "$TMPDIR_TEST"' EXIT

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     [TIMER] Log Parser Unit Test                            ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Test 1: 验证函数可提取
echo "─── Test Group 1: Function Extraction ───"
func_def=$(extract_parse_function)
if [[ -n "$func_def" && "$func_def" == *"parse_timer_logs"* ]]; then
    pass "T1: parse_timer_logs function extracted from build.sh ($(echo "$func_def" | wc -l) lines)"
else
    fail "T1: Failed to extract parse_timer_logs function"
fi

# Test 2: conda-llvm 日志解析 - started at 事件
echo ""
echo "─── Test Group 2: Conda-LLVM Mock Log Parsing ───"
MOCK_LLVM_LOG="$TMPDIR_TEST/conda-llvm-build.log"
generate_mock_conda_llvm_log "$MOCK_LLVM_LOG"
result=$(run_parser "$MOCK_LLVM_LOG")
log "$result"

if echo "$result" | grep -q "EVENT:.*Conda-LLVM variant build started"; then
    pass "T2: 'started at' event detected"
else
    fail "T2: 'started at' event NOT detected"
fi

# Test 3: conda-llvm Stage 1
if echo "$result" | grep -q "Stage 1/4 (config+init).*2s"; then
    pass "T3: Stage 1/4 (config+init) = 2s parsed correctly"
else
    stage1_line=$(echo "$result" | grep "Stage 1/4" || echo "NOT FOUND")
    fail "T3: Stage 1/4 (config+init) = 2s NOT parsed correctly, got: $stage1_line"
fi

# Test 4: conda-llvm Stage 2
if echo "$result" | grep -q "Stage 2/4 (install toolchain).*45s"; then
    pass "T4: Stage 2/4 (install toolchain) = 45s parsed correctly"
else
    stage2_line=$(echo "$result" | grep "Stage 2/4" || echo "NOT FOUND")
    fail "T4: Stage 2/4 (install toolchain) = 45s NOT parsed correctly, got: $stage2_line"
fi

# Test 5: conda-llvm Stage 3
if echo "$result" | grep -q "Stage 3/4 (symlinks+init+verify).*3s"; then
    pass "T5: Stage 3/4 (symlinks+init+verify) = 3s parsed correctly"
else
    stage3_line=$(echo "$result" | grep "Stage 3/4" || echo "NOT FOUND")
    fail "T5: Stage 3/4 (symlinks+init+verify) = 3s NOT parsed correctly, got: $stage3_line"
fi

# Test 6: conda-llvm Stage 4 (final stage) - should now be found after fix
if echo "$result" | grep -q "Stage 4/4 (metadata+final verify).*8s"; then
    pass "T6: Stage 4/4 (metadata+final verify) = 8s parsed correctly (bug fixed)"
else
    stage4_line=$(echo "$result" | grep "Stage 4/4" || echo "NOT FOUND")
    fail "T6: Stage 4/4 (metadata+final verify) = 8s NOT parsed, got: $stage4_line"
fi

# Test 7: Build duration should be parsed (now appended to log file after fix)
if echo "$result" | grep -q "TOTAL.*58s"; then
    pass "T7: Total Build duration = 58s parsed correctly (bug fixed: wrapper now appends to log)"
else
    total_line=$(echo "$result" | grep -i "total\|build duration" || echo "NOT FOUND")
    fail "T7: Total Build duration NOT found, got: $total_line"
fi

# Test 8: conda 日志解析
echo ""
echo "─── Test Group 3: Conda Mock Log Parsing ───"
MOCK_CONDA_LOG="$TMPDIR_TEST/conda-build.log"
generate_mock_conda_log "$MOCK_CONDA_LOG"
result_conda=$(run_parser "$MOCK_CONDA_LOG")
log "$result_conda"

conda_stages_found=$(echo "$result_conda" | grep -c "S[0-9]:.*Stage [0-9]/5" || true)
expected_conda_stages=5  # All 5 stages now have [TIMER] tags after fix
if [[ "$conda_stages_found" -eq "$expected_conda_stages" ]]; then
    pass "T8: Conda variant: $conda_stages_found stages parsed (all stages have [TIMER] tags after fix)"
else
    fail "T8: Conda variant: expected $expected_conda_stages stages, found $conda_stages_found"
fi

if echo "$result_conda" | grep -q "Stage 5/5 (metadata+final verify).*10s"; then
    pass "T9: Conda Stage 5/5 (metadata+final verify) = 10s parsed correctly (bug fixed)"
else
    stage5_line=$(echo "$result_conda" | grep "Stage 5/5" || echo "NOT FOUND")
    fail "T9: Conda Stage 5/5 NOT parsed correctly, got: $stage5_line"
fi

# Test 10: 边缘情况 - 0s 和 3600s
echo ""
echo "─── Test Group 4: Edge Cases ───"
MOCK_EDGE_LOG="$TMPDIR_TEST/edge-cases.log"
generate_mock_edge_cases_log "$MOCK_EDGE_LOG"
result_edge=$(run_parser "$MOCK_EDGE_LOG")
log "$result_edge"

if echo "$result_edge" | grep -q "quick stage.*0s"; then
    pass "T10: 0-second duration parsed correctly"
else
    fail "T10: 0-second duration NOT parsed"
fi

if echo "$result_edge" | grep -q "long stage.*3600s"; then
    pass "T11: 3600-second (1 hour) duration parsed correctly"
else
    fail "T11: 3600-second duration NOT parsed"
fi

# Test 12: 忽略非 [TIMER] 噪声
noise_count=$(echo "$result_edge" | grep -c "WARNING\|some noise\|more noise" || true)
if [[ "$noise_count" -eq 0 ]]; then
    pass "T12: Non-[TIMER] noise correctly filtered out"
else
    fail "T12: Noise leaked into parser output ($noise_count non-TIMER lines found)"
fi

# Test 13: 表格行不被解析为stage（应只被识别为summary）
table_lines=$(echo "$result_edge" | grep -c "Stage [0-9]/3" || true)
if [[ "$table_lines" -eq 3 ]]; then
    pass "T13: All 3 edge-case stages parsed, table not double-counted"
else
    fail "T13: Expected 3 stages, found $table_lines"
fi

# ─── 汇总 ────────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    TEST SUMMARY                              ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  %-20s %3d tests                           ║\n" "TOTAL:" "$TEST_TOTAL"
printf "║  %-20s %3d tests                           ║\n" "PASSED:" "$TEST_PASS"
printf "║  %-20s %3d tests                           ║\n" "FAILED:" "$TEST_FAIL"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

if [[ $TEST_FAIL -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}⚠  $TEST_FAIL test(s) failed — see details above${NC}"
    echo ""
    exit 1
else
    echo -e "${GREEN}All ${TEST_PASS} tests passed!${NC}"
    echo ""
    echo "Parser correctly extracts:"
    echo "  - 'started at' events from Dockerfile RUN output"
    echo "  - All stage timings (Stage N/M took Xs) including final stage"
    echo "  - Total build duration appended by build.sh wrapper"
    echo "  - 0s and 3600s+ durations"
    echo "  - Non-[TIMER] noise is properly filtered out"
    echo ""
    exit 0
fi
