---
title: "候选模式记录（单案例，待第二案例验证后正式入库）"
date: 2026-07-28
status: candidate
source_count: 1
---

# 候选模式记录

> ⚠️ 以下模式均来自单次bugfix案例，按萃取规范单案例不得入库为正式模式。记录于此，待第二案例出现后升级为正式模式。

## 候选模式1：CI门禁工具默认静默模式（Default-Silent for CI Gates）

**与现有模式的关系**：现有 [dual-channel-tiered-logging](../../../patterns/code-patterns/dual-channel-tiered-logging.md) 覆盖"控制台简洁+文件详细"双轨场景，但未覆盖"CI门禁工具默认零诊断输出"场景。本候选模式可作为其补充变体。

**核心差异**：
- 现有模式：Logger=DEBUG，ConsoleHandler=INFO（默认有INFO输出）
- 候选模式：Logger=CRITICAL+1，ConsoleHandler=NullHandler（默认零输出），仅 `-v` 时挂载StreamHandler

**触发场景**：CLI工具被CI/CD流水线或其他脚本消费stdout时，任何stderr诊断输出都会被视为噪音。

**待验证**：需要第二个CI门禁工具案例（如check-sensitive-info、link-check等）确认模式通用性。

---

## 候选模式2：多信号风险类别的严重度平方加权选择（Severity-Squared Weighted Category Selection）

**核心算法**：
```python
cat_scores = {}
for s in signals:
    if s.category == "context":
        continue
    cat_scores[s.category] = cat_scores.get(s.category, 0) + int(s.severity) ** 2
primary = max(cat_scores, key=cat_scores.get)
```

**为什么用平方而非线性**：平方放大了高严重度的权重，确保一个CRITICAL（16分）胜过两个HIGH（9+9=18分仍不够，因为两个HIGH的升级规则已单独处理），避免低严重度信号的"人海战术"淹没真正的高风险类别。

**待验证**：需要其他多信号分类/优先级决策场景（如告警聚合、漏洞优先级排序等）验证算法普适性。

---

## 候选模式3：多规则扫描的展示层二元组去重（Presentation-Layer Deduplication for Rule Scanners）

**核心原则**：
1. 规则层保持独立匹配（不去重），不同规则可能提供不同维度的风险描述
2. 展示层在渲染给用户前必须按 `(description, matched_text)` 二元组去重
3. 去重后按严重度降序，截断到Top N
4. DEBUG日志中记录去重统计供验证

**待验证**：需要第二个多规则扫描工具案例（如SAST/DAST/Lint工具）确认展示层去重是通用需求。
