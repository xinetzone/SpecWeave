#!/usr/bin/env bash
# lib.sh — audit-image-contract.sh 单测公共库。
#
# 由 run-tests.sh source；每个用例在独立子 shell 内执行（set -euo pipefail）。
# 用例函数内断言失败即 exit 1，由 run-tests.sh 记为 [FAIL]。
#
# 全局变量（run-tests.sh 注入 / 本库维护）：HERE、AUDIT、STUB_DIR、CASE、FX、RC。

# ---------------------------------------------------------------------------
# fixture 构造：键名与 fixtures/bin/podman 的分派一一对应
# ---------------------------------------------------------------------------
new_fixture() {
    FX="$(mktemp -d "$CASE/fx.XXXXXX")"
    mkdir -p "$FX/run"
}

fx_set() {  # fx_set <key> <value>：CLI 类应答（image_exists/vol_exists/working_dir/cmd/env）
    printf '%s' "$2" > "$FX/$1"
}

fx_run() {  # fx_run <run-key> <rc> [stdout]：容器类应答
    printf '%s' "$2" > "$FX/run/$1.rc"
    printf '%s' "${3-}" > "$FX/run/$1.out"
}

pth_text() {  # pth_text <ver>：npu-toolchain.pth 的三行期望正文（含结尾换行）
    printf '%s\n' \
        "/opt/build/npuusertools/userbase/lib/python$1/site-packages" \
        "/workspace/ai/notebook/libs/npuusertools" \
        "/workspace/ai/notebook/libs/npu_tvm/python"
}

fx_a5_text() {  # fx_a5_text <file>：把任意文件内容作为 a5_file 的实测应答（字节数 + sha256）
    local b s
    b="$(wc -c < "$1" | tr -d ' ')"
    s="$(sha256sum "$1" | cut -d' ' -f1)"
    fx_run a5_file 0 "$b
$s"
}

fx_a5_ok() {  # fx_a5_ok <ver>：按期望正文生成 a5_file 应答（应 PASS）
    local f="$CASE/a5.ok"
    pth_text "$1" > "$f"
    fx_a5_text "$f"
}

# ---------------------------------------------------------------------------
# 默认“好世界”：全部检查应 PASS（A1–A7 + B1–B3 = 10 项）
# ---------------------------------------------------------------------------
fx_default_good() {
    fx_set image_exists 1
    fx_set vol_exists 1
    fx_set working_dir /workspace
    fx_set cmd '["sleep","infinity"]'
    fx_set env 'TVM_LIBRARY_PATH=/opt/build/npu_tvm
TEST_DATA_ROOT_PATH=/opt/build/tvm_test_data
TVM_TEST_DATA_DIR=/opt/build/tvm_test_data'

    fx_run a1 0 'openkylin|3.0|huanghe'
    fx_run a2_gcc 0 'gcc (OpenKylin 15.2.0-16ok8) 15.2.0'
    fx_run a2_ldd 0 'ldd (Ubuntu GLIBC 2.43-ok2) 2.43'
    fx_run a3_dir 0 ''
    fx_run a3_py 0 'Python 3.14.10'
    fx_run a3_pip 0 '26.2.2'
    fx_run a3_tools 0 ''
    fx_run a4 0 'ok:conda-site.pth
ok:npu-toolchain.pth'
    fx_run a5_ver 0 '3.14'
    fx_a5_ok 3.14
    fx_run a6 0 'dir:ok
link:/opt/build'
    fx_run b1 0 ''
    fx_run b2 0 '0'
    fx_run b3 0 ''
    fx_run c2 0 'optbuild:mounted
workspace:mounted
libtvm:present'
    fx_run c1 0 '	libLLVM.so.22.1 => /var/opt/build/llvm22/lib/libLLVM.so.22.1 (0x00007f00)
size:195933536'
}

# ---------------------------------------------------------------------------
# 执行被测脚本
# ---------------------------------------------------------------------------
run_audit_script() {  # run_audit_script <script> [args...]
    local script="$1"
    shift
    set +e
    PATH="$STUB_DIR:$PATH" AUDIT_FIXTURE="$FX" bash "$script" "$@" > "$CASE/out.txt" 2>&1
    RC=$?
    set -e
}

run_audit() { run_audit_script "$AUDIT" "$@"; }

# ---------------------------------------------------------------------------
# 断言
# ---------------------------------------------------------------------------
fail() { printf '断言失败: %s\n' "$*" >&2; exit 1; }

assert_rc() { [ "$RC" -eq "$1" ] || fail "exit=$RC，期望 $1"; }

assert_summary() {  # assert_summary <total> <pass> <fail> <unknown>
    grep -qF "total=$1 pass=$2 fail=$3 unknown=$4" "$CASE/out.txt" \
        || fail "汇总行不匹配，期望 total=$1 pass=$2 fail=$3 unknown=$4"
}

assert_result() {  # assert_result <PASS|FAIL|UNKNOWN> <check-name>：SUMMARY 行精确命中
    local want
    want="$(printf '%-7s %-26s' "$1" "$2")"
    grep -qF "$want" "$CASE/out.txt" || fail "SUMMARY 缺少 ${1} 行: $2"
}

assert_no_result() {  # assert_no_result <PASS|FAIL|UNKNOWN> <check-name>
    local want
    want="$(printf '%-7s %-26s' "$1" "$2")"
    ! grep -qF "$want" "$CASE/out.txt" || fail "SUMMARY 不应出现 ${1} 行: $2"
}

assert_contains() { grep -qF -- "$1" "$CASE/out.txt" || fail "输出缺少文案: $1"; }

assert_not_contains() { ! grep -qF -- "$1" "$CASE/out.txt" || fail "输出不应包含: $1"; }

assert_json_ok() {
    grep '^{"image"' "$CASE/out.txt" | tail -n1 > "$CASE/audit.json"
    [ -s "$CASE/audit.json" ] || fail "输出中找不到 JSON 行"
    python3 -m json.tool "$CASE/audit.json" > /dev/null 2>&1 \
        || fail "JSON 不能被 python3 -m json.tool 解析"
}

assert_json_note_eq() {  # assert_json_note_eq <checks 下标> <期望 note 原文>
    # 解析 JSON 后逐字符比对 note：若控制字符被替换成空格或被二次转义，此处必然失败。
    python3 - "$CASE/audit.json" "$1" "$2" <<'PY' || fail "JSON note 与原文不符（控制字符可能被替换或转义错误）"
import json
import sys

path, idx, expected = sys.argv[1], int(sys.argv[2]), sys.argv[3]
note = json.load(open(path))["checks"][idx]["note"]
if note != expected:
    print("实测:", [hex(ord(c)) for c in note], file=sys.stderr)
    print("期望:", [hex(ord(c)) for c in expected], file=sys.stderr)
    sys.exit(1)
PY
}

assert_json_fields() {  # assert_json_fields <exit> <total> <pass> <fail> <unknown>
    local got
    got="$(python3 - "$CASE/audit.json" <<'PY'
import json
import sys

d = json.load(open(sys.argv[1]))
print(d["exit"], d["total"], d["pass"], d["fail"], d["unknown"], len(d["checks"]) - d["total"])
PY
)"
    [ "$got" = "$1 $2 $3 $4 $5 0" ] \
        || fail "JSON 字段不一致: 实测[$got]，期望[$1 $2 $3 $4 $5 0]"
}
