---
id: "release-gate-summary-template"
title: "{title}"
report_type: "release-gate-summary"
source: "{source}"
x-toml-ref: "../../../../.meta/toml/.agents/docs/retrospective/templates/release-gate-summary-template.toml"
format: "markdown"
date: "{date}"
status: "generated"
---
# {title}

## 结论摘要

- 发布判断: {release_decision}
- 发布门槛: {release_threshold}
- 当前差距: {release_gap}

## 核心指标

{core_metrics_lines}

## Top 风险

{top_risks_lines}

## 阻塞项

{blockers_lines}

## 复测建议

{retest_suggestions_lines}
