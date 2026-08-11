# Hermes OKF Wiki 教程 - 实施计划

> **方法论**：seven-concepts 知识沉淀场景（R→I→E→V→C）。本计划聚焦 E（萃取知识文档）与 C（原子提交），质量门 G3（模式可迁移）与 G4（行动项原子化）。

## 任务分解

### [ ] Task 1: 创建 hermes-okf-wiki 目录骨架与 README
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/hermes-okf-wiki/` 下创建目录
  - 创建 README.md：YAML frontmatter + OKF 生态定位 + 章节索引表 + 阅读路径建议 + 相关资源（返回上级 okf-wiki）
  - frontmatter 使用 YAML（--- 分隔），遵循 okf-wiki 现有格式
- **Acceptance Criteria**: AC-1, AC-2, AC-14
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录与 README.md 存在于正确路径
  - `programmatic` TR-1.2: frontmatter 使用 YAML 格式且包含必填字段
  - `human-judgement` TR-1.3: README 含章节索引表与阅读路径

### [ ] Task 2: 编写 00-overview（项目概述与 OKF 生态地图）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 一句话定位：首个基于 OKF 的开源 Agent 持久记忆系统，服务于 Hermes 生态
  - 核心价值主张（Filesystem-First、无数据库、无锁定、知识图）
  - OKF 生态定位：Agent 记忆层代表项目，对比 throughline / okf-harness / echoes-vault
  - 8-9 章导航表 + 阅读路径
- **Acceptance Criteria**: AC-3, AC-4
- **Test Requirements**:
  - `human-judgement` TR-2.1: 清晰说明核心定位
  - `human-judgement` TR-2.2: 生态对比（与 throughline/okf-harness/echoes-vault）
  - `human-judgement` TR-2.3: 章节导航表完整

### [ ] Task 3: 编写 01-core-concepts（背景与核心特性）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - OKF 背景（Google Cloud 2026-06-12 发布，Karpathy LLM wiki 标准化）
  - 核心特性详解：Agent Memory / Knowledge Graph / Filesystem-First / Zero-DB Core（仅 pyyaml）/ Hermes Plugin / Hermes-Ready / Resume / Portable / Config Validator / Git History
  - 特性表（Feature / What You Get）
- **Acceptance Criteria**: AC-4
- **Test Requirements**:
  - `human-judgement` TR-3.1: 覆盖全部 10 项核心特性
  - `human-judgement` TR-3.2: 特性表清晰呈现价值

### [ ] Task 4: 编写 02-architecture（五层架构）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 五层架构详解：Human Interface / Hermes Plugin Layer / Universal Provider / Core OKF Layer / Persistence
  - 每层组件说明（HermesOKFMemoryProvider、OKFBundle、GitOKFBundle、Concept、GraphExtractor、SearchIndex、OKFValidator、HotMemoryBuffer、ConfigValidator 等）
  - Mermaid 架构图 + 文本版结构
- **Acceptance Criteria**: AC-5, AC-13
- **Test Requirements**:
  - `human-judgement` TR-4.1: 五层架构阐述清晰
  - `human-judgement` TR-4.2: Mermaid 图语法正确可渲染

### [ ] Task 5: 编写 03-quickstart（快速上手）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - Step 1: `pip install hermes-okf`
  - Step 2: `hermes-okf install-plugin`（含预期输出）
  - Step 3: `hermes-okf validate-config`（15 项检查，预期输出）
  - Step 4: `hermes memory setup`（选择 provider）
  - 卸载：`hermes-okf uninstall-plugin`
- **Acceptance Criteria**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-5.1: 四步流程完整可复制
  - `programmatic` TR-5.2: 命令与预期输出标注正确

### [ ] Task 6: 编写 04-plugin-cli（Hermes 插件 CLI）
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - `hermes okf search "dark mode"`
  - `hermes okf list --type Decision`
  - `hermes okf show config/agent` / `sessions/...` / `--raw`
  - `hermes okf snapshot --note "..."` / `restore`
- **Acceptance Criteria**: AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: 覆盖 search/list/show/snapshot/restore 全部子命令

### [ ] Task 7: 编写 05-standalone-cli（独立 CLI 完整命令集）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 初始化/校验/检索：init / validate / list / show / search
  - 日志与版本管理：log / log --git / diff / revert / log-append
  - 图与快照：graph-edges / graph-neighbors / snapshot / context
  - 会话/计划/工具：sessions / plans / tools
- **Acceptance Criteria**: AC-8
- **Test Requirements**:
  - `programmatic` TR-7.1: 覆盖全部独立 CLI 命令及示例

### [ ] Task 8: 编写 06-agent-integration（Agent 集成）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - HermesMemoryMixin 用法
  - `@memorize_decision`、`@memorize_tool` 装饰器示例
  - `with_context` 召回
  - 说明：对多数用户推荐插件方式，装饰器用于高级/自定义场景
- **Acceptance Criteria**: AC-9
- **Test Requirements**:
  - `human-judgement` TR-8.1: 代码示例完整可运行
  - `human-judgement` TR-8.2: 说明插件 vs 装饰器的适用场景

### [ ] Task 9: 编写 RAG 集成与故障排查 + Roadmap（可并入 07/08）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - RAG 集成：`pip install hermes-okf[rag]` + LangChain DirectoryLoader + MarkdownHeaderTextSplitter + Chroma 示例
  - 故障排查：install-plugin 失败 / memory setup 不显示 / show 显示错误模型 / bundle 未找到 / Windows 文件名错误
  - Roadmap 解读：v0.5.9 里程碑，15 项特性（已交付 10 / 待办 5），当前焦点
- **Acceptance Criteria**: AC-10, AC-11, AC-12
- **Test Requirements**:
  - `human-judgement` TR-9.1: RAG 示例完整
  - `human-judgement` TR-9.2: 故障排查覆盖 5 个问题
  - `human-judgement` TR-9.3: Roadmap 15 项特性状态清晰

### [ ] Task 10: 编写 07-resources（术语表、FAQ、资源链接）
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 术语表：OKF / Hermes / provider / concept / bundle / hot-cold memory / snapshot / restore 等
  - FAQ：4-8 个常见问题
  - 资源链接：GitHub 仓库、PyPI、OKF 官方规范、OKF 生态交叉引用
- **Acceptance Criteria**: AC-12, AC-14
- **Test Requirements**:
  - `programmatic` TR-10.1: 术语表覆盖核心术语
  - `programmatic` TR-10.2: 资源链接 URL 正确

### [ ] Task 11: 更新 okf-wiki/README.md 索引
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 在 okf-wiki/README.md 文档索引表新增 hermes-okf-wiki 条目
  - 保持现有表格格式，含说明与标签
- **Acceptance Criteria**: AC-14
- **Test Requirements**:
  - `programmatic` TR-11.1: README.md 新增条目
  - `human-judgement` TR-11.2: 摘要准确、格式一致

### [ ] Task 12: 全量验证（链接 + 格式 + 命名）
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 运行 `python .agents/scripts/check-links.py` 验证交叉链接
  - 运行 `python .agents/scripts/check-filename-convention.py` 验证命名规范
  - 检查所有章节 frontmatter 合规、Mermaid 语法、14 个 AC 满足情况
- **Acceptance Criteria**: AC-1 ~ AC-14
- **Test Requirements**:
  - `programmatic` TR-12.1: 链接检查通过（无断链）
  - `programmatic` TR-12.2: 命名规范通过
  - `human-judgement` TR-12.3: 全部 AC 满足

# Task Dependencies
- Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8 → Task 9 → Task 10 → Task 11 → Task 12
- 全部任务串行依赖（每个 Task 依赖前一 Task 完成）
- Task 12（验证）依赖所有前序任务

# 质量门记录（seven-concepts G3/G4）
- **G3（模式可迁移）**：教程产出为可复用的 OKF 生态 Agent 记忆工具学习文档，含触发场景、核心步骤、反模式（如"插件 vs 装饰器选错"）、迁移验证（可复制到其他 OKF 记忆工具）
- **G4（行动项原子化）**：每个章节单一职责、可独立验证、有明确验收标准；最终通过原子提交交付