---
id: apps-agents-readme
version: 1.0
---

# Apps 区域 .agents 容器

本目录是 apps 区域的 AI 智能体元数据容器，由 SpecWeave 主权区维护，直接纳入版本管理。

## 用途

与子应用内的 `.agents/` 不同，本目录**不是**完整的规则体系容器，而是 apps 区域的**元数据与索引层**：

- **不存放** roles/rules/workflows/protocols 等完整规则（这些由各子应用自治管理）
- **存放** apps 区域的资产索引、子应用清单、跨边界调用记录

## 目录结构

```
apps/
├── AGENTS.md              ← apps 区域入口路由（指向本目录）
├── .agents/
│   └── README.md          ← 本文件（元数据容器说明）
├── README.md              ← apps 目录总览
├── shared/                ← 跨应用共享资源
├── tests/                 ← 全局测试用例
├── docker-images/         ← 容器镜像类分组
│   ├── devcontainer-base/ ← devcontainer-base 应用（有自己的 .agents/）
│   │   ├── AGENTS.md      ← devcontainer-base 入口（嵌套优先）
│   │   └── .agents/
│   ├── docker-ssh-dind/   ← docker-ssh-dind 应用（有自己的 .agents/）
│   │   ├── AGENTS.md
│   │   └── .agents/
│   ├── jupyter-ssh-base/  ← jupyter-ssh-base 应用（有 AGENTS.md）
│   │   └── AGENTS.md
│   ├── pytorch-base/
│   ├── caffe-ffi-jupyter/
│   ├── caffe-ffi-cross/
│   └── xmnn-runtime/
├── ai-agents/             ← AI 应用类分组
│   ├── zhujian-wudao/     ← zhujian-wudao 应用（有自己的 .agents/）
│   ├── ai-code-assistant/
│   └── eve-minimal-agent/
├── dev-tools/             ← 开发工具类分组
│   ├── camera-power-controller/
│   └── prompt_extraction/
└── samples/               ← 示例/原型类分组
    ├── cow-demo/
    ├── short-video-site/
    └── zleap-workspace-first-prototype/
```

## 与子应用 .agents/ 的关系

| 维度 | apps/.agents/（本目录） | apps/ai-agents/zhujian-wudao/.agents/ |
|------|------------------------|-----------------------------|
| 归属 | SpecWeave 主权区 | zhujian-wudao 应用 |
| 版本管理 | 直接纳入 SpecWeave（同仓库） | 直接纳入 SpecWeave（同仓库） |
| 内容 | 元数据/索引/路由 | 完整规范体系（rules/roles/skills 等） |
| 可修改 | ✅ SpecWeave 可直接修改 | ✅ 同仓库直接修改（遵循应用规范） |

> **注意**：apps 区域内的应用直接属于 SpecWeave 主仓库（不是 git submodule），但部分应用有自己的 `.agents/` 目录进行自治管理。没有 `.agents/` 的应用由 apps/AGENTS.md 直接路由。

## 资产索引

apps 区域可用的子应用资产索引见 [apps/AGENTS.md 的「可用资产索引」章节](../AGENTS.md#可用资产索引)。
