---
version: 1.0
created: 2026-07-04
source: "https://mp.weixin.qq.com/s/iiTmgbtrYHMMjQ7dn7CDrg?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/zleap-agent-harness-learning-analysis/spec.toml"
author: "未标注（微信公众号文章）"
topic: "AI Agent Harness 设计"
tags: ["Zleap-Agent", "Agent Harness", "Workspace-first", "本地小模型", "Context Engineering", "Agent Loop", "记忆系统", "多模型协作"]
---
# Zleap-Agent Harness 设计学习笔记 - Product Requirement Document

## Overview
- **Summary**: 本文系统分析一篇关于 Zleap-Agent 的技术文章。Zleap-Agent 被定位为"本地小模型的 Claude Code"，提出以 Workspace-first 为核心的完整 Agent Harness 设计，围绕 Context、Tools、Memory、Runtime、Boundary 五大问题，给出"先选工作区、再组装上下文"的解法。文章以 OpenClaw、Hermes Agent、WildClawBench 等真实样本为对照，论证了当上下文、工具、记忆不断膨胀时，如何让 Agent 只看该看的那部分，对本地小模型与企业私有化场景具有特殊意义。
- **Purpose**: 通过结构化学习笔记形式，系统梳理 Zleap-Agent 的 Harness 设计哲学、五大核心模块的实现思路与对照案例，评估其技术准确性与实用性，提炼可复用的 Agent 设计方法论与行业启示。
- **Target Users**: AI Agent 架构师、本地小模型应用开发者、企业私有化部署决策者、Agent 框架研究者、Context Engineering 实践者

## Goals
- 完整梳理文章核心观点与 Harness 五大模块设计
- 记录关键量化数据与对照案例
- 解析 Workspace-first 设计哲学及其对五大问题的统一处理
- 评估技术准确性、权威性与实用性
- 总结可应用的 Agent 设计方法论与行业启示
- 提取专业术语并建立术语表

## Non-Goals (Out of Scope)
- 不进行 Zleap-Agent 代码复现或部署验证
- 不做与 Claude Code、Cursor 等产品的深度功能对比
- 不进行 OpenClaw、Hermes Agent 的逆向工程分析
- 不涉及 Zleap-Agent 内部未公开的实现细节

## Background & Context
- **报道来源**：微信公众号文章（行业新闻转载）
- **发布时间**：2026年（具体日期未标注）
- **行业背景**：Agent 圈从讨论 Prompt → 讨论 Loop → 讨论 Harness，单轮提示词已不够用，需处理循环如何跑、系统如何撑住循环
- **核心矛盾**：上下文窗口变大不等于注意力变便宜；工具、记忆、历史不断追加会退化为长 Prompt，筛选压力回到模型身上
- **目标场景**：本地小模型、企业私有化部署
- **开源地址**：https://github.com/Zleap-AI/Zleap-Agent

## Functional Requirements
- **FR-1**: 提取文章主要观点与核心结论
- **FR-2**: 解析文章结构框架与论述逻辑（六大部分 + 结语）
- **FR-3**: 记录关键量化数据（上下文占用、harness 收益等）
- **FR-4**: 梳理 Harness 五大模块（Context/Tools/Memory/Runtime/Boundary）的设计原理
- **FR-5**: 对比 Workspace-first 与传统长 Prompt 方案的技术差异
- **FR-6**: 评估内容准确性、权威性、实用性
- **FR-7**: 总结可应用的 Agent 设计方法论与行业启示
- **FR-8**: 整理专业术语表

## Non-Functional Requirements
- **NFR-1**: 学习笔记结构清晰，便于快速检索关键信息
- **NFR-2**: 技术解析准确，不曲解原文含义
- **NFR-3**: 评估客观中立，区分事实陈述与方法论建议
- **NFR-4**: 知识要点具有可操作性，能指导 Agent 系统设计

## Constraints
- **Technical**: 仅基于文章公开信息进行分析，无法验证 Zleap-Agent 内部实现
- **Business**: 不涉及商业机密，仅使用公开可查信息
- **Dependencies**: 需依赖原文提供的设计描述与对照案例数据

## Assumptions
- 文章中引用的 OpenClaw context 数据真实可信
- WildClawBench 与 Agentic Harness Engineering 的实验数据准确
- Zleap-Agent 开源项目与文中描述的设计思路一致
- Hermes Agent Channel Fracture 案例分析符合论文原文

## Acceptance Criteria

### AC-1: 核心观点完整提取
- **Given**: 已提取文章完整内容
- **When**: 进行内容分析与结构化整理
- **Then**: 学习笔记包含 Workspace-first 设计哲学、Harness 五大问题、本地小模型价值三大核心观点
- **Verification**: `human-judgment`
- **Notes**: 需标注观点来源与支撑案例

### AC-2: 关键数据准确记录
- **Given**: 文章中明确给出的量化数据
- **When**: 整理关键指标章节
- **Then**: 准确记录 system prompt 38,412 字符、tool schemas 31,988 字符、harness 差异 18 个百分点、Terminal-Bench 2 pass@1 从 69.7% 提升到 77.0% 等数据
- **Verification**: `programmatic`
- **Notes**: 需标注数据来源（OpenClaw / WildClawBench / Agentic Harness Engineering）

### AC-3: 设计原理解析清晰
- **Given**: 文章对五大模块的设计描述
- **When**: 撰写技术解析章节
- **Then**: 清晰解释 Workspace-first 切分逻辑、Context 装配策略、Tools 工作区绑定、Memory 三分区（人/事/经验）、Runtime 可审计轨迹、Boundary 四类边界
- **Verification**: `human-judgment`
- **Notes**: 使用对照案例（OpenClaw/Hermes）帮助理解

### AC-4: 内容评估客观中立
- **Given**: 文章包含方法论建议与产品宣传成分
- **When**: 进行准确性、权威性、实用性评估
- **Then**: 区分客观事实与方法论建议，指出需要进一步验证的内容
- **Verification**: `human-judgment`
- **Notes**: 从来源可信度、数据可验证性、设计合理性三个维度评估

### AC-5: 知识要点实用可复用
- **Given**: 完成全文分析
- **When**: 总结可应用知识要点
- **Then**: 提炼出对 Agent 架构设计、本地模型部署、企业私有化场景有指导意义的要点
- **Verification**: `human-judgment`
- **Notes**: 按应用场景分类（架构设计/本地部署/企业场景/方法论启示）

### AC-6: 术语表完整规范
- **Given**: 文章中出现的专业术语
- **When**: 整理术语表
- **Then**: 包含所有关键术语的中英文对照与简明解释
- **Verification**: `programmatic`

## Open Questions
- [ ] Zleap-Agent 的 Workspace 切换是由模型自主决定还是由规则驱动？
- [ ] Memory Dream 离线整理的触发频率与资源消耗如何？
- [ ] 多模型协作中，工作区与模型的绑定是静态配置还是动态路由？
- [ ] 经验记忆的脱敏规则如何设计，如何判断"可复用性"？
- [ ] Workspace-first 在多用户高并发场景下的性能表现如何？
- [ ] PostgreSQL 持久化的运行轨迹如何支持回滚与重放？

## 文章结构框架

### 第一部分：Zleap-Agent 总览（本地小模型的 Claude Code）
- 定位：本地小模型的 Claude Code，一套完整的 Harness 设计
- 核心设计：Workspace-first 作为整个 Harness 的设计核心
- 五大问题：Context、Tools、Memory、Runtime、Boundary
- 解法精髓：先选工作区，再组装上下文；不让 Agent 每步加载全部工具、记忆和历史
- Workspace 与子 Agent/工具分组的区别：Workspace 是"同一个人切换工作台"，子 Agent 是"临时找另一个人帮忙"

### 第二部分：Context（不要问能塞多少，先问这一轮该看什么）
- 痛点：长上下文错觉——窗口变大不等于注意力变便宜
- OpenClaw 数据：system prompt 约 38,412 字符，tool schemas 约 31,988 字符
- 销售复盘案例：粗暴做法 vs 拆 context 做法（预取/摘要/按需读取）
- Main Workspace 设计：不直接承担所有上下文，是调度台
- 对照：OpenClaw 展示长上下文压力，Zleap 提前按工作区切上下文

### 第三部分：Tools（工具不是越多越好，关键是当前可见）
- 痛点：工具越多，动作空间越大，权限面越宽，审计成本越高
- OpenClaw 样本：本地常驻 Gateway，接入多种消息入口与本地能力
- 查资料 vs 改文件案例：不同任务需要不同工具集
- 解法：工具与 Workspace 绑定，不全局暴露
- 收益：tool schema 成本、误调用概率、权限审计压力都下降

### 第四部分：Memory（记忆要有归属，不能混成一个篮子）
- 痛点：记忆会影响未来推理，写错/取错/串任务都会污染行为
- Hermes Channel Fracture 案例：cron 路径因 skip_memory=True 出现"通道断裂"
- Zleap 双线设计：A 线 people notes（用户偏好/画像），B 线 core records（工作事件/经验）
- 经验记忆准入规则：只记录可复用流程/失败模式/验证习惯/恢复策略，禁止业务隐私进入
- Memory Dream：离线记忆整理器，提取稳定画像与可复用经验
- Recall 双层：prefetch（fast，不走 LLM）+ 主动 recall（精细检索 + rerank）
- 记忆三分区：人（用户偏好）、事（项目事实）、经验（脱敏方法）
- 新记忆 reconcile：跳过/并存/替换/保留

### 第五部分：Runtime（每一次循环都应该留下可复盘的轨迹）
- 痛点：无运行轨迹则无法定位失败原因
- WildClawBench 数据：同模型切换不同 harness，表现最高相差 18 个百分点
- Agentic Harness Engineering 数据：Terminal-Bench 2 pass@1 从 69.7% 提升到 77.0%，收益主要来自 tools/middleware/long-term memory
- 代码修复 Agent 案例：必须记录失败路径（读了什么/为什么改/执行了什么/错误信息/如何调整）
- Zleap runtime 模块：运行状态与记忆共用 PostgreSQL 持久化，支持审计与回滚
- Prompt 作用于单轮；Harness 管理执行过程、状态变化、失败恢复与后续优化

### 第六部分：Boundary（真实工作流必须有边界）
- 痛点：企业场景要求数据不出内网、成本可控、权限明确、记忆不串、工具受限
- 本地小模型回归原因：敏感数据本地处理、常规流程用便宜模型、复杂分析交给强模型
- 财务报销案例：不应看到销售客户记录，不应调用研发工具；敏感票据走本地模型
- 多模型协作：不同工作区绑定不同模型，按工作区分配合适模型
- 四类边界：数据边界、工具边界、模型边界、记忆边界
- Workspace-first 统一处理五大问题：Context 限工作区、Tools 按区暴露、Memory 分区、Runtime 记工作区、Boundary 落权限

### 第七部分：写在最后（方法论总结）
- Agent 演进：Prompt → Loop → Harness
- Zleap-Agent 价值：当上下文/工具/记忆膨胀时，让 Agent 只看该看的部分
- Workspace-first 思路可脱离 Zleap-Agent 单独使用
- 上下文公式：Context = System Prompt + Workspace Prompt + Tools + Memory + History
- 上下文两种加载：Prefetch（短/准/可控）+ Agentic（按需读取）
- 数据库驱动：分区/审计/回滚/复用能力
- 模型层稀疏注意力 ↔ Harness 层 Workspace 的呼应

## 关键知识点与数据

### 量化数据
| 指标 | 数值 | 来源 | 说明 |
|------|------|------|------|
| OpenClaw system prompt | 约 38,412 字符 | OpenClaw context 文档 | 任务展开前已占用上下文预算 |
| OpenClaw tool schemas | 约 31,988 字符 | OpenClaw context 文档 | 工具 schema 计入上下文 |
| Harness 差异 | 最高 18 个百分点 | WildClawBench | 同模型切换不同 harness 的表现差异 |
| Terminal-Bench 2 pass@1 | 69.7% → 77.0% | Agentic Harness Engineering | 多轮 harness 演化收益 |
| 收益来源 | tools/middleware/long-term memory | Agentic Harness Engineering | 非单纯改 system prompt |

### Workspace-first 与传统长 Prompt 对比
| 维度 | 传统长 Prompt 方案 | Workspace-first 方案（Zleap） |
|------|---------------------|------------------------------|
| 上下文组织 | 工具/记忆/历史不断追加 | 按工作区切分，按需加载 |
| 工具暴露 | 全局工具池 | 工具与工作区绑定 |
| 记忆管理 | 长期记忆桶 | 人/事/经验三分区 |
| 权限控制 | 难以隔离 | 工作区即权限边界 |
| 模型选择 | 单一模型 | 工作区绑定不同模型 |
| 失败定位 | 仅看最后报错 | PostgreSQL 持久化轨迹可回溯 |
| 上下文成本 | 高（全量加载） | 低（当前任务所需范围） |

### 五大模块设计要点
1. **Context**：Main Workspace 是调度台不承担所有上下文；进入具体 Workspace 只看当前工作区的 prompt/tools/memory/history
2. **Tools**：工具与 Workspace 绑定不全局暴露；模型每个空间只面对更小更明确的动作集合
3. **Memory**：A 线 people notes + B 线 core records；Memory Dream 离线整理；prefetch + 主动 recall 双层；新记忆 reconcile
4. **Runtime**：独立 runtime 模块；运行状态与记忆共用 PostgreSQL 持久化；支持审计与回滚
5. **Boundary**：数据/工具/模型/记忆四类边界；不同工作区绑定不同模型实现多模型协作

### 上下文装配公式
```
Context = System Prompt + Workspace Prompt + Tools + Memory + History
```
- System Prompt：保持全局行为风格
- Workspace Prompt：说明当前工作区
- Tools：只暴露当前工具
- Memory：只取相关记忆
- History：保留必要近期轨迹

### 上下文加载两种方式
| 方式 | 特点 | 风险 |
|------|------|------|
| Prefetch（预取） | 提前放进来的内容（用户偏好/近期事件/常用经验），短/准/可控 | 预取过多抬高上下文成本 |
| Agentic（按需读取） | 模型按需读取（看到旧记忆摘要后追问详情再读完整） | 全部按需读取增加交互轮次与失败点 |

### Memory 双线设计
| 线 | 内容 | 读写方式 |
|----|------|----------|
| A 线 people notes | 用户偏好、稳定画像、Agent 自身认知 | 快速预取 |
| B 线 core records | 工作事件、可复用经验 | 抽取/向量化/实体关联/召回/精排链路 |

### 经验记忆准入规则
| 允许进入 | 禁止进入 |
|----------|----------|
| 可复用流程 | 公司名 |
| 失败模式 | 客户名 |
| 验证习惯 | 项目名 |
| 恢复策略 | 财务事实 |
| | 私有路径 |
| | 一次性任务结果 |

## 对照案例样本

### OpenClaw（个人 Agent 本地常驻 Gateway）
- **角色**：展示真实 Agent 的长上下文压力与工具接入广度
- **数据**：system prompt 38,412 字符 + tool schemas 31,988 字符
- **能力**：接入 WhatsApp/Telegram/Slack/Discord/Signal/iMessage/WebChat 等消息入口，连接 CLI/Web UI/automations/nodes 等本地能力
- **启示**：个人 Agent 可成为长期在线的本地控制平面，但 Harness 必须回答"这一轮到底应该暴露哪些工具"

### Hermes Agent（Channel Fracture 案例）
- **角色**：警示记忆写入需验证完整通道
- **场景**：定时任务 Agent 向目标 Agent 注入持久记忆
- **三条路径**：直接写 SQLite / 目标 Agent 通过 memory tools 自写入 / cron delegated 写入
- **问题**：cron 路径因 skip_memory=True 和 memory manager 初始化条件，出现"看似完成、实际未送达"的通道断裂
- **启示**：记忆系统不能只看"有没有存储"，还要看完整链路（谁写入/写给谁/什么通道/是否送达/何时检索/是否污染）

### WildClawBench（真实 CLI harness 评估）
- **角色**：证明 Harness 对模型表现的影响
- **数据**：同模型切换不同 harness，表现最高相差 18 个百分点
- **评估对象**：OpenClaw、Claude Code、Codex、Hermes Agent 等
- **启示**：Harness 工程是独立于模型能力的关键变量

### Agentic Harness Engineering（harness 演化实验）
- **角色**：证明 harness 演化的收益来源
- **数据**：Terminal-Bench 2 pass@1 从 69.7% 提升到 77.0%
- **收益来源**：tools、middleware、long-term memory（非单纯改 system prompt）
- **启示**：Harness 优化的重点不在 prompt 文案，而在工具/中间件/长期记忆

## 专业术语表

| 术语（中文） | 术语（英文） | 解释 |
|-------------|-------------|------|
| 智能体外壳 | Harness | Agent 运行的支撑系统，管理上下文/工具/记忆/运行时/边界 |
| 工作区优先 | Workspace-first | 先选工作区再组装上下文的设计哲学 |
| 工作区 | Workspace | Agent 的运行环境单元，包含独立的 prompt/tools/memory/history/model/permission |
| 主工作区 | Main Workspace | 负责理解用户目标与任务调度的工作区 |
| 上下文工程 | Context Engineering | 围绕模型上下文装配的工程实践 |
| 智能体循环 | Agent Loop | 模型读上下文/选工具/调用/接收结果/修正计划的循环过程 |
| 预取 | Prefetch | 提前将内容放入上下文的加载方式 |
| 按需读取 | Agentic Recall | 模型按需读取完整详情的加载方式 |
| 工具模式 | Tool Schema | 工具的结构化描述，会发送给模型并计入上下文 |
| 记忆梦 | Memory Dream | 离线记忆整理器，从清理后的会话材料中提取稳定画像与可复用经验 |
| 人物笔记 | People Notes | A 线记忆，保存用户偏好/稳定画像/Agent 自身认知 |
| 核心记录 | Core Records | B 线记忆，保存工作事件与可复用经验 |
| 通道断裂 | Channel Fracture | 记忆写入"看似完成、实际未送达"的故障模式 |
| 协调 | Reconcile | 新记忆进入系统时与旧记忆比对，决定跳过/并存/替换/保留 |
| 重排序 | Rerank | 对召回结果进行精细排序的过程 |
| 终端基准 | Terminal-Bench | 评估 Agent 在终端任务表现的基准测试 |
| 通道网关 | Gateway | 本地常驻的 Agent 控制平面，可接入多种消息入口与本地能力 |
| 多模型协作 | Multi-Model Collaboration | 不同工作区绑定不同模型，按任务分配合适模型 |
| 私有化部署 | Private Deployment | 模型部署在企业内网，数据不出内网 |
| 稀疏注意力 | Sparse Attention | 模型层让模型不看所有 token 的技术 |

## 内容质量评估

### 准确性评估
- **数据可信度**：⭐⭐⭐⭐（4/5）
  - OpenClaw 的 context 字符数可复现验证
  - WildClawBench 与 Agentic Harness Engineering 的实验数据来源明确
  - Hermes Channel Fracture 案例引自论文分析
  - 需注意：数据均为引用，未独立验证
- **技术描述准确性**：⭐⭐⭐⭐（4/5）
  - Workspace 与子 Agent/工具分组的区分准确
  - 记忆三分区（人/事/经验）逻辑合理
  - 上下文装配公式符合工程实践
  - 未公开 Zleap-Agent 内部实现细节，无法深度验证
- **事实陈述**：
  - ✅ Zleap-Agent 开源项目可查
  - ✅ OpenClaw、Hermes Agent、WildClawBench 均为真实项目/研究
  - ⚠️ "本地小模型的 Claude Code"是定位比喻，非严格定义
  - ⚠️ 收益数据来自特定基准，迁移性需验证

### 权威性评估
- **来源可信度**：⭐⭐⭐（3/5）
  - 微信公众号文章，属于行业媒体转载性质
  - 非同行评审论文，但引用了论文级证据
  - 带有明显的方法论倡导色彩（"值得参考的起点"）
- **信息完整性**：⭐⭐⭐⭐（4/5）
  - 五大模块论述完整，结构清晰
  - 对照案例丰富（OpenClaw/Hermes/WildClawBench/Agentic Harness Engineering）
  - 未提及 Zleap-Agent 的局限性、失败案例与性能基准
  - 未披露 Zleap-Agent 的实际部署规模与用户反馈

### 实用性评估
- **对 Agent 架构师**：⭐⭐⭐⭐⭐（5/5）
  - Workspace-first 是可直接落地的设计模式
  - 五大模块划分提供了清晰的架构思考框架
  - 上下文装配公式与加载策略具有工程指导价值
- **对本地模型开发者**：⭐⭐⭐⭐⭐（5/5）
  - 明确针对本地小模型场景
  - 多模型协作机制解决成本与能力平衡
  - 记忆分区降低小模型的上下文压力
- **对企业私有化决策者**：⭐⭐⭐⭐（4/5）
  - 四类边界设计直接对应企业合规需求
  - 数据不出内网、权限隔离、记忆不串是核心价值
  - 需进一步评估实际部署复杂度与运维成本
- **对 Agent 框架研究者**：⭐⭐⭐⭐（4/5）
  - 提供了 Prompt→Loop→Harness 的演进视角
  - 模型层稀疏注意力 ↔ Harness 层 Workspace 的呼应有启发性
  - 缺少与主流框架（LangChain/AutoGen/CrewAI）的对比

## 可应用知识要点

### 架构设计领域
1. **Workspace-first 起点原则**：不管用什么模型/框架，先切工作区、再组装上下文，都是值得参考的起点；先问"当前任务应该发生在哪个工作区"，再问"Agent 能接多少工具"
2. **上下文装配公式**：Context = System Prompt + Workspace Prompt + Tools + Memory + History，每一层都有明确的职责边界
3. **调度台设计**：Main Workspace 不直接承担所有上下文，只负责理解目标、判断工作区、传递必要背景，避免主对话完整回放
4. **工具工作区绑定**：工具挂在工作区上而非全局暴露，模型进入哪个工作区就只看当前工作区的工具，缩小 tool schema 成本与误调用概率
5. **可审计 Runtime**：运行状态与记忆共用持久化存储（如 PostgreSQL），支持回溯某一步读了什么、调了什么工具、拿到什么结果
6. **Harness 五问题框架**：Context/Tools/Memory/Runtime/Boundary 是设计任何 Agent 系统都必须回答的五个问题

### 本地部署领域
1. **多模型协作路由**：常规沟通/网页检索/文件处理/复杂分析/本地敏感任务不必都交给同一模型，按工作区分配合适模型
2. **敏感数据本地处理**：涉及敏感票据/客户信息时优先走本地模型，需要复杂规则解释时再由工作区决定是否调用更强模型
3. **成本控制双路径**：上下文更省（按工作区切）+ 模型按需分配（不同工作区不同模型），同时控制延迟、成本和数据边界
4. **记忆分区降低小模型压力**：小模型长上下文定位能力弱，按人/事/经验分区 + prefetch 快取避免全量加载

### 企业场景领域
1. **四类边界设计**：数据边界（不出内网）、工具边界（按工作区可见）、模型边界（按工作区绑定）、记忆边界（不跨用户/任务/工作区串）
2. **多用户记忆隔离**：多个用户共享同一个 Agent 时，谁能看谁的记忆、哪个工作区能读哪些上下文、哪些经验可以共享，都需底层系统管理
3. **经验记忆脱敏复用**：经验记忆只记录可复用流程/失败模式/验证习惯/恢复策略，公司名/客户名/项目名/财务事实/私有路径/一次性任务结果禁止进入
4. **权限审计简化**：工具与工作区绑定后，权限面随工作区收窄，审计与安全成本下降

### 方法论启示领域
1. **Prompt→Loop→Harness 演进**：单轮提示词已不够用，需处理循环怎么跑、系统怎么撑住循环；Harness 是 Agent 工程的下一阶段
2. **Harness 独立于模型**：同模型切换不同 harness 表现最高相差 18 个百分点，Harness 工程是独立于模型能力的关键变量
3. **Harness 优化重点不在 prompt 文案**：收益主要来自 tools/middleware/long-term memory，而非单纯改 system prompt
4. **模型层与 Harness 层呼应**：模型层做稀疏注意力让模型不看所有 token，Harness 层做 Workspace 让 Agent 不加载所有上下文，是同一思想的两层实现
5. **记忆系统完整链路设计**：记忆不能只看"有没有存储"，还要看谁写入/写给谁/什么通道/是否送达/何时检索/是否污染
6. **记忆 reconcile 机制**：新记忆进入系统时与旧记忆比对，决定跳过/并存/替换/保留，避免记忆膨胀与冲突

## 行业启示与趋势判断

1. **Agent 工程进入 Harness 阶段**：从 Prompt 工程到 Loop 工程再到 Harness 工程，竞争焦点从"模型说什么"转向"系统如何撑住循环"
2. **Workspace-first 成为设计范式**：当上下文/工具/记忆膨胀时，工作区切分是控制可见范围的通用解法，可脱离具体框架单独使用
3. **本地小模型价值回归**：企业私有化与数据边界需求推动本地小模型复苏，Harness 设计让小模型在受限上下文下也能可靠工作
4. **记忆成为可治理系统**：从"长期记忆桶"到"人/事/经验三分区 + reconcile + 脱敏"，记忆系统走向工程化治理
5. **多模型协作成为常态**：不同工作区绑定不同模型，按任务分配合适模型，成本/延迟/能力的三角平衡通过工作区路由实现
6. **Harness 证据体系成熟**：WildClawBench、Agentic Harness Engineering 等研究为 Harness 工程提供量化证据，Harness 差异 18 个百分点成为标志性数据
7. **上下文即内存布局**：上下文不再是临时拼装的 prompt，而是有层次的内存布局（System/Workspace/Tools/Memory/History）， prefetch 与按需读取分离

## 相关资源链接
- Zleap-Agent GitHub 仓库: https://github.com/Zleap-AI/Zleap-Agent
- 原文链接: https://mp.weixin.qq.com/s/iiTmgbtrYHMMjQ7dn7CDrg
