---
type: facts
title: "free-claude-code 与 career-ops 事实登记"
source: "https://mp.weixin.qq.com/s/yEmCTdlwaKyj_h9eQRBsJg"
status: reviewed
---

# 事实登记

> R 阶段只记录可追溯陈述；“作者观点”与核验补充分别标注。P0 包括数字、许可证、隐私和核心能力声明。

| 编号 | 事实 | 来源/证据等级 |
|---|---|---|
| F-001 | 文章标题为《GitHub 这周最炸俩项目，一个白送 13 亿 token，一个帮你把工作找了》。 | 微信文章，P2 |
| F-002 | 文章介绍的两个项目是 `free-claude-code` 与 `career-ops`。 | 微信文章，P2 |
| F-003 | 文章称 free-claude-code 本周新增“四千多”星，图片标注 `+4235`。 | 微信文章，P0；时间快照 |
| F-004 | 文章称 career-ops 一天新增“八百多”星，图片标注 `+855`，总星数约六万六。 | 微信文章，P0；时间快照 |
| F-005 | free-claude-code README 称每月有 13 亿以上免费 token，连接 50 个 ToS 友好 provider。 | 官方 README，P0 |
| F-006 | free-claude-code README 列出 10 个编码 Agent：Claude Code、Codex、Pi、OpenCode、Cline、Hermes、DeepSeek Harness、Grok Build、Muse Code、Aider。 | 官方 README，P1 |
| F-007 | free-claude-code 将请求路由到免费、付费、订阅或本地模型，并声明遵守 provider 条款。 | 官方 README，P1 |
| F-008 | free-claude-code 支持 provider 故障后的自动切换。 | 官方 README，P1 |
| F-009 | free-claude-code 的可选 RTK 集成声称最多减少 90% 的终端输出 token。 | 官方 README，P0；成效数字 |
| F-010 | free-claude-code 支持终端、桌面、IDE、Discord、Telegram 和浏览器会话。 | 官方 README，P1 |
| F-011 | free-claude-code 支持本地 Whisper 或 NVIDIA NIM 语音转录。 | 官方 README，P1 |
| F-012 | free-claude-code 声明其为独立开源项目，不属于 Anthropic；Claude 与 Claude Code 是 Anthropic 商标。 | 官方 README，P0 |
| F-013 | free-claude-code 的免费额度与限制由各 provider 控制，并可能变化。 | 官方 README，P0 |
| F-014 | career-ops README 将自身描述为把 AI 编码 CLI 变成求职指挥中心。 | 官方 README，P1 |
| F-015 | career-ops 支持职位评估、定制 PDF、招聘平台扫描、批处理与终端 dashboard。 | 官方 README，P1 |
| F-016 | career-ops 使用 A-F 结构化评分，并换算为 1.0–5.0 分。 | 官方 README，P1 |
| F-017 | career-ops 建议不要申请评分低于 4.0/5 的职位。 | 官方 README，P1 |
| F-018 | career-ops 会进行简历与职位描述的语义匹配，并可检查诈骗或 ghost job 风险。 | 官方 README，P1 |
| F-019 | career-ops 生成 ATS 友好的 PDF 简历、求职信和 recruiter 邮件草稿。 | 官方 README，P1 |
| F-020 | career-ops 支持 Greenhouse、Ashby、Lever、Wellfound 等招聘平台和公司招聘页。 | 官方 README，P1 |
| F-021 | career-ops 文档强调人类在环，不自动提交申请，最终提交由用户确认。 | 官方 README，P0 |
| F-022 | career-ops 将个人资料、投递记录和生成文件放在本地，并把相关文件加入 gitignore；AI CLI 调用仍会访问所选模型服务。 | 官方 README，P0 |
| F-023 | career-ops 作者公开称评估过 740 多个职位、生成 100 多份定制简历并获得 Head of Applied AI 职位。 | 作者 README/案例，P0；自述 |
| F-024 | career-ops 项目 README 标注 MIT 许可证。 | GitHub 仓库，P0 |
| F-025 | 微信文章称两个项目都是 MIT 协议。 | 微信文章，P0；career-ops 已核验，free-claude-code需以仓库许可证为准 |
| F-026 | 微信文章的核心组合叙事是：用 free-claude-code 降低编码 Agent 的模型访问成本，再运行 career-ops 进行求职筛选与材料生成。 | 微信文章作者观点，P2 |
| F-027 | 微信文章将这两个项目概括为“一个省钱、一个赚钱”的组合。 | 微信文章作者观点，P2 |
| F-028 | “全程不花一分钱订阅费”不是两个项目的独立保证，因为免费额度、API 调用和平台限制由外部 provider 决定。 | 核验推论，P0 |
| F-029 | 文章未提供可复现的固定版本、完整输入输出和安装后验证步骤，因此本 bundle 不设 `examples/`。 | 文章结构审查，P1 |
| F-030 | 文章中的星标、免费额度、provider 数量和节省比例均属于时间敏感或 provider 自述数据。 | 文章与官方 README，P0 |
