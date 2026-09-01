---
id: "lib-api-constants"
title: "constants.py — 全局常量（scripts/ 根目录）"
source: "lib/api_docs.py#constants"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/14-constants.toml"
---

# constants.py — 全局常量（scripts/ 根目录）

位于 `.agents/scripts/constants.py`，全局共享常量模块，供所有脚本和 lib/ 模块引用。

导入方式：`from constants import EXCLUDED_DIRS, ANSI_GREEN, ...`

| 常量 | 类型 | 说明 |
|------|------|------|
| `ANSI_GREEN/ANSI_YELLOW/ANSI_RED/ANSI_CYAN/ANSI_RESET` | str | ANSI 颜色代码 |
| `EXCLUDED_DIRS` | set[str] | 文件扫描默认排除目录（.git/vendor/.venv/__pycache__/node_modules/.temp） |
| `REQUIRED_RULES` / `TEMP_PATHS` | list | .gitignore 必需规则与临时路径 |
| `LINK_CHECK_*` | - | check-links.py 默认参数（timeout/workers/user-agent等） |
| `VALID_TIERS` / `ROLE_EXCLUDED_FILES` | - | 角色权限校验常量 |
| `SPEC_MATCH_THRESHOLD` / `META_DOC_KEYWORDS` | - | Spec 一致性检查参数 |
| `SCAN_DIRS` / `TARGETS` / `MANUAL_DESCRIPTIONS` | - | 导航生成器配置 |

---

## 相关模式

- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 质量报告聚合与输出](13-quality-report.md) | **[返回索引](../README.md)** | 下一章 → [测试辅助工具库 →](15-testing.md)
