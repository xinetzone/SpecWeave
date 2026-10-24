"""check-temp-lifecycle.py 治理入口豁免单元测试（TDD 红绿闭环）。

对应行为（spec「治理入口豁免」Scenario）：
    根级治理入口——README.md / AGENTS.md（须为文件）与 .agents/（须为目录）——
    属治理基础设施而非中间产物，不参与命名合规校验、保留期计算与自动清理。

覆盖场景：
    1. 治理入口豁免：三件套 + 一个合规任务目录 → 0 不合规、豁免 3 项、退出码 0
    2. 普通根级文件（record.md）仍判不合规，退出码 1
    3. 类型不符不豁免：.agents 为文件 / README.md 为目录 → 仍判不合规
    4. 仅含治理入口时退出码 0（total_items=0、豁免 3 项）
    5. --clean --yes 不删除治理入口，仅清理过期合规项
    6. --json 输出含 governance_exempt 字段

运行：pytest .agents/scripts/tests/test_check_temp_lifecycle.py -v
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
CHECKER = SCRIPTS_DIR / "check-temp-lifecycle.py"


def _run(root: Path, *extra: str) -> subprocess.CompletedProcess:
    """以子进程方式运行检查器（与真实调用路径一致）。"""
    return subprocess.run(
        [sys.executable, str(CHECKER), "--path", str(root), *extra],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(root),
        check=False,
    )


def _payload(root: Path) -> dict:
    proc = _run(root, "--json")
    return json.loads(proc.stdout)


def _make_temp(root: Path) -> Path:
    temp = root / ".temp"
    temp.mkdir()
    return temp


def _write_governance_triplet(temp: Path) -> None:
    (temp / "README.md").write_text("# readme\n", encoding="utf-8")
    (temp / "AGENTS.md").write_text("# agents\n", encoding="utf-8")
    agents_dir = temp / ".agents"
    agents_dir.mkdir()
    (agents_dir / "README.md").write_text("meta\n", encoding="utf-8")


def test_governance_entries_exempt(tmp_path):
    """场景1：治理入口不参与命名校验，合规任务目录照常通过。"""
    temp = _make_temp(tmp_path)
    _write_governance_triplet(temp)
    task = temp / "experiments" / "20261024-demo"
    task.mkdir(parents=True)
    (task / "a.py").write_text("x\n", encoding="utf-8")

    proc = _run(tmp_path, "--json")
    data = json.loads(proc.stdout)

    assert proc.returncode == 0
    assert data["exit_code"] == 0
    assert data["summary"]["non_compliant_count"] == 0
    assert data["summary"]["expired_count"] == 0
    assert data["total_items"] == 1
    assert len(data["governance_exempt"]) == 3
    names = {Path(p).name for p in data["governance_exempt"]}
    assert names == {"README.md", "AGENTS.md", ".agents"}


def test_plain_root_file_still_flagged(tmp_path):
    """场景2：普通根级文件不受豁免影响，仍判不合规。"""
    temp = _make_temp(tmp_path)
    (temp / "record.md").write_text("x\n", encoding="utf-8")

    proc = _run(tmp_path, "--json")
    data = json.loads(proc.stdout)

    assert proc.returncode == 1
    assert data["summary"]["non_compliant_count"] == 1
    assert data["non_compliant"][0]["name"] == "record.md"
    assert data["governance_exempt"] == []


def test_wrong_type_not_exempt(tmp_path):
    """场景3：类型不符不豁免——.agents 为文件、README.md 为目录。"""
    temp = _make_temp(tmp_path)
    (temp / ".agents").write_text("not a dir\n", encoding="utf-8")
    (temp / "README.md").mkdir()

    proc = _run(tmp_path, "--json")
    data = json.loads(proc.stdout)

    assert proc.returncode == 1
    flagged = {it["name"] for it in data["non_compliant"]}
    assert {".agents", "README.md"} <= flagged
    assert data["governance_exempt"] == []


def test_only_governance_entries_pass(tmp_path):
    """场景4：.temp 仅含治理入口时退出码 0、无待检查项。"""
    temp = _make_temp(tmp_path)
    _write_governance_triplet(temp)

    proc = _run(tmp_path, "--json")
    data = json.loads(proc.stdout)

    assert proc.returncode == 0
    assert data["total_items"] == 0
    assert data["summary"]["non_compliant_count"] == 0
    assert len(data["governance_exempt"]) == 3


def test_clean_never_deletes_governance(tmp_path):
    """场景5：--clean 只清过期合规项，绝不动治理入口。"""
    temp = _make_temp(tmp_path)
    _write_governance_triplet(temp)
    old = temp / "experiments" / "20200101-old"
    old.mkdir(parents=True)
    (old / "x.py").write_text("x\n", encoding="utf-8")

    proc = _run(tmp_path, "--clean", "--yes")

    assert proc.returncode == 0
    assert (temp / "README.md").exists()
    assert (temp / "AGENTS.md").exists()
    assert (temp / ".agents" / "README.md").exists()
    assert not old.exists()
