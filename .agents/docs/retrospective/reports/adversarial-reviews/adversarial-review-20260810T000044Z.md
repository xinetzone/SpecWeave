---
id: "hermes-agent-learning-wiki-adversarial-review"
title: "Hermes Agent 学习 Wiki 教程 - 对抗审查报告（V 门）"
source: "spec.md（AC-1~AC-13 / NFR / checklist V 门）+ hermes-agent-wiki/ 13 个文件 + external/libs/hermes-agent 源码"
date: "2026-08-10"
status: "stable"
category: "learning"
tags: ["hermes", "adversarial-review", "v-gate", "quality-gate", "wiki"]
---

# Hermes Agent 学习 Wiki 教程 - 对抗审查报告（V 门）

本报告为对 `hermes-agent-wiki/`（README + 00~11 共 13 个文件）的**对抗审查（V 门）与质量门验证**结果，审查基准为 `spec.md` 的 AC/NFR 与本地源码 `external/libs/hermes-agent`。

## 一、多视角对抗审查意见（6 条）

| # | 视角 | 意见（文件/位置） | 采纳 | 理由 |
|---|------|-------------------|:----:|------|
| 1 | 魔鬼代言人 | **"唯一内置学习闭环的自进化 AI Agent"**（README L18、00-overview L17、L22）中的"唯一"是不可验证的绝对化营销断言，属夸大/过度自信风险 | **不采纳** | 系对官方 README 定位的准确转述，frontmatter `source` 已标注出处；学习 wiki 转述官方自称可接受，改写会削弱信息价值。已在报告中记录此表述为"官方自称"，供读者甄别。 |
| 2 | 新手视角 | **03-cli-commands L134-149 `quick_commands` 示例**中 `target: /gmail unread` 会让新手误以为 Hermes 内置 `/gmail` 命令 | **采纳** | 已在 03 章示例后加注：`/gmail` 为演示用用户自定义命令，需自行定义后才能用，防止新手误解。 |
| 3 | 开发者视角 | **02-quickstart L87 示例 `hermes config set OPENROUTER_API_KEY sk-or-...`** 把 API 密钥作为配置项写入 config，与 04 章"密钥只进 `.env`、`config.yaml` 只放非密钥"的硬性设计矛盾 | **采纳** | 已修正：将密钥命令改为注释指引写入 `~/.hermes/.env`，消除跨章矛盾，符合 NFR-1 术语/规则统一。另验证 03 章 `COMMAND_REGISTRY`/`CommandDef`（`hermes_cli/commands.py`）与 `hermes -z`（`hermes_cli/_parser.py` L105）均与源码一致，命令描述准确。 |
| 4 | 维护者视角 | **平台数量内部不一致**：05-messaging-gateway 能力矩阵实际列出 28 个平台，但正文（L24）与 01/README 写"约 20"，10/11 章又写"25+" | **采纳** | 已统一为"约 28 平台"（以 05 章能力矩阵实际行数为准，标注"官方文档所列，持续扩张"），消除正文与表格矛盾，符合 G1 质量门事实一致性。 |
| 5 | 未来视角 | **10-architecture-source** 中"约 1.2 万行/约 1.1 万行/约 1.7 万测试/约 1,250 文件"等 LOC 统计会随版本漂移 | **采纳** | 已在 10.1 开头加版本提示"行数/测试数随版本演进变化，以仓库最新代码为准"，符合 NFR-4 版本提示要求。 |
| 6 | 维护者/未来视角 | **04-07 章 frontmatter 含 `x-toml-ref`，其指向的 `.meta/toml/.agents/.../*.toml` 文件当前不存在**（悬空引用）；且 00-03/08-11 章无此字段，frontmatter 不一致 | **不采纳（记录）** | `x-toml-ref` 为系统元数据约定（他处 README 亦有），指向的 toml 疑由后续流程生成，不宜移除；已在报告中记录待确认。 |

> 采纳 4 条（#2/#3/#4/#5），满足"≥5 条意见、≥2 条采纳"的 V 门要求。

## 二、已应用的修正清单

1. **AC-2（frontmatter 补齐）**：为 00~11 全部 12 个章节文件在 `status` 与 `author` 之间补入 `category: "learning"`、`tags: [...]`、`date`（04-07 用 `2026-08-09`，其余 `2026-08-10`，与各文件 `last_verified` 一致），与现有 wiki（okf-wiki / zleap-agent-wiki）及本目录 README 的 frontmatter 约定对齐。
2. **AC-12（断链修复）**：11-glossary-faq-resources L73 交叉引用 `../hermes-agent-integration/00-overview.md`（该文件不存在）→ 改为 `../hermes-agent-integration/README.md`（存在）。
3. **平台数量一致性**：05-messaging-gateway 正文/description/summary、01-core-features（标题+能力+小结表）、README 导航表的"约 20 平台"→"约 28 平台"。
4. **新手防误导**：03-cli-commands `quick_commands` 示例补注 `/gmail` 为演示命令。
5. **开发者视角矛盾**：02-quickstart 密钥命令改为写入 `.env` 指引。
6. **未来视角**：10-architecture-source 10.1 加 LOC 统计版本提示。

## 三、验收标准核对结果

| 验收项 | 结果 | 说明 |
|--------|:----:|------|
| AC-1 目录结构完整（README + 00~0X，8-11 篇） | ✅ | 13 个文件，命名 kebab-case |
| AC-2 frontmatter 含 id/title/source/description/tags/category/date/status | ⚠️→✅ | 修正前 00-11 缺 category/tags/date；**已补齐** |
| AC-3 产品定位与核心理念 | ✅ | 00/01 覆盖自进化、闭环学习、核心窄腰/能力在边缘 |
| AC-4 核心特性覆盖完整 | ✅ | 01 章七大特性 |
| AC-5 快速安装上手可实操 | ✅ | 02 章命令完整可复制，含"示例/需验证"标注 |
| AC-6 CLI 与斜杠命令覆盖完整 | ✅ | 03 章覆盖 hermes 子命令、/model、/skills、/compress、/new、COMMAND_REGISTRY |
| AC-7 配置体系阐述清晰 | ✅ | 04 章 config.yaml/.env/HERMES_HOME/profiles/优先级 |
| AC-8 网关/工具/技能/记忆覆盖 | ✅ | 05/06/07/08 章 |
| AC-9 MCP/cron/委派并行覆盖 | ✅ | 09 章 |
| AC-10 架构解析与源码导读 | ✅ | 10 章含代码/结构/Mermaid |
| AC-11 术语表/FAQ/资源完整 | ✅ | 11 章 |
| AC-12 交叉链接有效、相对路径、上级索引更新 | ⚠️→✅ | 修复 11 章断链；`../hermes-agent-integration/README.md`、`okf-wiki/README.md` 均存在；03-agent-platforms-tools/README.md 已含 hermes-agent-wiki 入口（L50） |
| AC-13 Mermaid 语法正确 | ✅（留意） | 08 章 flowchart LR、10 章 flowchart TB 语法有效；10 章 subgraph 使用中文 id（`subgraph 入口[...]`），主流渲染器支持 unicode id，建议留意渲染兼容性 |
| NFR-2 单文件 <300 行 | ✅ | 最大 03 章约 190 行 |
| NFR-5 相对路径、无 file:/// | ✅ | 检查全部交叉引用均为相对路径 |
| NFR-7 三级标题 x.y 编号 | ✅ | 各章 `##` 均按 x.y 从 x.1 编号（00 章 0.1~0.6 … 11 章 11.1~11.4）；`###` 细节标题与既有 wiki 约定一致不编号 |
| NFR-8 不虚构特性、命令有依据或标注"示例/需验证" | ✅ | 已验证 COMMAND_REGISTRY/-z 等命令有源码依据；不确定处已标注"示例/需验证" |

## 四、遗留风险与建议

- **`x-toml-ref` 悬空引用**（04-07 章）：指向的 `.meta/toml/.../*.toml` 尚未生成，建议由元数据生成流程补齐或确认该约定。
- **"唯一内置学习闭环"表述**：属官方自称，非独立验证事实；读者应知晓其营销属性。
- **Mermaid 中文 subgraph id**：建议在目标渲染器上做一次实际渲染确认。
- **版本演进**：Hermes 生态演进快，10 章 LOC 数字与 05 章平台矩阵均已加"以官方最新为准/持续扩张"标注，后续维护需同步刷新 `last_verified`。
