---
id: "agent-workspace-hub-readme"
title: "通用智能体工作区脚手架使用说明"
source: "extract-agent-workspace-template"
---

# 通用智能体工作区脚手架

本脚手架是从 SpecWeave 的 `AGENTS.md` + `.agents/` 体系萃取出的**通用智能体工作区模板**，剥离了项目特定内容（特定第三方子模块、具体角色/脚本名），保留可复用的核心结构。

## 目录结构

```
agent-workspace-hub/
├── AGENTS.md             # 通用智能体全局契约模板（启动协议 + 四大区域 + 核心规范入口）
├── README.md             # 本文件（使用说明）
└── .agents/              # 精简版 .agents 规范容器骨架
    ├── README.md         # 容器总览（目录树 + Core/Tools 分层 + 各子目录职责）
    ├── roles/            # 角色定义骨架
    ├── rules/            # 规则体系骨架
    ├── workflows/        # 标准工作流骨架
    ├── protocols/        # 协作协议骨架
    ├── templates/        # 模板资产骨架
    ├── scripts/          # 自动化脚本骨架
    ├── skills/           # Skill 技能门面骨架
    ├── commands/         # 标准化指令集骨架
    └── docs/             # 人类可读文档骨架
```

## 使用步骤

1. **复制**：将 `agent-workspace-hub/` 目录内容复制到新项目根目录（`AGENTS.md` 与 `.agents/` 应为新项目根下的同层文件）。
2. **参数化**：用编辑器全局替换占位符：
   - `{{PROJECT_NAME}}` → 项目名称
   - `{{PROJECT_DESC}}` → 项目一句话说明（可选，可删除该行）
   - `{{OFFICIAL_REPO_URL}}` → 官方仓库地址（用于「一句话装载」安全规则 S1）
3. **删减**：按需裁剪四大顶层区域表——若不使用 submodule 结构，删除 `apps/projects/vendor` 对应行，仅保留 `.agents/`。
4. **装载/自举**：确保 `AGENTS.md` 位于项目根目录且包含"启动协议"关键词后，即可被任意智能体按启动协议加载。
5. **填充**：逐步在 `.agents/` 各骨架子目录中填充角色定义、规则、协议、脚本等实际内容。

## 关键设计

- **启动协议（PRIORITY ZERO）**：强制智能体先读规范再执行，避免"凭经验做对"。
- **入口 ↔ 容器分离**：`AGENTS.md`（约 100 行精简入口）负责路由，`.agents/` 承载具体规范细节。
- **Core/Tools 双层治理**：`.agents/` 内规范定义层（Core）与执行工具层（Tools）职责分离、依赖单向。
- **L0/L1/L2 渐进式披露**：按需加载，避免一次性装载全部上下文。
- **内容敏感度分流**：公开/私域两级判定决定工作流与存储位置。

## 关联资源

- 可复用模式完整说明：[agent-workspace-template.md](../../docs/retrospective/patterns/architecture-patterns/agent-workspace-template.md)