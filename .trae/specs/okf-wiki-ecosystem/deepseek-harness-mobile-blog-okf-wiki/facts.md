---
title: "facts：DSH Mobile 博文事实采集"
type: spec-facts
description: 腾讯技术工程《我用腾讯 Kuikly，把 DeepSeek Harness 装进了口袋》F-001~F-045 完整事实登记（含 P0 核验结论）
generated: { by: "process:blog-article-to-okf-bundle", at: "2026-09-09T00:00:00+08:00" }
---

# 事实采集清单（facts.md）

> 主信源：腾讯技术工程公众号，2026-09-08 17:57 发布，作者腾讯程序员 yuki。
> URL：https://mp.weixin.qq.com/s/THtcdws01AV_Q3fe2pYRlQ
>
> F-001~F-045 共 45 条。P0 核验 14 项：11✅ / 2⚠️ / 0❌。

## 元信息（F-001）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-001 | 标题《我用腾讯 Kuikly，把 DeepSeek Harness 装进了口袋》；公众号"腾讯技术工程"；作者腾讯程序员 yuki；2026-09-08 17:57 发布 | 元信息 | — |

## 项目定位与动机（F-002~F-005）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-002 | DSH（DeepSeek Harness）跑一个任务常需几分钟甚至更久，中间会停下等人处理审批、补充信息或确认方向；人离开电脑任务可能卡住 | 动机 | — |
| F-003 | 作者用腾讯 Kuikly 框架开发 DSH Mobile——一套 Kotlin 代码覆盖 Android/iOS/鸿蒙的跨端原生 App，按 DSH 官方 Host 协议与电脑上的 DeepSeek Harness 对话 | 项目定位 | ✅ |
| F-004 | 设计意图：让手机接住"短而频繁的交互"（通勤/开会/排队时查看进度、处理审批、回答追问），Agent 循环/工具执行/插件仍在电脑上运行 | 作者观点 | — |
| F-005 | 弃用 WebView 方案的理由：App 需维持 WebSocket 长连接、处理锁屏/切后台/网络切换、重连后补遗漏事件，扫码/SSH 隧道/本地缓存需要平台能力 → 原生客户端更合适 | 架构决策 | — |

## Kuikly 框架与选型（F-006~F-012）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-006 | Kuikly 是腾讯开源高性能跨端框架，基于 Kotlin Multiplatform，覆盖 Android/iOS/HarmonyOS/H5/微信小程序/Mac 六大平台，支撑业务日活用户超 5 亿 | 框架事实 | ✅/⚠️ |
| F-007 | 选 Kuikly 最直接原因：开发快——组件市场提供常用能力，找到合适组件加依赖即可在共享代码中使用，无需三端各写一套 | 作者观点 | — |
| F-008 | 使用组件 KuiklyMarkdown（坐标 com.tencent.kuiklybase:KuiklyMarkdown:1.0.6-2.1.21）：基于 intellij-markdown 解析输出 Block 列表、提供流式渲染状态；16ms 合帧、未闭合代码块补闭合标记 | 组件 | ✅ |
| F-009 | 使用组件 KuiklyWebview（坐标 com.tencent.kuiklybase:KuiklyWebview:1.0.1-2.0.21）：App 内打开 Markdown 链接与外部页面，监听加载事件 | 组件 | ⚠️ |
| F-010 | 组件市场还有 SQLite/相机/图片选择/录音/定位/蓝牙/MMKV 等常用能力（项目未全部接入） | 组件生态 | — |
| F-011 | KuiklyUI-AI 提供 Kuikly DSL 与 Kuikly Compose DSL 开发规则 + 组件使用/Module 扩展/网络请求/响应式状态/协程/多端资源等 Skills，可交给 CodeBuddy/Cursor/Claude Code 使用 | 开发配套 | ✅ |
| F-012 | 开发分工：协议模型/状态机/重复页面交给 Agent 完成，作者主要检查交互、平台差异与真机表现 | 作者工作流 | — |

## 原生桥接架构（F-013~F-015）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-013 | commonMain 定义统一 Module 接口（连接/发消息/收消息/断开），Android/iOS/鸿蒙分别接系统实现；以 WebSocket 为例三端底层为 OkHttp/NSURLSession/NetworkKit，上层统一 DshWebSocketModule | 架构 | — |
| F-014 | SSH 隧道、扫码配对采用同一套"差异下沉到原生层"的拆分方式 | 架构 | — |
| F-015 | 项目规模：约 1.3 万行 commonMain 共享 Kotlin；Android/iOS/鸿蒙宿主各三四千行（系统接入+平台工程配置） | 规模数据 | — |

## DSH Host 协议直连（F-016~F-023）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-016 | DSH Mobile 不加中间层，直接使用官方 Web 前端背后的 Host 协议（同一套方法/事件） | 架构决策 | — |
| F-017 | DSH 是基于 Cordis 的插件化 Agent 运行时；与移动端连接相关简化为三层：core/session+agent-loop+tools → host/apiproxy → client/connection | 架构 | ✅ |
| F-018 | client/connection 接本机 3080 端口，对外提供 HTTP /api/...、WebSocket /api/events.mux 与 /api/events.host | 协议 | ✅ |
| F-019 | 发消息对应 session.prompt：POST /api/session.prompt；会话列表/历史/工作区/模型/Goal/设置同走 RPC 通道 | 协议 | ✅ |
| F-020 | dsh-v0.1.1-rc.2 的 RPC 方法表有 52 个方法；完整方法表见 rpc-map.ts；DSH 快速迭代，应锁定已验证 tag | 协议 | ⚠️ |
| F-021 | 两条只下行 WebSocket：events.mux（会话内：模型输出/工具调用/审批/提问/消息队列/后台任务）、events.host（全局：会话增删/运行状态/工作区变更/Host 级错误） | 协议 | ✅ |
| F-022 | session/queue 与 session/jobs 推送完整快照（非增量），不进入会话日志，重连不能靠事件回放恢复，收到新快照直接覆盖本地状态 | 协议细节 | — |
| F-023 | session/projection.value 与 host/remote-event.args 为宽类型；App 需保留未知字段，解析失败时降级而非中断事件流 | 协议细节 | — |

## 断线重连与状态机（F-024~F-026）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-024 | 重连恢复顺序：①重建 SSH/Relay 隧道 ②用上次序号补回遗漏 session/event ③请求 session.history 重对齐 ④用最新快照覆盖 queue/jobs | 协议 | — |
| F-025 | 每次连接带世代号：断开后旧连接迟到的 RPC 响应会被丢弃，不能写进新会话状态 | 协议 | — |
| F-026 | 断线期间 Agent 仍在电脑运行则重连后重新订阅任务（非重发 Prompt）——重连是恢复观察与控制，不是重新执行；状态机位于共享层，三端同一补齐顺序与失效规则 | 架构 | — |

## 两种远程连接方式与安全（F-027~F-031）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-027 | DSH 默认监听 127.0.0.1:3080（应保留默认——能访问该端口的客户端可能获得高本机操作权限） | 安全 | ✅ |
| F-028 | SSH 模式：手机建立本地端口转发映射到电脑 127.0.0.1:3080，HTTP RPC+两条 WS 走隧道；不改 DSH 认证逻辑，认证在 SSH 层 | 连接方式 | — |
| F-029 | 扫码模式：作者开发 dsh-scan-remote 插件，DSH Settings 出现 Remote Access 页；电脑生成二维码手机扫码配对；两端主动连 Relay，sealed-tunnel-v1 转发流量 | 连接方式 | ✅ |
| F-030 | Relay 无需直接访问 3080，电脑不把 DSH 开放到局域网/公网；二维码主密钥在 URL fragment（不发给 Relay）；隧道数据密封 | 安全 | ✅ |
| F-031 | 定位：DSH Mobile 适合短/轻/高频交互；长 Prompt、大段代码 Diff、持续思考仍适合桌面——是远程控制面板而非把 IDE 搬上手机 | 作者观点 | — |

## 行业参照与路线图（F-032~F-035）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-032 | Cursor iOS 应用可启动云端 Agent、通过 Remote Control 操作电脑上的 Agent | 行业参照 | ✅ |
| F-033 | Claude Code Remote Control 支持从手机接续本机会话 | 行业参照 | ✅ |
| F-034 | 下一步：补输入能力（session.prompt 已支持图片内容数组 → 加图片上传/语音输入）；通知需电脑端配合；现阶段不私自增加官方协议之外的 RPC | 路线图 | — |
| F-035 | 客户端不永久绑定 DSH：列会话/下发消息/接收事件/处理审批等能力已放共享层，接其他 Agent 服务主要新增协议适配器 | 作者观点 | — |

## 快速上手与部署（F-036~F-041）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-036 | 本地扫码连接四步：①启动 Relay ②安装插件并启动 DSH ③手机安装 DSH Mobile ④扫描 Remote Access 二维码（同可信 Wi-Fi） | 步骤 | — |
| F-037 | Relay 启动命令：git clone https://github.com/yukiykchen/dsh-scan-remote.git → cd relay → cp .env.example .env → npm ci → npm run build → HOST=0.0.0.0 PORT=8787 npm start | 命令 | ✅ |
| F-038 | 插件安装：npx @deepseek-ai/dsh plugin --profile web add "github:yukiykchen/dsh-scan-remote#v0.0.1"；export PUBLIC_RELAY_URL=http://192.168.1.10:8787；npx @deepseek-ai/dsh web | 命令 | ✅ |
| F-039 | App 安装：Android 从 releases 下载 APK；iOS 用 Xcode 打开 iosApp/iosApp.xcworkspace 配签名；鸿蒙用 DevEco Studio 打开 ohosApp；代码仓库 deepseek-harness-mobile | 步骤 | ✅ |
| F-040 | 扫码超时排障三查：手机能否访问 http://电脑局域网地址:8787/health；PUBLIC_RELAY_URL 是否为当前地址；Relay 是否监听手机可达接口且防火墙放行 8787 | 排障 | — |
| F-041 | 腾讯云轻量应用服务器部署：Harness 持续运行在云端，手机只负责连接/交互/渲染，长任务不依赖电脑在线 | 部署场景 | — |

## 扩展开发入口（F-042~F-045）

| 编号 | 事实 | 分类 | 核验 |
|------|------|------|------|
| F-042 | 新增 Host 方法：DshHostProtocol.kt 增加定义复用 RPC 通道，不涉新系统能力则三端无需改原生代码 | 扩展 | — |
| F-043 | 新增原生能力：commonMain 定义 Module + 三端实现（Android KuiklyRenderActivity 导出 / iOS KuiklyExpand/Modules / 鸿蒙 kuikly/modules）；新增页面用 @Page 注解 + KSP 路由 | 扩展 | — |
| F-044 | DSH 新事件上手机：写 DSH 插件监听事件并经 host/remote-event 转发（需 Host 侧允许转发 + App 端宽类型容错）；注册新官方 RPC/替换传输层需改 DSH 本体 | 扩展 | — |
| F-045 | DSH 处于 developer preview，协议/包结构可能破坏性变化；本文方法数/目录/事件对应 dsh-v0.1.1-rc.2 | 时效声明 | ✅ |

## P0 核验总览（详见 bundle references/verification.md）

- 11 ✅：A1 Kuikly 六平台、A2 日活超 5 亿（官方口径）、A4 KuiklyUI-AI、B1 DSH 框架/preview、B2 3080+events.mux/host、B4 官方仓库与最新 tag、C1 dsh-scan-remote、C2 deepseek-harness-mobile、D1 Cursor iOS Remote Control、D2 Claude Code Remote Control
- 2 ⚠️：A3 KuiklyWebview 版本（博文 1.0.1-2.0.21 vs 当前 README 1.0.2-2.0.21）、B3 "52 个方法/rpc-map.ts" 仅博文单源（session.prompt 端点已独立证实）
- 0 ❌：无源文硬错误
