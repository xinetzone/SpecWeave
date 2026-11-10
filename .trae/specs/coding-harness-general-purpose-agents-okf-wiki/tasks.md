---
type: tasks
title: "Coding Harness → OKF 知识包任务清单"
generated_at: "2026-11-10"
---

# 任务清单

## R — 事实采集与核验

- [x] 抓取 Radar blip 正文，确认标题、日期、卷号、评级。
- [x] 抓取 Radar 首页，确认 Vol 35 / November 2026 与同簇 blip 评级。
- [x] 登记 F-001～F-047 到 `facts.md`。
- [x] 核验 Claude Agent SDK overview / hosting。
- [x] 核验 Codex SDK README / app-server README。
- [x] 核验 OpenCode SDK / server / permissions。
- [x] 核验 Pi SDK / CLI Integration / README。
- [x] 记录 E-1～E-4 四条口径勘误。
- [x] 标注单源边界（.NET 案例、token 成本、编码偏向）。

## I — 知识拆分

- [x] 判定不设 `examples/`（操作可复现性两问均否）。
- [x] 确定六篇概念文档与三层结构。
- [x] 确定落点 `jishu/ai/practice/coding-harness-general-purpose-agents/`。

## E — Bundle 生成

- [x] 先写 `references/article-source.md` 与 `references/verification.md`。
- [x] 写六篇 concepts。
- [x] 写 `concepts/index.md`、`references/index.md`。
- [x] 写 bundle `index.md` 与 `log.md`。
- [x] 在 `practice/index.md` 增加导航行与 toctree 条目。
- [x] 更新 `ai/index.md`、`bundles/index.md`、`doc/index.md` 计数。

## V — 对抗审查与门禁

- [x] 事实溯源：正文数字/机构名/日期均有 F 编号。
- [x] 结构规范：frontmatter、toctree、相对链接。
- [x] 读者可用性：阅读路径与主题关联可达。
- [x] 时效边界：`stale_after=2027-04-30`，OpenCode 版本边界。
- [x] 双份 F 编号一致（47/47，连续）。
- [x] UTF-8 检查通过。
- [x] 本 bundle 相对链接 0 断链。
- [x] 本 bundle toctree 检查通过。
- [x] 全库 `check-bundles-index.py`：通过（729 束 / 9 域 / 64 组）。
- [x] 全库 `check-toctrees.py`：通过（并发 bundle 补齐 log 后）。

## C — 原子提交

- [x] 在 `projects/awesome-okf-xs` 子模块内显式列文件提交（13 个文件，`d4fd88d4`）。
- [ ] 在主仓库提交 spec。
- [ ] 在主仓库更新子模块指针。
- [ ] 不 push（用户未要求）。
