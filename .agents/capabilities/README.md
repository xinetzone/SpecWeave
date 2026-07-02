---
id: "capability-index"
title: "能力注册与发现中心（Capability Registry）"
version: "1.0.0"
last_updated: "2026-06-30"
---
# 能力注册与发现中心（Capability Registry）

> **P0模块1**：基于渐进式披露三层架构的能力发现体系。
> 解决"Agent新会话如何快速建立上下文认知"的核心问题。

---

## 文件索引

| 文件 | 层级 | 用途 | 行数限制 |
|------|------|------|---------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | L2 | 三层架构完整规范：边界定义、内容要求、检查清单、反模式 | 不限 |
| [ONBOARDING-TEMPLATE.md](ONBOARDING-TEMPLATE.md) | 模板 | L0入口层模板：新模块创建ONBOARDING.md时使用 | < 100行 |
| [REGISTRY-TEMPLATE.md](REGISTRY-TEMPLATE.md) | 模板 | L1索引层模板：新模块创建REGISTRY.md时使用 | < 500行 |

---

## 三层架构速览

```
L0 入口层（<100行）  → ONBOARDING.md → "我是谁？有什么？去哪？"
L1 索引层（<500行）  → SKILL.md / REGISTRY.md → "怎么用？注意什么？"
L2 深度层（不限行数） → 完整规范文档 → "为什么？完整参数？"
```

详细规范见 [ARCHITECTURE.md](ARCHITECTURE.md)。

---

## 如何使用

### 创建新模块/子系统的能力文档

1. 阅读 [ARCHITECTURE.md](ARCHITECTURE.md) 理解三层架构
2. 复制 [ONBOARDING-TEMPLATE.md](ONBOARDING-TEMPLATE.md) 为目标目录的 `ONBOARDING.md`，填写内容并控制在100行以内
3. 复制 [REGISTRY-TEMPLATE.md](REGISTRY-TEMPLATE.md) 为目标目录的 `REGISTRY.md`，填写能力条目
4. SKILL.md 使用 [../skills/SKILL-TEMPLATE.md](../skills/SKILL-TEMPLATE.md)（已有模板，遵循五要素模型，<500行）
5. 深度参考文档放在L2层，在SKILL.md中引用
6. 对照 ARCHITECTURE.md 第五节检查清单验证

### 现有实例参考

| 模块 | L0入口 | L1索引 | 状态 |
|------|--------|--------|------|
| SpecWeave全局（.agents/根目录） | [../ONBOARDING.md](../ONBOARDING.md) | [../capability-registry.md](../capability-registry.md) | ✅ 已实现（v2.0，严格L0规范） |
| Skill体系 | [../skills/README.md](../skills/README.md) | [../skills/SKILL-TEMPLATE.md](../skills/SKILL-TEMPLATE.md) | ✅ L1模板已有，待补L0 |

---

## 与现有体系的关系

- **根目录ONBOARDING.md**：全局L0入口，86行（符合<100行限制），v2.0严格遵循L0规范（L0只引用L1，无跨层跳跃）
- **根目录capability-registry.md**：全局L1能力注册表，231行（符合<500行限制），v1.2新增知识参考索引区块（docs/knowledge、docs/retrospective/patterns、docs/development-standards）
- **会话启动协议**：[../protocols/onboarding-protocol.md](../protocols/onboarding-protocol.md) 是L2深度规范，定义Onboarding设计原理和完整流程
- **SKILL-TEMPLATE.md**：已在[../skills/](../skills/)目录下，是L1 SKILL的标准模板，本目录不重复创建
- **skill-development.md**：[../rules/skill-development.md](../rules/skill-development.md) 是L2深度规范，定义Skill开发的详细要求

---

## 版本历史

- **v1.2.0** (2026-06-30): ONBOARDING.md严格化——移除L0→L2跨层链接，frontmatter对齐l0-onboarding-v1标准；capability-registry.md v1.2新增知识参考索引区块，完善L0→L1引用链。
- **v1.1.0** (2026-06-30): 更新实例状态——全局ONBOARDING.md v2.0已精简至90行，capability-registry.md v1.1已添加三层声明，L2 onboarding-protocol.md已创建。
- **v1.0.0** (2026-06-30): 初始版本。基于架构优先级复盘洞察A创建，包含三层架构规范和L0/L1模板。
