---
type: Reference
id: "short-video-skills-concept-03"
title: "实战教程四线：口播/知识、AI 艺术片、带货、复盘分析"
category: "short-video-skills"
tags: ["实战", "教程", "ffmpeg", "edge-tts", "Seedance", "复刻拆解"]
date: "2026-10-20"
last_verified: "2026-10-20"
status: "stable"
author: "SpecWeave Agent（session sc-20261020-video-skill-wiki）"
summary: "四条可落地流水线的操作骨架：B 范式口播知识线、A 范式 AI 艺术片线、带货复刻线、复盘分析线；含命令骨架、耗时估计与验收门。"
source: "../references/source-inventory.md"
---

# 03 实战教程四线

> **时点声明**：以下为操作骨架（各 skill 的具体命令以本机安装版本的引用文件为准，本页事实锁定在 2026-10-20 的 skill 文档原文）[F-010、F-013~F-017、F-019~F-026]。storyboard.json（结构化分镜文件，定义见 [02 §0 术语速查](02-pipeline-and-selection.md)）为四条线共用的中间契约；**耗时估计**均为经验估计（非实测基线，视素材、机器与网络而变）。

## 线 1：口播/知识讲解线（范式 B · 量产主力）

**输入**：一个话题或一篇文章。**参考形态**：knowledge-video、short-video-maker、github-trending-douyin [F-019、F-021、F-025]。

1. **策划**：Agent 选题与受众 → 按公式写钩子（9 型钩子库，3 秒开头定去留，见 02 §2 ①段质量门）与分段口播稿 [F-024]；**事实先行**：数字/价格/排名类论断先联网核实，无法核实则改写或删除，信源 URL 记入 storyboard `sources` [F-022]
2. **配音**：`edge-tts` 逐句合成（免 Key）或本机 `local-tts`（Intel AIPC 离线）；记录每句 `tts_duration` 回填 storyboard [F-021]
3. **排版**：视觉形态按内容选——Pillow 直绘风格卡帧（资讯类）[F-021]、PPT 逐段导出（教学类）[F-025]、HTML/GSAP 动效（质感类，`npx hyperframes init --example <name>` 起步，`inspect`/`preview` 再转 `render`）[F-012、F-013]
4. **合成**：ffmpeg 拼 9:16 + ASS 字幕（术语见 [02 §0](02-pipeline-and-selection.md)：可设字体/位置/逐词同步的字幕格式）+ BGM 自动闪避 + 两遍响度标准化（≈-14 LUFS）[F-024]
5. **质检**：字形/emoji 检测门（如 verify_emoji.py：不过门不合成）[F-021]；平台规格导出 [F-024]

**耗时估计（经验值）**：首次跑通约 1~2 小时（装 Node/ffmpeg/edge-tts、踩 ASS 样式与安全区）；熟练后单条 15s 解说成片约 10~20 分钟。

**验收**：成片前 3 秒过观众快看；字幕逐帧可读；响度达标；发布前过 [02 §6 合规门](02-pipeline-and-selection.md)（AI 素材须标识 [F-031]）。

## 线 2：AI 艺术片线（范式 A · 低产高质）

**输入**：节日祝福/产品大片/虚构剧情。**参考形态**：classical-festival-video（本机）、ai-video-creator [F-010、F-023]。

1. **立意**：先定情感分寸/品牌基调（如"祝福重量 ≤ 关系深度"矩阵），再定美学基调 [F-010]
2. **关键帧**：Seedream 生成 3 张一致性分镜静图（竖版 1440x2560、风格锚点句每张必带、负向约束"绝不能出现任何文字/汉字/印章"）[F-008、F-010、F-023]
3. **目检门**：关键帧先交用户目检（无崩字/主体唯一/风格达标），不过门只重新生成帧，不消耗视频生成额度 [F-010]
4. **图生视频**：Seedance I2V（或可灵 3.0），首尾帧衔接保连贯，`generate_audio` 按需（仅 Seedance 1.5 支持）[F-007、F-020]
5. **合成交付**：ffmpeg 拼接成片 + 随片文案（文字走文案通道而非画面）[F-010、F-023]

**耗时估计（经验值）**：首次跑通约半天（Key 申请、一致性约束词调参、首镜返工 1~3 次属正常）；熟练后单条 10~15s 成片约 30~60 分钟（多数时间花在目检与重生成）。

**验收**：全片无崩字、单主体贯穿、分寸矩阵逐句自查（不越阶）；发布前必过 [02 §6 合规门](02-pipeline-and-selection.md)——生成式内容是标识义务的核心场景 [F-031]。

## 线 3：带货/电商复刻线（范式 B 为主 + A 点睛）

**参考形态**：ecommerce-video-skills 13-skill 簇 [F-024]。

1. **复刻/破题**：丢爆款链接或转写 → viral-remake 爆款五拍拆解（5-beat，术语见 [02 §0](02-pipeline-and-selection.md)）→ 换成自家商品直接产出 storyboard.json
2. **钩子**：hook-3s-script 一次出 6~10 版，标 Top3；广告法绝对化用语自检（"最/第一/绝对"类词回报）[F-024]
3. **分镜静图**：selling-point-storyboard 输出每镜一信息的 storyboard.json；商品一致性锁（形状/颜色/Logo 约束词先锁）[F-024]
4. **镜头**：multi-model-shot-prompts 出中性提示词（Seedance/可灵/Veo 皆可接），**本地 Ken Burns 兜底**保证零 Key 可出片 [F-024]
5. **成片**：edge-tts 逐句 → ASS 四样式字幕（避开底部商品卡/右侧按钮安全区）→ 转场 → BGM 闪避 → 响度标准化（≈-14 LUFS）[F-024]
6. **导出**：platform-spec-export 按抖音/TikTok Shop/视频号/小红书/淘宝主图/Amazon 分版；cover-title-AB 出封面+标题 A/B 测试记录 [F-024]

**耗时估计（经验值）**：首次跑通约半天~1 天（多 skill 装配与安全区调教）；熟练后单条 15~30s 带货成片约 20~40 分钟。

## 线 4：复盘/分析线（用已有视频反哺选题）

**输入**：任意视频 URL 或竞品主页。**参考形态**：hook-analyzer + report-generator [F-016、F-017]。

1. **拆解**：先经分镜拆解工序产出 breakdown.json（含每段时长/关键帧 URL/运镜）
2. **钩子评分**：`python scripts/analyze_hook_segments.py breakdown.json`从中提取**前三秒分镜数据**；LLM 按 30/25/15/15/15（视觉冲击力/语言钩子/情绪唤起/信息密度/节奏掌控）五维权重评分 [F-016]
3. **生成报告**：`python scripts/generate_report.py breakdown.json hooks.json > report.md`（基本信息/钩子/分镜/BGM/场景章节）[F-017]
4. **反哺**：报告中的优势/不足/优化建议写入下次 storyboard 的钩子策略——即"分析 → 复盘 → 再制作"的闭环入口

**耗时估计（经验值）**：首次跑通约 30~60 分钟（装依赖）；熟练后单个视频分析约 10~15 分钟，报告可直接进入下一轮线 1/线 3 的策划段。

**验收**：report.md 五章节齐全；评分理由引用关键帧可回查。

## 平台规格速查（⑤ 段共用）

| 维度 | 典型口径（生态事实，时点 2026-10-20） |
|---|---|
| 竖屏分辨率 | 1080x1920（主流）[F-020、F-022] 或 1440x2560（HyperFrames 竖版）[F-013、F-025] |
| 时长 | 15s（剪辑起步）/ 10s（节日情感片）[F-010] |
| 音频 | 响度标准化 ≈ -14 LUFS [F-024]；BGM 对人声 ducking（自动压低避让人声清晰） |
| 安全区 | 字幕避开底部商品卡/右侧互动按钮 [F-024] |
| 模式标识 | 生成合成内容须过 AI 标识合规门 [F-031、S20]（操作见 [02 §6](02-pipeline-and-selection.md)） |
| 互动 H5 | ≤8MB、零外链、单入口 index.html [F-011] |

> 提示：平台规格与审核政策随时间变动，发布前以平台当期官方规范复核——本表只收录调研时点的 skill 内置口径。

---

- [🏠 返回知识包首页](../index.md)
- [上一篇：生产管线与选型](02-pipeline-and-selection.md)
