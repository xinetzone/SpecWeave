---
id: "retrospective-tuya-projects-for-xlsx-agentization-20260701-example-release-gate-summary-20260327"
title: "【20260327】单目1M插值3M232测试报告 测试报告学习摘要"
report_type: "release-gate-summary"
source: "d:\AI\.temp\【20260327】单目1M插值3M232测试报告.xlsx"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-tuya-projects-for-xlsx-agentization-20260701/example-release-gate-summary-20260327.toml"
format: "markdown"
date: "2026-07-01"
status: "generated"
---
# 【20260327】单目1M插值3M232测试报告 测试报告学习摘要

## 结论摘要

- 发布判断: 不建议发布
- 发布门槛: DI <= 12 且 致命+严重 <= 2
- 当前差距: DI=35，严重问题数=11，均未满足门槛。

## 核心指标

- 总用例: 489
- Pass: 380
- Fail: 26
- NoTest: 70
- Block: 13
- DI: 35
- 严重问题数: 11

## Top 风险

- 重启恢复
- 存储回放
- 音频
- 预览稳定性
- 升级稳定性

## 阻塞项

- DI=35，严重问题数=11，均未满足门槛。
- 01功能测试: 发现 53 条高风险状态，其中 FAIL=16、NT=37、Block=0。
- 06音频专项测试: 发现 11 条高风险状态，其中 FAIL=9、NT=2、Block=0。
- 00接口测试: 发现 16 条高风险状态，其中 FAIL=4、NT=12、Block=0。

## 平台影响面

- 重启恢复: `tuya`.camera (特征: hub / cloud_push; 观察面: status / status_range / diagnostics)
- 存储回放: `tuya`.camera (特征: hub / cloud_push; 观察面: status / function / status_range)
- 音频: `tuya`.camera (特征: hub / cloud_push; 观察面: status / function / status_range)

## 复测建议

- 复测模块：重启恢复（优先复核 FAIL/Block 用例）
- 复测存储：TF 卡兼容/卡录首检/回放稳定/文件可用性
- 复测音频：底噪/回声/啸叫/吞字/连续性
- 复测预览：弱网/长时预览/帧率与延迟/同步性
- 复测升级：升级成功率/断电恢复/版本回滚
