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

