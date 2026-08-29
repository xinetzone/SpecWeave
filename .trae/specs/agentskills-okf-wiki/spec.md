---
spec_id: agentskills-okf-wiki
created: 2026-08-29
status: draft
source_skills: [seven-concepts-cmd, source-code-to-okf-wiki]
source_dir: external/libs/ai/agentskills
target_dir: projects/awesome-okf-xs/doc/bundles/ai/ai-agent/agent-skills-spec
---

# Agent Skills 开放标准源码 OKF Wiki 教程生成

## Problem Statement

`external/libs/ai/agentskills/` 收录了 Agent Skills 开放标准官方仓库（agentskills.io，最初由 Anthropic 开发并开源），包含权威格式规范（`docs/specification.mdx`）、技能创作教程（`docs/skill-creation/` 5 篇）、客户端生态文档（`clients.mdx`、`client-implementation/`）以及 Python 参考实现（`skills-ref/`：parser/validator/prompt/cli 六模块）。这是 SpecWeave 自身 Skill 体系（`.agents/skills/`）所依赖格式的上游标准，但目前缺乏系统化中文源码级教程。

需注意与既有知识束的区分：
- `ai/ai-agent/anthropics-skills`——Anthropic 官方 Skills 库（19 个技能实例），讲"怎么用技能"
- `ai/anthropic/official-skills`——同一仓库的另一视角知识束
- **本任务**：`agentskills` 仓库——开放**标准规范** + **参考实现**，讲"格式如何定义、如何被校验"

## Users

- Skill 开发者——需要理解 SKILL.md 格式的权威规范（字段约束、命名规则、渐进式披露）
- Agent 客户端开发者——需要实现技能加载支持（规范 + skills-ref 参考实现）
- SpecWeave 贡献者——理解 `.agents/skills/` 体系的上游标准来源

## Goals

1. 生成 1 个 OKF v0.2 规范知识束 `agent-skills-spec`，覆盖规范文档与 skills-ref 参考实现两大板块
2. 所有 API 引用（类名/函数名/CLI 命令）经 Grep 级源码验证，杜绝虚构
3. 更新 `ai/ai-agent/index.md` 分组索引（30→31 束）与 `bundles/index.md` 总索引统计
4. 通过 `invoke gates.all` 质量门（UTF-8 + toctree 完整性）

## Non-Goals

- 不覆盖 `external/libs/anthropics/skills`（已有 anthropics-skills / official-skills 知识束）
- 不修改源码（external/ 下 git submodule，禁止本地修改）
- 不生成模式沉淀文档（C 阶段仅做原子提交，跨项目模式沉淀留后续任务）

## Source Scope

| 板块 | 路径 | 内容 | 权威性 |
|------|------|------|--------|
| 格式规范 | `agentskills/docs/specification.mdx` | SKILL.md 格式权威定义（frontmatter 字段、命名规则、目录约定） | **权威**（AGENTS.md 明确声明） |
| 技能创作 | `agentskills/docs/skill-creation/` | quickstart / best-practices / evaluating-skills / optimizing-descriptions / using-scripts（5 篇 mdx） | 说明性文档 |
| 客户端生态 | `agentskills/docs/clients.mdx` + `client-implementation/adding-skills-support.mdx` | 支持技能的客户端列表与客户端实现指南 | 说明性文档 |
| 参考实现 | `agentskills/skills-ref/src/skills_ref/` | parser.py / validator.py / prompt.py / models.py / cli.py / errors.py | 演示性实现（非生产 SDK） |
| 参考实现测试 | `agentskills/skills-ref/tests/` | test_parser / test_prompt / test_validator | 行为参照 |

排除：`.github/`（profile）、`.claude/`（元配置）、`docs/images/`（logo 资源）、`docs/snippets/`（展示组件）。

## Bundle 归属与命名

- **分组**：`doc/bundles/ai/ai-agent/`（"技能规范"类别，与 anthropics-skills 并列）
- **束名**：`agent-skills-spec`（避免与既有 `anthropics-skills` 混淆；束内 frontmatter/sources 标注源路径 `external/libs/ai/agentskills`）

## Functional Requirements

### FR1: R 阶段——源码事实采集
- 通读 specification.mdx（权威格式要求）、skill-creation 5 篇、clients.mdx、adding-skills-support.mdx
- 通读 skills-ref 全部 6 个源码模块与 3 个测试文件，提取可验证事实（函数签名、校验规则、frontmatter 字段约束、CLI 命令）
- 所有事实编号 F-xxx 写入 `.trae/specs/agentskills-okf-wiki/facts.md`，零推测（G1 门）

### FR2: I 阶段——架构洞察与知识地图
- 提炼 3-5 个核心洞察四元组（陈述+证据+反常识+行动）
- 设计知识地图：入门（格式概览/渐进式披露）→ 核心（规范细则/校验规则）→ 高级（参考实现/客户端集成）
- 写入 insights.md（G2 门）

### FR3: E 阶段——OKF 文档批量生成
- **信源先行**：先生成 references/（≥2 篇：规范文档信源登记、skills-ref 源码登记）
- 分批生成 concepts/（每批 ≤7 文件，预估 6-9 篇）
- 生成 examples/（预估 2 篇：创建第一个 Skill、skills-ref CLI 实战）
- **Index 最后写**：根 index.md（含 okf_version: "0.2"）+ 各子目录 index.md（无 frontmatter、含 toctree 块）
- 生成 log.md 变更日志（G3 门）

### FR4: V 阶段——独立验证
- Frontmatter 完整性检查（type/title/description/tags/generated/verified/status/stale_after/sources）
- 交叉链接使用 `/` 开头 bundle-relative 路径，无断链
- Grep 级 API 验证：文档引用的每个函数名/类名/CLI 命令在 skills-ref 源码中存在
- 规范条款与 specification.mdx 原文一致性抽查
- 运行 `invoke gates.all`（UTF-8 + toctrees），修复全部问题（G4 门）

### FR5: 导航索引更新
- `ai/ai-agent/index.md`：total_bundles 30→31，"技能规范"类新增 agent-skills-spec 表格行，toctree 追加条目
- `bundles/index.md`：总索引统计更新（束数、文档数、分组详情）

### FR6: C 阶段——原子提交
- 子模块 awesome-okf-xs 一次原子提交（新 bundle + 索引更新）
- 主仓库 SpecWeave 一次原子提交（spec 同步 + 子模块指针推进）
- 遵循 Conventional Commits，中文主体

## Non-Functional Requirements

- 正文中文撰写，英文术语首次出现括号注释
- 代码块标注语言；YAML 示例与 specification.mdx 一致；Python/CLI 示例与 skills-ref 源码一致
- 每个概念/示例文档结尾含"## 相关概念"章节
- 概念文档按学习路径编号（00-xxx.md 起）
- stale_after 统一为生成日期 + 1 年；verified 标注 `process:seven-concepts-v`

## Constraints

- 源码为 git submodule，只读
- 输出位于 `projects/awesome-okf-xs/doc/bundles/ai/ai-agent/agent-skills-spec/`
- 遵循 awesome-okf-xs AGENTS.md 启动协议、frontmatter 规范、toctree 完整性要求
- 遵循 source-code-to-okf-wiki 五阶段工作流与 G1-G5 质量门（seven-concepts-cmd 知识沉淀场景 R→I→E 链路编排）

## Acceptance Criteria

### Rules (binary verification)

- **AC-R1**: `agent-skills-spec` bundle 创建于 `doc/bundles/ai/ai-agent/` 下，含 index.md、log.md、concepts/、examples/、references/ 标准结构
- **AC-R2**: 根 index.md 含 `okf_version: "0.2"`；子目录 index.md 无 frontmatter 且含 `{toctree}` 块
- **AC-R3**: 所有非保留 .md 文件含有效 YAML frontmatter，type 字段非空
- **AC-R4**: references/ 先于 concepts/examples 生成；各级 index 最后生成
- **AC-R5**: 文档引用的函数名/类名/CLI 命令经 Grep 验证存在于 skills-ref 源码
- **AC-R6**: 内部交叉链接为 `/` 开头 bundle-relative 路径，无断链
- **AC-R7**: `ai/ai-agent/index.md` 与 `bundles/index.md` 均已更新
- **AC-R8**: `invoke gates.all` 通过
- **AC-R9**: external/ 目录零变更；子模块与主仓库各完成 1 次原子提交

### Rubrics (evaluative quality)

- **AC-RU1: 规范覆盖度** (0-3)：3=覆盖 SKILL.md 格式全部权威要求（字段/命名/目录/渐进式披露）+ 校验规则 + 参考实现；2=覆盖主要方面；阈值 ≥2
- **AC-RU2: 溯源完整性** (0-3)：3=每个技术声明可追溯到 facts.md 编号事实与 references/ 信源；阈值 ≥2
- **AC-RU3: 代码示例质量** (0-3)：3=示例可运行、与规范/源码 API 完全一致；阈值 ≥2

## Dependencies

- source-code-to-okf-wiki 技能 Prompt 模板
- awesome-okf-xs frontmatter 规范与 check-toctrees 门禁
- 既有 anthropics-skills 知识束（边界参照，避免内容重复）
