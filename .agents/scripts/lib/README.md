---
id: "lib-api"
title: ".agents/scripts/lib/ API 参考"
source: "lib/api_docs.py"
x-toml-ref: "../../../.meta/toml/.agents/scripts/lib/README.toml"
---

# .agents/scripts/lib/ API 参考

> 本文档由 `lib/api_docs.py` 自动生成，描述共享库所有公开模块和函数。

## 文档导航

| 文档 | 模块 | 说明 |
|------|------|------|
| [docs/01-project.md](docs/01-project.md) | `lib.project` | 项目路径解析 |
| [docs/02-cli.md](docs/02-cli.md) | `lib.cli` | CLI 输出格式化 |
| [docs/03-frontmatter.md](docs/03-frontmatter.md) | `lib.frontmatter` | Frontmatter 解析 |
| [docs/04-markdown.md](docs/04-markdown.md) | `lib.markdown` | Markdown 文件处理 |
| [docs/05-link-fixer.md](docs/05-link-fixer.md) | `lib.link_fixer` | 链接修复 |
| [docs/06-patterns.md](docs/06-patterns.md) | `lib.patterns` | 模式成熟度分析 |
| [docs/07-spec.md](docs/07-spec.md) | `lib.spec` | Spec 文档处理 |
| [docs/08-checks.md](docs/08-checks.md) | `lib.checks` | 检查器框架 |
| [docs/09-rules.md](docs/09-rules.md) | `lib.rules` | 误报过滤规则引擎 |
| [docs/11-process.md](docs/11-process.md) | `lib.process` | 进程探测与安全终止 |
| [docs/12-quality-rules.md](docs/12-quality-rules.md) | `lib.quality_rules` | 质量规则复用函数 |
| [docs/13-quality-report.md](docs/13-quality-report.md) | `lib.quality_report` | 质量报告聚合与输出 |
| [docs/14-constants.md](docs/14-constants.md) | `constants.py` | 全局常量（scripts/ 根目录） |
| [docs/15-testing.md](docs/15-testing.md) | `lib.testing` | 测试辅助工具库（多智能体边界场景模板） |

## 文档生成

- **拆分模式（当前使用）**：索引页 + 15个模块分片文档，位于 `lib/docs/` 目录
- **重新生成**：运行 `python .agents/scripts/lib/api_docs.py --split`
- **单文件预览**：运行 `python .agents/scripts/lib/api_docs.py` 输出到 stdout

---

## 新增脚本开发流程

新建 `.agents/scripts/` 下的脚本前，请遵循以下流程：

1. **先查本文件**，确认 lib/ 是否已有可复用的函数
2. **优先使用共享函数**，避免重复实现相同逻辑
3. 如确需新功能，先考虑是否应提取到 lib/ 供其他脚本复用
4. 脚本头部添加 sys.path 设置：
```python
import sys
from pathlib import Path
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
```
5. 使用 `add_common_args(parser)` 注册通用参数（--path/--json）
6. 使用 `print_pass/print_warn/print_error/print_summary` 输出检查结果
7. 完成后运行 `python check-duplication.py` 检查是否引入新的重复代码

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)