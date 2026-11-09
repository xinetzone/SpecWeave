# 规格说明（Spec Mode · spec.md）

> 第二轮规格：既有 OKF 知识包的**源码级增量扩展**。第一轮规格见 [../wechat-intelligence-hub-blog-okf-wiki/spec.md](../wechat-intelligence-hub-blog-okf-wiki/spec.md)。

## 1. 背景与触发

用户下达：`/七概念 D:\spaces\SpecWeave\external\dao\wechat\wechat-intelligence-hub 是源码`。

该路径是既有知识包 `jishu/ai/products/wechat-intelligence-hub/` 的**上游源码本地副本**。用户意图是对该主题做源码级学习、核验与沉淀，把既有束从「博文 + 文档核验层」推进到「代码事实层」。

## 2. 目标与非目标

### 目标

| # | 目标 | 验收标准 |
|---|------|---------|
| G-1 | 按 G0 规则锁定可追溯信源 | 固定不可变 commit hash + remote URL + 工作区一致性核验；禁止 `main`/`master` |
| G-2 | 采集源码级事实并编号 | 新增 F 编号段，与首轮 F-001~F-057 衔接无跳号、无重叠 |
| G-3 | 对首轮结论做对抗性对账 | 8 项 ⚠️ 逐项给出源码证据与判定；识别新增漂移 |
| G-4 | 增量扩展 bundle | 新增 references 与 concepts；定向修订受漂移影响的表述；**不重写已验证结论** |
| G-5 | 质量门与计数断言 | 机械门禁通过；所有数量陈述双口径独立复核 |

### 非目标

| # | 非目标 | 理由 |
|---|--------|------|
| N-1 | 不新建独立 bundle | 主题、归属、索引接入均已存在；§6.5 要求增量扩展 |
| N-2 | 不重排首轮 F 编号 | 首轮 57 条已提交并被外部引用，重排会破坏引用 |
| N-3 | 不实机执行上游脚本 | `install.sh` / `run_demo.sh` 涉及真实环境与副作用，超出本轮授权 |
| N-4 | 不修改上游源码 | `external/` 为只读参考区（`external/AGENTS.md` 规则 1「上游只读」） |
| N-5 | 不写入 `external/` | 同上规则 8 + 边界声明「禁止把 external 当交付区」 |
| N-6 | 不做 star 时序核验 | GitHub stargazers 时序接口非本轮可得，维持 ⚠️ |

## 3. 关键约束

| 约束 | 来源 | 落地方式 |
|------|------|---------|
| 内容敏感度 Public → 标准 Spec Mode | 根 AGENTS.md 步骤 2.3 | 源码为公开开源代码；产出物落既有 bundle（`projects/` 区，非 `playground/`） |
| 上游只读 | `external/AGENTS.md` 规则 1 | 仅 `git ls-tree` / `ast` / `grep` 读取，无写入 |
| 交付物不落 `external/` | `external/AGENTS.md` 边界声明 | 全部产出在 `projects/awesome-okf-xs/doc/bundles/...` |
| 增量扩展不重写 | `source-code-to-okf-wiki` §6.5 | 首轮 concepts 原文保留，受影响处加 🔬 修订框 |
| F 编号续编 | 同上 | F-058~F-101，双份登记于 `references/source-code-map.md` 与本 spec `facts.md` |
| 计数断言双口径 | `source-code-to-okf-wiki` 计数断言验证 | R 阶段 AST、grep 计数；V 阶段正则/awk 独立复核 |
| 无虚构 API | 同上 Grep 级验证 | 所有类名/函数名/常量名在上游源码验证存在 |
| 相对路径引用 | 子项目 AGENTS.md「路径引用」 | 无 `file:///`、无本机绝对路径 |

## 4. 章节结构（Requirements）

### R-1 信源稳定性（G0）

- **R-1.1**：信源固定于不可变 commit hash，记录 remote URL、commit 完整 SHA、提交时间、工作区状态。
- **R-1.2**：固定对象**不得**为 `main`/`master` 分支引用。
- **R-1.3**：运行 `check-source-path-stability.py` 定向扫描本束，rc=0。

### R-2 事实采集（R）

- **R-2.1**：以 `git ls-tree -r HEAD` 取 HEAD 口径规模（禁用工作区 `find` 快照）。
- **R-2.2**：以 Python `ast` 解析类、函数签名、常量元组长度、字典条目数；脚本须同时处理 `ast.Assign` 与 `ast.AnnAssign`。
- **R-2.3**：新增事实编入 F-058~F-101，**零推测表述**（不写「用于」「目的是」「设计为」）。
- **R-2.4**：F 编号与 `references/source-code-map.md` **双份登记**，集合相等、连续无跳号。

### R-3 对抗性对账（I）

- **R-3.1**：首轮 8 项 ⚠️ **逐项**给出源码/官方文档证据与判定（坐实 / 修正 / 维持）。
- **R-3.2**：产出漂移分类（D1 文档漂移 / D2 范围缺口 / D3 计数口径 / D4 新增事实 / D5 维持）。
- **R-3.3**：对首轮判定给出**可信度评估**（是否为保守判定、是否存在事实性错误）。

### R-4 增量落盘（E）

- **R-4.1**：信源先行——`references/source-code-map.md` → `references/source-code-verification.md` → `concepts/06~09` → 三级 `index.md` → 根 `index.md` → `log.md`。
- **R-4.2**：新概念续编号 06 起，不重排旧编号。
- **R-4.3**：首轮文件仅**定向修订**（受漂移影响处），其余原文不动。
- **R-4.4**：`references/verification.md` 以**追加节**形式记录源码轮追记，不改写首轮结论。

### R-5 质量门（V/C）

- **R-5.1**：机械门禁 `check-utf8.py` / `check-toctrees.py` / `check-bundles-index.py` / `check-asset-baseline.py` / `check-source-path-stability.py` 全部通过或登记归属。
- **R-5.2**：所有数量陈述经 R + V 双口径复核；不一致项**先修文档**再登记。
- **R-5.3**：Grep 级验证全部 API 名称在源码中存在。
- **R-5.4**：相对链接零断链、零绝对路径、frontmatter 必填字段齐备、`okf_version` 仅在根 `index.md`。

## 5. 验收词汇

| 词汇 | 含义 |
|------|------|
| rule | 硬约束（违反即返工） |
| rubric | 质量导向标准（可权衡） |

**rule**：R-1.2 / R-2.1 / R-2.4 / R-4.2 / R-4.3 / R-5.2 / R-5.3 / R-5.4
**rubric**：R-1.1 / R-1.3 / R-2.2 / R-2.3 / R-3.1 / R-3.2 / R-3.3 / R-4.1 / R-4.4 / R-5.1

## 6. 与第一轮的关系

| 维度 | 第一轮 | 第二轮 |
|------|--------|--------|
| 主题 | 同一 | 同一（**不新建束**） |
| 归属 | `jishu/ai/products/wechat-intelligence-hub/` | 同（**不变**） |
| F 编号 | F-001~F-057 | F-058~F-101（**续编**） |
| 信源 | 微信博文 + GitHub API + README 网页快照 | 固定 commit `fb6a42c` 的本地源码 |
| 文件 | 12 个 | 新增 6 个 + 定向修订 3 个 |
| 结论 | 22 项 P0/P1 = 14✅/8⚠️/0❌ | 8 项 ⚠️ 对账 = 6 坐实 / 1 拆分 / 2 维持 |
