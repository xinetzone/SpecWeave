---
source: "agent-skills-open-standard-wiki.md#十五快速参考卡"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/14-quick-reference.toml"
id: "agent-skills-wiki-quick-reference"
title: "My Skill"
---
## 十五、快速参考卡

### SKILL.md 最小模板

````markdown
---
name: my-skill
description: Brief description of what this skill does and when to use it.
---

# My Skill

## Instructions
Step-by-step instructions here...

## Gotchas
- Common pitfall 1
- Common pitfall 2

## Scripts
- `scripts/example.py` — What it does
````

### 验证命令速查

```bash
# 验证技能
skills-ref validate path/to/skill

# 查看属性
skills-ref read-properties path/to/skill

# 生成提示
skills-ref to-prompt path/to/skill
```

### 名称规则速记

- ✅ `my-skill`、`pdf-processing`、`数据处理`（中文小写）
- ❌ `MySkill`（大写）、`-my-skill`（开头连字符）、`my--skill`（连续连字符）、`my_skill`（下划线）
- 📏 最大 64 字符
- 📁 必须与文件夹名一致

### Description 写作检查清单

- [ ] 使用命令式语气 "Use when..."
- [ ] 说明做什么 + 何时触发
- [ ] 包含关键词变体（即使没有显式提到领域名称）
- [ ] 1024 字符以内
- [ ] 不模糊、不宽泛

### 脚本设计检查清单

- [ ] 无交互式提示
- [ ] 有 `--help` 文档
- [ ] 错误消息清晰有用
- [ ] 结构化输出（JSON 优先）
- [ ] 数据→stdout，诊断→stderr
- [ ] 幂等性
- [ ] 固定版本依赖
