---
id: "wiki-atom-template-readme"
title: "Wiki原子化模板使用说明"
source: "retrospective-mopmonk-wiki-20260704"
x-toml-ref: "../../../.meta/toml/.agents/templates/wiki-atom-template/README.toml"
---
# Wiki原子化模板使用说明

本目录提供Wiki教程原子化结构的预置模板，基于MopMonk Wiki复盘萃取的标准模式。

## 目录结构

```
wiki-atom-template/
├── README.md                    # 本说明文件
├── example-wiki.md              # 索引页模板（复制后重命名为你的wiki名）
└── example-wiki/                # 原子文件目录（复制后重命名为你的wiki名）
    ├── 00-overview.md           # 概述与学习目标
    ├── 01-core-concepts.md      # 核心概念解析
    ├── 02-step-by-step.md       # 步骤式操作指南
    ├── 03-faq.md                # 常见问题解答
    └── 04-resources.md          # 相关资源链接
```

## 使用方法

### 快速开始（3步）

1. **复制模板目录结构**：
   ```
   复制 example-wiki.md → 目标目录下的 your-wiki-name.md
   复制 example-wiki/ → 目标目录下的 your-wiki-name/
   ```

2. **全局替换占位符**：将所有文件中的 `example-wiki` 替换为你的实际wiki名称（kebab-case英文），`{{标题}}` 替换为实际中文标题，`{{来源URL}}` 替换为原始来源链接。

3. **计算并修正x-toml-ref路径**：
   - 索引页（your-wiki-name.md）：x-toml-ref指向 `.meta/toml/` 镜像路径，层级根据实际位置计算
   - 原子文件（00-overview.md等）：x-toml-ref指向 `.meta/toml/` 镜像路径下的子目录，多一层`../`
   - 参考：mopmonk索引页用 `../../../.meta/toml/...`（3层上级），原子文件用 `../../../../.meta/toml/...`（4层上级）

## 原子化拆分判断标准

不是所有wiki都需要原子化拆分，满足以下任一条件建议拆分：

| 判断维度 | 拆分阈值 | 不拆分场景 |
|---------|---------|-----------|
| 文件长度 | >300行建议拆分 | <200行可保持单文件 |
| 章节独立性 | 各章节可单独阅读引用 | 内容紧密耦合不可分割 |
| 未来扩展 | 预期会持续新增章节 | 内容已稳定不会扩展 |
| 复用需求 | 单个章节需要被其他文档引用 | 整体作为一个完整文档使用 |

## 原子化三原则

1. **单一职责**：每个文件只聚焦一个主题，不跨主题混杂内容
2. **可独立引用**：每个原子文件有完整的frontmatter和TOML元数据，可单独被引用
3. **内部链接完整**：文件间使用相对路径链接，导航表格在索引页中维护

## 标准提交模式（双层提交）

原子化Wiki生产遵循双次提交模式：

| 提交顺序 | 提交内容 | commit message示例 |
|---------|---------|-------------------|
| 第一次提交 | 内容创作（单文件或原子文件内容填充） | `docs(knowledge): 创建xxx Wiki教程` |
| 第二次提交 | 原子化拆分/结构重构 | `docs(knowledge): 原子化拆分xxx Wiki教程` |

两次提交职责分离：第一次聚焦"写了什么内容"，第二次聚焦"怎么组织这些内容"，便于回溯和revert。

## 配套TOML元数据

复制后还需要在 `.meta/toml/` 镜像路径下创建对应的TOML文件：

- 索引页：`.meta/toml/docs/knowledge/learning/your-wiki-name.toml`
- 原子文件：`.meta/toml/docs/knowledge/learning/your-wiki-name/NN-xxx.toml`

TOML字段参考：
```toml
id = "your-wiki-name-NN-xxx"
title = "章节中文标题"
category = "knowledge/learning"
tags = ["标签1", "标签2"]
date = "2026-07-04"
version = "1.0"
source = "原始来源URL"
part_of = "wiki-tutorial-standardization"
```

## 关联参考

- [wiki-spec-template.md](../wiki-spec-template.md) - Wiki教程制作完整工作流模板（四层漏斗+DoD）
- [subagent-wiki-delivery-checklist.md](../subagent-wiki-delivery-checklist.md) - 子代理委派与验收检查清单
- [mopmonk-security-agent-wiki.md](../../../docs/knowledge/learning/mopmonk-security-agent-wiki.md) - 原子化Wiki完整示例
