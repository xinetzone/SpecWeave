---
source:
  - ../../../AGENTS.md
  - ../../../apps/AGENTS.md
  - ../../../projects/AGENTS.md
  - ../../../vendor/AGENTS.md
  - ../../scripts/README.md
status: stable
updated_at: 2026-08-23
---

# 模块职责

## 顶层模块矩阵

| 模块 | 当前职责 | 代表入口 |
|---|---|---|
| `AGENTS.md` | 启动协议、区域分流、规范总入口 | [AGENTS.md](../../../AGENTS.md#L3-L32) |
| `.agents/` | 规范主权区、脚本实现区、知识沉淀区 | [AGENTS.md](../../../AGENTS.md#L49-L80) |
| `.trae/specs/` | Spec 驱动开发的过程文档 | [context-routing.md](../../context-routing.md#L53-L55) |
| `apps/` | 内置应用区，可直接修改 | [apps/AGENTS.md](../../../apps/AGENTS.md#L21-L35) |
| `projects/` | 第一方 git submodule 区 | [projects/AGENTS.md](../../../projects/AGENTS.md#L14-L25) |
| `vendor/` | 第三方与协作型依赖区 | [vendor/AGENTS.md](../../../vendor/AGENTS.md#L15-L25) |
| `docs/` | Sphinx 公开文档站工程 | [docs/tasks.py](../../../docs/tasks.py#L54-L128) |
| `bundles/` / `promotion/` / `templates/` | 内容打包、推广与模板资产 | 当前工作树 |

## `.agents/` 子系统

### 规范目录

| 子目录 | 主要职责 |
|---|---|
| `roles/` | 角色定义与职责边界 |
| `modules/` | 自我演进模块定义 |
| `prompts/` | 系统提示词与 few-shot |
| `protocols/` | 协作协议、路由协议、工作区发现与提示词自举 |
| `rules/` | 全局治理、阶段守卫、内容分级、硬编码治理等 |
| `workflows/` | 功能开发、代码审查、测试流程 |
| `templates/` | 任务、交接与图表模板 |
| `skills/` | 规范化 Skill 门面 |
| `teams/` / `worlds/` | 团队协作与环境治理 |
| `docs/` | 知识库、复盘、项目文档、Code Wiki |

### 脚本目录

`.agents/scripts/` 是整个仓库最重要的执行层，按职责可以分成 4 类：

| 类别 | 代表文件 | 说明 |
|---|---|---|
| 聚合 CLI | `docgen.py`、`repo-check.py`、`agents.py` | 统一入口，负责参数解析与流程编排 |
| 检查器 | `check-links.py`、`check-gitignore.py`、`check-duplication.py` | 把规则落到自动验证 |
| 生成器/修复器 | `build-ref-index.py`、`generate-readme.py`、`finalize-atomization.py` | 生成导航、索引、报告或做批量修复 |
| 子系统包 | `lib/`、`sg_dashboard/`、`mdi/` | 共享库与较完整的领域实现 |

速查表来源见 [scripts/README.md](../../scripts/README.md#L24-L53)。

## `.agents/scripts/lib/` 共享库

`lib/` 不是杂项目录，而是脚本生态的复用中心。可以按“基础设施”和“领域能力”两类理解。

### 基础设施模块

| 模块 | 职责 | 关键入口 |
|---|---|---|
| `project.py` | 解析项目根、`.agents/` 和脚本目录路径 | [resolve_project_root()](../../scripts/lib/project.py#L18-L53) |
| `cli.py` | 安全输出、CLI 通用选项与打印行为 | `lib/cli.py` |
| `atomic_write.py` | 原子写入文本和缓存 | `lib/atomic_write.py` |
| `frontmatter.py` | 统一 YAML/TOML frontmatter 解析 | [parse_frontmatter_unified()](../../scripts/lib/frontmatter.py#L508-L536) |
| `markdown.py` | 标题、摘要、链接与 marker 区更新 | `lib/markdown.py` |
| `cache.py` | JSON 缓存与 TTL 管理 | `lib/cache.py` |

### 领域能力模块

| 模块 | 职责 | 关键入口 |
|---|---|---|
| `link_fixer/` | 断链检测与自动修复 | [fix_broken_links()](../../scripts/lib/link_fixer/cli.py#L32-L110) |
| `spec_loader.py` | 规范渐进式加载 | [SpecLoader](../../scripts/lib/spec_loader.py#L376-L497) |
| `stage_guardrails/` | 阶段状态机、边界校验、运行时拦截 | [StageStateManager](../../scripts/lib/stage_guardrails/state/manager.py#L21-L115) |
| `quality_report.py` | 质量结果聚合与统计 | `lib/quality_report.py` |
| `duplication.py` | 跨文件重复块检测 | `lib/duplication.py` |
| `checks/` | 可组合的轻量检查器 | `lib/checks/` |

## `sg_dashboard/` 子系统

`sg_dashboard/` 是一个独立的“日志解析 -> 统计聚合 -> HTML 展示”子系统：

| 文件 | 职责 |
|---|---|
| `models.py` | 定义 `LogEntry`、`SessionStats`、`AggregateStats` 三个 dataclass |
| `parser.py` | 解析 SG-LOG/PDR-LOG 文本日志 |
| `aggregator.py` | 把日志聚合到会话与全局统计 |
| `renderer.py` | 渲染自包含 HTML 报表 |
| `cli.py` | 聚合整个子系统的命令入口 |

核心数据模型见 [models.py](../../scripts/sg_dashboard/models.py#L25-L107)，日志解析入口见 [parser.py](../../scripts/sg_dashboard/parser.py#L29-L77)。

## `apps/` 区域

### 规范角色

[apps/AGENTS.md](../../../apps/AGENTS.md#L21-L35) 将 `apps/` 定义为主仓库内置应用区，理论上包含 `docker-images/`、`ai-agents/`、`dev-tools/`、`samples/` 等分组。

### 当前工作树

当前 checkout 中可见内容以这些目录为主：

| 目录 | 当前职责 |
|---|---|
| `apps/samples/cow-demo/` | C++ COW 读写分离示例 |
| `apps/tests/onnx_adaround/` | ONNX 量化相关 Python 包与测试 |
| `apps/shared/` | 共享占位目录 |

这意味着 `apps/AGENTS.md` 更像“完整路由蓝图”，而当前工作树只包含其中一部分实现。

## `projects/` 区域

`projects/` 存放第一方子项目，当前路由和实际登记基本一致：

| 子项目 | 当前定位 | 代表入口 |
|---|---|---|
| `xuanspace` | Python 3.14.6+ monorepo 工程 | [projects/xuanspace/pyproject.toml](../../../projects/xuanspace/pyproject.toml#L5-L119) |
| `awesome-okf-xs` | OKF 文档库子项目 | [projects/AGENTS.md](../../../projects/AGENTS.md#L27-L33) |

其中 `xuanspace` 自带 `tools/xs/` CLI，[`xs` 命令入口](../../../projects/xuanspace/tools/xs/pyproject.toml#L37-L38) 指向 `xs.cli:app`。

## `vendor/` 区域

`vendor/` 既是依赖区，也是外部方法论资产区。当前登记来自两份权威来源：

- [vendor/AGENTS.md](../../../vendor/AGENTS.md#L27-L39)
- [`.gitmodules`](../../../.gitmodules#L1-L35)

按作用可分为：

| 子模块 | 类型 | 当前作用 |
|---|---|---|
| `vendor/flexloop` | 协作型依赖 | 提供可跨边界调用的技能与规则资产 |
| `vendor/ark-cli` | 第三方只读依赖 | CLI 工具 |
| `vendor/awesome-okf*` | 第三方只读依赖 | OKF 生态工具与模板 |
| `vendor/knowledge-catalog` | 第三方只读依赖 | 知识目录相关项目 |

## `.trae/specs/` 过程资产区

`.trae/specs/` 保存的是任务执行过程中的规格文档，而不是最终长期知识。当前工作树里能看到大量 `*-okf-wiki`、`*-wiki`、`*-fix` 等主题目录，说明这个仓库长期用 Spec 驱动方式沉淀任务过程。

## `docs/` 站点工程

根 `docs/` 目录的职责很明确：

- 保存公开站点的内容页
- 通过 [tasks.py](../../../docs/tasks.py#L54-L128) 调用 Sphinx make-mode
- 和 `.agents/docs/` 形成“公开站点”与“知识主容器”的职责分工

## 模块观察结论

- `.agents/` 是仓库的主体，`apps/`、`projects/`、`vendor/` 更像承载层。
- `.agents/scripts/lib` 是整个脚本生态的复用重心，很多顶层脚本只是门面。
- `apps/` 路由文件包含比当前 checkout 更完整的目标结构，使用时要区分“蓝图”与“实况”。
