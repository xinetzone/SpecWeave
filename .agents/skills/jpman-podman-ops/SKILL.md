---
name: jpman-podman-ops
version: 1.0.0
description: "jupyter-podman-rootless（jpman）容器日常运维与 Podman on WSL2 驾驶纪律。当用户提到 jpman、启动/重启/停止 Jupyter 容器、jupyter 容器起不来、podman machine、podman 机器未运行、工作区挂载(-w)、挂载目录不对、容器警告/WARN 分诊、fuse device not found、Jupyter 隐藏文件不显示、rootless podman 排障、jpman start/restart/status/logs/shell、WSL 保活(keepalive) 等场景时，必须使用此技能。封装日常驾驶 SOP（machine 就绪预检→幂等 start→Mounting 行核对→healthcheck 验证→WARN 警告先验分诊）、rootless 三必需参数、容器内 root 运行模型、.env 与工作区路径优先级、rebuild 增量/全量构建选择，并与 docker-cache-cmd（镜像灾备缓存）、docker-wsl-bridge-cmd（镜像转 WSL 发行版）形成边界路由。不要手动拼接 podman 命令或套用 Docker 经验排障——本 Skill 已封装 podman machine ssh 纪律、禁止 systemd=true、hello-world 最小验证等实战教训。"
argument-hint: "<日常操作> [start|stop|restart|status|info|logs|shell|rebuild...] [选项]"
disable-model-invocation: false
user-invocable: true
paths:
  - ".agents/skills/jpman-podman-ops/**"
  - "apps/containers/jupyter-podman-rootless/bin/**"
title: "jpman 容器日常运维 (jpman Podman Ops)"
x-toml-ref: "../../.meta/toml/.agents/skills/jpman-podman-ops.toml"
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
| ML 模型管理 / invoke 任务 / 首次构建镜像 | 应用内 invoke，见 [01-getting-started.md](../../apps/containers/jupyter-podman-rootless/docs/01-getting-started.md) |

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

> **关于触发**：即使没有明确说"用 skill"，只要涉及 jupyter-podman-rootless 容器的日常操作与排障，就应使用本技能，不要手动拼接 `podman create` 参数或凭 Docker 经验操作——rootless/WSL2 的约束与 Docker Desktop 完全不同。

## 4. 任务路由决策树

```
用户要对 jupyter-podman-rootless 做什么？
├─ 日常启停/进入/日志/查访问地址？            → §6 日常驾驶 SOP
├─ podman machine 连不上/报连接错误/启动有 WARN？ → §7 machine 就绪与警告分诊
├─ 改了配置/装了包要固化进镜像？               → §8 构建场景（rebuild 增量 vs rebuild-all 全量）
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

> 完整参数表以 [14-jpman-cli.md](../../apps/containers/jupyter-podman-rootless/docs/14-jpman-cli.md) 与 `jpman help` 为准（命令可能随版本演进）。

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

> **为什么默认动作是"验证"而不是"修复"？** rootless/WSL2 环境的大部分 WARN 是自动降级提示（如 cgroup v1→cgroupfs 回退、shared mount 建议），功能不受影响。为"消除警告"而改配置，极易引入真故障——典型如给 podman-machine-default 的 `/etc/wsl.conf` 设 `systemd=true`，这是 Podman 官方 Issue [containers/podman#28341](https://github.com/containers/podman/issues/28341) 明确不支持的配置。

**rootless 容器三必需参数**（jpman 与 compose.yaml 均已内置，手动建容器时不可遗漏）：`--device /dev/fuse`、`--security-opt label=disable`、`--cgroupns=host`。**不需要也不应该加 `--privileged`**。

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

## 9. 容器内运行模型（排障前必读）

- **Jupyter 以 root 运行**：supervisor 配置 `user=root`，Jupyter 配置在 `/root/.jupyter/`。rootless podman 中容器内 root 映射为宿主机普通用户（subuid 范围），并不拥有宿主机 root 权限
- **隐藏文件显示需双端配置**：服务端 `ContentsManager.allow_hidden=True` + `FileContentsManager.allow_hidden=True` 已内置；Jupyter Lab UI 还需在 View 菜单勾选 **Show Hidden Files**
- **/workspace 权限**：entrypoint 仅 `chmod 777 /workspace`，**无递归 chown**（保护宿主机文件属主）
- **交互默认用户**：`shell`/`exec` 默认 devuser（UID 1000），`--root`/`root` 命令为 root
- sudo：jpman create 硬编码 `GRANT_SUDO=yes`（compose/invoke 路径默认关闭，opt-in 开启）

> **为什么不要把 Jupyter 改成 devuser 运行？** rootless 下容器 root 即宿主机普通用户，以 root 跑 Jupyter 写入绑定挂载的文件属主与宿主机用户一致；改 devuser 反而造成挂载文件权限错配（这正是"rootless 容器内禁止以 devuser 跑 Jupyter"约束的来源）。
>
> **勘误警示**：`JUPYTER_ROOT_CHOWN`（auto/yes/no/named-only）属于 **apps/docker-images/devcontainer-base**（Docker 变体），jupyter-podman-rootless **没有这个机制**。排障时不要把 Docker 变体的经验张冠李戴。

## 10. 安全检查清单（逐项确认）

日常驾驶与排障完成前逐项确认：

- [ ] 已确认操作平台与入口（WSL bash 版 / Windows pwsh 版），且当前位于应用根目录
- [ ] Windows 上已确认 podman machine 就绪（start + sleep infinity 保活）
- [ ] 启动后已核对 `Mounting` 输出行与 info 的 Mount 字段指向预期工作区
- [ ] 已运行 `jpman status` 确认 healthcheck healthy，或已验证浏览器可打开 Jupyter
- [ ] 出现 WARN 时已先执行 hello-world 最小验证，未直接改配置
- [ ] 已确认未给 podman-machine-default 设置 systemd=true、未给容器加 --privileged
- [ ] rebuild / wsl-export 等写操作前，已确认工作区数据与镜像缓存状态
- [ ] 排查权限问题时，已确认未误用 Docker 变体的 JUPYTER_ROOT_CHOWN 经验
- [ ] 已优先使用 jpman 命令，未手动拼接 podman create/run 参数

## 11. 常见错误处理

| 现象 | 场景 | 处理方式 |
|------|------|---------|
| `fuse device not found` | 建容器/容器内挂载 | 确认三必需参数齐全（jpman/compose 已内置）；machine 异常则 `podman machine ssh` 后重查 |
| `Cannot connect to Podman` / 提示 run podman machine start | Windows 机器未起 | `podman machine start` + sleep infinity 保活（§7.1） |
| shared mount / cgroup 类 WARN | 交互会话 | 先 hello-world 验证；检查是否 wsl -d 误进入；三板斧（§7.2） |
| 容器里"数据不见了" | 挂载错误 | 核对 Mounting 行与 WORKSPACE 优先级（§6 步骤3），数据在另一个挂载目录 |
| Jupyter 看不到 .temp/.gitignore | 隐藏文件 | 服务端已配 allow_hidden；UI 勾选 View → Show Hidden Files |
| 忘记 token / 密码 | 访问 | `jpman info` 或 `jpman logs`；默认见 §5 |
| start 后长时间 dots | 健康等待 | 正常，最长 120 秒；超时用 `jpman logs` 查失败原因 |
| 全量构建极慢 | 9p 文件系统 | 拷上下文到 WSL 原生 fs（~/build/）；日常改配置用 rebuild |
| bash 脚本语法错误 | CRLF 行尾 | 转 LF 后在 WSL 执行 |
| wsl-export 报 distro exists | 重名 | 加 `--force` 或 `--distro-name` 换名 |
| 容器内 apt 装的包重启后消失 | 容器无状态 | 固化到镜像（改 Containerfile + rebuild-all） |

> 更多 FAQ 见 [13-faq.md](../../apps/containers/jupyter-podman-rootless/docs/13-faq.md)（SSH 排查 5 步、registry HTTP insecure 配置、toolbox conda 激活等）。

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

- **两套镜像缓存互不相通**：应用内 `.image-cache/`（jpman save/load）与 .agents 体系 `.docker-cache/`（docker-cache-cmd）是独立机制，不要互相找文件
- **jpman vs invoke 分工**：jpman 零 Python 依赖、管日常驾驶/缓存/导出；invoke 管 ML 模型、三层后端（podman-compose→podman-py→CLI）、13 个任务。日常驾驶不要绕去 invoke

## 13. 关键参考速查表

| 目标 | 参考 |
|------|------|
| jpman 命令与环境变量全表 | [14-jpman-cli.md](../../apps/containers/jupyter-podman-rootless/docs/14-jpman-cli.md) |
| 首次构建 / invoke 入门 | [01-getting-started.md](../../apps/containers/jupyter-podman-rootless/docs/01-getting-started.md) |
| FAQ（SSH/registry/toolbox 等） | [13-faq.md](../../apps/containers/jupyter-podman-rootless/docs/13-faq.md) |
| 构建与 7 步验证规范 | [build-test.md](../../apps/containers/jupyter-podman-rootless/.agents/rules/build-test.md) |
| 2026-08-27 警告复盘（21 事实/5-Why/警告先验法） | [retrospective-podman-wsl-rootless-warnings-20260827.md](../../docs/retrospective/reports/task-reports/retrospective-podman-wsl-rootless-warnings-20260827.md) |
| 镜像灾备缓存 | [docker-cache-cmd/SKILL.md](../docker-cache-cmd/SKILL.md) |
| 镜像转 WSL 发行版（通用桥接） | [docker-wsl-bridge-cmd/SKILL.md](../docker-wsl-bridge-cmd/SKILL.md) |
| systemd 不支持上游依据 | [Podman Issue #28341](https://github.com/containers/podman/issues/28341) |

## 14. Changelog

- **v1.0.0** (2026-08-29): 初始版本。基于 jupyter-podman-rootless 日常运维实践与 2026-08-27 podman/WSL rootless 警告复盘萃取（42 条事实、4 条跨案例洞察、4 视角对抗审查）。覆盖 machine 就绪纪律、jpman 幂等驾驶 SOP、警告先验法分诊、rootless 运行模型、构建/缓存/导出路由；含 15 条反模式、9 项安全检查清单、12 条 Gotchas；与 docker-cache-cmd、docker-wsl-bridge-cmd 建立边界路由。
