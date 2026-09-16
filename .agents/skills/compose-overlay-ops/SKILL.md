---
name: compose-overlay-ops
version: 1.0.1
description: "apps/containers/client 下 podman-compose 工作负载叠加栈（quant.* / xmnn.* / monetize.* 三命名空间，overlays/onnx-quantized、overlays/xmnn-dev、overlays/agent-monetize-dev）的启动/停止/重建/冒烟验证运维编排。当用户提到启动/重启/重新构建/重建 xmnn-dev、onnx-quantized、agent-monetize-dev 叠加栈或镜像，xmnn.up/xmnn.build/xmnn.smoke、quant.up、monetize.up，栈起不来、容器 Exited (0)、Jupyter 8890/8888/8892 打不开、netavark nft 报错、nftables、保存 notebook Errno 13、checkpoint 权限、WSL 发行版回收容器、发行版里跑 podman-compose、基底镜像缺失、tuna 构建 xmnn 镜像 等场景时，必须使用此技能。封装经实证的标准 SOP（保活锚→四维修复预检→build→up→浸泡→官方 smoke→双端端口/保存验证）、执行发行版选择（jupyter-podman-rootless 而非 flapping machine）、普通重建与 --no-cache 的裁决、8 个本机实证陷阱。与 jpman-podman-ops（单容器日常驾驶/构建端/嵌套 Podman）、client-overlay-scaffold（新建叠加栈）形成边界路由；不要手动拼 podman-compose 参数或套用 Docker Desktop 经验。"
argument-hint: "<栈名> <up|down|build|rebuild|smoke|ps|logs> [选项]"
disable-model-invocation: false
user-invocable: true
paths:
  - ".agents/skills/compose-overlay-ops/**"
  - "apps/containers/client/overlays/**"
  - "apps/containers/client/src/jpman_client/tasks/{quant,xmnn,monetize}.py"
title: "Compose 叠加栈运维 (compose-overlay-ops)"
---

# Compose 叠加栈运维 (compose-overlay-ops)

> 本 Skill 是 **client 已交付叠加栈的运行编排层**：把 2026-09-14 xmnn-dev
> 首次实战启动、EACCES 修复、镜像重建三次任务中实证的环境纪律与排障链路
> 固化为可复用 SOP。所有结论均有当次工具输出证据，排障时**以容器内实时
> `ps/stat/logs` 实证为准**，不得凭本文件推断替代取证。

## 1. Skill ID
`compose-overlay-ops`（内部 ID；对外名称：**叠加栈运维**）

## 2. 功能与边界

| Skill | 管辖对象 | 不管辖 |
|---|---|---|
| **compose-overlay-ops（本）** | **已交付**的 quant/xmnn/monetize compose 栈：启动、停止、重建镜像、重建栈、冒烟、运行时权限/网络/发行版排障 | 新建栈（→ scaffold）、构建端基底镜像、镜像灾备、嵌套 Podman |
| jpman-podman-ops | jpman 单容器日常驾驶、构建端镜像 rebuild、.image-cache/wsl-export、容器内嵌套 podman（newuidmap EPERM §9.1）、machine 就绪通用纪律 | compose 工作负载栈编排 |
| client-overlay-scaffold | **从零新建**一个叠加栈（12 件套/骨架模板/接线登记） | 栈交付后的运行 |
| docker-cache-cmd / docker-wsl-bridge-cmd | 镜像 tar 灾备、镜像转 WSL 发行版 | — |

> **为什么独立于 jpman-podman-ops？** jpman 管的是命令式**单容器**
> （`podman run` 谱系）；叠加栈是声明式 **podman-compose 子进程层**
> （invoke 任务内禁 `import podman`），有独立的路径注入、构建期守卫、
> 端口表与宿主侧编排修复（如 checkpoint 权限），两套 SOP 混用过载。

## 3. 三栈速查（单一事实源=各 compose.yaml 与 tasks 模块）

| 命名空间 | overlay 目录 | 宿主端口（SSH/Jupyter） | 特有内容 |
|---|---|---|---|
| `quant.*`（6 任务） | overlays/onnx-quantized | 2222 / 8888 | ONNX 五包，纯 cp314t |
| `xmnn.*`（8 任务） | overlays/xmnn-dev | 2223 / 8890 | 双 ABI（base cp314 GIL 打包/main cp314t 服务）、LLVM 22.1.8、Nuitka 4.1.3、bind npu_tvm/npuusertools/models |
| `monetize.*`（8 任务） | overlays/agent-monetize-dev | 2224 / 8892 | apt clang + apache-tvm-ffi，单一 cp314 GIL |

> 任务清单、环境变量键、守卫契约以 client `AGENTS.md` 路由表与
> `.agents/rules/{quant,xmnn,monetize}-overlay.md` 为权威；本 Skill 不复制其内容。

## 4. 何时触发

- "启动/拉起/重启/重建 xmnn-dev（或 quant/monetize）栈/镜像/容器"
- "xmnn.up / xmnn.build / xmnn.smoke / quant.up / monetize.up 失败/卡住"
- 容器状态 `Exited (0)`、Jupyter 端口打不开、netavark/nft 报错
- Jupyter 保存 notebook `[Errno 13] .ipynb_checkpoints`
- WSL 发行版里跑 podman-compose、基底镜像"缺失"误报、tuna 构建
- 即使没说"用 skill"，只要操作对象是上述三个 overlay 栈即应加载本 Skill。

## 5. 执行环境决策树（先选对发行版，再做任何事）

```
要在 Windows 宿主上操作叠加栈？
├─ 在哪个发行版跑 invoke？
│   ├─ 首选 podman-machine-default 发行版（唯一执行环境）
│   │    实证：自带 podman 5.7.0、/mnt/d 直通、sudo 免密、Python 3.14、
│   │    历史上已 load 全部 localhost 镜像；无 systemd
│   │    （2026-09-15 改名顶替：注销 flapping 的 Podman Desktop machine 后，
│   │    把 jupyter-podman-rootless 经 export/unregister/import 改名为
│   │    podman-machine-default 并设默认；compose 桥接默认名随之变更）
│   └─ 历史教训（原 Podman Desktop machine 已删除）：gvproxy 不驻留、
│       start 成功后空闲即退（ssh 竞态）、镜像存储与 jupyter 发行版不互通
├─ 发行版存活纪律
│   ├─ 每个 wsl.exe 命令结束后发行版可能被回收（vmIdleTimeout=-1 只保 VM）
│   │   → 长任务/长驻栈前先开保活锚（§6 步骤 0）
│   └─ 无 systemd：XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir（WSLg），
│       禁止改成 /run/user/<uid>（会 lstat 失败）
└─ Windows 原生 CPython？ → 默认自动桥接到上述发行版（COMPOSE_WSL_DISTRO
   可覆盖、none 回退门禁）；亦可手动进 WSL 发行版执行
```

## 6. 标准 SOP

### 步骤 0：保活锚（后台，整个会话持有）

```powershell
wsl -d podman-machine-default -- sleep infinity   # 后台运行，勿关
```

> **为什么必须先开？** 无锚时最后一个 wsl 客户端退出 → 发行版回收 →
> 容器整体被杀，`podman ps -a` 显示 `Exited (0) 292 years ago`，
> 入口日志停在中段，极易误诊为 entrypoint 崩溃（2026-09-14 包裹式入口
> 尸检实证：连 `sleep infinity` 兜底进程都被杀=外部回收，非应用退出）。

### 步骤 1：四维修复预检（只读，先取证再动手）

```bash
wsl -d podman-machine-default -- bash -lc '
  podman ps -a --format "{{.Names}} | {{.Status}}" ;
  podman images --format "{{.Repository}}:{{.Tag}}" | grep -E "xmnn|quant|monetize|jupyter-podman-rootless" ;
  ls -d /mnt/d/spaces/SpecWeave/external/chaos/{npu_tvm,npuusertools,models} 2>/dev/null'
```

- **栈容器**：Exited 多为发行版回收（步骤 0 后重新 up 即可）
- **基底镜像缺失**：从构建端缓存载入（31 秒实测）：
  `podman load -i /mnt/d/spaces/SpecWeave/apps/containers/jupyter-podman-rootless/.image-cache/jupyter-podman-rootless-latest.tar.gz`
- **compose 工具缺失**（首次，2026-09-15 实证于 Fedora 43 Container Image
  发行版：自带 python3 3.14 但**无 pip**，且 jpman-common 是 PyPI 不发布的
  本地兄弟包，直接装 client 必报 `No matching distribution found for
  jpman-common`）。正确安装序三步（均 `--user`，产物落 `~/.local/bin`，
  桥接器已自动把该目录前置到 PATH）：
  ```bash
  python3 -m ensurepip --user
  cd /mnt/d/spaces/SpecWeave/apps/containers/client
  python3 -m pip install --user -e ../shared -i https://pypi.tuna.tsinghua.edu.cn/simple
  python3 -m pip install --user -e '.[compose]' -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```
- **nft 缺失**（bridge 网络）：`sudo apt-get install -y nftables`
  （报错 `netavark: unable to execute "nft"` 时）

### 步骤 2：构建镜像（普通重建，勿默认 --no-cache）

```bash
# 推荐固化一个执行器脚本（避免 PowerShell→wsl 的 $ 插值问题，见 §9 陷阱 7）：
#   export PATH="$HOME/.local/bin:$PATH"
#   cd /mnt/d/spaces/SpecWeave/apps/containers/client && exec invoke "$@"
wsl -d podman-machine-default -- bash <run-inv.sh> xmnn.build --pip-mirror tuna --conda-mirror tuna
```

- 普通重建命中层缓存，**镜像 ID 不变是正常结论**（修复若只在宿主侧
  invoke 代码，镜像内容本就不变）；仅当 Containerfile/构建资产变更或明确
  要求时才 `--no-cache`（xmnn 全量约 6 分钟，重下 LLVM 427MB）。
- 长构建用后台任务 + 流式落盘观察；**禁止 `Select-Object -Last N`**
  （它缓冲到进程结束才输出，伪装"卡死"）。
- 构建日志中 `WARN SHELL/HEALTHCHECK is not supported for OCI image
  format` = 设计内（Containerfile 全部 RUN 显式 `/bin/bash -lc`）；
  Nuitka 探针 `failed to detect GCC version` 是 stderr 噪音，守卫只认退出码。

### 步骤 3：启动 / 重建栈

```bash
invoke xmnn.up                 # 默认随带构建
invoke xmnn.down && invoke xmnn.up --skip-build   # 重建栈（换镜像/换配置后必须）
```

### 步骤 4：浸泡后再验证（不要 up 完立刻下结论）

- 等 **45~90 秒**：entrypoint Step 4 含最长 30s socket 等待循环，
  Jupyter 其后还要 ~5s；随后 `invoke xmnn.ps` 必须是 `Up`。
- 官方冒烟：`invoke xmnn.smoke`（工具链守卫 + 挂载/import/算例；
  libtvm 已编译时会真实跑 `tvm.build('llvm')` 向量加）。
- 双端端口：WSL 内 `curl -o /dev/null -w '%{http_code}' 127.0.0.1:8890/lab`
  期望 302；Windows PowerShell `Invoke-WebRequest http://localhost:8890/lab`
  同样期望 302；SSH 端口 TCP 可连。
- 凭证：密码/token 看**容器启动 banner**（ServerApp 日志里 `token=...`
  是脱敏，不是真值）。

## 7. 运行时权限：Jupyter checkpoint Errno 13

**症状**：notebook 本体能存，保存 checkpoint 报
`[Errno 13] Permission denied: '/workspace/.ipynb_checkpoints/<nb>-checkpoint.ipynb'`。

**根因（实证链）**：Jupyter 经 supervisord 以 **devuser(uid 1000)** 运行；
rootless+9p/drvfs 下容器内 root 预建的 checkpoint 目录在容器视角为
`0:0 755`，devuser 无 w 位；而 `/workspace` 根本身被 entrypoint chmod 777
（非递归），所以 notebook 本体可写、子目录不可写。

**修复（已固化在编排层）**：`utils.ensure_workspace_checkpoint_writable()`
在 xmnn/quant 的 `_prepare_env()` mkdir 工作区后幂等 `chmod 0777` **仅
`.ipynb_checkpoints` 单一目录**（不改属主、不递归、不碰源码 bind；
drvfs metadata 模式宿主 chmod 即时透传容器视图）。手工救急：
`chmod 777 apps/containers/client/workspace/.ipynb_checkpoints`。

> **修复落点纪律**：这类问题在**编排层（宿主 invoke）**修，不回灌
> 基底镜像/entrypoint（薄叠加不覆盖基底，且镜像重建不影响已建容器）。

## 8. 安全检查清单

- [ ] 已开保活锚，且整条命令链在同一发行版（podman-machine-default）
- [ ] 未覆盖 XDG_RUNTIME_DIR；未给 machine 发行版设 systemd=true
- [ ] compose 栈未出现 `--privileged`；三必需只用标准字段（devices/
      security_opt/cgroupns），与各 `*-overlay.md` 一致
- [ ] 普通重建优先缓存；`--no-cache`/清卷/注销发行版等破坏性操作须用户明确授权
- [ ] up 后浸泡 ≥45s 再判活；下"已修复"结论前有 ps/curl/smoke 真实输出
- [ ] 外部源码树（npu_tvm/npuusertools）只读挂载，验收无 `.bak_*` 残留
- [ ] 栈 down 默认保留 ccache 命名卷；`--volumes` 才删除
- [ ] 诊断脚本放 `.temp/`（不入库），探针文件测完即删

## 9. 错误处理速查

| 现象 | 实证根因 | 处理 |
|---|---|---|
| 容器 `Exited (0)`、日志停在中段 | 发行版空闲被回收（非应用崩溃） | 开保活锚 → `xmnn.down && xmnn.up --skip-build` |
| **假 Up**：`podman ps` 显示 Up、`inspect .State.Pid` 有值且 status=running、Jupyter 端口甚至仍 302，但任何 `exec` 报 `crun: container <id> does not exist: open $XDG_RUNTIME_DIR/crun/<id>/status: No such file or directory`；该 PID 在宿主 `ps -p` 已不存在，`crun/` 目录下只剩 `.cache`/`.empty-directory` | conmon/容器进程在发行版回收循环中被杀，但 libpod sqlite 仍记 running；stale conmon 与 rootlessport 作为孤儿进程存活（端口/HTTP 因此假象正常）。**ps 与端口都不可信，`podman exec <name> echo ok` 是唯一活体判据** | **定向清理（免 `wsl --shutdown`，2026-09-15 实证，不影响同发行版其他栈）**：①`invoke <ns>.down`（容忍 `conmon exited prematurely`/netavark netns ENOENT 告警，记录已删）；②`ss -ltnp \| grep <端口>` 找孤儿 **rootlessport** PID → `kill`；③`ps -ef \| grep <容器ID>` 找 **stale conmon** PID → `kill`；④复查端口 free；⑤`invoke <ns>.up --skip-build` → 浸泡 70~90s → exec+curl 双验证 |
| `podman machine ssh` 报 not running（start 刚成功） | machine gvproxy 不驻留、空闲回收 | 原 flapping machine 已删除（由 jupyter-podman-rootless 改名顶替） |
| 守卫误报"本地缺少基底镜像"（镜像明明在） | `.env` 空 `CONTAINER_HOST=` 被注入致 podman CLI 误入 REST 模式 exit 125 | 已修为仅注入非空值（manage._load_env_overrides）；勿在 shell 里 export 空串 |
| `netavark: unable to execute "nft"` | 发行版缺 nftables | `sudo apt-get install -y nftables` |
| `lstat /run/user/1001: no such file` | 错误覆盖 XDG_RUNTIME_DIR | 删除覆盖，沿用 /mnt/wslg/runtime-dir |
| Jupyter 保存 Errno 13（checkpoint） | root 预建目录 0:0 755 | §7（编排层已自动 chmod；手工 chmod 777） |
| `npu_tvm 源码树宿主路径不存在`（指向 client/external） | 默认路径锚错层级；仓库根=client.parents[2] | xmnn.py 已修；自定义栈注意同级锚定 |
| aardvark-dns / user scope bus 报错 | machine 无 systemd user bus | compose 已声明 `network_mode: bridge`（带证据偏差，勿删） |
| `up -d` 报 `rootlessport listen tcp 0.0.0.0:2223: bind: address already in use`（exit 125），前序常伴 `conmon exited prematurely: conmon process killed`，同一次 up 先打印旧容器 ID 又打印新容器 ID；换端口却能成功 | **四因（① 为 2026-09-15 晚实证的确定性首因，三次复现）**：① **跨控制平面标签分歧**——Windows 原生裸 `podman-compose`（overlay 目录执行）给容器打 `com.docker.compose.project.config_files=D:\...`，Windows `invoke`（透明桥接）/WSL invoke 固定用 `--file /mnt/d/...`；compose config-hash 按标签**原文**计算，两平面交替即判漂移强制 recreate，pod 模式强拆 infra conmon 时 rootlessport 已被 WSL `/init` 收养为孤儿，新 pod bind 必败（**先优雅 down 也可能留同样孤儿**）；同平面连续执行幂等可作鉴别。② Created/Exited 残留容器持有端口分配。③ **假 Up 后容器被 down 但孤儿 rootlessport 存活**：`ss -ltnp` **能**看到 `users:(("rootlessport",pid=NNN))` 显式持有者；同时查杀 stale conmon（见"假 Up"行）。④ WSL localhost 转发（wslrelay）粘滞：幽灵 LISTEN 无可见持有者，`ss/netstat/fuser/lsof` 查不到≠没占 | **首选 `invoke <ns>.up --skip-build`**：up 前 `up_preflight` 三道全自动（v1.0.3）——残留 compose down / 跨平面活体栈先优雅 down / 孤儿 rootlessport 经 `ss -ltnp` 定点 kill（只认 rootlessport 名，不碰他栈 pasta），裸 compose 翻车现场直接重跑即恢复。**纪律：同一栈固定单一控制平面**，勿在 Windows 裸 compose 与 invoke 间来回切。手工兜底：`ss -ltnp \| grep <端口>` 有显式持有者定向 kill；无持有者=wslrelay 粘滞才用 `wsl --shutdown`（需用户授权，波及同发行版全部栈）或 `.env` 固化换端口 2225/8891 |
| **Windows 原生 `inv <ns>.build`（或任何桥接任务）不执行任务，终端却进入一个交互 shell**（伴随 *automatically entered into a nested process namespace... to log out you need to exit twice* 的 motd，原 build 命令丢失，2026-09-16 实证） | **桥接登录 shell 被 enterns 劫持**：桥接器曾下发 `wsl -d podman-machine-default -- bash -lc <任务>`；Fedora-WSL 系镜像的 `/etc/profile.d/enterns.sh` 在检测到嵌套 systemd（`/lib/systemd/systemd` 非 PID 1）时无参执行 `/usr/local/bin/enterns`，对普通用户走 `sudo nsenter -m -p -t <pid> su -l $USER`——拉起全新交互登录 shell，`-lc` 任务串在命名空间切换中被丢弃；同目录 `docker-host.sh` 登录即跑 `podman info`，podman 未就绪时还会污染 `DOCKER_HOST=unix://`（client W-I11） | **已自动修复（editable 即时生效，零操作）**：桥接改非登录 `bash -c`（PATH 显式前置 `~/.local/bin`、LANG 兜底 C.UTF-8），profile 两个副作用均不触发。手工纪律：在该发行版跑自动化一律 `wsl -d <d> -- bash <script.sh>`（非登录，与 run-inv.sh 同构），不要用裸 `wsl -d <d>` 登录会话承载任务；已误入嵌套 shell 时连按两次 `exit`/Ctrl-D 退出 |
| podman 任意命令（含 WSL 内原生 invoke）报 `creating events dirs: mkdir /run/user/1000: permission denied`（exit 125），warning `RunRoot ... not writable`；常伴容器 `Exited (0) 292 years ago` | **VM 回收后 tmpfs 运行时目录未重建**：`/run/user/<uid>` 在 tmpfs 上，由 systemd-logind/pam 会话创建；本发行版无 systemd 于 PID 1，VM 重启后未经 enterns 进 systemd ns 的会话不重建该目录；rootless podman events/runroot 硬编码回退此路径（**仅 export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir 不能替代**，client W-I12） | **已自动修复（零操作）**：`inv <ns>.*` 的 Linux 放行路径调 `ensure_wsl_rootless_runtime()`（仅 WSL2），`sudo -n mkdir/chown/chmod 700` 幂等重建，免密不可用仅警告。手工：`sudo mkdir -p /run/user/$(id -u) && sudo chown $(id -u):$(id -u) /run/user/$(id -u) && sudo chmod 700 /run/user/$(id -u)`，再 `inv <ns>.up --skip-build` 恢复栈 |
| 外部 Go-http-client 经 `podman.sock` 调 `POST /libpod/system/prune`（journal 可见，2026-09-16 实证一次），跨项目删除全部 Exited 容器（含 jupyter-podman 单容器）与悬空镜像；有 tag 镜像/命名卷无损 | 共享该 socket 的 UI/自动化（容器管理面板等）执行了 system prune（all=false 只删 stopped 容器+dangling 镜像）；本项目编排器从不下发 prune | 恢复栈一条命令：`inv <ns>.up --skip-build`；jupyter-podman 单容器走 jpman 单容器路径启动。预防：不要在共享该发行版 socket 的 UI 里点"清理/Purge"，或操作前先确认栈处于 Up |
| 裸 compose 后 workspace 下出现 npu_tvm 等空目录 | podman-compose 1.6 相对 source+create_host_path 预创建副产物 | 不影响真挂载；down 后 `rmdir`；用 invoke 绝对路径注入不产生 |
| 裸 `podman-compose up -d` exit 0 但 Jupyter 根目录出现 `.git`/`apps`/`docs`，容器里 `/workspace` 竟是整个仓库根 | overlay 目录私有 `.env` 的 `<NS>_WORKSPACE` 误按 client 基准写层级：overlay 文件比 client 深两级，`../../../../..`（五级）相对 overlay 子目录正好解析到仓库根；模板正确值是 `../../workspace`（上两级=client/workspace） | 把 `.env` 改回 `XMNN_WORKSPACE=../../workspace`（quant/monetize 同理）→ `down && up -d`；仓库根已被入口 chmod 777 的副作用要 `chmod 755 <仓库根>` 还原。`.env` 被 gitignore 属本地私有，排查时务必实读该文件而非只看 compose.yaml |
| up 后 55~60 秒 Jupyter 端口 curl 返回 000，容器却是 Up | entrypoint Step 4 容器内 podman 初始化偶发等 ~70 秒（平时约 30s），浸泡不足误判 | 等满 70~90s 再判活；日志走到 `Step 5/7` 后 supervisord 约 5s 内起 Jupyter（非故障） |
| 容器内 podman/podman-compose 报 newuidmap EPERM | 嵌套 rootless 结构性死路 | 不在本 Skill 处理，转 jpman-podman-ops §9.1（B-scheme） |
| PowerShell 内联 wsl bash 命令报 `syntax error near (` | `$()`/`$VAR` 被 PowerShell 插值展开 | 把 bash 逻辑写成脚本文件，`wsl -d <d> -- bash /mnt/d/.../x.sh` |

## 10. Gotchas

1. **重建镜像 ID 不变 ≠ 构建失败**：层缓存全命中即与原镜像同 digest；
   先看构建日志 `Using cache` 与任务退出码，再决定是否需要 `--no-cache`。
2. **"容器活着"与"发行版活着"是两层**：保活锚保的是发行版；
   `vmIdleTimeout=-1` 只保 VM 不保发行版。
3. **镜像存储按发行版隔离**：load 进 jupyter 发行版的镜像，machine 里看不到。
4. **宿主文件属主映射**：容器 root→宿主 1001；容器 devuser(1000) 新建文件
   在 drvfs 显示 100999:100999（uid+subuid 100000），属正常映射非污染。
5. **守护/验证用不同身份**：supervisord 以 devuser 跑 Jupyter；权限探针
   必须带 `podman exec -u devuser`，root 探针通过不能代表 Jupyter 可写。
6. **编排层修复不重建镜像也会生效**：invoke 代码 editable 安装，up 时
   `_prepare_env()` 即时执行；但**必须 down→up 新建容器**才会重新走入口。
7. **观察长构建**：后台任务 + 读 output.log 尾部；勿用会缓冲的 cmdlet。
8. **overlay `.env` 的相对路径基准比 client 深两级**：裸 compose 的相对
   路径相对 `overlays/<stack>/compose.yaml`，而 invoke 相对 client cwd。
   `<NS>_WORKSPACE` 正确裸值是 `../../workspace`（client/workspace），
   误抄 client `.env` 的 `../../..`（仓库根）会让 `/workspace` 挂成整个
   仓库根——exit 0、端口正常，工作区隔离却已失效（Jupyter 里能看到 `.git`）。
   排查裸 compose 异常必须实读 overlay 目录的**私有 `.env`**（被 gitignore，
   与 `.env.example` 可能已漂移），不能只看 compose.yaml 默认值。
9. **`podman ps` 的 Up 与端口可达都不能证明容器可 exec**：发行版回收循环后
   可留下"libpod 记 running + 孤儿 conmon/rootlessport 续命端口"的假活状态，
   HTTP 302 也可能是孤儿转发制造的假象。栈内 exec 长任务（build-tvm/wheel）
   启动前先 `podman exec <name> echo ok` 做活体探针；失败按 §9"假 Up"行
   定向清理（down→kill 孤儿 rootlessport/conmon→up），可免 `wsl --shutdown`、
   不影响同发行版其他栈（2026-09-15 wheel 构建前实证）。
10. **同一栈固定单一控制平面（Windows 裸 compose vs invoke 桥接不可混用）**：
    裸 Windows `podman-compose` 给容器打 `D:\...` 路径标签，invoke（WSL 桥接/
    WSL 内）固定 `--file /mnt/d/...`；config-hash 按标签原文计算，交替执行必
    强制 recreate，在 podman-compose 1.6 pod 模式下高概率留下孤儿 rootlessport
    致 bind 2223/8890 失败（2026-09-15 三次确定性复现，优雅 down 也不免疫）。
    同平面重复执行幂等。已用 invoke 管栈就继续用 `invoke <ns>.up/down`；若
    必须在裸 compose 翻车后切回，直接 `invoke <ns>.up --skip-build`——
    up_preflight 三道（残留 down / 跨平面优雅 down / 孤儿定点 kill）自动收敛，
    不要手工先删容器。
11. **桥接/自动化必须走非登录 shell（`bash -c`/`bash script.sh`），禁止 `bash -lc`**
    （2026-09-16 实证，client W-I11）：podman-machine-default 是 Fedora-WSL
    系镜像，登录会话的 `/etc/profile.d/enterns.sh` 在嵌套 systemd 存活时无参
    执行 enterns → `sudo nsenter ... su -l $USER`，把命令劫持成交互 shell
    （`inv xmnn.build` “进入 shell”的真相）；同目录 docker-host.sh 还会在
    podman 未就绪时污染 `DOCKER_HOST=unix://`。client 桥接器已固定非登录
    （PATH 显式前置 + LANG 兜底）；手工诊断/脚本一律
    `wsl -d <d> -- bash /mnt/d/.../*.sh`，不要用裸 `wsl -d <d>` 登录会话承载
    自动化。同次实证的姊妹坑：VM 回收后 `/run/user/<uid>`（tmpfs）不重建，
    podman 全命令 exit 125——invoke 已在 Linux 放行路径自动 `sudo -n` 重建
    （ensure_wsl_rootless_runtime，W-I12）；手工诊断若撞上
    `RunRoot not writable`，先建目录再继续。

## 11. Changelog

- **v1.0.4** (2026-09-16): 错误表新增三行——① `inv <ns>.build` 等桥接任务
  误入交互 shell（登录 shell 被 Fedora-WSL enterns `su -l` 劫持，client
  W-I11）；② VM 回收后 `/run/user/<uid>` tmpfs 不重建致 podman exit 125
  （W-I12，编排层 ensure_wsl_rootless_runtime 已自动 sudo -n 重建）；
  ③ 外部客户端经 podman.sock `system/prune` 跨项目误删 Exited 容器的识别与
  恢复。Gotchas 新增第 11 条「桥接必须非登录 shell」。实证 session
  sc-20260916-xmnn-build-shell：build 90s 正常完成、模拟回收自愈、up/smoke
  全过；client 侧配套 test_wsl_bridge 9 例（84 passed）。

- **v1.0.3** (2026-09-15): 端口占用行三因扩四因，新增**确定性首因「跨控制平面
  标签分歧」**（Windows 裸 compose `D:\` vs invoke `--file /mnt/d/`，config-hash
  按原文算 → 强制 recreate → infra 强拆 → rootlessport 被 `/init` 收养为孤儿；
  三次复现、优雅 down 同样触发）；首选修复改为 `invoke <ns>.up` 的 up_preflight
  三道自动自愈（编排层 overlay_core，三栈同族）；Gotchas 新增第 10 条「单一
  控制平面纪律」。实证序列：破损现场自愈 / 裸 compose 干净起栈 / 同平面幂等 /
  桥接跨平面自愈 / invoke 幂等，jupyter 栈全程零影响（session
    sc-20260915-xmnn-2223-bind；client 排障 W-I10）。
- **v1.0.2** (2026-09-15): 错误表新增"假 Up"（ps/HTTP 302 正常但 exec 报
  `crun ... status: No such file`；libpod 记 running、容器 PID 已死、孤儿
  conmon/rootlessport 续命）及免 `wsl --shutdown` 的五步定向清理；端口占用行
  从两因扩为三因（新增 `ss -ltnp` 可见显式 rootlessport 持有者的可定向 kill
  变体，置于 wslrelay 粘滞裁决之前）；步骤 1 修正 compose 工具安装序
  （Fedora 43 镜像无 pip → ensurepip；jpman-common 须先于 client 从
  `../shared` editable 安装，否则 No matching distribution）；Gotchas 新增
  第 9 条（exec 是唯一活体判据）。实证于 xmnn wheel 构建任务。
- **v1.0.1** (2026-09-14): 错误表新增"裸 up exit 0 但 /workspace 挂成仓库根"
  （overlay `.env` 的 `<NS>_WORKSPACE` 相对基准比 client 深两级，误填五级
  路径致工作区隔离失效，附仓库根 chmod 777 副作用还原）与"浸泡不足误判
  Jupyter 000"（Step4 偶发 ~70s）两行；Gotchas 新增第 8 条。
- **v1.0.0** (2026-09-14): 初版。源自 xmnn-dev 栈三次实战（首次启动 →
  checkpoint EACCES 修复 → 镜像/栈重建）：固化发行版选择（jupyter 发行版
  优先 + 保活锚）、四维修复预检、build/up/浸泡/smoke SOP、tuna 普通重建
  裁决、8+ 本机实证陷阱（发行版回收 exit 0 假象、空 CONTAINER_HOST 致
  CLI exit 125、nftables、XDG 覆盖、checkpoint 755、路径错锚三级、
  PowerShell 插值、OCI/Nuitka 日志噪音）；与 jpman-podman-ops、
  client-overlay-scaffold 建立边界路由。
