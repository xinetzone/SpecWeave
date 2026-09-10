---
title: "Spec：DSH Mobile 博文 → OKF 知识包"
status: "draft"
source: "腾讯技术工程公众号《我用腾讯 Kuikly，把 DeepSeek Harness 装进了口袋》(2026-09-08)"
---

# Spec：DSH Mobile 博文 → OKF 知识包

## 内容敏感度预检

- URL：`https://mp.weixin.qq.com/s/THtcdws01AV_Q3fe2pYRlQ`（腾讯技术工程公众号公开文章，无访问控制参数）→ **公开内容 → 标准工作流**
- 产出物：`projects/awesome-okf-xs/doc/bundles/` 下既有分组

## 目标

将微信公众号「腾讯技术工程」《我用腾讯 Kuikly，把 DeepSeek Harness 装进了口袋》（2026-09-08，作者腾讯程序员 yuki）转化为 OKF v0.2 知识包，归属 `jishu/ai/ai-agent/` 分组，bundle 名 `deepseek-harness-mobile`，与既有源码教程 `deepseek-harness`（同实体）互链为同主题簇。

## 归属位置分析

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `ai/ai-agent/deepseek-harness-mobile/`（选定） | ✅ | ① 文章主线实体是 DSH Mobile——DeepSeek Harness 的移动客户端，DSH 承担核心角色（被连接的 Agent 运行时）；② 同分组已有既有 bundle `deepseek-harness/`（源码教程）与多个博文转化先例（doubao-work/qwen-ui-agent 等"产品实测/工具教程"分类）；③ 可与之互链为主题簇 |
| `ai/deepseek/` | ❌ | 该组为 DeepSeek-AI 组织开源基础设施源码教程（GPU kernel/MoE 等），主题不符 |
| `ai/tencent/` | ❌ | 文章不是讲腾讯开源项目源码，Kuikly 只是实现手段，非主线 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程 |

## 骨架判定（操作可复现性两问）

1. 有可照做流程？✅（Relay 部署命令、插件安装命令、扫码连接四步、排障三查、扩展开发入口均给出具体命令/路径）
2. 作者一手实测 + 可复现？✅（作者即 DSH Mobile/dsh-scan-remote 开发者，仓库公开、含版本 tag、有视频演示）
→ **技术教程/实测类，含 `examples/`**

## 内容结构（信源先行）

| 层 | 文件 | 内容 |
|----|------|------|
| references | article-source.md | F-001~F-045 事实登记（与 spec facts.md 双份一致） |
| references | verification.md | P0 核验报告（11✅/2⚠️/0❌）、勘误与口径、信源距离 |
| concepts/00 | dsh-mobile-overview.md | 产品定位与架构总览：为何需要手机接 Agent、为何弃 WebView、手机=远程控制面板 |
| concepts/01 | kuikly-cross-platform.md | 跨端框架选型：Kuikly 六平台、组件市场（KuiklyMarkdown/KuiklyWebview）、原生桥接差异下沉、KuiklyUI-AI |
| concepts/02 | dsh-host-protocol.md | DSH Host 协议直连：Cordis 三层、HTTP RPC、两条 WebSocket、快照/宽类型 |
| concepts/03 | connection-and-reconnect.md | 连接与断线恢复：SSH 隧道、扫码 Relay（sealed-tunnel-v1）、重连顺序、世代号、安全模型 |
| concepts/04 | mobile-agent-control-patterns.md | 行业参照与趋势：Cursor/Claude Code Remote Control、手机=决策节点、路线图、不绑定 DSH |
| examples/00 | local-scan-connect.md | 快速跑起来：Relay 启动 + 插件安装 + 扫码连接 + 排障 |
| examples/01 | extend-dsh-mobile.md | 扩展开发入口：新增方法/原生能力/页面/事件 |

## 质量门

- G1：事实句无因果词，全部 F 编号可溯，观点标"作者观点/设计取向"
- G2：概念层区分事实与设计决策（作者观点）
- G3：examples 命令来自博文原文（经作者实测），标注版本敏感性
- G4：Mermaid 遵循安全编码六规则；toctree 完整、相对链接可达
- 机械门禁：UTF-8 strict、双份 F 编号一致、三级 toctree、相对链接可达、三级计数同步（ai-agent 45→46 / ai 域 / 全库 +1）、敏感信息零残留

## 核验要点（勘误四张清单关注）

- **日期/版本表**：DSH dsh-v0.1.1-rc.2（博文时点）vs 核验最新 dsh-v0.1.3-alpha.1；KuiklyWebview 版本博文 1.0.1-2.0.21 vs 当前 README 1.0.2-2.0.21（⚠️ 标注时点）
- **成效数字溯源**：Kuikly"日活超 5 亿"为腾讯官方口径，标注厂商自述，不可独立验证
- **口径对照**：Kuikly 覆盖"六大平台"官方标注 H5/小程序 Beta、macOS Alpha；组件归属 Kuikly-contrib 组织
- **引文逐字**：博文为作者一手实测（开发者自述），无外部高管引语

## 配图

无（不生成位图，以 Mermaid 架构图呈现三层协议与连接拓扑）。
