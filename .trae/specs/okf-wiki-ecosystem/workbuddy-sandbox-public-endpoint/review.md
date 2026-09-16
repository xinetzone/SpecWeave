---
okf_version: "0.2"
type: review
title: "WorkBuddy 沙箱公网端点 V 阶段对抗审查"
generated: { by: "seven-concepts-cmd:V", at: "2026-09-16T22:50:00+08:00" }
status: stable
source:
  - ./facts.md
  - ./insights.md
---

# V 阶段对抗审查记录

## 1. 四视角结论

| 视角 | 审查重点 | 结论 |
|------|----------|------|
| 魔鬼代言人 | 是否把 CLB、sandbox-proxy、固定 sh1 域名写成官方事实 | 通过。能力层、观测层、博文内部实现层已分开；未证实内容均标 ⚠️ |
| 新人视角 | 是否解释产品形态、域名漂移和非示例教程定位 | 通过。区分临时预览、CloudStudio、Remote Control、WMA；补充 CLB 中文含义 |
| 老板视角 | 临时演示、Webhook、生产服务、安全与成本边界是否清楚 | 通过。Demo/静态页可用，Webhook 仅短时联调，生产走 WMA/云服务器/容器 |
| 未来视角 | 平台域名、网关和生命周期是否会过期 | 通过。`stale_after=2026-11-30`，并留存实时响应头证据快照与复核要求 |

## 2. 独立审查发现与修复

独立子代理审查结果：**P0 = 0，P1 = 2，P2 = 7**。

| 级别 | 问题 | 处理 |
|------|------|------|
| P1 | 5 篇正文/信源 frontmatter 缺 `verified` | 已为 3 篇 Concept 和 2 篇 Reference 补 `process:seven-concepts-v` |
| P1 | article-source.md 的实时实证 URL 未列入 sources | 已补 3 个 live `*.agentos-app.net` URL |
| P2 | F-022 被用于证明保留地址/TCP/UDP 等完整隧道差异，引用越界 | 已改写为“自定义域名见 F-022，其余为编者推导” |
| P2 | “地域/队列前缀”无证据 | 已改为“不同前缀（部分疑似地域标识）” |
| P2 | CLB 首次出现未展开 | 已补“云负载均衡 Cloud Load Balancer” |
| P2 | 第三方实时 URL 未来可能失效 | verification.md 已增加证据快照说明和复核重测要求 |
| P2 | 根 index 的全角括号锚点可能有构建差异 | 已改为不带锚点的普通链接 |
| P2 | tasks/log 未闭环 | 已更新任务清单并在 bundle log 记录门禁 |
| P2 | F-005 双份符号不一致 | spec facts.md 已统一为 ✅/⚠️ |

跨束预存问题（其他并行会话的未跟踪 WIP）曾导致全库 gate 短暂失败；最终复跑时已由当前工作树收敛，不归属本束。

## 3. 机械门禁

| 检查项 | 结果 | 证据 |
|--------|------|------|
| 双份 F 编号 | ✅ 通过 | spec `facts.md` 与 bundle `article-source.md` 均为 F-001~F-039，集合一致 |
| 本束专项 toctree/链接/frontmatter/敏感路径 | ✅ 通过 | 9 个文件、8 个 toctree 条目、39 对 F 编号，无本束断链、无 `file:///`、无家目录绝对路径 |
| `scripts/check-utf8.py` | ✅ 通过 | `10412 个文件均为有效 UTF-8` |
| `scripts/check-bundles-index.py` | ⚠️ 当前受并行会话 WIP 影响 | 曾在工作树短暂收敛时通过（9 域 / 59 组 / 555 束）；最终复跑时其他会话回写根索引，报错不含本束路径 |
| `scripts/check-toctrees.py` | ⚠️ 当前受并行会话 WIP 影响 | 最终复跑有 83 处其他新增束未接入 ai/index，输出中无 `workbuddy` 或 `tencent` 本束问题 |
| `invoke gates.*` | ⚠️ 包装器不可用 | 当前 Anaconda 环境的 `invocations` 分发包元数据缺失，invoke 导入阶段报 `PackageNotFoundError: invocations`；已直接运行底层脚本完成本束等效验证 |

## 4. 最终判定

- 高层能力“WorkBuddy/CloudStudio 相关环境可提供公网 HTTPS 入口”有官方端口转发能力与实时页面证据支撑。
- 博文关于固定 `sh1.agentos-app.net`、CLB TLS 终止和 `sandbox-proxy` 的内部架构说法未获官方公开文档证实，正文已持续标注。
- 本束满足 `stable` 条件；保留 2026-11-30 前复核域名、网关和生命周期的时效要求。
