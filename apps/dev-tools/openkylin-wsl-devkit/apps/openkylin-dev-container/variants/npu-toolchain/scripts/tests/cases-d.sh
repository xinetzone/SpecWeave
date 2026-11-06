#!/usr/bin/env bash
# cases-d.sh — D 组：输出契约（--json 与汇总行自洽）

case_d18() {  # --json 可被 python3 -m json.tool 解析，字段与 exit_code 一致
    new_fixture
    fx_default_good
    run_audit --json
    assert_rc 0
    assert_summary 10 10 0 0
    assert_json_ok
    assert_json_fields 0 10 10 0 0
    assert_contains '"with_volume":false'
    assert_contains '"exit":0'
}

case_d19() {  # 汇总行自洽：total == pass + fail + unknown，且等于 SUMMARY 行数
    new_fixture
    fx_default_good
    fx_set vol_exists 0
    fx_run a2_gcc 0 'gcc (GCC) 13.2.0'
    run_audit --with-volume
    assert_rc 1

    local line t p f u nrows sum
    line="$(grep -F 'total=' "$CASE/out.txt")"
    t="$(printf '%s' "$line" | sed -n 's/.*total=\([0-9]*\).*/\1/p')"
    p="$(printf '%s' "$line" | sed -n 's/.*pass=\([0-9]*\).*/\1/p')"
    f="$(printf '%s' "$line" | sed -n 's/.*fail=\([0-9]*\).*/\1/p')"
    u="$(printf '%s' "$line" | sed -n 's/.*unknown=\([0-9]*\).*/\1/p')"
    [ -n "$t" ] && [ -n "$p" ] && [ -n "$f" ] && [ -n "$u" ] || fail "汇总行解析失败: $line"
    sum=$((p + f + u))
    [ "$sum" -eq "$t" ] || fail "自洽性失败: total=$t ≠ pass+fail+unknown=$sum"
    nrows="$(grep -cE '^(PASS|FAIL|UNKNOWN) ' "$CASE/out.txt" || true)"
    [ "$nrows" -eq "$t" ] || fail "SUMMARY 行数 $nrows ≠ total=$t"
    assert_summary "$t" "$p" "$f" "$u"
}

case_d22() {  # note 含 Tab（ldd 真实输出形态）时 --json 仍是合法 JSON
    new_fixture
    fx_default_good
    fx_run c1 0 '	libLLVM.so.22.1 => /usr/lib/x86_64-linux-gnu/libLLVM.so.22.1 (0x00007f00)
size:147600808'
    run_audit --with-volume --json
    assert_rc 1
    assert_summary 12 11 1 0

    # 前提确认：note 里确实带进了裸 Tab，否则这条用例测不到东西
    grep -q "$(printf '\t')" "$CASE/out.txt" || fail "输出中未出现 Tab，构造无效"
    assert_json_ok
    assert_json_fields 1 12 11 1 0
}

case_d24() {  # pth 期待值含非 ASCII 时仍按字节计（副本替换路径，不改被测脚本）
    new_fixture
    fx_default_good
    local mut="$CASE/mutant-utf8.sh"
    local line3="/workspace/ai/notebook/libs/工具链/python"

    sed "s|/workspace/ai/notebook/libs/npu_tvm/python|$line3|g" "$AUDIT" > "$mut"
    cmp -s "$AUDIT" "$mut" && fail "变异未生效：未找到期望路径行"

    {
        printf '%s\n' "/opt/build/npuusertools/userbase/lib/python3.14/site-packages"
        printf '%s\n' "/workspace/ai/notebook/libs/npuusertools"
        printf '%s\n' "$line3"
    } > "$CASE/a5utf8"
    fx_a5_text "$CASE/a5utf8"

    run_audit_script "$mut"
    assert_rc 0
    assert_summary 10 10 0 0
    assert_result PASS "A5 npu-toolchain.pth 逐字三行"
    # 148 B（字节）而非 143（字符）：旧口径会把这条判成 FAIL
    assert_contains "148 B"
}
