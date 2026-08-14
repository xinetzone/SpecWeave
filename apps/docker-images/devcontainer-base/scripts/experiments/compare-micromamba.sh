#!/usr/bin/env bash
# =============================================================================
# compare-micromamba.sh — micromamba vs Miniforge3 对比实验脚本 (B1)
# =============================================================================
# 基于公理A1（构建时间=生产力）和A3（镜像体积∝拉取成本），评估micromamba替代
# Miniforge3的可行性。通过构建两个功能等价的镜像进行三维对比：
#   1. 构建速度（冷构建时间）
#   2. 镜像体积（磁盘占用、层数、base Python冗余）
#   3. 功能完整性（Python/Jupyter/Docker/C扩展/free-threading）
#
# 输出：
#   - JSON报告：scripts/experiments/results/micromamba-compare-<timestamp>.json
#   - Markdown报告：scripts/experiments/results/micromamba-compare-<timestamp>.md
#
# 用法：
#   bash scripts/experiments/compare-micromamba.sh            # 完整冷构建对比
#   bash scripts/experiments/compare-micromamba.sh --quick     # 仅体积+快速功能测试
#   bash scripts/experiments/compare-micromamba.sh --keep      # 保留构建镜像（不自动清理）
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
MICRO_DOCKERFILE="${SCRIPT_DIR}/micromamba/Dockerfile.micromamba"
RESULTS_DIR="${PROJECT_DIR}/scripts/experiments/results"
mkdir -p "$RESULTS_DIR"

# ── 参数解析 ──
QUICK_MODE=false
KEEP_IMAGES=false
BUILD_VERIFY_MODE="${BUILD_VERIFY_MODE:-fast}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --quick) QUICK_MODE=true; shift ;;
        --keep) KEEP_IMAGES=true; shift ;;
        --verify) BUILD_VERIFY_MODE="$2"; shift 2 ;;
        -h|--help)
            grep '^#' "$0" | grep -v '#!/' | sed 's/^# \?//'
            exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BASE_IMAGE="devcontainer-base:miniforge3-baseline"
MICRO_IMAGE="devcontainer-base:micromamba-experiment"
JSON_REPORT="${RESULTS_DIR}/micromamba-compare-${TIMESTAMP}.json"
MD_REPORT="${RESULTS_DIR}/micromamba-compare-${TIMESTAMP}.md"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     micromamba vs Miniforge3 Comparison Experiment          ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Mode:        %-46s║\n" "$([ "$QUICK_MODE" = true ] && echo 'quick' || echo 'full cold build')"
printf "║  Verify:      %-46s║\n" "$BUILD_VERIFY_MODE"
printf "║  Keep images: %-46s║\n" "$([ "$KEEP_IMAGES" = true ] && echo 'yes' || echo 'no (cleanup after)')"
printf "║  Results:     %-46s║\n" "$RESULTS_DIR"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# ── 预检查 ──
echo "[PRECHECK] Verifying experiment files..."
if [ ! -f "$MICRO_DOCKERFILE" ]; then
    echo "[ERROR] Micromamba Dockerfile not found: $MICRO_DOCKERFILE"
    exit 1
fi
echo "  - Baseline Dockerfile: ${PROJECT_DIR}/Dockerfile"
echo "  - Micromamba Dockerfile: ${MICRO_DOCKERFILE}"

# ── 构建镜像 ──
build_image() {
    local name="$1" dockerfile="$2" tag="$3"
    local log_file="${RESULTS_DIR}/build-${name}-${TIMESTAMP}.log"

    echo ""
    echo ">>> Building ${name} image..."
    local start_time=$(date +%s)
    local rc=0

    DOCKER_BUILDKIT=1 docker build \
        --no-cache \
        --progress=plain \
        --build-arg BUILD_VERIFY_MODE="${BUILD_VERIFY_MODE}" \
        -f "$dockerfile" \
        -t "$tag" \
        "${PROJECT_DIR}" 2>&1 | tee "$log_file" || rc=$?

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    if [ $rc -ne 0 ]; then
        echo "[FAIL] ${name} build failed (exit code: $rc, log: ${log_file})"
        echo "0"
        return 1
    fi
    echo "[OK] ${name} build completed in ${duration}s"
    echo "$duration"
}

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 1: Building baseline (Miniforge3)..."
echo "═══════════════════════════════════════════════════════════════"
MINI_BUILD_TIME=$(build_image "miniforge3" "${PROJECT_DIR}/Dockerfile" "$BASE_IMAGE" || echo "FAILED")

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 2: Building experiment (micromamba)..."
echo "═══════════════════════════════════════════════════════════════"
MICRO_BUILD_TIME=$(build_image "micromamba" "$MICRO_DOCKERFILE" "$MICRO_IMAGE" || echo "FAILED")

# ── 收集镜像指标 ──
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 3: Collecting image metrics..."
echo "═══════════════════════════════════════════════════════════════"

collect_metrics() {
    local tag="$1"
    local size_bytes layers
    size_bytes=$(docker inspect "$tag" --format='{{.Size}}' 2>/dev/null || echo "0")
    layers=$(docker history "$tag" --format='{{.ID}}' 2>/dev/null | wc -l)
    echo "${size_bytes}|${layers}"
}

IFS='|' read -r MINI_SIZE_BYTES MINI_LAYERS <<< "$(collect_metrics "$BASE_IMAGE")"
IFS='|' read -r MICRO_SIZE_BYTES MICRO_LAYERS <<< "$(collect_metrics "$MICRO_IMAGE")"

MINI_SIZE_MB=$((MINI_SIZE_BYTES / 1024 / 1024))
MICRO_SIZE_MB=$((MICRO_SIZE_BYTES / 1024 / 1024))
SIZE_DIFF_MB=$((MINI_SIZE_MB - MICRO_SIZE_MB))
SIZE_DIFF_PCT=$(python3 -c "print(round(($MINI_SIZE_MB - $MICRO_SIZE_MB) / max($MINI_SIZE_MB, 1) * 100, 1))" 2>/dev/null || echo "0")

echo "  Miniforge3: ${MINI_SIZE_MB}MB, ${MINI_LAYERS} layers, build=${MINI_BUILD_TIME}s"
echo "  micromamba: ${MICRO_SIZE_MB}MB, ${MICRO_LAYERS} layers, build=${MICRO_BUILD_TIME}s"
echo "  Size difference: ${SIZE_DIFF_MB}MB (${SIZE_DIFF_PCT}%)"

# ── 功能完整性测试 ──
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 4: Functional completeness tests..."
echo "═══════════════════════════════════════════════════════════════"

run_func_tests() {
    local tag="$1" prefix="$2"
    local cname="func-test-${prefix}-$(date +%s)"
    local tests="{}"

    # Start container
    docker run -d --name "$cname" --privileged "$tag" tail -f /dev/null >/dev/null 2>&1 || \
    docker run -d --name "$cname" "$tag" tail -f /dev/null >/dev/null 2>&1 || {
        echo '{"error":"cannot_start_container"}'
        return 1
    }
    sleep 3

    _test() {
        local key="$1" cmd="$2"
        if docker exec "$cname" bash -c "$cmd" >/dev/null 2>&1; then
            tests=$(echo "$tests" | python3 -c "import sys,json; d=json.load(sys.stdin); d['$key']=True; json.dump(d,sys.stdout)")
        else
            tests=$(echo "$tests" | python3 -c "import sys,json; d=json.load(sys.stdin); d['$key']=False; json.dump(d,sys.stdout)")
        fi
    }

    _get() {
        local key="$1" cmd="$2"
        local val
        val=$(docker exec "$cname" bash -c "$cmd" 2>/dev/null || echo "unknown")
        tests=$(echo "$tests" | python3 -c "import sys,json; d=json.load(sys.stdin); val=open('/dev/stdin').read().strip(); d['$key']=val; json.dump(d,sys.stdout)" <<< "$val")
    }

    _test "python" "python --version"
    _test "pip" "pip --version"
    _test "conda_cmd" "conda --version"
    _test "jupyter" "jupyter --version"
    _test "docker" "docker --version"
    _test "c_extensions" "python -c 'import brotli,cffi,sqlite3,ssl,zlib,hashlib'"

    # Free-threading verification
    ft_val=$(docker exec "$cname" python -c "import sysconfig; print(sysconfig.get_config_var('Py_GIL_DISABLED'))" 2>/dev/null || echo "0")
    soabi_val=$(docker exec "$cname" python -c "import sysconfig; print(sysconfig.get_config_var('SOABI'))" 2>/dev/null || echo "unknown")
    tests=$(echo "$tests" | python3 -c "import sys,json; d=json.load(sys.stdin); d['ft_verified']=(${ft_val}==1); d['soabi']='${soabi_val}'; json.dump(d,sys.stdout)")

    # Base Python detection (Miniforge3 has py313 in base, micromamba has none)
    base_py_count=$(docker exec "$cname" bash -c 'find /opt/conda -maxdepth 2 -name "python*" -type f ! -path "*/envs/*" 2>/dev/null | wc -l' 2>/dev/null || echo "0")
    tests=$(echo "$tests" | python3 -c "import sys,json; d=json.load(sys.stdin); d['has_base_python']=(${base_py_count}>0); d['base_python_binaries']=${base_py_count}; json.dump(d,sys.stdout)")

    # Package count in main env
    pkg_count=$(docker exec "$cname" bash -c 'conda list -n main 2>/dev/null | tail -n +4 | wc -l' 2>/dev/null || echo "0")
    tests=$(echo "$tests" | python3 -c "import sys,json; d=json.load(sys.stdin); d['main_env_packages']=${pkg_count}; json.dump(d,sys.stdout)")

    # Python version
    py_ver=$(docker exec "$cname" python --version 2>&1 | awk '{print $2}')
    tests=$(echo "$tests" | python3 -c "import sys,json; d=json.load(sys.stdin); d['python_version']='${py_ver}'; json.dump(d,sys.stdout)")

    # /opt/conda size
    conda_size=$(docker exec "$cname" du -sm /opt/conda 2>/dev/null | awk '{print $1}' || echo "0")
    tests=$(echo "$tests" | python3 -c "import sys,json; d=json.load(sys.stdin); d['conda_dir_mb']=${conda_size}; json.dump(d,sys.stdout)")

    docker rm -f "$cname" >/dev/null 2>&1
    echo "$tests"
}

MINI_FUNC=$(run_func_tests "$BASE_IMAGE" "mini")
MICRO_FUNC=$(run_func_tests "$MICRO_IMAGE" "micro")

echo "  Miniforge3 functional tests:"
echo "$MINI_FUNC" | python3 -m json.tool 2>/dev/null || echo "$MINI_FUNC"
echo ""
echo "  micromamba functional tests:"
echo "$MICRO_FUNC" | python3 -m json.tool 2>/dev/null || echo "$MICRO_FUNC"

# ── 生成报告 ──
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Phase 5: Generating reports..."
echo "═══════════════════════════════════════════════════════════════"

python3 - "$JSON_REPORT" "$MD_REPORT" <<PYEOF
import json, sys, datetime

mini_func = json.loads('''$MINI_FUNC''')
micro_func = json.loads('''$MICRO_FUNC''')

mini_build = ${MINI_BUILD_TIME} if "${MINI_BUILD_TIME}" != "FAILED" else None
micro_build = ${MICRO_BUILD_TIME} if "${MICRO_BUILD_TIME}" != "FAILED" else None

speedup = None
if mini_build and micro_build and micro_build > 0:
    speedup = round(mini_build / micro_build, 2)

# Functional parity check
parity_checks = ["python", "pip", "conda_cmd", "jupyter", "c_extensions", "ft_verified"]
functional_parity = all(
    mini_func.get(k) == micro_func.get(k) for k in parity_checks
)

report = {
    "experiment": "micromamba-vs-miniforge3",
    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    "verify_mode": "${BUILD_VERIFY_MODE}",
    "build_time_seconds": {
        "miniforge3": mini_build,
        "micromamba": micro_build,
        "speedup": speedup,
        "faster": "micromamba" if micro_build and mini_build and micro_build < mini_build else ("miniforge3" if mini_build else "unknown")
    },
    "image_size": {
        "miniforge3_mb": ${MINI_SIZE_MB},
        "micromamba_mb": ${MICRO_SIZE_MB},
        "difference_mb": ${SIZE_DIFF_MB},
        "difference_pct": ${SIZE_DIFF_PCT},
        "smaller": "micromamba" if ${MICRO_SIZE_MB} < ${MINI_SIZE_MB} else "miniforge3"
    },
    "layers": {
        "miniforge3": ${MINI_LAYERS},
        "micromamba": ${MICRO_LAYERS}
    },
    "functional_tests": {
        "miniforge3": mini_func,
        "micromamba": micro_func,
        "parity": functional_parity,
        "key_differences": [
            k for k in ["has_base_python", "base_python_binaries", "conda_dir_mb"]
            if mini_func.get(k) != micro_func.get(k)
        ]
    },
    "verdict": {
        "functional_parity": functional_parity,
        "build_speed_winner": "micromamba" if micro_build and mini_build and micro_build < mini_build else "miniforge3",
        "size_winner": "micromamba" if ${MICRO_SIZE_MB} < ${MINI_SIZE_MB} else "miniforge3",
        "recommendation": ""
    }
}

# Generate recommendation
if functional_parity and ${SIZE_DIFF_PCT} > 5 and (speedup or 0) > 1.0:
    report["verdict"]["recommendation"] = "✅ Recommend switching to micromamba: functional parity confirmed, smaller image, faster build"
elif functional_parity and ${SIZE_DIFF_PCT} > 0:
    report["verdict"]["recommendation"] = "⚠️ Consider micromamba: functional parity confirmed but benefit is marginal (size reduction only)"
elif not functional_parity:
    report["verdict"]["recommendation"] = "❌ Do NOT switch: functional parity not confirmed, missing features detected"
else:
    report["verdict"]["recommendation"] = "⚠️ Inconclusive: build failed or insufficient data"

with open(sys.argv[1], 'w') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

# Markdown report
md = f"""# micromamba vs Miniforge3 对比实验报告

> 实验时间：{report['timestamp']}
> 验证模式：{report['verify_mode']}

## 一、构建速度对比（冷构建，--no-cache）

| 指标 | Miniforge3 | micromamba | 差异 |
|------|-----------|-----------|------|
| 构建时间 | {mini_build or 'FAILED'}s | {micro_build or 'FAILED'}s | {f'{speedup}x faster ({report["build_time_seconds"]["faster"]})' if speedup else 'N/A'} |

## 二、镜像体积对比

| 指标 | Miniforge3 | micromamba | 差异 |
|------|-----------|-----------|------|
| 镜像体积 | {MINI_SIZE_MB}MB | {MICRO_SIZE_MB}MB | **-{SIZE_DIFF_MB}MB (-{SIZE_DIFF_PCT}%)** |
| /opt/conda大小 | {mini_func.get('conda_dir_mb', 'N/A')}MB | {micro_func.get('conda_dir_mb', 'N/A')}MB |  |
| 镜像层数 | {MINI_LAYERS} | {MICRO_LAYERS} |  |
| Base Python冗余 | {'❌ 有 (py313, ~250MB)' if mini_func.get('has_base_python') else '✅ 无'} | {'❌ 有' if micro_func.get('has_base_python') else '✅ 无 (单一Python环境)'} |  |

## 三、功能完整性对比

| 功能 | Miniforge3 | micromamba |
|------|-----------|-----------|
| Python {mini_func.get('python_version', '')} | {'✅' if mini_func.get('python') else '❌'} | {'✅' if micro_func.get('python') else '❌'} |
| Free-threading (cp314t) | {'✅' if mini_func.get('ft_verified') else '❌'} | {'✅' if micro_func.get('ft_verified') else '❌'} |
| SOABI | {mini_func.get('soabi', 'N/A')} | {micro_func.get('soabi', 'N/A')} |
| conda命令 | {'✅' if mini_func.get('conda_cmd') else '❌'} | {'✅' if micro_func.get('conda_cmd') else '❌'} |
| pip | {'✅' if mini_func.get('pip') else '❌'} | {'✅' if micro_func.get('pip') else '❌'} |
| Jupyter | {'✅' if mini_func.get('jupyter') else '❌'} | {'✅' if micro_func.get('jupyter') else '❌'} |
| Docker CLI | {'✅' if mini_func.get('docker') else '❌'} | {'✅' if micro_func.get('docker') else '❌'} |
| C扩展加载 | {'✅' if mini_func.get('c_extensions') else '❌'} | {'✅' if micro_func.get('c_extensions') else '❌'} |
| main环境包数量 | {mini_func.get('main_env_packages', 'N/A')} | {micro_func.get('main_env_packages', 'N/A')} |

## 四、结论

- **功能对等**：{'✅ 完全对等' if functional_parity else '⚠️ 存在差异，请检查具体项'}
- **构建速度**：{report['verdict']['build_speed_winner']} 更快
- **镜像体积**：{report['verdict']['size_winner']} 更小（减少{SIZE_DIFF_PCT}%）
- **建议**：{report['verdict']['recommendation']}
"""

with open(sys.argv[2], 'w') as f:
    f.write(md)

print(json.dumps(report, indent=2, ensure_ascii=False))
print()
print(md)
PYEOF

# ── 清理 ──
if [ "$KEEP_IMAGES" != true ]; then
    echo ""
    echo "[CLEANUP] Removing experiment images..."
    docker rmi "$BASE_IMAGE" "$MICRO_IMAGE" 2>/dev/null || true
    echo "[OK] Experiment images removed (use --keep to preserve)"
else
    echo ""
    echo "[KEEP] Images preserved:"
    echo "  - $BASE_IMAGE"
    echo "  - $MICRO_IMAGE"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Experiment complete!                                       ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  JSON: %-52s║\n" "$(basename "$JSON_REPORT")"
printf "║  MD:   %-52s║\n" "$(basename "$MD_REPORT")"
echo "╚══════════════════════════════════════════════════════════════╝"
