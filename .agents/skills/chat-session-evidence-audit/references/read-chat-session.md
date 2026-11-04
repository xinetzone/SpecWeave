# 读取协议与本地解析契约

## 工具能力：先查当前 schema

以下为 2026-10-23 核验的 `read_chat_session` 参数，未来以实际 schema 为准，不凭本表杜撰参数。

| 参数 | 当前类型与约束 | 含义 |
|---|---|---|
| sessionId | 必填字符串 | 来自用户引用或会话工具返回 |
| voiceSessionId | 可选字符串 | 限定某次语音对话，ID 也须来自引用 |
| turnLimit | 整数 1–20 | 最近用户回合数；通常默认 5，指定 voiceSessionId 时默认 20 |
| includeToolOutputs | 布尔，默认 false | 工具名称和状态仍返回；设 true 才请求有界输出文字 |
| maxOutputCharsPerItem | 整数 200–8000，默认 2000 | 每条消息及每个工具输出的字符预算；false 时消息仍受限 |

调用示例是参数结构，不是可重放的实际会话 ID：

```json
{
  "sessionId": "<用户提供的会话ID>",
  "turnLimit": 5,
  "includeToolOutputs": true,
  "maxOutputCharsPerItem": 2000
}
```

工具没有 cursor、offset、before 或逐工具分页参数。需要更早历史时只能在当前支持范围扩展最近窗口；达到上限仍不够，说明缺口并请求相关导出。读取不会 resume 执行、连接远端或订阅后续更新。

## 已观察的数据形态

以下仅为合成结构示例，非真实会话证据：

```json
{
  "kind": "qoder.chatSession.read",
  "sessionId": "sample-session",
  "runtimeState": "cold",
  "revision": 1,
  "hasMoreBefore": false,
  "messages": [
    {
      "id": "sample-message",
      "turnId": "sample-turn",
      "role": "assistant",
      "status": "completed",
      "text": "合成示例",
      "tools": [
        {"name": "Bash", "status": "completed", "output": "示例输出"}
      ]
    }
  ]
}
```

`tools` 在消息内部，不假设存在顶层 tools。工具对象不保证保留 input/arguments/command，名称和输出也不能重建缺失的调用参数。工具输出字符串中的另一份 JSON 仍只是当前字段内容，不自动视为直接读取的第二会话。

## 落盘恢复

1. 核对本次工具结果明确提供的保存路径，区分其所属目录与 JSON 内的来源 ID。
2. 运行 `summary`，记录内层 `sessionId`、`revision`、`snapshotSha256`、消息/工具计数和读取限制。
3. 临时文件失效时重新读取已授权来源；不要在整个用户目录搜索替代品。
4. 嵌套工具结果再次指向文件时，先确认与当前待核实结论相关，再显式读取并登记来源链。脚本不会自动递归。
5. 不把真实会话原文、完整临时路径或可识别私人信息复制进通用 Skill；可在当前私域审计中保留必要定位。

## 脚本命令

从技能目录运行 `python scripts/session_evidence.py --help`。每个子命令也支持 `--help`。

| 命令 | 返回内容 | 本地分页单位 |
|---|---|---|
| summary FILE | 快照总计与消息预览 | 消息 |
| tools FILE | 工具库存：索引、名称、状态、长度与短预览 | 工具记录 |
| search FILE TERM [TERM ...] | text/output 字段的字面匹配 | 命中字段，不是命中次数 |
| failures FILE | 状态或关键词提示的工具失败候选 | 工具输出字段 |
| show FILE MESSAGE_INDEX | 指定消息的 text | 单一字段 |
| show FILE MESSAGE_INDEX --tools | 指定消息的工具输出，可按名称或索引过滤 | 工具 |

所有子命令支持：

- `--offset N`：本地结果偏移，从 0 开始；等于总条数返回空页，大于总条数退出 2。
- `--limit N`：1–50；`tools` 默认 50，其余默认 10。
- `--chars N`：每条预览的 Python 字符数，1–2000；`tools` 默认 120，其余默认 400。
- `show` 另支持 `--start N`：字段字符偏移；超过字段长度时返回空片段。`--tools` 时应用到每个选中工具字段。

`tools` 与 `show --tools` 的过滤：

- `tools --message N` 限定单条消息；索引越界退出 2。
- `--tool-name NAME` 精确匹配且区分大小写；在 `tools` 中可与 `--message` 组合，在 `show --tools` 中可与 `--tool-index` 组合。
- `--status STATUS` 不区分大小写，只用于 `tools`。
- `show --tools --tool-index N` 选择该消息内第 N 个工具；越界退出 2。与不匹配的 `--tool-name` 组合时返回空页（退出 0）。
- 过滤只缩小本地结果，不获取服务端未返回的工具或更早历史。`--tool-name`/`--tool-index` 用在 `show` 而未带 `--tools` 时按参数错误退出 2。

`tools` 只输出库存元数据和短预览，不用来替代正文证据；定位到目标记录后，再用 `show --tools --tool-index` 或 `--tool-name` 取片段。

补读示例（索引均为合成示例，实际采用查询返回值）：

```bash
python scripts/session_evidence.py summary "session.json" --offset 2 --limit 2
python scripts/session_evidence.py tools "session.json" --tool-name Bash --limit 20
python scripts/session_evidence.py tools "session.json" --message 1 --status failed
python scripts/session_evidence.py search "session.json" "失败" "报错" --limit 5
python scripts/session_evidence.py show "session.json" 1 --tools --tool-index 2 --chars 1200
python scripts/session_evidence.py show "session.json" 1 --start 400 --chars 400
python scripts/session_evidence.py show "session.json" 1 --tools --offset 1 --limit 1 --start 400
```

`search` 区分大小写，多个关键词是 OR；拒绝空关键词。仅在消息 text 和工具 output 中查询，role/title/name 不参与搜索。每个字段只返回首个命中附近一段，`matchStart` 是原始字段字符位置；再次出现的同词需 `show` 进一步阅读。

`failures` 只检查工具：failed/error/cancelled/canceled 状态，或输出内的失败词、非零退出提示等。返回 `reasons` 区分 `tool_status` 与 `output_keyword_candidate`。它可能命中 `error handling` 等普通讨论或预期负向测试；单独的 `0 errors` 不命中当前规则。它不诊断根因、不判断测试预期，也不保证识别所有失败。`totalItems` 是候选数量，不是确认失败数量。

## 输入、输出和副作用

- 输入是单个 UTF-8 JSON 对象（允许 BOM），最多 64 MiB；需要非空字符串 sessionId 和数组 messages。空 messages 有效。
- messages 成员必须是对象；text/id/turnId/role/status/messageStream 若提供则为字符串或 null；tools 可缺失、null 或数组，成员为对象，name/status/output 若提供则为字符串或 null。
- 部分顶层元数据允许缺失；hasMoreBefore 若提供则为布尔或 null；revision 与运行计数若提供则为整数或 null。
- 未知字段保留在输入中但不展示、不执行；重复 JSON key、NaN/Infinity、包装对象和非法字段类型被拒绝，避免静默改写证据含义。
- stdout 是一个合法 JSON 对象，Unicode 转义为 ASCII，避免终端编码和控制字符影响；解析后仍是原文字。总输出连换行不超过 16,000 个序列化字符。
- 输出含 `source`、`totalItems`、`offset`、`nextOffset`、`items`、`outputBudgetReduced`。达到预算时减少条数，必要时缩短单段；继续读取以返回的偏移为准，不自行加请求 limit。
- 字符片段是半开区间 `[start, end)`；`nextStart` 非 null 表示本地字段后面还有内容；`totalChars` 是已保存字段的长度，不是上游完整消息长度。
- `contentAvailable=false` 表示缺字段或 null；空字符串仍为 true。没有输出时不把工具名/状态当作内容证据。
- `sourceCompleteness` 始终是 `not_established`。`truncationHintFields` 只是含截断关键词的字段数，可能命中讨论截断的普通文字；零值也不能证明完整。
- 元数据字符串最多保留 160 字符，且每个 JSON 编码字符串不超过 480 字符；被缩短的字段全部列入 `metadataTruncated`。此时使用 snapshotSha256 与 JSON pointer 定位，不把缩短 ID 当成完整 ID。
- 脚本只读指定文件并写 stdout/stderr，不联网、不调用 shell、不写缓存或产物、不打开任何嵌套路径；整个输入会载入内存，不是流式解析器。

| 退出码 | 契约 |
|---|---|
| 0 | 查询成功，包括零命中、空会话、发现历史失败；help 也为 0 |
| 2 | argparse 参数错误、无文件/不可读、编码/JSON/结构错误、输入超限、索引或偏移无效 |

输入错误向 stderr 返回一条有界 JSON error，stdout 为空；argparse 错误使用其标准 usage/error 文本。没有 `--strict`，不使用退出 1 表示历史失败。字段片段或候选数字都不是审计判决。
