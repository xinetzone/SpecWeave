# Open Code Review 项目学习与 Wiki 教程文档 - 实施计划

## L1 内容提取（已完成）
- [x] 使用 defuddle 提取原始网页内容
- [x] 验证提取质量，去噪
- [x] 保存为 .temp/open-code-review-raw.md

## L2 内容分析（已完成）
- [x] 通读并标记核心观点
- [x] 识别关键概念
- [x] 梳理逻辑结构
- [x] 验证内容完整性

## L3 结构设计（已完成）
- [x] 完成 spec.md（含 DoD 完成定义）
- [x] **原子化决策**：按 4 项判断标准评估，明确选择"需要拆分"（11章节原子文件结构）
- [x] 设计章节结构（11章节，基于8章节标准结构扩展）
- [x] 完成 checklist.md（含子代理验收5点检查）
- [x] 在 tasks.md 中预置原子化步骤（L5阶段）

## L4 文档生成（首次提交：内容创作提交）

### [x] Task 1: 创建 Wiki 教程索引页与目录导航
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 docs/knowledge/learning/ 目录下创建 open-code-review-wiki.md 索引页文件
  - 添加符合规范的 YAML frontmatter（title/source/date/tags）
  - 创建完整的目录导航表格，包含所有 11 个章节的相对路径链接
  - 添加原文参考和 GitHub 项目链接的开头引用
  - 创建 docs/knowledge/learning/open-code-review-wiki/ 子目录
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-11]
- **Test Requirements**:
  - `programmatic` TR-1.1: 索引页文件存在于正确路径 docs/knowledge/learning/open-code-review-wiki.md
  - `programmatic` TR-1.2: frontmatter 包含所有必填字段（title/source/date/tags）
  - `human-judgement` TR-1.3: 目录导航结构完整，所有章节链接可跳转
  - `programmatic` TR-1.4: 包含原文 URL 和 GitHub 项目 URL
- **Notes**: 参考 mopmonk-security-agent-wiki.md 的索引页结构和格式

### [x] Task 2: 编写 00-overview.md 概述与学习目标章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 介绍 AI 代码评审的背景：AI 每天生成的代码量已远超人工评审上限
  - 引出 Open Code Review 项目：阿里开源的 AI 驱动代码评审 CLI 工具，前身在内部服务数万开发者
  - 列出 5-6 条学习目标
  - 说明前置知识要求
  - 添加文档导航表
- **Acceptance Criteria Addressed**: [AC-1, AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 背景介绍清晰，引出项目定位
  - `human-judgement` TR-2.2: 学习目标具体可衡量（5-6条）
  - `human-judgement` TR-2.3: 前置知识说明完整
  - `programmatic` TR-2.4: 文档导航表链接到所有章节

### [x] Task 3: 编写 01-core-concepts.md 核心概念与设计理念章节
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 介绍通用 Agent + Skills 方案在代码评审场景的三大问题：覆盖不全、位置漂移、效果不稳定
  - 解析"确定性工程 × Agent 混合驱动"的核心设计理念
  - 详细说明确定性工程负责的强约束环节：精准文件筛选、智能文件打包、精细化规则匹配、外挂定位与反思组件
  - 详细说明 Agent 负责的动态决策环节：场景化提示词调优、场景化工具集沉淀
  - 用表格对比确定性工程与 Agent 的职责分工
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 清晰阐述通用 Agent 方案的3个问题
  - `human-judgement` TR-3.2: 准确解析"确定性工程×Agent混合驱动"理念
  - `human-judgement` TR-3.3: 确定性工程4大强约束环节说明完整
  - `human-judgement` TR-3.4: Agent 2大动态决策环节说明完整

### [x] Task 4: 编写 02-installation.md 安装与配置指南章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - npm 安装命令：npm install -g @alibaba-group/open-code-review
  - 验证安装：ocr version
  - LLM 配置流程：ocr config provider 和 ocr config model
  - 配置自定义供应商的方法
  - 各步骤说明清晰，命令可直接复制执行
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 安装步骤完整（npm install + ocr version 验证）
  - `programmatic` TR-4.2: 所有命令代码块格式正确
  - `human-judgement` TR-4.3: LLM 配置流程说明清晰
  - `human-judgement` TR-4.4: 包含必要的注意事项

### [x] Task 5: 编写 03-usage.md 使用流程与命令详解章节
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - ocr review 命令详解：工作区模式、分支对比、单次提交、附带需求背景
  - ocr review 常用参数表（--repo/--format/--concurrency/--timeout/--audience/--background/--preview）
  - ocr scan 全量扫描模式：适用场景（审计陌生代码库/迁移重构前体检/无意义diff目录/非Git目录）
  - ocr scan 多阶段评审流程：Plan 阶段、批次评审、Dedup 阶段、Project Summary 阶段
  - ocr scan 成本控制：token 成本预估、--preview、--max-tokens-budget
  - ocr scan 常用参数表
  - 包含可直接复制执行的命令示例
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-5.1: ocr review 4种使用方式说明完整
  - `human-judgement` TR-5.2: ocr scan 适用场景和多阶段流程说明完整
  - `programmatic` TR-5.3: 常用参数表格式正确
  - `human-judgement` TR-5.4: 成本控制策略说明清晰

### [x] Task 6: 编写 04-optimizations.md 关键技术优化章节
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 假阴性（漏报）优化：智能文件打包、Plan 阶段、Agent 化动态上下文召回、场景化工具集设计
  - 假阳性（误报）优化：反思模型（Qwen3-30B-A3B，误报拦截率从30.09%提升到52.63%）、精细化规则模板、上下文隔离设计
  - 用户主观性问题：四层规则穿透机制（CLI参数/项目维度/用户维度/系统默认）
  - 定位准确率优化：三层递进式定位策略（Hunk-based文本匹配→全文件内容扫描→LLM重定位）
  - Token 消耗优化：分治策略、双阈值内存压缩、大文件预过滤、工具输出上限、Plan阶段智能跳过、精确token预算控制、确定性逻辑接管
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 假阴性4个优化策略说明完整
  - `human-judgement` TR-6.2: 假阳性3个优化策略说明完整，含反思模型数据
  - `human-judgement` TR-6.3: 四层规则穿透机制说明清晰
  - `human-judgement` TR-6.4: 三层递进式定位策略说明完整
  - `human-judgement` TR-6.5: Token 7个优化策略说明完整

### [x] Task 7: 编写 05-integrations.md 集成与高级用法章节
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - Claude Code 集成：Command 与 Skills 两种接入方式的对比表
  - Command 安装命令（mkdir + curl）
  - Skills 安装命令（mkdir + curl）
  - Claude Code 集成的4大工作机制：上下文隔离、需求感知、置信度分级、自动修复
  - GitHub Actions 集成：核心命令、配置方式
  - GitLab CI 集成：MR 触发、行级讨论回写、支持自托管实例
  - CI 集成所需的环境变量（OCR_LLM_URL/OCR_LLM_AUTH_TOKEN/OCR_LLM_MODEL）
  - 自定义评审规则：四层链路解析、规则配置文件格式、glob pattern 支持
  - OpenTelemetry 可观测性配置
  - Web 视图（ocr viewer）
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-7.1: Command 与 Skills 两种方式对比清晰
  - `programmatic` TR-7.2: 安装命令代码块格式正确
  - `human-judgement` TR-7.3: 4大工作机制说明完整
  - `human-judgement` TR-7.4: GitHub Actions 和 GitLab CI 集成说明完整
  - `human-judgement` TR-7.5: 自定义规则四层链路说明清晰

### [x] Task 8: 编写 06-effectiveness.md 效果验证与质量评估章节
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 内部使用数据：2万月活、370万次评审任务、30%+采纳率、近80% AI评论占比、97%+位置准确率
  - 开源评测集对比：50个开源仓库、200个PR、10种编程语言、80+工程师交叉标注
  - 评测对比的工具：Open Code Review v1.3.1、Claude Code v2.1.169、Codex v0.140.0
  - 评测对比的模型：Claude-4.6-Opus、Claude-4.8-Opus、GPT-5.5、Qwen3.7-Max、Deepseek-V4-Pro、GLM-5.1
  - 结论一：准确率与召回率各有所长（OCR准确率25-38% vs CC 7-16%；CC召回率28.90%最高；F1指标OCR领先25.10% vs 14.13%）
  - 结论二：资源开销与适用场景差异（OCR 352K-743K token/1-6分钟；CC 2062K-5664K token/5-14分钟；Codex 525K token/3分钟）
  - 结论三：新一代模型并非全面优于上一代（Claude-4.8-Opus更精确但更保守）
  - 实践案例：Claude Code 用 Go 语言重写开源版本，106次变更发现145个有效问题
  - 质量评估方法论：基于运行轨迹对过程评估、基于客观评测集对结果量化
  - 为什么 CLI 形态更具可评测性（3项优势）
  - AACR-Bench 行业基准：南大与阿里TRE联合推出，3大核心优势（人机结合/多维度评估/深刻行业洞察）
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 内部数据5项指标完整
  - `human-judgement` TR-8.2: 3个评测结论说明清晰，含具体数据
  - `human-judgement` TR-8.3: 实践案例说明完整
  - `human-judgement` TR-8.4: AACR-Bench 3大优势说明完整
  - `programmatic` TR-8.5: 数据引用准确无误

### [x] Task 9: 编写 07-limitations.md 局限性与对比章节
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 召回率不及 Claude Code：OCR 最优 20.00% vs CC 28.90%（差 45%），适合"宁可错杀不可放过"的场景应选 CC
  - 规则存在边际效益递减现象：写得越多，指令跟随越差
  - 需要配置 LLM 端点：对纯本地化部署场景有门槛
  - 内部版特性未完全开源：对外版本暂时采用固定分治策略
  - 系统默认规则偏向阿里内部场景：外部团队可能需要自定义规则
  - 专用模型（Qwen3-30B-A3B 反思模型、Qwen3-8B 定位模型）未开源
  - 适用场景说明：需要工程级稳定评审时使用，安全审计等场景可配合 Claude Code
  - 与 Claude Code/Codex 的对比表（准确率/召回率/F1/资源开销/适用场景）
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 列出至少6个局限性
  - `human-judgement` TR-9.2: 表述客观中立，不夸大不贬低
  - `human-judgement` TR-9.3: 包含适用场景和不适用场景说明
  - `human-judgement` TR-9.4: 与 CC/Codex 对比表完整

### [x] Task 10: 编写 08-summary.md 总结与展望章节
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 核心要点回顾：6条关键 takeaway
    1. AI 写代码与 AI 审代码是两种截然不同的能力
    2. 确定性工程 × Agent 混合驱动是更稳定的设计思路
    3. CLI 形态在可观测性和可评测性上具备天然优势
    4. 四层规则穿透机制解决用户主观性问题
    5. AACR-Bench 重新定义了 ACR 任务的评估标准
    6. 评估 AI 代码评审质量应基于过程和结果，而非用户行为
  - 未来规划：Ultra 评审模式、IDE 插件、MCP 集成、专用模型训练、特定领域长期记忆
  - 下一步学习建议：动手安装使用、配置自定义规则、集成到 CI 流水线、参与社区共建
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `human-judgement` TR-10.1: 6条核心要点总结到位
  - `human-judgement` TR-10.2: 与开头痛点形成呼应
  - `human-judgement` TR-10.3: 未来规划说明完整
  - `human-judgement` TR-10.4: 下一步学习建议具体可行

### [x] Task 11: 编写 09-faq.md 常见问题章节
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 整理常见问题并提供解答，如：
    - Q: Open Code Review 适合什么场景使用？
    - Q: ocr review 和 ocr scan 有什么区别？
    - Q: 必须配置自己的 LLM 端点吗？支持哪些模型？
    - Q: 与 Claude Code 的 /code-review 相比有什么优势？
    - Q: 如何自定义评审规则？四层规则如何生效？
    - Q: 可以集成到现有的 CI/CD 流水线吗？
    - Q: 内部版的反思模型和定位模型是否开源？
    - Q: 评审结果的位置准确率如何？
    - Q: Token 消耗如何控制？大仓库扫描会不会很贵？
    - Q: 项目还在积极维护吗？
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `human-judgement` TR-11.1: 至少包含9个 FAQ 问题
  - `human-judgement` TR-11.2: 问题具有实际参考价值
  - `human-judgement` TR-11.3: 解答清晰准确

### [x] Task 12: 编写 10-resources.md 资源链接章节
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 原始资源：微信公众号文章 URL
  - 官方资源：
    - GitHub 项目地址：https://github.com/alibaba/open-code-review
    - 规则文档：https://github.com/alibaba/open-code-review/tree/main/internal/config/rules/rule_docs
    - GitHub Issues：https://github.com/alibaba/open-code-review/issues
  - 论文资源：
    - 反思模型论文：https://arxiv.org/pdf/2602.20166v1
    - AACR-Bench 论文：https://arxiv.org/abs/2601.19494
  - 数据集资源：
    - AACR-Bench GitHub：https://github.com/alibaba/aacr-bench
    - HuggingFace 数据集：https://huggingface.co/datasets/Alibaba-Aone/aacr-bench
  - 相关学习资源：Claude Code、AI 代码评审相关概念
  - 本项目内相关 wiki（如适用）
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-12.1: GitHub 链接正确
  - `programmatic` TR-12.2: 原文链接正确
  - `human-judgement` TR-12.3: 资源分类清晰
  - `programmatic` TR-12.4: 论文和数据集链接完整

### [x] Task 13: 更新知识库索引 README.md
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 在 docs/knowledge/README.md 的 learning 分类表格中新增 Open Code Review 教程条目
  - 条目包含：标题、摘要、日期（2026-07-04）、标签（open-code-review、ai-code-review、alibaba、cli、agent、aacr-bench、code-quality、devops）
  - 遵循现有索引格式，保持表格结构一致
- **Acceptance Criteria Addressed**: [AC-12]
- **Test Requirements**:
  - `programmatic` TR-13.1: README.md 中 learning 分类新增了条目
  - `human-judgement` TR-13.2: 摘要准确概括教程内容
  - `human-judgement` TR-13.3: 标签设置合理
  - `programmatic` TR-13.4: 表格格式保持一致

## L5 原子化配套（与 L4 同步进行）
- [x] 为每个原子文件添加正确的 YAML frontmatter（id/title/source/x-toml-ref）
- [x] source 字段指向索引页 open-code-review-wiki.md 对应章节锚点
- [x] x-toml-ref 指向 .meta/toml/docs/knowledge/learning/open-code-review-wiki/ 镜像路径
- [x] 文件名使用两位数字前缀（00-10），kebab-case 命名

## L6 收尾验证
- [x] 运行 fix-x-toml-ref.py 自动修复 x-toml-ref 路径并创建缺失 TOML 文件：`python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/open-code-review-wiki/ --write --create-toml`
- [x] 运行 check-links.py 验证所有链接有效
- [x] 运行 check-filename-convention.py 验证文件名规范
- [x] 确认工作区无无关文件混入
- [ ] 原子提交（commit: docs(knowledge): 新增 Open Code Review 学习 Wiki 教程）

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
- [Task 5] depends on [Task 4]
- [Task 6] depends on [Task 5]
- [Task 7] depends on [Task 6]
- [Task 8] depends on [Task 7]
- [Task 9] depends on [Task 8]
- [Task 10] depends on [Task 9]
- [Task 11] depends on [Task 10]
- [Task 12] depends on [Task 11]
- [Task 13] depends on [Task 12]
- [L5 配套] 与 [Task 2-12] 同步进行
- [L6 收尾验证] depends on [Task 13]
