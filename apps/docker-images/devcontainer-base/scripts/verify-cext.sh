#!/bin/bash
# =============================================================================
# scripts/verify-cext.sh — C Extension ABI 兼容性验证脚本（参数化版 v2.2）
# =============================================================================
set -euo pipefail

# ── 默认值（环境变量覆盖） ──
PYTHON="${PYTHON:-}"
EXPECT_SOABI="${EXPECT_SOABI:-}"
CONDA_ENV="${CONDA_ENV:-main}"
JSON_OUTPUT="${JSON_OUTPUT:-0}"
DEEP_VERIFY="${DEEP_VERIFY:-0}"
VERBOSE="${VERBOSE:-0}"
QUIET="${QUIET:-0}"

# ── 结果收集 ──
FAIL_COUNT=0
PASS_COUNT=0
WARN_COUNT=0
declare -a RESULTS_JSON
SCRIPT_START=$(date +%s)

# ── 颜色（TTY和非JSON模式下） ──
RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; RESET=''
_init_colors() {
    if [ -t 1 ] && [ "$JSON_OUTPUT" != "1" ]; then
        RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
        CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'
    fi
}

# ── 输出辅助函数（必须在主逻辑前定义） ──
log_pass() {
    PASS_COUNT=$((PASS_COUNT+1))
    local name="$1"; local detail="${2:-}"
    if [ "$JSON_OUTPUT" = "1" ]; then
        RESULTS_JSON+=("{\"name\":\"${name}\",\"status\":\"pass\",\"detail\":\"${detail}\"}")
    elif [ "$QUIET" != "1" ]; then
        echo -e "  ${GREEN}✔${RESET} $1"
        [ -n "$detail" ] && [ "$VERBOSE" = "1" ] && echo "      ${detail}"
    fi
    return 0
}

log_fail() {
    FAIL_COUNT=$((FAIL_COUNT+1))
    local name="$1"; local detail="${2:-}"
    if [ "$JSON_OUTPUT" = "1" ]; then
        RESULTS_JSON+=("{\"name\":\"${name}\",\"status\":\"fail\",\"detail\":\"${detail}\"}")
    else
        echo -e "  ${RED}✘${RESET} $1"
        [ -n "$detail" ] && echo "      ${RED}${detail}${RESET}"
    fi
    return 0
}

log_warn() {
    WARN_COUNT=$((WARN_COUNT+1))
    local name="$1"; local detail="${2:-}"
    if [ "$JSON_OUTPUT" = "1" ]; then
        RESULTS_JSON+=("{\"name\":\"${name}\",\"status\":\"warn\",\"detail\":\"${detail}\"}")
    elif [ "$QUIET" != "1" ]; then
        echo -e "  ${YELLOW}⚠${RESET} $1"
        [ -n "$detail" ] && [ "$VERBOSE" = "1" ] && echo "      ${detail}"
    fi
    return 0
}

log_info() {
    if [ "$JSON_OUTPUT" != "1" ] && [ "$QUIET" != "1" ]; then
        echo "  $1"
    fi
}

log_verbose() {
    if [ "$VERBOSE" = "1" ] && [ "$JSON_OUTPUT" != "1" ] && [ "$QUIET" != "1" ]; then
        echo "    $1"
    fi
}

_output_result() {
    local end_time=$(date +%s)
    local duration=$((end_time - SCRIPT_START))
    local result="pass"
    [ "$FAIL_COUNT" -gt 0 ] && result="fail"

    if [ "$JSON_OUTPUT" = "1" ]; then
        local json_results="["
        local first=1
        for r in "${RESULTS_JSON[@]}"; do
            [ $first -eq 0 ] && json_results+=","
            json_results+="$r"
            first=0
        done
        json_results+="]"
        cat << JSON
{"status":"${result}","python_version":"${PY_VER:-unknown}","python_path":"${PY_PATH:-unknown}","soabi":"${SOABI:-unknown}","expect_soabi":"${EXPECT_SOABI:-}","free_threading":$( [ "${FT_BUILD:-no}" = "yes" ] && echo true || echo false ),"deep_verify":${DEEP_VERIFY},"pass_count":${PASS_COUNT},"fail_count":${FAIL_COUNT},"warn_count":${WARN_COUNT},"duration_seconds":${duration},"checks":${json_results}}
JSON
    else
        if [ "$QUIET" != "1" ]; then
            echo ""
            echo "═══════════════════════════════════════════════════"
        fi
        if [ "$FAIL_COUNT" -eq 0 ]; then
            echo -e "  ${GREEN}RESULT: PASS${RESET} ($PASS_COUNT passed, $WARN_COUNT warnings, ${duration}s)"
        else
            echo -e "  ${RED}RESULT: FAIL${RESET} ($FAIL_COUNT failed, $PASS_COUNT passed, $WARN_COUNT warnings, ${duration}s)"
        fi
        if [ "$QUIET" != "1" ]; then
            echo "═══════════════════════════════════════════════════"
        fi
    fi
}

# ── 用法 ──
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Verify C extension ABI compatibility for Python (esp. free-threading builds).

Options:
  -p, --python PATH       Path to Python interpreter (default: auto-detect)
  -s, --expect-soabi STR  Expected SOABI tag (default: auto-detect from Python)
  -e, --conda-env NAME    Conda environment name (default: main)
  -j, --json              Output JSON format (machine-parseable)
  -d, --deep              Deep verification (numpy/pandas if installed)
  -v, --verbose           Verbose output
  -q, --quiet             Quiet mode (only final result)
  -h, --help              Show this help

Examples:
  $0                                    # Auto-detect Python, standard checks
  $0 -p /usr/bin/python3                # Check system Python
  $0 -s cpython-314t                    # Expect free-threading Python 3.14
  $0 -d                                 # Include numpy/pandas deep checks
  $0 -j                                 # JSON output for CI
  docker exec mycontainer verify-cext.sh -d -j
EOF
}

# ── 参数解析 ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--python) PYTHON="$2"; shift 2 ;;
        -s|--expect-soabi) EXPECT_SOABI="$2"; shift 2 ;;
        -e|--conda-env) CONDA_ENV="$2"; shift 2 ;;
        -j|--json) JSON_OUTPUT=1; shift ;;
        -d|--deep) DEEP_VERIFY=1; shift ;;
        -v|--verbose) VERBOSE=1; shift ;;
        -q|--quiet) QUIET=1; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
    esac
done

_init_colors

# ── PATH初始化：确保conda在PATH中 ──
export PATH="/opt/conda/bin:/opt/conda/envs/${CONDA_ENV}/bin:$PATH"

# ── 自动检测Python ──
if [ -z "$PYTHON" ]; then
    if [ -x "/opt/conda/envs/${CONDA_ENV}/bin/python" ]; then
        PYTHON="/opt/conda/envs/${CONDA_ENV}/bin/python"
    elif command -v python &>/dev/null; then
        PYTHON="$(command -v python)"
    elif command -v python3 &>/dev/null; then
        PYTHON="$(command -v python3)"
    fi
fi

# ── 启动信息 ──
if [ "$JSON_OUTPUT" != "1" ] && [ "$QUIET" != "1" ]; then
    echo "═══════════════════════════════════════════════════"
    echo "  C Extension ABI Compatibility Verification v2.2"
    echo "═══════════════════════════════════════════════════"
fi

# ── Check Python exists ──
if [ -z "$PYTHON" ] || [ ! -x "$PYTHON" ]; then
    log_fail "python_not_found" "Python not found. Set --python or ensure python is in PATH."
    _output_result
    exit 1
fi

PY_VER=$("$PYTHON" -c 'import sys; print(sys.version.split()[0])' 2>&1)
PY_PATH="$PYTHON"
log_info "Python: $PY_VER ($PY_PATH)"

# ── 检测free-threading构建类型 ──
FT_BUILD=$("$PYTHON" -c 'import sysconfig; print("yes" if sysconfig.get_config_var("Py_GIL_DISABLED") else "no")' 2>&1)
SOABI=$("$PYTHON" -c 'import sysconfig; print(sysconfig.get_config_var("SOABI") or "unknown")' 2>&1)

if [ "$FT_BUILD" = "yes" ]; then
    log_info "Build type: free-threading (GIL disabled by default)"
else
    log_info "Build type: standard (GIL always enabled)"
fi
log_verbose "SOABI detected: $SOABI"

# ── 自动设置EXPECT_SOABI（如果未指定） ──
if [ -z "$EXPECT_SOABI" ]; then
    if [ "$FT_BUILD" = "yes" ]; then
        EXPECT_SOABI=$(echo "$SOABI" | grep -oE 'cpython-[0-9]+t' || echo "")
    fi
    if [ -z "$EXPECT_SOABI" ] && [ "$FT_BUILD" = "no" ]; then
        EXPECT_SOABI=$(echo "$SOABI" | grep -oE 'cpython-[0-9]+' || echo "")
    fi
fi

if [ "$JSON_OUTPUT" != "1" ] && [ "$QUIET" != "1" ] && [ -n "$EXPECT_SOABI" ]; then
    log_info "Expected SOABI: $EXPECT_SOABI"
fi

# ── 输出header ──
if [ "$JSON_OUTPUT" != "1" ] && [ "$QUIET" != "1" ]; then
    echo ""
    echo "─── C Extension Load Tests ───"
fi

# ── 测试执行函数 ──
run_py_test() {
    local name="$1"; local desc="$2"; shift 2
    local code="$1"
    local output
    if output=$("$PYTHON" -c "$code" 2>&1); then
        log_pass "$name" "$desc"
        return 0
    else
        log_fail "$name" "${desc}: ${output}"
        return 1
    fi
}

# Test 1: brotli
run_py_test "brotli" "compress/decompress roundtrip" "
import brotli
data = b'test' * 100
c = brotli.compress(data)
d = brotli.decompress(c)
assert d == data, 'roundtrip failed'
" || true

# Test 2: cffi
run_py_test "cffi" "C FFI interface" "
import cffi
ffi = cffi.FFI()
ffi.cdef('int printf(const char *format, ...);')
C = ffi.dlopen(None)
" || true

# Test 3: _sqlite3
run_py_test "_sqlite3" "built-in C ext, in-memory DB" "
import sqlite3
conn = sqlite3.connect(':memory:')
conn.execute('CREATE TABLE t (id INTEGER)')
conn.execute('INSERT INTO t VALUES (1)')
r = conn.execute('SELECT * FROM t').fetchone()
assert r == (1,), f'expected (1,), got {r}'
conn.close()
" || true

# Test 4: _ssl
run_py_test "_ssl" "built-in C ext, TLS context" "
import ssl
ctx = ssl.create_default_context()
assert ctx.protocol == ssl.PROTOCOL_TLS_CLIENT, 'SSL context creation failed'
" || true

# Test 5: zlib
run_py_test "zlib" "built-in C ext, compress/decompress" "
import zlib
data = b'hello world' * 50
c = zlib.compress(data)
d = zlib.decompress(c)
assert d == data
" || true

# Test 6: hashlib
run_py_test "hashlib" "built-in C ext, SHA-256" "
import hashlib
h = hashlib.sha256(b'test').hexdigest()
assert len(h) == 64, f'expected 64 hex chars, got {len(h)}'
" || true

# Test 7: json (pure Python baseline)
run_py_test "json" "pure Python baseline" "
import json
d = {'key': 'value', 'num': 42}
s = json.dumps(d)
assert json.loads(s) == d
" || true

# Test 8: ipykernel (optional)
if "$PYTHON" -c "import ipykernel" 2>/dev/null; then
    log_pass "ipykernel" "Jupyter kernel available"
else
    log_warn "ipykernel" "not found (not installed in this env)"
fi

# ── ABI 一致性检查 ──
if [ "$JSON_OUTPUT" != "1" ] && [ "$QUIET" != "1" ]; then
    echo ""
    echo "─── ABI Consistency Checks ───"
fi

log_info "SOABI: $SOABI"
if [ -n "$EXPECT_SOABI" ]; then
    if echo "$SOABI" | grep -q "$EXPECT_SOABI"; then
        log_pass "soabi_match" "SOABI matches expected: $EXPECT_SOABI"
    else
        log_fail "soabi_mismatch" "Expected SOABI containing '$EXPECT_SOABI', got '$SOABI'"
    fi
else
    log_warn "soabi_no_expectation" "No expected SOABI specified; skipping strict match"
fi

if command -v conda &>/dev/null; then
    if conda list -n "$CONDA_ENV" 2>/dev/null | grep -qE "cp[0-9]+-[^t]"; then
        MIXED_PKGS=$(conda list -n "$CONDA_ENV" 2>/dev/null | grep -E "cp3[0-9]+-" | grep -v "cp3[0-9]+t" || true)
        if [ -n "$MIXED_PKGS" ]; then
            log_warn "abi_mixing" "Potential ABI mixing in conda packages"
            log_verbose "$(echo "$MIXED_PKGS" | head -5 | sed 's/^/      /')"
        else
            log_pass "no_abi_mixing" "No ABI mixing detected in conda packages"
        fi
    else
        log_pass "no_abi_mixing" "No ABI mixing detected in conda packages"
    fi
else
    log_warn "conda_not_found" "conda not in PATH; skipping ABI mixing check"
fi

if command -v conda &>/dev/null; then
    if conda config --show channels 2>/dev/null | grep -qE "^\s*-\s+defaults\s*$"; then
        log_warn "defaults_channel" "defaults channel detected! May cause ABI conflicts with free-threading builds."
    else
        log_pass "conda_forge_only" "No defaults channel (conda-forge only - safe for ft builds)"
    fi
fi

# ── 深度验证（--deep） ──
if [ "$DEEP_VERIFY" = "1" ]; then
    if [ "$JSON_OUTPUT" != "1" ] && [ "$QUIET" != "1" ]; then
        echo ""
        echo "─── Deep Verification (numpy/pandas) ───"
    fi

    if "$PYTHON" -c "import numpy" 2>/dev/null; then
        run_py_test "numpy" "matrix multiplication" "
import numpy as np
a = np.random.rand(200, 200)
b = np.random.rand(200, 200)
c = a @ b
assert c.shape == (200, 200)
print(f'numpy {np.__version__} OK')
" || true
    else
        log_warn "numpy" "not installed (skipping deep numpy test)"
    fi

    if "$PYTHON" -c "import pandas" 2>/dev/null; then
        run_py_test "pandas" "DataFrame operations" "
import pandas as pd
import numpy as np
df = pd.DataFrame({'a': np.random.rand(1000), 'b': np.random.rand(1000)})
df['c'] = df['a'] + df['b']
assert len(df) == 1000
print(f'pandas {pd.__version__} OK')
" || true
    else
        log_warn "pandas" "not installed (skipping deep pandas test)"
    fi
fi

_output_result
exit $([ "$FAIL_COUNT" -eq 0 ] && echo 0 || echo 1)
