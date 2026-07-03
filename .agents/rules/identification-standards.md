---
id: "rules-identification-standards"
title: "硬编码识别标准"
source: "AGENTS.md#规则体系"
x-toml-ref: "../../.meta/toml/.agents/rules/identification-standards.toml"
---
# 硬编码识别标准

> 本文档定义硬编码（Hard-coding）的统一识别标准，为代码审查和自动化检测提供判断依据，覆盖8大类硬编码场景。

## 文档导航

| 文档 | 主题 | 说明 |
|------|------|------|
| [identification-standards/01-overview.md](identification-standards/01-overview.md) | 规范说明 | 文档目的、定义、适用范围 |
| [identification-standards/02-category-table.md](identification-standards/02-category-table.md) | 分类定义表 | 8大类别（HARD-STR/NUM/PATH/URL/ENC/REGEX/STYLE/CFG）概要与风险等级 |
| [identification-standards/03-categories-str-num-path.md](identification-standards/03-categories-str-num-path.md) | 类别详解：字符串·数值·路径 | HARD-STR/HARD-NUM/HARD-PATH的定义、正反例与检测要点 |
| [identification-standards/04-categories-url-enc-regex.md](identification-standards/04-categories-url-enc-regex.md) | 类别详解：URL·编码·正则 | HARD-URL/HARD-ENC/HARD-REGEX的定义、正反例与检测要点 |
| [identification-standards/05-categories-style-cfg.md](identification-standards/05-categories-style-cfg.md) | 类别详解：样式·配置 | HARD-STYLE/HARD-CFG的定义、正反例与检测要点 |
| [identification-standards/06-boundary-judgment.md](identification-standards/06-boundary-judgment.md) | 区分标准与边界判断 | 合理常量vs硬编码判断矩阵、决策流程图、合理常量典型场景 |
| [identification-standards/07-checklist.md](identification-standards/07-checklist.md) | 检查清单 | 代码审查时的8项快速检查清单 |

**[返回上级](README.md)**
