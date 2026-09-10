# jupyter-podman-client - AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文（含首部「启动协议」四个字）
> 步骤 2：确认父级工作区 — 本项目是 SpecWeave apps/containers/ 下的消费端子应用，
>         全局规则继承自 SpecWeave 根 AGENTS.md 与 apps/AGENTS.md（应用区入口路由）
> 步骤 3：按「文档边界」声明：本项目对外的人类可读文档以根 README.md 为唯一入口；
>         AI 级硬约束以本文件路由表指向的 .agents/rules/*.md 为唯一权威
> 步骤 3.5：自检 — 逐项勾选：
>   □ 已完成内容敏感度预检（本项目=公开开源代码，产出物一律放 client 根目录
>     或 docs/ 对应子目录，禁止向 apps/containers/client/.agents/docs/ 写入）
>   □ 父级 AGENTS.md 已回读磁盘原文（启动协议步骤 1.1），与系统注入一致
>   □ 本次任务若命中 vendor 方法论资产（podman-py/七概念/等），对应规范已加载
>   □ 进入 client 子目录后遵循「嵌套优先」，未覆盖规则回退到根/ apps/ 两级
> 步骤 4：在规范指导下执行任务
> ```
>
> 本文件是 **jupyter-podman-client（镜像消费端）** 的 AI 协作者入口。本项目定位为
> `apps/containers/jupyter-podman-rootless` 的消费端：基于 `podman-py` 从本地 tar 缓存加载镜像，
> 并提供极简 invoke 任务的容器生命周期管理；**没有构建流程、没有 Compose、没有 ML 模型管理**，
> 核心能力是「跨平台 SDK 连接 + rootless 三必需」，其中 **Windows 11 WSL2 支持是本项目的差异化场景**。
>
> 所有全局规则（沟通语言、提交规范、上下文节省、路径引用）继承自 SpecWeave 根工作区；
> 本文件仅定义本项目特有的上下文路由与约束入口。

## 项目概述

- **项目类型**：容器镜像消费端（Invoke 任务包 + podman-py SDK 强依赖）
- **目标镜像**：`localhost/jupyter-podman-client:latest`（基于 rootless 叠加的通用镜像管理枢纽，可在其中运行/管理任意本地镜像）
- **编排架构**：两层后端自动降级——podman-py SDK（优先）→ CLI fallback（`podman.exe` 子进程）；**无 podman-compose 层**
- **Python 环境**：Python ≥ 3.14，构建后端 scikit-build-core，src 布局，wheel package=`["src/jpman_client"]`
- **跨平台**：WSL2 / Linux（原生 unix socket）+ macOS + **Windows 11 原生 CPython（WSL9P/Machine/tcp 多候选）**
- **任务管理**：invoke（`src/jpman_client/tasks/` 包，根 `tasks.py` 仅转发入口），三命名空间——根（`load`/`images`/`run`/`stop`/`status`/`clean`）+ `container.*` 别名 + `env.*` 自举（`build-layer`/`run-cmd`/`shell`）
- **Windows WSL 核心能力**：SDK 连接四级优先级（P0 env → P1 WSL9P → P2 Machine → P3 tcp），三变量逃生舱（`PODMAN_CLIENT_SDK_STRATEGY` / `WSL_DISTRO_NAME` / `CONTAINER_HOST`），W-I1~W-I3 30秒速查表
- **rootless 三必需**（所有启动路径硬编码，调用方不可覆盖）：`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`，**严禁 `--privileged`**
- **挂载/连接 A/B 维度分离**：Dimension A=容器卷挂载路径（D:\→/mnt/d/，`to_posix_path`）；Dimension B=SDK daemon URL（Windows 原生必须显式 `base_url`，`sdk_base_url_candidates`）
- **父级工作区**：SpecWeave 根目录（`../../../AGENTS.md`） → apps 入口（`../../AGENTS.md`）— 全局规则、Skill、角色、七概念指令均以父级为准
- **AI 资产容器**：`.agents/` 目录（本项目特有规则，按单一职责原子化拆分；其余子目录预留占位，未定义即回退父级）
- **内容敏感度**：本项目所有代码/文档均为公开内容，产出物入根 `docs/` 或本目录；私域镜像 tar / 个人工作区路径默认不入 git，由 `.gitignore` 守卫

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则、Skill、角色、团队、七概念指令）
  └─ apps/AGENTS.md（应用区入口路由，containers/client 条目回退到本文件）
       └─ apps/containers/client/AGENTS.md（本文件 = 消费端子应用路由入口）
            ├─ README.md                       ← 人类可读文档（Windows WSL 落地说明 + SDK 速查）
            ├─ .agents/README.md               ← AI 资产容器索引
            │   ├─ CHANGELOG.md                ← 项目变更日志（原子提交汇总）
            │   └─ rules/                      ← 单一职责原子化硬约束
            │       ├─ invoke-tasks.md         ← src/jpman_client/tasks/ 包结构 / 命名空间 / CLI fallback 行为承诺
            │       ├─ sdk-connection.md       ← podman-py 连接策略、6 scheme 限制、逃逸舱四策略
            │       └─ windows-wsl.md          ← Windows 11 × WSL2 三级探测 + W-I1~W-I3 速查
            ├─ tasks.py                        ← invoke 入口转发器（转发至 jpman_client.tasks）
            ├─ src/jpman_client/tasks/         ← invoke 任务定义（5 个模块：__init__ / client_core / env_in_container / manage / utils）
            ├─ pyproject.toml                  ← Python 配置（podman>=5 + python-dotenv>=1 + scikit-build-core）
            ├─ .env.example                    ← 环境变量模板（容器级 9 项 + SDK 级 4 项）
            └─ .gitignore                      ← git 忽略（.env / __pycache__ / .temp / workspace / 等）
```

**嵌套优先原则**：进入本目录后优先读取本文件；详细约束按主题加载 `.agents/rules/` 对应文件；未覆盖的规则按 client → apps/containers → apps → SpecWeave 根 逐级回退。

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| invoke 任务新增/修改（load/run/stop/status/clean） | [.agents/rules/invoke-tasks.md](.agents/rules/invoke-tasks.md) | 两层后端架构、`get_client() yield None` 零回归承诺、命名空间别名一致性 |
| podman-py SDK 连接行为修改 / 新增 scheme | [.agents/rules/sdk-connection.md](.agents/rules/sdk-connection.md) | 6 合法 scheme 白名单、无 npipe、`base_url` 在 Windows 必须显式、策略归一化 |
| Windows 11 WSL2 探测逻辑修改 / 新增发行版兼容 | [.agents/rules/windows-wsl.md](.agents/rules/windows-wsl.md) | 3 级发行版回退、UID 不硬编码 1000、UTF-16 LE 解析中文 Windows、W-I1~W-I3 修复 |
| 容器配置（rootless 三必需 / 卷挂载 / 端口映射） | `src/jpman_client/tasks/utils.py::ContainerConfig`（源代码真源） + [README.md §7](README.md#7-内置纪律rootless-三必需参数) | 严禁 `--privileged`；挂载路径走 `to_posix_path` |
| 人类可读文档更新（快速开始、WSL 落地、.env 清单） | [README.md](README.md) + [.env.example](.env.example) | README 中 5.4 速查表与 utils.py `windows_diagnose_hint` 必须保持一一对应 |
| AI 资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/ 目录结构、父级继承关系、预留占位目录说明 |
| 全局规则（提交/代码风格/沟通/修复闭环） | [../../../AGENTS.md](../../../AGENTS.md) → [.agents/global-core-rules.md](../../../.agents/global-core-rules.md) | 中文 commit、Conventional Commits、修复即闭环三阶段 |
| Skill 使用 | [../../../.agents/skills/](../../../.agents/skills/) | 优先 seven-concepts-cmd / jpman-podman-ops / atomic-commit-cmd / check-duplication-cmd |
| 七概念指令（R→I→E→C→A→F→V） | [../../../.agents/commands/seven-concepts.md](../../../.agents/commands/seven-concepts.md) | 复杂任务（如本次 WSL 支持改造）必须走方法论编排，禁止凭经验跳跃 |
| podman-py OKF v0.2 知识包（冲突裁决只读源） | `../../../projects/awesome-okf-xs/doc/bundles/jishu/containers/podman-py/concepts/01-connection.md` + `05-advanced.md` | 所有与 podman-py 行为相关的冲突以知识包 bundles 为最高可信度（G1级） |

## 核心规范入口

| 规范 | 入口 | 说明 |
|-----|------|------|
| 父级全局规则 | [../../../AGENTS.md](../../../AGENTS.md) | SpecWeave 根工作区入口（启动协议必经之路，必回读磁盘原文） |
| apps 应用区路由 | [../../AGENTS.md](../../AGENTS.md) | apps 区域总入口，containers/client 条目显式回退到本文件 |
| 本文件入口 | AGENTS.md（本文件） | jupyter-podman-client 子应用路由入口（启动协议嵌套路由） |
| AI 资产容器索引 | [.agents/README.md](.agents/README.md) | .agents/ 目录结构与父级继承关系清单 |
| Invoke 任务规范 | [.agents/rules/invoke-tasks.md](.agents/rules/invoke-tasks.md) | 两层后端 / CLI fallback / 命名空间 / 命令一致性 |
| SDK 连接硬约束 | [.agents/rules/sdk-connection.md](.agents/rules/sdk-connection.md) | 6 scheme / base_url 必显式 / 四策略逃生舱 |
| Windows WSL 规则 | [.agents/rules/windows-wsl.md](.agents/rules/windows-wsl.md) | 3 级发行版探测 / UTF-16 LE / W-I1~W-I3 速查 |
| 人类操作文档 | [README.md](README.md) | 安装 / 快速开始 / WSL 说明 / .env 完整清单 / 分工表 |
| 环境变量模板 | [.env.example](.env.example) | 容器级 9 项 + SDK 级 4 项完整带注释模板 |
| 源代码真源 | `src/jpman_client/tasks/`（`__init__.py` / `utils.py` / `client_core.py` / `env_in_container.py` / `manage.py`） | 行为与文档冲突时以源代码为准，README/AGENTS 同步后通过对抗审查更新 |

## 项目约束速览（P0 硬约束，违反 = PR 打回）

详细约束已按主题拆分到 `.agents/rules/` 下 3 个文件；以下是违反即打回的 P0 清单：

| # | P0 约束 | 所在文件 |
|---|--------|---------|
| C1 | **podman-py 合法 scheme 只有 6 个**：`unix / http+unix / ssh / http+ssh / tcp / http`；**严禁**出现 `npipe://`（Windows 命名管道）——抛 `ValueError: Unsupported URL scheme` | [sdk-connection.md](.agents/rules/sdk-connection.md) |
| C2 | **Windows 原生 CPython 环境下，PodmanClient 构造必须显式传 `base_url`**；无参构造等价于调用 `from_env()`，其回退路径为纯 Linux 语义（`XDG_RUNTIME_DIR/run/user/$UID/podman/podman.sock`），Windows 原生必抛 `FileNotFoundError` 进入 W-I1 诊断 | [sdk-connection.md](.agents/rules/sdk-connection.md) |
| C3 | **所有 run 路径（SDK 与 CLI fallback）必须硬编码携带 rootless 三必需**：`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`；**严禁** 任何路径出现 `--privileged` | [invoke-tasks.md](.agents/rules/invoke-tasks.md) + `utils.py::ContainerConfig` |
| C4 | **CLI fallback 行为承诺**：`get_client()` 必须是 `@contextmanager`，**只有所有 4 条候选路径都失败** 才 `yield None`；调用方 `if client is not None:` 判断零修改；新增候选不能破坏 CLI 回退 | [invoke-tasks.md](.agents/rules/invoke-tasks.md) + `client_core.py::get_client` |
| C5 | **WSL UID 不得硬编码 1000**；必须通过 `wsl.exe -d <Distro> id -u` 实际探测并 `lru_cache` 缓存 | [windows-wsl.md](.agents/rules/windows-wsl.md) + `utils.py::_wsl_user_uid` |
| C6 | **wsl.exe 输出编码必须显式 UTF-16 LE**（不是 UTF-8！）；中文 Windows PowerShell 5.1 默认输出是 UTF-16 LE，UTF-8 解析会乱码无法匹配发行版名 | [windows-wsl.md](.agents/rules/windows-wsl.md) + `utils.py::wsl_distro_name` |
| C7 | **逃生舱策略四值白名单**：`{auto, legacy, wsl, machine}`；非白名单值必须归一化为 `auto`，不得抛错；`legacy` 必须严格等价于旧行为（单次 `from_env()`，不走多候选） | [sdk-connection.md](.agents/rules/sdk-connection.md) + `utils.py::sdk_strategy_from_env` |
| C8 | **A/B 维度分离，禁止混淆**：容器卷挂载路径（`--workspace D:\...`）和 SDK 连接 URL（`PodmanClient(base_url=...)`）是两个彼此独立的维度，修改其中一个不能顺带改另一个的代码路径 | [windows-wsl.md](.agents/rules/windows-wsl.md) 维度表 + README §5.5 |
| C9 | **.env → os.environ 同步必须使用 `load_dotenv(override=False)`**；shell 中已显式 `export` / `$env:` 的同名变量优先级必须高于 `.env`，不得用 `override=True` 覆盖用户显式设置 | `manage.py::_load_env_overrides` |
| C10 | **修复即闭环三阶段**：任何 Bug 修复必须走 `修复点 → 预防（为什么下次不会再出现？如加白名单/加断言） → 闭环（诊断文案对齐速查表 W-I1~W-I3 / C-I1~C-I2，README 同步更新）`；严禁只做纯点修复不改对应 README/诊断文案。**容器内坑（C-Ix）与平台无关，其在 `windows_diagnose_hint()` 中的分支必须置于 `platform.system() != "Windows"` 守卫之前**，否则容器内（Linux）永远匹配不到 | 根 AGENTS 开发规范 + 本文件 §约束速览 |

## 快速开始（人类 & AI 共用最小验证路径）

```powershell
# === Windows 11 原生 CPython（推荐验证 WSL9P 路径） ===
# 1. WSL2 发行版内一次性启动 podman.socket（WSL9P 前置条件）
wsl -d Ubuntu -- bash -lc "sudo loginctl enable-linger \$USER && systemctl --user enable --now podman.socket"

# 2. 首次使用 Podman Machine 顺手把 known_hosts 写了（防 W-I3，没装可跳过）
# podman machine ssh true  # yes 回车

# 3. 安装消费端 + 验证 invoke 命名空间
cd apps/containers/client
pip install -e .
invoke --list   # 应看到：load / images / run / stop / status / clean + container.* 别名 + env.* 自举（build-layer / run-cmd / shell）

# 4. 加载构建端最新缓存镜像 + 启动容器
invoke load      # 自动从 ../jupyter-podman-rootless/.image-cache/ 拿最新 tar
invoke run --workspace D:/spaces/SpecWeave   # 启动成功打印 SSH/Jupyter URL
```

Linux/WSL2 内原生跑消费端的步骤完全相同，Windows 特有分支零差异。

## 引用父级 SpecWeave 规范

本项目完全遵循 SpecWeave 工作区发现协议（五步发现流程）：
- AGENTS.md 包含「启动协议」关键词（文件首部醒目块，含 PRIORITY ZERO 字样）
- 正确声明嵌套父级：`apps/containers → apps → SpecWeave 根`，路由指向 `../../../AGENTS.md`
- 遵循嵌套优先原则，未覆盖规则逐级回退，不重复父级已定义规则
- AI 资产已原子化拆分至 `.agents/rules/` 目录（3 个主题文件 = 单一职责单一事实源）
- 预留占位目录（roles / skills / scripts / workflows / templates / docs）各有 `.gitkeep`，未来扩展可直接填充
- 人类可读文档以根 `README.md` 为唯一入口，不新增 `.agents/docs/` 冲突路径

## 变更日志

完整原子提交历史见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)。

- **2026-09-10** | fix: 补全容器内 EACCES（C-I2）诊断与修复闭环（socket 属组自适应）并续接 `windows_diagnose_hint()` C-I2 分支；`inv load` / `inv run` 增加 podman 就绪预检与中文提示
- **2026-09-09** | fix: B-scheme 宿主 socket 直通端到端连通；`inv load` 增加镜像缓存完整性校验；`ensure_known_hosts` / `refresh_host_keys` 修复 Windows 路径失效与 sshd 就绪等待
- **2026-09-08** | feat/fix: 默认目标镜像泛化为 `jupyter-podman-client` 管理枢纽（叠加镜像 2.82 GB → 1.80 GB）；修复非 root 运行 entrypoint 致 `chpasswd` 失败容器退出；修复容器内 SDK socket ENOENT（C-I1，bootstrap 预建 `libpod/tmp` + `PODMAN_SERVICE_BOOT` 自举）
- **2026-09-07** | feat: Windows 11 WSL2 SDK 支持（四策略逃生舱、3 级发行版探测、W-I1~W-I3 诊断速查）；`tasks/` 迁移至 `src/jpman_client/tasks/`（5 模块）并保留根 `tasks.py` 转发层；新增 `env.*` 自举命名空间（`build-layer` / `run-cmd` / `shell`）；同步新增 `AGENTS.md` + `.agents/` AI 自治规范容器
- **2026-08-31** | refactor: 消费端首次拆分自构建端；初始版本发布（ContainerConfig + podman-py 两层后端 + rootless 三必需）
