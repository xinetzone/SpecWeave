---
type: tasks
title: GPT-6 Astra 博文 → OKF bundle 任务清单
date: 2026-09-16
---

# 任务清单（R→I→E→V）

## R 阶段（事实与核验）
- [x] R1 博文全文提取（browser_use，#js_content，6555 字）
- [x] R2 F-001～F-043 事实采集（spec facts.md）
- [x] R3 信源距离预判：第三方编译，10 集群 P0 回官方文档核验（✅8 / ⚠️2 / ❌0）
- [x] R4 勘误台账：F-006 发布时间措辞、F-042 标题命题；博文遗漏补全 8 处

## I 阶段（结构洞察）
- [x] I1 骨架判定：操作可复现性两问皆否 → 无 examples/（官方指南解读类）
- [x] I2 归属判定：`jishu/ai/gpt6-astra-usage-guide/` 直挂束
- [x] I3 三层知识地图：00 发布事实 / 01 行为机制 / 02 Prompt 配方 / 03 迁移生态
- [x] I4 三条四元组洞察（spec §8），G2 自检通过

## E 阶段（bundle 生成，信源先行）
- [x] E1 references/article-source.md（F 编号双份登记）
- [x] E2 references/verification.md（P0 报告 + 勘误）
- [x] E3 concepts/00-astra-release-and-features.md
- [x] E4 concepts/01-behavior-patterns.md
- [x] E5 concepts/02-prompt-recipes.md
- [x] E6 concepts/03-migration-and-ecosystem.md
- [x] E7 各级 index.md + log.md（最后写）

## V 阶段（对抗审查与收尾）
- [x] V1 四视角对抗审查（review.md，7 条意见、采纳修复 4 条）
- [x] V2 机械门禁：UTF-8 strict / 双份 F 集合一致（43=43）/ toctree（9/9）/ 相对链接（45/45）/ 敏感路径零残留
- [x] V3 三级索引接入：jishu/ai/index.md、bundles/index.md 计数 544/411/192 → 545/412/193（并行会话基线上 +1）
- [x] V4 实测 scripts/check-utf8.py ✅；check-toctrees/bundles-index 仅被并行会话在途束阻断，本束作用域干净（log.md 留痕）

## C 阶段
- [ ] C1 原子提交（待用户显式确认；顺序：子模块 → 主仓库 spec → gitlink；不 push）
