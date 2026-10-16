---
name: jpman-podman-ops
version: 1.3.0
description: "jupyter-podman-rootless（jpman）容器日常运维与 Podman on WSL2 驾驶纪律。当用户提到 jpman、启动/重启/停止 Jupyter 容器、容器起不来、podman machine、机器未运行、工作区挂载(-w)、挂载目录不对、容器 WARN 分诊、fuse device not found、Jupyter 隐藏文件不显示、rootless podman 排障、jpman start/restart/status/logs/shell、WSL 保活、镜像构建慢/卡住/miniforge 下载慢/镜像源加速、容器内 podman 报 newuidmap EPERM/嵌套容器/SSH 与 podman exec 行为不一致，以及 WSL 3.0 后 crun pids not available/non-systemd cgroup 未委托/--pids-limit 不生效/start 报 machine not in running state 但实例实际 Running 等场景时必须使用。封装日常驾驶 SOP（就绪预检→幂等 start→Mounting 核对→healthcheck→WARN 先验分诊）、rootless 三必需参数、.env 与工作区路径优先级、rebuild 增量/全量选择、invoke 构建加速（tuna 三镜像源+预灌+9p 规避）、嵌套 Podman 分诊（newuidmap 结构性根因+B-scheme 宿主 socket 五通道桥接）、WSL3 cgroup pids 委托缺失修复（systemd=true+/sbin/init argv[0] shim 两步，§7.3，仅限四条件齐备）；与 docker-cache-cmd（镜像灾备缓存）、docker-wsl-bridge-cmd（镜像转 WSL 发行版）、wsl-vhdx-compact-cmd（VHDX 压缩迁移）边界路由。不要手动拼 podman 命令或套 Docker 经验——已封装 machine ssh 纪律、hello-world 最小验证、systemd=true 唯一合法使用边界（禁止为消普通 WARN 单独开启）、禁嵌套自建 rootless daemon 等实战教训。"
argument-hint: "<日常操作> [start|stop|restart|status|info|logs|shell|rebuild...] [选项]"
disable-model-invocation: false
user-invocable: true
paths:
  - ".agents/skills/jpman-podman-ops/**"
  - "apps/containers/jupyter-podman-rootless/bin/**"
title: "jpman 容器日常运维 (jpman Podman Ops)"
x-toml-ref: "../../../.meta/toml/.agents/skills/jpman-podman-ops/SKILL.toml"
---
# jpman 容器日常运维 (jpman Podman Ops)

## 1. Skill ID

`jpman-podman-ops`

## 2. 功能描述

封装 **jupyter-podman-rootless** 应用（rootless Podman + WSL2 上的 Jupyter Lab 开发容器，应用 CLI 名为 `jpman`）的**日常驾驶工作流**。jpman CLI 本身零依赖、设计成熟，本 Skill 不重复实现它，而是提供 CLI 之外的**环境纪律、分诊 SOP 与任务路由**。

核心能力：

- **podman machine 生命周期就绪预检**（Windows/WSL 平台差异、保活、进入纪律）
- **jpman 幂等启停**与工作区挂载核对（start/stop/restart/-w）
- **健康验证与访问信息**（status/info/url/healthcheck）
- **WARN/警告分诊**（警告先验法：hello-world 最小验证 → 进入方式检查 → 三板斧）
- **构建/缓存/导出场景路由**（rebuild vs rebuild-all、save/load、wsl-export，及姊妹 Skill 边界）

> **为什么需要这个 Skill？** 日常故障 90% 不在 CLI 用法，而在环境纪律：错误的 machine 进入方式、见 WARN 就改配置、9p 慢速构建、挂载错工作区后误以为数据丢失。这些教训分散在 2026-08-27 警告复盘（21 条事实）、项目记忆与 FAQ 中，没有门面封装时每次都要重新踩坑。

**与姊妹 Skill 的边界**：

| 需求 | 路由 |
|------|------|
| 日常启停/进入/日志/挂载/警告分诊 | **本 Skill** |
| 镜像 tar.gz 灾备缓存（.agents 体系，`.docker-cache/`） | [docker-cache-cmd](../docker-cache-cmd/SKILL.md) |
| 镜像转 WSL 发行版（通用桥接） | [docker-wsl-bridge-cmd](../docker-wsl-bridge-cmd/SKILL.md) |
| ML 模型管理 / invoke 任务 / 首次构建镜像 | 应用内 invoke，见 [01-getting-started.md](../../../apps/containers/jupyter-podman-rootless/docs/01-getting-started.md) |

## 3. 何时使用本技能

当用户提到以下任何内容时触发：

- "jpman"、"jpman start/restart/status/logs/shell"、"jupyter 容器"
- "启动 jupyter 容器"、"重启 jupyter"、"jupyter 起不来"、"容器打不开"
- "podman machine"、"podman 机器"、"podman machine start"、"podman 连接失败"
- "工作区挂载"、"-w 参数"、"挂载目录不对"、"容器里数据不见了"
- "容器警告"、"WARN"、"fuse device not found"、"cgroup 警告"、"shared mount"
- "隐藏文件不显示"、"allow_hidden"、".temp 看不到"
- "rootless podman"、"WSL 保活"、"keepalive"、"WSL 自动关闭"
- "rebuild"、"增量重建"、"改了配置怎么生效"
- "构建慢"、"镜像构建卡住"、"构建一直不动"、"miniforge 下载慢/超时"、"GitHub 限速"、"镜像源加速"、"tuna 镜像构建"
- "容器里跑 podman 报错"、"podman-compose up 失败"、"newuidmap"、"write to uid_map failed"、"Operation not permitted"、"嵌套容器/DinP 起不来"、"SSH 连进去 podman 不能用"、"podman exec 可以但 SSH 不行"
- "crun controller pids is not available"、"non-systemd cgroup"、"cgroup.controllers 为空"、"--pids-limit 不生效/被忽略"、"WSL 升级到 3.0 后容器起不来"、"start 报 machine not in running state 但 wsl -l -v 显示 Running"

> **关于触发**：即使没有明确说"用 skill"，只要涉及 jupyter-podman-rootless 容器的日常操作与排障，就应使用本技能，不要手动拼接 `podman create` 参数或凭 Docker 经验操作——rootless/WSL2 的约束与 Docker Desktop 完全不同。

## 4. 任务路由决策树

```
用户要对 jupyter-podman-rootless 做什么？
├─ 日常启停/进入/日志/查访问地址？            → §6 日常驾驶 SOP
├─ podman machine 连不上/报连接错误/启动有 WARN？ → §7 machine 就绪与警告分诊
│   └─ 普通容器直接报 crun pids not available（non-systemd 路径）？
│       四条件齐备 → §7.3 WSL 3.0 cgroup 委托修复（systemd=true+argv0 shim）
├─ 改了配置/装了包要固化进镜像？               → §8 构建场景（rebuild 增量 vs rebuild-all 全量）
├─ invoke build 很慢/卡在下载/疑似构建挂起？   → §8.5 构建加速分诊速查
├─ 容器内 podman/podman-compose 报 newuidmap EPERM？
│   （SSH/终端里起容器失败，podman exec 却正常）→ §9.1 嵌套 Podman 分诊
├─ 镜像打包灾备 / 换机 / WSL 重置后恢复？
│   ├─ 应用内快速缓存（.image-cache/）        → jpman save/load（§8.3）
│   └─ .agents 体系灾备（.docker-cache/）     → docker-cache-cmd
├─ 把镜像变成 WSL 发行版（无 Podman 也能跑）？
│   ├─ 应用内一键导出                        → jpman wsl-export（§8.4）
│   └─ 通用桥接编排                          → docker-wsl-bridge-cmd
└─ ML 模型管理 / invoke 13 任务 / 首次全量构建？ → 应用内 invoke（不在本 Skill 范围）
```

## 5. 环境与前置准备

- **应用根目录**：`apps/containers/jupyter-podman-rootless/`（仓库相对路径，下文命令均在此目录执行）
- **三平台入口**：

```bash
# WSL / Linux / macOS（推荐，完整功能）
bash bin/jpman <命令>
# 可选：软链到 ~/.local/bin 后直接用 jpman
bash bin/jpman install

# Windows PowerShell 7
pwsh -File bin/jpman.ps1 <命令>
# 或 cmd / 双击
bin\jpman.cmd <命令>
```

- **运行时前置**：Windows 需 Podman machine（`podman machine init` 后 `podman machine start`）；WSL/Linux 需本机 rootless podman
- **配置文件**：应用根 `.env`（从 `.env.example` 复制）；常用变量默认值：容器名 `jupyter-podman`、镜像 `localhost/jupyter-podman-rootless:latest`、SSH 端口 2222、Jupyter 端口 8888、登录密码 `devpass123`、token `chaostest2026`

> **为什么 .env 不能用 `source` 加载？** .env 由 jpman **逐行解析**（剥离 CRLF、支持引号、Windows 反斜杠路径安全）。若用 shell source，`D:\spaces\x` 中的反斜杠会被 shell 转义吞掉，短名/`JUPYTER_*` 前缀双名 fallback 也会失效。手动调试时只读查看，不要 source 进当前 shell。

> **为什么 Windows 上优先在 WSL 里跑 bash 版？** jpman.ps1 多数命令是转发到 WSL 内执行 `bash jpman`，仅 wsl-export/wsl-verify 为原生 PowerShell 实现。直接在 WSL 里跑少一层 interop，路径与编码问题最少。

## 6. 日常驾驶 SOP（核心流程）

### 步骤 0：定位与入口

确认当前在应用根目录 `apps/containers/jupyter-podman-rootless/`，按平台选择入口（§5）。

### 步骤 1：运行时就绪预检

- **Windows**：先 `podman machine start`（若已运行会提示已启动）；随后后台保活：`wsl -d podman-machine-default -- sleep infinity`（见 §7.1）
- **WSL/Linux**：确认 `podman info` 正常
- jpman 自身会做就绪探测（`podman version` 探测 Server 端），不可达时给出 `podman machine start/init` 提示

### 步骤 2：启动容器（幂等，可安全重复执行）

```bash
bash bin/jpman start                 # 默认工作区 <应用根>/workspace
bash bin/jpman start -w /path/to/proj   # 指定工作区
bash bin/jpman start -w D:\spaces\SpecWeave   # Windows 路径，自动转 /mnt/d/...
```

> **为什么 start 可以放心重复执行？** start 是幂等三分支：容器运行中→直接显示访问信息；容器存在但停止→删除后重建；不存在→创建。重复执行不会产生重复容器，也不会丢数据。

### 步骤 3：核对挂载行（关键！）

启动输出中**必须**看到并核对：

```
Mounting <宿主机绝对路径> -> /workspace
```

> **为什么必须核对 Mounting 行？** 工作区路径经多层解析（`-w` > `WORKSPACE` env > `JUPYTER_WORKSPACE` env > .env > 默认 workspace/），相对路径基于执行 jpman 时的 $PWD。挂错目录时容器完全正常，但文件"看起来不见了"——实际写到了另一个宿主机目录。这是日常驾驶中误报率最高的"数据丢失"。

### 步骤 4：验证健康与获取访问信息

```bash
bash bin/jpman status    # 三态 + ps 表 + 主动触发 healthcheck（healthy/starting）
bash bin/jpman info      # Jupyter URL（含 token）、SSH 命令、密码、Mount 行
bash bin/jpman url       # 仅输出 URL
```

启动后 jpman 已自动执行健康等待（`podman healthcheck run`，每 2 秒一次、最多 120 秒）。status 中 Health 显示 healthy 后，浏览器打开 info 给出的 URL。

### 步骤 5：日常使用

```bash
bash bin/jpman shell          # 以 devuser 进入容器（登录 shell）
bash bin/jpman shell --root   # 以 root 进入
bash bin/jpman exec <cmd...>  # 以 devuser 执行单条命令
bash bin/jpman root <cmd...>  # 以 root 执行单条命令
bash bin/jpman logs -f        # 跟踪日志（忘 token 时也可 logs 查看）
```

### 步骤 6：停止与重启

```bash
bash bin/jpman stop           # stop -t 5 + rm -f（删容器，不删镜像/不碰挂载数据）
bash bin/jpman restart -w /path/to/proj   # restart 透传全部参数（含 -w）
```

> **为什么重启后数据不丢？** 容器是无状态的：`/workspace` 是宿主机绑定挂载，镜像独立保留，stop 只删除容器实例本身。容器内非 /workspace 的改动（如 apt 装包）会随重建消失——那类需求应走 §8 重建镜像，而不是依赖容器内状态。

### 命令速查表

| 分组 | 命令 | 用途 |
|------|------|------|
| 生命周期 | `start [-w PATH]` / `stop` / `restart [-w PATH]` | 幂等启停 |
| 状态 | `status`（别名 `ps`）/ `info` / `url` | 健康状态与访问信息 |
| 进入 | `shell [--root]`（别名 `sh`）/ `exec CMD` / `root CMD` | 容器交互 |
| 日志 | `logs [-f]` | tail 100 行或跟踪 |
| 镜像 | `rebuild` / `rebuild-all` / `save` / `load` | 增量/全量构建、缓存 |
| WSL | `wsl-export` / `wsl-verify` / `keepalive` | 发行版导出与保活 |
| 安装 | `install [DIR]` / `help` | 软链安装、帮助 |

> 完整参数表以 [14-jpman-cli.md](../../../apps/containers/jupyter-podman-rootless/docs/14-jpman-cli.md) 与 `jpman help` 为准（命令可能随版本演进）。

## 7. Podman machine 就绪与 WARN 分诊

### 7.1 machine 就绪纪律（Windows）

1. `podman machine start` 启动 machine
2. 后台保活防回收：`wsl -d podman-machine-default -- sleep infinity`（配合 Windows 用户 `.wslconfig` 设 `vmIdleTimeout=-1`、`networkingMode=NAT`）
3. 需要进入 machine 排查时，**必须**使用 `podman machine ssh`

> **为什么不能用 `wsl -d podman-machine-default` 起交互 shell 排查？** 两种方式进入的看似是同一个发行版，但 `wsl -d` 直连的会话没有 `XDG_RUNTIME_DIR` 与 `DBUS_SESSION_BUS_ADDRESS` 会话环境，podman 命令会输出 shared mount 等警告并出现异常行为；`podman machine ssh` 会建立完整的用户会话。2026-08-27 警告复盘的双警告 5-Why 根因均汇合于此。
>
> **注意澄清**：`wsl -d podman-machine-default -- sleep infinity` 是**非交互保活命令**——不启动 shell、不读取会话环境变量，与"禁止 wsl -d 交互进入排查"不冲突。

WSL 内运行 jpman 时另有会话层保活：jpman start 会自动调用 keepalive（`setsid sleep infinity & disown`，pgrep 去重），也可手动 `jpman keepalive`。

### 7.2 警告先验法（WARN ≠ ERROR）

看到 podman/WSL 警告时，按固定顺序分诊：

1. **最小功能验证**：`podman run --rm hello-world`（容器内 DinP 场景则在容器里执行）。成功 = 警告为降级提示，功能正常，无需处理
2. **检查进入方式**：是否误用 `wsl -d` 交互进入 machine（改用 `podman machine ssh` 后警告消失）
3. **临时三板斧**（确有功能异常时）：
   ```bash
   sudo mount -o remount,shared /
   export XDG_RUNTIME_DIR=/run/user/$(id -u)
   export DBUS_SESSION_BUS_ADDRESS=unix:path=$XDG_RUNTIME_DIR/bus
   ```
4. 以上均无效，再深入排查（日志、复现、查上游 Issue）

> **为什么默认动作是"验证"而不是"修复"？** rootless/WSL2 环境的大部分 WARN 是自动降级提示（如 cgroup v1→cgroupfs 回退、shared mount 建议），功能不受影响。为"消除警告"而改配置，极易引入真故障——典型如给 podman-machine-default 的 `/etc/wsl.conf` 设 `systemd=true`，这是 Podman 官方 Issue [containers/podman#28341](https://github.com/containers/podman/issues/28341) 在常规场景下明确不支持的配置。
>
> **唯一合法例外（2026-10-14 WSL 3.0.3 实测）**：WSL 3.0 下 podman machine 的嵌套 systemd 布局导致 cgroup 控制器完全未委托，**连 hello-world 这类普通容器都无法启动**（不是 WARN，是 crun 直接报错）时，按 §7.3 启用 `systemd=true` 并**必须同时**部署 `/sbin/init` argv[0] shim——单独开 systemd=true 会让 podman start 永远误判机器未运行。判据不满足（容器其实能跑、只是有 WARN）时，本节旧纪律原样有效，禁止动 wsl.conf。

**rootless 容器三必需参数**（jpman 与 compose.yaml 均已内置，手动建容器时不可遗漏）：`--device /dev/fuse`、`--security-opt label=disable`、`--cgroupns=host`。**不需要也不应该加 `--privileged`**。

### 7.3 WSL 3.0 cgroup pids 委托缺失修复（systemd=true + argv[0] shim）

**判据（四条全部满足才走本节；任一不满足回 §7.2，禁止为消 WARN 动 wsl.conf）**：宿主 `wsl --version` 为 3.0.x；任意普通容器（含 hello-world）报 `crun ... pids is not available` 且 cgroup 路径含 `/non-systemd/`；`--cgroups=disabled` 能跑（证明非存储/镜像问题）；machine 内 `/proc/1/cgroup` 在 `/non-systemd/` 且该子树 `cgroup.controllers` 为空。

**根因一句话**：podman machine 不用 WSL 原生 systemd（`/root/bootstrap` 以 unshare 手搓嵌套 systemd），WSL3 将其挂入 `/non-systemd` 子树；层内 9 个跨 PID 命名空间隐藏进程使 `subtree_control` 委托恒 EBUSY，根级旁路 cgroup 跨树迁移恒 EPERM——逐级委托、旁路 cgroup、重启 `user@1000.service`（会终止整个 VM）三条弯路均已实证堵死，源码级根因与证伪记录见参考文档。

**修复（两步缺一不可，machine 内 root 执行）**：① `/etc/wsl.conf` 加 `[boot] systemd=true`，PID1 回到根 `/init.scope`，cpu/io/memory/pids 自动委托；② `/sbin/init` 换成 `exec -a /lib/systemd/systemd /usr/lib/systemd/systemd "$@"` 的 shim——podman 5.8.x 就绪探针（`pkg/machine/wsl/declares.go` 的 `sysdpid`，硬编码 `grep ^/lib/systemd/systemd`）按 argv[0] 字面量匹配，只做①会导致 start 30~50s 后误报 not running（实例实际健康、API 可用）。

**验收口径**：`wsl --shutdown` 冷启动 start 11~15s 成功；`/proc/1/cmdline`=/lib/systemd/systemd 且 user@1000.service 的 controllers 含 `cpu io memory pids`；宿主侧容器 cgroup 路径 `pids.max`=设定值（容器内视图显示 max 是命名空间假象，不足为据）；ssh/API 双路容器正常、映射端口 Windows 侧 HTTP 200。

完整修复/冷启动/验证/回滚命令、`machine rm/init` 后重做要求、podman 升级后去 shim 评估、`cgroups=disabled`/rootful 两个降级退路、PowerShell base64 传参手法见 [references/wsl3-cgroup-fix.md](references/wsl3-cgroup-fix.md)。

## 8. 构建、缓存与导出场景

### 8.1 改了配置要生效 → rebuild（增量，<10 秒）

```bash
bash bin/jpman rebuild
```

直接从项目根的主 Containerfile 构建（`--format docker` + tuna 三镜像源）：配置文件位于 Layer 4 独立层，变更后 Stage 1-3 与 Layer 2/3 缓存全命中，仅 Layer 4/5 重建，秒级完成；完成后自动 start，运行中容器会先停止删除。提速依赖层缓存有效（首次构建或缓存清理后即为全量速度）。

### 8.2 全量重建 → rebuild-all

```bash
bash bin/jpman rebuild-all   # 项目根 podman build -f Containerfile，tuna 三镜像源
```

> **为什么不要在 /mnt/d（9p）上直接全量构建？** Windows 盘挂载到 WSL 的 9p 文件系统 IO 极慢，全量构建可能从分钟级膨胀到数十分钟。把构建上下文先复制到 WSL 原生文件系统（如 `~/build/`）再构建；rebuild 增量场景因上下文在 /tmp 且仅两个小文件，天然不受影响。

### 8.3 镜像缓存（应用内）

```bash
bash bin/jpman save   # 导出 .image-cache/jupyter-podman-rootless-<id>-<ts>.tar.gz（pigz 并行 + SHA256 manifest）
bash bin/jpman load   # 从 latest 缓存恢复
```

应用内缓存位于应用目录 `.image-cache/`；.agents 体系的灾备缓存（`.docker-cache/`，含 doctor/clean/list）是另一套机制，跨项目灾备用 [docker-cache-cmd](../docker-cache-cmd/SKILL.md)。

### 8.4 导出为 WSL 发行版

```bash
bash bin/jpman wsl-export [--force] [--distro-name <名称>] [--install-dir <目录>]
bash bin/jpman wsl-verify [发行版名]   # 14 项冒烟检查（含 Python 3.14 free-threading 检测）
```

导出流程五步（rootful load 缓存→export rootfs→`wsl --import`→写 wsl.conf + conda 激活→terminate 重启+冒烟）。导出的 wsl.conf 明确 `systemd=false`。通用桥接/无 Podman 场景用 [docker-wsl-bridge-cmd](../docker-wsl-bridge-cmd/SKILL.md)。

### 8.5 构建加速分诊速查（invoke build 慢/疑似卡住）

适用：`invoke build`（全量/缓存失效）或 client 侧 `invoke env.build-layer` 长时间停在 **Stage 2 conda-builder（STEP 11/11）**。jpman `rebuild`（§8.1）内置 tuna 三源且上下文在 /tmp，不适用本节。

**第 1 步：先取证再决定是否杀进程（最长 30 秒）**

进入 `podman machine ssh` 会话后执行：

```bash
# 当前构建进程：curl=在下安装包 / apt|dpkg=装系统包 / mamba=conda 求解（收尾阶段）
ps -eo etime,pcpu,comm,args | grep -Ei 'buildah|curl|apt|dpkg|mamba' | grep -v grep

# 5 秒采样网络收包速率（KB/s）
R1=$(awk '/eth0/{print $2}' /proc/net/dev); sleep 5; R2=$(awk '/eth0/{print $2}' /proc/net/dev)
echo "$(( (R2-R1)/1024 )) KB/s"
```

判读：有 `curl ... miniforge.sh` = 安装包下载中（裸 build 的头号瓶颈）；有 apt/dpkg = 系统包阶段；有 mamba = conda 求解中（最慢的下载已过）；流量≈0 但 buildah 在跑 = 9p IO 瓶颈（§8.2）。

**第 2 步：按瓶颈选加速手段（成本从低到高）**

| # | 手段 | 命令/位置 | 适用 |
|---|------|----------|------|
| 1 | **tuna 三镜像源参数**（首选，零副作用） | `invoke build --apt-mirror tuna --conda-mirror tuna --pip-mirror tuna` | 裸 `invoke build` 默认走 Containerfile `*) ` 分支只列 GitHub 单源；实测 GitHub **221 KB/s**（150MB ETA ~11 分钟）→ tuna **7.5 MB/s** |
| 2 | **本地预灌 Miniforge 安装包** | 下载到 `local-cache/miniforge/Miniforge3-Linux-x86_64.sh`（见下） | 断网/反复全量重建；解析顺序为本地缓存（判据 `-s` 非空）→镜像源→GitHub，命中即零下载 |
| 3 | **上下文移出 9p** | 拷到 WSL 原生 fs（如 `~/build/`）再构建（§8.2） | 流量≈0、buildah CPU 低、构建目录在 /mnt/d |

预灌命令（在 podman machine 内，tuna 实测 16 秒/119MB）：

```bash
cd /mnt/d/spaces/SpecWeave/apps/containers/jupyter-podman-rootless
curl -fSL --retry 3 -o local-cache/miniforge/Miniforge3-Linux-x86_64.sh \
  https://mirrors.tuna.tsinghua.edu.cn/github-release/conda-forge/miniforge/LatestRelease/Miniforge3-Linux-x86_64.sh
bash local-cache/miniforge/Miniforge3-Linux-x86_64.sh -h   # 自检必须用 -h（见反模式）
```

- 安装包被 `.gitignore` 忽略（~119MB，仅本机加速，不入库）；架构不同换 `aarch64`
- 灌入后 `COPY local-cache/` 层 hash 变化、Stage 2 重跑一次属预期；之后重跑全缓存
- **实测基线**（2026-09-12，WSL2/podman machine）：本地安装包 + tuna 三源 → Stage 2 conda-builder **148 秒**、全镜像约 5 分钟

**反模式（均有实战实证）**

- ❌ 裸 `invoke build` 不带镜像参数，再把慢归因于"网络/机器卡"——默认分支只有 GitHub 一个源
- ❌ 看到终端长时间无输出就杀构建：先 `ps` 取证，curl 活着就是在下载
- ❌ Windows 用 `... | Select-Object -Last N` 观察构建：该 cmdlet 缓冲到进程结束才输出，伪装成"卡死"；改用 `... 2>&1 | Tee-Object build.log` 流式落盘，另开终端 `Get-Content build.log -Tail 20`
- ❌ 用 `bash Miniforge3-*.sh --help` 自检：安装包不支持 `--help`（退出非 0 被误判 CORRUPT），用 `-h`，或 `od -c` 看头部 `#!/bin/sh`

## 9. 容器内运行模型（排障前必读）

- **Jupyter 以 root 运行**：supervisor 配置 `user=root`，Jupyter 配置在 `/root/.jupyter/`。rootless podman 中容器内 root 映射为宿主机普通用户（subuid 范围），并不拥有宿主机 root 权限
- **隐藏文件显示需双端配置**：服务端 `ContentsManager.allow_hidden=True` + `FileContentsManager.allow_hidden=True` 已内置；Jupyter Lab UI 还需在 View 菜单勾选 **Show Hidden Files**
- **/workspace 权限**：entrypoint 仅 `chmod 777 /workspace`，**无递归 chown**（保护宿主机文件属主）
- **交互默认用户**：`shell`/`exec` 默认 devuser（UID 1000），`--root`/`root` 命令为 root
- sudo：jpman create 硬编码 `GRANT_SUDO=yes`（compose/invoke 路径默认关闭，opt-in 开启）

> **为什么不要把 Jupyter 改成 devuser 运行？** rootless 下容器 root 即宿主机普通用户，以 root 跑 Jupyter 写入绑定挂载的文件属主与宿主机用户一致；改 devuser 反而造成挂载文件权限错配（这正是"rootless 容器内禁止以 devuser 跑 Jupyter"约束的来源）。
>
> **勘误警示**：`JUPYTER_ROOT_CHOWN`（auto/yes/no/named-only）属于 **apps/docker-images/devcontainer-base**（Docker 变体），jupyter-podman-rootless **没有这个机制**。排障时不要把 Docker 变体的经验张冠李戴。

### 9.1 嵌套 Podman 分诊：容器内 podman/podman-compose 报 newuidmap EPERM

**典型症状**（devuser 在容器终端/SSH/Jupyter Terminal 内）：

```
$ podman-compose up
ERRO running `/usr/bin/newuidmap 472 0 1000 1 1 100000 65536`: newuidmap: write to uid_map failed: Operation not permitted
Error: cannot set up namespace using "/usr/bin/newuidmap": exit status 1
ERROR:podman_compose:Prepare images failed
```

伴生 `WARN "/" is not a shared mount` 是无害降级提示（§7.2），**不是**阻断点。

**根因是结构性的，不是配置问题**：外层是非特权 rootless 容器，中间 user namespace 内 root 的能力集（实测 `0x800405fb`）**不含 CAP_SYS_ADMIN(21)**；setuid 的 newuidmap 在中间 ns 内只是"被映射的 root"，内核拒绝它写多行 uid_map → 非 root 用户的容器内 rootless podman 在此环境**必然失败**，容器内调参无法修复。唯一正解是 **B-scheme：让容器内 podman 直连宿主 rootless daemon**（宿主 socket bind-mount 在 `/run/user/1000/podman/podman.sock`），构建/运行全部发生在宿主侧。

> **已被对照实验证伪的方向（不要再试）**：① 改 `/etc/subuid` 区间（100000→524288 对齐外层委托区间，仍 EPERM）；② 容器内 root 跑 podman（single-map 模式连撞 lchown EINVAL `requested 0:42`、devpts EINVAL、cgroup 只读三堵墙，需 `ignore_chown_errors` 等侵入配置且子容器仍跑不起来）；③ `--privileged`（违反 rootless 三必需红线，且不在非特权外层容器能力授予范围内）。

**分诊第 1 步：先确认"报错的容器是不是旧容器"**

镜像修复只对修复后**新建**的容器生效；重建镜像不改变已运行容器。`podman ps` 对比容器 Created 时间与镜像构建时间，并核对镜像内桥接资产：

```bash
podman ps --format "{{.ID}} {{.Names}} {{.CreatedAt}}"
podman exec -u root <容器> ls -l /etc/profile.d/80-podman-host-socket.sh   # 2026-09-12 后镜像才有
```

基底 entrypoint/Containerfile 变更后的完整生效链路：构建端 `invoke build --apt-mirror tuna --conda-mirror tuna --pip-mirror tuna`（§8.5）→ 消费端重建 client 叠加层并重建容器（client 目录 `invoke run --rebuild-layer`）→ **用户重新登录 SSH**（旧会话保留旧环境，不会补注入变量）。

**分诊第 2 步：按真实通道验证（podman exec ≠ SSH，这是最高频误诊点）**

容器 config 注入的 env（`HOST_PODMAN_SOCK` 等）只被 entrypoint 进程子树和 `podman exec` 继承；**sshd+PAM 派生的 SSH 会话会清洗这些变量**（`env -i` 可在 exec 侧复现干净环境）。因此"exec 里 podman 正常"完全不能证明"SSH 里正常"。验证必须走真实通道：

```bash
# VM 内真实 SSH（或用户自己 ssh -p 2222 devuser@localhost 后手动确认）
ssh -p 2222 devuser@<host> 'printenv CONTAINER_HOST'      # ssh host "cmd"：非交互最外层
ssh -tt -p 2222 devuser@<host>                            # 交互登录终端（Jupyter Terminal 同形态）
```

> **测量纪律**：读远程会话变量用 `printenv VAR`，不要在双引号命令里写 `$VAR`——会被 SSH 外层 shell 提前展开为空，制造"变量没注入"的假象。

**五通道桥接矩阵**（镜像自 2026-09-12 起内置，排障时按形态对号入座；权威契约见构建端 [.agents/rules/entrypoint.md](../../../apps/containers/jupyter-podman-rootless/.agents/rules/entrypoint.md) §[4/7]）：

| shell 形态 | 典型入口 | 生效通道 | 失败表现 |
|---|---|---|---|
| 登录 shell | `ssh host`（交互）、`bash -lc` | `/etc/profile.d/80-podman-host-socket.sh` | 交互终端 newuidmap |
| 非登录交互 | Jupyter/IDE Terminal、`bash -ic` | devuser `~/.bashrc` source 同文件 | 同上（最常见报障现场） |
| 非交互脚本文件 | `podman exec … bash x.sh`、cron | 容器 `ENV BASH_ENV` + pam_env 版 `/etc/environment` | 脚本内 newuidmap |
| 非交互命令字符串 | **`ssh host "cmd"`、sshd 最外层** | **sshd_config `SetEnv CONTAINER_HOST`**（entrypoint 运行时写入） | `ssh host podman ps` newuidmap |

> **反直觉点（F1/F2/F3 实证）**：bash **只在执行脚本文件时读 `BASH_ENV`**，对 `bash -c "命令字符串"` 完全不读（profile/.bashrc 也不读）。所以 `ssh host "cmd"` 形态只能靠 sshd `SetEnv`——它不经任何 shell 启动文件，由 sshd 直接把变量放进会话进程环境。

桥接脚本内部为**四级解析**，任一级是真 socket（`-S`）才导出，全缺失则 no-op（无 socket 的回退部署零影响）：

```
显式 CONTAINER_HOST（最高优先；tcp/远程/强制本地 daemon 的唯一逃生手段）
  > HOST_PODMAN_SOCK 环境变量
  > /etc/podman-host-sock.path 事实文件（entrypoint B-scheme 分支写入，覆盖 SSH 环境丢失与非标准挂载点）
  > /run/user/$(id -u)/podman/podman.sock 标准路径自探测
```

**分诊第 3 步：取证命令（需要向他人描述问题时一并附上）**

```bash
cat /proc/self/uid_map                                   # 中间 ns 映射，形如 0 1000 1 / 1 524288 65536
grep CapBnd /proc/self/status                            # 0x...05fb 无 bit21(CAP_SYS_ADMIN) 即结构性死路
ls -l /run/user/$(id -u)/podman/podman.sock              # B-scheme socket 是否挂载
id                                                       # 须在 root 组（entrypoint usermod -aG 处理 EACCES）
cat /etc/podman-host-sock.path 2>/dev/null               # 事实文件
grep -E 'SetEnv CONTAINER_HOST' /etc/ssh/sshd_config     # ssh cmd 形态通道
```

**二级失败（B-scheme 已桥接但报 libpod mkdir 拒绝）**：GUI 透传容器注入 `XDG_RUNTIME_DIR=/tmp/runtime-user`，该挂载点父目录由 podman 自动建为 root:0755，devuser 无法在其中 `mkdir libpod`（`Failed to obtain podman configuration: ... permission denied`）。entrypoint 已在 B-scheme 分支**只 chown 目录本身**对齐属主——手工救急同此操作，**严禁 `chown -R`**（目录内含 wayland-0 单文件 bind-mount，与 podman.sock 穿透改宿主 inode 属主同红线，2026-09-11 事故实证）。

**反模式（均有实战实证）**

- ❌ 在容器内折腾 newuidmap/subuid/userns 试图救活本地 rootless：能力边界是外层容器授予方式决定的，容器内无解
- ❌ 用 `podman exec` 验证后宣称"SSH 已修复"：两者环境模型不同，必须真实 SSH/`env -i` 复核
- ❌ 重建镜像后不重建 client 叠加层、不重建容器，或让用户在旧 SSH 会话里重试：三类"修复没生效"假象
- ❌ 在双引号 SSH 命令里用 `$VAR` 判断注入是否成功：外层 shell 提前展开，用 `printenv`
- ❌ 为消 newuidmap 给容器加 `--privileged`：违反 rootless 三必需（§7.2），且不解决能力缺失

## 10. 安全检查清单（逐项确认）

日常驾驶与排障完成前逐项确认：

- [ ] 已确认操作平台与入口（WSL bash 版 / Windows pwsh 版），且当前位于应用根目录
- [ ] Windows 上已确认 podman machine 就绪（start + sleep infinity 保活）
- [ ] 启动后已核对 `Mounting` 输出行与 info 的 Mount 字段指向预期工作区
- [ ] 已运行 `jpman status` 确认 healthcheck healthy，或已验证浏览器可打开 Jupyter
- [ ] 出现 WARN 时已先执行 hello-world 最小验证，未直接改配置
- [ ] 未为消除普通 WARN 给 podman-machine-default 设置 systemd=true（§7.2 旧纪律）；若已按 §7.3 启用，确认四条件齐备且 `/sbin/init` argv[0] shim 同步部署、wsl --shutdown 冷启动后 start/ssh/pids 三项验证全过；未给容器加 --privileged
- [ ] rebuild / wsl-export 等写操作前，已确认工作区数据与镜像缓存状态
- [ ] 排查权限问题时，已确认未误用 Docker 变体的 JUPYTER_ROOT_CHOWN 经验
- [ ] 容器内 podman 报 newuidmap EPERM 时，未尝试 subuid/特权修复，已按 §9.1 走 B-scheme，并经真实 SSH（非 podman exec）验证、确认容器为修复后新建
- [ ] 已优先使用 jpman 命令，未手动拼接 podman create/run 参数

## 11. 常见错误处理

| 现象 | 场景 | 处理方式 |
|------|------|---------|
| `fuse device not found` | 建容器/容器内挂载 | 确认三必需参数齐全（jpman/compose 已内置）；machine 异常则 `podman machine ssh` 后重查 |
| `Cannot connect to Podman` / 提示 run podman machine start | Windows 机器未起 | `podman machine start` + sleep infinity 保活（§7.1） |
| shared mount / cgroup 类 WARN | 交互会话 | 先 hello-world 验证；检查是否 wsl -d 误进入；三板斧（§7.2） |
| 任意容器报 `crun: controller 'pids' is not available under /sys/fs/cgroup/non-systemd/...` | WSL 3.0.x machine 嵌套 systemd 未委托 cgroup | 核对 §7.3 四条件（含 `--cgroups=disabled` 能跑）；systemd=true + /sbin/init argv[0] shim 两步修复后 wsl --shutdown 冷启动 |
| `podman machine start` 等 30~50s 报 `machine not in running state: ssh error`，但 `wsl -l -v` 显示 Running、gvproxy API 可用 | 已开 systemd=true 但缺 argv[0] shim，podman 就绪探针 grep `^/lib/systemd/systemd` 失配 | 按 §7.3 步骤 2 部署 /sbin/init shim（原符号链接备份 .orig-symlink），wsl --shutdown 后重启 |
| 容器里"数据不见了" | 挂载错误 | 核对 Mounting 行与 WORKSPACE 优先级（§6 步骤3），数据在另一个挂载目录 |
| Jupyter 看不到 .temp/.gitignore | 隐藏文件 | 服务端已配 allow_hidden；UI 勾选 View → Show Hidden Files |
| 忘记 token / 密码 | 访问 | `jpman info` 或 `jpman logs`；默认见 §5 |
| start 后长时间 dots | 健康等待 | 正常，最长 120 秒；超时用 `jpman logs` 查失败原因 |
| invoke build 极慢/卡在 Stage 2 | GitHub 单源/9p | 按 §8.5 两步分诊：tuna 三镜像源参数 + 本地安装包预灌；9p 瓶颈拷 ~/build/ |
| 构建终端长时间无输出 | 观察方式/真下载 | 先 ps 取证（curl 活着=在下载）；勿用 `Select-Object -Last` 观察（§8.5 反模式） |
| bash 脚本语法错误 | CRLF 行尾 | 转 LF 后在 WSL 执行 |
| wsl-export 报 distro exists | 重名 | 加 `--force` 或 `--distro-name` 换名 |
| 容器内 apt 装的包重启后消失 | 容器无状态 | 固化到镜像（改 Containerfile + rebuild-all） |
| 容器内 `newuidmap ... write to uid_map failed: Operation not permitted` | 嵌套 rootless 结构性不可用（中间 ns 无 CAP_SYS_ADMIN） | 按 §9.1：B-scheme 宿主 socket 桥接，勿改 subuid/勿加特权；核对容器是否修复后新建 |
| `podman exec` 里 podman 正常、SSH/Jupyter 终端报 newuidmap | SSH 经 sshd+PAM 清洗容器 env，五通道缺注入 | 按 §9.1 第 2 步真实 SSH 复核；查 profile.d/.bashrc/BASH_ENV/SetEnv 四通道（§9.1 矩阵） |
| `set sticky bit` / `mkdir .../libpod: permission denied`（GUI 透传容器内） | /tmp/runtime-user 挂载点父目录 root:0755 | entrypoint B-scheme 已只 chown 目录本身；手工救急同操作，禁 -R（wayland-0 挂载红线，§9.1） |
| 重建镜像后终端报错依旧 | 旧容器/旧 SSH 会话仍在跑 | 重建 client 叠加层+重建容器（invoke run --rebuild-layer），用户重新登录 SSH（§9.1 第 1 步） |

> 更多 FAQ 见 [13-faq.md](../../../apps/containers/jupyter-podman-rootless/docs/13-faq.md)（SSH 排查 5 步、registry HTTP insecure 配置、toolbox conda 激活等）。

## 12. Gotchas（陷阱与反直觉行为）

### 12.1 路径与编码陷阱

- **`wsl.exe -l -q` 输出是 UTF-16 LE 带 null 字节**：脚本解析发行版列表必须正确解码，否则名称匹配失败
- **.env 逐行解析 ≠ source**：jpman 对 .env 逐行读取以兼容 Windows 反斜杠路径；手动 source 会破坏路径
- **Windows 路径自动转换只在 jpman 内生效**：`jpman start -w D:\x` 会自动转 `/mnt/d/x`；手动执行 `podman run -v D:\x:...` 不转换，必须自己给 POSIX 路径
- **CRLF 行尾**：在 Windows 编辑过的 bash 脚本进 WSL 跑会报语法错误，需转 LF

### 12.2 行为反直觉

- **start 完全幂等**：运行中重复 start 不会重建容器，只显示 info；停止态容器会被删除重建
- **`jpman status` 的 healthcheck 是主动触发**：`podman healthcheck run` 是当场运行一次健康检查，不是读取缓存状态
- **stop 删容器但不删镜像和数据**：镜像（localhost/jupyter-podman-rootless:latest）与 /workspace 挂载均保留
- **两层保活不要混淆**：`jpman keepalive`/start 自动保活的是运行 jpman 的 WSL 会话层（setsid sleep infinity）；`wsl -d podman-machine-default -- sleep infinity` 保的是 podman machine 层
- **rebuild 快的部分原因是上下文在 /tmp**：mktemp 临时目录在 WSL 原生文件系统，只有两个小文件，天然规避 9p
- **GRANT_SUDO 差异**：jpman create 硬编码开启 sudo；compose/invoke 路径默认关闭
- **wsl-export 用 rootful podman**：导出链路自动探测 rootful（sudo -n podman），rootless 降级仅告警

### 12.3 机制边界陷阱

- **嵌套容器内非 root rootless 是结构性死路**：中间 userns root 无 CAP_SYS_ADMIN（能力集 `0x800405fb` 实证），newuidmap 写多行 uid_map 必被内核拒绝；改 /etc/subuid 区间、容器内 root single-map 均已被对照实验证伪。正解只有 B-scheme 直连宿主 daemon（§9.1）
- **podman exec ≠ SSH 会话（环境模型不同）**：`podman exec` 继承容器 config env（HOST_PODMAN_SOCK 等可见）；SSH 经 sshd+PAM 重建环境，这些变量全空。"exec 验证通过"不能证明 SSH 正常，独立 shell 必须真实 SSH 或 `env -i` 复核
- **bash 读 BASH_ENV 挑执行形态**：只在执行**脚本文件**时读，`bash -c "字符串"`（`ssh host "cmd"`）不读任何启动文件；该形态唯一通道是 sshd `SetEnv`（§9.1 五通道矩阵）
- **镜像修复不溯及已运行容器，也不溯及旧 SSH 会话**：需重建 client 叠加层 + 重建容器 + 用户重新登录；三者缺一都会表现为"修复没生效"
- **远程会话读环境变量用 printenv，不要在双引号里写 `$VAR`**：SSH 外层 shell 会提前展开为空，制造"变量没注入"的测量假象
- **裸 `invoke build` 与 jpman rebuild 的源策略不同**：rebuild 内置 tuna 三镜像源；裸 invoke build 默认只有 GitHub 单源，必须显式 `--apt-mirror/--conda-mirror/--pip-mirror tuna`（§8.5）
- **PowerShell `Select-Object -Last N` 会伪装构建"卡死"**：它必须等上游进程结束才输出最后 N 行，长时间构建期间日志文件为 0 字节属观察方式问题而非挂起；用 `Tee-Object` 流式落盘（§8.5）
- **两套镜像缓存互不相通**：应用内 `.image-cache/`（jpman save/load）与 .agents 体系 `.docker-cache/`（docker-cache-cmd）是独立机制，不要互相找文件
- **jpman vs invoke 分工**：jpman 零 Python 依赖、管日常驾驶/缓存/导出；invoke 管 ML 模型、三层后端（podman-compose→podman-py→CLI）、13 个任务。日常驾驶不要绕去 invoke
- **WSL 3.0 的 `/non-systemd` 是委托死区**：podman machine 用 bootstrap+unshare 手搓的 systemd 挂在该子树，层内 9 个跨 PID 命名空间进程在发行版里只显示为 PID 0；对其写 `cgroup.subtree_control` 恒 EBUSY、根级旁路 cgroup 迁进程恒 EPERM（cgroup v2 跨树迁移需写公共祖先 cgroup.procs）。guest 内任何"逐级 echo 控制器"脚本都不要试，正解是 §7.3 改用 WSL 原生 systemd
- **podman 5.8.x 就绪探针按 argv[0] 字面量匹配**：探针 `ps -eo cmd,pid | grep -m 1 ^/lib/systemd/systemd` 不识别符号链接形态的 `/sbin/init`；WSL3 原生 systemd 经 /sbin/init 拉起时实例健康但 start 误判 not running。症状是"wsl -l -v=Running、TCP 59047 可连、手动密钥 SSH 正常，唯独 podman start/ssh 拒绝"——这是客户端状态机误判，别去查 sshd 或防火墙
- **WSL3 原生 systemd 下的两个观察假象**：`wsl --terminate <distro>` 可能不重启 systemd（`journalctl --list-boots` boot id 不变），排障以 `/proc/1/cmdline` 与 boot 列表为准、勿信单次 `wsl -l -v` 的瞬时 Stopped；machine 空闲约 60s 被 vmIdleTimeout 回收是正常现象，重新 start 即可，不是故障

## 13. 关键参考速查表

| 目标 | 参考 |
|------|------|
| jpman 命令与环境变量全表 | [14-jpman-cli.md](../../../apps/containers/jupyter-podman-rootless/docs/14-jpman-cli.md) |
| 首次构建 / invoke 入门 | [01-getting-started.md](../../../apps/containers/jupyter-podman-rootless/docs/01-getting-started.md) |
| FAQ（SSH/registry/toolbox 等） | [13-faq.md](../../../apps/containers/jupyter-podman-rootless/docs/13-faq.md) |
| 构建与 7 步验证规范 | [build-test.md](../../../apps/containers/jupyter-podman-rootless/.agents/rules/build-test.md) |
| 2026-08-27 警告复盘（21 事实/5-Why/警告先验法） | [retrospective-podman-wsl-rootless-warnings-20260827.md](../../../docs/retrospective/reports/task-reports/retrospective-podman-wsl-rootless-warnings-20260827.md) |
| 镜像灾备缓存 | [docker-cache-cmd/SKILL.md](../docker-cache-cmd/SKILL.md) |
| 镜像转 WSL 发行版（通用桥接） | [docker-wsl-bridge-cmd/SKILL.md](../docker-wsl-bridge-cmd/SKILL.md) |
| systemd 不支持上游依据（常规场景） | [Podman Issue #28341](https://github.com/containers/podman/issues/28341) |
| podman 5.8.1 就绪探针源码（argv[0] 硬匹配依据） | `pkg/machine/wsl/declares.go` 的 `sysdpid` 常量（github.com/podman-container-tools/podman v5.8.1） |
| WSL 发行版跨盘迁移 / VHDX 压缩与稀疏化 | [wsl-vhdx-compact-cmd/SKILL.md](../wsl-vhdx-compact-cmd/SKILL.md)（`wsl --manage --move/--compact`、junction 收尾） |

## 14. Changelog

- **v1.3.0** (2026-10-14): 新增 §7.3 WSL 3.0 cgroup pids 委托缺失修复。源于 WSL 2.9.3→3.0.3 升级后 podman machine 普通容器全部报 `crun controller pids is not available`（/non-systemd 路径）的实战排障（七概念 I→F→V→C）：① 源码级根因——podman 5.8.x machine 靠 /root/bootstrap 以 unshare 手搓嵌套 systemd，WSL3 将其挂入 /non-systemd 子树，层内 9 个跨 PID 命名空间进程（cgroup.procs 显示 PID 0）使 subtree_control 恒 EBUSY；② 两条内部修复路径对照实验证伪（逐级委托 EBUSY、根级旁路 cgroup 跨树迁移 EPERM），重启 user@1000.service 会杀整个 VM 立为禁令；③ 正解两步——wsl.conf 启用 WSL 原生 systemd=true（PID1 回根 /init.scope，cpu/io/memory/pids 自动委托）+ /sbin/init argv[0] shim（`exec -a /lib/systemd/systemd`，绕过 declares.go sysdpid 探针 `grep ^/lib/systemd/systemd` 的字面量失配，单独开 systemd=true 会导致 start 30~50s 误报 not running）；④ 验证含宿主侧 pids.max=42 实证（容器内命名空间视图显示 max 不足为据）、nginx -p 18080 Windows HTTP 200、wsl --shutdown 冷启动 11~15s、ssh/API 双路；⑤ 同步修正"禁止 systemd=true"旧纪律为唯一例外边界（四条件判据），决策树、§3 触发词、§10 安全清单、§11 错误表（2 行）、§12.3 Gotchas（3 条：non-systemd 死区/argv[0] 探针/terminate 与 vmIdleTimeout 观察假象）、frontmatter description 同步；完整修复手册（命令块、回滚、降级退路、base64 传参手法）按渐进式披露抽到 references/wsl3-cgroup-fix.md，正文 §7.3 保留判据与决策摘要，质量门禁 34 项全 PASS。
- **v1.2.0** (2026-09-12): 新增 §9.1 嵌套 Podman 分诊。源于两轮"SSH 终端 podman-compose up 报 newuidmap EPERM"实战（七概念 F→V→C 链路）：① 根因实证为结构性能力缺失（中间 userns root 能力集 `0x800405fb` 无 CAP_SYS_ADMIN，setuid newuidmap 写多行 uid_map 必被拒），改 /etc/subuid 区间（100000→524288）、容器内 root single-map（lchown/devpts/cgroup 三墙）两个假设均被对照实验证伪，正解为 B-scheme 宿主 socket 直连；② 沉淀 SSH 五通道桥接矩阵（profile.d/.bashrc/ENV BASH_ENV/pam_env 版 /etc/environment/sshd SetEnv），关键反直觉点：sshd+PAM 清洗容器 config env（podman exec 与 SSH 环境模型不同）、bash 仅脚本文件形态读 BASH_ENV；③ 桥接脚本四级解析顺序（显式 CONTAINER_HOST＞env＞事实文件＞标准路径自探测）；④ 三条验证纪律（真实 SSH/env -i 复核、printenv 读变量防引号展开假象、修复需重建叠加层+容器+重新登录）。决策树、触发词、§10 安全清单、§11 错误表（4 行）、§12.3 Gotchas（5 条）、frontmatter description 同步。
- **v1.1.0** (2026-09-12): 新增 §8.5 构建加速分诊速查。源于一次"构建疑似卡死"排障的实证：裸 `invoke build` 默认只走 GitHub 单源（实测 Miniforge 下载 221 KB/s、ETA ~11 分钟），取证后确认非挂起；tuna 三镜像源参数 + 本地安装包预灌（`local-cache/miniforge/`，解析顺序本地→镜像源→官方）使 Stage 2 conda-builder 降至 148 秒、全镜像约 5 分钟。同步沉淀 4 条反模式（裸 build 不带镜像参数、无输出即杀进程、`Select-Object -Last` 缓冲伪装卡死、安装包 `--help` 自检假阳性须用 `-h`）；决策树、触发词、§11 错误表、§12.3 Gotchas 同步；顺带修复 §2/§6/§13 共 7 条既有断链（apps 相对路径少一层 `../`）。
- **v1.0.0** (2026-08-29): 初始版本。基于 jupyter-podman-rootless 日常运维实践与 2026-08-27 podman/WSL rootless 警告复盘萃取（42 条事实、4 条跨案例洞察、4 视角对抗审查）。覆盖 machine 就绪纪律、jpman 幂等驾驶 SOP、警告先验法分诊、rootless 运行模型、构建/缓存/导出路由；含 15 条反模式、9 项安全检查清单、12 条 Gotchas；与 docker-cache-cmd、docker-wsl-bridge-cmd 建立边界路由。
