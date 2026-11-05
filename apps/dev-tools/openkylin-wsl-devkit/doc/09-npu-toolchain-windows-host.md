---
type: "Spec"
title: "Windows 侧经 SSH 使用 10.16.11.3 Podman 的 npu-toolchain 规格（v2 远程后端）"
frontmatter_spec_version: "v2.1.0-draft"
status: "implemented-draft（阶段 0–4 已实施，2026-11-03 实测）"
owner: "未指定"
---

# Windows 侧经 SSH 使用 10.16.11.3 Podman 的 npu-toolchain 规格（v2 远程后端）

> **文档定位**：本规格替代 v1.x 的「Windows 宿主 WSL + OpenKylin 发行版 + 本地 rootless Podman」方案。新方案中 **Windows 只承担客户端角色**，镜像构建、容器运行、两库编译全部在 `10.16.11.3`（Ubuntu 22.04.5）上完成。本文件已**原子化拆分**，此处只保留入口索引与文档地图，技术正文按主题分布于 7 个分篇；v1.x 全文作为历史归档保留于[归档篇](09-7-appendix-v1-wsl-deprecated.md)，不再作为实施依据。

> **当前状态（2026-11-03）**：阶段 0–4 已实施；A1–A6、A8、A9 判定 PASS，A7 记 N/A（默认不发布端口）；容器内 LLVM **22.1.8**，`libtvm.so` 已按 LLVM 22 **重编完成**（854 目标 rc=0，`ldd` 链接 `libLLVM.so.22.1`），`import tvm` **0.19.0**、`import xmnn` **1.0.1.dev120** 均通过；Windows 侧 `podman --connection remote-ai` 缺陷**已修复**（`Host` → `Match host`），默认连接仍未切换。证据见[验收与实测](09-5-acceptance-and-evidence.md)。

## 方案变更（2026-11-03）

1. **D: 盘容量不可持续**：D: 总量 112 GB，导入过程峰值占用后可用一度跌至 8.82 GB；ext4.vhdx + podman graphroot + 构建卷三者叠加无法留出安全余量。
2. **WSL 导入被系统服务独占锁反复阻塞**：`vmcompute` / `wslservice` 以 SYSTEM 身份持有 9.5 GB tar 的独占句柄，非管理员会话无法释放；多次导入尝试均以 `E_UNEXPECTED` / `E_ILLEGAL_STATE_CHANGE` 终止。
3. **远程后端已具备全部前置条件**：10.16.11.3 上 rootless Podman 5.6.2 + overlay 驱动 + XFS 本地盘、LLVM 22.1.2、Python 3.14.6、以及**已构建完成并在运行的 `npu-toolchain` 容器**（含 `libtvm.so`）。远程方案不是新建，而是**接管既有可用资产**。

## 硬约束

- Windows 侧不得再尝试导入或注册任何 WSL 发行版；D: 盘只保留用户既有数据。
- 不改动 `notebook/libs/npu_tvm` 与 `notebook/libs/npuusertools` 源码。
- SMB/SSH 凭据只允许存在于环境变量或 `.env`（不提交、不入日志、不写入本文档）。远程访问依赖已配置的 SSH 密钥免密，不使用口令。
- 容器运行契约沿用组级 G3：rootless 三必需（`--device /dev/fuse`、`--security-opt label=disable`、`--cgroupns=host`），**永不使用 `--privileged`**。

## 适用范围与非目标

### 目标（In-Scope）

1. Windows 通过 SSH 以**密钥免密**方式管理 10.16.11.3 上的 rootless Podman（方案 A 为主、方案 B 为备用）。
2. 复用远程既有 `npu-toolchain` 容器（或等价重建），使容器内 `/workspace/ai/notebook/libs/npu_tvm` 与 `npuusertools` **可读写**，且容器内 UID 与宿主 `1006` 一致。
3. 容器内 LLVM 版本门禁落地为 **22.x 实测通过**（宿主已有 22.1.2，容器内补齐同版本）。
4. npu_tvm 构建通过：`libtvm.so` 存在、`import tvm` 成功、`Target("llvm")` 与 `Target("ccompiler")` 可解析。
5. npuusertools 构建与导入通过：`build.sh` + `pip install --user -e .` + `import xmnn`。
6. 容器运行满足 G3 rootless 契约，且**不发布端口**为默认状态；仅当需要 Jupyter 时才按需发布 `8890/8891` 等非冲突端口。
7. 分层落盘在远程天然成立：源码/构建产物在 XFS 本地盘，podman 存储在同一 XFS，**全链路不经过 CIFS**，无 vfs 回退风险。
8. 磁盘余量受控：graphroot 所在 XFS 可用 ≥ **50 GB**；低于阈值时禁止启动新构建。

### 非目标（Out-of-Scope）

- 不在 Windows 侧导入任何 WSL 发行版（v1.x 方案已废弃，见[归档篇](09-7-appendix-v1-wsl-deprecated.md)）。
- 不运行 NPU 硬件推理或精度验证（需板端）。
- 不重建 `npu-toolchain` 变体逻辑；构建链沿用服务器侧 `all-in-one.sh`（S5/S6/S7）。
- 不支持 free-threading Python（cp314t）；实测宿主与容器 Python 均为 GIL 版 cp314，已排除该风险路径。
- 不把宿主 conda 环境整体挂载/复制进容器作为运行时（理由见[工具链供给](09-3-toolchain-provisioning.md)）。
- 不启用容器内 sshd、不预置常驻服务；Jupyter 仅在明确需要时按需启动并显式发布端口。

## 术语表

| 术语 | 一句话释义 |
|---|---|
| rootless Podman | 以非 root 用户运行的 Podman，容器进程不具备特权，容器内不执行挂载。 |
| graphroot | Podman 镜像层与容器层的存储根目录，本方案实际落点为软链指向的 XFS 本地盘路径。 |
| runroot | Podman 运行时状态（锁文件、socket、临时层标记）的存放目录，位于 tmpfs。 |
| overlay | Podman 存储驱动，要求底层文件系统支持 d_type、user xattr、hardlink 与 flock。 |
| vfs | Podman 的另一种存储驱动，空间与性能代价高，属不推荐的回退形态。 |
| `--userns=keep-id` | 容器内 UID 与宿主用户 UID 对齐的用户命名空间选项。 |
| bind mount | 把宿主目录直接映射进容器的挂载方式，容器内不做特权挂载。 |
| XFS | graphroot 所在 `/dev/sda1` 的文件系统，满足 overlay 的底层要求。 |
| CIFS | Windows/SMB 共享文件系统；v2 远程方案全链路不经过它。 |
| G3 契约 | 组级 rootless 运行契约：`--device /dev/fuse`、`--security-opt label=disable`、`--cgroupns=host` 三必需，且禁用 `--privileged`。 |
| A1–A9 | 本规格的九项可测量验收标准，标准表与实测结果分列一篇。 |
| PASS / N/A | 验收判定用语；N/A 表示该项按默认策略不执行（如 A7 端口发布）。 |
| DEPRECATED | 已废弃标记，仅用于 v1.x 归档篇。 |

## 文档地图

| 文件 | 职责 | 何时读 |
|---|---|---|
| [09-1-backend-and-decision.md](09-1-backend-and-decision.md) | 预检事实基线、七概念分解、架构图、连接形态 A/B 对比、端口与访问策略 | 想了解方案依据与连接方式时先读 |
| [09-2-mounts-uid-storage.md](09-2-mounts-uid-storage.md) | 挂载与 UID 策略、graphroot 实际落点 | 排查读写属主或存储位置时 |
| [09-3-toolchain-provisioning.md](09-3-toolchain-provisioning.md) | LLVM 22 供给决策、Python 3.14 环境复用、附录 B 事实卡 | 准备补装工具链时 |
| [09-4-build-and-verify.md](09-4-build-and-verify.md) | 两库构建链复用点与验证方案（含命令块） | 实际构建、验证时照做 |
| [09-5-acceptance-and-evidence.md](09-5-acceptance-and-evidence.md) | A1–A9 标准表与实施结果（判定表、偏差 D1–D6、容器内配置、遗留问题） | 验收、复核证据时 |
| [09-6-risks-todos-changelog.md](09-6-risks-todos-changelog.md) | 风险矩阵、回滚方案、分阶段实施、Q1–Q6、附录 A/C | 做决策、回溯问题时 |
| [09-7-appendix-v1-wsl-deprecated.md](09-7-appendix-v1-wsl-deprecated.md) | v1.x WSL 本地后端全文归档（DEPRECATED） | 仅历史追溯，按需 |

## 推荐阅读顺序

1. **本索引**：先看状态结论、方案变更、硬约束、目标与非目标，其余细节按需下钻。
2. **架构与决策**：[09-1](09-1-backend-and-decision.md) 的预检基线、七概念、架构图与方案 A/B 对比。
3. **供给与构建**：[09-2](09-2-mounts-uid-storage.md) 挂载与 UID → [09-3](09-3-toolchain-provisioning.md) LLVM 22 与 Python 3.14 → [09-4](09-4-build-and-verify.md) 构建与验证命令。
4. **验收**：[09-5](09-5-acceptance-and-evidence.md) 对照标准与实测；[09-6](09-6-risks-todos-changelog.md) 风险、待确认与版本历史按需查阅；[09-7](09-7-appendix-v1-wsl-deprecated.md) 归档仅在追溯决策时阅读。

## 相关文档

- [文档站点首页](index.md)
- [09-1 预检基线、七概念与连接决策](09-1-backend-and-decision.md)
- [09-5 验收标准与实测证据](09-5-acceptance-and-evidence.md)
- [10 里程碑复盘（WSL → 远程 Podman）](10-milestone-retro-remote-podman.md)