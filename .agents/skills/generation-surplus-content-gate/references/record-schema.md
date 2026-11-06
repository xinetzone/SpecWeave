# 验收记录字段契约

配套校验器：[check_acceptance_record.py](../scripts/check_acceptance_record.py)。

## 字段表

| 字段 | 类型 | 必填 | 说明 |
|---|---|:---:|---|
| `record_id` | string | ✅ | 同一产物重复验收时复用，保证幂等 |
| `artifact` | string | ✅ | 产物**相对路径**；不得含盘符或协议前缀 |
| `artifact_type` | enum | ✅ | `bitmap` / `text` / `code` / `data` |
| `expected` | string[] | ✅ | 生成前冻结的正向清单 |
| `negative_constraints` | string[] | ✅ | 生成前写入 prompt 的 `no-X` 短语，**不得为空** |
| `negative_constraints_applied_before_generation` | bool | ✅ | 必须为 `true`；事后补写不算 |
| `missing_items` | string[] | ✅ | 「少了什么」命中项，无则 `[]` |
| `surplus_items` | object[] | ✅ | 「多了什么」命中项，无则 `[]` |
| `surplus_items[].item` | string | ✅ | 计划外元素的内容 |
| `surplus_items[].location` | string | ✅ | 出现位置（左上／页脚／第 N 行…） |
| `surplus_items[].evidence` | string | ✅ | 证据来源（目视审／全文扫／工具输出） |
| `check_method` | string | ✅ | 检查方式；结论为 `clean` 时必填且具体 |
| `conclusion` | enum | ✅ | 见下 |

## conclusion 枚举

| 值 | 含义 | 与列表的约束 |
|---|---|---|
| `clean` | 双向均无发现 | `missing_items` 与 `surplus_items` 必须都为空 |
| `surplus_found` | 发现计划外内容 | `surplus_items` 非空 |
| `missing_found` | 发现缺项 | `missing_items` 非空 |
| `both_found` | 两侧都有 | 两者均非空 |
| `not_checked` | 目视门未执行 | 需在交付说明中明示限制，且 `check_method` 写明原因 |

## 退出码契约

| 码 | 语义标记 | 含义 |
|:---:|---|---|
| 0 | `[CHECK-OK]` / `[SELFTEST-OK]` | 通过 |
| 2 | `[CHECK-FAILED]` / `[SELFTEST-FAILED]` | 契约检出，记录不合规或自检行为异常 |
| 3 | `[IO-ERROR]` | 文件不存在 / 编码 / JSON 解析失败 |

> **为什么不用 1？** Python 未捕获异常固定退出 1，恰是校验脚本常用的检出码。用 2/3 加语义标记，才能区分「确实检出了问题」与「脚本自己崩了」。

## 内置真实样例

[example-record.json](example-record.json) 取自首轮海报生成的真实情况：生成前未建立负向清单，因此校验器会返回 `2 [CHECK-FAILED]` 并命中 `GSG_001`。这是刻意保留的反例——同一份记录若按本门重新执行，应在生成阶段就被拦下，而不是等到交付后目视审才发现。
