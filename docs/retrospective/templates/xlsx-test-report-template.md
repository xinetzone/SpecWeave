---
id: "xlsx-test-report-template"
title: "{title}"
report_type: "xlsx-test-report"
source: "{source}"
x-toml-ref: "../../../.meta/toml/docs/retrospective/templates/xlsx-test-report-template.toml"
format: "markdown"
date: "{date}"
status: "generated"
---
# {title}

{fallback_notice}
## 结论摘要

- 发布判断: {release_decision}
- 发布门槛: {release_threshold}
- 当前差距: {release_gap}

## 基本信息

{basic_info_lines}

## 工作簿结构

{workbook_summary_lines}

## 总体结果

{overall_metrics_lines}

## 模块结论

{module_findings_lines}

## 风险聚类

{risk_clusters_lines}

## 最终判断

{final_conclusion}
