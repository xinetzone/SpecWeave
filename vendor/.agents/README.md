# Vendor 区域 .agents 容器

本目录是 vendor 区域的 AI 智能体元数据容器,由 SpecWeave 主权区维护,直接纳入版本管理。

## 用途

与 flexloop 子模块内的 `.agents/` 不同,本目录**不是**完整的规则体系容器,而是 vendor 区域的**元数据与索引层**:

- **不存放** roles/rules/workflows/protocols 等完整规则(这些由 flexloop 子模块自治管理)
- **存放** vendor 区域的资产索引、子模块清单、跨边界调用记录

## 目录结构

```
vendor/
├── AGENTS.md              ← vendor 区域入口路由(指向本目录)
├── .agents/
│   └── README.md          ← 本文件(元数据容器说明)
├── README.md              ← vendor 依赖总览(由 check-vendor 自动生成)
├── VERSION.md             ← vendor 版本元数据
└── flexloop/              ← flexloop 子模块(git submodule,自治管理)
    ├── AGENTS.md          ← flexloop 入口(嵌套优先)
    └── apps/chaos/.agents/ ← 完整规则体系(skills/scripts/rules 等)
```

## 与 flexloop .agents/ 的关系

| 维度 | vendor/.agents/(本目录) | vendor/flexloop/apps/chaos/.agents/ |
|---|---|---|
| 归属 | SpecWeave 主权区 | flexloop 子模块 |
| 版本管理 | 直接纳入 SpecWeave | 通过 gitlink 追踪 |
| 内容 | 元数据/索引/路由 | 完整规则体系(roles/rules/skills/scripts 等) |
| 可修改 | ✅ SpecWeave 可直接修改 | ❌ 需走子模块开发流程 |

## 资产索引

vendor 区域可用的 skill 资产索引见 [vendor/AGENTS.md 的「可用资产索引」章节](../AGENTS.md#可用资产索引)。
