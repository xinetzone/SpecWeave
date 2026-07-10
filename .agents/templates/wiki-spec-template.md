---
id: "templates-wiki-spec-template"
title: "Wiki教程制作标准工作流模板"
source: "retrospective-competitive-analysis-text-to-cad"
x-toml-ref: "../../.meta/toml/.agents/templates/wiki-spec-template.toml"
version: "1.2.0"
patterns_applied: ["meta-document-leverage", "entry-container-separation", "spec-driven-development", "knowledge-base-three-stage"]
---
# Wiki教程制作标准工作流模板

> 本模板整合"网页→wiki四层信息加工漏斗模型"，用于指导外部资源学习类wiki教程的创建。
> 使用方法：复制本模板，替换所有 `{{占位符}}` 内容，按四层漏斗逐步推进，即可生成高质量的wiki教程。
>
> **L3标准化模式集成**：本模板已应用以下L3标准化模式——
> - [meta-document-leverage](../../docs/retrospective/patterns/methodology-patterns/document-architecture/meta-document-leverage.md)：元文档杠杆效应，先更新索引再写内容
> - [entry-container-separation](../../docs/retrospective/patterns/methodology-patterns/document-architecture/entry-container-separation.md)：入口-容器二元架构，索引页精简<100行
> - [spec-driven-development](../../docs/retrospective/patterns/methodology-patterns/creative-design/spec-driven-development.md)：Spec驱动开发，先spec再执行

---

## ⚠️ 强制前置检查（必须先完成）

> **格式一致性优先原则**：创建新文件前，必须先读取同目录现有文件确认格式，本模板和project_memory仅作参考。

### 第一步：确认wiki类型（单文件 vs 原子化）

根据spec.md中的原子化决策，确定本次wiki的类型，不同类型使用不同frontmatter规范：

| 类型 | 判断标准 | frontmatter必填字段（YAML） | 参考示例 |
|------|---------|---------------------------|---------|
| **单文件wiki** | spec决策为"保持单文件"（<300行或章节独立性低） | `title`, `source`, `date`, `tags`（4个，不多不少） | `sunlogin-security-wiki.md`, `sunlogin-bootbox-analysis.md` |
| **原子化wiki** | spec决策为"需要拆分"（>300行或章节独立性高） | `id`, `title`, `source`, `x-toml-ref`（4个，其余元数据放TOML） | `mopmonk-security-agent-wiki/00-overview.md` |

**单文件wiki frontmatter标准模板**（禁止添加author/version等额外字段）：
```yaml
---
title: "{{中文完整标题}}"
source: "{{原始URL或来源描述}}"
date: "{{YYYY-MM-DD}}"
tags: ["tag1", "tag2", "..."]
---
```

**原子化wiki frontmatter标准模板**（禁止添加category/date/tags等应在TOML中的字段）：
```yaml
---
id: "{{wiki-name}}-{{chapter-id}}"
title: "{{章节标题}}"
source: "{{来源URL或父文件路径}}"
x-toml-ref: "{{正确计算的相对路径}}"
---
```

### 第二步：确认现有wiki格式规范

1. 读取 `docs/knowledge/learning/` 下1-2个现有wiki文档（优先选择最近创建的或结构类似的）
2. 对照第一步的字段清单，确认所选参考文档的frontmatter字段是否一致
3. 确认以下格式细节，**必须以现有文档实际做法为准**：
   - [ ] frontmatter字段：与第一步确定的类型对应的4个字段完全一致，无多余字段
   - [ ] 链接格式：确认相对路径写法（如`./01-xxx.md`、`../`层级等）
   - [ ] 章节风格：确认标题层级、列表风格、表格格式
   - [ ] 命名规范：确认文件夹命名、文件编号规则
   - [ ] **三级标题编号**：单文件wiki中三级标题格式为"x.y"（如1.1、2.3），从x.1开始连续编号，**禁止使用x.0**
4. 参考示例目录：
   - `docs/knowledge/learning/07-vendor-product-learning/sunlogin/sunlogin-security-wiki.md`（单文件wiki示例）
   - `docs/knowledge/learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/`（原子化wiki示例）

### 第三步：禁止凭记忆做格式决策

- ❌ 不要仅凭project_memory中的描述决定格式
- ❌ 不要仅凭本模板的示例做最终决策
- ❌ 不要在frontmatter中添加"看起来有用"的额外字段（如author/version/category）
- ✅ 必须以同目录现有同类文档的实际做法为权威标准
- ✅ 如果发现本模板/规范与实际文档不一致，以实际文档为准

---

## 📚 四层信息加工漏斗模型

本工作流采用四层漏斗式信息加工，确保从原始网页到成品wiki的质量逐级提升：

| 层级 | 名称 | 目标 | 工具/方法 | 产出物 |
|------|------|------|-----------|--------|
| **L1** | 原始网页层 | 提取干净内容，去噪 | defuddle CLI | 干净的markdown文本 |
| **L2** | 干净文本层 | 验证完整性，识别核心 | 人工阅读+标记 | 核心观点/概念/结构笔记 |
| **L3** | 结构化大纲层 | 设计信息架构 | 章节划分+目录设计 | spec.md + tasks.md |
| **L4** | wiki成品层 | 生成完整文档 | 按骨架填充内容 | 带frontmatter的完整wiki |

### L1 原始网页层：内容提取

**目标**：从原始网页中提取干净、无噪音的核心内容。

**操作步骤**：
1. 使用defuddle工具提取网页内容：
   ```bash
   defuddle parse "{{网页URL}}" --md > {{source-raw.md}}
   ```
   > ⚠️ **URL必须用引号包裹**：避免URL中的`&`截断参数（如微信公众号URL常包含`&color_scheme=light`）。

2. **微信公众号文章特殊处理**：
   - WebFetch通常无法获取（需要认证/Cookie），必须使用defuddle提取
   - 如果defuddle输出仍为HTML而非Markdown，说明URL参数被截断，检查引号是否正确
   - 若defuddle提取不完整，可尝试使用`kimi-webbridge`（控制真实浏览器）作为备选方案
   - 提取后需手动解析HTML内容去除标签，获得干净文本

3. 提取后检查：
   - [ ] 导航栏、广告、评论区、相关推荐等噪音是否已去除
   - [ ] 正文标题、段落、列表、代码块是否完整保留
   - [ ] 图片链接是否有效
4. 如果defuddle效果不佳，可改用web-to-markdown技能作为备选

**产出**：`{{source-clean.md}}` - 去噪后的干净markdown文本

### L2 干净文本层：内容分析

**目标**：理解并标记核心内容，为结构化做准备。

**操作步骤**：
1. 通读干净文本，回答以下问题：
   - 这篇文章/资源的核心主题是什么？（一句话总结）
   - 作者的核心观点/主张有哪些？（3-5条）
   - 有哪些关键概念/术语需要解释？
   - 内容的逻辑结构是怎样的？（问题→方案→论证→总结？）
2. 标记内容：
   - 🔴 核心观点（必须保留）
   - 🟡 支撑论据/案例（选择性保留）
   - 🟢 扩展阅读/背景信息（可简化/链接）
   - ⚫ 广告/无关内容（直接删除）
3. 验证内容完整性：确认没有遗漏关键论点、数据、步骤

**产出**：在干净文本上添加标记注释，或单独写一份分析笔记

### L3 结构化大纲层：信息架构设计

**目标**：设计wiki的章节结构、目录导航、逻辑组织，输出spec规划。

**操作步骤**：
1. 根据L2的分析，设计wiki的章节划分（参考下方"8章节标准结构"）
2. 创建spec规划文件：
   - `spec.md`：需求与范围说明
   - `tasks.md`：任务拆解清单
   - `checklist.md`：质量检查点
3. 设计章节间的逻辑关系：确保读者可以按顺序学习，也可以按需跳转
4. 设计目录导航：在overview页提供清晰的章节索引

**产出**：完整的spec规划文档集

#### AI辅助大纲生成Prompt原型

在L3层，可以使用以下Prompt从L2层的干净文本自动生成结构化大纲，提高效率。使用前请确保已完成L2层的内容通读和核心观点标记。

**使用方法**：将下方Prompt与干净文本一起发送给AI，即可获得符合8章节标准结构的大纲。

```markdown
你是一位专业的技术wiki编辑，擅长从外部资源中提炼结构化的学习教程。请根据我提供的干净网页Markdown文本，为我生成一份符合标准wiki结构的大纲。

## 输入
我将提供一段经过defuddle提取去噪的干净网页Markdown文本（L2层产物）。

## 输出要求
请输出以下内容：

### 1. Frontmatter字段建议
为每个章节文件建议合适的frontmatter字段，格式如下（YAML格式）：
```yaml
---
id: "{{wiki-name}}-{{chapter-id}}"
title: "{{章节标题}}"
category: learning
tags: ["tag1", "tag2", "tag3"]
date: "{{自动填充当前日期YYYY-MM-DD格式}}"
status: draft
source: "{{原始URL}}"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/{{wiki-name}}/{{chapter-file}}.toml"
---
```

### 2. 8章节标准wiki大纲结构
请严格按照以下8章节结构设计大纲，每个章节列出小节标题和核心内容要点：

| 文件 | 章节 | 内容要求 |
|------|------|---------|
| 00-overview.md | 概述 | 背景介绍、核心主题、学习目标（3-5条）、前置知识、文档导航表 |
| 01-core-concepts.md | 核心功能/概念 | 核心概念解释、关键功能、原理说明、术语对照表 |
| 02-installation.md | 安装指南 | 环境要求、安装步骤、验证安装方法 |
| 03-usage.md | 使用流程 | 快速上手（3步以内）、典型使用场景、代码/命令示例 |
| 04-limitations.md | 局限性 | 不适用场景、已知问题/陷阱、与其他方案的对比表 |
| 05-summary.md | 总结 | 核心要点回顾、关键takeaway（3-5条）、下一步学习建议 |
| 06-faq.md | FAQ | 5-8个读者最可能遇到的问题及简明答案 |
| 07-resources.md | 资源链接 | 原始资源、官方资源、相关学习资源、本项目内相关wiki |

### 3. 大纲输出格式
请使用Markdown格式输出，每个章节包含：
- 章节ID和文件名
- 章节标题
- 2-5个小节标题
- 每个小节的核心内容要点（3-5条，用bullet points）
- 该章节是否有表格/代码块/特殊内容的提示

## 注意事项
1. 客观真实：尤其是"局限性"章节，必须如实说明，不要刻意美化
2. 实用导向：内容要面向学习者，"使用流程"章节必须有可复现的示例
3. 逻辑连贯：章节之间要有递进关系，读者可以按顺序学习
4. frontmatter中的date字段请使用今天的日期：{{替换为当前日期}}
5. source字段填写原始资源URL：{{替换为实际URL}}
6. wiki-name请根据内容提炼一个kebab-case风格的英文名称

---
以下是干净的网页Markdown文本：
```

**使用说明**：
- 使用时将 `{{替换为当前日期}}` 和 `{{替换为实际URL}}` 替换为真实值
- 将干净的Markdown文本粘贴在Prompt末尾
- AI生成的大纲需要人工审核调整后再进入L4层文档生成
- 建议先让AI生成大纲，再根据实际内容调整章节划分和内容分配

### L4 wiki成品层：文档生成

**目标**：按照spec和结构骨架，生成完整的wiki文档。

**操作步骤**：
1. 创建wiki目录：`docs/knowledge/learning/{{wiki-name}}/`
2. 按8章节标准结构创建各章节md文件
3. 每个文件添加正确的YAML frontmatter
4. 填充内容，添加内部链接（相对路径）
5. 在00-overview.md中添加文档导航表
6. 运行质量检查清单

**产出**：可直接使用的完整wiki教程

---

## 📋 Spec规划模板

### spec.md 骨架

```markdown
# {{Wiki标题}} Spec

## 1. 资源来源
- 原始URL：{{URL}}
- 资源类型：文章/论文/文档/视频/其他
- 作者/来源：{{作者或网站名}}
- 提取时间：{{YYYY-MM-DD}}

## 2. 核心主题与目标
- 一句话总结：{{...}}
- 学习目标：读者学完后能做什么？（3-5条）
- 目标读者：谁应该读这个wiki？
- 前置知识：需要什么基础？

## 3. 信息架构设计
### 章节划分
| 文件 | 章节标题 | 核心内容 |
|------|---------|---------|
| 00-overview.md | 概述 | 背景、学习目标、导航 |
| 01-{{...}}.md | 核心功能/概念 | ... |
| ... | ... | ... |
| 10-resources.md | 资源链接 | 原文、相关资源 |

### 逻辑组织方式
- [ ] 线性递进（适合教程类）
- [ ] 主题模块化（适合参考类）
- [ ] 问题-方案式（适合问题解决类）

### 🔍 原子化决策（必须明确选择）

> 根据以下判断标准，在Spec阶段就明确本wiki是否需要原子化拆分，避免后期追加。

**判断标准**（满足任一条件即建议拆分）：
| 判断维度 | 拆分阈值 | 本wiki预估 |
|---------|---------|-----------|
| 内容长度 | 预计>300行建议拆分，<200行可保持单文件 | 预计约____行 |
| 章节独立性 | 各章节是否可单独阅读/引用？ | □是 □否 |
| 未来扩展 | 是否预期会持续新增章节/内容？ | □是 □否 |
| 复用需求 | 单个章节是否会被其他文档引用？ | □是 □否 |

**决策结果**：
- [ ] **需要原子化拆分**：采用"索引页(xxx-wiki.md) + 目录(xxx-wiki/) + 数字前缀原子文件"结构，进入L5原子化拆分阶段
- [ ] **保持单文件**：所有内容在一个md文件中，不进入L5阶段。理由：____（说明为什么不满足拆分阈值）

```

### tasks.md 骨架

```markdown
# {{Wiki标题}} Tasks

## L1 内容提取
- [ ] 使用defuddle提取原始网页
- [ ] 验证提取质量，去噪
- [ ] 保存为clean-source.md

## L2 内容分析
- [ ] 通读并标记核心观点
- [ ] 识别关键概念
- [ ] 梳理逻辑结构
- [ ] 验证内容完整性

## L3 结构设计
- [ ] 完成spec.md（含DoD完成定义）
- [ ] **原子化决策**：按4项判断标准评估，明确选择"需要拆分"或"保持单文件"，记录在spec.md中
- [ ] 设计章节结构（可参考8章节标准结构）
- [ ] 拆分内容到各章节
- [ ] 完成checklist.md（含子代理验收5点检查）
- [ ] 在tasks.md中预置原子化步骤（L5阶段，如决策为"需要拆分"则保留，否则标记为N/A）

## L4 文档生成（首次提交：内容创作提交）
- [ ] 创建wiki目录
- [ ] 创建所有章节文件并添加frontmatter（先以单文件形式或原子文件均可）
- [ ] 填充各章节内容
- [ ] 添加内部链接和导航表
- [ ] **子代理产出验收**：按5点检查清单逐项验证frontmatter格式
- [ ] 运行文件名规范检查
- [ ] 原子提交1（commit: docs(knowledge): 创建{{Wiki标题}}Wiki教程）

## L5 原子化拆分（第二次提交：结构重构提交，如spec决策为"需要拆分"时执行）
- [ ] 将单文件wiki拆分为目录原子结构（按决策执行）
- [ ] 创建索引页xxx-wiki.md（含导航表格，无深度内容）
- [ ] 迁移内容到xxx-wiki/目录下的两位数字前缀原子文件
- [ ] 为每个原子文件添加正确frontmatter和source溯源
- [ ] 创建配套TOML元数据文件
- [ ] 运行文件名规范检查验证
- [ ] 原子提交2（commit: docs(knowledge): 原子化拆分{{Wiki标题}}Wiki教程）

## L6 收尾验证
- [ ] 运行fix-x-toml-ref.py自动修复x-toml-ref路径并创建缺失TOML文件：`python .agents/scripts/fix-x-toml-ref.py --dir <wiki目录> --write --create-toml`
- [ ] 运行check-links.py验证所有链接有效
- [ ] 运行check-filename-convention.py验证文件名规范
- [ ] 确认工作区无无关文件混入
- [ ] **指令集评估**：知识库建成后，执行第一性原理分析判断是否需要配套指令集（参考 [knowledge-to-command-pipeline](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/knowledge-to-command-pipeline.md) 六步转化流程），评估结果记录在spec.md Open Questions中
```

### 标准完成定义（DoD）

Wiki教程任务完成必须满足以下全部条件：

| 阶段 | 完成标准 | 验证方式 |
|------|---------|---------|
| 内容完整性 | 六大要素齐全（概述/核心概念/操作指南/FAQ/资源链接/学习目标） | 人工检查 |
| 格式规范 | frontmatter使用YAML（---）：单文件wiki仅含title/source/date/tags四字段；原子化wiki含id/title/source/x-toml-ref四字段且路径正确 | 5点检查清单 |
| 元数据配套 | 原子化wiki：.meta/toml/镜像路径下有对应TOML文件；单文件wiki：不需要TOML文件 | fix-x-toml-ref.py --create-toml（仅原子化） |
| 原子化结构 | 需要拆分的wiki已原子化（索引页+目录+数字前缀原子文件），保持单文件的wiki在spec.md中有明确决策依据 | 文件结构+spec检查 |
| 链接有效 | 所有内部相对路径可到达，无断链 | check-links.py（仅原子化wiki） |
| 标题编号 | 单文件wiki三级标题从x.1开始连续编号（如1.1、2.1），禁止使用x.0 | 人工检查 |
| 自动化验证 | fix-x-toml-ref.py、check-links.py、check-filename-convention.py 三重验证通过 | 工具输出确认 |
| 指令集评估 | 知识库建成后，reviewer执行第一性原理分析判断是否需要配套指令集（认知方法→指令集，自动化工具→Skill），评估结果记录在spec.md中 | spec.md Open Questions章节 |
| 原子提交 | 内容创作和原子化拆分（如适用）为独立提交，单一职责 | git log验证 |
| 命名规范 | 文件名kebab-case、纯英文、原子文件两位数字前缀 | 文件名检查脚本 |

### checklist.md 骨架

```markdown
# {{Wiki标题}} Quality Checklist

## frontmatter规范（按wiki类型检查）
- [ ] **类型确认**：spec.md中已明确"单文件"或"原子化"决策
- [ ] 单文件wiki：frontmatter仅含title/source/date/tags四个字段，无多余字段（如author/version）
- [ ] 原子化wiki：frontmatter含id/title/source/x-toml-ref四个字段，路径正确
- [ ] 所有.md文件frontmatter使用YAML（---）格式，没有使用+++（TOML）

## 格式规范
- [ ] 链接使用相对路径，无死链（原子化wiki必须检查）
- [ ] 文件名符合kebab-case规范，纯英文无中文
- [ ] 原子文件编号正确（00-, 01-, ...）
- [ ] **三级标题编号**：单文件wiki中三级标题从x.1开始连续编号（如1.1、2.1），无x.0编号

## 内容质量
- [ ] 核心观点完整保留，无重大遗漏
- [ ] 关键概念解释清晰
- [ ] 章节逻辑连贯，无跳脱
- [ ] 代码/命令示例可验证
- [ ] 有明确的学习路径
- [ ] **参数完整性**（硬件/产品类wiki）：对照原始数据源逐一核对参数表，确保无遗漏参数

## 结构完整性
- [ ] 包含标准章节结构（按需调整）
- [ ] **原子化决策已明确**：spec.md中记录了"需要拆分"或"保持单文件"的决策及理由
- [ ] 如决策为原子化拆分：索引页有完整导航表，原子文件结构正确
- [ ] 如决策为保持单文件：文件<300行，决策理由充分
- [ ] FAQ覆盖常见疑问
- [ ] 资源链接有效且相关

## 子代理产出验收5点检查（强制！）
- [ ] ✅ **frontmatter分隔符正确**：使用`---`（YAML），不是`+++`（TOML）
- [ ] ✅ **x-toml-ref存在且路径正确**：指向.meta/toml/镜像路径，相对层级计算正确
- [ ] ✅ **标题层级从h1开始**：文件第一行是`# 标题`，无跳级
- [ ] ✅ **文件名合规**：kebab-case、纯英文、数字前缀正确（原子文件两位数字）
- [ ] ✅ **source溯源字段存在**：派生产物标注原始来源URL或父文件

## 元数据
- [ ] tags分类准确
- [ ] date字段正确
- [ ] status标记正确（draft/stable）
- [ ] x-toml-ref路径正确

## 自动化验证（提交前必做）
- [ ] `python .agents/scripts/fix-x-toml-ref.py --dir <wiki目录> --write --create-toml` 通过（x-toml-ref路径正确，0个需修复）
- [ ] `python .agents/scripts/check-links.py --path <wiki目录>` 通过（所有内部链接有效，无断链）
- [ ] `python .agents/scripts/check-filename-convention.py` 通过（暂存区文件符合kebab-case规范）
```

---

## 📄 Wiki文档8章节标准结构骨架

> 适用于大多数外部资源学习类wiki。可根据资源类型灵活调整章节名称，但应保持类似的逻辑递进。

### 00-overview.md（概述页）

```markdown
---
id: "{{wiki-name}}-overview"
title: "{{标题}}：概述与学习目标"
category: learning
tags: [{{tag1}}, {{tag2}}, ...]
date: "{{YYYY-MM-DD}}"
status: draft
author: "{{作者/整理者}}"
summary: "{{一句话摘要，介绍本wiki的核心内容和价值}}"
source: "{{原始URL}}"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/{{wiki-name}}/00-overview.toml"
---
# {{标题}}：概述与学习目标

## 背景

{{介绍资源来源、作者背景、为什么这个资源值得学习。2-3段。}}

## 核心主题

{{一句话说明本wiki讲的是什么，解决什么问题。}}

## 学习目标

通过本教程，你将能够：

1. {{目标1}}
2. {{目标2}}
3. {{目标3}}
...

## 前置知识

{{说明读者需要预先具备什么知识。无则填"无"。}}

## 文档导航

| 章节 | 内容 |
|------|------|
| [01 - 核心功能/概念](01-{{...}}.md) | {{说明}} |
| [02 - 安装指南](02-{{...}}.md) | {{说明}} |
| [03 - 使用流程](03-{{...}}.md) | {{说明}} |
| [04 - 局限性](04-{{...}}.md) | {{说明}} |
| [05 - 总结](05-{{...}}.md) | {{说明}} |
| [06 - FAQ](06-{{...}}.md) | {{说明}} |
| [07 - 资源链接](07-{{...}}.md) | {{说明}} |
```

### 01 - 核心功能/概念章

```markdown
---
id: "{{wiki-name}}-{{chapter}}"
title: "{{章节标题}}"
source: "{{source-ref}}"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/{{wiki-name}}/01-{{...}}.toml"
---
## 一、{{章节标题}}

{{核心内容：这是wiki的主体，详细讲解核心概念、功能、原理。}}

### 1.1 {{小节标题}}

{{内容}}

### 1.2 {{小节标题}}

{{内容}}

| 概念 | 说明 |
|------|------|
| {{term1}} | {{解释}} |
| {{term2}} | {{解释}} |
```

### 02 - 安装指南章（如适用）

```markdown
---
id: "{{wiki-name}}-installation"
title: "安装与配置指南"
source: "{{source-ref}}"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/{{wiki-name}}/02-installation.toml"
---
## 二、安装指南

### 2.1 环境要求

- {{要求1：如Python 3.10+}}
- {{要求2}}

### 2.2 安装步骤

```bash
{{安装命令1}}
{{安装命令2}}
```

### 2.3 验证安装

```bash
{{验证命令}}
# 预期输出：{{成功标志}}
```
```

### 03 - 使用流程章

```markdown
---
id: "{{wiki-name}}-usage"
title: "使用流程与实战示例"
source: "{{source-ref}}"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/{{wiki-name}}/03-usage.toml"
---
## 三、使用流程

{{按步骤讲解典型使用流程，配示例。}}

### 3.1 快速上手：三步完成第一个{{任务}}

**第1步：{{做什么}}**
```bash
{{命令/代码}}
```

**第2步：{{做什么}}**
```bash
{{命令/代码}}
```

**第3步：验证结果**
```bash
{{验证命令}}
```

### 3.2 {{典型场景/进阶用法}}

{{详细内容}}
```

### 04 - 局限性章（重要！）

```markdown
---
id: "{{wiki-name}}-limitations"
title: "局限性与注意事项"
source: "{{source-ref}}"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/{{wiki-name}}/04-limitations.toml"
---
## 四、局限性与注意事项

> 🎯 **重要**：客观介绍该技术/资源的局限性、适用边界、已知问题，避免读者踩坑。

### 4.1 不适用场景

| 场景 | 为什么不适用 | 建议替代方案 |
|------|-------------|-------------|
| {{场景1}} | {{原因}} | {{方案}} |
| {{场景2}} | {{原因}} | {{方案}} |

### 4.2 已知问题/陷阱

- ⚠️ **{{问题1}}**：{{具体说明，如何规避}}
- ⚠️ **{{问题2}}**：{{具体说明}}

### 4.3 与其他方案的对比

| 方案 | 优势 | 劣势 | 适用场景 |
|------|------|------|---------|
| {{本方案}} | | | |
| {{竞品A}} | | | |
```

### 05 - 总结章

```markdown
---
id: "{{wiki-name}}-summary"
title: "总结与回顾"
source: "{{source-ref}}"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/{{wiki-name}}/05-summary.toml"
---
## 五、总结

### 5.1 核心要点回顾

- ✅ {{要点1}}
- ✅ {{要点2}}
- ✅ {{要点3}}

### 5.2 关键 takeaway

{{3-5条最重要的收获，用自己的话总结。}}

### 5.3 下一步学习建议

- [ ] {{建议1：如"尝试动手做一个小项目"}}
- [ ] {{建议2：如"阅读进阶资源"}}
- [ ] {{建议3}}
```

### 06 - FAQ章

```markdown
---
id: "{{wiki-name}}-faq"
title: "常见问题（FAQ）"
source: "{{source-ref}}"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/{{wiki-name}}/06-faq.toml"
---
## 六、常见问题（FAQ）

### Q1: {{问题1}}？
**A**: {{答案}}

### Q2: {{问题2}}？
**A**: {{答案}}

### Q3: {{问题3}}？
**A**: {{答案}}
```

### 07 - 资源链接章

```markdown
---
id: "{{wiki-name}}-resources"
title: "资源与参考链接"
source: "{{source-ref}}"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/{{wiki-name}}/07-resources.toml"
---
## 七、资源链接

### 7.1 原始资源

- [{{原文标题}}]({{原始URL}}) - {{一句话说明}}

### 7.2 官方资源

- [{{官方文档}}]({{URL}})
- [{{GitHub仓库}}]({{URL}})

### 7.3 相关学习资源

- [{{相关教程1}}]({{URL}}) - {{说明}}
- [{{相关文章2}}]({{URL}}) - {{说明}}

### 7.4 本项目内相关wiki

- [{{相关wiki1}}](../{{related-wiki}}/00-overview.md)
```

---

## ✅ 质量检查清单

完成wiki后，逐项检查：

### 前置检查确认
- [ ] 已读取同目录1-2个现有wiki文档，确认格式规范
- [ ] 格式决策基于实际文档，而非仅凭记忆或本模板

### L1层检查
- [ ] 使用defuddle正确提取了网页内容
- [ ] 导航、广告、评论等噪音已去除
- [ ] 正文内容完整保留

### L2层检查
- [ ] 已识别出3-5个核心观点
- [ ] 关键概念已标记并计划解释
- [ ] 内容完整性已验证，无重大遗漏

### L3层检查
- [ ] spec.md已完成，范围清晰（遵循[spec-driven-development](../../docs/retrospective/patterns/methodology-patterns/creative-design/spec-driven-development.md)模式）
- [ ] tasks.md已拆解，任务可执行
- [ ] 章节划分合理，逻辑连贯
- [ ] 8章节结构骨架已确定
- [ ] **元文档优先检查**（[meta-document-leverage](../../docs/retrospective/patterns/methodology-patterns/document-architecture/meta-document-leverage.md)）：先设计00-overview.md的导航结构，再填充各章节深度内容
- [ ] **入口精简检查**（[entry-container-separation](../../docs/retrospective/patterns/methodology-patterns/document-architecture/entry-container-separation.md)）：原子化wiki的索引页（00-overview.md）控制在<100行，仅含导航+学习目标，不放深度内容

### L4层检查
- [ ] 所有文件有正确的YAML frontmatter（---分隔）
- [ ] 单文件wiki：frontmatter仅含title/source/date/tags四个字段，无多余字段
- [ ] 原子化wiki：id/title/source/x-toml-ref字段完整且路径正确
- [ ] 单文件wiki三级标题从x.1开始连续编号，无x.0编号
- [ ] 硬件/产品类wiki：参数表对照原始数据源逐一核对，无遗漏
- [ ] 所有内部链接使用相对路径，无死链（原子化wiki必须检查）
- [ ] 文件名使用kebab-case，纯英文无中文
- [ ] 原子文件编号正确（00-07）
- [ ] 00-overview.md有完整的文档导航表（原子化wiki）
- [ ] 局限性章节客观真实，不夸大优点
- [ ] FAQ覆盖读者可能遇到的问题
- [ ] 资源链接有效
- [ ] tags分类准确，date字段正确
- [ ] 已运行 `python .agents/scripts/check-filename-convention.py` 验证文件名

---

## 路径引用说明

- 模板内部路径参考：本模板位于 `d:\AI\.agents\templates\wiki-spec-template.md`
- wiki输出目录：`d:\AI\docs\knowledge\learning\{{wiki-name}}\`
- TOML元数据路径：`d:\AI\.meta\toml\docs\knowledge\learning\{{wiki-name}}\`
- 相对路径规则：
  - 从wiki子目录到 `.meta/toml/`：`../../../../.meta/toml/...`（4层上级）
  - 同目录文件：`./{{filename}}.md`
  - 相邻wiki：`../{{other-wiki}}/00-overview.md`

### 🛠️ 自动化工具（推荐使用）

**不要手动计算`../`层数**，使用以下工具自动处理x-toml-ref路径和TOML文件创建：

```bash
# 预览：检查x-toml-ref路径是否正确，预览需要创建的TOML文件
python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/{{wiki-name}}/ --dry-run --create-toml

# 执行：自动修复x-toml-ref路径 + 创建缺失的TOML骨架文件
python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/{{wiki-name}}/ --write --create-toml

# 单个文件处理
python .agents/scripts/fix-x-toml-ref.py --file docs/knowledge/learning/{{wiki-name}}.md --write --create-toml
```

工具功能：
- 自动计算正确的`../`层级（无需手动数）
- 自动修复或添加x-toml-ref字段（保持id→title→source→x-toml-ref字段顺序）
- `--create-toml`自动在.meta/toml/镜像路径创建TOML骨架文件（含id/title/category/date/version）
- `--dry-run`安全预览，不实际写入文件
