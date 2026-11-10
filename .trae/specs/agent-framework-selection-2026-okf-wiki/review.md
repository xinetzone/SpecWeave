# 对抗审查记录 — 2026 AI Agent 框架选型

## 审查范围

- 对象：`agent-framework-selection-2026` bundle（index + 5 concepts + 2 references + log）
- 方式：四视角审查 + 双份 F 编号比对 + 链接/计数/UTF-8 机械门禁
- 结论：**通过，status=stable**；1 项已确认勘误（LlamaIndex 1.0 年份）、2 项过度表述降级、1 项用户名单部分确认、1 项价格区间不可独立核验。

## 四视角意见

### 1. 事实溯源视角

| # | 意见 | 处置 |
|---|------|------|
| 1 | 原文称 LlamaIndex Workflows 1.0 于 2026-06-22 发布，但 PyPI 1.0.0 上传于 2025-06-25 | 新增 F-072 记录正确值；正文改为“1.0 实际于 2025-06 发布，原文年份有误”；verification 单列勘误 |
| 2 | 原文称 MAF 的 A2A 在 1.0 原生支持，官方公告写“A2A 1.0 support coming soon” | 降级为 ⚠️；正文写“MCP 原生，A2A 已有支持但 1.0 时仍在补齐” |
| 3 | 原文生产用户含 Replit，LangChain 官方客户页只列 LinkedIn/Uber/Klarna/Elastic/AppFolio | 标 ⚠️“5/6 官方页确认，Replit 仅博文单源” |
| 4 | “团队反馈不到一周上线”“一行代码切换模型”无出处 | 分别标 🏷️ 作者自述 / 厂商宣传；正文不写成事实 |
| 5 | “每 100 万 token 1~5 美元”过宽 | 保留为区间，标 ⚠️；说明随模型与档位变化，不用于预算精算 |

### 2. 结构规范视角

| # | 意见 | 处置 |
|---|------|------|
| 1 | 原文无安装/代码/实测流程，是否设 examples/ | 两问均为“否”，不设；在 index 与 spec 中说明 |
| 2 | 五个框架是否拆成五个 bundle | 否；单篇博文禁止新建多束，按“选型对比”单束承载 |
| 3 | 是否需要新建顶级分组 | 否；落 `ai-agent`，并在组内新增“框架选型与横向对比”小节 |
| 4 | frontmatter 是否齐全 | 补齐 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources |

### 3. 读者可用性视角

| # | 意见 | 处置 |
|---|------|------|
| 1 | 决策表是全文最有价值部分，不能被版本细节淹没 | 放在 concepts/04 开头，并回链 concepts/00 的一览表 |
| 2 | 读者可能拿“1.0 刚稳定”判断 LlamaIndex 成熟度 | 勘误 explicitly 说明其 1.0 已稳定一年半，成熟度高于原文暗示 |
| 3 | 需要与现有单框架束互链 | index“主题关联”链到 `microsoft-agent-framework`、`langchain-ai/langgraph`、`agent-runtime-protocol` |
| 4 | 相对链接深度易错 | 全部链接逐一 Test-Path；跨束链接只放在 index，避免 concepts 三层上跳 |

### 4. 时效边界视角

| # | 意见 | 处置 |
|---|------|------|
| 1 | 框架版本迭代快，stale_after 不能设太远 | 设 2027-01-31，并写“选型前以当前官方文档为准” |
| 2 | MAF 在 2026-10 已新增 Go 预览、连接器改为 Foundry 优先 | 新增 F-078，在 MAF 概念篇写“时点更新” |
| 3 | LlamaIndex 包已到 2.26.1，原文“1.0”已过时 | 在 LlamaIndex 概念篇注明最新版本与时点 |

## 机械门禁

- [x] 双份 F 编号一致：spec `facts.md` 与 bundle `references/article-source.md` 均为 F-001~F-081，连续无跳号
- [x] 三级 toctree：根 index 收录 concepts/index、references/index、log；子目录 index 收录全部内容文件
- [x] 相对链接：全部 Test-Path 通过，无 `file:///`
- [x] 计数同步：ai-agent 63、frameworks 97、ai 294、jishu 532、全库 727（工作树当前值，含并行新增束）
- [x] UTF-8 严格 roundtrip：全部新增/修改 .md 通过
- [x] 敏感路径零残留：无用户家目录绝对路径
- [x] 勘误落实：正文使用正确值（LlamaIndex 2025-06、A2A 待补齐），verification 单列

## 未采纳意见

- “把五个框架分别建束”：违反单篇博文最小变更原则，且内容体量不足以独立成束。
- “删除印度市场段落”：保留与选型相关的三条约束（人才/成本/数据保护），删除服务推销细节。
