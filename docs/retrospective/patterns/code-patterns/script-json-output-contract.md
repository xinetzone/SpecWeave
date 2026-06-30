+++
id = "script-json-output-contract"
domain = "code"
layer = "code"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "detailed"
source = "docs/retrospective/reports/competitive-analysis/retrospective-tuyaopen-dev-skills-learning-20260630/insight-extraction.md"

[bindings]
rules = []
references = []
skills = []
related_patterns = ["structured-lightweight-logging", "dual-channel-tiered-logging"]
+++

# 脚本可编排输出契约：统一 --json

## 模式概述

当脚本会被“上层 agent/CI/编排器”调用时，最常见的稳定性问题不是脚本功能错误，而是输出不可解析：

- 输出混杂自然语言与结构化字段
- 错误场景仅打印日志但退出码为 0
- 字段命名与层级随版本漂移

本模式通过统一 `--json` 输出契约，使脚本在“可读输出”与“可编排输出”之间具备可切换的稳定接口。

## 触发条件

- 脚本会被其他脚本/智能体/CI 流水线调用
- 需要可靠地判断成功/失败并获取关键数据
- 需要在不同平台/不同终端编码下保持解析一致

## 接口约定

### 参数

- `--json`：开启机器可读输出

### 输出（JSON 模式）

建议最小字段集合：

- `ok`：boolean
- `error`：string（失败时必须提供）

按场景补充字段（示例）：

- `pid`：number
- `log_file`：string
- `text`：string
- `data`：object

### 退出码

- 成功：退出码 0
- 失败：退出码非 0

## 实现要点

- `--json` 模式下 stdout 只输出一行 JSON
- 人类可读输出走默认模式（不加 `--json`），避免污染 JSON
- 错误时同时满足：`ok=false`、退出码非 0、`error` 非空
- 字段名稳定，新增字段只增不改，禁止重命名既有字段

## Python 最小实现模板

```python
import json
import sys


def out(obj, as_json):
    if as_json:
        sys.stdout.write(json.dumps(obj, ensure_ascii=False))
        sys.stdout.write("\n")
    else:
        for k, v in obj.items():
            sys.stdout.write(f"{k}: {v}\n")


def fail(message, as_json, code=1):
    out({"ok": False, "error": message}, as_json)
    raise SystemExit(code)
```

## 验证清单

- [ ] `--json` 输出可被 `json.loads()` 解析
- [ ] 失败场景退出码非 0 且 `ok=false`
- [ ] 成功场景退出码为 0 且 `ok=true`
- [ ] 输出字段具备向后兼容性（新增字段不破坏旧解析器）

