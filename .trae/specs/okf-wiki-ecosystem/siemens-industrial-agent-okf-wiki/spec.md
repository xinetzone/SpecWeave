---
title: "Spec：siemens-industrial-agent OKF 知识包"
status: "draft"
---

# Spec：siemens-industrial-agent OKF 知识包

> 来源：量子位/田晏林《工业Agent不是"套壳"大模型！西门子百年经验灌进工业AI》（2026-08-27）
> URL：https://mp.weixin.qq.com/s/ssuJECesZ-UHrW6GRv_BkQ
> 模式：blog-article-to-okf-bundle L2（商业分析骨架，无 examples/）

## 产出位置

- Bundle：`projects/awesome-okf-xs/doc/bundles/ai/ai-agent/siemens-industrial-agent/`
- 归属：ai 域 / ai-agent 组（产品资讯序列）

## 文件骨架（10 文件）

| 文件 | 内容 |
|------|------|
| index.md | 入口、版图Mermaid、数据性质提示、勘误、已知边界 |
| concepts/index.md | 概念学习路径（4篇） |
| concepts/00-industrial-agent-barrier.md | 门槛：43%/8%调研、IT/OT断层、系统工程、办公vs工业对比 |
| concepts/01-eigen-engineering-agent.md | Eigen：ECAD/PLC标签/端到端执行、ROI数据、中科摩通勘误 |
| concepts/02-icx-orchestration.md | ICX编排层、Skill"装接口"、ECX、支点/全晓案例 |
| concepts/03-xcelerator-flywheel.md | 三层架构、阿丘/设序案例、平台数字勘误、飞轮方法论 |
| references/index.md | 信源索引（官方新闻稿+第三方） |
| references/article-source.md | F-001~F-036 事实登记 |
| references/verification.md | P0核验报告（3✅3⚠️） |
| log.md | 变更日志 |

## 事实基数

36条事实（F-001~F-036）；P0核验 3✅ 3⚠️ 0❌。

关键勘误：
1. 平台规模官方口径 800余款产品/500余家伙伴/中国60万用户（博文写900/600/未限定地域）
2. 《2025工业智能体报告》系西门子与至顶科技联合发布（厂商赞助）
3. 中科摩通30/30/10数字2025年稿原归属Industrial Copilot
4. Skill Creator/Agent Framework组件名、Teamcenter PLM对接仅见博文
5. 所有成效数据均为厂商/客户自述

## 质量门

- G1（事实）：36条编号登记，5745字全文逐字提取 ✅
- G2（核验）：6大项3✅3⚠️，勘误不掩盖 ✅
- G3（结构）：3个toctree块、相对链接、无file:///、UTF-8严格解码12/12 ✅
- G4（索引）：bundles 279→280、ai域106→107、ai-agent 27→28（frontmatter=toctree=28）✅
