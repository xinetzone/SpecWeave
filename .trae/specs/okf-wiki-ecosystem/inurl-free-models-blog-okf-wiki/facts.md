# 事实集：微信推广博文《一个程序员的省钱实录》

> 采集时间：2026-09-16；**二次复核（站点直证）：2026-09-28（G4：F-071 ~ F-087）**
> 信源：https://mp.weixin.qq.com/s/dSTvvOjPIRpbSJHIqxi0Gw（browser_use 提取 `#js_content` 全文，约 2800 字符）；二次复核信源：token.inurl.link 四页面 HTML 与公开 GET 接口（curl 直打，未注册未下载）
> 类型标记：O=客观事实　V=作者观点/体验/推断　P=产品/厂商声明（推广对象）
> 信源距离：博文=推广软文；核验结论：待核 / ✅通过 / ⚠️口径差异或单源 / ❌证伪
> P 级：P0=必核验（数字/日期/产品核心声明）　P1=选核验　P2=可单源（背景/个人叙事/观点）

## A. 博文元信息与营销证据（F-001 ~ F-006）

| 编号 | 类型 | 事实 | 原文位置 | P级 | 核验 |
|------|------|------|---------|-----|------|
| F-001 | O | 标题《一个程序员的省钱实录：从月付 500 到 0 元，我是怎么用免费模型干完所有活的》 | 标题 | P2 | 与抓取页一致 |
| F-002 | O | 发布账号：微信公众号"风信旗"，作者署名"检校千牛卫" | 文首 | P2 | 与抓取页一致 |
| F-003 | O | 发布时间 2026-09-02 22:00，发布地河南，标注"原创" | 文首 | P2 | 与抓取页一致 |
| F-004 | O | 栏目题注"风信旗 · AI 免费模型实用指南" | 文首 | P2 | 与抓取页一致 |
| F-005 | O | 文首横幅广告文案"免费AI Token额度／输入即可领取 高效生成不中断／立即领取" | 顶部推广图 | — | 营销成分证据（图片） |
| F-006 | O | 文末三条产品链接（token.inurl.link 主站、/guide、/models）+ "🔗 立即免费体验 token.inurl.link" CTA | 文末 | — | 软文性质证据 |

## B. 账单叙事与作者身份（F-007 ~ F-010，个人自述）

| 编号 | 类型 | 事实 | 原文位置 | P级 | 核验 |
|------|------|------|---------|-----|------|
| F-007 | O | 作者自称独立开发者：Copilot+Cursor 写代码、ChatGPT 查资料、Claude 写文案/文档、Midjourney 画图 | 第一阶段 | P2 | 作者自述 |
| F-008 | O | 2025-10 AI 开销账单：ChatGPT Plus $20 + Claude Pro $20 + OpenAI API $35 + 各种小工具订阅 ≈ 人民币 550 元/月 | "先上账单" | P0（定价项） | 待核 |
| F-009 | O | 作者称曾有一个月 OpenAI 账单冲到 $80，因而开始寻找替代方案 | 第一阶段 | P2 | 作者自述，无外部可核性 |
| F-010 | O | 作者称 2026-03 AI 开销为 0 元，全部走免费模型，且 AI 用得更多 | "先上账单" | P2 | 作者自述 |

## C. 免费模型踩坑期（F-011 ~ F-018）

| 编号 | 类型 | 事实 | 原文位置 | P级 | 核验 |
|------|------|------|---------|-----|------|
| F-011 | O | 作者注册了"十几家"免费模型：智谱、百度、阿里、美团、Groq、硅基流动、OpenRouter 等 | 第二阶段 | P1 | 平台存在性待核 |
| F-012 | V | 痛点一：各家 API 格式、模型名称、Endpoint 均不同；Cursor 里配 5 个自定义模型，限额/故障时手动切换 | 第二阶段 | P2 | 作者体验 |
| F-013 | O+P | 智谱 GLM-4-Flash 免费，但并发一高就报 429 | 第二阶段 | P0 | 待核 |
| F-014 | O+P | 美团 LongCat 新用户送 1000 万 Tokens，作者重度使用两周造完 | 第二阶段 | P0 | 待核（口径疑点：库内先例为 500 万/天且每日刷新） |
| F-015 | O+P | 百度免费额度"每月 100 万"，作者月中就见底 | 第二阶段 | P0 | 待核（口径疑点：千帆先例为每模型 100 万/3 个月） |
| F-016 | O | Groq 速度快但免费额度有限 | 第二阶段 | P1 | 待核 |
| F-017 | V | 痛点三：模型质量不稳定（代码强则中文弱等），需按任务类型手动选模型，构成认知负担 | 第二阶段 | P2 | 作者观点 |
| F-018 | V | 作者结论：免费模型单独用体验不如付费；问题不在模型而在缺少统一管理层 | 第二阶段 | P2 | 作者观点 |

## D. 主推产品 token.inurl.link 声明（F-019 ~ F-033，核心 P0 区）

| 编号 | 类型 | 事实 | 原文位置 | P级 | 核验 |
|------|------|------|---------|-----|------|
| F-019 | P | 产品定位：把多家厂商 API Key 收拢成一枚统一令牌，本地代理自动切换 | 第三阶段导语 | P0 | 待核（核心声明） |
| F-020 | P | 架构声称：客户端（WorkBuddy/Cursor）以 OpenAI 格式请求本地代理 localhost:3003（OpenAI 兼容）；代理仅在启动时向云端保管库取一次密钥密文与模型目录；之后用用户自己的 Key 直连厂商 API（通义/OpenAI 等），云端不中转请求 | 架构图注 | P0 | 待核 |
| F-021 | P | 配置四步：注册账号拿统一令牌 → 把十几家免费 Key 填进密钥库 → 一键启动本地代理 → Cursor 填一个地址和令牌；作者称 10 分钟配好 | 配置段 | P0 | 待核 |
| F-022 | P | 注册入口 https://token.inurl.link/app，邮箱+密码注册，含 Cloudflare 人机验证 | 注册卡片图 | P0 | 待核 |
| F-023 | P | 注册成功显示两样东西：🔑统一令牌 Unified Token（登录+本地代理凭证）、🛡️恢复密语 Recovery Secret（忘密码找回密钥库）；仅显示一次；端到端加密、云端不留明文、站点无法代为找回 | 注册卡片图 | P0 | 待核 |
| F-024 | P | 自动路由：Model 填 `inurl`；写代码自动路由 qwen-coder 和 deepseek，日常对话自动选 GLM-4-Flash 和 LongCat | 自动路由段 | P0 | 待核 |
| F-025 | P | 某家限额时 0.1 秒内切到下一家，作者"感觉不到切换" | 自动路由段 | P0 | 待核（性能数字，厂商自述性质） |
| F-026 | P | 分类路由：`inurl-code`（仅代码模型）、`inurl-image`（画图）、`inurl`（日常）；一个令牌全场景、不需记模型名 | 分类路由段 | P0 | 待核 |
| F-027 | P | 官网六宫格功能声明：①浏览器端端到端加密密钥库（主密钥在浏览器加密，云端只存密文）②统一令牌收拢 OpenAI/Anthropic/Gemini 等 Key ③本地 Agent 代理本机发起调用、云端不中转、避免被厂商判定代理封号 ④内置 OpenAI/DeepSeek/Mistral/Anthropic/Gemini 格式互转与流式归一 ⑤AES-256-GCM + PBKDF2 派生 + 双份 escrow 托管 ⑥原生 SSE 流式透传、登录注册速率限制 | 六宫格图 | P0 | 待核 |
| F-028 | P+V | Cursor 配置：Base URL `http://localhost:3003/v1`、API Key 填统一令牌、Model=`inurl-code`；作者称 Python/JavaScript/Shell 代码补全与重构流畅 | 工作流 | P0（配置参数）/P2（体验） | 待核 |
| F-029 | P | 日常对话用 WorkBuddy 客户端，Model 填 `inurl`，自动在 GLM-4-Flash、LongCat、Agnes 之间切换 | 工作流 | P0 | 待核（WorkBuddy 身份待查） |
| F-030 | P+O | 长文档直接用 inurl：声称 Agnes AI 百万上下文、LongCat 具备 1M 上下文 | 工作流 | P0 | 待核 |
| F-031 | P | 画图用 `inurl-image`，自动路由到支持图像生成的免费模型 | 工作流 | P1 | 待核 |
| F-032 | P | Ollama 本地运行也可加入密钥库，inurl 会在网络模型与本地模型间智能选择 | 工作流 | P1 | 待核 |
| F-033 | O | 作者称三周用下来没为 AI 花过一分钱，月 500+ 变 0 | 工作流尾 | P2 | 作者自述 |

## E. 免费模型质量评估（F-034 ~ F-038，作者观点区）

| 编号 | 类型 | 事实 | 原文位置 | P级 | 核验 |
|------|------|------|---------|-----|------|
| F-034 | V | 普通业务代码/CRUD/脚本/前端页面：免费模型完全够，qwen-coder、deepseek 代码能力已很强 | 够不够用 | P2 | 作者观点 |
| F-035 | V | 日常对话/查资料/写文案/总结文档：完全够，GLM-4-Flash 和 LongCat 中文能力"甚至比 GPT-3.5 好" | 够不够用 | P2 | 作者观点（比较无评测出处） |
| F-036 | V | 复杂推理、数学证明、前沿研究：免费模型不够，仍需 GPT-4o 或 Claude Opus | 够不够用 | P1 | 作者观点；型号时效性待核（2026-09 旗舰已更迭） |
| F-037 | V | "90% 的人 90% 的时间都不需要这种级别的推理" | 够不够用 | P2 | 作者观点，无出处 |
| F-038 | V | 作者策略：90% 任务用免费模型，10% 复杂任务偶尔充一次 OpenAI API，月最多几十元，比 500+ 省 90% | 够不够用 | P2 | 作者自述/观点 |

## F. 安全声明、总结与 CTA（F-039 ~ F-043）

| 编号 | 类型 | 事实 | 原文位置 | P级 | 核验 |
|------|------|------|---------|-----|------|
| F-039 | P | BYOK 模式：Key 在用户浏览器里用 AES-256 加密后上传，云端只存密文；调用从本地代理直连厂商，厂商看到的是用户自己的 Key 和 IP | 安全性段 | P0 | 待核 |
| F-040 | V | 作者推断：即使平台数据库被拖库，攻击者也拿不到明文 Key；比服务端明文存 Key 的中转平台"安全太多" | 安全性段 | P1 | 基于产品声明的作者推断 |
| F-041 | O | 总结三件事：①注册了 17 家免费模型的 Key ②用 token.inurl.link 统一管理、自动路由 ③在 Cursor 和 WorkBuddy 配好 | 总结 | P0（计数）/P2 | "17 家"计数待核 |
| F-042 | V | 推荐语："花 10 分钟配置，省下来的钱够你吃好几顿好的""强烈建议你试试" | 总结 | P2 | 作者推荐（软文 CTA） |
| F-043 | O | 三个推广 URL：注册/主站 https://token.inurl.link/；使用教程 https://token.inurl.link/guide；免费模型清单 https://token.inurl.link/models | 文末 | P0 | 待核（可达性） |

## G. 核验补充事实（F-044 ~ F-070，2026-09-16 三独立子代理核验回填）

### G1. 产品 token.inurl.link 实测核验（F-044 ~ F-057，browser_use 仅浏览公开页/公开接口，未注册）

| 编号 | 类型 | 事实（权威/实测口径） | 来源 | 核验 |
|------|------|------|------|------|
| F-044 | O | 四个 URL 当日均正常打开（HTTPS 有效证书、Cloudflare 代理、http 301→https）：`/` 落地页、`/app` 控制台外壳、`/guide` 5 步图文教程、`/models`（落 `/models#free`） | 浏览器实测 | ✅ |
| F-045 | O | 站点自我定位"inurl · 聚合 APIToken · 端到端加密密钥库"；首页展示统一令牌形如 `byok_live_9f3a…`，宣传语"已托管密钥 6 / 支持厂商 8+ / 明文上云 0" | 官网首页 | ✅（宣传数字为站点自述） |
| F-046 | O | 公开接口 `/api/catalog` 实时返回约 424KB 目录，含 **46 个 provider**（agnes/zhipu/longcat/openai/deepseek/anthropic/gemini/qwen/moonshot/doubao/minimax/jd/netease/xiaomi-mimo/huawei-pangu 等），证明后端真实运营 | `/api/catalog` | ✅ |
| F-047 | O | 官方教程确认：代理地址固定 `http://localhost:3003/v1`，已实现 OpenAI 兼容的 `GET /v1/models`；可手动 `AGENT_TOKEN=… AGENT_MASTERKEY=… node local-agent.js` 启动；Windows 启动器为 `byok-launch.bat`，控制台 JS 存在对本机 `/v1/metrics` 的真实轮询联调逻辑 | /guide + 前端代码 | ✅（代理二进制闭源、运行时下载，未实测） |
| F-048 | O | 官方教程路由别名表：`inurl`/`inurl-text`（文本默认，旧名 auto 兼容）、`inurl-code`（代码）、`inurl-image`（图像），另有 `inurl-video`、`inurl-audio`；某厂商 5xx/429 自动切下一家；可用 `AUTO_MODELS`/`AUTO_PROVIDER_ORDER` 限定 | /guide | ✅ |
| F-049 | O | 博文点名的 5 个自动路由模型在实时目录中均有精确 id：`qwen/qwen-coder-plus`、`deepseek/deepseek-v4-flash`、`zhipu-free/glm-4-flash`、`longcat/LongCat-Flash-Chat`、`agnes/agnes-2.5-flash`；但路由池实际取决于用户自己录入了哪些 Key，官网未逐字承诺"默认池=这 5 个" | `/api/catalog` | ✅（机制属实，"默认五选"为博文表述） |
| F-050 | O | `/models` 分区真实存在：**免费 17 家**（Agnes AI、智谱 GLM-4-Flash、硅基流动、美团 LongCat、StableHorde、Ollama 本机、阿里云百炼、Pollinations、百度千帆、Groq、OpenRouter 免费模型、Akash、Google Gemini 免费层、京东言犀、网易有灵妙启、小米 MiMo、华为盘古）；**付费 19 家**（含 OpenAI、DeepSeek、Mistral、Claude、Gemini、通义、智谱、Kimi、豆包等）——**DeepSeek 被官方归入付费区** | /models | ✅ |
| F-051 | O+P | 官方定价接口 `/api/billing/plans`（enabled、非 mock）：**免费版 ¥0（限 3 个厂商密钥 + 本地代理）；标准版 ¥9.9/月（10 个密钥 + 邮件支持）；专业版 ¥29.9/月（无限密钥、多会话/多 Agent、优先支持）**；邀请奖励送 7 天标准版；已接入支付宝 | `/api/billing/plans` + /guide FAQ | ✅（**核心勘误证据**） |
| F-052 | O | E2EE 前端代码实证：WebCrypto `deriveKeyFromSecret` 用 PBKDF2（100000 次、SHA-256）派生 AES-GCM-256 密钥；注册生成 `escrow_pw` 与 `escrow_rec` 双份密文 POST `/api/escrow`，与"双份 escrow + 恢复密语"文案逐字对应；服务端只收密文 | 前端 JS 审计 | ✅（浏览器侧加密兑现） |
| F-053 | O | 安全边界：本地代理/启动器由同一运营者分发且闭源、运行时下载，教程称启动器"已内嵌统一令牌与主密钥"——E2EE 不覆盖本地代理供应链层，运营者可经更新推送任意代码 | /guide + 代码观察 | ⚠️ 风险事实 |
| F-054 | O | Cloudflare Turnstile 组件已集成（`/api/turnstile` 返回 siteKey）但当日 `enabled:false`——与博文卡片/教程"注册会有人机验证，请完成 Cloudflare 验证框"的当下状态有出入 | `/api/turnstile` | ⚠️ 文案与现状脱节 |
| F-055 | O | WorkBuddy 是**第三方独立产品**（AI Agent 云沙箱，分配 `<id>.sh1.agentos-app.net` HTTPS 域名、腾讯云 CLB、内置 sandbox-proxy），不是 inurl 组件；官方教程将其与 Cursor、OpenWebUI 并列为"支持 OpenAI 格式的 AI 客户端" | /guide + 公开文章 | ✅（博文 F-029 易让读者误以为同厂） |
| F-056 | O | 运营主体线索：产品四站页脚仅"© 2026 inurl"，**无公司名、无 ICP 备案、无邮箱/电话、无 GitHub 仓库**（全闭源），隐私协议为空锚点；主域 inurl.link 可追溯至个人站长"李新（光山居士，河南光山人，90 后，资深 SEO/网络营销/站长）"的个人站 lixiaoxin.com（2023 年起有内容）；/models 挂 VPN"机场"广告、厂商 Key 链接走自有短链（返佣/统计性质） | 页脚/主域/广告位 | ⚠️ 主体匿名度高、营销变现痕迹 |
| F-057 | O | 工程成熟度信号：访问任意不存在路径返回裸 JSON `{"error":"unauthorized"}` 而非 404 页；生产页面残留 Vite 开发期 HMR 探针 `/@vite/client` | 浏览器实测 | ⚠️ 小团队快速迭代特征 |

### G2. 国内免费模型官方口径核验（F-058 ~ F-065）

| 编号 | 类型 | 事实（权威口径，截至 2026-09-16） | 来源 | 核验 |
|------|------|------|------|------|
| F-058 | O | 智谱 GLM-4-Flash-250414 官方定价表标"免费版"（128K），现主力免费型号为 **GLM-4.7-Flash（200K，/models/free/ 目录）**；并发按账号权益 V0–V3 动态限流、不公开发放固定值，超限返回错误码 1302（账户限流）/1305（高峰过载）即对应 429；社区 2026-09 实测免费档约 1 并发；新用户资源包 2000 万 tokens、90 天有效（非永久） | docs.bigmodel.cn 官方文档 + 控制台实测 | ✅ F-013 属实（"429"描述准确） |
| F-059 | O | 美团 LongCat：2026-06-30 发布 **LongCat-2.0**（总参 1.6T、激活 33B–56B，"原生支持 1M 超长上下文"）；同步商业化，**实名新用户奖励 1000 万 tokens 资源包、30 天有效**（Preview 内测用户另发 5000 万）；老 Flash 六模型（Chat/Thinking/Omni/Lite 等）已于 **2026-05-29 全部下线**（老政策：Chat 等共享 50 万/天、Flash-Lite 5000 万/天）；现行 LongCat-2.0 API 按量付费（限时折扣输入 ¥2/输出 ¥8 每百万 tokens） | meituan.com 官方新闻 + longcat.chat 官方文档/更新日志 + IT之家 | ✅ F-014 的"1000 万"有出处；⚠️ 但属一次性资源包非长期额度 |
| F-060 | O | **博文时间线硬伤**：博文称 2026-03 AI 开销已为 0（F-010），而其踩坑期注册的 LongCat"新用户 1000 万"政策 2026-06-30 才推出——两个时间点互斥，叙事存在时间错置 | 由 F-010 与 F-059 交叉推得 | ❌ 内部矛盾 |
| F-061 | O | 百度免费口径：产品为**百度智能云千帆 ModelBuilder**（V2 接口兼容 OpenAI）；新用户**每个模型独立 100 万 tokens、有效期 3 个月、到期不按月重置**（覆盖 ERNIE-4.5-Turbo、ERNIE-X1-Turbo、DeepSeek-R1/V3.x、Qwen3、Kimi-K2 等）；另有 **ERNIE-Speed/Lite/Tiny/ERNIE-3.5-8K 永久免费、不限 token 总量、限 QPS（实测约 50）**（博文漏报）；实名再送 20 元代金券 | cloud.baidu.com 千帆官方文档/公告 | ⚠️ F-015"每月 100 万"重置周期错误；漏报永久免费模型 |
| F-062 | O | Agnes AI（新加坡 Sapiens AI）：现行免费模型 **agnes-2.5-flash 上下文 512K、价格 $0**；agnes-2.0-flash 已废弃且同样 512K；**1M 上下文仅属于付费的 agnes-2.5-pro（2026-08-01 发布）**；2026 年 6–7 月灰度期 1M 高峰即降 512K | wiki.agnes-ai.com 官方文档 | ⚠️ F-030"Agnes 免费百万上下文"当前不成立 |
| F-063 | O | 通义代码模型官方名 **qwen3-coder-plus / qwen3-coder-flash**（1M 上下文，最大输出 65536）；阿里云百炼新用户**每模型 100 万 tokens、开通后 90 天有效**（北京地域，不补发）；另有通义灵码个人版 IDE 插件长期免费、Qwen Chat 网页免费限速 | aliyun.com 官方专题 + help.aliyun.com 官方帮助 | ✅ F-024/F-034 的 qwen-coder 真实存在且有免费渠道（一次性额度） |
| F-064 | O | **DeepSeek 官方 API 明确收费**（V3/V4 明码标价、V4 峰谷计价），仅一次性小额新人赠送（约 500 万 tokens/30 天，以控制台为准）；硅基流动免费层仅 ≤9B 开源小模型（DeepSeek 大模型付费）；OpenRouter 2026-09 免费名单（约 20 个 :free 模型）**已无 DeepSeek**；仅 AMD Radeon Cloud Token Factory、Hetzner 实验平台、WorkBuddy 海外版积分等**时限性渠道**可免费调用 | api-docs.deepseek.com + openrouter.ai 官方文档 | ❌ F-024/F-034 将 deepseek 当作稳定免费后端失实 |
| F-065 | O | 硅基流动：新用户 16 元（1 美元）赠金，≤9B 开源模型永久免费（限 RPM/并发），大模型付费。OpenRouter：`:free` 后缀机制仍在、约 20 个模型动态轮换，统一 20 请求/分钟；历史充值 <$10 限 50 请求/天、≥$10 为 1000 请求/天；余额为负时免费模型也 402 | siliconflow.cn 官方资讯 + openrouter.ai/docs 官方 Limits | ✅ F-011/F-016 平台与"额度有限"属实 |

### G3. 海外定价与型号时效核验（F-066 ~ F-070）

| 编号 | 类型 | 事实（权威口径，截至 2026-09-16） | 来源 | 核验 |
|------|------|------|------|------|
| F-066 | O | ChatGPT Plus 自 2023-02 推出至核验时点均为 **$20/月（无涨价）**，故博文 2025-10 账单的 $20 属实；2026-09 个人档另有 Go $8、Pro $100 与 Pro $200（Pro $200 自 2026-09-10 起暂停接受新订阅）、Business/Enterprise | help.openai.com 官方帮助中心 | ✅ F-008 定价项属实 |
| F-067 | O | Claude Pro：月付 **$20/月**、年付 $200/年（折 $17/月）；Max 5x $100/月、Max 20x $200/月；Team 标准席 $25/月 | claude.com/pricing + support.claude.com | ✅ F-008 定价项属实 |
| F-068 | O | Groq 免费层长期有效、无需信用卡；2026-09 官方面：主力模型多为 30 RPM/1000 RPD、TPM 6K–30K、TPD 10 万–50 万；compound 系列仅 250 RPD；触顶 429 | console.groq.com 官方速率限制文档 | ✅ F-016 属实 |
| F-069 | O | 型号时效：**GPT-4o 等老模型已于 2026-02-13 从 ChatGPT 退役**（2025-10 账单时点旗舰也已是 GPT-5）；2026-09 OpenAI 旗舰推理模型为 **GPT-5.6 Sol（2026-07-09 起推送）**；Anthropic 现旗舰为 **Claude Opus 5（2026-07-24 发布）**（Opus 4.8 为 2026-05-28 上代）；另有更高定位 Fable/Mythos 5.1（2026-09-01） | help.openai.com Model Release Notes + anthropic.com 官方新闻 | ❌ F-036 推荐在博文发布当日（2026-09-02）即已过时 |
| F-070 | O | **核心勘误（0 元口径冲突）**：博文 F-041 称"注册了 17 家免费模型的 Key"并用 inurl 实现月费 0 元；但产品免费档仅允许 3 个厂商密钥（F-051），而"17"恰为 /models 页免费厂商计数（F-050）。录入 10 个 Key 需 ¥9.9/月、无限 Key 需 ¥29.9/月——**"17 家 Key 全量托管"与"0 元"在产品自身价格表下不可兼得**；叠加 DeepSeek 付费（F-064）、Agnes/LongCat 百万上下文付费化（F-059/F-062），博文主结论"0 元干完所有活"仅在"≤3 个免费厂商 + 不含 DeepSeek + 长上下文受限"的收窄口径下方可成立 | F-041×F-050×F-051×F-064×F-059×F-062 交叉 | ❌ 核心声明口径勘误（flagged 依据） |

### G4. 2026-09-28 二次复核（F-071 ~ F-087，站点直证；curl 直打公开页面/接口，仍未注册未下载）

| 编号 | 类型 | 事实（2026-09-28 实测口径） | 来源 | 核验 |
|------|------|------|------|------|
| F-071 | O | 四个 URL（`/`、`/app`、`/guide`、`/models`）全部可达（HTTPS/Cloudflare），首页 title 与「聚合 APIToken·端到端加密密钥库」定位未变 | curl 状态码/title | ✅ F-044 持续 |
| F-072 | O+P | `/api/billing/plans` 原样：enabled/mock=false/manual=false；免费 ¥0/freeKeyLimit=3、标准 990 分（=¥9.9/月）/30 天/10 密钥、专业 2990 分（=¥29.9/月）/30 天/无限；inviteReward 7 天 standard；专业档功能列表新增「早期功能内测」，其余与 09-16 一致 | `/api/billing/plans` | ✅ F-051 持续（核心勘误证据仍成立） |
| F-073 | O | `/api/turnstile` 仍 `{"enabled":false,"siteKey":"0x4AAAAAAD7LmJfa2KBA4Uab"}`（siteKey 与 09-16 相同）；/guide 步骤 1 仍写「注册会有人机验证，请完成 Cloudflare 验证框」 | `/api/turnstile` + /guide | ⚠️ F-054 脱节持续 |
| F-074 | O | 博文点名 5 模型 id 当日逐一 EXISTS：`qwen/qwen-coder-plus`、`deepseek/deepseek-v4-flash`、`zhipu-free/glm-4-flash`、`longcat/LongCat-Flash-Chat`、`agnes/agnes-2.5-flash` | `/api/catalog` | ✅ F-049 持续 |
| F-075 | O | /app 内联 JS 加密链未变：`deriveKeyFromSecret` 仍 PBKDF2 iterations=100000/SHA-256 → AES-GCM length=256；`escrow_pw`（password+userId 盐）/`escrow_rec`（恢复密语+email 盐）POST `/api/escrow`；另观察到 `/api/recover`（邮箱发起、恢复密语解密）、`/api/password`（改密时重加密 escrow_pw）、`/api/me`、`/api/keys`，恢复/改密流程与双 escrow 设计自洽 | /app 前端 JS | ✅ F-052 持续 |
| F-076 | O | DeepSeek 仍在 catalog `tier=paid`（models：deepseek-v4-flash/deepseek-v4-pro/deepseek-reasoner），/models 付费区卡片保留 | `/api/catalog` + /models | ❌ F-064 持续 |
| F-077 | O | `/api/catalog` 当日 **428,592 字节**（09-16 约 424KB），provider 仍 46 家；tier 结构 **17 free + 29 paid**，其中 **10 家 paid 为 public:false**：ppio、mock（「Mock Vendor (local test only)」，baseUrl=`http://localhost:3002`，模型 mock-chat）、together、siliconflow（付费通道）、deepinfra、fireworks、hyperbolic、lepton、novita、openai-compatible（通用自定义，baseUrl 占位、模型 `your-model`）；`/api/catalog?all=1` 未鉴权响应与默认接口**字节级相同（SHA-256 一致）**——隐藏条目本就随公开接口下发；`/api/provider-meta` 亦无鉴权返回含全部隐藏 slug 的 websites 映射（38 条 inurl.link 短链、logos 空） | `/api/catalog` 对比分析 + `/api/provider-meta` | ⚠️ 测试/预留条目进入生产公开目录 |
| F-078 | O | /models 计数牌仍显示「免费模型 17 / 付费模型 19」，正文渲染 17 张免费卡 + 19 张 public:true 付费卡（页面内部自洽，但未反映后台 29 个 tier=paid 条目）；免费 17 家名单与 09-16 完全相同 | /models HTML | ✅/⚠️ F-050 页面口径未变 |
| F-079 | P | 站点自身目录继续重复已被官方勘误的口径：①Agnes 卡片/summary 称「agnes-2.5-flash 支持百万级上下文」（官方免费档 512K，F-062）；②百度千帆卡片称「新用户每月赠送 100 万 tokens」（官方每模型 100 万/3 个月，F-061）；③LongCat 免费条目含 LongCat-2.0 并宣传「原生 1M 上下文、新用户注册送 1000 万 Tokens」（2.0 现行按量付费、礼包 30 天一次性，F-059） | /models 渲染文本 + catalog summary | ❌ 站点自述 12 天内未修正 |
| F-080 | O | 免费目录陈旧/轮换信号：siliconflow-free 仍列旧代 `deepseek-ai/DeepSeek-V2.5`；OpenRouter 免费模型已轮换为 `google/gemini-2.5-flash:free`、`meta-llama/llama-3.3-70b-instruct:free`；gemini-free 仍列 gemini-1.5-flash/1.5-pro-002/2.0-flash-exp（落后官方当期）；agnes 目录仍挂已废弃的 agnes-2.0-flash | `/api/catalog` + /models | ⚠️ 目录维护频率不均 |
| F-081 | O | /guide 仍为五步但内容扩充：启动器跨平台（Windows `byok-launch.bat` + macOS/Linux `byok-launch.sh`，需 **Node.js 18+**，由 /app「本地代理与对话测试」区一键下载、自动检测连接）；FAQ 扩至 6 条（支付宝电脑网站支付付款后自动回调、1–2 分钟到账；模型 id 必须与 /app 下拉一字不差；catalog 更新需重启代理等）；新增「用量与剩余额度」（每厂商卡片手填额度如 1000000，剩余=手填额度−累计已用，教程明示各厂商 API 不提供剩余额度）；新增 OpenAI 兼容 `GET /v1/models` 的客户端识别说明 | /guide 全文 | ✅ 产品持续迭代 |
| F-082 | O | /guide 承诺 inurl-image/inurl-video/inurl-audio 按能力标签分类路由，且无支持厂商时「明确提示不静默失败」；但 catalog capabilities 映射仅覆盖 12 个模型、标签只有 **text/code/image** 三类（无 video/audio 标签，亦无 audio 模型）——当前 inurl-video/inurl-audio 必然落入「当前没有支持该类别的厂商」空类别提示 | /guide × capabilities 交叉 | ⚠️ 文档承诺超出现行目录数据 |
| F-083 | P | 首页新增「实时演示」区：不注册即可在 OpenAI/Anthropic/Gemini 三选间发起浏览器内模拟流式调用（明示模拟响应、不触真实密钥、不消耗额度）；hero 更新为「BYOK · 端到端加密 · 永不中转／你的密钥，由你亲自加密托管」；自述统计数字未随目录更新（已托管密钥 6 / 支持厂商 8+ / 明文上云 0，256，100%，8+） | 首页 HTML | ✅（宣传数字仍为站点自选口径，F-045 持续） |
| F-084 | O | 四个页面均加载主域脚本 `https://inurl.link/track.js`；脚本注释自称「website analytics tracker」、支持 `data-site` 多租户接入，采集 site/session/page/referer/language/url，load 上报、页面可见时心跳 ping、exit 经 sendBeacon 上报 duration，POST 至主域 `/api/track`——属同一运营者第一方统计（非第三方域名），但访问行为回传主域，与其短链/营销体系同域 | track.js 源码 | ⚠️ F-056 信任画像增量 |
| F-085 | O | 工程信号复核（修订 F-057）：随机不存在路径实际返回 HTTP **401** 裸 JSON `{"error":"unauthorized"}`（非 404；`/api/me`、`/api/keys`、`/api/escrow`、`/api/health`、`/api/stats`、`/api/config` 未鉴权一律 401 裸 JSON）；四页面 HTML 已无 `/@vite/client` HMR 探针残留（静态构建）；/models 底部常驻「暂无模型数据，请刷新页面或稍后重试」空状态占位 | curl + HTML 扫描 | 🔄 F-057 部分修订（裸 JSON 仍在且精确为 401；HMR 项不复现） |
| F-086 | O | 主域 inurl.link 形态变化：09-28 根路径直接 200 呈现「inurl.link · 互联网精选导航 — 发现 · 连接 · 探索」导航/短链门户（SSR 页面），不再是 F-056 记录时直接呈现的个人站 lixiaoxin.com（个人站追溯保留为历史主体线索）。短链枚举：/models 36 张公开卡的「前往获取 Key」仅 **5 个直连官方域**（aistudio.google.com、yl.163.com、www.huaweicloud.com、dashboard.cohere.com、console.upstage.ai），其余卡片均走 inurl.link/&lt;slug&gt; 短链（免费区顶部另有 1 个机场广告短链 mojie-inurl）；catalog 全量 46 家 website 字段为 38 条 inurl.link 短链 + 8 个其他域（含 mock 的 localhost:3002、隐藏厂商 lepton 的 dashboard.lepton.ai 与 openai-compatible 的 platform.openai.com 占位等） | inurl.link 根页 + /models 链接枚举 + /api/provider-meta | ⚠️ 短链矩阵系统化；主体匿名结论不变 |
| F-087 | O | 页脚/广告复核：四页页脚仍只有「© 2026 inurl · 聚合 APIToken · 端到端加密密钥库」（models 页加后缀「厂商请求从本机发出」），仍无公司名/ICP/公安备案/邮箱/GitHub；免费区顶部 VPN 机场广告仍在（短链 `inurl.link/mojie-inurl`，文案「稳定、便宜、速度快、节点多的机场」） | 四页页脚/广告位 | ⚠️ F-056 持续 |

### G5. 2026-09-28 三次复核（F-088 ~ F-105，四目标页面深度学习；curl 直打，未注册未下载）

> 用户指定四目标：`/app`、`/#why`、`/models#paid`、`/guide`。方法：curl.exe + Chrome UA、仅 GET 只读；catalog 计数/SHA-256 机器审计；/app 证据为前端渲染文本+内联 JS 接口枚举（界面证据，非运行验证）；OmniRoute 走四源 WebSearch 交叉。

| 编号 | 类型 | 事实（2026-09-28 实测口径） | 来源 | 核验 |
|------|------|------|------|------|
| F-088 | O | 四目标（/app、/#why、/models#paid、/guide）全部 HTTP 200；`/api/catalog` 当日 **428,592 字节、SHA-256 `3F689C07FAE9FC67C76C10F8850D02F9F5066697498358EE69D32A13714BD0F1`**——与 G4（F-077）记录的 428,592 字节为**字节级同一文件**；本轮机器审计（provider/tier/public/model/capabilities 计数）与 G4 全部一致 | curl 状态码 + sha256sum | ✅ 站点目录零迭代 |
| F-089 | O+P | `/api/billing/plans` 原样：enabled/mock=false/manual=false；免费 ¥0/freeKeyLimit=3、标准 990 分（=¥9.9/月）/30 天/10 密钥、专业 2990 分（=¥29.9/月）/30 天/无限；inviteReward 7 天 standard | `/api/billing/plans` | ✅ 持续（F-072）；F-070 核心勘误的定价证据第三次原样成立 |
| F-090 | O | catalog 机器审计：46 provider = **17 free + 29 paid（19 public:true + 10 public:false）**，共 **133 个模型**；10 家隐藏付费商名单与 G4 逐条一致（ppio、mock、together、siliconflow、deepinfra、fireworks、hyperbolic、lepton、novita、openai-compatible）；mock 仍 baseUrl=`http://localhost:3002`、模型 mock-chat | `/api/catalog` 机器审计 | ⚠️ 持续（F-077）：测试/预留条目仍在生产公开目录 |
| F-091 | O | capabilities 仍为顶层 dict 仅 **12 键**，标签分布 **text=12 / code=5 / image=7**，无 video/audio 标签亦无对应模型 | `/api/catalog` 机器审计 | ⚠️ 持续（F-082）：inurl-video/inurl-audio 必然空转 |
| F-092 | P | /models 渲染文本三审仍含三处已被官方勘误口径：①Agnes 卡「agnes-2.5-flash 支持百万级上下文」；②百度千帆卡「新用户每月赠送 100 万 tokens」；③LongCat 卡「原生 1M 上下文，新用户注册送 1000 万 Tokens」 | /models 渲染文本 | ❌ 持续（F-079）：站点 12+ 天未修正（F-061/F-062/F-059） |
| F-093 | O | `/api/turnstile` 仍 `{"enabled":false,"siteKey":"0x4AAAAAAD7LmJfa2KBA4Uab"}`；/guide 步骤 1 仍写「请完成 Cloudflare 验证框」；`/api/provider-meta` 仍无鉴权返回 38 条 inurl.link 短链映射（结构同 G4） | `/api/turnstile` + `/api/provider-meta` + /guide | ⚠️ 持续（F-073/F-086） |
| F-094 | O | /app 界面显示仪表盘四组件：模型调用量排行、实时请求活动（页面标注「每 4 秒采样一次请求累计值」）、厂商用量、每把 Key 的实时延迟；空态文案明示数据来自本机 Agent（localhost:3003），启动本地代理后才显示 | /app 前端渲染文本 | ✅ 功能在界面提供（未注册，未实测运行） |
| F-095 | O+P | /app 设置区显示「本地代理·路由与压缩」面板：**19 种路由策略**（轮询/延迟优先/优先级/成本优先/健康优先/成功率优先/随机/最少使用/余量优先/加权/粘性/多样性/可靠性/成本+延迟兼顾/新鲜度/自动/极速优先/极廉价优先/均衡 Top3 轮询）；**提示词压缩 5 档**（Lite≈15%、Standard≈30%、Aggressive≈50%、Ultra≈75%、RTK 工具链去重 60–90%；页面注「压缩率为估算值（OmniRoute 同款思路，规则式实现）」「代码块/链接/JSON 原样保留」）；**路由链 Combo** 以 `>` 分隔多策略、上一层全部失败时自动流转（页面注「与 OmniRoute 的 Combo 路由链一致」「共 19 种可任意组合」）；偏好下发本机代理，保存后下次请求自动生效、无需重启 | /app 前端渲染文本 | ✅ 功能在界面提供（未实测后端）；⚠️ 压缩率为页面自述估算；开源原型见 F-104 |
| F-096 | O | /app「自定义厂商」表单支持 3 类型（OpenAI 兼容/Anthropic/Gemini），字段含名称、Endpoint(baseUrl)、路径、模型 ID（逗号分隔可多个）、鉴权头、前缀；页面说明保存后自动进入模型目录与对话模型下拉，模型 ID 须与厂商文档一字不差；编辑时密钥留空=保留原密钥 | /app 前端 + /guide 步骤 2 | ✅（界面+教程双证） |
| F-097 | O | /app 侧边栏存在「🛡️系统管理」区，界面显示：Turnstile 开关与 Site Key 配置（Secret 走 wrangler secret 不展示）、邀请码批量生成、注册用户管理（统计/筛选/搜索/通知邮件/付费标记）、广告管理（左侧栏+密钥库面板两展位，建议 ≤3 条）、资讯模块（1 精选大图+4 列表）、厂商官网链接维护、模型目录管理 catalog-overrides（仅覆盖标题/描述/徽章/Key 链接/推荐/排序/隐藏，「只影响展示、不改基础数据，无需重新部署」）、待核销订单（用户用个人收款码付款后管理员手动核销升级） | /app 前端渲染文本 | ⚠️（界面证据）个人收款码+人工核销=小规模手工运营信号 |
| F-098 | O | /app「模型源同步」页自述：控制台目录「由 shared/catalog.json 在构建期生成（通过 refresh_catalog.mjs 索引各厂商公开模型列表）」，页内展示已部署目录快照与同步状态；套餐页同时显示「模拟支付成功」按钮（`/api/billing/mock-paid`）与支付宝电脑网站支付收银台（`/api/billing/checkout`，付款自动回调开通），并保留「填交易单号/微信昵称备注→管理员核销」通道 | /app 前端渲染文本 + JS 接口枚举 | ⚠️ 生产注册用户控制台保留 mock 支付按钮（测试设施外露） |
| F-099 | O | GET 只读鉴权边界：用户类（/api/me、/api/keys、/api/escrow 等）未鉴权 401 `{"error":"unauthorized"}`；admin 类（/api/admin 等）403 `{"error":"forbidden"}`；**`/api/ads` 与 `/api/news` 无鉴权公开返回运营内容** | curl 状态码/响应体 | ⚠️ 用户/管理接口鉴权分层明确；运营内容接口公开属设计但扩大无鉴权指纹面 |
| F-100 | P | 公开运营接口当日内容：`/api/news` 4 条——①标题「阿里云千问3.8-MAX预览版首发Token Plan」（徽章「首发」），摘要却是「基于 GPT-4o 在 ChatGPT 和 API 中直接生成高质量图像，替代原有的 DALL·E 集成」（**标题与摘要文不对题**）；②WorkBuddy 推广；③「DeepSeek-V4 预览版：迈入百万上下文普惠时代」；④豆包 Doubao-Seed-Evolving。`/api/ads` 1 条：阿里云通义千问（side/dash 双展位开启）。跳转全为 inurl.link 短链（tongyi/workbuddy/deepseek/doubao），图片走 img.inurl.link | `/api/news` + `/api/ads` | ❌ 运营资讯标题/摘要失配（内容质量新证据）；短链矩阵持续（F-086） |
| F-101 | P | 首页 `#why`「为何不封号」区给出「不是中转，是 BYOK」三论据：①云端不调厂商（中转平台服务端代调并缓存 Key；inurl 让调用发生在用户机器、云端零厂商请求）；②厂商看到你的 Key（鉴权身份是用户本人，不被判定为共享代理）；③统一令牌只在本地（仅用于本地 Agent 与控制台鉴权，不进入发往厂商的请求）。hero 演示令牌样例 `byok_live_9f3a·7Kq2…`；自述统计仍为已托管密钥 6 / 支持厂商 8+ / 明文上云 0 / AES-GCM 256 / 本地发起 100% | 首页 #why 渲染文本 | ✅/⚠️ 持续（F-045/F-083）：论据为站点自述；统计数字仍未随 46 家目录更新 |
| F-102 | O | /guide 三审新增细节：步骤 2 补自定义厂商图文流程（务必填模型名否则不进下拉）；FAQ 明示自动路由别名 `inurl`（`auto`/`default` 同义、旧版 auto 向后兼容）、inurl≡inurl-text；进阶环境变量 `AUTO_MODELS="deepseek-v4-flash,qwen-max"`（限定路由模型）与 `AUTO_PROVIDER_ORDER="deepseek,qwen,openai"`（厂商优先级）；开机自启指引（byok-launch.bat 放入 shell:startup）；停止代理「任务管理器结束 node 进程，或 taskkill /f /im node.exe」；启动器需 Node.js 18+；五步/分类路由/额度手填口径同 G4 | /guide 全文 | ✅ 持续并细化（F-048/F-081） |
| F-103 | O+P | /models#paid 付费公开卡型号陈旧：OpenAI 卡仍列 gpt-4o-mini/gpt-4o/gpt-3.5-turbo；Anthropic 卡 claude-3-5-sonnet-latest/claude-3-5-haiku-latest/claude-3-opus-latest；xAI 卡 grok-2/grok-2-mini；Google 卡仍 gemini-1.5-flash/1.5-pro/2.0-flash-exp（付费卡 1.5-pro 无 -002 后缀；-002 在免费卡）。对照 F-069（2026-09 当期旗舰 GPT-5.6 Sol、Claude Opus 5；GPT-4o 已于 2026-02-13 退役）——**付费目录整体落后官方当期至少 1 个大版本** | /models#paid 渲染文本 × F-069 | ⚠️ 新增：F-080 陈旧信号从免费区扩展至付费区；付费转用决策风险 |
| F-104 | O | OmniRoute 对标 P0 核验：真实存在的 **MIT 许可、本地优先开源 AI Gateway**——npm 包 `omniroute`（访问时 v3.8.49），全局安装后网关在 localhost:20128（/v1 OpenAI 兼容）；官方站 omniroute.online 自称 352 providers / 19 routing strategies；GitHub 仓库 diegosouzapw/OmniRoute（README 列 19 策略与 Combos、RTK+Caveman 压缩自述 15–95%、工具链重负载示例约 89%，项目已加入 Cheaper Inference 生态）；中文技术媒体（腾讯云开发者社区，2026-09-17）独立复述 19 策略/Combo。inurl 的「19 种策略、Combo 路由链、RTK 压缩档位」命名与口径有明确开源原型，且 inurl 页面主动标注「OmniRoute 同款思路 / Combo 一致」 | omniroute.online + npmjs.com/package/omniroute + github.com/diegosouzapw/OmniRoute + 腾讯云开发者社区（2026-09-17 访问） | ✅ 对标实体真实（四源交叉，2026-09-28）；providers/star 等计数随来源与时点变化，压缩率口径与 inurl 不同，差异详见 bundle references/omniroute-benchmark.md；**不作抄袭/侵权判定** |
| F-105 | O | 四页（/、/app、/guide、/models）仍均加载 `https://inurl.link/track.js`；页脚仍仅「© 2026 inurl · 聚合 APIToken · 端到端加密密钥库」，无公司名/ICP/公安备案/邮箱/GitHub；免费区顶部机场广告（短链 mojie-inurl）仍在 | 四页 HTML | ⚠️ 持续（F-084/F-087） |

### 裁决

- P0 合计（2026-09-16 首轮）：**✅ 通过 11 项 / ⚠️ 口径差异或风险 7 项 / ❌ 失实或矛盾 4 项（F-060 时间线、F-064 DeepSeek 免费、F-069 型号过时、F-070 0 元口径冲突）**
- **2026-09-28 二次复核（G4，F-071~F-087，✅6 / ⚠️8 / ❌2 / 🔄1）**：4 项 ❌ 的产品侧依据原样成立——DeepSeek 仍在付费区（F-076）、免费档 3 密钥定价未变（F-072），且站点目录继续重复 F-061/F-062/F-059 三处已勘误口径（F-079 ❌）；F-060/F-069 属博文历史事实，不随后续站点变化改变。产品持续迭代属实（跨平台启动器、额度管理、实时演示，F-081/F-083），但新增边界：catalog 公开下发测试/预留厂商（F-077）、video/audio 分类当前空转（F-082）、track.js 行为采集（F-084）、F-057 工程信号部分修订（F-085）。**结论：维持 `status: flagged`，`stale_after: 2026-12-31` 不变。**
- **2026-09-28 三次复核（G5，F-088~F-105，✅8 / ⚠️8 / ❌2 / 🔄0；其中 F-095、F-101 为 ✅ 带 ⚠️ 附注）**：站点对 G4 **零迭代**——catalog 与 G4 字节级同一文件（F-088），定价/隐藏商/能力标签/turnstile/短链/track.js/无备案页脚全部持续，三处官方已勘误口径三审未改（F-092 ❌）。新增 /app 功能面系统证据：仪表盘、19 路由策略+5 档压缩+Combo、自定义厂商三协议、运营后台八模块、源同步自述与生产环境 mock 支付按钮（F-094~F-098）；公开 ads/news 接口且 news 首条标题与摘要文不对题（F-100 ❌）；付费目录整体落后当期旗舰 ≥1 个大版本（F-103 ⚠️）；OmniRoute 对标实体经四源核实为真（F-104 ✅）。**结论：`status: flagged` 第三次维持，`stale_after: 2026-12-31` 不变。**
- 个人自述类（F-009 $80、F-010 0 元账单、F-033 三周、F-038 省 90%、F-025 0.1 秒切换）无独立出处，不判真伪，正文一律标注"作者自述/厂商自述"。
- **bundle 状态：flagged**——失败项命中博文主结论（0 元全免费工作流），按 L3 flagged 状态管理执行；G4/G5 两轮站点直证均未出现可改判证据。

---

## H. 第二信源合并区（信源 B：2026-09-04《一年省下5000块》，F-106 ~ F-122）

> **合并记录（2026-09-28，session=`sc-20260928-inurl-merge`）**：原同主题姊妹 spec `inurl-byok-free-models-blog-okf-wiki/`（信源 B：微信公众号《同事偷偷用这个网站，一年省下5000块 Token 费用》，URL `mp.weixin.qq.com/s/xbpFUmp2s87BUbcFagwQ0A`）并入本 spec，其 bundle 同步合并为 `jishu/ai/inurl-byok-token-hub/`。原 F-001~F-035 共 35 条：**14 条产品/加密/模型类与信源 A 重复，不另立编号**；**21 条独有原文归并登记为 17 条 F-106~F-122**。本区与 bundle `references/article-source.md` H.1 双份机械一致；去重映射见该文 H.2。
>
> 类型沿用信源 B 标注：O=客观叙述　S=厂商自述　V=作者观点　T=转述/传闻。

| 编号 | 类型 | 事实 | 核验 |
|------|------|------|------|
| F-106 | O | 第二文元信息：标题《同事偷偷用这个网站，一年省下5000块 Token 费用》；封面标「TOKEN 省钱实战 2026.08」；发布于 2026-09-04 22:00；URL `mp.weixin.qq.com/s/xbpFUmp2s87BUbcFagwQ0A`；正文 2090 字符、3 张设计卡片、无表格/代码块（归并原 F-001/F-003/F-004） | ✅ 博文元数据 |
| F-107 | O | 同公众号「风信旗」、作者「检校千牛卫」，标原创，IP 属地河南；账号自述定位「持续分享 AI 省钱实战与工具干货」（归并原 F-002/F-025） | ✅ 博文元数据 |
| F-108 | V | PART 01 观点组：「大多数人把 AI 当订阅制 SaaS 每月乖乖交会员」「会玩的人把各家免费、低价通道串成流水线」「涨价是真的，但用不起是假象」——未给出任何具体涨价事实或价格数字（归并原 F-005/F-006/F-008） | 📝 作者观点 |
| F-109 | T | 标题与导语钩子：「同事年度账单」一年省下 5000 块 Token 费用，「省下来的都是净利润」（原 F-007） | ❌ 无账单、无用量假设、无对比测算；官网/同号系列软文/全网查无出处（F-117）；BYOK 不经手 token 售卖、用户按厂商原价付费，不产生该量级价差 |
| F-110 | S | 第二文 Agnes 声明：美国·完全免费·Sapiens AI 出品的全模态免费网关；agnes-2.5-flash 支持百万级上下文；注册即送 Key，适合长文档长对话（原 F-017） | ❌/⚠️ 三重勘误：国籍（F-118）、上下文（F-062）、免费条件（F-119）；模型真实在线/OpenAI 兼容/注册可用 ✅ |
| F-111 | S | 第二文硅基流动声明：新老用户都有免费 Token 额度，可零成本体验 Qwen、DeepSeek、GLM 等开源模型（原 F-019） | ✅/⚠️ 免费 9B 级开源小模型全员 0 元属实；无 GLM-4-Flash 型号、满血 DeepSeek 付费（F-120） |
| F-112 | S | 第二文 LongCat 声明：美团自研万亿参数 MoE；新用户注册送 1000 万 Tokens；原生 1M 上下文；OpenAI 兼容（原 F-020） | ⚠️ 万亿/1M 仅属 LongCat-2.0；1000 万须实名领取+30 天+限时（F-121）；OpenAI 兼容 ✅ |
| F-113 | V | 「4 个免费 Key 收进 token.inurl.link 就是永不涨价的模型弹药库」（原 F-021） | 📝 作者观点；免费政策均可被厂商调整（F-119/F-120/F-121） |
| F-114 | V | PART 04：用统一令牌串免费/付费/自家 Key、按成本自动路由；「省下的会员费够买好几顿火锅」（原 F-022） | 📝 纯口号，无任何操作步骤 |
| F-115 | V | 结尾：「大厂涨的是他们的价格，创作权不该被绑票……把密钥握在自己手里、用免费模型补日常消耗」（原 F-023） | 📝 作者观点 |
| F-116 | O | CTA 与外链结构：注册链接 `token.inurl.link/app?tab=register`；正文 6 个 URL = 4 条 `inurl.link/<agnes-ai|bigmodel|siliconflow|longcat>` 导流短链 + 注册页 + 官网，**无一条第三方信源**（原 F-024 + 外链留档） | ✅ 营销结构证据 |
| F-117 | 核验 | 第三方独立证据为零：除自有域名与「风信旗」同号系列软文（另见 2026-09-09《学生党福音！4个免费大模型…》、2026-09-15《AI 模型 API「中转」和「BYOK」…》）外，Bing/百度/搜狗、GitHub/Gitee/npm、技术社区均无任何第三方报道、评测或开源仓库；「5000 块」在官网/软文/全网均查无（原 F-029） | ✅ 查证；与 F-056 互补——F-056 证运营主体匿名，本条证外部证据真空 |
| F-118 | 核验 | Agnes AI 运营主体为**新加坡 Sapiens Technology Pte. Ltd.**（非美国），创始人 Bruce Yang（NUS 博士生）；PRNewswire 2025-05-01 新闻稿（302443885）、App Store 上架主体、Tech in Asia 2026-03 融资 2000 万美元报道三源一致（原 F-030） | ✅ 查证 |
| F-119 | 核验 | Agnes 2.5-flash 当前 **$0 系阶段性优惠**（官方明示结束时间以平台公告为准），刊例价输入 $0.05/输出 $0.15 每百万 token；免费文本名义 30 RPM、第三方实测约 **20 RPM / 1,000 RPD**；付费 Token Plan（Starter/Plus/Pro）、agnes-2.5-pro（$0.45/$0.90）、视频按秒计费并存，免费层无 SLA（原 F-032） | ✅ 查证 |
| F-120 | 核验 | 硅基流动：实名认证后免费模型对全体用户（含老用户）长期 0 元（收费版以 `Pro/` 前缀区分）；现行激励为实名后活动中心**手动领取 ¥16（$1）通用代金券、180 天有效、活动至 2026-12-31**（「¥14/2000 万 token」为 2025 年初旧政）；免费档为 9B 级开源模型（Qwen3-8B、DeepSeek-R1-Distill-Qwen-7B 约 30 RPM/60K TPM、glm-4-9b-chat），平台**无 GLM-4-Flash 型号**、DeepSeek 满血版付费；OpenAI 兼容 `api.siliconflow.cn/v1`（原 F-034） | ✅ 查证 |
| F-121 | 核验 | LongCat-2.0（2026-06-30 发布）：总参 **1.6T**、每 token 平均激活约 **48B**（动态 33B–56B，零计算专家+ScMoE；上代 Flash 总参 560B）；基于 LSA 稀疏注意力**正式支持 1M** 窗口、最大输出 128K（Flash-Chat 仅 128K）；1000 万 Tokens 须**实名领取、30 天有效**、限时活动以页面为准（另有 ¥9.9/5000 万、¥399/10 亿付费包，Cache 命中不计入）；Flash 系列 6 个老模型 2026-05-29 停调；OpenAI 兼容 `api.longcat.chat/openai`（另有 Anthropic 端点）；官方确认限流但未公开 RPM/TPM（原 F-035） | ✅ 查证 |
| F-122 | O | 第二文结构留档：PART 01 焦虑铺垫（无具体涨价事实）→ PART 02 inurl 四项功能 → PART 03 四家免费模型 → PART 04「搭管道」口号（无操作步骤）→ LAST 观点升华+注册 CTA；搜狗微信索引未见本篇收录（传播面旁证，与 F-117 互证） | ✅ 结构留档 |

> 算术核对：14（重复）+ 21（独有编号事实）= 35（原编号总数）；21 条独有原文经 3 组合并（8 条→3 条）+ 13 条一对一登记为 16 条事实，另加 1 条结构留档（F-122）= **F-106~F-122 共 17 条**，与信源 A 编号连续无跳号。勘误编号续接信源 A 的 E1–E6：第二文三条勘误为 **E7**（5000 块查无）、**E8**（Agnes 新加坡国籍）、**E9**（Agnes 阶段性 $0/20RPM）；第二文「百万上下文」沿用 E5/F-062 不另立。
