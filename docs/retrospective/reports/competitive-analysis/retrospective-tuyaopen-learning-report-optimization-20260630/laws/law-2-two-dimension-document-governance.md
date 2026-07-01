---
id: "tuyaopen-law-2-two-dimension-document-governance"
source: "docs/knowledge/learning/tuya-open-learning-report.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/competitive-analysis/retrospective-tuyaopen-learning-report-optimization-20260630/laws/law-2-two-dimension-document-governance.toml"
---
# 规律2：文档治理的双维度检查

**来源**：TuyaOpen 学习报告优化任务

> **归档状态**：本规律已归档为模式 [two-dimension-document-governance](../../../../patterns/methodology-patterns/governance-strategy/two-dimension-document-governance.md)（L2），模式库为唯一权威来源。

## 模型描述

创建新文档时必须同时检查两个维度——位置维度和命名维度。

## 检查维度

| 检查维度 | 检查项 | 合规标准 | 验证工具 |
|---------|--------|---------|---------|
| 位置维度 | 文件放置目录 | 是否在 docs/knowledge/ 下的正确分类目录 | 查阅 docs/knowledge/README.md |
| 命名维度 | 文件名称格式 | kebab-case、纯英文、无中文、无空格 | check-filename-convention.py |

## 适用场景

- 任何创建新文档的任务
- 文档重构和迁移
- CI/CD 流程中的文档检查

## 关联洞察

- [洞察2：双重违规往往暴露流程漏洞](../insights/insight-2-double-violation-exposes-process-vulnerability.md)

## 关联模式

- [文件创建前置检查模式](../patterns/pattern-1-file-creation-precheck.md)