---
type: review
title: "mini-SWE-agent → OKF 知识包对抗审查与门禁记录"
generated_at: "2026-11-10"
---

# 对抗审查与门禁记录

## 一、四视角审查

### 1. 事实溯源视角

| 检查项 | 结果 |
|---|---|
| 正文中的 Stars、创建时间、版本、许可证是否有 F 出处 | 通过（F-035 ~ F-038） |
| 正文中的类名、方法名、配置字段是否能在 v2.4.6 源码中找到 | 通过（`DefaultAgent`、`LocalEnvironment`、`BASH_TOOL`、`AgentConfig` 等均实读核对） |
| 是否把博客观点写成事实 | 通过；作者观点标“作者观点/作者判断”，如 F-013、F-023 ~ F-030、F-032 |
| 是否把 README 自述写成独立事实 | 通过；F-041、F-082 标“机构自述”，F-042、F-083 标“无量化基准” |
| 勘误是否在正文落实 | 通过；E-1 Stars、E-2 年份、E-3 API、E-4 tool-calling 均在对应文档改写 |
| 是否伪造知乎内容 | 无；F-090 明示不可达，正文未引用其观点 |

### 2. 结构规范视角

| 检查项 | 结果 |
|---|---|
| bundle 目录结构 | `index.md` + `log.md` + `concepts/` + `examples/` + `references/` |
| frontmatter 必填字段 | 通过；根 index 含 okf_version/type/title/description/tags/generated/verified/status/stale_after/sources |
| 子目录 index | `concepts/index.md`、`examples/index.md`、`references/index.md` 均含 toctree |
| 根 index toctree | 收录 concepts/index、examples/index、references/index、log |
| 事实双份登记 | 通过；spec facts.md 90 条，bundle 两份 source 合计 90 条，集合相等且连续 |

### 3. 读者可用性视角

| 检查项 | 结果 |
|---|---|
| 阅读路径是否清晰 | 通过；根 index 给出 5 条路径 |
| 概念之间是否互链 | 通过；00→01→02→03→04→05→06→07 形成链路 |
| 主题关联是否可达 | 通过；6 个兄弟 bundle 链接逐一 Test-Path |
| 本 bundle 相对链接 | 0 断链（脚本逐条验证） |
| 示例是否标注执行边界 | 通过；三篇示例顶部与 examples/index 均标“未在本机实测” |

### 4. 时效边界视角

| 检查项 | 结果 |
|---|---|
| 是否锁定版本 | 通过；v2.4.6 / commit `04d809ce` / 2026-09-03 |
| 是否标注 Stars 时点 | 通过；2026-11-10 快照 |
| 是否标注 74% 口径 | 通过；F-088 与 06 篇均说明未公开完整配置 |
| 是否标注 v1/v2 边界 | 通过；01 与 04 篇均有对照表 |
| `stale_after` | 2027-03-31（仓库迭代快，半年复核） |

## 二、机械门禁

| 门禁 | 命令 | 结果 |
|---|---|---|
| 总索引对账 | `python scripts/check-bundles-index.py` | 通过：9 域 / 64 组 / 730 束，五面对账一致 |
| toctree | `python scripts/check-toctrees.py` | 通过：全部 index.md 引用有效，所有内容文档可达 |
| UTF-8 | `python scripts/check-utf8.py` | 通过：13,186 个文件均为有效 UTF-8 |
| F 编号双份一致 | 正则 `^\|\s*F-(\d{3})\s*\|` | 通过：spec 90 / bundle 90 / 无差集 / 1~90 无跳号 |
| 相对链接 | 逐条 Test-Path | 通过：0 断链 |
| 敏感路径 | 扫描 `C:\Users`、`D:\spaces`、`/Users/`、`file:///` | 通过：0 命中 |

## 三、审查意见与修正（≥5 条）

| # | 意见 | 修正 |
|---|---|---|
| 1 | 博客把 v1 的“无工具”写成现状，直接照抄会误导 | 01、04 篇增加 v1/v2 对照；E-4 单列；README 滞后写入 F-078 |
| 2 | 26k+ Stars 与实测差距过大 | E-1 勘误；00 篇统一用 9,496 |
| 3 | SWE-bench 年份错配 | E-2 勘误；00 篇时间线改为 2023 |
| 4 | 博客快速开始的 API 在 v2 不存在 | E-3 勘误；示例改用 `DefaultAgent` 真实代码 |
| 5 | 74% 容易被写成“框架能力” | F-088 + 06 篇明确“官方声明 + Gemini 3 Pro 单点 + 配置未公开” |
| 6 | 示例可能被误认为已实测 | 三篇示例与 examples/index 全部加执行边界声明 |
| 7 | 知乎信源不可达但用户要求覆盖 | F-090 + spec R-2 明示缺口，不虚构内容 |

## 四、结论

- 事实层：90 条事实可溯源，4 条硬勘误已落实，1 个信源缺口已披露。
- 结构层：三级 toctree 与计数全部通过机械门禁。
- 读者层：8 篇概念 + 3 篇示例形成“理解 → 动手 → 评测 → 迁移”的闭环。
- 时效层：锁定 v2.4.6，`stale_after=2027-03-31`，到期复核 v3 或新默认配置。
