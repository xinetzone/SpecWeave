---
title: "Spec：OpenViking 博文 → OKF 知识包"
status: "draft"
---

# Spec：OpenViking 博文 → OKF 知识包

## 目标

将微信公众号「macrozheng」（作者：梦想de星空）2026-09-09 博文《字节又开源了一个顶级 Agent 项目！》转化为 OKF v0.2 知识包，归属 `jishu/ai/ai-agent/` 分组「📰 产品资讯」板块，bundle 名 `openviking`。

## 内容敏感度预检（阶段 0）

- URL：`https://mp.weixin.qq.com/s/OFS4DzgTEcEgzNHyvRVD0g`，无 `code/token/邀请码` 等访问控制参数 → **公开内容（Public）**
- 标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/openviking-blog-okf-wiki/`，产出位于 `projects/awesome-okf-xs/doc/bundles/`

## 信源距离预判

- 博文：③ 第三方技术博主一手部署实测（macrozheng，Java 领域知名技术号；自购服务器实跑，无赞助声明、无成效数字营销叙事）
- 裁决源：① 官方 GitHub 仓库/README、GitHub API、docs.openviking.ai 官方文档、阿里云百炼官方文档
- 厂商自述数据：官方 README 的 LoCoMo/tau2-bench 基准为火山引擎自测（F-044），引用时显式标注"厂商自述基准"

## 骨架判定（操作可复现性两问）

1. 有读者可照做的安装/配置/实测流程？✅（ov.conf 完整 JSON、docker pull/run、/health 验证、Web Studio 连接与用户配置、VikingBot 跨会话记忆分步实测）
2. 经作者实测、有版本/输入输出/步骤顺序？✅（具体服务器地址、端口 1933、配置块、预期返回、UI 点击顺序、记忆文件路径）

→ **技术教程/工具实测类，含 examples/**（同组先例：wigolo、claude-vision-skill、qwen-ui-agent）。

## 归属判定

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/ai-agent/openviking/`（选定） | ✅ | ① 主线实体 OpenViking 是 AI Agent 的上下文/记忆基础设施，分组简介明确含"记忆系统"；②「📰 产品资讯」已有 wigolo（工具教程）、claude-vision-skill（工具教程）、zhihu-cli（CLI 工具）等同形态博文转化束先例；③ 与 ai-agent-fundamentals 的"记忆"架构模式、veadk-python 的"双层记忆"可交叉引用 |
| `jishu/ai/volcengine/` | ❌ | 该束为火山云商业产品分析（Ark/Computer-Use/Viking 搜索推荐云服务），OpenViking 是 AGPL 开源独立项目，形态不符 |
| `jishu/ai/volcengine-agent/` | ❌ | AgentKit/VEADK 商业化 Agent 开发套件主题，非开源上下文数据库 |
| ai 域直挂束 | ❌ | 能落分组不直挂；ai-agent 分组语义最贴且先例充分 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程 |

## 内容结构（信源先行）

| 层 | 文件 | 内容 |
|----|------|------|
| references | article-source.md | F-001~F-048 双份事实登记（与 facts.md 集合一致） |
| references | verification.md | P0 核验报告（10 项：10✅ 含口径细化 / 0❌ / 2⚠️）、勘误四张清单、信源距离 |
| concepts/00 | 00-context-database-overview.md | 发布事实层：项目档案、定位、解决的四类痛点、与传统向量库差异、许可与商业形态 |
| concepts/01 | 01-viking-vfs-context-layers.md | 机制层：viking:// 虚拟文件系统、三类上下文、L0/L1/L2、目录递归检索（TrieHI） |
| concepts/02 | 02-memory-lifecycle-integrations.md | 架构层：会话沉淀记忆生命周期、15 个 MCP 工具、集成矩阵、官方自述基准、研究背景 |
| examples/00 | 00-docker-server-deployment.md | Linux 服务器 Docker 全流程：ov.conf 四块（百炼模型）、镜像/挂载/密钥、health/ready、Studio 双密钥配置 |
| examples/01 | 01-cross-session-memory-walkthrough.md | VikingBot 跨会话记忆实测：写入→新会话召回→终端 /search→明文文件定位 |
| examples/02 | 02-agent-integration-mcp-cli.md | 外接 Coding Agent：安装脚本/Hooks、手动 MCP 配置、ov CLI 与 SDK、其他部署形态 |

## 质量门

- G1：事实句无推断词，数字/模型名/端口/工具名全部挂 F 编号
- G2：概念层四元组（现象→机制→边界→信源），作者观点显式标注
- G3：examples 命令来自博文或官方文档，博文与官方差异处双标注
- G4：双份 F 编号集合一致（F-001~F-048 连续）；toctree/相对链接/UTF-8 手动等效验证
- 计数：bundles 538→539、jishu 406→407、ai 187→188、ai-agent 47→48
