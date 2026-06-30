---
version: "1.4"
last_updated: "2026-06-30"
generator: "manual"
schema: "specweave-capability-registry-v1"
note: "初始版本手动维护，后续由 generate-capability-registry.py 自动生成"
layer: "L1"
counts:
  scripts: 30
  skills: 13
  commands: 6
  workflows: 3
  protocols: 7
  rules: 7
  knowledge: 4
---

# SpecWeave 能力注册中心

> ⚠️ **本文件是L1索引层**，遵循[渐进式披露三层架构](capabilities/ARCHITECTURE.md)：
> - L0：[ONBOARDING.md](ONBOARDING.md)（入口速查，<100行，<30秒读完）
> - L1：本文件（全量能力索引，1-3分钟读完）
> - L2：[commands/](commands/)、[protocols/](protocols/)、[rules/](rules/) 等目录下的完整规范文档（按需阅读）
>
> **如何使用**：
> - Agent 在新会话中通过本文件快速了解全部能力
> - 按功能分类组织，先定位类别，再找具体工具
> - 每个条目包含：名称、用途、触发关键词、安全等级、路径
> - 不确定用什么？先看底部"快速查找指南"

---

## 脚本索引（.agents/scripts/）

### ✅ 检查/验证类（Check & Validate）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| check-links.py | Markdown链接有效性校验与自动修复（本地文件+外部URL） | "检查链接"、"修复链接"、"断链" | 读+修复 | ✅ | [scripts/check-links.py](scripts/check-links.py) |
| check-skill-quality.py | Skill质量检查：验证SKILL.md是否符合五要素模型规范 | "检查Skill"、"验证Skill质量"、"五要素检查" | 只读 | ✅ | [scripts/check-skill-quality.py](scripts/check-skill-quality.py) |
| check-stage-guardrails.py | 阶段守卫日志离线分析：检测SG-LOG/PDR-LOG的拦截/跳转/缺失异常 | "分析阶段守卫日志"、"SG日志分析"、"检查SG-LOG" | 只读 | ✅ | [scripts/check-stage-guardrails.py](scripts/check-stage-guardrails.py) |
| check-stage-guardrail-runtime.py | 阶段守卫运行时强制执行与拦截演示 | "阶段守卫运行时"、"SG运行时检查" | 只读 | ✅ | [scripts/check-stage-guardrail-runtime.py](scripts/check-stage-guardrail-runtime.py) |
| check-source-traceability.py | 派生产物溯源检查：扫描frontmatter的source字段，建立反向索引 | "溯源检查"、"派生产物检查"、"source字段检查" | 只读 | ✅ | [scripts/check-source-traceability.py](scripts/check-source-traceability.py) |
| check-move.py | 文件移动路径迁移工具：移动文件后批量修正引用路径 | "移动文件"、"迁移路径"、"修复引用路径" | 写 | ✅ | [scripts/check-move.py](scripts/check-move.py) |
| check-duplication.py | 跨文件重复代码检测 | "检查重复代码"、"重复检测" | 只读 | ✅ | [scripts/check-duplication.py](scripts/check-duplication.py) |
| check-action-items.py | 扫描复盘报告中的行动计划表，提取待办清单 | "检查行动项"、"待办清单"、"行动项状态" | 只读 | ✅ | [scripts/check-action-items.py](scripts/check-action-items.py) |
| check-atomization-coverage.py | 原子化前置检查：搜索模式库判断新洞察是否已被覆盖 | "原子化检查"、"模式覆盖检查"、"创建模式前检查" | 只读 | ✅ | [scripts/check-atomization-coverage.py](scripts/check-atomization-coverage.py) |
| check-atomization-duplication.py | 原子化后内容一致性检查：检测源文件残留的深度分析内容 | "原子化一致性检查"、"残留内容检查" | 只读 | ✅ | [scripts/check-atomization-duplication.py](scripts/check-atomization-duplication.py) |
| check-pattern-quality.py | 方法论模式文档质量检查 | "模式质量检查"、"验证模式文档" | 只读 | ✅ | [scripts/check-pattern-quality.py](scripts/check-pattern-quality.py) |
| check-report-categorization.py | 复盘报告归类验证：检查reports/下未归类报告 | "报告归类"、"检查报告分类" | 只读 | ✅ | [scripts/check-report-categorization.py](scripts/check-report-categorization.py) |
| check-retrospective-index.py | Retrospective体系索引一致性检查 | "索引一致性"、"检查复盘索引" | 只读 | ✅ | [scripts/check-retrospective-index.py](scripts/check-retrospective-index.py) |
| repo-check.py | 综合检查统一入口（整合filename/gitignore/mermaid/vendor/roles五项检查） | "综合检查"、"多项目检查" | 只读 | ✅ | [scripts/repo-check.py](scripts/repo-check.py) |
| spec-tool.py | Spec工具统一入口（整合check/format两项检查） | "Spec检查"、"Spec格式" | 只读 | ✅ | [scripts/spec-tool.py](scripts/spec-tool.py) |

> **向后兼容包装脚本**（以下脚本为薄包装层，转发到 repo-check.py / spec-tool.py 对应子命令）：
> - `check-gitignore.py` → `repo-check.py gitignore`
> - `check-vendor.py` → `repo-check.py vendor`
> - `check-filename-convention.py` → `repo-check.py filename`
> - `check-mermaid.py` → `repo-check.py mermaid`
> - `check-role-permissions.py` → `repo-check.py roles`
> - `check-spec-consistency.py` → `spec-tool.py check`
> - `check-spec-format.py` → `spec-tool.py format`

### 🔧 生成/构建类（Generate & Build）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| docgen.py | 文档索引与看板生成统一工具（nav/dashboard/apps/all 子命令），标记区域覆盖，幂等 | "生成导航"、"生成看板"、"生成应用索引"、"更新文档索引"、"docgen" | 写（标记区域） | ✅ Git-based预览 | [scripts/docgen.py](scripts/docgen.py) |
| finalize-atomization.py | 原子化一键收尾：断链修复+导航更新+看板刷新，支持dry-run | "收尾原子化"、"原子化完成"、"断链修复导航更新" | 写 | ✅ | [scripts/finalize-atomization.py](scripts/finalize-atomization.py) |
| generate-tests.py | 测试骨架自动生成 | "生成测试"、"测试骨架" | 写 | ✅ | [scripts/generate-tests.py](scripts/generate-tests.py) |
| generate-sg-dashboard.py | 阶段守卫日志聚合可视化仪表盘（HTML输出） | "SG仪表盘"、"日志可视化"、"阶段守卫仪表盘" | 写 | ✅ | [scripts/generate-sg-dashboard.py](scripts/generate-sg-dashboard.py) |
| build-ref-index.py | 构建文件引用反向索引：{目标文件: [引用文件列表]} | "引用索引"、"反向索引"、"谁引用了这个文件" | 只读 | ✅ | [scripts/build-ref-index.py](scripts/build-ref-index.py) |
| agents.py | 新项目脚手架初始化工具（init子命令） | "初始化项目"、"项目脚手架" | 写 | ❌ | [scripts/agents.py](scripts/agents.py) |

> **向后兼容包装脚本**（已整合进 docgen.py）：
> - `generate-nav.py` → `docgen.py nav`
> - `generate-dashboard.py` → `docgen.py dashboard`
> - `generate-apps-index.py` → `docgen.py apps`

### 📊 统计/分析类（Stats & Analysis）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| pattern-maturity.py | 模式成熟度管理（verify/upgrade/batch-upgrade子命令） | "模式成熟度"、"升级成熟度" | 只读+建议 | ✅ | [scripts/pattern-maturity.py](scripts/pattern-maturity.py) |
| pattern-maturity-stats.py | 模式成熟度统计报告 | "成熟度统计"、"模式统计" | 只读 | ✅ | [scripts/pattern-maturity-stats.py](scripts/pattern-maturity-stats.py) |
| scan-maturity-upgrades.py | 扫描可升级成熟度的模式 | "扫描升级"、"成熟度扫描" | 只读 | ✅ | [scripts/scan-maturity-upgrades.py](scripts/scan-maturity-upgrades.py) |

### 🤖 自动化操作类（Automation）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| forum-bot.py | Discourse论坛（forum.trae.cn）自动化脚本 | "论坛脚本"、"forum-bot"、"发帖脚本" | 读+写 | ✅ | [scripts/forum-bot.py](scripts/forum-bot.py) |
| trae_edge_case_handler.py | Trae IDE边界情况处理（论坛/工具链/Work等） | "Trae边界处理"、"edge case" | 读+写 | ✅ | [scripts/trae_edge_case_handler.py](scripts/trae_edge_case_handler.py) |

### 🔧 工具/一次性修复类（Utilities）

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| fix-flexloop-reverse-links.py | 修复flexloop子模块反向链接（一次性工具） | "修复flexloop链接" | 写 | ❌ | [scripts/fix-flexloop-reverse-links.py](scripts/fix-flexloop-reverse-links.py) |

### 🚀 CI/流水线

| 脚本名 | 用途 | 触发关键词 | 安全等级 | 支持dry-run | 路径 |
|--------|------|-----------|---------|------------|------|
| ci-check.ps1 | Windows CI综合检查脚本（8步流水线：检查+文档生成） | "CI检查"、"提交前检查"、"全量检查"、"pre-commit" | 读+写（标记区域） | ✅ Git-based预览 | [scripts/ci-check.ps1](scripts/ci-check.ps1) |
| ci-check.sh | Linux/Mac CI综合检查脚本（8步流水线） | "CI检查"、"提交前检查"、"全量检查" | 读+写（标记区域） | ✅ Git-based预览 | [scripts/ci-check.sh](scripts/ci-check.sh) |

> **共享库**（非直接执行脚本，被其他脚本import）：
> - `lib/` — 共享工具库（CLI输出、frontmatter解析、Markdown处理、链接修复、模式扫描等）
> - `constants.py` — 脚本共用常量定义
> - `config/false-positive-rules.toml` — 误报规则配置

---

## Skill索引（.agents/skills/）

### 完整Skill（2个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| forum-posting | "发帖"、"编辑帖子"、"回复帖子"、"跟帖"、"清理草稿"、"读取帖子"、"操作forum.trae.cn"、"Discourse论坛" | 2（forum-bot.py脚本 + integrated_browser MCP） | v1.1.0 | [skills/forum-posting/SKILL.md](skills/forum-posting/SKILL.md) |
| home-assistant | "智能家居"、"控制设备"、"查询状态"、"home assistant"、"ha_api" | 1（REST API） | v1.0.0 | [skills/home-assistant/SKILL.md](skills/home-assistant/SKILL.md) |

### 命令集门面（6个）

| Skill名 | 触发词 | 方案数 | 版本 | 路径 |
|---------|--------|-------|------|------|
| retrospective-cmd | "复盘"、"retrospective"、"回顾"、"总结经验"、"项目总结"、"阶段回顾" | 3（标准/轻量/故障复盘） | v1.2.1 | [skills/retrospective-cmd/SKILL.md](skills/retrospective-cmd/SKILL.md) |
| insight-cmd | "洞察"、"insight"、"分析问题"、"萃取洞察"、"根因分析"、"问题诊断"、"为什么" | 3（数据驱动/根因诊断/萃取洞察） | v1.2.1 | [skills/insight-cmd/SKILL.md](skills/insight-cmd/SKILL.md) |
| export-report-cmd | "导出报告"、"export"、"生成报告"、"导出文档"、"归档" | 2（Markdown/JSON） | v1.2.1 | [skills/export-report-cmd/SKILL.md](skills/export-report-cmd/SKILL.md) |
| atomization-cmd | "原子化"、"拆分文件"、"atomize"、"拆分大文档"、"文档拆分" | 3（文档原子化/一键收尾/预检） | v1.2.1 | [skills/atomization-cmd/SKILL.md](skills/atomization-cmd/SKILL.md) |
| atomic-commit-cmd | "提交"、"commit"、"原子提交"、"代码提交"、"git commit" | 3（标准/快速/CI检查） | v1.2.1 | [skills/atomic-commit-cmd/SKILL.md](skills/atomic-commit-cmd/SKILL.md) |
| mermaid-cmd | "mermaid"、"流程图"、"时序图"、"状态图"、"画个图"、"图表"、"架构图"、"思维导图"、"画流程图" | 3（快速生成/检查修复/复杂协作） | v1.1.0 | [skills/mermaid-cmd/SKILL.md](skills/mermaid-cmd/SKILL.md) |

### 脚本命令门面（5个）

| Skill名 | 触发词 | 对应脚本 | 版本 | 路径 |
|---------|--------|---------|------|------|
| link-check-cmd | "链接检查"、"检查链接"、"断链"、"链接修复"、"fix links"、"check links"、"验证链接"、"死链" | check-links.py + lib/link_fixer.py | v1.0.0 | [skills/link-check-cmd/SKILL.md](skills/link-check-cmd/SKILL.md) |
| atomization-finalize-cmd | "原子化收尾"、"finalize atomization"、"文档拆分完成"、"文件移动后处理"、"断链修复导航更新"、"一键收尾" | finalize-atomization.py | v1.0.0 | [skills/atomization-finalize-cmd/SKILL.md](skills/atomization-finalize-cmd/SKILL.md) |
| docgen-cmd | "生成导航"、"更新导航"、"docgen"、"更新README"、"刷新看板"、"生成文档索引"、"应用清单" | docgen.py | v1.0.0 | [skills/docgen-cmd/SKILL.md](skills/docgen-cmd/SKILL.md) |
| ci-check-cmd | "CI检查"、"提交前检查"、"综合检查"、"ci-check"、"流水线检查"、"提交门禁"、"全量检查"、"跑一下CI"、"pre-commit"、"预检" | ci-check.ps1 + ci-check.sh | v1.0.0 | [skills/ci-check-cmd/SKILL.md](skills/ci-check-cmd/SKILL.md) |
| check-duplication-cmd | "重复代码"、"重复检查"、"代码重复"、"check-duplication"、"重复检测"、"提取共享库"、"DRY检查"、"脚本重复" | check-duplication.py + lib/ | v1.0.0 | [skills/check-duplication-cmd/SKILL.md](skills/check-duplication-cmd/SKILL.md) |

> **Skill类型说明**：
> - **完整Skill**：包含完整双方案实现、工具函数、详细步骤，可独立完成复杂任务
> - **命令集门面**：对 `.agents/commands/` 命令集的轻量封装，提供触发词、决策树、快速开始和安全检查
> - **脚本命令门面**：对 `.agents/scripts/` 高频自动化脚本的封装，提供参数说明、dry-run/预览机制、幂等性说明和错误处理

---

## 命令集索引（.agents/commands/）

| 命令 | ID | 用途 | 触发词 | 关联自我演进模块 | 路径 |
|------|----|------|--------|----------------|------|
| 复盘 | retrospective | 项目复盘流程，生成复盘报告与改进建议 | "复盘"、"retrospective"、"回顾"、"总结经验" | 自我复盘 (self-retrospective) | [commands/retrospective.md](commands/retrospective.md) |
| 洞察 | insight | 数据分析与问题诊断，识别优化机会与异常 | "洞察"、"insight"、"分析问题"、"萃取洞察" | 自我洞察 (self-insight) | [commands/insight.md](commands/insight.md) |
| 导出报告 | export-report | 结构化报告导出，支持多格式与归档 | "导出报告"、"export"、"生成报告" | 自我复盘 (self-retrospective) | [commands/export-report.md](commands/export-report.md) |
| 原子化 | atomization | 文档与代码的原子化拆分，确保单一职责 | "原子化"、"拆分文件"、"atomize"、"拆分大文档" | 自我萃取 (self-extraction) | [commands/atomization.md](commands/atomization.md) |
| 原子提交 | atomic-commit | Git原子化提交规范，确保单次提交单一职责 | "提交"、"commit"、"原子提交" | 自我迭代 (self-iteration) | [commands/atomic-commit.md](commands/atomic-commit.md) |
| Mermaid图表管理 | mermaid | Mermaid图表生成、解析、检查、修复与协作管理 | "mermaid"、"流程图"、"时序图"、"画个图"、"架构图" | 自我管理 (self-management) | [commands/mermaid.md](commands/mermaid.md) |

完整设计理念和执行流程见 [commands/README.md](commands/README.md)。

---

## 工作流索引（.agents/workflows/）

| 工作流 | 适用场景 | 参与角色 | 路径 |
|--------|---------|---------|------|
| 功能开发（feature-development） | 新功能、功能扩展、功能重构三路径 | 全部角色 | [workflows/feature-development.md](workflows/feature-development.md) |
| 代码审查（code-review） | PR审查、代码质量检查 | developer, reviewer, orchestrator | [workflows/code-review.md](workflows/code-review.md) |
| 测试流程（testing） | 测试执行、用例编写、覆盖率验证 | tester, developer, reviewer | [workflows/testing.md](workflows/testing.md) |

完整工作流定义和角色参与表见 [workflows/README.md](workflows/README.md)。

---

## 协议索引（.agents/protocols/）

| 协议 | 用途 | 路径 |
|------|------|------|
| 会话启动协议（Onboarding） | L0-L2三层认知建立流程、设计理由、上下文恢复 | [protocols/onboarding-protocol.md](protocols/onboarding-protocol.md) |
| 任务交接（handoff） | 智能体间任务转移规范 | [protocols/handoff.md](protocols/handoff.md) |
| 消息传递（messaging） | 智能体间通信机制 | [protocols/messaging.md](protocols/messaging.md) |
| 冲突解决（conflict-resolution） | 分歧仲裁流程 | [protocols/conflict-resolution.md](protocols/conflict-resolution.md) |
| 前置文档强制读取（PDR） | 必读文档清单与确认机制 | [protocols/pre-document-reading.md](protocols/pre-document-reading.md) |
| 临时依赖管理 | .temp/ 依赖存放与清理 | [protocols/dependency-management.md](protocols/dependency-management.md) |
| 应用开发生命周期 | .temp/暂存 → apps/稳定迁移 | [protocols/app-development-workflow.md](protocols/app-development-workflow.md) |

---

## 规则体系索引（.agents/rules/）

| 规则 | 用途 | 适用角色 | 路径 |
|------|------|---------|------|
| 阶段守卫（stage-guardrails） | 阶段边界定义、跨阶段拦截、SG-LOG规范 | 全部角色 | [rules/stage-guardrails.md](rules/stage-guardrails.md) |
| Skill开发规范（skill-development） | SpecWeave主权区Skill开发补充规范 | developer, reviewer | [rules/skill-development.md](rules/skill-development.md) |
| 硬编码识别标准 | 8大类硬编码定义与检测要点 | developer, reviewer | [rules/identification-standards.md](rules/identification-standards.md) |
| 硬编码允许场景与审批 | 允许场景清单、例外审批流程 | developer, reviewer, architect | [rules/allowable-scenarios.md](rules/allowable-scenarios.md) |
| 硬编码替代方案指南 | 7种替代方案实施指南 | developer | [rules/alternatives-guide.md](rules/alternatives-guide.md) |
| 检测与报告机制 | 三层检测体系 | developer, reviewer, orchestrator | [rules/detection-and-reporting.md](rules/detection-and-reporting.md) |
| 执行与验证规则 | 6条可执行治理规则 | 全部角色 | [rules/enforcement-guidelines.md](rules/enforcement-guidelines.md) |

完整规则体系见 [rules/README.md](rules/README.md)。

---

## 知识参考索引（docs/）

| 知识库 | 用途 | 触发关键词 | 安全等级 | 路径 |
|--------|------|-----------|---------|------|
| 技术知识库（knowledge） | 操作指南、排障经验、最佳实践、VENDOR集成方案 | "知识库"、"最佳实践"、"怎么操作"、"排障" | 只读 | [../docs/knowledge/README.md](../docs/knowledge/README.md) |
| 复盘模式库（patterns） | 可复用架构/代码/方法论模式、资产清单 | "模式库"、"复用模式"、"有没有现成方案" | 只读 | [../docs/retrospective/patterns/README.md](../docs/retrospective/patterns/README.md) |
| 开发规范（standards） | 代码风格、提交规范、Markdown规范、测试要求 | "开发规范"、"代码风格"、"提交规范"、"测试要求" | 只读 | [../docs/development-standards.md](../docs/development-standards.md) |
| 复盘体系（retrospective） | 复盘报告、洞察报告、经验萃取 | "复盘报告"、"经验总结"、"回顾文档" | 只读 | [../docs/retrospective/README.md](../docs/retrospective/README.md) |

---

## 快速查找指南

按场景快速定位：

```
我要...
├─ 检查链接是否有效/修复断链 → link-check-cmd Skill → check-links.py --fix
├─ 提交前做CI全量检查 → ci-check-cmd Skill → ci-check.ps1 / ci-check.sh
├─ 快速检查（仅关键阻断项） → ci-check-cmd Skill §5.2 快速模式
├─ 把大文档拆成小文件 → atomization-cmd Skill → finalize-atomization.py收尾
├─ 原子化后一键收尾 → atomization-finalize-cmd Skill（断链+导航+看板）
├─ 更新文档导航/看板/应用清单 → docgen-cmd Skill → docgen.py (nav/dashboard/apps/all)
├─ 检查脚本重复代码/提取共享库 → check-duplication-cmd Skill → check-duplication.py
├─ 创建一个新Skill → 读skill-development.md + vendor skill-creator
├─ 操作论坛帖子 → forum-posting Skill
├─ 控制智能家居设备 → home-assistant Skill
├─ 做项目复盘 → retrospective-cmd Skill
├─ 从执行中萃取洞察 → insight-cmd Skill
├─ 导出正式报告 → export-report-cmd Skill
├─ 原子化Git提交 → atomic-commit-cmd Skill
├─ 创建/检查/修复Mermaid图表 → mermaid-cmd Skill → mermaid命令集
├─ Mermaid复杂架构图协作 → team-mermaid专项团队
├─ 生成测试用例 → generate-tests.py
├─ 检查Skill是否符合五要素 → check-skill-quality.py
├─ 分析阶段守卫日志 → check-stage-guardrails.py / generate-sg-dashboard.py
├─ 查知识库/最佳实践 → docs/knowledge/
├─ 查可复用模式 → docs/retrospective/patterns/
├─ 查开发规范 → docs/development-standards.md
└─ 了解有哪些角色/模块/协议 → 读AGENTS.md索引表
```

---

## 更新说明

- **v1.4** (2026-06-30): 完成第一批5个高频脚本Skill化，Skill索引从7个增至13个。新增：link-check-cmd（链接检查/修复）、atomization-finalize-cmd（原子化一键收尾）、docgen-cmd（文档导航/看板生成）、ci-check-cmd（CI综合检查）、check-duplication-cmd（重复代码检测）。Skill分类扩展为三类（完整Skill/命令集门面/脚本命令门面）；补充遗漏的home-assistant完整Skill；更新脚本dry-run标注和安全等级（docgen/finalize-atomization/ci-check标注Git-based预览机制）；快速查找指南全面更新为Skill路由模式。
- **v1.3** (2026-06-30): 新增Mermaid图表管理能力注册：mermaid-cmd Skill（命令门面）、mermaid命令集、team-mermaid专项团队；更新计数（skills:7, commands:6）；快速查找指南补充Mermaid相关条目。
- **v1.2** (2026-06-30): 新增知识参考索引区块（docs/knowledge、docs/retrospective/patterns、docs/development-standards、docs/retrospective），完善L0→L1引用链；快速查找指南补充知识库入口。
- **v1.1** (2026-06-30): 添加三层架构声明，明确本文件为L1索引层；新增会话启动协议条目；修正计数（protocols: 7, rules: 7）。
- **v1.0** (2026-06-29): 初始版本，手动创建。基于实际目录扫描整理，覆盖scripts/skills/commands/workflows四大类能力。
- **待实现**：`generate-capability-registry.py` 自动生成脚本，将在后续版本中实现自动扫描与本文件更新。
