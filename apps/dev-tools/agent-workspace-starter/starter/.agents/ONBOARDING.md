---
id: "onboarding"
title: "Agent Onboarding（工作区入门指南）"
source: ".agents/ONBOARDING.md"
version: "2.5"
layer: "L0"
max_lines: 100
---
# Agent Onboarding（工作区入门指南）

> ⚠️ **L0 入口层**（<100 行）：L0=本文件，L1=[capability-registry.md](capability-registry.md)，L2=完整规范（按需进入）

## 环境准备

```
Windows 建议：
  1. pwsh7.4+（PowerShell 7）——安装：winget install Microsoft.PowerShell；验证：pwsh --version
  2. Python 3.10+——安装：winget install Python.Python.3.12；验证：python --version
```

## 快速开始（3 步）

```
1. 读本文件 ✅  2. 读 capability-registry.md  3. 按路由表定位能力，按需加载 L2 文档
```

## 核心实践（17 条）

| # | 实践 | 一句话说明 |
|---|------|-----------|
| 1 | 启动协议先行 | 先读 AGENTS.md + 本文件，再动手 |
| 2 | Spec-driven 开发 | 先写 spec 再实施，减少返工 |
| 3 | 入口 + 容器二元架构 | 入口 <100 行，细节放 `.agents/` 按需加载 |
| 4 | 零依赖原则 | 脚本只用标准库，跨环境即用 |
| 5 | 原子化单一职责 | 每个文件聚焦一个主题，支持并行编辑 |
| 6 | 三层治理闭环 | 原子化→自动化→验证 |
| 7 | 高频批次复盘 | 每个里程碑后复盘，把经验转化为知识资产 |
| 8 | 事实表述一致性 | 修一处→搜同类→统一修正→验证闭环 |
| 9 | 探索区到持久区 | 先在临时区探索，经验证后再沉淀进正式目录 |
| 10 | MECE 分类 + 决策树 | 新内容按主题自动归位 |
| 11 | Skill 渐进披露 | L0<100 / L1<500 / L2 按需 |
| 12 | 引用精确化 | 先确认目标章节再写引用，减少断链 |
| 13 | 单元测试保障质量 | 关键脚本配单元测试，防回归 |
| 14 | 边界清晰 | 明确各目录职责，保持核心区轻量 |
| 15 | 问题驱动治理演化 | 治理规则来自真实问题抽象 |
| 16 | pwsh7 统一标准 | Windows 脚本用 pwsh7.4+ |
| 17 | Python 版本统一 | 脚本要求 Python 3.10+ |

> 💡 修复即闭环 SOP 见 [rules/fix-prevent-close-loop.md](rules/fix-prevent-close-loop.md)。

## 能力速查（核心高频 Skill）

| 任务 | Skill | 任务 | Skill |
|------|-------|------|-------|
| 复盘 | retrospective-cmd | 原子提交 | atomic-commit-cmd |
| 洞察萃取 | insight-cmd | Mermaid 画图 | mermaid-cmd |
| 导出报告 | export-report-cmd | CI 全量检查 | ci-check-cmd |
| 原子化文档 | atomization-cmd | 链接检查/修复 | link-check-cmd |
| 原子化收尾 | atomization-finalize-cmd | 导航/看板更新 | docgen-cmd |

> 完整能力索引见 [capability-registry.md](capability-registry.md)。

## 任务路由

```
收到任务 → 匹配对应 Skill → 执行
└─ 不确定 → 查 capability-registry.md
```

## 新会话启动确认

```
📋 上下文已建立：已读 AGENTS.md、ONBOARDING.md（L0）、capability-registry.md（L1）
任务类型：<类型>  将使用：<对应能力>
```