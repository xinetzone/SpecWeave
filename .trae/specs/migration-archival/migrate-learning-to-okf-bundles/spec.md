---
title: "docs/knowledge/learning 全量迁移至 OKF 知识包库"
status: "draft"
---

# docs/knowledge/learning 全量迁移至 OKF 知识包库 Spec

## Why

`docs/knowledge/learning/` 积累了 12 个分类、约 2124 个 Markdown 文件（含 10 个已成型 OKF 知识包）的学习笔记与 Wiki 教程，但游离于最高可信度知识库 `projects/awesome-okf-xs/doc/bundles/`（9 域/44 组/389 束）之外，形成双体系并存、内容重复（已识别 10 对明确重复、5 项部分重叠）、时效性无人维护的治理欠账。需要一次性完成调研、整理、迁移与收敛，删除源目录，消除双体系。

## What Changes

* **调研登记（R）**：对 learning/ 全部 2124 个 md 文件建立文件级事实台账（facts-ledger），逐主题登记内容概要、重复关系、时效敏感度，确保无遗漏

* **内容迁移**：将全部主题按映射表迁入 `projects/awesome-okf-xs/doc/bundles/` 的恰当域/组，遵循 OKF v0.2 frontmatter 规范（`type` 必填、派生物 `sources` 溯源）

* **重复收敛**：10 对已存在对应束的主题做内容比对合并（learning 侧独有内容回填对应束），不重复建束

* **时效核验**：对版本/定价/产品状态敏感主题执行 WebSearch 实时核验，过时内容更新或标注 `status: deprecated` + `stale_after`

* **隐私脱敏**：迁移前完成隐私扫描与脱敏——个人工作流元数据（retrospective/seven-concepts-report 中的 session ID、token 消耗、执行时间线、个人环境细节）不迁入公开知识库；迁入束的 log.md 重置为迁移事件日志；真实凭据（密码/API Key/私钥）格式扫描零容忍，占位符与官方示例白名单放行

* **洞察产出（I）**：产出迁移洞察报告（重复率、时效衰减、知识分布、治理建议）

* **对抗审查（V）**：独立子代理对迁移结果做无遗漏对账与内容保真审查

* **源目录删除**：迁移验证通过后删除 `docs/knowledge/learning/` 整目录，修复主仓库上游引用（`docs/knowledge/index.md` 等 toctree/链接）

* **索引与门控**：更新 `bundles/index.md` 五面计数，跑 `invoke gates.all` 三门全绿 + `sphinx-build` 零警告

* **原子提交（C）**：子模块内分批原子提交（add 与 commit 分离，防并行会话暂存区竞态），主仓库最后 bump 指针

## Impact

* Affected specs: 无（本变更为收敛性迁移，不改变既有束的知识内容语义）

* Affected code/docs:

  * `projects/awesome-okf-xs/doc/bundles/**`（新增/合并束、各级 index.md、bundles/index.md）

  * `docs/knowledge/learning/`（**整体删除**）

  * `docs/knowledge/index.md`、`docs/knowledge/README.md`（移除 learning 入口）

  * 主仓库 `docs/` Sphinx 构建 toctree

## 迁移原则

1. **内容保真**：正文语义不改写，仅做结构重组、frontmatter 转换、链接修正；合并重复束时以 bundles 侧为基线，learning 侧独有事实以增量章节回填并在 `log.md` 登记
2. **无遗漏**：文件级台账对账——迁移前后文件计数、主题清单双向核对，删除源目录前必须通过对抗审查对账
3. **单一可信源**：bundles 已有对应束的一律合并回填，不建影子束；okf-bundles/chaos 下 10 个已成型 OKF 包直接重定位（格式已合规，仅调路径与索引）
4. **实时性**：时效敏感主题（版本/定价/产品状态/Release Notes 类）迁移时执行 WebSearch 核验，核验结论写入该束 `log.md`；无法核验的保留原文并标注 `status` 与核验日期
5. **子模块纪律**：目标库是 git submodule——提交在子模块内完成；`git add` 与 `git commit` 分两次工具调用，中间核对 `git diff --cached --name-only` 防并行会话竞态；全部完成后主仓库 bump 指针
6. **门控强制**：每批迁移后跑 `invoke gates.toctrees`；全量完成后跑 `invoke gates.all` + `sphinx-build` 零警告；主仓库侧跑 `check-links.py` 与 Sphinx 构建

## 分类映射表（learning → bundles）

> 下表为规划映射，实施时可按内容实质微调，但任何新增域/组/束必须同步登记 `bundles/index.md` 并通过 `gates.bundles`。

| learning 分类                      | 目标域/组                                                                                                                                                                                                                                                                        | 处置要点                                                                                                                                                                        |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 00-essence-and-thinking          | `zhexue/`（新建组 `methodology` 收 first-principles）；boshu-laozi-wiki → 合并入 `guoxue/laozi/boshu-reading/`                                                                                                                                                                         | first-principles 无对应束，新建；boshu-laozi 为重复对 #1                                                                                                                                |
| 01-agent-protocols-interfaces    | `jishu/ai/`（agent 协议类）、`jishu/comm/`（ffi/idl/protobuf）                                                                                                                                                                                                                       | 重复对：agent-skills-wiki、graphql-wiki、okf-wiki（→meta/okf-spec）、protobuf-wiki；新建：ffi、idl、tvm-ffi、jira-skill、knowledge-catalog（→合并 meta/okf-spec）、okf-desktop                    |
| 02-agent-engineering-methodology | `jishu/ai/`（AI 工程方法论组）                                                                                                                                                                                                                                                       | 范式/提示词/上下文/评估/性能六板块整合为 1-2 束                                                                                                                                                |
| 03-agent-platforms-tools         | `jishu/ai/ai-agent/` 等                                                                                                                                                                                                                                                       | 重复对：agency-agents-wiki、deepseek-harness-wiki、codewhale；新建：eve、orca、okf-kit、open-code-review、quantdinger 及散文件主题                                                              |
| 04-docs-markup-tooling           | `jishu/document/`、`jishu/build/`、`jishu/python/`                                                                                                                                                                                                                             | 重复对：pyinvoke-wiki、scikit-build-core-wiki；myst 系两主题合并入 `jishu/document/myst/` 相关束；新建：mermaid、weasyprint、python314-stdlib；python314-cpython-wiki → 合并 `jishu/python/cpython/` |
| 05-ai-multimodal-content         | `jishu/ai/`、`jishu/viz/`                                                                                                                                                                                                                                                     | 全部新建：animejs-threejs-adapter、atomic-emergence、causal-ai、mainecoon、minit2i 及散文件主题                                                                                            |
| 06-business-trends-analysis      | `sheke/`（新建组 `industry` 产业趋势）                                                                                                                                                                                                                                                | 全部新建：ai-monetization、ai-switch-governance、douyin-vibecoding、ems-energy、rqndd、three-ai-tools、volcengine-ecosystem 等                                                          |
| 07-vendor-product-learning       | `jishu/ai/`（AI 厂商）、`jishu/iot/`（新建组，收 sunlogin/oray/tuya）、`sheke/workplace/`（okr-wiki）                                                                                                                                                                                       | baidu-ocr、deepseek 定价、volcengine 系、miaowu、openai-codex（与既有 openai-codex 束比对合并）、google-cloud→meta/okf-spec；okr-wiki 入 sheke/workplace                                        |
| 08-systems-infrastructure        | `jishu/`（新建组 `systems` 收 wsl/powershell/terminal/git）、conda-dev → 合并 `jishu/build/conda/`、caffe → `jishu/ml/`、cpython-devguide → 合并 `jishu/python/cpython/`                                                                                                                  | github-cli、git-baidu-sync、ai-powershell5-hell、intelligent-terminal、wsl 等新建                                                                                                  |
| 09-ml-inference-deployment       | `jishu/ml/`                                                                                                                                                                                                                                                                  | onnx-wiki 与既有 `jishu/ml/onnx/` 组比对合并回填                                                                                                                                      |
| 10-foundational-knowledge        | `kexue/math/`（勾股定理）、`sheke/`（学术写作，入 `workplace` 或新建 `academic`）、python314-cpython-wiki → 合并 `jishu/python/cpython/`                                                                                                                                                          | 注意与 04 的 python314-cpython-wiki 同名目录去重                                                                                                                                      |
| okf-bundles/chaos（10 个已成型 OKF 包） | 直接重定位：ai-agent-skills→`jishu/ai/`、apache-tvm→`jishu/ml/`、english-grammar→`wenxue/`（新建组 `english`）、home-assistant→`jishu/iot/`、laozi-lineage→`guoxue/laozi/`、mobile-use→`jishu/ai/`、okf-ecosystem→`meta/`、tiktoken→`jishu/ai/`、tuya-iot→`jishu/iot/`、veadk-python→`jishu/ai/` | 格式已合规，仅迁移路径+登记索引+toctree 接线；chaos 根级 4 个元文件（CROSS\_BUNDLE\_REVIEW 等）归入 `meta/` 或对应束 references                                                                              |

## ADDED Requirements

### Requirement: 文件级迁移台账

系统 SHALL 在迁移前生成覆盖 learning/ 全部 md 文件的台账（路径、所属主题、目标束、处置类型：新建/合并/直迁/删除），作为无遗漏验收的唯一对账依据。

#### Scenario: 台账完整性

* **WHEN** 台账生成完成

* **THEN** 台账条目数等于 learning/ 实际 md 文件数（约 2124，以实测为准），每个条目有明确处置类型与目标位置

### Requirement: 内容迁移与合并

系统 SHALL 按映射表将每个主题迁移为合规 OKF 束（或合并入既有束），每个非保留 `.md` 含可解析 frontmatter 与非空 `type`，派生物含 `sources` 溯源，束根含 `index.md`（toctree 接线）与 `log.md`。

#### Scenario: 重复主题合并

* **WHEN** 处理 10 对重复主题之一

* **THEN** 以 bundles 侧束为基线，learning 侧独有内容回填为增量章节，`log.md` 登记合并事件，不新建影子束

#### Scenario: 已成型 OKF 包重定位

* **WHEN** 迁移 okf-bundles/chaos 下的包

* **THEN** 文件内容零改写，仅调整存放路径、登记上级索引、接入 toctree

### Requirement: 时效性核验

系统 SHALL 对时效敏感主题（版本/定价/产品状态/Release Notes）执行 WebSearch 实时核验，核验结论（核验日期、来源、结论）写入对应束 `log.md`；确认过时的内容标注 `status: deprecated` 或 `stale_after`。

#### Scenario: 定价类内容核验

* **WHEN** 迁移 deepseek 定价、volcengine 产品等时效敏感束

* **THEN** 该束 `log.md` 含 2026-09 核验记录，过时数据已更新或显式标注过时

### Requirement: 隐私脱敏

系统 SHALL 在迁移前完成隐私扫描与脱敏，确保迁入公开知识库（bundles）的内容不含个人工作流元数据、隐私信息与真实凭据。

#### Scenario: 工作流元数据文件处置

* **WHEN** 迁移含个人工作流元数据的文件（12 个 retrospective、17 个 seven-concepts-report、37 个 log.md 中的个人操作历史）

* **THEN** retrospective/seven-concepts-report 类过程元数据文件不迁入 bundles（台账登记为“低价值舍弃-隐私元数据”）；迁入束的 log.md 重置为迁移事件日志（仅记录本次迁移）；正文中残留的 session ID、token 消耗、执行时间线、个人环境细节（IDE/设备/路径习惯）在迁移时剔除

#### Scenario: 占位符与公开信息保留

* **WHEN** 内容为教程占位符（`sk-xxxx`、`C:\Users\<你>`）、厂商公开联系方式、开源项目署名

* **THEN** 原样保留，不做脱敏（脱敏会破坏教程价值）

#### Scenario: 脱敏复查

* **WHEN** 对抗审查阶段

* **THEN** 独立子代理对迁入内容复扫隐私模式（个人标识/凭据格式/第一人称私人叙事/工作流元数据），确认零残留

#### Scenario: 真实凭据零容忍

* **WHEN** 每批迁移完成与最终审查阶段

* **THEN** 对迁入内容执行真实凭据格式扫描（GitHub `ghp_/gho_/github_pat_`、OpenAI/Anthropic `sk-ant-/sk-proj-` 及长熵 `sk-`、AWS `AKIA/ASIA`、Slack `xox`、Google `AIza`、PEM 私钥块、JWT、URL 内嵌 `user:pass@`、`password/secret/token` 赋值），真实凭据零命中；教程占位符/官方示例密钥（如 `AKIAIOSFODNN7EXAMPLE`、`sk-xxxx…`）/脱敏演示代码逐一核实后白名单放行

### Requirement: 洞察报告

系统 SHALL 产出迁移洞察报告，包含：重复率统计、时效衰减发现、知识资产分布分析、双体系治理建议，存放于本 spec 目录 `insights.md`。

### Requirement: 源目录删除与上游修复

系统 SHALL 在对抗审查对账通过后删除 `docs/knowledge/learning/` 整目录，并修复 `docs/knowledge/index.md` 等上游 toctree/链接引用，主仓库 Sphinx 构建与 `check-links.py` 通过。

#### Scenario: 删除后无断链

* **WHEN** learning/ 删除完成

* **THEN** 主仓库 `check-links.py --path docs/` 无断链，`sphinx-build` 零错误

### Requirement: 门控与提交纪律

系统 SHALL 在每批迁移后运行 `invoke gates.toctrees`，全量完成后运行 `invoke gates.all` 与 `sphinx-build`（零警告）；子模块提交遵守 add/commit 分离与暂存区核对；主仓库在子模块全部提交后 bump 指针。

## Constraints

* 目标库为 git submodule，存在并行会话写入风险：`git add` 与 `git commit` 必须分两次工具调用，中间以 `git diff --cached --name-only` 核对暂存集，发现非本任务文件立即停止并报告

* 主仓库 `docs/` 删除 learning 后，根 `docs/` Sphinx toctree 必须同步修复，否则主仓库构建失败

* bundles 计数（当前 389 束/44 组/9 域）一律以 `gates.bundles` 门控重算为准，禁止手填采信

* 中文语境内嵌引号一律全角“”，防 MyST YAML 解析告警

* 待补文件禁止先放链接（纯文本"（待补）"标注）

## Assumptions

* A1：learning/ 内容为公开学习材料（公开内容级别），走标准工作流，产出物入 bundles

* A2：10 对重复主题以 bundles 侧为权威基线；若 learning 侧有 bundles 缺失的实质内容则回填

* A3：新增域/组数量保持克制（预计新增组：zhexue/methodology、sheke/industry、jishu/systems、jishu/iot、wenxue/english，实施可微调）

* A4：非 md 资源（.html/.png 等）随所属主题一并迁移或按内容舍弃，台账中登记处置

* A5：迁移不改写正文语义；时效更新仅限数据性内容（版本号/定价/状态）并留痕

* A6：主仓库侧删除 learning 与子模块迁移分批独立提交，可独立回滚

## Acceptance Criteria

### AC-1：无遗漏

* **Given** 迁移完成

* **When** 以台账对账 learning/ 原 2124 个 md 文件（实测数）

* **Then** 每个文件有且仅有四种归宿之一：已迁移、已合并入既有束、重复删除（内容已确认覆盖）、低价值舍弃（台账登记理由）；`docs/knowledge/learning/` 已删除

### AC-2：门控全绿

* **Given** 迁移完成

* **When** 在 awesome-okf-xs 运行 `invoke gates.all` 与 `invoke build`

* **Then** utf8/toctrees/bundles 三门全绿，sphinx-build 零错误零警告

### AC-3：主仓库构建通过

* **Given** learning/ 已删除且上游引用修复

* **When** 主仓库运行 `check-links.py --path docs/` 与 Sphinx 构建

* **Then** 无断链、零构建错误

### AC-4：时效留痕

* **Given** 任一时效敏感束

* **When** 检查其 `log.md`

* **Then** 含 2026-09 核验记录或显式过时标注

### AC-5：洞察交付

* **Given** 迁移完成

* **When** 检查本 spec 目录

* **Then** 存在 `insights.md`，含重复率、时效衰减、分布分析、治理建议四部分

### AC-6：隐私与凭据零泄露

* **Given** 迁移完成

* **When** 对迁入 bundles 的新增内容复扫隐私模式与真实凭据格式（个人标识/真实凭据/私人叙事/工作流元数据/密码密钥）

* **Then** 零真实泄露；工作流元数据文件（retrospective/seven-concepts-report）未迁入，台账中登记为舍弃；占位符与官方示例逐一核实放行

### AC-7：提交合规

* **Given** 全部提交完成

* **When** 检查子模块与主仓库提交历史

* **Then** 提交为 Conventional Commits 中文描述、单一职责分批；主仓库指针指向子模块最终 SHA

