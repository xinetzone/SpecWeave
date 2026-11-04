---
okf_version: "0.2"
type: spec-tasks
title: "ub-mode 博文→OKF 知识包转化任务清单"
description: "七阶段工作流 R→I→E→V→C 的任务分解与完成记录"
generated: { by: "seven-concepts-cmd", at: "2026-11-04T10:00:00+08:00" }
---

# 任务清单

## 0. 预检（T0）

- [x] T0-1 读取根 `AGENTS.md`、`.agents/context-routing.md`（启动协议步骤 1-2）
- [x] T0-2 读取 `projects/AGENTS.md` → `projects/awesome-okf-xs/AGENTS.md` → 子项目 `.agents/context-routing.md`、`global-core-rules.md`、`rules/frontmatter.md`
- [x] T0-3 内容敏感度预检 → **公开内容**，标准工作流
- [x] T0-4 幂等检查：全仓 Grep `ub-mode|unclebob` 无同名 bundle（命中均为无关误报），确认首次转化

## R. 事实采集与核验（T1）

- [x] T1-1 获取博文全文（信源 1）；记录标题/公众号/作者/发布时间/正文主张
- [x] T1-2 获取 GitHub API 元数据（信源 2）：owner、创建/更新时间、Star、forks、issues、默认分支、language、license
- [x] T1-3 获取仓库文件树（信源 3）：3 个 blob 及字节数
- [x] T1-4 获取官方 `SKILL.md` 全文（信源 4）：三大节原则清单、Crapper/Dryer/Mutator 阈值
- [x] T1-5 获取官方 `README.md`（信源 5）：companion 工具 4 仓库、`@poteto` 溯源、安装三路径
- [x] T1-6 获取官方 `LICENSE`（信源 6）：MIT + Copyright (c) 2026 Robert C. Martin
- [x] T1-7 F-001~F-037 编号登记（spec `facts.md`），区分事实与作者观点
- [x] T1-8 信源距离预判：第三方综述（开源项目推介号），非厂商自宣
- [x] T1-9 P0 核验 + 勘误四张清单逐项过筛（13 组：7✅/6⚠️/0❌）

## I. 骨架与知识拆分（T2）

- [x] T2-1 操作可复现性两问 → Q1 是 / Q2 否 → **不设 examples/**
- [x] T2-2 归属判定决策树 → 选定 `jishu/ai/practice/`
- [x] T2-3 三层知识拆分 → concepts 5 篇映射表

## E. bundle 生成（T3）

- [x] T3-1 写 `references/article-source.md`（信源先行）
- [x] T3-2 写 `references/verification.md`（P0 核验报告 + 勘误）
- [x] T3-3 写 `references/index.md`
- [x] T3-4 写 `concepts/00`~`04` 5 篇
- [x] T3-5 写 `concepts/index.md`
- [x] T3-6 最后写 `index.md` 与 `log.md`

## V. 对抗审查与索引收尾（T4）

- [x] T4-1 四视角审查（魔鬼代言人 / 新人 / 老板 / 未来）
- [x] T4-2 双份 F 编号一致性核对（facts.md ↔ article-source.md）
- [x] T4-3 toctree 完整性（三级：bundle → concepts/references → 分组）
- [x] T4-4 计数同步四处：`practice/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`bundles/index.md`
- [x] T4-5 相对链接可达性：子模块等价检查器 `check_doc_links.py` → 11 文件 / 60 链接 / **0 broken**（主仓 `check-links.py` 结构性不覆盖 `projects/` 子模块）
- [x] T4-6 记录未运行的 `invoke gates.*`（不声称通过）

## C. 原子提交（T5）

- [ ] T5-1 子模块 `projects/awesome-okf-xs` 内提交 bundle 变更
- [ ] T5-2 主仓库提交 spec 变更
- [ ] T5-3 主仓库更新子模块指针（不 push）

> T5 需用户显式授权后执行；本次未获授权，交付停在 V 阶段。
