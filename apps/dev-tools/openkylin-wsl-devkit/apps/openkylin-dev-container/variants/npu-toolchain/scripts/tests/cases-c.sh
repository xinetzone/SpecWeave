#!/usr/bin/env bash
# cases-c.sh — C 组：UNKNOWN 语义与非法参数

case_c15() {  # 镜像不存在 → unknown=1、exit 2
    new_fixture
    fx_default_good
    fx_set image_exists 0
    run_audit
    assert_rc 2
    assert_summary 1 0 0 1
    assert_result UNKNOWN "镜像存在"
    assert_contains "不存在"
    assert_not_contains "[FAIL   ]"
}

case_c16() {  # 非法参数 → 用法提示、exit 2
    new_fixture
    run_audit --bogus
    assert_rc 2
    assert_contains "未知参数: --bogus"
    assert_contains "用法:"
    assert_not_contains "total="
}

case_c17() {  # FAIL 与 UNKNOWN 同时出现 → exit 1（FAIL 优先），且两类分行呈现
    new_fixture
    fx_default_good
    fx_set vol_exists 0
    fx_run a2_gcc 0 'gcc (GCC) 13.2.0'
    run_audit --with-volume
    assert_rc 1
    assert_summary 12 9 1 2
    assert_result FAIL "A2 gcc 15.2.0 + ldd"
    assert_result UNKNOWN "C2 npu-build / workspace 挂载"
    assert_result UNKNOWN "C1 libtvm.so -> llvm22 解析"
    assert_contains "卷 npu-build 不存在"
    assert_not_contains "exit=2"
}

case_c23() {  # --with-volume 且卷不存在 → C2/C1 均 UNKNOWN、exit 2、fail=0
    new_fixture
    fx_default_good
    fx_set vol_exists 0
    run_audit --with-volume
    assert_rc 2
    assert_summary 12 10 0 2
    assert_result UNKNOWN "C2 npu-build / workspace 挂载"
    assert_result UNKNOWN "C1 libtvm.so -> llvm22 解析"
    assert_not_contains "[FAIL   ]"
    assert_contains "exit=2"
}
