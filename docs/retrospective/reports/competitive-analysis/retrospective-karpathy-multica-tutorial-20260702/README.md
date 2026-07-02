---
id: "retrospective-karpathy-multica-tutorial-20260702-readme"
source: "docs/knowledge/learning/karpathy-llm-coding-guidelines-tutorial.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-karpathy-multica-tutorial-20260702/README.toml"
---
# Karpathy LLM编程准则教程·Multica生态扩充复盘

> **分析对象**：基于本地 `.temp/libs/multica-ai/multica` 和 `.temp/libs/multica-ai/multica-cli` 两个开源仓库，扩充Karpathy LLM编程准则教程
> **复盘日期**：2026-07-02
> **任务类型**：外部开源项目深度学习与知识库教程完善
> **报告类型**：知识捕获执行型复盘报告

## 项目概览

### 核心指标

| 指标 | 数值 |
|------|------|
| 源仓库 | `.temp/libs/multica-ai/multica`（Multica主平台）+ `.temp/libs/multica-ai/multica-cli`（CLI Skill） |
| 学习文件数 | 8+（multica: README.zh-CN.md、docs/product-overview.md(973行)、AGENTS.md、CLAUDE.md；multica-cli: README.zh.md、SKILL.md、EXAMPLES.md、.cursor/rules/*.mdc、.claude-plugin/*.json） |
| 新增文档数 | 2（06-multica-platform.md、07-multica-cli-skill.md） |
| 更新文档数 | 2（主入口tutorial、05-resources.md） |
| 总新增行数 | 2568 行（9个文件） |
| 教程文档总数 | 8个Markdown文件（00~07） |
| 本地链接校验 | 34个链接全部通过 |
| 提交哈希 | 3692958 |

**关键发现**：本次任务成功将Karpathy四条LLM编程准则从"抽象原则"层面扩展到"真实AI Agent协作平台（Multica）上下文中"。通过深度研读multica-cli的SKILL.md（本身就是Karpathy准则的典范实践）和multica主仓库的产品全景文档，识别出一个关键洞察：**Karpathy准则不是孤立的编码技巧，而是Managed Agents平台设计哲学的核心组成部分**——multica-cli Skill对安全边界的严格把控、对副作用操作的谨慎态度、对Mention循环的防护机制，正是Think Before Coding和Surgical Changes在Agent协作领域的具象化。同时，本次任务再次遭遇Windows GBK编码问题，验证了stdin-bytes修复方案的有效性（使用Python脚本文件而非命令行-c参数传递UTF-8字节）。

### 子模块导航

| 章节 | 说明 |
|------|------|
| [execution-retrospective.md](execution-retrospective.md) | 执行过程复盘：两阶段任务（网页内容转换→本地仓库深度学习）、内容组织结构设计、编码问题修复、链接验证策略 |
| [insight-extraction.md](insight-extraction.md) | 洞察萃取：由insight-cmd Skill深度萃取 |
| [export-suggestions.md](export-suggestions.md) | 导出建议：由export-report-cmd处理 |

## 关联报告

- [retrospective-wsl-learning-plan-20260701](../retrospective-wsl-learning-plan-20260701/) — 同类先例：基于 `.temp/libs/` 本地仓库的学习教程制作
- [retrospective-tuyaopen-dev-skills-learning-20260630](../retrospective-tuyaopen-dev-skills-learning-20260630/) — 同类先例：外部开源Skill学习与知识库归档
- [karpathy-llm-coding-guidelines-tutorial.md](../../../../knowledge/learning/karpathy-llm-coding-guidelines-tutorial.md) — 源知识条目（任务产出物）
- [ai-coding-guidelines.md](../../../../../.agents/rules/ai-coding-guidelines.md) — 已整合的SpecWeave规则文件
- [insight-windows-git-encoding-20260701.md](../../../insights/insight-windows-git-encoding-20260701.md) — Windows Git编码问题（本次再次验证）
