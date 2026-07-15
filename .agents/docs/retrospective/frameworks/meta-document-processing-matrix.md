> **来源**：从 `docs/retrospective/knowledge-extraction.md` 五、可复用决策框架 拆分

# 元文档处理决策矩阵

## 来源
v1.1 数据引用区分优化

## 决策矩阵

| 文档类型 | 识别方式 | 数据引用不一致 | 处理级别 |
|---------|---------|--------------|---------|
| 普通 spec | 非元文档 | ❌ 错误 | 阻塞 |
| 复盘报告 | 关键词/显式标记 | ⚠️ 警告 | 提示 |
| 审计报告 | 关键词/显式标记 | ⚠️ 警告 | 提示 |
| 技术评审 | 关键词/显式标记 | ⚠️ 警告 | 提示 |
| 迁移方案 | 关键词/显式标记 | ⚠️ 警告 | 提示 |

## 识别优先级
显式标记（YAML frontmatter `type`）> 关键词检测 > 结构推断。

> **关联模块**：
> - `concepts/meta-document.md`
> - `patterns/code-patterns/meta-document-detection.md`