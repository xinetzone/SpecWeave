#!/bin/bash
# =============================================================================
# scripts/ft-benchmark.sh — Free-Threading 自动性能基准测试脚本
# =============================================================================
# 用途：构建新镜像后自动运行 free_threading_demo.py，解析加速比数据，
#       记录到日志文件，并验证加速比是否达到阈值。
#
# 用法：
#   ./scripts/ft-benchmark.sh [OPTIONS]
#
# 选项：
#   -i, --image IMAGE       镜像名 (default: devcontainer-base:conda-libmamba-ft)
#   -r, --range N           素数范围 (default: 500000 for quick, 2000000 for full)
#   -t, --min-threshold X   8线程最小加速比阈值 (default: 3.0)
#   -o, --log-file FILE     基准测试日志JSONL文件路径
#   -q, --quick             快速模式 (BENCHMARK_RANGE=500000, threshold=3.0)
#   -f, --full              完整模式 (BENCHMARK_RANGE=2000000, threshold=4.0)
#   -c, --cleanup           测试后删除容器 (default: true)
#   -v, --verbose           显示demo完整输出
#   -j, --json              JSON输出（机器可解析）
#   -h, --help              显示帮助
#
# 环境变量：
#   BENCHMARK_RANGE    素数范围 (覆盖 -r)
#   MIN_SPEEDUP        最小加速比阈值 (覆盖 -t)
#   BENCHMARK_LOG      日志文件路径 (覆盖 -o)
#
# 退出码：
#   0 - 测试通过（8线程加速 >= 阈值）
#   1 - 测试失败（加速比不达标或运行错误）
#   2 - 参数错误
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Defaults
IMAGE="${IMAGE:-devcontainer-base:conda-libmamba-ft}"
RANGE="${BENCHMARK_RANGE:-500000}"
MIN_SPEEDUP="${MIN_SPEEDUP:-3.0}"
LOG_FILE="${BENCHMARK_LOG:-${PROJECT_DIR}/logs/benchmarks/ft-benchmark-$(date +%Y%m%d).jsonl}"
CLEANUP=true
VERBOSE=false
QUICK=false
FULL=false
JSON_OUTPUT=false

# Colors (TTY only)
if [ -t 1 ]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; RESET=''
fi

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Run free-threading performance benchmark on a Docker image and record results.

Options:
  -i, --image IMAGE       Docker image (default: devcontainer-base:conda-libmamba-ft)
  -r, --range N           Prime range upper bound (default: 500000)
  -t, --min-threshold X   Minimum 8-thread speedup threshold (default: 3.0)
  -o, --log-file FILE     Benchmark log JSONL file path
  -q, --quick             Quick mode (range=500000, threshold=3.0, CI/smoke test)
  -f, --full              Full mode (range=2000000, threshold=4.0, thorough validation)
  --no-cleanup            Keep test container after run
  -v, --verbose           Show full demo output
  -j, --json              Output JSON result to stdout
  -h, --help              Show this help

Examples:
  $0                                    # Quick smoke benchmark (500K primes, 3.0x threshold)
  $0 -f                                 # Full benchmark (2M primes, 4.0x threshold)
  $0 -i myimage:tag -r 100000 -t 3.5   # Custom image/threshold
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -i|--image) IMAGE="$2"; shift 2 ;;
        -r|--range) RANGE="$2"; shift 2 ;;
        -t|--min-threshold) MIN_SPEEDUP="$2"; shift 2 ;;
        -o|--log-file) LOG_FILE="$2"; shift 2 ;;
        -q|--quick) QUICK=true; RANGE=500000; MIN_SPEEDUP=3.0; shift ;;
        -f|--full) FULL=true; RANGE=2000000; MIN_SPEEDUP=4.0; shift ;;
        --no-cleanup) CLEANUP=false; shift ;;
        -v|--verbose) VERBOSE=true; shift ;;
        -j|--json) JSON_OUTPUT=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 2 ;;
    esac
done

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

echo -e "${BOLD}━━━ Free-Threading Performance Benchmark ━━━${RESET}"
echo ""
echo "  Image:        $IMAGE"
echo "  Prime range:  0..$RANGE"
echo "  Min speedup:  ${MIN_SPEEDUP}x (8-thread)"
echo "  Log file:     $LOG_FILE"
echo ""

# Check image exists
if ! docker image inspect "$IMAGE" >/dev/null 2>&1; then
    echo -e "${RED}ERROR: Image '$IMAGE' not found${RESET}"
    exit 1
fi

# Detect Python build type
echo "─── Environment Detection ───"
PY_BUILD=$(docker run --rm --entrypoint /opt/conda/envs/main/bin/python "$IMAGE" -c \
    "import sysconfig; print('cp314t' if sysconfig.get_config_var('Py_GIL_DISABLED') else 'cp314')" 2>&1)
PY_VER=$(docker run --rm --entrypoint /opt/conda/envs/main/bin/python "$IMAGE" -c \
    "import sys; print(sys.version.split()[0])" 2>&1)
CPU_COUNT=$(docker run --rm --entrypoint /opt/conda/envs/main/bin/python "$IMAGE" -c \
    "import os; print(os.cpu_count() or 0)" 2>&1)

echo "  Python:       $PY_VER"
echo "  Build type:   $PY_BUILD"
echo "  CPU cores:    $CPU_COUNT"
echo ""

# Check if it's a free-threading build; standard build can't benefit from threading
if [ "$PY_BUILD" != "cp314t" ]; then
    echo -e "${YELLOW}WARNING: Not a free-threading build (cp314). Threading speedup will be ~1.0x.${RESET}"
    echo "  Benchmark will still run but 8-thread speedup threshold will be adjusted."
    MIN_SPEEDUP="0.8"  # Standard build should have ~1x speedup (no worse than 0.8x)
fi

# Copy demo script to a temp location and mount it
DEMO_SCRIPT="${PROJECT_DIR}/examples/free_threading_demo.py"
if [ ! -f "$DEMO_SCRIPT" ]; then
    echo -e "${RED}ERROR: Demo script not found at $DEMO_SCRIPT${RESET}"
    exit 1
fi

CONTAINER_NAME="ft-bench-$(date +%s)"
echo "─── Running Benchmark ───"
echo "  Container: $CONTAINER_NAME"
echo ""

BENCH_START=$(date +%s)
BENCH_START_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Run the benchmark
set +e
DEMO_OUTPUT=$(docker run --rm \
    --name "$CONTAINER_NAME" \
    -e BENCHMARK_RANGE="$RANGE" \
    -v "${DEMO_SCRIPT}:/tmp/demo.py:ro" \
    --entrypoint /opt/conda/envs/main/bin/python \
    "$IMAGE" /tmp/demo.py 2>&1)
DEMO_RC=$?
set -e

BENCH_END=$(date +%s)
BENCH_DURATION=$((BENCH_END - BENCH_START))
BENCH_END_ISO=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [ "$VERBOSE" = true ]; then
    echo "$DEMO_OUTPUT"
    echo ""
fi

if [ $DEMO_RC -ne 0 ]; then
    echo -e "${RED}ERROR: Benchmark script failed (exit code: $DEMO_RC)${RESET}"
    echo "  Last 20 lines of output:"
    echo "$DEMO_OUTPUT" | tail -20 | sed 's/^/    /'
    
    # Record failure to log
    cat >> "$LOG_FILE" << JSON
{"ts":"$BENCH_END_ISO","type":"benchmark","image":"$IMAGE","python_version":"$PY_VER","build_type":"$PY_BUILD","range":$RANGE,"status":"failed","exit_code":$DEMO_RC,"duration_seconds":$BENCH_DURATION,"cpu_cores":$CPU_COUNT}
JSON
    exit 1
fi

# Parse results from output
echo "─── Results ───"

# Parse speedup values from the result table
# Format: "  <status> <name>                   <elapsed>s   <speedup>x 加速"
# Example: "  ✅ 8 threads                    2.345s    4.29x 加速"
extract_speedup() {
    local pattern="$1"
    echo "$DEMO_OUTPUT" | grep -E "$pattern" | grep -oP '[\d]+\.[\d]+(?=x)' | head -1 || echo ""
}
extract_time() {
    local pattern="$1"
    echo "$DEMO_OUTPUT" | grep -E "$pattern" | grep -oP '[\d]+\.[\d]+(?=s)' | head -1 || echo ""
}

SINGLE_THREAD_TIME=$(extract_time "1 thread[^s]")
THREAD_2_SPEEDUP=$(extract_speedup "2 threads")
THREAD_4_SPEEDUP=$(extract_speedup "4 threads")
THREAD_8_SPEEDUP=$(extract_speedup "8 threads")
THREADPOOL_8_SPEEDUP=$(extract_speedup "ThreadPool.*\(8\)")
PROCPOOL_4_SPEEDUP=$(extract_speedup "ProcessPool.*\(4\)")

# Also check the best speedup line: "最佳多线程加速比: X.XXx"
BEST_LINE_SPEEDUP=$(echo "$DEMO_OUTPUT" | grep -oP '最佳多线程加速比:\s*\K[\d]+\.[\d]+(?=x)' | head -1 || echo "")
if [ -n "$BEST_LINE_SPEEDUP" ]; then
    THREAD_8_SPEEDUP="${THREAD_8_SPEEDUP:-$BEST_LINE_SPEEDUP}"
fi

# Display results
if [ -n "$SINGLE_THREAD_TIME" ]; then
    printf "  Single-thread:  ${CYAN}%ss${RESET}\n" "$SINGLE_THREAD_TIME"
fi
if [ -n "$THREAD_2_SPEEDUP" ]; then
    printf "  2 threads:      ${CYAN}%sx${RESET}\n" "$THREAD_2_SPEEDUP"
fi
if [ -n "$THREAD_4_SPEEDUP" ]; then
    printf "  4 threads:      ${CYAN}%sx${RESET}\n" "$THREAD_4_SPEEDUP"
fi
if [ -n "$THREAD_8_SPEEDUP" ]; then
    BEST_SPEEDUP="$THREAD_8_SPEEDUP"
    printf "  8 threads:      ${GREEN}%sx${RESET} (threading.Thread)\n" "$THREAD_8_SPEEDUP"
fi
if [ -n "$THREADPOOL_8_SPEEDUP" ]; then
    printf "  8 threads:      ${GREEN}%sx${RESET} (ThreadPoolExecutor)\n" "$THREADPOOL_8_SPEEDUP"
    # Use the best of both
    if [ -z "$BEST_SPEEDUP" ] || awk "BEGIN {exit !($THREADPOOL_8_SPEEDUP > $BEST_SPEEDUP)}" 2>/dev/null; then
        BEST_SPEEDUP="$THREADPOOL_8_SPEEDUP"
    fi
fi
echo "  Duration:       ${BENCH_DURATION}s"
echo ""

# Determine pass/fail
if [ -z "$BEST_SPEEDUP" ]; then
    echo -e "${YELLOW}WARNING: Could not parse 8-thread speedup from output${RESET}"
    STATUS="parse_error"
    EXIT_CODE=1
else
    # Compare speedup against threshold using awk for float comparison (bc may not be installed)
    if awk "BEGIN {exit !($BEST_SPEEDUP >= $MIN_SPEEDUP)}" 2>/dev/null; then
        echo -e "${GREEN}✔ PASS${RESET}: 8-thread speedup ${BEST_SPEEDUP}x >= threshold ${MIN_SPEEDUP}x"
        STATUS="pass"
        EXIT_CODE=0
    else
        echo -e "${RED}✘ FAIL${RESET}: 8-thread speedup ${BEST_SPEEDUP}x < threshold ${MIN_SPEEDUP}x"
        echo -e "${YELLOW}  This indicates GIL may be active or free-threading is not working correctly.${RESET}"
        STATUS="fail"
        EXIT_CODE=1
    fi
fi

# Record to JSONL log
cat >> "$LOG_FILE" << JSON
{"ts":"$BENCH_END_ISO","type":"benchmark","image":"$IMAGE","image_id":"$(docker inspect --format='{{.Id}}' "$IMAGE" 2>/dev/null | cut -c1-19)","python_version":"$PY_VER","build_type":"$PY_BUILD","prime_range":$RANGE,"single_thread_s":${SINGLE_THREAD_TIME:-null},"thread_2x":${THREAD_2_SPEEDUP:-null},"thread_4x":${THREAD_4_SPEEDUP:-null},"thread_8x":${THREAD_8_SPEEDUP:-null},"threadpool_8x":${THREADPOOL_8_SPEEDUP:-null},"procpool_4x":${PROCPOOL_4_SPEEDUP:-null},"best_8x":${BEST_SPEEDUP:-null},"threshold":$MIN_SPEEDUP,"duration_seconds":$BENCH_DURATION,"cpu_cores":$CPU_COUNT,"status":"$STATUS"}
JSON

echo ""
echo "  Results recorded to: $LOG_FILE"
echo ""

# JSON output to stdout (for CI/automation)
if [ "$JSON_OUTPUT" = true ]; then
    cat << JSON
{"status":"${STATUS}","image":"${IMAGE}","python_version":"${PY_VER}","build_type":"${PY_BUILD}","prime_range":${RANGE},"best_8x":${BEST_SPEEDUP:-null},"threshold":${MIN_SPEEDUP},"duration_seconds":${BENCH_DURATION},"cpu_cores":${CPU_COUNT},"thread_8x":${THREAD_8_SPEEDUP:-null},"threadpool_8x":${THREADPOOL_8_SPEEDUP:-null}}
JSON
fi

exit $EXIT_CODE
