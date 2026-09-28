---
type: spec
title: "《WorkBuddy，提个需求就能做产品了？》博文 → OKF Wiki 知识包"
status: approved
created: 2026-09-28
skill: blog-article-to-okf-wiki
source_url: "https://mp.weixin.qq.com/s/RePxoTb2EXkSWnoWhLjapQ?from=industrynews&color_scheme=light#rd"
---

# Spec：WorkBuddy「一句话需求」实测博文 → OKF 知识包

## 1. 内容敏感度预检（阶段 0）

- URL 为微信公众号公开文章（`mp.weixin.qq.com`，无 `token=`/`share?code=`/邀请码等访问控制参数）→ **公开内容（Public）**
- 走标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/workbuddy-one-sentence-blog-okf-wiki/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`
- **信源距离预判**：厂商自宣相邻——第三方产品经理媒体（网易号同步源显示为「人人都是产品经理社区」）发布的腾讯 WorkBuddy 正面「实测」软文，文末含试用导流 CTA（F-022），与 2026-09-24 小程序发布能力官宣同日配套传播。核心声明（沙利文双榜第一、新增应用发布能力）默认 P0；文末「厂商赞助」关系无官方证据，按属性判断标注，不做事实断言（F-032）

## 2. 骨架判定（操作可复现性两问）

| 判据 | 结论 |
|------|------|
| 问 1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **否**。全文为第一人称体验叙事，操作以截图承载（纯文本提取后无点击路径、无参数、无代码），无可照做步骤 |
| 问 2：流程是否经作者实测、具备可复现性（版本、输入输出、步骤顺序）？ | **否**。无客户端版本号（核验后才知 5.6.1）、无输入输出记录、无环境说明，不可由读者复现 |

→ **任一为「否」，不设 `examples/`**。内容性质：**厂商正面产品体验软文（商业/产品资讯类）**；目录骨架 = index + concepts/ + references/ + log.md；description 显式标注「产品体验资讯，非操作教程」。

## 3. 归属位置分析（决策树）

主线实体 = WorkBuddy（腾讯自主研发桌面 AI 智能体，F-023）。

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/tencent/`（选定） | ✅ | ① 主线实体 WorkBuddy 为腾讯产品；② 分组已有同主体非源码类 bundle 先例：`tencent-buddy-family`（WorkBuddy/CodeBuddy/DataBuddy 产品观察，flagged，非操作教程）、`workbuddy-sandbox-public-endpoint`（WorkBuddy 运行边界核验）、`octop`（WorkBuddy/Octop），可主题互链；③ 分组导语已声明收录「腾讯系开源与商业项目」 |
| `jishu/ai/ai-agent/` | ❌ | 收录 Agent 运行时框架源码解读，博文非源码主题 |
| `sheke/industry/` | ❌ | 收录 AI 行业商业趋势快照；本文主线是具体产品能力实测而非行业分析，落 ai/tencent 更便于与同主体 bundle 聚合 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

**产出路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/tencent/workbuddy-one-sentence-mvp/`

## 4. 知识地图（I 阶段三层拆分）

商业/产品资讯类三层映射（无 examples）：

| 层 | 篇目 | 覆盖 F 编号 |
|----|------|-----------|
| 事件时间线层（What/When/Who） | `concepts/00-ranking-event-and-product.md` 双榜第一事件与 WorkBuddy 产品背景 | F-001、F-002、F-023 ~ F-028、F-032 |
| 机制/体验层（How：五阶段实测 + 能力机制） | `concepts/01-one-sentence-mvp-walkthrough.md` 一句话需求到 MVP 的实测全流程 | F-004 ~ F-020、F-029 ~ F-031 |
| 格局/判读层（So-what：评价框架与软文读法） | `concepts/02-agent-capability-reading.md` 桌面 Agent 能力判读与营销叙事识别 | F-002、F-003、F-021、F-024 ~ F-029 |

信源层：`references/article-source.md`（F-001~F-032 双份登记）+ `references/verification.md`（8 项核验：6✅/2⚠️/0❌）。

## 5. 事实与核验摘要

- 共 **32 条事实**：F-001 ~ F-022 博文事实（其中 F-003/F-010/F-012 末句/F-015/F-019 末句/F-020/F-021 显式标注作者观点/体验评价，F-022 为营销 CTA），F-023 ~ F-032 核验补充
- 核心声明核验：沙利文双榜第一 ✅（2026-09-20 发布，央广网/21 世纪经济报道/雷锋网三源）；应用发布能力 ✅（2026-09-24 上线、5.6.1+、14 天试用版、微信第三方服务商身份，IT 之家/Tech 星球）；腾讯身份、100+ 专家、50+ 版本、月活 1115.23 万（AICPB/科技日报）均 ✅
- ⚠️ 单源两项：「腾讯问卷」具体连接器（F-031）、微信原文账号与精确发布日期（F-032）
- **源文零硬错误**，无需 flagged；`status: stable` + 软文提示块 + 已知边界；`stale_after: 2026-12-31`

## 6. ADDED Requirements（验收标准）

### Requirement: 信源先行与双份 F 编号一致

bundle 的 references/ 先于 concepts/ 生成；`article-source.md` 与本 spec `facts.md` 的 F 编号集合须正则比对一致（F-001~F-032 连续无跳号）。

### Requirement: 事实分层与软文提示

作者观点/体验评价（F-003、F-010、F-015、F-020、F-021 等）在 concepts 中保留性质标注；index 顶部放置「厂商正面实测软文」提示块；腾讯问卷连接器与元信息缺口在已知边界中单列。

### Requirement: 三级索引与计数同步

父级 `tencent/index.md` 导航表加行 + toctree 追加 + 束数 7→8、事实/概念/信源聚合计数更新；`bundles/index.md` total_bundles 571→572、jishu 431→432、ai 211→212（正文计数三处同步）。

### Requirement: 主题互链

index.md 设「主题关联」段，与 `tencent-buddy-family`、`workbuddy-sandbox-public-endpoint`、`codebuddy` 互链并说明分工。

### Requirement: 机械门禁

UTF-8 strict roundtrip、三级 toctree 条目逐一存在、相对链接全可达、零 `file:///`、frontmatter 双信源齐备；`invoke gates.*` 依赖不可用时执行手动等效清单并在 log.md 注明，禁止谎报。
