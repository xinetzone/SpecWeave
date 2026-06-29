---
id = "specweave-skills-index"
date = "2026-06-29"
type = "index"
source = "AGENTS.md#能力索引;.agents/capability-registry.md"
---

# .agents/skills/ 目录索引

本目录存放 SpecWeave 项目中所有 Skill 定义。Skill 分为两类：

- **完整Skill**：包含完整的自动化操作能力（脚本、MCP工具调用等），可独立完成任务
- **命令门面**：对现有命令集的轻量封装，提供触发词、决策树、快速开始和安全检查，提升命令集的可发现性

## Skill 列表

### 命令集门面（5个）

| Skill名称 | 类型 | 对应命令集 | 核心触发词 | SKILL.md路径 |
|-----------|------|-----------|-----------|-------------|
| retrospective-cmd | 命令门面 | 复盘 | 复盘、retrospective、回顾、总结经验、项目总结 | [retrospective-cmd/SKILL.md](retrospective-cmd/SKILL.md) |
| insight-cmd | 命令门面 | 洞察 | 洞察、insight、分析问题、诊断问题、找原因、根因分析 | [insight-cmd/SKILL.md](insight-cmd/SKILL.md) |
| export-report-cmd | 命令门面 | 导出报告 | 导出、export、生成报告、导出报告、输出报告 | [export-report-cmd/SKILL.md](export-report-cmd/SKILL.md) |
| atomization-cmd | 命令门面 | 原子化 | 原子化、atomization、拆分文件、拆分文档、整理文件 | [atomization-cmd/SKILL.md](atomization-cmd/SKILL.md) |
| atomic-commit-cmd | 命令门面 | 原子提交 | 提交、commit、原子提交、提交代码、保存更改 | [atomic-commit-cmd/SKILL.md](atomic-commit-cmd/SKILL.md) |

### 完整Skill（1个）

| Skill名称 | 类型 | 功能描述 | 核心触发词 | SKILL.md路径 |
|-----------|------|---------|-----------|-------------|
| forum-posting | 完整Skill | Discourse论坛自动化操作（发帖、编辑、回复、清理草稿等），支持双方案（MCP+Playwright脚本） | 发帖、编辑帖子、回复帖子、forum.trae.cn、forum-bot | [forum-posting/SKILL.md](forum-posting/SKILL.md) |

## 模板

| 文件 | 用途 | 路径 |
|------|------|------|
| SKILL-TEMPLATE.md | Skill创建模板，包含五要素模型骨架 | [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md) |

## Skill 结构规范

每个Skill遵循以下目录结构（遵循 vendor skill-creator 规范）：

```
.agents/skills/<skill-name>/
├── SKILL.md          # 必需：技能定义（YAML frontmatter + Markdown）
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档（按需加载）
└── assets/           # 可选：模板、图标等资源
```

SKILL.md 必须包含五要素：
1. **Trigger-Ready Description**：触发就绪描述（YAML frontmatter 中的 description）
2. **Decision Tree**：方案决策树（多方案时必须提供）
3. **Progressive Disclosure**：渐进式披露（正文≤500行，低频内容引用外部文档）
4. **Why-Explanation**：设计意图解释（关键规则后用 `> **为什么？**` 说明）
5. **Safety Checklist**：安全检查清单（写操作必须包含dry-run/幂等/验证）

## 发现机制（L0-L3）

Skill通过四层发现机制被Agent发现：

```mermaid
flowchart LR
    L0["L0: ONBOARDING.md<br/>入门快速路由"] --> L1["L1: capability-registry.md<br/>全量能力索引"]
    L1 --> L2["L2: 语义匹配<br/>关键词/触发词匹配"]
    L2 --> L3["L3: 本目录 SKILL.md<br/>详细操作指南"]
```

- **L0 入口**：[ONBOARDING.md](../ONBOARDING.md) — 新会话快速开始
- **L1 索引**：[capability-registry.md](../capability-registry.md) — 全量能力静态索引
- **L3 详情**：各SKILL.md — 具体操作步骤与安全检查

## 创建新 Skill

1. 复制 [SKILL-TEMPLATE.md](SKILL-TEMPLATE.md) 到 `<skill-name>/SKILL.md`
2. 阅读 [skill-development.md](../rules/skill-development.md) 了解SpecWeave补充规范
3. 阅读 vendor [skill-creator/SKILL.md](../../vendor/flexloop/apps/chaos/.agents/skills/skill-creator/SKILL.md) 了解权威方法论
4. 完成后运行 `python .agents/scripts/check-skill-quality.py <skill-name>` 验证质量
5. 更新本索引和 [capability-registry.md](../capability-registry.md)

## Changelog

- **v1.0** (2026-06-29): 初始版本，包含5个命令集门面 + 1个完整Skill + SKILL-TEMPLATE模板。基于Skill发现协议SOP的P0实施路径创建。
