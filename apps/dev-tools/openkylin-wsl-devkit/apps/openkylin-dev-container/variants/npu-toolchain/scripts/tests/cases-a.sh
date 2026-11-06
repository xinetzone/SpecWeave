#!/usr/bin/env bash
# cases-a.sh — A 组：应 PASS 的用例（由 run-tests.sh source）

case_a01() {  # 全部符合契约 → 全 PASS、exit 0、total 与 pass 计数一致
    new_fixture
    fx_default_good
    run_audit
    assert_rc 0
    assert_summary 10 10 0 0
    assert_contains "exit=0"
    assert_result PASS "A1 /etc/os-release"
    assert_result PASS "A2 gcc 15.2.0 + ldd"
    assert_result PASS "A3 conda env / python / pip / 工具"
    assert_result PASS "A4 conda-site.pth + npu-toolchain.pth"
    assert_result PASS "A5 npu-toolchain.pth 逐字三行"
    assert_result PASS "A6 /var/opt/build -> /opt/build"
    assert_result PASS "A7 WorkingDir / Cmd / Env"
    assert_result PASS "B1 无 tvm/xmnn 实体"
    assert_result PASS "B2 /opt/build 为空"
    assert_result PASS "B3 无挂载时不可 import"
    assert_not_contains "[FAIL   ]"
    assert_not_contains "[UNKNOWN]"
}
