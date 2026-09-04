# Ψhē 理论体系 OKF Wiki 教程 - 产品需求文档

## Overview

- **Summary**: 基于 `source-code-to-okf-wiki` 五阶段工作流（R→I→E→V→C）和 `seven-concepts-cmd` 知识沉淀链路（R→I→E→V→C），系统学习三个网站（godgpt.fun、dw.cash、math.dw.cash）的全部子页面以及本地 `external/dao/AllTheory` 资源，在 `projects/awesome-okf-xs/bundles/` 下创建新的 `psi/` 知识束分组，生成符合 OKF v0.2 规范的结构化中文 Wiki 教程。

- **Purpose**: 将 Ψhē（ψ=ψ(ψ)）理论体系——一个横跨哲学、数学、物理学、宇宙学、意识研究、文学批评和 AI 应用的宏大思想系统——转化为可导航、可溯源、可验证的 OKF 知识束，使读者能够系统化理解该理论的核心概念、数学形式化和实践应用。

- **Target Users**: 对意识哲学、自指系统、数学基础、跨学科思想实验感兴趣的中文读者；OKF 知识生态的贡献者和消费者。

## Goals

- 创建 `psi/` 知识束分组，包含 4 个知识束：`psi-core`（核心哲学）、`psi-math`（数学形式化）、`psi-universe`（XOR-SHIFT 宇宙本论）、`godgpt`（应用产品）
- 每个知识束遵循 OKF v0.2 规范，包含 `concepts/`、`examples/`、`references/` 三层结构
- 所有概念文档携带完整 YAML frontmatter（type/title/description/tags/generated/verified/status/sources）
- 交叉引用使用 `/` 开头的 bundle-relative 路径
- 信源先行：`references/` 先于 `concepts/` 生成
- 分批生成：每批 ≤ 7 文件
- Index 最后生成
- 更新 `bundles/index.md` 总索引，注册新分组

## Non-Goals (Out of Scope)

- 不逐字复制 600+ 章原始内容——Wiki 是策展式教程，提炼核心概念而非全文搬运
- 不对理论主张的科学正确性做评判——客观记录理论体系的内容和结构
- 不生成英文版本——仅中文
- 不修改 `external/dao/AllTheory/` 下的任何源文件
- 不初始化 `automath/` 和 `the-omega/` 两个空子模块（无检出内容）
- 不涉及 GodGPT 移动应用的逆向工程或 API 分析

## Background & Context

### 数据源全景

| 数据源 | 类型 | 内容规模 | 核心主题 |
|--------|------|----------|----------|
| godgpt.fun | 商业网站 | 5 页面 | AI 灵性引导移动应用，功能/推广/法律 |
| dw.cash | Docusaurus 文档站 | 17 部著作 600+ 章 | ψ=ψ(ψ) 哲学体系：意识/塌缩/回声/物理/宇宙/文学 |
| math.dw.cash | Docusaurus 数学站 | 153 页面 | ψ 的数学形式化：RH 证明/坍缩数学/CST/物理常数 |
| AllTheory/alltheory/ | 本地 Docusaurus 源码 | dw.cash 的完整源码 | 同上，含构建脚本和双语资源 |
| AllTheory/universe/ | 本地形式化理论库 | 778 个理论文件 | XOR-SHIFT 宇宙本论 v37.5，D0-D∞ 维度谱系 |

### 两大形式体系的关系

- **Ψhē 理论**（alltheory/dw.cash）：以 ψ=ψ(ψ) 为唯一公理，用"塌缩（Collapse）"和"回声（Echo）"描述意识-实在关系，文学哲学叙事为主
- **宇宙本论**（universe/math.dw.cash）：以 𝒰=ℱ(𝒰), ℱ(x)=x⊕SHIFT(x) 为核心，用 XOR/SHIFT 操作构建公理化系统，数学推演为主
- 二者同构：ψ 的"塌缩"对应 XOR-SHIFT 的"状态更新"，"回声"对应 SHIFT 后的"信息迹"

### OKF 规范要点

- 唯一必填字段：`type`
- 根 `index.md` 含 `okf_version: "0.2"`
- 子目录 `index.md` 无 frontmatter
- 交叉引用用 `/` 开头 bundle-relative 路径
- `references/` 信源文件先于 `concepts/` 生成

## Functional Requirements

- **FR-1**: 创建 `bundles/psi/` 分组目录及 `index.md` 分组索引
- **FR-2**: 创建 `psi-core/` 知识束，涵盖 ψ=ψ(ψ) 核心哲学（塌缩、回声、观察者、语言涌现、元递归、统一回归等）
- **FR-3**: 创建 `psi-math/` 知识束，涵盖数学形式化（theory_psi 核心文档、RH 证明、坍缩数学、CST、物理常数、ZFC 坍缩、未解问题）
- **FR-4**: 创建 `psi-universe/` 知识束，涵盖 XOR-SHIFT 宇宙本论（三大公理、FLIP/XOR/SHIFT/REC/Meta 操作层级、维度谱系、学科覆盖）
- **FR-5**: 创建 `godgpt/` 知识束，涵盖 GodGPT 应用（产品定位、核心功能、商业模式、法律框架）
- **FR-6**: 每个知识束包含完整的 OKF 目录结构（index.md、log.md、concepts/、examples/、references/）
- **FR-7**: 所有概念文档含完整 frontmatter 和 `## 相关概念` 章节
- **FR-8**: 信源文件登记三个网站 URL 和本地路径
- **FR-9**: 更新 `bundles/index.md` 注册 psi 分组
- **FR-10**: 所有文档使用中文撰写，英文术语首次出现时括号注释

## Non-Functional Requirements

- **NFR-1**: 每个概念文档 500-5000 字符，保持语义完整性
- **NFR-2**: frontmatter 字段完整，`sources` 指向实际存在的 references 文件
- **NFR-3**: 交叉链接无断裂（V 阶段链接检查）
- **NFR-4**: 无虚构 API 或事实（V 阶段源文件验证）
- **NFR-5**: 文件命名使用 kebab-case 英文
- **NFR-6**: 遵循 awesome-okf-xs 项目的路径引用规范（相对路径，禁止 file:///）

## Constraints

- **Technical**: 必须遵循 OKF v0.2 规范；必须遵循 source-code-to-okf-wiki 五阶段工作流；Windows 环境路径分隔符注意
- **Business**: 内容为哲学-数理思想实验，须在 references 中保留原始免责声明
- **Dependencies**: 依赖 `external/dao/AllTheory/` 本地内容和三个网站的可访问性

## Assumptions

- `psi/` 作为新分组名称（以核心符号 ψ 命名），不与现有 23 个分组冲突
- 四个知识束的划分能合理覆盖全部数据源内容
- automath/ 和 the-omega/ 空子模块无可用内容，不纳入
- GodGPT 虽为商业产品，但其产品理念与 ψ 理论体系相关（AI 作为意识镜像），值得独立成束
- 理论体系中的"证明"和"定理"应作为理论主张客观记录，不做科学性背书

## Acceptance Criteria

### AC-1: 分组结构完整
- **Given**: 规范已批准
- **When**: 检查 `bundles/psi/` 目录
- **Then**: 存在 `index.md`（含 okf_version）和 4 个知识束子目录，每个子目录含完整 OKF 结构
- **Verification**: `programmatic`

### AC-2: 知识束内容覆盖
- **Given**: 四个知识束已生成
- **When**: 审查 concepts/ 目录
- **Then**: psi-core 覆盖核心哲学概念（≥8 个），psi-math 覆盖数学形式化关键主题（≥6 个），psi-universe 覆盖 XOR-SHIFT 体系（≥6 个），godgpt 覆盖产品要点（≥4 个）
- **Verification**: `human-judgment`

### AC-3: Frontmatter 合规
- **Given**: 所有 .md 文件已生成
- **When**: 检查每个非 index.md 文件的 frontmatter
- **Then**: 包含 type/title/description/tags/generated/verified/status/sources 字段，type 非空
- **Verification**: `programmatic`

### AC-4: 信源溯源完整
- **Given**: references/ 目录已生成
- **When**: 检查每个概念文档的 sources 字段
- **Then**: 每个 source 指向的 references 文件实际存在，且 references 文件包含原始 URL 或本地路径
- **Verification**: `programmatic`

### AC-5: 交叉链接有效
- **Given**: 所有文档已生成
- **When**: 检查所有 `/` 开头的交叉链接
- **Then**: 链接目标文件存在，无断裂
- **Verification**: `programmatic`

### AC-6: 无虚构内容
- **Given**: V 阶段验证
- **When**: 对文档中引用的关键概念、公式、定理名称进行源文件比对
- **Then**: 所有关键事实可在 sources 指向的原始材料中找到对应
- **Verification**: `human-judgment`

### AC-7: 总索引更新
- **Given**: 知识束已就位
- **When**: 查看 `bundles/index.md`
- **Then**: psi 分组出现在分组导航表和分组详情中
- **Verification**: `programmatic`

### AC-8: 分批生成纪律
- **Given**: E 阶段执行记录
- **When**: 审查生成过程
- **Then**: references/ 先于 concepts/ 生成；每批 ≤ 7 文件；index.md 最后生成
- **Verification**: `human-judgment`

## Open Questions

- [ ] GodGPT 知识束是否需要包含隐私政策和服务条款的详细分析，还是仅概述产品功能？
- [ ] psi-math 中 RH 证明部分是否需要包含数学推导细节，还是仅记录证明结构和方法论？
- [ ] universe 的 778 个形式理论文件是否需要逐一覆盖，还是按维度/学科分类做概览？
