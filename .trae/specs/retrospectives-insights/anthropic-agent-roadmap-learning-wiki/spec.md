# Anthropic Agent 产品线路线图学习 Wiki 教程 Spec

## Why
Anthropic在Opus 4.8发布一周后，被TestingCatalog从代码引用和隐藏界面字符串中挖出至少六条重磅产品线——Conway永久在线智能体、Orbit主动助手、Operon科研平台、BugCrawl代码审计、文件级记忆系统、多语言语音模式，同时GPT-5.6也在悄悄内测。这标志着AI正在走出聊天框，从被动响应转向主动工作、永久在线、垂直专精的Agent生态时代。需要系统学习该网页内容并沉淀为一份结构清晰、通俗易懂的wiki教程，便于读者理解Anthropic的Agent战略布局和即将到来的AI工作流变革。

## What Changes
- 新增 wiki 教程文档 `docs/knowledge/learning/anthropic-agent-roadmap-wiki.md`，作为 Anthropic Agent 产品线路线图的系统性学习资料
- 文档包含目录导航系统，覆盖文章背景、Conway永久在线智能体、文件级记忆、Orbit主动助手、Operon科研平台、BugCrawl代码审计、生态护城河升级、GPT-5.6竞争、行业影响分析等核心内容
- 整理关键功能点、技术架构、产品定位与战略意义
- 提供内容三维评估（专业性/准确性/时效性）与个人洞察分析
- 汇总相关资源链接（原文、TestingCatalog原始爆料、相关产品页面）
- 在 `docs/knowledge/README.md` 知识库索引中登记新增的学习文档
- **BREAKING**: 无破坏性变更（纯新增文档）

## Impact
- Affected specs: 无（独立新增学习文档）
- Affected code:
  - 新增 `docs/knowledge/learning/anthropic-agent-roadmap-wiki.md`
  - 修改 `docs/knowledge/README.md`（追加索引条目）

## Background & Context
- **产品来源**: TestingCatalog从Claude代码引用和隐藏界面字符串中挖掘的未发布产品线
- **文章来源**: 微信公众号"新智元"
- **发布时机**: Opus 4.8发布一周后，Anthropic即将开启Agent生态爆发期
- **核心产品线**: Conway（永久在线Agent）、文件记忆、Orbit（主动助手）、Operon（生命科学）、BugCrawl（代码Bug审计）、语音/会议/安全生态升级
- **竞争态势**: OpenAI GPT-5.6传闻内测，Anthropic用Agent生态包围，OpenAI用高性能低成本模型突围，形成"恐怖平衡"
- **战略方向**: Anthropic定位自己是"智能公司而非编程公司"，目标是把AI从"搜索引擎替代品"变成"人类大脑外部协处理器"
- **原文来源**: https://mp.weixin.qq.com/s/e-cbArpf6-RShpjqBJWB5A?from=industrynews&color_scheme=light#rd

## ADDED Requirements

### Requirement: Wiki 教程文档主框架
系统 SHALL 提供一份 Markdown 格式的 wiki 教程文档，放置在 `docs/knowledge/learning/anthropic-agent-roadmap-wiki.md`，文档顶部包含完整的目录导航系统，所有章节通过锚点链接支持跳转。

#### Scenario: 用户打开文档导航
- **WHEN** 用户打开 `anthropic-agent-roadmap-wiki.md`
- **THEN** 文档顶部展示完整目录，覆盖概述与背景、Conway永久在线智能体、文件级记忆系统、Orbit主动助手、Operon科研平台、BugCrawl代码审计、生态护城河升级、GPT-5.6竞争分析、行业洞察与影响、内容评估、FAQ、资源链接等章节
- **AND** 每个目录条目是可点击的锚点链接，能跳转到对应章节

### Requirement: 文章背景与核心论点
系统 SHALL 在文档开篇阐述文章背景与Anthropic的核心战略定位：Opus 4.8发布一周后产品线曝光、六条产品线指向"Claude走出聊天框"、Anthropic内部名言"智能公司而非编程公司"、AI从聊天Bot向超级智能体生态转型。

#### Scenario: 读者理解战略背景
- **WHEN** 读者阅读文档的"概述与背景"章节
- **THEN** 能够理解六条产品线曝光的时机（Opus 4.8后一周）
- **AND** 知晓信息来源（TestingCatalog代码挖掘）
- **AND** 理解Anthropic的战略转型方向（走出聊天框→主动工作流接管）

### Requirement: Conway 永久在线智能体详解
系统 SHALL 详细讲解Conway产品的核心特性：
1. **定位**: 始终在线的常驻代理（Always-on Agent），拥有独立托管容器环境
2. **交互范式**: 告别对话框，独立侧边栏+专属工作台，不占用传统聊天界面
3. **扩展生态**: .EXT打包格式与插件帝国，侧边栏卡片/标签页切换，AI时代App Store时刻，跨代理复用插件
4. **触发机制**: Webhook唤醒与被动触发，公开URL接口，外部服务调用（服务器崩溃/订单/邮件）时云端惊醒，Chrome控制台+通知系统处理后发报告
5. **部署范围**: Claude Code、移动端、Web端全面登录
6. **限制**: 每位用户限一个Conway代理（控制算力消耗）
7. **竞争定位**: 对OpenClaw、Hermes等开源AI代理项目的直接反击

#### Scenario: 读者掌握Conway核心能力
- **WHEN** 读者阅读"Conway永久在线智能体"章节
- **THEN** 理解Conway"始终在线"的含义（独立容器、Webhook唤醒、云端常驻）
- **AND** 知晓.EXT扩展标准的战略意义（插件生态/App Store）
- **AND** 理解Webhook被动触发的革命性（无需用户Prompt，外部事件直接唤醒）
- **AND** 了解为什么限制每人一个代理（算力控制）

### Requirement: 文件级记忆系统详解
系统 SHALL 详细讲解Anthropic即将推出的记忆革命：
1. **现有痛点**: AI无记忆，扁平摘要（Flat Summary）机制在复杂项目中灾难性失效
2. **新方案**: 基于文件的记忆（File-based Memory），用户和AI代理能以文件形式结构化、分类、长期微调上下文
3. **记忆进化**: 随时间和互动不断优化记忆文件
4. **跨产品共享记忆层**: 网页聊天/Conway写代码/移动端语音共享同一个"大脑文件柜"
5. **记忆深度**: 不仅知道你是谁，还记得上周代码bug、上个月策划案数据
6. **类比**: AI终于拥有可沉淀的"潜意识"

#### Scenario: 读者理解记忆革命
- **WHEN** 读者阅读"文件级记忆系统"章节
- **THEN** 理解扁平摘要与文件记忆的本质区别（扁平vs结构化/分类/持久）
- **AND** 知晓跨产品共享记忆层的价值（统一大脑、全端一致体验）
- **AND** 理解"潜意识"类比的含义（记忆沉淀、无需每次重新教学）

### Requirement: Orbit 主动助手详解
系统 SHALL 详细讲解Orbit主动助手的核心逻辑：
1. **核心理念**: 在你不问的时候把答案准备好，从被动响应走向主动出击
2. **应用部署能力**: 深度整合日常生产力工具
3. **工具集成列表**: Gmail&日历、Slack聊天记录、GitHub代码库、Google Drive云端硬盘、Figma设计图
4. **后台运作**: 安静游走于软件之间，持续捕捉个性化见解
5. **使用场景示例**: 早上9点自动总结Slack群聊、结合财务报表草拟Gmail回复、弹窗提醒会议材料准备
6. **价值定位**: AI从"工具"蜕变为"搭档"

#### Scenario: 读者掌握Orbit主动能力
- **WHEN** 读者阅读"Orbit主动助手"章节
- **THEN** 理解"主动"与"被动"的本质区别（不等Prompt、提前准备、主动推送洞察）
- **AND** 知晓五大集成工具（Gmail/日历、Slack、GitHub、Drive、Figma）
- **AND** 能够描述早上9点的典型场景（Slack总结+邮件草拟+会议提醒）
- **AND** 理解Orbit如何让AI从工具变搭档

### Requirement: Operon 生命科学科研平台详解
系统 SHALL 详细讲解Operon垂直领域平台：
1. **定位**: 专为生命科学研究者打造的第四种桌面模式（与Chat/Code/Cowork并列）
2. **核心理念验证**: Anthropic是"智能公司而非编程公司"的最佳证明
3. **平台能力**:
   - 私密环境与项目会话（科研数据安全）
   - Plan与Auto模式（AI自主设计实验步骤）
   - 本地文件直接访问权限（抓取分析庞大数据集）
4. **适用场景**: CRISPR（基因编辑）筛选设计、单细胞RNA分析
5. **试点推测**: 可能已在顶尖科研机构秘密试点测试
6. **价值意义**: AI不仅写前端页面，更在微观世界破解生命密码

#### Scenario: 读者理解Operon垂直价值
- **WHEN** 读者阅读"Operon科研平台"章节
- **THEN** 理解Operon是第四种桌面模式（Chat/Code/Cowork/Operon）
- **AND** 知晓三大核心能力（私密环境、Plan/Auto模式、本地文件访问）
- **AND** 了解CRISPR和单细胞RNA分析两个重点应用场景
- **AND** 理解这验证了Anthropic"智能公司"的定位

### Requirement: BugCrawl 代码审计详解
系统 SHALL 详细讲解BugCrawl程序员工具：
1. **定位**: 完善代码代理领域布局，对标Claude Security但专注通用Bug而非安全漏洞
2. **入口位置**: Claude Code中独立入口，带"存储库选择器"
3. **贴心设计**: "高Token消耗警告"提示
4. **完整工作流五步**:
   1. 主动从GitHub、Jira或Linear提取Bug工单
   2. 在代码库中爬行定位问题
   3. 自动编写测试用例
   4. 修复代码并验证修复结果
   5. 持续监控代码后续部署
5. **影响**: 初级QA测试工程师的工作流将被大幅改变

#### Scenario: 读者掌握BugCrawl工作流
- **WHEN** 读者阅读"BugCrawl代码审计"章节
- **THEN** 理解BugCrawl与Claude Security的区别（通用Bug vs 安全漏洞）
- **AND** 能够完整复述五步工作流（工单提取→定位→写测试→修复验证→持续监控）
- **AND** 注意到"高Token消耗警告"的贴心设计
- **AND** 理解对QA岗位的潜在影响

### Requirement: 生态护城河升级详解
系统 SHALL 讲解Anthropic在生态细节上的四大升级：
1. **多语言无缝切换语音模式**: 一句话中间多语言无缝切换（仍基于TTS，每语种1-2个声音）
2. **会议笔记捕捉**: 类似Granola/Notion的原生智能会议记录与提炼服务
3. **全新改版Claude Security仪表盘**: 应对企业数据安全焦虑
4. **AI流利度记分卡**: 设置面板新增功能，直观显示AI驾驭能力段位
5. **搁置功能**: 像素风虚拟形象Avatar已被内部搁置，近期不会推出

#### Scenario: 读者了解生态升级
- **WHEN** 读者阅读"生态护城河"章节
- **THEN** 能够列出四项生态升级（多语言语音、会议笔记、安全仪表盘、流利度记分卡）
- **AND** 知晓Avatar功能已被搁置

### Requirement: GPT-5.6 竞争分析
系统 SHALL 客观分析OpenAI的反击：
1. **竞争格局**: 两家技术实力处于"恐怖平衡"，用户随最新发布来回切换
2. **GPT-5.6传闻**: 已开启灰度测试，Discord核心开发者社区有人看到输出
3. **Canvas路由**: OpenAI全新编程界面Canvas已在底层暗中路由给GPT-5.6测试
4. **三大核心特征**:
   - 性能抗衡Mythos级别模型（与Anthropic预期发布的神话级模型并驾齐驱）
   - 效率与成本极致压缩（更高Token效率、价格显著降低、价格战+高性能双管齐下）
   - 修复"AI感"废话（Slop问题，类似Sonnet 3.7的记忆与表达方式）
5. **战略对比**: Anthropic用丰富Agent生态包围，OpenAI用更强大便宜的底层模型暴力突围

#### Scenario: 读者理解竞争态势
- **WHEN** 读者阅读"GPT-5.6竞争分析"章节
- **THEN** 理解"恐怖平衡"的含义（两家咬得很紧，无绝对领先者）
- **AND** 知晓GPT-5.6三大核心特征（性能、效率成本、Slop修复）
- **AND** 理解双方战略差异（生态包围 vs 模型暴力突围）

### Requirement: 核心信息汇总表
系统 SHALL 整理六条产品线+生态升级+GPT-5.6的关键信息为表格形式，包含：产品线名称、核心定位、关键特性、战略意义、部署状态。

#### Scenario: 数据可快速查阅
- **WHEN** 读者查阅核心信息汇总表
- **THEN** 能够快速对比六大产品+生态+GPT-5.6的核心信息

### Requirement: 行业洞察与个人思考
系统 SHALL 提供深度分析章节：
1. **交互范式革命**: 对话框→工作台→永远在线，人机交互三次跃迁
2. **记忆层的重要性**: 从无记忆→扁平摘要→文件记忆→跨端共享，AI认知能力的进化路径
3. **主动vs被动**: Orbit代表的主动AI范式将重新定义人机协作关系
4. **垂直化趋势**: Operon/BugCrawl标志着Agent从通用走向垂直专精
5. **生态战争**: .EXT插件标准是Anthropic的App Store时刻，生态护城河决定长期胜负
6. **双雄争霸格局**: Anthropic（生态/Agent）vs OpenAI（模型/成本）的路线之争
7. **工作流变革**: 当AI主动思考、持久记忆、独立推进项目时，人类工作流的重新定位

#### Scenario: 读者获得深度洞察
- **WHEN** 读者阅读"行业洞察"章节
- **THEN** 能够从交互范式、记忆、主动AI、垂直化、生态、竞争格局、工作流七个维度理解本次变革的意义
- **AND** 获得可用于讨论和决策的深度观点

### Requirement: 内容三维评估章节
系统 SHALL 对网页内容进行三维评估：
1. **专业性**: 基于代码挖掘和界面字符串分析，信息来源具体（TestingCatalog），但属于未发布产品爆料，存在变动可能
2. **准确性**: 爆料来源可信（TestingCatalog有多次成功挖掘历史），但产品细节和发布时间可能调整；GPT-5.6信息来自社区传闻，可信度较低
3. **时效性**: 文章发布于2026年7月初（Opus 4.8发布一周后），信息较新，属于前沿动态
同时评估信息价值与潜在风险（未发布产品可能延期/取消）。

#### Scenario: 读者了解内容可信度
- **WHEN** 读者阅读"内容评估"章节
- **THEN** 能够从专业/准确/时效三个维度判断信息价值
- **AND** 知晓六条产品线是代码挖掘结果，非官方发布，存在变动风险
- **AND** 理解GPT-5.6信息属于社区传闻，需谨慎对待

### Requirement: FAQ 常见问题解答
系统 SHALL 提供 FAQ 章节，解答读者学习时可能遇到的常见问题。

#### Scenario: 读者疑问被解答
- **WHEN** 读者查阅 FAQ
- **THEN** 至少覆盖以下问题：六条产品线何时正式发布、Conway的Webhook如何使用、文件记忆与现有记忆功能的区别、Orbit与Claude Tag的关系、Operon普通用户能否使用、BugCrawl是否会取代程序员、.EXT插件标准何时开放、GPT-5.6是否真的存在、Anthropic与OpenAI谁会最终胜出、永久在线Agent的安全风险如何控制

### Requirement: 资源链接汇总
系统 SHALL 在文档末尾汇总所有相关资源链接，包括：原文链接、TestingCatalog原始爆料文章、X平台相关讨论、Anthropic官方产品页面、Claude Code相关资源。

#### Scenario: 链接有效可达
- **WHEN** 用户点击资源链接
- **THEN** 链接指向正确的资源页面
- **AND** 链接以 Markdown 标准链接格式呈现

### Requirement: 知识库索引登记
系统 SHALL 在 `docs/knowledge/README.md` 的学习类目下登记新增的 Anthropic Agent 路线图学习文档条目。

#### Scenario: 索引可发现
- **WHEN** 用户浏览 `docs/knowledge/README.md`
- **THEN** 能够在 learning 类目下看到 Anthropic Agent 路线图学习 wiki 的条目
- **AND** 条目包含文档标题与相对路径链接

## Non-Functional Requirements
- **NFR-1**: 文档语言使用标准现代汉语，逻辑严谨，对不同技术水平的读者友好
- **NFR-2**: 在适当位置引用原网页内容作为参考依据，区分已证实信息（代码挖掘）和传闻信息（GPT-5.6）
- **NFR-3**: 文档结构清晰，使用 Markdown 标准标题层级（H1/H2/H3）、列表、表格、引用块
- **NFR-4**: 文件命名遵循 kebab-case 纯英文规范（`anthropic-agent-roadmap-wiki.md`），通过 `python .agents/scripts/check-filename-convention.py` 校验
- **NFR-5**: 文档篇幅适中（预估 4000–6000 字），重点突出，避免冗余
- **NFR-6**: 客观呈现爆料信息的不确定性，不将传闻当作确定事实

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范，frontmatter 使用 YAML 格式
- **Business**: 基于公开爆料文章内容创建，明确标注哪些是代码挖掘信息、哪些是传闻、哪些是分析推测
- **Dependencies**: 网页内容已通过 defuddle 工具成功获取并解析

## Assumptions
- 读者对 AI Agent、Claude、大语言模型有基础认知
- 读者了解ChatGPT/Claude等主流AI产品
- 读者对AI行业发展趋势有兴趣

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: `docs/knowledge/learning/anthropic-agent-roadmap-wiki.md` 包含目录导航、背景概述、Conway详解、文件记忆、Orbit、Operon、BugCrawl、生态升级、GPT-5.6竞争、行业洞察、内容评估、FAQ、资源链接等完整章节
- **Verification**: `human-judgment`

### AC-2: Conway 永久在线智能体讲解完整
- **Given**: 用户阅读Conway章节
- **When**: 用户理解核心特性
- **Then**: 包含独立容器、工作台交互、.EXT插件标准、Webhook唤醒、部署范围、单实例限制、竞争定位七大要点
- **Verification**: `human-judgment`

### AC-3: 文件级记忆系统讲解清晰
- **Given**: 用户阅读记忆章节
- **When**: 用户理解记忆革命
- **Then**: 包含扁平摘要痛点、文件记忆方案、记忆进化、跨产品共享层、记忆深度、潜意识类比六个要点
- **Verification**: `human-judgment`

### AC-4: Orbit 主动助手场景具体
- **Given**: 用户阅读Orbit章节
- **When**: 用户理解主动范式
- **Then**: 包含核心理念、五大集成工具、早上9点典型场景、工具到搭档的蜕变
- **Verification**: `human-judgment`

### AC-5: Operon 与 BugCrawl 垂直产品讲解完整
- **Given**: 用户阅读垂直产品章节
- **When**: 用户理解垂直化趋势
- **Then**: Operon包含第四种桌面模式、三大能力、CRISPR/单细胞RNA场景；BugCrawl包含与Security区别、五步工作流、Token警告
- **Verification**: `human-judgment`

### AC-6: 四大生态升级与GPT-5.6分析完整
- **Given**: 用户阅读生态与竞争章节
- **When**: 用户了解护城河与竞争态势
- **Then**: 生态包含四项升级+Avatar搁置说明；GPT-5.6包含恐怖平衡、Canvas路由、三大特征、战略对比
- **Verification**: `human-judgment`

### AC-7: 行业洞察章节有深度
- **Given**: 用户阅读洞察章节
- **When**: 用户获得分析观点
- **Then**: 覆盖交互范式、记忆层、主动AI、垂直化、生态战争、双雄争霸、工作流变革七个维度
- **Verification**: `human-judgment`

### AC-8: 内容评估客观区分信息可信度
- **Given**: 用户阅读评估章节
- **When**: 用户判断信息可信度
- **Then**: 明确区分代码挖掘信息（可信度较高）与GPT-5.6传闻（可信度较低），标注产品变动风险
- **Verification**: `human-judgment`

### AC-9: FAQ 章节实用
- **Given**: 用户遇到疑问
- **When**: 用户查阅 FAQ
- **Then**: 至少 10 个常见问题被解答，覆盖发布时间、使用方式、功能对比、安全风险、竞争格局等
- **Verification**: `human-judgment`

### AC-10: 资源链接完整
- **Given**: 用户点击资源链接
- **When**: 用户访问链接
- **Then**: 包含原文、TestingCatalog爆料、X讨论、官方页面、Claude Code资源等链接
- **Verification**: `human-judgment`

### AC-11: 知识库索引已登记
- **Given**: wiki 文档创建完成
- **When**: 用户浏览 `docs/knowledge/README.md`
- **Then**: learning 类目下出现 Anthropic Agent 路线图学习文档条目
- **Verification**: `programmatic`

### AC-12: 文件命名规范合规
- **Given**: wiki 文档创建完成
- **When**: 运行 `python .agents/scripts/check-filename-convention.py`
- **Then**: `anthropic-agent-roadmap-wiki.md` 通过命名规范校验
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要在文档中加入 Mermaid 产品路线图或架构图来可视化产品线关系？（倾向：加入1张产品线全景图增强可读性）
- [ ] 是否需要在文档中加入与Claude Tag（之前发布的企业协作产品）的对比分析？（倾向：在Orbit章节简要对比，不单独开章节）
