# 变更日志

## 2026-08-29：供应商源码同步

本次变更将 Wiki 信源从已删除的临时克隆目录同步至正式 git submodule `vendor/jira-skill/`（v3.29.0, commit b0dba28），并修正 frontmatter 格式和事实偏差。

### 修复

- **信源路径迁移**：7 处 `file:///` URL 更新为 `file:///d:/AI/vendor/jira-skill/`（source-code.md 3 处、api-reference.md 4 处），另修正 log.md 中 1 处 Windows 路径
- **frontmatter 格式合规**：17 个文件的 `generated`/`verified` 字段从块格式 `date:` 修正为 OKF v0.2 inline flow `at:` 格式；`verified.by` 统一为 `"process:seven-concepts-v"`
- **事实校正**：测试文件数 23→25（24 个 test_*.py + conftest.py）；jira-communication/references/ 参考文档数 16→17
- **API 补全**：api-reference.md 的 changelog.py 部分新增 4 个遗漏函数（`parse_jira_datetime`、`extract_status_transitions_with_authors`、`find_transition_window`、`format_timedelta`），共 7 个函数全部与源码 Grep 验证一致
- **pyproject.toml 描述修正**：补充说明该文件仅含 ruff/bandit 工具配置，无 `[project]` 表，运行时依赖通过 PEP 723 内联声明
- **时间戳更新**：所有文件 `generated.at`/`verified.at` 更新为 2026-08-29，`stale_after` 顺延至 2027-08-29

## 2026-08-28：转换为 OKF v0.2 Bundle

本次变更将原有的扁平 Markdown 教程结构转换为符合 OKF（Open Knowledge Format）v0.2 规范的知识包（Bundle）。

### 新增

- `index.md`：Bundle 根索引，含 `okf_version: "0.2"` 声明
- `log.md`：本变更日志
- `concepts/`：概念文档目录（从根目录迁移）
- `examples/`：示例文档目录
  - `basic-cli-usage.md`：基础 CLI 操作示例
  - `workflow-automation.md`：工作流自动化示例
  - `syntax-templates.md`：Wiki markup 模板示例
- `references/`：信源登记目录
  - `source-code.md`：源码结构、模块划分、版本信息
  - `api-reference.md`：所有 CLI 脚本的子命令、选项和参数
  - `official-docs.md`：Jira REST API、Agent Skills 标准、Wiki Markup 官方文档

### 变更

- 10篇概念文档（00-overview 至 09-glossary）从根目录迁移至 `concepts/` 目录
- 所有概念文档的 frontmatter 从项目自定义格式转换为 OKF v0.2 规范：
  - 新增字段：`type`、`description`、`generated`、`verified`、`stale_after`、`sources`
  - 移除字段：`id`、`x-toml-ref`、`category`、`author`、`date`、`source`（项目内部字段，TOML 信源文件不存在）
  - `summary` 字段重命名为 `description`
- 所有交叉链接从简单文件名改为 `/` 开头的 bundle-relative 路径
- 每个概念文档末尾新增"## 相关概念"章节（09-glossary 已有类似导航章节，仅更新链接路径）

### 事实基础

- 源码版本：jira-skill v3.29.0
- 源码路径：`d:\AI\vendor\jira-skill`（2026-08-29 从临时克隆目录同步更新）
- 转换方法论：source-code-to-okf-wiki（R→I→E→V→C 五阶段）
- 所有脚本名、子命令、参数均通过源码 Grep 验证
