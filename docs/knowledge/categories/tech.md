---
type: Reference
title: "分类索引：tech"
---

# 分类索引：tech

- [返回分类总索引](../category-index.md)
- [返回知识库首页](../README.md)
- [按标签检索](../tags/README.md)

> 本分片收录 **1** 个子分类，共 **86** 条条目。

## tech

| 标题 | 摘要 | 日期 | 标签 |
|------|------|------|------|
| [caffe-ffi Conv v4 OpenMP 并行优化技术总结](../tech/caffe-ffi-conv-v4-optimization-summary.md) | caffe-ffi Conv 层 OpenMP 并行优化（v4）的技术总结，覆盖并行策略、环境变量配置、抖动诊断与生产部署指南，供团队内部分享。 |  | - |
| [GLM 大模型调用可复用示例（本地加载 + API 调用）](../tech/glm-model-call-example.md) | 从 chaos/flexloop/models 沉淀的 GLM 大模型调用可复用示例：本地模型加载（transformers + torch）与 Z.AI 云端 API 调用（zai-sdk）两种方式，含脱敏代码与环境变量配置说明。 | 2026-08-07 | glm、llm、transformers、zai、huggingface、python |
| [ListenHub API 规范——Authentication（认证与基础 URL）](../tech/listenhub-api-authentication.md) | 沉淀 ListenHub 开放平台的统一认证规范：环境变量 LISTENHUB_API_KEY、基础 URL、必备请求头（Authorization/Content-Type/X-Source）、curl 模板与安全注意事项。所有 Key 均以占位符表示。 | 2026-08-07 | listenhub、api、authentication、security、marswave |
| [ListenHub API 规范——Image Generation（AI 图片生成）](../tech/listenhub-api-image.md) | 沉淀 ListenHub AI 图片生成接口规范：POST /images/generation，记录请求参数（provider/prompt/model/imageConfig/referenceImages）、宽高比表、参考图 URL/base64 两种格式、同步 base64 返回与调用要点。 | 2026-08-07 | listenhub、api、image-gen、image-generation、gemini、marswave |
| [ListenHub API 规范——Podcast（播客节目生成）](../tech/listenhub-api-podcast.md) | 沉淀 ListenHub 播客生成接口规范：POST /podcast/episodes 创建节目、GET /podcast/episodes/{episodeId} 查询状态结果，记录接口用途、关键参数（speakers/query/sources/language/mode）与调用要点（异步轮询、两段式生成）。 | 2026-08-07 | listenhub、api、podcast、marswave |
| [ListenHub API 规范——Speakers（主播列表）](../tech/listenhub-api-speakers.md) | 沉淀 ListenHub 主播列表接口规范：GET /speakers/list，记录查询参数（language/status）、响应字段（name/speakerId/demoAudioUrl/gender/language）与调用要点；含内置默认主播表。 | 2026-08-07 | listenhub、api、speakers、marswave |
| [ListenHub API 规范——Storybook（解说视频/故事本）](../tech/listenhub-api-storybook.md) | 沉淀 ListenHub 解说视频（Storybook）接口规范：POST /v1/storybook/episodes 创建、GET 查询状态结果、POST /v1/storybook/episodes/{episodeId}/video 触发视频生成，记录参数（sources/speakers/language/mode）、mode 取值与调用要点。 | 2026-08-07 | listenhub、api、storybook、explainer、video、marswave |
| [ListenHub API 规范——TTS / Speech（文本转语音）](../tech/listenhub-api-tts.md) | 沉淀 ListenHub 文本转语音（TTS）两套接口规范：/v1/tts（单声、低延迟、同步 MP3 流）与 /v1/speech（多角色脚本转音频），记录接口用途、关键参数与调用要点。 | 2026-08-07 | listenhub、api、tts、speech、marswave |
| [ListenHub 技能集总览——asr/tts/podcast/image-gen/content-parser/explainer 设计模式与共享规范](../tech/listenhub-skill-set-overview.md) | 沉淀 flexloop chaos 技能库中 6 个内容生成类 AI 技能（asr/tts/podcast/image-gen/content-parser/explainer）的触发词、能力定位、API 依赖与共享通用模式（异步轮询/错误处理/@file/交互式参数收集），并说明已废弃的 listenhub 单体技能状态。 | 2026-08-07 | listenhub、skill、ai-skill、api-integration、design-pattern、marswave |
| [DaoMind 项目概览（道家哲学 TypeScript 框架）](../tech/p1-09-daomind-project-overview.md) | DaoMind 是基于道家哲学宇宙论的现代化 TypeScript 框架，采用 pnpm monorepo 架构，核心包覆盖无/有/行动/应用/时序/道宇宙六层抽象，含函数式错误处理与 DaoUniverse 桥接体系。 |  | - |
| [道衍 DaoYan 项目概览（帛书道德经 AI 对话系统）](../tech/p1-10-daoyan-project-overview.md) | 道衍是以马王堆帛书版《道德经》为权威底本的 AI 智慧对话系统，融合道家无为、佛家直心与 ψ=ψ(ψ) 万物理论，支持 5 大 AI 模型切换与 Agent API/MCP 开放接入。 |  | - |
| [DaoMind 2.0 哲学架构：无名/有名与 TypeScript 类型系统映射](../tech/p1-13-daomind-philosophy-architecture.md) | DaoMind 2.0 将帛书《道德经》"无名/有名"哲学概念与 TypeScript 类型/值空间进行映射，建立了独特的哲学驱动架构设计模式 |  | - |
| [MCP 技能开发与 REST API 集成规范——以道衍为例](../tech/p1-17-daoyan-mcp-skill-spec.md) | 以道衍（DaoYan）MCP Server 为例，说明 AI IDE 技能（Skill）定义、MCP 工具配置、REST API 调用与回答规范的完整模式 |  | - |
| [Reasonix 架构：Python AI Agent 分层设计模式](../tech/p1-18-reasonix-architecture.md) | DeepSeek-Reasonix 是一个配置驱动、多模型协作的 AI Coding Agent，采用清晰的分层架构（组装器+Provider+Agent+Controller），是 Python AI Agent 项目的优秀架构参考 |  | - |
| [TVM Relax 前端 MLP 实验记录](../tech/p2-13-tvm-relax-mlp-experiment.md) | TVM Relax 前端 nn.Module API 的最小 MLP 实验，展示从模型定义到 export 导出链路的验证样例，可作为 Relax 前端学习与回归参考。 |  | - |
| [Python 3.14 Free-Threading 适用场景分析](../tech/python-314-free-threading-scenario-analysis.md) |  | 2026-08-19 | python、free-threading、no-gil、concurrency、performance |
| [onnx-pytorch v1.1.0 发布说明](../tech/release-onnx-pytorch-v1-1.md) |  | 2026-08-15 | - |
| [onnx-quantized v2.0.0 发布说明](../tech/release-onnx-quantized-v2.md) |  | 2026-08-14 | - |
| [文章转动漫视频/短剧：AI 视频化工具链 Wiki 教程](../tech/article-to-video-wiki/index.md) | 把一篇文章/小说/公众号故事做成动漫视频（漫剧/动画解说）或 AI 真人短剧的完整工具链教程：八段制片管线、五层工具选型图谱（2026-10 时点）、TRAE 本机 Skill 落地工作流、三种成品配方、成本账与合规避坑。 | 2026-10-18 | - |
| [01 · 八段制片管线全景与术语词典](../tech/article-to-video-wiki/concepts/01-pipeline.md) |  | 2026-10-18 | - |
| [02 · 五层工具选型图谱（2026-10 时点）](../tech/article-to-video-wiki/concepts/02-tool-map.md) |  | 2026-10-18 | - |
| [03 · TRAE 落地工作流：从零代码到 Skill 编排](../tech/article-to-video-wiki/concepts/03-trae-workflow.md) |  | 2026-10-18 | - |
| [04 · 三种配方、成本账与避坑清单](../tech/article-to-video-wiki/concepts/04-recipes-and-pitfalls.md) |  | 2026-10-18 | - |
| [V 对抗审查记录：文章转动漫/短剧 Wiki 教程](../tech/article-to-video-wiki/references/adversarial-review.md) |  | 2026-10-18 | - |
| [信源台账：文章转动漫/短剧工具链（S01~S127 + L1~L6）](../tech/article-to-video-wiki/references/source-inventory.md) |  | 2026-10-18 | - |
| [Fedora CoreOS 系统性知识分析：不可变容器 OS 的机制、模式与边界](../tech/fedora-coreos/index.md) | 以七概念方法论（R→I→E→V，deep）对 Fedora CoreOS 做系统理解：77 条一手事实、4 条四元组洞察、2 个可迁移模式（镜像基座契约 / 图控灰度更新）、4 视角对抗审查与采纳修正、与本仓 Podman/WSL 栈的关系界定。 | 2026-09-15 | - |
| [Medium 平台知识包：从"思想之地"到注意力订阅平台](../tech/medium-wiki/index.md) | Medium 平台知识束：总览/时间线/产品/商业模式/技术/生态/竞争/转型，冲突口径并列，13 信源可溯源。 | 2026-10-20 | medium、publishing-platform、business-model、partner-program、substack、creator-economy、turnaround、product-research |
| [Medium 知识包变更日志](../tech/medium-wiki/log.md) | Medium 知识包生成过程记录：R→I→E→V→C 各阶段事件。 | 2026-10-20 | medium、changelog |
| [Medium 平台总览：从"思想之地"到注意力订阅平台](../tech/medium-wiki/concepts/00-overview.md) | Medium 是 2012 年由 Evan Williams 创立的美国在线出版平台，以阅读时间而非流量为核心计量单位，靠会员订阅与 Partner Program 而非广告变现。 | 2026-10-20 | medium、publishing-platform、social-journalism、evan-williams、content-platform |
| [Medium 历史时间线：2012–2026](../tech/medium-wiki/concepts/01-timeline.md) | Medium 十五年历程分三阶段：设计时代以产品美学赢得长篇内容地位，商业模式时代靠会员订阅确立收入但伤害作者信任，转型时代经资本重组与内容治理于 2024 年首次月度盈利。 | 2026-10-20 | medium、timeline、history、business-model、turnaround |
| [Medium 产品形态与设计理念：为"深读"而生的交互系统](../tech/medium-wiki/concepts/02-product-design.md) | Medium 的产品哲学是把写作与阅读体验打磨到极致，用 Claps/Tags/高亮/阅读指标等机制把'深度'而非'流量'变成可观察、可分配的信号。 | 2026-10-20 | medium、product-design、claps、tags、publications、reading-metrics、ui-ux |
| [Medium 商业模式：会员订阅 + Partner Program 的分成引擎](../tech/medium-wiki/concepts/03-business-model.md) | Medium 以 $5/月或 $50/年会员订阅为收入核心，Partner Program 按会员阅读时长把订阅费分配给作者；历经原生广告→会员+分成→内容治理的三阶段商业化演进。 | 2026-10-20 | medium、business-model、membership、partner-program、monetization、subscription |
| [Medium 技术架构：从 Node.js 单体到 AWS 全栈](../tech/medium-wiki/concepts/04-architecture.md) | Medium 技术栈以 Node.js 为主应用、AWS 为基础设施、Go 处理图片服务；个性化推荐系统 Elevators 于 2020 年公开。技术细节公开资料有限。 | 2026-10-20 | medium、architecture、nodejs、aws、golang、recommendation、tech-stack |
| [Medium 内容生态与治理：作者关系、治理实验与全球访问限制](../tech/medium-wiki/concepts/05-ecosystem-governance.md) | Medium 的内容生态以质量为旗号却长期受作者信任危机困扰；公司治理经历合弄制实验与工会运动；内容审核在克制干预与平台责任间摇摆；并曾在多国遭遇访问限制。 | 2026-10-20 | medium、ecosystem、governance、moderation、holacracy、authors |
| [Medium 竞争格局：与 Substack、Ghost 的范式分岔](../tech/medium-wiki/concepts/06-competition.md) | Medium 与 Substack 代表'平台拥有受众'与'作者拥有受众'两种范式；Substack 以 10% 抽成与可导出邮件列表验证了去平台化模式，Medium 以算法分发换取低门槛发现。 | 2026-10-20 | medium、substack、ghost、competition、creator-economy、newsletter |
| [2022–2025 转型复盘：Stubblebine 的扭亏之战](../tech/medium-wiki/concepts/07-turnaround.md) | 2022 年 Medium 月亏约 250-260 万美元，Stubblebine 通过资本重组（recap）、裁员 250 人到 77 人、内容质量治理三线并进，于 2024-08 首次月度盈利，成为内容平台扭亏的罕见案例。 | 2026-10-20 | medium、turnaround、stubblebine、recap、content-governance、profitability |
| [Medium 知识包 concepts 索引](../tech/medium-wiki/concepts/index.md) | Medium 知识包 concepts 子索引。 | 2026-10-20 | medium、index |
| [作者收入模式演算：Medium vs Substack（示例）](../tech/medium-wiki/examples/01-author-earnings-model.md) | 同一作者的两种收入路径演算：Medium 按会员阅读时长分成（收入不确定、随算法波动）；Substack 按订阅人数线性分成（90% 归作者），并讨论各模式对头部/长尾作者的含义。 | 2026-10-20 | medium、substack、earnings-model、worked-example、creator-economy |
| [Medium 知识包 examples 索引](../tech/medium-wiki/examples/index.md) | Medium 知识包 examples 子索引。 | 2026-10-20 | medium、index |
| [V 对抗审查记录：Medium 知识包](../tech/medium-wiki/references/adversarial-review.md) | 四视角对抗审查共提出 9 条意见，采纳 5 条实质修正：补充口径并列、修正示例表述、强化数据标注、收敛推断、明确限制。 | 2026-10-20 | medium、adversarial-review、quality-gate、verification |
| [Medium 知识包 references 索引](../tech/medium-wiki/references/index.md) | Medium 知识包 references 子索引。 | 2026-10-20 | medium、index |
| [Medium 知识包信源台账（S01–S13）](../tech/medium-wiki/references/source-inventory.md) | 13 个信源家族覆盖维基百科镜像、官方帮助中心、行业深度复盘、转型复盘转述与竞品分析；所有数字标注机构+时间+口径。 | 2026-10-20 | medium、sources、provenance、evidence |
| [openEuler 与 openKylin 系统性对比：后端根社区与桌面根社区的分工、治理、生命周期与选型](../tech/openeuler-vs-openkylin/index.md) | 以七概念方法论（R→I→E→V→C，standard）系统对比 openEuler 与 openKylin：新采集 openEuler 侧 35 条带来源客观事实（O-001~O-035，2010 EulerOS 起源至 2026-09 装机 2000 万口径与 24.03 LTS SP4），以 12 条锚点（K-001~K-012）引用本地 openKylin 知识包 62 条事实，形成 5 条四元组洞察与 1 个 L1-draft 可迁移模式（场景区间选型法）。核心结论：两者不是直接竞品，而是同一开放原子基金会体系内后端基础设施根社区与桌面/AI 终端根社区的产业分工，麒麟软件同时为两边参与者且其服务器/桌面商业版分别以两者为上游。知识包按问题域拆为画像、定位场景、治理生态、版本生命周期、技术栈、选型指南 6 个概念页，附信源台账与对抗审查记录。 | 2026-09-30 | - |
| [openKylin 官方文档平台学习教程（OKF Wiki）：237 篇社区文档的逆向导读](../tech/openkylin-docs-wiki/index.md) | 以七概念方法论（R→I→E→V→C，standard）系统学习 openKylin 官方文档平台 docs.openkylin.top：递归解析 Gitee 源仓库 3181 条目/237 篇中文文档、精读 35 篇代表性文档、提取 44 条客观事实，形成 4 条四元组洞察与 1 个 L1 可迁移模式（逆序文档学习法）。教程按学习者问题域重组为平台地图、版本生命周期、安装路径、桌面使用、AI 三层体系、开发者基础设施、社区治理 7 个概念页，附信源台账与完整文档分类地图。 | 2026-09-29 | - |
| [openKylin 3.0 Kylin AI SDK 文字识别（OCR）能力落机 POC 实测（Desktop WSL）](../tech/openkylin-docs-wiki/references/ai-sdk-ocr-poc.md) |  | 2026-10-08 | - |
| [openKylin 3 AI 子系统源码架构剖析：两代 SDK、运行时 D-Bus 与引擎插件层（huanghe 本机核验）](../tech/openkylin-docs-wiki/references/ai-subsystem-source-architecture.md) | 在 openKylin-3.0-desktop WSL（huanghe）上以 dpkg/apt 只读核验结合 Gitee 上游源码（kylin-ai-subsystem、kylin-ai-engine、kysdk-ai-common、libkysdk-genai-*、kylin-ondevice-nlp-engine、libkylin-ai-base），还原 openKylin 3 AI 子系统的真实分层：Gen1 libkylin-ai-base2 与 Gen2 kysdk 1.1 两套 SDK 同机并存、SDK 全部是 D-Bus/IPC 代理不含推理、Gen2 走 per-uid 私有 unix socket 接 kylin-ai-runtime、引擎以 C++ AbstractAiEngine 插件方式接入、本地文本生成链路终点是预装的 kytensor(Triton)+llama.cpp，并给出 huanghe 官方源组件可用性矩阵与源码分支错位的证据边界。 | 2026-10-08 | - |
| [openKylin 3 显示服务器双栈：kylin-wayland-compositor 与 KWin/Xorg 源码剖析（huanghe 本机核验）](../tech/openkylin-docs-wiki/references/kylin-wayland-compositor-architecture.md) | 以 openKylin-3.0-desktop WSL（huanghe）本机包/会话/设备只读核验结合 Gitee kylin-wayland-compositor（openkylin/huanghe 分支）源码审阅，还原 openKylin 3 的显示服务器双栈：物理态默认 Wayland 合成器 kywc（基于 wlroots 0.17 的 C 项目，drm/fbdev/嵌套三后端、兼容 KDE Plasma 与 UKUI 私有协议、用户态 systemd 拉起 ukui-session），与 xrdp/Xorg 路径使用的 KWin 5.24 X11 栈并存；并以 WSL 无 /dev/dri、无 /dev/fb*、仅有 /dev/dxg + WSLg weston(rdp-backend) 的设备事实，界定 WSL 用户实际处于 X11 孤岛，kywc 嵌套 WSLg 仅源码可行而未实测。 | 2026-10-08 | - |
| [openKylin 3.0 架构适配评估草案：纸面预评估、风险登记与 POC 验证方案](../tech/openkylin-docs-wiki/references/openkylin-v3-adaptation-assessment.md) | 基于同知识包两份已验证报告（62 条项目事实、44 条文档平台事实与 3.0 WSL 本机实测），对 openKylin 3.0（Huanghe）做适配前纸面预评估：覆盖工具链跨代、不可变系统、多架构、图形栈、后量子安全、智能体底座、工程供应链 7 个维度，登记 12 项风险，给出软件/硬件/AI 智能体三类适配主体的工作路径、版本策略矩阵与 P0–P5 六阶段 POC 方案。本文为草案 v0.1，所有结论未经实机 POC 验证。 | 2026-09-29 | - |
| [openKylin 全面调研：从桌面根社区到 Agent OS 的事实、洞察与模式](../tech/openkylin-docs-wiki/references/project-overview.md) | 以七概念方法论（R→I→E→V，standard）全面调研 openKylin：62 条多源事实（2022 社区成立至 2026-09 openKylin 3.0）、4 条四元组洞察、2 个可迁移模式（根社区—商业发行版双轮 / OS 智能体原生化四级演进）、4 视角对抗审查与采纳修正、与优麒麟/银河麒麟/统信 UOS/openEuler 的版图界定。 | 2026-09-29 | - |
| [openKylin 3.0 Desktop WSL 桌面启动与日常使用教程（Windows 10/11 实测）](../tech/openkylin-docs-wiki/references/wsl-desktop-startup-tutorial.md) |  | 2026-10-08 | - |
| [openKylin 3.0 双 WSL 镜像对照与选型参考（Desktop WSL 已于 2026-10-08 落机实测）](../tech/openkylin-docs-wiki/references/wsl-dual-image-selection.md) |  | 2026-09-30 | - |
| [openKylin 3.0 WSL 安装与稀疏 VHD 实操指南（Windows 10 实测）](../tech/openkylin-docs-wiki/references/wsl-install-sparse-vhd-guide.md) |  | 2026-09-29 | - |
| [公网服务器安全加固教程](../tech/public-server-hardening/index.md) | 以七概念方法论（F→V→I 风险证伪 + R→I→E→V 知识沉淀，standard）分析'IP 地址暴露是否有风险'并沉淀为公网服务器加固教程：提取 30 条客观事实、形成 4 条四元组洞察与 1 个 L1 可迁移模式（假设暴露·分层加固法）。教程按运维问题域重组为 8 个概念页：IP 暴露风险本质、暴露面盘点与防火墙、SSH 与暴力破解防御、补丁与源站隐藏、Web 服务加固、最小权限与隔离、监控备份与韧性、非技术人员执行摘要，附信源台账与对抗审查记录。 | 2026-09-30 | server-security、hardening、ssh、firewall、ddos、cdn、backup、ip-exposure |
| [AI Harness 与 Agent Python 包全景调研：从 AutoGPT 退潮到 harness 品类成型](../tech/python-agent-harness/index.md) | 以七概念方法论（R→I→E→V→C，standard）调研 2025-2026 年 AI harness/agent 方向的主流 Python 包：采集 45 条带来源客观事实，覆盖 15+ 个框架/SDK 与编码 agent 赛道，形成 4 条四元组洞察与 1 个可迁移模式（最小充分脚手架选型法，3 个外部独立案例支撑，入库定级 L1-draft）。知识包按问题域拆为生态格局、harness 解剖、框架目录、编码 agent 赛道、选型模式 5 个概念页，附信源台账与对抗审查记录。 | 2026-09-30 | - |
| [Python 与 Rust 技术对比分析报告 Wiki · 总览](../tech/python-rust-comparison/00-overview.md) | 基于最新标准（Python 3.14 / Rust 1.97.1）从零创作的 Python 与 Rust 技术对比分析 Wiki，覆盖语言机制、性能、工程化、生态、应用场景、决策矩阵与迁移路径。 | 2026-08-07 | python、rust、技术选型、性能、混合架构 |
| [Python 与 Rust 技术对比 · 语言与运行时基础](../tech/python-rust-comparison/01-language-runtime.md) | 从最新标准对比 Python 与 Rust 在语法、类型、内存、并发与运行时上的机制差异。 | 2026-08-07 | python、rust、类型系统、内存、并发、异步 |
| [Python 与 Rust 技术对比 · 性能与工程化](../tech/python-rust-comparison/02-performance-engineering.md) | 对比 Python 与 Rust 在运行时性能、资源占用与工程化工具链上的差异。 | 2026-08-07 | python、rust、性能、工具链、工程化 |
| [Python 与 Rust 技术对比 · 生态、应用场景与代码示例](../tech/python-rust-comparison/03-ecosystem-scenarios.md) | 对比 Python 与 Rust 的生态成熟度、典型应用场景，并提供对照代码示例。 | 2026-08-07 | python、rust、生态、应用场景、代码示例 |
| [Python 与 Rust 技术对比 · 决策矩阵与迁移路径](../tech/python-rust-comparison/04-decision-migration.md) | 提供 Python 与 Rust 选型决策矩阵、场景化建议、迁移路径与结论。 | 2026-08-07 | python、rust、决策矩阵、选型建议、迁移、混合架构 |
| [Python 迁移到 Rust 简易检查清单](../tech/python-rust-comparison/05-migration-checklist.md) | 基于《Python 与 Rust 技术对比》报告萃取的迁移到 Rust 的简易检查清单，覆盖决策、热点识别、PoC、逐模块迁移、测试、培训与灰度回退。 | 2026-08-07 | python、rust、迁移、检查清单、混合架构 |
| [量子密信调研：中国电信量子安全办公平台与 QKD+PQC 融合体系](../tech/quantum-secret-messaging/index.md) | 以七概念方法论（R→I→E→V→C，standard）对「量子密信」开展系统性案头研究：采集 50 条带来源客观事实，覆盖产品定义、从量子密话到量子密信的演进、融 QKD 与 PQC 的三层分布式密码体系、16 城量子城域网基础设施、国际安全机构立场与用户评价；形成 4 条四元组洞察与 1 个可迁移模式（双轨分层迁移法，多源支撑但未做本项目实测，入库定级 L1-draft）。知识包按问题域拆为产品定位、演进时间线、技术架构、基础设施、安全边界、采用模式 6 个概念页，附信源台账与对抗审查记录。 | 2026-09-30 | - |
| [TVM FFI 教程总览](../tech/tvm-ffi-wiki/00-overview.md) | Apache TVM FFI 中文wiki教程总览 | 2026-07-28 | tvm-ffi、ffi、c++、python、ml-system |
| [项目结构说明](../tech/tvm-ffi-wiki/01-project-structure.md) |  | 2026-07-28 | tvm-ffi、project-structure |
| [Any/AnyView 类型系统](../tech/tvm-ffi-wiki/02-any-type.md) |  | 2026-07-28 | tvm-ffi、type-system、any、type-erasure |
| [Object 对象系统](../tech/tvm-ffi-wiki/03-object-system.md) |  | 2026-07-28 | tvm-ffi、object、reference-counting、inheritance |
| [Function 函数与全局注册表](../tech/tvm-ffi-wiki/04-function-registry.md) |  | 2026-07-28 | tvm-ffi、function、packed-func、registry |
| [Container 容器类型](../tech/tvm-ffi-wiki/05-containers.md) |  | 2026-07-28 | tvm-ffi、container、array、map、tensor |
| [Reflection 反射系统](../tech/tvm-ffi-wiki/06-reflection.md) |  | 2026-07-28 | tvm-ffi、reflection、dataclass、stubgen |
| [Module 模块系统](../tech/tvm-ffi-wiki/07-module-system.md) |  | 2026-07-28 | tvm-ffi、module、dynamic-loading、dll |
| [C++ 开发指南](../tech/tvm-ffi-wiki/08-cpp-guide.md) |  | 2026-07-28 | tvm-ffi、cpp、guide、cmake、build |
| [Python 开发指南](../tech/tvm-ffi-wiki/09-python-guide.md) |  | 2026-07-28 | tvm-ffi、python、guide、cython |
| [构建与打包](../tech/tvm-ffi-wiki/10-build-packaging.md) |  | 2026-07-28 | tvm-ffi、build、cmake、packaging、wheel |
| [实战案例](../tech/tvm-ffi-wiki/11-examples.md) |  | 2026-07-28 | tvm-ffi、examples、tutorial、kernel |
| [常见问题解答 (FAQ)](../tech/tvm-ffi-wiki/12-faq.md) |  | 2026-07-28 | tvm-ffi、faq、troubleshooting |
| [核心源码解析（进阶）](../tech/tvm-ffi-wiki/13-source-analysis.md) |  | 2026-07-28 | tvm-ffi、source-code、internals、advanced |
| [教程总览：用 xuan-compose 编排手帐贴纸风格照片生成](../tech/xuan-compose-sticker-wiki/00-overview.md) | 以『一张照片→手帐记忆卡+透明底贴纸双产物』为实战案例，系统讲解 xuan-compose（podman-compose 翻译重构的 Compose 规范编排引擎）的安装、compose 文件、卷与 secret、服务生命周期、一次性任务与库 API。 | 2026-10-09 | xuan-compose、podman、compose、容器编排、seedream、手帐贴纸 |
| [流水线设计与 xuan-compose 七层架构](../tech/xuan-compose-sticker-wiki/01-pipeline-architecture.md) | 先按『长驻/一次性』『确定性/模型判断』两个轴切分创意流水线，再把每个环节映射到 xuan-compose 的服务与一次性任务；最后对照引擎七层架构理解编排是如何被翻译为 podman 调用的。 | 2026-10-09 | xuan-compose、podman、compose、架构、服务拓扑 |
| [安装、工程骨架与 compose 文件发现规则](../tech/xuan-compose-sticker-wiki/02-install-discovery.md) | 安装 xuan-compose 与 Podman，搭好 sticker-studio 工程骨架；讲透 compose 文件的 14 个默认名、向上 10 层递归发现、-f/COMPOSE_FILE 指定方式，以及项目名与 .env 的解析优先级。 | 2026-10-09 | xuan-compose、安装、compose、文件发现、项目名 |
| [compose.yaml 逐段精讲：服务、插值与 config 校验](../tech/xuan-compose-sticker-wiki/03-compose-walkthrough.md) | 逐段讲解 sticker-studio 的 compose.yaml：build/image/command、environment 与 bash 风格变量插值（:-/-/:?/?/:+/+ 与 $$ 转义）、profiles、顶层 volumes/secrets 声明，以及用 config 命令在起容器前验证合并结果。 | 2026-10-09 | xuan-compose、compose、yaml、插值、build、config |
| [卷、密钥与网络：照片进出、API Key 托管与服务互通](../tech/xuan-compose-sticker-wiki/04-volumes-secrets.md) | 讲透短挂载语法与 bind/命名卷/tmpfs 的判定规则、宿主目录自动创建与未声明卷报错；文件 secret 与环境 secret 两种 API Key 托管方式；默认网络自动创建、命名规则与 network_mode 边界。 | 2026-10-09 | xuan-compose、volumes、secrets、networks、安全 |
| [服务生命周期、依赖条件与 run --rm 一次性任务](../tech/xuan-compose-sticker-wiki/05-lifecycle-tasks.md) | 讲透 depends_on 三种条件到 podman wait 的映射、healthcheck、up 的镜像准备与配置哈希重建对账、down 的逆序清理，以及用 run --rm 把色幕去底实现为退出码可判定的一次性任务。 | 2026-10-09 | xuan-compose、depends_on、healthcheck、up、down、run、一次性任务 |
| [生图服务实战：把 Seedream 5.0 Pro 装进容器](../tech/xuan-compose-sticker-wiki/06-generator-worker.md) | 构建 generator 镜像：用环境变量外置端点/模型/密钥，用经官方文档核实的 images/generations 请求完成记忆卡与色幕贴纸稿两次 I2I 生成；提示词按 seedream-50 方法论与 travel-memory-card-duo 规范落地为模板文件；同一镜像兼顾长驻 API 与一次性 CLI。 | 2026-10-09 | xuan-compose、seedream、dockerfile、fastapi、i2i、提示词 |
| [色幕去底：把一次性任务做成退出码可判定的容器](../tech/xuan-compose-sticker-wiki/07-chroma-key-task.md) | 用 Pillow/numpy 实现均匀色幕抠除（边框取色、RMS 色差双阈值、软蒙版、溢色抑制 despill、边缘腐蚀），打包成无守护进程的 keychroma 镜像，通过 xuan-compose run --rm 触发并以退出码与四角 alpha 校验透明底 PNG 的正确性。 | 2026-10-09 | xuan-compose、一次性任务、chroma-key、pillow、rgba、贴纸 |
| [库 API 与无 Podman 预演：把编排错误挡在起容器之前](../tech/xuan-compose-sticker-wiki/08-library-api.md) | xuan-compose 不只是 CLI：import 零副作用，ComposeEngine 是纯状态对象，parse_args 纯解析回写，_parse_compose_file 可在 Python 中完成发现/插值/合并/规范化；配合 config、--dry-run 与一段断言脚本，可在没有 Podman 的环境里把绝大多数编排错误挡下来。 | 2026-10-09 | xuan-compose、库-api、dry-run、静态校验、python314 |
| [避坑、上游怪癖与 FAQ](../tech/xuan-compose-sticker-wiki/09-pitfalls-faq.md) | 汇总 xuan-compose 刻意保留的 podman-compose 上游怪癖（退出码 -1、时间解析、./ 前缀、tag 百分号编码、ls 非标准 JSON 等）、版本门槛、Windows/WSL 取舍、GPL-2.0 许可边界，以及本案例高频报错的定位与处理。 | 2026-10-09 | xuan-compose、避坑、faq、怪癖、wsl、许可证 |
| [可复用模式、端到端演练与验收清单](../tech/xuan-compose-sticker-wiki/10-pattern-checklist.md) | 把案例抽象为可迁移模式『声明式创意流水线：服务-任务分离编排』，给出适用边界、核心步骤、反模式、端到端命令演练与验收清单，并迁移到 ETL/文档批处理/ML 推理后处理等领域。 | 2026-10-09 | xuan-compose、模式、反模式、验收清单、迁移、知识沉淀 |

---

*索引自动生成于 2026-10-20 11:27:18*
