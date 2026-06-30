+++
id = "tuyaopen-tos-cli-command-registry"
domain = "code"
layer = "code"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "standard"
source = "docs/retrospective/reports/insight-extraction/retrospective-tuyaopen-folder-20260630/insight-extraction.md#3-可复用模式"

[bindings]
rules = []
references = [
  ".temp/libs/TuyaOpen/tos.py#L33-L53"
]
skills = []
+++

# TuyaOpen tos.py 命令注册表模式（单入口 + 子命令字典）

## 场景

- 需要为一个工具链提供统一入口，但又要支持多个子命令（build/flash/monitor 等）。
- 希望新增子命令只改一处注册表，避免散落式入口文件与难以维护的 argparse 分支。

## 结论（模式定义）

用一个 `dict` 作为子命令注册表，再通过 click 的自定义 `cls` 将其装配为命令树：

- 子命令以模块级 `cli` 对象导出
- 根入口聚合导入并注册到 `CLIS = {...}`
- 根命令使用 `@click.command(cls=set_clis(CLIS))` 绑定子命令集合

## 证据（来自 TuyaOpen）

- `CLIS = { "version": ..., "prepare": ..., "check": ..., "build": ..., ... }`：[tos.py](../../../../.temp/libs/TuyaOpen/tos.py#L33-L47)
- 根命令绑定注册表：[tos.py](../../../../.temp/libs/TuyaOpen/tos.py#L50-L53)

## 适用边界

- 适用：工具链 CLI、脚手架 CLI、需要多子命令且扩展频繁的场景。
- 不适用：单命令脚本或子命令极少且不需要自动补全/帮助系统的场景。

## 验证方法

1. 新增一个子命令模块（导出 `cli`），并在 `CLIS` 中增加映射项。
2. 运行 `tos.py -h` 验证新命令已出现在帮助列表。

