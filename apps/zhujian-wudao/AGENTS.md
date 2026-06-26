# AGENTS.md — 竹简悟道 AI 协作入口

> 本文档是路由索引，不包含具体规范。根据需求选择性阅读子模块。

---

## 项目身份

**竹简悟道**：以帛书《老子》为哲学根基的 AI 反思引导工具。不做知识翻译者，不做建议者，只做提问者。

当前阶段：HTML 原型验证期。

---

## 文件地图

```
zhujian-wudao/
├── README.md                      # 应用说明（面向使用者）
├── AGENTS.md                      ← 本文件（路由索引，面向 AI 协作者）
├── 竹简悟道_完整版.html           # 自包含 HTML 原型（全部 CSS/JS 已内联，可直接打开）
├── 报名帖_竹简悟道.md             # 大赛报名帖
└── .agents/                       ← 全部项目规范与文档
    ├── project.md                 # 项目概述、核心概念词典、目标用户群
    ├── conventions.md             # 文件命名、代码风格、文档规范、洞察编号规则
    ├── workflows.md               # 标准工作流（洞察撰写、复盘、同步、不一致修正）
    ├── constraints.md             # 禁止事项与约束清单（产品/文档/代码/哲学）
    ├── git.md                     # Git 约定式提交规范
    ├── docs/
    │   ├── product/               # 产品规格文档
    │   │   └── ...-product-spec.md  # 产品规格文档（§一至§九）
    │   ├── insights/              # 洞察库
    │   │   ├── ...-insights-01-30.md  # 洞察 1-30（产品层+架构层）
    │   │   └── ...-insights-31-65.md  # ✅ 洞察 31-68（哲学层+元层）⚠️ 注意：R14已从 insights-31-52.md 重命名，旧文件名已废弃
    │   ├── reviews/               # 复盘报告
    │   │   ├── ...-project-review.md     # 全面复盘报告（P0-P3 优先级清单）
    │   │   └── ...-registration-review.md # 报名流程复盘报告
    │   └── knowledge-transfer/    # 可迁移知识
    │       ├── ...-transferable-patterns.md # 可迁移洞察与模板集
    │       └── ...-transferable-methods.md  # 可迁移方法论全集（面向人类读者）
    ├── roles/
    │   ├── README.md               # 角色索引
    │   ├── philosopher.md          # 哲思引导者（洞察撰写与审查）
    │   └── references/
    │       ├── insight-writing-guide.md  # 洞察撰写速查手册
    │       └── constraints-cheatsheet.md # 约束速查表
    ├── skills/
    │   ├── zhujian-insight-writer/  # 竹简洞察撰写者 Skill
    │   │   ├── SKILL.md             # Skill 主描述（5 步工作流）
    │   │   ├── agents/openai.yaml   # Agent 接口配置
    │   │   ├── references/          # 参考文档
    │   │   │   ├── insight-structure.md   # 洞察结构参考
    │   │   │   ├── tao-core-concepts.md   # 帛书核心概念词典
    │   │   │   ├── constraint-guard.md    # 约束守护
    │   │   │   └── prompt-templates.md    # 提示词模板
    │   │   └── assets/examples/     # 示例洞察（待填充）
    │   └── dao-scholar-illustrations/  # 道德经学者配图 Skill
    │       ├── SKILL.md                # Skill 主描述（5 步工作流）
    │       ├── agents/openai.yaml      # Agent 接口配置
    │       ├── references/             # 参考文档
    │       │   ├── style-dna.md         # 风格 DNA（极简手绘）
    │       │   ├── scholar-ip.md        # 道德经学者 IP 定义
    │       │   ├── composition-patterns.md  # 九种构图模式
    │       │   ├── prompt-template.md   # 生图提示词模板
    │       │   └── qa-checklist.md      # QA 检查清单
    │       └── assets/examples/        # 示例配图（待填充）
    └── html/
        ├── styles.css             # HTML CSS 样式（模块化源文件，完整版已内联）
        ├── data.js                # 数据层（每日一问/AI回复/帛书章节）
        └── app.js                 # 逻辑层（交互函数与事件监听）
```

---

## 路由索引

| 需要了解 | 阅读文件 |
|---------|---------|
| 项目整体定位、核心概念（体道四法/体道链/玄同/场景标签） | [project.md](.agents/project.md) |
| 文件命名规则、洞察编号规则、编辑洞察前必须了解的规范 | [conventions.md](.agents/conventions.md) |
| 产品规格与设计细节 | [spec](.agents/docs/product/2026-06-17-product-spec.md) |
| 已有洞察库（68 条） | [insights-01-30](.agents/docs/insights/2026-06-17-insights-01-30.md) + [insights-31-65](.agents/docs/insights/2026-06-17-insights-31-65.md) |
| 已知问题与优先级清单 | [project-review.md](.agents/docs/reviews/2026-06-17-project-review.md) |
| 撰写新洞察的步骤 | [workflows.md](.agents/workflows.md) §工作流一 |
| 执行全面复盘 | [workflows.md](.agents/workflows.md) §工作流二 |
| 什么绝对不能做 | [constraints.md](.agents/constraints.md) |
| Git 提交格式规范 | [git.md](.agents/git.md) |
| 可迁移模式与方法论 | [transferable-patterns.md](.agents/docs/knowledge-transfer/2026-06-17-transferable-patterns.md) |
| 报名阶段复盘 | [registration-review.md](.agents/docs/reviews/2026-06-17-registration-review.md) |
| 角色分工与职责边界 | [philosopher.md](.agents/roles/philosopher.md) + [角色索引](.agents/roles/README.md) |
| 使用 Skill（智能体能力扩展） | [zhujian-insight-writer](.agents/skills/zhujian-insight-writer/SKILL.md) — 洞察撰写专用 Skill \| [dao-scholar-illustrations](.agents/skills/dao-scholar-illustrations/SKILL.md) — 道德经学者配图 Skill |

