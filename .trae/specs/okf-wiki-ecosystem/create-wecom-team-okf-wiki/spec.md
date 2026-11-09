---
title: "WecomTeam 企业微信开源生态 OKF Wiki 教程 - 需求文档"
status: "draft"
id: create-wecom-team-okf-wiki
---

# WecomTeam 企业微信开源生态 OKF Wiki 教程 Spec

## Why

`vendor/WecomTeam/` 于 2026-11-09 引入 3 个 third_party 只读子模块（wecom-cli、wecom-unified、wecom-aibot-python-sdk），覆盖「CLI 运行时 / Skill 路由层 / 机器人协议 SDK」三个层次，但当前仅有一份 25 行的分组 README 与 VERSION.md 元数据，源码内部机制（schema 驱动命令树、双域文件沙箱、凭证加密与会话刷新、WS 心跳与串行回复队列、文件解密）无任何结构化中文文档。同时这三个子模块的工作树为空（目录内只有 `.git` 指针，索引中全部文件处于已删除状态），无法直接阅读。

需按 `source-code-to-okf-wiki` 工作流（阶段 0 信源稳定性门 + R→I→E→V→C 五阶段）与 `seven-concepts-cmd` 的「知识沉淀」链路，生成可溯源、零虚构 API 的 OKF v0.2 中文 Wiki 教程。

## What Changes

- **阶段 0（G0 信源稳定性门）**：用户已批准对 3 个子模块执行 `git reset --hard HEAD` 恢复工作树（不联网、不改 vendor 元数据、不切换 commit）。恢复后核验文件数（600 / 197 / 19）、HEAD commit（`1d48b6c` / `cae8a5b` / `6bcb59a`）与 `git status --porcelain` 为空；此三个 commit 即本次所有事实的唯一基线。
- **R 阶段（G1）**：逐仓库、逐模块阅读源码，产出编号事实清单（F-xxx），每条附 `路径:行号` 与可复跑取证命令，零推测、零因果词。
- **I 阶段（G2）**：每束提炼 ≥4 条四元组洞察（陈述 + 证据 + 反常识 + 行动），并设计「入门 → 机制 → 工程」的编号学习路径。
- **E 阶段（G3）**：在 `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/` 下新增 3 个知识束（每仓库一束），信源先行、每批 ≤7 文件、各级 `index.md` 最后写。
- **V 阶段（G4）**：独立验证——类名/方法名/常量 Grep 真实性、数量陈述机械复算、链接与 toctree 完整、frontmatter 齐全、门禁脚本全绿。
- **C 阶段（G5）**：在 3 束 `log.md` 中沉淀跨仓库「三层读法」模式与反模式；**不执行 git commit/push**（用户未要求）。
- **索引同步**：按机械真值更新 tencent 分组索引、ecosystems 索引、jishu/ai 索引、jishu 索引、`doc/bundles/index.md`，以及 `README.md`、`doc/index.md` 的规模数字（分组数不变，束数 +3）。
- 无 BREAKING 变更：不修改 vendor 源码，不重写既有 `wecom-5-0-10-release` / `wecom-5-0-12-release` / `wecom-topic-scenarios` 三束正文（仅允许补互链）。

## Impact

- Affected specs: `.trae/specs/okf-wiki-ecosystem/create-wecom-team-okf-wiki/`（本 spec 新增）
- Affected code:
  - `vendor/WecomTeam/wecom-cli`、`vendor/WecomTeam/wecom-unified`、`vendor/WecomTeam/wecom-aibot-python-sdk`（仅恢复工作树，源码只读）
  - `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/`（新增 `wecom-cli/`、`wecom-unified/`、`wecom-aibot-python-sdk/`）
  - `projects/awesome-okf-xs/doc/bundles/jishu/ai/ecosystems/tencent/index.md`、`.../ecosystems/index.md`、`.../jishu/ai/index.md`、`.../jishu/index.md`、`.../doc/bundles/index.md`、`README.md`、`doc/index.md`（计数与导航）
- 受影响 Skill：`source-code-to-okf-wiki`（方法论执行）、`seven-concepts-cmd`（知识沉淀链路编排）、`okf-atomize-migrate`（文档原子化边界）

## ADDED Requirements

### Requirement: 信源稳定性门（G0，R 阶段前强制）

系统 SHALL 在事实采集开工前恢复 3 个子模块工作树，并满足：

| 仓库 | 上游 | 固定基线 | 受控文件数 | 许可证 |
|---|---|---|---|---|
| wecom-cli | git@github.com:WecomTeam/wecom-cli.git | `1d48b6c9ecd1b4897c4bf728d564bfda1d62fbde`（npm `@wecom/cli` 1.3.4，无 tag） | 600 | MIT |
| wecom-unified | git@github.com:WecomTeam/wecom-unified.git | `cae8a5befac67d96bfe573b1675c5faab474758e`（无独立版本号） | 197 | MIT |
| wecom-aibot-python-sdk | git@github.com:WecomTeam/wecom-aibot-python-sdk.git | `6bcb59a9a636c566f4c6ea5268b228e3def1611a`（pyproject 1.0.1，无 tag） | 19 | MIT |

- **WHEN** 执行 `git -C <sub> reset --hard HEAD` 并检查状态
- **THEN** `git status --porcelain` 输出为空，`git rev-parse HEAD` 等于上表完整 hash，`git ls-tree -r HEAD --name-only` 计数分别为 600 / 197 / 19
- **THEN** 磁盘上 `wecom-cli/README.md`、`wecom-unified/skills/wecom-unified/SKILL.md`、`wecom-aibot-python-sdk/aibot/ws.py` 均可直接读取
- **THEN** 不执行 `git fetch` / `git pull` / 切换分支；`vendor/VERSION.md` 与 `vendor/WecomTeam/README.md` 元数据保持不变

#### Scenario: 恢复失败

- **WHEN** 在 SMB/UNC 路径上 `reset --hard` 因权限或文件系统语义失败
- **THEN** 保留已恢复的部分，改以 `git show HEAD:<path>` / `git grep <pat> HEAD` 取证，并在各束 `references/sources.md` 显著声明「工作树未检出 + 读取命令」，禁止把未取证内容写成事实

### Requirement: 事实采集（G1）

系统 SHALL 对 3 个仓库逐模块阅读源码，产出编号事实清单，写入各束 `references/facts.md`。

- **WHEN** 审查事实清单
- **THEN** `wecom-cli` ≥80 条、`wecom-unified` ≥50 条、`wecom-aibot-python-sdk` ≥45 条，编号 `F-001` 起连续无跳号
- **THEN** 每条含「事实陈述 + `路径:行号` + 取证命令」三要素，不出现「用于 / 目的是 / 设计为 / 为了」等推断性表述
- **THEN** 覆盖各仓库核心模块：wecom-cli 的 5 个 crate、13 个 service 域、15 个 skills、认证与配置、沙箱与传输；wecom-unified 的前置检查、14 个业务域、133 篇 references、6 个脚本、PPT 模板系统；aibot 的 9 个模块、WS 生命周期、帧协议、流式队列、模板卡片、文件解密

### Requirement: 架构洞察（G2）

系统 SHALL 为每束提炼 ≥4 条洞察，采用「陈述 + 证据（F 编号）+ 反常识 + 行动」四元组，并给出编号学习路径。

- **WHEN** 审查 `references/insights.md`
- **THEN** 每条洞察至少引用 2 条事实编号，反常识项须给出与直觉相反的机制解释，行动项须可执行
- **THEN** 各束 `concepts/index.md` 给出 `00 → NN` 的递进路径，并标注建议阅读顺序与前置依赖

### Requirement: OKF 文档生成（G3）

系统 SHALL 生成 3 个知识束，每束含 `concepts/`、`examples/`、`references/`、`index.md`（含 `okf_version` frontmatter）、`log.md`。

- **WHEN** 检查生成顺序与批次
- **THEN** `references/` 先于 `concepts/`、`examples/` 生成；单批写入 ≤7 个文件；各级 `index.md` 最后写且含 `{toctree}` 块；子目录 `index.md` 不带 frontmatter
- **WHEN** 检查 frontmatter
- **THEN** 每个非保留 `.md` 文件具备 `type / title / description / tags / generated / verified / status / stale_after / sources`，`sources` 指向本束已存在的 `references/` 文件
- **WHEN** 检查内容规模
- **THEN** wecom-cli = 8 概念 + 3 示例 + 4 信源文档；wecom-unified = 6 概念 + 3 示例 + 4 信源文档；aibot = 5 概念 + 3 示例 + 4 信源文档

### Requirement: 索引与计数同步

系统 SHALL 按机械真值更新五级导航与三处全局规模数字，且不出现跨文件矛盾。

- **WHEN** 运行 `python scripts/check-bundles-index.py`
- **THEN** 五面一致（frontmatter `total_bundles` / `groups` / `domains`、正文计数行、各域行、节标题、实际目录树）通过，束数 = 722 + 3，分组数保持 64，域数保持 9
- **WHEN** 检查 tencent 分组索引
- **THEN** 「知识包导航」新增 3 行、「关于本分组」的束数/概念/示例/信源/事实计数按实际值复算（19 → 22 束），并与 3 个既有企业微信束双向互链
- **WHEN** 检查全局文件
- **THEN** `README.md` 徽章与内容总览表、`doc/index.md` 规模段落、`doc/bundles/index.md` 的 jishu 行与节标题数字全部同步

### Requirement: 独立验证（G4）

系统 SHALL 对每束执行独立验证并输出验证结论，缺陷修复后重新验证。

- **WHEN** 对文档中出现的每个类名 / 方法名 / 常量 / 命令名在 vendor 源码执行 Grep
- **THEN** 零虚构 API；所有「N 个 / N 篇 / N 行」数量陈述经 Glob/Grep 独立计数一致
- **THEN** `python scripts/check-toctrees.py`、`python scripts/check-bundles-index.py`、`python scripts/check-asset-baseline.py` 全部 rc=0；如存在 `check-section-anchors.py` 亦须 rc=0
- **THEN** 束内交叉链接使用 `/` 开头的 bundle-relative 路径或相对路径，链接检查零断裂

### Requirement: 模式沉淀（G5）

系统 SHALL 在交付后回顾工作流，萃取可复用模式并登记，不擅自提交。

- **WHEN** 3 束 `log.md` 完成
- **THEN** 至少沉淀 1 条跨仓库模式（「运行时 → 路由层 → 协议层」三层读法）与 ≥3 条反模式
- **THEN** 不执行 `git add` / `commit` / `push`，交付物状态由用户确认后另行提交

## Non-Goals (Out of Scope)

- 不修改任何 vendor 源码（third_party 只读），不升级子模块 commit，不执行 fetch/pull
- 不编译 Rust、不安装 npm 包、不运行 CLI、不连接企业微信服务端（示例一律标注「未在本机实跑」）
- 不逐篇翻译 wecom-unified 的 133 篇 references（只做分类统计与代表性讲解）
- 不重写既有 `wecom-5-0-10-release` / `wecom-5-0-12-release` / `wecom-topic-scenarios` 三束正文
- 不新增分组、不新增学科域、不修改 OKF v0.2 规范本体
- 不生成英文文档、不构建可独立运行的可执行示例工程

## Constraints

- **Technical**：Windows + PowerShell，主路径为 UNC `\\10.16.11.3\ai\`；SMB 存在元数据缓存，计数以 `git ls-tree` 与门禁脚本为准；长路径需引号包裹
- **Business**：`projects/awesome-okf-xs` 为子模块，写入前遵循其 `AGENTS.md` 与 `.agents/rules/frontmatter.md`；vendor 区域改动遵从 `vendor/README.md` 治理说明
- **Dependencies**：`source-code-to-okf-wiki`、`seven-concepts-cmd` 两个 Skill 已装载；Python 3.14 环境用于门禁脚本
- **口径纪律**：wecom-cli `docs/skills.md` 与 `AGENTS.md` 称「14 个 Skill」而目录实际 15 个（含 `shared`）、aibot `__version__ = "1.0.0"` 与 pyproject `1.0.1` 不一致——一律并置登记，不择一、不抹平

## Open Questions

- [ ] 恢复工作树后若 SMB 产生大批权限位/行尾噪声，是否需要先做 `git-change-triage` 三分法归因再进入 R 阶段？（建议：是，只在子模块内执行，不触碰其他子模块）
- [ ] 3 束是否需要统一 `type` 大小写（`concept` 小写 vs 仓库既有大写 `Concept`）？（建议：跟随 tencent 分组既有大小写，束内自洽）