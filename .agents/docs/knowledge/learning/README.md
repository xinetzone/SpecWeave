---
id: "learning-hub"
title: "Learning Wiki 知识库"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/README.toml"
---
# Learning Wiki 知识库

Learning Wiki 知识库——SpecWeave 项目的 AI 技术学习资料库，汇集 Agent 协议、工程方法论、平台工具、文档标记、多模态内容、商业趋势、厂商产品、系统基础设施八大主题的学习笔记与深度 Wiki。

## 📊 统计数字

| 指标 | 数值 |
|------|------|
| 总 Wiki 数 | 63 |
| 原子化 Wiki | 24 |
| 单文件 Wiki | 39 |
| 主题数 | 8（含 2 个厂商二级子目录）+ 1 个跨领域专题 |
| 文件总数 | ~309 |

## 🧭 快速导航

| 编号 | 主题名称 | 一句话描述 | Wiki 数量 | 入口链接 |
|------|----------|-----------|-----------|----------|
| 01 | Agent 协议与接口 | Agent 通信协议、Skills 开放标准、接口四层抽象、FFI/IDL 底层技术 | 9 | [01-agent-protocols-interfaces/](01-agent-protocols-interfaces/README.md) |
| 02 | Agent 工程方法论 | Harness/Headroom/Karpathy/LongCat 等工程方法论与 Prompt 模式 | 7 | [02-agent-engineering-methodology/](02-agent-engineering-methodology/README.md) |
| 03 | Agent 平台与工具 | Anthropic/TRAE/浏览器/安全/量化/翻译等各类 Agent 平台与工具 | 13 | [03-agent-platforms-tools/](03-agent-platforms-tools/README.md) |
| 04 | 文档与标记工具 | MyST Markdown、HTML 声明式更新、Python 构建工具 | 4 | [04-docs-markup-tooling/](04-docs-markup-tooling/README.md) |
| 05 | AI 多模态内容 | AI 短剧、3D 动画、音频生成、AI 配图、文本转 CAD | 6 | [05-ai-multimodal-content/](05-ai-multimodal-content/README.md) |
| 06 | 商业趋势分析 | AI 变现、国产模型对比、个人 IP 趋势、供应链风险分析 | 6 | [06-business-trends-analysis/](06-business-trends-analysis/README.md) |
| 07 | 厂商产品学习 | 向日葵远程控制系列、涂鸦 TuyaOpen AI-IoT、火山引擎系列产品 | 14 | [07-vendor-product-learning/](07-vendor-product-learning/README.md) |
| 08 | 系统与基础设施 | WSL 命令树架构与系统学习计划 | 2 | [08-systems-infrastructure/](08-systems-infrastructure/README.md) |
| - | 跨领域思维方法论 | 第一性原理思维方法（哲学/物理/商业跨领域） | 1 | [first-principles/](first-principles/README.md) |

> 详细的分类说明与边界定义见 [CATEGORIES.md](CATEGORIES.md)。

---

## 📂 各主题 Wiki 快速链接

### 01 Agent 协议与接口

| Wiki | 说明 | 链接 |
|------|------|------|
| Agent 通信协议完整教程（MCP/ACP/A2A/ANP） | 四层协议栈系统讲解，含 12 章原子化内容 | [agent-communication-protocols-wiki.md](01-agent-protocols-interfaces/agent-communication-protocols-wiki.md) |
| Agent Runtime Protocol | 生产级 Agent 运行时协议对象与八大维度解析 | [agent-runtime-protocol-wiki.md](01-agent-protocols-interfaces/agent-runtime-protocol-wiki.md) |
| Agent Skills 开放标准完整指南 | agentskills.io 官方规范全解，含 15 章原子化内容 | [agent-skills-open-standard-wiki.md](01-agent-protocols-interfaces/agent-skills-open-standard-wiki.md) |
| 国内 Skill/MCP 生态盘点 | 16 个品牌的 Agent 化浪潮全景 | [domestic-skill-mcp-ecosystem-wiki.md](01-agent-protocols-interfaces/domestic-skill-mcp-ecosystem-wiki.md) |
| Interface/API/ABI/Protocol 四层抽象 | 软件接口四层概念辨析（通用版，7 章） | [interface-api-abi-protocol-wiki/](01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/README.md) |
| Agent 视角 Interface 四层抽象 | Agent 语境下的 Interface/API/ABI/Protocol 深度解析（6 章） | [agent-interface-deep-dive/](01-agent-protocols-interfaces/agent-interface-deep-dive/README.md) |
| FFI 外部函数接口 Wiki | FFI 原理、多语言实现、使用场景（7 章） | [ffi-wiki/](01-agent-protocols-interfaces/ffi-wiki/README.md) |
| IDL 接口定义语言 Wiki | IDL 语法、主流规范、工具链、对比分析（9 章） | [idl-wiki/](01-agent-protocols-interfaces/idl-wiki/README.md) |
| TVM FFI Wiki | TVM 深度学习编译器 FFI 系统深度解析（16 章） | [tvm-ffi-wiki/](01-agent-protocols-interfaces/tvm-ffi-wiki/README.md) |

### 02 Agent 工程方法论

| Wiki | 说明 | 链接 |
|------|------|------|
| AI 四大工程概念演进 | Prompt → Context → Harness → Loop 范式演进 | [four-engineering-concepts-wiki.md](02-agent-engineering-methodology/four-engineering-concepts-wiki.md) |
| Harness Engineering 驾驭工程 | 阿里 Harness Engineering 系统教程（10 章原子化） | [harness-engineering-wiki.md](02-agent-engineering-methodology/harness-engineering-wiki.md) |
| Headroom 上下文压缩中间件 | 6 种压缩算法 + CCR 可逆机制（11 章原子化） | [headroom-context-compression-wiki.md](02-agent-engineering-methodology/headroom-context-compression-wiki.md) |
| Karpathy LLM 编程准则教程 | GitHub 61.6k 星项目四条准则完整教程（8 章原子化） | [karpathy-llm-coding-guidelines-tutorial.md](02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md) |
| LongCat-2.0 Agent 能力实测 | 美团 1.6T MoE 模型接入 Claude Code 实战（9 章原子化） | [longcat-agent-learning-wiki.md](02-agent-engineering-methodology/longcat-agent-learning-wiki.md) |
| DeepSeek DSpark 推理加速论文 | DSpark 推理加速论文深度解析 | [dspark-paper-wiki.md](02-agent-engineering-methodology/dspark-paper-wiki.md) |
| Vibe Coding 两大神级 Prompt | 第一性原理 + 对抗式审查双 Prompt 模式 | [vibe-coding-prompts-learning-analysis.md](02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md) |

### 03 Agent 平台与工具

| Wiki | 说明 | 链接 |
|------|------|------|
| Anthropic Agent 产品路线图 | Conway/Orbit/Operon/BugCrawl 等六条产品线解析 | [anthropic-agent-roadmap-wiki.md](03-agent-platforms-tools/anthropic-agent-roadmap-wiki.md) |
| Anthropic 金融服务 Agent 工具箱 | 华尔街 AI 金融 Agent 工具箱完整教程 | [anthropic-financial-services-wiki.md](03-agent-platforms-tools/anthropic-financial-services-wiki.md) |
| AReaL 2.0 自演进 Agent | 蚂蚁集团在线强化学习基础设施 | [areal-agent-rl-wiki.md](03-agent-platforms-tools/areal-agent-rl-wiki.md) |
| BrowserAct 浏览器自动化 Agent | 让 Agent 真正能操作浏览器的工具 | [browseract-wiki.md](03-agent-platforms-tools/browseract-wiki.md) |
| Claude Tag 企业协作工具 | 卡帕西称 LLM UI 第三次变革（8 章原子化） | [claude-tag-article.md](03-agent-platforms-tools/claude-tag-article.md) |
| EchoBird 百灵鸟桌面 Agent | Tauri+Rust 桌面 Agent 项目 | [echobird-wiki.md](03-agent-platforms-tools/echobird-wiki.md) |
| MopMonk 安全 Agent | MiniMax 安全 Agent + CyberGym 漏洞挖掘（7 章原子化） | [mopmonk-security-agent-wiki.md](03-agent-platforms-tools/mopmonk-security-agent-wiki.md) |
| Octo 明略科技多 Agent 协作平台 | Private AI 时代多 Agent 协作基础设施 | [octo-platform-wiki.md](03-agent-platforms-tools/octo-platform-wiki.md) |
| Open Code Review 代码评审工具 | 阿里开源 AI 代码评审工具（11 章原子化） | [open-code-review-wiki.md](03-agent-platforms-tools/open-code-review-wiki.md) |
| QuantDinger AI 量化交易平台 | 开源自托管 AI 量化交易全链路平台 | [quantdinger-ai-trading-wiki.md](03-agent-platforms-tools/quantdinger-ai-trading-wiki.md) |
| Rainman AI 翻译工具 | AI 翻译书工具教程（8 章原子化） | [rainman-translate-book-wiki.md](03-agent-platforms-tools/rainman-translate-book-wiki.md) |
| TRAE v3.3.74 版本发布笔记 | TRAE IDE 版本更新：Browser 配置聚合页、Windows MSSDK 接入 | [trae-v3-3-74-release-notes.md](03-agent-platforms-tools/trae-v3-3-74-release-notes.md) |
| The Agency 项目 | The Agency Agent 项目 | [the-agency-project-wiki.md](03-agent-platforms-tools/the-agency-project-wiki.md) |

### 04 文档与标记工具

| Wiki | 说明 | 链接 |
|------|------|------|
| HTML 声明式局部更新 | Chrome Declarative Partial Updates 能力解析 | [declarative-partial-updates-wiki.md](04-docs-markup-tooling/declarative-partial-updates-wiki.md) |
| ExecutableBooks MyST 指南 | MyST Markdown 生态与实践（7 章 + 示例） | [executablebooks-myst-guide-wiki.md](04-docs-markup-tooling/executablebooks-myst-guide-wiki.md) |
| MyST Markdown 完整教程 | 17 章 MyST Markdown 从入门到精通 | [myst-markdown-tutorial/](04-docs-markup-tooling/myst-markdown-tutorial/README.md) |
| scikit-build-core Python 构建 | CMake 驱动的现代 Python 构建工具（6 章） | [scikit-build-core-wiki/](04-docs-markup-tooling/scikit-build-core-wiki/README.md) |

### 05 AI 多模态内容

| Wiki | 说明 | 链接 |
|------|------|------|
| Agnes/Pavo AI 短剧创作平台 | 免费多模态 API + 一站式 AI 短剧工作流 | [agnes-pavo-creative-platform-wiki.md](05-ai-multimodal-content/agnes-pavo-creative-platform-wiki.md) |
| Anime.js + Three.js 3D 动画 | 前端 3D 动画适配器模式分析 | [animejs-threejs-adapter-analysis.md](05-ai-multimodal-content/animejs-threejs-adapter-analysis.md) |
| AudioX-Turbo 极速音频生成 | 4 步推理 + 6 种任务统一的 Anything-to-Audio | [audiox-turbo-audio-generation-wiki.md](05-ai-multimodal-content/audiox-turbo-audio-generation-wiki.md) |
| Ian 小嘿插图 AI 配图 | AI 配图 Skill 工具解析 | [ian-xiaohei-illustrations.md](05-ai-multimodal-content/ian-xiaohei-illustrations.md) |
| LibTV AI 短剧创作 | AI 短剧/漫画/3D 导演全流程工具 | [libtv-ai-shortdrama-wiki.md](05-ai-multimodal-content/libtv-ai-shortdrama-wiki.md) |
| Text-to-CAD 文本转 CAD | AI 驱动的 CAD 模型生成 | [text-to-cad-wiki.md](05-ai-multimodal-content/text-to-cad-wiki.md) |

### 06 商业趋势分析

| Wiki | 说明 | 链接 |
|------|------|------|
| AI 变现完整指南 | 从技术到商业全流程方法论（13 章原子化） | [ai-monetization-wiki/](06-business-trends-analysis/ai-monetization-wiki/README.md) |
| 国产 AI 模型对比与场景推荐 | DeepSeek/Kimi/MiniMax/GLM 四款模型深度对比 | [domestic-llm-comparison-notes.md](06-business-trends-analysis/domestic-llm-comparison-notes.md) |
| Papi酱个人 IP 创业趋势 | "把公司做小，把IP做大"趋势观察（9 章原子化） | [papi-jiang-solo-ip-trend-wiki.md](06-business-trends-analysis/papi-jiang-solo-ip-trend-wiki.md) |
| 七概念印度制造业供应链风险分析 | 基于七概念理论框架分析印度塔塔电子泄密事件（7 章原子化） | [seven-concepts-india-manufacturing-wiki/](06-business-trends-analysis/seven-concepts-india-manufacturing-wiki/README.md) |
| 三大 AI 工具分析 | 三大 AI 工具深度剖析 | [three-ai-tools-wiki.md](06-business-trends-analysis/three-ai-tools-wiki.md) |
| 火山引擎 KickArt 营销创作 | AI 营销创作平台分析 | [volcengine-kickart-marketing-creation-analysis.md](06-business-trends-analysis/volcengine-kickart-marketing-creation-analysis.md) |

### 07 厂商产品学习

#### 🌻 向日葵（Sunlogin）系列

以 [sunlogin-product-series-index.md](07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md) 为系列总入口。

| Wiki | 说明 | 链接 |
|------|------|------|
| 向日葵产品系列索引 | 系列总入口，含产品矩阵与导航 | [sunlogin-product-series-index.md](07-vendor-product-learning/sunlogin/sunlogin-product-series-index.md) |
| 贝锐 Oray AI 产品矩阵分析 | OrayClaw、龙虾、向日葵/蒲公英/花生壳/洋葱头全景 | [oray-ai-product-matrix-analysis.md](07-vendor-product-learning/sunlogin/oray-ai-product-matrix-analysis.md) |
| 向日葵开机盒子 | WOL 远程开机硬件深度分析（10 章原子化） | [sunlogin-bootbox-analysis.md](07-vendor-product-learning/sunlogin/sunlogin-bootbox-analysis.md) |
| 向日葵 USB 摄像头 SU1 | 400 万高清 + 双全向麦克风远程视频 | [sunlogin-camera-su1-wiki.md](07-vendor-product-learning/sunlogin/sunlogin-camera-su1-wiki.md) |
| 向日葵智能远控鼠标 | BM110/MM110 鼠标产品分析 | [sunlogin-mouse-bm110-mm110-analysis.md](07-vendor-product-learning/sunlogin/sunlogin-mouse-bm110-mm110-analysis.md) |
| 向日葵无网远控硬件系列 | 控控/Q 系列无网远控（11 章原子化） | [sunlogin-offline-hardware-wiki.md](07-vendor-product-learning/sunlogin/sunlogin-offline-hardware-wiki.md) |
| 智能插线板 P4/P1Pro 对比 | 两款智能插线板对比评测 | [sunlogin-p4-p1pro-comparison-wiki.md](07-vendor-product-learning/sunlogin/sunlogin-p4-p1pro-comparison-wiki.md) |
| 智能 PDU 电源管理 | 数据中心级 PDU 电源管理方案 | [sunlogin-pdu-hardware-wiki.md](07-vendor-product-learning/sunlogin/sunlogin-pdu-hardware-wiki.md) |
| 向日葵安全产品 | 远控安全产品体系 | [sunlogin-security-wiki.md](07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md) |
| 智能插座 | 向日葵智能插座产品 | [sunlogin-smart-socket-wiki.md](07-vendor-product-learning/sunlogin/sunlogin-smart-socket-wiki.md) |

#### 🔌 涂鸦（Tuya）系列

| Wiki | 说明 | 链接 |
|------|------|------|
| TuyaOpen 全面学习报告 | 跨平台 AI-IoT SDK 系统学习报告 | [tuya-open-learning-report.md](07-vendor-product-learning/tuya/tuya-open-learning-report.md) |
| TuyaOpen-dev-skills 学习笔记 | 硬件开发 AI Skills 仓库 | [tuyaopen-dev-skills-learning.md](07-vendor-product-learning/tuya/tuyaopen-dev-skills-learning.md) |
| TuyaOpen 目录学习路径 | LINUX 闭环到 AI 能力区实操路线 | [tuyaopen-folder-learning-path.md](07-vendor-product-learning/tuya/tuyaopen-folder-learning-path.md) |

#### 🌋 火山引擎（Volcengine）系列

| Wiki | 说明 | 链接 |
|------|------|------|
| ACEP 云手机 | 一站式云手机解决方案+四大能力+超低延时音视频 | [volcengine-acep-cloudphone-analysis.md](07-vendor-product-learning/volcengine-acep-cloudphone-analysis.md) |
| Mobile Use Agent 移动端 AI 智能体 | 云手机+豆包视觉大模型的企业级移动端 Agent，含 MCP 协议实践 | [volcengine-mobile-use-agent-analysis.md](07-vendor-product-learning/volcengine-mobile-use-agent-analysis.md) |

### 08 系统与基础设施

| Wiki | 说明 | 链接 |
|------|------|------|
| WSL CLI 命令树与架构 | 基于源码核实的 WSL CLI 命令树与四层架构 | [wsl-cli-and-architecture-wiki.md](08-systems-infrastructure/wsl-cli-and-architecture-wiki.md) |
| WSL 系统学习计划 | 4 周 WSL 系统学习路径 + 5 个实操练习 | [wsl-learning-plan.md](08-systems-infrastructure/wsl-learning-plan.md) |

### 跨领域思维方法论

> 不局限于 Agent 技术栈的通用思维方法与认知工具，可应用于所有知识工作场景。

| Wiki | 说明 | 链接 |
|------|------|------|
| 第一性原理知识档案 | 哲学起源+物理应用+商业案例跨领域系统化档案，含对抗性审查质量控制、术语表、时间线、方法论框架 | [first-principles/](first-principles/README.md) |

---

## 🛤️ 推荐学习路径

### 🟢 入门者推荐（从概念到实践）

1. **第一性原理思维方法** → [first-principles/](first-principles/README.md)——建立反类比、回归本质的思维基础（所有技术学习的元方法论）
2. **四大工程概念演进** → [four-engineering-concepts-wiki.md](02-agent-engineering-methodology/four-engineering-concepts-wiki.md)——建立 AI 工程全局认知
3. **Karpathy LLM 编程准则** → [karpathy-llm-coding-guidelines-tutorial.md](02-agent-engineering-methodology/karpathy-llm-coding-guidelines-tutorial.md)——养成正确的 AI 协作编程习惯
4. **Agent 通信协议（MCP/ACP/A2A/ANP）** → [agent-communication-protocols-wiki.md](01-agent-protocols-interfaces/agent-communication-protocols-wiki.md)——理解 Agent 互联互通的基础
5. **Vibe Coding 两大 Prompt** → [vibe-coding-prompts-learning-analysis.md](02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md)——掌握生成+验证双 Prompt 闭环

### 🔵 垂直领域推荐（按方向深入）

| 方向 | 推荐路径 |
|------|----------|
| **Agent 平台开发** | Agent Runtime Protocol → Agent Skills 开放标准 → 国内 Skill/MCP 生态 → BrowserAct/EchoBird/MopMonk 等具体平台 |
| **文档与知识工程** | MyST Markdown 完整教程 → ExecutableBooks MyST 指南 → HTML 声明式局部更新 |
| **AI 内容创作** | Agnes/Pavo AI 短剧 → AudioX-Turbo 音频生成 → LibTV AI 短剧 → Text-to-CAD |
| **商业化与创业** | AI 变现完整指南 → Papi酱个人 IP → 国产模型对比 → 火山引擎 KickArt |
| **金融/交易** | Anthropic 金融服务 → QuantDinger AI 量化交易 |
| **智能硬件/IoT** | 向日葵系列（产品系列索引入手）→ 涂鸦 TuyaOpen 系列 |

### 🟣 底层技术推荐（筑基方向）

1. **Interface/API/ABI/Protocol 四层抽象** → [interface-api-abi-protocol-wiki/](01-agent-protocols-interfaces/interface-api-abi-protocol-wiki/README.md)——建立接口分层的底层认知
2. **FFI 外部函数接口** → [ffi-wiki/](01-agent-protocols-interfaces/ffi-wiki/README.md)——理解跨语言互操作
3. **IDL 接口定义语言** → [idl-wiki/](01-agent-protocols-interfaces/idl-wiki/README.md)——掌握接口描述规范
4. **TVM FFI** → [tvm-ffi-wiki/](01-agent-protocols-interfaces/tvm-ffi-wiki/README.md)——深度学习编译器 FFI 实战
5. **WSL 系统架构** → [wsl-cli-and-architecture-wiki.md](08-systems-infrastructure/wsl-cli-and-architecture-wiki.md)——Windows/Linux 互操作底层

---

> 📋 详细的主题分类说明、边界定义和维护规范请参见 [CATEGORIES.md](CATEGORIES.md)。
