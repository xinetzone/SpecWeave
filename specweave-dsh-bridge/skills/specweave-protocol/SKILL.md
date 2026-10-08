---
name: specweave-protocol
description: "SpecWeave 启动协议、内容敏感度分流与产出物路径纪律参考。进入 SpecWeave 工作区执行任务前先加载，用于在读取规范文件、判定公开/私域、确定落盘位置与子区域路由时对齐仓库约定。"
source: "AGENTS.md#启动协议 + .agents/global-core-rules.md + .agents/rules/content-sensitivity-precheck.md"
user-invocable: true
---

# SpecWeave 启动协议参考

本技能是 SpecWeave 工作区 `AGENTS.md` 启动协议的**只读摘要**，用于快速对齐入口纪律。
规范真源始终是工作区磁盘上的 `AGENTS.md` 与其路由到的 `.agents/` 规范文件；
本摘要与磁盘原文冲突时，一律以磁盘原文为准。

## 一、启动协议（PRIORITY ZERO）

收到任务后按顺序执行，**不得跳步**：

1. **读取**：用文件读取工具从磁盘读取工作区根 `AGENTS.md` **全文**，不得只依赖会话内联副本。
   读取后确认三个锚点：① 首部存在「启动协议」标题块；② 明确声明 `docs/` 为唯一文档中心；
   ③ 声明内容敏感度预检产出物入根 `docs/`。缺任一锚点即视为读取失败，须重读。
2. **路由**：按 `.agents/context-routing.md` 确定本次任务必读规范。
   先做 **vendor 方法论资产预检**——即使工作目录不在 `vendor/` 内，只要任务类型命中
   （如 Skill 创建/优化），也必须读取对应的 vendor 方法论资产。
3. **敏感度分流**：判定分析对象/产出物的内容级别（详见第三节）。
4. **自检**：确认 vendor 预检、敏感度预检、入口读取、Skill 加载判断四项均已完成后，
   才允许加载 Skill 或生成产出物。

## 二、子区域嵌套路由

工作目录落在 `apps/`、`projects/`、`vendor/` 之下时，进入对应的子区域入口路由，遵循「嵌套优先」：

| 区域 | 入口 | 可否直接修改 |
|---|---|---|
| `apps/` | `apps/AGENTS.md` | ✅ 主仓库直接维护 |
| `projects/` | `projects/AGENTS.md` | ❌ git submodule，走子项目流程 |
| `vendor/` | `vendor/AGENTS.md` | ❌ 第三方，禁止本地修改 |

退出子区域后恢复 SpecWeave 主权区路由。

## 三、内容敏感度分流

| 级别 | 判定信号 | 工作流与落盘 |
|---|---|---|
| 公开内容 | 公开网页、开源代码、官方文档、公开新闻 | 标准工作流；Spec 规划入 `.trae/specs/<主题>/`，产出物入根 `docs/` |
| 私域内容 | 内部会议记录、带 `share?code=`/`token=` 的私域链接、个人笔记、商业培训、含隐私/商业秘密 | 跳过 `.trae/specs/`，产出物直接入 `playground/` 或用户指定目录 |

不确定时**就高不就低**，默认按私域处理，或向用户确认。

## 四、产出物路径纪律（落盘前三查）

1. 查目标目录是否在根 `docs/`（公开）或 `playground/`（私域）之下。
2. 查同类产出物的现有位置（参考同类索引/看板），不要新造平行目录。
3. 查所依据的规范是否为磁盘原文——内联副本可能过期，冲突时以磁盘原文为准。

**禁止**：向 `.agents/docs/` 写入任何产出物（该路径随 2026-08-31 整体迁移已废止）；
用 DOCX 替代 Markdown；把产物丢在仓库根或临时目录。

## 五、配套工具与命令

| 入口 | 用途 |
|---|---|
| `specweave_route` 工具 | 任务描述 → 规范入口路径（含子区域与 stale 校验） |
| `specweave_status` 工具 | 报告工作区根、子区域、入口与产出物路径纪律 |
| `specweave_check` 工具 | 返回提交前校验命令（不代为执行，执行用 `pwsh`） |
| `specweave_protocol` 工具 | 技能目录不可用时的协议兜底入口 |
| `/specweave status \| route <任务> \| help` | 人机命令面 |

## 六、校验门禁

提交前按变更类型执行对应校验（命令由 `specweave_check` 给出）：

- 链接与引用：`python .agents/scripts/check-links.py --path <变更目录>`
- Mermaid 图表：`python check_mermaid.py`
- 忽略规则：`python .agents/scripts/check-gitignore.py`
- 重复代码：`python .agents/scripts/check-duplication.py`
- 原子化覆盖：`python .agents/scripts/check-atomization-coverage.py`
- 全量：`.agents/scripts/ci-check.ps1`（Windows）/ `.agents/scripts/ci-check.sh`
