---
id: "lib-api-cli"
title: "lib.cli — CLI 输出格式化"
source: "lib/api_docs.py#cli"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/02-cli.toml"
---

# lib.cli — CLI 输出格式化

| 函数 | 签名 | 说明 |
|------|------|------|
| `print_pass` | `(msg: str) -> None` | 打印绿色 [PASS] 通过信息 |
| `print_warn` | `(msg: str) -> None` | 打印黄色 [WARN] 警告信息 |
| `print_error` | `(msg: str) -> None` | 打印红色 [FAIL] 错误信息 |
| `print_header` | `(title: str, width: int = 60) -> None` | 打印等宽分隔标题行 |
| `print_summary` | `(pass_count: int, warn_count: int, error_count: int, width: int = 60) -> None` | 打印彩色检查摘要（通过/警告/错误） |
| `add_common_args` | `(parser: ArgumentParser) -> None` | 注册通用 CLI 参数（--path、--json） |

**示例**：

```python
from lib.cli import print_pass, print_warn, print_header, add_common_args
import argparse

parser = argparse.ArgumentParser(description='我的检查脚本')
add_common_args(parser)  # 自动添加 --path 和 --json
args = parser.parse_args()
print_header('开始检查')
print_pass('文件格式正确')
print_summary(pass_count=5, warn_count=1, error_count=0)
```

---

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 项目路径解析](01-project.md) | **[返回索引](../README.md)** | 下一章 → [Frontmatter 解析 →](03-frontmatter.md)
