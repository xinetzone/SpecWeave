---
id: "agent-workspace-starter-guide-03-next-steps"
title: "03 进阶（10 分钟）——深潜入口与后续路径"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 03 进阶（10 分钟）

**本段目标**：从「能用」走到「知道往哪深挖」——选定 1~3 个深潜条目，并了解完整版体系。

**前置**：02 首个任务完成——你已跑通一次规格驱动开发，拿到产出物与验收记录。

## 1. 什么时候深潜哪一条

starter 的 `rules/` 与 `protocols/` 是深潜主战场。按你遇到的场景挑：

| 你遇到的情况 | 深潜条目 | 路径 |
|---|---|---|
| 智能体写的代码风格/结构不合意 | AI 编码准则（四原则） | [../starter/.agents/rules/ai-coding-guidelines.md](../starter/.agents/rules/ai-coding-guidelines.md) |
| 修了 bug 又复发，想根治 | 修复→预防→闭环 SOP | [../starter/.agents/rules/fix-prevent-close-loop.md](../starter/.agents/rules/fix-prevent-close-loop.md) |
| 不确定某内容该不该公开/入哪 | 内容敏感度预检 | [../starter/.agents/rules/content-sensitivity-precheck.md](../starter/.agents/rules/content-sensitivity-precheck.md) |
| 想让任务规格化、可追溯 | Spec 写作 + 创建前预检 | [../starter/.agents/rules/spec-writing-guide.md](../starter/.agents/rules/spec-writing-guide.md) |
| 想把工作区搬到别的项目 | 工作区发现协议 | [../starter/.agents/protocols/workspace-discovery.md](../starter/.agents/protocols/workspace-discovery.md) |
| 想自定义装载提示词 | 一句话装载协议 | [../starter/.agents/protocols/prompt-bootstrap.md](../starter/.agents/protocols/prompt-bootstrap.md) |

**建议起步**：先深潜「AI 编码准则」与「修复闭环」两条——它们覆盖日常编码最高频的两个场景。

## 2. 让深潜形成闭环

不要只读不练。选一条后：

1. 读完，用一句话总结它的核心动作。
2. 在你自己的项目里制造一个该场景的小任务，验证它是否够用。
3. 若发现规范不合你的项目，**直接改你的项目副本**（你拷进来的是你自己的，不必迁就原样）。

> 规范容器的价值不在于「照抄」，而在于「有一个稳定、可修改的起点」。

## 3. 完整版：SpecWeave 开源仓库

本 starter 是从 SpecWeave 的 `.agents/` 中萃取的最小化导览集。当你需要更多角色、工作流、检查清单、技能与验证脚本时，可访问完整开源仓库：

- https://github.com/xinetzone/SpecWeave

完整版包含：7 个角色定义、8 个自我演进模块、多智能体协作协议、三阶段方法论、复盘与知识库体系，以及数百个技能与验证脚本。starter 里每个类目的 README 都标注了它从完整版哪一类目精简而来，可顺藤摸瓜。

## 4. 后续学习建议

- **先固化，再扩展**：用一周时间在真实项目里跑通 2~3 个规格驱动任务，再增加类目。
- **渐进式加载**：不要一上来装全套。按 [../starter/.agents/context-routing.md](../starter/.agents/context-routing.md) 的映射，用到哪个类目再读哪个。
- **回看检查点**：把四段的「完成检查点」当作你的能力清单，逐项确认。

## 完成检查点

- [ ] 从 `rules/` 或 `protocols/` 选定 ≥1 个深潜条目并写下路径。
- [ ] 为选定的条目写下一句话后续动作（什么时候、在哪个项目上用）。
- [ ] 已收藏完整版 SpecWeave 仓库地址。
- [ ] 能说出「渐进式加载」的含义：用到哪个类目再读哪个。

---

学习路径结束。回到 [README.md](README.md) 复习时间盒，或回到 [../walkthrough/](../walkthrough/) 再跑一遍演练。