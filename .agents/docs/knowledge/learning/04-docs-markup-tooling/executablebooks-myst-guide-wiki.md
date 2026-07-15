---
id: "executablebooks-myst-guide-wiki"
title: "ExecutableBooks 与 MyST Markdown 完整学习指南"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide-wiki.toml"
---
# ExecutableBooks 与 MyST Markdown 完整学习指南

> 基于 executablebooks.org 和 mystmd.org 官方文档系统整理
> 创建日期：2026-07-02
> 源文档链接：[executablebooks.org](https://executablebooks.org) | [mystmd.org](https://mystmd.org)
> 文档形式：原子化学习资料库，包含核心文档、使用示例、配置模板

---

## 文档导航

本文档已按单一职责原则原子化为7个独立章节文件，存放于 [executablebooks-myst-guide/](executablebooks-myst-guide/README.md) 目录：

| 序号 | 章节 | 文件 | 内容概要 |
|------|------|------|---------|
| 00 | 生态概览 | [00-overview.md](executablebooks-myst-guide/00-overview.md) | ExecutableBooks生态、MyST定位、与Jupyter Book关系、核心特性 |
| 01 | 核心语法 | [01-myst-syntax.md](executablebooks-myst-guide/01-myst-syntax.md) | Directives语法、Roles语法、嵌套规则、常用指令速查表 |
| 02 | 项目结构与配置 | [02-project-structure.md](executablebooks-myst-guide/02-project-structure.md) | 标准目录结构、myst.yml详解（project/site块）、常用CLI命令 |
| 03 | Frontmatter配置 | [03-frontmatter-config.md](executablebooks-myst-guide/03-frontmatter-config.md) | YAML元数据字段详解、作者/许可/引用/导出配置 |
| 04 | 目录结构配置 | [04-table-of-contents.md](executablebooks-myst-guide/04-table-of-contents.md) | TOC节点类型、Glob模式匹配、页面标题、隐藏页面、{toc}指令、Slug规则 |
| 05 | 最佳实践 | [05-best-practices.md](executablebooks-myst-guide/05-best-practices.md) | 围栏选择、项目组织、常见陷阱、CommonMark兼容、写作建议 |
| 06 | 参考资源 | [06-resources.md](executablebooks-myst-guide/06-resources.md) | 官方链接、GitHub仓库、核心功能文档索引、社区资源、词汇表 |

---

## 子目录说明

除核心文档外，[executablebooks-myst-guide/](executablebooks-myst-guide/README.md) 目录还包含以下辅助资源：

### examples/ - 实战示例目录

提供可直接运行的MyST语法示例，用于动手实践：

| 文件 | 说明 |
|------|------|
| [basic-syntax.md](executablebooks-myst-guide/examples/basic-syntax.md) | 基础语法示例（标题、列表、链接、图片等CommonMark兼容语法） |
| [admonitions.md](executablebooks-myst-guide/examples/admonitions.md) | 提示框/警告框示例（note/warning/tip/important等） |
| [roles-demo.md](executablebooks-myst-guide/examples/roles-demo.md) | Roles语法演示（数学公式、引用、缩写、下标等） |
| [cross-references.md](executablebooks-myst-guide/examples/cross-references.md) | 交叉引用示例（标签定义、章节引用、图表引用） |

### templates/ - 配置模板目录

提供开箱即用的配置文件模板：

- [myst.yml.template](executablebooks-myst-guide/templates/myst.yml.template) - myst.yml标准配置模板，包含project/site完整配置项注释

### syntax/ - 语法参考目录（预留）

预留目录，未来将存放语法速查卡片、语法树可视化等参考资料（当前仅含.gitkeep标记）。

### resources/ - 资源目录（预留）

预留目录，未来将存放图片资源、字体文件、导出样式表等静态资源（当前仅含.gitkeep标记）。

---

## 快速开始

三步上手MyST Markdown：

1. **安装mystmd**
   ```bash
   npm install -g mystmd
   ```

2. **初始化项目**
   ```bash
   myst init
   ```
   按向导配置项目信息，自动生成myst.yml配置文件。

3. **预览文档**
   ```bash
   myst start
   ```
   启动本地开发服务器，实时预览渲染效果（默认地址：http://localhost:3000）。

---

## 学习路径建议

根据不同背景选择适合的学习路径：

- **初学者（无Markdown/文档工具经验）**：按00→06顺序阅读，配合examples/中的示例动手实践，每学完一个章节就运行对应示例验证理解。
- **有Markdown经验者**：从01（核心语法）开始，重点关注Directives和Roles这两个MyST扩展特性，CommonMark兼容部分可快速浏览。
- **Jupyter Book v1迁移用户**：重点阅读02（项目结构）了解mystmd新架构，参考04（TOC配置）迁移目录结构，03（Frontmatter）了解新的元数据格式变化。

---

## Changelog

<!-- changelog -->
- 2026-07-02 | docs | 初次创建：基于官方文档系统学习并原子化为7份核心文档（00-06）+4个示例文件（examples/）+1个配置模板（templates/myst.yml.template）+2个预留目录（syntax/、resources/）
