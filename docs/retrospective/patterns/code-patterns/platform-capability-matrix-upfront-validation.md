---
id: "platform-capability-matrix-upfront-validation"
title: "平台×量化能力矩阵前置硬校验模式"
type: "code-pattern"
date: "2026-09-09"
maturity: "L1-draft"
source: "npuusertools R/I/E 复盘：SIM i16 split error 定位与能力矩阵收敛 (2026-09-09, npuusertools .agents/docs/2026-09-09-sim-i16-split-error-retrospective.md)"
related_patterns:
  - "configurable-by-default-principle"
  - "config-source-priority-explicitness"
  - "framework-parameter-semantics-verification"
  - "runtime-numerics-golden-binary"
tags: ["platform", "capability-matrix", "quantization", "config-validation", "asymmetric", "hard-error", "config-contract", "toolchain"]
validation_count: 1
reuse_count: 0
documentation_level: "standard"
---

# 平台×量化能力矩阵前置硬校验模式（Platform-Capability-Matrix-Upfront-Validation）

## 背景与动机

编译/部署类工具链中，"数据类型×量化选项"的能力常随目标平台（硬件/仿真、架构代际）而不同。若能力约束只在**量化/执行阶段**才暴露（报错、数值损坏或 crash），用户定位成本极高；更糟的是，工具链可能为了"能用"而在量化阶段**静默改写**用户配置（如把 `asymmetric_activation` 强制为 `false`），掩盖了"所选组合本就不被支持"的事实，导致后续所有精度/性能分析基于被篡改的意图。

本次复盘的直接证据：`a16w8/a16w8_auto + asymmetric_activation=true` 仅 `SIM_VTA4.0 / XM210V300` 支持；此前 npuusertools 在 `set_quantize_config` 中对 VTA2.0 系列静默强制对称量化（提交 6630b66），使"平台不支持该组合"被隐式吞掉，一度误导了对 SIM VTA2.0 a16w8 数值行为的整个排查（最终发现该组合本就不应被使用）。

> **反常识**：配置校验里的"宽容默认"不是友好，而是把平台能力问题转嫁成运行时数值 mystery。能力矩阵应在**配置加载即报错**（含允许列表提示），而不是在量化/编译阶段悄悄降级后再让用户从精度指标反推。

---

## 触发场景

- 工具链支持多个目标平台（仿真/硬件、V2/V3/V4 代际），且平台间算子/量化/数据类型能力不同
- 存在"某量化选项仅在部分平台可用"的硬件约束（如 i16 非对称量化）
- 现状是量化阶段做了隐式降级/强制改写，用户配置未如实生效
- 排障时发现"某组合的数值行为"与"平台能力"纠缠不清

**不适用于**：
- 全平台能力一致（无矩阵差异）的简单工具
- 运行时才能确定的能力（无法静态枚举），仍需在运行时给出同样清晰的错误与允许列表
- 策略性自动降级被产品明确定义为特性（需显式文档化并让用户知情，而非静默）

---

## 核心步骤

1. **维护显式能力矩阵**：以代码常量维护 `平台 → 支持(量化类型, 选项标志)` 的白名单集合（如 `I16_ASYMMETRIC_TARGETS = {"SIM_VTA4.0", "XM210V300"}`）。
2. **前置硬校验**：在配置加载/校验阶段（早于量化与编译）检查组合：
   - 命中允许集合 → 放行；
   - 未命中 → 抛带**允许列表**的错误（`ConfigValidationError: 该组合仅支持 X / Y`），绝不静默改写。
3. **移除量化阶段的隐式覆盖**：删除"强制对称/强制降级"类逻辑；让错误意图在配置层暴露，量化逻辑保持忠实执行用户配置。
4. **回归测试**：为「允许组合放行」与「非法组合报错且信息含允许列表」各写用例；非法组合断言错误类型与提示。
5. **校准示例配置**：把仓库内曾用非法组合的示例/测试配置改为合法组合，避免新版本校验直接拦死既有用例。

---

## 反模式（不要这么做）

- ❌ **量化阶段静默强制改写**：配置被篡改而不告知，精度问题变成"幽灵"，无法追溯
- ❌ **报错信息不含允许列表**：用户不知道"换成什么才对"，只能试错
- ❌ **把校验藏在深处**：直到量化/推理才报错，浪费用户时间与算力
- ❌ **矩阵散落在多处条件里**：同一能力判断在 compile/autotune/export 各写一遍，口径漂移后互相矛盾
- ❌ **只加校验不改示例配置**：仓库自带示例因旧组合集体失败，误导后续使用者

---

## 检验标准

- 非法组合在配置加载阶段即抛错，错误消息含明确允许列表
- 量化/编译阶段不再存在该能力的隐式降级代码（grep 可证）
- 能力集合在单一常量处定义，各模块引用同一事实源
- 合法组合端到端跑通（如 SIM_VTA4.0 + a16w8 非对称编译+推理成功）
- 仓库内示例/测试配置与能力矩阵一致，无被校验拦死的遗留
