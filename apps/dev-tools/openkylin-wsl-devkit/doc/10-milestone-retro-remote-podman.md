---
type: "Report"
title: "里程碑复盘：从 WSL 本地后端转向远程 rootless Podman（npu-toolchain）"
report_version: "v1.0"
date: "2026-11-03"
status: "final（事实截至 2026-11-03）"
owner: "未指定"
part_of: "09-npu-toolchain-windows-host.md"
source: "本会话执行记录（2026-11-01 至 2026-11-03）＋ 09-1～09-7 与 09 入口文档实测数据"
---

# 里程碑复盘：从 WSL 本地后端转向远程 rootless Podman（npu-toolchain）

> **本篇职责**：按七概念（R-I-E-C-A-F-V）复盘一次方案级转向——从「Windows 宿主 WSL + OpenKylin + 本地 rootless Podman」改为「Windows 经 SSH 使用 10.16.11.3 的 rootless Podman」，并记录失败路径、决策依据、可复用命令与量化结果。
> **本篇不负责**：技术方案与决策依据见[架构与决策](09-1-backend-and-decision.md)；挂载与 UID 见[挂载与存储](09-2-mounts-uid-storage.md)；工具链供给见[工具链供给](09-3-toolchain-provisioning.md)；构建命令见[构建与验证](09-4-build-and-verify.md)；验收判定见[验收与实测](09-5-acceptance-and-evidence.md)；风险与待确认项见[风险与待办](09-6-risks-todos-changelog.md)；v1.x 全文见[归档篇](09-7-appendix-v1-wsl-deprecated.md)。

## 0. 结论摘要

- **方案层**：v1.x 的 WSL 本地后端被两条**不可协商的系统边界**否决——D: 盘容量（112 GB 总量，峰值后仅剩 8.82 GB）与 `vmcompute`/`wslservice` 的系统级独占锁（`E_UNEXPECTED` / `E_ILLEGAL_STATE_CHANGE`）。转向 10.16.11.3 远程 rootless Podman 后，阶段 0–6 全部落地。
- **能力层**：容器内 LLVM **22.1.8**、Python **3.14.10**；`libtvm.so` 按 LLVM 22 **重编完成**（854 目标 rc=0，`ldd` → `libLLVM.so.22.1`，79,226,112 B）；`import tvm` **0.19.0**、`Target("llvm")` / `Target("ccompiler")` 可解析、`import xmnn` **1.0.1.dev120**。
- **文档层**：`doc/09-npu-toolchain-windows-host.md` 由 1171 行单体重构为 8 篇（合计 1346 行），入口保留原编号，v1.x 归档为 DEPRECATED 独立篇。
- **治理层**：回收 **≈28.3 GB**（D: 25.19 GB + XFS 3.0 GB + 后续 75.6 MiB）；`.temp` 删除 6,904 文件 / 3,001,480,000 B；D:\WSL 清理 4 个空目录。

**核心洞察**

1. 这个任务的真实瓶颈不是「能不能编」，而是「存储语义 + 系统服务权限」——两者都在操作系统边界之外，工具链再全也无法绕过。
2. 远程环境不是新建，而是**接管**：14 GB 镜像、Up 22 小时的容器、已存在的 `libtvm.so` 都已就位，真实缺口只有「Python 包层」与「LLVM 22 入容器」两项。
3. `import tvm` 成功不代表验收通过：既有 `libtvm.so` 是 LLVM 21 链接产物，与容器内 LLVM 22 门禁错配，必须显式 `-DUSE_LLVM` 重编，否则是「假通过」。
4. 链接期决定运行期：`-DUSE_LLVM` 的绝对路径被 **rpath 固化**进二进制，`/opt/build/llvm22` 由此成为不可删的隐含运行时依赖。
5. 文档原子化的安全网是版本控制：`doc/*.md` 在本仓库呈**未跟踪**状态，拆分前原件没有 Git 兜底，只能靠 `.temp` 里的整档副本。

**最值得复用的一条**：**先做「可行性探测」再定存储方案**——在 v1.x 花了数轮尝试才发现 S: 是网络盘（DriveType=4），而 `wsl --import` 强制要求本地固定磁盘（DriveType=3）。一次 `Get-Volume`/`DriveType` 探测就能把整条路线判死，成本不到一分钟。

## 1. 目标与边界

### 1.1 原始需求

在 Windows 侧获得一个**可持续使用**的 npu_tvm 与 npuusertools 构建/运行环境，源码位于共享盘 `\\10.16.11.3\ai`（远程侧即 `/media/pc/data/ai`），且不牺牲宿主可用空间。

### 1.2 约束

| # | 约束 | 来源 | 实际执行情况 |
|---|---|---|---|
| C1 | 源码通过共享盘挂载使用，不在容器内复制源码树 | 需求 | bind `/media/pc/data/ai → /workspace/ai`（rw） |
| C2 | rootless，禁用 `--privileged`，遵守组级 G3（`--security-opt label=disable`、`--cgroupns=host`、容器内不执行 mount） | 组级契约 | 容器 `Privileged=false`、`CgroupMode=host`、`SecurityOpt=[label=disable]` |
| C3 | 不膨胀 D: 盘 | 需求 | 清理前 D: 8.82 GB → 34.01 GB；后续只删不增 |
| C4 | 两库跑通：`import tvm`、`Target("llvm")`、`Target("ccompiler")`、`import xmnn` | 验收 A4/A5 | 全部 rc=0 |
| C5 | 不改两库源码（除最小必要修复并说明） | 需求 | 未改源码；仅新增容器内运行时配置（`.pth`、`/etc/profile.d/tvm.sh`） |
| C6 | 不提交凭据、不发布容器端口 | 需求 | 复用既有 SSH 密钥免密；`PortBindings=map[]` |
| C7 | 长命令用 tmux 或足够超时并保留日志 | 需求 | 重编在远程执行并留日志 |

### 1.3 非目标

- 不在 Windows 侧导入任何 WSL 发行版（v1.x 已废弃）。
- 不做 NPU 硬件推理或精度验证（需板端）。
- 不重建 `npu-toolchain` 的变体逻辑；构建链沿用服务器侧 `all-in-one.sh`。
- 不支持 free-threading Python（`Py_GIL_DISABLED=0`，cp314 GIL 版）。
- 不启用容器内 sshd、不预置常驻服务；Jupyter 仅在明确需要时按需启动。
- 本轮不做 `verify.sh` 更新（阶段 7 未启动）。

## 2. 七概念分述

> 概念映射：本报告按委托方给定的七个标题组织，括号内为一对一的方法论代号——第一性原理（**F**）、结构化分解（**A**）、对抗审查（**V**）、洞察（**I**）、原子化交付（**C**）、验证与证据（**R/E**）、演进与复用（**E**，跨场景迁移）。

### 2.1 第一性原理（F）：三条不可协商的硬边界

**F1 存储语义边界。** overlay 驱动要求底层文件系统提供 d_type、user xattr、hardlink、flock 四项能力。SMB/CIFS 不提供完整语义；而 `wsl --import` 又强制要求 `ext4.vhdx` 落在 **DriveType=3（本地固定磁盘）**，预检实测 **S: 盘是 DriveType=4（网络盘）**，D: 是唯一可选落点。远程侧 `/dev/sda1` 为 **XFS**，实测 `GraphDriverName=overlay`，因此 v2 全链路不经过 CIFS，v1.x 对「overlay 落到 CIFS 会回退 vfs」的担忧整体消失。

**F2 系统服务边界。** `vmcompute` / `wslservice` 以 **SYSTEM** 身份持有 9.5 GB tar 的独占句柄，非管理员会话无法释放；而 UAC 提权无法在自动化会话内完成交互。这不是脚本写法问题，是 Windows 服务权限模型，任何重试都不会收敛。

**F3 链接期决定运行期。** `libtvm.so` 的 LLVM 依赖由构建期 `-DUSE_LLVM=<绝对路径>` 决定，并写入二进制（rpath）。因此「运行期可用」这件事由**构建期的一个绝对路径**决定，而这个路径一旦被删除，二进制的 `dlopen` 立即失败。版本一致性因此是硬验收项，不是软性建议。

### 2.2 结构化分解（A）：阶段与职责

| 阶段 | 职责 | 完成判据 | 状态（2026-11-03） |
|---|---|---|---|
| 0 | 规格确认（v2.0.0-draft） | 人类批准 | 已批准（Q1/Q2/Q5 放行） |
| 1 | 只读预检，落事实基线 | 基线表全部有实测值 | 完成 |
| 2 | 连接落地（方案 A，暂不改默认） | `podman --remote info` 通过 | 完成（缺陷 D1 已修复） |
| 3 | 容器重建 + LLVM 22 + Python 包层 | A3/A6/A8 PASS | 完成 |
| 4 | 两库构建 | A4/A5 PASS | 完成（A4 经重编修正） |
| 5 | 端口按需发布 | A7 PASS | 未执行（默认不发布，记 N/A） |
| 6 | 端到端复核与容量复核 | A1–A9 全 PASS，余量 ≥ 50 GB | 完成（A7 N/A，余量 295 GB） |
| 7 | 文档定稿与 `verify.sh` 更新 | 脚本与规格一致 | 部分完成（文档已定稿，脚本未启动） |

职责拆分的实际价值：阶段 3 与阶段 4 被拆开后，才暴露「复用既有 `libtvm.so`」与「LLVM 22 门禁」之间的冲突——两者若合并在一个「构建与验证」大步骤里，这个冲突会被 `import tvm` 的成功掩盖。

### 2.3 对抗审查（V）：被证伪的假设

| # | 曾被当作前提的假设 | 攻击视角 | 实测结果 | 处置 |
|---|---|---|---|---|
| V1 | S: 盘可用于 WSL 发行版落盘 | 新人视角：为什么先试 S: | **证伪**：S: 为 DriveType=4 网络盘，`wsl --import` 只接受 DriveType=3 | 改 D:，随后仍因容量失败 |
| V2 | 管理员权限可在自动化会话中自动获取 | 魔鬼代言人：UAC 怎么办 | **证伪**：无法在无人值守会话内完成 UAC 交互，多次导入以 `E_UNEXPECTED` / `E_ILLEGAL_STATE_CHANGE` 终止 | 放弃 WSL 路线 |
| V3 | 宿主 py314 的 conda 环境可直接挂进容器复用 | 新人视角：何必再装一遍 | **证伪**：`llvm-config --prefix` 指向宿主路径，容器内不存在该路径，`LLVMConfig.cmake` 失效；且跨发行版 glibc 差异不可控 | 容器内 conda 安装 `llvmdev=22.1.*` |
| V4 | `podman --connection <name>` 在 Windows 客户端可靠 | 未来视角：客户端与服务器版本不一致怎么办 | **证伪**：Windows podman 5.8.1 解析匹配实体 `Host` 块时主机名丢失，报 `dial tcp :22` | `~/.ssh/config` 用 `Match host 10.16.11.3` 规避 |
| V5 | 容器内可直接访问国内 conda 镜像 | 老板视角：外网可达性已测 200 | **证伪**：容器 IPv6 无路由，容器内解析失败；宿主侧正常 | 追加 `/etc/gai.conf` `precedence ::ffff:0:0/96 100`，并改走离线 `@EXPLICIT` 安装 |
| V6 | `pip install .` 可正常安装 npu_tvm | 新人视角：标准 PEP 517 流程 | **证伪**：卡在 `Preparing metadata`（构建后端与 3.14 环境组合未收敛） | 改 `.pth` 最小安装 + `TVM_LIBRARY_PATH` + `TEST_DATA_ROOT_PATH` |
| V7 | 复用既有 `libtvm.so` 即满足 A4 | 老板视角：既然能 import 就算过 | **部分证伪**：产物是 LLVM 21 链接，容器内门禁为 22.x；`import` 成功但后端版本错配 | 以 `-DUSE_LLVM=/opt/build/llvm22/bin/llvm-config` 重编 |
| V8 | `D:\WSL` 下 4 个目录清理后仍含残留 | 魔鬼代言人：删前不留底？ | **未证伪（成立）**：递归实测 4 项均 0 文件 / 0 子目录 | 逐项删除并复验 `GONE` |

结论：8 条假设中 6 条被实测证伪、1 条部分证伪。被证伪的假设**没有一条属于「工具链能力」**，全部属于「平台语义与权限」。

### 2.4 洞察（I）：五个四元组

**I1 环境已存在——动作应是「接管」而非「从零」。**
- 现象：远程已有 14 GB `openkylin-npu-toolchain:3.0` 镜像、Up 22 小时的同名容器、已存在的 `libtvm.so` 与 `npuusertools`。
- 根因：前序会话已在同一台机器完成镜像构建与容器运行，资产仍在。
- 影响：把「从零构建」的工作量（预估 15–25 GB、多轮镜像构建）压缩为「补两层依赖」。
- 建议：任何环境类任务开题先跑一次资产盘点（镜像 / 容器 / 卷 / 已构建产物），再决定是否新建。

**I2 真实缺口只有两项。**
- 现象：容器内 `import tvm`、`import xmnn` 均 `ModuleNotFoundError`，但 `libtvm.so` 与 `npuusertools` 源码均已就位。
- 根因：C++ 侧已通，Python 包层未安装；LLVM 22 未入容器。
- 影响：实际执行只需「conda 装 llvmdev + 装构建后端 + 建 Python 绑定」三步。
- 建议：先区分「C++ 产物缺失」与「Python 绑定缺失」，两者修复成本差一个数量级。

**I3 `import` 成功 ≠ 验收通过。**
- 现象：`import tvm` 返回 0.19.0，但 `ldd` 显示链接的是 LLVM 21 时期的产物，而规格要求 22.x。
- 根因：验收项被实现为「能 import」，而规格要求是「版本门禁 + 后端可解析」。
- 影响：若不重编，A4 会以「假通过」进入交付，后续 LLVM 相关算子行为不可预期。
- 建议：验收断言必须同时覆盖「可导入」「版本/链接对象」「目标可解析」三层。

**I4 客户端故障域与服务端故障域必须分离。**
- 现象：`--connection` 报 `dial tcp :22`（客户端解析缺陷），而同期 `ssh` 与远程 `podman` 完全正常。
- 根因：podman 5.8.1 客户端自带的 ssh_config 解析路径与服务端无关。
- 影响：若混用，会误判为服务器故障并做无效的远端排查。
- 建议：短命令走 A（`--connection`），长构建走 B（远程 tmux）；两侧分别留证。

**I5 文档原子化的安全网是版本控制。**
- 现象：拆分后核查发现 `doc/*.md` 在本仓库**未跟踪**（`git status` 为 `??`，`git log -- doc/09-...` 无提交）。
- 根因：文档目录长期以「共享盘 + 直接编辑」方式维护，未纳入提交。
- 影响：拆分前原件没有 Git 兜底，唯一整档副本只能留在 `.temp`（106,206 B / 1171 行），形成「临时目录承担不可再生资产」的结构性隐患。
- 建议：任何原子化/大改前，先确认目标文件在版本控制内；否则先落一份正式归档副本，再动原文。

### 2.5 原子化交付（C）：交付单元与独立验证

| 交付单元 | 产物 | 独立验证方式 |
|---|---|---|
| 连接层 | `remote-ai` 连接条目（`default=false`）+ `Match host` 配置 | `podman --remote --connection remote-ai info` → 5.6.2 / rootless / overlay |
| 容器层 | 同名容器 `npu-toolchain` 重建（`--userns=keep-id`） | 容器内 `id -u` = 1006；`/workspace/ai` 可写；`/opt/build` 内容保留 |
| 工具链层 | `/opt/build/llvm22`（22.1.8 + clang-22 + lld 23.1.4） | `llvm-config --version` = 22.1.8 |
| Python 层 | `.pth` 绑定 + `/etc/profile.d/tvm.sh` + 构建后端 | `import tvm` / 两个 Target / `import xmnn` 全 rc=0 |
| 二进制层 | 重编 `libtvm.so`（854 目标） | `ldd | grep libLLVM` → `libLLVM.so.22.1` |
| 文档层 | 09 入口 + 09-1～09-7（8 篇） | 相对路径链接可点；入口含文档地图与阅读顺序 |
| 治理层 | `.temp` 清理 + 台账登记 | 删前断言、删后复验 `No such file` |

### 2.6 验证与证据（R/E）

A1–A9 判定（完整证据见[验收与实测](09-5-acceptance-and-evidence.md)）：

| 项 | 判定 | 关键证据 |
|---|---|---|
| A1 远程 Podman 可用 | PASS | `podman info` → 5.6.2、rootless=true、overlay |
| A2 Windows 连接可用 | PASS | `--connection remote-ai info` 通过（缺陷修复后） |
| A3 LLVM 22 门禁 | PASS | `llvm-config --version` = 22.1.8 |
| A4 npu_tvm 可用 | PASS | `import tvm` 0.19.0；`ldd` 链接 `libLLVM.so.22.1` |
| A5 npuusertools 可用 | PASS | `import xmnn` 1.0.1.dev120 |
| A6 容器 UID 对齐 | PASS | 容器内 `uid=1006(ai)` |
| A7 端口发布 | **N/A** | `PortBindings=map[]`（默认不发布；Q4 已选 8888） |
| A8 挂载可读写 | PASS | `/workspace/ai` 内 `touch` 成功 |
| A9 容量门禁 | PASS | XFS 可用 295 GB ≥ 50 GB |

计数：**8 PASS / 1 N/A**。按全部九项计通过率 8/9 = 88.9%；按可判定项计 8/8 = 100%。两个口径同时给出，避免用「100%」掩盖 A7 未执行。

### 2.7 演进与复用（E）

**演进路径**：v1.0.0-draft（2026-11-01，WSL 本地后端）→ v1.2.0 / v1.3.0-draft（2026-11-02，LLVM 兼容性、D: 盘方案、容量基线）→ **v2.0.0-draft（2026-11-03，换后端）** → v2.1.0-draft（落地实施）→ v2.1.0-draft 补记 1–3（缺陷修复、清理）。换后端而非打补丁的判断依据：v1.x 的两条阻塞都在 OS 边界外，继续在 WSL 内做优化不会收敛。

**可迁移性**：Windows 侧零状态（仅 `~/.ssh/config` 的一个匹配块 + 一条 podman connection），换机器只需重建连接并要求远程具备 XFS + rootless Podman + 本地镜像。
**不可迁移的部分**：SMB/共享盘作为构建后端存储——这条在任何平台都不成立（见 §5(b)）。

## 3. 里程碑时间线

| 日期 / 时点 | 事件 | 结果 | 证据位置 |
|---|---|---|---|
| 2026-11-01 | 规格 v1.0.0-draft：WSL + OpenKylin + 本地 rootless Podman | 立项 | 09-6 附录 C |
| 2026-11-02 | v1.2.0-draft：LLVM 21/22 兼容结论、A8/A9、分层落盘 | 规格扩充 | 09-6 附录 C |
| 2026-11-02 | v1.3.0-draft：D: 盘方案、容量基线、Q9、阶段 1a/1b | 规格扩充 | 09-6 附录 C |
| 2026-11-02 02:04 | 远程镜像 `localhost/openkylin-npu-toolchain:3.0`（14 GB）已构建 | 复用基线就位 | 09-1 预检表 |
| 2026-11-02 13:11 | 既有 `libtvm.so` 为 LLVM 21 链接产物（`libtvm.so.bak-llvm21` 时间戳） | 隐含债务 | 容器内 `ls -l` |
| 2026-11-02 13:57 | `.temp/npu-toolchain` 验收证据目录建立 | 证据留存 | `.temp` 台账 |
| 2026-11-03 | WSL 导入失败（`E_UNEXPECTED` / `E_ILLEGAL_STATE_CHANGE`），D: 可用低至 8.82 GB | **路线判死** | 09 入口 §方案变更 |
| 2026-11-03 | v2.0.0-draft：转向远程后端，重写目标/验收/架构 | 方案切换 | 09-6 附录 C |
| 2026-11-03 | 只读预检：Ubuntu 22.04.5 / 48 vCPU / XFS 15T / rootless 5.6.2 / overlay | 基线落表 | 09-1 §1 |
| 2026-11-03 | `podman image prune -f` 回收 0 GB（dangling 为 tagged 镜像祖先层） | Q5 结案 | 09-6 §8 |
| 2026-11-03 | `--connection` 报 `dial tcp :22`；定位为客户端解析缺陷 | 缺陷定位 | 09-1 §4.1 |
| 2026-11-03 10:18:52 | `~/.ssh/config` 改为 `Match host 10.16.11.3`（631 B） | 连接恢复 | 文件 mtime |
| 2026-11-03 08:53:16 | 容器 `npu-toolchain` 同名重建（`Created` 时间戳） | 容器层就位 | `podman inspect` |
| 2026-11-03 | 容器内装 `llvmdev=22.1.8` + clang-22 + lld 23.1.4 | A3 达成 | 09-3 |
| 2026-11-03 | Python 构建后端补齐（cython / scikit-build-core / setuptools-scm / wheel） | 构建前置就位 | 09-3 |
| 2026-11-03 | `.pth` 最小安装替代 `pip install .`；新增 `/etc/profile.d/tvm.sh` | A5 达成 | 09-4 |
| 2026-11-03 10:24 | 重编 `libtvm.so` 完成（854 目标 rc=0，79,226,112 B） | A4 真通过 | 产物 mtime |
| 2026-11-03 | 09 文档原子化为 8 篇（1171 → 1346 行） | 文档层完成 | 09 入口 |
| 2026-11-03 10:46 | `.temp` 清理：6,904 文件 / 3,001,480,000 B 与 2 文件 / 97,370 B | XFS 292 → 295 GB | 清理日志 |
| 2026-11-03 | Q3/Q4 定案；删除 `libtvm.so.bak-llvm21` 与拆分脚本 | +79,253,504 B | 09-6 补记 3 |
| 2026-11-03 | `D:\WSL` 删除 4 个空目录（dl2 / downloads / OpenKylin-3.0 / spaces） | 结构收敛为 2 项 | 本次清理记录 |

> 说明：构建与依赖安装的**精确耗时未记录（unknown）**；上表只列有文件时间戳或命令输出支撑的时点，不据此推导耗时分布。

## 4. 决策复盘表

| # | 决策 | 当时依据 | 代价 | 结果 | 若重来会怎么做 |
|---|---|---|---|---|---|
| D-1 | 放弃 WSL 本地后端，转向远程 rootless Podman | D: 8.82 GB 不可持续；`vmcompute`/`wslservice` 独占锁无法在自动化会话内释放 | 前两日规格（v1.0–v1.3）整体作废，需重写目标与验收 | 成功，阶段 0–6 落地 | 同样切换；但把「盘型探测 + 服务锁探测」提到立项第一步，省掉两日规格 |
| D-2 | 方案 A（`podman-remote`）为主、方案 B（SSH + tmux）为必备并行路径 | A 与本地 CLI 一致、前置已满足；长构建不能受 SSH 会话影响 | 需维护两套调用习惯 | 成功：短命令用 A，重编走远程 | 不变 |
| D-3 | 不切换默认连接（保持 `podman-machine-default`） | 切换会影响既有 WSL 工作流 | 每次需显式写 `--connection remote-ai` | 成功（Q3 定案） | 不变 |
| D-4 | 重建同名容器并加 `--userns=keep-id` | 原容器 `UsernsMode=private`，容器内 UID 与宿主 1006 不一致 | 需重建容器（原容器仅 Up 22h，无长任务） | 成功：容器内 `uid=1006`，卷内容完整保留 | 不变 |
| D-5 | 先用既有 `libtvm.so`，不立即重编 | 减少一次全量构建；先验证 Python 层 | 随后发现 LLVM 21/22 错配，仍需重编（多一轮） | 先快后慢，最终重编通过 | 直接以版本门禁为准，先 `ldd` 再决定是否复用 |
| D-6 | 用 `.pth` 最小安装代替 `pip install .` | `pip install .` 卡在 `Preparing metadata` | 属非标准安装形态，需显式维护 `TVM_LIBRARY_PATH`/`TEST_DATA_ROOT_PATH` | 成功，且可复现 | 不变；但把运行时变量写进文档（已做） |
| D-7 | 修复 `--connection` 用 `Match host`，而非新建连接条目 | 缺陷在客户端 ssh_config 解析，不在凭据/URL | 每台 Windows 客户端需一次性配置 | 成功，连接稳定 | 在预检阶段就把 podman 客户端版本与 ssh 配置纳入检查项 |
| D-8 | 09 文档拆为 8 篇，保留 09 编号作入口 | 单文件数千行混装架构/实测/归档；外部链接不能失效 | 拆分与交叉引用校对成本 | 成功，1346 行覆盖 1171 行原文 | 拆分前先确认文档已纳入 Git（见 §5(f)） |
| D-9 | 默认不发布容器端口 | 安全默认；容器端口不可后加 | 需要 Jupyter 时须重建容器 | A7 记 N/A；Q4 已预选 8888 | 不变 |
| D-10 | 删除 `libtvm.so.bak-llvm21`（79 MB） | 删前 `import tvm`/`xmnn`/连接均通过；`grep` 确认无脚本/profile/rpath 引用 | 失去 LLVM 21 二进制回滚点（源码与 `llvm21` 目录仍在，可重编） | 已执行，回归全绿 | 保留至首次完整用例跑通后再删更稳 |

## 5. 失败路径萃取

**(a) 先做可行性探测，再定存储方案。**
- 现象：v1.x 在 D: 上反复尝试导入，直到容量跌至 8.82 GB 才发现路线不可行。
- 判据：`wsl --import` 要求 DriveType=3；S: 为 DriveType=4。该判据一条命令即可获得。
- 正确做法：立项 15 分钟内完成「盘型 / 容量 / 卷类型（VHDX 或目录）/ 服务占用」四项探测，再写规格。
- 反模式：先写完整规格再验证环境前提——规格越完整，返工越贵。

**(b) 共享盘与 overlay 的协议边界不可调。**
- 现象：v1.x 担心 overlay 落在 CIFS 上会回退 vfs；预检确认 CIFS 不满足 d_type/xattr/hardlink/flock 全套语义。
- 判据：`podman info` 的 `GraphDriverName` 是否为 `overlay`，以及底层文件系统类型与 `d_type` 支持。
- 正确做法：构建后端存储只用本地块设备文件系统（XFS/ext4）；共享盘只承载**源码与数据**，不承载镜像层与构建缓存。
- 反模式：用「网络盘挂载成功后能读写」推断「可以跑 overlay」——可读写 ≠ 满足 overlay 语义。

**(c) Windows 服务级锁只能靠权限突破，不能靠重试。**
- 现象：`vmcompute`/`wslservice` 以 SYSTEM 持有 tar 独占句柄，多次导入以 `E_UNEXPECTED` / `E_ILLEGAL_STATE_CHANGE` 终止。
- 判据：报错是否指向服务锁；`handle.exe` / 句柄检查是否能定位持有者。
- 正确做法：识别为服务级锁后立即止损，改换执行位置（远程主机），不在客户端反复重试。
- 反模式：把「再试一次」当作排障手段——对服务级锁的重试不会改变结果。

**(d) 既有环境优先于从零搭建。**
- 现象：远程已有 14 GB 镜像、运行中的容器、已构建的 `libtvm.so`。
- 判据：资产盘点清单（`podman images` / `ps -a` / 卷内已构建产物）是否显示目标已存在。
- 正确做法：先盘点、再接管、最后补缺口；把「新建」作为兜底而非首选。
- 反模式：为「干净」而重建一切——会重复付出前序会话已经付出的构建成本。

**(e) rpath 隐含的运行时依赖必须显式记录。**
- 现象：`libtvm.so` 的 `ldd` 指向 `/var/opt/build/llvm22/lib/libLLVM.so.22.1`（即宿主 `/opt/build/llvm22`）。
- 判据：`ldd <so> | grep -E "libLLVM|not found"`，以及 `readelf -d` 的 RUNPATH 项。
- 正确做法：在规格中把「构建期绝对路径 → 运行期不可删目录」作为显式约束登记（已写入 09-5 §9.4 与本篇 §8）。
- 反模式：只记录「构建成功」，不记录「运行时还依赖哪些绝对路径」。

**(f) 文档原子化与版本控制的关系。**
- 现象：拆分后核查发现 `doc/*.md` 未纳入 Git；拆分前原件唯一副本落在 `.temp`。
- 判据：`git status -- <path>` 是否显示 `??`；`git log -- <path>` 是否为空。
- 正确做法：原子化前先把原件纳入版本控制（或落一份正式归档），再拆分；`.temp` 只能放可再生中间件。
- 反模式：把「内容已拆分到 8 篇」当作「原件可以安全删除」——拆分覆盖内容，但不等于保有整档快照。

## 6. 可复用清单

### 6.1 连接与客户端配置

```bash
# 1) 新增远程连接（不切默认）
podman system connection add remote-ai \
  --identity %USERPROFILE%\.ssh\id_ed25519 \
  ssh://ai@10.16.11.3:22/run/user/1006/podman/podman.sock

# 2) 验证连接（显式指定，避免影响既有默认连接）
podman --remote --connection remote-ai info
podman --remote --connection remote-ai ps -a

# 3) 查看默认项（确认未被切换）
podman system connection ls
```

Windows podman 5.8.1 的 `--connection` 缺陷规避：`~/.ssh/config` 中目标主机必须写成**匹配块**而非实体 `Host` 块：

```
Match host 10.16.11.3
    HostName 10.16.11.3
    User ai
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
```

### 6.2 容器运行契约（实测 CreateCommand 原文）

```bash
podman run -d --name npu-toolchain \
  --userns=keep-id \
  --cgroupns=host \
  --security-opt label=disable \
  -v /media/pc/data/ai:/workspace/ai \
  -v npu-build:/opt/build \
  -w /workspace \
  localhost/openkylin-npu-toolchain:3.0 sleep infinity
```

检查项（重建后逐条核对）：

| 检查 | 期望 | 命令 |
|---|---|---|
| 非特权 | `Privileged=false` | `podman inspect npu-toolchain --format '{{.HostConfig.Privileged}}'` |
| cgroup | `host` | `--format '{{.HostConfig.CgroupMode}}'` |
| 安全选项 | `[label=disable]` | `--format '{{.HostConfig.SecurityOpt}}'` |
| 端口 | 空映射 | `--format '{{.HostConfig.PortBindings}}'` |
| UID 对齐 | 容器内 1006 | `podman exec npu-toolchain id -u` |
| 挂载可写 | `touch` 成功 | `podman exec npu-toolchain touch /workspace/ai/.probe` |
| 卷保留 | `/opt/build` 原内容在 | `podman exec npu-toolchain ls /opt/build` |

### 6.3 容器内工具链补装（离线 conda）

```bash
# 1) 容器内 IPv6 无路由时，优先 IPv4
echo 'precedence ::ffff:0:0/96 100' >> /etc/gai.conf

# 2) 离线 @EXPLICIT 安装（宿主下载、容器内 --offline）
conda create -p /opt/build/llvm22 --offline \
  --file explicit-llvmdev-22.1.txt   # @EXPLICIT 清单
# 包缓存与 HOME 需重定向，避免写满容器内临时层
export CONDA_PKGS_DIRS=/opt/build/conda-pkgs
export HOME=/opt/build/home

# 3) 校验
/opt/build/llvm22/bin/llvm-config --version    # 期望 22.1.8
/opt/build/llvm22/bin/llvm-config --libdir     # 目录必须存在
ls /opt/build/llvm22/include/llvm              # 头文件必须存在
```

### 6.4 Python 包层最小安装（npu_tvm）

```bash
# 构建后端
pip install "scikit-build-core>=1.0" "setuptools-scm>=8.0" wheel cython

# .pth 绑定源码 python/，免全量 pip install
echo '/workspace/ai/notebook/libs/npu_tvm/python' \
  > /opt/conda/envs/main/lib/python3.14/site-packages/npu_tvm.pth

# 运行期变量（写入 profile，务必用 bash -lc 执行才生效）
cat > /etc/profile.d/tvm.sh <<'EOF'
export TVM_LIBRARY_PATH=/opt/build/npu_tvm
export TEST_DATA_ROOT_PATH=/opt/build/tvm_test_data
EOF
```

### 6.5 构建与验收命令

```bash
# 重编（显式绝对路径，禁止 PATH 隐式解析）
cmake -S /workspace/ai/notebook/libs/npu_tvm -B /opt/build/npu_tvm \
  -G Ninja -DUSE_LLVM=/opt/build/llvm22/bin/llvm-config
ninja -C /opt/build/npu_tvm tvm

# 二进制层断言
ls -l /opt/build/npu_tvm/libtvm.so*
ldd /opt/build/npu_tvm/libtvm.so | grep -E "libLLVM|not found"

# 运行层断言（必须走 bash -lc，否则 profile 不生效）
podman exec npu-toolchain bash -lc '
python -c "import tvm;print(tvm.__version__);print(tvm.target.Target(\"llvm\"));print(tvm.target.Target(\"ccompiler\"))"
python -c "import xmnn,importlib.metadata as m;print(m.version(\"xmnn\"),xmnn.__file__)"
'
```

### 6.6 排障判据表

| 症状 | 判据 | 处置 |
|---|---|---|
| `dial tcp :22` | 客户端 ssh_config 匹配块是否为实体 `Host` | 改 `Match host <ip>` |
| `PermissionError: /workspace/.tvm_test_data` | 是否缺 `TEST_DATA_ROOT_PATH`；是否未走 `bash -lc` | 补 profile 变量并用 `bash -lc` |
| 宿主 `ls /opt/build/...` 报 `No such file` | `/opt/build` 是容器 volume，不是宿主路径 | 断言写进 `podman exec` 内 |
| `podman exec -e VAR=...` 后变量缺失 | 未加载 profile | 统一用 `bash -lc` |
| `pip install .` 卡 `Preparing metadata` | 构建后端与 Python 3.14 组合 | 改 `.pth` 最小安装 |
| 容器内 conda 解析失败、宿主正常 | 容器 IPv6 无路由 | `/etc/gai.conf` 优先 IPv4 + 离线 `@EXPLICIT` |
| `podman system df` 报 infra-container 缺失 | libpod 临时目录残留缺失 | 用 `df`/`du -sh` 替代统计（非阻塞） |

### 6.7 清理门禁（断言式删除）

1. **先取证**：文件数、字节和、逐文件 `sha256sum`、`du -sb`、删除前 `df`。
2. **先验活**：目标资产删除前先跑一次真实入口（`import tvm` 等），确认功能不依赖待删项。
3. **查引用**：`grep` 待删路径于脚本、`profile.d`、文档、`readelf` 的 RUNPATH。
4. **逐项删**：禁通配符；每项单独 `rm` 并记录返回码。
5. **删后复验**：路径不存在 + 功能回归 + `df` 差值；差值应≈删除字节数（含元数据小量偏差）。

## 7. 量化结果

| 指标 | 数值 | 来源 |
|---|---|---|
| D: 可用空间 | 8.82 GB → 34.01 GB（**+25.19 GB**） | 09-5 D6 |
| XFS 可用空间（`.temp` 清理） | 292 GB → 295 GB（**+3 GB**） | 清理日志 |
| XFS 可用字节（旧库备份清理） | 316,398,936,064 → 316,478,189,568 B（**+79,253,504 B**） | `df --output=avail -B1` |
| 回收合计 | **≈28.3 GB**（三段相加，非单次测量） | 上三行 |
| 构建目标数 | **854**（`ninja` rc=0） | 重编日志 |
| `libtvm.so` 体积 | 79,226,112 B（重编后） | 容器内 `ls -l` |
| 验收通过 | **8 PASS / 1 N/A**（可判定项 8/8 = 100%；全九项 8/9 = 88.9%） | 09-5 |
| 文档规模 | 8 篇 / **1346 行**（原 1171 行，+14.9%） | `wc -l` |
| `.temp` 删除 | 6,904 文件 / 3,001,480,000 B + 2 文件 / 97,370 B | 清理断言 |
| Windows 侧删除 | `config.bak-20261103-split` 596 B；`D:\WSL` 4 个空目录（0 文件） | 本次清理记录 |
| 构建耗时 | **unknown**（未记录） | — |
| 依赖安装耗时 | **unknown**（未记录） | — |
| 文档拆分耗时 | **unknown**（仅有目录 mtime 10:06 与 09-1 mtime 10:27 两个时点） | — |

## 8. 遗留与下一步

| # | 项 | 现状 | 建议 |
|---|---|---|---|
| 1 | Q3 默认连接 | 保持 `podman-machine-default`；`remote-ai` 需显式调用 | 维持现状；如需切换，走 `podman system connection default remote-ai`，须另行批准 |
| 2 | Q4 Jupyter 端口 | 选定 8888→8888（备用 8894），双检通过，但**未发布** | 需要时重建容器并加 `-p 0.0.0.0:8888:8888`；届时 A7 可转 PASS |
| 3 | `podman system df` infra-container 瑕疵 | 仍报 `lstat /run/user/1006/libpod/tmp/infra-container` | 非阻塞；统计改用 `df`/`du`；修复需重建 infra 容器 |
| 4 | `doc/*.md` 未纳入 Git | `??` 未跟踪，历史无提交 | 建议纳入版本控制，否则归档与回滚只能靠 `.temp` 副本 |
| 5 | `/opt/build/llvm22` 不可删 | `libtvm.so` 的 rpath 依赖该目录 | 在运维层面标记为受保护路径；删除前必须 `ldd` 复验 |
| 6 | LLVM 21 回滚点已删 | `libtvm.so.bak-llvm21` 已清理 | 回滚路径改为「用 `/opt/build/llvm21` 重编」，须预留一次重编时间 |
| 7 | `.temp/npu-toolchain/`（254 MB） | 被 `run.sh` / `verify.sh` / `all-in-one.sh` 硬编码引用 | 保留；如需清理须先改脚本常量 |
| 8 | `.temp/doc09-atomize/original-backup.md` | 拆分前原件唯一整档副本（未纳入 Git） | 迁入正式归档后删除，需批准 |
| 9 | `verify.sh` 与规格一致性（阶段 7） | 未启动 | 按 A1–A9 重写断言，纳入自动化 |

## 附录 A：证据与引用

- 方案与预检基线：[09-1-backend-and-decision.md](09-1-backend-and-decision.md)（含 §4.1 `--connection` 缺陷根因）
- 挂载与 UID：[09-2-mounts-uid-storage.md](09-2-mounts-uid-storage.md)
- 工具链供给：[09-3-toolchain-provisioning.md](09-3-toolchain-provisioning.md)
- 构建与验证命令：[09-4-build-and-verify.md](09-4-build-and-verify.md)
- 验收标准与实测：[09-5-acceptance-and-evidence.md](09-5-acceptance-and-evidence.md)
- 风险、Q1–Q6、版本历史：[09-6-risks-todos-changelog.md](09-6-risks-todos-changelog.md)
- v1.x 归档（DEPRECATED）：[09-7-appendix-v1-wsl-deprecated.md](09-7-appendix-v1-wsl-deprecated.md)

> 本篇所有数字均取自上述文档的实测记录或本会话命令输出；未记录项已标注 `unknown`，未作估算填充。

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [验收与实测证据](09-5-acceptance-and-evidence.md)
- [风险、待办与版本历史](09-6-risks-todos-changelog.md)
