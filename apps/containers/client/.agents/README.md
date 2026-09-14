---
id: "jupyter-podman-client-agents-readme"
title: "jupyter-podman-client AI 资产容器"
source: "AGENTS.md#嵌套路由关系"
---
# jupyter-podman-client - .agents 目录

本目录是 `apps/containers/client`（jupyter-podman 镜像消费端）的 AI 协作者资产容器，
存放项目特有的规则、角色、技能、脚本、工作流和模板。

本项目的定位与构建端（`apps/containers/jupyter-podman-rootless`）不同：
- 本项目是 **消费端**：根运行路径没有构建流程、没有 ML 模型管理能力；编排为 SDK→CLI 两层降级
- 本项目的核心差异能力是 **Windows 11 × WSL2 跨平台 SDK 连接** + **rootless 三必需硬编码** + **两层后端自动降级（SDK → CLI fallback）**
- 2026-09-13 起增加第 4 个规则主题：opt-in 的 `quant.*` 工作负载栈（podman-compose 子进程层，Windows 原生门禁）；根运行路径仍不引入 compose
- 2026-09-14 起增加第 5 个规则主题：opt-in 的 `xmnn.*` 开发/打包栈（同族 podman-compose 子进程层；双 ABI + LLVM 22 + Nuitka wheel 打包 + 源码运行时挂载）
- 因此本目录下的 `rules/` 保留消费端独有的 5 个主题文件；其余构建端主题（Containerfile/entrypoint/ml-models 等）一律不重复，相关需求回退到父级工作区

## 目录结构

```
.agents/
├── README.md              ← 本文件（资产容器索引）
├── CHANGELOG.md           ← 项目变更日志（原子提交汇总，七概念链路归档）
├── rules/                 ← 项目特有规则（单一职责，按主题拆分；5 个实文件 = 消费端独有）
│   ├── invoke-tasks.md    ← invoke 任务开发规范（两层后端架构、命名空间、CLI fallback 承诺）
│   ├── sdk-connection.md  ← podman-py SDK 连接硬约束（6 scheme 白名单、四策略逃生舱、Windows base_url 必显式）
│   ├── windows-wsl.md     ← Windows 11 × WSL2 支持规范（3 级发行版探测、UTF-16 LE、W-I1~W-I3）
│   ├── quant-overlay.md   ← quant.* podman-compose 量化栈规范（双门禁、三必需映射、深合并、镜像守卫契约）
│   └── xmnn-overlay.md    ← xmnn.* podman-compose 开发/打包栈规范（双 ABI、源码运行时挂载、Nuitka 打包契约）
├── roles/                 ← （预留占位；未定义 → 回退 SpecWeave 根 7 角色）
├── skills/                ← （预留占位；未定义 → 回退 SpecWeave 根 skills/）
├── scripts/               ← （预留占位；未定义 → 回退 SpecWeave 根 .agents/scripts/）
├── workflows/             ← （预留占位；未定义 → 回退 SpecWeave 根 workflows/）
├── templates/             ← （预留占位；未定义 → 回退 SpecWeave 根 templates/）
└── docs/                  ← （预留占位；⚠️ 不写任何产出物；人类文档在 ../README.md，公开知识在根 docs/）
```

**关于 `docs/` 占位目录的特别说明**：`apps/containers/client/.agents/docs/` 是保留的占位目录（gitkeep 空），
遵循 SpecWeave 根 AGENTS 文档边界声明——对外可读文档一律入根 `docs/` 或应用根 `README.md`，
**禁止** 在本 `.agents/docs/` 下写入任何报告/复盘/Wiki。

## 项目核心资产（AI 协作者必读）

除 `.agents/rules/` 下的 5 个规则文件外，AI 协作者还必须同步了解以下源代码真源，
**文档与代码冲突时一律以源代码为准**：

| 资产 | 路径 | 说明 |
|------|------|------|
| Invoke 命名空间入口 | [../src/jpman_client/tasks/__init__.py](../src/jpman_client/tasks/__init__.py) | ns configure：根命名空间 + `container.*` 聚合别名 + `env.*` 自举命名空间 |
| 工具函数 + Windows 探测层 | [../src/jpman_client/tasks/utils.py](../src/jpman_client/tasks/utils.py) | ContainerConfig / sdk_strategy_from_env / sdk_base_url_candidates / wsl_distro_name / windows_diagnose_hint / to_posix_path |
| 连接主入口 + 多候选循环 | [../src/jpman_client/tasks/client_core.py](../src/jpman_client/tasks/client_core.py) | `@contextmanager get_client()`（两层后端、`yield None` 行为承诺、失败汇总表） |
| 人类 CLI 入口 + .env 加载 | [../src/jpman_client/tasks/manage.py](../src/jpman_client/tasks/manage.py) | `load/run/stop/status/clean/images` 6 个根任务 + 容器级 `container.*` 命名空间 |
| 容器内自举任务 | [../src/jpman_client/tasks/env_in_container.py](../src/jpman_client/tasks/env_in_container.py) | `env.*` 三任务（build-layer / run-cmd / shell）+ `PODMAN_SERVICE_BOOT`（容器内 podman service 自举） |
| quant 工作负载栈任务 | [../src/jpman_client/tasks/quant.py](../src/jpman_client/tasks/quant.py) | `quant.*` 六任务（build/up/down/ps/logs/smoke），podman-compose 子进程层，双门禁，禁 import podman |
| xmnn 开发/打包栈任务 | [../src/jpman_client/tasks/xmnn.py](../src/jpman_client/tasks/xmnn.py) | `xmnn.*` 八任务（build/up/down/ps/logs/smoke/build-tvm/wheel），同族双门禁，源码路径硬校验，禁 import podman |
| 量化叠加层资产 | [../overlays/onnx-quantized/](../overlays/onnx-quantized/README.md) | Containerfile.quantized + compose.yaml/compose.gpu.yaml + smoke/（守卫+3 冒烟）+ .env.example + docs/ |
| xmnn-dev 叠加层资产 | [../overlays/xmnn-dev/](../overlays/xmnn-dev/README.md) | Containerfile.xmnn-dev + compose.yaml + builder/（自包含打包内核）+ smoke/ + scripts/ + .env.example |
| invoke 入口转发器 | [../tasks.py](../tasks.py) | 根 `tasks.py` 仅转发至 `jpman_client.tasks`（src 布局下 invoke 的入口发现锚点） |
| Python 依赖声明 | [../pyproject.toml](../pyproject.toml) | invoke>=2 / podman>=5 / python-dotenv>=1；scikit-build-core；`[compose]` extra = podman-compose（quant.* 专用） |
| 环境变量模板（四清单） | [../.env.example](../.env.example) | 容器级 9 项 + SDK 级 4 项 + quant 栈 12 项 + xmnn 栈 17 键（16 生效 + 注释态 BASE_IMAGE）完整带注释 |
| 人类可读文档入口 | [../README.md](../README.md) | 安装/快速开始/§5 Windows WSL/§8 .env 完整清单 |

## 人类文档 ↔ AI 规则对应关系表

`README.md`（人类用户视角）与 `.agents/rules/`（AI 协作者硬约束）双向锚定，
修改一方必须同步更新另一方：

| 人类文档章节 | 对应 AI 规则文件 | 同步锚点（修改时必须一一核对） |
|------------|----------------|------------------------------|
| [README §5 Windows 11 × WSL2 支持](../README.md#5-windows-11--wsl2-支持) | [windows-wsl.md](rules/windows-wsl.md) | §5.1 三路径矩阵、§5.2 四级优先级、§5.3 四策略值、§5.4 速查表（Windows 原生坑 W-I1~W-I3 + 容器内坑 C-I1/C-I2，共 5 条） |
| [README §5.5 A/B 维度分离表](../README.md#55-挂载路径-vs-连接-urlab-维度分离避免混淆) | [windows-wsl.md](rules/windows-wsl.md) §2 + [sdk-connection.md](rules/sdk-connection.md) §1 | Dimension A / B 两张表的函数名、功能描述、所在行号 |
| [README §7 内置纪律 rootless 三必需](../README.md#7-内置纪律rootless-三必需参数) | [invoke-tasks.md](rules/invoke-tasks.md) §3 + AGENTS §约束速览 C3 | 三必需参数值、禁止 --privileged |
| [README §8 .env 完整清单](../README.md#8-env-配置完整清单) | [sdk-connection.md](rules/sdk-connection.md) §3 | 容器级 9 项 + SDK 级 4 项变量名、默认值、优先级顺序 |
| [README §6 作为 SDK 使用](../README.md#6-作为-sdk-使用python-import) | [invoke-tasks.md](rules/invoke-tasks.md) §4 | load_image / run_container / stop_container 三个 API 签名与 ContainerConfig 字段 |
| [README §9 与 jpman 分工表](../README.md#9-与-jpman-cli-的分工) | （无对应 AI 规则；仅属于人类产品定位说明） | 不一致时以本项目 `pyproject.toml` 实际依赖 + `src/jpman_client/tasks/` 实际实现为准 |
| [overlays/onnx-quantized/README.md](../overlays/onnx-quantized/README.md)（量化工作负载栈） | [quant-overlay.md](rules/quant-overlay.md) | quant.* 六任务、双门禁、三必需 compose 映射、GPU 覆盖 list 追加、镜像守卫五包版本、smoke 双路径 |
| [overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md)（开发/打包栈） | [xmnn-overlay.md](rules/xmnn-overlay.md) | xmnn.* 八任务、双 ABI 工具链、四源码 bind、build-tvm/wheel 长任务、AST 还原、SONAME 守卫、双冒烟 |

## 父级继承（所有未定义一律回退）

所有未在本目录定义的规则、角色、技能、脚本、工作流、模板，
**一律逐级回退**，不做任何本地重写：

| 层级 | 入口路径 | 提供的资产 |
|------|---------|-----------|
| L1 apps 容器组 | `apps/containers/.agents/`（预留；当前不存在，直接跳 L2） | apps/containers 组级共享规则（预留） |
| L2 apps 应用区 | [../../../AGENTS.md](../../../AGENTS.md) | apps 总入口、应用路由表 |
| L3 SpecWeave 根（最上层） | [../../../../AGENTS.md](../../../../AGENTS.md) | 全局启动协议、沟通语言、提交规范、修复闭环三阶段、路径引用规则 |
| （根规则） | [../../../../.agents/global-core-rules.md](../../../../.agents/global-core-rules.md) | 全局核心规则（内容敏感度预检、嵌套路由回退链） |
| （根 Skill） | [../../../../.agents/skills/](../../../../.agents/skills/) | seven-concepts-cmd / jpman-podman-ops / atomic-commit-cmd / check-duplication-cmd / ci-check-cmd 等 L1 门面 |
| （根命令） | [../../../../.agents/commands/](../../../../.agents/commands/) | seven-concepts / retrospective / insight / extraction / first-principles / adversarial-review / atomic-commit / atomization |
| （根脚本共享库） | [../../../../.agents/scripts/lib/](../../../../.agents/scripts/lib/) | Python 共享函数（禁止重复实现，新增脚本前必先 lib/README.md 查重） |

## 新增规则的标准流程

需要在 `.agents/rules/` 下**新增**主题文件时（不允许修改现有 4 文件的职责边界；
新增只能加，不能把现有文件中的规则抽出来拆分）：

1. 走七概念方法论（至少 I→F→V→C）：
   - **I（洞察）**：明确现有 3 文件为什么覆盖不了，给出具体反例（如"X 场景下改了 Y 文件但 3 份规则都没提"）
   - **F（第一性原理）**：单文件 = 单一职责；新文件标题必须能被一句话概括（如"镜像缓存策略规范"）
   - **V（对抗审查）**：回退到父级是否已有同名规则？会不会和 README 某章产生双写漂移？
2. 在本文件 `rules/` 目录结构段与上方「人类文档 ↔ AI 规则对应关系表」同步新增条目
3. 在 AGENTS.md「上下文路由表」+「核心规范入口」+「项目约束速览 C#」三处同步新增索引
4. 在 README.md 对应章节的末尾加一句「对应 AI 硬约束详见 .agents/rules/xxx.md」双向锚点

## 变更日志

完整条目见 [CHANGELOG.md](CHANGELOG.md)。

- 2026-09-14 | feat | 新增第 5 个规则文件 xmnn-overlay.md（xmnn.* 开发/打包栈，C12）；overlays/xmnn-dev 落盘（双 ABI 工具链镜像 + 自包含打包内核 + 8 任务），规格见 .trae/specs/xmnn-dev-overlay/
- 2026-09-13 | feat/refactor | 新增第 4 个规则文件 quant-overlay.md（quant.* podman-compose 工作负载栈，C11）；onnx-quantized 完整迁移至 overlays/onnx-quantized（薄叠加镜像+compose 栈+6 任务），machine E2E 全通过
- 2026-09-10 | fix | 补全容器内 EACCES（C-I2）诊断与修复闭环（socket 属组自适应）；`inv load` / `inv run` 增加 podman 就绪预检与中文提示
- 2026-09-09 | fix | B-scheme 宿主 socket 直通端到端连通；`inv load` 镜像缓存完整性校验；`ensure_known_hosts` / `refresh_host_keys` 修复
- 2026-09-08 | feat/fix | 默认目标镜像泛化为 `jupyter-podman-client` 管理枢纽（2.82 GB → 1.80 GB）；修复非 root entrypoint 致 `chpasswd` 失败退出；修复容器内 SDK socket ENOENT（C-I1）
- 2026-09-07 | feat | 初始化 client 端 AI 资产容器：AGENTS.md + .agents/README + 3 rules（invoke-tasks / sdk-connection / windows-wsl）+ CHANGELOG；对齐 README.md §5 WSL 支持与 .env.example 双文档；同时完成 `tasks/` → `src/jpman_client/tasks/` 布局迁移与 `env.*` 自举命名空间新增
- 2026-08-31 | init | 消费端首次拆分；目录结构预留（本 changelog 条目倒推补录）
