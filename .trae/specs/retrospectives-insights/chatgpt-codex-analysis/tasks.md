---
version: 1.1
created: 2026-07-08
updated: 2026-07-08
source: "https://chatgpt.com/zh-Hans-CN/codex/?openaicom_referred=true"
output_path: "docs/knowledge/learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/"
---

# ChatGPT Codex 产品页面深度洞察与Wiki教程 - The Implementation Plan (Decomposed and Prioritized Task List)

## Phase 1: 数据采集与分析（网页深度探索）

## [ ] Task 1: 网页内容深度采集与完整截图
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 使用浏览器工具完整浏览页面，滚动查看所有内容模块
  - 展开所有折叠菜单（功能、学习、Codex、商业应用下拉项）
  - 截取完整页面截图（fullPage）和关键区域截图（Hero区、功能模块区、定价区、集成区、页脚）
  - 提取页面所有文本内容、文案、按钮文字、标题层级、alt文本
  - 记录所有交互元素（链接、按钮、下拉菜单等）及其ref标识
  - 使用defuddle提取干净的markdown内容
  - 保存原始页面内容供后续分析使用
- **Acceptance Criteria Addressed**: [AC-2, AC-4, AC-5, AC-7]
- **Test Requirements**:
  - `programmatic` TR-1.1: 页面完整滚动，所有模块都被访问到，所有折叠菜单已展开
  - `programmatic` TR-1.2: 至少5张关键区域截图保存（Hero区、功能区、使用方式区、定价区、集成区）
  - `programmatic` TR-1.3: 完整提取页面所有可见文本内容，包括折叠菜单内容
  - `programmatic` TR-1.4: 使用defuddle提取干净markdown并保存
  - `human-judgement` TR-1.5: 截图清晰，能够辨认界面元素和文字内容
- **Notes**: 注意收集动态内容、hover状态提示、折叠菜单等隐藏内容；中文版本文案需完整提取

## Phase 2: Wiki文件编写（原子化单职责文件）

## [ ] Task 2: 创建Wiki目录结构与概述文件（00-overview.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 创建输出目录 `docs/knowledge/learning/07-vendor-product-learning/openai/chatgpt-codex-wiki/`
  - 编写 00-overview.md：
    - YAML frontmatter（id、title、source、x-toml-ref等）
    - 1.1 什么是ChatGPT Codex？产品简介
    - 1.2 为什么学习Codex产品设计？学习价值
    - 1.3 本Wiki教程结构与学习路径
    - 1.4 章节导航（链接到其他所有Wiki文件）
    - 1.5 阅读建议与前置知识
- **Acceptance Criteria Addressed**: [AC-11, AC-12]
- **Test Requirements**:
  - `programmatic` TR-2.1: 目录已在正确路径创建
  - `programmatic` TR-2.2: 00-overview.md包含完整YAML frontmatter
  - `human-judgement` TR-2.3: 概述清晰说明Codex是什么、为什么学、怎么学
  - `programmatic` TR-2.4: 章节导航包含所有其他Wiki文件的相对链接
- **Notes**: frontmatter格式参考项目中已有Wiki文件，如agent-skills-wiki/00-overview.md

## [ ] Task 3: 编写产品定位与价值主张（01-product-positioning.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 分析Hero区域核心文案（"你的 AI 工作助手"）
  - 解读副标题和宣传语（"从始至终，高效推进任务与项目落地"等）
  - 分析双轨定位策略（工作助手 + 代码助手）
  - 梳理核心价值支柱（任务自动化、多端协同、工具集成、团队协作）
  - 对比ChatGPT传统定位，分析从Chat到Work的演进逻辑
  - 提炼核心价值主张与差异化卖点
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 清晰阐述Codex的产品定位与核心价值主张
  - `human-judgement` TR-3.2: 分析双用户群体（办公+开发者）的设计逻辑
  - `human-judgement` TR-3.3: 提炼从对话AI到执行Agent的演进路径
  - `programmatic` TR-3.4: 引用页面原文作为分析依据
  - `programmatic` TR-3.5: 文件包含完整YAML frontmatter，单一职责聚焦定位分析
- **Notes**: 结合OpenAI产品战略背景理解定位；引用具体文案作为论据

## [ ] Task 4: 编写信息架构与导航设计（02-information-architecture.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 分析顶部主导航7个板块（简介/功能/学习/Codex/商业应用/定价/下载）的逻辑关系
  - 研究每个导航项的下拉菜单内容
  - 研究导航项的分组逻辑与用户路径设计
  - 分析页脚导航结构（OpenAI品牌区、研究/安全/API/新闻、条款政策区、社交媒体区、语言选择）
  - 研究锚点导航与滚动交互
  - 绘制信息架构图（Mermaid）
  - 分析页面内容区块的组织顺序与叙事逻辑
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-4.1: 完整列出所有导航项及其层级关系（含下拉菜单）
  - `human-judgement` TR-4.2: 分析导航设计背后的用户决策路径
  - `human-judgement` TR-4.3: 评价信息架构的合理性与可发现性
  - `programmatic` TR-4.4: 用Mermaid图呈现信息架构
  - `programmatic` TR-4.5: 文件包含完整YAML frontmatter
- **Notes**: 注意分析主导航的折叠/展开交互设计

## [ ] Task 5: 编写Hero区域与首屏转化策略（03-hero-conversion.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 分析首屏视觉构成（Logo、标题、副标题、CTA按钮、主视觉/演示图）
  - 研究主CTA按钮设计（位置、文案、颜色、大小）
  - 分析次CTA与辅助链接设计
  - 研究信任信号展示（企业Logo区位置与设计）
  - 分析首屏信息层级与视觉引导
  - 解读首屏转化漏斗设计
  - 分析"选择一个ChatGPT套餐即可开始使用"引导区
- **Acceptance Criteria Addressed**: [AC-1, AC-6]
- **Test Requirements**:
  - `programmatic` TR-5.1: 列出首屏所有UI元素及其位置关系
  - `human-judgement` TR-5.2: 分析视觉流设计与注意力引导策略
  - `human-judgement` TR-5.3: 评价CTA按钮设计的转化有效性
  - `programmatic` TR-5.4: 引用截图展示首屏布局
  - `programmatic` TR-5.5: 文件包含完整YAML frontmatter
- **Notes**: 首屏是转化关键，需重点分析CTA组合策略和信任信号位置

## [ ] Task 6: 编写核心功能模块解析（04-core-features.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 分析"使用 Codex 的方式"模块
  - 详细分析"为工作打造的Codex"模块：
    - 物流延迟调查场景（Gmail/Google Drive/Slack集成、调查摘要文档）
    - Stripe扣费调试场景（日志/截图/Slack讨论串/Linear工单、幂等性漏洞修复）
    - 任务管理场景（接下来/未读/已读三栏、状态追踪）
    - 团队周报自动化场景（GPT-5.5、自动化流程创建）
  - 详细分析"为开发者打造的Codex"模块：
    - 天气应用构建场景（Web界面提示输入）
    - 代码diff与测试添加场景（编辑器界面）
    - 终端深色模式场景（CLI界面）
  - 研究功能展示的叙事逻辑（痛点→方案→效果）
  - 分析演示截图/插画的信息密度与表达方式
  - 对比两大用户群体功能设计的异同
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 每个场景都有功能描述、痛点分析、价值解读
  - `programmatic` TR-6.2: 详细解读每个演示截图展示的功能点（共7个场景）
  - `human-judgement` TR-6.3: 分析功能展示的叙事结构与说服力
  - `human-judgement` TR-6.4: 对比两大用户群体功能设计的异同
  - `programmatic` TR-6.5: 文件包含完整YAML frontmatter
- **Notes**: 7个场景截图需逐一详细解读，这是功能分析的核心

## [ ] Task 7: 编写多端使用方式（05-multi-platform.md）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 分析四种使用方式：
    - Web界面（浏览器访问、主交互界面）
    - IDE集成（"在IDE中试用"按钮、支持的编辑器推测）
    - CLI工具（npm安装命令展示：`$ npm i -g @openai/codex`、代码块样式、复制按钮）
    - 桌面应用（"下载Windows版"按钮、多平台支持）
  - 研究每种方式的入口设计与展示顺序
  - 分析安装/启动引导文案
  - 研究多端协同策略与场景适配
  - 分析CLI命令展示设计（代码块样式、复制按钮、语法高亮）
  - 分析"在IDE中试用"的下拉菜单设计
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-7.1: 清晰列出四种使用方式及其入口
  - `human-judgement` TR-7.2: 分析多端策略背后的用户场景覆盖逻辑
  - `programmatic` TR-7.3: 记录CLI命令、下载按钮等关键交互元素
  - `human-judgement` TR-7.4: 评价开发者入口（CLI/IDE）的设计友好度
  - `programmatic` TR-7.5: 文件包含完整YAML frontmatter
- **Notes**: CLI命令代码块设计是开发者体验的重要细节，需重点分析

## [ ] Task 8: 编写工具集成生态（06-integration-ecosystem.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 分析连接器（Connectors）展示区域设计
  - 研究已集成工具列表（Linear、Notion已开启；Stripe、Figma显示连接按钮）
  - 从截图中识别更多集成工具（Gmail、Google Drive、Slack等）
  - 分析集成状态视觉设计（开关toggle vs 连接按钮）
  - 研究集成列表布局（图标+名称+简短描述+操作按钮）
  - 解读工具选择策略（生产力工具+开发工具混合）
  - 分析"详情请参阅开发者文档"链接的作用
  - 分析连接状态的视觉反馈设计（蓝色渐变背景、开关颜色）
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-8.1: 列出页面展示的所有集成工具及其状态（从截图和文案识别）
  - `human-judgement` TR-8.2: 分析集成生态的设计逻辑与扩展策略
  - `human-judgement` TR-8.3: 评价连接状态的视觉反馈设计
  - `programmatic` TR-8.4: 分析集成列表的UI组件设计模式（图标布局、开关样式、按钮样式）
  - `programmatic` TR-8.5: 文件包含完整YAML frontmatter
- **Notes**: 连接器是Agent产品的核心竞争力，需深入分析其设计模式

## [ ] Task 9: 编写定价体系与转化路径（07-pricing-strategy.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 分析三档定价结构：Plus、专业推理、Business
  - 解读每档定位文案：
    - Plus: "最适合进阶工作与高效办公"
    - 专业推理: "提供更高的使用上限，助力你在多个项目中高效完成整天的工作"
    - Business: "安全的共享工作空间，配备管理员控制与灵活定价，适合团队在多个代码仓库中使用Codex"
  - 研究价格锚点与档位对比设计
  - 分析CTA按钮文案（"获取Plus"、"获取Pro版本"、"试用ChatGPT Business"）
  - 解读Business档位的座位说明（"For 2+ seats, billed annually"）
  - 分析从免费到付费的转化路径设计
  - 分析顶部导航"联系销售团队"入口的企业转化路径
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `programmatic` TR-9.1: 清晰列出三档定价的定位、目标用户、核心权益文案
  - `human-judgement` TR-9.2: 分析定价分层逻辑与用户进阶路径
  - `human-judgement` TR-9.3: 评价价格展示与转化按钮设计
  - `programmatic` TR-9.4: 记录定价区域所有CTA按钮及其链接目标
  - `programmatic` TR-9.5: 文件包含完整YAML frontmatter
- **Notes**: 注意分析个人版与企业版不同的转化策略设计

## [ ] Task 10: 编写视觉设计与品牌语言（08-visual-design.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 分析配色系统：
    - 主色调（黑白为主的极简风格）
    - 品牌渐变色（蓝色→淡紫色渐变背景）
    - 强调色（CTA按钮、链接颜色）
    - 背景色与区块分隔
  - 研究字体层级与排版系统：
    - H1标题（大字号、粗体、"你的 AI 工作助手"）
    - H2/H3副标题（"使用 Codex 的方式"、"为工作打造的 Codex"等）
    - 正文与说明文字
    - 代码字体（CLI命令展示）
  - 分析空间系统与留白设计
  - 研究插画/截图风格（UI界面直接展示、渐变背景衬托）
  - 分析ChatGPT绽放标识（品牌Logo）的使用
  - 研究圆角、阴影、边框等UI细节
  - 分析微交互与动效线索（按钮hover、滚动动效等）
  - 分析深色/浅色模式（页面以浅色为主，终端截图展示深色模式）
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 系统总结配色方案与色彩心理学应用
  - `human-judgement` TR-10.2: 分析字体层级与可读性设计
  - `human-judgement` TR-10.3: 评价品牌视觉识别的一致性
  - `programmatic` TR-10.4: 用截图示例说明关键视觉元素
  - `programmatic` TR-10.5: 文件包含完整YAML frontmatter
- **Notes**: OpenAI的极简设计风格是重要学习点，需深入分析

## [ ] Task 11: 编写客户信任建立策略（09-trust-social-proof.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 分析企业客户Logo展示区（Cisco、Instacart、Duolingo、Vanta）
  - 研究Logo选择逻辑（行业分布：网络/零售/教育/安全；公司规模；品牌知名度）
  - 分析Logo展示的视觉设计（尺寸、排列、是否灰度、间距）
  - 研究是否有客户案例/证言（Testimonials）
  - 分析"了解更多"链接在信任建立中的作用
  - 解读开发者文档链接在技术可信度建立中的作用
  - 分析品牌标识（ChatGPT绽放标识）的信任强化作用
  - 分析页脚研究/安全/API链接的信任背书作用
- **Acceptance Criteria Addressed**: [AC-1, AC-6]
- **Test Requirements**:
  - `programmatic` TR-11.1: 列出所有展示的企业Logo及所属行业
  - `human-judgement` TR-11.2: 分析客户选择策略与社会证明设计
  - `human-judgement` TR-11.3: 评价信任信号在转化漏斗中的位置有效性
  - `human-judgement` TR-11.4: 分析多重信任信号（Logo+文档+品牌+安全链接）的协同效应
  - `programmatic` TR-11.5: 文件包含完整YAML frontmatter
- **Notes**: B2B产品信任建立是关键设计课题，需多角度分析

## [ ] Task 12: 编写可借鉴设计模式与最佳实践（10-design-patterns.md）
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10
- **Description**: 
  - 提炼产品定位模式：双轨用户策略（通用用户+专业用户，工作场景+开发场景）
  - 提炼信息架构模式：渐进式披露、分层导航、折叠菜单
  - 提炼转化设计模式：首屏CTA组合、信任信号前置、定价锚点、双转化路径（个人+企业）
  - 提炼功能展示模式：场景化演示、截图叙事、痛点-方案-效果结构、真实UI截图而非插画
  - 提炼多端策略模式：Web+IDE+CLI+桌面全场景覆盖、开发者友好入口设计
  - 提炼集成生态模式：连接器设计、开关/连接按钮双状态视觉反馈
  - 提炼视觉设计模式：极简黑白+品牌渐变、代码块展示设计、UI截图直接展示
  - 提炼文案模式：第二人称"你"、行动导向文案、价值驱动标题
  - 针对AI助手/Agent/开发者工具类产品给出具体可复用建议
  - 每个模式包含：模式名称、问题描述、Codex解决方案、应用场景、借鉴要点
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `human-judgement` TR-12.1: 至少提炼10个可复用的设计模式
  - `human-judgement` TR-12.2: 每个模式都有模式名称、问题描述、解决方案、应用场景
  - `human-judgement` TR-12.3: 给出对同类产品（AI助手/Agent/开发者工具）的具体借鉴建议
  - `programmatic` TR-12.4: 引用Codex页面的具体设计作为示例（截图或文案引用）
  - `programmatic` TR-12.5: 文件包含完整YAML frontmatter
- **Notes**: 这是Wiki教程最有价值的章节，需确保提炼的模式具有可操作性

## [ ] Task 13: 编写前端技术实现线索分析（11-technical-insights.md）
- **Priority**: low
- **Depends On**: Task 1
- **Description**: 
  - 观察页面渲染特征（SSR/CSR、hydration线索）
  - 分析响应式设计线索（断点、布局适配、移动端表现）
  - 研究性能优化特征（图片懒加载、代码分割、资源加载）
  - 分析交互实现方式（滚动监听、平滑滚动、动画效果）
  - 查看控制台消息与网络请求（如有明显特征）
  - 分析技术栈线索（React/Next.js等框架特征、CSS方案）
  - 分析折叠菜单、下拉菜单等交互组件实现
  - 分析i18n多语言实现线索
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-13.1: 基于可观察特征推断前端技术选型
  - `programmatic` TR-13.2: 记录响应式布局、动画等实现特征
  - `human-judgement` TR-13.3: 分析性能优化策略
  - `programmatic` TR-13.4: 文件包含完整YAML frontmatter
- **Notes**: 技术分析需基于可观察证据，不做无根据猜测

## [ ] Task 14: 编写多语言本地化策略（12-localization.md）
- **Priority**: low
- **Depends On**: Task 1
- **Description**: 
  - 分析中文版本的翻译质量与本地化程度
  - 研究技术术语的中文处理策略：
    - 保留英文：Codex、Plus、Pro、Business、Connector、IDE、CLI、npm
    - 翻译为中文：功能、学习、商业应用、定价、下载、登录
  - 分析文案长度变化对布局的影响（中英文长度差异）
  - 研究语言选择器设计（页脚位置、下拉交互、 globe图标）
  - 分析中文标点、排版习惯的适配
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-14.1: 评价中文本地化的质量与自然度
  - `programmatic` TR-14.2: 列出保留英文vs翻译为中文的术语示例（至少10个）
  - `human-judgement` TR-14.3: 分析多语言设计的技术实现线索
  - `programmatic` TR-14.4: 文件包含完整YAML frontmatter
- **Notes**: 中文本地化质量反映国际化策略，值得学习

## [ ] Task 15: 编写常见问题与开放问题（13-faq.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 整理页面中已有答案的常见问题
  - 列出开放问题（基于页面信息无法回答但用户可能关心的问题）：
    - Codex与ChatGPT的关系
    - CLI工具具体功能
    - IDE集成支持的编辑器
    - 连接器实现方式
    - Business管理员控制功能
    - 定价档位差异细节
    - 任务自动化触发方式
    - 团队协作功能形态
    - 中文本地化差异
    - 竞品对比
  - 对每个问题给出已知信息和待探索方向
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-15.1: 列出至少10个FAQ/开放问题
  - `programmatic` TR-15.2: 每个问题标注是页面已有答案还是开放问题
  - `human-judgement` TR-15.3: 问题覆盖产品、技术、定价、使用等多个维度
  - `programmatic` TR-15.4: 文件包含完整YAML frontmatter

## [ ] Task 16: 编写专业术语表（14-glossary.md）
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 收集页面出现的专业术语
  - 按类别分组（产品术语、技术术语、设计术语、商业术语）
  - 为每个术语提供：中文名称、英文原文、定义解释、出处/上下文
  - 术语应包含但不限于：Codex、ChatGPT、Connector（连接器）、Agent、IDE、CLI、npm、Plus、Pro、Business、工作空间（Workspace）、管理员控制、任务自动化、GPT-5.5、Linear、Notion、Stripe、Figma、Gmail、Slack、Google Drive等
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `programmatic` TR-16.1: 术语表包含至少20个相关术语
  - `programmatic` TR-16.2: 每个术语都有中文名称、英文原文、定义解释
  - `programmatic` TR-16.3: 术语按逻辑分类组织（产品/技术/设计/商业）
  - `programmatic` TR-16.4: 文件包含完整YAML frontmatter

## [ ] Task 17: 编写参考资源与延伸阅读（15-resources.md）
- **Priority**: low
- **Depends On**: Task 1
- **Description**: 
  - 整理页面中的所有链接资源：
    - 官方链接：登录、下载、联系销售、开发者文档
    - 社交媒体链接：X、YouTube、LinkedIn、GitHub、Instagram、TikTok
    - 政策链接：使用条款、隐私政策、使用政策、其他政策
    - OpenAI品牌链接：研究、安全、API、新闻
  - 提供延伸阅读建议：
    - OpenAI官方文档
    - Codex CLI npm包
    - 相关竞品分析方向
    - Agent设计相关资源
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-17.1: 完整列出页面所有外部链接（分类整理）
  - `human-judgement` TR-17.2: 提供有价值的延伸阅读建议
  - `programmatic` TR-17.3: 文件包含完整YAML frontmatter

## Phase 3: 质量保证与收尾

## [ ] Task 18: Wiki文件交叉引用与链接校验
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 15, Task 16, Task 17
- **Description**: 
  - 检查所有Wiki文件间的交叉引用是否正确
  - 确保所有相对路径符合项目规范（无file:///绝对路径）
  - 运行链接检查脚本验证无断链
  - 更新00-overview.md中的章节导航，确保所有文件链接正确
  - 确保每个文件的"相关阅读"或"下一章/上一章"导航正确
- **Acceptance Criteria Addressed**: [AC-13]
- **Test Requirements**:
  - `programmatic` TR-18.1: 所有交叉引用使用相对路径
  - `programmatic` TR-18.2: 运行链接检查无断链
  - `programmatic` TR-18.3: 00-overview.md导航包含所有16个Wiki文件的链接
  - `human-judgement` TR-18.4: 交叉引用逻辑合理，便于读者跳转学习

## [ ] Task 19: Wiki教程完整性与质量审核
- **Priority**: high
- **Depends On**: Task 18
- **Description**: 
  - 对照checklist.md逐项验证所有检查点
  - 检查每个Wiki文件是否遵循单一职责原则
  - 检查YAML frontmatter完整性
  - 检查Markdown格式规范（标题层级、列表、代码块、引用）
  - 通读整个Wiki教程，确保逻辑连贯、语言流畅
  - 确保关键论点有截图或原文引用支撑
  - 确保洞察有深度，不只是信息罗列
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-9, AC-10, AC-11, AC-12, AC-13]
- **Test Requirements**:
  - `human-judgement` TR-19.1: 对照checklist完成所有验证项
  - `programmatic` TR-19.2: 共16个Wiki文件全部创建完成
  - `human-judgement` TR-19.3: 教程整体质量达标，洞察深刻，结构清晰
  - `programmatic` TR-19.4: 无Markdown语法错误
