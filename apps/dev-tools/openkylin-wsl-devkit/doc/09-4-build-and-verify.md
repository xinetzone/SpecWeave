---
type: "Spec"
title: "npu-toolchain 远程后端：两库构建链复用点与验证方案"
frontmatter_spec_version: "v2.1.0-draft"
status: "implemented-draft（阶段 0–4 已实施，2026-11-03 实测）"
owner: "未指定"
part_of: "09-npu-toolchain-windows-host.md"
---

# npu-toolchain 远程后端：两库构建链复用点与验证方案

> **本篇职责**：记录 npu_tvm 与 npuusertools 的构建链复用点、关键命令与分阶段验证方案（含失败判定）。
> **本篇不负责**：验收标准与实测结果见[验收与实测](09-5-acceptance-and-evidence.md)；LLVM 22 供给决策见[工具链供给](09-3-toolchain-provisioning.md)；风险与回滚见[风险与待办](09-6-risks-todos-changelog.md)。

## 5. 两库构建链复用点

| 环节 | 现状 | v2 动作 |
|---|---|---|
| 镜像 | `localhost/openkylin-npu-toolchain:3.0`（14 GB，已构建） | 复用；仅当需要 LLVM 22 固化进镜像时重建 |
| 容器 | `npu-toolchain` Up 22h，bind + volume 已就位 | 复用；重建时补 `--userns=keep-id` |
| npu_tvm C++ | `/opt/build/npu_tvm/libtvm.so` 已存在 | 复用；若换 LLVM 22 则重编 |
| npu_tvm Python | **未安装**（`ModuleNotFoundError: tvm`） | `pip install -e python` 或 `PYTHONPATH` 指向 `python/` |
| npuusertools C++ | `/opt/build/npuusertools` 已存在 | 复用；`build.sh` 幂等 |
| npuusertools Python | **未安装**（`ModuleNotFoundError: xmnn`） | `pip install -e .`（需补 `scikit-build-core`、`setuptools-scm`） |
| 构建脚本 | `scripts/{all-in-one,build-image,run,verify}.sh` | 直接复用；`scripts-host/preflight-wsl.sh` 随 v1.x 废弃 |

**关键命令（沿用服务器侧已验证形态）**：

```bash
# npu_tvm（LLVM 22 显式指定，避免 PATH 隐式解析到 20/21）
cmake -G Ninja -S /workspace/ai/notebook/libs/npu_tvm -B /opt/build/npu_tvm \
  -DUSE_CODEGENC=ON -DUSE_LLVM=/opt/build/llvm22/bin/llvm-config
ninja -C /opt/build/npu_tvm tvm

# npuusertools
BUILD_DIR=/opt/build/npuusertools bash /workspace/ai/notebook/libs/npuusertools/scripts/build.sh
```

## 6. 验证方案

| 阶段 | 命令 | 对应验收 |
|---|---|---|
| V0 连通 | `ssh -o BatchMode=yes ai@10.16.11.3 'whoami'` | A1 |
| V1 存储 | `podman info --format '{{.Host.Security.Rootless}} {{.Store.GraphDriverName}} {{.Store.GraphRoot}}'` + `findmnt -T <graphroot>` | A2 |
| V2 LLVM | 宿主/容器各执行 `llvm-config --version`，并校验 `--libdir`、`--includedir` | A3 |
| V3 挂载与属主 | 容器内 `stat` + `touch /workspace/ai/.temp/.probe` | A8 |
| V4 两库 | `ninja` + `import tvm`；`build.sh` + `pip install -e .` + `import xmnn` | A4/A5 |
| V5 契约 | `podman inspect` 校验 `Privileged/CgroupMode/UsernsMode/SecurityOpt` | A6 |
| V6 端口 | 按需发布后 Windows `Test-NetConnection` | A7 |
| V7 容量 | `df -hT /media/pc/data` 的 `Avail` ≥ 50 GB | A9 |

**失败判定**：任一验收项 FAIL 即停止后续步骤，先修复再前进；长构建一律在 `tmux` 中执行并留存日志。

## 7. 镜像重建与挂载契约（`3.0-minimal` 重基线）

### 7.1 复现口径

> **正确表述**：**镜像 + `npu-build` 卷**可复现，不是「镜像自身可复现」。

镜像只提供解释器与工具链（Python 3.14 环境、gcc、cmake、ninja、zlib），**不烘入** `tvm` / `xmnn` 任何实体。运行时可见的 Python 层由两部分组成：

| 组成 | 落点 | 由谁产生 | 是否在镜像层 |
|---|---|---|---|
| `npu-toolchain.pth`（唯一允许在镜像内的东西，3 行纯指针） | `/opt/conda/envs/main/lib/python3.14/site-packages/npu-toolchain.pth` | 配方 Layer 3b | 是（纯文本指针） |
| `libtvm.so`、`llvm22/`、`userbase/`（xmnn 安装） | volume `npu-build` → `/opt/build` | `all-in-one.sh` S5/S6/S7 | 否 |
| tvm Python 源码 | bind `/media/pc/data/ai:/workspace/ai` | 工作区仓库 | 否 |

版本口径：卷由 S6/S7 重建，**版本随源码前进**——当前源码树（`V1.0.0-127-gd9c48d1c`）会产出 `xmnn 1.0.1.dev127`；卷内冻结的是 `1.0.1.dev120`（2026-11-03 安装）。验收基线取卷内现值 `dev120`。

### 7.2 必需挂载（缺一即 A3/A4/A5 不可达）

| 挂载 | 支撑的检查项 | 缺失时的后果 |
|---|---|---|
| `-v npu-build:/opt/build` | A3（`/opt/build/llvm22/bin/llvm-config`）、A4（`libtvm.so`）、A5（S7 的 `userbase` 安装） | `/opt/build` 为空目录；`/var/opt/build -> /opt/build` 软链指向空处，`libtvm.so` 的 RUNPATH 段全部落空 |
| `-v /media/pc/data/ai:/workspace/ai` | A4（tvm Python 源码，见 `npu-toolchain.pth` 第 3 行）、A8（写入门禁）、A9（容量门禁） | `pth` 第 2/3 行指向不存在目录（`site.py` 静默跳过）→ `import tvm` 失败；A8 `mkdir` 失败；A9 `df` 无目标 |
| `-v npu-build:/opt/build` 与 `/var/opt/build` 软链的配合 | 反向补上 minimal 根的 usr-merge 缺失：旧基 `/opt -> /var/opt`，minimal 基无此等价关系 | `ldd libtvm.so` 会落到系统 `libllvm22`（147,600,808 B）而非 conda-forge 的 `22.1.8`（195,933,536 B） |

### 7.3 缺挂载时的预期失败形态（`verify.sh` 已保证可读）

`verify.sh` 在触碰解释器之前先做挂载门禁（`has_mount()` 读 `podman container inspect` 的 `.Mounts` 目标路径）：

| 场景 | 预期输出（A3 / A4 / A5） |
|---|---|
| 缺 `npu-build` | `npu-build 卷未挂载到 /opt/build（A3 依赖 /opt/build/llvm22）` / 同型 A4 文案 / `npu-build 卷未挂载到 /opt/build（A5 依赖 S7 安装的 xmnn）` |
| 有卷但 S5/S6/S7 未跑 | `npu-build 卷已挂载，但缺少 /opt/build/llvm22/bin/llvm-config（S5 LLVM 供给未执行）` 等，逐项区分「未挂载」与「未构建」 |
| 缺 `/workspace/ai` | A4：`/workspace/ai 绑定挂载缺失（A4 依赖 tvm python 源码，见 npu-toolchain.pth）`；A8/A9 各自给出同因文案 |

改造原则：**只改判定，不改镜像**（不在镜像里加任何检测脚本或实体）。

> **变体镜像走仓库配方**：下面这块构建的是 `openkylin-npu-toolchain:3.0-minimal`（不是 7.4 的两个基线 tag）。配方已回写仓库 `variants/npu-toolchain/Containerfile`，基线由 `ARG BASE_IMAGE` 注入；`.temp` 下的 `Containerfile.minimal*` 已随 `rebase-20261104` 清理废弃，勿再引用。

```bash
cd /media/pc/data/ai/notebook/dev/libs/AI/apps/dev-tools/openkylin-wsl-devkit/apps/openkylin-dev-container/variants/npu-toolchain

# 变体镜像：仓库 Containerfile + 基线 tag 作 build-arg（上下文即变体目录）
podman build --network host --format docker \
  --build-arg BASE_IMAGE=localhost/openkylin:3.0-minimal-gcc \
  -t localhost/openkylin-npu-toolchain:3.0-minimal \
  -f Containerfile .
```

上述路径已用独立 tag `localhost/openkylin-npu-toolchain:3.0-repo-check` 真构建验证：420 s、16 步、exit 0，随后 `verify.sh` 为 13 PASS / 1 N/A / 0 FAIL。

### 7.4 基线镜像的两步产出（脚本化，`scripts/build-minimal-base.sh`）

`3.0-minimal` 与 `3.0-minimal-gcc` 由脚本产出，不再依赖 `.temp` 中的临时脚本或包清单：

```bash
cd /media/pc/data/ai/notebook/dev/libs/AI/apps/dev-tools/openkylin-wsl-devkit/apps/openkylin-dev-container/variants/npu-toolchain

bash scripts/build-minimal-base.sh                # 幂等：已存在则逐步 SKIP（仍复跑只读断言），退出码 0
bash scripts/build-minimal-base.sh --force        # 强制重建；旧镜像保留为 <none>，不删除任何对象
bash scripts/build-minimal-base.sh /path/to/openKylin-3.0-wsl-amd64.wsl   # 换源文件
```

| 步骤 | 产出 tag | 动作 | 断言 |
|---|---|---|---|
| S1 | `localhost/openkylin:3.0-minimal` | `podman import` 官方 rootfs（sha256 内置校验） | os-release `openkylin / 3.0 / huanghe`、`ldd` 可用、镜像内无 tvm/xmnn 实体、`gcc` 不存在 |
| S2 | `localhost/openkylin:3.0-minimal-gcc` | `podman build` 补 gcc 15.2.0（apt 25 包） | 同上 + `gcc --version` 含 `15.2.0` + `dpkg-query` 25/25 |

`--force` 前会检查目标 tag 是否被任一容器（含已停止）使用，命中即中止；脚本从不 `rmi`/`prune`。三口径逐步打印：`df -B1` 差（**准**）、`podman images` SIZE、容器内 `du -sb --one-file-system /`。实体断言只读复用 `verify.sh` 的表达式，不修改 `verify.sh`。

复现实测（2026-11-05，`--force`）：S1 22 s / S2 240 s（其中 apt 取包 3 min 6 s，305 kB/s）；`df` 增量 S1 20,480 B（同 ID 去重）/ S2 255,614,976 B；`podman images` SIZE 2,365,215,839 B / 1,456,141,985 B；`du` rootfs 1,162,377,061 B / 1,306,094,039 B。

**源文件校验值**：`openKylin-3.0-wsl-amd64.wsl` 的实测 sha256 为 `d6d0d708c54bbc643961aba21d74c0b18270715bdf2266ecec3bc55f486d07d4`（352,431,812 B）。脚本在 `podman import` 前校验该值，不匹配即退出。**限定**：该值只能证明本地文件未发生变化；官方未发布该文件的校验值，因此不能用它声称"与官方发布逐字节一致"。

**默认值切换条件**：仓库 `Containerfile` 的 `ARG BASE_IMAGE` 默认值与 `all-in-one.sh` 的 `BASE_IMAGE` 仍指向 `localhost/openkylin:3.0`；当该镜像退役时，两处一并切换为 `localhost/openkylin:3.0-minimal-gcc`。

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [工具链供给](09-3-toolchain-provisioning.md)
- [验收与实测证据](09-5-acceptance-and-evidence.md)
- [风险与待办](09-6-risks-todos-changelog.md)