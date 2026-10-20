---
type: Reference
id: "short-video-skills-source-inventory"
title: "信源台账（S01~S24）"
category: "short-video-skills"
date: "2026-10-20"
status: "stable"
author: "SpecWeave Agent（session sc-20261020-video-skill-wiki）"
summary: "本知识包全部信源清单：本机磁盘文件（S 级一手）、宿主注册表、agentskills.io/P0 规范、GitHub 开源仓库（P2）、自报口径标注。"
source: "session sc-20261020-video-skill-wiki"
---

# 信源台账

> 采集时点：2026-10-20。分级沿用 research-guide 信源层级：P0 官方规范/官方文档；P2 公开开源仓库（可复核）；P3 仓库作者自报数据（单独标注，不入权威事实）。磁盘文件属一手可回查信源。

| 键 | 级别 | 信源 | 说明 |
|---|---|---|---|
| S01 | P0 | https://agentskills.io/specification | Agent Skills 开放规范（目录结构/frontmatter/渐进式披露/校验） |
| S02 | P0 | https://github.com/agentskills/agentskills | 规范文档仓库（specification.mdx 与 S01 同源互证） |
| S03 | P0 | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | Claude 平台 Agent Skills 官方文档（含 name 保留词约束） |
| S04 | P0 | https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | Anthropic 工程博客（发布时点 2025-10-16，渐进式披露三层） |
| S05 | P0 | https://github.com/anthropics/skills | Anthropic 官方公共 skill 仓库（template-skill） |
| S06 | P0（一手） | 本仓库磁盘 `.agents/skills/<skill>/SKILL.md` 原文：byted-seedance-video-generate / byted-seedream-image-generate / byted-mediakit-shared / classical-festival-video / douyin-interact-creation / hyperframes / hyperframes-cli / hyperframes-media / asr / hook-analyzer-skill / report-generator-skill | 2026-10-20 逐文件读取引录；frontmatter 均"镜像自 Trae IDE builtin" |
| S07 | P0（运行时） | 宿主 available_skills 注册表（会话注入，本时点） | explainer/local-tts/local-asr/local-realtime-translator/image-gen/local-txt2img/local-img2img 描述；非磁盘信源，注明"未镜像到 .agents/skills/" |
| S08 | P2 | https://github.com/chemny/short-video-maker | 可移植短视频 skill（Node+Remotion 分工） |
| S09 | P2 | https://github.com/Bruce-Agnet/douyin-video-forge | OpenClaw 抖音全链路（热榜采集→可灵生成→ffmpeg 拼接） |
| S10 | P3（含自报） | https://github.com/askxiaozhang/hermes-skills | github-trending-douyin 流水线；"30 天 10 万+播放/+388 粉"为作者自报口径 |
| S11 | P2 | https://github.com/Trudiemisanthropic314/tiktok-video-skill（SKILL.md 原文） | facts-first 规则、素材/TTS/卡拉OK字幕/ffmpeg 管线 |
| S12 | P2 | https://github.com/Frank-oll/ai-video-creator | Seedream 分镜静图 + Seedance I2V 原生配音 + ffmpeg，ARK 单 Key |
| S13 | P2 | https://github.com/xianyu110/ecommerce-video-skills | 13 skill 簇；免 Key 本地渲染口径、广告法/响度/安全区细节 |
| S14 | P2 | https://github.com/xuliang2024/video_skills | Cursor/Claude skill 合集（tumblr/knowledge/svg 视频） |
| S15 | P3（含自报） | https://github.com/maxazure/video-editing-skill | 单体剪辑生产线；QA 门/收据机制为原文；"替代 80% 剪辑工作"为作者自报口径 |
| S16 | P0（一手） | 本仓库 `AGENTS.md`（磁盘回读，2026-10-20） | 文档边界/落盘三查/`.agents/docs/` 废止声明 |
| S17 | P0（一手） | 本仓库 `docs/knowledge/template.md`、`docs/knowledge/README.md` | frontmatter 必填字段、last_verified、`generate_index.py` 入库流程 |
| S18 | P0（一手） | 本仓库 `docs/knowledge/` 目录清单 + `projects/awesome-okf-xs/doc/bundles/` grep 检索（关键词：视频/短视频/video） | 覆盖度核查：无同类主题知识包 |
| S19 | P2 | https://github.com/anthropics/skills/blob/main/spec/agent-skills-spec.md（同规范镜像） | 与 S01 交叉互证 |
| S20~S24 | P2 | 留位：后续追加核验信源（如模型官方定价页） | 当前版本未触发新增核验需求 |

## 口径分级说明

- 技能"功能/参数表"事实：P0 磁盘原文或 P0 官方文档，普通事实。
- 播放量/粉丝增量/"替代 80% 工作量"类效果：P3 作者自报（interest-conflict 原则），仅作生态现象记录，不作为选型依据。
- 模型价格/单位价格：本包未收录具体数字（多利益主体、时限性强），引用时请以厂商当期官网为准。
