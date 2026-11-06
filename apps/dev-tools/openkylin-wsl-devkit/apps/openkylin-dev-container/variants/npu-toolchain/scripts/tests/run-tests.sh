#!/usr/bin/env bash
# run-tests.sh — audit-image-contract.sh 的离线单元测试入口。
#
# 用法（在 variants/npu-toolchain 目录下）：
#   bash scripts/tests/run-tests.sh
#
# 设计要点：
#   - 全部用例离线执行：把 fixtures/bin/podman 桩前置到 PATH，按 fixture 应答，
#     绝不接触真实 podman、真实镜像或 npu-build 卷。
#   - 每条用例独立 fixture + 独立临时目录；整体用 mktemp -d + trap 清理。
#   - 输出每行一个 [PASS]/[FAIL] <case-id> <说明>，末尾汇总 total/pass/fail 与 exit。
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT="$HERE/../audit-image-contract.sh"
STUB_DIR="$HERE/fixtures/bin"

[ -f "$AUDIT" ] || { echo "找不到被测脚本: $AUDIT" >&2; exit 1; }
[ -x "$STUB_DIR/podman" ] || { echo "podman 桩缺失或不可执行: $STUB_DIR/podman" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || echo "[warn] 未找到 python3，D 组 JSON 用例将失败" >&2

TMPROOT="$(mktemp -d "${TMPDIR:-/tmp}/audit-contract-tests.XXXXXX")"
cleanup() { rm -rf "$TMPROOT"; }
trap cleanup EXIT INT TERM

# shellcheck source=lib.sh
. "$HERE/lib.sh"

CASES_TOTAL=0
CASES_PASS=0
CASES_FAIL=0

CASE=""
FX=""
RC=0

run_case() {  # run_case <case-id> <一句话说明> <用例函数>
    local id="$1" desc="$2" fn="$3"
    CASES_TOTAL=$((CASES_TOTAL + 1))
    CASE="$TMPROOT/$id"
    mkdir -p "$CASE"
    if (set -euo pipefail; "$fn") > "$CASE/case.log" 2>&1; then
        printf '[PASS] %-4s %s\n' "$id" "$desc"
        CASES_PASS=$((CASES_PASS + 1))
    else
        printf '[FAIL] %-4s %s\n' "$id" "$desc"
        sed 's/^/       | /' "$CASE/case.log" >&2
        CASES_FAIL=$((CASES_FAIL + 1))
    fi
}

for f in "$HERE"/cases-*.sh; do
    # shellcheck source=/dev/null
    . "$f"
done

echo "===== audit-image-contract.sh 离线单元测试 ====="
echo "被测脚本: $AUDIT"
echo "podman 桩: $STUB_DIR/podman"
echo

# ---- A 组：应 PASS --------------------------------------------------------
run_case A01 "全部符合契约 → 10/10 PASS、exit 0" case_a01

# ---- B 组：单项 FAIL ------------------------------------------------------
run_case B02 "gcc 缺失 → A2 FAIL、exit 1" case_b02
run_case B03 "gcc 版本漂移 13.2.0 → A2 FAIL" case_b03
run_case B04 "conda-site.pth 缺失 → A4 FAIL" case_b04
run_case B05 "npu-toolchain.pth 少一行 → A5 FAIL" case_b05
run_case B06 "npu-toolchain.pth 行序颠倒 → A5 FAIL（非集合比对）" case_b06
run_case B07 "npu-toolchain.pth 结尾无换行 → A5 FAIL（字节级比对生效）" case_b07
run_case B08 "/var/opt/build 软链指向 /opt → A6 FAIL" case_b08
run_case B09 "WorkingDir 非 /workspace → A7 FAIL" case_b09
run_case B10 "Env 缺 TVM_LIBRARY_PATH → A7 FAIL" case_b10
run_case B11 "镜像内存在 libtvm.so → B1 FAIL" case_b11
run_case B12 "镜像内存在 xmnn 目录 → B1 FAIL" case_b12
run_case B13 "/opt/build 非空 → B2 FAIL" case_b13
run_case B14 "--with-volume 下 libLLVM 落到系统包 → C1 FAIL" case_b14

# ---- C 组：UNKNOWN 与参数 ------------------------------------------------
run_case C15 "镜像不存在 → unknown=1、exit 2" case_c15
run_case C16 "非法参数 → 用法提示、exit 2" case_c16
run_case C17 "FAIL+UNKNOWN 同时出现 → exit 1（FAIL 优先）" case_c17
run_case C23 "--with-volume 且卷不存在 → C2/C1 均 UNKNOWN、exit 2" case_c23

# ---- D 组：输出契约 ------------------------------------------------------
run_case D18 "--json 可解析且字段与 exit_code 一致" case_d18
run_case D19 "汇总行自洽 total == pass+fail+unknown" case_d19
run_case D22 "note 含 Tab 时 --json 仍是合法 JSON" case_d22
run_case D24 "pth 含非 ASCII 时仍按字节口径比对" case_d24

# ---- E 组：变异测试 ------------------------------------------------------
run_case E20 "变异：移除 A5 检查后同一 FAIL 构造不再被检出" case_e20
run_case E21 "变异：移除 B1 检查后同一 FAIL 构造不再被检出" case_e21

echo
echo "-----------------------------------------"
printf 'total=%d pass=%d fail=%d\n' "$CASES_TOTAL" "$CASES_PASS" "$CASES_FAIL"
if [ "$CASES_FAIL" -gt 0 ]; then
    echo "exit=1"
    exit 1
fi
echo "exit=0"
exit 0
