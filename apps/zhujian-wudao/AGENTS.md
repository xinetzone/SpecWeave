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
    ├── docs/superpowers/specs/
    │   ├── ...-spec.md            # 产品规格文档（§一至§九）
    │   ├── ...-review.md          # 全面复盘报告（P0-P3 优先级清单）
    │   ├── ...-insights-01-30.md  # 洞察 1-30（产品层+架构层）
    │   ├── ...-insights-31-52.md  # 洞察 31-54（哲学层）
    │   ├── ...-registration-review.md  # 报名流程复盘报告
    │   └── ...-transferable-patterns.md # 可迁移洞察与模板集
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
| 产品规格与设计细节 | [spec](.agents/docs/superpowers/specs/2026-06-17-zhujian-wudao-spec.md) |
| 已有洞察库（54 条） | [insights-01-30](.agents/docs/superpowers/specs/2026-06-17-zhujian-wudao-insights-01-30.md) + [insights-31-52](.agents/docs/superpowers/specs/2026-06-17-zhujian-wudao-insights-31-52.md) |
| 已知问题与优先级清单 | [review.md](.agents/docs/superpowers/specs/2026-06-17-zhujian-wudao-review.md) |
| 撰写新洞察的步骤 | [workflows.md](.agents/workflows.md) §工作流一 |
| 执行全面复盘 | [workflows.md](.agents/workflows.md) §工作流二 |
| 什么绝对不能做 | [constraints.md](.agents/constraints.md) |
| Git 提交格式规范 | [git.md](.agents/git.md) |
| 可迁移模式与方法论 | [transferable-patterns.md](.agents/docs/superpowers/specs/2026-06-17-transferable-patterns.md) |
| 报名阶段复盘 | [registration-review.md](.agents/docs/superpowers/specs/2026-06-17-zhujian-wudao-registration-review.md) |

