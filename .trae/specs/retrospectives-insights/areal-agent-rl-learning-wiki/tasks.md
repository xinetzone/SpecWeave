# AReaL 2.0 自演进 Agent 在线强化学习基础设施学习 Wiki - The Implementation Plan

## [x] Task 1: L1 内容提取与验证
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 使用 defuddle 工具重新提取微信公众号文章完整内容
  - 验证提取质量：去除导航、广告、评论区噪音，保留正文标题、段落、列表、图片链接
  - 确认核心内容完整：三大支柱、微服务架构、实践范例、未来方向等无遗漏
  - 如 defuddle 效果不佳，使用备选方案（web-to-markdown 或浏览器工具）
- **Acceptance Criteria Addressed**: AC-1（间接）、AC-3（间接）
- **Test Requirements**:
  - `programmatic` TR-1.1: 提取的 Markdown 文本包含文章核心关键词（AReaL、ATDP、Data Proxy、Control Plane、Gateway、Router、Worker、Hermes、Claude Code）
  - `human-judgement` TR-1.2: 正文内容完整，无大段缺失，无明显噪音残留
- **Notes**: defuddle 初次提取已基本成功，但需验证完整性

## [x] Task 2: L2 内容分析与核心观点标记
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 通读干净文本，识别核心主题和作者主张
  - 标记核心观点（🔴）、支撑论据（🟡）、扩展信息（🟢）、无关内容（⚫）
  - 梳理文章逻辑结构：背景→问题→三大支柱→架构设计→实践范例→趋势展望
  - 识别需要解释的关键术语：ATDP、Agent-compute、Online RL、Rollout、KPop、reward hacking、token-in-token-out 等
  - 验证内容完整性：确认无关键论点、数据、链接遗漏
- **Acceptance Criteria Addressed**: AC-3、AC-4、AC-5、AC-6、AC-7
- **Test Requirements**:
  - `human-judgement` TR-2.1: 识别出至少 5 个核心观点并标记
  - `human-judgement` TR-2.2: 梳理出清晰的逻辑结构大纲
  - `human-judgement` TR-2.3: 列出至少 10 个需要解释的关键术语
- **Notes**: 重点关注三大支柱和微服务架构的对应关系

## [x] Task 3: L3 结构设计与 Wiki 大纲确认
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 基于 L2 分析，设计 Wiki 章节结构（参考 octo-platform-wiki 的风格）
  - 章节划分建议：
    1. 行业背景与问题定位
    2. AReaL 版本演进与核心定位
    3. Agent 自演进三大支柱（ATDP/Data Proxy/Control Plane）
    4. Agent-compute 微服务架构（五大组件）
    5. Online RL 工作流
    6. 实践范例（Hermes + Claude Code）
    7. 行业趋势与未来方向
    8. 关键术语表
    9. 常见问题解答（FAQ）
    10. 相关资源链接
  - 明确原子化决策：保持单文件（预估 250-300 行 < 300 行阈值），记录理由
  - 为每个章节分配核心内容要点
- **Acceptance Criteria Addressed**: AC-2、AC-11
- **Test Requirements**:
  - `human-judgement` TR-3.1: 章节结构逻辑递进，覆盖所有核心内容
  - `human-judgement` TR-3.2: 原子化决策明确，理由充分（预估行数+章节独立性判断）
  - `human-judgement` TR-3.3: 每个章节有明确的内容要点分配

## [x] Task 4: L4 Wiki 文档创建（内容创作）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建文件 `docs/knowledge/learning/areal-agent-rl-wiki.md`
  - **强制前置步骤**（开始写文件前必须执行）：
    - 读取 `docs/knowledge/learning/octo-platform-wiki.md` 确认实际格式
    - 确认 frontmatter 格式：YAML（--- 分隔），包含 title/source/date/tags 字段
    - 确认标题层级、列表风格、表格格式与现有文档一致
  - 添加正确的 YAML frontmatter
  - 添加原文链接和 GitHub 项目链接
  - 添加目录导航（带锚点链接）
  - 按章节填充内容，使用表格、列表、引用等格式增强可读性
  - 确保关键术语解释清晰，技术概念有必要说明
  - 在局限性部分客观说明技术成熟度（当前处于早期阶段）
- **Acceptance Criteria Addressed**: AC-1、AC-2、AC-3、AC-4、AC-5、AC-6、AC-7、AC-8、AC-9
- **Test Requirements**:
  - `human-judgement` TR-4.1: frontmatter 使用 YAML（---），字段完整且正确
  - `human-judgement` TR-4.2: 目录导航完整，锚点链接可跳转
  - `human-judgement` TR-4.3: 十大章节内容完整，核心观点无遗漏
  - `human-judgement` TR-4.4: 术语表包含 10+ 术语，FAQ 包含 6+ 问题
  - `human-judgement` TR-4.5: 资源链接包含原文、论文、GitHub、示例代码路径
  - `human-judgement` TR-4.6: 内容客观，如实说明技术现状和局限性
  - `programmatic` TR-4.7: 运行文件名规范检查 `python .agents/scripts/check-filename-convention.py docs/knowledge/learning/areal-agent-rl-wiki.md` 通过
- **Notes**: 子代理交付后必须执行"主代理验收5点检查"（frontmatter分隔符、x-toml-ref或字段完整性、标题层级、文件名、source溯源）

## [x] Task 5: 知识库索引更新
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 读取 `docs/knowledge/README.md` 找到 learning 分类表格位置
  - 在表格中新增 areal-agent-rl-wiki 条目
  - 条目格式与现有条目保持一致：标题（带链接）、摘要、日期（2026-07-04）、标签
  - 摘要示例："系统学习蚂蚁集团AReaL 2.0自演进Agent在线强化学习基础设施的wiki教程，涵盖Agent自演进三大支柱（ATDP/Data Proxy/Control Plane）、Agent-compute微服务架构、Online RL工作流、Hermes/Claude Code实践范例，以及从执行闭环到学习闭环的行业趋势。"
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `human-judgement` TR-5.1: learning 分类表格新增条目，格式与现有条目一致
  - `human-judgement` TR-5.2: 摘要准确概括 Wiki 核心内容，标签正确
  - `programmatic` TR-5.3: 表格结构未破坏，列数对齐

## [x] Task 6: 质量验证与收尾
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 运行链接检查：`python .agents/scripts/check-links.py docs/knowledge/learning/areal-agent-rl-wiki.md`
  - 如项目规范要求 x-toml-ref，运行 `python .agents/scripts/fix-x-toml-ref.py --file docs/knowledge/learning/areal-agent-rl-wiki.md --write --create-toml`
  - 确认工作区无无关文件混入
  - 主代理最终验收：对照 checklist.md 逐项检查
- **Acceptance Criteria Addressed**: AC-1、AC-9、AC-11
- **Test Requirements**:
  - `programmatic` TR-6.1: 链接检查无断链（内部锚点除外）
  - `human-judgement` TR-6.2: 对照 checklist.md 所有检查点通过
  - `human-judgement` TR-6.3: 工作区干净，无临时文件或无关文件

## [x] Task 7: 原子提交（可选，用户未要求则跳过）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 使用 Conventional Commits 规范提交
  - 提交类型：docs(knowledge)
  - 提交信息示例："新增AReaL 2.0自演进Agent在线强化学习基础设施Wiki教程"
  - 确保单一职责：只包含 areal-agent-rl-wiki.md 和 README.md 的修改
- **Acceptance Criteria Addressed**: 项目规范要求
- **Test Requirements**:
  - `programmatic` TR-7.1: git status 确认只包含预期文件
  - `human-judgement` TR-7.2: commit message 符合 Conventional Commits 规范
- **Notes**: 如用户未要求提交，可跳过此任务
