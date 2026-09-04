---
spec: ai-agents-okf-wiki
created: 2026-08-23
status: draft
---

# Implementation Tasks

## Task Dependency Graph

```
T1 (R: CodeWhale facts) ─┐
T2 (R: DeepSeek-Reasonix facts) ─┤
T3 (R: openai-codex facts) ─┤
T4 (R: deepcode-cli facts) ─┼──→ T8 (I: all insights) ──→ T9-T15 (E per project) ──→ T16 (V) ──→ T17-T18 (nav) ──→ T19 (review)
T5 (R: nanobot facts) ─────┤
T6 (R: opencode facts) ────┤
T7 (R: pi-cli facts) ──────┘
```

> R 阶段任务 T1-T7 可并行委派（各项目源码独立），I 阶段 T8 需等全部 R 完成后执行，E 阶段 T9-T15 按优先级顺序逐个执行（大型项目先做以控制风险），V 阶段 T16 等全部 E 完成后执行。

---

## Phase R: 事实采集

### Task 1: R 阶段——CodeWhale 源码事实采集
- **Priority**: high
- **Depends**: none
- **AC Coverage**: FR1, AC-R11
- **Scope**: 扫描 `external/libs/ai/agents/CodeWhale/` 核心源码
  - Cargo.toml 依赖与项目结构
  - src/ 核心 Rust 代码（Agent 循环、工具系统、MCP、Subagent）
  - web/ 前端架构概览（不深入细节）
  - docs/ 下的关键文档（FLEET/MCP/MODES/HOOKS/WEB/SKILLS/SUBAGENTS）
- **Output**: `bundles/ai-agent/codewhale/spec/facts.md`（编号事实 F-001~F-xxx，零推测）
- **Test Requirements**:
  - **rule**: facts.md 中无"用于"/"目的是"/"设计为"等推断词（G1 质量门）
  - **rule**: 每条事实标注源码文件路径和行号范围
  - **rule**: 核心模块全覆盖（Agent 循环、工具注册、MCP 协议、Subagent、Skills 系统）
  - **rubric** (事实覆盖率 0-3): ≥ 2（核心模块事实 ≥ 50 条）

### Task 2: R 阶段——DeepSeek-Reasonix 源码事实采集
- **Priority**: high
- **Depends**: none
- **AC Coverage**: FR1, AC-R11
- **Scope**: 扫描 `external/libs/ai/agents/DeepSeek-Reasonix/` 核心源码
  - internal/agent/（Agent 运行循环、任务、会话、分支、调度器）
  - internal/acp/（ACP 协议实现）
  - internal/bot/（Bot 网关、Feishu/QQ 适配器）
  - internal/cli/（CLI 入口、TUI、MCP、插件、Provider）
  - cmd/reasonix/（主入口）
  - desktop/（Wails 桌面应用概览）
- **Output**: `bundles/ai-agent/deepseek-reasonix/spec/facts.md`
- **Test Requirements**:
  - **rule**: facts.md 中无推断性表述（G1）
  - **rule**: 每条事实标注源码路径
  - **rule**: 核心包（agent/acp/bot/cli）全覆盖
  - **rubric** (事实覆盖率 0-3): ≥ 2（核心模块事实 ≥ 60 条）

### Task 3: R 阶段——openai-codex 源码事实采集
- **Priority**: high
- **Depends**: none
- **AC Coverage**: FR1, AC-R11
- **Scope**: 扫描 `external/libs/ai/agents/codex/` 核心源码
  - codex-cli/（Node.js CLI 入口、bin/codex.js）
  - codex-rs/（Rust TUI、CLI、config）
  - sdk/python/（Python SDK）
  - docs/（skills.md、sandbox.md、agents_md.md、config.md、exec.md）
- **Output**: `bundles/ai-agent/openai-codex/spec/facts.md`
- **Test Requirements**:
  - **rule**: facts.md 中无推断性表述（G1）
  - **rule**: 每条事实标注源码路径
  - **rule**: 三部分（JS CLI/Rust TUI/Python SDK）核心结构均覆盖
  - **rubric** (事实覆盖率 0-3): ≥ 2（核心模块事实 ≥ 50 条）

### Task 4: R 阶段——deepcode-cli 源码事实采集
- **Priority**: medium
- **Depends**: none
- **AC Coverage**: FR1, AC-R11
- **Scope**: 扫描 `external/libs/ai/agents/deepcode-cli/` 核心源码
  - package.json、tsconfig.json 项目结构
  - src/ 或 lib/ 下的 CLI 入口和核心逻辑
  - docs/mcp.md（MCP 支持）
- **Output**: `bundles/ai-agent/deepcode-cli/spec/facts.md`
- **Test Requirements**:
  - **rule**: facts.md 中无推断性表述（G1）
  - **rule**: 每条事实标注源码路径
  - **rubric** (事实覆盖率 0-3): ≥ 2（核心模块事实 ≥ 20 条）

### Task 5: R 阶段——nanobot 源码事实采集
- **Priority**: high
- **Depends**: none
- **AC Coverage**: FR1, AC-R1
- **Scope**: 扫描 `external/libs/ai/agents/nanobot/` 核心源码
  - nanobot/ Python 包（nanobot.py、cli/、bus/、sdk/、webui/）
  - tui/ TypeScript TUI
  - webui/ React 前端
  - docs/（concepts.md、memory.md、providers.md、quick-start.md）
- **Output**: `bundles/ai-agent/nanobot/spec/facts.md`
- **Test Requirements**:
  - **rule**: facts.md 中无推断性表述（G1）
  - **rule**: 每条事实标注源码路径
  - **rule**: Python 核心模块（Agent 入口、Bus、CLI、SDK）全覆盖
  - **rubric** (事实覆盖率 0-3): ≥ 2（核心模块事实 ≥ 40 条）

### Task 6: R 阶段——opencode 源码事实采集
- **Priority**: medium
- **Depends**: none
- **AC Coverage**: FR1, AC-R11
- **Scope**: 扫描 `external/libs/ai/agents/opencode/` 核心源码
  - packages/ 下的包（如有）
  - infra/（app、lake、stage、stats）
  - specs/v2/（API、config、session、tools 规范文档）
  - script/（hooks、release、format 等脚本）
  - 主入口文件
- **Output**: `bundles/ai-agent/opencode/spec/facts.md`
- **Test Requirements**:
  - **rule**: facts.md 中无推断性表述（G1）
  - **rule**: 每条事实标注源码路径
  - **rubric** (事实覆盖率 0-3): ≥ 2（核心模块事实 ≥ 30 条）

### Task 7: R 阶段——pi-cli 源码事实采集
- **Priority**: medium
- **Depends**: none
- **AC Coverage**: FR1, AC-R11
- **Scope**: 扫描 `external/libs/ai/agents/pi/` 核心源码
  - packages/ai/（模型、OAuth、CLI、compat、images、types）
  - packages/tui/（终端 UI）
  - packages/agent/、packages/client/、packages/server/、packages/evals/
  - .pi/prompts/（内置 prompt 模板）
- **Output**: `bundles/ai-agent/pi-cli/spec/facts.md`
- **Test Requirements**:
  - **rule**: facts.md 中无推断性表述（G1）
  - **rule**: 每条事实标注源码路径
  - **rubric** (事实覆盖率 0-3): ≥ 2（核心模块事实 ≥ 30 条）

---

## Phase I: 架构洞察

### Task 8: I 阶段——全部项目架构洞察与知识地图设计
- **Priority**: high
- **Depends**: T1, T2, T3, T4, T5, T6, T7
- **AC Coverage**: FR2
- **Scope**: 基于 7 个 facts.md，逐项目提炼核心洞察和设计知识地图
  - 每个项目 3-5 个核心洞察（陈述+证据+反常识+行动四元组）
  - 每个项目设计 concepts/ 文档列表（编号、标题、覆盖的事实范围）
  - 每个项目设计 examples/ 和 references/ 文档列表
  - 确定文档间依赖关系和推荐学习路径
- **Output**:
  - `bundles/ai-agent/<name>/spec/insights.md`（每个项目一个）
- **Test Requirements**:
  - **rule**: 每个洞察包含完整四元组（陈述+证据+反常识+行动）（G2）
  - **rule**: 知识地图中每个概念文档明确标注覆盖的 F-xxx 事实范围
  - **rule**: 大型项目（CodeWhale/DeepSeek-Reasonix/openai-codex）概念文档 ≥ 5 篇
  - **rule**: 中小型项目概念文档 ≥ 3 篇
  - **rubric** (知识地图合理性 0-3): ≥ 2（学习路径逻辑清晰，概念分层合理）

---

## Phase E: 文档生成（按项目逐个执行，信源先行、分批生成、Index 最后写）

### Task 9: E 阶段——CodeWhale Bundle 生成
- **Priority**: high
- **Depends**: T8
- **AC Coverage**: FR3, AC-R2, AC-R3, AC-R4, AC-R5, AC-R6
- **Scope**:
  1. 创建目录结构 `bundles/ai-agent/codewhale/{concepts,examples,references}`
  2. 生成 references/ 信源登记文件（信源先行）
  3. 分 2-3 批生成 concepts/ 概念文档（每批 ≤ 7 文件）
  4. 生成 examples/ 示例文档
  5. 生成 log.md
  6. 最后生成 concepts/index.md、examples/index.md、references/index.md、根 index.md
- **Estimated docs**: 8-12 concepts, 2-3 examples, 3-5 references ≈ 13-20 content docs
- **Test Requirements**:
  - **rule**: references/ 文件先于 concepts/examples 创建（G3 信源先行）
  - **rule**: 每批生成文档数 ≤ 7
  - **rule**: 所有内容文档 frontmatter 字段完整（type/title/description/sources/generated/verified/status/stale_after）
  - **rule**: 子目录 index.md 无 frontmatter
  - **rule**: 根 index.md 含 okf_version: "0.2" 和 type: bundle
  - **rubric** (内容质量 0-3): ≥ 2（架构覆盖度满足 AC-RU1）

### Task 10: E 阶段——DeepSeek-Reasonix Bundle 生成
- **Priority**: high
- **Depends**: T8
- **AC Coverage**: FR3, AC-R2, AC-R3, AC-R4, AC-R5, AC-R6
- **Scope**: 同 Task 9 流程，聚焦 internal/agent、internal/acp、internal/bot、internal/cli 核心包
- **Estimated docs**: 8-12 concepts, 2-3 examples, 3-5 references ≈ 13-20 content docs
- **Test Requirements**:
  - **rule**: references/ 先于 concepts/examples 创建
  - **rule**: 每批 ≤ 7 文件
  - **rule**: frontmatter 完整、index.md 规范
  - **rubric** (内容质量 0-3): ≥ 2

### Task 11: E 阶段——openai-codex Bundle 生成
- **Priority**: high
- **Depends**: T8
- **AC Coverage**: FR3, AC-R2, AC-R3, AC-R4, AC-R5, AC-R6
- **Scope**: 同 Task 9 流程，覆盖 codex-cli（Node.js）、codex-rs（Rust TUI）、sdk/python 三部分
- **Estimated docs**: 7-10 concepts, 2-3 examples, 3-4 references ≈ 12-17 content docs
- **Test Requirements**:
  - **rule**: references/ 先于 concepts/examples 创建
  - **rule**: 每批 ≤ 7 文件
  - **rule**: frontmatter 完整、index.md 规范
  - **rubric** (内容质量 0-3): ≥ 2

### Task 12: E 阶段——nanobot Bundle 生成
- **Priority**: high
- **Depends**: T8
- **AC Coverage**: FR3, AC-R2, AC-R3, AC-R4, AC-R5, AC-R6
- **Scope**: 同 Task 9 流程，聚焦 Python Agent 核心（bus、cli、sdk）+ TUI/WebUI 概览
- **Estimated docs**: 5-8 concepts, 2 examples, 2-3 references ≈ 9-13 content docs
- **Test Requirements**:
  - **rule**: references/ 先于 concepts/examples 创建
  - **rule**: 每批 ≤ 7 文件
  - **rule**: frontmatter 完整、index.md 规范
  - **rubric** (内容质量 0-3): ≥ 2

### Task 13: E 阶段——opencode Bundle 生成
- **Priority**: medium
- **Depends**: T8
- **AC Coverage**: FR3, AC-R2, AC-R3, AC-R4, AC-R5, AC-R6
- **Scope**: 同 Task 9 流程，聚焦 TUI Agent、MCP 集成、插件架构、infra 模块
- **Estimated docs**: 4-6 concepts, 1-2 examples, 2-3 references ≈ 7-11 content docs
- **Test Requirements**:
  - **rule**: references/ 先于 concepts/examples 创建
  - **rule**: 每批 ≤ 7 文件
  - **rule**: frontmatter 完整、index.md 规范
  - **rubric** (内容质量 0-3): ≥ 2

### Task 14: E 阶段——pi-cli Bundle 生成
- **Priority**: medium
- **Depends**: T8
- **AC Coverage**: FR3, AC-R2, AC-R3, AC-R4, AC-R5, AC-R6
- **Scope**: 同 Task 9 流程，聚焦多包架构（ai/tui/agent）、内置 prompts、CLI 入口
- **Estimated docs**: 4-6 concepts, 1-2 examples, 2-3 references ≈ 7-11 content docs
- **Test Requirements**:
  - **rule**: references/ 先于 concepts/examples 创建
  - **rule**: 每批 ≤ 7 文件
  - **rule**: frontmatter 完整、index.md 规范
  - **rubric** (内容质量 0-3): ≥ 2

### Task 15: E 阶段——deepcode-cli Bundle 生成
- **Priority**: medium
- **Depends**: T8
- **AC Coverage**: FR3, AC-R2, AC-R3, AC-R4, AC-R5, AC-R6
- **Scope**: 同 Task 9 流程，聚焦 CLI 入口、MCP 支持、核心命令
- **Estimated docs**: 3-5 concepts, 1 example, 1-2 references ≈ 5-8 content docs
- **Test Requirements**:
  - **rule**: references/ 先于 concepts/examples 创建
  - **rule**: frontmatter 完整、index.md 规范
  - **rubric** (内容质量 0-3): ≥ 2

---

## Phase V: 验证

### Task 16: V 阶段——独立验证与修复
- **Priority**: high
- **Depends**: T9, T10, T11, T12, T13, T14, T15
- **AC Coverage**: FR4, AC-R7, AC-R8
- **Scope**:
  1. **结构检查**：所有 7 个 bundle 目录结构完整（index.md/log.md/concepts/examples/references）
  2. **Frontmatter 检查**：每个非保留 .md 文件有有效 YAML frontmatter，type 非空；根 index.md 有 okf_version
  3. **链接检查**：所有内部交叉链接（/concepts/xxx.md、/references/xxx.md 等）有效无断链
  4. **Grep API 验证**：对每个 bundle 中引用的关键类名/方法名/函数名，在源码中 Grep 验证存在性
  5. **Index 完整性**：各级 index.md 列出的文档与实际文件一致，无遗漏无多余
  6. 发现的问题逐一修复并记录
- **Output**: 验证报告（可附在 review.md 中），修复后的完整文档集
- **Test Requirements**:
  - **rule**: 0 个虚构 API（所有引用的类名/方法名 Grep 验证通过）（G4）
  - **rule**: 0 个断链
  - **rule**: frontmatter 合规率 100%
  - **rule**: index 列出文档数 = 实际内容文档数
  - **rubric** (验证彻底性 0-3): ≥ 2（API 验证覆盖每个 bundle 至少 10 个关键标识符）

---

## Phase Nav: 导航更新

### Task 17: 更新 ai-agent 分组索引
- **Priority**: high
- **Depends**: T16
- **AC Coverage**: FR5, AC-R9
- **Scope**:
  - 更新 `bundles/ai-agent/index.md` frontmatter 中的 total_bundles 和描述
  - 在知识束概览表中添加 7 个新知识束
  - 更新推荐学习路径
  - 更新生态关系图
  - 更新信源与验证统计
- **Test Requirements**:
  - **rule**: index.md 列出所有 7 个新知识束
  - **rule**: 新知识束的链接有效
  - **rule**: 统计数据（束数、文档数）与实际一致

### Task 18: 更新 bundles 总索引
- **Priority**: high
- **Depends**: T16
- **AC Coverage**: FR5, AC-R10
- **Scope**:
  - 更新 `bundles/index.md` frontmatter 的 total_bundles 和 groups
  - 更新分组导航表中 ai-agent 行的知识束数
  - 更新分组详情中 AI Agent 框架部分
  - 更新生态关系概览图
- **Test Requirements**:
  - **rule**: total_bundles 和各组束数统计正确
  - **rule**: ai-agent 分组详情包含 7 个新知识束简介

---

## Phase Review

### Task 19: 独立审查
- **Priority**: high
- **Depends**: T17, T18
- **AC Coverage**: All ACs
- **Scope**: 委派独立审查者对全部产出物进行最终审查
  - 检查所有 rule 类型 AC 的满足情况
  - 评估所有 rubric 类型 AC 是否达到阈值
  - 确认源码零修改
  - 输出 review.md
- **Test Requirements**:
  - **rule**: 所有 rule AC 有独立验证证据
  - **rule**: 所有 rubric AC 评分 ≥ 阈值
  - **rule**: review 结果为 pass
