# apps/ 文件夹系统性分组重构 Spec

## Why

`apps/` 目录当前是 20 个一级条目的纯扁平结构（17 个应用 + shared/tests/.agents/AGENTS.md/README.md），7 个 Docker 镜像类应用、AI 应用、开发工具、示例原型混杂在同一层级，无任何分类。新用户/智能体无法快速定位某类应用，扩展时无分组规则可循，违背模块化设计与可维护性原则。

## What Changes

- 将 apps/ 下 17 个应用按**应用类型**归入 4 个分组子文件夹：
  - `apps/docker-images/`（7 个容器镜像类）：devcontainer-base, docker-ssh-dind, jupyter-ssh-base, pytorch-base, caffe-ffi-jupyter, caffe-ffi-cross, xmnn-runtime
  - `apps/ai-agents/`（3 个 AI 应用类）：ai-code-assistant, eve-minimal-agent, zhujian-wudao
  - `apps/dev-tools/`（2 个开发工具类）：camera-power-controller, prompt_extraction
  - `apps/samples/`（3 个示例/原型类）：cow-demo, short-video-site, zleap-workspace-first-prototype
- `apps/` 根级保留：`AGENTS.md`、`README.md`、`.agents/`、`shared/`、`tests/`（治理层，不移动）
- 同步更新所有**活跃引用**中的旧路径 `apps/<app>/` → `apps/<group>/<app>/`，包括：
  - `apps/AGENTS.md`（应用路由表、边界声明、嵌套优先级、流程图）
  - `apps/README.md`（应用清单、目录结构）
  - `apps/.agents/README.md`（目录结构示意）
  - 各应用内部 AGENTS.md（如 devcontainer-base/docker-ssh-dind 中的路由层级示意）
  - 根 `.agents/`（context-routing.md、capability-registry、checklists、docs/code-wiki、docs/tools/docker-cache.md 等）
  - 各应用内部文档与脚本中的 `apps/<app>/` 路径引用
- **BREAKING**：应用目录物理位置从 `apps/<app>/` 变更为 `apps/<group>/<app>/`；依赖这些路径的外部命令、脚本、文档链接需同步更新
- 不追改 `.trae/specs/` 历史规范文档中的旧路径（历史快照保持原样）

## Impact

- Affected specs: `core-foundation/create-apps-directory`、`devcontainer-base` 系列（目录移动，行为不变）
- Affected code（活跃引用更新）：
  - `apps/AGENTS.md`、`apps/README.md`、`apps/.agents/README.md`
  - 各应用内 AGENTS.md、docs、scripts（含 `/SpecWeave/apps/...` 绝对路径引用）
  - 根 `.agents/context-routing.md`、`.agents/docs/code-wiki/*`、`.agents/docs/tools/docker-cache.md`、`.agents/checklists/conda-build-best-practices.md`、`.agents/capability-registry/*`
- 不受影响：`projects/`、`vendor/`、`.trae/specs/` 历史文档、Docker 镜像构建行为（跨应用依赖是镜像标签非路径）

## ADDED Requirements

### Requirement: 应用类型分组目录
系统 SHALL 将 apps/ 下 17 个应用按应用类型归入 4 个分组子文件夹（docker-images/ai-agents/dev-tools/samples），各分组内应用目录名保持不变。

#### Scenario: 成功分组
- **WHEN** 完成分组后列出 `apps/` 一级目录
- **THEN** 一级目录为：AGENTS.md、README.md、.agents/、shared/、tests/、docker-images/、ai-agents/、dev-tools/、samples/，且每组下应用齐全无遗漏

### Requirement: 活跃引用同步更新
系统 SHALL 更新所有活跃文档/脚本中对 `apps/<app>/` 旧路径的引用为新路径 `apps/<group>/<app>/`，保证链接与路径正确。

#### Scenario: 链接可解析
- **WHEN** 运行链接检查（link-check）扫描 apps/ 与根 .agents/ 活跃文档
- **THEN** 旧路径 `apps/<app>/` 不再出现在活跃文件中，新路径均可解析

### Requirement: 功能等价性保持
系统 SHALL 保证分组后各应用功能不变：Docker 构建、Python 测试、脚本执行均不受目录移动影响。

#### Scenario: 构建与测试验证
- **WHEN** 在分组后的目录中执行代表性验证（如 pytest、Dockerfile 解析、脚本路径检查）
- **THEN** 与分组前结果一致，无因路径变更导致的失败

## MODIFIED Requirements

### Requirement: apps 路由与索引（apps/AGENTS.md、apps/README.md）
原扁平索引更新为分组索引：应用路由表、边界声明、嵌套优先级树、README 应用清单均改为分组路径 `apps/<group>/<app>/`，并按分组小节组织。

## REMOVED Requirements

（无功能移除；仅物理路径层级变更）

## 非目标（Out of Scope）

- 不重命名任何应用目录本身
- 不追改 `.trae/specs/` 历史快照中的旧路径
- 不改动 `camera-power-controller/` 内指向旧 `d:/AI/apps/...` 的历史绝对路径（与本次路径变更无关的遗留）
- 不进行应用内部代码重构（仅移动目录 + 更新引用）
