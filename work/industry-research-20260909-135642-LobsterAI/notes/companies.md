## 核心判断

网易有道以 LobsterAI 切入桌面级 Agent 赛道，定位为"国内大厂首个开源桌面级 Agent"，采用「个人端开源免费 + 企业端私有化交付」的双轨商业化路径 [1][2]。截至 2026-09-09，LobsterAI 开源仓库累计 3,882 次提交、71 个发布版本、422 个 Issue，最新版本 2026.9.4，8—9 月保持几乎每周发版的高频迭代节奏 [3][4]。其技术底座明确基于 OpenClaw 框架生态：Cowork 为产品会话层，OpenClaw 为底层运行时与网关，仓库内专设 `openclaw-extensions` 目录并在 `package.json` 中锁定 OpenClaw 版本 [3]。有道正从教育科技公司向 AI 科技企业转型，CEO 周枫将 AI 产品划分为"聊天 AI—思考 AI—行动 AI"三代际，全力布局第三代"行动的 AI"；2025 年有道 AI 订阅销售额接近 4 亿元，验证了"能力 + 订阅"模式的付费意愿 [5]。

桌面级 Agent 竞争格局已形成"大厂闭源生态绑定 + 开源框架生态"双线并行结构。国内闭源阵营以豆包专业版（字节）、WorkBuddy（腾讯）、QoderWork（阿里）为代表，均绑定自有模型与办公生态、采用积分或订阅计费 [6]；海外闭源阵营以 Manus、ChatGPT Agent 为代表，走通用 Agent 路线。LobsterAI 的差异化在于 100% 代码开源、支持 10+ 主流模型与本地 Ollama 部署、深度适配 Windows 生态，并依托有道 OCR、翻译、子曰大模型等能力底座 [1][2]。

## 样本对比

| 产品 | 厂商 | 开源属性 | 地域 | 核心定位 | 上线/发布时间 | 桌面与执行能力 | 模型开放度 |
|---|---|---|---|---|---|---|---|
| LobsterAI | 网易有道 | 开源（MIT） | 国内 | 全场景办公助手 Agent，国内大厂首个开源桌面级 Agent | 2026-02-18 开源 | 28 内置技能、MCP、多 Agent 协作、IM 远程指挥（微信/企微/钉钉/飞书等）、本地 SQLite 记忆、沙箱执行 | 支持 10+ 主流模型及本地 Ollama |
| 豆包专业版 | 字节跳动 | 闭源 | 国内 | 办公任务模式，豆包生产力升级包 | 2026-06-24 上线 | Office 套件、多模态（Seedream/Seedance）、语音通话 + 共享屏幕 | 仅豆包自家模型 |
| WorkBuddy | 腾讯云 | 闭源 | 国内 | 全场景桌面 AI 智能体 | 2026-03-09 上线，06-05 企业版 | 腾讯生态全家桶、SkillHub、IM 全家桶 | 腾讯系模型 |
| QoderWork | 阿里 | 闭源 | 国内 | Agent 能力从代码领域扩展到日常工作 | 2026-01-30 发布，03-03 开放 | 钉钉集成、技能市场 + 15 套专家套件、Mobile 端 | 主流国产模型 |
| Manus | Manus | 闭源 | 海外 | 通用 AI Agent，云端 + 本地混合 | 不详 | 异步任务、多工具链、My Computer 桌面集成 | 多模型协作 |
| ChatGPT Agent | OpenAI | 闭源 | 海外 | 端到端通用 Agent | 不详 | 内化工具使用、操作过程可视化 | OpenAI 模型 |

> 说明：商业化计费口径不一（个人版积分、企业版席位、美元订阅、积分包等），不作同口径数值比较；模型开放度为定性分类。LobsterAI 数据来自官网与 GitHub 仓库 [1][2][3]；豆包专业版、WorkBuddy、QoderWork 数据来自横评实测 [6]；Manus、ChatGPT Agent 为搜索发现的具名来源事实，用于补足海外样本。

## 企业简析

### 网易有道 / LobsterAI

**行业位置**：国内大厂中首个 100% 开源桌面级 Agent 的厂商，在"百虾大战"中以开源透明锚定差异化定位 [1][5]。有道从教育科技公司向 AI 科技企业转型，AI 产品矩阵包括 LobsterAI、有道同传 Agent、有道宝库 Agent 等 [5]。

**产品与路线**：LobsterAI 定位 7×24 小时全场景个人助理 Agent，可连接本地文件、终端、浏览器与项目，支持应用开发、数据分析、定时任务、调研报告、网页操作、文档处理、长期记忆七大场景 [1]。架构上分为 Cowork（产品/会话层）与 OpenClaw（运行时/网关层），保持本地持久化、权限、UI 状态、产物、记忆与 IM 绑定在桌面端，由 OpenClaw 负责 Agent 执行 [3]。

**商业化阶段**：个人端代码开源、客户端免费，模型费用由用户直接支付给服务商，并辅以积分活动（如 2026 年 8 月面向网易用户派发 5000 积分）[1][5]；企业端为"全栈式企业级 AI 智能体操作系统"，支持全流程私有化部署、低代码分钟级编排数字员工，面向客服、HR、法务、运维等场景，宣称 100+ 企业客户、99.9% 系统可用性 [2]。有道整体 2025 年 AI 订阅销售额接近 4 亿元 [5]。

**关键能力**：28 个内置技能（文档处理、数据分析、PPT、PDF、Remotion 视频、浏览器自动化、邮件等）、MCP 协议支持、多 Agent 协作、Sites 站点发布、IM 远程指挥（微信/企微/钉钉/飞书/Telegram/Discord 等）、本地 SQLite 记忆、QEMU + Alpine Linux 沙箱执行；深度融合有道 OCR、翻译、子曰大模型 [1][2][3]。

### 字节跳动 / 豆包专业版

**行业位置**：字节"飞书 + 豆包"整合后推出的桌面 Agent，背靠豆包 2.1 Pro 模型与 Seedream/Seedance 多模态能力 [6]。

**产品与路线**：核心为"办公任务模式"——操作本地电脑、使用浏览器、调用 Skills、定时任务，内置 Office 套件，是豆包的生产力升级包 [6]。

**商业化阶段**：三档付费——标准 68 元/月、加强 200 元/月、高级 500 元/月，按 token、生图生视频次数混合计费 [6]。

**关键能力**：本地电脑操控丝滑、信息搜索并行交叉验证、多模态一家独秀（Seedream 5.0 Lite 图像、Seedance 视频）、独家语音通话 + 共享屏幕；但 IM 生态较弱（仅飞书）、不支持外接模型 [6]。

### 腾讯 / WorkBuddy

**行业位置**：腾讯云出品的全场景桌面 AI 智能体，与 CodeBuddy 共享账号与积分，三个月迭代 43 个版本，迭代速度突出 [6]。

**产品与路线**：主打腾讯生态适配，定位全场景桌面 AI 智能体；2026 年 6 月发布企业版 [6]。

**商业化阶段**：积分制计费，与 CodeBuddy 共享同一套账号与积分；企业旗舰版每月 2000 积分 [6]。

**关键能力**：IM 生态最全（微信小程序/微信/企微/钉钉/飞书）、SkillHub 腾讯全家桶连接器、可生成 HTML 调研报告与 5 秒视频；但默认情况下浏览器操控倾向写代码而非 Computer Use，效率偏低 [6]。

### 阿里 / QoderWork

**行业位置**：阿里将 Qoder 的 Agent 能力从代码领域扩展到日常工作场景的桌面产品 [6]。

**产品与路线**：以任务为中心组织领域工作流，深度集成钉钉；另有 Mobile 端 [6]。

**商业化阶段**：具体定价未在公开横评中披露 [6]。

**关键能力**：钉钉/微信/飞书三大 IM 打通、带下载量排名的技能市场 + 15 套专家套件、任务监控面板展示待办进度与调用技能；但暂不支持文生视频、信息时效性偶有滞后 [6]。

### Manus（海外）

**行业位置**：海外通用 AI Agent 代表，以云端 + 本地混合架构提供 7×24 小时可用性与桌面深度集成。

**产品与路线**：Manus My Computer 将云端 Agent 能力与本地桌面应用安全集成，授予特定本地文件夹访问权限后，可从移动端发起任务并在本地机器上执行。

**关键能力**：异步长流程任务、多工具链串联、My Computer 桌面集成；采用蒙特卡洛树搜索（MCTS）拆解任务的多模型协作架构。

### OpenAI / ChatGPT Agent（海外）

**行业位置**：OpenAI 推出的端到端通用 Agent，代表"内化工具使用"的技术路线。

**产品与路线**：将 Operator 与 Deep Research 合并开发，通过强化学习内化工具使用能力，形成单一代理模型，低通信开销、任务连贯、响应快。

**关键能力**：自主选择工具（文本/可视化浏览器、终端、API）、实时展示操作过程、支持任务中断与动态调整；关键操作需人工授权。

## LobsterAI 开源仓库活跃度与版本演进

LobsterAI 于 2026 年 2 月 18 日首次开源（Initial open-source release），采用 MIT 许可证，由 NetEase Youdao 维护 [3]。截至 2026-09-09，仓库累计 3,882 次提交、422 个 Issue、191 个开放 Pull Request、71 个 Release，最新版本为 2026.9.4（2026-09-04 发布）[3][4]。版本号从内部 v0.1.16 演进为日期制 `YYYY.M.D`，2026 年 8 月单月发布 8 个版本（8.7、8.11、8.14、8.18、8.21、8.25、8.26、8.28），9 月已发布 9.3、9.4，呈现高频迭代 [4]。

关键演进节点：4 月 17 日版本将 OpenClaw 升级至 v2024.4.8 [4]；8 月 18 日起集成 DeepSeek Harness（dsh）运行时，引入新推理引擎 [4]；8 月 25 日上线 Library 资料库功能，增强跨平台产物管理 [4]；9 月 4 日恢复交互式内置浏览器并完善订阅恢复引导 [4]。仓库结构包含 `SKILLs/`、`openclaw-extensions/`、`src/`、`tests/`、`docs/` 等目录，工程化配置完整（Prettier、ESLint v9、Husky、commitlint）[3]。

```visual
type: timeline
title: LobsterAI 开源以来关键版本演进
source: [3][4]
item: 2026-02-18 | 首次开源（Initial open-source release） | 国内大厂首个开源桌面级 Agent，MIT 许可证
item: 2026-04-17 | 升级 OpenClaw 至 v2024.4.8 | 底层运行时跟随 OpenClaw 生态迭代
item: 2026-08-18 | 集成 DeepSeek Harness（dsh）运行时 | 引入新推理引擎，支持 dsh 进程启动器
item: 2026-08-25 | 上线 Library 资料库功能 | 增强跨平台缩略图与本地产物生命周期管理
item: 2026-09-04 | 2026.9.4（最新版） | 恢复交互式内置浏览器，完善订阅恢复引导
```

## OpenClaw 生态关系

LobsterAI 与 OpenClaw 是"产品层 + 运行时层"的明确分工关系，而非简单 fork [1][3]。官网定位为"基于 openclaw 框架生态" [1]；GitHub README 明确说明："Cowork is the LobsterAI product/session layer. OpenClaw is the runtime and gateway underneath it"——这种分层使 LobsterAI 将本地持久化、权限、UI 状态、产物、Agent、记忆与 IM 绑定保留在桌面应用中，而由 OpenClaw 负责 Agent 执行 [3]。

工程层面，LobsterAI 仓库设有 `openclaw-extensions` 目录，并通过 `openclawEngineManager`、`openclawConfigSync`、`openclawRuntimeAdapter`、`coworkEngineRouter` 等模块将 LobsterAI 状态翻译为 OpenClaw 运行时行为；`package.json` 中锁定 OpenClaw 版本与第三方插件列表 [3]。LobsterAI 开源后获得 OpenClaw 创始人 Peter Steinberger 的公开关注与肯定 [5]。2026 年 8 月 31 日 OpenClaw 发布 2.0 版本（v2026.8.1），由 933 位贡献者完成、超 16,000 个 PR，LobsterAI 作为基于 OpenClaw 的桌面产品持续跟进上游演进。

```visual
type: matrix
title: 桌面级 Agent 竞争格局定位（开源属性 × 地域）
source: [1][3][6]
item: 开源 × 国内 | LobsterAI | 基于 OpenClaw，100% 代码开源，主打 Windows 适配与私有化部署
item: 闭源 × 国内 | 豆包专业版 / WorkBuddy / QoderWork | 大厂自有模型 + 办公生态绑定，积分或订阅计费
item: 闭源 × 海外 | Manus / ChatGPT Agent | 通用 Agent 路线，云端或云端 + 本地混合架构
```

## 参考资料

1. [LobsterAI 有道龙虾官网](https://lobsterai.youdao.com/) — 网易有道，日期不详
2. [LobsterAI 企业版](https://ai.youdao.com/new/lobsterai) — 网易有道智云，日期不详
3. [netease-youdao/LobsterAI GitHub 仓库](https://github.com/netease-youdao/LobsterAI/) — NetEase Youdao，2026-09-04（最新提交）
4. [LobsterAI Releases](https://github.com/netease-youdao/LobsterAI/releases) — NetEase Youdao，2026-09-04（最新版本）
5. [「OpenClaw之父点赞」终结百虾大战？一场升级版的AI原生革命上演](https://post.m.smzdm.com/p/a035rqdr/) — 新智元（引自知乎），2026-04-07
6. [豆包、WorkBuddy、QoderWork怎么选？我用8个真实办公任务把三家桌面Agent测明白了](https://m.huxiu.com/article/4875072.html?type=text) — 夕小瑶科技说（虎嗅转载），2026-07-14
