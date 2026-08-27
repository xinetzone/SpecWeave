# OKF Bundle 转换日志

## 2026-08-22

- **Bundle 名称**：specweave-tech-docs
- **OKF 版本**：0.2
- **转换日期**：2026-08-22
- **转换过程**：`process:docs-to-okf-conversion`
- **验证过程**：`process:seven-concepts-v`

## 文件映射

| 原始路径 | 目标路径 | 类型 | 处理说明 |
|---|---|---|---|
| `index.md` | `index.md` | Bundle 根 | frontmatter 精简为仅 `okf_version: "0.2"`；修正 toctree 与目录清单表格路径 |
| `README.md` | `references/readme.md` | Reference | 内容与 index.md 不同，移动至 references/；保留原有 frontmatter 字段；修正 9 处内部链接 |
| `intro.md` | `concepts/intro.md` | Tutorial | 新增完整 frontmatter；正文无链接需修正 |
| `quickstart.md` | `concepts/quickstart.md` | Tutorial | 新增完整 frontmatter；正文无内部链接需修正 |
| `features.md` | `concepts/features.md` | Tutorial | 新增完整 frontmatter；正文无内部链接需修正 |
| `contributing.md` | `concepts/contributing.md` | Reference | 新增完整 frontmatter；`../../AGENTS.md` → `../../../AGENTS.md` |
| `changelog.md` | `concepts/changelog.md` | Reference | 新增完整 frontmatter；`../../CHANGELOG.md` → `../../../CHANGELOG.md` |
| `four-layer-logging-pattern.md` | `concepts/four-layer-logging-pattern.md` | Pattern | 新增完整 frontmatter；两处 `../../.agents/` → `../../../.agents/` |
| `release-onnx-pytorch-v1-1.md` | `references/release-onnx-pytorch-v1-1.md` | Reference | 保留原有 frontmatter（id/title/category/date/source），追加 OKF 字段；正文无内部链接需修正 |
| `release-onnx-quantized-v2.md` | `references/release-onnx-quantized-v2.md` | Reference | 保留原有 frontmatter，追加 OKF 字段；同目录链接 `release-onnx-pytorch-v1-1.md` 保持不变 |
| — | `concepts/index.md` | 目录索引 | 新建，无 frontmatter |
| — | `references/index.md` | 目录索引 | 新建，无 frontmatter |

## Frontmatter 规范

所有内容文件（不含根 index.md 与子目录 index.md）均包含以下字段：

```yaml
type: "<Tutorial|Reference|Pattern>"
title: "<标题>"
description: "<描述>"
generated:
  by: "process:docs-to-okf-conversion"
  at: "2026-08-22T00:00:00Z"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00Z"
status: "stable"
stale_after: "2027-08-22"
```

已有 frontmatter 的文件（README.md、两个 release 文件）保留原有 `id`、`title`、`category`、`date`、`source` 字段，并在其后追加上述 OKF 字段。

## 链接修正汇总

| 文件 | 原始链接 | 修正后链接 | 原因 |
|---|---|---|---|
| `concepts/contributing.md` | `../../AGENTS.md` | `../../../AGENTS.md` | 目录深度增加一层 |
| `concepts/changelog.md` | `../../CHANGELOG.md` | `../../../CHANGELOG.md` | 目录深度增加一层 |
| `concepts/four-layer-logging-pattern.md` | `../../.agents/scripts/templates/path-migration-template.py`（两处） | `../../../.agents/scripts/templates/path-migration-template.py` | 目录深度增加一层 |
| `references/readme.md` | `changelog.md` | `../concepts/changelog.md` | 文件移动至 references/ |
| `references/readme.md` | `contributing.md` | `../concepts/contributing.md` | 同上 |
| `references/readme.md` | `features.md` | `../concepts/features.md` | 同上 |
| `references/readme.md` | `four-layer-logging-pattern.md` | `../concepts/four-layer-logging-pattern.md` | 同上 |
| `references/readme.md` | `index.md` | `../index.md` | 同上 |
| `references/readme.md` | `intro.md` | `../concepts/intro.md` | 同上 |
| `references/readme.md` | `quickstart.md` | `../concepts/quickstart.md` | 同上 |
| `references/readme.md` | `../README.md`（两处） | `../../README.md` | 目录深度增加一层 |
| `index.md` | toctree 中裸文件名 | `concepts/` 或 `references/` 前缀路径 | 反映新目录结构 |

## 最终目录结构

```
docs/tech/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── intro.md
│   ├── quickstart.md
│   ├── features.md
│   ├── contributing.md
│   ├── changelog.md
│   └── four-layer-logging-pattern.md
└── references/
    ├── index.md
    ├── readme.md
    ├── release-onnx-pytorch-v1-1.md
    └── release-onnx-quantized-v2.md
```

## 备注

- 所有正文内容保持原样，未做改写
- `generated` 与 `verified` 字段均采用嵌套 YAML 格式，未使用 inline 花括号
- 根 `index.md` 的 toctree 与目录清单表格已同步更新为新路径
