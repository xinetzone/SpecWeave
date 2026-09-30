# 04 编码 agent 赛道：131 行与 4161 行之间发生了什么

> 读完本文你会知道：编码 agent 与通用框架的差异、mini-swe-agent/SWE-agent/OpenHands/Aider 四个代表项目的现状、SWE-bench 分数该怎么读（以及为什么不能直接排座次）、"极简派胜在何处、厚栈值在哪里"。

## 4.1 赛道边界：编码 agent 是 harness 的垂直特化

通用框架（[03](03-framework-catalog.md)）面向任意任务；编码 agent 把 harness 的九大部件全部针对"读懂仓库→定位文件→改代码→跑测试→提交"这一条流水线重新裁剪：

- 工具面收敛为 **bash + 编辑器 + 浏览器（部分）**；
- 记忆特化为**仓库地图**（Aider 的 RepoMap，F-036）；
- 沙箱成为硬需求——agent 要在真实仓库里执行任意命令（F-030/F-033）；
- 评测有统一标尺：SWE-bench Verified（真实 GitHub issue + 真实测试）。

## 4.2 四个代表项目登记

### mini-swe-agent（Princeton / Stanford）

- **体量与架构**：PyPI 1.4.2；核心 `agents/default.py` 约 100 行，env/model/script 各约 100 行；仅用 bash、不调用 tool-calling API、线性消息历史、`subprocess.run` 无状态执行（F-029）。
- **成绩**：Claude Sonnet 4 在 SWE-bench Verified 上 65%，README 称强配置可超 74%（F-030）。
- **隔离**：docker、podman、singularity、apptainer 四种容器（F-030）。
- **定位**：研究者证明"模型够强时，scaffold 可以多薄"的参照实现；其文档将已转 maintenance-only 的 SWE-agent 列为被替代对象（F-031）。

### SWE-agent（Princeton NLP）

- **现状**：maintenance-only（F-031）。
- **量化对照**：约 4161 行、67%、每任务约 2.50 美元；对照 mini-swe-agent 的约 131 行、65%、0.37 美元（F-032）。

> 口径警告：F-032 的数字来自 Software Letters SL#68 单一来源（ICLR 2026 相关博客），"代码行数"的统计边界（是否含提示词模板、测试、配置）以该文口径为准；引用时须连同口径一起引用，不得只摘数字。

### OpenHands（All Hands AI）

- **身世**：前身 OpenDevin 2024-03-12 发起，2024-08-26 更名；MIT；2026-06 stars 超 76K（F-033）。
- **架构**：默认 CodeActAgent，LiteLLM 模型无关，Docker 沙箱（F-033）。
- **成绩**：Claude 3.7 Sonnet 单次 60.6%、5 次采样 66.4%；官方 leaderboard API 记录 v1.18.1 + claude-fable-5（2026-06-09）95.8 分、平均每任务 1.43 美元（F-034）。
- **定位**：平台型编码 agent——UI、API、leaderboard、多 agent 研究分支，是这一赛道工程化最重的开源栈之一。

### Aider（Paul Gauthier）

- **规模**：约 44K stars、约 680 万安装、每周约 15B tokens（F-035）。
- **特征**：RepoMap（tree-sitter 代码库地图）、git 自动提交、architect 双模型模式（一个模型出方案、另一个模型改代码）、LiteLLM 接本地模型、100+ 语言（F-036）。
- **定位**：终端结对程序员，不走 SWE-bench 打榜路线，而是以真实日常编码的工作流（每次修改自动 commit，可回滚）立身。

## 4.3 SWE-bench 分数的正确读法

跨项目数字**不能直接排座次**，至少有四个口径差异：

| 口径 | 影响 | 本调研中的实例 |
|---|---|---|
| 模型不同 | 分数首先反映模型，其次才反映 scaffold | mini 用 Claude Sonnet 4（65%，F-030）；OpenHands 有 claude-fable-5 记录 95.8（F-034） |
| 采样次数不同 | 单次 vs best-of-N 差距可达数个点 | OpenHands 60.6%（1 次）vs 66.4%（5 次）（F-034） |
| 框架/版本不同 | v1.18.1 等具体版本与提示词策略均影响结果 | F-034 |
| 成本口径不同 | 每任务成本含不含重试、人工审阅 | 0.37 / 1.43 / 2.50 美元三个数字分别来自不同文章口径（F-032/F-034），不可横比绝对值 |

读图原则：**同文章、同模型、同采样次数下**的比较才有效。F-032 之所以有说服力，正是因为它在同一篇文章内对照 SWE-agent 与 mini-swe-agent；而把 65%（mini/Sonnet 4）、67%（SWE-agent/原文口径）、95.8（OpenHands/fable-5/2026-06）拉成一张排行榜是错误用法。

## 4.4 极简派胜在何处：三个机制而非"代码少"

mini-swe-agent 的 131 行不是随机地少，而是把四个在厚框架里常见的东西拿掉了（F-029）：

1. **拿掉 tool-calling 协议依赖**——直接让模型在 bash 里完成一切动作，少一层格式转换与协议失配；
2. **拿掉状态管理**——`subprocess.run` 无状态执行，线性消息历史即全部状态，没有状态机就没有状态机 bug；
3. **拿掉花哨提示词资产**——动作空间小，提示词可以短；
4. **把隔离外包给容器**——docker/podman 负责"别搞坏机器"，agent 内部不需要安全层。

这与 I-1 的判断一致：当模型能力到位时，环境干净（无状态、容器隔离、唯一 bash 入口）比 scaffold 功能多更重要。

## 4.5 厚栈仍然成立的场景

"薄"不是免费午餐，下列场景厚框架仍有独立价值：

- **异步长任务与恢复**：跑 2 小时的大规模 issue 批量修复需要 checkpoint/hydration（F-012/F-018），无状态循环只能整轮重跑；
- **多 agent 协作研究**：OpenHands 平台的 agent 研究分支、并行重现（best-of-5 采样，F-034）需要调度与 UI；
- **企业治理**：权限、审批、OTel 导出（F-018/F-037/F-038）不是 131 行能覆盖的；
- **日常 IDE 工作流**：Aider 的 RepoMap + git 原子提交（F-036）是另一种"厚"——厚在对真实工作流的贴合，而非抽象层数。

换言之，SWE-agent 的 4161 行不是被"效率更低的自己"击败的，而是被**更强的模型 + 更干净的环境假设**绕过去了；一旦任务环境假设不成立（要恢复、要审计、要协作），厚部件逐个都得请回来。选型含义见 [05 模式](05-selection-pattern.md) 步骤①的任务分级。

## 4.6 给想跑一次编码 agent 的人

最小验证路径（按本调研事实排列，非安装教程，命令以官方文档当日版本为准）：

1. 先明确模型供给：有 Anthropic/OpenAI key 还是本地模型（Aider 经 LiteLLM 接本地，F-036；Qwen-Agent 接 vLLM/SGLang，F-028）；
2. 在**一次性容器**里跑第一个真实 issue（mini-swe-agent 的四容器支持，F-030；OpenHands 的 Docker 默认，F-033），不要在主工作副本里试；
3. 用 git 自动提交型工作流（Aider，F-036）或容器快照保证每次修改可回滚；
4. 用同一 issue 跑 ≥2 个候选，记录你自己的 TTFA 与成功率——把 F-003/F-032 的他人实测当作假设而非结论。

---

上一篇：[03 框架目录与对比表](03-framework-catalog.md) ｜ 下一篇：[05 模式：最小充分脚手架选型法](05-selection-pattern.md)
