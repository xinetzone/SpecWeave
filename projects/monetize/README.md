---
title: "monetize · 变现执行工作区容器"
date: 2026-09-23
updated: 2026-09-23
source: "参考实现：projects/monetize/zhihu-monetization/（规划与审查记录：.trae/specs/create-zhihu-monetization-workspace/）；区域索引：projects/README.md、projects/AGENTS.md"
tags: [变现, 执行工作区, 容器, 主题注册表]
---

# monetize · 变现执行工作区容器

> **本容器是什么**：`projects/monetize/` 是个人变现的**执行工作区容器**——每个变现主题（平台/赛道）在此建一个**主题工作台**，承载该主题的执行状态与记录；定义与知识始终留在各自信源，容器与工作台**只链接不复制**。
> **形态**：主仓库直接跟踪的普通目录（非 git 子模块），已登记于[区域索引](../README.md)与[区域路由](../AGENTS.md)。
> **智能体入口**：[AGENTS.md](AGENTS.md)（主题路由表 + 全容器纪律红线）。
> **运营与演进**：[roadmap.md](roadmap.md)（容器级运营节奏 / 知识回流 / 主题扩增与归档 / 形态演进）。

## 一、主题注册表

| 主题 | 工作台入口 | 状态 | 说明 |
|---|---|---|---|
| zhihu-monetization | [AGENTS.md](zhihu-monetization/AGENTS.md) · [README.md](zhihu-monetization/README.md) | 已就绪 | 知乎变现执行工作台（参考实现）：定义层 = docs 路径报告；知识层 = OKF bundle；含执行台账 / 记录表 / 内容规划 / 数据隔离 |

> 新增主题时在此登记（步骤见 §三）。

## 二、主题工作台标准形态

自参考实现 zhihu-monetization 萃取，经独立对抗审查验证：

**目录骨架**：

```text
<theme>/
├── README.md        # 入口：定位 / 链接矩阵 / 每日用法 / 时效与防画饼声明
├── AGENTS.md        # 智能体入口：文件地图 / 读写纪律 / 纪律传导 / 路由
├── tracker.md       # 执行台账：行项勾选 + 日期戳 + 周期节奏 + 触发器 + 复核锚点
├── records.md       # 记录表：到账 / 周核对 / 复盘 / 发布自检留痕（模板 + 占位）
├── .gitignore       # local/ 数据隔离规则
└── local/
    └── README.md    # 隔离区机制说明（唯一入库文件；其余内容不入库）
```

> 可选扩展：**内容与选题规划**（`content-plan.md` + `local/` 填写版）——内容型主题按需引入（参考实现已引入）。

**五条设计公理**：

1. **单一事实来源**——定义在公开文档、知识在知识库（OKF bundle 或等价物）、执行状态在工作台；三者互不复制，跨层引用一律相对链接回源；
2. **数字必须溯源**——一切平台口径数字挂事实编号（F 编号或等价物）并链接出处；零无源数字；
3. **数据边界**——模板与机制入库，真实数据零入库（`local/` 隔离，由 `.gitignore` 保障）；
4. **时效应答**——`rule_snapshot` 登记规则时点、`stale_after` 设定强制复核线，并传导到入口与台账；引用规则前回源复核当期版本；
5. **防画饼**——池规模 ≠ 个人收益；个人实得以到账记录为唯一事实源；不提供期望值。

## 三、新增主题步骤

1. **信源底座确认**：明确该主题的**定义层**（公开文档/报告）与**知识层**（知识库）；无信源时先做信源采集，禁止在工作台内编造；
2. **复制标准形态**：按 §二骨架建 `<theme>/` 六个文件（可自 zhihu-monetization 复制，逐文件替换 frontmatter `source`）；
3. **登记**：在本 README §一与 [AGENTS.md](AGENTS.md) 主题路由表各加一行；
4. **验证**：相对链接可达、`git check-ignore` 隔离生效、零敏感路径、平台数字全部挂溯源编号；
5. **提交**：工作台文件与登记行按原子提交规范一并提交。

## 四、与区域的关系

- **路由链**（嵌套优先）：[projects/AGENTS.md](../AGENTS.md) → [monetize/AGENTS.md](AGENTS.md)（本容器）→ 各主题工作台 `AGENTS.md`；
- **修改权限**：本容器与各主题工作台均属 SpecWeave 主权区（✅ 可直接修改）；`local/` 为本地隔离区（禁入库）——边界明细见 [projects/AGENTS.md](../AGENTS.md)「边界声明」。