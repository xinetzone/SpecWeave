---
id: "retrospective-jpman-client-stability-milestone-20260910"
title: "jpman-client 消费端可用性加固里程碑复盘（构建瘦身→加载校验→SSH 接入→运行时就绪）"
date: "2026-09-10"
source: "2026-09-07~09-10 apps/containers/client 可用性加固批次（16 提交）"
type: milestone-retrospective
scope: milestone
status: completed
methodology: "七概念 R→I→E→C"
related_patterns:
  - "win-powershell-compress-archive-gzip-mismatch"
  - "python-pathlib-tilde-no-expansion"
  - "external-cli-version-drift-fallback"
  - "container-copy-context-whitelist"
  - "user-switch-cleanup-partitioning"
---

# jpman-client 消费端可用性加固里程碑复盘

## 里程碑范围

`apps/containers/client`（jupyter-podman-rootless 镜像消费端）自镜像构建瘦身起，到镜像加载校验、容器启动、SSH 接入、运行时就绪预检的全链路可用性加固。时间窗 2026-09-07 ~ 2026-09-10，共 16 笔提交（含 2 笔文档复盘、1 笔脱敏）。

## 事实清单（R 阶段）

| # | 事实 |
|---|------|
| F-01 | 提交 `b4329b4b9` 将 `ContainerConfig.image` 默认值泛化为 `localhost/jupyter-podman-client:latest`，使其成为"镜像管理枢纽" |
| F-02 | 提交 `5299380ea` 将 client 镜像体积从 2.82 GB 优化至 1.80 GB（增量层 -59%） |
| F-03 | `.image-cache/` 中的 `.tar.gz` 由 Windows `Compress-Archive` 生成，实际为 ZIP 格式；`podman load` 报 `archive/tar: invalid tar header`（提交 `b2480446c` 记录） |
| F-04 | 修复方式为 Python `gzip.open()` 重压（对齐 build-end `podman save \| gzip` 管道），重新生成 571 MB / 357 MB 两个归档 |
| F-05 | 提交 `b2480446c` 新增 `validate_manifest_integrity()`，在 `inv load` 前校验 manifest.txt 的 SIZE/SHA256 |
| F-06 | 首次实现的块匹配按"段标题白名单"命中，导致加载任意镜像都匹配 manifest 第一个块（client 571M），rootless 镜像误报 `manifest=571M, 实际=357MB`（提交 `4c409f6d5` 修复） |
| F-07 | 修复后改为按 `IMAGE_FILE` 字段与当前 tar 文件名精确一致匹配；实测 rootless→357M、client→571M、未登记文件跳过校验 |
| F-08 | `ensure_known_hosts()` 使用 `Path(os.environ.get("HOME", "~"))` 构造 known_hosts 路径 |
| F-09 | 实测 Windows PowerShell 环境：`HOME` 为 `None`；`Path("~")` 返回 `WindowsPath('~')`（字面量）；`.exists()` 为 `False`；`Path.home()` 返回 `C:\Users\<user>` |
| F-10 | 提交 `a5ab75d75` 改 `Path.home()`，并拆分 `clean_stale_host_keys()`（启动前仅清理）与 `refresh_host_keys()`（启动后获取），正则限定 localhost/127.0.0.1/::1 |
| F-11 | 容器 entrypoint `generate_host_keys()` 每次启动 `rm -f /etc/ssh/ssh_host_*_key` 后 `ssh-keygen -A`（镜像不携带预生成密钥） |
| F-12 | 容器条目 `-v <workspace>:/workspace` + podman socket 两条挂载，未挂宿主 D 盘；用户 `cd /mnt/d` 报 `No such file or directory` |
| F-13 | 提交 `72118fcde` 将 refresh 的 4 次盲 keyscan（约 5s 窗口）改为 TCP 探测等待 sshd 就绪（最长 20s） |
| F-14 | 实测沙箱：`127.0.0.1:2222` OPEN、`::1:2222` closed，即容器端口转发仅绑定 IPv4 |
| F-15 | 容器内 sshd banner 为 `SSH-2.0-OpenSSH_10.2p1 Ubuntu-2ubuntu3.6` |
| F-16 | Windows `C:\Windows\System32\OpenSSH\ssh-keyscan.exe`（OpenSSH_for_Windows_9.5p2）对上述服务器报 `choose_kex: unsupported KEX method sntrup761x25519-sha512@openssh.com`，退出码 1 |
| F-17 | `C:\Program Files\Git\usr\bin\ssh-keyscan.exe` 对同一服务器成功返回 `[127.0.0.1]:2222 ssh-rsa` 与 `ssh-ed25519` 两条 host key，退出码 0 |
| F-18 | 提交 `5c5f06b5f` 引入 keyscan 候选列表（Git 版优先）并将输出 host 段规范化为 `[localhost]:2222` |
| F-19 | 验证输出：`[Run] ✓ known_hosts 已更新为新容器 host key (2222)`，known_hosts 写入 rsa/ed25519 两条 `[localhost]:2222` 记录 |
| F-20 | `podman machine list` 显示 `podman-machine-default` LAST UP 12 days ago；`wsl -l -v` 显示该发行版 Stopped |
| F-21 | `podman system connection list` 默认连接为 `ssh://user@127.0.0.1:63851/run/user/1000/podman/podman.sock` |
| F-22 | `inv load` 在 machine 停止时报 podman 原生英文错误 + `命令执行失败 (exit=125)`；`_load_via_cli` 内既有的"Podman machine 未运行"检测分支未被执行 |
| F-23 | `check_runtime_ready()` 已存在且提供 Windows 中文提示，但仅被 `run_container()` 调用，`load_image()` 未调用 |
| F-24 | 提交 `aadef02e8` 后实测：machine 停止环境下 `inv run`/`inv load` 均输出 `无法连接到 podman 服务。请确保 Podman machine 正在运行：podman machine start` |
| F-25 | 本批次沉淀模式 2 个（`win-powershell-compress-archive-gzip-mismatch`、`python-pathlib-tilde-no-expansion`）+ 复盘报告 1 篇（SSH host key 冲突） |
| F-26 | 用户最终可正常 `ssh -p 2222 devuser@localhost` 进入容器（提示符 `(main) devuser@<host>:~$`，conda base 已激活） |
| F-27 | 沙箱环境无法启动 podman machine（写 `C:\Users\<user>\.config\containers\podman\machine\wsl\` 被拒：Access is denied） |

## 核心洞察（I 阶段）

### I1：防御代码"写了"不等于"可达"——静默失效是本批次一半故障的共性形态

- **陈述**：本批次两次故障的直接原因都是防御逻辑存在但从未真正执行：`ensure_known_hosts` 因 `exists()` 恒 False 而静默 `return`；`_load_via_cli` 的 machine 检测分支被上游 `raise Exit` 提前截断。
- **证据**：F-08/F-09/F-10（路径失效侧）；F-22/F-23/F-24（分支不可达侧）。
- **反常识**：常见假设是"代码里写了检测/清理，功能就有保障"；实际上**存在性 ≠ 可达性 ≠ 有效性**，三层任一层断裂都等价于功能缺失，且表现与"没有该功能"完全一致。
- **行动**：凡"容错/清理/校验"类防御逻辑，落地时必须配套一次**可达性验证**（构造触发条件跑一遍），并把静默 `return` 改为带原因的 WARN 或显式跳过理由。

### I2：跨层级同因异相——"依赖状态先于目标资源生命周期"是本批次的第二类共性

- **陈述**：多处故障共享同一抽象结构：对目标资源（新容器、新 host key、运行时环境）的探测或写入，发生在其**生命周期边界之前**：keyscan 预写在旧容器删除前（抓到旧 key）、镜像校验/加载在无 runtime 时执行（注定失败）、`image_exists` 在就绪预检前调用（误报未找到镜像）。
- **证据**：F-11/F-13（host key 时序）；F-22/F-23（runtime 时序）；F-24（预检顺序调整后消除误报）。
- **反常识**：惯常按"调用顺序 = 业务顺序"排列代码（先查镜像、先写配置、先取状态），但**业务顺序 ≠ 依赖就绪顺序**；不把"依赖是否就绪"显式建模为门，顺序错误就会以"另一个看起来不相关的错误"暴露。
- **行动**：在含外部依赖的操作链前统一放置"就绪门"（本次以 `check_runtime_ready()` 前置到 `load_image`/`run` 首行实现），并在资源创建后再做状态回填（clean→run→refresh）。

### I3：环境异构下的"工具存在 ≠ 工具可用"——外部 CLI 需能力探测与候选回退

- **陈述**：同名工具在不同来源下能力不等价：System32 的 `ssh-keyscan`（OpenSSH_for_Windows_9.5p2）因 KEX 构建集不含 `sntrup761x25519-sha512` 而无法与容器内 OpenSSH 10.2p1 协商，Git 附带的 MSYS 版本则成功；同时 `keyscan localhost` 与 `python socket` 的双栈解析行为也不一致（::1 closed / 127.0.0.1 OPEN）。
- **证据**：F-14/F-15/F-16/F-17/F-18。
- **反常识**：`shutil.which()` 命中即认为可用，是把"可执行文件存在"误当"协议能力兼容"；版本协商失败的报错还常表现为"目标不可达"，误导排障方向。
- **行动**：对外部 CLI 采用**候选列表 + 结果判定**（本次：Git 版优先、系统版兜底，以"是否产出有效 key 行"而非 returncode 判定成功），并对地址族歧义显式探测后直连。

## 萃取（E 阶段）

- **新增模式**：[external-cli-version-drift-fallback](../../../patterns/code-patterns/external-cli-version-drift-fallback.md)（L1，外部 CLI 版本漂移的候选回退与能力探测）
- **复用既有模式**：`win-powershell-compress-archive-gzip-mismatch`（F-03/F-04）、`python-pathlib-tilde-no-expansion`（F-08~F-10）、`container-copy-context-whitelist` 与 `user-switch-cleanup-partitioning`（镜像瘦身批次）

## 行动项（A/C 阶段）

| # | 行动 | 验收标准 | 状态 |
|---|------|---------|------|
| A1 | 萃取模式 `external-cli-version-drift-fallback` 入库并更新索引 | 模式文件存在、G3 检查项齐备、索引含该 id | ✅ |
| A2 | 本里程碑复盘报告落盘 + toml 元数据 + milestone 索引更新 | 报告可被索引检索、frontmatter source 完整 | ✅ |
| A3 | 全链路端到端复核（inv load → inv run → ssh → /workspace 访问） | 用户实操通过，无 HAS CHANGED/无英文原生报错 | ✅（F-26） |
| A4 | 防御逻辑可达性回归（`clean_stale_host_keys`/`refresh_host_keys`/就绪预检） | 三处均在机实测触发一次、行为符合预期 | ✅（F-19/F-24） |

## 质量门记录

- **G1**：事实 27 条，均为可验证客观陈述（含提交号、命令输出、实测数值），无因果推断词
- **G2**：洞察 3 条，均含陈述/证据（引用 F 编号）/反常识/行动四元组
- **G3**：新模式含触发边界、5 步做法、4 反模式、检验标准与跨域迁移示例
- **G4**：行动项 4 项均可独立验证，A1/A2 以原子提交交付
