---
type: "Spec"
title: "npu-toolchain 远程后端：预检基线、七概念与连接决策"
frontmatter_spec_version: "v2.1.0-draft"
status: "implemented-draft（阶段 0–4 已实施，2026-11-03 实测）"
owner: "未指定"
part_of: "09-npu-toolchain-windows-host.md"
---

# npu-toolchain 远程后端：预检基线、七概念与连接决策

> **本篇职责**：记录预检事实基线（只读实测）、七概念分解（F→V→I→C）、架构图、连接形态对比（方案 A/B）与端口访问策略。
> **本篇不负责**：目标与非目标见[入口索引](09-npu-toolchain-windows-host.md)；A1–A9 验收与实测证据见[验收与实测](09-5-acceptance-and-evidence.md)；挂载与 UID 细节见[挂载与存储](09-2-mounts-uid-storage.md)；工具链供给见[工具链供给](09-3-toolchain-provisioning.md)；构建与验证命令见[构建与验证](09-4-build-and-verify.md)；风险与待确认项见[风险与待办](09-6-risks-todos-changelog.md)。

> **预检事实基线（2026-11-02/03 只读实测）**：

| 维度 | 实测值 | 判定 |
|---|---|---|
| 网络与登录 | `10.16.11.3:22` 可连；`ssh -o BatchMode=yes ai@10.16.11.3` 直接成功（密钥免密，无口令交互）；本机 OpenSSH 9.5p2 | ✅ 免密可用 |
| 远程系统 | Ubuntu 22.04.5 LTS，kernel 5.15.0-122-generic，x86_64，48 vCPU，125 GiB RAM，swap 23 GiB | ✅ 算力充足 |
| 远程身份 | `ai`，uid=1006，gid=1006，附加组 docker、smbshare；`/etc/subuid` 与 `/etc/subgid` 均为 `ai:493216:65536` | ✅ rootless 映射就绪 |
| Podman | 5.6.2（`/usr/local/bin/podman`），Rootless=**true**，CgroupManager=cgroupfs | ✅ |
| 存储驱动 | `GraphDriverName=overlay`（**非 vfs**），`GraphRoot=/home/ai/.local/share/containers/storage` → 实际落点 `/media/pc/data/ai/.agents/podman-storage/storage`（38 GB） | ✅ 无回退 |
| graphroot 文件系统 | `/dev/sda1`，**XFS**，15 TB，已用 99%，**可用 298 GB** | ✅ 本地盘，非 CIFS |
| runroot | `/run/user/1006/containers`（tmpfs） | ✅ |
| `/ai` 对应远程路径 | `/media/pc/data/ai`（同属 `/dev/sda1` XFS 本地盘；`/ai` 不存在） | ✅ 本机磁盘 |
| 两库可读 | `/media/pc/data/ai/notebook/libs/npu_tvm` 与 `/media/pc/data/ai/notebook/libs/npuusertools` 均存在，属主 `1001:codesrc`、权限 `drwxrwxrwx+`，`CMakeLists.txt` 与 `scripts/build.sh` 可读 | ✅ |
| 已有镜像 | `localhost/openkylin-npu-toolchain:3.0`（14 GB，2026-11-02 02:04 构建）；`localhost/openkylin:3.0`（13 GB）；`localhost/jupyter-podman-rootless:latest`（1.19 GB）等 | ✅ 免重建基线 |
| 已有容器 | `npu-toolchain` **Up 22 小时**，镜像同上，`Privileged=false`、`CgroupMode=host`、`UsernsMode=private`、`SecurityOpt=[label=disable]`；bind `/media/pc/data/ai → /workspace/ai`，volume `npu-build → /opt/build`；**未发布端口** | ✅ 可直接接管 |
| 容器内工具链 | Python **3.14.10**；`/opt/build/llvm20`=20.0.0、`/opt/build/llvm21`=21.0.0；`/opt/build/npu_tvm/libtvm.so` **已存在**；`/opt/build/npuusertools` 已存在；conda 通道已指向 USTC conda-forge | ⚠️ 见 §3.3（LLVM 22 待补、Python 包层未安装） |
| 容器内挂载可写 | `touch /workspace/ai/.temp/.probe` 成功 | ✅ |
| 宿主 Python 3.14 | `/media/pc/data/lxw/envs/anaconda3a/envs/py314/bin/python` = **3.14.6**，`Py_GIL_DISABLED=0`（**cp314 非 cp314t**），SOABI `cpython-314-x86_64-linux-gnu`；pip 26.1.2、setuptools 83.0.0、numpy 2.5.1、cmake 4.4.2、ninja 1.13.0；**wheel、cython、scikit-build-core、setuptools-scm 缺失** | ✅ 可用（需补装构建后端） |
| 宿主 LLVM | `py314/bin/llvm-config` = **22.1.2**（conda llvmdev，含 `libLLVM-22.so`、`include/llvm`、`lib/cmake/llvm`、clang 22.1.2、52 个 clang 工具）；base=`21.1.8`；系统 `/usr/lib/llvm-21`=21.0.0、`/usr/lib/llvm-20`=20.0.0；**无 `/usr/lib/llvm-22`** | ✅ LLVM 22 已具备 |
| 外网可达性 | USTC conda-forge repodata **200**；清华 PyPI **200**；`registry-1.docker.io` **不可达（000）** | ⚠️ 镜像只能本地构建/本地镜像，不能 pull |
| 防火墙与端口 | ufw **inactive**、firewalld **inactive**；既有容器已成功发布 `0.0.0.0:2223→22`、`0.0.0.0:8890→8888`、`0.0.0.0:2224→22`、`0.0.0.0:8892→8888`；Windows 侧 `Test-NetConnection` 对这 4 个端口及 22 全部 **True**；8888/8889 当前**空闲** | ✅ 端口发布可用 |
| 本机客户端 | Windows 已装 **podman 5.8.1**（`C:\Program Files\RedHat\Podman\podman.exe`），winget 1.29.380；已存在 4 条 `podman-machine-*` 连接（WSL 后端，默认项为 `podman-machine-default`），**尚无指向 10.16.11.3 的连接** | ✅ 方案 A 前置满足 |
| 已知瑕疵 | `podman system df` 报 `lstat /run/user/1006/libpod/tmp/infra-container: no such file`；`podman-compose` 未安装（`podman compose` 转调 docker-compose 插件） | ⚠️ 非阻塞 |

## 2. 七概念分解

> 场景判定：**问题解决 + 创新突破**（既有方案失效后的路径重构），执行链路 **F → V → I → C**。

### 2.F First Principles — 第一性原理

本质约束（本轮全部经实测确认，不再是推测）：

1. **构建算力与存储必须在有盘的地方**：v1.x 失败的根因不是挂载语义，而是 Windows 宿主没有可持续的本地 ext4 空间。远程 XFS 有 298 GB 可用、48 核、125 GB 内存，构成天然落点。
2. **overlay 需要 d_type / user xattr / hardlink / flock**：XFS 全部满足（实测 `GraphDriverName=overlay`），因此**不存在 vfs 回退**；v1.x 对 CIFS 的担忧在远程方案中整体消失。
3. **rootless 边界不可绕过**：容器内不得执行 `mount`，挂载必须在宿主侧完成；远程方案中宿主机直接以 `bind` 提供 `/media/pc/data/ai`，容器内只做 bind mount，无需任何 CIFS 凭据。
4. **UID 一致性是写入前提**：宿主 uid=1006；容器 `--userns=keep-id` 使容器内 UID=1006，与源码目录属主（1001:codesrc，权限 777）无冲突。
5. **LLVM 22 已在允许区间内且有实物**：宿主 py314 环境内含 22.1.2 全套（shared libLLVM-22.so、headers、cmake config、clang/lld）。
6. **Python ABI 风险已被排除**：`Py_GIL_DISABLED=0`、SOABI `cpython-314-x86_64-linux-gnu`，即 **cp314（GIL 版）**，与容器内 3.14.10 同系列；不存在 cp314t 的 C 扩展 ABI 风险。
7. **镜像来源受限**：`registry-1.docker.io` 不可达，只能使用远程本地镜像或本地构建，conda/PyPI 走国内镜像可达。
8. **端口发布可用**：防火墙 inactive，既有容器已成功发布并可从 Windows 访问。

### 2.V Adversarial Review — 对抗审查

| 视角 | 攻击点 | 防御 |
|------|--------|------|
| 魔鬼代言人 | SSH 断线会让 `podman --remote` 命令失败，长构建中断 | 长构建一律在远程 `tmux`/`nohup` 中运行（方案 B 形态），客户端只做轮询；`podman --remote` 只用于短命令 |
| 新人视角 | 为什么不直接把宿主 py314 环境挂进容器，省事？ | 路径耦合：conda 环境的 `llvm-config --prefix` 指向宿主机路径，容器内该路径不存在，CMake 会拿到失效的 `LLVMConfig.cmake`；且跨发行版 glibc 差异不可控。见 §3.3 |
| 老板视角 | XFS 已用 99%，只剩 298 GB，够不够？ | 单次完整构建预估 15–25 GB（镜像层 + 构建卷）；298 GB 余量足够多轮；A9 设 50 GB 硬门禁 |
| 未来视角 | 若以后要迁回 Windows 本地或换机器，方案是否绑定？ | 构建链完全在远程标准路径与 conda-forge，迁移只需重跑 `all-in-one.sh`；Windows 侧仅是客户端，无状态 |
| 供应链 | Docker Hub 不通，镜像怎么来？ | 远程已有 `openkylin-npu-toolchain:3.0` 等本地镜像；新镜像用本地 Containerfile 构建，不依赖 pull |
| 一致性 | 容器内 LLVM 20/21 与宿主 22 混用会不会误判？ | A3 明确要求 `llvm-config --version` 实测为 22.x，并在 CMake 中显式 `-DUSE_LLVM=<绝对路径>`，禁止 PATH 隐式解析 |

### 2.I Insight — 洞察

**I1 复用而非重建**：远程已有 14 GB 的 `openkylin-npu-toolchain:3.0` 镜像与一个 Up 22 小时的容器，`/opt/build/npu_tvm/libtvm.so` 已存在。新方案的第一个动作是**接管**，不是「从零构建」。

**I2 唯一真实缺口是「Python 包层」与「LLVM 22 入容器」**：容器内 `import tvm` 与 `import xmnn` 均失败（`ModuleNotFoundError`），说明 C++ 侧已通、Python 侧未装。这决定了下一步工作量很小。

**I3 端口策略应默认关闭**：npu-toolchain 是常驻构建环境，按需 `podman exec` 进入即可；Jupyter 只在需要时以独立端口发布，避免占用 8888 与既有服务冲突。

**I4 存储位置已是最优**：graphroot 通过软链指向 `/media/pc/data/ai/.agents/podman-storage/storage`，与源码同盘，bind mount 与镜像层共享同一 XFS，无跨盘拷贝。

**I5 构建后端的补装成本极低**：宿主缺 wheel / cython / scikit-build-core / setuptools-scm，但 PyPI 镜像可达，`pip install` 即可；容器内缺的是同一类包。

### 2.C Atomic Commit — 原子化交付

| 步骤 | 产物 | 判定 |
|---|---|---|
| C1 | `podman system connection add remote-ai` | `podman --remote info` 通过 |
| C2 | 容器内 LLVM 22 供给（conda 安装或卷内复制） | A3 PASS |
| C3 | 容器内 npu_tvm Python 绑定安装 | A4 PASS |
| C4 | 容器内 npuusertools 构建与安装 | A5 PASS |
| C5 | 端口与 Jupyter 按需发布 | A7 PASS |
| C6 | 文档与验证脚本更新 | `verify.sh` 全绿 |

## 3.1 架构图

```
Windows 11（仅客户端，无发行版、无本地 podman 存储参与）
  ├─ ssh.exe  (OpenSSH 9.5p2)  ── 密钥免密（BatchMode 实测 OK）
  └─ podman.exe 5.8.1（remote client）
        │  ssh://ai@10.16.11.3:22/run/user/1006/podman/podman.sock
        ▼
10.16.11.3  Ubuntu 22.04.5 / kernel 5.15 / 48 vCPU / 125 GiB
  ├─ sshd :22
  ├─ rootless podman 5.6.2（cgroupfs，subuid/subgid ai:493216:65536）
  │    ├─ graphroot → /media/pc/data/ai/.agents/podman-storage/storage   [XFS /dev/sda1, 298 GB avail]
  │    └─ runroot   → /run/user/1006/containers                            [tmpfs]
  ├─ 源码与数据：/media/pc/data/ai  （XFS 本地盘，非 CIFS、非 drvfs）
  ├─ LLVM 22.1.2：/media/pc/data/lxw/envs/anaconda3a/envs/py314（conda llvmdev）
  ├─ Python 3.14.6：同目录 py314/bin/python（cp314，非 cp314t）
  └─ 容器 npu-toolchain  (localhost/openkylin-npu-toolchain:3.0, 14 GB)
        ├─ bind  /media/pc/data/ai            → /workspace/ai   (rw)
        ├─ volume npu-build                   → /opt/build      (rw)
        │     ├─ llvm20 (20.0.0) / llvm21 (21.0.0) / llvm22 (22.1.8，已补)
        │     ├─ npu_tvm/（含 libtvm.so）
        │     └─ npuusertools/
        └─ Python 3.14.10 + conda（通道 = USTC conda-forge）
```

## 4. 连接形态对比与推荐

| 维度 | 方案 A：Windows `podman-remote` | 方案 B：直接 SSH 远程 shell |
|---|---|---|
| 前置 | Windows 已装 podman 5.8.1；远程 socket 已存在（`/run/user/1006/podman/podman.sock`） | 仅需 ssh（已免密） |
| 命令形态 | Windows 侧 `podman --remote ps/logs/inspect`，语法与本地一致 | 远程 `podman` / `podman compose` / `bash scripts/*.sh` |
| 文件传输 | 仍需 `scp`/`rsync`；`podman cp` 走远程 | `scp`/`rsync` 或直接编辑共享盘（`/media/pc/data/ai` 即 Windows `\\10.16.11.3\ai`） |
| 端口访问 | 由远程发布端口决定，与 A 无差异 | 同上 |
| IDE/编辑器协作 | VS Code Remote-SSH 或本地编辑 SMB 共享；`podman --remote` 不参与 | VS Code Remote-SSH 原生支持，终端/调试一致 |
| 凭据管理 | 需要单独维护 connection 的 Identity 文件（复用 `~/.ssh/id_ed25519`）；不涉及口令 | 复用既有 ssh config，零新增凭据 |
| 长任务可靠性 | 受 SSH 会话影响；不适合长构建 | `tmux`/`nohup` 稳定承载长构建 |
| 可脚本化/CI | 好（Windows 侧脚本可直接驱动） | 好（远程脚本天然可复用，`all-in-one.sh` 已存在） |
| 故障域 | 多一层客户端 → socket 映射，排障面更大 | 最少环节，排障直接 |

**推荐：A 为主、B 为必备并行路径。**

- 日常短命令（查看状态、`exec` 探针、日志）走 **A**，在 Windows 上直接可读，不必登录远程 shell。
- **所有长构建与镜像构建走 B**（`tmux` 内执行 `scripts/all-in-one.sh`），避免 SSH 断线中断。
- 理由：A 提供与本地一致的 CLI 体验且前置已满足；B 是长任务与排障的最低故障面路径。二者共用同一套密钥与同一 socket，不产生凭据分裂。

**A 的落地命令（已执行，2026-11-03）**：

```powershell
podman system connection add remote-ai --identity $env:USERPROFILE\.ssh\id_ed25519 ssh://ai@10.16.11.3:22/run/user/1006/podman/podman.sock
podman --remote --connection remote-ai info
```

> 注意：Windows 现有默认连接为 `podman-machine-default`（WSL 后端）。切换默认项会影响既有 WSL 工作流，故**未切换默认**，一律以 `--connection remote-ai` 显式指定。

### 4.1 `--connection` 缺陷：根因与修复（2026-11-03 实测）

| 项 | 实测 |
|---|---|
| 现象 | `podman --connection remote-ai info` 报 `dial tcp :22: connectex: ... actively refused`；`--log-level=debug` 只打印 `ssh_config alias found: 10.16.11.3` 与 `Hostname: 10.16.11.3`，随后主机名丢失 |
| 隔离 | ① 仅改端口到 2200 → `dial tcp :2200`，说明端口被解析、主机为空；② 换到 `10.16.11.4`（`~/.ssh/config` 无对应 `Host` 块）→ 主机保留并到达对端 SSH（认证失败属预期）；③ 配置临时只保留 `Host *` → 连接成功（`5.6.2`）；④ 任意精确实体 `Host` 块（含最小三行、含新增别名）→ 主机再次为空 |
| 根因 | podman 5.8.1 Windows 客户端在 `--connection`/`CONTAINER_HOST` 路径解析 ssh_config：只要存在匹配目标的 `Host` 块，就把目标主机解析为空串；`--url` 与「无匹配块」均不触发 |
| 修复 | 将 `~/.ssh/config` 中 `Host 10.16.11.3` 改为 `Match host 10.16.11.3`（块内指令不变）：podman 的解析器不识别 `Match`，主机得以保留；OpenSSH 仍按 `Match` 生效 |
| 验证 | `ssh -G 10.16.11.3` → `user ai` / `hostname 10.16.11.3` / `forwardx11 no`；`ssh -o BatchMode=yes ai@10.16.11.3 whoami` → `ai`；`podman --remote --connection remote-ai info` → `5.6.2` 且 `rootless`；`podman --remote --connection remote-ai ps -a` 正常列出 `npu-toolchain` 等容器 |
| 回滚 | 原配置已备份为 `~/.ssh/config.bak-20261103-split`（保留未删） |

## 3.4 端口与访问策略

| 场景 | 做法 | 依据 |
|---|---|---|
| 常驻构建环境 | **不发布端口**（现状即如此），一律 `podman exec` 进入 | 减少暴露面；与服务器侧一致 |
| 需要 Jupyter | 显式发布 `0.0.0.0:8890→8888`（或 8891/8892 中空闲者），并先确认端口未被占用 | 实测 8888/8889 空闲；既有服务占用 8890、8892（`native-dev` 与 `agent-monetize-dev`） |
| Windows 访问 | 直连 `http://10.16.11.3:<发布端口>`；已验证同网段端口可达 | 防火墙 inactive，既有发布端口 Windows 侧全部可达 |
| 反向隧道（备用） | 若将来网络策略收紧，用 `ssh -L 8888:127.0.0.1:8888 ai@10.16.11.3` | 不依赖远程防火墙改动 |

> **注意**：8890、8892 已被既有容器占用，**不得直接复用**；新发布端口需先 `ss -lnt` 与 Windows `Test-NetConnection` 双重确认。

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [挂载与存储](09-2-mounts-uid-storage.md)
- [工具链供给](09-3-toolchain-provisioning.md)
- [验收与实测证据](09-5-acceptance-and-evidence.md)