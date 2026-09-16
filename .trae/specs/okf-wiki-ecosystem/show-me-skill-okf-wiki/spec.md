---
type: Spec
id: spec-show-me-skill-okf-wiki
title: 微信博文《show-me Skill 体验文》→ OKF Wiki 知识包转化
date: 2026-09-16
status: active
source:
  - https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ
tags: [博文转化, OKF, 知识包, Agent-Skill, HumanLayer, show-me, 知识沉淀]
workflow: blog-article-to-okf-wiki（七阶段 R→I→E→V→C）
orchestrator: seven-concepts-cmd（场景4：知识沉淀）
---

# 微信博文《show-me Skill 体验文》→ OKF Wiki 知识包转化 Spec

## 1. 任务概述

将微信公众号"阿胖 AI 手记"博文《我发现一个神仙 Skill，就几行规则，没教AI任何新本事，却让我的WorkBuddy像换了个脑子！》（2026-09-06）按 `blog-article-to-okf-wiki` 七阶段工作流转化为 OKF v0.2 知识包（bundle），方法论编排走 seven-concepts-cmd 场景 4（知识沉淀 R→I→E→V→C）。

## 2. 阶段 0：内容敏感度预检

| 项目 | 结论 |
|------|------|
| URL | `https://mp.weixin.qq.com/s/dG6w9Dd_vqb_qcEqaQRPsQ` |
| 访问控制特征 | 无 `share?code=`/`token=`/邀请码参数，公众号公开文章 |
| 敏感度级别 | **公开（Public）** |
| 工作流 | 标准工作流：spec 在 `.trae/specs/okf-wiki-ecosystem/`，产出在 `projects/awesome-okf-xs/doc/bundles/` |
| 信源距离 | **作者一手实测**（独立公众号作者在自有 Agent 环境实测开源工具）+ 官方发布物核验；非厂商自宣（作者与 HumanLayer 无归属关系） |

## 3. 骨架判定（操作可复现性两问）

| 两问 | 判定 | 依据 |
|------|------|------|
| ① 是否有读者可照做的安装/配置/代码/调用流程？ | **是** | 官方安装命令 `npx skills add humanlayer/skills --skill show-me`；三种调用方式（`/show-me`、自然语言、`/show-me as an html explainer`）；WorkBuddy 内两条安装路径 |
| ② 是否经作者实测、具备可复现性（步骤顺序/输入输出）？ | **是** | 作者三轮实测（流程问答→方案取舍→HTML 讲解页），输入问题具体、输出形态有截图与文字描述；命令经官方博客逐字核验。版本号缺失（F-039 单源注记），不影响安装调用复现 |

**骨架结论**：技术工具教程骨架 → `index + concepts/ + examples/ + references/ + log.md`（先例：同分组 `claude-vision-skill` 工具教程博文转化，2 examples）。

## 4. 归属位置分析

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `jishu/ai/ai-agent/show-me-skill/`（选定） | ✅ | ① 主线实体 show-me 是面向 Coding Agent 的开源 Skill，属 Agent 技能生态；② 分组"🎯 Tier 3：专项工具/应用/技能"已收 anthropics-skills/agent-skills-spec/ai-agent-skills 等技能规范束，"📰 产品资讯"已收 claude-vision-skill/wigolo/openviking/zhihu-cli 等工具教程类博文转化束，板块语义完全匹配；③ 单篇博文不新建分组 |
| `jishu/ai/anthropic/` | ❌ | show-me 为 HumanLayer 出品，非 Anthropic 官方生态；尽管可在 Claude Code 安装，归属锚点不是 Anthropic |
| `jishu/ai/` 直挂 | ❌ | 技能类束已有 ai-agent 分组承载，直挂会造成同主题分散（参照 mattpocock-skills 直挂属生态格局分析、非单一技能教程） |
| 新建分组 | ❌ | 单篇博文新建分组属过度工程 |

**bundle 路径**：`projects/awesome-okf-xs/doc/bundles/jishu/ai/ai-agent/show-me-skill/`
**分类板块**：ai-agent 分组索引"📰 产品资讯"表，类型标注"工具教程"。

## 5. R 阶段结论：事实与核验

- 事实登记：**39 条**（博文事实 F-001~F-030 共 30 条 + 核验补充 F-031~F-039 共 9 条），详见 [facts.md](facts.md)。
- P0 核验：**7 项全部 ✅，0 硬错误**；1 项 ⚠️ 口径精度补充（Grill Me 为 Matt Pocock 出品，博文未误归因但需防读者误读，F-037）；1 项单源注记（仓库内 SKILL.md 具体路径未直取，F-039）。
- 状态判定：无核心声明失败 → `status: stable`（非 flagged）。

## 6. I 阶段：三层知识拆分（知识地图）

| 知识层 | 篇目 | 内容 |
|--------|------|------|
| 发布事实层（What） | `concepts/00-show-me-what-and-why.md` | show-me 是什么、HumanLayer 2026-08-12 发布（Dex Horthy）、"小作文墙"问题、"不增加新能力、改变表达方式"的 Skill 形态、视觉皮层设计论据 |
| 机制词汇层（How） | `concepts/01-visual-vocabulary.md` | 官方 9 类可视化词汇（组件树/调用栈/Mermaid 图/文件布局/伪代码/类型签名/diff/HTML mockup/HTML explainer）；程序设计前置与大 diff 回顾两场景；作者三轮实测映射 |
| 模式观点层（Why/So-what） | `concepts/02-subtraction-skills-pattern.md` | "做减法的 Skill"模式：show-me 白板（别急着写）vs Grill Me 质询（别急着干）；适用/不适用场景（作者观点分层标注）；Agent 复杂度正相关 |
| 可演练内容 | `examples/00-install-and-invocation.md` | 安装命令、三种调用、WorkBuddy 两条安装路径、自测话术 |

## 7. E 阶段：文件清单（11 个文件）

```
show-me-skill/
├── index.md                         # 根索引（frontmatter + 已知边界 + toctree）
├── log.md                           # 变更日志
├── concepts/
│   ├── index.md                     # 子目录索引（toctree）
│   ├── 00-show-me-what-and-why.md
│   ├── 01-visual-vocabulary.md
│   └── 02-subtraction-skills-pattern.md
├── examples/
│   ├── index.md
│   └── 00-install-and-invocation.md
└── references/
    ├── index.md
    ├── article-source.md            # 博文事实清单（F 编号双份登记之一）
    └── verification.md              # P0 核验报告
```

## 8. V 阶段验收标准（G4）

- [ ] 双份 F 编号一致：facts.md ↔ article-source.md 编号集合相等、F-001~F-039 连续
- [ ] 所有具体声明（日期/命令/9 类词汇/产品名）带 F 编号，作者观点显式分层
- [ ] 三级 toctree 完整，相对链接逐一可达，无 `file:///`
- [ ] frontmatter 齐备，sources 含博文 + HumanLayer 官方博客双信源
- [ ] 计数同步：ai-agent 49→50、ai 194→195、jishu 413→414、全库 546→547
- [ ] UTF-8 strict roundtrip、无家目录绝对路径
- [ ] `invoke gates` 不可用时执行手动等效验证并在 log.md 注明

## 9. C 阶段：提交策略

用户未明确要求提交 → V 阶段完成后输出原子提交建议（① 子模块 bundle+索引 ② 主仓库 spec ③ 主仓库 gitlink），待确认后执行，不 push。
