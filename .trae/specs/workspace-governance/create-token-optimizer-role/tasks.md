---
id: "tasks-create-token-optimizer-role"
title: "创建Token优化专家角色 - 实施计划"
date: "2026-08-01"
status: "draft"
---

# 创建Token优化专家（Token Optimizer）角色 - 实施计划

## [ ] Task 1: 验证TOML元数据文件存在性并确认x-toml-ref策略
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 检查 `.agents/.meta/toml/.agents/roles/` 目录是否存在
  - 检查现有角色对应的TOML文件（architect.toml、developer.toml等）是否存在
  - 确认新角色是省略x-toml-ref字段还是引用路径
  - 读取1-2个现有TOML文件（如存在）了解其格式
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: 通过LS/Glob检查.meta目录结构，确认TOML文件是否存在
  - `human-judgement` TR-1.2: 根据检查结果决定x-toml-ref字段策略，记录决策理由
- **Notes**: 如.meta目录不存在或为空，新角色frontmatter中省略x-toml-ref字段，仅保留id、title、source

## [ ] Task 2: 创建token-optimizer.md角色文件
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 在 `d:\AI\.agents\roles\` 下创建 `token-optimizer.md`
  - 编写YAML frontmatter（id: "token-optimizer", title: "Token Optimizer（Token优化专家）", source字段）
  - 根据Task 1结果决定是否包含x-toml-ref
  - 编写Description章节：定位为LLM Token使用优化专家，在成本-质量-延迟三维空间寻找帕累托最优
  - 编写Responsibilities章节，涵盖：
    1. Token优化方案设计与技术选型（参考决策树+选型矩阵）
    2. Prompt结构优化（静态前缀+动态后缀，缓存友好设计）
    3. 分层缓存策略设计（Layer1前缀/Layer2会话/Layer3语义）
    4. 上下文压缩与对话管理策略
    5. 模型路由与分级策略（三级模型路由）
    6. 优化方案评审与风险识别（27条禁令P0-P3检查）
    7. 评估指标体系建立（19项指标框架）
    8. 渐进式优化路线图规划（P-001模式四阶段）
    9. 查阅知识库提供决策支持（明确引用关键文档路径）
  - 编写Non-Goals章节，明确不负责：
    - 架构整体设计（归architect）
    - 具体代码实现（归developer）
    - 代码审查（归reviewer）
    - 测试编写（归tester）
    - 任务编排协调（归orchestrator）
    - 脱离质量底线的极端成本优化（C-001禁令）
    - 未建立质量基线就给出优化建议（C-024禁令）
  - 在Responsibilities中引用关键知识库文档，使用相对路径
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-6]
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件存在且frontmatter可解析（id为"token-optimizer"）
  - `programmatic` TR-2.2: 包含Description、Responsibilities、Non-Goals三个章节
  - `programmatic` TR-2.3: 所有相对路径链接指向存在的文件（验证README.md、quick-reference、constraints、patterns等核心引用）
  - `human-judgement` TR-2.4: 职责覆盖三大路径、五大模式、P0禁令、三维权衡、知识库指引五个核心领域
  - `human-judgement` TR-2.5: Non-Goals清晰界定与architect/developer/reviewer/tester/orchestrator的边界
  - `human-judgement` TR-2.6: 格式（标题层级、列表风格、语言风格）与architect.md/developer.md一致

## [ ] Task 3: 更新roles/README.md角色索引
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 读取最新的roles/README.md内容
  - 在"角色职责矩阵"表格中新增一行：
    - 角色：Token优化专家
    - ID：token-optimizer
    - 领域：optimization
    - 层级：specialist
    - 层级标记：💡 专家
    - 核心职责：LLM Token优化方案、成本-质量-延迟权衡、缓存策略、优化评审
  - 在"文件结构说明"代码块中添加 `├── token-optimizer.md           # Token优化专家` 行
  - 保持表格列数、对齐方式、分隔符与原有表格完全一致
  - 遵循Markdown表格修改规则：替换整个表格，不做局部修改
- **Acceptance Criteria Addressed**: [AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-3.1: 职责矩阵表格列数与修改前一致，新增行各列有内容
  - `programmatic` TR-3.2: 文件结构列表中包含token-optimizer.md
  - `human-judgement` TR-3.3: 表格格式（分隔符、对齐）与原有部分一致，无语法错误
  - `human-judgement` TR-3.4: 新增行的领域、层级、描述与角色定位一致

## [ ] Task 4: 整体验证与格式检查
- **Priority**: medium
- **Depends On**: Task 3
- **Description**: 
  - 读取新创建的token-optimizer.md全文，检查格式一致性
  - 读取更新后的README.md全文，验证表格完整性
  - 验证所有相对路径链接在文件系统中存在
  - 运行文件名规范检查（如可用）
  - 检查是否符合project_memory中的格式约束：
    - 文件名kebab-case、纯英文
    - frontmatter YAML格式正确
    - 链接使用相对路径而非file:///绝对路径
- **Acceptance Criteria Addressed**: [AC-1, AC-4, AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-4.1: 所有引用的相对路径文件实际存在（通过Read工具验证）
  - `programmatic` TR-4.2: 文件名token-optimizer.md符合kebab-case规范
  - `human-judgement` TR-4.3: 通读两个文件，语言为标准现代汉语，无网络流行语，术语使用准确
  - `human-judgement` TR-4.4: 角色职责与Non-Goals无自相矛盾，与其他角色无职责重叠

## [ ] Task 5: 原子提交
- **Priority**: high
- **Depends On**: Task 4
- **Description**: 
  - 使用atomic-commit-cmd技能执行原子提交
  - 提交类型：feat(roles): 添加Token优化专家角色
  - 提交内容包含：token-optimizer.md（新文件）、README.md（修改）
  - 三查暂存法验证：
    - 查新增：确认token-optimizer.md已add
    - 查修改：确认README.md修改已add
    - 查删除：无文件删除
  - 提交信息遵循Conventional Commits规范，中文描述
- **Acceptance Criteria Addressed**: [AC-1, AC-5]
- **Test Requirements**:
  - `programmatic` TR-5.1: git status显示仅两个文件变更（1个新增，1个修改）
  - `programmatic` TR-5.2: 提交成功，commit message符合规范
  - `human-judgement` TR-5.3: 提交单一职责，仅包含角色创建相关变更
