---
type: spec
title: 云知声 U2Flash 免费月群公告 + 官方 Q&A → OKF Wiki 知识包
created: 2026-10-21
status: done
workflow: blog-article-to-okf-wiki
scenario: 资讯速报（厂商活动公告 + 官方接入文档 + 社群 Q&A）
bundle: projects/awesome-okf-xs/doc/bundles/jishu/ai/practice/u2flash-free-month/
---

# Spec：云知声 U2Flash 免费月活动 → OKF Bundle

## 0. 内容敏感度预检

- **判定：公开内容**。群公告为公开社群活动文案；全部链接无 `share?code=`/`token=`/邀请码参数；官方模型页、文档页、问卷页可匿名访问；飞书 Q&A 可匿名读取（revision 490）。
- **分流**：标准工作流。spec 落 `.trae/specs/okf-wiki-ecosystem/`，bundle 落 `projects/awesome-okf-xs/doc/bundles/`。

## 1. 信源清单（4+1）

| ID | 信源 | 类型 | 采集 |
|----|------|------|------|
| S1 | 云知声用户社群群公告原文（用户提供，无公开 URL） | 厂商活动文案 | 2026-10-21 |
| S2 | https://maas.unisound.com/model-hub/u2-flash | 官方模型页 | WebFetch 2026-10-21 |
| S3 | https://maas.unisound.com/docs/toolAI/workbuddy | 官方接入教程 | WebFetch 2026-10-21 |
| S4 | https://kcn0mpv7063o.feishu.cn/wiki/MVgSwGLRXi6VDik9nLHciUSunZc | 官方飞书 Q&A（rev.490） | lark-cli 2026-10-21 |
| S5 | https://workbuddy.ai/ | WorkBuddy 官网（实体归属核验） | WebFetch 2026-10-21 |

**信源距离预判**：S1 厂商自宣（营销文案）；S2/S3/S4 均为云知声官方一手信源（价格/限流/端点/排障的权威源）；S5 用于核验 WorkBuddy 出品方。**厂商自宣的成效/赠品数字（"5 亿 token"）默认 P0**，无第三方条款页可佐证时标"厂商自述"。

## 2. 骨架判定（操作可复现性两问）

| 两问 | 判定 | 依据 |
|------|------|------|
| Q1 有读者可照做的安装/配置/调用流程？ | **是** | API curl、WorkBuddy 自定义模型四字段、实名认证 URL（S2/S3/S4） |
| Q2 经作者实测、具备可复现性（版本/输入输出/步骤顺序）？ | **否** | 流程为**厂商官方文档与社群 Q&A 的汇编**，非作者一手实测；Q&A 是多用户故障经验的官方归纳；本会话无 API Key 未实跑 |

→ **不设 `examples/`**。接入与排障步骤以"操作指南型 concept"承载（与先例 `deepseek-v41-flash-1017` 一致：含操作清单但无 examples）。

## 3. 归属判定（决策树）

| 候选位置 | 判定 | 理由 |
|----------|------|------|
| `jishu/ai/practice/u2flash-free-month/` | ✅ **采纳** | 主线实体=U2Flash 模型的限时活动+成本解读；强先例 `practice/deepseek-v41-flash-1017`（Flash 模型发布/成本，8 文件无 examples）与 `practice/fable5-cost-optimization`（AI 编程成本） |
| `jishu/ai/ecosystems/<新厂商>/` | ❌ | 单篇资讯新建厂商生态分组=过度工程，违反"单篇禁止新建分组" |
| `jishu/ai/models/` | ❌ | 该组为模型架构/源码/能力教程，非时效性活动资讯 |
| `sheke/industry/` | ❌ | 行业组承载纯商业/评测分析；本束含可执行接入配置，归技术域更准；行业视角在 concepts 内分层呈现 |

横向关联：WorkBuddy 已由官网核验为腾讯产品（F-013），与库内 `jishu/ai/ecosystems/tencent/workbuddy-*` 5 束互链。

## 4. 知识地图（三层拆分）

| 层 | 文件 | 内容 |
|----|------|------|
| 事件事实层 What/When | `concepts/00-free-month-event.md` | 活动卡片、主体与模型定位（厂商自述标注）、价格/规格/限流、时间窗、"无限量"口径澄清、术语 |
| 操作与排障层 How | `concepts/01-access-and-troubleshooting.md` | 资格三检、API 直连、WorkBuddy 五步配置、Q&A 八问排障表、泛化到其他 OpenAI 兼容工具 |
| 机制与趋势层 Why | `concepts/02-token-economics-and-funnel.md` | 扣费顺序、恢复价、5 亿钩子（非官方测算标注）、免费漏斗拆解（分析者洞察）、限免模型淘金五查法、窗口行动清单 |
| 信源层 | `references/article-source.md` + `verification.md` | F-001～F-030 事实清单（双份登记）、P0 核验台账、勘误 3 条、四视角审查 |

**时效**：活动 2026-10-31 截止，11-01 恢复价；`status: stable`（核心声明零价/活动期/限流均经官方页核验），`stale_after: 2026-11-15`（活动结束 +2 周，便于核对 5 亿 token 到账与恢复价）。

## 5. P0 核验结论摘要

✅ 6 类：活动时间（S1+S2 双源）、三档价格与原价、规格 512K/128K、RPM/TPM、端点与凭证、WorkBuddy 归属腾讯（S5）。
⚠️ 2 类：排障口径（S4 官方 Q&A 单源）、5 亿 token 赠送（厂商自述，无条款页）。
❌ 勘误 3 条：E-1 "无限量"与官方限流矛盾；E-2 Base URL 官方族内两口径并存；E-3 公告错字"在得 5 亿"应为"再得 5 亿"。
