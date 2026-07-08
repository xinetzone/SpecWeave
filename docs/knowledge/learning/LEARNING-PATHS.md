---
id: "learning-paths"
title: "Learning Wiki 学习路径推荐表"
category: "learning"
tags: ["learning-path", "study-guide", "prerequisites", "knowledge-graph", "curriculum"]
date: "2026-07-05"
version: "1.0"
status: "stable"
author: ""
summary: "Learning Wiki知识库59个Wiki的系统化学习路径推荐，包含8主题内部学习顺序、前置依赖、关联知识点、角色定制路径"
source: ""
x-toml-ref: "../../../.meta/toml/docs/knowledge/learning/LEARNING-PATHS.toml"
changelog: "2026-07-05 | docs | 初始创建：基于8主题分类体系生成分主题详细学习路径"
---
# Learning Wiki 学习路径推荐表

> 系统化学习导航 · 前置依赖标注 · 知识点关联图 · 角色定制路径
> 创建日期：2026-07-05
> 适用对象：AI Agent开发者、技术研究者、产品经理、IoT开发者、AI创作者

---

## 一、使用说明

### 难度标注说明

| 标注 | 含义 | 适合人群 |
|------|------|---------|
| ⭐ 入门 | 无需前置知识，概念性内容为主 | 所有学习者 |
| ⭐⭐ 进阶 | 需要基本的编程/技术背景 | 开发者、技术产品经理 |
| ⭐⭐⭐ 高级 | 需要深入的系统级知识或特定领域经验 | 高级开发者、研究员 |

### 主题依赖关系总览

```
08 底层系统 ──────────────────────────────┐
    │                                     │
    ▼                                     ▼
01 协议与接口 ──→ 02 工程方法论 ──→ 03 平台与工具 ──→ 06 商业趋势
                      │                   │              │
                      ├──→ 04 文档工具 ───┘              ▼
                      │                                 07 厂商产品
                      └──→ 05 多模态内容 ────────────────┘
```

**关键规则**：
- 实线箭头（→）表示强依赖，建议按顺序学习
- 04（文档工具）和05（多模态）可与03并行学习
- 07（厂商产品）建议在01-03之后学习，以获得最佳理解
- 08（底层系统）可随时穿插学习，不阻塞其他主题

---

## 二、分主题学习路径

---

### 01 Agent协议与接口技术栈

**主题定位**：Agent生态的"通信宪法"——理解Agent之间如何互操作的基础标准层
**学习前提**：基本的网络通信概念（HTTP/JSON/RPC），了解API基本概念

| 步骤 | Wiki | 难度 | 学习目标 | 预计时间 | 前置步骤 |
|------|------|------|---------|---------|---------|
| 1.1 | [四层概念辨析](01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/00-overview.md) | ⭐ | 建立Interface/API/ABI/Protocol四层抽象的通用认知框架 | 40min | 无 |
| 1.2 | [Agent通信协议](01-agent-protocols-interfaces/agent-communication-protocols-wiki.md) | ⭐⭐ | 掌握MCP/ACP/A2A/ANP四层协议栈的定位、架构和交互流程 | 2h | 1.1 |
| 1.3 | [Agent Interface深度解析](01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md) | ⭐⭐ | 从Agent视角理解四层抽象在MCP/A2A生态中的具体落地 | 1.5h | 1.2 |
| 1.4 | [Agent Skills开放标准](01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md) | ⭐⭐ | 理解agentskills.io开放标准：SKILL.md格式、渐进式披露、自包含脚本 | 2h | 1.2 |
| 1.5 | [Agent Skills完整教程](01-agent-protocols-interfaces/agent-skills-wiki/00-overview.md) | ⭐⭐ | 动手实践Skill开发：快速入门→最佳实践→描述优化→质量评估→客户端集成 | 3h | 1.4 |
| 1.6 | [国内Skill/MCP生态盘点](01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md) | ⭐ | 了解国内16个品牌的Agent化进展（微信/飞书/钉钉/支付等） | 40min | 1.2 |
| 1.7 | [IDL接口定义语言](01-agent-protocols-interfaces/idl-wiki/00-overview.md) | ⭐⭐ | 系统掌握接口定义语言的语法类型、主流规范对比、工具链 | 2h | 1.1 |
| 1.8 | [FFI外部函数接口](01-agent-protocols-interfaces/ffi-wiki/00-overview.md) | ⭐⭐⭐ | 深入理解跨语言调用的底层机制、多语言实现、工作原理 | 2h | 1.1, 1.7 |
| 1.9 | [TVM FFI深度学习编译器](01-agent-protocols-interfaces/tvm-ffi-wiki/00-overview.md) | ⭐⭐⭐ | FFI在深度学习编译器中的实战案例，C++核心API/Python绑定/CUDA支持 | 2h | 1.8 |
| 1.10 | [Agent Runtime Protocol](01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md) | ⭐⭐⭐ | 生产级Agent运行时协议八大维度，对比LangGraph/OpenAI Assistants/AutoGen | 1.5h | 1.2, 1.3 |

**主题内知识关联**：
- 1.1是所有Wiki的概念基础
- 1.2→1.3是Agent协议从通用到Agent语境的深化
- 1.4→1.5是Skills标准从理论到实践的递进
- 1.7→1.8→1.9是接口技术从通用到FFI到实战案例的深度链路
- 1.10是协议层的高级话题，建议在理解基础协议后再学

**学完本主题后建议延伸**：
- → [02 工程方法论](02-agent-engineering-methodology/four-engineering-concepts-wiki.md)：理解协议之上如何构建工程体系
- → [03 平台工具](03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md)：看具体平台如何实现这些协议
- → [08 底层系统](08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)：WSL中Plan9/DrvFs的跨进程通信与协议思想相通

---

### 02 Agent工程方法论

**主题定位**：Agent开发的"兵法"——四代工程范式演进与系统化思维框架
**学习前提**：完成01主题（至少1.1-1.3），具备基本的LLM使用经验

| 步骤 | Wiki | 难度 | 学习目标 | 预计时间 | 前置步骤 |
|------|------|------|---------|---------|---------|
| 2.1 | [四代工程概念演进](02-agent-engineering-methodology/four-engineering-concepts-wiki.md) | ⭐ | 建立Prompt→Context→Harness→Loop的范式演进全局认知，理解瓶颈转移逻辑 | 40min | 01主题基础 |
| 2.2 | [Vibe Coding神级Prompt](02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md) | ⭐ | 掌握第一性原理（管生成）+对抗式审查（管验证）双Prompt闭环 | 30min | 无（可独立阅读） |
| 2.3 | [Karpathy LLM编程准则](02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md) | ⭐⭐ | 四条行为准则：编码前思考/简约至上/精确编辑/目标驱动，含真实代码正反例 | 2.5h | 2.1 |
| 2.4 | [Harness驾驭工程](02-agent-engineering-methodology/harness-engineering-wiki.md) | ⭐⭐ | 四条反直觉铁律、六大工程模式、悟空AI招聘实战案例 | 2h | 2.1, 2.3 |
| 2.5 | [LongCat Agent实测](02-agent-engineering-methodology/longcat-agent-learning-wiki.md) | ⭐⭐ | 美团LongCat-2.0接入Claude Code实战：BI看板项目、Token效率、Loop Engineering | 2h | 2.3, 2.4 |
| 2.6 | [Headroom上下文压缩](02-agent-engineering-methodology/headroom-context-compression-wiki.md) | ⭐⭐⭐ | 六种压缩算法、CCR可逆机制、四种接入方式、跨Agent记忆 | 2h | 2.4 |
| 2.7 | [DSpark推理加速论文](02-agent-engineering-methodology/dspark-paper-wiki.md) | ⭐⭐⭐ | DeepSeek推理加速论文笔记，理解LLM推理性能优化方法论 | 1.5h | 2.4, 2.6 |

**主题内知识关联**：
- 2.1是全主题的认知地图，建议最先阅读
- 2.2最简短实用，可作为入门的"热身"材料
- 2.3（Karpathy准则）是日常编码的行动指南，建议在2.4之前掌握
- 2.4（Harness工程）是核心方法论，2.5是Harness+Loop的实战验证
- 2.6（上下文压缩）和2.7（推理加速）是性能优化方向的高级话题

**学完本主题后建议延伸**：
- → [03 平台工具](03-agent-platforms-tools/claude-tag-article.md)：看方法论在真实产品中的落地
- → [07 厂商产品](07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)：看厂商如何应用工程方法论做产品
- → [04 文档工具](04-docs-markup-tooling/executablebooks-myst-guide-wiki.md)：知识沉淀是Harness的重要组成部分

---

### 03 Agent平台与工具生态

**主题定位**：Agent技术的"兵器谱"——主流平台与工具的全景认知与选型参考
**学习前提**：完成01主题（理解协议层）和02主题的2.1-2.3（理解工程范式）

| 步骤 | Wiki | 难度 | 学习目标 | 预计时间 | 前置步骤 |
|------|------|------|---------|---------|---------|
| 3.1 | [Anthropic Agent路线图](03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md) | ⭐ | 了解Anthropic六条Agent产品线（Conway/Orbit/Operon/BugCrawl等）和行业竞争格局 | 1h | 02主题基础 |
| 3.2 | [Claude Tag企业协作](03-agent-platforms-tools/claude-tag-article.md) | ⭐⭐ | 理解Ambient Mode（主动介入）、共享上下文、异步执行等企业协作Agent设计 | 1.5h | 3.1 |
| 3.3 | [Open Code Review代码评审](03-agent-platforms-tools/open-code-review-wiki.md) | ⭐⭐ | 阿里开源AI代码评审工具：安装、使用、优化、集成、效果验证 | 2h | 2.3 Karpathy准则 |
| 3.4 | [BrowserAct浏览器自动化](03-agent-platforms-tools/browseract-wiki.md) | ⭐⭐ | 让Agent操作浏览器的自动化工具，Playwright+Skill Forge架构 | 1h | 01主题Skills标准 |
| 3.5 | [EchoBird百灵鸟桌面Agent](03-agent-platforms-tools/echobird-wiki.md) | ⭐⭐ | Tauri+Rust桌面Agent，Model Nexus支持本地LLM | 1h | 3.1 |
| 3.6 | [Octo多Agent协作平台](03-agent-platforms-tools/octo-platform-wiki.md) | ⭐⭐ | 明略科技Private AI多Agent协作：Matter/Taste/Orchestration | 1h | 1.2 A2A协议 |
| 3.7 | [AReaL自演进Agent RL](03-agent-platforms-tools/areal-agent-rl-wiki.md) | ⭐⭐⭐ | 蚂蚁集团在线强化学习基础设施，Agent自演进机制 | 1.5h | 2.4 Harness工程 |
| 3.8 | **垂直领域选读**：[Anthropic金融服务](03-agent-platforms-tools/anthropic-financial-services-wiki.md) | ⭐⭐ | 华尔街AI金融Agent工具箱（金融方向必读） | 1h | 3.1 |
| 3.9 | **垂直领域选读**：[QuantDinger量化交易](03-agent-platforms-tools/quantdinger-ai-trading-wiki.md) | ⭐⭐⭐ | 开源自托管AI量化平台、MCP Agent Gateway（金融方向） | 1.5h | 3.8 |
| 3.10 | **垂直领域选读**：[MopMonk安全Agent](03-agent-platforms-tools/mopmonk-security-agent-wiki.md) | ⭐⭐ | MiniMax M3驱动的安全Agent、CyberGym漏洞挖掘（安全方向） | 1h | 3.3 |
| 3.11 | **垂直领域选读**：[Rainman AI翻译](03-agent-platforms-tools/rainman-translate-book-wiki.md) | ⭐⭐ | AI翻译工具Wiki教程（内容创作方向） | 1h | 无 |
| 3.12 | **垂直领域选读**：[The Agency项目](03-agent-platforms-tools/the-agency-project-wiki.md) | ⭐⭐ | The Agency多Agent项目学习笔记 | 50min | 3.6 |

**主题内知识关联**：
- 3.1（路线图）是全局视野，建议最先阅读
- 3.2（Claude Tag）是企业协作Agent的典型案例，与Harness工程中的"团队共享"概念呼应
- 3.3（Code Review）和3.4（BrowserAct）是开发效率工具，建议开发者优先阅读
- 3.5-3.7是不同技术路线的Agent平台（桌面/多Agent/RL），按需选读
- 3.8-3.12是垂直领域选读，根据兴趣和工作方向选择

**学完本主题后建议延伸**：
- → [06 商业趋势](06-business-trends-analysis/ai-monetization-wiki/00-overview.md)：思考这些产品的商业价值
- → [07 厂商产品](07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md)：对比通用平台和垂直厂商产品的差异
- → [04 文档工具](04-docs-markup-tooling/myst-markdown-tutorial/README.md)：如果你需要为自己的Agent产品写文档

---

### 04 文档工具链与标记语言

**主题定位**：知识沉淀的"工匠精神"——高质量文档是知识可复用的基础
**学习前提**：Markdown基础语法，无其他硬性要求（可独立学习）

| 步骤 | Wiki | 难度 | 学习目标 | 预计时间 | 前置步骤 |
|------|------|------|---------|---------|---------|
| 4.1 | [HTML声明式局部更新](04-docs-markup-tooling/declarative-partial-updates-wiki.md) | ⭐⭐ | 理解Chrome声明式局部更新、Streaming SSR、Declarative Shadow DOM | 50min | 无（可独立阅读） |
| 4.2 | [ExecutableBooks/MyST指南](04-docs-markup-tooling/executablebooks-myst-guide-wiki.md) | ⭐⭐ | MyST Markdown生态概览、Directives/Roles核心语法、项目配置 | 2h | 无 |
| 4.3 | [MyST Markdown完整教程](04-docs-markup-tooling/myst-markdown-tutorial/README.md) | ⭐⭐ | 从入门到精通16章：基础语法→高级特性→数学公式→UI组件→工具链 | 4h | 4.2 |
| 4.4 | [scikit-build-core Python构建](04-docs-markup-tooling/scikit-build-core-wiki/00-overview.md) | ⭐⭐⭐ | 下一代Python构建系统，概念架构、项目结构、核心API（Python开发者选读） | 1.5h | 基本Python包管理知识 |

**主题内知识关联**：
- 4.1是Web标准的文档/UI相关知识，可独立阅读
- 4.2→4.3是MyST从概览到精通的递进路径
- 4.4是Python构建工具，与MyST同属"工具链"但关联度不高，可按需选读

**学完本主题后建议延伸**：
- 本主题是横向支撑能力，可服务于所有其他主题的文档写作需求
- → 回到[02 工程方法论](02-agent-engineering-methodology/headroom-context-compression-wiki.md)：Headroom文档中可能涉及文档压缩表示
- → 可使用MyST重写或优化其他主题的Wiki文档

---

### 05 AI多模态与内容生成

**主题定位**：AI创造力的"工具箱"——文本之外的多模态内容生成技术
**学习前提**：基本的AI概念，无硬性技术门槛（可独立学习）

| 步骤 | Wiki | 难度 | 学习目标 | 预计时间 | 前置步骤 |
|------|------|------|---------|---------|---------|
| 5.1 | [Ian小嘿插图AI配图](05-ai-multimodal-content/ian-xiaohei-illustrations.md) | ⭐ | AI配图Skill入门，了解AI图像生成在实际项目中的应用 | 30min | 无 |
| 5.2 | [AudioX-Turbo极速音频生成](05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md) | ⭐⭐ | 4步推理+6种任务统一的Anything-to-Audio框架，DMD师生蒸馏 | 1h | 无 |
| 5.3 | [Anime.js+Three.js 3D动画](05-ai-multimodal-content/animejs-threejs-adapter-analysis.md) | ⭐⭐ | 适配器模式解决Three.js动画痛点，API扁平化设计 | 1h | 基本JavaScript/前端知识 |
| 5.4 | [Text-to-CAD文本转CAD](05-ai-multimodal-content/text-to-cad-wiki.md) | ⭐⭐ | 文本转CAD技术概述（3D建模方向） | 50min | 无 |
| 5.5 | [Agnes/Pavo AI短剧平台](05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md) | ⭐⭐ | 免费多模态API+一站式AI短剧工作流（AI视频创作方向） | 1h | 无 |
| 5.6 | [LibTV AI短剧创作](05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md) | ⭐⭐ | AI短剧/漫画创作：3D导演、角色质量控制、情感控制（AI视频方向） | 1h | 5.5 |

**主题内知识关联**：
- 5.1最简短，可作为快速入门
- 5.2（音频）、5.3（3D动画）、5.4（CAD）是不同模态的技术解析，彼此独立
- 5.5→5.6是AI短剧/视频方向的递进学习（先平台概览再工具详解）

**学完本主题后建议延伸**：
- → [06 商业趋势](06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md)：多模态内容的商业化路径
- → [07 厂商产品](07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md)：多模态在硬件产品中的应用（如远程摄像头）

---

### 06 AI商业与趋势观察

**主题定位**：技术价值的"罗盘"——连接技术能力与商业价值
**学习前提**：完成01-03主题（对Agent技术有基本认知），对商业分析有兴趣

| 步骤 | Wiki | 难度 | 学习目标 | 预计时间 | 前置步骤 |
|------|------|------|---------|---------|---------|
| 6.1 | [AI变现完整指南](06-business-trends-analysis/ai-monetization-wiki/00-overview.md) | ⭐⭐ | AI变现全流程：市场分析→商业模式→技术选型→产品开发→GTM→盈利→三类场景 | 3h | 03主题基础 |
| 6.2 | [国产AI模型对比](06-business-trends-analysis/domestic-llm-comparison-notes.md) | ⭐ | DeepSeek V4/Kimi K2.7/MiniMax M3/GLM 5.2对比，按场景推荐选型 | 40min | 无 |
| 6.3 | [三大AI工具分析](06-business-trends-analysis/three-ai-tools-wiki.md) | ⭐ | AI工具对比分析框架 | 30min | 无 |
| 6.4 | [Papi酱个人IP创业趋势](06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md) | ⭐ | "把公司做小，把IP做大"创业新趋势，小而美模式实践 | 1h | 无 |
| 6.5 | [火山引擎KickArt营销创作](06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md) | ⭐⭐ | 营销创作平台案例分析（AI+营销方向） | 50min | 6.1 |

**主题内知识关联**：
- 6.1（AI变现指南）是核心框架，建议最先阅读
- 6.2-6.3是工具/模型选型参考，可独立阅读
- 6.4（Papi酱案例）是个人IP/小而美创业的案例研究，与6.1中的ToC/个人变现场景呼应
- 6.5是AI+营销的商业案例，是6.1变现框架的具体应用

**学完本主题后建议延伸**：
- → [07 厂商产品](07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)：看成熟厂商如何选择商业赛道
- → [03 平台工具](03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)：垂直领域产品的商业模式分析

---

### 07 厂商产品学习系列

**主题定位**：理论落地的"解剖台"——通过产品拆解验证方法论
**学习前提**：完成01-03主题（理解协议、方法论、平台全景）

#### 7A. 向日葵子系列（贝锐Oray）

| 步骤 | Wiki | 难度 | 学习目标 | 预计时间 | 前置步骤 |
|------|------|------|---------|---------|---------|
| 7A.1 | [产品系列索引](07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md) | ⭐ | 向日葵全系列产品导航，建立产品矩阵全景认知 | 20min | 03主题基础 |
| 7A.2 | [贝锐Oray AI产品矩阵](07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md) | ⭐⭐ | 贝锐五大产品线（向日葵/蒲公英/花生壳/洋葱头/龙虾OrayClaw）AI战略分析 | 1.5h | 7A.1 |
| 7A.3 | [向日葵开机盒子](07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md) | ⭐⭐ | 开机盒子深度拆解：WOL远程开机、版本策略、Web UX分析（原子化10章节） | 2h | 7A.2 |
| 7A.4 | [向日葵无网远控硬件](07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md) | ⭐⭐ | 无网远控系列（空空2/Q1/Q2Pro/Q0.5/Q5Pro）BLE技术解析与对比（原子化10章节） | 2h | 7A.3 |
| 7A.5 | [向日葵USB摄像头SU1](07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md) | ⭐ | 400万高清摄像头产品解析，远程医疗/视频会议场景 | 40min | 7A.1 |
| 7A.6 | [向日葵智能远控鼠标](07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md) | ⭐ | 智能远控鼠标BM110/MM110产品分析 | 40min | 7A.1 |
| 7A.7 | [向日葵智能插线板P4/P1Pro](07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md) | ⭐ | P4与P1Pro对比分析 | 40min | 7A.1 |
| 7A.8 | [向日葵智能PDU](07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md) | ⭐⭐ | 机房配电设备学习，企业级远程电源管理 | 50min | 7A.7 |
| 7A.9 | [向日葵智能插座](07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md) | ⭐ | 智能插座产品学习 | 30min | 7A.1 |
| 7A.10 | [向日葵安全产品](07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md) | ⭐⭐ | 向日葵安全产品与远程访问安全 | 50min | 7A.2 |

#### 7B. 涂鸭子系列（TuyaOpen AI-IoT SDK）

| 步骤 | Wiki | 难度 | 学习目标 | 预计时间 | 前置步骤 |
|------|------|------|---------|---------|---------|
| 7B.1 | [TuyaOpen全面学习报告](07-vendor-product-learning/tuya/tuya-open-learning-report.md) | ⭐⭐ | 跨平台/跨芯片/跨OS的AI-IoT SDK，TKL/TAL/TDD/TDL分层架构 | 2h | 01主题FFI/IDL基础 |
| 7B.2 | [TuyaOpen目录学习路径](07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md) | ⭐⭐⭐ | 从LINUX构建闭环到硬件烧录与AI能力区的可执行路线 | 1.5h | 7B.1 |
| 7B.3 | [TuyaOpen-dev-skills学习笔记](07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md) | ⭐⭐ | AI Skills仓库三分结构：最小SKILL.md+references按需加载+scripts可执行 | 1h | 7B.1, 01主题Skills标准 |

**主题内知识关联**：
- 7A.1（系列索引）是向日葵系列的入口，必须最先阅读
- 7A.2（AI产品矩阵）从公司战略高度理解产品线布局
- 7A.3→7A.4是两个原子化深度拆解Wiki，建议精读（核心产品）
- 7A.5-7A.10是各产品线单篇学习，可按兴趣选读
- 7B.1→7B.2→7B.3是涂鸦SDK从概览到实操到Skills集成的递进链路

**学完本主题后建议延伸**：
- → 回到[02 工程方法论](02-agent-engineering-methodology/harness-engineering-wiki.md)：重新审视Harness模式在产品设计中的体现
- → [06 商业趋势](06-business-trends-analysis/ai-monetization-wiki/00-overview.md)：分析贝锐/涂鸦的商业模式与变现路径

---

### 08 底层系统与基础设施

**主题定位**：所有上层应用的"地基"——操作系统与运行时环境
**学习前提**：基本的操作系统概念，可随时学习（不阻塞其他主题）

| 步骤 | Wiki | 难度 | 学习目标 | 预计时间 | 前置步骤 |
|------|------|------|---------|---------|---------|
| 8.1 | [WSL系统学习计划](08-systems-infrastructure/wsl-learning-plan.md) | ⭐⭐ | WSL系统学习路线图：三层架构、核心进程、Plan9/DrvFs、Container API、CMake、5个实操、4周路径 | 30min（制定计划） | 无 |
| 8.2 | [WSL CLI与架构参考](08-systems-infrastructure/wsl-cli-and-architecture-wiki.md) | ⭐⭐⭐ | 基于源码的CLI命令树、四层架构模型、interop binfmt、systemd启动、COM接口 | 3h（参考手册，按需查阅） | 8.1 |

**主题内知识关联**：
- 8.1是学习计划/路线图，建议先阅读以建立学习框架
- 8.2是参考手册性质的文档，不需要一次性读完，可在实践中按需查阅
- WSL学习建议配合实际操作（按照学习计划中的4周路径执行）

**学完本主题后建议延伸**：
- → [01 协议与接口](01-agent-protocols-interfaces/ffi-wiki/00-overview.md)：WSL的interop binfmt机制与FFI跨语言调用思想相通
- → [04 文档工具](04-docs-markup-tooling/scikit-build-core-wiki/00-overview.md)：WSL中的CMake跨编译与Python构建系统关联

---

## 三、角色定制学习路径

### 🧑‍💻 路径A：AI Agent应用开发者

**目标**：掌握Agent开发全流程，能独立构建Agent应用
**预计时间**：6-8周

| 周次 | 主题 | 核心步骤 | 重点产出 |
|------|------|---------|---------|
| 第1周 | 01 协议与接口 | 1.1→1.2→1.3→1.4→1.5 | 理解MCP协议，能写一个简单的Skill |
| 第2周 | 02 工程方法论 | 2.1→2.2→2.3→2.4→2.5 | 掌握Karpathy准则，理解Harness模式，运行LongCat实战 |
| 第3周 | 03 平台工具 | 3.1→3.2→3.3→3.4 | 使用过Claude Tag/Code Review/BrowserAct等工具 |
| 第4周 | 04 文档工具 | 4.2→4.3 | 能用MyST写技术文档 |
| 第5周 | 03 垂直领域 | 按方向选读3.8-3.12 | 深入1-2个垂直领域Agent |
| 第6周 | 06 商业趋势 | 6.1→6.2 | 理解AI产品商业模式，能做技术选型 |
| 第7-8周 | 07 厂商产品 | 7A.1→7A.3→7B.1 | 深入拆解1-2个厂商产品，做产品对标分析 |

### 🎯 路径B：AI产品经理

**目标**：建立Agent技术认知，能进行产品规划和选型决策
**预计时间**：3-4周

| 周次 | 主题 | 核心步骤 | 重点产出 |
|------|------|---------|---------|
| 第1周 | 01 协议与接口 | 1.1→1.2→1.6 | 理解Agent互操作标准和国内生态 |
| 第2周 | 02 工程方法论 | 2.1→2.2→2.4 | 建立工程范式认知，理解Harness设计思想 |
| 第3周 | 03 平台工具 | 3.1→3.2→3.6 + 垂直领域选读 | 了解主流平台和竞品 |
| 第4周 | 06+07 | 6.1→6.4→7A.1→7A.2 | 理解商业变现，分析厂商产品矩阵策略 |

### 🔬 路径C：AI技术研究员

**目标**：深入Agent底层技术，理解系统架构与性能优化
**预计时间**：8-10周

| 周次 | 主题 | 核心步骤 | 重点产出 |
|------|------|---------|---------|
| 第1-2周 | 08+01底层 | 8.1→8.2→1.7→1.8→1.9 | 掌握WSL架构、FFI/IDL底层机制、TVM FFI案例 |
| 第3周 | 01 协议层 | 1.2→1.3→1.10 | 深入理解协议栈和Runtime Protocol设计 |
| 第4-5周 | 02 方法论 | 2.1→2.3→2.4→2.6→2.7 | 深入Harness工程、上下文压缩、推理加速 |
| 第6周 | 03 前沿平台 | 3.6→3.7 | 多Agent协作、自演进RL等前沿方向 |
| 第7-8周 | 04+05 | 4.2→4.3→5.2→5.4 | 文档工具链、多模态生成技术 |
| 第9-10周 | 07 厂商产品 | 7A.3→7A.4→7B.1→7B.2 | 深度产品拆解和架构分析 |

### 🔧 路径D：IoT/硬件开发者

**目标**：掌握AI-IoT开发，理解软硬结合产品设计
**预计时间**：5-6周

| 周次 | 主题 | 核心步骤 | 重点产出 |
|------|------|---------|---------|
| 第1周 | 01 协议基础 | 1.1→1.2→1.7→1.8 | 理解协议/接口/FFI/IDL，为IoT SDK开发打基础 |
| 第2周 | 02 工程方法 | 2.1→2.3→2.4 | 掌握LLM编程准则和工程范式 |
| 第3周 | 08 底层系统 | 8.1→8.2 | WSL开发环境配置与系统理解 |
| 第4-5周 | 07 涂鸦SDK | 7B.1→7B.2→7B.3 | TuyaOpen SDK实战：构建闭环→烧录→AI Skills |
| 第6周 | 07 向日葵 | 7A.1→7A.2→7A.3→7A.4 | 学习软硬结合产品设计（远程控制硬件系列） |

### 🎨 路径E：AI内容创作者

**目标**：掌握多模态AI工具，提升内容创作效率
**预计时间**：2-3周

| 周次 | 主题 | 核心步骤 | 重点产出 |
|------|------|---------|---------|
| 第1周 | 02 方法入门 | 2.2→2.3 | Vibe Coding Prompt + Karpathy准则（AI辅助创作效率） |
| 第2周 | 05 多模态 | 5.1→5.2→5.5→5.6 | AI配图、音频生成、短剧创作工具 |
| 第3周 | 03+06 | 3.11（翻译工具）→6.4（IP案例） | AI翻译工作流、个人IP商业化路径 |

---

## 四、知识点交叉索引

### 跨主题核心概念关联

| 核心概念 | 主要主题 | 关联主题与Wiki |
|---------|---------|---------------|
| **MCP协议** | 01 | [01 通信协议](01-agent-protocols-interfaces/agent-communication-protocols-wiki.md) → [01 Interface深度](01-agent-protocols-interfaces/agent-interface-deep-dive/00-overview.md) → [03 QuantDinger](03-agent-platforms-tools/quantdinger-ai-trading-wiki.md) → [03 BrowserAct](03-agent-platforms-tools/browseract-wiki.md) → [07 涂鸦Skills](07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md) |
| **Harness模式** | 02 | [02 Harness工程](02-agent-engineering-methodology/harness-engineering-wiki.md) → [05 Agnes/Pavo](05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md)（harness在多模态中的应用）→ [07 开机盒子](07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md)（产品Harness设计） |
| **Skill开发** | 01 | [01 Skills标准](01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md) → [01 Skills教程](01-agent-protocols-interfaces/agent-skills-wiki/00-overview.md) → [05 Ian小嘿](05-ai-multimodal-content/ian-xiaohei-illustrations.md) → [07 涂鸦Skills](07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md) |
| **上下文压缩** | 02 | [02 Headroom](02-agent-engineering-methodology/headroom-context-compression-wiki.md) → [02 LongCat](02-agent-engineering-methodology/longcat-agent-learning-wiki.md)（Token效率对比）→ [02 DSpark](02-agent-engineering-methodology/dspark-paper-wiki.md)（推理级压缩） |
| **Agent协作** | 01-03 | [01 A2A协议](01-agent-protocols-interfaces/agent-communication-protocols-wiki.md) → [02 Harness多Agent](02-agent-engineering-methodology/harness-engineering-wiki.md) → [03 Octo](03-agent-platforms-tools/octo-platform-wiki.md) → [03 The Agency](03-agent-platforms-tools/the-agency-project-wiki.md) → [03 Claude Tag](03-agent-platforms-tools/claude-tag-article.md)（团队协作） |
| **软硬结合** | 07 | [07 Oray矩阵](07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md) → [07 开机盒子](07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md) → [07 无网远控](07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md) → [07 涂鸦SDK](07-vendor-product-learning/tuya/tuya-open-learning-report.md) → [05 摄像头SU1](05-ai-multimodal-content/../07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md) |
| **AI变现** | 06 | [06 AI变现指南](06-business-trends-analysis/ai-monetization-wiki/00-overview.md) → [03 QuantDinger](03-agent-platforms-tools/quantdinger-ai-trading-wiki.md)（SaaS+金融）→ [03 MopMonk](03-agent-platforms-tools/mopmonk-security-agent-wiki.md)（安全SaaS）→ [07 Oray矩阵](07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md)（软硬结合变现） |

### 按问题类型快速定位

| 我想了解... | 推荐阅读顺序 |
|------------|-------------|
| Agent之间是怎么通信的？ | 1.1 → 1.2 → 1.3 |
| 怎么让LLM写代码更靠谱？ | 2.2 → 2.3 → 2.4 → 3.3 |
| 怎么做一个AI Agent产品？ | 2.1 → 2.4 → 3.1 → 3.2 → 6.1 |
| 怎么解决Token不够用的问题？ | 2.4 → 2.6 → 2.5（Token效率章节）→ 2.7 |
| 有哪些AI工具可以直接用？ | 3.3 → 3.4 → 3.11 → 5.1 → 5.5 |
| 怎么做AI视频/短剧？ | 5.1 → 5.5 → 5.6 → 5.2（配音） |
| AI怎么赚钱？ | 6.1 → 6.2 → 6.4 → 3.8/3.9（金融方向） |
| 怎么做IoT+AI？ | 1.7 → 1.8 → 8.1 → 7B.1 → 7B.2 → 7B.3 |
| 怎么做远程控制硬件？ | 7A.1 → 7A.2 → 7A.3 → 7A.4 → 7A.5 |
| 怎么写高质量技术文档？ | 4.2 → 4.3 → 2.3（简约至上原则） |
| Agent的底层运行机制是什么？ | 8.2 → 1.8 → 1.9 → 1.10 → 2.6 |

---

## 五、学习节奏建议

### 每日学习量建议

- **精读（原子化Wiki）**：每天1-2个章节，配合动手实践
- **泛读（单文件Wiki）**：每天1-2篇，快速建立认知
- **复习**：每周花30分钟回顾本周所学，绘制知识点关联图

### 学习闭环建议

每个主题学完后，建议执行以下闭环：
1. **总结**：用自己的话写一段200字以内的核心要点
2. **关联**：思考这个主题与之前学过的主题有什么联系
3. **实践**：找一个小项目或练习应用所学知识
4. **复盘**：记录学习中的疑问和新发现，补充到个人笔记

---

> **提示**：本学习路径表与 [CATEGORIES.md](CATEGORIES.md)（分类体系说明）和 [README.md](README.md)（主题导航入口）配合使用效果最佳。
> 遇到不熟悉的术语时，可通过各Wiki中的"参考资料"章节追溯原始文档。
