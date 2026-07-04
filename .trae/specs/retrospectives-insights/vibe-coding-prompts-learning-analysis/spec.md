# Vibe Coding 两大神级 Prompt 学习分析 Spec

## Why

网页 `https://mp.weixin.qq.com/s/umPqTD_-IubbhXIgiS47eQ` 是数字生命卡兹克撰写的一篇关于 Vibe Coding 实战技巧的文章,系统阐述了两个被作者称为"神级 Prompt"的核心技巧——**第一性原理**与**对抗式审查**。这两个技巧构成了 Vibe Coding 的"生成—验证"完整闭环,对本项目 AI 智能体开发实践具有直接的参考与借鉴价值。需要通过系统学习与分析,将其方法论沉淀为可复用的知识资产。

## What Changes

- 新增 Vibe Coding 两大 Prompt 学习分析文档,完整解析文章核心观点、案例与方法论
- 提炼"第一性原理"Prompt 的使用场景、调用方式与底层机理
- 提炼"对抗式审查"Prompt 的执行模式、多 Agent 协同策略与典型 BUG 类型
- 总结两大 Prompt 构成的闭环逻辑及其在代码之外的延伸应用
- 将分析成果归档至 `docs/knowledge/learning/` 目录,并更新知识库索引

## Impact

- Affected specs: 无直接影响,属于新增学习类知识资产
- Affected code: 无代码改动,仅新增 Markdown 文档
- Affected docs: `docs/knowledge/learning/` 新增学习分析文档;`docs/knowledge/README.md` 索引需同步更新

## ADDED Requirements

### Requirement: 学习分析文档内容完整性

学习分析文档 SHALL 包含以下核心章节:

1. **文章基本信息**:标题、作者、来源、主题概述
2. **核心观点提炼**:第一性原理与对抗式审查的定义、定位与关系
3. **第一性原理深度解析**:
   - Prompt 的具体形式("从第一性原理出发")
   - 底层机理:打断 AI 类比推理,回到事实本质重新推导
   - 实战案例:AIHOT 飞书推送 BUG 修复(治标 vs 治本)
   - 跨领域案例:马斯克 SpaceX 火箭成本重构
4. **对抗式审查深度解析**:
   - Prompt 的具体形式("开启多 Agent 进行对抗式审查")
   - 执行模式:多 Agent 并发、攻击者视角
   - 典型 BUG 类型:OOM 死循环、未来时间污染、性能炸弹、缓存穿透假阳性
   - 工具实践:Claude Code Ultracode(动态工作流)、Codex 多 Agent
5. **闭环逻辑分析**:第一性原理管生成、对抗式审查管验证的协同关系
6. **延伸应用**:写作审查、商业方案审视、人生决策的迁移价值
7. **对本项目的启示**:可复用到 SpecWeave 智能体开发的方法论要点
8. **FAQ 与延伸资源**

#### Scenario: 读者快速掌握两大 Prompt 用法

- **WHEN** 读者阅读学习分析文档
- **THEN** 能够理解第一性原理与对抗式审查的核心定义、调用方式与适用场景
- **AND** 能够在自己的 Vibe Coding 实践中直接套用这两个 Prompt

#### Scenario: 团队成员借鉴方法论改进开发流程

- **WHEN** 项目成员查阅文档的"对本项目的启示"章节
- **THEN** 能够识别出可复用到 SpecWeave 智能体开发的具体改进点
- **AND** 能够将对抗式审查思路应用到代码审查工作流中

### Requirement: 文档结构规范

学习分析文档 SHALL 遵循以下结构规范:

- 文件路径:`docs/knowledge/learning/vibe-coding-prompts-learning-analysis.md`
- 文件名使用 kebab-case 纯英文命名
- 包含目录导航系统(TOC)
- 关键概念使用加粗或引用块突出
- 案例部分使用代码块或引用块呈现关键对话
- 文末包含参考资料链接与原文出处

#### Scenario: 文档命名与路径合规

- **WHEN** 文档创建完成
- **THEN** 文件位于 `docs/knowledge/learning/` 目录下
- **AND** 文件名为 `vibe-coding-prompts-learning-analysis.md`
- **AND** 通过文件名规范检查脚本验证

### Requirement: 知识库索引同步更新

文档创建后 SHALL 同步更新 `docs/knowledge/README.md` 索引:

- 在"学习类"或对应分类下新增条目
- 条目包含文档标题与相对路径链接
- 保持索引整体格式一致

#### Scenario: 索引条目正确添加

- **WHEN** 学习分析文档创建完成
- **THEN** `docs/knowledge/README.md` 中新增对应索引条目
- **AND** 索引链接指向正确的相对路径

## MODIFIED Requirements

无

## REMOVED Requirements

无
