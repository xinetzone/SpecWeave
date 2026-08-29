---
title: 维护指南
description: 知识库维护与扩展指南
last_updated: YYYY-MM-DD
---

# 维护指南

## 1. 新增文档

### 步骤

1. **确定文档类型**
   - 技术文档 → `tech/`
   - 通用知识 → `general/`
   - 深度研究 → `topics/`

2. **创建文件**
   - 使用 [DOC_TEMPLATE.md](DOC_TEMPLATE.md) 作为模板
   - 遵循 [FORMAT_GUIDE.md](FORMAT_GUIDE.md) 格式规范

3. **更新索引**
   - 在对应目录的 `index.md` 中添加文档链接
   - 更新 `toctree` 结构

4. **添加交叉引用**
   - 在相关文档的"延伸阅读"章节添加新文档链接

5. **更新知识图谱**
   - 如有必要，更新 `index.md` 中的 Mermaid 图表

### 命名规范

| 类型 | 命名格式 | 示例 |
|---|---|---|
| 技术文档 | `kebab-case.md` | `quickstart.md` |
| 章节文档 | `chapter-XX-name.md` | `chapter-01-intro.md` |
| API 文档 | `module-name.md` | `api-client.md` |

## 2. 新增领域

### 步骤

1. **创建目录**
   ```bash
   mkdir -p general/new-domain/
   ```

2. **创建索引文件**
   - 创建 `general/new-domain/index.md`
   - 参考 [general/index.md](general/index.md) 格式

3. **更新上级索引**
   - 在 `general/index.md` 的 `toctree` 中添加新领域

4. **定义知识图谱**
   - 在新领域的 `index.md` 中添加 Mermaid 图表

### 领域分类

| 分类 | 说明 | 位置 |
|---|---|---|
| 哲学基础 | 理论框架 | `general/philosophy/` |
| 领域知识 | 跨学科知识 | `general/domain/` |
| 方法论 | 思维模型 | `general/methodology/` |

## 3. 知识图谱管理

### 更新流程

1. **确定节点**
   - 新文档作为节点
   - 确定与现有节点的关系

2. **更新图表**
   - 在对应 `index.md` 的 Mermaid 代码中添加新节点和关系

3. **验证图表**
   - 检查图表渲染是否正确
   - 确保关系逻辑清晰

### 图表类型

| 类型 | 用途 | 示例 |
|---|---|---|
| flowchart | 知识体系结构 | 展示层级关系 |
| sequenceDiagram | 流程时序 | 展示操作流程 |
| classDiagram | 概念关系 | 展示概念层次 |

## 4. 交叉引用管理

### 内部链接

```markdown
[文档标题](relative/path/to/file.md)
```

### 跨模块链接

```markdown
[技术文档](../tech/index.md)
[通用知识](../general/index.md)
```

### 锚点链接

```markdown
[章节标题](#章节标题)
```

## 5. 版本管理

### 版本标注

```yaml
---
version: 1.0.0
---
```

### 变更记录

- 更新 `tech/changelog.md`
- 创建月度变更记录文件 `tech/changelogs/project-YYYY-MM.md`

## 6. 质量保障

### 检查清单

- [ ] 文档包含完整的 frontmatter
- [ ] 标题层级规范
- [ ] 表格格式正确
- [ ] 代码块有语言标识
- [ ] 链接使用相对路径
- [ ] 更新了 `last_updated` 字段
- [ ] 添加了延伸阅读

### 格式检查

```bash
# 使用 markdownlint 检查格式
markdownlint **/*.md
```

## 7. 归档与迁移

### 归档流程

1. 创建归档目录
2. 移动归档文档
3. 更新相关链接
4. 在原位置添加重定向说明

### 迁移流程

1. 更新文档内容
2. 更新所有引用链接
3. 更新知识图谱
4. 更新变更日志

## 8. 协作规范

### 分支管理

- `main`：稳定版本
- `develop`：开发版本
- `feature/*`：功能分支

### PR 流程

1. 创建功能分支
2. 提交文档变更
3. 发起 PR
4. 代码审查
5. 合并到 develop

### 审查要点

- 格式规范
- 内容准确性
- 链接有效性
- 知识图谱完整性

## 9. 工具推荐

| 工具 | 用途 |
|---|---|
| markdownlint | Markdown 格式检查 |
| MkDocs | 文档构建与托管 |
| Mermaid Live Editor | 图表编辑与预览 |
| obsidian | 知识库管理 |

## 10. 常见问题

### Q1: 如何处理断链？

**解决方案**: 使用相对路径，定期运行链接检查工具。

### Q2: 如何组织大型知识库？

**解决方案**: 按领域分层，使用知识图谱展示关联，保持每个文件单一职责。

### Q3: 如何保证文档一致性？

**解决方案**: 遵循格式规范，使用模板，定期审查。