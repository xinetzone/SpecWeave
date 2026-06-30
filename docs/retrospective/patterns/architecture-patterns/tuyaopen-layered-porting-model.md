+++
id = "tuyaopen-layered-porting-model"
domain = "architecture"
layer = "architecture"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "standard"
source = "docs/retrospective/reports/insight-extraction/retrospective-tuyaopen-folder-20260630/insight-extraction.md#3-可复用模式"

[bindings]
rules = []
references = [
  "docs/knowledge/learning/tuya-open-learning-report.md#三-核心架构-分层设计"
]
skills = []
+++

# TuyaOpen 分层移植模型（TKL/TAL/TDD/TDL）

## 场景

- 你需要阅读或移植 TuyaOpen 到新的芯片/RTOS/主机平台，但被大量组件与目录淹没。
- 你需要快速判断“我应该改哪里、哪些是必须实现的最小集合”。

## 结论（模式定义）

以 **TKL/TAL/TDD/TDL** 作为“分层认知与移植工作分解”的主索引：

- **TKL（Tuya Kernel Layer）**：硬件/内核适配层，移植时必须实现。
- **TAL（Tuya Abstract Layer）**：在 TKL 之上提供统一 OS/系统 API。
- **TDD（Tuya Device Driver）**：具体硬件器件驱动实现。
- **TDL（Tuya Device Library）**：对上层提供器件无关的统一接口。

## 适用边界

- 适用：平台移植、阅读源码、定位驱动与系统抽象、梳理“最小可运行闭环”。
- 不适用：仅做云侧能力调用（不涉及端侧 SDK）或仅做单一示例应用修改（不涉及平台适配）。

## 操作步骤（How to use）

1. 先确认目标平台与第一闭环（建议先 LINUX target），再进入平台移植。
2. 以 TKL 为切入点建立“必须实现清单”，再向上过渡到 TAL。
3. 设备接入按“驱动二层模型”处理：先找 TDL 对外接口，再替换/实现对应 TDD。

## 验证方法（可复现）

- 在学习报告中定位该四层模型与示例说明：[tuya-open-learning-report.md](../../../knowledge/learning/tuya-open-learning-report.md#L69-L78)
- 在实际代码中检索对应前缀目录或符号（例如 `src/**/tkl_*`、`src/**/tal_*`、`src/**/tdd_*`、`src/**/tdl_*`），并验证依赖方向满足“下层为上层提供抽象”。

