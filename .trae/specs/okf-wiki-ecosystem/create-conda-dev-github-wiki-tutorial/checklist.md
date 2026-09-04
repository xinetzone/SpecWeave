# Checklist

## 文档结构与完整性
- [x] `docs/knowledge/learning/08-systems-infrastructure/conda-dev-github-wiki/` 目录存在
- [x] 包含 `00-overview.md` 到 `09-resources.md` + `README.md` 共 11 个文件
- [x] 每个原子文档 < 300 行

## 内容覆盖度
- [x] 00-overview 含教程总览、章节导航表、Mermaid 定位图
- [x] 01-repository-structure 目录树与本地仓库实际结构一致，含文件作用说明
- [x] 02-workflows-deep-dive 覆盖全部 7 个工作流（cla/issues/labels/lock/project/stale/update），每个含触发事件/权限/步骤/配置语义/使用场景
- [x] 03-issue-templates 覆盖 4 个模板（bug/feature/documentation/epic），字段与 validations 解析准确
- [x] 04-community-files 覆盖 CODE_OF_CONDUCT/HOW_WE_USE_GITHUB/profile-README/.gitignore
- [x] 05-infrastructure-sync-model 完整解析 template-files/config.yml 映射清单与中央同步机制
- [x] 06-issue-sorting-labeling 含 Issue Sorting 概念、标签体系、Roadmap Board Mermaid 流程图
- [x] 07-operations-guide 含配置修改/功能扩展/问题排查三个场景，步骤与示例可执行
- [x] 08-best-practices 含可迁移治理模式、安全最佳实践、≥3 个反模式、检验标准
- [x] 09-resources 术语表 ≥15 条，含权威参考资料与分级阅读建议

## 配置准确性
- [x] 被引用的工作流名、Action 名、参数名、触发事件均与本地仓库 `external/libs/conda-dev/.github` 一致，无臆造
- [x] 代码/配置示例标注语言类型（yaml/mermaid/bash）

## 质量规范
- [x] 所有文件 frontmatter 含完整字段（id/title/x-toml-ref/source/category/tags/date/status/author/summary）
- [x] `source` 字段值为 `spec:create-conda-dev-github-wiki-tutorial`
- [x] `category` 字段值为 `learning`
- [x] 01-08 分章文档底部含上一章/返回目录/下一章三向导航
- [x] 所有内部链接为相对路径，无 file:/// 绝对路径断链
- [x] 至少包含 2 处 Mermaid 流程图
