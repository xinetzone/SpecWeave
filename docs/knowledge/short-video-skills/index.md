---
type: Reference
id: "short-video-skills"
title: "做短视频的 Skill 全景调研：从零到发布的多智能体流水线教程"
category: "short-video-skills"
tags:
  - 短视频
  - agent-skills
  - SKILL.md
  - 视频生成
  - Seedance
  - HyperFrames
  - ffmpeg
  - edge-tts
  - 抖音
  - TikTok
date: "2026-10-20"
last_verified: "2026-10-20"
next_review: "2027-04-20"
status: "stable"
author: "SpecWeave Agent（方法论编排 session sc-20261020-video-skill-wiki）"
summary: "以七概念方法论（R→I→E→V→C，standard）全面调研『做短视频的 skill』：31 条带来源客观事实（F-001~F-031，覆盖 Agent Skills 规范、本机磁盘 Skill 资产、宿主注入 Skill、8 个开源短视频 Skill 仓库、AI 内容标识合规义务），3 条四元组洞察，1 个可复用选型模式「工序五段·双范式选型法」。核心结论：调研样本内多数头部方案是『创意判断交给 Agent、机械执行交给脚本』的工序化 skill 簇（单体重生产线为反例）；成片存在『生成式成片』与『程序排版成片』两大范式，知识/资讯类方案多数默认后者；成熟 skill 与玩具 skill 的分水岭是阻断式质量门。知识包按问题域拆为生态全景、管线选型、实战教程 3 个概念页，附信源台账与对抗审查记录。"
security_level: "public"
knowledge_type: "procedural+conceptual"
validation_status: "verified"
source: "references/source-inventory.md + session sc-20261020-video-skill-wiki 联网核验信源 S16~S20 采集时点 2026-10-20"
---

# 做短视频的 Skill 全景调研：从零到发布的多智能体流水线教程

> 一句话摘要：**"做短视频"不是一个 skill，而是一条由 5~13 个原子 skill 组成的工序化流水线**——选题与脚本等创意见解决策交给 Agent，配音、字幕、渲染、打包等机械执行交给脚本/CLI；成片先分清"生成式成片"（Seedance/可灵/Veo，贵、有汉字崩坏风险）与"程序排版成片"（HTML/ffmpeg/edge-tts，零 Key 本地可跑）两大范式；评估一个短视频 skill 成熟与否，看功能数量不如看有没有阻断式质量门。

- **编排 session**：`sc-20261020-video-skill-wiki`
- **场景与链路**：场景 4 知识沉淀，`R→I→E→V→C（入库）`，depth=standard
- **采集时点**：2026-10-20（本机磁盘 SKILL.md 原文 + 联网核验开源生态，见[信源台账](references/source-inventory.md)）
- **事实编号**：F-001~F-031，来源键 [S01]~[S20]
- **任务背景**：用户以"全面调研做短视频的 skill，生成 okf wiki 教程"发起，产出面向要用 Agent Skill 搭建短视频生产线的读者

---

## 0. 快速导航：按你的问题出发

| 我想…… | 去读哪一篇 |
|---|---|
| 一分钟看懂 Skill 是什么、本机有哪些视频 skill | [01 生态全景与 Agent Skills 规范](concepts/01-landscape-and-spec.md) |
| 拿到"我的内容该走哪条管线"的选型决策树 | [02 生产管线与选型](concepts/02-pipeline-and-selection.md) |
| 直接抄一条能跑的实战教程（口播/AI 艺术片/带货/复盘） | [03 实战教程四线](concepts/03-recipes.md) |
| 核查每条事实出处、URL 与口径分级 | [信源台账](references/source-inventory.md) |
| 了解本知识包经受了哪些攻击、哪些结论被修正 | [V 对抗审查记录](references/adversarial-review.md) |

---

## 1. R 阶段：客观事实清单

> G1 已通过：F 组 31 条全部为可验证客观陈述（文件原文引录、公开仓库/官网原文或一手实测），无"因为/所以/导致"等因果推断词；凡 Skill 自报的效果数据（播放量、替代率）单独标注"自报"口径，不与客观事实混排。

### 1.1 A 组：Agent Skills 规范（P0，F-001 ~ F-005）

| 编号 | 事实 | 来源 |
|---|---|---|
| F-001 | Agent Skills 开放规范（agentskills.io）：一个 skill 是一个目录，最少包含一个 `SKILL.md` 文件，可选 `scripts/`、`references/`、`assets/` 目录 | [S01][S02] |
| F-002 | SKILL.md frontmatter 必填字段：`name`（≤64 字符，仅小写字母/数字/连字符，须与目录同名、不得以连字符开头或结尾）、`description`（≤1024 字符，须同时描述"做什么"与"何时使用"） | [S01][S03] |
| F-003 | 规范采用三级渐进式披露：启动时仅加载各 skill 的 name+description（约 100 token）；任务匹配才加载 SKILL.md 全文（建议 <5000 token）；scripts/references/assets 按需加载；SKILL.md 建议 <500 行 | [S01][S04] |
| F-004 | Claude 平台实现额外约束：name 不能含 XML 标签，不能含保留词 "anthropic"/"claude"；官方公共仓库 anthropics/skills 提供 template-skill 起点 | [S03][S05] |
| F-005 | 规范提供校验工具：`skills-ref validate ./my-skill` 检查 frontmatter 与命名约定 | [S01][S02] |

### 1.2 B 组：本机磁盘 Skill 资产（生成式与素材线，F-006 ~ F-011）

| 编号 | 事实 | 来源 |
|---|---|---|
| F-006 | 本仓库 `.agents/skills/` 中 video 类目 skill 的 frontmatter 均标注 `source: "镜像自 Trae IDE builtin"`，即由 Trae IDE 内置 skill 镜像落盘 | 磁盘抽查：byted-seedance/hyperframes/douyin-interact 等 SKILL.md [S06] |
| F-007 | byted-seedance-video-generate：用火山 Seedance 1.0/1.5 模型生成视频，支持文生视频、首帧/首尾帧引导、参考图(1-4)/参考视频(0-3, 每段2-15s 合计≤15s)/参考音频；输出参数含 aspect ratio（16:9/9:16/4:3/3:4/1:1/2:1/21:9/adaptive）、时长 2-12s、480p/720p/1080p；`generate_audio` 仅 Seedance 1.5 支持；依赖 `ARK_API_KEY`/`MODEL_VIDEO_API_KEY` 等 | `.agents/skills/byted-seedance-video-generate/SKILL.md` [S06] |
| F-008 | byted-seedream-image-generate：火山 Seedream 4.0/4.5/5.0-lite 文生图/图生图，支持批量、自定义尺寸、水印关闭；同走 ARK API Key | `.agents/skills/byted-seedream-image-generate/SKILL.md` [S06] |
| F-009 | byted-mediakit-shared：mediakit-cli 支持音视频处理/剪辑/图片的云+本地双模（14 类能力），npm 全局安装 `@volcengine/mediakit-cli`，云模式必须 `MEDIAKIT_API_KEY`，并要求调用方显式设置 `MEDIAKIT_SURFACE=skill|plugin` | `.agents/skills/byted-mediakit-shared/SKILL.md` [S06] |
| F-010 | classical-festival-video：以古典文献为底本的节日祝福短视频 skill，交付"三张 AI 关键帧 → 10 秒竖版视频 → 随片文案 + 考据"；内置情感分寸矩阵（祝福重量≤关系深度）、画面禁字约束（AI 生成汉字必崩坏，画面禁出现可辨文字）与预览确认门（关键帧先交用户目检再图生视频） | `.agents/skills/classical-festival-video/SKILL.md` [S06] |
| F-011 | douyin-interact-creation：为抖音互动空间生成离线 H5 作品，产物为单 `index.html` 或 zip（总体积 ≤8MB），严禁外链/网络请求/iframe/站外跳转，`index.html` 必须为唯一入口 | `.agents/skills/douyin-interact-creation/SKILL.md` [S06] |

### 1.3 C 组：本机磁盘 Skill 资产（程序排版与分析线，F-012 ~ F-018）

| 编号 | 事实 | 来源 |
|---|---|---|
| F-012 | hyperframes：以 HTML 为视频唯一的 source of truth——composition 是带 `data-*` 时序属性的 HTML + GSAP 时间线 + CSS，框架负责 clip 显隐、媒体播放与时间线同步；支持字幕/口播/音频反应动画/场景转场；流程强制先过 design.md 视觉身份门（HARD-GATE：未取得视觉身份不得写 composition HTML） | `.agents/skills/hyperframes/SKILL.md` [S06] |
| F-013 | hyperframes-cli：`npx hyperframes init/lint/inspect/preview/render/doctor` 六命令开发环；render 支持 `--output/--quality draft|high/--fps 60/--format webm/--docker`（docker 模式字节一致） | `.agents/skills/hyperframes-cli/SKILL.md` [S06] |
| F-014 | hyperframes-media：本地 TTS（Kokoro-82M，54 音色，无 API Key，模型缓存 `~/.cache/hyperframes/`）、Whisper 转转录（词级时间戳；非英语音频禁用 `.en` 模型，否则被翻译而非转录）、u2net 抠背景 | `.agents/skills/hyperframes-media/SKILL.md` [S06] |
| F-015 | asr（本机）：`coli asr` 完全离线本地语音识别，无需 API Key，支持中/英/日/韩/粤语（sensevoice）与英语（whisper）；声明"要合成语音用 /tts、要播客/解说用 /podcast 或 /explainer" | `.agents/skills/asr/SKILL.md` [S06] |
| F-016 | hook-analyzer-skill：从分镜拆解 JSON 中提取视频前三秒分镜数据供 LLM 评分，评分五维权重为视觉冲击力 30%、语言钩子 25%、情绪唤起 15%、信息密度 15%、节奏掌控 15%；上游为 video-breakdown 流程 | `.agents/skills/hook-analyzer-skill/SKILL.md` [S06] |
| F-017 | report-generator-skill：将分镜拆解+钩子分析 JSON 整合为 Markdown 视频分析报告（基本信息/钩子分析/分镜概览/BGM/场景等章节），脚本 `generate_report.py <breakdown.json> [hook_analysis.json]` | `.agents/skills/report-generator-skill/SKILL.md` [S06] |
| F-018 | 宿主运行时另注册一批不入库（未镜像到 `.agents/skills/`）的视频相关 skill：explainer（解说视频）、tts、local-tts（OpenVINO Qwen3-TTS，Intel AIPC 本地）、local-asr、local-realtime-translator、image-gen、local-txt2img、local-img2img 等；其描述仅存在于运行时注册表 | 宿主 available_skills 注册表（会话注入）[S07] |

### 1.4 D 组：开源生态代表仓库（P2-P3，F-019 ~ F-026）

| 编号 | 事实 | License（2026-10-20 时点） | 来源 |
|---|---|---|---|
| F-019 | chemny/short-video-maker：可移植 skill（适配 Codex/Claude Code/OpenClaw），输入文章/话题/想法输出竖版讲解短视频包；分工为"Agent 负责调研/分析/脚本/分镜，Node+Remotion 流程负责校验/TTS 同步/字幕/首帧预览/渲染/封面导出/打包"；自称强项为中文知识讲解/观点拆解/工具方法视频；本地渲染依赖 Node.js、FFmpeg、Remotion | 未核验（未复查 LICENSE 文件） | https://github.com/chemny/short-video-maker [S08] |
| F-020 | Bruce-Agnet/douyin-video-forge：OpenClaw 抖音全链路 skill——浏览器采集热榜/搜索（零 API 成本）→ 低粉高赞筛选 → 竞品分析 → faster-whisper 转写分析 → 双版本脚本（可灵 + Seedance 格式）→ 可灵 3.0 API 文生/图生视频（首末帧衔接保连贯）→ FFmpeg 多段拼接 + BGM → MP4 1080x1920 竖屏；支持 Cron 每日自动化 | 未核验 | https://github.com/Bruce-Agnet/douyin-video-forge [S09] |
| F-021 | askxiaozhang/hermes-skills 的 github-trending-douyin：每日抓 GitHub Trending → LLM 写钩子口播稿 → edge-tts 合成 → Pillow 画帧 + ffmpeg 合成 9:16 竖版 → 出抖音标题/描述/话题，宣称 0 人工成片；内建 `verify_emoji.py` 字形/emoji 检测门（不过门不合成）；规模数据（"30 天 10 万+播放、+388 粉"）为作者自报口径 | 未核验 | https://github.com/askxiaozhang/hermes-skills [S10] |
| F-022 | tiktok-video-skill：一行 brief 生成 TikTok/抖音/Shorts/Reels 成片（1080x1920 MP4）——脚本、免费素材（Pexels/Pixabay，有 Key 时启用；无 Key 零 API 可跑）、中英 TTS、词级卡拉OK字幕、BGM、ffmpeg 合成；明文规则"VERIFY FACTS FIRST"：写分镜前先核实每个具体论断，无可核实素材的新闻/价格/排名/节日时效性表述一律替换或删除，信源 URL 记入 storyboard `sources` 供审计 | MIT（V 阶段实测仓库页，⚠️ 风险标注见台账 S11） | https://github.com/Trudiemisanthropic314/tiktok-video-skill/blob/main/SKILL.md [S11] |
| F-023 | Frank-oll/ai-video-creator：生活妙招选题 → 端到端可发布 9:16 AI 短视频——Doubao-Seedream-5.0-lite 生成一致性分镜静图 → Doubao-Seedance-1.5-pro 并发 I2V（带原生 AI 配音）→ ffmpeg 拼接；单一火山 ARK 网关单 Key，提示词中文优先；默认 3 镜 × 5 秒 = 15 秒，同时交分镜 xlsx/口播稿/分段视频供剪映精修 | 未核验 | https://github.com/Frank-oll/ai-video-creator [S12] |
| F-024 | xianyu110/ecommerce-video-skills：13 个可单独安装的电商短视频 skill（hook-3s-script 九型钩子六到十版、viral-remake 爆款五拍拆解、selling-point-storyboard 分镜表、multi-model-shot-prompts 多模型中性提示词、edge-tts 配音、ASS 字幕花字、ffmpeg-auto-assemble 成片、platform-spec-export 六平台规格、multilingual-dubbing、cover-title-AB、live-stream-clips 等）；与同名仓库的区分口径：本仓库**本地 Python+ffmpeg 渲染、免 Key、不依赖云端视频服务**，图生视频为可选项、每镜头带本地 Ken Burns 兜底；宣传内置广告法绝对化用语检查与"只写测过的数据"；响度以两遍标准化目标 ≈-14 LUFS；并声明"不编造任何模型价格或参数" | 未核验 | https://github.com/xianyu110/ecommerce-video-skills [S13] |
| F-025 | xuliang2024/video_skills：Cursor/Claude Code 双端 skill 合集——tumblr-video（TTS+跑酷背景逐行揭示）、knowledge-video（调研→撰稿→PPT→TTS→逐段合成）、svg-video（Lottie 动画素材检索 + HTML 渲染）、coze-upload、xskill-api；输出 1080p 或 1440×2560 竖版 MP4/WebM，面向抖音/快手/小红书/TikTok/Shorts | 未核验 | https://github.com/xuliang2024/video_skills [S14] |
| F-026 | maxazure/video-editing-skill：面向口播/教程/访谈/播客切片/录屏的单体剪辑生产线——项目启动与能力预检(runtime_preflight) → telecine/VFR 时基归一 → 黑场裁切 → 多机位同步 → 转写清稿 → 分镜 → 分镜静帧预演(animatic) → 生成素材预检与角色绑定(@ImageN/@VideoN/@AudioN) → BGM/SFX cue 混音 → J-cut/speed ramp/freeze-punch → 单次编码渲染 → 字幕字形 cmap QA/像素复核/与语音对齐 → 逐短语响度(LUFS/dBTP) → 闪屏/单帧瞬态筛查 → 唇形复核 → 多平台导出 → 标题文案与续跑交接；全程以"审批绑定文件 SHA-256"的收据机制防漂移；作者自报"对口播短视频至少替代 80% 常规剪辑工作"（自报口径） | 未核验 | https://github.com/maxazure/video-editing-skill [S15] |

### 1.5 E 组：知识库落点、既有覆盖与合规核验（F-027 ~ F-031）

| 编号 | 事实 | 来源 |
|---|---|---|
| F-027 | 根 `docs/` 为唯一文档中心（OKF v0.2，Sphinx 构建），承载 Wiki 教程与知识包；`.agents/docs/` 为已废止路径，禁止写入 | AGENTS.md（磁盘原文，2026-10-20 回读）[S16] |
| F-028 | docs/knowledge 条目 frontmatter 必填 title/category/tags/date/status/author/summary，新入库条目必填 `last_verified`，缺失将导致 generate_index.py 告警降级 | docs/knowledge/template.md [S17] |
| F-029 | docs/knowledge 知识条目新增后运行 `python scripts/generate_index.py` 重新生成入口页、分类索引与标签分片（README"入库流程"步骤） | docs/knowledge/README.md [S17] |
| F-030 | 截至 2026-10-20，docs/knowledge 与 projects/awesome-okf-xs/doc/bundles 中无"短视频制作 skill"主题知识包；bundles 中视频相关仅收录工具产品（如 VidBee 视频下载转录）与可视化教程素材，未覆盖"用 Agent Skill 产短视频"的方法论 | docs/knowledge 目录清单 + bundles grep 检索 [S18] |
| F-031 | 《人工智能生成合成内容标识办法》（国信办通字〔2025〕2号）2025-03-07 由网信办、工信部、公安部、国家广电总局印发，2025-09-01 施行：AI 生成合成内容须携带显式标识（视频场景：起始画面与播放周边的显著提示标识）与隐式标识（文件元数据中嵌入生成合成属性信息）；用户发布生成合成内容应主动声明并使用平台标识功能；任何组织和个人不得恶意删除、篡改、伪造、隐匿标识；配套强制性国标 GB 45438-2025 同步实施 | https://www.cac.gov.cn/2025-03/14/c_1743654684782215.htm [S20]（V 阶段追加核验） |

---

## 2. I 阶段：核心洞察（四元组）

> G2 已通过：3 条洞察均含陈述/证据（引用 F 编号）/反常识/行动四元组，维度独立不重叠；V 阶段已做幸存者偏差与样本口径降级（见[对抗审查记录](references/adversarial-review.md)）。

### 洞察 1：调研样本内，生产级多数方案呈"工序化 skill 簇"形态

| 元素 | 内容 |
|---|---|
| 陈述 | 调研样本内（本机磁盘 skill + 开源 8 仓库，时点 2026-10-20）、面向内容生产的头部方案**多数**呈"工序化簇"形态：按五段工序拆分原子 skill/脚本段协作，Agent 只保留创意判断（选题/脚本/分镜/审片），配音、字幕、渲染、QA、打包交给脚本机械执行。**样本口径**：8 个开源仓库 + 本机资产，非全生态统计。**反例**：maxazure/video-editing-skill 以 60+ 步骤单体重生产线组织 [F-026] |
| 证据 | F-001/F-003（渐进式披露架构利于按工序拆分）；F-024（13 个可单独安装的 skill 簇）；F-025（多 skill 合集）；F-012~F-014（hyperframes 三件套分工）；F-019（"Agent 负责创意、Remotion 流程负责机械执行"双轨）；反例 F-026 单体 |
| 反常识 | 挑战默认假设"找一个最强短视频工具/skill 就行"——但即便 maxazure 单体成功打样，其 60+ 步骤内部仍按工序分层、以审批收据（SHA-256 绑定）做交接，与簇形态的工程实质（工序可替换、结构化契约交接）一致；差别在打包粒度，不在"是否工序化" |
| 行动 | 搭流水线时按工序选型组装（见 02 概念页决策树），簇/单体皆可；无论形态，自研时以 storyboard.json 这类结构化中间产物作为各环节交换契约 |

### 洞察 2：成片分两大范式；知识/资讯类方案多数默认"程序排版"，但量产与范式不硬绑定

| 元素 | 内容 |
|---|---|
| 陈述 | 短视频成片存在两条成本结构截然不同的范式路线：A. 生成式成片（T2V/I2V：Seedance/可灵/Veo，秒级计费、需 API Key、有汉字崩坏与商品/角色一致性风险）；B. 程序排版成片（HTML/GSAP、Remotion、Pillow 帧绘制 + ffmpeg 合成、edge-tts/Kokoro 配音，零 Key 本地可跑）。调研样本内，知识/解说/资讯类头部方案**多数**默认走 B [F-021、F-024、F-025]；**边界反例**：douyin-video-forge 面向 Cron 每日量产却走 A（可灵 3.0 + Seedance 双版脚本）[F-020] |
| 证据 | F-021（Pillow 直绘 GitHub 风格卡帧成片，不用视频模型）；F-024（"图生视频只是可选项，每镜头带本地 Ken Burns 兜底"）；F-025（知识视频走 PPT→TTS→逐段合成）；F-012/F-013（HTML 即视频）；对照 F-007/F-023（生成式路线均强调参考图锁定一致性）；反例 F-020 |
| 反常识 | 双向违背直觉：①"做短视频=必须调视频生成模型"不成立——多数跑量方案不消耗任何视频生成额度；②反过来，"量产内容必然走省钱范式"也不成立——douyin-video-forge 证明量产也可走 A，只是要自负逐镜一致性锁定与生成额度成本 |
| 行动 | 默认按 B 范式搭建量产管线（低试错成本），A 范式用于关键镜头、品牌片、节日情感片等"每秒都值钱"的场景；走 A 时生成画面中禁止出现可辨文字（F-010），并先过成本估算三步法（见 02 §3） |

### 洞察 3：skill 成熟度的分水岭是"阻断式质量门"，不是功能数量

| 元素 | 内容 |
|---|---|
| 陈述 | 成熟短视频 skill 的共同特征是把"验证"固化成阻断式硬门禁——用户目检预览门、字形/emoji 渲染检测、字幕像素级复核、响度 LUFS 校验、广告法用语检查、平台安全区检查；不达标即阻断交付；toy 方案与生产方案的分界在此而不在功能多少 |
| 证据 | F-010（预览确认门：关键帧未过目检不消耗视频生成额度）；F-021（verify_emoji.py 不过门不合成）；F-024（广告法自检 + -14 LUFS 两遍标准化 + 安全区预览）；F-026（字幕 cmap 逐字符 QA、像素复核、闪屏筛查、审批绑定 SHA-256）；F-022（事实先行 VERIFY FACTS FIRST：未核实论断不进脚本） |
| 反常识 | 挑战假设"功能多=好"——maxazure 单体 60+ 步骤的价值核心是那一组 QA 门与收据机制；反之一个只有"TTS+合图"无任何验收门的 skill 在生产中不可托付 |
| 行动 | 选型时用"三问门禁"检查：①有没有交付前的阻断检查点？②失败时 fail-loud 还是无声降级？③上传/发布权限是否绑定具体产物？自研管线至少内置四道门：分镜观众/用户确认、字幕字形检测、平台合规与响度校验、**AI 内容标识合规门（2025-09-01 起法定义务，F-031）** |

---

## 3. E 阶段沉淀：可复用选型模式

**模式名：「工序五段·双范式选型法」**（完整形态见 [02 生产管线与选型](concepts/02-pipeline-and-selection.md)，此处摘要）

- **触发场景**：任何"我要让 Agent 帮我做短视频/给我推荐短视频 skill"类任务。
- **核心步骤**：①按五段工序盘点需求（策划→素材→音频→合成→发布质检）；②判定内容走 A 生成式还是 B 程序排版范式；③每段工序映射 1~2 个候选 skill（优先带质量门者）；④以 storyboard.json 为中间契约串接；⑤交付前过四道门检（其中合规门为 2025-09-01 起法定义务 [F-031]）。
- **反模式**：①找"单点全能 skill"一步到位；②全管线默认接视频生成模型烧钱；③以模型自评代替用户目检。
- **检验标准**：给出的方案中每个工序的 skill 均有明确输入/输出/阻断门；成片在交付前多数场景可 0 成本本地 dry-run 预览。
- **迁移说明**：同法可推演迁移到播客/图文排版流水线（形态一致性经对抗审查确认，样本为设计推演、未见落地实证，定级 L1）。

---

## 4. V 与 C 记录

- **V 对抗审查**：四视角（魔鬼代言人/新人/老板/未来）共 21 条实质意见——采纳修正 15 项（含 token 崩坏修复、幸存者偏差降级与样本口径声明、反例边界回填、因果词清除、自报数据降权、空信源虚胖修复、术语速查与首释、合规门与 S20 新增、时点快照声明、License 列标注等），部分采纳 3 条、维持原判 3 条，完整记录见 [adversarial-review.md](references/adversarial-review.md)。
- **C 原子提交**：知识包入库 + `generate_index.py` 索引再生 + 导航更新，按原子提交规范执行（单一职责：docs(knowledge): 新增短视频 skill 全景调研知识包）。

### 维护者复核指引（下次复核优先级）

下次复核时点 `next_review: 2027-04-20`（发布后 6 个月）。按维护成本排序：

1. **模型敏感事实（优先，厂商迭代即过期）**：F-007（Seedance 1.0/1.5 参数与 `generate_audio` 支持）、F-008（Seedream 版本线）、F-020（可灵 3.0、faster-whisper）、F-023（Doubao-Seedream-5.0-lite / Doubao-Seedance-1.5-pro 型号与原生 AI 配音能力）。
2. **平台/渠道敏感**：F-024 的平台规格与安全区口径、F-011 抖音互动空间限制、F-021 hermes-skills 自报数据状态。
3. **合规敏感**：F-031 依据的标识办法实施情况与 GB 45438-2025 具体参数（视频起始提示的高度/时长），以及平台侧标识功能的实际入口。
4. **仓库存活**：S08~S15 的 8 个开源仓库 URL 与 License（F-022 的 MIT 外其余均标注"未核验"）；S11 仓库的营销文案风险状态。

模型价格策略不变：本包不收录具体定价数字，引用以厂商当期官网为准。

## 5. 参考

- [01 生态全景与 Agent Skills 规范](concepts/01-landscape-and-spec.md)
- [02 生产管线与选型](concepts/02-pipeline-and-selection.md)
- [03 实战教程四线](concepts/03-recipes.md)
- [信源台账](references/source-inventory.md)
- [对抗审查记录](references/adversarial-review.md)
- [docs/knowledge 入库流程](../README.md)
