#!/usr/bin/env bash
# =============================================================================
# Unit tests for resolve_script_path() logic in scripts/start-dev.sh
# These tests run in pure bash WITHOUT requiring Docker.
# Usage: bash tests/test_resolve_script_path.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Copy of resolve_script_path() from start-dev.sh ──
# This is intentionally duplicated for reliable unit testing.
# If you change resolve_script_path() in start-dev.sh, update this copy too.
resolve_script_path() {
    local input="$1"
    if [[ "$input" == /* ]]; then
        echo "$input"
        return
    fi
    local candidates=(
        "$VARIANT_ROOT/$input"
        "$VARIANT_ROOT/examples/$input"
        "$VARIANT_ROOT/tools/$input"
        "$VARIANT_ROOT/scripts/$input"
    )
    local labels=("根目录" "examples/" "tools/" "scripts/")
    for i in "${!candidates[@]}"; do
        local cand="${candidates[$i]}"
        local label="${labels[$i]}"
        if [[ -f "$cand" ]]; then
            local resolved
            if [[ $i -eq 0 ]]; then
                resolved="$input"
            else
                resolved="${label%/}/$input"
            fi
            echo "$resolved"
            return
        fi
    done
    echo "$input"
}

# (debug is a no-op in tests, matching start-dev.sh signature)
debug() { :; }

# ── Test framework ──
PASS=0
FAIL=0

assert_eq() {
    local desc="$1" expected="$2" actual="$3"
    if [[ "$expected" == "$actual" ]]; then
        PASS=$((PASS+1))
        echo "  ✅ $desc"
    else
        FAIL=$((FAIL+1))
        echo "  ❌ $desc"
        echo "     期望: '$expected'"
        echo "     实际: '$actual'"
    fi
}

# ── Setup temp directory to simulate VARIANT_ROOT ──
TEST_TMP="$(mktemp -d)"
trap 'rm -rf "$TEST_TMP"' EXIT

mkdir -p "$TEST_TMP/examples" "$TEST_TMP/tools" "$TEST_TMP/scripts"
touch "$TEST_TMP/examples/simple_verify.py"
touch "$TEST_TMP/examples/inference_demo.py"
touch "$TEST_TMP/tools/ft_compat_check.py"
touch "$TEST_TMP/scripts/run_all_tests.sh"
touch "$TEST_TMP/scripts/start-dev.sh"
touch "$TEST_TMP/Dockerfile"

echo "=== resolve_script_path() 单元测试 ==="
echo "测试目录: $TEST_TMP"
echo ""

# Override VARIANT_ROOT for testing
ORIG_VR="$VARIANT_ROOT"
VARIANT_ROOT="$TEST_TMP"

echo "[Group 1] examples/ 目录自动查找"
result=$(resolve_script_path "simple_verify.py")
assert_eq "simple_verify.py → examples/simple_verify.py" "examples/simple_verify.py" "$result"

result=$(resolve_script_path "inference_demo.py")
assert_eq "inference_demo.py → examples/inference_demo.py" "examples/inference_demo.py" "$result"

echo ""
echo "[Group 2] tools/ 目录自动查找"
result=$(resolve_script_path "ft_compat_check.py")
assert_eq "ft_compat_check.py → tools/ft_compat_check.py" "tools/ft_compat_check.py" "$result"

echo ""
echo "[Group 3] scripts/ 目录自动查找"
result=$(resolve_script_path "run_all_tests.sh")
assert_eq "run_all_tests.sh → scripts/run_all_tests.sh" "scripts/run_all_tests.sh" "$result"

echo ""
echo "[Group 4] 显式路径原样返回（根目录匹配优先级）"
result=$(resolve_script_path "examples/simple_verify.py")
assert_eq "显式 examples/simple_verify.py → examples/simple_verify.py" "examples/simple_verify.py" "$result"

result=$(resolve_script_path "tools/ft_compat_check.py")
assert_eq "显式 tools/ft_compat_check.py → tools/ft_compat_check.py" "tools/ft_compat_check.py" "$result"

echo ""
echo "[Group 5] 根目录文件查找"
result=$(resolve_script_path "Dockerfile")
assert_eq "Dockerfile → Dockerfile（根目录命中）" "Dockerfile" "$result"

echo ""
echo "[Group 6] 绝对路径直通"
result=$(resolve_script_path "/workspace/custom/script.py")
assert_eq "绝对路径 /workspace/... 原样返回" "/workspace/custom/script.py" "$result"

echo ""
echo "[Group 7] 不存在的文件容错（返回原始输入）"
result=$(resolve_script_path "nonexistent_file.py")
assert_eq "不存在的.py → 原样返回" "nonexistent_file.py" "$result"

result=$(resolve_script_path "missing_script.sh")
assert_eq "不存在的.sh → 原样返回" "missing_script.sh" "$result"

echo ""
echo "[Group 8] 查找顺序优先级验证（根目录 > examples > tools > scripts）"
# Create a file that exists in BOTH examples and tools - examples should win
touch "$TEST_TMP/examples/duplicate_test.py"
touch "$TEST_TMP/tools/duplicate_test.py"
result=$(resolve_script_path "duplicate_test.py")
assert_eq "同名文件优先匹配examples/" "examples/duplicate_test.py" "$result"
rm -f "$TEST_TMP/examples/duplicate_test.py" "$TEST_TMP/tools/duplicate_test.py"

# Restore
VARIANT_ROOT="$ORIG_VR"

echo ""
echo "═══════════════════════════════════════"
echo "  测试结果: ✅ $PASS 通过, ❌ $FAIL 失败, 总计 $((PASS+FAIL))"
echo "═══════════════════════════════════════"
if [[ $FAIL -gt 0 ]]; then
    echo "  ❌ 有测试失败！"
    exit 1
else
    echo "  🎉 所有路径解析测试通过！"
fi
