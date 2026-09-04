---
version: "1.0"
---

# DeepSeek-V4 正式版免费方案深度调研 Spec

## Why

2026年8月12日深夜，DeepSeek 悄然上线 V4-Pro 正式版（版本号 DeepSeek-V4-Pro-0813），结束了4月预览版的测试阶段，转为正式商用。8月17日0时起，DeepSeek API 执行全新峰谷定价体系，高峰时段旗舰模型输出价格涨幅达350%，缓存命中输入涨幅高达1100%。

在 API 大幅涨价的背景下，用户对"DeepSeek 是否还免费"产生了大量疑问与焦虑。部分自媒体传播不实信息（如"79.9元会员"、"每日50次API调用限制"等），混淆了官方免费政策。同时，DeepSeek 采用"C端免费引流、B端API收费造血"的双轨商业模式，免费路径实际上包含三个层次：网页/App完全免费、新用户API赠送额度、开源模型自托管，用户难以全面了解。

本调研基于官方API文档、DeepSeek官网、多个权威新闻/分析来源（新浪财经、潮新闻、中新经纬、51CTO、CSDN、博客园、第三方定价分析平台等），系统性梳理 DeepSeek-V4 正式版免费方案的完整图景，澄清不实信息，为用户提供准确、全面、可操作的参考。

## What Changes

- **新增** 1个原子化wiki目录：`docs/knowledge/learning/07-vendor-product-learning/deepseek/`
- **新增** 调研总览（`00-overview.md`）：免费方案全景图、核心结论速览、三层免费路径对比
- **新增** 网页端与App免费使用详解（`01-web-app-free.md`）：功能范围、模型能力、使用限制（fair-use节流）、登录方式、支持特性
- **新增** API新用户免费额度详解（`02-api-free-tier.md`）：500万tokens赠送规则、有效期、适用模型、注册流程、额度消耗估算
- **新增** API峰谷定价与付费对比（`03-api-pricing-comparison.md`）：V4-Pro/V4-Flash峰谷价格表、缓存命中机制、与竞品价格对比、错峰使用建议
- **新增** V4-Pro正式版模型能力详解（`04-v4-pro-capabilities.md`）：技术规格、Agent能力跃升数据、三档推理模式、支持的API协议、基准测试成绩
- **新增** V4-Flash轻量模型详解（`05-v4-flash-capabilities.md`）：定位、规格、与Pro的差异、适用场景
- **新增** 开源模型自托管免费方案（`06-self-hosting.md`）：MIT开源协议、硬件需求、vLLM部署步骤、权重下载
- **新增** 第三方免费路径与注意事项（`07-third-party-free.md`）：OpenRouter免费层、HuggingFace推理、Kaggle/Colab试用额度、第三方工具风险提示
- **新增** 免费vs付费完整对比（`08-free-vs-paid.md`）：各维度对比表、适用场景建议、何时需要付费
- **新增** 常见问题与误区澄清（`09-faq-mythbusting.md`）：会员谣言澄清、API额度误解、网页限流解释、涨价影响范围
- **新增** 术语表（`10-glossary.md`）：≥15个核心术语的中英对照与一句话解释
- **更新** `07-vendor-product-learning/README.md` 导航（新增deepseek条目）
- **不修改** 任何现有文档内容（仅README追加导航条目）

## Impact

- **Affected specs**: 无（独立新增调研报告）
- **Affected code**: 无代码改动，仅文档新增
- **Affected files**:
  - 新增：`docs/knowledge/learning/07-vendor-product-learning/deepseek/00-overview.md` ~ `10-glossary.md` 共11个文件
  - 更新：`docs/knowledge/learning/07-vendor-product-learning/README.md`（追加子目录导航条目）

## Background & Context

### 关键时间线

1. **2026-04-23/24**：DeepSeek-V4 预览版发布（Pro/Flash双版本），初期定价被吐槽"涨价"
2. **2026-04-25**：V4-Pro限时2.5折特惠（输入/输出均降75%）
3. **2026-04-26**：缓存命中输入永久降至首发价1/10
4. **2026-07-31**：V4-Flash正式版（DeepSeek-V4-Flash-0731）上线
5. **2026-08-12深夜**：V4-Pro正式版（DeepSeek-V4-Pro-0813）无预告上线，同步预告API将大幅涨价
6. **2026-08-13**：DeepSeek发布API调价公告，引入峰谷分级计价
7. **2026-08-17 00:00**：新定价正式生效
8. **2026-08-13**：DeepSeek Harness (dsh) v0.1开发者预览版开源（MIT协议）

### V4-Pro 正式版核心规格

| 项目 | 规格 |
|------|------|
| 模型版本 | DeepSeek-V4-Pro-0813 |
| 架构 | MoE（混合专家），总参数1.6T，激活~49B |
| 上下文长度 | 1M（100万token） |
| 最大输出 | 384K token |
| 推理模式 | 非思考/Think High/Think Max 三档 |
| API协议 | OpenAI Chat Completions、Responses API、Anthropic API兼容 |
| 能力 | JSON Output、Tool Calls、前缀续写(Beta)、FIM补全(Beta) |
| 并发限制 | 500（可申请扩容） |

### 三层免费路径

1. **网页/App聊天（chat.deepseek.com）**：完全免费，无需付费，无会员计划，V4-Pro默认模型，支持文件上传/联网搜索/三档推理
2. **API新用户赠送**：注册即赠500万tokens（约30天有效），无需信用卡，覆盖V4-Pro和V4-Flash
3. **开源自托管**：V4-Flash权重MIT协议开源，可下载至自有GPU部署运行，无调用限制

### 不实信息标记

- ❌ "79.9元/180元/299元个人会员套餐"——新浪看点某文章编造，官方无个人付费会员计划
- ❌ "每日50次API调用+每月100万tokens免费额度"——错误；实际为注册一次性赠送500万tokens，有效期约30天
- ❌ "网页端要收费了"——错误；官方多次明确普通用户网页/App继续完全免费

### 信息来源

1. https://api-docs.deepseek.com/zh-cn/quick_start/pricing/ — 官方中文定价文档（峰谷价格）
2. https://api-docs.deepseek.com/quick_start/pricing — 官方英文定价文档（美元基准价）
3. https://api-docs.deepseek.com/zh-cn/quick_start/rate_limit — 官方API限速文档
4. https://www.deepseek.com/ — DeepSeek官网首页
5. https://chat.deepseek.com/ — 官方聊天界面
6. https://platform.deepseek.com/ — 开发者平台
7. 潮新闻/中新经纬/新浪财经等多篇API涨价报道（2026-08-17/18）
8. 博客园V4-Pro正式版技术拆解（cnblogs.com/vibecodinghuanzhe）
9. CSDN多篇V4 Pro 0813版本分析（2026-08-13/14）
10. 51CTO免费额度深度分析（2026-06-06）
11. apidog.com免费路径完整指南（2026-04-24）
12. costgoat.com定价计算器（2026-08-02更新）
13. geotoolbox.ai定价分析（2026-08-08更新）
14. grabon.com优惠券/赠送额度汇总

## ADDED Requirements

### Requirement: 调研总览文档

The system SHALL provide a `00-overview.md` file containing the complete free plan overview.

#### Scenario: 用户快速了解免费方案全貌

- **WHEN** 用户打开 `deepseek/00-overview.md`
- **THEN** 文档包含：核心结论速览（3条关键信息）、三层免费路径对比表（网页/App vs API赠送 vs 开源自托管）、文档导航表、适用人群推荐、信息更新时间标注

### Requirement: 网页端与App免费使用详解

The system SHALL provide a `01-web-app-free.md` file covering web and app free usage details.

#### Scenario: 普通用户了解如何免费使用DeepSeek

- **WHEN** 用户阅读本章
- **THEN** 文档包含：访问入口（chat.deepseek.com）、登录方式（手机号/微信/邮箱）、默认模型（V4-Pro）、可用功能清单（文件上传/PDF/图片/代码/联网搜索/三档推理/对话历史/文件夹）、fair-use限流说明（重新生成/修改消息的软限制）、明确声明无付费会员计划、高峰期可能的软节流说明

### Requirement: API新用户免费额度详解

The system SHALL provide a `02-api-free-tier.md` file covering API free tier details.

#### Scenario: 开发者了解API免费额度

- **WHEN** 用户阅读本章
- **THEN** 文档包含：赠送额度（500万tokens）、有效期（约30天）、适用模型（V4-Pro和V4-Flash）、无需信用卡、注册流程（platform.deepseek.com→Sign Up→API Keys）、扣费优先级（赠送余额优先）、额度消耗估算表（不同任务类型可调用次数）、免费阶段限速说明、额度用完后的处理（充值或暂停）

### Requirement: API峰谷定价与付费对比

The system SHALL provide a `03-api-pricing-comparison.md` file covering API pricing details.

#### Scenario: 用户理解免费额度用完后的付费成本

- **WHEN** 用户阅读本章
- **THEN** 文档包含：V4-Pro/V4-Flash峰谷价格表（缓存命中/未命中/输出三类，高峰/空闲两档）、峰谷时段定义（北京时间9:00-12:00、14:00-18:00为高峰）、上下文缓存机制说明、与竞品价格对比（GPT-5.5/Claude Opus/Gemini/Grok/Qwen）、错峰使用成本优化建议、缓存命中率优化技巧、企业级服务说明

### Requirement: V4-Pro正式版模型能力详解

The system SHALL provide a `04-v4-pro-capabilities.md` file covering V4-Pro capabilities.

#### Scenario: 用户了解V4-Pro正式版的能力边界

- **WHEN** 用户阅读本章
- **THEN** 文档包含：技术规格（1.6T MoE/49B激活/1M上下文/384K输出）、三档推理模式（Non-Think/Think High/Think Max）、Agent能力跃升数据（DeepSWE 12.8→62.7等）、API协议支持（OpenAI/Responses/Anthropic三协议）、基准测试成绩（SWE-bench/GPQA/HMMT等）、与预览版的差异、Codex/Claude Code兼容说明

### Requirement: V4-Flash轻量模型详解

The system SHALL provide a `05-v4-flash-capabilities.md` file covering V4-Flash details.

#### Scenario: 用户了解何时选择Flash而非Pro

- **WHEN** 用户阅读本章
- **THEN** 文档包含：版本（DeepSeek-V4-Flash-0731）、定位（高性价比轻量模型）、规格（同1M上下文/384K输出）、并发限制（2500，Pro的5倍）、价格优势（约为Pro的1/3）、适用场景（高吞吐/批处理/RAG/简单对话）、与Pro的能力差距量化

### Requirement: 开源模型自托管免费方案

The system SHALL provide a `06-self-hosting.md` file covering open-source self-hosting options.

#### Scenario: 技术团队了解自托管方案

- **WHEN** 用户阅读本章
- **THEN** 文档包含：开源协议（MIT）、权重获取方式（HuggingFace下载命令）、硬件需求表（V4-Flash/V4-Pro的FP8/INT4最低配置）、vLLM部署示例命令、兼容OpenAI API格式、适用场景（合规/私有化/已有GPU资源）、成本分析（自有GPU vs API调用）

### Requirement: 第三方免费路径与注意事项

The system SHALL provide a `07-third-party-free.md` file covering third-party free options.

#### Scenario: 用户了解其他免费获取途径

- **WHEN** 用户阅读本章
- **THEN** 文档包含：OpenRouter免费层、Chutes免费层、HuggingFace推理端点、Kaggle/Colab/RunPod试用额度、各路径的限制说明（速率限制/额度上限/稳定性）、风险提示（第三方平台条款变更/隐私风险/封号风险）

### Requirement: 免费vs付费完整对比

The system SHALL provide a `08-free-vs-paid.md` file with comprehensive comparison.

#### Scenario: 用户决定是否需要付费

- **WHEN** 用户阅读本章
- **THEN** 文档包含：三维度对比表（网页免费/API免费额度/API付费/自托管）、各维度覆盖（功能/限制/成本/SLA/隐私/适用人群）、决策树（什么场景用什么方案）、成本估算示例（个人开发者/小团队/企业）

### Requirement: 常见问题与误区澄清

The system SHALL provide a `09-faq-mythbusting.md` file covering FAQs and myth-busting.

#### Scenario: 用户消除误解获得准确信息

- **WHEN** 用户查阅FAQ
- **THEN** 文档包含：≥12个常见问题，包括但不限于：是否有会员/网页端是否会收费/API免费额度是否每日刷新/涨价后DeepSeek还便宜吗/缓存命中为什么涨幅最大/网页端为什么提示操作次数上限/第三方工具安全吗/V4-Pro和V4-Flash怎么选/500万tokens能用多久/免费额度过期了怎么办/企业是否有免费方案/联网搜索是否免费；明确标注并驳斥不实信息

### Requirement: 术语表

The system SHALL provide a `10-glossary.md` file with glossary of terms.

#### Scenario: 初学者理解专业术语

- **WHEN** 用户查阅术语表
- **THEN** 文档包含：≥15个核心术语的中英对照与一句话解释，包括但不限于：Token/MoE/上下文窗口/缓存命中/峰谷定价/并发限制/FIM/Tool Calls/Responses API/Anthropic API/Thinking Mode/KV Cache/FP8/INT8/SWE-bench

## Data Sources

调研信息来源：

1. **官方一手来源**：
   - https://api-docs.deepseek.com/zh-cn/quick_start/pricing/ — 官方中文定价（峰谷价格，8月17日生效）
   - https://api-docs.deepseek.com/quick_start/pricing — 官方英文定价（美元基准价）
   - https://api-docs.deepseek.com/zh-cn/quick_start/rate_limit — 并发限制文档
   - https://www.deepseek.com/ — 官网首页公告
   - https://platform.deepseek.com/ — 开发者平台
   - https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash — 开源权重

2. **权威媒体报道**：
   - 潮新闻《DeepSeek API调价今日生效》（2026-08-17）
   - 中新经纬/新浪财经多篇API涨价报道（2026-08-17/18）
   - 新浪看点《DeepSeek的网页和App普通聊天的价格是多少》（官方声明无会员计划）

3. **技术分析来源**：
   - 博客园《DeepSeek V4 Pro 正式版发布，对标Fable5》（2026-08-13）
   - CSDN《DeepSeek V4 Pro 0813正式发布》（2026-08-13）
   - 51CTO《DeepSeek免费额度还够用吗？》（2026-06-06）
   - apidog.com《How to Use DeepSeek V4 for Free》（2026-04-24）

4. **第三方定价分析**：
   - costgoat.com DeepSeek API定价计算器（2026-08-02）
   - geotoolbox.ai DeepSeek Pricing分析（2026-08-08）
   - grabon.com优惠券汇总

<!-- changelog -->
<!--
- 2026-08-19 | initial | 初始版本，定义11章原子化文档的完整Requirements
-->
