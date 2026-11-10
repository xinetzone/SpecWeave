---
type: tasks
title: "mini-SWE-agent → OKF 知识包任务清单"
generated_at: "2026-11-10"
---

# 任务清单

## R — 事实采集与核验

- [x] 抓取博客正文，登记标题、日期、设计哲学、基准表与快速开始。
- [x] 尝试抓取知乎文章三种入口，记录 403/404 信源缺口（F-090）。
- [x] 浅克隆官方仓库到 `external/dao/SWE-agent/mini-swe-agent`，锁定 commit `04d809ce`。
- [x] 阅读 `agents/default.py`、`environments/local.py`、`environments/docker.py`、`models/litellm_model.py`、`models/utils/actions_*.py`、`config/mini.yaml`、`run/mini.py`。
- [x] 阅读 docs/ 的 quickstart、usage、advanced、FAQ、v2 migration、control flow。
- [x] 抓取 GitHub API 元数据（stars/forks/license/language/created_at）。
- [x] 抓取 arXiv 2310.06770 摘要页，核对 SWE-bench 提交日期。
- [x] 登记 F-001～F-090 到 `facts.md`。
- [x] 记录 E-1～E-4 四条硬勘误与 F-088 口径边界。

## I — 知识拆分

- [x] 判定设 `examples/`（官方文档有可照做步骤；本机未执行，标注边界）。
- [x] 确定八篇概念文档与三层结构。
- [x] 确定落点 `jishu/ai/frameworks/ai-agent/mini-swe-agent/`。

## E — Bundle 生成

- [x] 先写 `references/blog-source.md`、`references/repo-source.md`、`references/verification.md`。
- [x] 写八篇 concepts。
- [x] 写三篇 examples。
- [x] 写 `concepts/index.md`、`examples/index.md`、`references/index.md`。
- [x] 写 bundle `index.md` 与 `log.md`。
- [x] 在 `ai-agent/index.md` 增加导航行与 toctree 条目。
- [x] 更新 `frameworks/index.md`、`ai/index.md`、`jishu/index.md`、`bundles/index.md`、`doc/index.md` 计数。

## V — 对抗审查与门禁

- [x] 事实溯源：正文数字/日期/类名/命令均有 F 编号。
- [x] 结构规范：frontmatter、toctree、相对链接。
- [x] 读者可用性：阅读路径与主题关联可达。
- [x] 时效边界：`stale_after=2027-03-31`，锁定 v2.4.6。
- [x] 双份 F 编号一致（90/90，连续）。
- [x] UTF-8 检查通过。
- [x] 本 bundle 相对链接 0 断链。
- [x] 本 bundle toctree 检查通过。
- [x] 全库 `check-bundles-index.py`：通过（730 束 / 9 域 / 64 组）。
- [x] 全库 `check-toctrees.py`：通过。

## C — 原子提交

- [x] 在 `projects/awesome-okf-xs` 子模块内显式列文件提交（25 个文件，`ca7bd277`）。
- [x] 在主仓库提交 spec（4 个文件，`453ce90f`）。
- [x] 在主仓库更新子模块指针（`e66efc7c`）。
- [ ] 不 push（用户未要求）。
