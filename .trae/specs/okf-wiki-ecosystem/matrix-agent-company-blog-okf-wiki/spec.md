---
title: "Spec: Matrix "0人公司" 博文 → OKF Wiki 教程"
status: "draft"
---

# Spec: Matrix "0人公司" 博文 → OKF Wiki 教程

## 1. 任务概述

将微信公众号"智潮笔记"博文《这个AI工具真的疯了！它可以帮你开一家"0人公司"，只需要一个想法，Agent就能自己去赚钱》（2026-07-04）转化为 OKF v0.2 知识包，遵循 `blog-article-to-okf-wiki` Skill 七阶段工作流。

## 2. 内容敏感度预检（步骤1）

- URL：`mp.weixin.qq.com/s/C5clrnoai50eneYvgP1nLw`，无 `share?code=`/`token=`/邀请码等访问控制参数
- 判定：**公开内容（Public）** → 标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/matrix-agent-company-blog-okf-wiki/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/ai/ai-agent/`

## 3. 信源获取（R）

- WebFetch 对微信域名 13/13 反爬拦截（Skill 已知）→ 直接使用 browser_use 子代理提取 `#js_content`，成功获取全文 2768 字
- 信源距离预判：**第三方自媒体转述 + 厂商自宣浓度高**——博文核心成效数字（GDPval 95.45%、100+ 视频、700k+ 播放）均转述自 Matrix 官网宣称，全部按厂商自述处理并 P0 必核验

## 4. 骨架判定（步骤2，操作可复现性两问）

1. 博文中是否有读者可照做的安装/配置/代码/调用/实测流程？→ **否**（全文为产品介绍与评论，无任何可操作步骤）
2. 这些流程是否经作者实测、具备可复现性？→ **否**（作者未实测，案例均为官网转述）

**两问皆"否" → 无 `examples/`**。内容性质：**商业分析/产品资讯类**（厂商自宣产品的媒体转述），index 顶部须加"厂商自述数据"提示块。

骨架：`index.md + concepts/ + references/ + log.md`

## 5. 归属判定（步骤3）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `ai/ai-agent/`（选定） | ✅ | ① 主线实体 Matrix 是 AI Agent 公司操作系统产品；② 该分组已有大量非源码类先例（doubao-work 产品实测、agora-gemini-transcribe 厂商动态、siemens-industrial-agent 行业分析、a2a-mcp-convergence 技术分析），"📰 产品资讯"板块语义完全匹配；③ Matrix 可与既有 Coding Agent 源码解读 bundle（openai-codex 等）形成生态对照 |
| `ai/trae/` | ❌ | 字节 AI 产品矩阵专属分组，主题不符 |
| `ai/anthropic/` | ❌ | Anthropic 官方开源生态，Matrix 仅是接入 Claude Code 的第三方产品 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程，违反最小变更原则 |

**选定路径**：`projects/awesome-okf-xs/doc/bundles/ai/ai-agent/matrix-zero-person-company/`

## 6. 三层知识拆分（I 阶段，知识地图）

| 博文内容层 | 映射篇目 |
|-----------|---------|
| 产品定位与叙事层（What：0人公司叙事、模型接入、平台形态） | `concepts/00-product-overview.md` |
| 架构机制层（How：CEO Office/部门/OKR/记忆/proof/商业基建/VPTD） | `concepts/01-agent-company-architecture.md` |
| 案例成效与证据边界层（证据分级：厂商自述 vs 独立验证） | `concepts/02-case-evidence-boundary.md` |
| 事实清单 + 核验报告 | `references/article-source.md`、`references/verification.md` |

## 7. 核验计划（R 阶段 P0 清单）

1. Matrix 产品存在性与定位（矩阵式多部门 Agent 平台）→ 三方工具站收录 ✅
2. 模型接入列表 F-006 → aitoolnet+hotools 一致 ✅
3. 商业基建/Revenue 能力 F-024 → 一致 ✅（补充 VPTD 指标）
4. GDPval-Bench 95.45% 与对照数字 F-025 → 仅厂商自述 ⚠️（GDPval 口径分歧：Elo vs 百分比）
5. aivideopro.io 案例数字 F-020~F-022 → 仅厂商自述 ⚠️
6. macOS 桌面应用/Web 未上线 F-018 → 仅博文单源
7. 同名产品排除（Hebbia Matrix / matrix-agent-neo）→ F-045

## 8. 状态判定

- 无 ❌ 硬错误，核心叙事未被证伪 → `status: stable`
- 但厂商自宣类 → index 顶部"厂商自述数据"提示块 + 已知边界 6 条 + `stale_after: 2026-12-31`

## 9. 索引接入计划（V 阶段）

1. `ai/ai-agent/index.md`：📰 产品资讯导航表加行 + toctree 追加 + 束数 34→35 + 内容统计 299→305 文档（4 概念 + 2 信源 + 3 索引 + 根 index + log = 9 文件，实际 +6 内容文档与 +1 束）
2. `bundles/index.md`：ai-agent 组束数 34→35、ai 域 120→121、全库 348→349（frontmatter + 正文三处同步）
