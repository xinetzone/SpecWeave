---
type: "Spec"
title: "npu-toolchain v1.x「WSL 本地后端」方案归档（已废弃）"
frontmatter_spec_version: "v2.1.0-draft"
status: "DEPRECATED"
owner: "未指定"
part_of: "09-npu-toolchain-windows-host.md"
---

# npu-toolchain v1.x「WSL 本地后端」方案归档（已废弃）

> **本篇职责**：逐字保留 v1.x「Windows 宿主 + WSL + OpenKylin 发行版 + 本地 rootless Podman」方案原文，供决策追溯。
> **本篇不负责**：当前有效规格；现行结论、命令与验收一律以[入口索引](09-npu-toolchain-windows-host.md)及其分篇为准。

> **⚠ 废弃声明（DEPRECATED，2026-11-03）**：本篇所述方案已于 2026-11-03 废弃，**仅作历史参考，不得作为实施依据**。废弃原因：
> 1. **容量不可持续**：D: 盘总容量 112 GB，导入 OpenKylin 镜像与 podman graphroot 后可用最低降至 8.82 GB；VHDX 只增不减，无法满足长期构建需求。
> 2. **导入被系统服务独占锁阻断**：`vmcompute` / `wslservice` 以 SYSTEM 身份持有 tar 文件独占句柄，非管理员会话无法释放；多次尝试分别以 `E_UNEXPECTED`、`E_ILLEGAL_STATE_CHANGE` 失败。
> 3. **收益已被远程方案完全覆盖**：目标机器本身即 `10.16.11.3`，本地 WSL 方案属于「在客户端重建一遍服务器环境」，投入产出不成比例。
>
> 当前有效规格见 [09 入口索引](09-npu-toolchain-windows-host.md)。

## 附录 D：v1.x「WSL 本地后端」方案归档（**已废弃**，原文保留）

> **废弃状态**：`DEPRECATED`。本附录内容**不再作为实施依据**，仅作历史留存与决策追溯。
>
> **废弃原因**：
> 1. **容量不可持续**：D: 盘总容量 112 GB，导入 OpenKylin 镜像与 podman graphroot 后可用最低降至 8.82 GB；VHDX 只增不减，无法满足长期构建需求。
> 2. **导入被系统服务独占锁阻断**：`vmcompute` / `wslservice` 以 SYSTEM 身份持有 tar 文件独占句柄，非管理员会话无法释放；多次尝试分别以 `E_UNEXPECTED`、`E_ILLEGAL_STATE_CHANGE` 失败，管理员路径亦无法在自动化会话内完成 UAC 交互。
> 3. **收益已被远程方案完全覆盖**：目标机器本身即 `10.16.11.3`，本地 WSL 方案属于「在客户端重建一遍服务器环境」，投入产出不成比例。
>
> **仍具参考价值的 v1.x 结论（迁移到 v2 继续沿用）**：
> - LLVM 版本区间结论（下限 6.0、`static_assert <= 229`、22.x 合规）——用于 v2 的 A3。
> - 组级 G3 rootless 三必需与「禁 `--privileged`」契约——v2 继续沿用。
> - 分层落盘思想（存储本地、源码/构建外置）——v2 中由「XFS 本地盘天然同盘」自动满足。
> - v1.x 中关于 CIFS/overlay 的实测与推理结论，在 v2 中**不再适用**（无 CIFS 参与），仅作背景。
---

### 归档正文（v1.x 原样保留，2026-11-02 版本）

# WSL + OpenKylin + rootless Podman 宿主侧 npu-toolchain 规格

> **文档定位**：将已在服务器侧（`ai@10.16.11.3`，宿主路径 `/media/pc/data/ai`）验证通过的 `npu-toolchain` 变体，迁移到 **Windows 11 宿主 + WSL + OpenKylin 发行版 + rootless Podman** 场景，跑通 `/workspace/ai/notebook/libs/npu_tvm` 与 `npuusertools`。本轮为**只读调研 + 规格设计**，不涉及镜像构建或长时间运行。
>
> **硬约束（新增，2026-11-02）**：
> - WSL 发行版 VHDX 落盘在 **D: 盘**（本地固定 NTFS）—— 预检确认 S: 盘是网络映射盘（DriveType=4，`ProviderName=\\10.16.11.3\ai`），WSL 禁止在网络盘上创建 ext4.vhdx
> - **容量事实基线（2026-11-02 预检实测）**：`D:` DriveType=3 本地固定 NTFS，可用 **34.2 GB**（写入测试通过，唯一合格候选）；`C:` 剩余 **21.5 GB**（低于 25 GB 门槛，不作为落盘目标）；`S:` DriveType=4 网络映射盘，总容量 14900 GB、可用 297.7 GB，但 **不可承载 ext4.vhdx**
> - **开发活动尽量走 CIFS 挂载省 D: 盘空间**，podman 存储（graphroot/runroot）因 overlay 驱动硬约束必须在 ext4.vhdx（D: 盘），通过分层落盘 + 主动清理措施控制 D: 盘不膨胀
> - 服务器侧变体：`apps/openkylin-dev-container/variants/npu-toolchain/`（Containerfile + compose.yaml + all-in-one.sh + verify.sh，已在 ai 服务器实测通过，见该目录 README）
> - 容器运行契约（组级 G3）：`apps/containers/AGENTS.md` — rootless 三必需 + 禁 `--privileged`
> - devcontainer-base 变体体系：`apps/docker-images/devcontainer-base/variants/`（conda-llvm 等）
> - jupyter-podman-rootless：`apps/containers/jupyter-podman-rootless/`（rootless + free-threading + invoke 三层后端）

---

## 1. 目标、非目标与验收标准

### 1.1 目标（In-Scope）

1. 在 **Windows 11 宿主 + WSL + OpenKylin 发行版**中，将共享目录 `\\10.16.11.3\ai` 以**三层挂载**（Windows UNC → WSL 内挂载点 → 容器 bind mount）形式提供给 rootless Podman 容器。
2. 容器内能够 **读写** `notebook/libs/npu_tvm` 与 `notebook/libs/npuusertools` 源码目录，属主与容器运行用户匹配（`userns=keep-id` 或等价方案）。
3. 容器内具备 **Python ≥ 3.14**、**CMake ≥ 3.18**、**Ninja ≥ 1.10**、**GCC/G++** 的原生构建工具链。
4. **LLVM ≥ 21**（21 或 22 均可）工具链可用于 TVM 编译（`llvm-config --version` 输出 21.x 或 22.x）。
5. **npu_tvm 构建通过**：`cmake -G Ninja -S ... -B ... -DUSE_CODEGENC=ON -DUSE_LLVM=/opt/build/llvm${LLVM_MAJOR}/bin/llvm-config` + `ninja tvm`（`LLVM_MAJOR`=21 或 22，对应实际供给版本），产物 `libtvm.so` 存在且可被 `import tvm` 加载。
6. **npuusertools 构建与导入通过**：`BUILD_DIR=/opt/build/npuusertools bash scripts/build.sh` + `pip install --user -e .` + `import xmnn` 成功。
7. **容器运行时满足 rootless 三必需**：`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`，无 `--privileged`。
8. **分层落盘策略**：podman 存储（overlay graphroot/runroot）留在 WSL ext4.vhdx（D: 盘），源码树、构建目录、conda/pip 缓存、模型与数据集全部外置到 CIFS 挂载。
9. **D: 盘防膨胀**：D: 盘剩余空间 ≥ 20GB（阈值）；`podman system prune` 主动清理 + WSL VHDX 定期压缩。

### 1.2 非目标（Out-of-Scope）

- **不运行实际 NPU 硬件**：本规格仅验证编译、导入、工具链就绪，不进行板端推理或精度验证（需连接 NPU 板）。
- **不生产构建时长的端到端指标**：本轮为只读调研，镜像构建耗时、`ninja tvm` 编译耗时等数据不在本规格产出范围。
- **不支持 free-threading Python (cp314t)**：目标工具链来自 conda-forge，以标准 GIL Python 3.14 为基准，与 `devcontainer-base` / `jupyter-podman-rootless` 的 cp314t 路线有分叉——这是本方案的已知取舍。
- **不重建 npu-toolchain 变体逻辑**：核心构建链、环境变量设计、LLVM 21/22 供给策略均沿用服务器侧 `all-in-one.sh`（S5/S6/S7），仅做宿主侧适配。
- **不启用容器内服务**：npu-toolchain 容器无 sshd、无 supervisord、不发布任何端口，仅作为常驻构建环境通过 `podman exec` 进入（与服务器侧一致）。

### 1.3 可测量的验收标准（Acceptance Criteria）

| # | 标准 | 可观测证据 | 失败判定 |
|---|------|-----------|---------|
| A1 | 容器内可读/写指定子目录 | `podman exec $CTR stat -c '%a %u:%g' /workspace/ai/notebook/libs/npu_tvm/CMakeLists.txt` 返回 `644 <host_uid>:<host_gid>`；`podman exec $CTR touch /workspace/ai/.temp/npu-toolchain/.probe` 后宿主侧可见该文件 | 属主不匹配或文件不可写 |
| A2 | Python ≥ 3.14 + CMake ≥ 3.18 + Ninja ≥ 1.10 | `podman exec $CTR python -c 'import sys; print("%d.%d" % sys.version_info[:2])'` + `cmake --version` + `ninja --version` 三者均通过版本门禁 | 任一低于版本门槛 |
| A3 | LLVM ≥ 21 可用 | `podman exec $CTR /opt/build/llvm${LLVM_MAJOR}/bin/llvm-config --version` 输出 `21.x` 或 `22.x`（`LLVM_MAJOR`=21 或 22，对应实际供给版本） | 输出 < 21 或命令不存在 |
| A4 | npu_tvm 构建通过 | `ninja -C /opt/build/npu_tvm tvm` exit 0 + `libtvm.so` 存在 + `import tvm` 成功（`Target("llvm")` 与 `Target("ccompiler")` 均可解析） | `ninja` exit ≠ 0 或 import 失败 |
| A5 | npuusertools 构建与导入通过 | `build.sh` exit 0 + `pip install --user -e .` exit 0 + `import xmnn` 成功 | 任一步骤 exit ≠ 0 |
| A6 | rootless 运行契约 | `podman inspect` 显示 `Privileged=false` + `CgroupMode=host`；容器启动命令包含 `--device /dev/fuse` + `--security-opt label=disable` | 出现 `--privileged` 或缺少三必需 |
| A7 | 容器不发布端口 | `podman port $CTR` 输出为空 | 输出非空 |
| A8 | 分层落盘：可外置目录在 CIFS | `podman exec $CTR python -c 'import sys; print(sys.prefix)'` 非 CIFS 路径 OK；`podman exec $CTR ls /workspace/ai/notebook/libs/npu_tvm/CMakeLists.txt` 可读；podman `graphDriverName=overlay` 且 graphroot 在 WSL home（非 CIFS） | graphroot 被放在 CIFS 上导致容器启动失败 |
| A9 | D: 盘剩余 ≥ 20GB | `(Get-PSDrive -Name D).Free` ≥ 21474836480（20GB） | 低于阈值，需执行 VHDX 压缩 |

---

## 2. 七概念分解

> 本任务属于**创新突破**场景（新宿主环境适配既有方案），执行链路 **F → V → I → C**。

### 2.F First Principles — 第一性原理

**核心矛盾链**：
```
Windows 共享目录 (\\10.16.11.3\ai)
    ↓ 不存在于 WSL 的本地文件系统
    ↓ 必须经挂载才能被 WSL 进程看到
    ↓ 挂载后文件权限属主映射可能错乱
    ↓ rootless Podman 不允许特权挂载
    ↓ 解决方案：WSL 侧先挂载（可 root），容器内只 bind mount（非特权）
    ↓ 容器内运行用户 UID 必须与 WSL 挂载点的属主匹配
    ↓ 解决方案：--userns=keep-id（容器内 UID = WSL 宿主 UID）
```

**本质约束（不可绕过的底层事实）**：
1. **Windows 文件系统 POSIX 语义退化**：drvfs（9p）权限恒映射为 777；CIFS 可配置 uid/gid 但需 mount.cifs 在 WSL 侧先完成。两者都不支持硬链接。
2. **rootless Podman 安全边界**：容器进程以 unprivileged 用户运行，无法执行 `mount.cifs`（需要 `CAP_SYS_ADMIN`）。**CIFS/SMB 挂载必须在 WSL 宿主侧先完成**，容器内只做 bind mount。
3. **LLVM ≥ 21 满足 TVM 最低门槛，21 或 22 均可**（源码只读调研，2026-11-02）：
   - `cmake/utils/FindLLVM.cmake:229` 仅校验 `TVM_LLVM_VERSION LESS 40`，**无上限检查**
   - `cmake/modules/LLVM.cmake:32` 校验 `LESS 60`，有效最低 LLVM 为 6.0
   - `src/target/llvm/llvm_compat.h:157-166` — `getOrInsertDeclaration` 门控 `TVM_LLVM_VERSION >= 200`（源码注释明确 "LLVM 20.0+ 引入"，此前规格误写为 21）
   - `src/target/llvm/llvm_module.cc:518` — linker 签名简化门控 `TVM_LLVM_VERSION >= 210`（LLVM 21+ 走简化 ObjectLayer 构造函数，20 走 `#elif >= 130` 分支）
   - 不存在任何 `TVM_LLVM_VERSION >= 220` 特判，LLVM 22 完全复用 21+ 代码路径
   - **结论**：LLVM 21 或 22 均可，两者均满足所有版本门控；服务器侧已验证 LLVM 21 链路端到端通过
4. **LLVM 获取路径不唯一**：WSL 宿主有两条通路——(a) 从服务器 `scp /usr/lib/llvm-21` 到 WSL 宿主（~300MB 含 headers/cmake）；(b) conda-forge `llvmdev` 从 USTC 镜像拉取（linux-64 22.1.7 体积约 59MB，21.1.4 约 58MB，均显著小于此前规格误写的 800MB+）。两条通路均需网络可达性前置验证。
5. **`userns=keep-id` 的语义**：podman 不启用嵌套 user namespace（保持宿主 UID），容器内进程直接以宿主 UID 运行。这意味着如果 WSL 挂载点的文件属主是 WSL 宿主 UID，容器内进程就能正常读写。
6. **Overlay 存储驱动硬约束（新增，2026-11-02）**：podman rootless 默认使用 `overlay` 驱动（搭配 `fuse-overlayfs`），底层文件系统必须支持 **d_type、user xattr (security.*)、hardlink、flock**。CIFS/SMB 3.0 协议层不返回 d_type，不支持 user xattr，不支持 hardlink → **overlay 绝对不能跑在 CIFS 上**（已在 Windows + WSL + SMB 场景实测失败，podman 会自动回退 vfs 驱动）。仅 vfs 驱动能跑在 CIFS 上，但代价极高（空间膨胀 N 倍 + 容器启动慢 + 运行时写时复制全量复制），**不推荐**。
7. **WSL VHDX 位置约束（新增，2026-11-02）**：Windows 10/11 上 `wsl --import` 的 rootfs 目标路径必须在本地固定磁盘（DriveType=3），网络映射盘（DriveType=4）不允许 ext4.vhdx 存放——**预检确认 S: 盘是 DriveType=4 网络盘，发行版落 D: 盘是唯一选择**。
8. **VHDX 不自动缩小（新增，2026-11-02）**：WSL 删除文件后，ext4 内部空间被释放但 Windows 侧的 ext4.vhdx 文件**不会自动缩小**。每次构建/镜像 pull 都会使 VHDX 只增不减，需要定期执行 VHDX 压缩。

**为什么不选 Ubuntu 26.04 方案（devcontainer-base / jupyter-podman-rootless）**？
- Ubuntu 有完整 apt 源，理论上可以直接 `apt install llvm-21`。但当前网络环境下 openKylin 官方源都不可达，Ubuntu 源大概率也不可达（同一防火墙白名单）。
- devcontainer-base 需要 `--privileged` 跑 Docker DinD，违反 G3 组级契约。
- jupyter-podman-rootless 是专门为 rootless 设计的，但其 Python 是 **free-threading cp314t**，对 npu_tvm/npuusertools 有 C 扩展兼容性风险——用户未指定 free-threading 需求，没必要引入额外不确定性。
- **服务器侧已验证 openkylin:3.0 + conda-forge 路线可用**，迁移成本最低。

### 2.V Adversarial Review — 对抗审查

**4 视角证伪**：

| 视角 | 攻击点 | 防御 |
|------|--------|------|
| **魔鬼代言人** | CIFS 挂载不稳——Windows 机器重启、WSL 会话断开后挂载失效，容器 bind mount 变成死链 | `run.sh up` 在起容器前必须做**挂载探针**（`ls /mnt/srv/ai/notebook/libs/npu_tvm/CMakeLists.txt` 存在性检查），缺失即 FAIL；已在服务器侧 `verify.sh` 有同等机制 |
| **新人视角** | 为什么不直接用 WSL 的 `\\wsl$\` 路径？为什么不在容器里用 `smbclient` 挂载？ | `\\wsl$\` 是 Windows 访问 WSL 的反向通道（WSL → Windows 不能用它）；容器内 `mount.cifs` 需要 `CAP_SYS_ADMIN`，rootless Podman 不提供——这就是三层挂载设计的来源 |
| **老板视角** | 服务器侧的 `/usr/lib/llvm-21` 在 Windows 宿主上不存在——LLVM 怎么来？ | **阻塞级待确认项**：LLVM ≥ 21（21 或 22 均可）必须在 WSL 发行版宿主上就绪。可能路径：(a) 从服务器 `scp /usr/lib/llvm-21` 到 WSL 宿主 + tar 分发到容器；(b) **WSL 宿主 conda-forge 装 llvmdev**（USTC 镜像，linux-64 22.1.7 仅 ~59MB，21.1.4 ~58MB，远小于此前误写的 800MB；含 `llvm-config`、headers、cmake 文件）——这是最简单直接的路径，需先验证 WSL 宿主 conda-forge 镜像可达性；(c) 容器 bind mount 宿主 LLVM 路径（但 WSL 宿主可能没有） |
| **未来视角** | 如果 WSL 的 OpenKylin 发行版 apt 源能通了，openKylin 包管理比 conda-forge 更适合装系统工具链——方案能否平滑切换？ | Containerfile 里 Miniforge + conda-forge 是一个独立 Layer，可以在后续迭代中替换为 `apt install cmake ninja` 等，不影响上层 S6/S7 构建逻辑；**但本轮不**做此重构，按服务器侧经过验证的 conda-forge 方案推进 |

**V 门通过条件**：所有攻击点要么有已知防御（挂载探针、all-in-one.sh 幂等），要么已列为阻塞级待确认项进入规格 §9。

### 2.I Insight — 洞察

从服务器侧已验证方案（`ai@10.16.11.3`，宿主 uid=1006，挂载路径 `/media/pc/data/ai`）迁移到 Windows/WSL 宿主，洞察如下：

**I1 宿主 UID 与挂载属主匹配是核心**
- 服务器侧：宿主 uid=1006 → `--userns=keep-id` → 容器内 uid=1006 → CIFS 挂载点属主也必须是 1006
- Windows/WSL 侧：宿主 UID 可能不同（OpenKylin 发行版默认用户 UID 是多少？WSL 内 `/etc/subuid` 是否配置？）——**这是 Windows 侧必须先验证的前置条件**

**I2 Windows UNC → WSL 挂载的两条通道**
- **通道 A（推荐）**：`mount.cifs //10.16.11.3/ai /mnt/srv/ai -o user=<user>,pass=<pass>,vers=3.0,iocharset=utf8,file_mode=0644,dir_mode=0755,uid=<host_uid>,gid=<host_gid,forceuid,forcegid`。优点：属主可预测，不依赖 SMB 协议协商。缺点：需要凭据（**用 `.env` 或环境变量，禁止硬编码**），WSL 发行版内可能没有 `cifs-utils` 包（OpenKylin 源可达性待确认）。
- **通道 B（仅本地固定卷，不能覆盖共享目录）**：WSL 的 `[automount]` **只自动挂载 DriveType=3 的本地固定卷**（如 `C:` → `/mnt/c/`、`D:` → `/mnt/d/`），**网络映射盘（DriveType=4，如 `S:` 映射到 `\\10.16.11.3\ai`）不会被自动挂载**，`/mnt/s/` 不存在。优点：本地固定卷零配置、自动可用。缺点：权限恒映射为 777（`stat` 显示属主 99999/99999），与 `userns=keep-id` 的容器属主不匹配；**且该通道根本无法覆盖本任务的共享目录**，显式 `mount -t drvfs //10.16.11.3/ai` 属凭据敏感且语义更弱，不列为方案。

**结论**：通道 A 是本任务唯一可行路径（通道 B 只能访问本地卷，无法触达 `\\10.16.11.3\ai`）。

**I3 容器内不需要做 CIFS 挂载**
- rootless Podman 不允许容器内执行 `mount.cifs`（需要特权）。这不是"容器里挂载更干净"的问题，是**权限模型不允许**。解决方案是 WSL 宿主侧先挂载，容器内只做 bind mount。

**I4 LLVM ≥ 21 在 Windows/WSL 宿主的供给策略变化**
- 服务器侧：`/usr/lib/llvm-21` 已存在，用 `podman cp` 复制 + `tar` 分发到容器命名卷 `/opt/build/llvm21/`
- Windows/WSL 侧：WSL 宿主可能**没有** LLVM。获取路径（优先级从高到低）：
  1. **WSL 宿主 conda-forge llvmdev**（~59MB，USTC 镜像）——安装后宿主就有完整 LLVM，再按服务器侧同样策略 `podman cp` + tar 分发进容器
  2. **从服务器 `scp` `/usr/lib/llvm-21`** 到 WSL 宿主（~300MB，含 headers/lib/cmake）
  3. 以上均不可行时才考虑容器 bind mount 宿主路径
- 源码无上限检查，**21 或 22 均可**（证据见 §2.F 约束 3）

**I5 两库构建链直接复用服务器侧**
- npu_tvm：`cmake -G Ninja -S /workspace/ai/notebook/libs/npu_tvm -B /opt/build/npu_tvm -DUSE_CODEGENC=ON -DUSE_LLVM=/opt/build/llvm${LLVM_MAJOR}/bin/llvm-config` + `ninja tvm`
- npuusertools：`BUILD_DIR=/opt/build/npuusertools bash scripts/build.sh` + `pip install --user -e .`
- 环境变量：`PYTHONPATH` / `TVM_LIBRARY_PATH` / `LD_LIBRARY_PATH` / `PYTHONUSERBASE` 设计**完全复用服务器侧**，见 all-in-one.sh S6/S7

**I6 Overlay vs CIFS 硬约束 → 分层落盘是唯一正确路径（新增）**
- **事实链**：podman `overlay` 驱动（rootless + fuse-overlayfs 或内核）→ 要求底层文件系统支持 d_type/user xattr/hardlink → CIFS/SMB 不支持这些特性 → overlay 无法跑在 CIFS 上 → **podman graphroot/runroot 必须留在 WSL ext4.vhdx（D: 盘）**
- **fuse-overlayfs 在 CIFS 上？** fuse-overlayfs 比内核 overlay 宽松，但仍要求底层支持 hardlink 和 xattr——CIFS 缺失这些 → fuse-overlayfs 也会失败。仅 vfs 驱动能跑在 CIFS 上，但代价极高（空间膨胀 N 倍 + 容器启动慢 + 运行时写时复制全量复制），**不推荐**
- **结论**：分层落盘是唯一正确路径——D: 盘承担 WSL 发行版 VHDX + podman overlay graphroot/runroot；所有可外置的东西全部走 CIFS
- **风险**：D: 盘 34.2GB 可用空间是有限的；每次构建/镜像 pull 都会增加 VHDX 占用；VHDX 不会自动缩小（删除文件后 ext4 里只是空间释放，VHDX 文件本身不缩小），需要 `wsl --shutdown` + 宿主侧 VHDX 压缩

### 2.C Atomic Commit — 原子化交付

按 G4 行动门原则（单一职责、可独立验证、有验收标准），分 4 个阶段交付：

**阶段 0：只读预检（本轮）**
- 产出：本规格文档
- 验收：规格经人类评审通过

**阶段 1：WSL 宿主侧准备**
- 新增 WSL 只读预检脚本：`bash scripts/preflight-wsl.sh`
- 检查项：OpenKylin 发行版版本、rootless Podman 状态（`podman info` rootless=true）、`/etc/subuid`/`/etc/subgid`、宿主 UID、CIFS 可达性（`mount.cifs` 或 drvfs 检查）、LLVM ≥ 21 存在性
- 验收：退出码 0 + 每项 PASS

**阶段 2：三层挂载 + 容器启动**
- 新增/适配 `run.sh`：CIFS 挂载脚本 + 起容器 + 挂载探针
- 核心命令（草案，非最终）：
  ```bash
  # WSL 侧先挂载 CIFS（首次或 WSL 会话重建后）
  sudo mkdir -p /mnt/srv/ai
  sudo mount.cifs //10.16.11.3/ai /mnt/srv/ai \
    -o user="$SMB_USER",pass="$SMB_PASS",vers=3.0,\
       uid=$(id -u),gid=$(id -g),file_mode=0644,dir_mode=0755,\
       forceuid,forcegid,iocharset=utf8

  # rootless Podman 容器启动（三必需 + keep-id + bind mount）
  podman run -d --name npu-toolchain \
    --device /dev/fuse --security-opt label=disable --cgroupns=host \
    --userns=keep-id \
    -v type=bind,source=/mnt/srv/ai,target=/workspace/ai,bind={create_host_path:false,propagation:rshared} \
    -v type=volume,source=npu-build,target=/opt/build \
    localhost/openkylin-npu-toolchain:3.0 sleep infinity
  ```
- 验收：A1 + A6 + A7

**阶段 3：LLVM ≥ 21 供给 + 两库构建**
- 直接复用 all-in-one.sh S5/S6/S7（需适配 LLVM 宿主供给路径）
- 验收：A2 + A3 + A4 + A5

**阶段 4：端到端冒烟 + 回滚验证**
- 复用服务器侧 `verify.sh`（已包含 R1-R4 验收项）
- 回滚：`podman rm -f npu-toolchain` + `podman volume rm npu-build` + `sudo umount /mnt/srv/ai`
- 验收：`verify.sh` exit 0 + 回滚命令全部可执行

---

## 3. 三层挂载设计

### 3.1 架构图

```
┌─────────────────────── Windows 11 宿主 ───────────────────────┐
│                                                              │
│  \\10.16.11.3\ai  (SMB/CIFS share)                           │
│         │                                                    │
│         │ 通道A: mount.cifs (推荐)                           │
│         │ 通道B: drvfs 9p（仅本地固定盘自动挂载）             │
│         ▼                                                    │
│  ┌──────────── WSL OpenKylin 发行版 ─────────────┐           │
│  │  rootfs: D:\WSL\OpenKylin-3.0\ext4.vhdx       │           │
│  │  podman graphroot: $HOME/.local/.../storage   │           │
│  │  /mnt/srv/ai  (CIFS mount, uid/gid 可控)      │           │
│  │  /mnt/c/      (drvfs 本地盘, 属主 99999)      │           │
│  │  （S: 是网络映射盘，WSL 不自动挂载、也不能放 VHDX）│         │
│  │         │                                     │           │
│  │         │ podman run -v type=bind,...         │           │
│  │         ▼                                     │           │
│  │  ┌────────── rootless Podman 容器 ─────────┐   │           │
│  │  │  /workspace/ai  (bind mount)            │   │           │
│  │  │  用户: 宿主 UID (userns=keep-id)        │   │           │
│  │  └─────────────────────────────────────────┘   │           │
│  └───────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 通道 A — CIFS/SMB 挂载（推荐）

**挂载参数**：
```bash
sudo mount.cifs //10.16.11.3/ai /mnt/srv/ai \
  -o user="${SMB_USER}",pass="${SMB_PASS}",vers=3.0,\
     uid=$(id -u),gid=$(id -g),\
     file_mode=0644,dir_mode=0755,\
     forceuid,forcegid,iocharset=utf8,\
     cache=strict,serverino
```

| 参数 | 作用 | 取舍 |
|------|------|------|
| `vers=3.0` | 协议版本，Windows 10+ 默认支持 SMB 3.0 | 比 2.1 支持更大文件、符号链接 |
| `uid/gid + forceuid/forcegid` | **强制**所有文件属主映射为 WSL 宿主 UID/GID | 与容器 `userns=keep-id` 对齐，容器内读写时 `stat` 返回同一 UID；**不指定 forceuid 时属主会变成 SMB 服务端报告的 UID（通常是 0 或 99999）** |
| `file_mode/dir_mode` | 统一权限位 | 覆盖 SMB 权限映射的不确定性 |
| `iocharset=utf8` | 处理中文路径（如 `notebook/libs/npu_tvm/` 下的中文注释文件） | 默认 CP936 或 ASCII 会导致文件名乱码 |
| `cache=strict` | 客户端缓存策略 | 与 `forceuid` 冲突时可能需要调 `cache=loose` 或 `none`；首次部署需实测 |
| `serverino` | 强制使用服务端 inode | SMB 协议默认 inode 可能冲突（Windows 不支持硬链接），影响 `ls -li` 等命令 |

**凭据管理**：
- **禁止硬编码** `SMB_USER` / `SMB_PASS` 在任何仓库文件或镜像内。
- 首选方案：环境变量（用户登录 WSL 后手动 `export`）或 `.env` 文件 + `source`。
- 备选：`credentials=/etc/cifs-credentials` + `chmod 600` 保护（文件内一行 `username=<user>` + 一行 `password=<pass>`）。
- **待确认**：`\\10.16.11.3\ai` 是否需要 Windows 域凭据或匿名访问？服务器侧用什么凭据访问？

### 3.3 通道 B — drvfs 9p（临时验证用）

- WSL `[automount]` **只自动挂载本地固定卷**（DriveType=3，如 C:、D: → `/mnt/c/`、`/mnt/d/`）。**网络映射盘（DriveType=4，如 `S:` = `\\10.16.11.3\ai`）不会被自动挂载**——这也正是本规格必须自建 CIFS 通道、且发行版 VHDX 不能落 S: 的原因（2026-11-02 预检：`S:` DriveType=4，`ProviderName=\\10.16.11.3\ai`）。
- 若确需走 drvfs 访问网络共享，只能显式 `mount -t drvfs '\\10.16.11.3\ai' /mnt/ai -o username=...`，仍属凭据敏感操作，且语义比 CIFS 更弱，**不列为方案**。
- **问题**：本地盘 drvfs 下所有文件属主显示为 `99999:99999`，权限位恒为 777。
- **影响**：与 `--userns=keep-id` 不匹配——容器内属主是宿主 UID（如 1000），但挂载点属主是 99999，写入时可能 Permission Denied 或静默失败。
- **使用场景**：在正式配置 CIFS 之前，用 drvfs 做**只读验证**（`podman exec ls /workspace/ai/notebook/libs/npu_tvm/CMakeLists.txt`）确认路径可达性。
- **禁用方法**：`/etc/wsl.conf` 设置 `[automount] enabled=false` + 手动 `mount.cifs`，重启发行版生效。

### 3.4 rootless Podman UID 映射方案

**方案 A：`--userns=keep-id`（推荐，服务器侧已验证）**
- 容器内运行用户 UID/GID = WSL 宿主用户 UID/GID。
- CIFS 挂载已通过 `forceuid/forcegid` 把文件属主设为同一 UID/GID。
- 容器内读写文件时属主一致。
- **条件**：WSL 宿主用户不是 root（`id -u` ≠ 0），且 `/etc/subuid`/`/etc/subgid` 为空（`keep-id` 不依赖 subuid/subgid 映射——它直接跳过 user namespace）。

**方案 B：显式 UID 映射 + `--userns=auto`（备选）**
- 设置 `--userns=auto`，容器内 root（UID 0）映射到宿主的 subuid 区间（如 `user:100000:65536`）。
- 容器内进程仍以 root 运行，但宿主侧是从属 UID。
- **问题**：CIFS 挂载文件属主是宿主 UID（如 1000），但容器内进程以映射后的从属 UID 运行（如 100000），属主不匹配 → 无法写入。
- **适用场景**：容器内不需要直接操作宿主文件（所有数据通过卷传递），本方案不适用。

**方案 C：容器内 chown + CAP_DAC_OVERRIDE（不推荐）**
- 在容器启动时把挂载点 `chown` 为容器内运行用户。
- **问题**：rootless Podman 容器通常没有 `CAP_DAC_OVERRIDE`/`CAP_CHOWN`，`chown` 会 `Operation not permitted`。这就是 G3 契约禁 `--privileged` 的原因。

### 3.5 性能与一致性

| 维度 | CIFS（通道 A） | drvfs 9p（通道 B） |
|------|---------------|-------------------|
| **延迟** | SMB 协议 ~1-5 ms 往返 | 9p fsync ~20-50 ms（每次写触发 flush） |
| **吞吐量** | 大文件顺序读 ~100-200 MB/s | 小文件密集操作 ~10-50 文件/秒（严重瓶颈） |
| **权限属主** | 可配置、可预测 | 恒 99999/99999，权限 777 |
| **大小写敏感** | SMB 默认大小写无关 | 9p/drvfs 继承 Windows（大小写无关） |
| **硬链接** | Windows 不支持 SMB 硬链接 | 9p 不支持 |
| **符号链接** | SMB 3.0 支持（需确认） | 9p 不支持 |
| **并发写入** | SMB 锁机制支持多人并发 | 9p 元数据锁可能冲突 |
| **容器 bind mount 性能** | CIFS → bind mount 透传，性能接近原生 | 9p → bind mount 二次穿透，更慢 |
| **`ninja` 增量编译** | 可能因 mtime/inode 变化触发不必要重编译 | 9p mtime 精度差，更容易触发假重编译 |

**影响评估**：npu_tvm 构建涉及 ~2000 个 `.o` 文件的密集小文件操作（ninja + C++ 编译 + 链接），**9p/drvfs 性能不可接受**。**必须用 CIFS 通道 A**。

**缓存选项**：
- `mount.cifs cache=strict`：客户端严格缓存，宿主侧修改需要客户端同步刷新。适合单用户开发场景。
- `mount.cifs cache=none`：每次都走网络，一致性最高但性能最差。适合多人协作场景。
- **首次部署用 `cache=strict` 验证性能**，若出现宿主侧文件修改容器内不可见，再切换。

### 3.6 分层落盘设计与 D: 盘防膨胀（新增，2026-11-02）

#### 3.6.1 强制分层表

| 类别 | 内容 | 落盘位置 | 环境变量/参数 | 为什么 |
|------|------|---------|--------------|--------|
| **必须 D: 盘（ext4.vhdx）** | WSL 发行版 rootfs + ext4.vhdx | D:\WSL\OpenKylin-3.0\ext4.vhdx | `wsl --import ... --location D:\...` | WSL 强制要求 VHDX 在本地固定盘（DriveType=3） |
| **必须 D: 盘（overlay 硬约束）** | podman graphroot（镜像层 + 容器层 CoW） | WSL 宿主 `$HOME/.local/share/containers/storage/`（默认，等价于 `~/.local/share/containers/storage/`） | 或显式设 `containers-storage.conf` → `graphroot = "$HOME/.local/share/containers/storage"` | overlay 驱动硬要求底层 ext4 支持 d_type + xattr + hardlink + flock；CIFS 缺失 → overlay 无法跑在 CIFS 上 |
| **必须本地（runroot，tempfs）** | podman runroot（容器运行时状态：锁文件、socket、临时层标记） | WSL 宿主 `/run/user/<uid>/containers/`（默认，`/run` 为 tmpfs，占用内存而非 D: 盘） | `runroot = "/run/user/$(id -u)/containers"` | 必须落在 POSIX 语义完整的 tmpfs/ext4 上；放 CIFS 会因锁与 xattr 缺失导致 podman 启动失败，且 runroot 本身不消耗 D: 盘容量 |
| **必须 D: 盘（容器内）** | 容器内 `/` 根文件系统（container runtime rootfs） | podman graphroot overlay upper 层 | — | 跟随 graphroot 自动落盘 |
| **必须 D: 盘（构建卷）** | 容器内 `/opt/build`（TVM + npuusertools 构建产物 + LLVM） | podman 命名卷 `npu-build` 底层 ext4 | `podman volume create npu-build` | 构建密集小文件操作（ninja 产出 ~2000 个 .o）→ 性能优先；产物量小（TVM ~500MB + npuusertools ~100MB + LLVM ~300MB ≈ 900MB），不构成 D: 盘主要压力 |
| **应外置到 CIFS（源码树）** | `notebook/libs/npu_tvm/` + `notebook/libs/npuusertools/` | CIFS `/mnt/srv/ai/` → 容器 bind mount `/workspace/ai/` | 容器 `-v type=bind,source=/mnt/srv/ai,target=/workspace/ai,bind: {create_host_path: false, propagation: rshared}` | 源码由 Git 管理，体积小（npu_tvm ~100MB + npuusertools ~50MB），变更频繁，**必须共享**给多人协作 |
| **应外置到 CIFS（pip cache）** | pip 下载缓存 | 容器内 `/workspace/ai/.cache/pip/` | `PIP_CACHE_DIR=/workspace/ai/.cache/pip` | pip wheel/源码包缓存 ~几百 MB；外置可跨容器/跨构建复用 |
| **应外置到 CIFS（conda pkgs）** | conda 包缓存 | 容器内 `/workspace/ai/.conda/pkgs/` | `CONDA_PKGS_DIRS=/workspace/ai/.conda/pkgs` | conda 包缓存 ~2-5 GB（取决于装多少包），外置显著减轻 D: 盘压力 |
| **应外置到 CIFS（模型/数据集）** | NPU 模型、ONNX 模型、训练数据集 | 容器内 `/workspace/ai/notebook/models/` 或类似路径 | 硬编码到路径 | 模型体积大（每个 NPU 模型 ~100-500MB），外置省 D: 盘 |
| **应外置到 CIFS（构建中间）** | 宿主侧预构建产物（若有） | CIFS 任意子目录 | — | 构建中间产物可随时删除，外置省 D: 盘 |

#### 3.6.2 vfs 驱动评估（用户坚持放共享盘时）

**假设场景**：用户坚持把 podman graphroot 放到 CIFS 上 → 必须用 vfs 驱动。

| 维度 | vfs 在 CIFS 上 | overlay 在 ext4 上（推荐） |
|------|---------------|--------------------------|
| **空间膨胀** | 每个新容器 = 容器运行时层全量复制（CoW 失效）。多容器并行 + 频繁重建 → VHDX 膨胀 N 倍 | overlay CoW 共享 lower 层，仅 upper 层占空间，空间效率最优 |
| **容器启动** | 秒级 → 分钟级（启动时全量复制 runtime layer） | 秒级 |
| **构建性能** | 容器内编译会写 upper 层 → 每次 `ninja` 触发大量 SMB 写 → 比 overlay 慢 2-5x | 容器内写在 ext4 upper 层 → 接近原生 |
| **并发与锁** | SMB CIFS 锁语义 ≠ 本地 flock → 多容器并发构建可能出现元数据冲突（两个 pod 同时写同名文件） | ext4 flock 原生支持，安全 |
| **回退可行性** | podman 启动时自动检测 overlay 不可用就回退 vfs → 很容易"意外"进入 vfs 模式，需显式 `storage.conf driver = "overlay"` + 启动前 graphroot 路径校验 | 显式配置 + 预检 |
| **推荐** | **不推荐**。空间、性能、锁三重劣势 | ✅ **唯一正确选择** |

**结论**：vfs 驱动代价极高，**强烈不推荐**把 podman 存储放共享盘。overlay 硬约束是不可绕过的底层事实，分层落盘是唯一正确路径。

#### 3.6.3 D: 盘防膨胀措施

**容量监控（每次进入容器前检查）**：
```powershell
# Windows 宿主 PowerShell
$freeGB = [math]::Round((Get-PSDrive -Name D).Free / 1GB, 1)
$thresholdGB = 20
if ($freeGB -lt $thresholdGB) {
    Write-Host "⚠️ D: 盘剩余 ${freeGB} GB < 阈值 ${thresholdGB} GB — 需要清理" -ForegroundColor Yellow
}
```

**主动清理（容器内 + 宿主侧）**：
```bash
# --- WSL 宿主侧 ---
# 清理未使用的镜像层 + dangling images + 停止的容器
podman system prune -af   # ⚠️ 会删除所有未运行的镜像！

# 只清理 dangling images（推荐日常用）
podman image prune

# 清理构建缓存（如果有）
podman builder prune

# 清理 conda/pip 缓存（外置到 CIFS 的路径）
rm -rf /workspace/ai/.cache/pip/*
conda clean --all -y   # 容器内

# --- Windows 宿主侧 VHDX 压缩（WSL 已关机时）---
# 步骤 1：关闭所有 WSL 发行版
wsl --shutdown

# 步骤 2：diskpart 压缩 VHDX（需管理员 PowerShell）
diskpart
select vdisk file="D:\WSL\OpenKylin-3.0\ext4.vhdx"
compact vdisk
detach vdisk
exit

# 或用 Optimize-VHD（Hyper-V 可选功能安装时自带）
Optimize-VHD -Path "D:\WSL\OpenKylin-3.0\ext4.vhdx" -Mode Full
```

**容量预估（首次全量构建后）**：

| 组件 | 预估占用 |
|------|---------|
| WSL 发行版 VHDX（openkylin:3.0 基线） | ~10 GB |
| podman graphroot（openkylin-npu-toolchain:3.0 镜像层 × 3） | ~3-5 GB |
| 容器运行时层（容器运行时写入，每次重建叠加） | ~0.5-1 GB |
| `/opt/build` 命名卷（TVM 构建 + LLVM 21/22 + npuusertools） | ~1.5 GB |
| **首次构建总计** | **~15-17 GB** |

D: 盘 34.2 GB 可用 → 首次构建后剩余 ~17-19 GB。阈值 20 GB → 首次构建就会触发告警，**首次构建完成后应立即执行 VHDX 压缩**。

#### 3.6.4 WSL 宿主侧 storage.conf 示例（只读参考）

```ini
# /etc/containers/storage.conf — WSL 宿主侧 rootless podman
# 该文件控制 WSL 宿主侧的 podman 存储，不是容器内 DinP 的

[storage]
driver = "overlay"                    # 硬约束：必须 overlay
runroot = "/run/user/$(id -u)/containers"   # tmpfs，WSL ext4.vhdx
graphroot = "$HOME/.local/share/containers/storage"  # overlay 层，WSL ext4.vhdx

[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"   # rootless 必需
mountopt = "nodev,metacopy=on"
```

**不写进文件的安全项**：
- `containers-auth.json`（镜像 registry 凭据）→ 放在 `$XDG_RUNTIME_DIR/containers/` 或 `$HOME/.config/containers/`，**不提交 Git**
- `.env`（SMB 凭据 `SMB_USER` / `SMB_PASS`）→ WSL 宿主侧 shell 环境变量，**不写入任何脚本或配置文件**

---

## 4. 性能与一致性（展开）

### 4.1 并发写入与大小写敏感

- **TVM 构建**：ninja 并行编译（`ninja -j$(nproc)`）涉及大量并发写临时文件、`.ninja_deps`、`.ninja_log`。CIFS 在并发写入场景下的 SMB 文件锁机制比 9p/drvfs 更可靠。
- **Python .pyc 生成**：ninja 编译过程中 TVM 的 Python 部分会触发 `.pyc` 写入（除非 `PYTHONDONTWRITEBYTECODE=1`）。建议在容器内设置 `PYTHONDONTWRITEBYTECODE=1`。
- **大小写敏感**：Windows NTFS 默认大小写保留但比较不敏感。TVM C++ 源码通常混用大小写（`include <tvm/runtime/TVM.h>` vs `tvm/runtime/tvm.h`），这种在 NTFS 下不会出问题，但 TVM 构建产物中的符号表如果有大小写敏感的符号可能出错——**首次构建后用 `ninja -C /opt/build/npu_tvm tvm` 的 exit 码验证**。

### 4.2 文件权限与属主冲突矩阵

| 场景 | CIFS 通道 A (forceuid=host_uid) | drvfs 通道 B (属主 99999) |
|------|----------------------------------|--------------------------|
| 容器内新建文件 | 属主 host_uid，与挂载一致 | 属主 host_uid，挂载侧显示 99999 |
| 容器内写入已有文件 | forceuid 覆盖后以 host_uid 写入 | 9p 不支持 chown，可能 Permission Denied |
| 容器内删除宿主创建的文件 | forceuid 覆盖，可删除 | 9p 可能不支持删除属主 99999 的文件 |
| `git status` 在容器内 | 属主一致，git 正常 | 属主不一致（99999 vs host_uid），git 可能报 modified 或 untracked |

---

## 5. 镜像基线选择

### 5.1 三方案对比

| 维度 | A. openkylin:3.0 + conda-forge（服务器侧） | B. devcontainer-base + conda-llvm | C. jupyter-podman-rootless |
|------|------------------------------------------|-----------------------------------|----------------------------|
| **基础镜像** | `localhost/openkylin:3.0`（WSL rootfs 导入） | `ubuntu:26.04` | `ubuntu:26.04` |
| **工具链来源** | conda-forge（USTC 镜像） | Ubuntu apt + conda-forge（conda-llvm 变体） | Ubuntu apt + conda-forge |
| **LLVM ≥ 21** | 宿主复制 或 conda-forge llvmdev（USTC 镜像 ~59MB，可达性待预检） | apt llvm-21 + conda llvmdev（Ubuntu 源可达？） | 同左 |
| **Python 版本** | conda-forge CPython 3.14（标准 GIL） | conda-forge CPython 3.14t free-threading | conda-forge CPython 3.14t free-threading |
| **服务栈** | 无（仅 `sleep infinity`） | supervisord（ssh + dockerd + podman + jupyter） | supervisord（ssh + jupyter + rootless podman） |
| **运行契约** | rootless 三必需 + keep-id + **无 privileged** | DinD 需 `--privileged`（违反 G3） | rootless 三必需 + keep-id |
| **APT 源可达性** | ~~openKylin 官方源**不可达**（防火墙白名单）~~ → **2026-11-04 实测修正**：`https://mirrors.aliyun.com/openkylin/dists/huanghe/Release` 返回 **200**（`Suite: huanghe`、`Version: 3.0`、`Codename: huanghe`），apt 层**有源**；仍不可达的仅官方站 `mirrors.openkylin.top`（无响应）与 `registry.openkylin.top`（`000`） | Ubuntu 源**待确认**（同防火墙） | 同左 |
| **网络白名单** | 仅 `mirrors.ustc.edu.cn` + `mirrors.aliyun.com` | 未知 | 未知 |
| **服务器侧已验证** | ✅ 全链路 OK（all-in-one.sh 已跑通） | ❌ 未在 ai 服务器验证 | ❌ 未在 ai 服务器验证 |
| **迁移成本** | 低（继承经过验证的 Containerfile + S5/S6/S7） | 高（需重写 Containerfile 适配 openKylin 不可达场景） | 高（Python free-threading 对 npu_tvm/npuusertools 有兼容风险） |

### 5.2 选型结论

**选型：方案 A — openkylin:3.0 + conda-forge（服务器侧变体）**

**核心理由**：
1. **网络白名单不可更改**：openKylin 官方源和 `pypi.org` 不可达是物理约束（防火墙），不是临时问题。方案 B/C 的 Ubuntu 源大概率同样不可达（同防火墙），届时也会被迫用 conda-forge 镜像兜回方案 A 的路线。
2. **服务器侧已端到端验证**：`all-in-one.sh` 已在 `ai@10.16.11.3` 上跑通 LLVM 21 供给 + npu_tvm 构建（libtvm.so + `import tvm` + `Target("llvm")`/`Target("ccompiler")`）+ npuusertools 构建（editable + `import xmnn`）+ onnx.yolov5s 端到端（6/6 模型编译完成）。
3. **违反 G3 契约**：devcontainer-base 的 DinD 需要 `--privileged`，而 G3 组级契约严禁。
4. **Python free-threading 对 npu_tvm/npuusertools 有风险**：方案 B/C 用 cp314t，npu_tvm 的 C 扩展编译链在 free-threading 下可能出现 ABI 不兼容（需要额外的 `-DPy_GIL_DISABLED` 编译标记和 `PYTHON_GIL=0` 环境变量）。没有必要为一个"暂时不用"的 free-threading 特性引入额外不确定性。

> **原判断已被实测修正（2026-11-04）**：§5.1「APT 源可达性」行与本节理由 1 原载「openKylin 官方源不可达」，并据此外推「方案 B/C 的 Ubuntu 源大概率同样不可达」。实测 `https://mirrors.aliyun.com/openkylin/dists/huanghe/Release` 返回 **200**，`Suite: huanghe / Version: 3.0 / Codename: huanghe`——即 openKylin 3.0 的 **apt 仓库在既有白名单内的阿里云镜像站可得**。原判断仅对「官方站与官方 registry」成立，对「apt 源」不成立；缺的不是源，而是引导工具（`debootstrap` 未安装、`sudo` 需密码、rootless 下 `chroot`/`mknod` 受限）。上文原文一律保留、不静默改写：这条本身即「推断写入文档后被下游继承」的实例——「官方站不可达」→「发行版 apt 源不可达」→「方案 B/C 不可行」三步皆为推断。方案 A 的选型结论不变，但理由 1 的适用范围须按上述收窄。评估与不采纳决策的完整记录见[风险与待办 §9](09-6-risks-todos-changelog.md)。

**需要新增/适配的层**（不是从零开始，是服务器侧容器的**宿主侧适配**）：
- **CIFS 挂载脚本**：`scripts/mount-cifs.sh`（WSL 宿主侧执行）
- **run.sh 适配**：把服务器侧 `/media/pc/data/ai` 路径替换为 WSL 侧 `/mnt/srv/ai`；`podman run` 命令行适配
- **LLVM ≥ 21 供给适配**：把服务器侧从 `/usr/lib/llvm-21` 复制改为从 WSL 宿主 LLVM 路径（21 或 22，取决于供给版本）；LLVM 获取路径优先级：WSL 宿主 conda-forge llvmdev > 服务器 scp > 容器 bind mount（见 §2.I I4）；**LLVM 在 WSL 宿主上的可用性（21 或 22）是阻塞级待确认项**，见 §9 Q2
- **preflight 预检脚本**：`scripts/preflight-wsl.sh`（检查 CIFS/LLVM/rootless/Uid 等）

---

## 6. npu_tvm 与 npuusertools 的依赖与构建链

### 6.1 npu_tvm

| 项 | 值 |
|----|-----|
| **源码** | `/workspace/ai/notebook/libs/npu_tvm`（bind mount 进入容器） |
| **构建系统** | CMake + Ninja（`cmake` 驱动，`ninja` 执行） |
| **LLVM 依赖** | **LLVM ≥ 21（21 或 22 均可）**。最低门槛由 `src/target/llvm/llvm_compat.h:161` 门控 `getOrInsertDeclaration` ≥ 200（LLVM 20+，源码注释明确 "LLVM 20.0+ 引入"）；`llvm_module.cc:518` linker 签名简化门控 ≥ 210（21+ 走简化 ObjectLayer，20 走 elif >= 130 分支）；**无上限检查**（源码不存在 `TVM_LLVM_VERSION >= 220` 特判）。FindLLVM.cmake:229 仅校验 `LESS 40`，LLVM.cmake:32 校验 `LESS 60`。服务器侧已验证 LLVM 21 端到端通过，22 预期兼容。 |
| **关键 CMake 开关** | `-DUSE_CODEGENC=ON`（注册 `ccompiler` target）+ `-DUSE_LLVM=/opt/build/llvm${LLVM_MAJOR}/bin/llvm-config`（宿主 LLVM 路径，`LLVM_MAJOR`=21 或 22） |
| **构建目录** | `/opt/build/npu_tvm`（命名卷 npu-build，不回写工作区） |
| **产物** | `/opt/build/npu_tvm/libtvm.so`（~79 MB） |
| **Python 路径** | `PYTHONPATH=/workspace/ai/notebook/libs/npu_tvm/python:/workspace/ai/notebook/libs/npu_tvm/vta/python:/workspace/ai/notebook/libs/npuusertools` |
| **运行时库路径** | `LD_LIBRARY_PATH=/opt/build/npu_tvm:/opt/build/llvm${LLVM_MAJOR}/lib` + `TVM_LIBRARY_PATH=/opt/build/npu_tvm` |
| **pip 安装** | 无（直接用 PYTHONPATH 指向源码树） |

**陷阱**：仓库根没有 `config.cmake`，`cmake/config.cmake` 不会被自动 include，所以 `USE_CODEGENC` / `USE_LLVM` **必须命令行显式传入**。漏传典型症状：`Attribute 'RelayToTIR' is not registered` 或 `target.build.llvm is not enabled`。

### 6.2 npuusertools

| 项 | 值 |
|----|-----|
| **源码** | `/workspace/ai/notebook/libs/npuusertools`（bind mount 进入容器） |
| **构建系统** | scikit-build-core（pyproject.toml）+ CMake + Ninja（`cmake -G Ninja -DCMAKE_BUILD_TYPE=Release`） |
| **Python 版本** | `requires-python = ">=3.14"` |
| **依赖（pip）** | numpy/scipy/pandas/matplotlib/onnx/protobuf/Pillow/openpyxl/tabulate/rich/tqdm/tomlkit/decorator/attrs/psutil/typing_extensions/pytest |
| **构建目录** | `/opt/build/npuusertools`（`BUILD_DIR` 环境变量 + `--config-settings=build-dir=`） |
| **安装目录** | `/opt/build/npuusertools/userbase`（`PYTHONUSERBASE` 重定向 `--user` 安装前缀） |
| **命令** | `BUILD_DIR=/opt/build/npuusertools bash scripts/build.sh` + `PYTHONUSERBASE=/opt/build/npuusertools/userbase python -m pip install --no-cache-dir --no-build-isolation --user -e . --config-settings=build-dir=/opt/build/npuusertools` |
| **验证命令** | `python -c 'import xmnn; print(xmnn.__file__)'`（路径必须在 `/opt/build/npuusertools/userbase/` 下） |

**陷阱**：容器内 conda 主环境的 `site-packages` 只读，不能直接 `pip install` 写入系统前缀。必须三件套：`BUILD_DIR` + `PYTHONUSERBASE` + `--user`。

### 6.3 两库共存时的路径与 LD_LIBRARY_PATH 设计

```bash
# TVM 导入时需要（容器内执行）：
export PYTHONPATH=/workspace/ai/notebook/libs/npu_tvm/python:/workspace/ai/notebook/libs/npu_tvm/vta/python:/workspace/ai/notebook/libs/npuusertools
export TVM_LIBRARY_PATH=/opt/build/npu_tvm

# 兜底：如果新建卷没有写 rpath，显式给动态库搜索路径
# 顺序：TVM libtvm.so 先被搜索，然后 LLVM libLLVM*
export LD_LIBRARY_PATH="/opt/build/npu_tvm:/opt/build/llvm${LLVM_MAJOR}/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# npuusertools 安装前缀
export PYTHONUSERBASE=/opt/build/npuusertools/userbase

# 用户目录（避免写回宿主）
export HOME=/tmp/tvmhome
export MPLCONFIGDIR=/tmp/mplconfig
mkdir -p "$HOME" "$MPLCONFIGDIR"
```

### 6.4 启动钩子约定（从 npuusertools AGENTS.md 继承）

`_xmnn_bootstrap.py` 是解释器启动期 AST 兼容钩子，由 `xmnn_bootstrap.pth` 在 site 初始化期加载。其语义真源在 `../npu_tvm/` 仓库根（2026-10-16 迁移），载荷与安装器同域。当前源码构建（非 Nuitka 编译）已原生改用 `ast.Constant`，从宿主源码构建不再依赖本钩子。但在役打包链仍 pin Nuitka 4.2.2，builder overlay 副本与已交付 wheel 内置 `.pth` 仍在役。**容器内首次构建时默认不带这个钩子**，如遇 `from ast import Num/Str/NameConstant` 错误再手动安装 `.pth`。

---

## 7. 验证方案

### 7.1 容器启动与运行契约（宿主侧 `verify.sh` 复用）

```bash
# 验收脚本（复用服务器侧 apps/openkylin-dev-container/variants/npu-toolchain/scripts/verify.sh）
CTR=npu-toolchain
IMAGE=localhost/openkylin-npu-toolchain:3.0

# R1 容器存在且运行
podman container exists $CTR && podman inspect --format '{{.State.Status}}' $CTR == running

# R2 rootless 三必需 + 无 privilege
podman inspect --format '{{.HostConfig.Privileged}}' $CTR == false
# 设备 + security-opt + cgroupns 已在 compose.yaml 声明

# R3 工具链版本
podman exec $CTR python -c 'import sys; print(sys.version_info >= (3,14))'
podman exec $CTR cmake --version | grep -E "3\.18\+"
podman exec $CTR ninja --version | grep -E "1\.10\+"

# R4 挂载契约（容器内写 probe → 宿主侧可见）
podman exec $CTR bash -c 'touch /workspace/ai/.temp/npu-toolchain/.probe && chmod 700 /workspace/ai/.temp/npu-toolchain/.probe && stat -c "%a %u" /workspace/ai/.temp/npu-toolchain/.probe'
sudo ls -la /mnt/srv/ai/.temp/npu-toolchain/.probe  # 宿主侧 CIFS 挂载点可见
```

### 7.2 npu_tvm 构建验证（容器内）

```bash
# 前置：LLVM ≥ 21（21 或 22）已经在 /opt/build/llvm${LLVM_MAJOR}/
export LLVM_MAJOR=21  # 或 22，根据实际供给版本
cd /opt/build/npu_tvm 2>/dev/null || {
  cmake -G Ninja -S /workspace/ai/notebook/libs/npu_tvm -B /opt/build/npu_tvm \
    -DCMAKE_BUILD_TYPE=Release \
    -DUSE_CODEGENC=ON \
    -DUSE_LLVM=/opt/build/llvm${LLVM_MAJOR}/bin/llvm-config
}
ninja -C /opt/build/npu_tvm tvm
test -f /opt/build/npu_tvm/libtvm.so || { echo "FAIL: libtvm.so 缺失"; exit 1; }

# 导入 + Target 断言
export PYTHONPATH=/workspace/ai/notebook/libs/npu_tvm/python:/workspace/ai/notebook/libs/npu_tvm/vta/python:/workspace/ai/notebook/libs/npuusertools
export TVM_LIBRARY_PATH=/opt/build/npu_tvm
export LD_LIBRARY_PATH="/opt/build/npu_tvm:/opt/build/llvm${LLVM_MAJOR}/lib"
python - <<'PY'
import tvm
print("tvm.__version__ =", tvm.__version__)
assert tvm.__version__.startswith("0.19"), tvm.__version__
for key in ("llvm", "ccompiler"):
    tgt = tvm.target.Target(key)
    print(f'Target("{key}") -> {tgt}')
print("tvm file =", tvm.__file__)
PY
```

### 7.3 npuusertools 构建验证（容器内）

```bash
cd /workspace/ai/notebook/libs/npuusertools
export HOME=/tmp/tvmhome PYTHONUSERBASE=/opt/build/npuusertools/userbase
mkdir -p "$HOME" /opt/build/npuusertools

BUILD_DIR=/opt/build/npuusertools bash scripts/build.sh
PYTHONUSERBASE=/opt/build/npuusertools/userbase python -m pip install --no-cache-dir --no-build-isolation --user -e . \
  --config-settings=build-dir=/opt/build/npuusertools

# import xmnn 路径断言
out="$(python -c 'import xmnn; print(xmnn.__file__)')"
[[ "$out" == /opt/build/npuusertools/userbase/* ]] || { echo "FAIL: xmnn 路径不在 userbase 下"; exit 1; }
echo "PASS: xmnn.__file__ = $out"

# 命令行工具冒烟
python tools/compile.py -h 2>/dev/null && echo "PASS: compile.py -h" || echo "FAIL: compile.py -h"
python tools/infer.py -h 2>/dev/null && echo "PASS: infer.py -h" || echo "FAIL: infer.py -h"
```

### 7.4 失败判定标准

| 失败类型 | 判定 | 处置 |
|----------|------|------|
| **挂载层** | 容器内 `ls -la /workspace/ai/notebook/libs/npu_tvm/CMakeLists.txt` 返回 Permission Denied 或 No such file or directory | CIFS 挂载参数错误或未挂载；回 WSL 宿主侧重挂，确认 `forceuid/forcegid` |
| **LLVM 层** | `/opt/build/llvm${LLVM_MAJOR}/bin/llvm-config --version` 输出 < 21 或命令不存在 | 宿主侧 LLVM ≥ 21（21 或 22）供给未完成；按 §9 Q2 处置 |
| **CMake 层** | `cmake -G Ninja -S ... -B ...` exit ≠ 0 | 检查 `USE_CODEGENC`/`USE_LLVM` 开关；检查 LLVM 路径；检查 cmake/ninja/gcc 版本 |
| **Ninja 层** | `ninja -C /opt/build/npu_tvm tvm` exit ≠ 0 | 看末尾 stderr；常见是缺少头文件、LLVM 符号找不到、libLLVM 路径不对 |
| **Import 层** | `import tvm` 报 `libtvm.so not found` 或 `libLLVM*.so not found` | `LD_LIBRARY_PATH` 缺 `/opt/build/npu_tvm` 或 `/opt/build/llvm${LLVM_MAJOR}/lib` |
| **xmnn 安装层** | `pip install --user -e .` exit ≠ 0 | `BUILD_DIR` 未传递；`--no-build-isolation` 导致依赖缺失；容器内需要先 `pip install scikit-build-core cmake ninja` |

---

## 8. 风险、回退与分阶段实施计划

### 8.1 风险矩阵

| # | 风险 | 可能性 | 影响 | 缓解/处置 |
|---|------|--------|------|-----------|
| R1 | WSL 宿主 apt 源不可达（openKylin/CIFS 都装不了） | 高 | 阻塞 | 确认 apt 源；若真不可达，改用 conda-forge 镜像在 WSL 宿主装 cifs-utils |
| R2 | LLVM ≥ 21 在 WSL 宿主上获取失败 | 中（原"高"，降为中：conda-forge llvmdev ~59MB 远小于此前误写的 800MB，获取路径更短） | 阻塞 TVM 构建 | 宿主侧 conda-forge llvmdev（USTC 镜像，22.1.7 约 59MB、21.1.4 约 58MB，均含 llvm-config + headers + cmake）；或从服务器 `scp /usr/lib/llvm-21`（~300MB）；两条路径均需预检 |
| R3 | CIFS 挂载后容器属主仍不匹配 | 中 | 容器内无法写入 | 检查 `forceuid/forcegid` 生效；改用 `--userns=host`（容器内 root）+ run.sh 里手动 `chown -R $(id -u) /workspace/ai`（⚠️ 容器内 root 有安全风险，仅作临时处置） |
| R4 | `ninja tvm` 在 WSL 容器内比服务器慢 10 倍以上 | 中 | 体验差 | CIFS `cache=strict`；`ninja -j$(nproc)`；考虑把 `/opt/build` 从 CIFS 移到容器命名卷（已是） |
| R5 | Windows 重启后 WSL 发行版丢失 | 低 | 环境不可用 | 导出 WSL 发行版（`wsl --export OpenKylin <backup.tar>`）；定期备份 |
| R6 | Podman rootless 在 OpenKylin WSL 发行版内安装失败 | 中 | 阻塞容器运行 | `okw podman preflight/install/verify` 三步流程（openkylin-wsl-devkit 已有）；若 OpenKylin 源缺 podman，用 Ubuntu 包替代或从 Debian 源 deb 安装 |
| R7 | SMB 凭据硬编码到容器镜像或 compose.yaml | 极低（规格已禁止） | 安全风险 | 凭据只在 `.env` 或 shell 环境变量；镜像内绝不出现；`podman ps` 可能显示环境变量——部署时注意 |
| R8 | **D: 盘空间膨胀（新增，2026-11-02）** | **中（首次构建后必触发）** | 构建中断 + 系统不稳定 | 分层落盘（conda/pip 缓存外置）+ `podman system prune` + **构建完成后立即 VHDX 压缩**（`wsl --shutdown` + `diskpart compact vdisk`）；设 20GB 剩余阈值告警 |
| R9 | **overlay 意外回退 vfs（新增，2026-11-02）** | 低（但一旦发生危害大） | 空间膨胀 + 性能暴跌 | 预检阶段显式检查 `podman info --format '{{.GraphDriverName}}'` 返回 `overlay`；storage.conf 硬写 `driver = "overlay"` |

### 8.2 回滚方案

```bash
# 1. 容器 + 卷（保留构建产物可跳过 volume rm）
podman rm -f npu-toolchain
podman volume rm npu-build

# 2. CIFS 挂载
sudo umount /mnt/srv/ai

# 3. 镜像
podman rmi localhost/openkylin-npu-toolchain:3.0
# 基线镜像保留：localhost/openkylin:3.0 不受影响

# 4. WSL 发行版（谨慎操作，需确认）
wsl --unregister OpenKylin-3.0  # ⚠️ 彻底删除发行版
```

### 8.3 分阶段实施计划

| 阶段 | 产出物 | 验收 | 前置 | 预计工作量 |
|------|--------|------|------|-----------|
| **0. 规格确认** | 本规格文档 v1.3-draft 经人类评审 | 规格批准或带批注批准 | 无 | 本轮完成 |
| **1a. 发行版导入（D: 盘）** | 注册 `OpenKylin-3.0`，`ext4.vhdx` 落 `D:\WSL\OpenKylin-3.0\` | `wsl -l -v` 显示 `OpenKylin-3.0 … 2`；`Test-Path D:\WSL\OpenKylin-3.0\ext4.vhdx` 为 True；`wsl -d OpenKylin-3.0 -- id -u` 非 0 | 阶段 0 批准；**管理员 PowerShell**；镜像 `\\.agents\wsl-images\openKylin-3.0-desktop-wsl-amd64.wsl`（6.2 GB） | 0.5 天（复制 + import） |
| **1b. WSL 宿主侧预检** | `scripts-host/preflight-wsl.sh` + 预检结果报告 | 所有前置条件 PASS（OpenKylin 版本、Podman rootless、CIFS、LLVM ≥ 21、UID 映射），并覆盖 **A8**（`graphDriverName=overlay`、graphroot 非 CIFS）与 **A9**（D: 剩余 ≥ 20GB） | 阶段 1a 发行版已注册 | 0.5 天 |
| **2. WSL 宿主侧环境就绪** | (a) CIFS 挂载常驻 (b) LLVM ≥ 21 就绪（21 或 22） (c) Podman rootless 已装 | (a) `/mnt/srv/ai/notebook/libs/npu_tvm/CMakeLists.txt` 可读 (b) `/opt/build/llvm${LLVM_MAJOR}/bin/llvm-config --version` → 21.x 或 22.x (c) `podman info --format '{{.Host.Security.Rootless}}'` → true | 阶段 1b 预检完成 | 1 天（LLVM 获取路径已缩短，原计划 1-2 天） |
| **3. 镜像构建** | `localhost/openkylin-npu-toolchain:3.0`（容器内 Python 3.14 + cmake ≥ 3.18 + ninja ≥ 1.10 + conda-forge 镜像就绪） | 版本门禁 PASS | 阶段 2 环境就绪 + 服务器侧基线镜像已导入 | 镜像构建 ~30 分钟（已在服务器侧验证） |
| **4. 容器启动 + 挂载门禁** | 容器运行 + `verify.sh` R1-R4 | A1 + A6 + A7 + A8 | 阶段 3 镜像就绪 | 0.5 天 |
| **5. LLVM ≥ 21 供给** | 容器内 `/opt/build/llvm${LLVM_MAJOR}/bin/llvm-config --version` → 21.x 或 22.x | A3 | 阶段 4 容器已运行 | 0.5 天（宿主侧复制 + 验证） |
| **6. 两库构建** | npu_tvm libtvm.so + npuusertools editable 安装 | A4 + A5 | 阶段 5 LLVM 就绪 | TVM ~20-30 分钟 + npuusertools ~5 分钟（首次构建） |
| **7. 端到端冒烟 + 回滚** | `verify.sh` 全 PASS + 回滚脚本可执行 + D: 盘容量复核 | A1-A9 全 PASS + 回滚零副作用 + D: 剩余 ≥ 20GB（否则执行 VHDX 压缩） | 阶段 6 完成 | 0.5 天 |

---

## 9. 待确认问题清单

| # | 问题 | 阻塞级别 | 负责方 | 状态 | 预计决策时间 |
|---|------|----------|--------|------|-------------|
| Q1 | **OpenKylin WSL 发行版宿主 apt 源是否可达？**（`apt update` 能成功吗？） | **阻塞级** | 用户 | 未确认；**前置**：当前 Windows 机器 **零 WSL 发行版注册**（2026-11-02 预检：wsl -l -v 输出"无 Linux 发行版已安装"），需先导入 OpenKylin 发行版后才能测 apt 源 | 阶段 1 预检（需先完成 Q1a 前置） |
| Q1a | **当前 Windows 机器零 WSL 发行版注册**（新增前置） | **阻塞级前置** | 用户 | 已确认（2026-11-02 预检）；WSL 组件已装（WSL 3.0.3.0 + kernel 6.18.54.1，Windows 10.0.19044.7807），但 wsl -l -v 输出"无 Linux 发行版已安装" | **阶段 1 前置**：先导入发行版再做 Q1/Q2/Q3/Q5 预检 |
| Q2 | **LLVM ≥ 21（21 或 22）在 WSL 宿主上如何获取？**（**阻塞级，但路径已收窄**）选项：(a) **WSL 宿主 conda-forge llvmdev**（USTC 镜像，linux-64 22.1.7 约 59MB、21.1.4 约 58MB；含 `llvm-config --libfiles --headers --cmakedir` 全部可用）—— 首选；(b) 从服务器 `scp /usr/lib/llvm-21` 到 WSL 宿主（~300MB）；(c) 容器 bind mount 宿主 LLVM 路径（不推荐，宿主可能没有） | **阻塞级**（但已从"高可能性"降为"中"，conda-forge 路径已在 Q2 预检覆盖） | 用户 + 实施者 | 预检前置：验证 WSL 宿主 Miniforge/conda 可达 USTC 镜像 + `conda-forge llvmdev` 安装是否成功 | 阶段 1 预检 + 阶段 2 开始前 |
| Q3 | **SMB 凭据**：`\\10.16.11.3\ai` 需要 Windows 域凭据吗？用户名/密码是什么？匿名访问可能吗？ | **阻塞级** | 用户（涉及凭据，AI 不得主动获取） | 未确认 | 阶段 2 CIFS 挂载前 |
| Q4 | **OpenKylin WSL 发行版默认用户 UID 是多少？**（服务器侧是 1006，WSL 侧 OpenKylin 可能默认 1000） | **非阻塞**（影响 userns 配置参数） | 实施者 | 可通过 `id -u` 直接获取 | 阶段 1 预检 |
| Q5 | **WSL 宿主上是否已有 rootless Podman？** 若没有，`okw podman preflight/install/verify` 三步能跑通吗？（OpenKylin 源缺 podman 包怎么办？） | **阻塞级** | 实施者 | 未确认 | 阶段 1 预检 |
| Q6 | **容器内是否需要 free-threading (cp314t)？** 当前方案用标准 GIL Python 3.14。若需要 cp314t，需切换到 jupyter-podman-rootless 路线或在 openkylin:3.0 上加 cp314t 层——会显著增加工作量。 | **决策级**（影响方案选型） | 用户 | 未确认 | 阶段 0 规格批准前 |
| Q7 | **CIFS `cache=strict` 与 `forceuid` 组合是否会出现权限竞争？**（多人同时写入 + 缓存延迟导致权限检查错乱） | **非阻塞**（影响一致性但不阻塞首跑） | 实施者 | 未确认 | 阶段 5 构建 TVM 时实测 |
| Q8 | **服务器侧基线镜像 `localhost/openkylin:3.0` 如何传到 Windows/WSL 宿主？** `podman save localhost/openkylin:3.0 > baseline.tar` + `podman load < baseline.tar` 需要 1-2 GB 数据传输 | **非阻塞**（阶段 3 前置） | 实施者 | 未确认 | 阶段 2 开始前 |
| Q9 | **D: 盘 34.2 GB 可用容量是否构成长期基线？** 首次构建预估占用 15-17 GB（VHDX 基础 ~4-6 GB + graphroot 镜像层 + 构建卷），叠加 TVM 多次重建与镜像迭代后余量可能不足 20 GB 阈值；是否需要 (a) 仅靠 `podman system prune` + VHDX 压缩维持，(b) 将 VHDX 迁至更大本地盘，或 (c) 提升容量阈值告警频率 | **非阻塞**（不阻塞首跑；影响阶段 7 之后的可持续性） | 用户 | 未确认；当前 34.2 GB 可支撑单轮端到端验证 | 阶段 7 端到端验证后复核 |

---

## 附录 A：与服务器侧 all-in-one.sh 的差异点汇总

| 项 | 服务器侧 | 本规格（Windows/WSL 侧） |
|----|----------|------------------------|
| **宿主路径** | `/media/pc/data/ai`（本地 sshfs 挂载） | `/mnt/srv/ai`（CIFS 挂载） |
| **宿主 UID** | 固定 1006 | 待预检（WSL OpenKylin 发行版默认用户 UID） |
| **LLVM ≥ 21 宿主源** | `/usr/lib/llvm-21`（系统已装） | **待预检**（路径一：WSL 宿主 conda-forge llvmdev ~59MB；路径二：服务器 scp ~300MB） |
| **APT 源可达性** | 不可达（openKylin 官方源） | **待预检**（OpenKylin 发行版源 + 防火墙白名单） |
| **SMB 凭据** | 不涉及（本地 sshfs） | 阻塞级待确认 |
| **CIFS 挂载脚本** | 不需要 | 必须新增 `mount-cifs.sh` |
| **preflight 预检** | 不涉及（服务器环境稳定） | 必须新增（WSL/OpenKylin 首次部署） |

## 附录 B：规格版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.3-draft | 2026-11-02 | 一致性收尾修订（不改变 v1.2 的设计结论）：(1) **A9 修正**——原 `Get-PSDrive -Name D \| Select-Object ...` 中的裸管道符会破坏 Markdown 表格列，改为 `(Get-PSDrive -Name D).Free`；(2) **§3.1 架构图**补入 `rootfs: D:\WSL\OpenKylin-3.0\ext4.vhdx`、`podman graphroot: $HOME/.local/.../storage`、`/mnt/c/`，并标注"S: 是网络映射盘，WSL 不自动挂载、也不能放 VHDX"；(3) **§3.3 事实纠错**——原文"WSL 自动挂载 S: 盘到 /mnt/s/"错误，WSL `[automount]` 只自动挂载本地固定卷（DriveType=3），网络映射盘（DriveType=4）不自动挂载；显式 `mount -t drvfs` 挂网络共享仍属凭据敏感且语义更弱，不列为方案；(4) **§3.6.1 runroot 定位纠错**——原文"tmpfs……必须在 ext4 上"自相矛盾，改为"必须本地、放 `/run/user/<uid>/containers`（tmpfs，占用内存而非 D: 盘），放 CIFS 会因锁与 xattr 缺失导致 podman 启动失败"；(5) **§8.3 阶段表**：阶段 0 版本号改为 v1.3-draft，新增 **阶段 1a 发行版导入（D: 盘）** 与 **阶段 1b 预检**（明确覆盖 A8/A9），阶段 4 验收改为 `A1 + A6 + A7 + A8`，阶段 7 验收扩至 `A1-A9` + D: 剩余 ≥ 20GB 复核；(6) **头部硬约束**补入容量事实基线（D: 34.2 GB / C: 21.5 GB / S: 网络盘）；(7) **§9 新增 Q9**（D: 盘 34.2 GB 是否构成长期基线，非阻塞）；(8) frontmatter 版本号由 v1.2.0-draft 同步为 v1.3.0-draft；(9) **§2.I I2 通道 B 纠错**——原文"WSL 自带 drvfs 9p 挂载，通常自动出现在 `/mnt/s/`（`S:` 盘）"与 §3.3 事实冲突，改为"`[automount]` 仅自动挂载本地固定卷（DriveType=3），网络映射盘（DriveType=4）不自动挂载、`/mnt/s/` 不存在"，并明确通道 B 无法覆盖本任务的共享目录、通道 A 为唯一可行路径 |
| v1.2-draft | 2026-11-02 | **新增硬约束**：(1) WSL 发行版 VHDX 落盘 D: 盘（预检确认 S: 盘是 DriveType=4 网络映射盘 `ProviderName=\\10.16.11.3\ai`，WSL 禁止在网络盘上创建 ext4.vhdx）；(2) D: 盘 34.2GB 本地固定 NTFS 是唯一合格候选；(3) **Overlay 存储驱动硬约束**——podman rootless overlay 要求底层 ext4 支持 d_type + user xattr + hardlink + flock，CIFS/SMB 协议层不返回 d_type、不支持 xattr、不支持 hardlink → **overlay 绝对不能跑在 CIFS 上**，podman graphroot/runroot 必须留在 WSL ext4.vhdx（D: 盘）；(4) **分层落盘设计**（§3.6）：强制分层表（10 类条目，覆盖 VHDX / graphroot / runroot / 构建卷 / 源码树 / pip cache / conda pkgs / 模型数据集），overlay 在 ext4 上 vs vfs 在 CIFS 上的 5 维度对比（vfs 强烈不推荐），D: 盘防膨胀措施（容量监控 + 主动清理 + VHDX 压缩 diskpart/Optimize-VHD），首次构建容量预估 ~15-17 GB；(5) **验收标准 A8 分层落盘 + A9 D: 盘 ≥ 20GB**；(6) **风险 R8 D: 盘膨胀 + R9 overlay 意外回退 vfs**；(7) 七概念新增 §2.F 约束 6-8、§2.I I6、硬约束追加到文档头部 |
| v1.1-draft | 2026-11-02 | 用户接受 LLVM 22 可接受，源码只读调研（2026-11-02）核实：(1) `FindLLVM.cmake:229` + `LLVM.cmake:32` 仅设下限（< 60 FATAL_ERROR），**无上限**；(2) `llvm_compat.h:161` `getOrInsertDeclaration` 门控 `>= 200`（源码注释明确 "LLVM 20.0+ 引入"，此前规格误写为 21）；(3) `llvm_module.cc:518` linker 简化门控 `>= 210`（21+ 走简化分支，20 走 elif >= 130）；(4) **不存在任何 >= 220 特判**，LLVM 22 完全复用 21+ 代码路径；(5) conda-forge llvmdev USTC 镜像 linux-64 22.1.7 约 59MB、21.1.4 约 58MB（此前误写 800MB+）。**Q2 阻塞级别从"高可能性阻塞"降为"中（阻塞级但路径收窄）"**，conda-forge 成为首选获取路径。规格全文 LLVM 引用从"仅 21"改为"≥ 21（21 或 22 均可）"，验收标准 A3、§6.1 LLVM 依赖行、§8.1 R2、§9 Q2 均同步更新 |
| v1.0-draft | 2026-11-02 | 首轮只读调研产出：七概念组织（F→V→I→C），三层挂载设计，镜像基线选型（openkylin:3.0 + conda-forge 经对抗审查通过），验收标准 A1-A7，分阶段计划，阻塞级待确认 Q1-Q3 |

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [风险、回退与版本历史](09-6-risks-todos-changelog.md)
- [验收与实测证据](09-5-acceptance-and-evidence.md)