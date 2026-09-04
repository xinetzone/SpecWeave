# Checklist

## 文档结构与完整性
- [x] `docs/knowledge/learning/08-systems-infrastructure/conda-dev-source-wiki/` 目录存在
- [x] 包含 `00-overview.md` 到 `09-resources.md` + `README.md` 共 11 个文件
- [x] 每个原子文档 < 350 行

## 内容覆盖度（六大要素）
- [x] 00-overview 含教程总览、章节导航表、Mermaid 分层定位图
- [x] 01-architecture 含 conda 源码分层架构 + conda-docs 文档架构 + 二者关系
- [x] 02-core-modules 覆盖 base/common/models/core 及根级模块
- [x] 03-cli-commands 覆盖 cli/main 入口与各 main_*.py 命令，含注册分发流程
- [x] 04-gateways-plugins-env 覆盖 gateways/plugins/env/notices/auxlib/shell
- [x] 05-key-apis 覆盖 conda.api/MatchSpec/PrefixData/SubdirData/Context/History/exports 及 conda-docs 扩展
- [x] 06-scenarios 含 ≥6 个典型应用场景，每场景含背景/步骤/示例/预期结果
- [x] 07-faq 含 ≥8 条常见问题，每条含现象/原因/解决步骤
- [x] 08-best-practices 含环境管理/求解器/API 健壮性/插件开发/源码贡献/文档写作 + ≥3 反模式
- [x] 09-resources 术语表 ≥15 条，含权威参考资料与分级阅读建议

## 内容准确性
- [x] 被引用的模块名、函数签名、参数、命令名均与本地仓库 `external/libs/conda-dev/conda` 与 `conda-docs` 一致，无臆造
- [x] 代码示例标注语言类型（python/bash/yaml/mermaid）

## 质量规范
- [x] 所有文件 frontmatter 含完整字段（id/title/source/category/tags/date/status/author/summary）
- [x] `source` 字段值为 `spec:create-conda-dev-source-wiki-tutorial`
- [x] `category` 字段值为 `learning`
- [x] 01-08 分章文档底部含上一章/返回目录/下一章三向导航
- [x] 所有内部链接为相对路径，无 file:/// 绝对路径断链
- [x] 至少包含 2 处 Mermaid 图（分层架构定位图 + 分层依赖图）