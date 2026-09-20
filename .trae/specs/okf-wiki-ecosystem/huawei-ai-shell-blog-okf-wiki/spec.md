---
type: specification
title: "华为云 AI Shell 公众号文章转 OKF Wiki"
source: "https://mp.weixin.qq.com/s/sIQVJOwquej8BC-4aQ3wWA"
status: draft
---

# 华为云 AI Shell 公众号文章转 OKF Wiki

## 内容敏感度预检

- URL 为公开微信公众号文章，无 `code`、`token`、邀请码或内部域名参数。
- 判定：公开内容，采用标准文章转 OKF Wiki 工作流。
- 规划产物位于 `.trae/specs/`，最终知识包位于 `projects/awesome-okf-xs/doc/bundles/`。

## 七概念编排

- 场景：知识沉淀
- 链路：R（事实采集）→ I（结构洞察）→ E（知识包生成）→ V（对抗审查）→ C（原子交付）
- G1：事实与作者观点分离，事实条目不使用因果推断作为事实。
- G2：结构洞察包含现象、机制、影响和使用建议。
- G3：知识包包含触发场景、操作步骤、边界与反模式，可迁移到其他云端 Agent 开发环境。
- G4：文件按信源、概念、示例、索引和日志原子化组织。

## 骨架判定

文章给出了入口、登录、授权、提示词和环境检查流程，读者可以照做；流程包含明确步骤和输入输出。因此采用技术教程骨架：

`index.md` + `concepts/` + `examples/` + `references/` + `log.md`

## 归属位置

| 候选位置 | 判定 | 理由 |
|---|---|---|
| `jishu/ai/agent-platform-notes/` | 选定 | 主线是云端 Agent 开发平台与终端工作环境，目标分组已收录 BrowserAct、Minitap、Octo 等平台散篇 |
| `jishu/ai/ai-agent/` | 排除 | 该分组更偏 Agent 框架、协议与应用教程，本文主线是华为云平台环境 |
| 新建华为云分组 | 排除 | 单篇文章新建分组违反最小变更原则 |

## 知识地图

1. `concepts/00-platform-positioning.md`：AI Shell 的产品定位、工作流与适用场景。
2. `concepts/01-environment-and-constraints.md`：体验版/持久化版、ARM 环境与资源边界。
3. `concepts/02-ai-assisted-cloud-operations.md`：自然语言、授权执行、模型与技能的协作机制。
4. `concepts/03-vps-selection-boundary.md`：AI Shell 与 VPS 的选型边界。
5. `examples/01-first-session.md`：首次进入、探查配置和保存文件的操作流程。
6. `examples/02-use-case-matrix.md`：编程、Linux 学习、自动化和生产环境的决策矩阵。

## 事实登记

详见同目录 `facts.md`。文章事实统一从 F-001 编号，官方核验补充从 F-021 起。

## 验收标准

- [ ] references 先于 concepts/examples 生成。
- [ ] 博文声明和官方核验事实双份 F 编号连续一致。
- [ ] 文章单源声明、作者实测和官方事实明确分层。
- [ ] 根索引、分组索引和 bundle toctree 可达。
- [ ] 不将作者实测配置或模型自述写成华为官方承诺。
