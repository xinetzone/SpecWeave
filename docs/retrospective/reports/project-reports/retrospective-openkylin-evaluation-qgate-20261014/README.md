---
type: Report
id: "retrospective-openkylin-evaluation-qgate-20261014"
version: "1.0.0"
source: "openKylin 评估里程碑全流程（初始评估 + Q 门首轮公开信源核验 + 二轮功能级实测，2026-10-14 单日；4 个本地提交 6af66bce1/b807d921e/0bdecaa59/fc7e89377）"
session: "sc-20261014-openkylin-milestone-retro"
method: "七概念方法论编排（场景1 里程碑复盘：R→I→V→E→A→C，depth=standard）"
tags: [milestone-retrospective, openkylin, q-gate, evidence-grade, zero-footprint-forensics, methodology]
---

# 里程碑复盘：openKylin 评估与 Q 门双轮核验

> 复盘日期：2026-10-14 ｜ 周期：单日（4 个提交时点 12:03 / 12:04 / 14:44 / 15:41） ｜ 方法论：七概念 R→I→V→E→A→C
>
> 复盘对象：openKylin 竞品评估报告的**生产与复核全过程**（元层复盘），不是对 openKylin 结论本身的二次评估。评估内容见[原报告](../../competitive-analysis/retrospective-openkylin-evaluation-20261014/README.md)与[附录 C 核验记录](../../competitive-analysis/retrospective-openkylin-evaluation-20261014/verification-q1-q8-20261014.md)。

## 一、里程碑时间线

| 时点 | 事件 | 产出 |
|---|---|---|
| 上午 | 七概念 R→I→E→V 完成初始评估：4 路并行调研＋本机 okw 切片 | 报告 6 文件、CMP/ECO 145 条事实、Q-1~Q-8 待验证清单 |
| 12:03 | 提交 6af66bce1 | 模式「社区指标三查法」L1-draft（3 文件，+163） |
| 12:04 | 提交 b807d921e | 初始评估报告（6 文件，+718/-1） |
| 13:22—14:25 | Q 门首轮：4 路并行调研代理（Q-1/7、Q-3/6、Q-4、Q-5）＋本机只读实测（Q-2/8） | VF-01~49、信源 S36~S50 |
| 14:44 | 提交 0bdecaa59 | 首轮核验（6 文件，+240/-39），评分 70→73 |
| 用户授权后 | 二轮功能级实测：服务端通道取证＋Gen2 零安装解包 | VF-50~61、信源 S51~S54 |
| 15:41 | 提交 fc7e89377 | 二轮实测（3 文件，+73/-16），Q-2 闭环/Q-8 架构级验证，评分维持 73 |

## 二、事实清单（R 阶段，F-001~F-030）

### A. 规模与产出

| 编号 | 事实 | 来源 |
|---|---|---|
| F-001 | 里程碑于 2026-10-14 单日完成，4 个提交时点为 12:03/12:04/14:44/15:41，截至复盘时全部处于本地未推送状态 | git log |
| F-002 | 4 提交合计 10 文件次、+1194/-56 行（163+718+240+73 增行） | git show --numstat |
| F-003 | 报告目录 5 个文件：README 332 行/42.5KB、两份事实附录 192+188 行/27.2+36.1KB、核验附录 250 行/47.2KB、index 11 行 | 文件系统 |
| F-004 | 一手事实登记合计 206 条：初始新增 CMP-01~75（75）＋ECO-01~70（70）＝145 条，Q 门 VF-01~61（61 条）；报告另标注复用既有知识包事实约 148 条 | 报告正文/附录 |
| F-005 | 核验附录含 64 个 URL、19 个新增信源（S36~S54）、2 个新登记冲突（NC-01/02）、原 12 缺口与 12 冲突核销对照表各 1 张 | 附录 C |
| F-006 | 主报告 15 个一级章节，覆盖执行摘要、画像、方法、事实清单、4 条洞察、模式、六维详评、评分对照、风险、适用性、okw 切片、Q 清单、V 门、质量门、信源 | README.md |
| F-007 | 同里程碑产出第 1 个 L1-draft 模式 community-metric-triple-check（161 行/13.3KB，frontmatter validation_count=1）；本复盘再产出第 2 个 L1-draft 模式 | patterns 目录 |

### B. 方法与过程

| 编号 | 事实 | 来源 |
|---|---|---|
| F-008 | 初始报告第十二章显式登记 Q-1~Q-8 待验证清单，每行含验证方式与复核窗口（90 天/季度/持续/随版本等） | 报告第十二章 |
| F-009 | Q 门首轮以 4 路并行调研代理执行（Q-1/Q-7 一路、Q-3/Q-6 一路、Q-4 一路、Q-5 一路），Q-2/Q-8 走本机 okw 只读实测 | 会话记录 |
| F-010 | 首轮网络抓取时间窗 13:22—14:25（约 63 分钟），14:44 完成提交 | 附录时间戳/git |
| F-011 | 首轮结果：Q-1 部分推翻原判断（成文 LTS 政策存在但口径冲突）、Q-6 证伪（9 份安可公告零在列）、Q-4 强化单源结论、Q-3 取得 DistroWatch 6 个月 #107/HPD 132、Q-7 四日期事件定性闭环、Q-5 取得麒麟占单位归属 PR 85.2%/Issue 96.1% | 附录 C 总览 |
| F-012 | 评分仅 7.2 一个维度 2→3，总分 70→73（3.65/5）；其余五维未动；V 门历史意见以追加 Q 门结果方式保留，原文不改写 | 报告第八/十三章 |
| F-013 | 二轮功能级实测在用户明确授权（「执行吧」）后启动，距首轮提交约 57 分钟（14:44→15:41） | 会话记录/git |
| F-014 | 二轮枚举 cdimage 目录：2.0、2.0-SP1、2.0-SP2 三个目录均无 WSL/rootfs 镜像；3.0 目录有双 WSL 镜像 | cdimage.openkylin.top |
| F-015 | upgrade-config/kylin-revision-manager-sources.json 的 sources 数组仅 1 条（version=Beta1，目标 openKylin-Desktop-V2.0-Release-x86_64.iso，isosize 4.8）；HTTP Last-Modified=2024-08-26；display.json Last-Modified=2024-06-06 | S51/S52 |
| F-016 | 解包 kylin-revision-manager 1.0.3.0-1ok3（deb 115MB）：changelog 止于 2023-12-12；形态为 Python3 D-Bus 系统服务（systemd Before=lightdm）＋Qt 前端；升级走 initramfs-upgrade 重启流程，包内自带双架构 docker.io/containerd/runc/KARE | 包级实测 |
| F-017 | 模拟安装结果：kylin-ai-subsystem 拉入 267 包；libkylin-ai-base2 最小闭包 88 包、Installed-Size 合计约 330MB；两方案均提示移除 libcurl3-gnutls | apt-get install -s |
| F-018 | 二轮下载 91 个 deb（88 闭包中实际取得 87 个＋kylin-bot＋3 个云引擎插件；unixodbc-common 1 个缺失）至 /mnt/ai（宿主 S: 盘，15T 容量），全部以 apt-get download 落私有目录解包，结束后删除 | 实测日志 |
| F-019 | 二轮取证前后 dpkg -l 中 Gen2 包均为未安装状态，根分区占用两次记录均为 3.0G | 实测对账 |
| F-020 | kylin-bot 0.7.5 二进制免安装运行：--version 输出 kylinbot 0.7.5；--help 列出 27 个子命令；providers 子命令输出 "Supported providers (66 total)"；ldd 无缺失库 | 免安装实测 |
| F-021 | kylin-bot 二进制含 mcp_client.rs/mcp_transport.rs/mcp_tool.rs 路径字符串、tools/call、JSON-RPC、mcp.servers 配置键、ACP（JSON-RPC 2.0 over stdio）等实现痕迹 | strings 实测 |
| F-022 | 包内预置 12 个桌面技能（audio/bluetooth/keyboard/mouse/navigations/network-manager/osdserver/panel/power/shortcut-navigations/srceen/touchpad），SKILL.md 内为 gdbus 调 org.ukui.Framework 示例；模型清单 modelsmd5 列 47 个文件，download.py 经 ModelScope 匿名下载 | 包级实测 |
| F-023 | VF-61 显式登记三项未验证：模型实际推理、外部 MCP tools/call 往返、语音端到端链路；7.6 维评分维持 4 分 | 附录 C |

### C. 异常、环境与协作边界

| 编号 | 事实 | 来源 |
|---|---|---|
| F-024 | 首轮调研代理在 d:\AI 根目录遗留 18 个临时 HTML 与 oktmp 目录，核验完成后统一删除并做 PowerShell 验证 | 会话记录 |
| F-025 | 会话期间 Write/Edit/DeleteFile 工具出现 IPC 故障（aha_ipc_send/RestartNeeded），文件写入改走 PowerShell [System.IO.File]::WriteAllText（UTF-8 无 BOM、LF） | 会话记录 |
| F-026 | python/py 不在 PATH，全部使用 Python 3.14.7 全路径；复杂 bash 经 base64 投递以规避 PowerShell 引号解析 | 会话记录 |
| F-027 | okw 各 exec 会话间 /tmp 不保留，下载改持久目录；/mnt/ai 为 drvfs，不支持 chmod 且 strings 读大文件耗时长，静态取证改在 ext4 家目录执行 | 实测记录 |
| F-028 | 工作区存在并行会话遗留的 4 个 openkylin-docs-wiki 脏文件及其他 agent 的 6 个 .agents 脏文件；本里程碑 4 次提交均未暂存上述文件 | git status |
| F-029 | 每次提交前运行 check-links（报告目录本地引用 16 个）、repo-check mermaid/filename 校验，结果全绿；pre-commit 钩子通过 | 门禁记录 |
| F-030 | 既有知识包 openkylin-docs-wiki（2026-09-29/10-08 实测）提供 3.0 WSL 双镜像、51.6 秒导入、Gen1 OCR 等事实，本轮复用并在正文标注来源 | 知识包 |

**G1 结论**：30 条事实均为可验证客观陈述，关键数字（提交行数、包数、版本号、时间戳、URL 数）附来源，无因果推断词。

## 三、洞察与对抗审查

3 条四元组洞察与 4 视角对抗审查记录见 [insight-extraction.md](insight-extraction.md)。

## 四、萃取产物

- 新模式：[缺口双轮核验法](../../../patterns/methodology-patterns/research-knowledge/gap-two-round-verification.md)（L1-draft，单案例）——公开信源轮（供给侧观测优先）＋零变更功能轮（制品/二进制/CLI 取证），证据四档 L0~L3，7 条反模式。
- 同批既有模式：[社区指标三查法](../../../patterns/methodology-patterns/governance-strategy/community-metric-triple-check.md)（解决规模数字可信度，与新模式互补）。

## 五、行动项

5 条原子行动项（含 owner 与时点）见 [actionable-items.md](actionable-items.md)。

## 六、质量门记录

| 门 | 标准 | 结果 |
|---|---|---|
| G1 | 事实≥20、无因果词、可回溯 | 通过（30 条） |
| G2 | ≥3 条四元组洞察、维度独立、有反常识与行动 | 通过（3 条） |
| V | 四视角、意见≥5、采纳≥2 | 通过（意见 7 条，采纳 3 条并修正模式/行动项） |
| G3 | 模式触发/步骤/≥3 反模式/检验/迁移/单案例标注 | 通过（130 行，7 反模式，4 迁移例） |
| G4 | 单一职责、预提交验证、Conventional Commits | 见本次原子提交 |

---

*本复盘只对「工作过程」做结论，不改变原评估对 openKylin 的任何评分（73/100 维持）。*