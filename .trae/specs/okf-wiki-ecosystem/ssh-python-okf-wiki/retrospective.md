# SSH Python OKF Wiki 全局验证复盘

> 日期：2026-08-23
> 范围：`bundles/networking/` 下 6 个知识束（paramiko/fabric/asyncssh/pexpect/netmiko/scrapli）
> 验证类型：最终全局验证（7 项检查 + 修复闭环）

## 一、产出统计

### 文档总量

| 指标 | 数量 |
|------|------|
| `.md` 文件总数 | 122 |
| 概念文档（concepts，不含 index） | 60 |
| 示例文档（examples，不含 index） | 25 |
| 信源登记（references，不含 index） | 6 |
| 内容文档合计 | 91 |
| 索引文件（各层 index.md） | 25 |
| 生成日志（log.md） | 6 |

### 各束明细

| 知识束 | 版本 | 概念 | 示例 | 信源 | 事实数 | 内容文档合计 |
|--------|------|------|------|------|--------|-------------|
| paramiko | 5.0.0 | 11 | 5 | 1 | 123 | 17 |
| fabric | 4.0.0 | 9 | 4 | 1 | 92 | 14 |
| asyncssh | 2.24.0 | 12 | 4 | 1 | 180 | 17 |
| pexpect | 4.9.0 | 9 | 4 | 1 | 77 | 14 |
| netmiko | 4.7.0 | 10 | 4 | 1 | 120 | 15 |
| scrapli | 2.x | 9 | 4 | 1 | 133 | 14 |
| **合计** | — | **60** | **25** | **6** | **725** | **91** |

## 二、七项检查结果

| # | 检查项 | 结果 | 说明 |
|---|--------|------|------|
| 1 | Frontmatter type 字段 | ✅ PASS | 91 个内容文档全部包含有效的 `type: Concept/Example/Reference` |
| 2 | 链接完整性 | ✅ PASS（修复后） | 初始发现 11 个断链，全部修复 |
| 3 | 跨束链接 | ✅ PASS | fabric→paramiko、netmiko→paramiko、scrapli→paramiko+asyncssh、fabric→pyinvoke 均存在 |
| 4 | 日志文件 | ✅ PASS | 6 个 log.md 均存在且有实质内容 |
| 5 | 文档数量 | ✅ PASS | concepts=60(≥55)、examples=25(≥24)、references=6(≥6) |
| 6 | 无占位符 | ✅ PASS | 无真实 TODO/FIXME/TBD/占位内容（误报见下） |
| 7 | OKF 版本 | ✅ PASS | 6 个束根 index.md 均包含 `okf_version: "0.2"` |

## 三、发现的问题与修复

### 3.1 断链修复（11 处，涉及 9 个文件）

**根因分析**：两类路径错误

1. **跨组链接路径深度不足**（8 处）：fabric 子目录（concepts/、references/）中引用 `tooling/pyinvoke` 时使用了 `../../tooling/`，但从 `networking/fabric/concepts/` 出发，`../../` 仅到达 `networking/`，而 `tooling/` 位于 `bundles/tooling/`（与 `networking/` 同级），需要三层 `../../../`。
   - 修复：`../../tooling/pyinvoke/concepts/XX.md` → `../../../tooling/pyinvoke/index.md`
   - 涉及文件：`00-introduction.md`、`01-getting-started.md`、`02-connection.md`、`03-configuration.md`、`04-command-execution.md`、`08-advanced-patterns.md`、`references/fabric-source.md`

2. **束根 index.md 路径过度**（2 处）：`fabric/index.md` 和 `netmiko/index.md` 中引用 paramiko 时使用了 `../../paramiko/`，但从束根目录出发 `../` 即到达 `networking/`，多了一层 `../` 导致解析到 `bundles/paramiko/`（不存在）。
   - 修复：`../../paramiko/concepts/00-introduction.md` → `../paramiko/concepts/00-introduction.md`
   - 涉及文件：`fabric/index.md`、`netmiko/index.md`

3. **pyinvoke 目标文件不存在**（伴随修复）：pyinvoke 束当前仅有 `index.md` 和 `log.md`，无 `concepts/` 子目录。所有指向具体概念文件（如 `03-context-object.md`）的链接统一修正为 `index.md`。
   - `fabric/index.md` 中的 pyinvoke 链接路径深度正确（`../../tooling/pyinvoke/` 从束根出发可到达 `bundles/tooling/pyinvoke/`），仅修正目标文件名。

### 3.2 占位符误报澄清

初次扫描报告 5 处占位符，经逐一核查均为误报：

| 文件 | 匹配词 | 实际情况 |
|------|--------|---------|
| `fabric/concepts/02-connection.md:182` | "占位" | "占位符"是 SSH ProxyCommand 中 `%h`/`%p` 令牌替换的技术术语 |
| `fabric/concepts/07-tunnels.md:235` | "占位" | 同上，描述 SSH config 令牌解析 |
| `fabric/concepts/08-advanced-patterns.md:64` | "TODO" | `NothingToDo` 异常类名的子串匹配 |
| `fabric/log.md:90` | "TODO" | 同上，`NothingToDo` 异常验证表 |
| `fabric/references/fabric-source.md:99` | "TODO" | 同上，异常体系描述 |

改进：验证脚本已更新为使用词边界正则 `\bTODO\b` 和否定先行断言 `占位(?!符)` 消除技术术语误报。

### 3.3 fabric/log.md 验证结论修正

fabric/log.md 原文声称"跨束引用 pyinvoke 使用相对路径 `../../tooling/pyinvoke/concepts/` 格式"和"所有引用目标文件均存在"，经验证两点均不准确。已修正为实际路径 `../../../tooling/pyinvoke/index.md` 并追加修正记录。

## 四、各束虚构 API 拦截记录

### paramiko（3 处修复）

| # | 问题 | 修复 |
|---|------|------|
| 1 | `NoValidConnectionsError` 引用路径错误（误用 `paramiko.NoValidConnectionsError`） | 修正为 `paramiko.ssh_exception.NoValidConnectionsError` |
| 2 | `examples/interactive-shell.md` 非阻塞读取示例使用 `socket.timeout` 但未导入 socket | 补充 `import socket` |
| 3 | 事实 F-105 含因果推断词"用于" | 修改为客观描述 |

额外拦截：任务简报列出的 `DSSKey` 类在 paramiko v5.0.0 中已移除，文档未引用；`request_pty` 实际方法名为 `get_pty`，`file` 实际为 `open`，文档均使用正确名称。

### fabric（2 处拦截，0 处泄露）

任务简报验证清单中列出的 `create_sftp_conn` 和 `from_context` 方法在 fabric v4.0.0 源码中不存在：
- 实际 SFTP 访问方法为 `sftp()`（connection.py:880），文档使用正确名称
- `from_context` 不存在，文档未引用
- 文档生成过程中成功拦截，无虚构 API 泄露

### asyncssh（5 处修复）

| # | 问题 | 修复 |
|---|------|------|
| 1 | `asyncssh.sp()` 拼写错误 | 修正为 `asyncssh.scp()`（scp.py:931） |
| 2 | `asyncssh.run_scp_server()` 未在 `__init__.py` 导出 | 修正为 `from asyncssh.scp import run_scp_server` |
| 3 | `process.create_sftp_server()` 方法不存在 | 重写示例，改用 `sftp_factory=True, allow_scp=True` 参数 |
| 4 | 四个不存在的服务端选项（`permit_root_login`、`max_sessions`、`max_startups`、`allow_agent_forwarding`） | 替换为实际存在的 `keepalive_count_max`、`rekey_seconds`、`agent_forwarding`、`sftp_factory`、`allow_scp` |
| 5 | 规划中的三个不存在转发权限参数（`permit_remote_port_forwards` 等） | 最终文档未使用，改用 SSHServer 回调控制 |

### pexpect（0 处虚构，5 项边界确认）

无虚构 API。额外确认：
- `spawnu`/`runu` 为弃用函数，文档明确标注
- `PopenSpawn` 不支持 PTY 专属方法（interact/setwinsize 等），能力矩阵如实反映
- `fdspawn.terminate()` 在 Windows 上抛出异常而非静默无操作
- `pxssh.login()` 完整签名包含 `ssh_tunnels`、`sync_original_prompt` 等额外参数

### netmiko

V 阶段执行了 Grep 验证，所有类名和方法名均在源码中确认存在。日志记录较简略，未列出逐项验证表。

### scrapli

V 阶段执行了 Grep 验证，所有类名和方法名均在源码中确认存在。日志记录较简略。

### 跨束汇总

| 知识束 | 虚构 API 修复数 | 拦截但未泄露数 |
|--------|----------------|---------------|
| paramiko | 3 | 3（DSSKey、request_pty、file） |
| fabric | 0 | 2（create_sftp_conn、from_context） |
| asyncssh | 5 | 3（规划中未使用的参数） |
| pexpect | 0 | 0 |
| netmiko | 0 | 0 |
| scrapli | 0 | 0 |
| **合计** | **8** | **8** |

## 五、经验教训

### 5.1 相对路径深度需根据文件位置区分

同组跨束链接（`networking/A/` → `networking/B/`）和跨组链接（`networking/A/` → `tooling/B/`）的路径深度不同：

| 文件位置 | 同组跨束（如→paramiko） | 跨组（如→tooling/pyinvoke） |
|---------|------------------------|---------------------------|
| 束根 `index.md` | `../paramiko/` | `../../tooling/pyinvoke/` |
| 子目录 `concepts/` | `../../paramiko/` | `../../../tooling/pyinvoke/` |

教训：生成链接时不能假设统一的 `../../` 前缀，必须根据当前文件深度和目标层级计算。建议在 OKF 规范中增加路径深度对照表。

### 5.2 跨束链接目标必须验证存在性

fabric 文档引用了 pyinvoke 的 7 个具体概念文件（`00-introduction.md`、`02-task-basics.md`、`03-context-object.md` 等），但 pyinvoke 束当前仅有 `index.md`。V 阶段的链接检查仅验证了路径格式，未验证目标文件实际存在，导致断链在最终全局验证中才暴露。

教训：V 阶段的链接检查应自动化验证目标文件存在性，而非人工确认"格式正确"。

### 5.3 占位符扫描需要词边界感知

简单的子串匹配会将 `NothingToDo`（异常类名）匹配为 TODO，将"占位符"（技术术语）匹配为"占位"。在 Python SSH 领域，`NothingToDo` 是 fabric 的合法异常类，"占位符"是 SSH config 令牌替换的标准术语。

教训：占位符扫描应使用词边界正则（`\bTODO\b`）和上下文感知（`占位(?!符)`），避免技术术语误报消耗审查精力。

### 5.4 各束 V 阶段日志详细度不均衡

paramiko 和 asyncssh 的日志包含完整的类名/方法名验证表（含源码行号），fabric 也有详细验证记录；但 netmiko 和 scrapli 的日志仅一句话概括"Grep 验证所有类名和方法名"，缺乏可审计的逐项验证证据。

教训：V 阶段日志应遵循统一模板，至少列出验证的 API 清单和源码位置，确保可审计性。

### 5.5 任务简报验证清单可能包含过时 API

多个束的任务简报中列出了在目标版本中已移除或不存在的 API（paramiko 的 DSSKey、fabric 的 create_sftp_conn/from_context、asyncssh 的多个选项参数）。R 阶段的事实采集成功识别了这些差异，但说明简报本身需要与源码版本同步更新。

教训：任务简报应标注其基于的库版本，R 阶段必须以实际源码为准而非简报清单。

## 六、验证方法论备注

本次全局验证使用自动化 Python 脚本执行 7 项检查，覆盖 122 个 `.md` 文件。脚本特点：
- Frontmatter 解析：YAML `---` 分隔符 + 字段提取
- 链接验证：正则提取 Markdown 链接，按 `/`（束根相对）和 `../../`（跨束）分类解析，`Path.resolve()` 验证存在性
- 占位符检测：词边界正则 + 否定先行断言，消除技术术语误报
- 修复后二次验证：确保所有检查项 PASS
