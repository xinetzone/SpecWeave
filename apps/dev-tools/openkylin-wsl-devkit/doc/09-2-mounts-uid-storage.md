---
type: "Spec"
title: "npu-toolchain 远程后端：挂载、UID 与存储落点"
frontmatter_spec_version: "v2.1.0-draft"
status: "implemented-draft（阶段 0–4 已实施，2026-11-03 实测）"
owner: "未指定"
part_of: "09-npu-toolchain-windows-host.md"
---

# npu-toolchain 远程后端：挂载、UID 与存储落点

> **本篇职责**：给出容器挂载方式、UID 对齐策略与存储落点约束。
> **本篇不负责**：预检事实基线与连接方案见[架构与决策](09-1-backend-and-decision.md)；构建与验证命令见[构建与验证](09-4-build-and-verify.md)；容量门禁判定与实测证据见[验收与实测](09-5-acceptance-and-evidence.md)。

## 3.2 挂载与 UID 策略

| 项 | 策略 | 理由 |
|---|---|---|
| 源码挂载 | 宿主 `/media/pc/data/ai` 直接 bind 到容器 `/workspace/ai`（`bind rw`） | 与 v1.x 的容器路径一致，构建脚本零改动；XFS 支持 overlay 所需全部特性 |
| 构建目录 | 命名卷 `npu-build` → `/opt/build`（落在 graphroot 同盘） | 构建产物不入源码树；卷随镜像生命周期管理，便于清理 |
| UID | 新建/重建容器时用 `--userns=keep-id`（宿主 1006 → 容器 1006） | 源码目录 777 虽允许 `private` 写入（现状 `WRITE_OK`），但 `keep-id` 让新建文件的属主与宿主一致，避免后续 git 操作出现 `dubious ownership` |
| CIFS | **完全不需要** | 远程已是本地盘；无凭据、无 `cifs-utils`、无 mount 探针 |
| 运行契约 | `--cgroupns=host` + `--security-opt label=disable`；需嵌套 podman 时再加 `--device /dev/fuse` | 组级 G3 |

graphroot 的实际落点见[预检事实基线](09-1-backend-and-decision.md)：`GraphRoot=/home/ai/.local/share/containers/storage` 软链至 `/media/pc/data/ai/.agents/podman-storage/storage`，所在 `/dev/sda1` 为 **XFS**。磁盘余量门禁见 [A9 磁盘余量门禁](09-5-acceptance-and-evidence.md)。

## 相关文档

- [入口索引](09-npu-toolchain-windows-host.md)
- [架构与决策](09-1-backend-and-decision.md)
- [工具链供给](09-3-toolchain-provisioning.md)
- [验收与实测证据](09-5-acceptance-and-evidence.md)