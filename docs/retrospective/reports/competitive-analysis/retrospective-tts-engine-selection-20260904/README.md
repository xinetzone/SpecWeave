---
title: "TTS 引擎选型深度报告：sherpa-onnx/Matcha / Edge TTS / Gemini TTS / KittenTTS / Piper"
date: 2026-09-04
updated: 2026-09-04
source: "Hermes Agent 首次配置向导 TTS 提供商选择菜单（场景：个人 AI Agent 语音朗读/语音交互）"
method: "七概念方法论编排（场景5 创新突破：F→V→I），session=sc-20260904-tts-provider-selection；v2 增量修订：V-1 预言证实后重构推荐结构"
tags: [tts, 选型, sherpa-onnx, matcha, edge-tts, gemini, piper, kittentts, hermes]
revision:
  - "v1 (2026-09-04)：四引擎首版，推荐 Edge TTS 默认 + Piper 兜底"
  - "v2 (2026-09-04)：Edge TTS 403 已发生（F-025），补入 sherpa-onnx/Matcha 本地中文方案（F-026~F-030），推荐结构改为本地 Matcha 为主"
---

# TTS 引擎选型深度报告：sherpa-onnx/Matcha / Edge TTS / Gemini TTS / KittenTTS / Piper

> 方法论：七概念编排 **F（第一性原理）→ V（对抗审查）→ I（洞察落地）**。F 前完成 Web 事实采集（F-001~F-030），F 后强制 4 视角对抗审查，I 阶段形成决策矩阵。
> 场景边界：**Hermes 这类个人 AI Agent 的语音朗读/语音回复**，非商用播客制作、非嵌入式设备量产。
>
> **v2 重大变更**：Edge TTS 免费端点已被微软反滥用机制封锁（F-025，v1 中 V-1 预警的风险已实际发生）。中文轻量本地首选从"Piper 兜底"升级为 **sherpa-onnx + Matcha 中文模型（F-026~F-030）**。

---

## 一、事实清单（R 阶段，无因果词）

> 来源：官方文档与 2025-08 ~ 2026-09 公开实测文章，逐条可追溯。

### Edge TTS（非官方 edge-tts Python 库）

- F-001：edge-tts 是第三方 Python 库，调用微软 Edge 浏览器「在线朗读」服务，**无需 Edge 浏览器、无需 Windows、无需 API key**，`pip install edge-tts` 即用。
- F-002：支持 140+ 语言/地区、400+ 神经语音（中文含 zh-CN-XiaoxiaoNeural 女声、zh-CN-YunxiNeural 男声等）。
- F-003：输出 MP3，支持语速/音量/音调微调（rate/volume/pitch），可同时生成 SRT/VTT 字幕。
- F-004：**在线服务**，每次合成需联网；长文本需分块（社区实践按 ~500 字符分块）。
- F-005：历史上出现过 403 访问限制（User-Agent 验证/区域限制），曾靠升级库版本修复（如 6.1.15）。
- F-006：许可证 MIT/LGPL 双许可；服务本身是微软未公开承诺的免费端点，无 SLA、无商用授权条款。
- **F-025（v2 新增·已发生事实）**：2026-08 起多位用户实测 edge-tts 返回 **403 Forbidden "Our services aren't available right now"**；微软加强反滥用机制，此前可用的 `Sec-MS-GEC` token 鉴权方式已失效，表现为免费端点被封/不稳定（来源：openclaw 社区迁移实录 2026-08-12）。v1 报告 V-1 预警的"端点随时被封"已实际发生。

### Google Gemini TTS（gemini-3.1-flash-tts-preview）

- F-007：Google DeepMind 专用 TTS 模型，模型 ID `gemini-3.1-flash-tts-preview`，2026-04-15 发布，经 Gemini API / AI Studio / Vertex AI 提供。
- F-008：30 种预置语音（神话/天文命名：Kore、Puck、Aoede、Charon 等），70+ 语言及地区变体。
- F-009：支持 200+ 内联音频标签（`[whispers]`、`[laughs nervously]`、`[slow]`、`[fast]` 等）与自然语言风格 prompt，可句中切换情绪/节奏；原生多说话人对话。
- F-010：定价：输入 $1.00 / 百万 token，音频输出 **$20.00 / 百万 token**；批处理 $0.50 / $10.00（五折）。AI Studio 免费层有速率限制。
- F-011：所有生成音频带 **SynthID 水印**；**免费层输出不授权商用**，商用需付费 Cloud Billing。
- F-012：Hermes 菜单标注其为 `[preview]`；需要 Google API key。

### KittenTTS

- F-013：KittenML 开源 TTS，1500 万参数，三档模型：nano（<25MB）/ micro（41MB）/ mini（80MB），ONNX/PyTorch，**纯 CPU 推理，无需 GPU**。
- F-014：内置 8 种音色（4 男 4 女，expr-voice-2~5），24kHz 采样率。
- F-015：**目前主要支持英语**（中文等多语言为未来计划）；首次运行下载权重后可完全离线。
- F-016：项目处于**开发者预览阶段**（模型权重、移动 SDK、网页版部分清单未完成），GitHub ~12.4k stars，v0.8（2026-03 前后）。

### Piper

- F-017：Open Home Foundation 维护（原 rhasspy/piper，2025-10 归档只读，活跃开发转至 OHF-Voice/piper1-gpl，v1.4.2 / v1.7.0，2026 年仍在提交）。
- F-018：VITS 架构导出 ONNX + espeak-ng 音素化，`pip install piper-tts`；语音模型为独立文件（x_low/low/medium/high 质量档，每个 tens of MB，约 20-90MB）。
- F-019：**44 种语言、100+ 语音**，含中文 zh_CN-huayan-medium 等；试听页 rhasspy.github.io/piper-samples。
- F-020：性能：树莓派 5 上 medium 语音可实时合成（无 GPU），现代桌面 CPU 上比实时快约一个数量级；本地生成约 0.5-1s 量级。
- F-021：生态：Home Assistant 默认 TTS（Wyoming 协议）、NVDA 屏幕阅读器、LocalAI 使用；提供 CLI / Python API / HTTP server / C++ 绑定。
- F-022：**许可证变化**：旧 rhasspy/piper 为 MIT（已归档），现行维护版 piper1-gpl 为 **GPL-3.0**。
- F-023：模型从 HuggingFace 下载，国内网络可能需 hf-mirror.com 镜像。
- F-024：社区评价：音质"能听出是 TTS"，约为 macOS 系统语音 10 年前水平（主观样本，建议试听页自行确认）；不做声音克隆。

### sherpa-onnx + Matcha 中文模型（v2 新增·中文轻量本地首选）

- F-026：sherpa-onnx 是 k2-fsa 出品的跨平台语音推理工具包（C++ 核心，Apache-2.0 许可），基于 ONNX Runtime，提供 Python/Java/C++ 等原生绑定；TTS 可加载 VITS / Matcha / Kokoro 等多种模型，纯 CPU 可跑。
- F-027：中文实测三模型（openclaw 纯 CPU 迁移实录，2026-08）：
  - **matcha-icefall-zh-en** ⭐：声学模型 ~72MB + vocoder ~51MB（vocos-16khz-univ），RTF 0.04（**比实时快约 25 倍**），单说话人，实测音质"像微软晓晓"，推荐；
  - vits-zh-aishell3：~200MB，RTF 0.02（最快），**174 个说话人**可选，适合多音色需求；
  - vits-melo-tts-zh_en：~170MB，RTF 0.25，实测"像外国人学中文"，不推荐。
- F-028：模型文件托管于 HuggingFace（如 csukuangfj/sherpa-onnx-matcha-icefall-zh-en，含 model-steps-3.onnx、vocos-16khz-univ.onnx、lexicon.txt、tokens.txt、espeak-ng-data）；国内可用 hf-mirror.com 镜像。
- F-029：sherpa-onnx 同样支持加载 Kokoro-82M 模型（~50MB 档，MIT）；Kokoro 共 82M 参数、90+ 预设音色、ONNX 可部署到边缘/浏览器，英文质量突出，但多方实测**中文质量一般**。
- F-030：生态对比：sherpa-onnx 有官方 Java 原生 API（团队内网离线 TTS 选型中因"Jar 包即服务"击败 Piper/PaddleSpeech）；可封装为 OpenAI 兼容 `/v1/audio/speech` 本地 HTTP 服务供 Agent 调用。

> 重量级参考（不符合"轻量"，不在主推荐内）：ChatTTS（39k★，中文对话最自然）、GPT-SoVITS（59k★，少样本声音克隆，中英日混合）、微软 VibeVoice（49k★，Apache-2.0）、阿里 CosyVoice（21k★，中文字符错误率 1.12%）、Qwen3-TTS（0.6B/1.7B）——多需 GPU 或 1GB+ 显存。

---

## 二、F 阶段：第一性原理拆解

### 2.1 问题界定

不是"哪个 TTS 最好"，而是：**在个人 AI Agent 场景下，文本→语音这条链路上，哪些是不可再分的本质要素，哪些是可堆叠的增强属性？**

### 2.2 假设剥离（把默认假设逐条归零验证）

| # | 隐含假设 | 归零验证 |
|---|---------|---------|
| A1 | "推荐的就是最好的" | ⚠️ 菜单的 ⭐ 标注的是**零配置成本**（免费、无 key），不是音质/可控性最优。推荐的对象是"不想配置的人"。 |
| A2 | "免费 = 无成本" | ❌ Edge TTS 免费但成本是**联网依赖 + 非官方端点稳定性风险**（v2：风险已兑现，F-025）；本地引擎成本是模型下载 + CPU/内存占用。 |
| A3 | "本地 = 隐私好 = 一定更优" | ⚠️ 本地引擎消除数据外传和按量计费，但代价是音质档位和语言覆盖；且对"朗读 AI 回复"场景，回复内容本就要发给云端 LLM，TTS 走云的边际隐私增量很小。**但本地引擎额外提供了"服务不被封"的可持续性，这一条在 v2 权重上调。** |
| A4 | "音色越多越好" | ❌ 个人 Agent 实际固定使用 1-2 个音色。400 音色与 8 音色在该场景效用无差异；**语言覆盖**（中文有没有、好不好）才是硬约束。 |
| A5 | "可控性（情绪标签）是刚需" | ❌ 200+ 音频标签是播客/有声书/游戏场景的杀手锏；Agent 回复朗读只需"清晰、自然、断句正常"。这是**场景错配的功能**。 |
| A6 | "在线 TTS 都一样可靠" | ❌ Edge TTS 是逆向的未公开端点（F-005/F-006/F-025），Gemini 是官方付费 API 带 SLA——两者"在线"但法律与稳定性地位完全不同。 |
| A7（v2 新增） | "本地中文必然又机械又难装" | ❌ sherpa-onnx + Matcha 在纯 CPU 上 RTF 0.04、音质实测接近微软晓晓（F-027），且 pip 安装 + 模型文件即可，打破了"本地中文=Piper 那种机械感"的旧印象。 |

### 2.3 不可再分的基础要素（公理层）

1. **可懂度（Intelligibility）**：发音正确、断句合理、数字/代码可读——不过线一切免谈。
2. **语言匹配（Language Fit）**：使用者的主力语言必须有高质量语音（本场景：中文）。
3. **可获得性（Accessibility）**：成本（钱）、配置（key/注册）、网络（在线/离线）三者构成的获取门槛。
4. **可持续性（Sustainability）**：服务会不会停/被封、条款是否允许该用途、许可证是否传染。**（v2：Edge 被封后，此公理从"风险项"升级为"一票否决项"）**
5. **延迟（Latency）**：从文本到出声的等待，影响对话体感（本地 RTF 0.02~0.25 vs 云端流式）。

增强属性（非公理，按场景加权）：表现力/情绪控制、音色数量、声音克隆、字幕生成、采样率。

### 2.4 自下而上重构：决策结构（v2 重构）

```
TTS 选型决策树（个人 AI Agent 场景 · v2）
│
├─ Q1 主力语言是中文？
│   ├─ 是 → KittenTTS 出局（仅英语，F-015）；进入 Q2
│   └─ 否（英语为主）→ KittenTTS / Kokoro / Piper 皆轻量可选
│
├─ Q2 核心诉求？
│   ├─ 中文 + 本地 + 免费 + 音质好（桌面 CPU）
│   │   └─ ★ sherpa-onnx + matcha-icefall-zh-en（RTF 0.04，音质近晓晓，F-027）
│   ├─ 中文 + 离线 + 多音色/嵌入式/智能家居生态
│   │   └─ Piper（HA/NVDA 生态）或 sherpa vits-zh-aishell3（174 说话人，F-027）
│   ├─ 始终联网 + 要表现力/多说话人/句中情绪，且有 GCP key/愿付费
│   │   └─ Gemini TTS（官方 SLA，免费层禁商用）
│   └─ 只想零配置临时用、能接受随时失效
│       └─ Edge TTS（⚠️ 端点 2026-08 起已大面积 403，F-025，不再作为默认）
│
└─ Q3 预算与商用？
    ├─ 个人非商用朗读 → sherpa-onnx（Apache-2.0）/ Piper 零成本本地
    └─ 商用产品 → Gemini 付费层（F-011）；Piper 注意 GPL-3.0 传染（F-022）；sherpa-onnx Apache-2.0 友好
```

---

## 三、V 阶段：4 视角对抗审查

> 对 2.4 的决策结构进行攻击。v1 共 8 条意见、采纳 6 条；v2 复核并新增 V-9。

### 🔴 视角 1：魔鬼代言人（刻意挑刺）

- **V-1（P1）**：Edge TTS 的"免费无 key"建立在逆向工程的未公开端点上——微软随时可以改鉴权/封端点/收费。→ **v1 采纳：定位为"个人玩具"并给本地兜底；v2 状态更新：预言已证实（F-025，2026-08 大面积 403），Edge TTS 降级为"临时可用、随时失效"，不再作为默认推荐。**
- **V-2（P2）**：Gemini TTS $20/百万输出 token，长篇朗读成本会累积。→ **采纳**：成本量级注记见 4.4。
- **V-3（P2）**：KittenTTS 中文用户选了即不可用。→ **采纳**：决策树 Q1 出局标红。
- **V-4（P3）**：Piper 音质评价是主观样本。→ **部分采纳**：表述为"建议试听页自行确认"。
- **V-9（v2 新增，P2）**：Matcha "音质像晓晓"是单一社区作者的主观结论，RTF 数字来自其特定 CPU；且 sherpa-onnx 配置需手工凑齐 acoustic/vocoder/lexicon/tokens/espeak-ng-data 多个文件，上手摩擦比"pip 装完就能用"高。→ **采纳**：上手节给出完整文件清单与镜像方案；结论中标注"音质为社区实测，建议先跑通 5 分钟样例自行确认"。

### 🟢 视角 2：新人视角

- **V-5（P1）**：新手不懂术语、不知道第一步干嘛。→ **采纳**：第 5 节给最小可运行命令。
- **V-6（P2）**：Windows/国内用户 HuggingFace 下载会失败。→ **采纳**：上手节给出 hf-mirror 镜像（F-023/F-028）。

### 🟠 视角 3：老板视角（投入产出）

- **V-7（P2）**：低频朗读为情绪标签付费 ROI 接近零。→ **采纳**：按场景分档推荐。

### 🔵 视角 4：未来视角

- **V-8（P2）**：本地小 TTS 是趋势，Edge 逆向端点是最可能消失的形态。→ **v1 采纳"默认+兜底"双层架构；v2 状态更新：趋势判断已兑现，架构翻转为"本地为主、在线为增强"。**

---

## 四、I 阶段：洞察落地（决策矩阵与推荐）

### 4.1 核心洞察（四元组）

**洞察 1：菜单的"⭐推荐"推荐的是配置成本，不是综合质量——选型第一性问题是语言，不是功能。**
- 证据：F-001/F-007/F-015/F-019/F-027（中文覆盖差异）、A1。
- 反常识：KittenTTS 虽是"本地免费新星"，中文用户选了即不可用；而真正适合中文的轻量本地方案（sherpa-onnx/Matcha）根本不在 Hermes 菜单里。
- 行动：中文用户先按语言过滤，本地首选直接上 sherpa-onnx + Matcha。

**洞察 2：可持续性差异大于音质差异——逆向免费端点不是"便宜的方案"，而是"租期不定的方案"。**
- 证据：F-005/F-006/F-025（Edge 端点从风险到被封全过程）、F-010/F-011（Gemini 官方 SLA）、F-026（sherpa-onnx Apache-2.0 本地自持）。
- 反常识：v1 报告把 Edge 当默认、Piper 当兜底；仅几个月后 Edge 被封，"兜底"变成了"唯一能用的免费路径"——本地引擎的真正价值不是隐私，而是**不可被远程吊销**。
- 行动：把"服务会不会明天就没了"列为一票否决项；能本地自持的能力不依赖远端免费端点。

**洞察 3：个人 Agent 朗读场景下表现力是伪需求，但"本地中文不机械"在 2026 年已成立。**
- 证据：F-009（Gemini 200+ 标签面向内容创作）、F-027（Matcha RTF 0.04、音质近晓晓）、A7。
- 反常识：旧印象里"本地中文 TTS = Piper 那种机械感"，但 Matcha/VITS 级模型在纯 CPU 上已做到接近云端神经语音的自然度，且比实时快 25 倍。
- 行动：默认本地 Matcha（中文），Gemini 仅在内容创作场景启用，Edge 仅作零配置临时项。

### 4.2 决策矩阵（v2：新增 sherpa-onnx 列）

| 维度（权重·中文个人场景） | **sherpa-onnx/Matcha** | Edge TTS | Gemini TTS | KittenTTS | Piper |
|---|:---:|:---:|:---:|:---:|:---:|
| 中文质量/覆盖 | ★★★★ 实测近晓晓 | ★★★★ 神经语音（在线） | ★★★★ 70+语言 | ✗ **仅英语** | ★★★ 有中文、偏机械 |
| 成本 | 免费 | 免费（端点已不稳） | 免费层限流/付费 $20/百万 | 免费 | 免费 |
| 配置摩擦 | ★★★ pip+模型文件 | ★★★★★ 无 key | ★★ 需 GCP key | ★★★★ pip 即用 | ★★★ 需下模型 |
| 离线可用 | ✓ 离线 | ✗ 在线 | ✗ 在线 | ✓ 离线 | ✓ 离线 |
| 延迟 | ★★★★★ RTF 0.04（快25×） | 在线流式，依赖网络 | 在线，低延迟宣传 | 本地快（CPU） | ★★★★ 本地 0.5-1s |
| 可持续性 | ★★★★★ 本地自持·Apache-2.0 | 🔴 **已大面积 403（F-025）** | ★★★★★ 官方 API | ⚠️ 预览期 | ★★★★ 基金会维护 |
| 许可证 | **Apache-2.0（商用友好）** | MIT/LGPL（库） | 商用需付费 | 开源 | ⚠️ **GPL-3.0**（新版） |
| 表现力 | 基础（多说话人模型可选） | 语速/音调 | ★★★★★ 200+标签/多说话人 | 基础 | 基础 |
| 资源占用 | ~123MB（Matcha+vocoder） | ~0（云端） | ~0（云端） | 25-80MB | 20-90MB/语音 |

### 4.3 场景化推荐（v2 重构：本地 Matcha 为主）

| 你的情况 | 推荐 | 理由 |
|---|---|---|
| **中文用户、个人用、桌面 CPU（Hermes 主场景）** | **★ sherpa-onnx + matcha-icefall-zh-en** | 本地免费、RTF 0.04、音质近晓晓、Apache-2.0；断网可用、不被封 |
| 想要多音色/嵌入式/智能家居生态 | **Piper** 或 sherpa vits-zh-aishell3（174 说话人） | Piper 生态最成熟（HA/NVDA）；aishell3 音色多；注意 Piper GPL-3.0 |
| 零配置临时用、能接受随时失效 | Edge TTS | 装完即用，但 2026-08 起已大面积 403（F-025），**不建议作为依赖** |
| 英语为主、树莓派/超低配设备 | **KittenTTS**（25MB nano）或 Kokoro-82M | 最小本地引擎；中文不可用/一般 |
| 做播客/有声书/多角色配音、有预算 | **Gemini TTS（付费层）** | 唯一句中情绪控制+多说话人；免费层禁商用、带 SynthID |

### 4.4 成本量级注记（采纳 V-2）

- 本地引擎（sherpa-onnx/Piper/Kitten）：**零边际成本**，一次性模型下载（123~200MB），之后无任何费用、无网络依赖。
- Gemini TTS：按音频输出 token $20/百万计费。日常"听几句回复"用量极低（免费层足够）；整本书/长播客朗读成本线性累积，批量用 Batch API 五折（$10/百万）。

---

## 五、5 分钟上手（采纳 V-5/V-6/V-9）

```powershell
# ① ★ sherpa-onnx + Matcha 中文（本地首选；国内先设 HF 镜像）
pip install sherpa-onnx soundfile
$env:HF_ENDPOINT = "https://hf-mirror.com"   # 国内 HuggingFace 加速
# 需下载模型 csukuangfj/sherpa-onnx-matcha-icefall-zh-en 的全部文件到同一目录：
#   model-steps-3.onnx（~72MB 声学模型）、vocos-16khz-univ.onnx（~51MB vocoder）
#   lexicon.txt、tokens.txt、espeak-ng-data/
# Python 调用：sherpa_onnx.OfflineTts(OfflineTtsConfig(matcha=OfflineTtsMatchaModelConfig(...)))
# 可封装为本地 OpenAI 兼容服务 POST /v1/audio/speech（body: {"input":"文本"}）供 Hermes Custom endpoint 调用

# ② Piper（离线生态兜底，中文女声 huayan）
pip install piper-tts
$env:HF_ENDPOINT = "https://hf-mirror.com"
python -m piper.download_voices zh_CN-huayan-medium
python -m piper -m zh_CN-huayan-medium -f hello.wav -- "你好，这是本地 Piper 语音。"
# 试听挑音色：https://rhasspy.github.io/piper-samples/

# ③ Edge TTS（零配置但可能随时 403）
pip install edge-tts
edge-tts --voice zh-CN-XiaoxiaoNeural --text "你好，这是 Edge TTS 测试。" --write-media hello.mp3

# ④ KittenTTS（离线，仅英语，25MB）
pip install kittentts
python -c "from kittentts import KittenTTS; import soundfile as sf; m=KittenTTS('KittenML/kitten-tts-nano-0.2'); sf.write('out.wav', m.generate('Hello from Kitten.', voice='expr-voice-2-f'), 24000)"

# ⑤ Gemini TTS（需 GOOGLE_API_KEY，30 音色如 Kore/Puck；AI Studio 可先免费试用）
# 经 Gemini API 调用 gemini-3.1-flash-tts-preview
```

> 提示：sherpa-onnx 首次配置需凑齐多个模型文件（V-9），建议先跑通官方 TTS 示例确认出声，再接入 Hermes。

---

## 六、质量门记录

| 质量门 | 结果 | 说明 |
|---|---|---|
| F 公理推导 | ✅ | 7 条假设剥离（v2 增 A7）+ 5 条公理（可持续性升级为一票否决）+ 决策树 v2 |
| V 门（强制） | ✅ | 4 视角全覆盖，v1 八条 + v2 新增 V-9；V-1/V-8 预言已被事实验证并驱动重构 |
| G2 洞察四元组 | ✅ | 3 条洞察均含陈述/证据（F 编号）/反常识/行动，v2 重写洞察 2/3 |
| 事实可追溯 | ✅ | F-001~F-030，均来自官方文档或 2025-08~2026-09 公开实测；F-025/F-027 为 2026-08 社区实测 |

> **一句话结论（v2）**：中文个人场景改用 **sherpa-onnx + Matcha（matcha-icefall-zh-en）作为本地首选**——免费、离线、RTF 0.04、音质近晓晓、Apache-2.0 商用友好；Edge TTS 因端点 2026-08 起大面积 403 已**降级为临时项、不再作为默认**；Piper 仍是生态最成熟的离线兜底（注意 GPL-3.0）；KittenTTS 仅限英语超低配；Gemini TTS 留给有预算的内容创作。**核心教训：能本地自持的能力，不要押注在随时可能被远程吊销的免费端点上。**

---

## 参考来源

- sherpa-onnx：github.com/k2-fsa/sherpa-onnx（Apache-2.0）；Matcha 中文模型 huggingface.co/csukuangfj/sherpa-onnx-matcha-icefall-zh-en
- openclaw 纯本地语音迁移实录（2026-08-12，含 EdgeTTS 403 实测与 sherpa-onnx 三模型 RTF 对比）；Java 离线 TTS 选型踩坑实录（sherpa-onnx vs Piper/PaddleSpeech，2026-03）
- 开源 TTS 2026 盘点（Kokoro-82M/ChatTTS/GPT-SoVITS/VibeVoice/CosyVoice，2026）；Best Lightweight Local TTS Models 2026（artifilog.com）
- edge-tts（GitHub 第三方库，MIT/LGPL）：支持 140+ 语言 400+ 语音；403 封禁见上述 openclaw 实录
- Google Gemini API 官方模型与定价：ai.google.dev/gemini-api/docs/models、/pricing；Gemini 3.1 Flash TTS 30 语音实测（2026-04）
- KittenTTS：github.com/KittenML/KittenTTS；HuggingFace/ModelScope KittenML/kitten-tts-nano-0.2
- Piper：github.com/OHF-Voice/piper1-gpl（GPL-3.0）；语音库 huggingface.co/rhasspy/piper-voices；试听 rhasspy.github.io/piper-samples
