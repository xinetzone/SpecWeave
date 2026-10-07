---
id: "skills-index"
title: ".agents/skills/ 目录索引"
source: ".agents/skills/README.md"
---
# .agents/skills/ 目录索引

本目录存放 Skill 定义。Skill 分为：**完整 Skill**（含自动化操作能力）、**命令集门面**（对指令集的轻量封装）、**脚本命令门面**（对高频自动化脚本的封装）、**工作流门面**（对方法论模式的触发封装）等。

## Skill 结构规范

```
.agents/skills/<skill-name>/
├── SKILL.md          # 必需：技能定义（YAML frontmatter + Markdown）
├── scripts/          # 可选：可执行脚本
├── references/       # 可选：参考文档（按需加载）
└── assets/           # 可选：模板、图标等资源
```

SKILL.md 必须包含五要素：

1. **Trigger-Ready Description**：触发就绪描述（frontmatter 中的 description）
2. **Decision Tree**：方案决策树（多方案时必须提供）
3. **Progressive Disclosure**：渐进式披露（正文 ≤500 行，低频内容引用外部文档）
4. **Why-Explanation**：设计意图解释（关键规则后说明为什么）
5. **Safety Checklist**：安全检查清单（写操作必须包含 dry-run/幂等/验证）

## 发现机制（L0-L3）

- **L0 入口**：[../ONBOARDING.md](../ONBOARDING.md)（入门快速路由）
- **L1 索引**：[../capability-registry.md](../capability-registry.md)（全量能力索引）
- **L2 匹配**：关键词/触发词语义匹配
- **L3 详情**：各 SKILL.md（详细操作指南）；示例技能 [load-specweave/SKILL.md](load-specweave/SKILL.md)

## 创建新 Skill

1. 复制 SKILL 模板到 `<skill-name>/SKILL.md`，遵循五要素模型。
2. 对照规范验证质量，更新本索引与能力索引。完整技能清单与开发补充规范见 SpecWeave 开源仓库。