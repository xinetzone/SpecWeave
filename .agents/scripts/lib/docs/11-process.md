---
id: "lib-api-process"
title: "lib.process — 进程探测与安全终止"
source: "lib/api_docs.py#process"
x-toml-ref: "../../../../.meta/toml/.agents/scripts/lib/docs/11-process.toml"
---

# lib.process — 进程探测与安全终止

提供跨平台进程存活探测、cmdline 获取、关键字匹配与 kill 前身份校验能力，适合 stop/kill 类脚本复用。

| 函数/类 | 签名 | 说明 |
|---------|------|------|
| `CmdlineResult` | `dataclass` | 进程命令行探测结果（ok/cmdline/error/source） |
| `is_process_running` | `(pid: int) -> bool` | 判断 PID 是否仍然存活 |
| `get_process_cmdline` | `(pid: int) -> CmdlineResult` | 获取进程命令行，Windows 优先 WMIC，失败回退 CIM |
| `cmdline_matches` | `(cmdline: str, must_contain: list[str]) -> bool` | 校验命令行是否包含全部关键字 |
| `safe_kill` | `(pid: int, must_contain: list[str], *, kill: bool) -> tuple[bool, str]` | kill 前先校验进程身份；默认可用于 dry-run 校验 |

**示例**：

```python
from lib.process import safe_kill

# 先校验，不实际终止
ok, msg = safe_kill(pid=1234, must_contain=['python', 'monitor'], kill=False)
print(ok, msg)
```

---

## 相关模式

- [共享库引力定律](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/shared-lib-gravity.md)
- [临时sys.path修改](../../../docs/retrospective/patterns/code-patterns/temporary-syspath-modification.md)

---

← 上一章: [← 误报过滤规则引擎](09-rules.md) | **[返回索引](../README.md)** | 下一章 → [质量规则复用函数 →](12-quality-rules.md)
