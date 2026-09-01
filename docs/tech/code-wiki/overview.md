---
type: Wiki Tutorial
source:
  - ../../../AGENTS.md
  - ../../../README.md
  - ../../../.gitmodules
  - ../../../apps/AGENTS.md
  - ../../../projects/AGENTS.md
  - ../../../vendor/AGENTS.md
status: stable
updated_at: 2026-08-23
---

# 仓库总览

## 一句话定位

`SpecWeave` 是一个“多智能体协作工作区规范仓库”，通过 [AGENTS.md](../../../AGENTS.md#L3-L32) 把角色定义、上下文路由、规则体系、自动化脚本、文档资产和子项目生态编织成统一入口。

和传统业务仓库不同，它的核心价值不在某个单独应用，而在于：

- 定义智能体如何进入项目并按需加载上下文。
- 提供一套可执行的规则、协议、模板与工作流。
- 用大量脚本把规则落到自动检查和自动修复上。
- 通过 `apps/`、`projects/`、`vendor/` 承载实验应用、第一方子项目和第三方依赖。

## 顶层结构

| 区域 | 当前角色 | 关键依据 |
|---|---|---|
| `AGENTS.md` | 全仓入口与启动协议 | [AGENTS.md](../../../AGENTS.md#L3-L32) |
| `.agents/` | 规范主权区与脚本实现区 | [AGENTS.md](../../../AGENTS.md#L49-L80) |
| `apps/` | 主仓库内置应用区，可直接修改 | [apps/AGENTS.md](../../../apps/AGENTS.md#L21-L35) |
| `projects/` | 第一方 git submodule 区 | [projects/AGENTS.md](../../../projects/AGENTS.md#L14-L25) |
| `vendor/` | 第三方与协作型依赖区 | [vendor/AGENTS.md](../../../vendor/AGENTS.md#L15-L25) |
| `.trae/specs/` | Spec 驱动开发的过程资产区 | [context-routing.md](../../../.agents/context-routing.md#L53-L55) |
| `docs/` | 唯一文档中心与 Sphinx 站点工程 | [docs/tasks/docs.py](../../../docs/tasks/docs.py#L72-L130) |

## 当前工作树快照

当前 checkout 下最值得关注的内容如下：

- `.agents/`：规范主权区，面向 AI 智能体承载角色、规则、协议、工作流、模板与技能；`.agents/scripts/` 是自动化工具主目录，包含大量顶层 CLI 和 `lib/` 共享库。
- `docs/`：OKF v0.2 唯一文档中心，承载知识库、复盘、标准、模式、工具说明与本 Code Wiki，并通过 Sphinx、MyST、Mermaid 扩展构建对外文档站。
- `apps/`：当前工作树可见内容以 `samples/`、`tests/`、`shared/` 为主。
- `projects/`：当前可见子项目为 `xuanspace` 与 `awesome-okf-xs`，并在 [`.gitmodules`](../../../.gitmodules#L8-L35) 中注册。
- `vendor/`：当前核心依赖为 `flexloop`、`ark-cli`、`awesome-okf*`、`knowledge-catalog`。

## 设计目标

### 1. 统一入口

智能体进入仓库时先读 [AGENTS.md](../../../AGENTS.md#L3-L32)，再根据 [context-routing.md](../../../.agents/context-routing.md#L21-L100) 只加载任务所需规范，避免一次性读取全仓文档造成上下文膨胀。

### 2. 规则即代码

规范并不只存在于文档中，还在 `.agents/scripts/` 中被实现为检查器、生成器、修复器与聚合工具。最典型的例子包括：

- [docgen.py](../../../.agents/scripts/docgen.py#L1-L17)
- [check-links.py](../../../.agents/scripts/check-links.py)
- [build-ref-index.py](../../../.agents/scripts/build-ref-index.py#L171-L210)
- [repo-check.py](../../../.agents/scripts/repo-check.py)

### 3. 分区治理

仓库通过四大区域来区分可修改资产与外部依赖：

- `apps/` 是主仓内资产，可直接编辑。
- `projects/` 是第一方子项目，应遵循子项目自己的 `AGENTS.md`。
- `vendor/` 是第三方或协作型依赖，默认不在主仓直接修改。
- `.agents/` 是主权规范区，保存仓库自己的方法论与执行代码。

### 4. 文档与过程并重

仓库既保存“长期知识资产”，也保存“任务过程资产”：

- 长期知识资产与对外发布内容统一沉淀在根 `docs/` 文档中心（知识库、复盘、模式、标准）
- 面向 AI 智能体的规范与执行资产在 `.agents/`（角色、规则、协议、脚本、技能、模板）
- 任务过程资产在 `.trae/specs/`

## 当前已知差异

### 规范声明比工作树更大

[apps/AGENTS.md](../../../apps/AGENTS.md#L37-L61) 描述了 `docker-images/`、`ai-agents/`、`dev-tools/` 等较完整的应用分组，但当前工作树可见内容并不完全覆盖这些路径。这意味着：

- 规范文件承载的是“目标架构或完整路由视图”。
- 当前 checkout 反映的是“当前拉取到的实际工作树”。

阅读源码时要优先区分这两层含义，避免把路由表里的条目误认为当前一定存在的目录。

### 文档单中心

[global-core-rules.md](../../../.agents/global-core-rules.md#L18-L18) 明确根 `docs/` 是 OKF v0.2 唯一文档中心，承载 Wiki 教程、知识包、复盘报告、模式库与最佳实践，并通过 Sphinx 构建对外站点；`.agents/` 仅承载面向 AI 智能体的规范与执行资产。因此：

- 读知识库、复盘与模式时看 `docs/`（如 `docs/knowledge/`、`docs/retrospective/`）
- 读智能体路由、规则与协议时看 `.agents/`
- 构建公开站点时在 `docs/` 下运行 invoke 任务

## 阅读建议

如果你要快速建立对仓库的正确心智模型，建议按这个顺序：

1. 先读 [AGENTS.md](../../../AGENTS.md#L3-L32) 理解入口协议。
2. 再读 [architecture.md](architecture.md) 建立系统图景。
3. 然后读 [modules.md](modules.md) 看各区域和子系统如何拆分。
4. 最后读 [runtime.md](runtime.md) 和 [debugging.md](debugging.md) 处理实际运行与排障问题。
