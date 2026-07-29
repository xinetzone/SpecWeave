---
id: apps-agents-manifest
version: 1.0
source: SpecWeave 四大区域路由体系优化
---

# Apps 区域智能体契约 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：按「应用路由表」确定本次任务需要进入的应用
> 步骤 3：若应用有自身的 AGENTS.md，进入后读取该文件（嵌套优先）
> 步骤 4：若应用无 AGENTS.md，直接遵循根 .agents/ 规范执行
> 步骤 5：退出 apps/ 目录后，恢复 SpecWeave 主权区路由（回到根 AGENTS.md）
> ```
>
> ⚠️ 本文件是 apps 区域的 AI 智能体入口。apps/ 存放 SpecWeave 主仓库内的**内置应用**，所有文件都在主仓库内直接管理，可直接修改——与 projects/vendor 的 git submodule 机制有本质区别。

## 区域性质

apps/ 存放 SpecWeave 主仓库内的内置应用，与 `projects/`（第一方自有子项目）、`vendor/`（第三方依赖）形成明确区分：

| 目录 | 用途 | 管理方式 | 是否可直接修改 |
|------|------|----------|:---:|
| `apps/` | 主仓库内置应用（直接属于 SpecWeave） | 同仓库直接管理，非 git submodule | ✅ 是 |
| `projects/` | 第一方自有子项目 | git submodule，子模块内开发 | ❌ 否（走子项目流程） |
| `vendor/` | 第三方依赖 | git submodule，第三方代码 | ❌ 否（禁止本地修改） |

> **关键区别**：apps/ 内所有内容都是 SpecWeave 主仓库的一部分，没有 git submodule 隔离，智能体可以直接修改 apps/ 下的任何文件。这是与 projects/vendor 的本质差异——projects/vendor 都是 git submodule，需要遵循子模块流程。

> **.gitignore 策略**：apps/ 目录完全纳入主仓库版本控制，不使用 .gitignore 排除应用内容。

apps/AGENTS.md 由 SpecWeave 主权区维护，直接纳入版本管理；部分应用有自己的 AGENTS.md 和 .agents/ 目录实现自治，部分应用直接遵循根 .agents/ 规范。

## 应用路由表

| 应用 | AGENTS.md 入口 | .agents/ | 说明 |
|------|---------------|:---:|------|
| docker-ssh-dind | [apps/docker-ssh-dind/AGENTS.md](docker-ssh-dind/AGENTS.md) | ✅ 有 | Docker SSH DinD（Docker-in-Docker）环境 |
| jupyter-ssh-base | [apps/jupyter-ssh-base/AGENTS.md](jupyter-ssh-base/AGENTS.md) | ❌ 无 | Jupyter Notebook SSH 基础镜像 |
| pytorch-base | [apps/pytorch-base/AGENTS.md](pytorch-base/AGENTS.md) | ❌ 无 | PyTorch 基础环境镜像 |
| caffe-ffi-jupyter | [apps/caffe-ffi-jupyter/AGENTS.md](caffe-ffi-jupyter/AGENTS.md) | ❌ 无 | Caffe-FFI Jupyter 开发环境（基于jupyter-ssh-base） |
| zhujian-wudao | [apps/zhujian-wudao/AGENTS.md](zhujian-wudao/AGENTS.md) | ✅ 有 | 竹简悟道——道家哲学AI洞察项目 |
| ai-code-assistant | —（遵循根规范） | ❌ 无 | AI 代码助手 Web 应用 |
| camera-power-controller | —（遵循根规范） | ❌ 无 | 摄像头电源控制工具 |
| prompt_extraction | —（遵循根规范） | ❌ 无 | 提示词质量评估与提取工具 |
| shared | —（遵循根规范） | ❌ 无 | 跨应用共享资源目录 |
| tests | —（遵循根规范） | ❌ 无 | 测试用例目录 |
| xmnn-runtime | —（遵循根规范） | ❌ 无 | XMNN 运行时环境 |

### 嵌套优先级

```
SpecWeave 根 AGENTS.md
  └─ apps/AGENTS.md（本文件，apps 区域入口）
       ├─ docker-ssh-dind/AGENTS.md（docker-ssh-dind 应用入口 · 嵌套优先）
       ├─ jupyter-ssh-base/AGENTS.md（jupyter-ssh-base 应用入口 · 嵌套优先）
       ├─ pytorch-base/AGENTS.md（pytorch-base 应用入口 · 嵌套优先）
       ├─ caffe-ffi-jupyter/AGENTS.md（caffe-ffi-jupyter 应用入口 · 嵌套优先）
       └─ zhujian-wudao/AGENTS.md（zhujian-wudao 应用入口 · 嵌套优先）
```

进入任意子目录后，优先读取**离当前工作目录最近**的 AGENTS.md。若应用自身的 AGENTS.md 规则与本文件冲突，以应用的 AGENTS.md 为准（子层覆盖父层）。无自身 AGENTS.md 的应用直接遵循根 .agents/ 规范。

### 路由流程图

```mermaid
flowchart TD
    Start["收到任务"] --> Step1["步骤1：读取 SpecWeave 根 AGENTS.md"]
    Step1 --> Step21{"步骤2.1：工作目录<br/>是否在 apps/ 内？"}
    Step21 -->|"否（主权区任务）"| Step3A["步骤3：读取 .agents/ 对应规范"]
    Step3A --> Step4A["步骤4：在规范指导下选择 Skill 执行"]
    Step4A --> Done1["完成任务"]
    Step21 -->|"是（apps 区域任务）"| Layer2["第二层：读取 apps/AGENTS.md<br/>（apps 区域入口路由）"]
    Layer2 --> SubApp{"步骤2：按应用路由表<br/>确定目标应用"}
    SubApp -.->|"❶ 无匹配项"| E1["确认是否为新增应用<br/>走新增应用流程"]
    E1 -.-> Layer2
    SubApp -->|"有自身 AGENTS.md<br/>（docker-ssh-dind/jupyter-ssh-base/<br/>pytorch-base/caffe-ffi-jupyter/zhujian-wudao）"| Layer3["第三层：读取应用自身 AGENTS.md<br/>（嵌套优先）"]
    SubApp -->|"无自身 AGENTS.md<br/>（ai-code-assistant/camera-power-controller/<br/>prompt_extraction/shared/tests/xmnn-runtime）"| Direct["直接遵循根 .agents/ 规范"]
    Layer3 -.->|"❷ 读取失败"| E2["检查文件是否存在<br/>回退到根规范执行"]
    E2 -.-> Direct
    Layer3 --> Step3B["步骤3：按应用上下文路由表<br/>读取对应规范（若有 .agents/）"]
    Direct --> Step4B["步骤4：在规范指导下直接执行任务<br/>（可直接修改文件）"]
    Step3B --> Step4C["步骤4：在应用规范指导下执行任务<br/>（可直接修改文件）"]
    Step4B -.->|"❸ 需要跨应用资源"| E3["按「跨应用调用规范」访问"]
    Step4C -.->|"❸ 需要跨应用资源"| E3
    E3 -.-> Step4B
    Step4B --> Done2["完成任务"]
    Step4C --> Done3["完成任务"]
    Done2 --> Exit["退出 apps/ 目录"]
    Done3 --> Exit
    Done1 --> Restore["恢复 SpecWeave 路由"]
    Exit --> Restore
    %% 样式分层
    classDef specWeave fill:#e1f5fe,stroke:#0288d1,stroke-width:2px,color:#01579b
    classDef apps fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    classDef appWithAgents fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    classDef appDirect fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    classDef exit fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f
    classDef decision fill:#fff9c4,stroke:#f9a825,stroke-width:2px,color:#f57f17
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px,color:#b71c1c
    class Step1,Step3A,Step4A,Done1 specWeave
    class Layer2,SubApp apps
    class Layer3,Step3B,Step4C,Done3 appWithAgents
    class Direct,Step4B,Done2 appDirect
    class Step21 decision
    class Exit,Restore exit
    class E1,E2,E3 error
```

**关键机制：**

- **实线箭头**（`-->`）主流程；**红色虚线箭头**（`-.->`）异常处理分支，编号 ❶-❸ 对应下方「异常处理分支」表格
- **嵌套优先**：有自身 AGENTS.md 的应用，进入后优先读取应用的 AGENTS.md，应用规则覆盖父级
- **直连模式**：无自身 AGENTS.md 的应用，跳过第三层，直接遵循根 .agents/ 规范执行
- **可直接修改**：apps/ 内所有文件都在主仓库，可直接修改——这是与 projects/vendor 的核心区别
- **退出恢复**：正常完成或异常回退均退出 `apps/` 目录，自动恢复 SpecWeave 路由

## 可用资产索引

apps 区域内有 `.agents/` 目录的应用，其规范资产可被跨应用调用。实际资产存放在各应用内，本索引仅提供路由定位。

### docker-ssh-dind 应用

| 资产 | 路径 | 说明 |
|------|------|------|
| 入门指南 | [docker-ssh-dind/.agents/README.md](docker-ssh-dind/.agents/README.md) | docker-ssh-dind .agents/ 入口 |
| 构建测试规则 | [docker-ssh-dind/.agents/rules/build-test.md](docker-ssh-dind/.agents/rules/build-test.md) | 构建与测试规范 |
| Containerfile 规则 | [docker-ssh-dind/.agents/rules/containerfile.md](docker-ssh-dind/.agents/rules/containerfile.md) | Containerfile/Dockerfile 编写规范 |
| Entrypoint 规则 | [docker-ssh-dind/.agents/rules/entrypoint.md](docker-ssh-dind/.agents/rules/entrypoint.md) | 入口脚本编写规范 |

### zhujian-wudao 应用

| 资产 | 路径 | 说明 |
|------|------|------|
| 约束规范 | [zhujian-wudao/.agents/constraints.md](zhujian-wudao/.agents/constraints.md) | 竹简悟道项目约束 |
| 约定规范 | [zhujian-wudao/.agents/conventions.md](zhujian-wudao/.agents/conventions.md) | 代码与文档约定 |
| 项目说明 | [zhujian-wudao/.agents/project.md](zhujian-wudao/.agents/project.md) | 项目概述 |
| 工作流 | [zhujian-wudao/.agents/workflows.md](zhujian-wudao/.agents/workflows.md) | 工作流程规范 |
| 哲学家角色 | [zhujian-wudao/.agents/roles/philosopher.md](zhujian-wudao/.agents/roles/philosopher.md) | 哲学洞察角色定义 |
| 洞察写作指南 | [zhujian-wudao/.agents/roles/references/insight-writing-guide.md](zhujian-wudao/.agents/roles/references/insight-writing-guide.md) | 洞察文档写作规范 |
| 约束速查表 | [zhujian-wudao/.agents/roles/references/constraints-cheatsheet.md](zhujian-wudao/.agents/roles/references/constraints-cheatsheet.md) | 约束条件速查 |
| 洞察写作技能 | [zhujian-wudao/.agents/skills/zhujian-insight-writer/SKILL.md](zhujian-wudao/.agents/skills/zhujian-insight-writer/SKILL.md) | 洞察写作 Skill |
| 道家学者插画技能 | [zhujian-wudao/.agents/skills/dao-scholar-illustrations/SKILL.md](zhujian-wudao/.agents/skills/dao-scholar-illustrations/SKILL.md) | 道家风格插画 Skill |
| 产品规格 | [zhujian-wudao/.agents/docs/product/2026-06-17-product-spec.md](zhujian-wudao/.agents/docs/product/2026-06-17-product-spec.md) | 产品规格文档 |
| 洞察库索引 | [zhujian-wudao/.agents/docs/insights/_index.md](zhujian-wudao/.agents/docs/insights/_index.md) | 洞察文档索引 |
| 可迁移方法 | [zhujian-wudao/.agents/docs/knowledge-transfer/2026-06-17-transferable-methods.md](zhujian-wudao/.agents/docs/knowledge-transfer/2026-06-17-transferable-methods.md) | 可迁移方法论 |
| 可迁移模式 | [zhujian-wudao/.agents/docs/knowledge-transfer/2026-06-17-transferable-patterns.md](zhujian-wudao/.agents/docs/knowledge-transfer/2026-06-17-transferable-patterns.md) | 可复用设计模式 |

## 边界声明

| 资产 | 归属 | 可直接修改 | 说明 |
|------|------|:---:|------|
| apps/AGENTS.md | SpecWeave 主权区 | ✅ 是 | apps 区域入口路由 |
| apps/README.md | SpecWeave 主权区 | ✅ 是 | apps 目录总览 |
| apps/shared/ | SpecWeave 主权区 | ✅ 是 | 跨应用共享资源 |
| apps/tests/ | SpecWeave 主权区 | ✅ 是 | 全局测试用例 |
| apps/ai-code-assistant/ | 应用自治（遵循根规范） | ✅ 是 | AI 代码助手应用 |
| apps/camera-power-controller/ | 应用自治（遵循根规范） | ✅ 是 | 摄像头电源控制工具 |
| apps/prompt_extraction/ | 应用自治（遵循根规范） | ✅ 是 | 提示词提取工具 |
| apps/xmnn-runtime/ | 应用自治（遵循根规范） | ✅ 是 | XMNN 运行时环境 |
| apps/docker-ssh-dind/ | 应用自治（有自身 AGENTS.md） | ✅ 是 | Docker SSH DinD 环境 |
| apps/docker-ssh-dind/AGENTS.md | 应用自治 | ✅ 是 | docker-ssh-dind 入口 |
| apps/docker-ssh-dind/.agents/ | 应用自治 | ✅ 是 | docker-ssh-dind 规范体系 |
| apps/jupyter-ssh-base/ | 应用自治（有自身 AGENTS.md） | ✅ 是 | Jupyter SSH 基础镜像 |
| apps/jupyter-ssh-base/AGENTS.md | 应用自治 | ✅ 是 | jupyter-ssh-base 入口 |
| apps/pytorch-base/ | 应用自治（有自身 AGENTS.md） | ✅ 是 | PyTorch 基础环境镜像 |
| apps/pytorch-base/AGENTS.md | 应用自治 | ✅ 是 | pytorch-base 入口 |
| apps/caffe-ffi-jupyter/ | 应用自治（有自身 AGENTS.md） | ✅ 是 | Caffe-FFI Jupyter 开发环境 |
| apps/caffe-ffi-jupyter/AGENTS.md | 应用自治 | ✅ 是 | caffe-ffi-jupyter 入口 |
| apps/zhujian-wudao/ | 应用自治（有自身 AGENTS.md） | ✅ 是 | 竹简悟道项目 |
| apps/zhujian-wudao/AGENTS.md | 应用自治 | ✅ 是 | zhujian-wudao 入口 |
| apps/zhujian-wudao/.agents/ | 应用自治 | ✅ 是 | zhujian-wudao 规范体系 |

> **与 projects/vendor 的本质区别**：apps/ 下的所有资产都标记为「✅ 可直接修改」，因为它们都是主仓库的一部分；而 projects/vendor 是 git submodule，标记为「❌ 不可直接修改」。

## 跨应用调用规范

SpecWeave 智能体需要跨 apps 区域调用其他应用资源时：

1. **定位**：通过本文件的「应用路由表」和「可用资产索引」找到目标路径
2. **进入**：若目标应用有自身的 AGENTS.md，读取并遵循其启动协议；若无则直接遵循根规范
3. **执行**：按目标应用的规范执行任务——**可直接读取和修改文件**（与 projects/vendor 不同）
4. **共享资源**：通用共享资源优先放置在 `apps/shared/` 目录
5. **不重复**：相同功能不要在多个应用重复实现，优先抽取到 `apps/shared/` 或根 `.agents/scripts/`

## 异常处理分支

| 异常场景 | 流程图节点 | 触发条件 | 处理方式 |
|----------|-----------|----------|----------|
| 未知应用 | 应用路由表 | 路由表无匹配项 | 确认是否为新增应用；若否，回退到 SpecWeave 主权区路由并提示路径可能有误 |
| 应用 AGENTS.md 读取失败 | 第三层入口 | 读取应用 AGENTS.md 失败或文件不存在 | 回退到直接遵循根 .agents/ 规范执行；可直接修复或补充 AGENTS.md（因为在主仓库内） |
| 需要跨应用资源 | 步骤 4 执行 | 当前应用需要其他应用的资源 | 按「跨应用调用规范」访问目标应用；通用资源优先抽取到 `apps/shared/` |

**通用回退原则**：任何异常无法在应用自治范围内解决时，可直接在主仓库内修复（因为 apps/ 不是 submodule），或回退到 apps/AGENTS.md 层重新路由。与 projects/vendor 不同，apps/ 内的问题可以直接本地解决，不需要反馈给外部团队。

## 新增应用说明

在 apps/ 下新增应用时遵循以下规则：

1. **直接创建目录**：apps/ 是主仓库的一部分，直接 `mkdir apps/<new-app>` 即可，不需要 git submodule 操作
2. **何时需要创建 AGENTS.md**：当应用需要自己的 `.agents/` 目录（包含独立的 roles/rules/skills/workflows 等规范体系）时，才需要创建 `apps/<new-app>/AGENTS.md`
3. **无需 AGENTS.md 的场景**：简单工具、单脚本应用、测试目录等，直接遵循根 .agents/ 规范即可，不需要创建独立的 AGENTS.md
4. **更新路由表**：新增应用后，更新本文件的「应用路由表」，添加对应条目
5. **README.md**：建议为每个应用添加 README.md 说明用途

```bash
# 新增简单应用（无需 AGENTS.md）
mkdir apps/<new-app>
# 直接开发，遵循根 .agents/ 规范

# 新增需要独立规范体系的应用（有 .agents/）
mkdir apps/<new-app>
mkdir apps/<new-app>/.agents
# 创建 apps/<new-app>/.agents/ 下的规范文件
# 创建 apps/<new-app>/AGENTS.md 作为入口
# 更新本文件的应用路由表
```

## 参考链接

- [SpecWeave 根 AGENTS.md](../AGENTS.md) — 主权区入口
- [projects/AGENTS.md](../projects/AGENTS.md) — projects 区域入口路由（git submodule 第一方子项目）
- [vendor/AGENTS.md](../vendor/AGENTS.md) — vendor 区域入口路由（git submodule 第三方依赖）
- [apps/README.md](README.md) — apps 目录总览
