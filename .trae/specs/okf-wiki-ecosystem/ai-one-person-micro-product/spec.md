---
type: spec
title: "AI 一人公司与单点微型产品博文转 OKF Wiki"
source: "https://mp.weixin.qq.com/s/NgiuQ1DfKyiaqhYOWRz_CA"
status: completed
---

# AI 一人公司与单点微型产品博文转 OKF Wiki

## 内容敏感度预检

来源为公开微信公众号文章，无 `code`、`token`、邀请码或内部域名信号，判定为 Public。按公开工作流处理：本 spec 位于 `.trae/specs/`，最终知识包位于 `projects/awesome-okf-xs/doc/bundles/`。

## 场景与方法论链路

- 场景：知识沉淀
- 七概念链路：R（事实采集）→ I（洞察分层）→ E（方法抽象）→ V（对抗审查）
- 质量门：G1 事实不混入因果判断；G2 洞察含现象、根因、影响、建议；G3 方法可迁移；V 门核对弱信源与数字口径。

## 归属位置分析

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `sheke/industry/`（选定） | ✅ | 文章讨论 AI 一人公司的商业模式、产品定位、需求验证与行业趋势，主线是商业化方法而非具体平台实现。 |
| `jishu/ai/` | ❌ | 该分组主要承载模型、Agent、平台与工程实现；本文没有可复现的技术实现流程。 |
| `sheke/marketing/` | △ | 文章包含用户验证和分发建议，但主结论是 AI 微型产品的整体商业化逻辑，行业分组更完整。 |
| 新建分组 | ❌ | 单篇文章不新建顶级分组。 |

## 骨架判定

文章没有版本、输入输出、步骤顺序明确且经作者实测的安装/配置/代码流程。两问判定为“否”，因此不创建 `examples/`，采用商业分析/战略资讯骨架：

`index.md` + `concepts/` + `references/` + `log.md`

## 知识地图

1. `00-single-friction-and-value.md`：单点痛点如何成为付费价值。
2. `01-narrow-product-and-solo-economics.md`：窄产品、一人公司与低试错成本。
3. `02-validation-loop-and-boundaries.md`：十人验证法、证据边界与可迁移检查。

## 已知边界

- 原文未提供脚注或外部原始链接，Photo AI、Coconote、Cal AI 的收入、下载量、收购等数字不得视为独立审计事实。
- Coconote 的部分增长数据可由 RevenueCat、Sub Club 等二手材料交叉支持，但仍不等于财务审计。
- Cal AI 的收购与“超过 1500 万下载、超过 3000 万美元年收入”可由 MyFitnessPal 公告转述材料支持；收入仍属于公司/媒体口径。
- “功能多一分成本翻一倍”“10 人中 3 人认可即可收费”等属于作者建议或经验规则，不是普适定律。
