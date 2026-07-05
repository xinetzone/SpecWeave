---
version: "2.3"
last_updated: "2026-07-05"
schema: "l0-onboarding-v1"
layer: "L0"
max_lines: 100
title: "SpecWeave Agent Onboarding"
---
# SpecWeave Agent Onboarding

> ⚠️ **L0入口层**（<100行）：L0=本文件，L1=[capability-registry.md](capability-registry.md)，L2=完整规范（按需进入）

---

## 快速开始（3 步）
```
1. 读本文件 ✅  2. 读capability-registry.md  3. 按路由表定位能力，按需加载L2文档
```

---

## 核心实践（793次提交验证·15条）

| # | 实践 | 一句话说明 |
|---|------|-----------|
| 1 | 启动协议先行 | 先读AGENTS.md+本文件+L1注册表，再动手 |
| 2 | Spec-driven开发 | 先写spec/tasks/checklist再实施，减少返工 |
| 3 | 入口+容器二元架构 | 入口<100行，细节放.agents/容器按需加载 |
| 4 | 零依赖原则 | 脚本只用Python标准库，跨环境即用 |
| 5 | 原子化单一职责 | 每个文件聚焦一个主题，支持并行编辑 |
| 6 | 三层治理闭环 | 原子化→自动化→验证，10+脚本防护 |
| 7 | 高频批次复盘 | 每个里程碑后复盘，知识转化率3×+ |
| 8 | 事实表述一致性 | 修一处→搜同类→统一修正→验证闭环 |
| 9 | 双区开发模型 | .temp/探索→门禁→apps/沉淀，多应用验证 |
| 10 | MECE分类+决策树 | 8主题分类，新内容自动归位 |
| 11 | Skills渐进披露 | L0<100/L1<500/L2按需，降认知负担 |
| 12 | 跨Wiki引用精确化 | 先读目录确认章节号再写引用，减少断链 |
| 13 | 单元测试保障质量 | 关键脚本/工具配单元测试，防回归 |
| 14 | 三区域边界模型 | vendor/flexloop子模块治理，核心区轻量化 |
| 15 | 问题驱动治理演化 | 治理规则来自真实问题抽象，而非预设 |

> 💡 详细说明见 [development-standards.md](../docs/development-standards.md)，新增：[三阶段原则](rules/three-stage-universal-principle.md)、[元文档优先](rules/meta-document-priority-principle.md)、[修复即闭环](rules/fix-prevent-close-loop.md)

---

## 能力速查（核心高频Skill）

| 任务 | Skill | 任务 | Skill |
|------|-------|------|-------|
| 复盘 | retrospective-cmd | 原子化提交 | atomic-commit-cmd |
| 洞察萃取 | insight-cmd | Mermaid画图 | mermaid-cmd |
| 导出报告 | export-report-cmd | CI全量检查 | ci-check-cmd |
| 原子化文档 | atomization-cmd | 链接检查/修复 | link-check-cmd |
| 原子化收尾 | atomization-finalize-cmd | 导航/看板更新 | docgen-cmd |

> 完整能力索引见 [capability-registry.md](capability-registry.md)（含脚本/协议/工作流/规则/知识库入口）

---

## 任务路由
```
收到任务 → 匹配对应Skill → 执行
└─ 不确定 → 查capability-registry.md
```

---

## 新会话启动确认
```
📋 上下文已建立：已读 AGENTS.md、ONBOARDING.md（L0）、capability-registry.md（L1）
任务类型：<类型>  将使用：<对应能力>
```
