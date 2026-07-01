---
id: "retrospective-link-fix-depth-adjustment-20260626-insight-08"
source: "insight-extraction.md#发现-8缓存是定期检查类工具的必备能力"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/insights/insight-08-cache-for-periodic-checks.toml"
---
# 发现 8：缓存是定期检查类工具的必备能力

> ✅ 本洞察已归档为全局代码模式：[periodic-check-caching](../../../../../patterns/code-patterns/periodic-check-caching.md)（L1）

外部链接检查加入7天缓存后，二次运行从10-20秒降至<1秒。任何访问外部资源或执行耗时计算的检查工具都应内置可配置缓存：支持--no-cache强制重检、--cache-ttl自定义有效期、--clear-cache清缓存。缓存目录须在.gitignore中，过期自动刷新不报错。
