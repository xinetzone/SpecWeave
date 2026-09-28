# Spec：微信推广博文《一个程序员的省钱实录》→ OKF Wiki 知识包

> spec id: inurl-free-models-blog-okf-wiki
> created: 2026-09-16；**updated: 2026-09-28（同主题合并：吸收姊妹 spec inurl-byok-free-models-blog-okf-wiki，F-106~F-122）**
> 历轮：G1-G3 首轮博文转化（2026-09-16，F-001~F-070）→ G4 站点直证二次复核（2026-09-28，F-071~F-087）→ G5 三次复核（2026-09-28，F-088~F-105）→ **同主题双软文合并（2026-09-28，信源 B 去重并入 F-106~F-122）**
> 方法论：seven-concepts 场景4（知识沉淀 R→I→E）× blog-article-to-okf-wiki 七阶段（R→I→E→V→C）；合并轮次为 seven-concepts 场景3（I→F→A→V→C）

> **🔀 2026-09-28 同主题合并注记（session=`sc-20260928-inurl-merge`）**：同账号同产品的第二封信源——09-04《同事偷偷用这个网站，一年省下5000块》原独立 spec `inurl-byok-free-models-blog-okf-wiki/` 与 bundle `jishu/ai/inurl-byok-free-models/`——经用户拍板并入本 spec 与主 bundle（主 bundle 更名 `jishu/ai/inurl-byok-token-hub/`，git mv 保历史）。第二文 35 条事实中 14 条与信源 A 重复不另立编号，21 条独有原文归并为 F-106~F-122（见 [facts.md](facts.md) H 区；去重映射见 bundle `references/article-source.md` H.2）；新增勘误 E7（5000 块查无）、E8（Agnes 新加坡国籍）、E9（Agnes 阶段性 $0/20RPM）。生态登记总数 575→574；两旧束路径最终均不存在。

## 1. 任务定义

将微信公众号文章 https://mp.weixin.qq.com/s/dSTvvOjPIRpbSJHIqxi0Gw 转化为可溯源、带时效管理的 OKF v0.2 知识包（bundle），入库 `projects/awesome-okf-xs/doc/bundles/`。

## 2. 内容敏感度预检（阶段0）

- URL 为 `mp.weixin.qq.com/s/` 标准公开链接，无 `share?code=`/`token=`/邀请码等访问控制参数 → **公开内容（Public）**
- 工作流：标准工作流——spec 位于 `.trae/specs/okf-wiki-ecosystem/inurl-free-models-blog-okf-wiki/`，bundle 位于 submodule `projects/awesome-okf-xs/doc/bundles/`

## 3. 信源距离预判（R 阶段必做）

- **信源性质：推广软文（最高营销叙事浓度）**。证据：①文首横幅广告「免费AI Token额度·立即领取」；②正文以第三方产品 token.inurl.link 为唯一转折点与解决方案；③文末三条推广链接（主站/guide/models）+「立即免费体验」CTA；④标题与全文叙事服务于产品引流。
- 归类：**厂商/推广自宣类**（账号"风信旗"与产品关系待核验；即使非厂商自营，亦属付费/引流软文）。
- 后果：所有成效数字（550→0 元、省 90%、0.1 秒切换、17 家、三周零花费）与产品技术声明默认 **P0 必核验**；bundle index 顶部加「厂商/推广自述数据」提示块；核心声明若无独立证据 → `status: flagged`。

## 4. 归属位置分析（步骤3 决策树）

文章主线实体：token.inurl.link——多厂商 API Key 收拢 + 本地代理 + 自动路由工具。

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/inurl-unified-token/`（选定，直挂束） | ✅ | ① 主线为 AI 模型接入工具（OpenAI 兼容本地代理/密钥管理/模型路由），属 jishu/ai 域；② 同形态先例：`echobird`（Model Nexus 模型枢纽+本地 LLM+Codex Proxy 桌面工具）证明直挂束可容纳"多模型统一接入产品"；③ 同主题先例：`free-llm-api-roundup`（40 家免费 API 盘点，flagged）、`deepseek-pricing`、`fable5-cost-optimization`、`context-optimization` 可交叉引用互链；④ 文中 GLM-4-Flash/LongCat/Agnes 等实体在 ai 域均有资料 |
| `sheke/industry/`（AI 行业与商业趋势） | ❌ | 该组容纳行业快照/商业分析（Copilot 成本、变现指南）；本文主体是工具配置实操与架构，非行业格局分析 |
| `jishu/ai/ai-security/` | ❌ | 虽含 BYOK/加密安全讨论，但仅为产品卖点之一，非主线 |
| 新建分组 | ❌ | 单篇博文新建分组违反最小变更原则 |

## 5. 骨架判定（操作可复现性两问）

1. 有读者可照做的流程吗？——**表面有**：注册（/app）→ 填 Key 入密钥库 → 启动本地代理 → Cursor 填 `http://localhost:3003/v1`+令牌+`inurl-code`，步骤、参数、顺序齐全。
2. 经作者实测、可复现吗？——作者自称"用了三周"，但信源为推广软文，且**产品真实性/可达性尚未核验**。

**最终判定（2026-09-16 核验后）**：产品真实运营、官方 /guide 五步流程与 localhost:3003/v1 配置参数经实测确认（流程可照做、两问通过）→ **设 `examples/`**（1 篇接入演练，含免费档 3 密钥约束与闭源代理安全清单）；同时因核心成效声明证伪（F-070「17 家 Key+0 元」与定价表冲突、F-064 DeepSeek 免费失实、F-069 型号过时、F-060 时间线矛盾）→ bundle 置 `flagged`。参照先例 qwen-ui-agent（含 examples 且有 ❌）。

## 6. 三层知识地图（I 阶段）

| 层 | 篇目 | 内容 |
|----|------|------|
| 事件/事实层 | `concepts/00-article-and-product.md` | 博文档案、软文性质、token.inurl.link 产品核验结论、推广链路与可信度总览 |
| 事实核验层 | `concepts/01-free-model-landscape.md` | 文中免费模型额度事实（GLM-4-Flash/LongCat/百度/Groq/Agnes/qwen-coder）+ 官方现状 + 勘误对照 |
| 架构模式层 | `concepts/02-unified-token-architecture.md` | BYOK 统一令牌 + 本地代理 + 分类自动路由架构（产品声明、安全模型、边界与风险） |
| 选型观点层 | `concepts/03-cost-strategy-and-boundaries.md` | 账单叙事与 90/10 分层策略（作者观点显式分层）、免费能力边界、时效提示 |
| 演练（条件） | `examples/01-inurl-setup-walkthrough.md` | 仅产品核验通过时设立：接入配置演练 |
| 信源 | `references/article-source.md` + `references/verification.md` | 博文 F 编号双份登记 + P0 核验报告（含勘误） |

## 7. P0 核验计划（勘误四张清单）

- ① 日期/版本/型号：ChatGPT Plus/Claude Pro $20（2025-10 时点 vs 2026-09 现价）；"复杂任务需 GPT-4o/Claude Opus"型号时效性；LongCat 1M 上下文；Agnes 百万上下文
- ② 成效数字溯源：550→0 元、省 90%、$80 月账单（个人自述，标注不可外部核验）；0.1 秒切换（产品技术声明，查官网/无独立证据则单源）；17 家计数
- ③ 口径对照：LongCat"新用户 1000 万"vs 库内已登记"Chat 500 万/天、Flash-Lite 5 亿/天、每日刷新"；百度"每月 100 万"vs 千帆"每模型 100 万/3 个月"
- ④ 产品/引文逐字核对：token.inurl.link 四链接可达性、六项官网功能声明、Unified Token/Recovery Secret 机制、WorkBuddy 客户端身份、运营主体/备案

## 8. 交付与门禁

- bundle 文件集 + 三级索引接入（ai 组 index 导航表+toctree、bundles/index.md 计数同步：jishu 406→407、total 538→539，以现值复核）
- V 阶段：四视角审查、双份 F 编号集合比对、手动等效机械门禁（gates 依赖可用性先探测，不可用则按清单手动验证并 log 注明）
- C 阶段：不主动 commit/push，输出原子提交建议（子模块 → 主仓库 spec → 主仓库 gitlink）待用户确认

## 9. 2026-09-28 二次复核（站点直证增量）

- 触发：用户指令「学习 https://token.inurl.link/，更新 okf wiki 教程」——方法论不变（seven-concepts 场景 4），信源从推广博文转为**产品站直接实测**（curl 直打四页面 + 公开 GET 接口，未注册未下载；浏览器子代理受拦截零产出后的降级路径）。
- 产物：facts.md 新增 G4（F-071~F-087，17 条，与 bundle `article-source.md` 双份一致）；bundle 侧 verification.md 增 §7、index/log/concepts 00-02/examples 01 增量补注，共改 9 个 bundle 文件。
- 结论：核心 ❌（F-060/F-064/F-069/F-070）的产品侧依据原样成立，站点目录反新增 F-079 ❌（重复已勘误口径 12 天未改）；产品迭代与新增边界并存（F-077/F-081/F-082/F-084）。**维持 status: flagged 与 stale_after: 2026-12-31**，下轮复核项增加 public:false 厂商开放情况与 track.js/短链数据披露。

## 10. 2026-09-28 三次复核（G5：四目标页面深度学习）

### 10.1 触发与范围

- 用户指令：全面学习 `https://token.inurl.link/app`、`https://token.inurl.link/#why`、`https://token.inurl.link/models#paid`、`https://token.inurl.link/guide`，更新 OKF Wiki 教程。
- 与 G4 的分工差异：G4 是「站点直证可行性」式快扫（核对首轮勘误是否仍成立）；**G5 是按用户指定四目标做功能面全量学习**——重点从"错误是否还在"转向"产品实际提供什么"，尤其 `/app` 内联应用界面暴露的路由/压缩/自定义厂商/运营后台能力，以及首页 `#why` 的 BYOK 论据与付费区模型陈旧度。
- 内容敏感度：四 URL 均无访问控制参数 → **公开内容**，沿用本 spec 与既有 bundle，不新建 spec/束/分组。

### 10.2 方法（证据纪律）

- `curl.exe` 直打 + Chrome UA（浏览器子代理在 G4 已证对该域零产出，本轮不再尝试）；**未注册、未下载启动器、仅 GET 只读**公开页面与公开接口。
- catalog 机器审计：providers/tier/public/models 计数、capabilities 标签分布、SHA256 与 G4（F-077 记录 428,592 字节）比对。
- `/app` 证据来自**前端渲染文本 + 内联 JS 接口枚举**，属"界面提供"证据而非"运行验证"证据（AC-7 纪律）。
- 新外部实体 OmniRoute 走 WebSearch P0 核验（官方站 omniroute.online / npm `omniroute` / GitHub diegosouzapw/OmniRoute / 中文技术媒体，四源交叉）。
- 抓取物与分析脚本留存 `.temp/inurl-refresh-g5/`（gitignored，不入库；Review 后可删）。

### 10.3 核心结论（初步，待 R 阶段裁决固化）

1. **站点零迭代**：`/api/catalog` 与 G4 为**字节级同一文件**（428,592 字节，SHA256 `3F689C07…BD0F1`）；G4 的结构性事实（46 商=17 free+29 paid、10 家隐藏、133 模型、caps 仅 text/code/image、定价、turnstile、短链矩阵、track.js、无备案页脚）全部持续。
2. **flagged 第三次维持**：三处官方已勘误口径（Agnes 百万/百度每月 100 万/LongCat 1M·1000 万）12+ 天未修正（F-079 持续）；DeepSeek 仍 paid；F-070 核心勘误的定价证据原样成立。
3. **功能面增量显著（G4 未系统覆盖）**：19 种路由策略 + 5 档提示词压缩 + Combo 路由链（界面自认"OmniRoute 同款思路"）；自定义厂商三协议（OpenAI 兼容/Anthropic/Gemini）；仪表盘四组件；完整运营后台（邀请码/用户/广告/资讯/catalog-overrides/个人收款码人工核销）；生产控制台保留"模拟支付成功"按钮。
4. **新增风险信号**：`/api/news` 首条标题（千问 3.8-MAX 首发）与摘要（GPT-4o 生图替代 DALL·E）文不对题；付费公开卡仍挂 gpt-4o/gpt-3.5/claude-3-5/grok-2/gemini-1.5 等，对照 F-069 当期旗舰（GPT-5.6 Sol/Claude Opus 5）整体落后 ≥1 个大版本；`/api/ads`、`/api/news` 无鉴权公开。
5. **新信源与新知识维度**：OmniRoute 为真实 MIT 开源本地优先网关（19 策略/Combo/RTK 压缩同源口径），concepts 需增补"闭源商业产品 vs 开源原型"对标维度，但不做抄袭判定。

### 10.4 增量事实清单（F-088 ~ F-105，共 18 条；R 阶段双份登记）

| 规划编号 | 簇 | 要点 | 主要来源 |
|---|---|---|---|
| F-088 | 零迭代 | 四 URL 全 200；catalog 428,592B / SHA256 3F689C07…BD0F1，与 G4 字节级一致 | curl + 哈希 |
| F-089 | 零迭代·P0 | plans 三档原价原额未变（0/3、¥990/30d/10、¥2990/30d/∞、邀新 7 天 standard）→ F-072/F-070 证据持续 | `/api/billing/plans` |
| F-090 | 零迭代 | 46=17 free+29 paid（19 public+10 hidden）、133 模型、隐藏 10 家名单逐条同 G4、mock 仍 localhost:3002/mock-chat | catalog 机器审计 |
| F-091 | 零迭代 | capabilities 仍顶层 12 键，text=12/code=5/image=7，无 video/audio → F-082 持续 | catalog 机器审计 |
| F-092 | 零迭代·P0 | Agnes「百万级上下文」、百度「每月 100 万」、LongCat「1M/注册送 1000 万」三审仍在 → F-079 持续 | /models 渲染文本 |
| F-093 | 零迭代 | turnstile 仍 enabled:false 同 siteKey；provider-meta 38 条短链不变 → F-073/F-086 持续 | `/api/turnstile`、`/api/provider-meta` |
| F-094 | /app 新增 | 仪表盘：模型调用量排行、实时请求活动（4 秒采样）、厂商用量、每 Key 实时延迟；数据来自 localhost:3003 本机代理 | /app 前端 |
| F-095 | /app 新增 | 设置「路由与压缩」：19 策略、5 档压缩（Lite≈15%/Standard≈30%/Aggressive≈50%/Ultra≈75%/RTK 60–90%）、Combo（`>` 分隔）；界面自认 OmniRoute 同款思路/Combo 一致；偏好下发本机代理保存即生效 | /app 前端 |
| F-096 | /app 新增 | 自定义厂商 3 类型（OpenAI 兼容/Anthropic/Gemini）+ baseUrl/路径/模型 ID/鉴权头/前缀字段，保存后进目录与模型下拉 | /app 前端 + /guide |
| F-097 | /app 新增 | 系统管理后台：邀请码、注册用户管理、广告管理、资讯模块（1+4）、厂商官网链接、catalog-overrides（仅覆盖展示）、待核销订单（个人收款码人工核销） | /app 前端 |
| F-098 | /app 新增 | 模型源同步页自述 catalog 由 `shared/catalog.json` 构建期生成、`refresh_catalog.mjs` 索引；套餐页并存「模拟支付成功」（`/api/billing/mock-paid`）与支付宝电脑网站支付（`/api/billing/checkout`） | /app 前端 |
| F-099 | 接口边界 | GET 只读探测：用户类 401 `{"error":"unauthorized"}`、admin 类 403 `{"error":"forbidden"}`；`/api/ads`、`/api/news` 无鉴权公开返回运营内容 | curl 状态码 |
| F-100 | 运营内容·P0 | news 4 条（首条千问 3.8-MAX 标题配 GPT-4o 生图摘要，文不对题；WorkBuddy/DeepSeek-V4/豆包）、ads 1 条（通义千问）；跳转全为 inurl.link 短链 | `/api/news`、`/api/ads` |
| F-101 | #why | 「不是中转，是 BYOK」三论据（云端不调厂商/厂商看到你的 Key/统一令牌只在本地）；演示令牌样例 `byok_live_9f3a·7Kq2…`；自述统计仍 6/8+/0/256/100% → F-045/F-083 持续 | 首页 #why |
| F-102 | guide | 自定义厂商图文步骤、`AUTO_MODELS`/`AUTO_PROVIDER_ORDER`、shell:startup 自启、taskkill 停止、FAQ 明示 auto/default/inurl 同义向后兼容、inurl≡inurl-text | /guide 全文 |
| F-103 | 付费时效·P0 | 付费公开卡仍列 gpt-4o/4o-mini/3.5-turbo、claude-3-5-sonnet/haiku/3-opus、grok-2/2-mini、gemini-1.5/2.0-flash-exp；对照 F-069 当期旗舰落后 ≥1 大版本（F-080 陈旧信号从免费区扩到付费区） | /models#paid × F-069 |
| F-104 | 外部对标·P0 | OmniRoute 真实存在：MIT 开源本地优先网关，npm `omniroute`（v3.8.49）、localhost:20128、官方站自称 352 providers/19 策略、GitHub diegosouzapw/OmniRoute、RTK+Caveman 压缩 15–95%；inurl 命名与口径有开源原型且页面主动自认 | omniroute.online + npm + GitHub + 媒体 |
| F-105 | 零迭代 | track.js 四页仍加载；页脚仍仅 ©2026 inurl 无公司/ICP/备案；免费区机场广告仍在 → F-084/F-087 持续 | 四页 HTML |

### 10.5 bundle 更新范围（最小变更；现有束 `jishu/ai/inurl-unified-token/`）

- `references/article-source.md`：G 节追加 G5 双份事实段（与 facts.md F-088~F-105 机械一致）。
- `references/verification.md`：新增 §8 三次复核（方法、持续项清单、新增项裁决、总裁决）。
- `references/omniroute-benchmark.md`：**唯一新增文件**，OmniRoute 独立对标信源页（四源 P0、含口径差异与"不判定抄袭"边界）；`references/index.md` 收录。
- `concepts/00`：增补 /app 功能全景（仪表盘/自定义厂商/后台/公开运营接口/mock 支付/源同步自述）与运营成熟度信号。
- `concepts/01`：增补付费目录陈旧度（F-103）。
- `concepts/02`：增补 19 策略/5 档压缩/Combo 机制 + OmniRoute 对标小节。
- `concepts/03`：必要时一句指针指向 00 的运营信号（不展开）。
- `examples/01`：增补 AUTO_MODELS/AUTO_PROVIDER_ORDER、自定义厂商三类型接入、shell:startup/taskkill。
- `index.md`：frontmatter reverified 更新为 G5/F-105、flagged 横幅追加三审行、时效截点；`log.md` 追加 2026-09-28 G5 段。
- **三级索引计数不变**（未新增束）；`inurl-byok-free-models` 姊妹束本轮不动（其 facts 主体未受四目标影响，仅在 index/log 交叉指针确有必要时加一行，默认不动）。

### 10.6 验收标准（AC）

| AC | 类型 | 标准 |
|---|---|---|
| AC-1 | rule | facts.md 与 article-source.md 的 G5 F 编号集合**机械相等**：恰为 F-088~F-105、连续无跳号、与既有 F-001~F-087 不重号 |
| AC-2 | rule | 每条 G5 事实带来源锚点（文件/接口/URL 或回链 F-0xx）；P0 项 F-103 回链 F-069 权威证据、F-104 至少 3 个独立来源（官方站/npm 与 GitHub 计 2 源 + 媒体） |
| AC-3 | rule | `references/omniroute-benchmark.md` 存在且被 references/index.md 与 concepts/02 引用；相对链接逐一可达 |
| AC-4 | rule | 持续型事实统一措辞"持续（F-0xx）"回链 G4，不把同一结论重写成新发现；G5 只登记 G4 未覆盖的新证据 |
| AC-5 | rule | `check-utf8.py`、`check-toctrees.py`、`check-bundles-index.py` 全过；零 `file:///`、零家目录路径；toctree 计数与 bundles 三级索引计数不变 |
| AC-6 | rule | verification.md §8 给出 G5 裁决计数（✅/⚠️/❌/🔄）与总裁决：status: flagged 第三次维持（或有充分证据改判），stale_after 明确 |
| AC-7 | rubric | **证据轴匹配**：/app 一切能力写作"界面/JS 显示提供"，禁止写成"已验证可用/已实测后端"；压缩率、352 providers 等数字标注"自述/估算"与时点 |
| AC-8 | rubric | OmniRoute 对标中立：陈述开源原型事实 + inurl 自认出处 + 口径差异（压缩率 15–95% vs 15–90% 等），不作抄袭/侵权法律结论，不贬低任一方案 |
| AC-9 | rubric | 最小变更：不新建束/分组、计数不变；除 omniroute-benchmark.md 外无新增文件；正文增量为补注式，不推翻 G1-G4 已裁结论 |
| AC-10 | rule | C 阶段不自行 commit/push；输出子模块→主仓库 spec→gitlink 的显式文件列表原子提交建议，待用户确认 |
