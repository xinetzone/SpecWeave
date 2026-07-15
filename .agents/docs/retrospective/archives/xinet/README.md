# xinet 目录归档体系

> **归档日期**: 2026-06-25
> **归档对象**: `d:\AI\.temp\.chaos\tests\xinet`
> **归档类型**: 元数据归档（文件索引 + 规范文档）

## 归档目录结构

| 目录 | 用途 | 价值等级 |
|------|------|---------|
| [core/](core/README.md) | 核心归档 | 高价值内容 |
| [reference/](reference/README.md) | 参考归档 | 中等价值内容 |
| [temporary/](temporary/README.md) | 临时归档 | 待清理内容 |

## 归档命名规范

### 文件名格式
```
{category-slug}-{sanitized-path}-{timestamp}{extension}
```

### 字段说明
- `category-slug`: 文件分类简写（code/doc/config/credential/backup/test/build/other）
- `sanitized-path`: 原始路径的安全版本（去除特殊字符）
- `timestamp`: 归档时间戳（YYYYMMDDHHMMSS）
- `extension`: 保留原始文件扩展名

### 安全规则
- 所有特殊字符替换为连字符 `-`
- 文件名最大长度 200 字符
- 不包含空格、中文、下划线

## 归档索引

归档索引存储于 `archive_index.csv`，包含以下字段：
- 原始路径
- 归档路径
- 价值等级
- 分类标签
- 文件大小
- 修改时间
- 归档时间
- 更新记录

## 归档说明

本归档采用**元数据归档模式**，不实际复制源文件，仅建立索引清单。实际文件仍保留在原始位置。

### 物理归档策略
- **高价值内容**: 建议按需进行物理归档，创建核心内容的副本
- **中等价值内容**: 保留索引，按需归档
- **低价值内容**: 仅保留索引，建议定期清理

## 关联文档

- [xinet 内容萃取与归档复盘](../../reports/project-governance/archiving-and-migration/retrospective-xinet-content-extraction-archiving-20260625/README.md) — 归档执行过程与结果详情
- [xinet 混沌多项目分析](../../reports/insight-extraction/meta-methodology/retrospective-xinet-chaos-multiproject-analysis-20260625/README.md) — 前期代码洞察分析基础
