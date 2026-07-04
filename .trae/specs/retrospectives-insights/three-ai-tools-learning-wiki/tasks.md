# 三个热门AI工具学习与Wiki教程文档 - 实施计划

## [x] Task 1: 创建wiki教程文档基础结构与目录导航
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在docs/knowledge/learning/目录下创建three-ai-tools-wiki.md
  - 添加符合MDI v1.0规范的YAML frontmatter（title/source/date/tags）
  - 创建完整的目录导航系统，包含所有章节的锚点链接
- **Acceptance Criteria Addressed**: [AC-1, AC-2]
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件存在于正确路径docs/knowledge/learning/three-ai-tools-wiki.md
  - `programmatic` TR-1.2: YAML frontmatter使用---包裹，包含title/source/date/tags四个必填字段
  - `programmatic` TR-1.3: 目录导航包含所有计划章节的锚点链接
  - `human-judgement` TR-1.4: 目录结构清晰，章节命名符合中文技术文档规范
- **Notes**: 参考同目录下declarative-partial-updates-wiki.md的格式

## [x] Task 2: 编写文章概述与intelligent-terminal章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 编写文章概述章节：介绍文章来源（逛逛GitHub公众号）、三个工具的整体背景
  - 编写intelligent-terminal详细章节：
    - 项目定位（微软Build 2026、Windows Terminal实验分支、AI原生终端）
    - 三大核心功能（Agent面板Ctrl+Shift+.、错误自动检测Ctrl+Alt+.、ACP协议支持）
    - 技术亮点（本地传输层、不调云API、不持久化会话、Copilot/Claude Code/Codex/Gemini CLI平等支持）
    - 系统要求（Win11 22H2+）
    - 安装命令（winget install --id Microsoft.IntelligentTerminal -e）
    - 适用人群分析
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 概述章节清晰说明文章来源和三个工具的整体定位
  - `human-judgement` TR-2.2: intelligent-terminal章节包含所有关键信息点（定位/功能/亮点/要求/安装/人群）
  - `programmatic` TR-2.3: 安装命令准确无误，与原文一致
  - `programmatic` TR-2.4: 快捷键（Ctrl+Shift+.、Ctrl+Alt+.）记录准确
- **Notes**: 原文中"微软下场做了个AI终端"作为章节引入

## [x] Task 3: 编写Claudian章节
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 编写Claudian详细章节：
    - 项目定位（Obsidian插件、中文博主Jackywine作品、笔记库变Agent工作目录）
    - 核心价值（替代Terminal类插件的糟糕体验）
    - 功能特性（侧边栏集成、文件读写、搜索、跑bash、多步工作流全闭环）
    - 社区热度（7个月1.3万Star、Obsidian社区最火AI插件之一）
    - 适用人群（Obsidian重度用户+AI Coding用户）
    - GitHub开源地址
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-3.1: Claudian章节包含所有关键信息点（定位/价值/功能/热度/人群/地址）
  - `programmatic` TR-3.2: Star数据准确（7个月1.3万Star）
  - `programmatic` TR-3.3: GitHub地址正确（https://github.com/YishenTu/claudian）
  - `human-judgement` TR-3.4: 清晰说明这是中文开发者的作品
- **Notes**: 客观说明之前方案（Terminal类插件）体验不佳的痛点

## [x] Task 4: 编写book-to-skill章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 编写book-to-skill详细章节：
    - 项目定位（技术书籍→符合Agent Skills开放标准的结构化技能）
    - 核心思想：与RAG的本质差异
      - RAG：查询时向量相似度搜索，返回原文片段
      - book-to-skill：编译时一次性深挖作者框架、命名方法、反模式，输出可推理结构
    - 金句解读："RAG indexes a shelf, book-to-skill masters a spine."
    - 基准测试数据（256K token大书：全上下文77,866 token/题 vs skill 5,000 token/题，节省15.6倍）
    - 成本分析（单本编译约1美元Sonnet 4.5一次性费用，之后每次查询固定5000 token）
    - 使用方法（git clone命令）
    - GitHub开源地址
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-4.1: book-to-skill章节包含所有关键信息点（定位/核心思想/金句/数据/成本/用法/地址）
  - `programmatic` TR-4.2: Star数据准确（2个月6.8k Star）
  - `programmatic` TR-4.3: token数据准确（77,866 vs 5,000，15.6倍节省）
  - `programmatic` TR-4.4: 成本数据准确（单本约1美元）
  - `programmatic` TR-4.5: GitHub地址正确（https://github.com/virgiliojr94/book-to-skill）
  - `human-judgement` TR-4.6: RAG vs book-to-skill的差异解释清晰
- **Notes**: 这是三个工具中最有技术深度的一个，需要重点解释其与RAG的路线差异

## [x] Task 5: 编写对比分析与技术趋势章节
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 编写对比分析章节：使用Markdown表格对比三个工具在以下维度的差异
    - 工具定位
    - 适用人群
    - 技术路线
    - 核心价值
    - 平台/环境要求
  - 编写技术趋势分析章节：
    - 趋势一：终端AI化（AI原生进命令行，intelligent-terminal体现）
    - 趋势二：知识工具Agent化（笔记软件变Agent工作区，Claudian体现）
    - 趋势三：知识结构化（从RAG片段检索到编译式深度理解，book-to-skill体现）
- **Acceptance Criteria Addressed**: [AC-6, AC-7]
- **Test Requirements**:
  - `human-judgement` TR-5.1: 对比表格维度完整，信息准确
  - `human-judgement` TR-5.2: 三个趋势方向分析有深度，不是简单罗列
  - `human-judgement` TR-5.3: 趋势分析与三个工具的对应关系清晰
- **Notes**: 趋势分析应有洞察力，结合当前AI工具生态发展方向

## [x] Task 6: 编写内容评估、FAQ与资源链接章节
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 编写内容评估章节：从准确性、实用性、创新性三个维度评估原文
    - 准确性：信息来源可靠（GitHub Trending/X平台），数据可验证
    - 实用性：三个工具均有明确使用场景和安装方法
    - 创新性：体现AI工具发展的新方向
  - 编写常见问题解答（FAQ）章节：覆盖可能的疑问
    - intelligent-terminal只支持Windows吗？
    - Claudian必须使用Claude Code吗？
    - book-to-skill支持哪些书籍格式？
    - 三个工具可以组合使用吗？
  - 编写相关资源链接章节：
    - 原文链接
    - intelligent-terminal GitHub
    - Claudian GitHub
    - book-to-skill GitHub
- **Acceptance Criteria Addressed**: [AC-8, AC-9, AC-10]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 内容评估三维度客观中立
  - `human-judgement` TR-6.2: FAQ覆盖用户可能遇到的常见问题
  - `programmatic` TR-6.3: 所有资源链接URL正确
- **Notes**: FAQ基于原文内容合理推断，不编造原文没有的信息

## [x] Task 7: 更新知识库索引
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 更新docs/knowledge/README.md，在learning分类中添加本教程条目
  - 条目包含：标题、摘要、日期、标签
  - 遵循现有索引格式
- **Acceptance Criteria Addressed**: [AC-11]
- **Test Requirements**:
  - `programmatic` TR-7.1: docs/knowledge/README.md中learning分类新增条目
  - `human-judgement` TR-7.2: 条目格式与现有条目一致
  - `programmatic` TR-7.3: 日期为2026-07-04
- **Notes**: 使用Edit工具精确插入，不要破坏现有索引结构
