---
type: Reference
id: "short-video-skills-concept-03"
title: "实战教程四线：口播/知识、AI 艺术片、带货、复盘分析"
category: "short-video-skills"
tags: ["实战", "教程", "ffmpeg", "edge-tts", "Seedance", "跳变复刻"]
date: "2026-10-20"
last_verified: "2026-10-20"
status: "stable"
author: "SpecWeave Agent（session sc-20261020-video-skill-wiki）"
summary: "四条可落地流水线的操作骨架：B 范式口播知识线、A 范式 AI 艺术片线、带货复刻线、复盘分析线；含命令骨架与验收门。"
source: "../references/source-inventory.md"
---

# 03 实战教程四线

> 以下为操作骨架（各 skill 的具体命令以本机安装版本的引用文件为准），四条线均以 storyboard.json 为中间契约。所有命令骨架来自对应 skill 文档原文事实 [F-010、F-013~F-017、F-019~F-026]。

## 线 1：口播/知识讲解线（范式 B · 量产主力）

**输入**：一个话题或一篇文章。**参考形态**：knowledge-video、short-video-maker、github-trending-douyin [F-019、F-021、F-025]。

1. **策划**：Agent 选题与受众 → 按公式写钩子（9 型钩子 3 秒定生死）与分段口播稿 [F-024]；**事实先行**：数字/价格/排名类论断先联网核实，无法核实则改写或删除，信源 URL 记入 storyboard `sources` [F-022]
2. **配音**：`edge-tts` 逐句合成（免 Key）或本机 `local-tts`（Intel AIPC 离线）；记录每句 `tts_duration` 回填 storyboard [F-021]
3. **排版**：R 侧选视觉形态——Pillow 直绘风格卡帧（资讯类）[F-021]、PPT 逐段导出（教学类）[F-025]、HTML/GSAP 动效（质感类，`npx hyperframes init --example <name>` 起步，`inspect`/`preview` 转 `render`）[F-012、F-013]
4. **合成**：ffmpeg 拼 9:16 + ASS 字幕 + BGM 自动闪避 + 两遍响度标准化（≈-14 LUFS）[F-024]
5. **质检**：字形/emoji 检测门（如 verify_emoji.py：不过门不合成）[F-021]；平台规格导出 [F-024]

**验收**：成片前 3 秒过观众 3-s 快看；字幕逐帧可读；响度达标。

## 线 2：AI 艺术片线（范式 A · 低产高质）

**输入**：节日祝福/产品大片/虚构剧情。**参考形态**：classical-festival-video（本机）、ai-video-creator [F-010、F-023]。

1. **立意**：先定情感分寸/品牌基调（如"祝福重量 ≤ 关系深度"矩阵），再定美学基调 [F-010]
2. **关键帧**：Seedream 生成 3 张一致性分镜静图（竖版 1440x2560、风格锚点句每张必带、负向约束"绝不能出现任何文字/汉字/印章"）[F-008、F-010、F-023]
3. **目检门**：关键帧先交用户目检（无乱码字/主体唯一/风格达标），不过只重生成帧，不消耗视频生成额度 [F-010]
4. **图生视频**：Seedance I2V（或可灵 3.0），首尾帧衔接保连贯，`generate_audio` 按需（仅 Seedance 1.5）[F-007、F-020]
5. **合成交付**：ffmpeg 拼接成片 + 随片文案（文字走文案通道而非画面）[F-010、F-023]

**验收**：全片无崩字、单主体贯穿、分寸矩阵逐句自查（不越阶）。

## 线 3：带货/电商复刻线（范式 B 为主 + A 点睛）

**参考形态**：ecommerce-video-skills 13-skill 簇 [F-024]。

1. **复刻/破题**：丢爆款链接或转写 → viral-remake 八维拆解出 5-beat 结构 → 换成自家商品直接产出 storyboard.json
2. **钩子**：hook-3s-script 一次出 6~10 版，标 Top3；广告法绝对化用语自检（"最/第一/绝对"类词回报）
3. **分镜静图**：selling-point-storyboard 输出每镜一信息的 storyboard.json；商品一致性锁（形状/颜色/Logo 约束词先锁）[F-024]
4. **镜头**：multi-model-shot-prompts 出中性提示词（Seedance/可灵/Veo 皆可接），**本地 Ken Burns 兜底**保证零 Key 工程
5. **成片**：edge-tts 逐句 → ASS 四样式字幕（避开底部商品卡/右侧按钮安全区）→ xfade 转场 → BGM 闪避 → 响度标准化
6. **导出**：platform-spec-export 按抖音/TikTok Shop/视频号/小红书/淘宝主图/Amazon 分版；cover-title-AB 出封面+标题 A/B 测试记录

## 线 4：复盘/分析线（用已有视频反哺选题）

**输入**：任意视频 URL 或竞品主页。**参考形态**：hook-analyzer + report-generator [F-016、F-017]。

1. **拆解**：先经分镜拆解工序产出 breakdown.json（含每段时长/关键帧 URL/运镜）
2. **钩子评分**：`python scripts/analyze_hook_segments.py breakdown.json` 提取前三秒病学；LLM 按 30/25/15/15/15 五维权重评分 [F-016]
3. **生成报告**：`python scripts/generate_report.py breakdown.json hooks.json > report.md`（基本信息/钩子/分镜/BGM/场景章节）[F-017]
4. **反哺**：报告中的优势/不足/优化建议写入下次 storyboard 的钩子策略——即"分析 → 复盘 → 再制作"的闭环入口

**验收**：report.md 五章节齐全；评分理由引用关键帧可回查。

## 平台规格速查（⑤ 段共用）

| 维度 | 典型口径（生态事实） |
|---|---|
| 竖屏分辨率 | 1080x1920（主流）[F-020、F-022] 或 1440x2560（HyperFrames 竖版）[F-013、F-025] |
| 时长 | 15s（剪辑起步）/ 10s（节日情感片）[F-010] |
| 音频 | 响度标准化 ≈ -14 LUFS [F-24 foutrou]；BGM 对人声 ducking |
| 安全区 | 字幕避开底部商品卡/右侧互动按钮 [F-024] |
| 互动 H5 | ≤8MB、零外链、单入口 index.html [F-011] |

> 提示：平台规格随审核政策变动，发布前以平台当期官方规范复核——本表只收录调研时点的 skill 内置口径。

---

- [🏠 返回知识包首页](../index.md)
- [上一篇：生产管线与选型](02-pipeline-and-selection.md)
