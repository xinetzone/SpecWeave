# Projects 区域 .agents 容器

本目录是 projects 区域的 AI 智能体元数据容器，由 SpecWeave 主权区维护，直接纳入版本管理。

## 用途

与子项目内的 `.agents/` 不同，本目录**不是**完整的规则体系容器，而是 projects 区域的**元数据与索引层**：

- **不存放** roles/rules/workflows/protocols 等完整规则（这些由各子项目自治管理）
- **存放** projects 区域的资产索引、子项目清单、跨边界调用记录

## 目录结构

```
projects/
├── AGENTS.md              ← projects 区域入口路由（指向本目录）
├── .agents/
│   └── README.md          ← 本文件（元数据容器说明）
├── README.md              ← projects 目录总览
└── xuanspace/             ← xuanspace 子项目（git submodule，自治管理）
    ├── AGENTS.md          ← xuanspace 入口（嵌套优先）
    └── .agents/           ← xuanspace 规范体系
```

## 与子项目 .agents/ 的关系

| 维度 | projects/.agents/（本目录） | projects/xuanspace/.agents/ |
|------|---------------------------|-----------------------------|
| 归属 | SpecWeave 主权区 | xuanspace 子项目 |
| 版本管理 | 直接纳入 SpecWeave | 通过 gitlink 追踪 |
| 内容 | 元数据/索引/路由 | 完整规范体系（rules/prompts/protocols 等） |
| 可修改 | ✅ SpecWeave 可直接修改 | ❌ 需走子项目开发流程 |

## 资产索引

projects 区域可用的子项目资产索引见 [projects/AGENTS.md 的「可用资产索引」章节](../AGENTS.md#可用资产索引)。