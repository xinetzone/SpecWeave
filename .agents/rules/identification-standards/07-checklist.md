---
id: "rules-identification-07-checklist"
title: "硬编码识别标准：检查清单"
source: "rules/identification-standards.md#检查清单"
x-toml-ref: "../../../.meta/toml/.agents/rules/identification-standards/07-checklist.toml"
---
# 硬编码识别标准：检查清单

代码审查时，以下清单用于快速判断是否存在硬编码问题：

| 序号 | 检查项 | 判定标准 |
|---|---|---|
| 1 | 是否存在写死的字符串消息或标签？ | `Ctrl+F` 搜索中文或完整英文句子在非注释代码中的出现位置 |
| 2 | 是否存在写死的业务数值（阈值、金额、比例）？ | 审查条件语句与函数参数中的非零数字字面量 |
| 3 | 是否存在写死的文件系统路径？ | 检查字符串中是否包含 `/`、`\` 与文件扩展名 |
| 4 | 是否存在写死的 HTTP/HTTPS 地址？ | 检查字符串中是否以 `http://` 或 `https://` 开头 |
| 5 | 是否存在写死的正则表达式？ | 检查 `re.match`、`re.search`、`re.compile` 的参数 |
| 6 | 是否存在写死的颜色值或 CSS 样式？ | 检查 `#` 开头的颜色值或含 `px`/`em` 的样式字符串 |
| 7 | 是否存在写死的运行参数（超时、重试、缓存时间）？ | 审查网络调用、缓存操作、线程池等参数 |
| 8 | 每个已确认的字面量是否通过了"合理常量"判定？ | 对照上一节的判断流程图与合理常量表格 |

审查者应在审查报告中标注每个硬编码实例的类别标识（如 `HARD-NUM`），以便开发者精准定位并根据对应的推荐写法进行重构。
---
## 相关模式

- [正则+Markdown解析](../../../docs/retrospective/patterns/code-patterns/regex-markdown-parsing.md)
- [多信号检测](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/multi-signal-detection.md)
---
← 上一章: [06 区分标准与边界判断](06-boundary-judgment.md) | **[返回索引](../identification-standards.md)**
