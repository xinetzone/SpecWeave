---
okf_version: "0.2"
type: facts
title: "事实登记表——免费大模型接入全攻略（2026-09 实战版）"
source: https://mp.weixin.qq.com/s/qnQqCivPiuRfJIVMM-zTNQ
generated: { by: "blog-article-to-okf-wiki:R", at: "2026-09-16T20:45:00+08:00" }
---

# 事实登记表（facts.md）

> 唯一合法事实集（R 阶段产出）。F-001~F-061 来自博文；F-062+ 为 V/R 核验阶段权威源补充。
> 规则：客观事实纯描述（G1：无"因为/导致/所以"因果词）；作者观点/作者实测显式标注；价格/额度/日期均为博文 2026-09-09 口径。

## A. 元信息与术语（F-001 ~ F-005）

| 编号 | 事实 | 原文位置/备注 |
|------|------|---------------|
| F-001 | 文章推送标题《我用3个免费模型，把WorkBuddy的成本砍到了零》；正文内主标题为「免费大模型接入全攻略（2026-09 实战版）」 | 标题区 |
| F-002 | 公众号「技术宅SuperLaos」，作者署名老商；带"原创"标记；发布时间 2026-09-10 08:40（页面时间戳 ct=1789000800），IP 属地河北；正文注"整理日期 2026-09-09"；结尾称"整合多渠道+腾讯/字节官方及社区资料，交叉核实于 2026-09-09" | 元信息区/结尾 |
| F-003 | 博文声明适用对象：想零成本把大模型接进 WorkBuddy / Trae Work 等 OpenAI 兼容客户端的开发者、运营、数据分析师 | 导语 |
| F-004 | 博文风险提示原文要点：各平台免费政策按周变动，额度/限流/截止日以控制台实时显示为准；医药、患者、未公开经营数据请勿传第三方模型；认准官方域名谨防仿冒站点 | 导语 |
| F-005 | 博文自定术语：LLM=纯文本大模型；VLM=视觉/多模态模型；Base URL 各家均须带 /v1 后缀否则 404；免费档五分法=无限期免费/限流不限量/每日重置/限时免费（有截止日）/一次性赠金；价格单位统一为"元/百万 token（输出）"；国内直连=无需代理 | §0 |

## B. 三平台总览（F-006 ~ F-008）

| 编号 | 事实 | 原文位置/备注 |
|------|------|---------------|
| F-006 | Agnes AI 总览口径：免费模型 agnes-3.0-flash（文本+图像 URL）＋image-2.5-flash（生图）＋video-2.5-flash（生视频）；另有 Agnes Code 桌面版内置 8 技能；国内直连；国内邮箱/Gmail·GitHub 注册、免绑卡；免费期限表述"无限期免费（定价待公布，免费档延续）"；横评表标约 20 RPM；博文列最大坑为"免费人多输出慢；4K 图 1 次/分" | §1/§5 |
| F-007 | 小红书 dots 总览口径：模型 dots3-note-prev（VLM 四模态）；国内直连；手机号/小红书账号注册、免绑卡；"限时（官方未公布；OpenRouter 通道 9-30 关）"；限流 60 RPM、150 万 TPM；上下文 512K；最大坑"认证头 api-key 非 Bearer" | §1/§3/§5 |
| F-008 | AMD Radeon 总览口径：4 款免费模型（2 LLM+2 VLM）；国内直连；手机号/邮箱/GitHub 等注册、免绑卡；每日重置积分制（不扣钱）；上下文表列 1M/128K/256K；最大坑"速度慢；Vision 标 LIMITED FREE 随时撤"；横评列"并发 >5 排队" | §1/§4/§5 |

## C. Agnes AI 细节（F-009 ~ F-032）

| 编号 | 事实 | 原文位置/备注 |
|------|------|---------------|
| F-009 | 两站对照表：国内站注册/控制台 platform.agnes-ai.cn（登录页 /login/），网关 Base URL `https://api.agnes-ai.cn/v1`，国内邮箱（QQ 邮箱等）或手机号登录，国内直连，文档 agnes-ai.cn/doc/overview；国际站 platform.agnes-ai.com，网关 `https://apihub.agnes-ai.com/v1`，Gmail/GitHub 登录，"服务器在境外，国内访问可能延迟偏高"，文档 agnes-ai.com/doc/overview；两站认证均为 Authorization: Bearer \<Key\>；推荐文本模型两站同为 agnes-3.0-flash | §2.1 |
| F-010 | 博文转述"⚠️ 官方公告"：因部分国内网络访问国际站 API 不稳定，请将 apihub.agnes-ai.com 切换为 api.agnes-ai.cn（域名 .com→.cn，apihub→api）；仅改域名，API Key/模型名/参数不变，改完重启应用 | §2.1（引文级，待逐字核验） |
| F-011 | 两站账号体系独立：此前在国际站注册过的用户用国内站需重新注册并生成新 Key | §2.1 |
| F-012 | agnes-3.0-flash 特性条（博文据官方口径整理）：面向真实 Agent 任务与开发工作流；更稳定的函数调用、多步骤工具编排，减少无效/重复调用与异常循环；文本+图像 URL 输入（公开可访问图片 URL，非本地文件直传）；多协议 Chat Completions（/v1/chat/completions）、Responses（/v1/responses）、Messages（/v1/messages，Anthropic 兼容）；Thinking 模式（chat_template_kwargs.enable_thinking 或 Anthropic thinking.type:enabled）；强化事实依据/结果确认/输出完整性；价格待公布、免费档延续 | §2.2 |
| F-013 | 注册拿 Key 流程（两站一致）：打开对应平台登录 → 控制台「API Key」管理页 → 点「创建 API Key」→ 生成后立即复制保存 | §2.3 |
| F-014 | 博文安全红线：API Key 勿进公开代码仓库、前端代码、截图、公开文档；泄露即去控制台删除/重置 | §2.3 |
| F-015 | 博文给的网络自测法：浏览器开 https://api.agnes-ai.cn/v1，返回 404 或 JSON 错误都算通，打不开才是不通 | §2.3 |
| F-016 | WorkBuddy 配置位：聊天输入框右下角模型选择按钮 →「添加模型」→ 提供商下拉选「自定义/Custom」→ Add Model 填 Provider=Custom、API Base URL（含 /v1）、API Key、模型名称 agnes-3.0-flash（区分大小写） | §2.4 |
| F-017 | 博文列常见易错点：① Base URL 漏写 /v1；② 模型名大小写不对（写成 Agnes-3.0-Flash 会失败） | §2.4 |
| F-018 | 高级配置建议：勾选工具调用、图片输入、思考模式、允许关闭思考；不勾选「仅思考模式、自定义协议」；思考强度保持「自动」 | §2.4 |
| F-019 | 连通性验证：新建对话发"你好，请介绍一下你自己。"，返回自我介绍即正确；博文附 chat/completions curl 示例（POST，Bearer，model=agnes-3.0-flash） | §2.5 |
| F-020 | agnes-image-2.5-flash（博文注依据官方文档 agnes-image-25-flash）：端点 POST https://api.agnes-ai.cn/v1/images/generations；能力文生图/图生图/多图合成；size 档位 1K/2K/3K/4K 与 ratio（1:1、3:4、4:3、16:9、9:16、2:3、3:2、21:9）组合；非原生精确尺寸（如 1920x1080）自动映射，标准 16:9 应请求 size:"2K"+ratio:"16:9"（得 2624x1472）再裁剪；response_format 不放请求体顶层而放 extra_body（URL 用 extra_body.response_format:"url"，图生图 Base64 用 "b64_json"）；图生图/多图合成输入放 extra_body.image（公共 HTTPS URL 或 Data URI Base64），不需传 tags:["img2img"]；文生图要 Base64 用 return_base64:true；返回路径 data[0].url 或 data[0].b64_json；客户端超时建议 60s–360s；博文附 curl 示例 | §2.6① |
| F-021 | 博文列刊例价（注明"以平台公告为准"）：1K 图 ¥0.07/张、4K 图 ¥0.16/张、视频 ¥0.15/秒；image-2.5-flash 与 video-2.5-flash 现价均为 ¥0 | §2.6 引 |
| F-022 | 博文转述官方提示词结构：文生图=[主体]+[场景/环境]+[风格]+[光照]+[构图]+[质量要求]；图生图=[改变要求]+[新风格]+[增删元素]+[需保留的元素] | §2.6① |
| F-023 | agnes-video-2.5-flash（博文注依据官方文档 agnes-video-25-flash）为异步两步：创建 POST https://api.agnes-ai.cn/v1/videos 成功返回 video_id；查询 GET `https://api.agnes-ai.cn/agnesapi?video_id=<ID>&model_name=agnes-video-2.5-flash`，建议每 1–2 秒轮询至 status 为 completed/failed；博文附两条 curl | §2.6② |
| F-024 | 视频三种 mode：text（纯文生视频）；keyframe（first_frame 与 last_frame 至少提供一个）；reference（图片参考 images ≤ 5 张或音频参考 audios ≤ 3 段；不支持参考视频，传 videos 直接 400） | §2.6② |
| F-025 | Flash 视频参数限制：size 只能是字符串 "720P"（其他值 400）；seconds 为字符串 "4"–"12"（默认 "5"）；n 固定 1；aspect_ratio 支持 21:9、16:9、4:3、1:1、3:4、9:16；博文称 16:9 实测输出 1280x704（作者实测口径）；校验失败（size≠720P/图超 5 张/音频超 3 段/传参考视频）创建时直接返回 400，不建任务、不产生费用 | §2.6② |
| F-026 | 博文给"懒人法"：在 WorkBuddy 发"我想使用 Agnes 2.5 Flash 系列模型生成图片和视频，请访问其 API 文档（agnes-image-25-flash 与 agnes-video-25-flash）并分别打包为两个 Skill"；并给图像/视频 Skill 的示例调用句 | §2.6③ |
| F-027 | Agnes Code 桌面版（爱思办公，博文注依据官方 agnes-ai.cn/agnescode）：桌面客户端自动连接本地工作空间，与爱思 Web 账户同步订阅与积分；另提供命令行 CLI（装完跑 agnes --version 验证，适合终端/脚本/CI）；系统支持 macOS 12.0+（Apple/Intel 各 .dmg）、Windows 10+（.exe x64）、Linux（.deb x86_64）；博文注"Linux 桌面版不与 CLI 混用（官方明示）"；macOS"无法打开"到隐私与安全性放行 | §2.7 |
| F-028 | Agnes Code 内置 8 技能：agnes-aigc（调度入口，路由 AIGC 请求）、agnes-text-to-image、agnes-image-to-image、agnes-text-to-video、agnes-image-to-video、agnes-sheet-author（CSV/Excel/仪表盘/数据清洗/搜索转表格）、agnes-doc-guide（查配方案/扩展/会话/Provider/语法/命令）、skill-creator（创建保存可复用技能） | §2.7② |
| F-029 | 双模式：智能模式（只输目标，自动选模型/工具/执行路径）；专家模式（手动控制模型、上下文、工具、预算、产物格式与权限） | §2.7③ |
| F-030 | 使用限制：必须用爱思账户登录，订阅/积分/团队权限与网页端一致，无独立"桌面版免费额度"，底层消耗 Agnes 账户积分；客户端本身免费；走国内站国内直连；首次登录选工作区目录时请求访问权限，只读授权目录、记录关键变更；博文一句总结"桌面版≠额外免费羊毛，而是 Agnes 账户积分的图形化操作入口"（末句为作者观点） | §2.7④ |
| F-031 | 故障排查表 5 行：文本不返回→URL 错/Key 无效→核对 /v1 与 Key；列表没这模型→大小写错→从平台复制 agnes-3.0-flash；Skill 创建失败→文档 URL 不可达→确认能开 /doc/overview；视频很久没好→本就慢→查状态/URL；认证失败→Key 错/余额不足→重填 Key 查积分 | §2.8 |
| F-032 | Agnes 段红线 4 条：Key 绝不外泄；敏感资料（医学/患者/未公开经营数据）不传第三方、对外内容人工复核标注来源；免费/积分额度以控制台为准、批量任务节制；模型各司其职（文本用 flash，图像/视频走对应 Skill） | §2.8 |

## D. 小红书 dots3（F-033 ~ F-038）

| 编号 | 事实 | 原文位置/备注 |
|------|------|---------------|
| F-033 | 本段来源：同公众号原创《薅羊毛！公测免费的小红书大模型 dots3-note-prev 接入 WorkBuddy 与 Trae 指南》（老商，2026-08-21） | §3 源注 |
| F-034 | 注册 3 步：浏览器开 https://dots.ai/platform 点登录；用国内手机号或小红书账号注册登录；控制台左侧「API Keys」→「创建 API Key」，Key 只展示一次，丢了只能重建 | §3.1 |
| F-035 | dots3 API 基础信息表：基础 URL `https://note3-prev-api.askdiandian.com`；OpenAI 端点 …/v1/chat/completions；Anthropic 端点 …/v1/messages；模型名称 dots3-note-prev；上下文 512K（输入+输出合计 ≤ 524,288 token）；认证头 `api-key: <你的 Key>`（博文加粗"不是标准 Bearer"，遇 401 先查这里）；限流 60 RPM、150 万 TPM（预览期可能调整） | §3.2 |
| F-036 | WorkBuddy 接入：右上角齿轮（Ctrl+,）→「模型」→「添加自定义模型」→ 提供商选自定义/OpenAI → 接口地址填完整 https://note3-prev-api.askdiandian.com/v1/chat/completions（必须带 /v1/chat/completions、无尾斜杠）→ 粘 Key、模型名 dots3-note-prev；高级配置勾工具调用、图片输入，推理模式选「仅思考/允许关闭思考」；保存后发"你好"验证 | §3.3 |
| F-037 | Trae 接入（博文限定"仅桌面版本地用"）：设置→模型→「+添加模型」→自定义配置；OpenAI 兼容（Chat Completions，模型 ID dots3-note-prev）或 Anthropic 兼容（Messages，Anthropic 版本 2023-06-01，需额外请求头）；对话框右下角关掉「Auto」手动选模型 | §3.4 |
| F-038 | dots 注意事项：免费截止未公布，端点/限流公测期随时变，只做开发测试别跑生产；429=限流，批量控节奏或多 Key 分摊；含视频输入时 TTFT 明显变长需放宽超时；预览版幻觉抑制不足，医疗/法律/财务须人工复核；Key 不写进前端/URL/GitHub/日志；深度思考默认开（OpenAI 用 chat_template_kwargs.enable_thinking:false 关，Anthropic 用 thinking.type:disabled 关） | §3.5 |

## E. AMD Radeon Token Factory（F-039 ~ F-044）

| 编号 | 事实 | 原文位置/备注 |
|------|------|---------------|
| F-039 | AMD 在中国开发者平台（Radeon Cloud）开设 Public Free Model APIs 免费窗口：OpenAI 兼容协议，一把 Key 通吃多款免费模型，国内直连；同时提供 OpenAI /v1/chat/completions 与 Anthropic /v1/messages 两套格式；博文称模型推理跑在 AMD GPU 云上、不消耗本地算力、本地没显卡也能用；入口 https://developer.amd.com.cn/radeon/modelapis | §4.1 |
| F-040 | 四款免费模型（博文注参数口径据 AMD 平台模型卡 2026-09）：① DeepSeek-V4-Flash-0731（LLM，约 64K–128K，0731 快照版，标 FREE）；② MiniCPM5-1B（LLM，约 128K，清华 OpenBMB，INT4 量化仅 0.5 GB，手机/浏览器可本地跑，FREE）；③ DeepSeek-V4-Flash-Vision-Exp（VLM，约 1M，博文称 305B/激活 13B、MIT 开源，看图/OCR/截图问答，标 LIMITED FREE）；④ Qwen3.8-Flash-Next（AMD 页面归"LLM 文本"但博文按实际能力列为 VLM，原生 262K 可扩至 1M，博文称 125B/激活 6B、Qwen4 架构先导版、编程/Agent 据平台标称接近 Qwen3.7-Plus 水平，FREE）；博文提示目录会更新、模型名以页面实时列表为准 | §4.2 |
| F-041 | 注册领 Key（博文称约 10 分钟 4 步）：入口右上角 Login；登录方式国内手机号/邮箱/GitHub/CSDN/魔搭 ModelScope（博文注 GitHub 登录仅请求读基础公开信息用于确认身份）；邮箱注册需点验证邮件激活；进 Public Free Model APIs 区域点任一模型卡片，弹窗给出 Base URL、Model 名、API Key（博文称所有免费模型共用同一把 Key）、现成 curl | §4.3 |
| F-042 | 额度规则：积分制，页面标输入 0.14 pts/1M、输出 0.28 pts/1M、缓存 0.0028 pts/1M，博文引页面英文原文"Free to use. Points show relative usage, not a charge"；每天重置、用完当天限流次日恢复；博文称早期宣传"每天 $10 免费额度"、近期实测已缩到约 $1/天；作者实测口径"DeepSeek-V4-Flash 跑 200 万 token 才耗约 5%，日常轻办公足够"（作者实测，非官方承诺）；博文提示活动无到期时间但随时可能缩水/收回 | §4.4 |
| F-043 | 调用方式：curl POST https://developer.amd.com.cn/radeon/api/v1/chat/completions，Authorization: Bearer，model=DeepSeek-V4-Flash-0731；base_url 填 AMD 地址、换 model 名即切换；VLM 两款可喂图片/截图；博文称 Cherry Studio、Cursor、opencode 等 OpenAI 兼容客户端接法相同 | §4.5 |
| F-044 | 短板与建议（作者实测+观点混合）：速度偏慢首字延迟高、高峰更甚；连接偶发网络错误，调大 retry 基本能稳；并发超过 5 个开始排队，定位开发调试非生产级；Vision 标 LIMITED FREE 随时可能撤；数据走云端推理，敏感内容建议本地 MiniCPM5-1B 或 Ollama；缓存读取极便宜（0.0028 pts/1M），多轮对话传历史自动命中 | §4.6 |

## F. 横向对比与全局表（F-045 ~ F-058）

| 编号 | 事实 | 原文位置/备注 |
|------|------|---------------|
| F-045 | §5 三平台横评关键数：Agnes 上下文"未公开（约数百 K）"、约 20 RPM；dots 512K、60 RPM/150 万 TPM；AMD 上下文 1M/128K/256K、并发 >5 排队；协议面 Agnes 为 OpenAI 兼容+Responses/Messages，dots 与 AMD 均 OpenAI/Anthropic 双兼容 | §5 |
| F-046 | §5 选型结论（**作者观点**）：要无限期免费→Agnes；要每日额度→AMD；要多模态→dots3（四模态）或 AMD Vision；做本地端侧→AMD MiniCPM5-1B 或 Ollama 本地部署 | §5 |
| F-047 | GLM-4.7-Flash（智谱，LLM，200K 上下文，永久免费，输出价 0，"限流不限量"） | §6 表 |
| F-048 | GLM-5.x（智谱，200K，免费档"新用户 2000 万/限免窗口"，输出价 8–28 元/百万 token；博文注"旗舰限免，随时收"） | §6 表 |
| F-049 | DeepSeek V4-Flash（64K–128K，"新户 500 万/30 天"，输出 3–9 元/百万 token；博文注"官方已预告涨价"） | §6 表 |
| F-050 | Qwen-Turbo（阿里，128K–1M，免费档 7000 万一次性，输出 0.5–1.0 元/百万） | §6 表 |
| F-051 | ERNIE-Lite / Speed（百度，128K，永久免费，0 元） | §6 表 |
| F-052 | 豆包 Seed-2.0-Lite（字节，128K，"100 万/月永久"，输出 0.6–3.66 元/百万，渠道火山方舟） | §6 表 |
| F-053 | Kimi K2.5（月之暗面，256K，网页免费/10 万月，输出 6–12 元/百万，"长文档强"） | §6 表 |
| F-054 | Hunyuan-lite（腾讯，上下文表中未列，免费档 0/0 永久，0 元） | §6 表 |
| F-055 | Hy3（混元 3，腾讯，256K，WorkBuddy 限时免费，295B 总参/21B 激活，MoE，Apache 2.0） | §6 表 |
| F-056 | Hy4 preview（混元 4，腾讯，1M 上下文，WorkBuddy 限时两周免费，770B/49B，MoE，Apache 2.0） | §6 表 |
| F-057 | Trae 内置模型两行：Doubao-1.5-pro / Seed-1.6；DeepSeek-V3.1 / Kimi-K2 / GLM-4.6 / Qwen-3-Coder；均注"Trae 基础版免费"；WorkBuddy 自带 Hy3/Hy4 preview 限时免费 | §6 表 |
| F-058 | 博文称付费旗舰（GLM-5、DeepSeek V4-Pro、Qwen3.5、ERNIE 6.0）输出价 3–28 元/百万 token；§6 表声明"价格/免费档为公开口径，波动频繁，以官网为准" | §6 |

## G. 词汇表/收尾/引用（F-059 ~ F-061）

| 编号 | 事实 | 原文位置/备注 |
|------|------|---------------|
| F-059 | §7 词汇表约 30 条：LLM/VLM/MoE/上下文窗口/Token（中文约 1–2 字=1 token）/RPM/TPM/RPD（举例 Gemini 免费层 1500 RPD）/QPS/OpenAI 兼容/Base URL/Endpoint/Bearer（注明 dots3 用 api-key 头）/Rate Limit（429 退避）/Multimodal/Thinking/Prompt Cache（举 AMD 0.0028 pts/1M）/Cache Hit Free/灰度发布/Streaming/Agent/Open Source（Apache 2.0、MIT、Qwen Community）/SDK | §7 |
| F-060 | §8 收尾（**作者观点+行动建议混合**）：组合策略=日常 Agnes（无限期）+AMD（每日积分）主力、dots3 处理多模态混流、高配旗舰看 §6、本地敏感走 Ollama；"免费有尽头"列举 dots OpenRouter 通道 9-30 确定关闭、AMD Vision LIMITED FREE、DeepSeek 已预告涨价，"能接先接"；合规红线重申；所有额度以控制台为准 | §8 |
| F-061 | 正文内微信跳转链接 5 条：①《零消耗！把免费模型 Agnes 接入 WorkBuddy》②《零消耗！把免费模型 Agnes2.5 接入 WorkBuddy（国内站注册版）》③《薅羊毛！公测免费的小红书大模型 dots3-note-prev 接入 WorkBuddy 与 Trae 指南》④《2B 干翻 4B！国产小钢炮重划斩杀线》（MiniCPM 关联文）⑤"Ollama 本地大模型系列教程合集"（文末「阅读原文」指向）；正文含 4 张无 alt 平台/配置截图 | 正文链接 |

---

## 核验补充事实（F-062 ~ F-088，2026-09-16 三独立子代理 WebSearch 权威源回填）

> 标注约定：【勘误】= 博文口径与权威源冲突，正文呈现本编号正确值；❓= 仅博文单源未获佐证。

### H. Agnes 核验（F-062 ~ F-068）

| 编号 | 事实 | 权威信源 |
|------|------|----------|
| F-062 | Agnes 官方规范文档站为 wiki.agnes-ai.cn/zh-Hans/docs/...（博文的 agnes-ai.cn/doc/overview 为 302 跳转别名，落地英文门户）；9 月现行国内站统一网关 `https://api.agnes-ai.cn/v1`，FAQ 原文"中国站统一使用以下 Base URL"；platform.agnes-ai.cn、platform.agnes-ai.com、apihub.agnes-ai.com 主机均存活 | wiki.agnes-ai.cn/zh-Hans/docs/overview、/faqs.md |
| F-063 | 【勘误·域名公告】2026-07-29 官方通稿的切换目标是 `https://apihub.agnes-ai.cn/v1`（仅 .com→.cn，**保留 apihub 主机名**），并非博文所写 api.agnes-ai.cn（apihub→api）；通稿原文"原国际站注册用户无需前往国内站重新注册，也无需更换原有 API Key……模型名称、请求参数和调用方式均无需修改"。api.agnes-ai.cn 是 9 月官方文档现行网关（两篇 9 月实测称 apihub.agnes-ai.cn 与 api.agnes-ai.cn 均可通），博文把"7·29 公告目标"与"9 月现行网关"两件事压成一条 | 太平洋科技 g.pconline.com.cn/x/2179/21794505.html（新智元同源）；腾讯云开发者社区 2718438 |
| F-064 | 【演变】7·29 通稿曾承诺国际站用户无需重新注册；2026 年 8-9 月多篇独立实测一致陈述两站账号/Key 已不通用、混用报"无效的令牌"（博文按 9 月现状描述基本准确，但中间存在政策收紧演变，官方无"两站独立"原句） | CSDN bigbear00007/163419246 等 |
| F-065 | 【勘误·定价与模型状态】agnes-3.0-flash 刊例价**已公布**：输入缓存命中 ¥0.035、输入 ¥0.35、输出 ¥1.00/百万 token，三项现价均 ¥0（非博文"价格待公布"）；agnes-2.5-flash 官方状态"已全量上线"（非"灰度中"）；agnes-2.0-flash 国际站文档标注"已废弃，不再建议用于新接入，现有调用方迁移 2.5"（非"灰度可用"）。3.0-flash 能力清单（函数调用/图像 URL/三协议/Thinking 两写法）与官方页逐字吻合 | wiki.agnes-ai.cn/zh-Hans/docs/agnes-30-flash、agnes-25-flash；wiki.agnes-ai.com agnes-20-flash |
| F-066 | Agnes 图像/视频 API 细节与官方文档逐字吻合：图像 size 四档+ratio 八种、2K 16:9=2624x1472、extra_body.response_format、return_base64、60-360s；视频 /v1/videos+GET /agnesapi 轮询、mode 三种、images≤5/audios≤3/videos→400、size 仅 "720P"、seconds "4"–"12"、n=1、16:9=1280x704（该实测注记本身出自官方文档"2026 年 9 月实测"）。刊例 1K ¥0.07/4K ¥0.16/视频 ¥0.15 秒、现价 ¥0 均属实；视频页措辞为"当前**限时**免费" | wiki.agnes-ai.cn/zh-Hans/docs/agnes-image-25-flash.md、agnes-video-25-flash.md |
| F-067 | Agnes 免费与限流获官方原文确认：FAQ"我们的核心 AI 模型可以**无限期免费**使用……完整多模态模型免费，包括文本、图像、视频"；Token Plan（2026-06-22 生效）default 用户文本"允许 RPM 30/实际 RPM 20"、4K 图"允许 1/实际 1"——博文约 20 RPM、4K 1 次/分精确对应"实际"列；文件顶部声明数值可按产品策略调整 | wiki.agnes-ai.cn/zh-Hans/docs/faqs.md、tokenplan.md |
| F-068 | 【部分单源】Agnes Code 官方页确认"爱思办公·Desktop + CLI"、三平台安装包（AgnesCode.dmg Apple/Intel 双架构、AgnesCode-Installer.exe、AgnesCode.deb x86_64，分发源 cos-agnes-code.agnes-ai.cn）、agnes --version、订阅积分一体化、智能/专家双模式、客户端免费；但以下三条❓仅博文单源：① "Linux 桌面版不与 CLI 混用（官方明示）"在官方页与三安装脚本中均无此警示；② 精确最低系统 macOS 12.0+/Windows 10+ 官方未列（第三方口径混乱）；③ 8 个内置技能 slug 清单全网零命中，官方仅泛述技能扩展（不可当官方事实引用）。另第三方载桌面端注册后每日登录送 1200 积分（账户级赠额），"无独立免费额度"表述绝对化 | agnes-ai.cn/agnescode；download_cli 脚本 |

### I. dots3 核验（F-069 ~ F-073）

| 编号 | 事实 | 权威信源 |
|------|------|----------|
| F-069 | dots.ai/platform 官方平台真实存在：页标题 dots3-note Preview，登录区"手机号登录 +86 可用 / 小红书扫码"，文档入口 dots.ai/platform/docs；官方定位"预览期**限时免费**"（非严格长期公测）；平台 favicon 托管于小红书 CDN（it-force.xhscdn.com）归属明确。模型补充规格：280B 总参/16B 激活 MoE，输出仅文本（预览版） | dots.ai/platform；机器之心经 36氪 ad.36kr.com/p/3938759517896072（2026-08-14） |
| F-070 | askdiandian.com 为小红书官方同一套服务：dots.ai 运行时配置 runtime-config.js 显式指向 authApiOrigin `https://www.askdiandian.com`、platformApiOrigin `https://dots-platform.askdiandian.com`；域名腾讯云 DNSPod 注册（2024-08-20），站点名"点点"（小红书 AI 品牌）。博文拼写 askdiandian.com 正确；网上 askdian.com/askdianian.com 为错拼 | dots.ai/platform/runtime-config.js；scamadviser WHOIS |
| F-071 | dots3 API 细节官方文档逐字确认：上下文 512K=524,288 token 且为"输入+最大输出之和"上限；四模态输入（文本/图片/视频/音频）；认证头 `api-key`（OpenAI 与 AnthropIC 两端点均用它，**不是** Bearer、也**不是** x-api-key）；60 RPM/1,500,000 TPM 按单 Key 计；深度思考默认开启（chat_template_kwargs.enable_thinking:false / thinking.type:disabled 关闭）；Anthropic 需 anthropic-version: 2023-06-01 | dots.ai/platform/docs（前端分包原文） |
| F-072 | 【关键时效】OpenRouter 免费通道 2026-09-30 关闭属实：官方模型页顶部明示 **"Going away September 30, 2026"**，slug `dots-studio/dots-3-note-preview:free`，当前由 AtlasCloud 单一供应商免费托管；dots.ai 官方直连仅称限时/预览期免费，截止日未公布 | openrouter.ai/dots-studio/dots-3-note-preview:free；igetoken 09-07 |
| F-073 | 【勘误·接入路径】WorkBuddy 直连 dots3 可行（OpenAI 兼容自定义渠道，有实测）；**Trae 直连存在鉴权障碍**：Trae 自定义模型仅支持标准 Bearer、无自定义请求头入口，而 dots 强制 api-key 头，直连大概率 401；可行路径为经 OpenRouter/AtlasCloud 的 Bearer 通道（AtlasCloud 页面已把 Trae 列入支持客户端）或本地头转换。博文"可接入 Trae"方向不错但遗漏头转换坑 | docs.trae.com.cn/ide/models/；atlascloud.ai/zh/models/dots-studio/dots-3-note-prev-free；cnblogs dqtx33/22621257 |

### J. AMD 核验（F-074 ~ F-077）

| 编号 | 事实 | 权威信源 |
|------|------|----------|
| F-074 | AMD 官方品牌名为 **Radeon Cloud / Token Factory（BETA）**；入口 developer.amd.com.cn/radeon/modelapis（社区亦常用 /radeon/tokenfactory）均官方；OpenAI 端点 /radeon/api/v1/chat/completions（Bearer），Anthropic 端点 /radeon/api/v1/messages（用 **x-api-key** + anthropic-version 2023-06-01）；模型卡"served by the AMD GPU Cloud"；一账户一个 `rc-` 开头 Key 全模型通用；登录支持手机号/邮箱/GitHub/CSDN/ModelScope；免绑卡国内直连 | AMD 官方面板模型卡 JSON；CSDN 164341618（2026-09-04 截图） |
| F-075 | 【重大时效·名单已变】博文 4 款名单在 2026-09 初成立（freeaiapi 09-02、CSDN 09-04 均列同款 4 款，Vision-Exp 标 Limited Free）；**但 2026-09-16 核验时官方页已变为 5 款**：DeepSeek-V4-Flash-0731（Free）、Qwen3.8-Flash-Next（Free）、Qwen3.8-27B（Limited Free，新增）、MiniCPM5-2B（Free，**取代 1B**）、MinerU2.5-Pro（Limited Free，新增）；DeepSeek-V4-Flash-Vision-Exp 模型卡返回 `{"detail":"Model card not found"}`。背景：DeepSeek 官方 2026-09-10 下线 V4-Flash/Vision-Exp，旧名请求路由 V4.1-Flash | developer.amd.com.cn/radeon/modelapis；api-docs.deepseek.com/updates；freeaiapi.org |
| F-076 | 积分单价官方模型卡 JSON 逐字确认：`"Free to use. Points show relative usage—not a charge."`（单位 pts/1M tokens），输入 0.14/输出 0.28/缓存读 0.0028，与博文完全一致（原文为 em-dash）。重置节奏两二手口径：固定日切（Asia/Shanghai 每日重置，tools321）vs 每 24h 滚动发放 1 积分≈2500 万 token（igetoken）——以登录后控制台为准 | AMD 模型卡 token_factory.pricing |
| F-077 | 【勘误·额度传言】① "早期每天 $10"有二手源（美卡论坛；tools321 09-15 仍称参考值约 $10/天），但官方明确 points 不构成真实扣费，$ 数仅参考价折算；② "近期缩到约 $1/天"**查无任何证据且被相反口径覆盖，判传言级 ❌**；③ "200 万 token 耗约 5%"与官方单价粗算不符（混合负载约 0.3–0.6 pts≈日额度 30–60%，仅大量缓存命中才可能个位数百分比）❓单源失准；④ "并发>5 排队"为单源体感，第三方硬口径约 20–30 RPM、并发 8（⚠️大体相容无权威佐证）；稳定性字段 experimental、全站 BETA 标签 | uscardforum 523739；tools321；igetoken |

### K. 模型规格与全局价格表核验（F-078 ~ F-088）

| 编号 | 事实 | 权威信源 |
|------|------|----------|
| F-078 | 【勘误·MiniCPM5 型号混用】1B 与 2B **均存在且各自属实**：MiniCPM5-1B 为 2026-05-26 面壁智能联合清华/OpenBMB 端侧开源周发布，参数 1,080,632,832、上下文 131,072（128K）、Apache-2.0、INT4 权重 0.5GB（GGUF Q4_K_M 约 657MB）；MiniCPM5-2B 为 2026-09-07/08 开源（博文发布前 2 天），AA 指数 23、全球 4B 以下开源基座第一。博文模型卡（0.5GB/128K/手机浏览器）描述的是 **1B**，正文"4B 斩杀线 MiniCPM5-2B"描述的是 **2B**——两处自相矛盾来自型号混用 | huggingface.co/openbmb/MiniCPM5-1B README-cn；openbmb.cn/news；CSDN 164717441 |
| F-079 | 【勘误·上下文+时效】DeepSeek-V4-Flash-Vision-Exp 规格 305B 总参/13B 激活/MIT（2026-09-01 开源权重）/1M 上下文/单图计 384 视觉 token/无视觉加价均属实；但**文本 DeepSeek-V4-Flash 上下文官方同为 1M，博文"64K–128K"失实**；2026-09-10 官方公告：旧模型名 deepseek-v4-flash、deepseek-v4-flash-vision-exp"仍可调用，但对应模型已下线，请求将由 DeepSeek-V4.1-Flash 提供服务"（V4-Flash-0731 为 2026-07-31 快照版） | api-docs.deepseek.com/zh-cn/quick_start/pricing、/updates；vLLM recipes；explainx.ai |
| F-080 | Qwen3.8-Flash-Next 规格高度属实：2026-08-26 Qwen 团队开源权重，125B MoE/6B 激活，HF 卡片自述为"this experimental preview of the architecture that will underpin **Qwen4**"，原生 262K、YaRN 扩 1M，单一 API 处理文本/图像/视频；百炼 API 名 Qwen3.8-Flash（08-28 上线），长上下文/编程/图文理解；"接近 Qwen3.7-Plus"偏保守（第三方称其 SWE-bench Pro 多项超 Claude Opus 4.6 Max、训练成本 1/9）；"AMD 归 LLM 文本类"无百炼对应分类证据 ❓ | datacamp.com/ru/blog/qwen3-8-flash-next；aliyun.com/product/news/30535 |
| F-081 | 混元规格全部属实：Hy3 正式版 2026-07-06（Preview 04-23），295B 总参/21B 激活/256K/MoE/Apache-2.0，API 输入 ¥1/输出 ¥4；Hy4 preview 2026-08-28 发布并开源，770B/49B/1M/Apache-2.0，输入 ¥6/输出 ¥18，首发 WorkBuddy/CodeBuddy 国内国际版、元宝、ima | 腾讯云 cloud.tencent.com.cn/developer/news/4205517；新华网 20260828 |
| F-082 | 【勘误·Kimi 价格】Kimi K2.5 存在（2026-01 发布，1T 总参/32B 激活 MoE，原生多模态，上下文 262,144）；官方定价输入缓存命中 ¥0.70/未命中 ¥4.00/**输出 ¥21.00**/百万 token——博文"输出 6–12 元"失实（严重低估）；网页/App 免费属实，"每月 10 万 token 免费"无官方口径 ❓（现行新用户资源为代金券，如 15 元）；现役已迭代 K2.6/K2.7 Code/K3 | platform.kimi.com/docs/pricing/chat-k25 |
| F-083 | 【勘误·智谱价格边界】GLM-4.7-Flash 永久免费/无 token 上限/200K/约 30 并发/缓存免费属实（2026-01-20 发布）；GLM 5.x 现役 5/5.1/5.2/5.3/5.3-Flash/5V-Turbo，输出价 GLM-5.1 ¥24、GLM-5.2 ¥28、GLM-5.3 ¥26.6、5.3-Flash ¥2.66——博文"GLM-5.x 输出 8–28 元"边界标错（¥8 实为 GLM-4.7 在火山方舟档；5.x 旗舰 24–28）；新用户 2000 万 token 体验包属实但 **90 天有效且分包**（200 万通用+600 万 GLM-4.6V+1200 万 GLM-4.5-Air） | 36kr.com/p/3977443117635203；open.bigmodel.cn/console/trialcenter；ai.360.com |
| F-084 | 【勘误·豆包三项】doubao-seed-2.0-lite 官方口径**上下文 256K、最大输出 128K**（博文 128K 上下文系混淆）；刊例 ≤32k 档输入 ¥0.6/输出 ¥3.6，32–128k 档 ¥0.9/¥5.4，128–256k 档 ¥1.8/¥10.8（博文"输出 0.6–3.66"把输入价当输出、3.66 无对应数字）；免费额度为每模型**一次性 50 万 token 试用**（博文"100 万/月永久"两项属性均失实），另有授权采集协作奖励每日最高返 500 万、资源包 30 天有效；Doubao-1.5-pro 曾入 Trae ✅，Seed-1.6 曾入 Trae 无直接证据 ❓ | docs.volcengine.com 2374452、1099320、1391869；pricing 页 |
| F-085 | 【勘误·其余免费档】① 百度：ernie-speed-128k（0/0 元、128K、永久免费基线）与 ernie-lite-8k（0/0 元、**8K**）——博文"ERNIE-Lite 128K"张冠李戴，128K 免费的是 Speed；② Hunyuan-lite 免费属实（官方购买指南 PDF，社区称支持 256K）；③ Qwen-Turbo 官方输入约 ¥0.3/输出 ¥0.6（博文 0.5–1.0 区间含 0.6）；"7000 万 token"是**百炼全平台新用户礼包总和**（各模型约 100 万、90 天有效），非 turbo 独占、非永久 | InfoQ xie.infoq.cn 计费表；腾讯云产品 PDF 1729_105924；help.aliyun.com 3023262 |
| F-086 | 【勘误·DeepSeek 价格方向】博文"输出 3–9 元、官方已预告涨价"对应 2026-08-17 生效的峰谷价（空闲 ¥4.5/高峰 ¥9；火山方舟 8-21、8-28 跟进至 3/9）；但 **2026-09-09 官方公告 9-10 起 Flash 降价**（空闲输出 ¥4、缓存未命中 ¥1，高峰翻倍）并随 V4.1-Flash 上线——博文发布当天旧价区间即被 4–8 元取代，"预告涨价"方向反了；"新户 500 万/30 天"官方文档无载 ❓ | finance.sina.com.cn 2026-08-17；36kr 快讯 3975405867069960 |
| F-087 | 【勘误·Trae 清单滞后】博文四款内置（DeepSeek-V3.1/Kimi-K2/GLM-4.6/Qwen-3-Coder）均为往代；2026-09 现行内置为 Seed-Evolving/2.1 系列、GLM-5.3 系列、DeepSeek-V4.1-Flash/V4-Pro/V4-Flash、Kimi K3/K2.8-Preview/K2.7-Code、MiniMax-M3、Qwen3.8-Flash/3.8-Max/3.7-Plus（Qwen-3-Coder 早在 2026-02-26 被 Qwen-3-Coder-Next 替代）；Trae 已上线积分为核心的计费与付费会员，"基础版免费"部分成立但非纯免费时代 | docs.trae.cn/ide_models；forum.trae.cn/t/topic/218；docs.trae.cn/work_what-is-trae-work |
| F-088 | WorkBuddy 身份核验：腾讯云 CodeBuddy 团队（内部代号"小龙虾"）出品的全场景 AI 办公桌面工作台（workbuddy.cn），支持文档/表格/PPT/数据分析、可读授权文件夹，内置 Hy3/Hy4 并可添加 OpenAI 兼容自定义模型；TraeWork 为**字节跳动**产品（2026-06 由 TRAE SOLO 改名，Work/Code/Design 模式）——二者是腾讯 vs 字节同赛道头号竞品，非同一产品；博文将二者并列为例未混淆归属 | workbuddy.cn/docs/workbuddy/Overview；36kr.com/p/3958796219137161 |

**核验统计**：P0/关键声明共 31 项（Agnes 10、dots 7、AMD 5、模型与价格 9）——✅ 属实/逐字吻合 18 项；⚠️ 口径差异/单源/已演变 7 项；❌ 失实或传言 6 项（$1/天缩水、V4-Flash 64K-128K、Kimi 6-12 元、豆包 100 万/月永久+128K、ERNIE-Lite 128K、DeepSeek"预告涨价"方向）；其余为时效失效（AMD 名单 09-16 已变、dots 通道 09-30 关闭、Trae 清单换代）。

### L. V 阶段第二轮独立复核追加（F-089）

| 编号 | 事实 | 权威信源 |
|------|------|----------|
| F-089 | V 阶段第二轮独立子代理复核（与首轮三簇核验相互独立）补三项：① Agnes `/v1/messages`（Anthropic 兼容）官方 curl 示例鉴权头为 `x-api-key: YOUR_API_KEY` + `anthropic-version: 2023-06-01`，并非博文 F-009 所称"两站认证均为 Bearer"（第三方实测 Bearer 亦兼容，官方口径为 x-api-key）；② Agnes Token Plan 表中视频免费档实际限流 1 RPM（博文未提）；③ AMD Radeon Cloud 另提供 `POST /v1/messages/count_tokens` 端点 | wiki.agnes-ai.cn/zh-Hans/docs/agnes-30-flash、tokenplan；amd-aim.github.io/radeon-cloud-docs/zh-cn/api/overview |
