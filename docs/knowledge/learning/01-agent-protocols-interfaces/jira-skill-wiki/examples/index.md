# Examples 索引

本目录包含 jira-skill OKF Wiki 的实操示例文档。

## 示例文件

| 文件 | 内容 |
|------|------|
| [basic-cli-usage.md](/examples/basic-cli-usage.md) | 基础CLI使用：搜索、获取、创建、评论、工时、附件等核心操作 |
| [workflow-automation.md](/examples/workflow-automation.md) | 工作流自动化：意图动词、多步转换路径、QA聚合、版本管理 |
| [syntax-templates.md](/examples/syntax-templates.md) | Wiki markup 模板填充、语法验证和提交流程 |

## 使用建议

- 初次使用 jira-skill 建议从[基础CLI使用示例](/examples/basic-cli-usage.md)开始
- 熟悉基础命令后，阅读[工作流自动化示例](/examples/workflow-automation.md)学习高级模式
- 创建工单前参考[语法模板示例](/examples/syntax-templates.md)确保内容格式正确
- 所有写操作命令建议先加 `--dry-run` 预览

```{toctree}
:maxdepth: 2

basic-cli-usage
syntax-templates
workflow-automation
```