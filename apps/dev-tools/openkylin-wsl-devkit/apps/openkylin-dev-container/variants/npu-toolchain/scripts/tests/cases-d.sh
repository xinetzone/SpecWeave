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

case_d25() {  # note 含 SOH/VT/US 时 --json 合法，且解析后原控制字符逐字还原（未被替换成空格）
    new_fixture
    fx_default_good
    local raw
    raw="$(printf 'x\001y\013z\037w')"
    fx_run a1 0 "$raw"
    run_audit --json
    assert_rc 1
    assert_summary 10 9 1 0

    # 前提确认：SUMMARY 表格里仍是裸控制字符（JSON 里才应是 \u00XX），否则构造无效
    grep -q "$(printf '\001')" "$CASE/out.txt" || fail "输出中未出现裸 SOH，构造无效"
    assert_json_ok
    assert_json_fields 1 10 9 1 0
    # 信息未丢失的判据：json.loads 后 note 与原文逐字符相等（空格替换/二次转义都会失败）
    assert_json_note_eq 0 "实测 ${raw}（期望 openkylin|3.0|huanghe）"
    grep -qF '\u0001' "$CASE/audit.json" || fail "SOH 未编码为 \\u0001"
}

case_d26() {  # note 同时含 反斜杠 / 双引号 / Tab / SOH 四类，转义各自正确
    new_fixture
    fx_default_good
    local raw
    raw="$(printf 'a\\b"c\td\001e')"
    fx_run a1 0 "$raw"
    run_audit --json
    assert_rc 1
    assert_summary 10 9 1 0
    assert_json_ok
    assert_json_fields 1 10 9 1 0
    assert_json_note_eq 0 "实测 ${raw}（期望 openkylin|3.0|huanghe）"
    # 逐类核对字面形态：反斜杠 \\、双引号 \"、Tab \t、SOH \u0001，且无二次转义
    grep -qF 'a\\b\"c\td\u0001e' "$CASE/audit.json" || fail "四类混合转义结果不符"
}

case_d27() {  # 已知边界：NUL（U+0000）无法存在于 bash 字符串，json_escape 不覆盖该码位
    # bash 的命令替换会丢弃 NUL 并告警（"ignored null byte in input"），NUL 根本到不了
    # json_escape；本用例锁定该边界的事实：JSON 仍合法、输出中无裸 NUL 泄漏。
    # 这是 bash 数据通路的固有限制，非本脚本缺陷；若要覆盖 U+0000 须先改造数据通路。
    new_fixture
    fx_default_good
    printf 'x\000y' > "$FX/run/a1.out"
    run_audit --json
    assert_rc 1

    # note 被 check() 截到 220 字符，故只匹配告警前缀，避免被截断位置不同的影响
    grep -q 'command substitution: ignored' "$CASE/out.txt" || fail "构造无效：NUL 未被命令替换丢弃"
    assert_json_ok
    [ "$(tr -cd '\000' < "$CASE/audit.json" | wc -c)" -eq 0 ] || fail "JSON 中出现裸 NUL 字节"
    ! grep -qF '\u0000' "$CASE/audit.json" || fail "不应出现 \\u0000（NUL 已在数据通路被丢弃）"
}
