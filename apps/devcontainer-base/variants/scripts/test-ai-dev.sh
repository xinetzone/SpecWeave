#!/bin/bash
# =============================================================================
# ai-dev Variant Unit Test Script (Enhanced Logging Edition)
#
# Features:
#   - Pre-flight checks (Docker daemon, image existence, image metadata)
#   - Per-test timing with timestamps
#   - Detailed failure diagnostics (full stdout/stderr, command echo, exit codes)
#   - Structured JSONL event logging
#   - Post-failure diagnostic dump (pip list, env vars, kernel config, etc.)
#   - L1-L6 layered test organization
#
# Usage:
#   bash variants/scripts/test-ai-dev.sh [--tag TAG] [--image IMAGE] [-v|--verbose]
# =============================================================================

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"

# shellcheck source=../shared/lib/logging.sh
source "${VARIANTS_DIR}/shared/lib/logging.sh" 2>/dev/null || true
LOG_SERVICE="test-ai-dev"
LOG_JSON_OUTPUT="/tmp/test-ai-dev-events.jsonl"

# ── Configuration ──
TAG="latest"
IMAGE=""
VERBOSE=0
COLLECT_DIAG=1  # Auto-collect diagnostics on first failure

# ── Counters ──
TEST_PASS=0
TEST_FAIL=0
TEST_TOTAL=0
SCRIPT_START=$(date +%s)

# ── Colors ──
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# ── Logging helpers ──

log_json() {
    local event="$1"; shift
    local ts
    ts=$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)
    printf '{"ts":"%s","service":"%s","event":"%s"%s}\n' \
        "$ts" "$LOG_SERVICE" "$event" "$*" >> "$LOG_JSON_OUTPUT" 2>/dev/null || true
}

log_section() {
    local title="$1"
    echo ""
    echo -e "${BLUE}┌──────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${NC}  ${BOLD}${title}${NC}"
    echo -e "${BLUE}└──────────────────────────────────────────────────────────────┘${NC}"
    log_json "SECTION_START" ",\"title\":\"${title}\""
}

log_test_start() {
    local tid="$1" desc="$2"
    local ts
    ts=$(date '+%H:%M:%S')
    echo -e "  ${CYAN}[${ts}]${NC} ${BOLD}${tid}${NC}: ${desc} ..."
    log_json "TEST_START" ",\"id\":\"${tid}\",\"desc\":\"${desc}\""
}

pass() {
    local tid="$1" elapsed="$2"; shift 2
    local msg="$*"
    TEST_PASS=$((TEST_PASS + 1))
    TEST_TOTAL=$((TEST_TOTAL + 1))
    echo -e "  ${GREEN}✓ PASS${NC} ${tid}: ${msg} ${YELLOW}(${elapsed}s)${NC}"
    log_json "TEST_PASS" ",\"id\":\"${tid}\",\"msg\":\"${msg}\",\"elapsed_s\":${elapsed}"
}

fail() {
    local tid="$1"; shift
    local msg="$*"
    TEST_FAIL=$((TEST_FAIL + 1))
    TEST_TOTAL=$((TEST_TOTAL + 1))
    local ts
    ts=$(date '+%H:%M:%S')
    echo -e "  ${RED}✗ FAIL${NC} ${tid}: ${msg}"
    log_json "TEST_FAIL" ",\"id\":\"${tid}\",\"msg\":\"${msg}\""
}

# ── Docker execution wrapper with diagnostics ──

docker_run() {
    docker run --rm "$IMAGE" "$@" 2>&1
}

docker_run_bash() {
    docker run --rm "$IMAGE" bash -c "$1" 2>&1
}

# run_test TEST_ID DESCRIPTION EXPECTED_PATTERN COMMAND...
# Captures stdout+stderr, timing, and provides full output on failure.
run_test() {
    local tid="$1" desc="$2" expected="$3"
    shift 3
    local cmd=("$@")
    local t_start t_end elapsed result rc

    log_test_start "$tid" "$desc"
    t_start=$(date +%s)

    # Execute and capture output + exit code
    set +e
    result=$("${cmd[@]}" 2>&1)
    rc=$?
    set -e
    t_end=$(date +%s)
    elapsed=$((t_end - t_start))

    if [ $rc -eq 0 ] && echo "$result" | grep -qE "$expected"; then
        pass "$tid" "$elapsed" "$desc"
        [ "$VERBOSE" -eq 1 ] && echo "$result" | sed 's/^/      /'
        return 0
    else
        fail "$tid" "$desc"
        echo -e "    ${RED}── Diagnostic ──${NC}"
        echo -e "    ${BOLD}Command:${NC} ${cmd[*]}"
        echo -e "    ${BOLD}Exit code:${NC} $rc"
        echo -e "    ${BOLD}Expected pattern:${NC} $expected"
        echo -e "    ${BOLD}Full output:${NC}"
        echo "$result" | head -30 | sed 's/^/      /'
        local line_count
        line_count=$(echo "$result" | wc -l)
        if [ "$line_count" -gt 30 ]; then
            echo -e "    ${YELLOW}... (${line_count} lines total, showing first 30)${NC}"
        fi
        log_json "TEST_DIAG" ",\"id\":\"${tid}\",\"exit_code\":${rc},\"output_lines\":${line_count}"

        # Auto-collect diagnostics on first failure
        if [ "$COLLECT_DIAG" -eq 1 ] && [ "$TEST_FAIL" -eq 1 ]; then
            collect_diagnostics
            COLLECT_DIAG=0
        fi
        return 1
    fi
}

# ── Pre-flight checks ──

preflight_checks() {
    log_section "Pre-flight Checks"
    local all_ok=1

    # Check Docker daemon
    echo -ne "  ${CYAN}[$(date '+%H:%M:%S')]${NC} Checking Docker daemon ... "
    if docker info &>/dev/null; then
        local dv
        dv=$(docker version --format '{{.Server.Version}}' 2>/dev/null)
        echo -e "${GREEN}OK${NC} (Docker $dv)"
        log_json "PREFLIGHT" ",\"check\":\"docker_daemon\",\"status\":\"ok\",\"version\":\"${dv}\""
    else
        echo -e "${RED}FAILED${NC} - Docker daemon not reachable"
        log_json "PREFLIGHT" ",\"check\":\"docker_daemon\",\"status\":\"fail\""
        all_ok=0
    fi

    # Check image exists
    echo -ne "  ${CYAN}[$(date '+%H:%M:%S')]${NC} Checking image ${IMAGE} ... "
    if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${IMAGE}$"; then
        local size created
        size=$(docker images "$IMAGE" --format '{{.Size}}')
        created=$(docker images "$IMAGE" --format '{{.CreatedAt}}' | cut -d' ' -f1-2)
        echo -e "${GREEN}OK${NC} (size=$size, created=$created)"
        log_json "PREFLIGHT" ",\"check\":\"image_exists\",\"status\":\"ok\",\"size\":\"${size}\""
    else
        echo -e "${RED}FAILED${NC} - Image not found"
        echo -e "  ${YELLOW}Hint:${NC} Build first with: bash variants/build.sh --variant ai-dev --cn"
        log_json "PREFLIGHT" ",\"check\":\"image_exists\",\"status\":\"fail\""
        all_ok=0
    fi

    # Show image labels/metadata
    if [ "$all_ok" -eq 1 ]; then
        echo ""
        echo -e "  ${BOLD}Image metadata:${NC}"
        docker inspect "$IMAGE" --format '    - Created: {{.Created}}' 2>/dev/null
        docker inspect "$IMAGE" --format '    - OS/Arch: {{.Os}}/{{.Architecture}}' 2>/dev/null
        docker inspect "$IMAGE" --format '    - Entrypoint: {{json .Config.Entrypoint}}' 2>/dev/null
        docker inspect "$IMAGE" --format '    - Cmd: {{json .Config.Cmd}}' 2>/dev/null
        docker inspect "$IMAGE" --format '    - WorkingDir: {{.Config.WorkingDir}}' 2>/dev/null
        docker inspect "$IMAGE" --format '    - User: {{.Config.User}}' 2>/dev/null
    fi

    echo ""
    if [ "$all_ok" -eq 0 ]; then
        echo -e "${RED}${BOLD}Pre-flight checks failed. Aborting.${NC}"
        log_json "PREFLIGHT_ABORT" ""
        exit 1
    fi
    echo -e "${GREEN}${BOLD}All pre-flight checks passed.${NC}"
    log_json "PREFLIGHT_DONE" ",\"status\":\"ok\""
}

# ── Diagnostic collection (runs once on first failure) ──

collect_diagnostics() {
    echo ""
    echo -e "${YELLOW}${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}${BOLD}║  DIAGNOSTIC DUMP (collected on first test failure)          ║${NC}"
    echo -e "${YELLOW}${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
    log_json "DIAG_START" ""

    echo -e "\n  ${BOLD}[1] Container environment:${NC}"
    docker_run_bash "echo 'HOSTNAME='\$(hostname); echo 'USER='\$(whoami); echo 'PWD='\$(pwd); echo 'PATH='\$PATH; echo 'OMP_NUM_THREADS='\$OMP_NUM_THREADS; echo 'PIP_USER='\$PIP_USER" 2>&1 | sed 's/^/    /'

    echo -e "\n  ${BOLD}[2] Python paths:${NC}"
    docker_run_bash "which python; which python3; which pip; /opt/conda/bin/python --version; /opt/venv/bin/python --version 2>&1" 2>&1 | sed 's/^/    /'

    echo -e "\n  ${BOLD}[3] Key package versions (pip list filtered):${NC}"
    docker_run_bash "/opt/conda/bin/pip list 2>/dev/null | grep -iE 'torch|onnx|transformers|datasets|fastapi|pandas|numpy|scikit|jupyter|matplotlib|jieba|nltk|httpx|pydantic|uvicorn|numba|librosa|pymupdf|elasticsearch|psycopg|pymongo|minio|nuitka|rich|typer' || echo '(pip list failed)'" 2>&1 | sed 's/^/    /'

    echo -e "\n  ${BOLD}[4] Jupyter kernels:${NC}"
    docker_run_bash "/opt/venv/bin/jupyter kernelspec list 2>&1; echo '---'; ls -la /opt/venv/share/jupyter/kernels/ 2>&1; echo '---'; ls -la /opt/conda/share/jupyter/kernels/ 2>&1; echo '---'; cat /opt/venv/share/jupyter/kernels/ai-dev/kernel.json 2>&1" 2>&1 | sed 's/^/    /'

    echo -e "\n  ${BOLD}[5] Build info:${NC}"
    docker_run_bash "cat /etc/devcontainer-variant-ai-dev-build-info 2>&1 || echo '(build-info not found)'" 2>&1 | sed 's/^/    /'

    echo -e "\n  ${BOLD}[6] Services:${NC}"
    docker_run_bash "which sshd; which supervisord; which docker; which podman; id devuser 2>&1; test -d /opt/venv && echo '/opt/venv exists' || echo '/opt/venv MISSING'" 2>&1 | sed 's/^/    /'

    echo -e "\n  ${BOLD}[7] Disk usage:${NC}"
    docker_run_bash "df -h / /opt/conda /opt/venv 2>/dev/null; echo '---'; du -sh /opt/conda 2>/dev/null; du -sh /opt/venv 2>/dev/null" 2>&1 | sed 's/^/    /'

    echo -e "\n  ${BOLD}[8] pip check (dependency conflicts):${NC}"
    docker_run_bash "/opt/conda/bin/pip check 2>&1 || echo '(pip check found issues)'" 2>&1 | sed 's/^/    /'

    echo ""
    log_json "DIAG_END" ""
}

# ═══════════════════════════════════════════════════════════════════
# L1: Toolchain Availability
# ═══════════════════════════════════════════════════════════════════

test_python_version() {
    run_test "T1" "Python version (>=3.14)" \
        "Python 3\.(1[4-9]|[2-9][0-9])" \
        docker_run /opt/conda/bin/python --version
}

test_conda_available() {
    run_test "T2" "conda available" \
        "conda [0-9]" \
        docker_run /opt/conda/bin/conda --version
}

test_pip_version() {
    run_test "T3" "pip available" \
        "pip [0-9]" \
        docker_run /opt/conda/bin/pip --version
}

test_jupyterlab_version() {
    local t_start elapsed result rc major minor ver
    log_test_start "T4" "JupyterLab >=4.4"
    t_start=$(date +%s)
    set +e
    result=$(docker_run /opt/venv/bin/jupyter lab --version 2>&1)
    rc=$?
    set -e
    elapsed=$(($(date +%s) - t_start))
    ver=$(echo "$result" | tail -1 | tr -d '[:space:]')
    major=$(echo "$ver" | cut -d. -f1)
    minor=$(echo "$ver" | cut -d. -f2)
    if [ "$rc" -eq 0 ] && { [ "$major" -gt 4 ] || { [ "$major" -eq 4 ] && [ "$minor" -ge 4 ]; }; }; then
        pass "T4" "$elapsed" "JupyterLab = $ver (>=4.4)"
    else
        fail "T4" "JupyterLab version check failed (got: $ver)"
        echo "    Full output: $result"
    fi
}

test_transformers_version() {
    run_test "T5" "transformers importable" \
        "VER=[0-9]" \
        docker_run /opt/conda/bin/python -c "import transformers;print('VER='+transformers.__version__)"
}

# ═══════════════════════════════════════════════════════════════════
# L2: Functional Tests
# ═══════════════════════════════════════════════════════════════════

test_core_imports() {
    run_test "T6" "All core package imports (25+ packages)" \
        "ALL_IMPORTS_OK" \
        docker_run_bash "/opt/conda/bin/python -c \"
import transformers, datasets, sentence_transformers, evaluate
import fastapi, uvicorn, pydantic, httpx
import pandas, pyarrow, sklearn
import matplotlib, seaborn, rich, typer
import jieba, nltk, pypinyin
import fitz, bs4, openpyxl
import psycopg2, pymongo, elasticsearch, minio
import nuitka, pytest, psutil, icecream
import einops, numba, librosa
print('ALL_IMPORTS_OK')
\""
}

test_pandas_basic() {
    run_test "T7" "Pandas basic operations" \
        "PANDAS_OK" \
        docker_run /opt/conda/bin/python -c "
import pandas as pd
df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
assert len(df) == 3
assert df['a'].sum() == 6
print('PANDAS_OK')
"
}

test_fastapi_app() {
    run_test "T8" "FastAPI app creation" \
        "FASTAPI_OK" \
        docker_run /opt/conda/bin/python -c "
from fastapi import FastAPI
app = FastAPI()
@app.get('/')
def read_root():
    return {'hello': 'world'}
print('FASTAPI_OK')
"
}

test_jieba_segment() {
    run_test "T9" "jieba Chinese segmentation" \
        "JIEBA_OK" \
        docker_run /opt/conda/bin/python -c "
import jieba
words = list(jieba.cut('我爱自然语言处理'))
assert len(words) > 0
print('JIEBA_OK')
"
}

# ═══════════════════════════════════════════════════════════════════
# L3: Deep Component Validation
# ═══════════════════════════════════════════════════════════════════

test_jupyter_kernel_registered() {
    run_test "T10" "Jupyter ai-dev kernel registered (dual-path)" \
        "KERNEL_OK" \
        docker_run_bash "
test -f /opt/venv/share/jupyter/kernels/ai-dev/kernel.json && \
test -f /opt/conda/share/jupyter/kernels/ai-dev/kernel.json && \
/opt/venv/bin/jupyter kernelspec list 2>/dev/null | grep -q ai-dev && \
echo 'KERNEL_OK'
"
}

test_kernel_config() {
    run_test "T11" "Kernel config (display_name, python path, language)" \
        "KERNEL_CONFIG_OK" \
        docker_run /opt/conda/bin/python -c "
import json
with open('/opt/venv/share/jupyter/kernels/ai-dev/kernel.json') as f:
    k = json.load(f)
assert k['display_name'] == 'Python 3 (AI Dev)', f'Bad display_name: {k[\"display_name\"]}'
assert '/opt/conda/bin/python' in k['argv'][0], f'Bad python path: {k[\"argv\"][0]}'
assert k['language'] == 'python'
assert 'env' in k and 'PATH' in k['env']
print('KERNEL_CONFIG_OK')
"
}

test_quantization_inherited() {
    run_test "T12" "onnx-quantized inheritance (quantization API)" \
        "QUANT_INHERIT_OK" \
        docker_run /opt/conda/bin/python -c "
from onnxruntime.quantization import quantize_dynamic, QuantType, quantize_static, CalibrationDataReader
print('QUANT_INHERIT_OK')
"
}

test_build_info() {
    run_test "T13" "Build-info file with correct fields" \
        "BUILD_INFO_OK" \
        docker_run_bash "
test -f /etc/devcontainer-variant-ai-dev-build-info && \
grep -q 'VARIANT=ai-dev' /etc/devcontainer-variant-ai-dev-build-info && \
grep -q 'BASE_IMAGE=devcontainer-base:onnx-quantized' /etc/devcontainer-variant-ai-dev-build-info && \
grep -q 'PACKAGES_COUNT' /etc/devcontainer-variant-ai-dev-build-info && \
grep -q 'TRANSFORMERS_VERSION' /etc/devcontainer-variant-ai-dev-build-info && \
echo 'BUILD_INFO_OK'
"
}

# ═══════════════════════════════════════════════════════════════════
# L4: Base Service Inheritance
# ═══════════════════════════════════════════════════════════════════

test_ssh_exists() {
    run_test "T14" "sshd available" \
        "^/" \
        docker_run_bash "which sshd"
}

test_supervisord_exists() {
    run_test "T15" "supervisord available" \
        "^/" \
        docker_run_bash "which supervisord"
}

test_docker_exists() {
    run_test "T16" "docker CLI available" \
        "^/" \
        docker_run_bash "which docker"
}

test_jupyter_exists() {
    run_test "T17" "Jupyter available in /opt/venv" \
        "JUPYTER_OK" \
        docker_run_bash "test -x /opt/venv/bin/jupyter && echo 'JUPYTER_OK'"
}

test_devuser_exists() {
    run_test "T18" "devuser exists" \
        "uid=" \
        docker_run_bash "id devuser"
}

# ═══════════════════════════════════════════════════════════════════
# L5: PATH Priority & Environment Isolation
# ═══════════════════════════════════════════════════════════════════

test_path_priority() {
    run_test "T19" "conda python is default in PATH" \
        "/opt/conda/bin/python" \
        docker_run_bash "which python"
}

test_venv_preserved() {
    run_test "T20" "/opt/venv preserved and executable" \
        "VENV_OK" \
        docker_run_bash "test -x /opt/venv/bin/python && echo 'VENV_OK'"
}

test_env_variables() {
    local t_start elapsed result omp kmp pip_user
    log_test_start "T21" "Environment variables (OMP, KMP, PIP_USER)"
    t_start=$(date +%s)
    result=$(docker_run_bash "
echo \"OMP=\${OMP_NUM_THREADS}\"
echo \"KMP=\${KMP_DUPLICATE_LIB_OK}\"
echo \"PIP_USER=\${PIP_USER}\"
" 2>&1)
    elapsed=$(($(date +%s) - t_start))
    omp=$(echo "$result" | grep '^OMP=' | cut -d= -f2)
    kmp=$(echo "$result" | grep '^KMP=' | cut -d= -f2)
    pip_user=$(echo "$result" | grep '^PIP_USER=' | cut -d= -f2)
    if [ "$omp" = "4" ] && [ "$kmp" = "TRUE" ] && [ "$pip_user" = "1" ]; then
        pass "T21" "$elapsed" "Env vars correct (OMP=$omp, KMP=$kmp, PIP_USER=$pip_user)"
    else
        fail "T21" "Env vars incorrect (OMP=$omp, KMP=$kmp, PIP_USER=$pip_user)"
        echo "    Full output: $result"
    fi
}

test_devuser_access() {
    run_test "T22" "devuser can access conda packages" \
        "devuser access OK" \
        docker_run_bash "su - devuser -c \"/opt/conda/bin/python -c 'import transformers,pandas;print(\\\"devuser access OK\\\")'\""
}

# ═══════════════════════════════════════════════════════════════════
# L6: Configuration Validation
# ═══════════════════════════════════════════════════════════════════

test_kernel_json_valid() {
    run_test "T23" "kernel.json is valid JSON with required fields" \
        "JSON_VALID" \
        docker_run /opt/conda/bin/python -c "
import json
with open('/opt/venv/share/jupyter/kernels/ai-dev/kernel.json') as f:
    k = json.load(f)
assert 'argv' in k and 'display_name' in k and 'language' in k
assert 'env' in k and 'PATH' in k['env']
assert len(k['argv']) >= 3
print('JSON_VALID')
"
}

test_pip_user_runtime() {
    run_test "T24" "Runtime PIP_USER=1 (user-level pip enabled)" \
        "PIP_USER=1" \
        docker_run_bash "echo \"PIP_USER=\${PIP_USER}\""
}

test_no_entrypoint_override() {
    local t_start elapsed result
    log_test_start "T25" "Entrypoint inherited from base (not overridden)"
    t_start=$(date +%s)
    set +e
    result=$(docker inspect "$IMAGE" --format '{{json .Config.Entrypoint}}' 2>&1)
    set -e
    elapsed=$(($(date +%s) - t_start))
    # Base image uses tini as entrypoint; variant should not override it
    if echo "$result" | grep -qE "tini|entrypoint"; then
        pass "T25" "$elapsed" "Entrypoint inherited (contains tini/entrypoint)"
    elif echo "$result" | grep -q "null"; then
        pass "T25" "$elapsed" "Entrypoint is null (inherits from base at runtime)"
    else
        fail "T25" "Entrypoint may have been overridden: $result"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Unit test script for ai-dev variant (enhanced logging edition).

Options:
  --tag TAG        Image tag suffix (default: latest)
  --image IMAGE    Full image name (overrides --tag)
  -v, --verbose    Show full output even for passing tests
  -h, --help       Show this help message

Default image: devcontainer-base:ai-dev-latest
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --tag) TAG="$2"; shift 2;;
        --image) IMAGE="$2"; shift 2;;
        -v|--verbose) VERBOSE=1; shift;;
        -h|--help) usage; exit 0;;
        *) echo "Unknown option: $1"; usage; exit 1;;
    esac
done

if [ -z "$IMAGE" ]; then
    IMAGE="devcontainer-base:ai-dev-${TAG}"
fi

# ── Header ──
echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║       Unit Tests: ai-dev variant (Enhanced Logging)        ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Image:${NC}  $IMAGE"
echo -e "  ${BOLD}Time:${NC}   $(date '+%Y-%m-%d %H:%M:%S')"
echo -e "  ${BOLD}Log:${NC}    $LOG_JSON_OUTPUT"
echo ""
log_json "TEST_RUN_START" ",\"image\":\"${IMAGE}\",\"verbose\":${VERBOSE}"

# ── Pre-flight ──
preflight_checks

# ── L1 ──
log_section "L1: Toolchain Availability"
test_python_version
test_conda_available
test_pip_version
test_jupyterlab_version
test_transformers_version

# ── L2 ──
log_section "L2: Functional Tests (Package Imports + Basic Ops)"
test_core_imports
test_pandas_basic
test_fastapi_app
test_jieba_segment

# ── L3 ──
log_section "L3: Deep Component Validation"
test_jupyter_kernel_registered
test_kernel_config
test_quantization_inherited
test_build_info

# ── L4 ──
log_section "L4: Base Service Inheritance"
test_ssh_exists
test_supervisord_exists
test_docker_exists
test_jupyter_exists
test_devuser_exists

# ── L5 ──
log_section "L5: PATH Priority & Environment Isolation"
test_path_priority
test_venv_preserved
test_env_variables
test_devuser_access

# ── L6 ──
log_section "L6: Configuration Validation"
test_kernel_json_valid
test_pip_user_runtime
test_no_entrypoint_override

# ── Summary ──
SCRIPT_END=$(date +%s)
TOTAL_ELAPSED=$((SCRIPT_END - SCRIPT_START))

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}║  Test Summary                                                ║${NC}"
echo -e "${BOLD}╠══════════════════════════════════════════════════════════════╣${NC}"
printf "${BOLD}║${NC}  Image:    %-49s ${BOLD}║${NC}\n" "$IMAGE"
printf "${BOLD}║${NC}  Total:    %-49s ${BOLD}║${NC}\n" "$TEST_TOTAL"
printf "${BOLD}║${NC}  ${GREEN}Passed:${NC}   %-49s ${BOLD}║${NC}\n" "$TEST_PASS"
printf "${BOLD}║${NC}  ${RED}Failed:${NC}   %-49s ${BOLD}║${NC}\n" "$TEST_FAIL"
printf "${BOLD}║${NC}  Duration: %-49s ${BOLD}║${NC}\n" "${TOTAL_ELAPSED}s"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_json "TEST_RUN_END" ",\"total\":${TEST_TOTAL},\"passed\":${TEST_PASS},\"failed\":${TEST_FAIL},\"duration_s\":${TOTAL_ELAPSED}"

if [ "$TEST_FAIL" -gt 0 ]; then
    echo -e "${RED}${BOLD}*** TESTS FAILED ***${NC}"
    echo -e "  Diagnostic log: ${LOG_JSON_OUTPUT}"
    echo -e "  Re-run with -v for full output on passing tests"
    exit 1
else
    echo -e "${GREEN}${BOLD}*** ALL TESTS PASSED ***${NC}"
fi
