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

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [工具链供给](09-3-toolchain-provisioning.md)
- [验收与实测证据](09-5-acceptance-and-evidence.md)
- [风险与待办](09-6-risks-todos-changelog.md)