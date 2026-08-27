#!/usr/bin/env bash
# =============================================================================
# test_safe_cleanup.sh — safe_cleanup.sh 单元测试
# 用法: bash test_safe_cleanup.sh
# 所有测试在隔离的临时目录中运行，不影响系统文件
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/safe_cleanup.sh"

PASS=0
FAIL=0
TESTS=()

# 测试辅助
test_start() {
    TESTS+=("$1")
    echo -n "  TEST: $1 ... "
}

test_pass() {
    echo "PASS"
    PASS=$((PASS + 1))
}

test_fail() {
    echo "FAIL: $1"
    FAIL=$((FAIL + 1))
}

# 创建隔离测试根目录
TEST_ROOT=$(mktemp -d)
trap "rm -rf $TEST_ROOT" EXIT

echo ""
echo "========================================"
echo " safe_cleanup.sh 单元测试"
echo " Test root: $TEST_ROOT"
echo "========================================"
echo ""

# ---------------------------------------------------------------------------
# Test 1: safe_is_subpath 基本判断
# ---------------------------------------------------------------------------
test_start "safe_is_subpath: /tmp/foo is inside /tmp"
if safe_is_subpath "/tmp/foo" "/tmp"; then
    test_pass
else
    test_fail "expected true"
fi

test_start "safe_is_subpath: /root is NOT inside /tmp"
if ! safe_is_subpath "/root" "/tmp"; then
    test_pass
else
    test_fail "expected false"
fi

test_start "safe_is_subpath: / is ancestor of everything"
if safe_is_subpath "/tmp/foo/bar" "/"; then
    test_pass
else
    test_fail "expected true"
fi

test_start "safe_is_subpath: path equals parent"
if safe_is_subpath "/tmp" "/tmp"; then
    test_pass
else
    test_fail "expected true"
fi

test_start "safe_is_subpath: trailing slash normalized"
if safe_is_subpath "/tmp/foo/" "/tmp"; then
    test_pass
else
    test_fail "expected true (trailing /)"
fi

# ---------------------------------------------------------------------------
# Test 2: safe_assert_isolated — 正确情况
# ---------------------------------------------------------------------------
test_start "safe_assert_isolated: /root/backup outside /tmp → pass"
if safe_assert_isolated "/root/backup" "/tmp" 2>/dev/null; then
    test_pass
else
    test_fail "expected pass"
fi

# ---------------------------------------------------------------------------
# Test 3: safe_assert_isolated — 违规情况（备份在删除域内）
# ---------------------------------------------------------------------------
test_start "safe_assert_isolated: /tmp/backup inside /tmp → fail (catches bug!)"
if safe_assert_isolated "/tmp/backup" "/tmp" 2>/dev/null; then
    test_fail "should have failed (this is the bug we prevent!)"
else
    test_pass
fi

# ---------------------------------------------------------------------------
# Test 4: safe_cleanup_dir — 无保留项，清理所有内容
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test4"
mkdir -p "$test_dir"
touch "$test_dir/file1.txt" "$test_dir/.hidden"
mkdir -p "$test_dir/subdir"
touch "$test_dir/subdir/nested.txt"

test_start "safe_cleanup_dir: no preserves — deletes all (including hidden)"
safe_cleanup_dir "$test_dir"
remaining=$(find "$test_dir" -mindepth 1 -maxdepth 1 | wc -l)
if [ "$remaining" -eq 0 ]; then
    test_pass
else
    test_fail "expected 0 remaining, got $remaining"
fi

# ---------------------------------------------------------------------------
# Test 5: safe_cleanup_dir — 白名单保留文件
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test5"
mkdir -p "$test_dir"
touch "$test_dir/keep.txt" "$test_dir/delete1.txt" "$test_dir/delete2.log"
mkdir -p "$test_dir/keepdir" "$test_dir/deletedir"
touch "$test_dir/keepdir/.gitkeep" "$test_dir/deletedir/junk"

test_start "safe_cleanup_dir: preserve keep.txt and keepdir"
safe_cleanup_dir "$test_dir" "$test_dir/keep.txt" "$test_dir/keepdir"
if [ -f "$test_dir/keep.txt" ] && [ -d "$test_dir/keepdir" ] && \
   [ ! -e "$test_dir/delete1.txt" ] && [ ! -d "$test_dir/deletedir" ]; then
    test_pass
else
    test_fail "preservation failed"
    ls -la "$test_dir"
fi

# ---------------------------------------------------------------------------
# Test 6: safe_cleanup_dir — 隐藏文件也被清理
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test6"
mkdir -p "$test_dir" "$test_dir/.hidden_dir"
touch "$test_dir/.hidden_file" "$test_dir/.hidden_dir/junk"
touch "$test_dir/visible.txt"

test_start "safe_cleanup_dir: cleans hidden files/dirs too"
safe_cleanup_dir "$test_dir" "$test_dir/.hidden_dir"
if [ -d "$test_dir/.hidden_dir" ] && [ ! -f "$test_dir/.hidden_file" ] && [ ! -f "$test_dir/visible.txt" ]; then
    test_pass
else
    test_fail "hidden file handling failed"
    ls -la "$test_dir"
fi

# ---------------------------------------------------------------------------
# Test 7: safe_cleanup_move_aside — 移开-清理-恢复模式
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test7"
backup_dir="${TEST_ROOT}/test7-backup"
mkdir -p "$test_dir" "$backup_dir"
mkdir -p "$test_dir/preserve-me"
echo "timer data" > "$test_dir/preserve-me/state.txt"
touch "$test_dir/junk1.tmp" "$test_dir/junk2.log"
mkdir -p "$test_dir/temp-cache"
touch "$test_dir/temp-cache/cache.bin"

test_start "safe_cleanup_move_aside: preserves directory contents, cleans rest"
safe_cleanup_move_aside "$test_dir" "$backup_dir" "$test_dir/preserve-me"
# 验证保留目录恢复且内容完整
if [ -f "$test_dir/preserve-me/state.txt" ] && \
   grep -q "timer data" "$test_dir/preserve-me/state.txt" && \
   [ ! -e "$test_dir/junk1.tmp" ] && [ ! -d "$test_dir/temp-cache" ]; then
    test_pass
else
    test_fail "move-aside/restore failed"
    echo "--- contents of $test_dir ---"
    find "$test_dir" -type f
fi

# ---------------------------------------------------------------------------
# Test 8: safe_cleanup_move_aside — 备份在删除域内时拒绝执行
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test8"
mkdir -p "$test_dir"
mkdir -p "$test_dir/preserve-me"
touch "$test_dir/preserve-me/data.txt"
touch "$test_dir/junk"

test_start "safe_cleanup_move_aside: REFUSES when backup parent is inside target (the bug!)"
# backup_parent_dir = /tmp/inside-test8 (在 test8 内) — 应该被拒绝
mkdir -p "$test_dir/backup-inside"
if safe_cleanup_move_aside "$test_dir" "$test_dir/backup-inside" "$test_dir/preserve-me" 2>/dev/null; then
    test_fail "should have refused! backup inside target = self-destruction bug"
else
    test_pass
fi

# ---------------------------------------------------------------------------
# Test 9: 根目录安全护栏
# ---------------------------------------------------------------------------
test_start "safe_cleanup_dir: refuses to clean / (root guard)"
if safe_cleanup_dir "/" 2>/dev/null; then
    test_fail "should refuse to clean root"
else
    test_pass
fi

# ---------------------------------------------------------------------------
# Test 10: 不存在的目录不报错
# ---------------------------------------------------------------------------
test_start "safe_cleanup_dir: nonexistent dir → warn but no error"
if safe_cleanup_dir "${TEST_ROOT}/nonexistent" 2>/dev/null; then
    test_pass
else
    test_fail "should return 0 for nonexistent dir"
fi

# ---------------------------------------------------------------------------
# Test 11: safe_mktemp_outside 创建的文件在目标域外
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test11"
mkdir -p "$test_dir"

test_start "safe_mktemp_outside: creates temp file outside target"
tmpf=$(safe_mktemp_outside "$test_dir" "test11-")
if [ -n "$tmpf" ] && [ -f "$tmpf" ] && ! safe_is_subpath "$tmpf" "$test_dir"; then
    test_pass
    rm -f "$tmpf"
else
    test_fail "tmp file missing or inside target: $tmpf"
fi

# ---------------------------------------------------------------------------
# Test 12: 符号链接死循环（symlink cycle: a→b→a）——不挂起、不逃逸
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test12"
mkdir -p "$test_dir"
touch "$test_dir/real-file.txt" "$test_dir/another.dat"
# 创建循环符号链接: link_a -> link_b, link_b -> link_a
ln -s "link_b" "$test_dir/link_a"
ln -s "link_a" "$test_dir/link_b"

test_start "symlink cycle (a→b→a): cleanup does not hang or escape"
# find -P (默认) 不跟随符号链接，不会死循环；timeout 作为最终安全护栏
if timeout 5 bash -c 'source "$0"; safe_cleanup_dir "$1"' "$SCRIPT_DIR/safe_cleanup.sh" "$test_dir" 2>/dev/null; then
    remaining=$(find "$test_dir" -mindepth 1 -maxdepth 1 | wc -l)
    if [ "$remaining" -eq 0 ]; then
        test_pass
    else
        test_fail "expected empty dir, got $remaining entries"
        ls -la "$test_dir"
    fi
else
    test_fail "cleanup hung or failed on symlink cycle"
fi

# ---------------------------------------------------------------------------
# Test 13: 自引用符号链接（dir/loop -> dir 自身）
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test13"
mkdir -p "$test_dir"
touch "$test_dir/data.txt"
# self-loop: test13/loop -> . (指向自己)
ln -s "." "$test_dir/loop"

test_start "self-referencing symlink (loop→.): cleanup completes without recursion"
if timeout 5 bash -c 'source "$0"; safe_cleanup_dir "$1"' "$SCRIPT_DIR/safe_cleanup.sh" "$test_dir" 2>/dev/null; then
    remaining=$(find "$test_dir" -mindepth 1 -maxdepth 1 | wc -l)
    if [ "$remaining" -eq 0 ]; then
        test_pass
    else
        test_fail "expected empty dir, got $remaining entries"
        ls -la "$test_dir"
    fi
else
    test_fail "cleanup hung on self-referencing symlink"
fi

# ---------------------------------------------------------------------------
# Test 14: 符号链接逃逸（symlink 指向外部目录）——删除链接而非目标
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test14"
outside_dir="${TEST_ROOT}/test14-outside-must-survive"
mkdir -p "$test_dir" "$outside_dir"
touch "$outside_dir/precious.txt"
# 创建指向外部目录的符号链接
ln -s "$outside_dir" "$test_dir/escape-link"
touch "$test_dir/normal-file.txt"

test_start "symlink escape (→outside dir): removes symlink, preserves target"
safe_cleanup_dir "$test_dir" 2>/dev/null
remaining=$(find "$test_dir" -mindepth 1 -maxdepth 1 | wc -l)
if [ "$remaining" -eq 0 ] && [ -f "$outside_dir/precious.txt" ]; then
    test_pass
else
    test_fail "symlink target was deleted or dir not empty"
    echo "  outside dir contents:"
    ls -la "$outside_dir" 2>/dev/null || echo "  (outside dir MISSING - escaped!)"
fi

# ---------------------------------------------------------------------------
# Test 15: 符号链接伪装——备份看似在域外实际在域内（realpath穿透检测）
# 场景：/root/inside-link -> /tmp/insidedir（symlink从外指向内）
#       备份路径 /root/inside-link/bk 看似在/root（域外），realpath解析到/tmp/insidedir/bk（域内）
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test15"          # 模拟 /tmp
outside_fake="${TEST_ROOT}/test15-outside-link" # 模拟 /root/inside-link
mkdir -p "$test_dir" "$outside_fake"
# outside_fake 是一个指向 test_dir 的符号链接——表面在域外，实际指向域内
rmdir "$outside_fake" 2>/dev/null || true
ln -s "$test_dir" "$outside_fake"

test_start "symlink disguise: backup appears outside but resolves inside → FAILS (catches trap!)"
# backup路径通过symlink看似在outside_fake（域外），但realpath解析后在test_dir（域内）
fake_backup="${outside_fake}/fake-backup"
if safe_assert_isolated "$fake_backup" "$test_dir" 2>/dev/null; then
    test_fail "should FAIL! realpath reveals backup is actually inside target"
else
    test_pass
fi

# ---------------------------------------------------------------------------
# Test 16: 符号链接正例——备份看似在域内实际在域外（realpath不误报）
# 场景：/tmp/outside-link -> /root/realbackup（symlink从内指向外）
#       备份路径 /tmp/outside-link/bk 看似在/tmp（域内），realpath解析到/root/realbackup/bk（域外）
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test16"          # 模拟 /tmp
real_outside="${TEST_ROOT}/test16-real-outside" # 模拟 /root/realbackup
mkdir -p "$test_dir" "$real_outside"
# test_dir/link 指向 real_outside——看似在域内，实际指向域外
ln -s "$real_outside" "$test_dir/outside-link"

test_start "symlink disguise: backup appears inside but resolves outside → passes"
real_backup="${test_dir}/outside-link/real-bk"
# 先创建备份文件（确保路径存在）
mkdir -p "$real_backup"
if safe_assert_isolated "$real_backup" "$test_dir" 2>/dev/null; then
    test_pass
else
    test_fail "should PASS! realpath resolves backup outside target"
fi
rm -rf "$real_backup"

# ---------------------------------------------------------------------------
# Test 17: safe_cleanup_dir 白名单保留在symlink场景下正常工作
# ---------------------------------------------------------------------------
test_dir="${TEST_ROOT}/test17"
mkdir -p "$test_dir"
touch "$test_dir/keep.txt" "$test_dir/delete.txt"
# 增加一个干扰symlink
ln -s "/etc/hostname" "$test_dir/link-to-outside"

test_start "safe_cleanup_dir: preserve works alongside symlinks"
safe_cleanup_dir "$test_dir" "$test_dir/keep.txt" 2>/dev/null
if [ -f "$test_dir/keep.txt" ] && [ ! -f "$test_dir/delete.txt" ] && [ ! -L "$test_dir/link-to-outside" ]; then
    test_pass
else
    test_fail "preserve/symlink handling failed"
    ls -la "$test_dir"
fi

# ---------------------------------------------------------------------------
# 结果汇总
# ---------------------------------------------------------------------------
echo ""
echo "========================================"
echo " 测试结果汇总"
echo "========================================"
echo "  PASS: $PASS"
echo "  FAIL: $FAIL"
echo "  TOTAL: $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "✅ 所有测试通过！"
    exit 0
else
    echo "❌ 有 $FAIL 个测试失败"
    exit 1
fi
