---
id: "rules-detection-reporting-06-tool-integration"
title: "检测与报告机制：工具集成建议"
source: "rules/detection-and-reporting.md#工具集成建议"
x-toml-ref: "../../../.meta/toml/.agents/rules/detection-and-reporting/06-tool-integration.toml"
---
# 检测与报告机制：工具集成建议

## 与现有 CI 脚本集成

项目的 CI 检查入口脚本（`.agents/scripts/ci-check.ps1` 与 `ci-check.sh`）已承担多项质量检查职责。硬编码检测脚本应作为其中一项新增步骤接入，建议插入顺序为"链接有效性检查之后、规格一致性检查之前"。

**集成示例（Shell 片段）**：

```bash
#!/usr/bin/env bash
# 在 ci-check.sh 中新增硬编码检测步骤

echo -e "\033[33m[N/5] 硬编码检测...\033[0m"
python "$ROOT/.agents/scripts/check-hardcode.py" --format json --level error
if [ $? -ne 0 ]; then
    echo -e "\033[31m错误: 存在 ERROR 级硬编码，请修复后重新提交\033[0m"
    exit 1
fi
echo -e "\033[32m  通过\033[0m"
```

**集成示例（PowerShell 片段）**：

```powershell
# 在 ci-check.ps1 中新增硬编码检测步骤

Write-Host "[N/5] 硬编码检测..." -ForegroundColor Yellow
python "$root\.agents\scripts\check-hardcode.py" --format json --level error
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误: 存在 ERROR 级硬编码，请修复后重新提交" -ForegroundColor Red
    exit 1
}
Write-Host "  通过" -ForegroundColor Green
```

## 推荐的外部工具

以下成熟工具提供了硬编码检测的相关规则，建议按项目技术栈有选择地集成：

| 工具 | 适用语言 | 相关规则/插件 | 集成方式 |
|---|---|---|---|
| **ruff** | Python | `S105`（硬编码密码）、`S106`（硬编码密钥）、`PLR2004`（魔法数字） | `ruff check --select S105,S106,PLR2004` |
| **bandit** | Python | `B105`（硬编码密码字符串）、`B106`（硬编码函数调用）、`B107`（硬编码默认参数） | `bandit -r src/ -c bandit.yaml` |
| **semgrep** | 多语言 | 社区规则 `generic.secrets.*`、`python.hardcoded.*`，支持自定义规则 | `semgrep --config auto --config .agents/rules/semgrep/` |
| **detect-secrets** | 多语言 | 基于熵值检测的密钥扫描引擎 | `detect-secrets scan --all-files` |
| **ESLint** | JavaScript/TypeScript | `no-magic-numbers`、`no-restricted-syntax`（自定义模式） | 配置 `.eslintrc.js` 中对应规则 |
| **gitleaks** | 多语言 | Git 历史中的密钥与凭证泄漏检测 | `gitleaks detect --source .` |

## 自定义扫描脚本模板

建议在 `.agents/scripts/` 目录下创建 `check-hardcode.py` 作为硬编码检测的统一入口脚本，其核心结构如下：

```python
#!/usr/bin/env python3
"""硬编码检测脚本
用途：扫描指定文件或目录中的硬编码模式，按规则集分级输出结果。
用法：python check-hardcode.py [--path DIR] [--format json|text] [--level error|warning|info]
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterator


def load_rules(rules_dir: Path) -> list[dict]:
    """从 .agents/rules/ 目录加载硬编码检测规则集。"""
    # 规则加载逻辑
    ...


def scan_file(file_path: Path, rules: list[dict]) -> Iterator[dict]:
    """对单个文件执行规则集扫描，逐条产出命中的检测结果。"""
    # 文件扫描逻辑
    ...


def format_output(results: list[dict], fmt: str) -> str:
    """按指定格式（JSON / text）格式化扫描结果。"""
    ...


def main():
    parser = argparse.ArgumentParser(description="硬编码检测脚本")
    parser.add_argument("--path", default=".", help="扫描目标路径")
    parser.add_argument("--format", choices=["json", "text"], default="text")
    parser.add_argument("--level", choices=["error", "warning", "info"], default="warning")
    args = parser.parse_args()

    rules = load_rules(Path(".agents/rules"))
    results = []

    target = Path(args.path)
    files = target.rglob("*.py") if target.is_dir() else [target]

    for f in files:
        results.extend(scan_file(f, rules))

    # 按级别过滤
    filtered = [r for r in results if r["level"] == args.level.upper() or args.level == "warning"]

    print(format_output(filtered, args.format))

    # 存在 ERROR 级结果时返回非零退出码
    if any(r["level"] == "ERROR" for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## pre-commit 钩子配置

推荐使用 `pre-commit` 框架将硬编码检测挂载至提交前阶段：

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: hardcode-check
        name: 硬编码检测
        entry: python .agents/scripts/check-hardcode.py --level error
        language: python
        files: \.(py|js|ts|java|go|rs)$
        stages: [pre-commit]
        pass_filenames: true
```
---
## 相关模式

- [多信号检测](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/multi-signal-detection.md)
- [周期检查缓存](../../../docs/retrospective/patterns/code-patterns/periodic-check-caching.md)
---
← 上一章: [05 定期报告规范](05-periodic-reporting.md) | **[返回索引](../detection-and-reporting.md)** | 下一章 → [07 角色职责与使用约束](07-roles-constraints.md)
