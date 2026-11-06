#!/usr/bin/env bash
# cases-b.sh — B 组：单项 FAIL，逐项独立构造（每例只破坏一个条件）

case_b02() {  # gcc 缺失 → A2 FAIL、exit 1
    new_fixture
    fx_default_good
    fx_run a2_gcc 127 ''
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "A2 gcc 15.2.0 + ldd"
    assert_contains "gcc 不可用"
}

case_b03() {  # gcc 版本漂移（13.2.0）→ A2 FAIL
    new_fixture
    fx_default_good
    fx_run a2_gcc 0 'gcc (GCC) 13.2.0'
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "A2 gcc 15.2.0 + ldd"
    assert_contains "gcc 版本不符: gcc (GCC) 13.2.0"
}

case_b04() {  # conda-site.pth 缺失 → A4 FAIL
    new_fixture
    fx_default_good
    fx_run a4 0 'missing:conda-site.pth
ok:npu-toolchain.pth'
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "A4 conda-site.pth + npu-toolchain.pth"
    assert_contains "missing:conda-site.pth"
}

case_b05() {  # npu-toolchain.pth 少一行 → A5 FAIL（字节数即不同）
    new_fixture
    fx_default_good
    printf '%s\n' \
        "/opt/build/npuusertools/userbase/lib/python3.14/site-packages" \
        "/workspace/ai/notebook/libs/npuusertools" > "$CASE/a5short"
    fx_a5_text "$CASE/a5short"
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "A5 npu-toolchain.pth 逐字三行"
    assert_contains "实测 103 B"
    assert_contains "期望 146 B"
}

case_b06() {  # npu-toolchain.pth 行序颠倒 → A5 FAIL（同字节数、不同 sha ⇒ 非集合比对）
    new_fixture
    fx_default_good
    printf '%s\n' \
        "/workspace/ai/notebook/libs/npu_tvm/python" \
        "/workspace/ai/notebook/libs/npuusertools" \
        "/opt/build/npuusertools/userbase/lib/python3.14/site-packages" > "$CASE/a5rev"
    fx_a5_text "$CASE/a5rev"
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "A5 npu-toolchain.pth 逐字三行"
    assert_contains "实测 146 B"
    assert_contains "期望 146 B"
}

case_b07() {  # npu-toolchain.pth 结尾无换行 → A5 FAIL（证明字节级比对生效）
    new_fixture
    fx_default_good
    printf '%s\n%s\n%s' \
        "/opt/build/npuusertools/userbase/lib/python3.14/site-packages" \
        "/workspace/ai/notebook/libs/npuusertools" \
        "/workspace/ai/notebook/libs/npu_tvm/python" > "$CASE/a5nonl"
    fx_a5_text "$CASE/a5nonl"
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "A5 npu-toolchain.pth 逐字三行"
    assert_contains "实测 145 B"
    assert_contains "期望 146 B"
}

case_b08() {  # /var/opt/build 软链指向别处（/opt）→ A6 FAIL
    new_fixture
    fx_default_good
    fx_run a6 0 'dir:ok
link:/opt'
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "A6 /var/opt/build -> /opt/build"
    assert_contains "link:/opt"
}

case_b09() {  # WorkingDir 不是 /workspace → A7 FAIL
    new_fixture
    fx_default_good
    fx_set working_dir /tmp
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "A7 WorkingDir / Cmd / Env"
    assert_contains "WorkingDir=/tmp"
}

case_b10() {  # Env 缺 TVM_LIBRARY_PATH → A7 FAIL
    new_fixture
    fx_default_good
    fx_set env 'TEST_DATA_ROOT_PATH=/opt/build/tvm_test_data
TVM_TEST_DATA_DIR=/opt/build/tvm_test_data'
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "A7 WorkingDir / Cmd / Env"
    assert_contains "Env 命中 2/3"
}

case_b11() {  # 镜像内存在 libtvm.so → B1 FAIL
    new_fixture
    fx_default_good
    fx_run b1 0 '/usr/local/lib/libtvm.so'
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "B1 无 tvm/xmnn 实体"
    assert_contains "1 处命中"
    assert_contains "/usr/local/lib/libtvm.so"
}

case_b12() {  # 镜像内存在 xmnn 目录 → B1 FAIL
    new_fixture
    fx_default_good
    fx_run b1 0 '/usr/local/lib/xmnn'
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "B1 无 tvm/xmnn 实体"
    assert_contains "1 处命中"
}

case_b13() {  # /opt/build 非空 → B2 FAIL
    new_fixture
    fx_default_good
    fx_run b2 0 '3'
    run_audit
    assert_rc 1
    assert_summary 10 9 1 0
    assert_result FAIL "B2 /opt/build 为空"
    assert_contains "/opt/build 内有 3 项"
}

case_b14() {  # --with-volume 下 libLLVM 解析到系统包（147,600,808 B）→ C1 FAIL
    new_fixture
    fx_default_good
    fx_run c1 0 '	libLLVM.so.22.1 => /usr/lib/x86_64-linux-gnu/libLLVM.so.22.1 (0x00007f00)
size:147600808'
    run_audit --with-volume
    assert_rc 1
    assert_summary 12 11 1 0
    assert_result PASS "C2 npu-build / workspace 挂载"
    assert_result FAIL "C1 libtvm.so -> llvm22 解析"
    assert_contains "落到了系统包"
    assert_contains "/usr/lib/x86_64-linux-gnu/libLLVM.so.22.1"
}
