# Spec —— Claude Agent SDK 生产级智能体构建指南 OKF Wiki

## 1. 目标

把 Stackademic 博文《Building Production AI Agents with Anthropic's Claude Agent SDK》转化为可溯源、可教学、可审计的 OKF v0.2 知识包，回答四个问题：SDK 是什么、怎么装与怎么跑、权限与 hooks 如何设护栏、生产落地与 SDK/raw API 的边界在哪里。

产出根目录：`projects/awesome-okf-xs/doc/bundles/jishu/ai/practice/`。

## 2. 信源与敏感度

| 项 | 结论 |
|---|---|
| 主源文 | https://stackademic.com/blog/building-production-ai-agents-with-anthropic-s-claude-agent-sdk |
| 访问控制 | 公开页面，无 token / 邀请码 / 内部域名 → 标准工作流 |
| 内容性质 | 第三方技术媒体对 Anthropic 产品发布的编译 + 快速上手解读 + 生产建议 |
| 信源距离 | 第三方综述（非厂商自宣、非作者一手实测）；产品事实回到 Anthropic 官方源核验 |
| 页面日期 | 2026-09-26（正文事件时点为 2025-09-29，见勘误 E-1） |
| 权威核验源 | Anthropic 官方新闻、官方工程文章、Agent SDK overview/quickstart/permissions/hooks、PyPI、npm、Claude Code model-config |
| 核验受限 | `platform.claude.com` 在核验环境返回 “App unavailable in region”；平台侧细节以 `code.claude.com` 文档与官方新闻为准 |

## 3. 骨架判定（操作可复现性两问）

1. 文章是否给出读者可照做的安装/配置/代码/调用/实测流程？**是（有限）**——给出 npm/pip 安装命令、API key 设置、最小 `query()` 代码与 7 项配置。
2. 这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？**否**——文章未给版本号、未展示运行结果、未给失败排查，代码片段不足以独立复现完整闭环。

结论：**不设 `examples/`**。将安装与最小 agent 代码收入 `concepts/01`，并显著标注“代码为博文/官方 quickstart 片段，未在本库环境实测”。骨架为 `index + concepts/ + references/ + log`。

## 4. 归属判定

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/practice` | ✅ 采用 | 该分类即“工程实践、方法论与行业洞察”，已含 `claude-model-selection`、`codex-agent-workflow-practices` 等博文核验/Agent 实践束，语义与先例同时吻合 |
| `jishu/ai/ecosystems/anthropic` | ❌ | 该目录是 Anthropic 官方仓库源码教程（python-sdk、claude-code、cookbooks 等）；本束是单篇第三方博文的生产实践解读，不是源码教程 |
| `jishu/ai/frameworks` | ❌ | 该分类是框架/代码库的源码或官方文档教程；本束不以 SDK 源码结构为主线 |
| `jishu/ai/learning` | ❌ | 该分类是体系化学习路径；本束是单篇发布解读 + 速查 |
| 新建分组 | ❌ | 单篇博文禁止新建分组 |

## 5. 三层知识拆分

| 层 | 内容 | 落点 |
|---|---|---|
| 事实层（What/When） | 发布日、更名、六项能力、与 Claude Code 的关系、四种接入方式 | `concepts/00-release-and-capabilities.md` |
| 操作层（How） | 安装、认证、最小 agent、7 项配置、版本快照与打包边界 | `concepts/01-quickstart-and-configuration.md` |
| 控制层（Guardrails） | 权限模式、allow/deny 规则、六步评估、PreToolUse hook、审计盲区 | `concepts/02-permissions-and-hooks.md` |
| 生产层（Operate） | 沙箱、日志、最小权限、权限边界测试、版本锁定、认证限制 | `concepts/03-production-hardening.md` |
| 选型层（Decide） | SDK vs raw API vs CLI vs Managed Agents、采用路径、失败模式 | `concepts/04-sdk-vs-raw-api-and-adoption.md` |
| 信源层 | 87 条 F 编号事实、P0 核验、勘误 E-1~E-4 | `references/article-source.md`、`references/verification.md` |

## 6. 质量门计划

| 门 | 检查项 | 通过标准 |
|---|---|---|
| G1 | 事实无因果推断 | `facts.md` 只登记源文明示内容、官方核验事实与显式标注的观点/建议；无“因为/所以/导致”式判断 |
| G2 | 洞察四元组 | 每篇 concept 具备“现象/机制/影响/适用边界”四要素 |
| G3 | 模式可迁移 | 权限六步评估、最小权限上线阶梯、SDK/raw API 决策树可迁移到其他 agent SDK |
| G4 | 行动项原子化 | `concepts/03` 的落地清单每项单一职责、可验证、有边界 |
| V 门 | 对抗有实质内容 | 四视角审查 ≥5 条具体意见，至少采纳 2 条；双份 F 编号集合一致 |

## 7. 交付物

1. bundle：`jishu/ai/practice/claude-agent-sdk-production/`（index + concepts×5 + references×3 + log）
2. 索引接入：`practice/index.md`、`jishu/ai/index.md`、`jishu/index.md`、`doc/bundles/index.md`、`doc/index.md`、`README.md` 计数同步
3. 门禁：`scripts/check-bundles-index.py`、`scripts/check-utf8.py`、`scripts/check-toctrees.py`、`scripts/check-frontmatter.py`（以仓库实际脚本名为准）
4. 双份 F 编号：本 spec `facts.md` 与 bundle `references/article-source.md` 集合一致、连续无跳号

## 8. 已知边界

- 页面日期与正文事件时点冲突，按 2025-09-29 的知识时点处理；页面日期作为源文元信息保留（E-1）。
- 文章建议的 `claude-sonnet-4-5` 在 2026-11-10 已非最新；正文保留原口径并加时效提示（E-2）。
- 文章“Python SDK 自动包含 CLI”有源码分发例外（E-3）。
- Darktrace 研究未能在核验环境独立定位，标“仅博文单源”（E-4）。
- 代码片段未在本库环境执行，不能声称“实测通过”。
- `stale_after` 设为 2027-01-31；模型与版本信息按 2026-11-10 快照登记。
