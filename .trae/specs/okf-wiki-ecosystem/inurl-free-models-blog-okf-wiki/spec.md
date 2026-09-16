# Spec：微信推广博文《一个程序员的省钱实录》→ OKF Wiki 知识包

> spec id: inurl-free-models-blog-okf-wiki
> created: 2026-09-16
> 方法论：seven-concepts 场景4（知识沉淀 R→I→E）× blog-article-to-okf-wiki 七阶段（R→I→E→V→C）

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
