#!/usr/bin/env bash
# cases-e.sh — E 组：变异测试（证明用例真的在“测东西”，而非恒真）
#
# 做法：取被测脚本的一份副本，删掉某一行 check 调用，再用同一 FAIL 构造重跑。
# 若“改前 FAIL、改后 PASS”不成立，则说明对应用例不具备检出能力 → 判本用例 FAIL。

case_e20() {  # 变异 1：移除 A5 的 pth 比对
    new_fixture
    fx_default_good
    printf '%s\n' \
        "/opt/build/npuusertools/userbase/lib/python3.14/site-packages" \
        "/workspace/ai/notebook/libs/npuusertools" > "$CASE/a5short"
    fx_a5_text "$CASE/a5short"

    run_audit
    assert_rc 1
    assert_result FAIL "A5 npu-toolchain.pth 逐字三行"
    echo "变异前：exit=$RC，A5 判 FAIL（检出有效）"

    grep -vF 'check "A5 npu-toolchain.pth 逐字三行" a5_pth_content' "$AUDIT" \
        > "$CASE/mutant-a5.sh"
    if cmp -s "$AUDIT" "$CASE/mutant-a5.sh"; then
        fail "变异未生效：副本与原文一致（未找到 A5 检查行）"
    fi

    run_audit_script "$CASE/mutant-a5.sh"
    [ "$RC" -eq 0 ] || fail "变异后仍 exit=$RC（用例对 A5 不敏感）"
    assert_no_result FAIL "A5 npu-toolchain.pth 逐字三行"
    assert_not_contains "A5 npu-toolchain.pth 逐字三行"
    assert_summary 9 9 0 0
    echo "变异后：exit=$RC，A5 行消失、total 10→9（用例会因此失败，说明它真的在测）"
}

case_e21() {  # 变异 2：移除 B1 的实体扫描
    new_fixture
    fx_default_good
    fx_run b1 0 '/usr/local/lib/libtvm.so'

    run_audit
    assert_rc 1
    assert_result FAIL "B1 无 tvm/xmnn 实体"
    echo "变异前：exit=$RC，B1 判 FAIL（检出有效）"

    grep -vF 'check "B1 无 tvm/xmnn 实体" b1_no_artifacts' "$AUDIT" \
        > "$CASE/mutant-b1.sh"
    if cmp -s "$AUDIT" "$CASE/mutant-b1.sh"; then
        fail "变异未生效：副本与原文一致（未找到 B1 检查行）"
    fi

    run_audit_script "$CASE/mutant-b1.sh"
    [ "$RC" -eq 0 ] || fail "变异后仍 exit=$RC（用例对 B1 不敏感）"
    assert_no_result FAIL "B1 无 tvm/xmnn 实体"
    assert_not_contains "B1 无 tvm/xmnn 实体"
    assert_summary 9 9 0 0
    echo "变异后：exit=$RC，B1 行消失、total 10→9（用例会因此失败，说明它真的在测）"
}
