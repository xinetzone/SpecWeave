"""check-raci-compliance.py 单元测试。"""

import importlib.util
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

_spec = importlib.util.spec_from_file_location(
    "check_raci_compliance", SCRIPTS_DIR / "check-raci-compliance.py"
)
rac = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rac)


VALID_RACI = """# 测试文档

## RACI责任分配矩阵

| 测试流程核心活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 流程触发与协调 | **R/A** | C | I | C | I | I |
| 方案设计 | C | **R** | C | **A** | I | I |
| 代码实现 | I | C | **R** | **A** | I | I |
| 质量验收 | C | C | I | **R/A** | I | I |
| 重大架构审批 | R | C | I | C | I | **A** |
"""

DOUBLE_A_RACI = """# 双A违规

| 活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 跨模块审批 | C | C | C | **A** | I | **A** |
"""

MISSING_A_RACI = """# 缺A违规

| 活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 某项活动 | C | C | **R** | C | I | I |
"""

UNBOLDED_A_RACI = """# A未加粗违规

| 活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 某项活动 | C | C | R | A | I | I |
"""

DEV_SELF_APPROVE_RACI = """# developer自审批违规

| 活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 代码实现与提交 | I | C | **R/A** | I | I | I |
"""

EXEC_NO_REV_A_RACI = """# 执行类reviewer非A

| 活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 代码实现 | I | C | **R** | C | I | **A** |
"""

COFOUNDER_OVERUSE_RACI = """# co-founder过度审批

| 活动 | orchestrator | architect | developer | reviewer | tester | co-founder |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| 日常流程协调 | **A** | I | I | C | I | I |
| 文档格式调整 | I | I | C | C | I | **A** |
"""

MISSING_ROLES_RACI = """# 缺少角色列

| 活动 | orchestrator | developer | reviewer |
|:---|:---:|:---:|:---:|
| 某项活动 | **R/A** | I | C |
"""


def _write_tmp(content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8")
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


class TestParseRaciTable:
    def test_parse_valid_table(self):
        tables = rac.parse_raci_table(VALID_RACI)
        assert len(tables) == 1
        t = tables[0]
        assert len(t.role_columns) == 6
        assert set(t.role_columns.keys()) == {"orchestrator", "architect", "developer", "reviewer", "tester", "co-founder"}
        assert len(t.rows) == 5

    def test_skip_code_block_tables(self):
        content = """# 文档

```markdown
| 活动 | orchestrator | developer | reviewer |
|:---|:---:|:---:|:---:|
| 示例 | **A** | R | C |
```

| 活动 | orchestrator | developer | reviewer |
|:---|:---:|:---:|:---:|
| 真实行 | **R/A** | I | C |
"""
        tables = rac.parse_raci_table(content)
        assert len(tables) == 1
        assert len(tables[0].rows) == 1

    def test_skip_ellipsis_rows(self):
        content = """| 活动 | orchestrator | developer | reviewer |
|:---|:---:|:---:|:---:|
| 活动1 | **R/A** | I | C |
| ... | ... | ... | ... |
| 活动2 | C | **R** | **A** |
"""
        tables = rac.parse_raci_table(content)
        assert len(tables) == 1
        assert len(tables[0].rows) == 2

    def test_no_raci_table(self):
        tables = rac.parse_raci_table("# 普通文档\n\n没有表格。")
        assert len(tables) == 0


class TestAUniqueness:
    def test_valid_single_a(self):
        tables = rac.parse_raci_table(VALID_RACI)
        results = rac.check_a_uniqueness(tables[0])
        errors = [r for r in results if not r.passed]
        assert len(errors) == 0

    def test_double_a_detected(self):
        tables = rac.parse_raci_table(DOUBLE_A_RACI)
        results = rac.check_a_uniqueness(tables[0])
        errors = [r for r in results if not r.passed and "双A" in r.message or ("存在2个A" in r.message)]
        assert any("存在2个A" in r.message for r in results if not r.passed)

    def test_missing_a_detected(self):
        tables = rac.parse_raci_table(MISSING_A_RACI)
        results = rac.check_a_uniqueness(tables[0])
        assert any("缺少A" in r.message for r in results if not r.passed)

    def test_unbolded_a_detected(self):
        tables = rac.parse_raci_table(UNBOLDED_A_RACI)
        results = rac.check_a_uniqueness(tables[0])
        unbolded = [r for r in results if not r.passed and "未加粗" in r.message]
        assert len(unbolded) >= 1


class TestRASeparation:
    def test_valid_separation(self):
        tables = rac.parse_raci_table(VALID_RACI)
        results = rac.check_r_a_separation(tables[0])
        errors = [r for r in results if not r.passed and r.severity == "error"]
        assert len(errors) == 0

    def test_dev_self_approve_detected(self):
        tables = rac.parse_raci_table(DEV_SELF_APPROVE_RACI)
        results = rac.check_r_a_separation(tables[0])
        assert any("developer同时为R和A" in r.message for r in results if not r.passed)

    def test_cofounder_overuse_warn(self):
        tables = rac.parse_raci_table(COFOUNDER_OVERUSE_RACI)
        results = rac.check_r_a_separation(tables[0])
        warnings = [r for r in results if not r.passed and "co-founder" in r.message]
        assert len(warnings) >= 1


class TestRoleColumns:
    def test_all_roles_present(self):
        tables = rac.parse_raci_table(VALID_RACI)
        results = rac.check_role_columns(tables[0])
        assert all(r.passed for r in results)

    def test_missing_roles_warn(self):
        tables = rac.parse_raci_table(MISSING_ROLES_RACI)
        results = rac.check_role_columns(tables[0])
        assert any("缺少标准角色列" in r.message for r in results if not r.passed)


class TestCheckFile:
    def test_valid_file_scores_100(self):
        f = _write_tmp(VALID_RACI)
        try:
            report = rac.check_file(f, f.parent)
            assert report.raci_tables_found == 1
            assert report.score == 100
            assert not report.errors
        finally:
            f.unlink()

    def test_double_a_file_fails(self):
        f = _write_tmp(DOUBLE_A_RACI)
        try:
            report = rac.check_file(f, f.parent)
            assert report.errors
        finally:
            f.unlink()

    def test_no_raci_file(self):
        f = _write_tmp("# 普通文档\n\n没有RACI矩阵。")
        try:
            report = rac.check_file(f, f.parent)
            assert report.raci_tables_found == 0
            assert report.score == 100
        finally:
            f.unlink()
