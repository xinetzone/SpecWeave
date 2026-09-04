# XMHub Agent Workspace 初始化 - The Implementation Plan

## [x] Task 1: 创建 .agents 目录结构
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `d:\spaces\SpecWeave\external\xmhub\` 下创建 `.agents/` 目录
  - 在 `.agents/` 下创建 `reports/` 子目录（用于存放报告和临时文档）
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-1.1: `.agents/` 目录存在
  - `programmatic` TR-1.2: `.agents/reports/` 目录存在
- **Notes**: 使用 mkdir 创建目录，确保路径正确

---

## [x] Task 2: 创建 AGENTS.md 入口文件
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 按照 spec.md 中设计的内容创建 `d:\spaces\SpecWeave\external\xmhub\AGENTS.md`
  - 包含：启动协议、子项目路由表、按需阅读索引、补充资料、使用约定、changelog
  - 必须包含「启动协议」关键词
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1: AGENTS.md 文件存在
  - `programmatic` TR-2.2: 文件包含「启动协议」关键词
  - `human-judgement` TR-2.3: 子项目路由表覆盖 5 个子项目，标注哪些已有 AGENTS.md
  - `human-judgement` TR-2.4: 风格与 llvm-dev/AGENTS.md 一致（按需阅读模式）
- **Notes**: 注意使用 LF 换行符，UTF-8 编码

---

## [x] Task 3: 创建 .agents/README.md
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `d:\spaces\SpecWeave\external\xmhub\.agents\README.md`
  - 包含：目录说明、文档索引表格、使用约定、文档维护指南
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在
  - `human-judgement` TR-3.2: 清晰说明 4 个主题文档的用途和阅读时机
- **Notes**: 与 spec.md 中设计内容一致

---

## [x] Task 4: 创建 .agents/01-overview.md
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `d:\spaces\SpecWeave\external\xmhub\.agents\01-overview.md`
  - 包含：工作区定位、目录结构、子项目关系图（Mermaid）、主要技术栈、开发模式
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在
  - `human-judgement` TR-4.2: Mermaid 流程图正确展示子项目依赖关系
  - `human-judgement` TR-4.3: 内容清晰，帮助智能体快速理解工作区结构
- **Notes**: Mermaid 语法要正确

---

## [x] Task 5: 创建 .agents/02-commands.md
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `d:\spaces\SpecWeave\external\xmhub\.agents\02-commands.md`
  - 包含：环境要求、npu_tvm 开发流程、Jupyter 访问、容器操作、dev-env/notebook 使用、跨项目引用约定、Git 操作约定
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在
  - `human-judgement` TR-5.2: compose.sh 命令说明与现有脚本一致
  - `human-judgement` TR-5.3: 工作流描述可操作、实用
- **Notes**: 命令要准确，参考 npu_tvm 现有的 compose.sh 脚本

---

## [x] Task 6: 创建 .agents/03-constraints.md
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `d:\spaces\SpecWeave\external\xmhub\.agents\03-constraints.md`
  - 包含：不可变全局约束（6条）、跨项目协作规则（5条）、代码风格约定（Python/Shell/C++）、文档约定
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在
  - `human-judgement` TR-6.2: 约束条目清晰、可执行，没有模糊表述
  - `human-judgement` TR-6.3: 换行符、Python 编码问题等已踩过的坑有记录
- **Notes**: 基于 npu_tvm 编译过程中遇到的实际问题（CRLF、GBK编码、Python版本等）

---

## [/] Task 7: 创建 .agents/04-troubleshooting.md
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `d:\spaces\SpecWeave\external\xmhub\.agents\04-troubleshooting.md`
  - 包含：常见问题（6个Q&A）、容器调试技巧、环境诊断清单、获取帮助
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在
  - `human-judgement` TR-7.2: 常见问题覆盖实际遇到的坑（CRLF、Jupyter权限、Python导入、Nuitka乱码等）
  - `human-judgement` TR-7.3: 诊断清单逻辑清晰，按顺序排查
- **Notes**: 问题和解决方案要基于实际编译过程中遇到的问题

---

## [x] Task 8: 创建根目录 README.md（人类开发者导航）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `d:\spaces\SpecWeave\external\xmhub\README.md`
  - 包含：项目简介、子项目速查表、快速开始（环境准备+启动TVM环境+编译）、常用命令表、AI协作说明、目录结构、注意事项、相关链接、changelog
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在
  - `human-judgement` TR-8.2: 子项目链接正确，快速开始步骤可操作
  - `human-judgement` TR-8.3: 风格友好，面向人类开发者
- **Notes**: 人类和 AI 入口分离：README.md 给人看，AGENTS.md 给 AI 看

---

## [x] Task 9: 验证文件完整性和一致性
- **Priority**: high
- **Depends On**: Task 2,3,4,5,6,7,8
- **Description**:
  - 检查所有 7 个文件已创建（AGENTS.md + README.md + .agents/ 下 5 个文件）
  - 检查无 file:/// 绝对路径（使用相对路径）
  - 检查 Markdown 交叉引用正确、无断链
  - 检查现有子项目文件未被修改
  - 检查 AGENTS.md 包含「启动协议」关键词
  - 检查所有新文件使用 LF 换行符、UTF-8 编码
  - 检查版本号一致性（LLVM >=22、Python >=3.14，无旧版本残留）
  - 检查 Mermaid 语法正确
  - 检查文件名引用一致性（英文文件名）
  - 检查 YAML frontmatter 格式正确
  - 检查 .agents/ 文档总行数 <500 行
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: 所有 7 个文件（AGENTS.md + README.md + .agents/ 下 5 个文件）存在
  - `programmatic` TR-9.2: 无 file:/// 绝对路径引用
  - `programmatic` TR-9.3: AGENTS.md 包含「启动协议」
  - `programmatic` TR-9.4: notebook/AGENTS.md、dev-env/llvm-dev/AGENTS.md 等已有文件未被修改
  - `programmatic` TR-9.5: 所有新文件使用 LF 换行符，无 CRLF
  - `programmatic` TR-9.6: 无 Python 3.11 或 LLVM 16 等旧版本号残留
  - `human-judgement` TR-9.7: Mermaid 流程图语法正确可渲染
  - `human-judgement` TR-9.8: 所有文档中引用的文件名与实际文件名一致
  - `human-judgement` TR-9.9: YAML frontmatter（id/title）格式正确
  - `human-judgement` TR-9.10: .agents/ 目录文档总行数 <500 行，符合轻量级定位
  - `human-judgement` TR-9.11: 文档之间风格一致，没有矛盾内容
- **Notes**: 使用 grep 检查绝对路径、关键词、版本号，使用 git status 检查未修改已有文件，使用 wc -l 统计行数
