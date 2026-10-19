---
type: Reference
id: "article-to-video-03-trae-workflow"
title: "03 · TRAE 落地工作流：从零代码到 Skill 编排"
category: "tech"
tags:
  - AI视频
  - TRAE
  - Seedance
  - Seedream
  - hyperframes
date: "2026-10-18"
status: "verified"
source: "session sc-20261018-article-to-anime-video；本机 Skill 命令以各 SKILL.md 实测签名为准（F-052~F-057）"
---

# 03 · TRAE 落地工作流：从零代码到 Skill 编排

[返回知识包首页](../index.md)

本页给两条路径：**路径 A 零代码 C 端**（今天就要成片）与**路径 B TRAE Skill 编排**（可复用、可批量、可复现的生产线）。二者共享第 1–2 段（确权/镜头表），从第 3 段分叉。

## 路径 A：零代码 C 端（无 API Key、无命令行）

| 段 | 操作 |
|---|---|
| 1–2 | 用任意 LLM 对话窗口把文章改成竖屏短剧脚本，再让它输出"镜号/景别/画面/旁白/对白/时长"分镜表（模板见下） |
| 3–5 | **即梦**（jimeng.jianying.com）：建主体库（角色外观 + 音色绑定）→ Agent 模式 `/创作分镜` `/叙事短片导演分镜`，逐镜生成；或直接用**火山剧创** Web 端"剧本→设定→分镜→视频"四步（F-027）；想要可编排 Agent 用**扣子**官方漫剧模板（F-028） |
| 6 | 剪映自带朗读/AI 配音；正面对白用剪映"照片生成多人对话场景"自动口型（F-043） |
| 7 | 剪映 Hub 无限画布拼接、自动字幕、转场 |
| 8 | 句易网/句无忧过一遍违禁词；核对商用授权与水印后发抖音/视频号/红果 |

> 个人最小组合：**即梦会员 + 剪映 AI Ultra**。团队工业化：火山剧创 / SkyProduction / LibTV / 扣子（见 [02 工具图谱](02-tool-map.md)）。

## 路径 B：TRAE Skill 编排（八段的工程化实现）

### 环境前提

- `ARK_API_KEY`（火山方舟，Seedream + Seedance 共用；亦可分别设 `MODEL_IMAGE_API_KEY` / `MODEL_VIDEO_API_KEY`）
- `LISTENHUB_API_KEY`（tts / explainer）
- 相关 Skill：`byted-seedream-image-generate`、`byted-seedance-video-generate`、`tts`、`explainer`、`hyperframes`

### 第 1–2 段：剧本拆镜（LLM 产出镜头表）

把原文与以下要求交给对话模型，产出物是一份 CSV/JSON 镜头表（schema 见 [01 §3](01-pipeline.md#3-镜头表管线的核心中间产物)）：

**剧本改编 Prompt 模板**：

```text
你是竖屏短剧编剧。把下面这篇文章改编为 9:16 竖屏短剧（单集 60–90 秒）。
要求：
1. 前 3 秒必须有钩子（悬念/冲突/反常画面），每 8–15 秒一个节拍（钩子→冲突→反转）；
2. 只保留一个主角视角，群像改为先后出场；不要旁白解释剧情，用动作和对白呈现；
3. 输出两部分：①角色表（角色ID、年龄、服装、发型、色板、音色描述）；
   ②镜头表 CSV，列：shot_id,duration_s,shot_size,camera,visual_prompt,char_ids,scene_id,narration,dialogue；
4. visual_prompt 只写可见内容（主体/动作/环境/光线/画风锚点），禁止写抽象词与任何文字（招牌、字幕、信件内容都不要出现在画面）。
原文：<<<粘贴文章>>>
```

### 第 3 段：资产先行（Seedream 出角色三视图与场景）

```bash
# 角色三视图（首图用文生图，之后用 -i 图生图锁同一张脸做正/侧/背与表情扩展）
python scripts/seedream_image_generate.py \
  --version 5.0 -s 1080x1920 --no-watermark --output-format png \
  -p "角色三视图（正面/侧面/背面），16岁少女，齐耳短发、靛蓝粗布衣裳、草鞋，\
吉卜力水彩风，柔和晨光，素色背景，角色设定稿，无文字"

# 以首图为参考做表情/服装扩展，保证同一角色
python scripts/seedream_image_generate.py \
  --version 5.0 -s 1080x1920 --no-watermark \
  -i "<三视图URL>" \
  -p "同一角色，半身像，惊讶表情，黄昏稻田场景，吉卜力水彩风，无文字"

# 场景定妆图
python scripts/seedream_image_generate.py \
  --version 5.0 -s 1920x1080 --no-watermark \
  -p "南方山村稻田全景，黄昏逆光，远处炊烟，吉卜力水彩风，空镜无人，无文字"
```

纪律：产出 URL **24 小时过期**，立即下载落盘并按 `CHAR_01_front.png`、`SCENE_07.png` 编号入 `assets/`。每个角色先做一张多角色同框测试图，确认不会"换脸"再进入下一段。

### 第 4–5 段：关键帧定稿 → 逐镜生成（Seedance）

```bash
# 每镜先出首帧（图生图，携带角色三视图参考）
python scripts/seedream_image_generate.py --version 5.0 \
  -s 1080x1920 --no-watermark \
  -i "assets/CHAR_01_front.png" \
  -p "少女站在稻田边，风掀起衣摆，手搭凉棚望向远山，黄昏逆光，吉卜力水彩风，无文字"

# 图生视频：首帧 + 参考图（角色+场景），竖屏 5–10 秒，批量时逐镜提交
python scripts/video_generate.py \
  -p "[图1]少女保持衣着与面容不变，风吹动头发与衣摆，缓缓向前走两步，\
镜头缓慢推进，电影感" \
  -n S01C03 \
  -f "frames/S01C03_in.png" \
  --ref-images "assets/CHAR_01_front.png" "assets/SCENE_07.png" \
  -r 9:16 -d 5 --resolution 720p --no-watermark

# 需要对白/环境音时用 Seedance 1.5
python scripts/video_generate.py \
  -m doubao-seedance-1-5-pro-251215 \
  -p "少女回头说话，口型自然，背景有风声与蛙鸣" \
  -n S01C04 -f "frames/S01C04_in.png" \
  --ref-images "assets/CHAR_01_front.png" --generate-audio \
  -r 9:16 -d 6 --resolution 1080p --no-watermark
```

实测参数边界（来自 Skill 签名）：时长 2–12 秒；参考图 1–4 张、参考视频/音频各不超过 3 个且总时长 ≤15s；超时用 `-q <task_id>` 查任务；模型报 `ModelNotOpen` 时回退 `doubao-seedance-1-5-pro-251215` → `doubao-seedance-1-0-pro-250528`。

**视频 prompt 组装公式**：`[图N]主体一致性声明 + 单一动作 + 运镜 + 氛围`；一个镜头只写一个动作、只出现一个主体（多角色先过同框测试）。

### 第 6 段：声音（tts 双模式）

- 旁白（单声）：tts quick 模式 `POST /v1/tts`，body `{"input": "...", "voice": "<speakerId>"}`，同步返回 MP3。
- 多角色对白：tts script 模式 `POST /v1/speech`，按镜头表 dialogue 列组装：

```json
{
  "scripts": [
    {"content": "等等我！", "speakerId": "<CHAR_02 的 speakerId>"},
    {"content": "快点，太阳要落山了。", "speakerId": "<CHAR_01 的 speakerId>"}
  ]
}
```

返回 `audioUrl` + `subtitlesUrl`（自带字幕，可直接喂给第 7 段）。speakerId 不硬编码，从 speakers API 选取。正面对白口型用 sync.so / HeyGen / 本地 LatentSync 后处理（API 价格见 [02 第五层](02-tool-map.md)）。

### 第 7 段：合成（hyperframes 代码化，或剪映）

需要**可复现/批量改词重渲染**时走 hyperframes：

```bash
npx hyperframes init        # 初始化 HTML 工程（视频事实源 = HTML + data-* 时序）
npx hyperframes lint        # 结构/时间属性检查
npx hyperframes validate    # 资产与时间轴校验
npx hyperframes render      # 渲染出片
```

在 HTML 中按镜头表组织：视频片段轨道、tts 音频轨道、字幕轨（字幕文本来自镜头表 narration/dialogue）、转场与 GSAP 运镜。换文案只改数据变量即可批量重渲（模板/活动视频尤其划算）。一次性的片子直接用剪映，不必工程化。

### 第 8 段：验收清单（不可省略）

- [ ] 物理量：分辨率/时长/帧率/文件大小与镜头表逐行核对（不能只看接口返回 success）
- [ ] 目检：每镜主体唯一、面容与角色卡一致、无多余肢体、画面无崩字、口型对齐
- [ ] 声音：响度统一、无截断；旁白与对白声道平衡
- [ ] 合规：文本改编授权、TTS 声音授权、BGM 来源、人脸视频条款、水印/C2PA
- [ ] 过审：句易网/句无忧违禁词检测（投流平台规则各查一遍）

## 捷径：用现有 Skill 直接覆盖的三类需求

| 需求 | 直接用 | 说明 |
|---|---|---|
| 文章→单主播解说视频（知识科普/课程） | **explainer**（mode=`info` 或 `story`，恰好 1 个 speaker） | 提交 `POST /storybook/episodes`（sources/speakers/language/mode），轮询 2–3 分钟出脚本，再调 video 端点 3–5 分钟出片 |
| 3 关键帧→10 秒竖版短片（节日/金句/邀请） | **classical-festival-video** 范式 | 已验证的最小闭环：3 张关键帧 + 单主体 + 一镜到底，适合先跑通管线再扩长 |
| 只要配音/有声书 | **tts**（quick / script） | script 模式返回字幕，可直接进剪辑 |

## 最小实践顺序（建议第一次就这么做）

1. 拿一篇 500 字短文，用剧本 Prompt 拆出 6–8 个镜头；
2. 只做 1 个角色 + 2 个场景的资产；
3. 先完整产出 **1 个 10 秒镜头**（关键帧→视频→配音→合成→验收），跑通全链路；
4. 再批量生成剩余镜头——**先打通再放量**，避免一次性生成几十个镜头后发现角色不一致全部返工。

下一页：[04 · 三种配方、成本账与避坑](04-recipes-and-pitfalls.md)
