---
id: "lib-api-powershell"
title: "lib.powershell — PowerShell脚本编码工具"
source: "lib/api_docs.py#powershell"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/10-powershell.toml"
---

# lib.powershell — PowerShell脚本编码工具

Windows PowerShell 5.x 要求 .ps1 脚本使用 UTF-8 BOM + CRLF 换行，否则含中文时可能报语法错误。本模块提供写入、验证、修复能力。

| 函数 | 签名 | 说明 |
|---------|------|------|
| `write_ps1_script` | `(file_path, content, *, add_bom=True, newline='\r\n') -> Path` | 以PS兼容编码（UTF-8 BOM + CRLF）写入.ps1文件 |
| `verify_ps1_encoding` | `(file_path) -> tuple[bool, list[str]]` | 验证.ps1文件编码是否合规，返回(是否合规, 问题列表) |
| `fix_ps1_encoding` | `(file_path) -> tuple[bool, list[str]]` | 修复编码问题（添加BOM、统一CRLF），返回(是否修复, 变更列表) |

**示例**：

```python
from lib.powershell import write_ps1_script, verify_ps1_encoding

# 写入新的.ps1文件（自动BOM+CRLF，PS5/PS7均兼容）
write_ps1_script('scripts/build.ps1', '''
Write-Host 'Hello World'
$x = 1
''')

# 验证已有.ps1文件
ok, issues = verify_ps1_encoding('ci-check.ps1')
if not ok:
    print(f'编码问题: {issues}')
```

---

## 相关模式

- [共享库引力定律](../../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 误报过滤规则引擎](09-rules.md) | **[返回索引](../README.md)** | 下一章 → [进程探测与安全终止 →](11-process.md)
