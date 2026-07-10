---
id: "retrospective-specweave-contest-advantage-analysis-20260624-meta-insight-02"
title: "洞察 2：信息缺口感知与策略暂挂——\"不知道的不算风险，不知道自己不知道的才算\" ⭐⭐⭐⭐⭐"
source: "external: 不存在-retrospective-specweave-contest-advantage-analysis-20260624/ — v3-v11 信息缺口与假设检验"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-specweave-contest-advantage-analysis-20260624/retrospective-meta-20260625/insights/information-gap-strategy-suspension.toml"
---
# 洞察 2：信息缺口感知与策略暂挂——"不知道的不算风险，不知道自己不知道的才算" ⭐⭐⭐⭐⭐

**现象**：v3-v8 阶段，分析在"评审维度权重未知"的缺口下持续产出策略建议。直到 v9 获取初赛指南后，才确认此前所有关于评审维度的推测都是基于 FAQ 的模糊描述——而实际权重分配（创新30%/体验30%/TRAE深度20%/价值20%）与此前推测存在偏差。

**规律**：

```
已知的未知（可以在分析中标注"待确认"）：
  ✅ "评审维度权重是多少？"           —— v3-v8 标注为"信息缺口"
  ✅ 缺口在 v9 补上后策略无需重写      —— 因为标注了不确定性

未知的未知（在分析中未感知到缺口）：
  ❌ "参赛者的实际作品不是 SpecWeave" —— v3-v10 全程基于错误假设
  ❌ 缺口在 v11 揭示后触发策略全量重写 —— 因为假设未被标注为假设
```

**操作指南**：在多源信息采集中，为每条策略建议标注「假设置信度」——该建议依赖哪些已知信息、哪些信息缺口可能推翻它。当缺口被补上时，只需更新置信度；当缺口证明假设错误时，执行全量重写。

> **一句话**：不是所有信息缺口都同等危险——你在分析中标注了"还差这个数据"的缺口是可控风险，你在分析中根本没意识到还差某个数据的缺口才是定时炸弹。
