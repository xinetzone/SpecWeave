+++
id = "tuyaopen-risk-pr2"
source = "export-suggestions.md#pr2ci-cd-故障风险"
created_at = "2026-06-30"
tags = ["risk", "process", "CI/CD"]
type = "process"
+++

# 风险 PR2：CI/CD 故障风险

**风险描述**：self-hosted runner 可能故障

**可能性**：低

**影响程度**：中

**预防措施**：
1. 建立备用 runner
2. 实现构建产物缓存
3. 建立手动构建指南

**应急预案**：
1. 切换到备用 runner
2. 手动构建发布

---

**[返回导出建议索引](../export-suggestions.md)**