# DSpark 论文学习与 Wiki 教程文档 Spec

## Why
DeepSeek 梁文锋署名的新论文 DSpark 在 LLM 推理加速领域取得显著突破（单用户速度提升 85%、高并发场景有效吞吐翻 4 倍），但其技术细节涉及系统工程与模型协同设计的复杂权衡。Fireworks AI 联合创始人兼 CTO、PyTorch 核心维护者 Dmytro Dzhulgakov 已将整篇论文梳理为 10 个递进式概念。需要系统学习并沉淀为一份结构清晰、通俗易懂的 wiki 教程，便于团队不同技术水平的成员快速理解这套端到端推理加速方案。

## What Changes
- 新增 wiki 教程文档 `docs/knowledge/learning/dspark-paper-wiki.md`，作为 DSpark 论文的系统性学习资料
- 文档包含目录导航系统，覆盖 10 个核心概念的递进式讲解
- 整理论文的关键性能数据、对比基线、工程权衡点
- 提供 DeepSpec 开源训练库的使用指引与资源链接
- 在 `docs/knowledge/README.md` 知识库索引中登记新增的学习文档
- **BREAKING**: 无破坏性变更（纯新增文档）

## Impact
- Affected specs: 无（独立新增学习文档）
- Affected code:
  - 新增 `docs/knowledge/learning/dspark-paper-wiki.md`
  - 修改 `docs/knowledge/README.md`（追加索引条目）

## Background & Context
- **论文**: DSpark（梁文锋署名的 DeepSeek 新论文）
- **拆解者**: Dmytro Dzhulgakov（Fireworks AI 联合创始人兼 CTO、PyTorch 核心维护者）
- **核心性能**: 单用户速度提升 85%、高并发有效吞吐翻 4 倍
- **基线对比**: 论文中所有加速数字均对比 MTP-1 基线（DeepSeek-V3 已采用的优化方案）
- **核心思想**: 系统工程与模型协同设计，将算法、调度、硬件适配三位一体闭环
- **开源资产**: DeepSpec 全栈训练库（GitHub 1.4k Star），支持 Eagle3、DFlash、DSpark 三种草稿模型，适配 Qwen3、Gemma
- **原文来源**: 量子位公众号文章，链接：https://mp.weixin.qq.com/s/BVlgO1e6StBGIaxGPTQIXQ
- **论文地址**: https://github.com/deepseek-ai/DeepSpec/blob/main/DSpark_paper.pdf

## ADDED Requirements

### Requirement: Wiki 教程文档主框架
系统 SHALL 提供一份 Markdown 格式的 wiki 教程文档，放置在 `docs/knowledge/learning/dspark-paper-wiki.md`，文档顶部包含完整的目录导航系统，所有章节通过锚点链接支持跳转。

#### Scenario: 用户打开文档导航
- **WHEN** 用户打开 `dspark-paper-wiki.md`
- **THEN** 文档顶部展示完整目录，覆盖 10 个核心概念、性能数据、FAQ、资源链接等章节
- **AND** 每个目录条目是可点击的锚点链接，能跳转到对应章节

### Requirement: 核心观点与论文主旨阐述
系统 SHALL 在文档开篇阐述 DSpark 论文的核心观点：真正的精髓在于系统工程与模型协同设计，将已有基础思路融合为自适应完整系统。

#### Scenario: 读者理解论文主旨
- **WHEN** 读者阅读文档的"论文主旨"章节
- **THEN** 能够准确复述 DSpark 的核心创新是把并行和串行拼在一起各取所长
- **AND** 理解 60%–85% 的速度提升是在 MTP-1 已优化基线上再叠加的

### Requirement: 10 个核心概念递进式讲解
系统 SHALL 按论文拆解者给出的逻辑顺序，逐个讲解 10 个核心概念，每个概念包含：定义、原理、关键数据、与前序概念的关联。

#### Scenario: 概念递进学习
- **WHEN** 读者按顺序阅读 10 个概念章节
- **THEN** 能够理解从 GPU 访存特性 → 推测解码 → 草稿模型 → 工程权衡 → DSpark 创新方案的完整逻辑链
- **AND** 每个概念章节包含关键性能数据（如接受长度提升百分比、延迟开销等）

#### Scenario: 关键概念交叉引用
- **WHEN** 读者阅读"DSpark≈Eagle+DFlash"章节
- **THEN** 文档明确引用前序的 Eagle/MTP 与 DFlash 概念，说明 DSpark 如何取两者所长
- **AND** 提供 26%–31%（vs Eagle3）和 16%–18%（vs DFlash）的接受长度对比数据

### Requirement: 关键性能数据与对比基线
系统 SHALL 整理论文中的所有关键性能数据，包括但不限于：单用户速度提升、高并发吞吐、接受长度对比、延迟开销、校准误差等，并明确标注对比基线。

#### Scenario: 数据可追溯
- **WHEN** 读者查阅性能数据章节
- **THEN** 每个数据点都标注对比基线（如 MTP-1、Eagle3、DFlash）
- **AND** 包含至少以下数据：85% 单用户速度提升、4 倍高并发吞吐、26%–31% 接受长度提升（vs Eagle3）、0.2%–1.3% 额外延迟、3%–8% → 1% 校准误差

### Requirement: 工程权衡点分析
系统 SHALL 单独章节分析 DSpark 的工程权衡哲学：不是越复杂越好，而是找到成本和收益的最优折中。

#### Scenario: 权衡点理解
- **WHEN** 读者阅读工程权衡章节
- **THEN** 理解三根杠杆（猜得更快、猜得更准、验得更聪明）的协同设计
- **AND** 理解马尔可夫头（rank 256）vs RNN 头的取舍决策（默认马尔可夫头，因 RNN 增益有限）

### Requirement: DeepSpec 开源库使用指引
系统 SHALL 提供 DeepSpec 开源训练库的使用指引，包含 GitHub 地址、支持的草稿模型类型、适配的外部模型、二次开发入口。

#### Scenario: 开发者上手 DeepSpec
- **WHEN** 开发者阅读 DeepSpec 章节
- **THEN** 获得 GitHub 仓库地址（含 1.4k Star 现状）
- **AND** 了解 Eagle3、DFlash、DSpark 三种草稿模型训练代码均已开源
- **AND** 知晓支持的 external model 包括 Qwen3、Gemma

### Requirement: FAQ 常见问题解答
系统 SHALL 提供 FAQ 章节，解答读者学习 DSpark 时可能遇到的常见问题。

#### Scenario: 读者疑问被解答
- **WHEN** 读者查阅 FAQ
- **THEN** 至少覆盖以下问题：DSpark 与 Eagle3/DFlash 的本质区别、为何默认用马尔可夫头而非 RNN 头、可变长度草稿如何动态决策、在线校准如何工作、如何用 DeepSpec 训练自己的草稿器

### Requirement: 资源链接汇总
系统 SHALL 在文档末尾汇总所有相关资源链接，包括原文、论文 PDF、DeepSpec GitHub、参考推文等。

#### Scenario: 链接有效可达
- **WHEN** 用户点击资源链接
- **THEN** 链接指向正确的资源页面（原文、论文 PDF、GitHub 仓库、参考推文）
- **AND** 链接以 Markdown 标准链接格式呈现

### Requirement: 知识库索引登记
系统 SHALL 在 `docs/knowledge/README.md` 的学习类目下登记新增的 DSpark 学习文档条目。

#### Scenario: 索引可发现
- **WHEN** 用户浏览 `docs/knowledge/README.md`
- **THEN** 能够在 learning 类目下看到 DSpark 论文学习 wiki 的条目
- **AND** 条目包含文档标题与相对路径链接

## Non-Functional Requirements
- **NFR-1**: 文档语言使用标准现代汉语，逻辑严谨，对不同技术水平的读者友好（关键术语附英文原文）
- **NFR-2**: 在适当位置引用原网页内容作为参考依据，不添加未经验证的信息
- **NFR-3**: 文档结构清晰，使用 Markdown 标准标题层级（H1/H2/H3）、列表、表格、引用块
- **NFR-4**: 文件命名遵循 kebab-case 纯英文规范（`dspark-paper-wiki.md`），通过 `python .agents/scripts/check-filename-convention.py` 校验
- **NFR-5**: 文档篇幅适中（预估 3000–5000 字），重点突出，避免冗余

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范与原子化原则
- **Business**: 基于公开文章与论文内容创建，不得添加未验证的推测性信息
- **Dependencies**: 网页内容已通过 defuddle 工具成功获取并解析

## Assumptions
- 读者已了解大模型推理的基本流程（自回归生成）
- 读者具备基础的 GPU/显存概念认知
- 读者可以访问互联网查阅论文原文与 GitHub 仓库

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: `docs/knowledge/learning/dspark-paper-wiki.md` 包含目录导航、论文主旨、10 个核心概念、性能数据、工程权衡、DeepSpec 指引、FAQ、资源链接等完整章节
- **Verification**: `human-judgment`

### AC-2: 目录导航系统可用
- **Given**: 用户打开 wiki 教程文档
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录包含所有章节的锚点链接，点击可跳转
- **Verification**: `programmatic`

### AC-3: 10 个核心概念讲解完整
- **Given**: 用户阅读核心概念章节
- **When**: 用户按顺序阅读 10 个概念
- **Then**: 用户能够阐述 DSpark 的核心创新（并行骨干 + 顺序头的混合方案）
- **Verification**: `human-judgment`

### AC-4: 性能数据可追溯
- **Given**: 用户查阅性能数据章节
- **When**: 用户检查每个数据点
- **Then**: 每个数据都标注对比基线，数据准确无臆造
- **Verification**: `human-judgment`

### AC-5: 工程权衡点分析清晰
- **Given**: 用户阅读工程权衡章节
- **When**: 用户理解三根杠杆的协同设计
- **Then**: 用户能够解释为何默认使用马尔可夫头而非 RNN 头
- **Verification**: `human-judgment`

### AC-6: DeepSpec 使用指引可用
- **Given**: 开发者阅读 DeepSpec 章节
- **When**: 开发者按指引访问 GitHub 仓库
- **Then**: 能够找到 Eagle3、DFlash、DSpark 三种草稿模型的训练代码
- **Verification**: `programmatic`

### AC-7: FAQ 章节实用
- **Given**: 用户遇到疑问
- **When**: 用户查阅 FAQ
- **Then**: 至少 5 个常见问题被解答
- **Verification**: `human-judgment`

### AC-8: 资源链接有效
- **Given**: 用户点击资源链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的资源页面（原文、论文 PDF、GitHub、参考推文）
- **Verification**: `programmatic`

### AC-9: 知识库索引已登记
- **Given**: wiki 文档创建完成
- **When**: 用户浏览 `docs/knowledge/README.md`
- **Then**: learning 类目下出现 DSpark 学习文档条目
- **Verification**: `programmatic`

### AC-10: 文件命名规范合规
- **Given**: wiki 文档创建完成
- **When**: 运行 `python .agents/scripts/check-filename-convention.py`
- **Then**: `dspark-paper-wiki.md` 通过命名规范校验
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要为 10 个核心概念创建独立的原子化子文档（类似 `agent-communication-protocols/` 目录结构），还是单文件 wiki 形式更合适？（倾向：单文件，因概念间强耦合，递进式阅读更有效）
- [ ] 是否需要在文档中加入 Mermaid 流程图来可视化 DSpark 的两步架构（并行骨干 + 顺序头）？（倾向：加入 1-2 张图增强可读性）
