# 变更日志

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
- 源码路径：`d:\AI\.chaos\libs\tests\jira-skill`
- 转换方法论：source-code-to-okf-wiki（R→I→E→V→C 五阶段）
- 所有脚本名、子命令、参数均通过源码 Grep 验证
