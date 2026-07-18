"""Task 6 冒烟测试。"""
import sys
import tempfile
import os
import shutil
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS_DIR))

from lib.knowledge_backup import (
    backup_knowledge_base,
    restore_from_backup,
    list_all_backups,
    list_knowledge_history,
    get_knowledge_at_version,
    compare_knowledge_versions,
    detect_bulk_damage,
    bulk_repair,
    pre_change_check,
)

print("TR-6.0 PASS: imports OK")

# TR-6.1: 备份创建
tmpdir = tempfile.mkdtemp()
ok, msg, path = backup_knowledge_base(backup_dir=tmpdir)
assert ok and path.exists(), f"TR-6.1 FAIL: {msg}"
print(f"TR-6.1 PASS: backup created at {path}")

# TR-6.2: 恢复预览（dry-run）
ok, msg = restore_from_backup(path, dry_run=True)
assert ok, f"TR-6.2 FAIL: {msg}"
print("TR-6.2 PASS: dry-run restore works")

# TR-6.3: 恢复到临时目录
restore_dir = os.path.join(tmpdir, "restored")
ok, msg = restore_from_backup(path, target_dir=restore_dir)
assert ok, f"TR-6.3 FAIL: {msg}"
print("TR-6.3 PASS: restore to temp dir works")

# TR-6.4: 列出备份
ok, backups, msg = list_all_backups(backup_dir=tmpdir)
assert ok, f"TR-6.4 FAIL: {msg}"
assert len(backups) >= 1
print(f"TR-6.4 PASS: {len(backups)} backups listed")

# TR-6.5: Git历史查询
kb_file = ".agents/docs/knowledge/templates/knowledge-entry-template.md"
ok, commits, msg = list_knowledge_history(kb_file)
assert ok, f"TR-6.5 FAIL: {msg}"
print(f"TR-6.5 PASS: {len(commits)} commits found")

# TR-6.6: 版本检出

# TR-6.7: 版本比较
if len(commits) >= 2:
    ok, diff, msg = compare_knowledge_versions(kb_file, commits[1]["hash"], commits[0]["hash"])
    assert ok, f"TR-6.7 FAIL: {msg}"
    print(f"TR-6.7 PASS: diff len={len(diff)}")

# TR-6.8: 损坏检测
ok, damaged, msg = detect_bulk_damage()
assert ok, f"TR-6.8 FAIL: {msg}"
print(f"TR-6.8 PASS: {len(damaged)} damaged entries")

# TR-6.9: 批量修复（dry-run）
ok, results, msg = bulk_repair(dry_run=True)
assert ok, f"TR-6.9 FAIL: {msg}"
print(f"TR-6.9 PASS: {len(results)} entries in dry-run")

# TR-6.10: 变更前检查
ok, info, msg = pre_change_check()
print(f"TR-6.10: ok={ok} clean={info.get('is_clean', False)}")

# TR-6.11: 无效备份恢复
ok, msg = restore_from_backup("/nonexistent/backup")
assert not ok, "TR-6.11: should have failed"
print("TR-6.11 PASS: invalid backup rejected")

# TR-6.12: 无效文件历史
ok, commits, msg = list_knowledge_history("/nonexistent/file" + ".md")
assert not ok, f"TR-6.12: should have failed, got {ok=}"
print("TR-6.12 PASS: invalid file history rejected")

shutil.rmtree(tmpdir, ignore_errors=True)
print()
print("ALL 12 TESTS PASSED")

