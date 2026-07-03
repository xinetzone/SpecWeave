---
id: "myst-example-admonitions-demo"
title: "示例：Admonitions 提示框样式大全"
---

# Admonitions 提示框样式大全

本文件展示 MyST 所有内置提示框样式的实际渲染效果，可直接复制使用。

配套教程：[../08-components-admonitions.md](../08-components-admonitions.md)

---

## 1. note（备注）

:::{note}
MyST Markdown 是 CommonMark 的超集，支持所有标准 Markdown 语法，同时扩展了指令、角色、交叉引用等出版级功能。
:::

---

## 2. tip（小技巧）

:::{tip}
按 `Ctrl+Shift+P` 打开命令面板，可以快速执行各种编辑器命令，无需记忆复杂的快捷键组合。
:::

---

## 3. hint（提示）

:::{hint}
遇到不理解的错误信息时，直接复制错误信息到搜索引擎，通常能快速找到解决方案。
:::

---

## 4. important（重要）

:::{important}
开始教程前，请确保已安装 Node.js 18 或更高版本，否则 mystmd 命令行工具无法正常运行。
:::

---

## 5. warning（警告）

:::{warning}
该 API 在 v2.0 版本中已被废弃，将在 v3.0 中完全移除。请迁移到新的 `fetchData()` 接口。
:::

---

## 6. caution（谨慎）

:::{caution}
执行此脚本将修改系统配置文件，建议先在虚拟机或测试环境中验证，确认无误后再在生产环境运行。
:::

---

## 7. attention（强烈注意）

:::{attention}
本周末（7月5日-7月6日）系统将进行维护升级，期间所有服务暂停使用，请提前安排好工作。
:::

---

## 8. danger（危险）

:::{danger}
此操作将永久删除所有用户数据，且无法恢复！执行前请确认已完成完整备份，并获得负责人书面批准。
:::

---

## 9. error（错误）

:::{error}
构建失败：缺少必要的依赖包 `@myst-theme/core`。请运行 `npm install` 安装所有依赖后重试。
:::

---

## 10. seealso（另见参考）

:::{seealso}
- [MyST 官方 Admonitions 文档](https://mystmd.org/guide/admonitions)
- [上一章：注释、脚注与参考文献](../07-advanced-notes-citations.md)
- [返回教程目录](../README.md)
:::

---

## 11. 自定义标题示例

:::{note} 📝 学习建议
学习 MyST 最好的方式是边学边练，每学完一个语法点就动手写一写，渲染看看效果。
:::

:::{tip} 💡 高效写作
- 先列大纲，再填内容
- 善用提示框突出重点
- 多使用交叉引用保持文档连贯
:::

---

## 12. 嵌套提示框示例

::::{important} 📦 部署检查清单
部署到生产环境前，请确认以下事项：

:::{warning} ✅ 数据库备份
已完成全量数据库备份，并验证备份可恢复。
:::

:::{tip} ✅ 测试验证
所有单元测试和集成测试均已通过，测试覆盖率不低于 80%。
:::

:::{caution} ✅ 回滚方案
已准备好回滚方案，如遇问题可在 5 分钟内恢复到上一稳定版本。
:::

所有检查项确认后才能执行部署操作。
::::

---

## 13. 包含 Markdown 格式的提示框

:::{note} 提示框内支持完整 Markdown
提示框内部可以包含：

- **粗体文本**和*斜体文本*
- `行内代码`和[超链接](https://mystmd.org)
- 有序和无序列表
- 甚至嵌套代码块：
  ```python
  def hello():
      print("Hello, MyST!")
  ```
:::

---

> 💡 提示：本文件本身就是用 MyST 编写的，你可以直接用 `myst start` 预览渲染效果。
