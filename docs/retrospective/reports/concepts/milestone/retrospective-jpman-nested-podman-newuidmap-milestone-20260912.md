---
id: "retrospective-jpman-nested-podman-newuidmap-milestone-20260912"
title: "嵌套 rootless 容器 newuidmap EPERM 三连修复里程碑复盘（B-scheme 五通道桥接→SSH 环境模型→构建加速分诊）"
date: "2026-09-12"
source: "2026-09-12 apps/containers/{jupyter-podman-rootless,client} 容器内 podman-compose 故障三连修复批次（3 提交 + 技能 v1.1/v1.2）"
type: milestone-retrospective
scope: milestone
status: completed
methodology: "七概念 场景2 F→V→C→R→I→E（故障）+ 场景1 R→I→E→V→A→C（里程碑）"
related_patterns:
  - "nested-capability-boundary-first（L1 候选，暂固化于 jpman-podman-ops §9.1）"
  - "shell-form-startup-matrix（L1 候选，暂固化于 jpman-podman-ops §9.1）"
  - "external-cli-version-drift-fallback"
---

# 嵌套 rootless 容器 newuidmap EPERM 三连修复里程碑复盘

## 里程碑范围

同一报错（容器内 `podman-compose up` → `newuidmap: write to uid_map failed: Operation not permitted`）在 2026-09-12 一天内经历三个回合：① podman exec 通道临时绕行并提出镜像侧改动；② 镜像桥接落地（提交 `d5df08dd1`）；③ 用户真实 SSH 终端仍报错，补全 sshd 环境链路（提交 `aa0a75170`）；并附带一次"构建疑似卡死"排障与技能文档两版升级（`dce9f050f` v1.1.0、`7232595b8` v1.2.0）。交付物：镜像侧 2 代码提交 + 技能文档 1 提交 + 本复盘，共 6 个提交推送 origin/main。

## 事实清单（R 阶段）

| # | 事实 |
|---|------|
| F-01 | 用户在容器 `e3c62786521a` 内 devuser 终端执行 `podman-compose up`，输出 `/usr/bin/newuidmap ... 0 1000 1 100000 65536: newuidmap: write to uid_map failed: Operation not permitted`，进程退出码 1 |
| F-02 | 外层容器 inspect 字段：Privileged=false、SecurityOpt=[label=disable]、CapAdd=[]、Devices 含 /dev/dxg、Config.User=root |
| F-03 | 容器内 /usr/bin/newuidmap、/usr/bin/newgidmap 权限位均为 `-rwsr-xr-x root root`（setuid 位存在） |
| F-04 | 容器内 /etc/subuid、/etc/subgid 内容均为单行 `devuser:100000:65536` |
| F-05 | devuser 视角 /proc/self/uid_map 两行：`0 1000 1`、`1 524288 65536` |
| F-06 | devuser 进程 CapEff=CapPrm=`0000000000000000`；root 进程 CapBnd=`00000000800405fb` |
| F-07 | 能力集 `0x800405fb` 按位解码：bit21（CAP_SYS_ADMIN）为 0，bit7（CAP_SETUID）为 1 |
| F-08 | devuser 对新 userns 子进程执行 newuidmap 写 `0 1000 1 1 100000 65536`，退出码 1，stderr 为 `newuidmap: write to uid_map failed: Operation not permitted` |
| F-09 | 将 /etc/subuid、/etc/subgid 改为 `devuser:524288:65536` 后同一调用退出码仍为 1，stderr 文本相同 |
| F-10 | 单 extent 调用 `newuidmap <pid> 0 1000 1`，退出码 1，stderr 文本相同 |
| F-11 | devuser 在新 user namespace 内自行向 /proc/self/uid_map 写 `0 1000 1`，shell 返回 `write error: Operation not permitted` |
| F-12 | podman machine VM 内核版本 `6.18.35.2-microsoft-standard-WSL2`；/proc/sys/user/max_user_namespaces=62907；无 unprivileged_userns_clone 键 |
| F-13 | VM 宿主 user(1000) 执行 newuidmap（`0 1000 1 1 100000 65536`），stderr 为 `newuidmap: uid range [1-65537) -> [100000-165536) not allowed`，文本与容器内 EPERM 不同 |
| F-14 | 容器内 root 执行 podman info 输出 `Using rootless single mapping into the namespace` 警告；graph driver=overlay，graphroot=/var/lib/containers/storage |
| F-15 | 容器内 root 首次 podman load（1.96 GB client 镜像管道传输）退出码 125，stderr 含 `lchown /etc/gshadow: invalid argument` 与 `requested 0:42 for /etc/gshadow` |
| F-16 | 在 /etc/containers/storage.conf 设置 ignore_chown_errors 并清空旧存储后，root podman load 输出 `Loaded image: localhost/jupyter-podman-client:latest` |
| F-17 | root podman build 执行到 STEP 2/2 RUN，crun 报 `open /proc/sys/net/ipv4/ping_group_range: Read-only file system` |
| F-18 | root `podman run --net host` 报 cgroup.subtree_control 只读；追加 `--cgroups=disabled` 后报 `mount devpts to dev/pts: Invalid argument` |
| F-19 | 容器 / 挂载 findmnt 传播属性为 `private`；容器内 `mount --make-rshared /` 返回 `mount failed: Unknown error 5005` |
| F-20 | 容器内存在单文件挂载 /run/user/1000/podman/podman.sock（容器内呈现 root:root 0660）；容器 config env 含 HOST_PODMAN_SOCK=/run/user/1000/podman/podman.sock |
| F-21 | devuser 设置 `CONTAINER_HOST=unix:///run/user/1000/podman/podman.sock` 后 podman ps 列出宿主侧 jupyter-dev、jupyter-podman 两个容器 |
| F-22 | 同一 CONTAINER_HOST 下 podman-compose build 输出 `Python 3.14.7` 与 `Successfully tagged localhost/tests_app:latest`；up 后 tests_app_1 状态 Up，down 后无残留 |
| F-23 | tests/Dockerfile 第 3 行原文为 `RUN "/opt/conda/envs/main/bin/python -V"`；修改为 `RUN /opt/conda/envs/main/bin/python -V` |
| F-24 | 在 VM 宿主建 /workspace → /mnt/d/spaces/SpecWeave 软链；删除软链后 compose build/up/down 输出与 F-22 相同；软链随后删除 |
| F-25 | 首版镜像桥接（/etc/profile.d/80-podman-host-socket.sh + devuser .bashrc source + `ENV BASH_ENV`）经提交 `d5df08dd1` 落地（4 文件，+49/-1） |
| F-26 | 裸 `invoke build` 期间 buildah 子进程为 `curl ... /tmp/miniforge.sh github.com...`；5 秒采样 eth0 收包速率 221 KB/s |
| F-27 | local-cache/miniforge/ 目录内容仅 .gitkeep 一个文件 |
| F-28 | 经 tuna 镜像 curl Miniforge3-Linux-x86_64.sh：文件 119MB，耗时 16 秒，平均约 7.5 MB/s；`bash <file> -h` 输出 usage（Miniforge3 26.7.2-0） |
| F-29 | 带 `--apt-mirror tuna --conda-mirror tuna --pip-mirror tuna` 的重建：Stage 2 conda-builder 构建计时 148 秒 |
| F-30 | 全天基底 jupyter-podman-rootless 镜像共重建 5 次（最终镜像 d0a678930b9e） |
| F-31 | 用户在 17:19 启动的容器 `f7acf37a5767`（localhost/jupyter-podman-client:latest）SSH 终端再次输出与 F-01 相同的 newuidmap 报错 |
| F-32 | `env -i HOME=... USER=devuser bash -lc` 干净环境下 printenv 三变量：HOST_PODMAN_SOCK、CONTAINER_HOST、XDG_RUNTIME_DIR 均为空；id=1000 |
| F-33 | 与 F-32 同一干净环境下 `ls /run/user/1000/podman/podman.sock` 成功，属性 srw-rw---- root root；devuser groups 含 0(root) |
| F-34 | 真实 SSH 同一会话内 `printenv BASH_ENV` 输出 `/etc/profile.d/80-podman-host-socket.sh`；双引号命令中 `$BASH_ENV` 输出为空 |
| F-35 | BASH_ENV 启动 trace 探针：`bash /tmp/form-test.sh`（脚本文件）与子 bash 各触发 1 次 source，`ssh host "cmd"` 最外层 bash 触发 0 次 |
| F-36 | /etc/pam.d/sshd 含两行 `session required pam_env.so`（默认 envfile 与 envfile=/etc/default/locale） |
| F-37 | 容器 OpenSSH 版本 OpenSSH_10.2p1 Ubuntu-2ubuntu3.6；镜像 sshd_config 原本无 SetEnv 行，AcceptEnv 仅 LANG/LC_* |
| F-38 | entrypoint.sh B-scheme 分支新增运行时写 `SetEnv CONTAINER_HOST=unix://<host_sock>`（写后 `sshd -t` 校验，失败 sed 删除回滚；回退分支同步删事实文件与 SetEnv 行），经提交 `aa0a75170` 落地（4 文件，+58/-11） |
| F-39 | 修复后真实 SSH `ssh host 'printenv CONTAINER_HOST'` 输出 `unix:///run/user/1000/podman/podman.sock`；容器启动日志含 `sshd SetEnv CONTAINER_HOST written` |
| F-40 | 真实 SSH（ssh -tt，key 免密）tests 目录全新周期：build → `tests_app_1 Up 3 seconds` → down → 无残留，全程无 newuidmap 行 |
| F-41 | GUI 透传容器启动日志含 `Inherited XDG_RUNTIME_DIR ownership aligned: /tmp/runtime-user -> devuser`、`[B-scheme] [OK] devuser can read/write host podman socket` |
| F-42 | 模拟全新状态（/tmp/runtime-user root:root 0755、libpod 移出）下 devuser podman ps 输出 `Failed to obtain podman configuration: mkdir /tmp/runtime-user/libpod: permission denied` |
| F-43 | 镜像内桥接资产 5 处：/etc/profile.d/80-podman-host-socket.sh（644，27 行，四级解析）、/etc/podman-host-sock.path（644）、/etc/environment 的 BASH_ENV 行、sshd_config 运行时 SetEnv 行、devuser .bashrc 末尾 source 行 |
| F-44 | 当日 6 个提交推送至 origin/main（区间 e644e6c8c..7232595b8）：d5df08dd1、并行会话 dce9f050f/9e70ff499/34a53c1aa、aa0a75170、7232595b8；远端 Git Hooks 输出 PASSED |
| F-45 | jpman-podman-ops SKILL.md 版本 v1.1.0 → v1.2.0：新增 §9.1（净增 97 行），含五通道矩阵表、三步分诊、取证命令包、5 条反模式；15 个本地链接检查全部通过 |
| F-46 | 最终容器 Jupyter `GET /api` HTTP 200；tests 目录属性 drwxrwxrwx root root（9p 挂载），全天未出现该目录属主变更记录 |
| F-47 | 全天 podman machine 内并存容器：jupyter-dev（localhost/jupyter-podman-rootless:toolbx，Up 28h）、jupyter-podman（client 镜像，当日 3 次重建）；另有 notebook_test_1（nvidia/cuda:13.3.1-base-ubuntu26.04）Created 状态 |

## 核心洞察（I 阶段）

### I1：报错文本指向的组件是"信使"不是"修复对象"——嵌套容器化先验能力边界

- **陈述**：newuidmap 与 /etc/subuid 都处于正常状态（F-03/F-04），EPERM 的决定因素是外层容器授予中间 user namespace 的能力集不含 CAP_SYS_ADMIN（F-06/F-07）；在该边界下，非 root 的容器内 rootless podman 没有任何容器内配置可以使其工作。
- **证据**：F-05~F-11（能力位 + 三种 newuidmap 调用形态全部退出 1）；F-13（VM 宿主同命令报不同文本，对照出边界位置）；F-14~F-19（容器内 root single-map 路径的三种独立失败）。
- **反常识**：报错自带的行动建议（`Check /etc/subuid and /etc/subgid`）与最显眼的可执行文件（setuid newuidmap）都指向"配置可修复"；连续三个沿报错字面构造的假设（subuid 区间对齐、root single-map、shared mount）被对照实验逐一否定。
- **行动**：嵌套容器化失败先取"三件套"——`/proc/self/uid_map`、`grep CapBnd /proc/self/status` 位解码、VM 宿主同命令对照；能力位不满足时直接切换架构（socket 转发给宿主 daemon），不在容器内做 userns 调参。

### I2：验证通道必须等于故障通道——"同容器同命令"有 4 种进程环境模型

- **陈述**：首版修复的 V1-V7 验证全部经 `podman exec` 进行并通过（F-21/F-22），但用户真实 SSH 终端在同一镜像、同一命令下失败（F-31）；两种通道的环境差异是 sshd+PAM 重建会话环境，容器 config env 三变量在 SSH 登录 shell 中为空（F-32），而 socket 文件客观存在（F-33）。
- **证据**：F-20（容器 env 注入点）、F-31~F-33（SSH 清洗实证）、F-34（environ 有值与 shell 变量表为空在同进程并存）。
- **反常识**：直觉把"容器"当作单一环境，实际 podman exec 继承容器 config env、sshd 会话经 PAM 清洗、Jupyter Terminal 又是第三类；甚至"变量已注入"的测量都有两个相反答案——`printenv`（读进程 environ）与双引号 `$VAR`（读 shell 变量表，且被外层 SSH shell 提前展开）。
- **行动**：环境注入类需求的验证矩阵必须按通道枚举（真实 SSH key 免密、`env -i` 干净会话、Jupyter Terminal 同形态），禁止用 podman exec 结论替代；远程会话变量一律用 `printenv VAR` 读取。

### I3：shell 启动文件的读取是"形态依赖"的——单一注入点必有盲区，五通道是穷举结果

- **陈述**：bash 只在执行**脚本文件**时读取 BASH_ENV，对 `bash -c "命令字符串"`（即 `ssh host "cmd"` 与 sshd 最外层 shell）不读取任何启动文件（F-35）；覆盖全部 shell 形态需要 5 条彼此独立的通道（F-43），其中 sshd `SetEnv` 是唯一不经任何 shell 启动文件的注入点（F-36~F-40）。
- **证据**：F-35（trace 计数 3 次 vs 0 次）、F-37（sshd 原无 SetEnv）、F-38/F-39（SetEnv 落地后 ssh cmd 形态 printenv 有值）、F-40（端到端通过）。
- **反常识**：BASH_ENV 的命名与常规文档暗示"非交互 bash 统一入口"，实测它按"是否有脚本文件路径"二分；profile.d/.bashrc/BASH_ENV 三通道看似完备，在 `ssh host "cmd"` 这一个常见形态上整体失效。
- **行动**：环境注入功能按四形态穷举设计（登录交互 / 非登录交互 / 非交互脚本文件 / 非交互命令字符串）并逐形态实测；动态路径信息用运行时事实文件（/etc/podman-host-sock.path，entrypoint 写入）桥接 PAM 环境丢失与非标准挂载点；桥接脚本自身做四级解析，显式值最高优先。

### I4："慢"与"卡"是两类问题——观察工具本身会制造故障假象

- **陈述**：首次构建的长耗时由两个独立成分构成：裸 invoke build 默认解析到 GitHub 单源（实测 221 KB/s，F-26）与本地安装包缓存为空（F-27）；而"日志 0 字节、疑似挂起"的观察来自 PowerShell `Select-Object -Last N` 必须等上游进程结束才输出，与构建进程无关。
- **证据**：F-26~F-29（取证→换源→148 秒基线）；后台任务 output.log 在整个构建期间为 0 字节、改 Tee-Object 后可实时 tail。
- **反常识**："屏幕长时间不动"在直觉里等价于"进程卡死"，但瓶颈可能在下载（curl 活着）、9p IO（流量 0 CPU 低）或观察管道（进程正常、缓冲在终端侧）三者之一，处置方式完全不同。
- **行动**：宣布构建"卡死"前先做 30 秒取证（ps 阶段识别 + 5 秒网卡采样）；长任务一律 `Tee-Object` 流式落盘；默认构建命令带齐 tuna 三镜像源参数，大安装包预灌 local-cache/。

## 萃取（E 阶段）

两个 L1 候选模式（单领域、多轮实验支撑）已固化于 `jpman-podman-ops` SKILL v1.2.0 §9.1，待第二个非容器领域案例出现后升级 L2 并迁移至 `docs/retrospective/patterns/`：

1. **嵌套能力边界先验（nested-capability-boundary-first）**：在"外层沙箱内再起同类隔离"失败时，先枚举外层授予的能力/系统调用边界，再决定是调参还是换架构；触发于 DinP/DinD、受限 PSP 的 Kubernetes Pod、CI runner 嵌套虚拟机、flatpak/snap 内包管理器。反模式：沿报错自带建议修配置、用 --privileged 消错、把信使组件当根因。
2. **Shell 形态启动文件矩阵（shell-form-startup-matrix）**：凡"给所有终端注入环境变量"的需求，按四种 shell 调用形态 × 启动文件读取语义建矩阵，逐格验证；跨域迁移：systemd Environment= 与 sshd/cron 差异、GitHub Actions 中 `$GITHUB_ENV` 对不同 step shell 的可见性、conda 激活在 Jupyter kernel 与 SSH 的差异。反模式：只验证交互终端即宣称全形态覆盖、用引号展开远程读变量、镜像改完不重建消费侧容器。

复用既有模式：`external-cli-version-drift-fallback`（候选回退思想同构于本次"显式 CONTAINER_HOST ＞ 多信息源回退"四级解析）。

## 对抗审查（V 阶段，轻量）

| 视角 | 攻击 | 处置 |
|---|---|---|
| 魔鬼代言人 | "CAP_SYS_ADMIN 缺失"只在当前外层启动参数下成立，换启动方式（--userns=host/特权）也许可行 | 结论显式限定"非特权 rootless 外层容器"；并记录 F-18/F-19 证明即便容器内 root 放开 userns，netns/cgroup/devpts 仍连续失败，换架构成本低于改授予方式 |
| 新人 | 报错里建议查 subuid，复盘却说不用查，第一次遇到怎么信？ | §9.1 保留"先取证三件套"可复跑命令，能力位解码可当场自证；证伪实验（F-09/F-10）写入文档 |
| 老板 | 一天 5 次重建、3 个回合才修完，投入产出？ | 首版若走真实 SSH 验证可省 2 次重建（约 10 分钟）；收益是后续同类报障按 §9.1 三分钟定位，且消除了"exec 过了即交付"的系统性验证盲区 |
| 未来 | 内核/podman 版本升级后嵌套 rootless 可能被支持，结论会过期 | 结论标注环境版本（kernel 6.18.35 WSL2 / podman 5.7.0 / OpenSSH 10.2p1）；桥接全部带守卫与 no-op 回退，未来原生可用时不会成为阻碍 |

## 行动项（A/C 阶段）

| # | 行动 | 验收标准 | 状态 |
|---|------|---------|------|
| A1 | 镜像侧五通道桥接 + 四级解析 + 回退清理（feat+fix 两提交） | 真实 SSH 四形态 printenv 有值；compose build/up/down 全新周期通过；无 socket 启动回退分支日志正常 | ✅（F-39/F-40，d5df08dd1、aa0a75170） |
| A2 | 构建加速分诊与操作纪律固化（tuna 三源 + 本地预灌 + Tee 观察） | Stage 2 基线 ≤150 秒；技能 §8.5 含取证命令与 4 反模式 | ✅（F-29，dce9f050f） |
| A3 | 嵌套 Podman 分诊固化进 jpman-podman-ops v1.2.0 | §9.1 含根因/五通道矩阵/三步分诊/取证包/5 反模式；链接检查通过 | ✅（F-45，7232595b8） |
| A4 | 本复盘落盘 + milestone 索引追加 | 报告 frontmatter 完整、索引行可检索、原子提交 | ✅（本次提交） |
| A5 | （后续）两个 L1 候选模式待第二领域案例后升级 L2 入 patterns/ 库 | 出现 1 个非容器领域复用案例 | ⏳ 待触发 |

## 质量门记录

- **G1**：事实 47 条，均为可验证客观陈述（含容器 ID、能力位十六进制、命令输出、计时、提交号），报错文本以引用形式作为证据，无因果判断词
- **G2**：洞察 4 条，均含陈述/证据（引用 F 编号）/反常识/行动四元组，维度各自独立（内核能力边界、进程环境模型、shell 启动语义、观察方法）
- **G3**：模式 2 个（L1 候选），含触发场景、核心做法、≥3 反模式、检验标准与跨领域迁移示例，已在技能 §9.1 结构化承载，升级条件明确（A5）
- **V 门**：4 视角各 1 条实质攻击，4 条全部采纳（结论限定环境边界、保留可复跑取证、记入复盘成本分析、守卫/no-op 防过期）
- **G4**：行动项 5 项（4 完成 1 待触发），已完成项均有原子提交与运行时验证，A5 为显式待触发而非遗留
