---
type: Pattern
id: "docs-retrospective-patterns-documentation-patterns-index"
title: "文档转化模式"
category: "retrospective"
date: "2026-08-28"
---
# 文档转化模式（documentation-patterns）

> 本目录收录"外部信源 → 结构化知识资产"转化类可复用模式：源码库教程化、博文转化为 OKF 知识包等场景的标准化工作流。

<!-- README_INDEX_START -->

## 📄 文档索引

| 文档 | 说明 | 成熟度 | 标签 |
|------|------|--------|------|
| [技术Wiki教程创建模式](tech-wiki-tutorial-creation.md) | 为第三方开源库创建系统性中文教程Wiki的六步流程：源码结构分析→8+4章节设计→内容编写规范→可运行Demo脚本→索引发布→批量生成元数据一致性检查；vendor 只读约束下在知识区独立落位 | draft | `wiki` `技术文档` `教程模式` `开源翻译` `知识沉淀` |
| [博文类文章→OKF知识包转化模式](blog-article-to-okf-bundle.md) | 微信公众号/技术博客/新闻稿等单篇博文转化为 OKF 知识包的六步工作流：敏感度预检→归属判定决策树→F 编号事实采集与官方核验→三层知识拆分→bundle 生成→四视角对抗审查与 gates.toctrees 门禁验证；解决单信源、时效性价格信息与作者观点混写的可信转化问题 | draft | `博文转化` `OKF` `知识包` `模型选型` `知识沉淀` `信源溯源` |
| [溯源一致性三查模式](source-trace-consistency-check.md) | 含「事实登记表+信源引用」文档体系交付后的四查复核：临时文件残留指向扫描→术语/译名全库一致性（含异体字）→版本差异 vs 转录歧义判别→计数/索引算术自洽核对；解决 .temp 信源断链、译名混用、真实版本差异被误统一、索引计数失真四类隐患 | draft | `OKF` `知识包` `信源溯源` `一致性检查` `质量门` `知识沉淀` |
| [版本差异判别模式](version-discrepancy-arbitration.md) | 同一实体在多文件出现不同署名/年份/卷数时的裁决流程：收集多值清单→权威信源核验（作者官方页/馆藏目录优先）→判别真实版本差异（分版表述+逐版本来源）或转录歧义（全库统一+记录裁决）→裁定依据回写 facts；解决"一刀切统一掩盖正确性"与"保留所有说法不设裁决"两类反模式 | draft | `版本差异` `勘误` `书目知识包` `事实核验` `权威信源` `知识沉淀` |
| [声明对账模式](declaration-reconciliation.md) | 对产出物中"共计、不超过、均为、全覆盖"类自我声明做实证核验的五步流程：声明扫描→实证对账→缺口定性→双向修正（禁止上调声明迁就现状，归档报告先收敛事实+勘误记录）→声明回写；解决先写声明后产出、凭印象填统计数、审查漏检声明类缺陷、机检计数未排除索引文件四类高发问题 | L2（双案例验证） | `声明核验` `事实对账` `勘误` `质量门` `知识沉淀` |

<!-- README_INDEX_END -->

## 模式统计

| 指标 | 数量 |
|------|------|
| 模式总数 | 5 |
| draft（L1 实验性，validation_count=1） | 4 |
| 已验证（L2+） | 1 |

## 🔗 相关资源

- [🏠 返回上级：可复用模式库](../index.md)
- [📚 复盘体系总览](../../index.md)

---

<!-- 2026-08-28 手动创建：登记 blog-article-to-okf-bundle 新模式（源自 spec-deepseek-vision-blog-okf-wiki-20260828），同时补录既有 tech-wiki-tutorial-creation -->
<!-- 2026-08-31 手动登记：source-trace-consistency-check、version-discrepancy-arbitration 两条新模式（源自 sexology-classics-wiki 里程碑复盘，reports/concepts/milestone/retrospective-sexology-classics-wiki-20260830.md） -->
<!-- 2026-09-11 手动登记：declaration-reconciliation 新模式（L2 双案例验证，源自 pipeline-parable 任务链里程碑复盘及两份归档报告声明对账复现） -->
