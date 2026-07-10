---
id: "executablebooks-myst-guide-readme"
title: "ExecutableBooks 与 MyST Markdown 学习资料库"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/executablebooks-myst-guide/README.toml"
---
# ExecutableBooks 与 MyST Markdown 学习资料库

## 简介

本资料库系统整理 ExecutableBooks 生态系统和 MyST Markdown 的学习资料，旨在帮助开发者快速掌握 MyST 的核心概念和使用方法。

**MyST 是什么？** MyST（Markedly Structured Text）是 CommonMark Markdown 的超集，灵感来自 Sphinx 和 reStructuredText 生态，专为科学和计算性叙事文档设计。它既保持了 Markdown 的简洁易写，又具备 LaTeX/reStructuredText 的出版级表达能力。

本资料库基于官方文档（[https://executablebooks.org](https://executablebooks.org) 和 [https://mystmd.org](https://mystmd.org)）系统整理而成。

---

## 目录导航

按学习顺序排列的核心文档：

| 文档 | 说明 |
|------|------|
| [00-生态概览](./00-overview.md) | 了解 ExecutableBooks 生态和 MyST 定位 |
| [01-核心语法](./01-myst-syntax.md) | 学习 Directives、Roles 等核心语法 |
| [02-项目结构与配置](./02-project-structure.md) | 掌握 myst.yml 配置和项目组织 |
| [03-Frontmatter配置](./03-frontmatter-config.md) | 文档元数据配置详解 |
| [04-目录结构配置](./04-table-of-contents.md) | TOC 配置和导航管理 |
| [05-最佳实践](./05-best-practices.md) | 使用经验和常见陷阱 |
| [06-参考资源](./06-resources.md) | 官方链接、社区资源和词汇表 |

---

## 子目录说明

### [examples/](./examples/README.md) - 可直接复制使用的代码示例

- **basic-syntax.md** - 基础语法示例
- **admonitions.md** - 提示框样式大全
- **roles-demo.md** - Roles 行内扩展示例
- **cross-references.md** - 交叉引用示例

### [templates/](./templates/) - 配置模板

- **myst.yml.template** - myst.yml 配置模板（含详细注释）

### [syntax/](./syntax/) - 语法速查相关资源（预留目录）

### [resources/](./resources/) - 其他学习资源（预留目录）

---

## 快速开始

3 步快速上手 MyST：

1. **安装 mystmd**
   ```bash
   npm install -g mystmd
   ```
   （或查看官方文档获取其他安装方式）

2. **初始化项目**
   运行 `myst init` 创建项目，或参考 [templates/myst.yml.template](./templates/myst.yml.template)

3. **本地预览**
   运行 `myst start` 启动开发服务器，访问 http://localhost:3000

> 💡 详细命令参考 [02-project-structure.md](./02-project-structure.md)

---

## 适用人群

- 需要编写技术文档、学术论文、书籍的作者
- Jupyter Notebook 用户想要构建可发布的文档
- 从 Jupyter Book v1 迁移的用户
- 需要 Markdown 扩展功能的文档工程师
- 对科学计算和可复现研究感兴趣的人

---

## 学习建议

- **初学者**：建议按文档编号顺序阅读（00 → 06）
- **有经验的用户**：可以直接查阅特定主题
- **动手实践**：配合 [examples/](./examples/README.md) 中的示例动手实践效果最佳
- **快速启动**：使用 [templates/](./templates/) 中的模板快速启动项目

---

## 相关链接

- **官方网站**：[https://executablebooks.org](https://executablebooks.org)
- **MyST 文档**：[https://mystmd.org/guide](https://mystmd.org/guide)
- **GitHub**：[https://github.com/executablebooks/mystmd](https://github.com/executablebooks/mystmd)
