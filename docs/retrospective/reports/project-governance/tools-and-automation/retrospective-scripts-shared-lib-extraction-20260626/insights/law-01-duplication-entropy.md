+++
id = "law-duplication-entropy"
date = "2026-06-26"
type = "insight"
scope = "duplication,entropy,governance"
source = "../insight-extraction.md#规律-1重复代码的熵增定律"
+++

# 规律1：重复代码的"熵增定律"

## 观察

项目从 5 个脚本增长到 30 个脚本的过程中，重复代码从 0 行增长到 280 行，且增长速度呈加速趋势。

## 规律

在没有主动治理的情况下，代码重复量随项目规模增长呈**超线性增长**（近似 O(n^1.5)）。原因是：

1. **脚本数量增加** → 新脚本作者找到可复制模板的概率增加
2. **已有脚本积累** → "复制旧脚本改改"成为最低成本路径
3. **认知负担增加** → 作者不知道共享库存在的概率增加

这三个正反馈因素叠加，导致重复量在项目早期增长缓慢，但越过临界点后加速膨胀。

## 对策

- 定期（如每季度）运行重复代码审计
- 在重复量超过阈值（如 200 行）时触发重构
- 将重复检测集成到 CI（已通过 check-duplication.py 第10步实现）

## 关联洞察

- [finding-01-duplication-threshold.md](finding-01-duplication-threshold.md) — 3次阈值是熵增治理的触发点
- [law-02-shared-lib-gravity.md](law-02-shared-lib-gravity.md) — 引力效应是对抗熵增的正反馈机制

---
*来源：[脚本共享库提取复盘](../README.md)*
