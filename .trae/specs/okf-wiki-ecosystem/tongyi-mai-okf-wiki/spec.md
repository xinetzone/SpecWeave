# Tongyi-MAI 源码学习 OKF Wiki 教程 Spec

## Why

`d:\spaces\SpecWeave/external/libs/tools/Tongyi-MAI` 是通义实验室 GUI Agent 生态的开源仓库集合（5 个子项目），涵盖移动 GUI Agent 基座模型（MAI-UI）、在线移动端基准框架（MobileWorld）、规划智能体基准（MobilePA-Bench）等前沿资产，但缺乏系统化中文教程。需按 `source-code-to-okf-wiki` Skill 的 R→I→E→V→C 五阶段链路，在 `projects/awesome-okf-xs/doc/bundles` 生成可溯源、无虚构 API 的 OKF v0.2 知识包。

## What Changes

在 `projects/awesome-okf-xs/doc/bundles/ai/ai-agent/` 分组下新增 **3 个 OKF bundle**（覆盖 Tongyi-MAI 全部 5 个子文件夹，按"是否有实现源码"归并）：

| 新 Bundle | 覆盖的源文件夹 | 内容形态 |
|---|---|---|
| `mai-ui/` | `MAI-UI/`（外层伞仓 + 内层 MAI-UI/MAI-UI 源码 + 内层 Qwen-UI-Agent 资产）+ `MAI-UI-blog/`（Grounding/Navigation 博客作信源） | 源码精读：grounding/navigation Agent 实现、unified_memory、prompt 体系、评估管线、 cookbook |
| `mobile-world/` | `MobileWorld/` | 源码精读：`src/mobile_world/`（agents/core/runtime/tasks）、CLI、eval_server、MCP 集成、Docker 环境 |
| `mobilepa-bench/` | `MobilePA-Bench/` + 顶层 `Qwen-UI-Agent/`（Next.js 网站源码） | 基准设计精读（以网站/Paper/README 为信源）+ 网站技术栈简析 |

同步更新：
- `bundles/ai/ai-agent/index.md`（分组索引，新增 3 束条目）
- `bundles/ai/index.md`（域索引计数）
- `bundles/index.md`（总索引计数：total_bundles 283→286、ai-agent 组束数、说明文字）
- 现有 `qwen-ui-agent/` 束与 3 个新束互相跨链接（该束为博客测评来源，新束为源码教程，互补关系）

不改动：源码目录 `external/libs/tools/Tongyi-MAI/` 本身（只读信源）、其他既有 bundle。

**BREAKING**: 无。

## Impact

- **Affected specs**: 无既有 spec 冲突；本 spec 新建于 `.trae/specs/okf-wiki-ecosystem/tongyi-mai-okf-wiki/`
- **Affected code/产物**:
  - `projects/awesome-okf-xs/doc/bundles/ai/ai-agent/mai-ui/**`（新增）
  - `projects/awesome-okf-xs/doc/bundles/ai/ai-agent/mobile-world/**`（新增）
  - `projects/awesome-okf-xs/doc/bundles/ai/ai-agent/mobilepa-bench/**`（新增）
  - `projects/awesome-okf-xs/doc/bundles/ai/ai-agent/index.md`（更新）
  - `projects/awesome-okf-xs/doc/bundles/ai/index.md`（更新计数）
  - `projects/awesome-okf-xs/doc/bundles/index.md`（更新计数）
  - `projects/awesome-okf-xs/doc/bundles/ai/ai-agent/qwen-ui-agent/index.md`（追加跨链接，最小改动）
- **质量门**：`invoke gates.all`（UTF-8 + toctree 完整性）必须通过
- **提交**：awesome-okf-xs 子模块原子提交 → SpecWeave 主仓库子模块指针提交

## 方法论约束（强制）

按 `source-code-to-okf-wiki` Skill（七概念编排场景4：知识沉淀 R→I→E→V→C）执行：

1. **R 阶段（事实采集）**：逐模块阅读源码，提取编号事实 F-xxx 写入 `.trae/specs/okf-wiki-ecosystem/tongyi-mai-okf-wiki/facts-*.md`，零推测（禁止"用于/目的是"推断词）；G1 门
2. **I 阶段（架构洞察）**：3-5 个洞察四元组（陈述/证据/反常识/行动）+ 知识地图与学习路径；G2 门
3. **E 阶段（批量生成）**：⚡ 信源先行（references/ 先于 concepts/）、每批 ≤7 文件、index 最后写、交叉链接用 `/` 开头 bundle-relative 路径、每个 index.md（根+子目录）必含 `{toctree}` 块；G3 门
4. **V 阶段（独立验证）**：Grep 验证文档引用的每个类名/方法名在源码中真实存在（重点防虚构 API）、链接无断裂、frontmatter 完整、`invoke gates.toctrees` 通过；G4 门
5. **C 阶段（模式沉淀+提交）**：`atomic-commit-cmd` 原子提交（子模块先、主仓库后）；G5 门

## ADDED Requirements

### Requirement: mai-ui 源码知识包
系统 SHALL 在 `ai/ai-agent/mai-ui/` 生成覆盖 MAI-UI Agent 实现源码的 OKF bundle，所有概念文档的事实均可溯源至 `facts-mai-ui.md` 编号事实。

#### Scenario: 概念文档引用 API 真实存在
- **WHEN** 概念文档中出现类名/方法名（如 `mai_grounding_agent` 模块中的 Agent 类）
- **THEN** Grep `external/libs/tools/Tongyi-MAI/MAI-UI` 源码可验证该符号存在，且签名与文档一致

### Requirement: mobile-world 源码知识包
系统 SHALL 在 `ai/ai-agent/mobile-world/` 生成覆盖 MobileWorld 框架（agents/core/runtime/tasks 四层 + CLI/eval_server/MCP）的 OKF bundle。

#### Scenario: 学习路径完整
- **WHEN** 读者按 concepts/index 的 toctree 顺序阅读
- **THEN** 可从环境安装 → 核心架构 → Agent 注册机制 → 评估管线渐进学习，无断链

### Requirement: mobilepa-bench 基准知识包
系统 SHALL 在 `ai/ai-agent/mobilepa-bench/` 生成覆盖 MobilePA-Bench 四能力维度（Tool Use/Memory/Skills/Sub-agent）与验证策略的 OKF bundle，并简析顶层 Qwen-UI-Agent Next.js 网站技术栈。

#### Scenario: 网站形态子项目的处理
- **WHEN** 子项目仅有网站/Paper 而无实现源码（MobilePA-Bench、Qwen-UI-Agent 网站）
- **THEN** 以 README/Paper/网站源码为信源登记（references/），文档明示"非实现代码仓"性质，不虚构实现细节

### Requirement: 索引同步
系统 SHALL 同步更新 ai-agent 分组索引、ai 域索引、总索引的束数与条目，使 `invoke gates.toctrees` BFS 导航可达全部新增文档。

#### Scenario: 质量门通过
- **WHEN** 在 `projects/awesome-okf-xs/` 运行 `invoke gates.all`
- **THEN** UTF-8 与 toctrees 检查全部通过，零失败项

## MODIFIED Requirements

### Requirement: qwen-ui-agent 束跨链接（最小修改）
现有 `qwen-ui-agent/` 束 SHALL 在 index.md 的相关章节追加指向 3 个新束的互链（仅此一处修改，不动其他内容）。

## REMOVED Requirements

无。
