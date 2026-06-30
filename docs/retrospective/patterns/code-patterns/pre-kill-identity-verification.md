+++
id = "pre-kill-identity-verification"
domain = "code"
layer = "code"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "detailed"
source = "docs/retrospective/reports/competitive-analysis/retrospective-tuyaopen-dev-skills-learning-20260630/insight-extraction.md"

[bindings]
rules = []
references = []
skills = []
related_patterns = ["session-file-externalization", "script-json-output-contract"]
+++

# 停止前身份校验：避免误杀进程

## 模式概述

当脚本需要停止后台进程（kill/stop/taskkill）时，单纯依据 PID 会带来两类风险：

- PID 被复用导致误杀无关进程
- session file 被污染或写错 PID 导致误杀

本模式在执行 kill 前增加“进程身份校验”：只有当 PID 的 cmdline 能证明其属于目标进程时，才允许停止。

## 触发条件

- 脚本具备 start/stop 能力并会保存 PID
- stop 操作具备破坏性（终止进程、释放端口、删除文件等）
- 运行环境存在 PID 复用风险（长时间运行、频繁启停、共享机器）

## 校验策略

### Linux/macOS

- 读取 `/proc/<pid>/cmdline`（若不可用则拒绝 kill）
- 校验 cmdline 同时包含“目标脚本标识”和“关键子命令”

### Windows

可选方案（按环境可用性择一）：

- `wmic process where ProcessId=<pid> get CommandLine`
- PowerShell `Get-CimInstance Win32_Process -Filter "ProcessId=<pid>"`

## 校验规则

给定 `cmdline` 与 `must_contain` 关键字集合：

- 任一关键字缺失则拒绝 kill
- 无法读取 cmdline 则拒绝 kill

## 最小实现伪代码

```text
if not running(pid): return
cmdline = read_cmdline(pid)
if cmdline is None: return
if not all(k in cmdline for k in must_contain): return
kill(pid)
```

## 失败处理原则

- “宁可不杀，也不误杀”
- 拒绝 kill 时返回明确原因，要求用户手动确认或重新 start 生成新会话

## 验证清单

- [ ] PID 不是目标进程时 stop 不会终止它
- [ ] cmdline 读取失败时 stop 会拒绝执行
- [ ] 成功 stop 后会清理 session file（若结合 session-file-externalization）

