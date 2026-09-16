---
id: "summary-jpman-client-wsl-bridge-retro-20260916"
title: "client WSL 透明桥接连环排障双里程碑复盘：2223 端口孤儿自愈、enterns 登录劫持与 tmpfs 运行时目录"
date: "2026-09-16"
type: "summary"
source: "七概念方法论双会话：sc-20260916-xmnn-2223-bind（podman-compose up -d 报 2223 bind + Windows invoke 桥接入口安装）与 sc-20260916-xmnn-build-shell（inv xmnn.build 误入交互 shell + /run/user/1000 丢失 exit 125）"
tags: [specweave, apps, containers, jupyter-podman-client, podman-compose, wsl, rootless, enterns, systemd, tmpfs, invoke, bridge, xmnn, seven-concepts, milestone]
methodology: "seven-concepts: 场景1 里程碑复盘 R→I→E→C；G1（40 条无因果事实）→ G2（4 条四元组洞察）→ G3（非登录命令通道模式）→ G4（原子行动项）"
target_files:
  - "apps/containers/client/src/jpman_client/tasks/utils.py"
  - "apps/containers/client/src/jpman_client/tasks/overlay_core.py"
  - "apps/containers/client/tests/test_wsl_bridge.py"
  - "apps/containers/client/tests/test_overlay_core.py"
  - "apps/containers/client/docs/04-troubleshooting-guide.md"
  - "apps/containers/client/.agents/rules/windows-wsl.md"
  - "apps/containers/client/.agents/CHANGELOG.md"
  - ".agents/skills/compose-overlay-ops/SKILL.md"
related_sessions:
  - "前序：sc-20260915-xmnn-2223-bind（跨控制平面标签分歧首证，compose-overlay-ops v1.0.3 / W-I10）"
  - "前序：sc-20260915-fake-up-auto-heal（假 Up 活体判据与 stale conmon 回收）"
  - "同族报告：summary-jpman-client-podman-sdk-file-not-found-20260908（WSL/rootless 连接排障）"
  - "运维 SOP：.agents/skills/compose-overlay-ops/SKILL.md（v1.0.4）"
---

# client WSL 透明桥接连环排障双里程碑复盘

## 一、任务摘要与上下文

2026-09-16 同一工作日内，xmnn-dev 叠加栈（podman-compose 工作负载，SSH 2223 / Jupyter 8890）在 Windows → WSL `podman-machine-default`（Fedora-WSL 系、无 systemd 于 PID 1）透明桥接通道上连续暴露两个独立故障，经两个七概念会话完成「诊断→修复→真机验证→治理资产沉淀」闭环：

| 里程碑 | session | 用户现象 | 处置结果 |
|--------|---------|---------|---------|
| A：端口占用复发 | sc-20260916-xmnn-2223-bind | 浏览器终端裸跑 `podman-compose up -d` 报 `conmon process killed` + `rootlessport ... 2223: bind: address already in use` | `invoke xmnn.up --skip-build` 的 preflight 三道全部命中自愈；py314 环境补装 Windows invoke 桥接入口并实证同平面幂等 |
| B：build 误入 shell | sc-20260916-xmnn-build-shell | `inv xmnn.build` 未构建，终端进入一个交互 shell（伴随 *nested process namespace... exit twice* 文案） | 定位 enterns 登录劫持 + tmpfs `/run/user/<uid>` 丢失双根因；桥接改非登录 shell + 运行时目录自动重建；84 测试通过、真机全验证 |

验证期间另记录一次**外部** `system/prune` 事件（非本项目代码触发），见洞察 I-3。

---

## 二、方法论链路回顾

| 阶段 | 链路 | 质量门 |
|------|------|--------|
| 里程碑 A | I→F→V→C（问题解决） | 真机四维修复预检 + 双端端口/官方冒烟验证 |
| 里程碑 B | I→F→V→C（问题解决） | 9 例 daemon-free 新单测 + 模拟回收真机对抗验证 |
| 本报告 | R→I→E→C（里程碑复盘） | G1 40 条事实 ✓ / G2 4 条四元组 ✓ / G3 模式 ✓ / G4 行动项 ✓ |

外部 Skill 协同：`compose-overlay-ops`（v1.0.3→v1.0.4，三栈运维 SOP 单一事实源）、`export-report-cmd`（本报告导出）。

---

## 三、R：客观事实清单（G1）

> 全部为当日工具输出或文件内容的可验证陈述；因果判断统一置于第四章。

### 3.1 里程碑 A：2223 端口占用与桥接入口安装

| 编号 | 事实 |
|------|------|
| F-001 | 用户提供的 trae-preview 控制台日志：`podman-compose up -d` 先输出 `Error: container 293dc1f0... conmon exited prematurely, exit code could not be retrieved: conmon process killed`，打印 `xmnn-dev` 与 3 个 64 位 ID，最后 `Error: unable to start container "fa7d9027...": rootlessport listen tcp4 0.0.0.0:2223: bind: address already in use`；同日志重复两次。 |
| F-002 | `podman ps -a`：jupyter-podman（294f2fe1f0f8）`Up 16 hours (healthy)`；xmnn-dev（fa7d90271ae9）状态 `Created`。 |
| F-003 | `ss -ltnp`：rootlessport pid=160171 持有 0.0.0.0 与 `[::]` 的 2223、8890 共 4 个 LISTEN。 |
| F-004 | `ps -ef`：rootlessport 160171 与 xmnn-dev 的 conmon 160191（-c 293dc1f0e029...）PPID 均为 157513；`ps -fp 157513` 为 root 身份的 `/init`。另有 jupyter-podman 自己的 conmon 27068（PPID 194）。 |
| F-005 | `podman inspect fa7d90271ae9` 标签：`com.docker.compose.project.config_files=D:\spaces\SpecWeave\apps\containers\client\overlays\xmnn-dev\compose.yaml`，working_dir 同为 `D:\...`，`io.podman.compose.version=1.6.0`。 |
| F-006 | Windows anaconda **base** 环境（D:\Users\xinzo\anaconda3）在 client 目录跑 `invoke -l` 报 RuntimeError：`No module named 'jpman_client'`，提示先 `pip install -e . --no-build-isolation`。 |
| F-007 | WSL podman-machine-default 内 `~/.local/bin/invoke` 存在，`invoke -l` 列出 xmnn.build/up/down/ps/logs/smoke/build-tvm/wheel 八任务。 |
| F-008 | 经 run-inv.sh 执行 `xmnn.up --skip-build` 的输出顺序：①检测到 Created/Exited 项目残留 → compose down；②孤儿 rootlessport pid=160171 定点回收；③1 个 stale conmon（容器 293dc1f0 不在 libpod）定点回收；④up -d 打印 7f0b619e、8b28ca2b 两个新 ID 与启动 banner；中间一行 `ERRO failed to move the rootless netns pasta process to the systemd user.slice: dbus: couldn't determine address of session bus`。 |
| F-009 | 浸泡 75 秒后：xmnn-dev `Up About a minute`、jupyter-podman 仍 `Up 16 hours (healthy)`；`podman exec xmnn-dev echo EXEC_OK` 输出 EXEC_OK；WSL 内 curl `127.0.0.1:8890/lab` 返回 302；2223/8890 均 LISTEN。 |
| F-010 | Windows 侧：`Invoke-WebRequest http://localhost:8890/lab` 得到 302（PS 以错误流呈现）；`Test-NetConnection -Port 2223` 的 TcpTestSucceeded=True。 |
| F-011 | `invoke xmnn.smoke` 全部 [OK]：base 3.14.7 cp314 GIL enabled / main 3.14.7 cp314t GIL disabled；llvm-config 与 clang 均 22.1.8；Nuitka 4.1.3；LLVM SONAME 系列；npu_tvm/npuusertools/models 挂载；tvm/vta/xmnn import 路径均在 /workspace；`tvm.build('llvm')` 向量加输出 [2,4,6,8]。 |
| F-012 | 用户在预防方案三选一中选择「装 Windows invoke 桥接（推荐）」。 |
| F-013 | py314（D:\Users\xinzo\anaconda3\envs\py314，Python 3.14.3）已装：invoke 3.0.3、jpman-common 0.1.0（editable 指向 apps/containers/shared）、podman-compose 1.6.0；未装 jpman-client。 |
| F-014 | py314 下 `pip install -e ".[compose]" --no-build-isolation`（tuna 源）先卸载一个同名非 editable 0.1.0，再 `Successfully installed jupyter-podman-client-0.1.0`。 |
| F-015 | py314 `invoke.exe xmnn.ps` 下发命令为 `podman-compose --project-name xmnn-dev --file /mnt/d/spaces/SpecWeave/...`，并打印「已经 WSL 发行版 podman-machine-default 桥接执行」。 |
| F-016 | py314 `invoke.exe xmnn.up --skip-build` 后再 ps：容器 ID 仍为 8b28ca2b0a4a、`Up 7 minutes`，无重建。 |

### 3.2 里程碑 B：enterns 劫持与 tmpfs 运行时目录

| 编号 | 事实 |
|------|------|
| F-017 | 用户报告 `inv xmnn.build`「为何进入 shell 了」。 |
| F-018 | 修复前桥接器（[utils.py](../../../../apps/containers/client/src/jpman_client/tasks/utils.py) `run_in_wsl_bridge`）下发的子进程 argv 为 `["wsl.exe","-d",distro,"--","bash","-lc",bash]`。 |
| F-019 | `/etc/profile.d/enterns.sh`：以 `ps -eo cmd,pid \| grep -m 1 ^/lib/systemd/systemd` 取 PID，非空且不等于 1 时 `cat /etc/wslmotd` 并执行 `/usr/local/bin/enterns`。 |
| F-020 | `/usr/local/bin/enterns`：对 `$UID != 0` 且**无参数**调用，组装 `sudo nsenter -m -p -t <pid> --wd=$PWD su -l $USER`；有参数时改为追加 `sudo -u $USER` 后执行 `"$@"`。 |
| F-021 | `/etc/profile.d/docker-host.sh` 全文：`export DOCKER_HOST="unix://$(podman info -f "{{.Host.RemoteSocket.Path}}")"`。 |
| F-022 | 后台实跑 py314 `inv xmnn.build --pip-mirror tuna --conda-mirror tuna` 退出码 1：`RunRoot is pointing to a path (/run/user/1000/containers) which is not writable`、`Error: creating events dirs: mkdir /run/user/1000: permission denied`、`[xmnn] ⚠ 无法连接到 podman 服务`、`WSL 桥接命令失败 (exit=1)`。 |
| F-023 | 登录与非登录 bash 探测均显示 `XDG_RUNTIME_DIR` 为空；`/run/user/1000` 不存在；`/mnt/wslg/runtime-dir` 存在且权限 777；探测输出头部均带 podman RunRoot warning。 |
| F-024 | 在命令内 `export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir` 后执行 podman，仍报相同的 `/run/user/1000: permission denied`，RC=125。 |
| F-025 | `sudo -n true` 成功；`stat -f /run/user` 文件系统类型 tmpfs；手工 `sudo mkdir -p /run/user/1000 && chown 1000:1000 && chmod 700` 后 `podman ps -a` RC=0，两个容器均 `Exited (0) 292 years ago`，伴随 `"/" is not a shared mount` warning。 |
| F-026 | 代码修改三处：①桥接 `bash -lc` → `bash -c`（PATH 前置 `~/.local/bin`、LANG 兜底 `C.UTF-8`、cd 移至 export 之后）；②新增 `ensure_wsl_rootless_runtime()`（`/proc/version` 含 microsoft 才动作；XDG 空且 /mnt/wslg/runtime-dir 可写则兜底；`/run/user/<uid>` 缺失则 `sudo -n` mkdir/chown/chmod 700；失败仅打印手工命令不阻断），在 `gate_platform` Linux 放行分支调用；③`Exit(cp.returncode, msg)` 改为 `Exit(msg, code=cp.returncode)`。 |
| F-027 | 新增 [test_wsl_bridge.py](../../../../apps/containers/client/tests/test_wsl_bridge.py) 9 例；test_overlay_core.py harness 增加 ensure 桩；全套 **84 passed, 1 skipped**。 |
| F-028 | 首轮新测试 5 failed，分别暴露：产品代码 `Exit` 参数反序（`.code` 实得消息字符串）、测试桩 WindowsPath `str()` 与 `/proc/version` 不匹配（改 `as_posix()`）、`argv=[]` 语义误判（空列表回退 sys.argv 后非空，改测 `argv=None` + 桩 sys.argv）。 |
| F-029 | 真机模拟回收：`sudo rm -rf /run/user/1000` 后裸 podman 复现 permission denied；Windows `inv xmnn.ps` 随即成功（自动重建目录、无登录 shell 的 podman warning），输出容器 `Exited (0) 292 years ago`。 |
| F-030 | 修复后 `inv xmnn.build --pip-mirror tuna --conda-mirror tuna` 直接进入 podman build 流（13 STEP，STEP 6 起因 ARG 值与旧缓存不同重新执行 apt），约 90 秒后 `COMMIT localhost/xmnn-dev:latest`（3d3df16730bf）。 |
| F-031 | 随后 `inv xmnn.up --skip-build`：Exited 残留先 down，新容器 c582c162（pod）/c6a0fd8b（容器）。 |
| F-032 | 约 1 分钟后跨 wsl.exe 的验证命令报 `no container with name or ID "xmnn-dev" found`（exit 56）、curl 000；当时 `uptime` 为 `up 20 min`（VM 未重启）；`/run/user/1000` 时间戳 08:52、属主 user；`podman ps -a` 输出为空。 |
| F-033 | `podman info`：graph=/home/user/.local/share/containers/storage，run=/run/user/1000/containers，events=journald；有 tag 镜像全部保留（xmnn-dev 3d3df16730bf、jupyter-podman-rootless、jupyter-podman-client、onnx-quantized 等）。 |
| F-034 | journalctl --user 08:53:04 记录：`POST /v5.7.0/libpod/system/prune?all=false&build=false&external=false&filters=%7B%7D&volumes=false HTTP/1.1" 200 875`，UA 含 Go-http-client；事件流：container remove c6a0fd8b（xmnn-dev）、pod remove c582c162（pod_xmnn-dev）、container remove 294f2fe1（jupyter-podman）、6 个 dangling image remove；08:52:28 另有 `system refresh` 与多条 acquiring lock 错误。 |
| F-035 | user `~/.bash_history` 尾部为 python/python3/exit 三组交替，无 prune；root history 为空；ps 无 prune/reset 残留；Windows tasklist 仅 wslservice.exe，无 podman/gvproxy/docker 桌面进程。 |
| F-036 | 单会话脚本 v-recover.sh（up→浸泡 80s→ps→exec→curl→smoke）退出码 0：up 时再收一个孤儿端口；新容器 c28f9008bbfc Up；EXEC_OK；HTTP 302；xmnn.smoke 全过。 |
| F-037 | 治理资产变更：[04 排障表](../../../../apps/containers/client/docs/04-troubleshooting-guide.md) 新增 W-I11/W-I12（表头计数改 W-I1~W-I12）；[windows-wsl.md](../../../../apps/containers/client/.agents/rules/windows-wsl.md) 新增 §8；client [CHANGELOG](../../../../apps/containers/client/.agents/CHANGELOG.md) 新增条目；[compose-overlay-ops](../../../../.agents/skills/compose-overlay-ops/SKILL.md) 错误表 +3 行、Gotchas +11、Changelog v1.0.4。 |
| F-038 | 全部代码与文档变更**未执行 git commit**；jupyter-podman 单容器（2222/8888）经用户确认暂不恢复。 |
| F-039 | 会话期间两次启动后台保活锚 `wsl -d podman-machine-default -- sleep infinity`。 |
| F-040 | py314 裸跑 `ruff check`（无项目 ruff 配置，默认规则集）报 8 errors：7 个 F401 在 utils.py:36-42 既存「再导出垫片」import 区、1 个 E741 在 utils.py:799 既存代码；本次新增/修改区段无违规，未顺手修改。 |

**G1 自查**：40 条 ≥20；无「因为/所以/导致/错误（作为判断）」等因果词；每条对应当日真实工具输出或文件内容。✓

---

## 四、I：核心洞察（G2 四元组）

### I-1：登录 shell 是给「人」的会话，自动化命令通道借道登录 shell 会被发行版人机交互设计劫持

| 维度 | 内容 |
|------|------|
| **陈述** | `wsl -- bash -lc <任务>` 把自动化任务注入了一个**完整登录会话**，而 Fedora-WSL 系镜像的登录会话包含面向真人的命名空间切换逻辑；无参数的 enterns 以 `su -l $USER` 收尾，其契约就是「交一个交互式 shell 给人」，命令串在边界处被丢弃。 |
| **证据** | F-017（现象）、F-018（-lc 通道）、F-019/F-020（enterns 条件与 `su -l` 分支）、F-030（改 -c 后 build 正常 90 秒完成）。 |
| **反常识** | 「`bash -lc` 比 `bash -c` 更完整（加载 PATH/环境）」是常见直觉；在该机镜像上这个「更完整」恰恰是故障源——profile 里既有劫持（enterns）又有副作用污染（F-021 docker-host.sh 每次登录跑 `podman info`，运行时坏掉时写出 `DOCKER_HOST=unix://`）。此前一直可靠的 run-inv.sh 用的恰是非登录的 `bash script.sh`，两种写法的差异在 build 之前从未被对照审视。 |
| **行动** | 所有自动化桥接固定非登录 `bash -c`，运行所需环境（PATH、LANG、工作目录、透传 env）在命令串内**显式**声明，不继承 profile 的隐含假设；新增非登录 argv 单测锁死（F-027）。 |

### I-2：rootless podman 的硬运行时根是 `/run/user/<uid>`，`XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir` 只覆盖套接字与临时文件，不能替代它

| 维度 | 内容 |
|------|------|
| **陈述** | 既有 SOP「无 systemd 发行版沿用 WSLg 的 XDG_RUNTIME_DIR」有适用边界：events dirs / runroot 仍按 `/run/user/<uid>` 解析；该目录在 tmpfs 上，VM 回收后无人重建，podman 全命令 exit 125，且「改 XDG」这一标准动作对它无效。 |
| **证据** | F-022/F-023（XDG 为空 + 目录缺失）、F-024（显式 XDG 后仍 125，反直觉关键证据）、F-025（tmpfs + 手工建目录后 RC=0、容器呈 292 年回收态）、F-029（删除目录→复现→自动重建→恢复的完整对照）。 |
| **反常识** | 过去多次排障形成的心智模型是「XDG 指对，podman 就对」；本次证明 XDG 与 `/run/user/<uid>` 是**两个独立前提**，前者由 WSLg 提供，后者在该发行版上是「enterns 进入 systemd 命名空间」的隐式副产品——不走登录会话（I-1 的修复方向）后，这个副产品也消失了，两个故障因此在同一天连环暴露。 |
| **行动** | 非登录通道必须配套**显式自愈**：`ensure_wsl_rootless_runtime()` 在 WSL2 判定下幂等补建目录（sudo -n，失败只警告）；排障速查 W-I12 明确写出「仅 export XDG 不够」，防止后人重走 F-024 的无效尝试。 |

### I-3：编排器能自愈「自己造成的混乱」，但对「第三方经共享套接字发起的全局操作」只能识别与恢复，不能防御

| 维度 | 内容 |
|------|------|
| **陈述** | 08:53 的容器整体消失不是 VM 回收（uptime 20min）、不是本项目命令（journal 显示 REST `system/prune`、UA Go-http-client），而是一个共享 podman.sock 的外部客户端的全局清理；preflight 三道针对的是 compose 平面分歧与孤儿进程，对 prune 这类合法但越界的外部写操作没有防御点。 |
| **证据** | F-032（VM 未重启但记录消失）、F-034（prune 请求行 + 跨项目删除清单）、F-033（有 tag 镜像/卷无损）、F-035（发起方进程已退出、本侧无可执行残留）、F-036（一条 up 即恢复）。 |
| **反常识** | 「容器不见了 = 又被 WSL 回收了」是本周期排障形成的强联想（F-025 的 292 年 Exited 强化了它）；本次 uptime 与 journal 证伪了该联想——回收态容器记录仍在，而 prune 会让记录本身消失。**记录在不在**是区分两类事故的最快判据。 |
| **行动** | 不在编排器里加防 prune 机制（超出边界、误伤合法运维）；在 SOP 错误表登记识别特征（journal 的 `POST /libpod/system/prune` + 跨项目容器同秒消失）与一条命令恢复路径；提示用户排查共享该 socket 的 UI/自动化（F-037 已落 v1.0.4）。 |

### I-4：对易错操作，「入口收敛」比「纪律约束」更可靠——第四次复发的终局是让错误入口不再可达

| 维度 | 内容 |
|------|------|
| **陈述** | 2223 事故在 2026-09-15 已三次复现并沉淀「同一栈固定单一控制平面」纪律（W-I10），次日用户在新的浏览器终端里再次裸跑 `podman-compose up -d` 即第四次复发；真正终止复发的不是重申纪律，而是在 py314 装好 invoke 桥接，使 `invoke` 成为该终端里最顺手的入口（裸 compose 路径长、无 preflight）。 |
| **证据** | F-005（D:\ 标签证明复发入口）、F-012（用户选择装桥接）、F-013~F-016（安装 + `/mnt/d` 同平面实证 + 二次 up 零重建）、F-008（preflight 对旧事故现场仍有效，说明两层防护互补）。 |
| **反常识** | 文档/SOP 倾向于把对策写成「不要做 X」的纪律；但人在新终端、新 UI 入口下不会携带纪律。把正确路径的**摩擦力降到低于**错误路径（装好、短命令、带自愈、出错给中文提示），比任何警示都有效。 |
| **行动** | 复发预防优先次序更新为：①入口收敛（默认装好/默认桥接）→ ②自动自愈（preflight）→ ③纪律文档（最后兜底）；环境装配清单（W-I9 三步安装）写入新人上手必填项。 |

**G2 自查**：4 条洞察维度独立（shell 会话语义 / rootless 文件系统前提 / 防御边界 / 预防策略层级），四元组完整且均引用事实编号。✓

---

## 五、E：模式萃取（G3）——「非登录命令通道」模式

### 5.1 模式卡

| 项 | 内容 |
|----|------|
| **名称（4–8 字）** | 非登录命令通道 |
| **一句话** | 自动化跨边界执行命令时，显式构造最小环境的非登录 shell，禁止借道面向真人的登录会话。 |
| **适用于** | ① 经 wsl.exe/ssh/nsenter/docker exec 等边界向另一个用户环境下发自动化命令；② 目标环境的 profile 含人机交互、环境探测或命名空间切换逻辑；③ 命令需要可重入、可被守护进程/IDE/CI 非交互调用。 |
| **不适用于** | ① 明确需要登录语义的人工排障（此时本就该有人坐在终端前响应交互）；② 目标环境 profile 经审计无副作用且团队已将登录 shell 作为唯一受支持入口。 |
| **多案例支撑** | L2（同会话两个独立案例：enterns `su -l` 劫持任务、docker-host.sh 污染 DOCKER_HOST；加此前 run-inv.sh 长期正例）。 |

### 5.2 核心步骤（可直接执行）

1. **通道选型**：自动化一律 `wsl -d <d> -- bash -c '<cmd>'` 或 `wsl -d <d> -- bash /abs/script.sh`；PowerShell 侧逻辑复杂时落脚本文件，杜绝内联引号插值（本仓库 §9 陷阱 7）。
2. **环境显式化**：命令串内自声明 `PATH`（含工具实际安装目录，如 `~/.local/bin`）、`LANG`（非登录无 lang.sh）、`cwd`、需要透传的 env 白名单；不假设 profile 存在。
3. **前置条件自愈化**：列出命令对登录会话副产品的隐式依赖（本次为 `/run/user/<uid>`），在非登录通道里以幂等、可降级（`sudo -n`，失败只警告）的方式自建。
4. **通道契约单测化**：断言最终 argv 含 `-c` 不含 `-lc/--login`、任务串逐字保留、空参数不裸开交互 shell、子进程退出码原样上抛（F-027/F-028）。
5. **双向验证**：先在目标环境模拟「VM/会话刚重启」的冷态（删 tmpfs 目录），再从宿主打一次完整调用；浸泡后用「真实动作探针」（podman exec echo ok）而非端口/进程表判活。

### 5.3 反模式（均来自实战教训）

- ❌ **`bash -lc` 一把梭**：贪图 profile 自动配好的环境，把 enterns `su -l` 劫持与 docker-host 探测污染一并引入（F-018~F-021）。
- ❌ **通道坏了先怀疑 XDG**：看到 podman 报路径权限就只改 `XDG_RUNTIME_DIR`，忽视 events/runroot 的独立硬编码路径，在同一个 125 上空转（F-024）。
- ❌ **容器消失就归因 VM 回收**：不看 uptime 与 journal，把外部 `system/prune` 当回收处理，排查方向整体偏移（F-032/F-034）。
- ❌ **用纪律终止复发**：只在文档写「不要裸跑 compose」，不给低摩擦正确入口，新终端里必然第四次复发（I-4）。
- ❌ **退出码靠位置参数「想当然」**：`Exit(rc, msg)` 在 invoke 里语义反了，测试缺失时桥接失败永远 exit 1（F-028）。

### 5.4 检验标准

- 冷态（删 `/run/user/<uid>`、新开非登录通道）一次调用成功，无交互提示、无 profile 噪音；
- 同通道连续两次调用幂等（容器 ID 不变）；
- 守护进程/IDE/CI 三种非交互发起方均可重入；
- argv 契约与冷态自愈均有 daemon-free 单测。

### 5.5 跨场景迁移

- **SSH 自动化**：`ssh host "<cmd>"`（非登录）与 `ssh host`（登录）之别同理；`~/.bashrc` 里输出欢迎语或 `read` 的机器，Ansible/CI 直连常挂——标准解法也是命令通道与交互通道分离。
- **CI runner**：runner 以非登录 shell 执行时依赖的 PATH 必须在 pipeline 显式声明，与本模式步骤 2 同构。
- **`docker exec`/`kubectl exec`**：自动化用 `exec -- cmd`（不经登录 shell）；需要 profile 时显式 `bash -lc` 是**有意选择**而非默认。

**G3 自查**：名称 7 字 ✓；适用/不适用边界 ✓；5 步骤 ✓；反模式 5 条 ✓；检验标准 ✓；跨域迁移 3 例 ✓；L2 多案例 ✓。

---

## 六、C：原子行动项与交付（G4）

| # | 行动项 | 验收标准 | 状态 |
|---|--------|---------|------|
| 1 | 桥接改非登录 + 运行时自愈 + Exit rc 修正（[utils.py](../../../../apps/containers/client/src/jpman_client/tasks/utils.py)、[overlay_core.py](../../../../apps/containers/client/src/jpman_client/tasks/overlay_core.py)） | 84 passed/1 skipped；冷态真机自愈；build 90s 成功 | ✅ 已完成未提交 |
| 2 | 新增 test_wsl_bridge.py 9 例 + harness 补桩 | 非登录 argv/空 argv/rc/平台判定/幂等/sudo 失败/XDG 兜底全覆盖 | ✅ |
| 3 | py314 安装 jupyter-podman-client[compose] editable | Windows invoke 下发 `/mnt/d` 平面；二次 up 零重建 | ✅（环境动作） |
| 4 | client 治理资产：W-I11/W-I12、windows-wsl §8、CHANGELOG | 速查表计数一致、规则与代码注释互指 | ✅ |
| 5 | compose-overlay-ops v1.0.4（错误表 3 行/Gotchas 11/Changelog） | 用户已批准落盘 | ✅ |
| 6 | 本复盘报告导出并注册 toctree + 链接检查 | check-links 无断链 | ✅（本次） |
| 7 | 原子提交：建议拆 `fix(client): WSL 桥接非登录与运行时自愈` 与 `docs(skills): compose-overlay-ops v1.0.4` 两个提交 | Conventional Commits + 中文「为什么」+ `[prevent: test-case]` | ⏳ 待用户指令 |
| 8 | jupyter-podman 单容器（2222/8888）恢复 | jpman 单容器路径启动、双端可达 | ⏳ 用户决定暂不恢复 |

---

## 七、遗留与风险

1. **外部 prune 发起方未最终指认**：journal 只有短连接的 UA，进程已退出（F-035）；镜像/卷无损，后续若复现应在 prune 发生时立即 `ss -xp` 抓 peer inode 对照，或临时收紧 podman.sock 的访问范围。
2. **ruff 8 个既存告警**（F-040）：再导出垫片 F401 与 E741 属历史代码，建议另开 `style(client)` 提交处理（加 per-file-ignores 或重命名变量），本次保持单一职责未触碰。
3. **autorest 式自愈的副作用面**：`ensure_wsl_rootless_runtime` 会在 WSL2 上执行 `sudo -n mkdir`；当前以 `/proc/version` 白名单 + 仅补 `/run/user/<真实uid>` + 失败不阻断三重收窄，后续若 client 支持其他无 sudo 发行版，需要按 SOP 警告路径验证。
4. 变更均未提交（F-038），工作区同时存有前序未提交改动，提交时需三查暂存、按 #7 拆分。

---

## 八、结论

两个故障表面无关（一个端口占用、一个误入 shell），底层同属一条主线：**Windows→WSL 自动化通道在 2026-09-15 重构后跑通了「能工作」的路径，但通道两侧的环境契约（shell 会话语义、tmpfs 运行时前提、控制平面身份）始终隐式存在**。一旦浏览器终端成为新入口、VM 回收改变冷态，这些隐性契约就连续显性化。

最终的稳态由三层构成，且三层都有自动化测试或真机证据锁定：**入口收敛**（py314 invoke 桥接，I-4）→ **非登录通道 + 冷态自愈**（I-1/I-2，代码层）→ **preflight 三道与 SOP 兜底**（既有 W-I8/W-I10 资产）。模式「非登录命令通道」可迁移到 SSH/CI/容器 exec 的所有自动化边界。
