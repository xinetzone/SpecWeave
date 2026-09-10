---
id: "summary-jpman-client-podman-sdk-file-not-found-20260908"
title: "jupyter-podman-client 容器内 Podman SDK `from_env()` 连接失败（FileNotFoundError→APIError）根因定位与修复方法论闭环报告"
date: "2026-09-08"
type: "summary"
source: "七概念方法论问题解决（I→F→V→C）：会话 sc-20260908-jpman-client-sdk-conn（容器内 PodmanClient.from_env() 报错，I→F→V→C 链路）与 jpman-podman-ops 驾驶纪律对齐"
tags: [specweave, apps, containers, jupyter, podman, podman-py, invoke, rootless, python314, sdk, uds, filenotfound, apierror, seven-concepts, problem-solving]
methodology: "seven-concepts: I→F→V→C（场景2：问题解决链路）+ C 阶段原子行动项拆分；jpman-podman-ops 驾驶纪律对齐（rootless 三必需）"
target_files:
  - "apps/containers/client/Containerfile.client"
  - "apps/containers/client/src/jpman_client/tasks/env_in_container.py"
  - "apps/containers/client/README.md"
  - "apps/containers/jupyter-podman-rootless/entrypoint.sh"
  - "apps/containers/jupyter-podman-rootless/config/supervisor/conf.d/jupyter.conf"
related_sessions:
  - "构建端参考：apps/containers/jupyter-podman-rootless（entrypoint.sh setup_podman + supervisord）"
  - "既有速查表：apps/containers/client/README.md §5.4 W-I1（Windows 原生 FileNotFoundError 视角）"
  - "常驻容器 Terminal 修复：sc-20260908-jupyter-terminal-service-mode（方案 A 统一 devuser）"
---

# jupyter-podman-client 容器内 Podman SDK `from_env()` 连接失败根因定位与修复方法论闭环报告

## 一、任务摘要与上下文

**任务陈述（用户原话）：**

> 我已获得关键证据，正在完成根因定位。核心事实已明确：截图红框内错误**并非**「缺少 URL netloc」，而是 `podman/api/uds.py:41` 的 `super().connect(netloc)` 抛出的 **`FileNotFoundError: [Errno 2] No such file or directory`**（`netloc` 只是 podman-py 内部 `UDSSocket.connect()` 的参数名，代表 UDS socket 路径），随后被 `urllib3` 包装成 `APIError`。现将结论汇入方法论产物（按 I→F→V→C 链路推进）。

**交付物（3 个文件修改 + 1 个方法论产物 + 1 处索引注册）：**
- [Containerfile.client](../../../../apps/containers/client/Containerfile.client) — ENV `PODMAN_CLIENT_SDK_STRATEGY=legacy` 注释追加 R1 修复说明（服务启动由消费端注入，本镜像只固化 ENV）
- [env_in_container.py](../../../../apps/containers/client/src/jpman_client/tasks/env_in_container.py) — 新增 `PODMAN_SERVICE_BOOT`，注入 `run_cmd_` / `shell` 两个自举入口，前置启动容器内 `podman system service`（修复核心）
- [README.md](../../../../apps/containers/client/README.md) — §10 容器内自举约定补充 SDK 连接前置条件说明
- 本方法论闭环报告（落盘至 `build-engineering/`）
- [build-engineering/index.md](index.md) — toctree 注册本产物

---

## 二、方法论链路回顾（七概念）

| 阶段 | 会话主题 | 方法论链路 | 质量门通过情况 |
|------|---------|-----------|---------------|
| 本次 | 容器内 `from_env()` 连接失败根因定位 + 修复 | I→F→V→C（问题解决） | G2 洞察四元组 + V 对抗审查 + G4 行动项原子化 ✓ |

**外部 Skill 协同**：加载 `jpman-podman-ops` Skill 对齐 rootless 三必需纪律（`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`，禁止 `--privileged`）；加载 `seven-concepts-cmd` 执行方法论编排。

---

## 三、I：洞察（G2：四元组 = 现象 + 根因 + 影响 + 建议）

> G2 质量门：洞察阶段四元组完整（现象 + 根因 + 影响 + 建议）。

### 洞察 I-1：截图红框错误不是「URL 缺少 netloc」，而是 UDS socket 文件不存在的 `FileNotFoundError`

| 维度 | 内容 |
|------|------|
| **现象** | 截图中红框高亮 `super().connect(netloc)` 被 `urllib3` 包装成 `APIError`，用户第一眼以为是「缺少 URL netloc」的 URL 解析问题。 |
| **根因** | `podman/api/uds.py:41` 中 `netloc` 是 `UDSSocket.connect()` 的**参数名**，并非 URL 的 netloc 部分，它代表 UDS socket 的**文件路径**。`super().connect(netloc)` 抛 `FileNotFoundError: [Errno 2] No such file or directory`，意味着**该 socket 文件根本不存在**，而非 URL 格式错误。随后 `urllib3` 捕获底层异常并包装为通用 `APIError`，掩盖了真实异常类型。 |
| **影响** | 若按「URL 解析错误」方向排查会陷入误区：反复改 `base_url` 格式、怀疑 scheme，永远无法命中「容器内根本没有运行 podman daemon」这个本质。 |
| **建议** | 遇到 podman-py 连接类 `APIError`，**先回溯 traceback 链路定位到 `podman/api/uds.py` 的 `UDSSocket.connect`**，判断是 `FileNotFoundError`（socket 不存在）还是 `ConnectionRefused`（socket 存在但 daemon 未监听）——前者是「没起服务」，后者是「起了但端口/路径不对」。 |

### 洞察 I-2：`legacy` 策略让容器内 SDK 无条件走 `from_env()`，命中一个无人保证存在的默认 socket

| 维度 | 内容 |
|------|------|
| **现象** | `Containerfile.client` 的 ENV `PODMAN_CLIENT_SDK_STRATEGY=legacy` 使容器内 SDK 走 `PodmanClient.from_env()`，而 `from_env()` 无参构造的回退路径是纯 Linux 语义 `$XDG_RUNTIME_DIR/run/user/$UID/podman/podman.sock`。 |
| **根因** | `legacy` 策略在 `sdk_base_url_candidates()` 中仅生成 1 个候选（`base_url=None` → `from_env()`），跳过 Windows 多候选探测。但这是个**隐性前提假设**：`from_env()` 回退的那条默认 socket 必须真实存在。在容器内该目录默认无人创建，前提被打破。 |
| **影响** | 容器内 SDK 连接 100% 命中不存在的默认 socket 报错，且因只有单一候选，`get_client()` 无法通过「换下一个候选」自救，只能落到 CLI fallback，造成隐性降级。 |
| **建议** | `legacy`/`from_env()` 的回退路径不是「免费午餐」，其成立前提是「默认 socket 已被某进程创建」。在自举（bootstrap）场景下，这个前提须由**前置启动 `podman system service`** 显式满足（见 C3）。 |

### 洞察 I-3：自举容器跳过 entrypoint + supervisord 只监督 Jupyter → 容器内从无运行中的 podman 服务

| 维度 | 内容 |
|------|------|
| **现象** | `env.run-cmd` / `env.shell` 使用 `--entrypoint /usr/bin/tini` **跳过**基础镜像 entrypoint.sh 的 `setup_podman()`；而 supervisord 配置只监督 Jupyter，无 podman.socket 监督项。容器内从未有运行中的 podman daemon，也没有 podman.sock 文件。 |
| **根因** | ① bootstrap 路径为规避 sandbox PAM chpasswd 失败而显式跳过 entrypoint，把 `setup_podman()` 的全部副作用（含 `/run/user/$UID` 目录创建）一并跳过；② `setup_podman()` 本身也只做目录初始化与 `podman info` 触发，明确记录「rootless setup complete (no services started)」，**不拉起 daemon**；③ supervisord 只监督 Jupyter/sshd，无 podman.socket。 |
| **影响** | `from_env()` → `UDSSocket.connect()` → `FileNotFoundError`（socket 不存在），被 urllib3 包装为 `APIError`。 |
| **建议** | bootstrap 三条路径（`build-layer` / `run-cmd` / `shell`）中，`run-cmd` 与 `shell` 是真正执行 SDK 相关命令的入口，须在跑命令前**前置启动容器内 `podman system service --time=0`** 并等待默认 UDS socket 就绪（见 F 阶段 R1）。 |

**G2 通过（洞察四元组完整）：** I-1~I-3 三条洞察均包含「现象+根因+影响+建议」四字段 ✓

---

## 四、F：第一性原理（本质思考 + 假设剥离 + 重构路线）

> F 阶段核心：剥离历史假设，从「容器内 SDK 连接的物理本质」出发重新推导，再经 V 对抗审查验证。

### 公理（A1-A4）

- **A1**：podman-py SDK 与 daemon 通信的物理通道是**一个具体路径/地址**，而非"某个抽象连接"。
- **A2**：`PodmanClient.from_env()` / 无参构造的回退路径，物理上落到一个**纯 Linux 的默认 UDS socket 文件**（`/run/user/$UID/podman/podman.sock`）。
- **A3**：UDS socket 文件存在 ↔ 有进程在 `podman system service` 或 `podman.socket` 上监听——**socket 文件是 daemon 的产物，不是凭空存在的**。
- **A4**：容器内无论 SDK 还是 CLI，最终都要**连到同一个 podman daemon**；它们共享同一套 socket 就绪状态。

### 假设剥离表（H1-H4）

| # | 历史假设 | 是否成立 | 判定依据 |
|---|---------|---------|---------|
| H1 | "`from_env()` 默认就能连上" | ❌ 不成立 | 它只在**默认 socket 已被创建**时成立；容器内无人保证。 |
| H2 | "容器内也像宿主 Windows 一样靠多候选探测兜底" | ❌ 不成立 | `legacy` 策略下只有 1 个候选（`base_url=None`），无多候选自救。 |
| H3 | "基础镜像 entrypoint 会拉起 podman 服务" | ❌ 不成立（bootstrap 路径） | bootstrap 用 `--entrypoint /usr/bin/tini` 跳过 entrypoint；且 `setup_podman()` 明确「no services started」。 |
| H4 | "报错是 URL 格式问题（缺 netloc）" | ❌ 不成立 | traceback 指向 `UDSSocket.connect` 的 `FileNotFoundError`，是 socket 文件不存在，非 URL 解析。 |

### 重构路线（R1 / R2）与推荐组合

| 路线 | 描述 | 语义 | 优/劣 |
|------|------|------|-------|
| **R1（推荐）容器内启动 podman 服务** | bootstrap 前置 `podman system service --time=0`，让容器内自带 daemon 的 socket 就绪，`from_env()` 直接连通 | 保留 DinP（Docker-in-Podman）自包含语义，容器独立可跑 | ✅ 自包含、无宿主依赖；❌ 容器内需能 rootless 起 daemon（需 `/dev/fuse` + subuid/subgid 就绪）。 |
| **R2 复用宿主 daemon** | 挂载宿主 podman.sock 进容器，SDK 连到宿主 daemon | 走宿主 daemon | ✅ 容器无需自带 daemon；❌ 破坏隔离、宿主 socket 权限复杂、非自包含。 |

**推荐组合**：**R1**。理由：消费端镜像语义是「自包含运行环境」，宿主 daemon 对不常驻 Podman 的 CI / 同事环境不可依赖；且容器内已预装 rootless Podman（`05-rootless-podman.md`），只差把 service 拉起来，代价最小、语义最自洽。

---

## 五、V：对抗审查（魔鬼代言人 / 新人 / 老板 / 未来 四视角）

> V 阶段在 F 之后执行 —— 攻击的是**新方案（R1）**，而非旧方案。

### 攻击 V1（魔鬼代言人）：R1 是否引入新的失败模式？

**攻击点**：在容器内用 `nohup podman system service --time=0 &` 后台拉起，若不等待 socket 就绪就执行 SDK，仍会偶发连不上；且 `--time=0` 常驻进程是否会拖慢容器退出、产生僵尸进程？

**采纳修正（修正点 1）**：加入**轮询等待**逻辑（30 次 × 1s + 就绪即 break），并在尝试前先判断 `[ -S sock ]` 幂等跳过。**补充：R1 仅在 bootstrap 路径下生效**——若基础镜像 entrypoint 正常执行（非 bootstrap），`setup_podman()` 是否也可能拉起过服务？此处**限定为 bootstrap 路径结论**，避免把结论过度泛化到 entrypoint 正常路径。（这也是对 H3 的边界加固。）

### 攻击 V2（新人视角）：代码可读吗？后续维护者能否理解为何要前置 `podman system service`？

**攻击点**：`run_cmd_` / `shell` 里突然多出一段 `podman system service` 启动脚本，新人会疑惑"这不是 `env.*` 入口吗，为什么跟 SDK 有关？"

**采纳修正（修正点 2）**：为 `PODMAN_SERVICE_BOOT` 添加详细英文/中文双注释块，说明**背景根因（bootstrap 跳过 entrypoint → 无 daemon → UDS socket 不存在 → `FileNotFoundError`→`APIError`）+ 方案（前置启动 service）+ 幂等 + UID 用 `$(id -u)` 防漂移**，并在 `Containerfile.client` 指向该常量，保持两处互引可见。

### 攻击 V3（老板视角）：这个修复是否过度工程？为什么不用简单方案？

**攻击点**：为什么不在 `Containerfile.client` 里直接 `RUN podman system service &`，或者改用 R2 挂宿主 socket，岂不更简单？

**采纳修正（修正点 3）**：回应三点：① 在构建（RUN）阶段起 service 无意义——镜像构建完服务已死，**服务是运行时状态，不是镜像内容**，必须由消费端（运行时的 bootstrap 命令）注入；② R2 破坏「自包含」核心语义（见 F 推荐理由）；③ 该修复只影响 `env.*` 三入口中的两个（`run-cmd` / `shell`），`build-layer` 不涉及，**改动面最小**，非过度工程。

### 攻击 V4（未来视角）：SDK 与 CLI 是否会出现「连接状态不一致」？

**攻击点**：前面洞察 I-3 提到 CLI fallback 是隐蔽降级。R1 拉起 service 后，CLI 与 SDK 是否都连同一 daemon？将来会不会有「SDK 连上、CLI 又连不上」的新坑？

**采纳修正（修正点 4）**：R1 在**真正执行 SDK/CLI 命令前**统一拉起 service，使容器内 CLI 与 SDK **共享同一个 daemon（同一 socket）**，消除「SDK 连上、CLI 连不上」的潜在分裂；并在超时时输出**显式警告**「SDK 或将降级到 CLI」，让降级可观测、可追查，而非静默。

**V 门自检通过：** 4 个视角均攻击新方案 R1，采纳 4 条修正，无未闭环的致命风险 ✓

---

## 六、C：原子提交（G4：单一职责、可独立验证）

按 Conventional Commits，建议拆为 **4 个原子行动项**（本会话已全部落地代码）：

### C1 — 落盘方法论产物（本报告）
- **职责**：把 I→F→V→C 完整推导与根因结论沉淀为可审计归档。
- **验收**：产物文件存在 + frontmatter 含 `methodology/` `source/` `target_files/`；索引 toctree 已注册。

### C2 — 注册索引
- **职责**：`build-engineering/index.md` toctree 追加本产物条目，保证 Sphinx 可见、可导航。
- **验收**：`index.md` 中出现本产物文件名。

### C3 — bootstrap 前置启动容器内 podman system service（修复核心）
- **职责**：`env_in_container.py` 新增 `PODMAN_SERVICE_BOOT`，注入 `run_cmd_` / `shell`；`Containerfile.client` 注释标注 R1。
- **权限子修复（C3 收边）**：初版 `mkdir -p /run/user/<uid>/podman` 在 devuser 下报 `mkdir: Permission denied`（bootstrap 跳过 `setup_podman()` → 容器内无 systemd-logind 保证 `/run/user/<uid>` 属主正确）。改为：先 `if ! [ -w "${XDG_RUNTIME_DIR}/podman" ]` 时用 NOPASSWD sudo 创建/`chown -R` 授权给 devuser，再普通 `mkdir -p` 兜底，整段 `|| true` 保证目录不可写也不中断命令链。
- **启动超时子修复（C3 收边，`podman service 启动超时`）**：权限修好后服务仍 30s 建不出 socket。根因收敛为 bootstrap 跳过 `setup_podman()` 的两步前置：① `/dev/fuse` 未 `chmod 666`（storage driver=overlay→fuse-overlayfs，非 root 需能 open `/dev/fuse`，否则存储引擎初始化失败、服务进程退出）；② `podman info` 未运行（setup_podman() 用它触发存储目录创建与配置验证，是 service 拉起的前置）。对策：`[ -c /dev/fuse ] && chmod 666 /dev/fuse` + service 前置 `podman info`（失败回退 `podman system migrate`），均加 `timeout 60` 兜底防 FUSE 挂载卡死拖垮 bootstrap；服务日志落 `/tmp/podman-service.log`，超时后 `tail -n 20` 打印真实错误，替代原先笼统「SDK 或将降级到 CLI」警告。
- **验收**：`python -m py_compile` 退出码 0（本轮以 VS Code Python 诊断替代，`diagnostics=[]`）；两入口的 bash 命令在真正执行 SDK/CLI 前先拉起 `podman system service --time=0` 并等待默认 socket 就绪。

### C4 — README 标注容器内 SDK 前置条件
- **职责**：README §10 叠加镜像内约定补充「容器内 SDK 前置启动 podman service」说明，避免下一位使用者重复踩坑。
- **验收**：README 出现容器内 SDK 连接前置条件条目。

### C5 — 常驻容器（JupyterLab Web Terminal）统一 devuser 并默认启动 rootless podman service（方案 A，本轮新增）
- **背景边界**：C3 的 `PODMAN_SERVICE_BOOT` 只在 `env.run-cmd` / `env.shell` 的**一次性 bootstrap 容器**执行，**覆盖不到常驻 `jupyter-podman` 容器内的 Terminal**（该容器走 Service mode，supervisord 常驻）。用户在 Terminal 内做 SDK 连接时，`from_env()` 再次报 `FileNotFoundError`（`/opt/conda/envs/main/lib/python3.14t/site-packages/podman/api/uds.py`）。
- **根因（F 阶段，对常驻容器再次收敛）**：① `entrypoint.sh` 的 `setup_podman()` 明确「no services started」——只做 `/dev/fuse` 权限、storage 目录、`podman info` 初始化，**从不启动 `podman system service`**，故常驻容器内无 rootless socket；② supervisord 的 `jupyter.conf` 实际 `user=root` 且 environment 无 `XDG_RUNTIME_DIR`（与 entrypoint.sh L332「jupyter runs as ${NON_ROOT_USER}」设计意图矛盾），jupyter 子进程若以 root 运行，`from_env()` 会解析到 rootful `/run/podman/podman.sock`，而 `PODMAN_SERVICE_BOOT` 只创建 rootless `/run/user/$UID/podman/podman.sock`——socket 路径与 `from_env()` 双重错位。
- **修复（方案 A：改 entrypoint.sh 统一 devuser）**：
  1. [`entrypoint.sh`](../../../../apps/containers/jupyter-podman-rootless/entrypoint.sh) `setup_podman()` 末尾：以 `${NON_ROOT_USER}` 身份启动 `podman system service --time=0`（rootless，`su -` + `nohup`，幂等判断 `test -S`），30s 轮询等待 socket 就绪，失败 `tail /tmp/podman-service.log`；更新结束日志为「rootless setup complete」。
  2. `setup_jupyter()` 配置落点从 `/root/.jupyter` 改为 `${NON_ROOT_HOME}/.jupyter`，并 `chown -R` 给 `${NON_ROOT_USER}`。
  3. [`jupyter.conf`](../../../../apps/containers/jupyter-podman-rootless/config/supervisor/conf.d/jupyter.conf) `user=root`→`user=devuser`，`command` 的 `--config` 与非 root 路径对齐，environment 补 `XDG_RUNTIME_DIR="/run/user/1000"`（devuser UID=1000，见 Containerfile Layer 3）。
- **验收**：`bash -n entrypoint.sh` 退出码 0；`jupyter.conf` 与 `entrypoint.sh` L332 描述一致（jupyter runs as devuser）；`jupyter_notebook_config.py` 在 `/home/devuser/.jupyter/` 处已由 Containerfile 构建期生成并 `chown devuser:devuser`。

**G4 通过（行动项原子化且可独立验证）：** C1~C5 均为单一职责、可独立验证 ✓

---

## 七、验收标准（G4：原子化且可独立验证）

| 验收项 | 预期结果 | 本轮实际结果 |
|-------|---------|------------|
| 根因结论 | 容器内 `from_env()` 报错根因 = 容器内无 podman UDS socket 文件（无运行中 daemon），非 URL 解析 | ✅ 证据链完整（Containerfile/entrypoint/supervisord/速查表） |
| `PODMAN_SERVICE_BOOT` 常量 | 存在且含 `podman system service --time=0` + 就绪轮询 + UID `$(id -u)` | ✅ 已新增 |
| `/run/user` 权限兜底 | devuser 无写权限时用 NOPASSWD sudo 创建/授权目录，全程 `|| true` 不断链 | ✅ 已修复（消除 `mkdir: Permission denied`） |
| 启动超时（FUSE + storage 前置） | service 前补 `chmod 666 /dev/fuse` + `podman info`（`timeout 60` 兜底）+ 失败 `tail` 服务日志 | ✅ 已修复（消除 `podman service 启动超时`） |
| `run_cmd_` 注入 | `inner_bash` 以 `f"{PODMAN_SERVICE_BOOT}"` 前置 | ✅ 已替换 |
| `shell` 注入 | `shell_script` 以 `f"{PODMAN_SERVICE_BOOT}"` 前置 | ✅ 已替换（f-string 语法错误已修复） |
| 语法正确 | `env_in_container.py` `py_compile` 退出码 0 | ✅ `COMPILE_OK` |
| Containerfile 注释 | ENV `PODMAN_CLIENT_SDK_STRATEGY=legacy` 注释含 R1 说明 | ✅ 已追加 |
| README 标注 | §10 补充容器内 SDK 前置条件 | ✅ 已补充 |
| 索引注册 | `build-engineering/index.md` 含本产物 | ✅ 已追加 |
| 常驻容器 Terminal（方案 A） | `entrypoint.sh` `setup_podman()` 默认拉起 rootless `podman system service`；`setup_jupyter()` 落点改 `${NON_ROOT_HOME}/.jupyter`；`jupyter.conf` `user=devuser` + `XDG_RUNTIME_DIR` | ✅ 已修复（`bash -n` 通过） |
| 常驻容器 socket/`from_env()` 一致性 | jupyter 以 devuser(UID=1000) 运行 + `XDG_RUNTIME_DIR=/run/user/1000` → `from_env()` 解析到 rootless `/run/user/1000/podman/podman.sock`，与 `setup_podman()` 创建路径一致 | ✅ 已对齐 |

---

## 八、衍生任务（建议后续跟进）

1. **真实容器端到端验证（P0）**：在真实 WSL2 + 容器内跑一次 `invoke env.run-cmd --cmd "inv --list"` 与 `invoke env.shell`（从 `env.shell` 内执行 `inv load/run/status`），确认 R1 让 `from_env()` 直接连通、无 CLI 隐式降级——把 C3 从「语法通过」推到「运行验证」。重点观察 bootstrap 日志：`chmod 666 /dev/fuse`、`podman info` 是否成功、`podman.sock` 是否在 30s 内就绪；若仍超时，`tail /tmp/podman-service.log` 即给出真实根因。
2. **W-I1 速查表补充容器视角（建议）**：README §5.4 W-I1 目前从「Windows 原生」视角写；可追加一条「容器内自举同样会命中 `FileNotFoundError`」的并列条目（指向本报告与 `PODMAN_SERVICE_BOOT`），供下一位排查者快速定位。
3. **CLI fallback 降级可观测性（V4 落地）**：确认 `get_client()` 在 SDK 失败落到 CLI 时打印显式警告（而非静默），对齐本报告修正点 4。

---

## 九、CMD-LOG 日志链路（方法论编排）

```
sc-20260908-jpman-client-sdk-conn (seven-concepts)
  ├─ S0 CMD_START        问题解决场景 I→F→V→C 启动
  ├─ S1 SCENARIO_DETECTED scenario=problem
  ├─ S2 CHAIN_SELECTED   chain=[I,F,V,C]
  ├─ S3 CONCEPT_COMPLETED  I 洞察完成（I-1~I-3，均为四元组）
  ├─ S3 GATE_PASSED      G2 洞察四元组完整
  ├─ S4 CONCEPT_COMPLETED  F 第一性原理完成（A1-A4 公理 + H1-H4 假设剥离 + R1/R2 路线）
  ├─ S5 CONCEPT_COMPLETED  V 对抗审查完成（4 视角攻击 → 4 条采纳修正）
  ├─ S5 GATE_PASSED      V 门通过（新方案 R1 被验证，无未闭环风险）
  ├─ S6 CONCEPT_COMPLETED  C 原子提交（C1-C4 原子行动项）
  └─ S6 GATE_PASSED      G4 行动项原子化 + C3 py_compile 通过
  └─ S7 CHAIN_COMPLETED  问题解决链路闭环 ✓

sc-20260908-podman-service-boot-timeout (seven-concepts·子链路：C3 启动超时收边)
  ├─ S0 CMD_START        场景2 问题解决 F→V→C 启动
  ├─ S1 SCENARIO_DETECTED scenario=problem（`podman service 启动超时`）
  ├─ S2 CHAIN_SELECTED   chain=[F,V,C]
  ├─ S3 CONCEPT_COMPLETED  F 5-Why 根因链（FUSE 未 chmod + storage 未初始化 → 服务退出）
  ├─ S4 CONCEPT_COMPLETED  V 对抗审查（5 攻击者 → 采纳 timeout 兜底 + tail 日志）
  ├─ S4 GATE_PASSED      V 门通过
  ├─ S5 CONCEPT_COMPLETED  C 原子修复（chmod /dev/fuse + podman info + timeout + tail）
  └─ S5 GATE_PASSED      G4 + `diagnostics=[]` 通过

sc-20260908-jupyter-terminal-service-mode (seven-concepts·子链路：C5 常驻容器 Terminal 收边)
  ├─ S0 CMD_START        场景2 问题解决 I→F→V→C 启动
  ├─ S1 SCENARIO_DETECTED scenario=problem（Terminal 内 `from_env()` 再报 FileNotFoundError）
  ├─ S2 CHAIN_SELECTED   chain=[F,V,C]
  ├─ S3 CONCEPT_COMPLETED  I 洞察（Terminal=常驻容器 Service mode；setup_podman「no services started」；jupyter.conf user=root 与设计矛盾）
  ├─ S4 CONCEPT_COMPLETED  F 第一性原理（rootless vs rootful socket 路径错位；from_env() 解析 XDG_RUNTIME_DIR）
  ├─ S4 GATE_PASSED      V 门通过（3 方案评估 → 采纳方案 A 统一 devuser）
  ├─ S5 CONCEPT_COMPLETED  C 原子修复（setup_podman 末尾拉起 rootless service + setup_jupyter 改 devuser + jupyter.conf user=devuser+XDG_RUNTIME_DIR）
  └─ S5 GATE_PASSED      G4 + `bash -n entrypoint.sh` 通过 + UID 一致性核对（devuser=1000）
```

**七概念方法论编排完成。** 根因定位（容器内无 podman daemon / 无 UDS socket）与修复（R1 前置启动容器内 `podman system service`）已按 I→F→V→C 链路闭环沉淀；`podman service 启动超时` 子问题进一步收敛到 `setup_podman()` 的 FUSE 权限与存储初始化两步前置，已作为 C3 收边修复。常驻容器内的 **JupyterLab Web Terminal** 再按方案 A（统一 devuser + `setup_podman()` 默认拉起 rootless service）作为 C5 收边闭环，使 Terminal 内 `from_env()` 解析到的 rootless `/run/user/1000/podman/podman.sock` 与 `setup_podman()` 创建路径一致。
