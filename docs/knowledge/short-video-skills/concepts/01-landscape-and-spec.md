---
type: Reference
id: "short-video-skills-concept-01"
title: "生态全景与 Agent Skills 规范"
category: "short-video-skills"
tags: ["agent-skills", "SKILL.md", "生态", "短视频"]
date: "2026-10-20"
last_verified: "2026-10-20"
status: "stable"
author: "SpecWeave Agent（session sc-20261020-video-skill-wiki）"
summary: "Agent Skills 开放规范（目录/SKILL.md/渐进式披露）与本机+开源生态全景：生成式、程序排版、分析三条能力带的代表 skill。"
source: "../references/source-inventory.md"
---

# 01 生态全景与 Agent Skills 规范

## 1. 先补一个前置知识：什么是"Skill"

本文中的 skill 指 Agent Skills 开放规范定义的能力单元：一个包含 `SKILL.md` 的目录，frontmatter 写 `name` + `description`（做什么/何时用），正文写指令，可随附 `scripts/`（可执行脚本）、`references/`（参考文献）、`assets/`（模板资源）[F-001、F-002]。Agent 对 skill 采取三级渐进式披露：启动只加载 name+description（约 100 token），命中任务才读全文，资源按需加载 [F-003]。校验用 `skills-ref validate` [F-005]。

这意味着：**skill 的规模可以很小（一段提示词）也可以很大（60+ 步骤的生产线）**，而"短视频生产"天然是后者——它是多工序协作，生态因此演化成 skill 簇而非单体。

## 2. 三条能力带

调研到的所有"做短视频的 skill"，按能力带可归入三桶：

| 能力带 | 职能（按工序） | 本机代表 | 开源生态代表 |
|---|---|---|---|
| 生成式带 | 选题→脚本→分镜静图→图/文生视频→拼接 | byted-seedream-image-generate、byted-seedance-video-generate [F-007、F-008] | ai-video-creator（Seedream+Seedance 双锚定）[F-023]、douyin-video-forge（可灵 3.0 + Seedance 双版脚本）[F-020] |
| 程序排版带 | 脚本→配音→排版/动画帧→ffmpeg 合成→字幕→平台导出 | hyperframes + hyperframes-cli + hyperframes-media [F-012~F-014] | short-video-maker（Remotion）[F-019]、github-trending-douyin（Pillow+ffmpeg）[F-021]、ecommerce-video-skills（13 skill 簇）[F-024]、knowledge-video [F-025] |
| 分析复盘带 | 分镜拆解→钩子评分→生成分析报告→反哺选题 | hook-analyzer-skill、report-generator-skill [F-016、F-017] | douyin-video-forge 的竞品分析/低粉高赞筛选 [F-020]、tiktok-video-skill 的 facts-first 规则 [F-022] |

另有平台形态的特殊分支：douyin-interact-creation 产的不是视频而是抖音互动空间的离线 H5 作品（≤8MB、零外链）[F-011]，属于"互动玩法"而非成片，量产管线通常不混入。

## 3. 本机 Skill 的两层分布

本机视频 skill 分布在两层（结构事实，与其他实现来源无关）：

- **仓库磁盘层**（`.agents/skills/`）：可见、可审计、可改造，frontmatter 标注"镜像自 Trae IDE builtin" [F-006]。生成式带、hyperframes 系、分析带均在此层。
- **宿主注册表层**（运行时 available_skills）：explainer、local-tts、local-asr、local-realtime-translator、image-gen、local-txt2img/local-img2img 等由运行时注入，不在本仓库磁盘 [F-018]。其中 local-* 系列面向 Intel AIPC 硬件本地运行（离线 TTS/ASR/翻译）。

**实用含义**：磁盘层 skill 可被 grep/脚本批量审计、可按本文方法论改造；宿主层 skill 只能通过会话触发调用。这是一篇公开教程，读者机器上的具体分布未必相同，选型时应以"本机实际注册的 skill"为准。

## 4. 规范细节速查（自建 skill 时用）

- `name`：≤64 字符，小写+数字+连字符，与目录同名，不含 `anthropic`/`claude` 保留词 [F-002、F-004]
- `description`：≤1024 字符，必须同时写"做什么"和"何时触发"，是 Agent 匹配任务的唯一入口 [F-002]
- SKILL.md <500 行；细节拆到 references/，脚本放 scripts/ [F-003]
- 新建视频类 skill 的推荐目录：`SKILL.md` + `scripts/`（渲染/合成/校验脚本）+ `references/`（分镜公式、平台规格表）+ `assets/`（字体、模板帧）

---

- [🏠 返回知识包首页](../index.md)
- [下一篇：生产管线与选型 →](02-pipeline-and-selection.md)
