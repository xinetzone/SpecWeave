---
id: "agent-skills-wiki-project-comparison"
source: "agent-skills-open-standard-wiki.md#十二与本项目现有-skill-体系的对比"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/01-agent-protocols-interfaces/agent-skills-wiki/11-project-comparison.toml"
---
## 十二、与本项目现有 Skill 体系的对比

### 12.1 对齐情况

我们当前的 Skill 体系（位于 [.agents/skills/](../../../../../.agents/skills/README.md)）与 Agent Skills 开放标准高度对齐：

| 开放标准特性 | 本项目状态 | 位置 |
|------------|----------|------|
| SKILL.md 核心文件 | ✅ 已实现 | 每个技能目录下 |
| name/description frontmatter | ✅ 已实现 | SKILL.md 头部 |
| scripts/ 目录 | ✅ 已实现 | 如 [link-check-cmd](../../../../../.agents/skills/link-check-cmd/) |
| references/ 目录 | ✅ 已实现 | 如各技能的参考文档 |
| 渐进式披露理念 | ✅ 已实现 | [progressive-context-disclosure.md](../../../../retrospective/patterns/methodology-patterns/ai-collaboration/progressive-context-disclosure.md) |
| 五要素模型 | ✅ 已扩展 | [skill-five-elements-model.md](../../../../retrospective/patterns/methodology-patterns/ai-collaboration/skill-five-elements-model.md) |

### 12.2 本项目扩展特性

我们在开放标准基础上做了有价值的扩展：

| 扩展特性 | 说明 |
|---------|------|
| **版本号管理** | SKILL.md 支持 `version` 字段（TOML frontmatter） |
| **五要素质量检查** | 20 项质量门禁检查体系 |
| **决策树+CMD-LOG** | 技能内决策树和执行日志规范 |
| **能力注册中心** | L0/L1/L2 三层架构的能力注册表 |
| **原子提交集成** | Skill 使用与原子提交规范集成 |

### 12.3 可以借鉴的改进点

基于开放标准和我们源码分析，以下方面可以考虑对齐：

| 改进点 | 开放标准要求 | 当前状态 |
|--------|------------|---------|
| **name 字符验证** | 小写字母+数字+连字符，与目录名严格匹配 | 部分技能可能不完全符合 |
| **description 长度限制** | 硬限制 1024 字符 | 未强制限制 |
| **非交互脚本设计** | 所有脚本禁止交互式提示 | 已有要求但未系统化验证 |
| **结构化输出约定** | stdout 数据/stderr 诊断分离 | 部分脚本已实现 |
| **evals/ 测试目录** | 每个技能可带质量评估用例 | 尚未系统化建立 |
| **skills-ref 验证集成** | 官方验证工具 | 可集成到 CI 流水线 |

### 12.4 国际化支持说明

**重要发现**：通过阅读 skills-ref 源码和测试用例，我们确认 name 字段**支持 Unicode 国际字符**（中文、俄文等），而不仅是 ASCII 小写字母。这与我们之前的理解略有不同。

源码中的实际验证逻辑（[validator/ 包（✅已拆分）](../../../../../.agents/scripts/mdi/validator/__init__.py)，核心逻辑在 [core.py](../../../../../.agents/scripts/mdi/validator/core.py)）使用 `c.isalnum()`，在 Python 中这对 Unicode 字母返回 True。测试用例明确验证了：
- 中文名称 `技能` 通过验证（[test_validator.py:165-176](../../../../../external/agentskills/skills-ref/tests/test_validator.py#L165-L176)）
- 俄文名称 `мой-навык` 通过验证（[test_validator.py:179-190](../../../../../external/agentskills/skills-ref/tests/test_validator.py#L179-L190)）

但仍需满足：
- 必须是小写形式（大写中文/俄文字母会被拒绝）
- 不能以连字符开头/结尾
- 不能有连续连字符
- NFKC 规范化后必须与目录名一致
