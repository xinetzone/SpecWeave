# jupyter-podman-client 变更日志（原子提交汇总）

> 本文件只记录消费端特有改动；SpecWeave 工作区根级、apps/containers 组级、构建端（jupyter-podman-rootless）的改动
> 不在本文件范围内。按七概念方法论每次 C（原子提交）阶段完成后追加一条；每条必须：
> ①可追溯（对应根工作区 git commit hash）②关联七概念场景（里程碑复盘/问题解决/重构优化/知识沉淀/创新突破）③说明验收点

## [Unreleased]

### 2026-09-10 · `feat:` 同步构建端运行时透传（5 个开关 + C-I3 诊断）

**关联七概念场景**：场景5「创新突破」（F→V→I→C 链路）；F 阶段确认执行模型不同（构建端 compose 分层覆盖 → 消费端 SDK/CLI 编程式），V 阶段对抗审查产出下述关键约束

**F 阶段公理（V 已逐条验证）**：

1. 透传均为运行期参数 → 只能落在 SDK kwargs / CLI 参数，无法进镜像
2. **挂载源与设备节点由 daemon 宿主（WSL2 / Podman Machine）解析** → 客户端本机 `Path.exists()` 必然为假，**禁止本机预检**（否则误判拒绝正确请求）
3. podman 对缺失源**硬失败**（退出码 125、不自动创建）→ 只能事后把原生报错翻译为 C-I3 指引
4. `--network host` 与端口发布互斥 → 不传 `-p`；rootless 无法绑特权 22 → 自动设 `SSHD_PORT=--ssh-port`
5. 既有 P0 不可破坏：C3 rootless 三必需保留、C8 A/B 维度分离、S1~S5

**验收点**（原子提交单一职责，可独立验证）：

A. **参数构造层（新增单一事实源）**
   - `utils.py`：新增 `PassthroughSpec` + `build_passthrough_spec(cfg)` + `passthrough_paths()`（路径变量与构建端 `compose.passthrough*.yaml` 同名）+ `CONTAINER_RUNTIME_DIR`
   - `ContainerConfig` 新增 5 个布尔字段（默认全关 = 默认隔离）

B. **两条路径等价消费**：`client_core.py::_sdk_run_kwargs`（`network_mode` / `volumes` / `devices` 追加）与 `_run_via_cli`（`--network host` / `-v` / `--device`）均由同一份 spec 驱动，禁止各自拼接

C. **C-I3 诊断**：`utils.py::passthrough_diagnose_hint()` 匹配 `statfs` / `stat ... no such file or directory`，给出缺失路径 + 可覆盖变量 + daemon 侧自检命令；在 `_run_via_sdk` 与 `run_container`（CLI 异常捕获）两处挂载

D. **CLI 面**：`manage.py::run` 新增 `--host-network` / `--wayland` / `--gpu` / `--usb` / `--dbus`；新增 `_env_bool()` 修复 `bool("no")` 判真导致 `GRANT_SUDO=no` 失效的既有缺陷

E. **文档同步**：`README.md` §4 / §5.4 / §8.3 / §11、`.agents/rules/invoke-tasks.md`（§3.2 统一 spec 约束 + §4.4 命令面）、`.agents/rules/windows-wsl.md` §5（C-I3 行）

**验证证据**：单元级 5 组组合参数全部正确（默认组与旧版本零差异）；实跑 `--dbus` 容器内落到 `srw-rw-rw- /tmp/runtime-user/bus` 且两个环境变量就位；实跑 `--gpu` 触发 `Error: stat /dev/dri`（退出码 125）并打印 C-I3 指引

### 2026-09-10 · `fix:` 容器内 Podman socket EACCES（C-I2）根因修复与诊断闭环

**关联七概念场景**：场景2「问题解决」（F→V→C→R→I→E 链路）；F 根因分析后经**强制 V 对抗审查**（采纳 5 条意见：自验证 / `%G` 空回退 `%g` / 代价与红线声明 / `stat` 失败必 warn / C-I2 分支先于平台守卫）

**验收点**（原子提交单一职责，可独立验证）：

A. **消费端代码改动（SDK 侧诊断能力）**
   - `src/jpman_client/tasks/utils.py`：`podman_sock_path()` 默认 `PODMAN_RUNTIME_UID=1000` 且支持环境变量覆盖（**严禁硬编码容器内 UID**）；`windows_diagnose_hint()` 新增 **C-I2 匹配**（`permission denied` 且 socket 路径存在 → 属组修复引导），与 C-I1（`ENOENT`，socket/目录不存在）语义分离
   - `src/jpman_client/tasks/client_core.py`：异常汇总表叠加 C-I2 诊断文案，`get_client()` 失败路径不回归

B. **消费端文档对齐（三处同步）**
   - `README.md` §5.4：新增 **C-I2**「socket 存在但无权限（EACCES）」条目，与 W-I1/W-I2/W-I3/C-I1 并列（共 5 条口径）
   - `.agents/rules/windows-wsl.md` §5：C-I2 速查表（30 秒修复须为一行命令）
   - `AGENTS.md` + `.agents/README.md`：坑位索引与双向锚点同步

C. **联动修复（构建端 `jupyter-podman-rootless`，跨端引用登记以保证可追溯）**
   - `entrypoint.sh`：B-scheme 分支新增 **socket 属组自适应**——`stat` 宿主 socket 取属组名 → `usermod -aG` 加入非 root 用户 → 复验可读写；`stat` 失败必 `log_warn`（不静默）；UID 动态推导，不硬编码 1000/1001
   - `config/supervisor/conf.d/jupyter.conf`：移除硬编码 UID 1001 漂移，改 `%(ENV_CONTAINER_HOST)s` / `%(ENV_XDG_RUNTIME_DIR)s` 继承 entrypoint 动态导出值
   - `.agents/rules/entrypoint.md`：规则同步

D. **验收证据（verify 全部通过）**
   - `bash -n entrypoint.sh` ✅
   - base 镜像重建 → `701c2e509fd8`（`socket group` 关键字命中 5，旧镜像基线 0）✅
   - client 层重建 → `5ed156783148`（`User=root`；`jpman_client` editable 安装 OK）✅
   - 容器重建 → `41d46c351352` ✅
   - entrypoint 日志：`[B-scheme] Added devuser to socket group 'root' (gid 0)` + `[B-scheme] [OK] devuser can read/write host podman socket` ✅
   - 容器内 `/proc/<jupyter>/status`：`Groups: 0 27 997 1001`（gid 0 已注入）✅
   - `PodmanClient.from_env()` 成功：`podman 5.7.1`、3 容器、**无 PermissionError** ✅
   - devuser 侧 `podman images`（11 镜像）/ `podman info`（`rootless=true`、`RemoteSocket=unix:///run/user/1000/podman/podman.sock`）在显式 `CONTAINER_HOST` 下成功 ✅
   - 反证：无 `CONTAINER_HOST` 时触发 `newuidmap: write to uid_map failed`（WSL 三层 userns 限制），证明 `su -` 登录 shell 丢环境变量是历史误判来源、非 C-I2 修复失败 ✅

**根仓库 git commit**：`[52084da68](#)`

### 2026-09-09 · `fix:` 宿主 socket 直通连通 + 镜像缓存完整性 + known_hosts 维护

**关联七概念场景**：场景2「问题解决」

**验收点**：

A. **宿主 socket 直通（B-scheme）端到端连通**：容器内 devuser 经 userns 映射后可读写宿主直通 socket，`podman images` / `from_env()` 均成功
B. **镜像缓存完整性**：`validation_manifest_integrity` 修正首块误匹配，`inv load` 在缓存损坏时给出明确错误而非静默失败
C. **SSH host key 维护**：`ensure_known_hosts` 修复 Windows 路径失效；`refresh_host_keys` 改为 TCP 探测等待 sshd 就绪，并兼容 OpenSSH 10 KEX 与 host 段规范化

**根仓库 git commit**：（见对应 `fix(containers)` 系列提交）

### 2026-09-08 · `feat:` 默认镜像泛化为 client 管理枢纽 + 容器内 SDK socket ENOENT（C-I1）修复

**关联七概念场景**：场景2「问题解决」（容器内 C-I1）+ 场景3「重构优化」（镜像泛化）

**验收点**：

A. **镜像泛化与瘦身**：默认目标镜像由构建端镜像改为 `localhost/jupyter-podman-client:latest` 通用管理枢纽；叠加镜像体积 2.82 GB → 1.80 GB
B. **非 root entrypoint 修复**：修复 client 镜像以非 root 运行 `entrypoint.sh` 致 `chpasswd` 失败、容器以 `Exited (1)` 退出的问题
C. **容器内 SDK socket ENOENT（C-I1）修复**：bootstrap 路径（`env.run-cmd` / `env.shell`）由 `env_in_container.py::PODMAN_SERVICE_BOOT` 自举 `podman system service --time=0` 并预建 `${XDG_RUNTIME_DIR}/libpod/tmp`；常驻容器由 `entrypoint.sh::setup_podman()` 保证

**根仓库 git commit**：（见对应 `feat/fix(containers)` 系列提交）

### 2026-09-07 · `feat:` Windows 11 WSL2 SDK 全链路支持 + AI 自治规范容器初始化

**关联七概念场景**：场景3「重构优化」（I→F→A→C 链路）+ 场景4「知识沉淀」（从 podman-py OKF v0.2 bundles 萃取跨平台模式）

**验收点**（原子提交 C4 单一职责，可独立验证）：

A. **src/jpman_client/tasks/ 层代码改动（podman-py SDK Windows 兼容）**
   - `utils.py`：新增 SDK 逃生舱常量、`sdk_strategy_from_env()` 归一化、`_has_wsl_host_support()` 双门卫、`wsl_distro_name()` 3 级回退 UTF-16 LE 解析、`_wsl_user_uid()` 探测缓存、`BaseUrlCandidate` 数据类、`sdk_base_url_candidates()` P0→P3 序列生成、`windows_diagnose_hint()` W-I1~W-I3 速查匹配
   - `client_core.py`：重写 `get_client()` 上下文管理器接入多候选 ping 循环、失败汇总表、诊断文案叠加；CLI fallback 行为零回归（全部失败仍 `yield None`）
   - `manage.py`：`_load_env_overrides()` 修复核心 Bug——新增 `load_dotenv(override=False, encoding="utf-8")` 把 .env 同步到 os.environ，保证 SDK 级逃生舱读到 .env 变量；import 清理未使用的常量
   - `tasks/` → `src/jpman_client/tasks/` 布局迁移（消除与构建端 `jpman_builder.tasks` 的命名冲突），根 `tasks.py` 降级为纯转发层，新增 `env_in_container.py`（`env.*` 自举命名空间）
   - 静态验证：`python -m py_compile src/jpman_client/tasks/*.py` exit_code=0；VS Code `GetDiagnostics` 五文件零告警

B. **人类文档层改动（README.md + .env.example）**
   - `README.md` 新增 §5「Windows 11 × WSL2 支持」：§5.1 三路径矩阵、§5.2 四级连接优先级、§5.3 四策略逃生舱、§5.4 W-I1~W-I3 速查表、§5.5 A/B 维度分离表；原 §5→§6 / §6→§7 / §7→§8 / §8→§9 编号顺延
   - `README.md` §8「.env 配置完整清单」拆 8.1 容器级（9 项） + 8.2 SDK 级（4 项）两张表，明确优先级链：命令行 > shell export > .env > 默认
   - `.env.example` 追加 Windows WSL 专属 4 个 SDK 级变量：`PODMAN_CLIENT_SDK_STRATEGY`（含四策略注释）/ `WSL_DISTRO_NAME` / `CONTAINER_HOST` / `DOCKER_HOST`（兜底注释）
   - 双向锚点：README§5.4 ⇄ `utils.py::windows_diagnose_hint` ⇄ `.agents/rules/windows-wsl.md §5` 三处 W-I1~W-I3 条目 1:1 对应

C. **AI 协作者自治规范容器初始化（AGENTS.md + .agents/）**
   - `AGENTS.md`：消费端专属启动协议（嵌套路由 + 文档边界 + 内容敏感度预检）；项目概述；嵌套路由关系树；上下文路由表（10+ 条目）；10 条 P0 硬约束 C1~C10 违反打回清单；快速开始最小验证路径；父级引用声明；变更日志倒排
   - `.agents/README.md`：AI 资产容器索引；6 目录结构 + 3 规则文件；源代码真源表；人类文档↔AI 规则双向对应表；父级继承 7 层；新增规则 4 步流程；变更日志倒排
   - `.agents/rules/invoke-tasks.md`：消费端 invoke 开发规范；模块职责边界 5×5 禁止跨层表；两层后端架构 8 条不可变行为契约；CLI fallback 7 函数等价实现表；三命名空间（根 + `container.*` 别名 + `env.*` 自举）；6 条 P0 安全约束；3 条修改后必跑冒烟
   - `.agents/rules/sdk-connection.md`：6 合法 scheme 白名单 + npipe 严禁；Windows base_url 必显式约束；四策略逃生舱矩阵；多候选优先级序列（strategy × platform）；P1 WSL9P 生成契约（distro 3 级/UID 探测）；P3 tcp 兜底；8 条错误输出格式不可变；ImportError 降级安全
   - `.agents/rules/windows-wsl.md`：A/B 两维度分离表（核心差异）；两种用户画像；WSL 发行版名 3 级回退；UTF-16 LE 编码硬规定；_has_wsl_host_support 双门卫；UID 严禁硬编码 1000；W-I1~W-I3 三处同步对齐；.env 加载语义 override=False 红线；4 条必跑验证脚本
   - `.agents/{CHANGELOG.md,README.md,rules/*}` 其余子目录（roles/skills/scripts/workflows/templates/docs）预留 .gitkeep 占位（父级回退路径）

D. **治理承诺（七概念 G1~G4 质量门）**
   - G1（事实无因果）：所有 podman-py 行为陈述均有 OKF v0.2 bundles 原文锚定，无"应该/可能"类推断
   - G2（洞察四元组）：上一轮 WSL SDK 改造的根因分析四元组见 AGENTS.md 项目约束速览 C1~C10 后附的根因段
   - G3（模式可迁移）：从 bundles 萃取 2 个模式已落地——「Windows Podman 连接多候选自动降级」+「WSL2 发行版名 3 级回退」
   - G4（行动项原子化）：本次变更拆 A/B/C 三大原子块，可单独 revert 任意一块不影响其他块

**根仓库 git commit**：`[91c29c240](#)`
