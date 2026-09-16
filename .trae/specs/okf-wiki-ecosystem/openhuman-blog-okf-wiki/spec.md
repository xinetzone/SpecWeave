---
type: Spec
id: spec-openhuman-blog-okf-wiki
title: 开源先驱博文《又一个人AI助手炸了》→ OpenHuman OKF 知识包转化
date: 2026-09-16
source:
  - https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ
workflow: blog-article-to-okf-wiki（R→I→E→V→C 七阶段）
status: executed
---

# OpenHuman 博文 → OKF Wiki 转化方案

## 1. 任务概述

将微信公众号「开源先驱」（作者：豆芽菜小萌）2026-07-28 发布的博文《又一个人AI助手炸了。连续9天GitHub Trending第一，3,900次提交，7,800+ Star》转化为可溯源 OKF v0.2 知识包。博文介绍对象为开源个人 AI 助手 **OpenHuman**（TinyHumans AI，GitHub: `tinyhumansai/openhuman`）。

- 博文 URL：https://mp.weixin.qq.com/s/pdH1ZB3yPfDdA7Ay72hjGQ
- 正文规模：约 2,800–3,000 汉字 / 5,324 字符（含 3 表 2 代码块），browser_use 两次加载交叉一致
- 产出 bundle：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ai-agent/openhuman/`

## 2. 内容敏感度预检（阶段 0）

- URL 为 `mp.weixin.qq.com/s/...` 公开文章，无 `code`/`token`/邀请码等访问控制参数 → **公开内容（Public）**
- 标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/openhuman-blog-okf-wiki/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`

## 3. 信源距离预判

| 维度 | 判定 |
|------|------|
| 信源性质 | **第三方自媒体推广/评测文**（公众号「开源先驱」为开源资讯导流号，文末"点赞在看转发"+标题党推荐阅读） |
| 一手性 | 作者明确写"我翻了翻社区讨论和评测"，**未声明一手实测**；"实际体验是什么感觉"段为设问式描述 |
| 营销叙事浓度 | 中高：标题党指标（9 天 Trending/3,900 commits/7,800 Star）、成效数字（省 80%/月省几百块）、"这有点意思"功能猎奇 |
| 核验策略 | 全部数字/功能声明默认 P0，以 **GitHub 仓库实况（页面+Contents/Releases/Tags API）+ 官方 GitBook + 官网 openhuman.dev** 为权威源；Trending 历史排名等不可回溯项标"仅博文/官方 README 自认" |

## 4. 骨架判定（操作可复现性两问）

| 两问 | 判定 |
|------|------|
| ① 是否有读者可照做的安装/配置/代码/调用/实测流程？ | **是（弱）**——含一键脚本/Homebrew/源码构建命令与 OAuth 三步走，但均为通用安装指引 |
| ② 是否经作者实测、具备可复现性（版本/输入输出/步骤顺序）？ | **否**——作者自陈基于社区讨论与评测，无一手实测声明；成本测算为假设推算 |

**结论：任一为"否" → 不设 `examples/`**（参照 threeui/a2a-mcp 技术综述先例）。性质 = **技术综述/产品介绍**，骨架 index + concepts/ + references/ + log，index 顶部声明"非操作教程"。安装命令经官方核验后作为概念篇中的事实章节呈现。

## 5. 归属判定（决策树）

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `ai/ai-agent/openhuman/`（选定） | ✅ | ① 主线实体 OpenHuman 自我定位即 "open source **agent harness** with local-first memory, agent orchestration, and workflows"（GitHub About 原文）；② 该组「📰 产品资讯」板块已有 pi-agent-harness（博文综述）、matrix-zero-person-company（产品资讯）、wigolo（工具教程）等 15+ 非源码类 bundle 先例；③ 可与 `second-me`（个人 AI 数字分身）、`pi-agent-harness`（harness 定位）交叉互链 |
| `ai/anthropic/` | ❌ | 博文竞品提 Claude Cowork，但主线实体非 Anthropic |
| `ai/coze/`、`ai/trae/` | ❌ | 厂商分组，OpenHuman 属 TinyHumans，主题不符 |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程 |

## 6. 知识地图（三层拆分）

技术综述/产品介绍类三层映射：

| 层 | 篇目 | 内容 |
|----|------|------|
| 事件事实层（What/When） | `concepts/00-what-is-openhuman.md` | 产品定位与 stateless 命题、热度事实与时间线、仓库元数据、技术栈与许可证、获取与安装（官方命令） |
| 机制原理层（Why/How） | `concepts/01-memory-tree-and-tokenjuice.md` | Memory Tree 官方管线（三树/分块/打分/作业队列/leaf 生命周期/Obsidian vault）、10 亿 token 口径勘误、TokenJuice 七阶段压缩（官方机制 vs 博文测算） |
| 机制原理层 | `concepts/02-runtime-and-agent-design.md` | 检查点图编排/Split Brain、Subconscious、吉祥物与语音、会议 Agent、隐私模式与 Ollama、Signal A2A + x402（tiny.place/USDC 勘误） |
| 格局/取舍层 | `concepts/03-landscape-tradeoffs.md` | 官方/博文两套竞品对照表、适用人群、Early Beta 短板与风险、组合使用建议（作者观点分层） |

无 examples/；无 Mermaid（机制描述以官方管线代码块呈现，不另绘未经证实的架构图）。

## 7. P0 核验结论摘要（详见 verification.md）

权威源核验 12 项：✅ 通过 6 项（GPL-3.0、9 天 Trending README 自认、Memory Tree 机制、TokenJuice 80%、四会议平台、安装脚本/brew）；⚠️ 口径漂移/单源 6 项（118+→官方现 100+、17→官方现 15、10 亿 token 官方文档无数字、star/commit 历史值不可回溯且与当前值差距大、"六十多个版本"与 56 releases/106 tags 口径、tiny.place/USDC/ChaCha20/React/Linux 沙箱未获官方证据）；**0 项硬 ❌**（主结论"有记忆的本地优先 agent harness 真实存在且爆火"成立）。

**状态判定：`status: stable`**——失败项均为时点口径漂移或单源声明，非核心声明证伪；但数字勘误数量多（6 类），index 顶部设醒目数字口径提示块，known boundaries 全列，`stale_after: 2026-12-31`（Early Beta 周级发版，指标强时效）。

## 8. 文件清单（10 新建 + 2 索引修改）

新建 bundle：
- `openhuman/index.md`、`openhuman/log.md`
- `openhuman/concepts/index.md` + 4 篇概念文档
- `openhuman/references/index.md` + `article-source.md` + `verification.md`

索引接入：
- `ai/ai-agent/index.md`：frontmatter 47→48、📰 产品资讯表加行、toctree 追加、页脚计数同步
- `bundles/index.md`：total 545→546、jishu 413→414（mermaid+表头两处）、ai 域 194→195

事实集：[facts.md](facts.md)（F-001~F-064，共 64 条：博文 42 条 + 核验补充 22 条）。

## 9. ADDED Requirements（验收标准）

1. 双份 F 编号（spec facts.md 与 article-source.md）集合一致、连续无跳号
2. 正文所有数字/功能名携带 F 编号；勘误项在正文呈现官方现值而非博文数字
3. 三级 toctree 完整、相对链接全可达、无 `file:///`、UTF-8 strict
4. 三级计数（组 48 / ai 195 / jishu 414 / total 546）同步
5. frontmatter 双信源（博文 + GitHub/官方 GitBook）齐备
