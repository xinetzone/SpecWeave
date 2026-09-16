---
okf_version: "0.2"
type: spec
title: "免费大模型接入实战博文→OKF 知识包转化规划"
description: "将微信公众号博文《我用3个免费模型，把WorkBuddy的成本砍到了零》（免费大模型接入全攻略 2026-09 实战版）转化为 OKF 知识包，覆盖 Agnes AI / 小红书 dots3 / AMD Radeon 三平台的免费模型、注册拿 Key、OpenAI 兼容接入 WorkBuddy/Trae、图像/视频 API 实操与全局选型"
tags: [okf-bundle, blog-article, free-llm, agnes-ai, dots3, amd-radeon, openai-compatible, workbuddy, trae, model-selection]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-09-16T20:40:00+08:00" }
---

# 免费大模型接入实战博文 → OKF 知识包 转化规划

> 方法论链路：七概念场景 4（知识沉淀）R→I→E→V（C 阶段仅给提交建议，用户未要求不提交），由 blog-article-to-okf-wiki 七阶段工作流执行。

## 1. 内容敏感度预检

| 项目 | 结论 | 依据 |
|------|------|------|
| 来源 | 微信公众号公开文章 | https://mp.weixin.qq.com/s/qnQqCivPiuRfJIVMM-zTNQ |
| 公众号 / 作者 | 技术宅SuperLaos / 老商 | 原创标记，2026-09-10 08:40 发布，IP 属地河北，正文注"整理日期 2026-09-09" |
| 访问控制 | 无（公开可访问） | `/s/<id>` 公开文章格式，无 share?code=/token=/邀请码参数；browser_use 直接提取 16,218 字符无反爬 |
| 敏感度级别 | **公开内容** | 公开技术教程，无个人隐私与商业秘密；文中反而反复强调敏感数据勿传第三方 |
| 工作流模式 | **标准工作流** | spec 在 `.trae/specs/okf-wiki-ecosystem/`，bundle 在 `projects/awesome-okf-xs/doc/bundles/` |
| 信源距离预判 | **第三方综述 + 作者一手实测混合**，Agnes 图像/视频段依据官方文档 | 个人技术号整合多渠道资料；含多条"实测"（并发>5 排队、200 万 token 耗约 5%、16:9 输出 1280x704）；无厂商赞助/软文号特征；无"提效倍数"类营销成效数字。P0 重点：免费额度/价格/截止日期/域名与模型名 |

## 2. 骨架判定（操作可复现性两问）

| 问题 | 回答 | 理由 |
|------|------|------|
| Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **是** | 三平台均给出注册入口→拿 Key 步骤→Base URL/模型名/认证头→WorkBuddy/Trae 客户端配置位→curl 可运行示例（chat/images/videos 三类端点）→验证语句与故障排查表；Agnes Code 给三平台安装包形态 |
| Q2：这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **是** | 步骤顺序完整；有明确输入（curl JSON 体）与预期输出（自我介绍/400 校验失败/status 轮询）；含作者实测口径（1280x704、2624x1472、并发 5、积分消耗 5%）；版本时点锚定 2026-09-09 |

**判定：两问皆"是" → 技术教程/选型类骨架，设 examples/**

**骨架**：
```
jishu/ai/free-llm-api-hands-on/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-free-model-landscape.md            # 三平台发布事实层：免费档位/模型清单/注册门槛（What）
│   ├── 01-platform-deep-dive.md              # 三平台能力与协议机制：多协议网关/异步视频/积分制（Why/How）
│   └── 02-selection-matrix.md                # 全局选型矩阵：三平台横评+国内免费档全景+组合策略
├── examples/
│   ├── index.md
│   ├── 00-agnes-walkthrough.md               # Agnes 注册拿 Key + 文本/图像/视频全流程
│   ├── 01-dots3-walkthrough.md               # dots3 接入 WorkBuddy/Trae（api-key 头特例）
│   └── 02-amd-walkthrough.md                 # AMD Radeon 领 Key 与四模型调用
└── references/
    ├── index.md
    ├── article-source.md                     # 博文事实清单（F 编号双份登记之一）
    └── verification.md                       # P0 核验报告（含勘误四张清单）
```

## 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/free-llm-api-hands-on/`（选定，直挂束） | ✅ | ① 主线是"免费大模型 API 接入"多平台实操，非单一厂商，挂任何厂商分组（agnes-ai 等）均以偏概全；② 组内直挂束先例充分：同主题目录束 `free-llm-api-roundup`（40 家平台目录，2026-06 博文转化，flagged）、博文转化束 mattpocock-skills/todesk-ai 均直挂本组；③ 与 roundup 构成"广度目录 ↔ 深度实战"主题簇，按 L3 规则互链 |
| `jishu/ai/agnes-ai/` 子分组 | ❌ | 该分组定位 AgnesAI 单一生态；本文 3 平台并列且 Agnes 仅占其一（§2），归入会割裂 dots/AMD 内容 |
| `jishu/ai/deepseek-pricing/` 周边 | ❌ | 该束聚焦 DeepSeek 单厂定价；AMD 窗口中的 DeepSeek 快照模型只是四款之一 |
| `sheke/industry/`（AI 行业趋势） | ❌ | 该域为行业快照/商业分析（无操作流程）；本文是可照做的技术教程，操作密度与形态不符 |
| 新建顶级分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

**最终路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/free-llm-api-hands-on/`

**主题簇互链**：与 `jishu/ai/free-llm-api-roundup/`（广度目录，2026-06 时点、flagged）互链——本束负责"3 平台 2026-09 深度实操"，roundup 负责"40 家额度目录"；与 `agnes-ai/agnes-ai-models/`（2.5/2.1 代际）互链——本束补充 3.0/image-2.5/video-2.5 新代际。

## 4. 时效性

| 项目 | 结论 |
|------|------|
| 博文发布时间 | 2026-09-10（整理 2026-09-09） |
| 官方核验时间 | 2026-09-16 |
| `stale_after` | **2026-11-30**（免费政策按周变动 + dots OpenRouter 通道 9-30 关闭 + AMD 额度有下调史；短于年末的常规值） |
| 高时效字段 | 免费额度/限流（RPM/TPM）、截止日、模型列表、积分单价、刊例价、$1/天额度、全局对比表价格 |
| 已知边界声明（预列） | ① 全部额度/限流/截止日以控制台实时显示为准（博文原风险提示）；② 作者实测数字（5%、1280x704、并发 5）为 2026-09 个人口径；③ dots3 为公测预览版、AMD Vision 为 LIMITED FREE；④ 全局对比表（§6）价格为公开口径合集，未逐项与本束 P0 核验等权处理，表内逐项标信源状态；⑤ roundup 束已 flagged（GitHub Models 退役等），本束不复用其失效条目 |

## 5. P0 必核验清单与结论摘要（2026-09-16 已回填，F-062 ~ F-089）

> 核验执行：3 个独立上下文子代理并行（Agnes 簇 / dots 簇 / AMD+全局表簇），权威源优先（官方文档/控制台/公告），WebSearch 锚定 2026-09。31 项关键声明：✅ 18 项 / ⚠️ 7 项 / ❌ 6 项，另捕获 3 类时效失效；V 阶段第二轮独立复核追加 F-089（Agnes Messages 端 x-api-key、视频免费档 1 RPM、AMD count_tokens）。

| 核验对象（F 编号） | 结论 |
|--------------------|------|
| Agnes 域名与网关（F-009） | ✅ 域名网关均存活；规范文档在 wiki.agnes-ai.cn，/doc/overview 为跳转别名（F-062） |
| .com→.cn 切换公告（F-010） | ⚠️【勘误】7·29 通稿目标是 apihub.agnes-ai.cn（保留 apihub），博文写成 api.agnes-ai.cn；后者为 9 月现行网关，属事实嫁接（F-063） |
| agnes-3.0-flash 能力（F-012） | ⚠️ 能力逐条属实；但"价格待公布"失实（刊例 ¥0.035/0.35/1.00 现价 ¥0）（F-065） |
| 旧模型 2.5/2.0 状态（F-006） | ⚠️【勘误】2.5 已全量上线非灰度；2.0 官方已废弃（F-065） |
| image/video-2.5-flash 全部技术细节（F-020~F-025） | ✅ 与官方文档逐字吻合（含 2624x1472、1280x704、错误码）（F-066） |
| 刊例价 ¥0.07/¥0.16/¥0.15（F-021） | ✅ 属实；视频页措辞为"限时免费"（F-066） |
| 无限期免费 + 20 RPM + 4K 1 次/分（F-006） | ✅ 官方 FAQ + Token Plan 精确吻合（F-067） |
| Agnes Code 形态/双模式（F-027/F-029） | ✅ 大框架属实；"Linux 不可混用 CLI"、macOS 12.0+、8 技能 slug 清单三条仅博文单源（F-068） |
| dots 平台/askdiandian 归属（F-034） | ✅ 官方平台+runtime-config.js 坐实"点点"同一服务（F-069/F-070） |
| dots3 512K/四模态/api-key 头/限流/思考参数（F-035/F-038） | ✅ 官方文档逐字确认（F-071） |
| OpenRouter 通道 9-30 关闭（F-007/F-060） | ✅ OpenRouter 页明示"Going away September 30, 2026"（F-072） |
| dots 接入 Trae（F-037） | ⚠️【勘误】Trae 仅 Bearer 无自定义头入口，直连 401；须经 OpenRouter/AtlasCloud 或头转换（F-073） |
| AMD 入口/端点/Key/登录（F-039/F-041/F-043） | ✅ 属实；品牌名 Radeon Cloud/Token Factory BETA，Anthropic 端点用 x-api-key（F-074） |
| AMD 四模型名单（F-040） | ⚠️【重大时效】09 初 4 款属实，09-16 已变 5 款：Vision-Exp 模型卡 404（DeepSeek 09-10 下线旧模型路由 V4.1），MiniCPM5-1B 被 2B 取代，新增 Qwen3.8-27B、MinerU2.5-Pro（F-075） |
| 积分 0.14/0.28/0.0028 与英文原文（F-042） | ✅ 模型卡 JSON 逐字确认；重置节奏两口径并存（F-076） |
| $10→$1 缩水/200 万 token 5%/并发 5（F-042/F-044） | ❌/❓ "缩到 $1/天"查无实据且被反证覆盖；5% 与单价粗算不符；并发 5 为单源体感（硬口径 20-30 RPM/并发 8）（F-077） |
| MiniCPM5-1B vs 2B（F-040） | ⚠️【勘误】两型号都存在，博文混用：0.5GB/128K 是 1B（05-26 发布），"2B 干翻 4B"是 2B（09-07 发布）（F-078） |
| Vision-Exp 305B/13B/MIT（F-040） | ✅ 规格属实；V4-Flash 文本上下文博文 64K-128K ❌（官方 1M）（F-079） |
| Qwen3.8-Flash-Next 125B/6B/262K-1M/Qwen4 先导（F-040） | ✅ 高度属实（2026-08-26 开源，百炼名 Qwen3.8-Flash）（F-080） |
| Hy3 295B/21B、Hy4 770B/49B（F-055/F-056） | ✅ 全部属实（另核得 API 定价 Hy3 ¥1/4、Hy4 ¥6/18）（F-081） |
| Kimi K2.5 输出 6-12 元（F-053） | ❌【勘误】官方输出 ¥21；"10 万/月免费"无据（F-082） |
| GLM-4.7-Flash 免费/GLM-5.x 8-28 元（F-047/F-048） | ⚠️ 4.7 永久免费属实；5.x 旗舰实为 ¥24-28（¥8 是 4.7 档）；2000 万包 90 天分包（F-083） |
| 豆包 Seed-2.0-Lite 128K/100 万月永久/0.6-3.66 元（F-052） | ❌【勘误】上下文 256K；一次性 50 万试用；0.6 是输入价、输出 3.6 起（F-084） |
| ERNIE/Qwen-Turbo/Hunyuan-lite（F-050/F-051/F-054） | ⚠️ Lite 为 8K（128K 免费的是 Speed）；7000 万为全平台礼包 90 天；Hunyuan-lite 免费 ✅（F-085） |
| DeepSeek V4-Flash 3-9 元/预告涨价（F-049） | ❌【勘误】9-10 起已降价为 4-8 元（峰谷），"预告涨价"方向反；新户 500 万无据（F-086） |
| Trae 内置四模型/基础版免费（F-057） | ⚠️ 四款均为往代（现行 V4.1/K3/GLM-5.3/Qwen3.8）；已改积分会员制（F-087） |
| WorkBuddy 产品身份 | ✅ 腾讯 CodeBuddy 团队出品；TraeWork 为字节竞品，博文并列未混淆（F-088） |

**状态裁决：`status: flagged`**。依据：① 博文标题级主推的 AMD 四款免费模型在核验日（发布后第 6 天）名单已变——Vision-Exp 下架、1B 被 2B 取代（核心推荐受影响，类比 roundup 束 GitHub Models 退役先例）；② dots OpenRouter 免费通道 14 天后（2026-09-30）关闭；③ 全局价格表 6 项 ❌ 硬错。三平台"当前仍可免费接入"的总论成立（Agnes/dots 直连/AMD 新名单），故非废弃而是带勘误与复核期的 flagged；verification.md 顶部明示，index.md 顶部提示，stale_after=2026-11-30 前安排复核。

## 6. 三层知识拆分（知识地图）

| 博文内容层 | 映射篇目 | F 编号支撑（初版） |
|-----------|---------|-------------------|
| 发布事实层（三平台是谁/免费什么/注册门槛/术语） | concepts/00-free-model-landscape.md | F-001~F-011、F-033~F-035、F-039~F-041、F-059 |
| 机制原理层（多协议网关/Thinking/图像参数/异步视频两步/积分制/认证差异） | concepts/01-platform-deep-dive.md | F-012、F-020~F-030、F-035~F-038、F-042~F-044 |
| 选型格局层（三平台横评、国内免费档全景、组合策略、安全合规） | concepts/02-selection-matrix.md | F-006~F-008、F-045~F-058、F-060 |
| 可演练：Agnes 全流程 | examples/00-agnes-walkthrough.md | F-013~F-032 |
| 可演练：dots3 双客户端接入 | examples/01-dots3-walkthrough.md | F-034~F-038 |
| 可演练：AMD 领 Key 调用 | examples/02-amd-walkthrough.md | F-039~F-044 |

## 7. ADDED Requirements（验收标准）

- bundle 13 个文件齐备（1 根 index + 1 log + 3 concepts + 3 examples + 2 references + 3 子目录 index = 13），每个 index.md 含隐藏 toctree，条目逐一对应磁盘文件
- 全部具体声明（数字/域名/命令/模型名/价格）携带 F 编号，无 facts.md 之外编造；作者观点与实测口径显式标注
- 双份 F 编号一致（facts.md ↔ article-source.md 编号集合相等、连续无跳号）
- P0 核验结论在 verification.md 按勘误四张清单组织；❌/⚠️ 项在正文呈现正确值并标注博文口径；不硬编权威 URL
- frontmatter 双信源（博文 URL + 核验权威 URL），stale_after=2026-11-30；与 roundup/agnes-ai-models 主题簇互链
- ai 域 index 导航表 + toctree 接入（束数按磁盘/门禁实测计数增量，不信任记忆值）；bundles/index.md 计数三处同步
- V 阶段执行四视角审查与机械门禁；invoke gates 不可用或被并行会话影响时执行手动等效清单并在 log.md 注明，禁止声称"gates 通过"
- C 阶段只给原子提交建议序列，不执行 commit/push（用户未要求）
