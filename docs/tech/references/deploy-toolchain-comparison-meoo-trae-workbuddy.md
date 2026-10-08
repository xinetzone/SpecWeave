# 阿里 Meoo CLI / 字节 Trae / 腾讯 WorkBuddy：网站部署与上线能力调研

> 调研日期：2026-10-03
> 方法论：方法论编排（R→I→E→V→C），session `sc-20261003-deploy-toolchain-compare`
> 内容敏感度：Public（三方公开产品文档与官方新闻）

---

## 摘要结论（先看这段）

| 场景 | 首选 | 理由 |
|---|---|---|
| 国内长期对外访问的**网站** | **腾讯 WorkBuddy** | EdgeOne Pages（腾讯云 CDN，可绑已备案域名）+ CloudBase/Supabase BaaS |
| 需要完整后端（DB/登录/存储/大模型）+ 全栈容器 | **阿里 Meoo** | 云端托管最完整，全栈容器常驻，`meoo deploy --runtime image` |
| 出海 / 全球加速的纯前端或 Next.js | **字节 Trae 国际版 + Vercel** | 一键 Deploy 体验最顺，但国内访问不可靠 |
| 微信小程序上线 | **腾讯 WorkBuddy** | 三方中唯一，5.6.1+ 支持生成→审核→发布全链路 |
| 把部署能力接进**自己的 Agent / CI** | **阿里 Meoo** | 唯一提供 Skill + CLI + OpenAPI + 临时 token 开放集成 |
| 免费分享一个静态页面 | WorkBuddy 或 Meoo 均可 | 两者静态部署都不消耗云服务额度 |

**一句话排序（网站部署上线综合能力）**：WorkBuddy ≈ Meoo > Trae。Trae 的差距不在"能不能部署"，而在"部署这件事不在它自己的责任边界内"。

---

## R 阶段：事实清单（45 条）

### 阿里 Meoo（秒悟，阿里云）

- F-001 `docs.meoo.com/cli` 页面标题为「CLI 开放集成接入」，面向**第三方 Agent 平台接入方**（B 端集成文档）
- F-002 终端用户使用指南位于 `docs.meoo.com/meoo-cli`（用户给的链接是集成文档，不是使用指南）
- F-003 Meoo 是阿里云旗下云端 AI 开发平台，Meoo CLI 于 2026-06-11 发布
- F-004 npm 包 `@aliyun-meoo/cli`，要求 Node.js 20+；Windows 需 Git for Windows 与 zip
- F-005 核心命令序列：`meoo login` → `meoo projects use <urlId>` → `meoo cloud status` → `meoo sandbox push` → `meoo deploy`
- F-006 CI 场景：`meoo deploy --project <urlId> --skip-build --skip-push --force`（直接用已有构建产物发布）
- F-007 静态部署 = 构建前端产物发布到 CDN；全栈部署 = 上传源码，云端构建并运行服务
- F-008 全栈首次部署命令 `meoo deploy --runtime image`，后续可直接 `meoo deploy`
- F-009 静态应用本地预览端口 `localhost:3015`
- F-010 全栈构建环境：Linux、OpenJDK 21、Node 24.15.0、Python 3.13、Go 1.26.0；必须监听 `0.0.0.0:${PORT:-9000}`；`scripts/setup.sh` 远端构建执行、`scripts/start.sh` 容器启动执行
- F-011 云端能力：AI 数据库、用户登录（手机/邮箱验证码）、文件存储、百炼模型服务（无需单独申请 API Key）
- F-012 可设置网页发布范围：全网可见 / 指定人员可见 / 仅自己可见
- F-013 自定义独立域名（含免费 SSL 证书）仅 Pro/Max；自定义三级子域 Pro 1 个、Max 5 个；Free/Lite 无
- F-014 云服务额度：Free 1 个、Lite 2 个、Pro 8 个、Max 20 个；全栈项目数 Free 1 / Pro 4 / Max 8
- F-015 计费：Free ¥0、Lite ¥29/月、Pro ¥59/月、Max ¥179/月；代码下载导出仅 Pro/Max 支持
- F-016 纯静态页面部署不消耗云服务额度
- F-017 全栈容器本地文件存储不持久，容器会冷启动/重建，持久化须走云数据库
- F-018 `meoo skill install` 会自动检测并注入 Claude Code、Cursor、Trae、CodeBuddy、Qoder 的配置目录
- F-019 提供 OpenAPI 自行封装路径：团队 AK/SK 签发成员临时 token，`MEOO_TOKEN` + `MEOO_API_URL` 注入环境
- F-020 官方定位：非单纯部署工具，是本地 Agent 与秒悟云端能力之间的连接入口

### 字节 Trae

- F-021 分国际版 `trae.ai` 与国内版 `trae.cn` / `trae.com.cn`，两套独立产品，账号、订阅、数据互不相通
- F-022 国际版支持一键部署到 Vercel：SOLO 模式 + Integrations 连接 Vercel 账号 → 点 Deploy → 立即返回 live URL
- F-023 国际版同时集成 Vercel AI Gateway（统一模型访问、自动 failover）
- F-024 国内版 IDE **未内置一键部署按钮**；官方社区答复建议手动用 `vercel-cli` / `netlify-cli`，或 Git 关联 Vercel/Netlify
- F-025 国内版社区推荐路径：安装火山引擎 IGA Pages 的 Skill 或 `@iga-pages/cli`，在对话框说「将当前项目部署到 IGA Pages」
- F-026 IGA Pages 为 Serverless + 全球边缘加速 + 自动 SSL；官方明示**不适合**常驻后台服务、定时任务、数据库常连接、深度定制 Nginx/容器镜像
- F-027 国际版外联域名含 `supabase.com`、`vercel.com`；国内版含 `trae.cn`、`zijieapi.com`、`bytedanceapi.com`
- F-028 社区反馈：Vercel 在国内网络环境域名污染较严重，国内优先建议 Netlify 或 GitHub Pages
- F-029 定价 Free / Lite $3 / Pro $10 / Pro+ $30 / Ultra $100（月）；国内版免费档每月 500 积分
- F-030 Trae 为 IDE + 工作台形态，自身不提供数据库、登录、文件存储等 BaaS 能力

### 腾讯 WorkBuddy

- F-031 内置 BaaS：Supabase / 腾讯云 CloudBase，覆盖数据库、用户认证（邮箱、手机验证码、微信登录）、文件存储、免密钥大模型调用
- F-032 内置部署平台：Tencent CloudStudio 沙箱环境 / EdgeOne Pages 生产环境，均可生成可分享链接
- F-033 EdgeOne Pages 部署走 `edgeone` CLI（`npm i -g edgeone@latest`，版本须 ≥ 1.2.30），命令 `edgeone pages deploy`
- F-034 支持浏览器登录与 Token 登录两种模式，后者覆盖 CI / headless / 远程环境
- F-035 支持预览环境：`edgeone pages deploy -e preview`
- F-036 部署 URL 形如 `xxx.edgeone.cool?<auth_query_params>`；官方提示国内网络下可能因备案状态/加速策略出现访问限制（401），长期对外建议绑定**已备案**自定义域名
- F-037 「发布为应用」工具支持静态站点 / PDF / Node.js / Python / Go 单端口 HTTP 服务
- F-038 发布沙箱仅暴露**单个 HTTP 端口**，不提供 MySQL/PostgreSQL/Redis/MongoDB；SQLite 与公网托管数据库（如 Supabase）可用
- F-039 明确不支持 Java / Maven / Gradle 项目
- F-040 5.6.1（2026-09-24）上线微信小程序发布能力：生成 → 扫码绑定（体验版无需 AppID）→ 上传 → 提交审核 → 发布，全程在客户端内
- F-041 小程序自带数据库、微信授权登录、手机号登录、文件存储；省掉服务器域名备案这一环
- F-042 2026-09-17 上线「网页应用」全栈生成能力
- F-043 部署有强制确认门禁：每轮对话需用户显式要求发布；线上已存在内容时，本地改动不会自动覆盖
- F-044 EdgeOne Pages 免费额度含全球 CDN 加速、自动 HTTPS、自定义域名绑定
- F-045 除官方通道外，还装配 `web-deploy`（Vercel / Railway / GitHub Pages）、`html-deploy`（htmlcode.fun）等第三方部署技能

---

## I 阶段：核心洞察

### 洞察 1 — 三家不在同一层竞争：只有两家把"部署"当成自己的责任

- **陈述**：Meoo 和 WorkBuddy 把部署当作产品内建能力（自带云 + BaaS），Trae 把部署当作"跳转到第三方平台"。
- **证据**：F-005/F-011/F-032/F-037 vs F-022/F-024/F-025。
- **反常识**：Trae 宣传的"one-click deploy"实际是"one-click 授权 Vercel"。对国内版用户，官方自己的答复是"去终端里用 vercel-cli/netlify-cli 手动部署"（F-024）——等于没有部署能力。而"一键部署"体验最顺的国际版，走的是国内网络不稳定的 Vercel（F-028）。
- **行动**：评估 Trae 时不要把"支持一键部署"记为能力项，要追问"部署到谁的账号、谁的网络、谁负责可用"。

### 洞察 2 — 分水岭不是"能不能部署"，而是"部署完谁能打开"

- **陈述**：国内可访问性（CDN 归属 + 备案）才是这三者真正的差距所在。
- **证据**：F-028（Vercel 域名污染）、F-036（EdgeOne 默认域名国内可能因备案出现 401，需绑已备案域名）、F-003/F-032（Meoo 在阿里云、WorkBuddy 在腾讯云）。
- **反常识**：默认分享链接能打开 ≠ 能长期对外服务。WorkBuddy 官方文档自己就写了默认链接"被分享给他人访问时可能出现访问限制"，建议绑已备案自定义域名。这意味着**三家里没有一家能让你绕过 ICP 备案**——区别只在于是否把这条路铺平。
- **行动**：面向国内用户的正式站点，提前 7–20 个工作日启动备案，并把它写进排期，而不是等开发完才想起来。

### 洞察 3 — 后端能力的强弱与锁定成本成正比

- **陈述**：Meoo 后端最完整但锁定最深；WorkBuddy 后端有硬边界但通道最多。
- **证据**：F-011/F-014/F-015（Meoo 提供 DB/登录/存储/百炼，但自定义域名与代码导出要 Pro/Max，Free/Lite 导出不了代码）；F-038/F-039（WorkBuddy 沙箱只有单端口，禁 MySQL/Redis/Java）；F-040/F-041（WorkBuddy 独有小程序的完整上线链路）。
- **反常识**：Meoo 的"能力全"是用"出不来"换的——Free/Lite 套餐不支持代码下载导出（F-015），且容器冷启动、本地文件不持久（F-017）。WorkBuddy 的"限制多"反而把项目推向 SQLite + 公网托管数据库这类可迁移架构。
- **行动**：选型时用一句问话定性——"如果下个月要迁走，这个项目有多少东西搬不动？"

---

## E 阶段：可迁移模式「部署选型三层筛」

**模式名**：部署选型三层筛
**触发场景**：在多个 AI 编程/低代码工具间做"谁来负责上线"的决策，或评估某工具的部署宣传是否可信。
**不适用于**：纯后端服务上架、企业内网交付、已有成熟 CI/CD 流水线的项目。

**核心步骤（按序过滤，任一层不通过即出局）**

1. **第一层 · 网络可达性**：访问者主要在哪？国内 → 只考虑部署在国内云的通道（WorkBuddy/EdgeOne、Meoo/阿里云）；出海 → Vercel/Netlify 系（Trae 国际版路径）。默认分享域名一律视为临时验证链接，正式站点必须绑定已备案自定义域名。
2. **第二层 · 状态与后端**：项目是否需要数据库/登录/文件存储？需要 → Meoo（云端全托管，最省事）或 WorkBuddy（CloudBase/Supabase，但沙箱只有单端口，禁外挂 MySQL/Redis）；纯静态 → 三家都能做，且 Meoo 与 WorkBuddy 静态部署都不消耗云服务额度。
3. **第三层 · 端形态与退出成本**：是否要小程序（只有 WorkBuddy）、是否要导出代码/自定义域名（Meoo 要 Pro/Max）、是否需要把部署接进自己的 Agent/CI（只有 Meoo 提供 OpenAPI + 临时 token）。

**反模式**

- ❌ 把"支持一键部署"当成能力项而不追问落地在谁的云平台——Trae 是典型（F-022 + F-024 + F-028）。
- ❌ 用默认分享链接交付正式项目——WorkBuddy 文档明示国内可能因备案出现 401（F-036）。
- ❌ 先开发后备案——备案 7–20 个工作日，审核 1–3 个工作日，串行等待会凭空多出两三周。
- ❌ 在 Meoo Free/Lite 上做沉淀型项目——代码导出与自定义域名都在 Pro 及以上。

**检验标准**：能一句话说清三件事——部署在谁的云、默认域名能否长期对外、迁走时哪些东西搬不动。说不清就还没选完。

**跨场景迁移示例**：同一套三层筛可用于评估任何"AI 生成 + 一键上线"类工具（如各类 AI 建站产品）——先问网络归属，再问状态托管，最后问退出成本。

---

## V 阶段：对抗审查

**🔴 魔鬼代言人**：本次结论的证据大量来自官方文档与厂商/社区软文，存在"最优场景数据"风险。Meoo 的额度表、WorkBuddy 的"一键部署"、Trae 的"one-click"均为厂商自述，无第三方实测。且 WorkBuddy 结论部分依赖本机技能库（一手但可能非最新版）。若某家的 CLI 实际失败率高，本文档无法体现。

**🟢 新人视角**：术语未解释——ICP 备案、BaaS、Serverless 边界为何排斥数据库常连接，对新人都是黑箱。且文档缺"第一步该做什么"：三家都要先登录/授权，但 Meoo 要 Node 20+、WorkBuddy 要 `edgeone` ≥ 1.2.30，这些前置条件埋在细节里。

**🟠 老板视角**：投入产出比未量化。Trae 最便宜（Free/$3 起）但部署要另接；Meoo Pro ¥59/月解锁自定义域名与代码导出；WorkBuddy 有免费额度但额度上限未公开。合规风险未评估：三方数据存放区域、Meoo/WorkBuddy 的账号体系是否满足企业数据出境要求，均未查证。

**🔵 未来视角**：三个产品都在高速迭代（WorkBuddy 9 月连上两个能力、Trae 版本线频繁变动、Meoo 6 月才发布 CLI），本文结论的半衰期约 3–6 个月。最大变量是"备案/合规"政策与各厂自有域名的可达性策略——这决定了第二层判断能否长期成立。

**已采纳修正**：（1）在结论表顶部明确标注"国内长期对外"需绑已备案域名，避免默认链接被误当作成品；（2）补充"证据以厂商自述为主，缺第三方实测"的声明；（3）为 Meoo 补充"锁定成本"提示，避免"能力最全=最好"的误读。

---

## 附：三方能力对照矩阵

| 维度 | 阿里 Meoo（秒悟） | 字节 Trae | 腾讯 WorkBuddy |
|---|---|---|---|
| 部署归属 | 阿里云（自有） | Vercel / 火山 IGA Pages（第三方） | 腾讯云 EdgeOne / CloudStudio（自有） |
| 静态站点 | ✅ 发布到 CDN，不耗额度 | ✅ 经第三方 | ✅ EdgeOne，免费额度 |
| 全栈/常驻服务 | ✅ 容器常驻，`--runtime image` | ⚠️ Serverless 边界，不支持常驻 | ⚠️ 单端口 HTTP，Node/Python/Go |
| Java 项目 | ✅ OpenJDK 21 | 取决于第三方 | ❌ 明确不支持 |
| 数据库 | ✅ 云端 AI 数据库 | ❌ 需外接 | ⚠️ CloudBase/Supabase，沙箱内无 |
| 用户登录 | ✅ 手机/邮箱验证码 | ❌ | ✅ 邮箱/手机/微信 |
| 文件存储 | ✅ | ❌ | ✅ |
| 大模型调用 | ✅ 百炼，免 API Key | 需自带 Key / AI Gateway | ✅ 免密钥调用 |
| 自定义域名 | Pro/Max 才支持（含 SSL） | 取决于第三方平台 | ✅ 支持，建议绑已备案域名 |
| 代码导出 | Pro/Max 才支持 | 本地文件，天然可导出 | 本地文件，天然可导出 |
| 小程序上线 | ❌ | ❌ | ✅ 5.6.1+ 全链路 |
| 开放集成（接自己 Agent/CI） | ✅ Skill + CLI + OpenAPI + 临时 token | ❌ | ❌ 绑定自家客户端 |
| 国内访问可靠性 | 高（阿里云） | 低（Vercel 域名污染） | 高（腾讯云，默认域名有备案限制） |
| 入门价格 | Free ¥0；Lite ¥29/月 | Free；Lite $3/月 | 免费额度（上限未公开） |

---

## 关键参考

- Meoo CLI 开放集成接入：https://docs.meoo.com/cli
- Meoo CLI 使用指南：https://docs.meoo.com/meoo-cli
- Meoo 订阅套餐&积分说明：https://docs.meoo.com/coindesc
- 阿里云 Meoo CLI 发布新闻：https://www.aliyun.com/product/news/29324
- WorkBuddy 产品简介：https://www.workbuddy.cn/docs/enterprise/215235156081283072
- TRAE 官方社区「关于大赛 demo 如何部署」：https://forum.trae.cn/t/topic/71168
