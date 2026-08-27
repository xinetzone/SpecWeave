# 知识沉淀报告索引

本目录存放基于七概念方法论知识沉淀场景（R→I→E→V链路）生成的分析报告。每份报告记录从复盘事实到洞察分析、模式萃取、对抗审查的完整闭环。

## 报告列表

| 报告ID | 报告名称 | 日期 | 场景 | 链路 | 质量门 | 核心成果 | 链接 |
|--------|---------|------|------|------|--------|---------|------|
| seven-concepts-analysis-kicrd | 微信文章分析任务知识沉淀（kICrd） | 2026-07-04 | 知识沉淀 | R→I→E→V | G1✓ G2✓ G3✓ V门✓ | 11条事实、3条核心洞察、2个可复用模式(BP-DUAL-LAYER+BP-SUBAGENT-STD)、4项原子行动项，全部质量门通过 | [kicrd-seven-concepts-analysis-20260704.md](kicrd-seven-concepts-analysis-20260704.md) |

## 归档规范

1. 所有知识沉淀报告必须通过七概念方法论R→I→E→V链路生成
2. 报告frontmatter必须包含id、date、type、source字段
3. G1-G3质量门与V对抗审查门必须全部通过才可归档
4. 报告文件命名格式：`<任务标识>-seven-concepts-analysis-<YYYYMMDD>.md`
5. 新增报告后必须更新本README索引
6. 归档后必须运行 `python .agents/scripts/check-links.py --path docs/retrospective/reports/knowledge/` 验证链接有效性
