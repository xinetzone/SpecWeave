---
source: "https://zhuanlan.zhihu.com/p/2050524686992380835"
type: "knowledge"
date: "2026-09-10"
tags: ["大模型", "免费API", "Token", "LLM", "资源汇总"]
---

# 2026 最新免费大模型 API 汇总｜海量免费 Token，学习够用一整年

**作者：** 蹦豆儿  
**发布时间：** 2026-06-17 14:10 · 河北  
**来源：** https://zhuanlan.zhihu.com/p/2050524686992380835

---

平时自己自学 AI、写 Demo、调试工具，每次调用大模型都要消耗 Token，长期充值花销实在太大。我一直优先找免费额度使用，索性把全网靠谱的免费大模型 API 全部整理汇总。

这份是 2026 年更新后的完整版，区分国内无需翻墙平台与海外模型渠道，每个平台免费 Token 数量、有效期、擅长场景、领取规则全部标注清楚。

足够大家日常学习、做实验、开发小型工具使用，有需要的朋友可以收藏，再也不用到处零散找免费资源。

---

## 国内平台（无需魔法，直连可用）

| 平台 | 免费额度 | 代表模型 | 擅长点 | 备注 |
|------|----------|----------|--------|------|
| 阿里云百炼 | 新用户7000万Token（90天）+ 单模型100万Token；企业最高100亿Token（1年） | Qwen3.6-Plus、Qwen-Plus、Qwen-Max、通义千问全系、DeepSeek全系、Kimi、MiniMax、GLM | 编程能力接近Claude Sonnet，100万token上下文，原生多模态（OCR、物体定位） | 支持OpenAI兼容接口；Token Plan首月5折，包季4.5折；Coding Plan 200元/月限量发售 |
| 腾讯云TokenHub | 各模型50-100万Token（90天），视觉模型50次，视频50积分，3D 100积分 | Hy3 preview、DeepSeek-V4-Flash/Pro、GLM-5、MiniMax-M2.7、Kimi-K2.6 | 一站式多模型聚合，适合快速原型验证 | 需登录控制台领取，90天内有效 |
| 中国移动MoMA | 新用户9000万Token体验包 | 九天、DeepSeek全系、豆包、通义千问、GLM、MiniMax等300+款 | 独创模型联邦与智能路由，成本优先/效果优先自动匹配，可降低30%成本 | 2026年5月发布，整合300+模型 |
| 百度智能云千帆 | 每模型100万Token（3个月）；200次/日（Lite/Speed-8K），60次/分（Speed-128K） | ERNIE-4.5-Turbo、ERNIE-X1-Turbo、DeepSeek R1/V3/V3.1、Qwen3系列、Kimi-K2 | 多模态全覆盖（文本+图像+视频理解），数理逻辑准确率92%+，支持联网搜索 | 每模型独立额度，适合分模型压测与横向对比 |
| 字节火山方舟（豆包） | 安心体验：每模型50万Token；协作奖励：每天200万Token（按天重置） | Doubao-Pro-128k、Seed 2.0/1.5、千问全系、DeepSeek全系、Kimi、MiniMax、GLM | 推理成本极低，中文理解优秀，适合AI应用开发；按天重置额度适合长期低频调用 | 2024年豆包定价激进引爆国内价格战；Lite Plan ¥40/月（1.8万次） |
| 智谱AI（BigModel） | 新用户2000万Token；GLM-4-Flash永久免费（限30并发） | GLM-5、GLM-4-Flash、GLM-Z1-Flash | 中文推理第一梯队，代码生成能力国内顶尖，GLM-4-Flash可长期兜底 | 原生支持OpenClaw接入，29元可订阅低价套餐；400次/周 |
| 硅基流动（SiliconFlow） | 新用户¥14赠金；部分小模型（Qwen2.5-7B等）永久免费；各模型1000 RPM | DeepSeek-R1-0528、Qwen3-8B、GLM-4-9B-chat、GLM-4系列、MiniMax-M2.5等数十款 | 国内直连海外模型，兼容OpenAI SDK，并发容量大，适合高频调用 | 企业认证送500元，学生认证送50元；更像中间层聚合平台 |
| 月之暗面Kimi | 不限Token总量，限3次/分钟；个人认证送15元 | Kimi-K2.6系列 | 256K超长上下文窗口，长文本阅读、文档摘要、书籍级内容处理 | 适合处理超长文档，不赶时间慢慢跑即可；¥49/月Andante套餐 |
| DeepSeek官方 | 新用户100万Token（3天有效） | DeepSeek-V4-Pro（1.6T参数）、V4-Flash（284B参数） | 推理+代码能力国内独树一帜，1M token上下文，性价比最高（1元/百万Token） | V4-Flash定价极低，适合长期低成本使用 |
| 百川智能 | 新用户500万Token | Baichuan系列 | 开源模型，网页版免费使用 | 适合开源生态开发者 |
| 腾讯混元 | 100万Token（1年有效） | 腾讯混元系列 | 对话、图片生成、视频生成，多模态能力强，数学方向排名靠前 | 搭配OpenClaw可0成本部署云端开发环境 |
| 美团LongCat（龙猫） | Chat/Thinking系列500万Token/天；Flash-Lite系列5亿Token/天 | LongCat-Flash-Chat、LongCat-Flash-Thinking、LongCat-Flash-Lite | 专为编程优化，额度完全用不完，支持OpenClaw自定义配置 | 每天自动刷新额度，长期免费无截止日期 |
| 讯飞星火 | 新用户200万Token；Spark 4.0 Ultra免费使用（Fair use） | Spark 4.0 Ultra | AI绘图、联网搜索、长文档一体化，语音交互能力著称 | 5 RPM速率限制；适合综合型应用 |
| 讯飞星辰MaaS | 0元/百万Token，无明确额度限制 | GLM-5、MiniMax-M2.5、Kimi-K2.5、GLM-4.7系列 | 实名认证后获取API Key，完美适配OpenClaw | 2026年3月限时活动，建议尽快申领 |
| 白山智算 | 邀请码+实名认证送150元，首次调用再送350元（共450元） | GLM-5及各类编程场景模型 | GLM5输入4元/百万Token、输出18元/百万Token，450元可用数月 | 限10次/分钟，适合高强度开发 |
| 商汤日日新 | Token Plan限时免费 | SenseNova 6.7 Flash-Lite | 轻量级多模态，推理效率高、算力消耗低，适合高响应速度场景 | 2026年5月8日发布，限时免费 |
| 小米MiMo | 新用户注册即得大额初始额度（实测超7亿Token），总计100万亿Token计划 | MiMo-V2.5系列 | 开源模型生态，支持接入Claude Code等第三方工具链 | 2026年5月12日启动，30天有效期，赠完即止 |
| 联通云Coding Plan | Lite版1.8万次/月，Pro版9万次/月，每日1200次 | GLM5、Qwen3.5、MiniMax | 0元订阅，按调用次数计费，适合团队协作 | 12000个免费名额，先到先得 |
| 欧派算力云 | R1/V3模型各100万Token（6个月有效） | DeepSeek-R1、DeepSeek-V3 | 高性能编程优化模型，调用速度稳定 | 配置简单，适合DeepSeek系列深度使用 |
| 零一万物 | 新用户¥10额度；Yi-Lightning免费使用 | Yi-Lightning | 李开复创办，Yi系列模型开源，性价比极高 | 5 RPM速率限制；万知助手免费使用 |
| 国家超算互联网 | 新用户1000万Token | 多款前沿大模型 | 国家队资源，提供千万卡时算力池 | DeepSeek API 3个月免费 |
| Jina AI | 新用户100万Token（Embedding/Reranker专用） | jina-embeddings-v3、jina-reranker-v2 | 多模态向量和reranker API，适合RAG、语义搜索 | 不是通用聊天模型，专精Embedding和搜索增强 |
| ModelScope魔搭 | 每天2000次免费调用（DeepSeek-R1深度推理版限200次） | Flux.1图像生成、QWen-Image、DeepSeek-R1等 | 阿里达摩院出品，图文多模态能力国内免费开放最好 | 适合需要多模态能力的开发者 |
| OpenRouter | 每天免费50次；充值10 credits后解锁每天1000次；25+免费模型 | 聚合30+模型（含DeepSeek、Llama、Qwen、Kimi等） | 一个API Key通吃多家模型，免费用尽可无缝切换付费，方便模型对比；国内可直连 | 模型超市，支持单一Key调用多家模型；统一OpenAI兼容格式 |

---

## 国际平台（需魔法访问）

| 平台 | 免费额度 | 代表模型 | 擅长点 | 备注 |
|------|----------|----------|--------|------|
| Google AI Studio（Gemini） | Gemini 2.5 Flash: 1500次/天（30 RPM）；Gemini 2.5 Flash-Lite: 1000次/天；Gemini 2.5 Pro: 5 RPM/400 RPD；新用户$5赠金 | Gemini 2.5 Flash/Pro、Gemini 3.5 Flash | 百万级上下文窗口（行业独一档），多模态能力极强，适合长文档处理 | 免费层额度最慷慨，每天1440次可用；3.x Pro系列已移出免费层 |
| Groq | 每天1000次请求，6000 tokens/分钟（8B模型14400次/天） | Llama 3系列、Mixtral等 | LPU硬件加速，推理速度极快（300+ tokens/s），适合实时对话、语音应用 | 全球最快公开推理服务，无需信用卡 |
| GitHub Models | 高级模型10 RPM/50 RPD；低级模型15 RPM/150 RPD | GPT-4.1、GPT-4.1-mini、GPT-4o、Phi系列、Llama 4、Grok 3 Mini | 免费用上GPT-4.1和GPT-4o，GitHub账户即用，适合OpenAI系模型测试 | 无需信用卡，单次请求8K输入/4K输出；适合快速Playground验证 |
| NVIDIA Build/NIM | 无限制（已取消额度限制），40 RPM速率限制 | DeepSeek V3.2/R1、Kimi K2.5、GLM-5.1、MiniMax M2.7、Gemma 4等100+模型 | 100+顶级模型完全免费，无需信用卡，适合研究测试多模型效果 | 目前最被低估的免费平台，验证国内手机号即可 |
| Mistral AI | 约10亿Token/月（1 req/s，50万tokens/min），手机验证即可 | Mistral Large、Mistral 8B、Codestral | 欧洲最强开源模型，高性能，天然满足GDPR合规 | 无需信用卡，手机验证即可；免费层数据可能用于模型改进 |
| Cerebras | 100万Token/天（30 RPM，6万tokens/min） | Llama系列 | 超高速推理（2600+ tokens/s），WSE专用芯片，但上下文较短 | 需等待列表，适合极速推理场景 |
| Cloudflare Workers AI | 10,000 Neurons/天 | 多种开源模型（LLM、嵌入、图像、音频） | 全球CDN边缘节点加速，延迟极低，适合面向全球用户的应用 | 无需信用卡，适合边缘AI应用 |
| HuggingFace | 每月动态积分（根据账户等级）；仅支持<10GB模型 | 数千开源模型（LLaMA、Mistral、Falcon等） | 开源模型最大宝库，适合研究和实验、横向对比不同架构 | 模型最丰富，社区活跃；Serverless Inference免费层 |
| AI21 Labs | $10积分（无需信用卡） | Jamba Large/Mini | 长上下文处理，混合架构 | 适合长文本生成任务 |
| Scaleway Generative | 100 RPM，20万tokens/min（免费测试中） | 多种开源模型 | 欧洲云服务商，GDPR合规 | 测试中，额度较宽松 |
| Together Free | 无明确限制 | Meta-Llama-3.1-8B等 | 开源模型推理优化 | 适合开源模型部署 |
| Fireworks AI | $1积分 | 多种模型 | 高并发支持，企业级推理 | 适合高并发场景测试 |
| Cohere | 20 RPM | command-a系列 | 企业级文本生成，RAG优化 | 适合企业文本处理 |
| Modal | 不计token，限1-2路并发 | GLM-5（OpenClaw优化） | 适合长上下文任务测试，无Token焦虑 | 限时免费，需创建API Token |
| xAI Grok | $25/月（每月重置）；Grok 4.20限速率 | Grok 4.20、Grok-3 | 256K token上下文，实时X/Twitter数据访问，幻觉率业界最低 | 支持OpenAI SDK兼容；数据共享计划（$150/月）已终止 |
| Anyscale | $10免费额度 | Llama 3.3 70B、Mixtral 8x22B | Ray分布式框架加速，推理效率高 | 30 RPM；由UC Berkeley教授创办 |
| OpenAI | 新用户（个月过期）；初创计划500-$50000+ | GPT-4o、GPT-4.1、GPT-4.1-Nano、o3、o4-mini | 行业标杆，通用能力最强；GPT-4.1 Nano最便宜（$0.1/百万Token输入） | Free Tier用完即止；Tier系统需累计付款解锁更高限额 |

---

## 按场景快速选型指南

| 你的需求 | 推荐平台 | 理由 |
|----------|----------|------|
| 🇨🇳 国内开发，不想折腾网络 | 阿里云百炼、硅基流动、智谱AI、美团LongCat | 直连稳定，中文优化，额度充足 |
| 💻 代码生成 & 编程辅助 | DeepSeek官方、智谱GLM-4-Flash、美团LongCat、GitHub Models | 代码能力顶尖，编程专用模型 |
| 📜 超长文本处理 | Kimi（256K上下文）、阿里云百炼（Qwen3.6-Plus 100万上下文） | 上下文窗口行业领先 |
| ⚡ 极速推理/实时对话 | Groq、Cerebras | LPU/WSE专用芯片，速度碾压GPU |
| 🖼️ 多模态（图文视频） | Google Gemini、百度千帆、腾讯混元、ModelScope魔搭 | 图像理解+文本生成+视频生成全覆盖 |
| 🔬 多模型对比评测 | OpenRouter、NVIDIA NIM、中国移动MoMA | 一个Key调用30+模型，横向对比最方便 |
| 🆓 永久免费兜底 | 智谱GLM-4-Flash、美团LongCat、Google Gemini 2.5 Flash | 长期免费，无额度焦虑 |
| 🚀 薅最多Token | 小米MiMo（7亿+）、中国移动MoMA（9000万）、阿里云百炼（7000万） | 新用户福利最壕 |

---

## 重要提醒

- **额度会动态调整**：各厂商免费政策随时可能变化，建议以官方最新公告为准
- **注意有效期**：很多额度有90天或30天的有效期，领取后尽快使用
- **速率限制**：免费层通常有RPM（每分钟请求数）限制，高并发场景需考虑
- **国内vs国际**：国内平台中文能力强、延迟低；国际平台模型更新快、选择多
- **多账号策略**：部分平台（如DeepSeek）额度有限，可注册多个账号轮换使用

---

如果这份免费大模型清单对你有帮助，欢迎点赞、收藏、转发给身边做 AI 开发的朋友。领取额度、调用过程中遇到任何问题，都可以在评论区留言交流，我会及时回复。感谢大家支持！

感谢看到这里！

如果本文对你有所帮助，欢迎点赞支持。

前端实战笔记、踩坑总结会持续更新，更多干货首发于公众号【**前端晨话**】，欢迎关注 ~
