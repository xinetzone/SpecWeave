# 毕业论文写作指导角色（Thesis Advisor）Spec

## Why
现有 `.agents/roles/` 仅覆盖软件工程角色（编排/架构/开发/审查/测试/联合创始），缺少面向学术写作场景的指导角色。用户专业为语言学及应用语言学，需要一个系统阐述学术论文完整写作流程、并提供阶段化操作指南与专业差异化建议的角色，帮助完成从开题到答辩的全过程。

## What Changes
- 新增角色定义文件 [.agents/roles/thesis-advisor.md](.agents/roles/thesis-advisor.md)：包含角色描述、职责清单、非目标边界
- 新增角色元数据 [.meta/toml/.agents/roles/thesis-advisor.toml](.meta/toml/.agents/roles/thesis-advisor.toml)：声明 id/domain/layer/tier 与绑定资源
- 更新 [.agents/roles/README.md](.agents/roles/README.md)：在角色职责矩阵中追加论文指导者条目，并扩展文件结构说明

## Impact
- Affected specs: 角色定义索引（roles/README.md）、能力注册中心（capability-registry.md 可选关联）
- Affected code: 无业务代码影响；仅为 `.agents/` 规范资产的增量扩展

## ADDED Requirements

### Requirement: 论文写作指导角色定义
系统 SHALL 在 `.agents/roles/` 目录下提供 `thesis-advisor` 角色文件，遵循现有角色文件结构（YAML frontmatter + Description/Responsibilities/Non-Goals 三段式正文）。

#### Scenario: 角色文件可被引用
- **WHEN** 工作流编排通过 `id = "thesis-advisor"` 引用角色
- **THEN** 系统能解析到 `.agents/roles/thesis-advisor.md` 与对应 TOML 元数据

#### Scenario: 覆盖完整写作流程
- **WHEN** 用户查阅角色职责
- **THEN** 职责清单覆盖选题确定、文献调研、研究设计、数据收集与分析、论文撰写、最终定稿六个阶段，并包含语言学专业差异说明、常见问题解决方案、学术规范要求、实用技巧与资源推荐

### Requirement: 阶段化操作指南
角色正文 SHALL 按六个阶段组织指导内容，每个阶段提供：
- 具体实施步骤（可操作的子任务）
- 关键注意事项（风险点与避坑提示）
- 时间管理建议（推荐周期占比）

#### Scenario: 选题阶段指导
- **WHEN** 用户处于选题确定阶段
- **THEN** 角色提供研究方向选择、选题可行性评估、研究问题凝练步骤，并标注语言学专业选题倾向（理论语言学/应用语言学/社会语言学/心理语言学等分支）

#### Scenario: 文献调研阶段指导
- **WHEN** 用户处于文献调研阶段
- **THEN** 角色提供文献检索策略（含语言学核心数据库如 LLBA、CNKI 语言学专辑）、文献阅读与笔记方法、文献综述撰写要点

#### Scenario: 研究设计阶段指导
- **WHEN** 用户处于研究设计阶段
- **THEN** 角色提供研究方法选择指导，覆盖语言学常用方法（语料库方法、田野调查、实验法、问卷调查、内省法等）、研究框架构建、伦理审查要点

#### Scenario: 数据收集与分析阶段指导
- **WHEN** 用户处于数据收集与分析阶段
- **THEN** 角色提供语料采集规范、转写标注约定、常用分析工具推荐（Praat/AntConc/SPSS/NVivo/Python NLTK 等）、统计方法选择建议

#### Scenario: 论文撰写阶段指导
- **WHEN** 用户处于论文撰写阶段
- **THEN** 角色提供论文结构规范（含语言学论文常见 IMRD 或特殊结构）、学术语言风格、引用规范（GB/T 7714、APA、Chicago 等）

#### Scenario: 定稿与答辩阶段指导
- **WHEN** 用户处于最终定稿阶段
- **THEN** 角色提供查重降重策略、格式排版规范、答辩 PPT 制作要点、答辩问答准备方法

### Requirement: 语言学专业差异化指导
角色正文 SHALL 包含「语言学及应用语言学专业写作差异」章节，明确本专业与其他人文社科在写作流程上的差异点。

#### Scenario: 专业差异可辨识
- **WHEN** 用户查看专业差异章节
- **THEN** 内容至少覆盖：语料为本专业核心证据、实证与理论并重、跨学科倾向明显、需处理国际音标与特殊符号、术语规范严格等差异点

### Requirement: 常见问题与学术规范
角色正文 SHALL 包含「常见问题解决方案」与「学术规范要求」两部分。

#### Scenario: 问题解决可操作
- **WHEN** 用户遇到选题过大、文献不足、数据偏倚、写作拖延等问题
- **THEN** 角色提供具体的应对策略而非泛泛建议

#### Scenario: 学术规范明确
- **WHEN** 用户查阅学术规范
- **THEN** 内容包含抄袭界定、引用规范、数据真实性、伦理审查、作者署名规范等要求

### Requirement: 资源推荐
角色正文 SHALL 提供「实用技巧与资源推荐」章节，列出可立即使用的工具、数据库、参考书目。

#### Scenario: 资源可用
- **WHEN** 用户查阅资源推荐
- **THEN** 列出的资源均为语言学领域通用且实际存在的工具/数据库/经典教材

### Requirement: 元数据 TOML 一致性
新增 TOML 元数据文件 SHALL 与现有角色 TOML 字段结构一致（id/domain/layer/tier/bindings），并通过 `x-toml-ref` 在 md 文件中正确引用。

#### Scenario: TOML 字段合规
- **WHEN** 校验 thesis-advisor.toml
- **THEN** 包含 id="thesis-advisor"、domain="academic"、layer="guidance"、tier="standard"，bindings 指向相关 rules 与 references

### Requirement: 索引同步
`.agents/roles/README.md` 的角色职责矩阵 SHALL 追加 thesis-advisor 行，文件结构说明 SHALL 包含 thesis-advisor.md 条目。

#### Scenario: 索引可发现
- **WHEN** 浏览角色索引
- **THEN** 能在矩阵与文件结构列表中发现论文指导者角色
