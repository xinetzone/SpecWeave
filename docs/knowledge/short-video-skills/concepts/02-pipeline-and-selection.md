---
type: Reference
id: "short-video-skills-concept-02"
title: "生产管线与选型：工序五段·双范式选型法"
category: "short-video-skills"
tags: ["选型", "流水线", "storyboard.json", "范式"]
date: "2026-10-20"
last_verified: "2026-10-20"
status: "stable"
author: "SpecWeave Agent（session sc-20261020-video-skill-wiki）"
summary: "短视频生产五段工序模型、成片双范式（生成式 vs 程序排版）判定、skill 映射矩阵与选型决策树，附 storyboard.json 中间契约。"
source: "../references/source-inventory.md"
---

# 02 生产管线与选型：工序五段·双范式选型法

> 模式成熟度：L1（跨 ≥2 个生态方案验证形态一致，可迁移性经对抗审查 migrated 到播客/资讯领域）

## 1. 适用于 / 不适用于

**适用于**：任何"让 Agent 帮我做短视频，帮我选/搭 skill 流水线"类任务；个人量产（口播/知识/带货）与企业批量生产均适用。

**不适用于**：①只要一条随手拍素材（手机直拍直传，无需 skill）；②互动 H5 玩法类的抖音互动空间交付（那是 douyin-interact-creation 的自有约束体系 [F-011]）；③追求逐帧 keyframe 手工精修的电影级制作（本文方法覆盖约 80% 常规剪辑 [F-026 自报]，其余属人工领域）。

## 2. 五段工序模型

生态中所有头部流水线（本机 + 开源 8 仓库）都能映射到同一组工序 [F-019、F-020、F-022~F-026]：

```mermaid
flowchart LR
    S1["① 策划<br/>选题/钩子/脚本/分镜"] --> S2["② 素材<br/>静图/实拍/生成/抠像"]
    S2 --> S3["③ 音频<br/>TTS配音/ASR校对/BGM"]
    S3 --> S4["④ 合成<br/>渲染/字幕/转场/响度"]
    S4 --> S5["⑤ 发布质检<br/>平台规格/封面/合规门"]
```

| 工序 | Agent 负责（创意判断） | 脚本/CLI 负责（机械执行） | 质量门标配 |
|---|---|---|---|
| ①策划 | 选题、受众、钩子类型、分镜结构（如 5-beat） | 转写竞品作对标输入 | 事实先行：论断未核实不进脚本 [F-022] |
| ②素材 | 画面方向、风格锚点、一致性约束词 | 文生图/图生图调用、Ken Burns 直出 | 用户目检预览门（生成画面禁汉字）[F-010] |
| ③音频 | 口播稿改写、音色推荐 | edge-tts/Kokoro/local-tts 逐句合成、ASR 校对时长 | 响度标准化（≈-14 LUFS 两遍）[F-024] |
| ④合成 | 转场/花字/节奏决策 | ffmpeg/Remotion/HTML 渲染、ASS 字幕、BGM 闪避 | 字形检测（emoji/汉字）[F-021] |
| ⑤质检发布 | 发布文案策略、AB 标题 | 平台导出（9:16 安全区）、封面挑帧 | 平台规格+广告法自检 [F-024] |

## 3. 双范式判定（核心决策）

**范式 A：生成式成片。** 适用：品牌感强、前期高投入低产量、每秒画面价值高（产品/节日情感/虚构剧情）。约束：秒级计费、需要 API Key（ARK 等）[F-007]、生成分镜/脚本/成片全链有 SEAL/一致性约束词表 [F-020、F-023]；AI 画面禁出现可辨文字 [F-010]。

**范式 B：程序排版成片。** 适用：解说、知识、资讯、带货主图、批量复刻——内容核心是"信息+节奏"而非画面奇观。特征：零 Key、本地 ffmpeg/Ken Burns/Pillow/HTML 渲染兜底 [F-021、F-024、F-025]，每个镜头有固定预算（时长与信息密度），生成模型退化为可选项。

**判定规则**：先用 B 成片 dry-run 出 15s 预览稿（Ken Burns/黑本书页），观众承诺后再评估是否需 A 补关键镜头。错用 A �解决的三个误区：烧钱抂数量、一致性失控、修改迭代贵。

## 4. skill 映射矩阵（每段 1~2 个候选）

| 工序 | 优先候选（带质量门） | 备选 | 本机可用 |
|---|---|---|---|
| ①策划 | hook-3s-script（9 型钩子）、viral-remake（复刻拆解） | LLM 自由发挥 | ✅（LLM 本能） |
| ②素材 | selling-point-storyboard / Seedream 分镜静图 | Pexels/Pixabay 实拍素材 [F-022] | ✅ byted-seedream / image-gen |
| ③音频 | ai-voiceover-edge-tts / hyperframes-media tts | local-tts（离线 AIPC）、TTS 大厂 API | ✅（宿主层也更 idiots） |
| ④合成 | ffmpeg-auto-assemble / hyperframes render / short-video-maker(Remotion) | 表演级可选 Seedance I2V | ✅ hyperframes+mediakit |
| ⑤发布质检 | platform-spec-export / cover-title-AB | 手工导出 | ✅ |

选型时对每个候选过"三问门禁"（见 index.md 洞察 3）。

## 5. 中间契约：storyboard.json

多 skill 协作的通用做法是用一个结构化分镜文件串接所有工序 [F-019、F-022、F-024]：策划 skill 写入 `hook/scene/duration/screen_text/sources`，音频 skill 按句合成并回填 `tts_duration`，合成 skill 消费全部字段渲染，导出 skill 按 platform goal 产出。**契约的价值**：单点 skill 可替换（换 TTS 引擎/换渲染器不动上游）——这正是洞察 1"簇而非单体"的工程表达。

## 6. 反模式

1. **单点全能幻想**：找"一个最强的短视频 skill"一步到位——生态头部全采取簇+双轨分工。
2. **默认接视频模型**：量产内容全走 T2V/I2V——成本、一致性、返工全线恶化。
3. **模型自评代替目检**：让模型自己说"效果很好"就交付——一切走人眼的门禁面前 FDA 是"表演式审查"。

## 7. 检验标准

方案合格当且仅当：每个工序有≥1 候选 skill 且标注门禁；存在 storyboard.json 契约；成片 prior 到 dry-run 可 0 成本地预览；交付包内含可审计 sources。

## 8. 迁移验证

同五段模型已验证可迁移至：图文排版流水线（素材带换水印/字幕带换格式）、播客制作（③ 音频为主工序、④ 合成退化为拼接）、数字人直播课件（② 素材带换数字人资产）。三个领域形态一致，故判定跨域成立。

---

- [🏠 返回知识包首页](../index.md)
- [上一篇：生态全景](01-landscape-and-spec.md)
- [下一篇：实战教程四线 →](03-recipes.md)
