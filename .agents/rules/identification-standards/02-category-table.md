---
id: "rules-identification-02-category-table"
title: "硬编码识别标准：分类定义表"
source: "rules/identification-standards.md#分类定义表"
x-toml-ref: "../../../.meta/toml/.agents/rules/identification-standards/02-category-table.toml"
---
# 硬编码识别标准：分类定义表

以下 8 大类硬编码按标识码、典型表现形式及风险等级进行概要划分：

| 类别 | 标识 | 典型形式 | 风险等级 |
|---|---|---|---|
| 固定字符串 | `HARD-STR` | 错误消息、日志文本、UI 标签、提示信息、消息模板 | 中 |
| 固定数值 | `HARD-NUM` | 业务阈值、超时时间、分页大小、权重系数、金额 | 高 |
| 固定路径 | `HARD-PATH` | 文件路径、目录路径、资源路径、临时目录 | 高 |
| 固定 URL/端点 | `HARD-URL` | API 地址、第三方服务地址、回调地址、OAuth 端点 | 高 |
| 固定编码值 | `HARD-ENC` | 字符编码标识、MIME 类型标识、协议版本号 | 低 |
| 固定正则模式 | `HARD-REGEX` | 正则表达式字面量、模式匹配字符串 | 中 |
| 固定颜色/样式 | `HARD-STYLE` | CSS 颜色值、字体大小、间距、边框样式 | 中 |
| 固定配置参数 | `HARD-CFG` | 连接池大小、线程数、重试次数、缓存过期时间 | 高 |
← 上一章: [01 规范说明](01-overview.md) | **[返回索引](../identification-standards.md)** | 下一章 → [03 类别详解：字符串/数值/路径](03-categories-str-num-path.md)
