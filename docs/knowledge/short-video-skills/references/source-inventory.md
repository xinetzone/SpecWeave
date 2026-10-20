---
type: Reference
id: "short-video-skills-source-inventory"
title: "信源台账（S01~S20）"
category: "short-video-skills"
date: "2026-10-20"
last_verified: "2026-10-20"
status: "stable"
author: "SpecWeave Agent（session sc-20261020-video-skill-wiki）"
summary: "本知识包全部信源清单（S01~S20）：本机磁盘文件（S 级一手）、宿主注册表、agentskills.io/P0 规范、GitHub 开源仓库（P2）、官方合规件（P0）、自报口径与风险标注。"
source: "session sc-20261020-video-skill-wiki"
---

# 信源台账

> 采集时点：2026-10-20。分级沿用 research-guide 信源层级：P0 官方规范/官方文档/法定文件；P2 公开开源仓库（可复核）；P3 仓库作者自报数据（单独标注，不入权威事实）。磁盘文件属一手可回查信源。

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
| S09 | P2 | https://github.com/Bruce-Agnet/douyin-video-forge | OpenClaw 抖音全链路（热榜采集→可灵生成→ffmpeg 拼接），量产+A 范式边界反例的出处 |
| S10 | P3（含自报） | https://github.com/askxiaozhang/hermes-skills | github-trending-douyin 流水线；"30 天 10 万+播放/+388 粉"为作者自报口径，仅作生态现象记录 |
| S11 | P2（含风险标注） | https://github.com/Trudiemisanthropic314/tiktok-video-skill（SKILL.md 原文） | ⚠️ **风险标注（V 阶段实测 2026-10-20）**：仓库真实存在（1 star、MIT License），但 README 为下载器式营销文案且含站外分发页链接（trudiemisanthropic314.github.io）。使用口径：仅引录其 SKILL.md 中 facts-first（VERIFY FACTS FIRST）规则文本为生态事实，不信任也不引导任何站外分发链接；License 列标注以此实测为准 |
| S12 | P2 | https://github.com/Frank-oll/ai-video-creator | Seedream 分镜静图 + Seedance I2V 原生配音 + ffmpeg，ARK 单 Key |
| S13 | P2 | https://github.com/xianyu110/ecommerce-video-skills | 13 skill 簇；免 Key 本地渲染口径、广告法/响度/安全区细节 |
| S14 | P2 | https://github.com/xuliang2024/video_skills | Cursor/Claude skill 合集（tumblr/knowledge/svg 视频） |
| S15 | P3（含自报） | https://github.com/maxazure/video-editing-skill | 单体剪辑生产线；QA 门/收据机制为原文；"替代 80% 剪辑工作"为作者自报口径，不作为任何效果承诺 |
| S16 | P0（一手） | 本仓库 `AGENTS.md`（磁盘回读，2026-10-20） | 文档边界/落盘三查/`.agents/docs/` 废止声明 |
| S17 | P0（一手） | 本仓库 `docs/knowledge/template.md`、`docs/knowledge/README.md` | frontmatter 必填字段、last_verified、`generate_index.py` 入库流程 |
| S18 | P0（一手） | 本仓库 `docs/knowledge/` 目录清单 + `projects/awesome-okf-xs/doc/bundles/` grep 检索（关键词：视频/短视频/video） | 覆盖度核查：无同类主题知识包 |
| S19 | P2 | https://github.com/anthropics/skills/blob/main/spec/agent-skills-spec.md（同规范镜像） | 与 S01 交叉互证 |
| S20 | P0（法定文件） | https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm | 《人工智能生成合成内容标识办法》全文（国信办通字〔2025〕2号，网信办/工信部/公安部/国家广电总局 2025-03-07 印发、2025-09-01 施行）：显式/隐式标识定义（第三条）、视频起始画面显著提示（第四条）、元数据隐式标识（第五条）、用户主动声明义务与禁删改条款（第十条）；配套强制性国标 GB 45438-2025 同步实施。V 阶段（2026-10-20）webfetch 实测可达并逐条比对条款原文 |

## 口径分级说明

- 技能"功能/参数表"事实：P0 磁盘原文或 P0 官方文档，普通事实。
- 播放量/粉丝增量/"替代 80% 工作量"类效果：P3 作者自报（interest-conflict 原则），仅作生态现象记录，不作为选型依据或效果承诺。
- 合规义务（S20）：法定 P0 事实；论及具体样式参数（如提示标识高度/时长）时须回查 GB 45438-2025 当期文本与平台规范，本包只记录义务存在与时点。
- 模型价格/单位价格：本包未收录具体数字（多利益主体、时限性强），引用时请以厂商当期官网为准。
- 开源仓库 License：除 S11（MIT，V 阶段实测）外均标注"未核验"，使用前请复查各仓库 LICENSE 文件。
