---
okf_version: "0.2"
type: spec
title: "WorkBuddy 沙箱公网端点博文→OKF 知识包转化规划"
description: "将微信公众号博文《你敢相信吗？WorkBuddy 白送你一台「免费服务器」》转化为 OKF 知识包，核验沙箱公网 HTTPS、临时服务、生命周期与生产边界。"
tags: [okf-bundle, blog-article, workbuddy, cloudstudio, sandbox, https, public-endpoint, temporary-deployment]
generated: { by: "seven-concepts-cmd+blog-article-to-okf-wiki", at: "2026-09-16T21:50:00+08:00" }
---

# WorkBuddy 沙箱公网端点博文 → OKF 知识包转化规划

> 方法论链路：七概念场景 4（知识沉淀）R→I→E→V→C，由 blog-article-to-okf-wiki 七阶段工作流执行。用户未要求提交，C 阶段仅产出原子提交建议。

## 1. 内容敏感度预检

| 项目 | 结论 | 依据 |
|------|------|------|
| 来源 | 微信公众号公开文章 | https://mp.weixin.qq.com/s/bMRwxrGDltjsoo-HneHi2Q |
| 公众号 / 作者 | AI工具实测派 / wrokbuddy | 原创，2026-08-28 19:53，发布地四川 |
| 访问控制 | 无 | `/s/<id>` 公开文章格式，无 share?code=/token=/邀请码参数；浏览器提取无验证码、登录或付费墙 |
| 敏感度级别 | **公开内容** | 产品使用技巧类公开博文，无个人隐私与商业秘密 |
| 工作流模式 | **标准工作流** | spec 在 `.trae/specs/okf-wiki-ecosystem/`，bundle 在 `projects/awesome-okf-xs/doc/bundles/` |
| 信源距离预判 | **第三方实操/技巧文**，含平台内部机制推断 | 非腾讯官方文档；作者给出操作提示与场景，但未提供版本、实测输入输出与平台文档链接 |

## 2. 骨架判定（操作可复现性两问）

| 问题 | 回答 | 理由 |
|------|------|------|
| Q1：博文中是否有读者可照做的安装/配置/代码/调用/实测流程？ | **弱是** | 仅给出“起服务→找域名→打开 HTTPS”的粗流程与通用 `nohup`/心跳命令，没有可直接运行的服务端示例命令、环境版本或端口发现步骤 |
| Q2：这些流程是否经作者实测、具备可复现性（有版本、有输入输出、有步骤顺序）？ | **否** | 无 WorkBuddy/CloudStudio 版本、无具体服务命令、无请求/响应输出、无官方 UI 路径截图文字；域名后缀在 2026-09-15 网易转载稿中已变为 `app.workbuddy.host` |

**判定：任一问为“否” → 技术综述/操作提示骨架，不设 examples/**。操作建议写入概念文档，但不伪装成经完整实测的官方教程。

**骨架**：

```text
jishu/ai/tencent/workbuddy-sandbox-public-endpoint/
├── index.md
├── log.md
├── concepts/
│   ├── index.md
│   ├── 00-public-endpoint-mechanism.md       # 公网端点事实、链路、证据与产品形态边界
│   ├── 01-temporary-service-use-cases.md      # 临时演示/Webhook/静态页/Agent API 场景适配
│   └── 02-lifecycle-and-operations.md         # 会话生命周期、保活、安全与生产替代
└── references/
    ├── index.md
    ├── article-source.md                      # 博文事实双份登记
    └── verification.md                        # P0 核验、实测响应头与勘误
```

## 3. 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/tencent/workbuddy-sandbox-public-endpoint/`（选定） | ✅ | 主线实体是腾讯 WorkBuddy/CodeBuddy/CloudStudio 运行环境；腾讯分组已有 `codebuddy` 与 `octop`，且 codebuddy bundle 已收录 WorkBuddy 在线助手 |
| `jishu/ai/ai-agent/` | ❌ | 该组聚焦 Agent 运行时框架与源码；本文是平台临时公网端点使用技巧，不是 Agent 框架 |
| `jishu/comm/` 或 `jishu/containers/` | ❌ | 虽涉及 HTTPS/反向代理/沙箱，但读者决策入口是 WorkBuddy 产品功能，不是通用通信协议或容器引擎 |
| 新建分组 | ❌ | 单篇博文新建分组违反最小变更原则 |

**最终路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/tencent/workbuddy-sandbox-public-endpoint/`

## 4. 时效性

| 项目 | 结论 |
|------|------|
| 博文发布时间 | 2026-08-28 |
| 核验时间 | 2026-09-16 |
| `stale_after` | **2026-11-30**（平台域名、网关与会话回收策略变化快） |
| 高时效字段 | 默认域名后缀、端口范围、限流策略、会话休眠/回收规则、CloudStudio/WMA 产品边界 |
| 已知边界 | 博文的 `sh1.agentos-app.net` 与 2026-09-15 转载稿的 `app.workbuddy.host` 已出现后缀差异；响应头可观测网关为 `CloudStudio Gateway`，CLB 与 `sandbox-proxy` 内部链路未获官方文档证实 |

## 5. P0 核验摘要

| 核验对象 | 权威/实证来源 | 结论 |
|----------|---------------|------|
| WorkBuddy/WMA 产品身份 | 腾讯云 WorkBuddy Enterprise 产品概述、WMA 产品介绍 | ✅ 产品矩阵与云端沙箱 Runtime 存在 |
| Runtime 是否具备端口转发 | 腾讯云 WMA 产品介绍 | ✅ 官方列明“端口转发”为一体化 Agent Runtime 能力 |
| `*.agentos-app.net` 公网 HTTPS 页面是否存在 | 3 个第三方案例 URL 的 WebFetch + `curl -I` | ✅ 2026-09-16 均可经 HTTPS 访问，HTTP 200，`Server: CloudStudio Gateway` |
| 博文所称 CLB TLS 终止 + sandbox-proxy | 公开检索与响应头 | ⚠️ 未找到官方公开文档；响应头只证明边缘网关为 CloudStudio Gateway，内部 CLB/proxy 链路仍按博文单源处理 |
| 域名稳定性 | 2026-09-15 网易转载稿与实测 | ⚠️ 转载稿使用 `<sandbox-id>.app.workbuddy.host`；该域名 HEAD 返回 501 但网关可达，说明后缀/环境可能已迁移 |
| “会话在、服务在”与 7×24 | 腾讯云 WMA 官方文档 | ⚠️ WMA 支持 7×24、自动休眠/毫秒级恢复；博文描述更像临时预览沙箱，不能与企业托管 Runtime 混同 |
| Webhook、生产服务、自定义域名等用途 | 博文 + 官方资料 | ⚠️ 临时 Demo/静态页可信；支付/GitHub Webhook 等生产用途受平台限流、端口、暴露策略约束 |

**状态判定**：高层能力“沙箱/部署环境可提供公网 HTTPS 端点”获得官方端口转发能力与实时域名实证支持；具体域名后缀和内部代理架构存在未证实/漂移项。因此 bundle 使用 `status: stable`，但在首页与正文显著标注核验边界，不将博文内部机制写成官方定论。

## 6. 三层知识拆分

| 博文内容层 | 映射篇目 | F 编号支撑 |
|-----------|---------|-----------|
| 事实层：平台、域名、HTTPS、代理链路、响应头 | `concepts/00-public-endpoint-mechanism.md` | F-005~F-011、F-028~F-038 |
| 方法层：六类适用场景、临时演示与长期基础设施分界 | `concepts/01-temporary-service-use-cases.md` | F-012~F-014、F-019~F-022、F-039 |
| 操作/生命周期层：启动、保活、风险提示、可复制提示词的安全改写 | `concepts/02-lifecycle-and-operations.md` | F-011、F-015~F-023、F-030、F-036~F-039 |

## 7. 验收标准

- bundle 9 个文件齐备，每个 index.md 含隐藏 toctree，条目逐一对应磁盘文件。
- 全部具体声明携带 F 编号；博文单源内容与官方/实测内容明确分层。
- `article-source.md` 与本 spec `facts.md` 的 F 编号集合均为 F-001~F-039，连续无跳号。
- 首页显著提示：`sh1.agentos-app.net`/CLB/sandbox-proxy 为博文口径；实时实证网关为 `CloudStudio Gateway`，域名后缀存在漂移。
- 接入腾讯分组、AI 分组和总索引；本束使 tencent 由 4 束增至 5 束。根索引按 2026-09-16 当前工作树地面真值对账（当时含并行会话其他新增束，总计 555 束），提交前需再次运行计数脚本确认。
- V 阶段完成四视角审查、UTF-8、本束 toctree、链接、F 编号、frontmatter 检查；全库计数/toctree 需在并行会话新增束索引收敛后复跑，若 invoke gates 不可用则维持底层脚本手动等效验证并在 log.md 注明。
