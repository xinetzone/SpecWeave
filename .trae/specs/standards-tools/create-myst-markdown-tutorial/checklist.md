---
version: 1.0
---
# MyST Markdown 技术教程 - Verification Checklist

## 结构与范围验证
- [x] 教程目录结构正确：`docs/knowledge/learning/myst-markdown-tutorial/` 包含主文档、`examples/`、`appendix/`
- [x] README.md 入口文档存在，包含简介、适用人群、学习路径、完整目录导航
- [x] 教程包含9大模块：快速上手、MyST简介与对比、基础语法、高级功能、扩展组件、工具链集成、应用案例、FAQ、语法速查表
- [x] 与现有 `executablebooks-myst-guide/` 资料库定位互补，无大段重复内容

## 内容覆盖验证
- [x] MyST 定义、核心特点、设计理念章节完整
- [x] MyST vs CommonMark 对比表格存在，至少列出10个差异点/增强点
- [x] 基础语法覆盖完整：标题(6级)、段落换行、文本强调(粗/斜/删/行内代码)、水平线、转义、HTML、列表(无序/有序/嵌套/任务/定义)、链接(6种类型)、图片
- [x] Directives 核心概念讲解完整：两种围栏语法、选项三种写法、嵌套规则
- [x] Roles 核心概念讲解完整：语法、与Directives区别、至少8个常用Roles示例
- [x] 交叉引用完整：标签添加(自动+显式)、ref/numref/eq/doc 四种引用方式、完整示例
- [x] 数学公式完整：行内公式、块级公式、标签引用、常用数学符号表
- [x] 代码块增强完整：linenos/emphasize-lines/caption/label 选项
- [x] 注释、脚注、参考文献快速入门完整
- [x] 扩展组件覆盖：admonitions(≥8种)、card、dropdown、tab-set/tab-item、table/list-table、figure
- [x] 三种工具链集成指南完整：Sphinx+myst-parser、Jupyter Book v1、mystmd，每种包含安装、最小配置、构建命令
- [x] 至少2个完整应用案例：技术文档项目、学术/技术报告
- [x] FAQ章节至少15个问题，覆盖语法/构建/工具链/迁移/编辑器问题
- [x] 语法速查表紧凑实用，包含≥12项基础语法、≥15个Directives、≥12个Roles、工具链命令对照

## 文档规范验证
- [x] 每个文档包含 YAML frontmatter（id、title 字段）
- [x] 所有文档行数 <300行（原子化原则）
- [x] 所有内部交叉引用使用相对路径，无 `file:///` 绝对路径
- [x] 每个章节文档包含双向导航：上一章/返回目录/下一章
- [x] 所有链接（包括到现有资料库的链接）有效，通过 `check-links.py` 检查零断链
- [x] 文档语言为中文，专业术语附中文解释
- [x] 每个语法点配有可直接复制的代码示例
- [x] 文档风格与现有知识库其他教程保持一致

## 质量检查验证
- [x] examples/ 目录下包含各组件演示文件和案例骨架
- [x] appendix/ 目录下包含语法速查表和参考资源
- [x] docs/knowledge/README.md 中已添加本教程的条目
- [x] 整体学习路径从易到难，逻辑连贯
- [x] 工具链配置示例（conf.py/_config.yml/_toc.yml/myst.yml）正确可参考
- [x] 每个扩展组件配有使用场景说明
- [x] FAQ中的问题是实际高频遇到的，解决方案实用
- [x] 语法速查表设计紧凑，适合快速查阅
