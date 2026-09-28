# jupyter-podman-client 变更日志（原子提交汇总）

> 本文件只记录消费端特有改动；SpecWeave 工作区根级、apps/containers 组级、构建端（jupyter-podman-rootless）的改动
> 不在本文件范围内。按七概念方法论每次 C（原子提交）阶段完成后追加一条；每条必须：
> ①可追溯（对应根工作区 git commit hash）②关联七概念场景（里程碑复盘/问题解决/重构优化/知识沉淀/创新突破）③说明验收点

> **归档索引**（2026-09-23 原子化，条目内容零改写）：本文件仅保留 [Unreleased] 与最新条目，
> 历史条目按日期段拆至 [archive/](archive/)；新增变更仍写入本文件 `## [Unreleased]` 顶部。
>
> | 归档文件 | 覆盖日期 | 条目 | 主题 |
> |---|---|---|---|
> | [archive/2026-09-21.md](archive/2026-09-21.md) | 2026-09-21 | 6 | int4 报告 / C31 源码树只读 / Task6 迁出 / C27-C32 |
> | [archive/2026-09-20-p1.md](archive/2026-09-20-p1.md) | 2026-09-20 前半 | 9 | GPU 透传 / C25 nvcc / C29-C30 SSH / host keys / W-I19 |
> | [archive/2026-09-20-p2.md](archive/2026-09-20-p2.md) | 2026-09-20 后半 | 9 | up 生命周期 C21-C24 / 离线形态 C20 / W-I17 / C18-C19 |
> | [archive/2026-09-17-18.md](archive/2026-09-17-18.md) | 2026-09-17~18 | 13 | 离线 save-load / xmnnctl / 终端噪声 / C15-C17 |
> | [archive/2026-09-15-16.md](archive/2026-09-15-16.md) | 2026-09-15~16 | 14 | OKF 重构 / README 原子化 / xmnnrt 栈 / torch 2.14 |
> | [archive/2026-09-07-13.md](archive/2026-09-07-13.md) | 2026-09-07~13 | 18 | client 基座 / SDK / save·load / run / 透传 / quant 迁移 |

## [Unreleased]

### 2026-09-28 · `fix(client):` `--gui` 支持动态会话目录与 SSH X11/TCP 透传（resolve_gui fail-fast 误伤 ssh -X 会话，C33 增补；排障 C-I11）

**关联七概念场景**：场景2「问题解决」（I→F→V→C）——物理 Linux 本机（UID=1006，`ssh -X` 远程会话）执行 `invoke native.up --passthrough --gpu --gui --offline` 连续 Exit(1)，trae-server 日志片段表现为 "ffline"，真实命令在 `resolve_gui()` 门禁失败。

**I 事实**：①GUI 候选目录硬编码 `/run/user/1000`，而本机会话在 `/run/user/1006`（同族 D-Bus 探测 2026-09-24 已改 `id -u` 动态、GUI 漏同步）；②门禁只认 Wayland/X11 unix 两通道，`ssh -X` 会话无 `.X11-unix` socket，sshd 只在宿主 loopback 开 `127.0.0.1:60<n>`（本机 `DISPLAY=localhost:11.0`）；③实证 **TCP 可连 ≠ X 可用**：6010 仍 LISTEN 但 X 握手被 RST（僵尸转发 proxy），6011 connection refused——故严禁自动扫描会话、严格按当前 `$DISPLAY` 探测；④`~/.Xauthority` 条目按显示号存放（family u16 + 4 段 u16 长度前缀串，本机 display 10–41），容器经 loopback 接入时宿主条目的地址族不匹配，必须 FamilyWild 单条授权；⑤invoke 2.2.0 `auto_shortflags=False`，"ffline" 确为 `--offline` 片段而非缩写歧义。

**F 定论**：GUI 扩为三形态——wayland / x11 unix（bridge 可用，bind mount）+ **x11-tcp**（仅 host 网络，env+cookie 文件 bind）。x11 与 x11-tcp 互斥（同一显示服务两传输），均可与 wayland 并存。安全约束：只接受 loopback 目标（localhost/127.0.0.1/::1，显示号 0–99）；只下发该显示号的 FamilyWild(0) 单条 cookie（不转发完整 .Xauthority），cookie 禁止入日志。

**V 对抗（12 条意见落地要点）**：探针全部落 daemon 宿主（禁本机 Path.exists，同 C19）；cookie 文件 0644（rootless 容器内子 uid 读不了 0600 单文件 bind，会话目录 0700 兜底）；裸 compose 缺令牌时 cookie 源为 sentinel `/tmp/.gui-xauthority-missing`（挂载即 exit 125，不静默放行）；bridge 命中转发端口不静默换形态、转 fail-fast 组合旗标指引；失效会话诊断**改用 X11 协议握手复核** `ss -lnt` 的 60xx 候选（发 44 字节 Connection 验响应首字节 l/B）——真机 6060 实为 HTTP 服务、6010 为 accept 后 RST 的僵尸转发，裸端口列举会双双误报；`parse_x11_tcp_display` 用 rpartition 正确解析 bracketed IPv6 `[::1]:2`；fail-fast 保留 WSLg/物理机/去旗标通用指引，cookie 失败不污染已命中形态。

**C 落地**：①内核 `overlay_core.py`：新增 `_runtime_session_gui_env`（printf 探针取会话三元组）、`parse_x11_tcp_display`/`parse_x11_unix_display`、`_runtime_tcp_open`（bash /dev/tcp 2s 超时）、`_runtime_active_x11_displays`、`extract_xauth_entry`/`_xauth_take16`/`encode_familywild_xauth`（纯 struct、零第三方）、`_prepare_x11_tcp_authority`；`resolve_gui(..., *, host_network=False)` 动态候选 + 三形态 + 证据化诊断；`compose_files/compose_argv/run_compose/up_preflight` 全链路参数透传 `x11-tcp`，`up_stack`/`smoke_stack` 以 `host_network=passthrough` 调用，横幅区分「仅 host 形态可达」。②部署面新增 `overlays/native-dev/compose.passthrough.gui.x11.tcp.yaml`（cookie read_only bind + `DISPLAY`/`XAUTHORITY`，文件头安全警示）；`native.py` bridge_env_keys 增 `GUI_X11_TCP_DISPLAY`/`GUI_XAUTHORITY_FILE`（声明模块守住 AC-5 ≤160 行护栏，最终 160 行）；`--gui` help 补 ssh -X 说明。③测试：FakeRunner 增会话探针/TCP 探活打桩，新增动态 UID、x11-tcp 成功（cookie 抽取+文件集+env 回写）、bridge 拦截、失效会话、缺 cookie、unix 抑制 TCP、up 横幅、smoke 同源及 `parse_*`/xauth 纯函数共 21 个用例，compose 渲染增 tcp 层与 sentinel 2 例。④文档：C33（native-overlay §11.7）增补第三形态全部规则，AGENTS.md C33 行同步；07 组合 D 维度表/探测序/SSH 小节、09 映射表、04 速查表 C-I11、透传主层文件头、native-dev `.env.example` 闭环。

**V 验收**：`pytest -q` **296 passed / 1 skipped**（全量，含 24 新增/更新）。真机三分支（UID=1006）：①原命令复跑——精确诊断「6011 无响应/会话可能失效」，X11 握手复核后**无任何确认存活的转发**（6010 accept 即 RST、6060 回 `HTTP/1.1` 均被排除），Exit 1 先于任何 down/up；②`GUI_X11_TCP_DISPLAY=127.0.0.1:10` 不带 `--passthrough`——bridge 拦截诊断并给 `invoke native.up --passthrough --gui` 指引；③直接调 `resolve_gui(host_network=True)` 对真实 `~/.Xauthority`——返回 `('x11-tcp',)`、回写 `GUI_DISPLAY=127.0.0.1:10`、生成 `/run/user/1006/gui-xauthority-10`（family=0 FamilyWild、仅含显示 10 单条、0644），验证后已清理。

提交 `fix(client)` = 本提交（CHANGELOG 留痕与代码/测试/文档变更同笔落盘）。

### 2026-09-24 · `fix(client):` 三叠加栈补齐 B-scheme 宿主 podman socket 直通（容器内 PodmanClient FileNotFoundError，C34）

**关联七概念场景**：场景2「问题解决」（I→F→V→C）——native-dev 容器 Jupyter（Python 3.14 kernel / devuser）执行 `PodmanClient.from_env().containers.list()` 报 `FileNotFoundError: [Errno 2]`（`podman/api/uds.py` UDS connect）；用户记忆中该问题已修，实则修过的范围未覆盖叠加栈。

**I 事实（非回归，是覆盖盲区）**：2026-09-07/12 的 B-scheme 修复（C-I2/C-I5）只接入 **jupyter 主栈**（`jupyter-podman-rootless/compose.yaml`）与**根 invoke run 路径**（`client_core.py`）；三个 extends `_shared/base-rootless.yaml` 的叠加栈（native-dev / onnx-quantized / agent-monetize-dev）compose **从未挂载宿主 socket**（`git log -S podman.sock -- overlays/` 零命中）。基底 entrypoint 无 `HOST_PODMAN_SOCK` 时静默回退容器内自建 rootless daemon（DinP），而 rootless 套 rootless 必被 `newuidmap: write to uid_map failed: Operation not permitted` 拒绝，socket 30s 内不生成，entrypoint 却仍导出指向死路径的 `CONTAINER_HOST`，故障迟到 Notebook 运行时才以 FileNotFoundError 暴露。

**F 定论**：受管栈信任模型与 jupyter 主栈一致（同机可信、devuser 即宿主用户），三栈默认直通宿主 rootless socket、不加 opt-out 开关；缺源必须 fail-fast，禁止 DinP 静默回退与 `os.makedirs` 误建挂载源。

**E/C 落地**：① 内核新增 `resolve_host_podman_socket()`（`overlay_core.py`），在 `up_stack()` 中**先于 build/一切门禁/任何 down** 调共享库唯一事实源 `jpman_common.connection.ensure_host_podman_socket()`（Linux 免提权 `systemctl --user start podman.socket` 自愈；非 Linux/容器内/非 podman 放行），失败打印 C-I5 三步中文指引并 `Exit(1)`；令牌优先级 shell export > 根 .env > `podman_sock_path()`（UID 经 `PODMAN_RUNTIME_UID`/`$XDG_RUNTIME_DIR`/`id -u` 推导，禁硬编码），回写 `os.environ` 供 compose source/target/env 三处插值。② 三栈 compose 各加同路径长语法 bind（`source == target == ${HOST_PODMAN_SOCK:-/run/user/1000/...}`，`create_host_path: false`）+ 同名 env，缺省 1000 仅服务裸 compose 的 WSL2 惯例 UID。③ 三栈 `.env.example` 增令牌文档（UID/systemctl/linger/裸 compose 硬失败保护说明）。④ 防再漏接的准入硬约束写入 native-overlay §11.8（C34）：凡 extends rootless-base 的新栈必须显式接 B-scheme 或书面声明禁用，禁依赖 DinP 回退；07 文档排障表增 C-I5 行、05 参数表补两键。独立评审另加固纯空白令牌逐级回落（strip 先于 or，防 env 空串与挂载缺省静默分叉）。entrypoint.sh 与镜像零改动（B-scheme 分支早已完备）。

**V 验收**：`pytest tests -q` **265 passed / 1 skipped**（新增 34 例：预检令牌优先级三态、纯空白令牌逐级回落、C-I5 fail-fast 且 runner 零子进程、自愈提示、compose 子进程环境带令牌；三栈渲染断言 socket bind/source==target/`create_host_path: false`/env 同步与 1006 覆盖、透传及全组合形态不丢挂载）。另两栈 `podman-compose -f compose.yaml config`（py314 / podman-compose 1.6.0）渲染对等：默认 1000 同路径 bind + env，`HOST_PODMAN_SOCK=/run/user/1006/...` 覆盖时 source/target/env 三处同步。真机 `native.down && native.up --passthrough --gpu --usb --offline`（约 32s 就绪）：日志含 `[B-scheme] Host podman socket linked`、`[OK] devuser can read/write host podman socket`，全日志 `newuidmap`/DinP 回退关键词计数 0；`podman inspect` 实证 `/run/user/1006/podman/podman.sock` 同路径挂载与 env 注入；容器内 devuser `python -c "from podman import PodmanClient; print(len(PodmanClient.from_env().containers.list(all=True)))"` 返回 `1`（native-dev 自身），原截图 FileNotFoundError 路径走通（浏览器重跑截图 cell 留用户复核，代码路径与该实测同构）。

提交 `fix(client)` = 本提交（CHANGELOG 留痕与代码/测试/文档变更同笔落盘）。

### 2026-09-24 · `fix:` up 就绪探测超时归因逐地址列出，::1 永久拒绝不再独占文案冒充 IPv6 故障

**关联七概念场景**：场景2「问题解决」（I→F→V→C）——承接同日 D-Bus 修复后真机 `native.up --passthrough` 首启，横幅误报「Jupyter 未在 120s 内应答（ConnectionRefusedError @ ::1:8888）」，而服务实际稍后即在 `127.0.0.1:8888` 正常 302。

**I 事实**：`utils.wait_http_ready` 每轮已按 `127.0.0.1` → `::1` 顺序探测、v4 成功即返回（**无假阴性**），但用单变量 `last` 记录末次异常，每轮都被最后探测的 `::1` 覆盖；Jupyter 默认只绑 `0.0.0.0`（容器日志 `running at http://0.0.0.0:8888`，宿主 `ss -lnt` 仅 `0.0.0.0:8888` 无 `:::8888`），**`::1` 拒绝是永久预期行为**——于是任何超时文案都只剩 `::1`，把 IPv4 侧真实信号（尚未 listen 的 ConnectionRefused、rootlessport 零字节窗的 ConnectionReset）淹没，被误读为「IPv6 故障」。时间线实证：容器 10:07:37 启动、Jupyter 10:09:37 才 listen，首启约 120s 紧贴 `UP_READY_TIMEOUT_S` 边界。

**F 定论**：探测策略无需改（双栈都试、v4 优先），缺陷只在错误归因——两地址末次错误须各自独立保留，超时文案逐地址列出且 IPv4 在前（权威信号），并显式注明「::1 拒绝在服务仅绑 IPv4 时属预期，以 127.0.0.1 状态为准」。

**E/C 落地**：`wait_http_ready` 以 `last_err` dict 替换单变量，超时返回 `127.0.0.1 <异常>；::1 <异常>（Ns 无 HTTP 应答；…）`；成功路径与「超时不抛异常、不判失败」契约不变。`test_up_readiness.py` 新增 2 例：双地址归因顺序（v4 在 v6 前、含「仅绑 IPv4」说明）、v4 零字节窗 ConnectionResetError 与 v6 ConnectionRefusedError 两类错误同时保留。

**V 验收**：`pytest tests -q` **231 passed / 1 skipped**；函数级实证运行中服务返回 `(True, '127.0.0.1 → HTTP 302')`、封闭端口返回双地址新文案；端到端 `native.down && native.up --passthrough --gpu --usb --offline` 约 100s 正确打印「Jupyter 已就绪（127.0.0.1 → HTTP 302）」无误报。遗留边界（本次未改）：cu130 镜像首启约 120s 紧贴超时上限，偶发超时时可单独调宽该栈超时。

提交 `fix(client)` = 本提交（CHANGELOG 留痕与代码/测试变更同笔落盘）。

### 2026-09-24 · `fix:` --passthrough D-Bus 会话总线缺省路径改运行期动态探测（UID 不再硬编码 1000）

**关联七概念场景**：场景2「问题解决」（I→F→V→C）——`invoke native.up --passthrough --gpu --usb --offline` 在物理 Linux 本机门禁 Exit(1)，报「/run/user/1000/bus 不是 socket」。

**I 事实**：`overlay_core.resolve_passthrough` 把会话总线缺省路径硬编码为 `/run/user/1000/bus`（仅 `DBUS_SESSION_BUS_PATH` 显式令牌可覆盖）；本机用户 `ai` 的 **UID=1006**，`/run/user/1000` 整个不存在，真实会话总线在 `/run/user/1006/bus`（`XDG_RUNTIME_DIR=/run/user/1006`、`DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1006/bus`、`systemctl --user` active，物理 Linux 非 WSL），门禁 `test -S` 必败。同条命令的 TORCH_FLAVOR 形态告警是另一独立非阻断项（本机 `.env` 未声明=空、镜像 LABEL 实为 cu130），按用户确认在本机 `.env`（gitignore，不入库）写 `TORCH_FLAVOR=cu130` 收口，不进本次提交。

**F 定论**：UID 随宿主而变，缺省路径不得写死。无显式令牌时在 **podman 真正运行的环境**（兼容 Windows→WSL 桥接，故经 `run_cmd` 而非读 Python 侧 `os.environ`）按标准优先级探测：`$DBUS_SESSION_BUS_ADDRESS`(unix:path=，剥除 `,guid=` 尾段) → `$XDG_RUNTIME_DIR/bus` → `/run/user/$(id -u)/bus`；显式令牌最高优先、只做 `test -S` 校验的语义不变。

**E/C 落地**：内核新增 `_runtime_probe_session_bus()`（单条 POSIX shell 三候选探测，命中输出路径，全失空串）；`resolve_passthrough` 拆「显式令牌无效」与「自动探测无果」两类中文 fail-fast 文案（后者列出探测顺序并给物理 Linux `loginctl`/`systemctl --user` 核对步骤与 WSL2 系统总线逃生路径）；`compose.passthrough.yaml` 前置检查注释、`docs/07-passthrough-and-combos.md` 排障行、`.env.example` 注释同步（注明 UID 未必是 1000、留空自动探测）。`test_overlay_core.py` FakeRunner 增加会话总线探测模拟，新增 5 例（UID≠1000 自动命中、显式令牌跳过探测、显式无效路径文案、探测全失 fail-fast、helper 空失败）。

**V 验收**：`pytest tests -q` **229 passed / 1 skipped**；真机重跑原命令 EXIT 0，横幅 `透传 host 网络 + D-Bus（/run/user/1006/bus；…passthrough）`、torch 形态告警消失；`podman inspect` 实证 `net=host` + 挂载 `/run/user/1006/bus -> /tmp/runtime-user/bus`，容器内 `test -S` 通过，`/dev/bus/usb` 001–008 可见，`nvidia-smi -L` 见 RTX 3090 + RTX 2080 Ti，Jupyter 302 可达。

提交 `fix(client)` = 本提交（CHANGELOG 留痕与代码/文档变更同笔落盘）。

### 2026-09-23 · `feat:` native 栈新增第五运行期维度 `up --gui`（WSLg Wayland/X11 双通道显示透传，C33）

**关联七概念场景**：场景5「创新突破」（F→V→I→C）——07 文档「GUI：现状与可用路径」原记载本栈无 GUI 叠加层、X11/Wayland 只能裸 compose 自行挂载；本次把文档承诺的「仿 USB 层扩展」落地为一等 opt-in 能力。

**F 公理**：GUI 转发本质 = daemon 宿主 AF_UNIX 显示 socket bind + 客户端寻址 env，纯运行期、零镜像变更；WSLg 在 podman-machine-default 内固定提供 Wayland（`/mnt/wslg/runtime-dir/wayland-0`）与 X11（`/mnt/wslg/.X11-unix/X0`）两通道（真机 `wsl -d podman-machine-default` 实证均为 0777 socket，非登录 shell 的 DISPLAY/XDG_RUNTIME_DIR 全空）；静态 compose 无法按缺源删 bind（缺源 exit 125），故文件集必须由探测结果决定（同 `gpu_override_file` 形态选择先例），不能一份文件写死双 bind。

**V 对抗（采纳 5 项）**：① X11 源首选 `/mnt/wslg/.X11-unix` 真实路径，规避他机 `/tmp/.X11-unix` 符号链接；② fail-fast 指引三分支（WSLg/Win10、物理 Linux、去开关）+ 物理机 `xhost local:root`；③ 文档给免依赖 Hello-World 验证（AF_UNIX connect 三行）；④ socket 挂载安全警示（截屏/输入注入面，仅可信镜像）；⑤ 任一通道命中即放行，纯 Wayland/纯 X11 宿主只挂一层。

**I/C 落地**：新增 `compose.passthrough.gui.yaml`（Wayland）与 `compose.passthrough.gui.x11.yaml`（X11 目录+DISPLAY）两姊妹层；`StackSpec.gui_overlay`（仅 native 置真）+ 内核 `resolve_gui()`（daemon 宿主 `test -S` 探测序：显式 env → WSLg → /run/user|/tmp 回退，回写 GUI_WAYLAND_SOCKET/HOST_WAYLAND_DISPLAY/GUI_X11_SOCKETDIR/GUI_DISPLAY）；`compose_files`/argv/preflight/up/smoke 全链贯通 `gui`/`gui_forms`（文件序 base→GPU→透传→GUI(wayland→x11)→USB）；工厂 up/smoke 形参并集加 `gui`；bridge_env_keys 转发用户可设四键。GUI **bridge 形态即可用**（不切 tag、不改网络），与 `--passthrough/--gpu/--usb/--offline` 全正交。

**文档/契约**：07 新增「组合 D：GUI」（矩阵 +11 行、排障 +3 行，全家桶顺延组合 E）、05 参数表 +4 键、`.env.example` GUI 段、client docs/09 栈等价表（标明是根 `--wayland` 超集）、native-overlay §11.7（C33 完整契约）、client AGENTS C18 扩五路 + C33 P0 行、invoke-tasks C18 同步。

**V 验收**：`pytest tests -q` **227 passed / 10 skipped**（新增 12 用例：resolve_gui 五态、文件序/形态不变量、up argv+横幅、门禁先于 down、smoke 同源、merge 渲染四层；三份黄金清单同步）；CLI `invoke native.up --help` 含 `--gui`。**真机 WSLg E2E（podman-machine-default）**：零配置 `invoke native.up --gui --skip-build` 自动加载两 GUI 层（argv 实证文件序正确），bridge 形态/`:latest` tag/8890 端口逐字不变；容器内 `WAYLAND_DISPLAY=wayland-0`/`DISPLAY=:0`/`XDG_RUNTIME_DIR=/tmp/runtime-user` 齐备，两 socket 可见，Wayland AF_UNIX connect 成功，**X11 真实协议握手成功**（12 字节 setup，status=1，XWayland 免认证应答——超越 socket 可达、证明 X server 真应答）；`native.smoke --gui` 同源 exec 通过。验收后栈恢复原 `--passthrough --gpu --usb` 形态。

提交 `feat(client)` = 本提交（CHANGELOG 留痕与代码/文档变更同笔落盘）。

### 2026-09-23 · `docs:` CHANGELOG 原子化拆分为 archive/ 六段（251296 字节 → 6.2KB 索引页）

**关联七概念场景**：场景3「重构优化」（I→F→A→C）——主文件累积至 2245 行 / 251296 字节 / 71 条目，超出 64KB 可读性阈值，新增条目被历史噪声淹没。

**I 事实**：71 条目跨 14 个日期（2026-09-07~09-23），其中 09-20 单日 18 条约 89KB 为绝对主体；引用面全仓扫描确认 6 处整文件链接不受影响；1 处行锚引用与 2 处目录树需随拆分同步；归档条目携带的相对链接（rules/、docs/、src/、tests/、overlays/ 等）在 archive/ 子目录下整体失效，由 link_fixer 自动校正 ../ 层级。

**F 定论**：变更日志是 append-only 时序结构，访问频率呈「最新热、历史冷」分布——主文件只应承载导航与最新窗口，历史按日期段归档；「条目内容零改写」为原子化保全边界。

**V 定稿**：7 文件方案——主文件 6.2KB（头部 + 归档索引表 + [Unreleased] 两条最新）+ 6 个 archive 文件（22~52KB，均 <64KB）；命名沿用仓库 date-named 归档惯例；参照 2026-09-15「README.md 原子化为 docs/」先例；AGENTS.md 与 .agents/README.md 目录树补 archive/ 子项；spec review.md:225 的 file:/// 绝对路径改相对路径（锚点 L31-L39 → L43-L51 按新行界校正）。

**V 验收**：守恒校验 PASS（71 条目 + 11 尾部行逐字一致，含顺序）；check-atomization-duplication 无残留；归档断链经 link_fixer 校正（17-18 10 处 / 20-p1 38 处 / 20-p2 24 处；21 与 07-13 零断链；另手工补 20-p2 一处裸文件名链接——link_fixer depth 校正对零 `../` 前缀 URL 存在盲区，遗留为工具改进项）；check-links 通过（13 条目录链接风格警告，属仓库既有基线形态）。

提交 `docs(client)` = 本提交（CHANGELOG 留痕与文档变更同笔落盘）。

### 2026-09-23 · `fix:` 同步 usbipd 5.x 语法与火绒场景指引（4 处散点）

**关联七概念场景**：场景2「问题解决」（I→F→V→C）——执行 `usbipd attach` 转发摄像头（busid 2-8）时暴露仓库 4 处 usbipd 命令用法停留在旧版语法，用户照做即报错。

**I 事实**：usbipd-win 5.x 起 `attach` 的 `--distribution` 参数已移除，改为 `--wsl <[DISTRIBUTION]>`（可选值）；旧语法 `attach --wsl --distribution podman-machine-default` 实测报 `Unrecognized command or argument 'podman-machine-default'`。散点 4 处：内核门禁文案（`overlay_core.resolve_usb_device`）、守卫测试断言、`docs/07` 组合 C powershell 块、`compose.passthrough.usb.yaml` 注释。附带两个环境事实：本机 usbipd 服务默认未启动（Manual，`sc.exe start usbipd` 可恢复；依赖内核驱动 VBoxUsbMon 由 usbipd-win 安装包自带、随服务自动加载，无需装 VirtualBox）；火绒安全（Huorong）的 hrdevmon 设备监控过滤器挂在 USB 设备类，usbipd 不识别 → list warning + bind 需 `--force`（非致命提示）。

**F 定论**：外围工具主版本升级后仓库命令示例未同步，属指引失真；bind 需管理员、attach 不需管理员的权限边界与火绒 `--force` 场景此前无记载。

**V 定稿**：4 处统一为 5.x 语法 `usbipd attach --wsl podman-machine-default --busid <BUSID>`；bind 标注「需管理员；装有火绒时加 --force」；`docs/07` 组合 C 前置补服务启动说明，排障表新增「service not running + hrdevmon」双根因行（服务 `sc.exe start usbipd` / 火绒过滤器 `bind --force`，两因独立）。

**E/C 落地**：`overlay_core.py` `resolve_usb_device` 门禁文案 5.x 化；`test_overlay_core.py` 断言同步（`assert "usbipd attach --wsl podman-machine-default" in out`）；`docs/07-passthrough-and-combos.md` 组合 C 前置 + powershell 块 + 排障行；`compose.passthrough.usb.yaml` 注释补 usbipd 5.3 实测标注。

**V 验收**：`pytest tests -q` **215 passed / 10 skipped**（断言同步后零回归）；`check-links --path overlays/native-dev/docs` **20/20 通过**；全仓 `--distribution` 扫描确认 usbipd 旧语法零残留（剩余命中均为 wsl bundle 的 `wsl --distribution`，无关）；真机 `usbipd attach --wsl podman-machine-default --busid 2-8` 成功（摄像头 Attached，WSL `/dev/bus/usb/001` 可见），`invoke native.up --passthrough --gpu --usb` EXITCODE=0 全家桶跑通。

提交 `fix(client)` = 本提交（CHANGELOG 留痕与代码/文档变更同笔落盘）。

### 2026-09-23 · `fix:` 透传门禁识别本栈 host 容器占用，重复 up 幂等放行

**关联七概念场景**：场景2「问题解决」（I→F→V→C）——`invoke native.up --passthrough --gpu --usb` 在 trae-preview 控制台构建后报「端口已被占用：8888, 2223」exit 1，实为误报。

**I 事实**：host 网络下容器内 Jupyter(8888)/SSH(`HOST_NET_SSHD_PORT` 默认 2223) 直接绑宿主，`ss -lnt` 看到的占用必然含本栈自身；真机实证 8888 行**无持有者 pid**（容器内 jupyter 以 root 运行，普通用户 ss 不可见），2223 持有者为 sshd——PID 树归属判定不可靠；`podman ps` 仅 native-dev passthrough 容器 Up，占用者即本栈。

**F 定论**：门禁语义缺口——把幂等场景（栈自身持有端口）误判成外部冲突 fail-fast。

**V 定稿**：占用者身份判定弃用 ss PID 归属，改用 `podman inspect --format '{{.State.Running}} {{.HostConfig.NetworkMode}}'` 双段判据（`true host` 才放行；容器不在跑/非 host 形态 → fail-fast 语义不变）。

**E/C 落地**：`overlay_core.py` 新增 `_own_host_container_running`；`resolve_passthrough` busy 分支分流（own host → ℹ 提示放行，交 podman-compose 幂等处理：文件集无变化=no-op、组合旗标变化=自动 recreate；其余保留原五条中文指引 fail-fast）；`docs/07-passthrough-and-combos.md` 排障表补「重复 up 被端口门禁拦」行；`test_overlay_core.py` 增 3 守卫测试（helper 判据矩阵 / own host 放行 / own bridge 仍 fail-fast）。

**V 验收**：`pytest tests -q` **215 passed / 10 skipped**（较修复前 +3，零回归）；`check-links --path overlays/native-dev/docs` 通过；真机复核待用户重跑 `invoke native.up --passthrough --gpu`（WSL2 宿主无 `/dev/bus/usb` 时 `--usb` 门禁按设计 fail-fast，属环境事实非 bug）。

提交 `fix(client)` = `e96eb84f0`。

