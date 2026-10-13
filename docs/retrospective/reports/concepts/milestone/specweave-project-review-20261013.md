---
id: specweave-project-review-20261013
title: SpecWeave 全面复盘报告（2026-10-13）——入口计数统一与规范容器边界
date: 2026-10-13
type: retrospective
source: 七概念方法论 R→I→E→V→A→C 里程碑复盘链路
category: milestone
maturity: L2
tags: [方法论, 七概念, 治理策略, 全面复盘, 项目复盘, 计数治理]
---

# SpecWeave 全面复盘报告（2026-10-13）

![SpecWeave 多智能体协作编织概念图](specweave-project-review-20261013-cover.png)

> **周期**：2026-06-23 至 2026-10-13（113 天）| **方法**：七概念 R→I→E→V→A→C | **基线**：承接 [2026-09-30 全面复盘](specweave-seven-concepts-project-review-20260930.md)，本次聚焦 13 天增量与一个上次未覆盖的结构性问题 | **数据**：git + 目录实测

---

## 一、事实（R · 纯客观，无因果/判断词）

### 1.1 提交数据（git 实测）

| 指标 | 数值 | 验证方式 |
|------|------|---------|
| 总提交数 | **4219** | `git rev-list --count HEAD` |
| 首次提交 | 2026-06-23 09:39 | `git log --reverse` |
| 最近提交 | 2026-10-13 11:36 | `git log -1` |
| 较 09-30 基线增量 | +229（3990→4219） | 两次计数之差 |
| 增量区间日均 | 约 17.6 次/天（13 天） | 229/13 |

**按月提交分布**：

| 月份 | 提交数 |
|------|-------|
| 2026-06（06-23 起） | 433 |
| 2026-07 | 1502 |
| 2026-08 | 1274 |
| 2026-09 | 812 |
| 2026-10（至 13 日） | 198 |

### 1.2 产出物存量（2026-10-13 目录实测）

| 资产 | 数量 | 验证方式 |
|------|------|---------|
| 主仓追踪文件总数 | 16866 | `git ls-files` |
| Python 脚本（`.agents/scripts`，含 lib/tests/mdi） | **657** | `Get-ChildItem -Recurse -Filter *.py` |
| Skill（`.agents/skills` 含 SKILL.md 的一级目录） | **169** | 逐目录确认 SKILL.md |
| 规则文件（`.agents/rules` .md） | **136** | `Get-ChildItem -Recurse -Filter *.md` |
| 指令集（`.agents/commands` 命令文档） | **15** | `git ls-files .agents/commands` |
| 可复用模式（`docs/retrospective/patterns` .md） | **946** | 递归计数 |
| `.agents` 下 .md 总数 | 1401 | 递归计数（排除 cache/logs/reports） |
| `docs` 下 .md 总数 | 4025 | 递归计数（排除 _build/.venv） |

**模式库分类**：methodology-patterns 566、code-patterns 233、architecture-patterns 97、process-patterns 29、analysis-cards 7、documentation-patterns 7、checklists 3。

### 1.3 区域与子模块

- 四大区域追踪文件：`.agents` 5505、`apps` 1496、`docs` 4090、`projects` 262、`vendor` 23（子模块 gitlink 不计内容）。
- `.gitmodules` 注册子模块 **21 个**（projects 3、vendor 18 路径，含 netease-youdao 下 6 个）；21 个的 `.git` 指针均存在、目录均有内容。
- `apps` 下 12 个目录；规模前三：docker-images 490、dev-tools 305、containers 292。
- `projects` 下除注册子模块外，`monetize`、`tvm-ffi` 两目录文件由主仓 `git ls-files` 直接追踪，未在 `.gitmodules` 注册。
- 根 `scripts/` 目录存在但无条目。

### 1.4 13 天增量主题（提交摘录）

1. **openKylin 开发容器体系**：okw CLI 新增 podman / image / compose 子命令；openKylin 3.0 全功能开发容器镜像；CLI 重构为 parser/main 分层 + 显式注册表分发；openkylin-wsl-devkit 迁入主权区。
2. **《守护品质生活》付费 MVP（gqlsite）**：支付宝电脑网站支付闭环、Vercel 静态部署、内网穿透、真实收款操作手册。
3. **第二交付产品 xmflow-cli**：纯 CLI 客户镜像、离线交付、bind-mount 消除 wheel 残留层。
4. **方法论模式**：开发容器镜像构建纪律、跨平台门禁权威分工、行为取证固化测试、依赖序切片门禁、第一性原理多维证伪、快照对拍迁移、统一契约工具编排层等。
5. **OKF 知识包**：REA 官网四轮到、Odyssey-3、embedded-weekly-03、oil-ui、openTPU、Lazada 等多包。
6. 另含 WSL VHDX 压缩门面、智能体工作区起步套件、travel-planner、麦田烘焙示例、大道极简生存指南。

### 1.5 关键事实：入口计数三套快照（本次复盘的直接触发点）

| 入口（复盘前） | 脚本 | Skills |
|----------------|------|--------|
| 根 `README.md` | 419+ | 28 |
| `docs/index.md` | 401+ | 21 |
| `.agents/README.md` | 341 | 19 |

> 三处与 1.2 实测值（657 / 169）均不一致，且彼此不一致。

---

## 二、洞察（I · 四元组：陈述 / 证据 / 反常识 / 行动）

### 洞察 1 — 治理工具覆盖了代码与链接，唯独漏了文档自身的计数

- **陈述**：项目所有对外计数均为手工快照，在高频提交下与实际规模持续偏离，且三个入口互相矛盾。
- **证据**：事实 1.5、1.2；09-30 复盘报告自身数字准确但入口未同步。
- **反常识**：团队建了 check-links、docgen、ci-check 等大量自动门禁，却没有把"文档里最易过期的数字"纳入自动生成——治理的灯下黑。
- **行动**：徽章/计数接入 `docgen stats` 自动生成或引用单一数据源，CI 校验根 README 与 docs/index 一致。

### 洞察 2 — `.agents/skills` 兼具「规范容器」与「技能仓库」双重身份而边界未声明

- **陈述**：skills 下 169 目录 / 4263 文件，仅约 40 个为自研门面、37 个为 IDE 镜像，其余为跨来源素材，混放于同一层级。
- **证据**：事实 1.2、1.3；trae-work-design（730 文件）、yuanli-design-system（744 文件）。
- **反常识**：方法论核心倡导"原子化、按需加载、入口轻量"，规范容器自身却无隔离地吸收上千文件外部资产，与自身原则相悖；新 Agent 无法区分"该遵守的规范"与"可参考的素材"。
- **行动**：skills/ 做二级分区（自研门面区 / 镜像区 / 素材区）或在索引中明确边界与口径。

### 洞察 3 — 对称区域治理不对称：vendor 有强校验，projects 无「名实」校验

- **陈述**：AGENTS.md 将 projects 定义为子模块区，但 monetize、tvm-ffi 为主仓直接追踪的普通目录，区域规则与实际内容不一致。
- **证据**：事实 1.3。
- **反常识**：项目对 vendor 边界有 check-vendor 深度校验，却对同名的 projects 内"普通目录混入"无对应校验。
- **行动**：更新 AGENTS.md 表述（已完成），并补一个 projects 对称校验脚本/检查项。

### 洞察 4 — 沉淀速度与开发速度在高峰期负相关，「高频复盘」在高压期失效

- **陈述**：CHANGELOG 停在 08-06，08 月中下至 10 月约两千次提交未汇总；方法论模式索引长期写"22 个"而目录已达 566。
- **证据**：事实 1.1、1.2；CHANGELOG 与各 index 文本。
- **反常识**：提交最密集的 7-8 月恰是复盘/CHANGELOG 最易被挤占的时期，"高频批次复盘"实践在高压期自然让位于交付。
- **行动**：里程碑复盘作为阶段硬门禁（而非事后补做）；模式/计数索引纳入自动统计。

---

## 三、萃取（E · 模式复用与升级，不重复造模式）

| 洞察 | 处理 | 状态 |
|------|------|------|
| 洞察 1、4（计数全量重算） | **升级既有模式** [合成统计权威数据来源](../../../patterns/methodology-patterns/document-architecture/synthetic-stats-source-of-truth.md)：L1→**L2**，新增「入口徽章计数漂移」案例、权威计数命令表与 3 条新反模式 | ✅ |
| 洞察 2（容器边界） | 复用 [入口-容器分离](../../../patterns/methodology-patterns/document-architecture/entry-container-separation.md) 的原则，本次先以口径声明落地，二级分区登记为待办 | ✅ 已覆盖 |
| 洞察 3（名实校验） | 复用 [信源稳定性门](../../../patterns/methodology-patterns/ai-collaboration/source-stability-gate.md) 与 [vendor 生命周期治理](../../../patterns/methodology-patterns/governance-strategy/vendor-lifecycle-governance.md) 的思路，projects 对称校验登记为待办 | ✅ 已覆盖 |

> **三查**：① 与 document-architecture 下 50+ 模式逐一比对，确认计数治理已由 synthetic-stats-source-of-truth 承载，不新建；② frontmatter 与 TOML 双轨一致；③ 索引同步。

---

## 四、行动项（A · 原子化，登记待办）

| # | 行动项 | 优先级 | 验收标准 |
|---|--------|--------|---------|
| 1 | 入口徽章计数接入 `docgen stats`，CI 校验一致 | 高 | 改任意计数后 CI 能自动复核 README/docs-index |
| 2 | `.agents/skills` 二级分区或显式边界 | 中 | 自研/镜像/素材三类在目录或索引可一眼区分 |
| 3 | projects「普通目录 vs 子模块」对称校验 | 中 | 存在可运行检查并纳入 ci-check |
| 4 | capability-registry/02-skills 补登最近迁入技能 | 中 | openkylin-wsl-devkit 等在册 |
| 5 | 里程碑复盘设为阶段硬门禁 | 中 | 阶段交付前含复盘产物 |

---

## 五、对抗审查（V · 四视角）

| 视角 | 攻击点 | 采纳/修正 |
|------|--------|----------|
| 🔴 魔鬼代言人 | 657 含 164 测试、276 库文件，称"650+ 脚本"是否夸大可执行能力？ | 徽章口径注明"含共享库与测试"；正文区分可执行脚本 |
| 🟢 新人 | "在册/镜像/素材"三类无物理隔离，仅文字说明仍会迷路 | 二级分区登记为行动项 2；README 补口径段落 |
| 🟠 老板 | 数字统一是"面子"，有无实证质量改善？ | 本次同时修正 6 处入口与 1 模式升级，数字均可复算，降低外部误读 |
| 🔵 未来 | 手工改一次仍会再漂移，根因未除 | 自动生成 + CI 校验登记为行动项 1，本次属止血 |

---

## 六、本次变更清单与验证

**已更新文件**：

1. 根 `README.md`：徽章（脚本 650+ / Skills 169 / 规则 136）、正文计数、新增 Skills 口径说明。
2. `docs/index.md`：徽章同步。
3. `.agents/README.md`：目录树与关系段计数。
4. `.agents/subdirectory-responsibilities.md`：规则/指令/脚本/技能计数，指令列补全为 15。
5. `.agents/ONBOARDING.md`：版本 2.6、提交数 4200+、刷新待办。
6. `.agents/capability-registry.md` 及 `03`：版本日期、命令表补 3 个指令。
7. `AGENTS.md`：projects 区域表述修正。
8. `CHANGELOG.md`：补 08-31、09-30、10-13 三个节点。
9. 模式 `synthetic-stats-source-of-truth.md`：升级 L2 + 案例二。

**验证**：关键计数均由命令实测；交叉引用使用相对路径；无 `file:///` 绝对路径；报告与 09-30 基线衔接。

> AI 生成
