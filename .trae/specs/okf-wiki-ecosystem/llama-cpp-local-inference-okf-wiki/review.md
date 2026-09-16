---
okf_version: "0.2"
type: review
title: "llama.cpp 博文转化 V 阶段对抗审查记录"
description: "四视角对抗审查、机械门禁结果与中断恢复说明；R→I→E→V 链路质量门 G1/G3/G4 通过记录"
tags: [okf-bundle, blog-article, llama-cpp, adversarial-review, verification]
generated:
  by: process:seven-concepts-v
  at: "2026-09-16T21:55:00+08:00"
---

# V 阶段对抗审查记录

> 审查对象：`jishu/ai/llama-cpp-local-inference/`（9 文件，无 examples/）
> 审查时间：2026-09-16；方法：四视角人工审查 + 子模块 stdlib 门禁脚本 + 独立信源重验。

## 1. 中断恢复与幂等

- 开工时检出 spec（spec.md/facts.md）与 bundle references/ 三文件已由前轮会话落盘，但根 index/concepts/log 缺失（R 后中断）。
- 处置：回读全部既有产物判定恢复点，E/V 续作而非重建；前轮 log.md 占位"待复核"项全部以实测结果替换；F-047 补登已同步双份登记。

## 2. 四视角审查

### 2.1 事实溯源视角

- 正文出现的每个具体声明（Star、端口、量化体积、硬件档、后端、许可证、创建时间）均带 F 编号；正则核对正文引用 F 集合为 47 个，全部在登记范围内，无越界编号。
- 勘误落实：4GB/7B/20–30 tok/s 呈现为 ❌ 并给出官方正确值（8–16GB、4.3–4.5GB），未照搬源文数字；Star 双时点（121K 发文时点 / 127,752 核验时点）；作者观点 11 处保留 V 标注，未固化为官方结论。
- 独立重验（不轻信前轮产物）：重新请求 GitHub API，`stargazers_count=127,752`、MIT、2023-03-10、master、llama.app 与 F-038 逐字一致；重新抓取官方 server 文档页，127.0.0.1:8080/Web UI/`/v1/chat/completions`/`/v1/embeddings` 与 F-040 一致，页面额外能力补登为 F-047。

### 2.2 结构规范视角

- 骨架：技术体验/科普综述，操作可复现性两问 Q1 弱是、Q2 否 → 无 examples/（与 spec 判定一致）。
- frontmatter：根 index（bundle）+ 3 概念篇（Concept）+ 2 信源（reference）必填字段齐备；子目录 index 无 frontmatter 但含 toctree。
- toctree：根 index 收录 concepts/index、references/index、log；concepts/index 收录 3 篇；references/index 收录 2 篇；组 index 导航表与 toctree 双接入。

### 2.3 读者可用性视角

- 30 条 Markdown 相对链接逐一 Test-Path 全部可达，含根 index 主题关联 3 条（echobird、tencent/ncnn、containers/ai-lab-recipes）。
- 无 `file:///` 链接与家目录绝对路径。
- 概念篇可独立 follow：事实/机制/决策分层，反模式 6 条可操作。

### 2.4 时效边界视角

- 动态数字带时点；stale_after 2027-03-16；已知边界声明第三方体验性质、树莓派限制、无鉴权 server 不得暴露公网。

## 3. 机械门禁结果（子模块 stdlib 脚本，未走 invoke）

| 门禁 | 结果 |
|------|------|
| `scripts/check-bundles-index.py` | ✅ 通过：9 域 / 59 组 / 546 束五面一致（本束计入） |
| `scripts/check-utf8.py` | ✅ 通过：10330 文件有效 UTF-8 |
| `scripts/check-toctrees.py` | ✅ 本束零问题；全库 14 处报错均属他会话在途 WIP（ai-agent-book/free-llm-api-hands-on/inurl-unified-token/workbuddy），按"谁添加谁对账"未代改 |
| 双份 F 编号（spec facts.md ↔ article-source.md） | ✅ 均 F-001~F-047（47 个），集合相等、无跳号 |
| 正文 F 引用范围 | ✅ 无 F-047 之外引用 |

## 4. 质量门结论

- **G1（事实门）**：通过。博文事实与观点分层（O/V/A），无因果推断词混入事实表。
- **G3（可迁移门）**：通过。决策篇给出触发场景、采用步骤 6 步、反模式 6 条与硬件/API 边界。
- **G4（原子交付门）**：待 C 阶段。建议提交序列：① 子模块 bundle（9 文件）+ ai/index.md + bundles/index.md → ② 主仓库 spec（spec.md/facts.md/review.md）→ ③ 主仓库子模块指针。
- **状态**：bundle `stable`（核心声明失败项不影响主结论，勘误完整落地，不触发 flagged）。
