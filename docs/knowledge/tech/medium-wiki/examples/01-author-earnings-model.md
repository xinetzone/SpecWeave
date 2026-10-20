---
type: Example
category: tech
okf_version: "0.2"
title: "作者收入模式演算：Medium vs Substack（示例）"
description: "用同一假设作者（月 1 万阅读、付费订阅 200 人）在 Medium 与 Substack 两种模式下的收入路径对照演算，展示分成引擎与自营订阅的数学差异。"
tags: [medium, substack, earnings-model, worked-example, creator-economy]
date: "2026-10-20"
last_verified: "2026-10-20"
status: stable
author: "SpecWeave"
source: "https://help.medium.com/hc/en-us/articles/360036691193 | https://mattgiaro.com/medium-vs-substack/ | https://brennan.day/medium-vs-substack/"
summary: "同一作者的两种收入路径演算：Medium 按会员阅读时长分成（收入不确定、随算法波动）；Substack 按订阅人数线性分成（90% 归作者），并讨论各模式对头部/长尾作者的含义。"
---

# 作者收入模式演算示例

> 本示例为**假设演算**，用于直观展示两种分成模式的数学结构，不代表 Medium 或 Substack 的真实支付水平。Medium 未公开分成公式，Substack 费率以公开资料为准 [S03][S08]。

## 假设前提

同一假设作者"阿明"，每月产出 8 篇文章：

| 参数 | Medium | Substack |
|------|--------|----------|
| 月阅读/订阅 | 1 万次会员阅读（假设） | 200 个付费订阅（假设） |
| 定价 | 读者统一 5 美元/月会员 | 阿明自定 8 美元/月 |
| 分成结构 | 按会员阅读时长占平台总时长的比例分配订阅池 | 平台抽 10% + Stripe 2.9%+0.30 美元/笔 |
| 受众数据 | 不拥有 | 拥有（可导出） |

## 演算

### Medium 路径（示意）

Medium 的 Partner Program 将每月订阅池按"会员在你内容上的阅读时长占比"分配 [S03]。示意公式：

```
阿明收入 ≈ 订阅池 × (阿明内容阅读时长 / 平台总阅读时长)
```

- 若订阅池为 100 万美元、阿明占比 0.01% → 月收入 100 美元；
- 收入随算法分发、会员参与度波动，无法线性预测 [S08]。

### Substack 路径

```
阿明收入 = 200 × 8 × (1 − 10%) − 200 × (0.30 + 2.9%×8)
        ≈ 1600 − 160 − (60 + 46.4)
        ≈ 1333.6 美元/月
```

- 收入随订阅人数线性增长，可预测 [S08]。

## 对照结论

| 维度 | Medium | Substack |
|------|--------|----------|
| 收入上限 | 取决于平台总池与算法分发 | 取决于自建受众规模 |
| 收入可预测性 | 低（黑箱算法） | 高（线性） |
| 冷启动难度 | 低（算法推荐） | 高（自建邮件列表） |
| 长期资产 | 低（不拥有受众） | 高（可携带） |

## 对作者的启示

1. **长尾/新作者**：Medium 的低门槛算法发现更友好，适合测试主题与积累作品 [S08]；
2. **头部/职业作者**：Substack 的资产归属与线性收入更符合职业化路径 [S08]；
3. **混合策略**：在 Medium 做发现、在 Substack 沉淀订阅，是 2025 年常见组合 [S08]。

## 计算说明

- 演算数字为简化模型：真实分成含编辑奖金、Boost 等变量 [S08]；
- Substack 费率为公开常例（5-20 美元/月定价区间、10% + Stripe 费）[S08]；
- Medium 未披露分成公式，任何"收入 ≈"均为示意，见 [数据口径](../references/source-inventory.md)。