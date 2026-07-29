---
id: "core-entry-structured-logging"
title: "核心入口全量日志模式"
type: "code-pattern"
date: "2026-07-23"
maturity: "L1-draft"
source: "retrospective-pycaffe-image-preprocessing-optimization-20260723"
related_patterns: ["structured-lightweight-logging", "dual-channel-tiered-logging"]
tags: ["logging", "debugging", "observability", "python", "troubleshooting"]
---

# 核心入口全量日志模式

在所有外部可见的核心入口函数添加结构化日志，包含「输入形状 + 数据范围 + 耗时」黄金三要素，让调试效率提升一个数量级。

## 触发场景

- 核心计算模块缺乏调试信息，出问题时无从下手
- 绑定层与底层 C++/CUDA 之间有隔离，底层日志不可达
- 排查 shape mismatch、NaN/Inf、不收敛等问题耗时
- 用户层需要快速定位"到底哪一步出了问题"

**不适用于**：
- 内部辅助函数（调用频率高，日志会淹没有效信息）
- 性能极其敏感的热路径（日志开销不可忽略）
- 已经有完善调试器的单步调试场景

## 核心做法

### 1. 确定日志范围

只在**外部可见的核心入口函数**加日志，遵循「入口-出口」两点原则：
- forward / backward / train / predict 等主入口
- 批量操作入口（forward_all / forward_backward_all）
- 配置变更入口（set_mean / set_scale 等参数设置）

### 2. 日志黄金三要素

每条入口日志必须同时回答三个问题：

| 要素 | 作用 | 示例 |
|------|------|------|
| **形状（shape）** | 维度对不对？ | `shape=(64, 3, 224, 224)` |
| **范围统计** | 数值对不对？ | `min=-123.0, max=135.0, mean=0.42` |
| **耗时** | 性能正常吗？ | `completed in 45.23ms` |

### 3. 批量操作额外信息

对于批量/迭代类操作，额外记录：
- 批次号 / 总批次数
- 当前批次大小
- 进度百分比
- padding 样本数（最后一批可能不足）

### 4. 结构化标签

使用统一前缀标签便于 grep 过滤：
```python
logger.info(f"[forward] start_layer='{name}'({idx}), ...")
logger.info(f"[backward] output diffs: ...")
logger.info(f"[forward_all] batch {i}: size={n}")
```

## 反模式

- ❌ **日志轰炸**：在循环内逐元素打印，反而拖慢性能和淹没有效信息
- ❌ **只有异常没有正常**：只在报错时打日志，无法对比正常与异常的差异
- ❌ **只看形状不看数值**：shape 对了不代表数据对了，NaN/Inf/全零 都是 shape 正确但数据错误
- ❌ **没有耗时信息**：不知道是卡在了这一步还是下一步
- ❌ **日志级别用错**：用 ERROR 记正常信息，用 DEBUG 记关键路径，导致过滤困难
- ❌ **格式不统一**：每个函数日志格式都不一样，无法批量 grep 分析

## 检验标准

做完之后怎么知道做对了？

1. **三问原则**：看日志能回答「输入是什么？输出是什么？花了多久？」三个问题
2. **定位效率**：出问题时能通过日志在 5 分钟内定位到具体哪一层/哪一批出了问题
3. **日志量适中**：正常运行时单次调用日志不超过 10 行，不会刷屏
4. **可过滤**：通过 grep [forward] / [backward] 等标签能快速过滤想看的日志
5. **可关闭**：通过 logging 级别配置能在生产环境关闭，不影响性能

## 迁移示例

这个模式还能用在什么其他场景？

- **Web 后端 API**：在每个 API 入口/出口记录请求参数、响应状态、耗时、调用方 IP
- **数据库访问层**：在每个查询入口记录 SQL、参数、返回行数、耗时
- **微服务调用**：在每个服务间调用入口记录请求体、响应码、trace_id、耗时
- **ETL 管道**：在每个处理阶段入口记录输入数据量、输出数据量、耗时、错误数
- **CLI 工具**：在每个子命令入口记录参数、执行结果、耗时，便于用户报告问题
