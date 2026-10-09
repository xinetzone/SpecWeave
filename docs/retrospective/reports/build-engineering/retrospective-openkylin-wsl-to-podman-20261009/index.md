---
id: "retrospective-openkylin-wsl-to-podman-index"
title: "openKylin WSL→podman 镜像转换里程碑复盘 索引"
date: "2026-10-09"
type: "index"
---

# openKylin WSL→podman 镜像转换里程碑复盘

| 项 | 值 |
|---|---|
| 报告 | [README.md](README.md) |
| 日期 | 2026-10-09 |
| 链路 | R→I→E→V→C（里程碑复盘） |
| 核心结论 | podman machine（WSL 后端）虚拟机空闲回收是连接反复失效根因；keep-alive 常驻可解；VM 内通道导入 + 三层验证闭环 |
| 萃取模式 | [wsl-rootfs-oci-image-export](../../../patterns/code-patterns/wsl-rootfs-oci-image-export.md)（L1-draft） |
| 会话 | sc-20261009-openkylin-wsl2podman |
