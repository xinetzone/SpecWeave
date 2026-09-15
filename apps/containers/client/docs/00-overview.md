---
id: "jupyter-podman-client-overview"
title: "项目概述"
source: "README.md#1-与构建端的关系"
---
# 项目概述

**定位**：`apps/containers/jupyter-podman-rootless` 镜像构建端的**消费端**。
基于 `podman-py` 从本地加载构建端产出的镜像，并提供极简的容器生命周期管理。

- 需要快速启停、日常驾驶（status/shell/logs 等）→ 用构建端的 `jpman` CLI
- 需要 Python 脚本化集成、在其他应用里以 SDK 方式加载/运行镜像 → 用本项目

## 与构建端的关系

```
apps/containers/
├── jupyter-podman-rootless/   ← 构建端（Containerfile + invoke + jpman CLI）
│   └── .image-cache/          ← 构建端 save 产出的 tar.gz 缓存目录（git 忽略）
└── client/                    ← 本项目：消费端（podman-py SDK + invoke）
```

消费端的默认加载路径：
```
../jupyter-podman-rootless/.image-cache/<latest-timestamp>.tar.gz
```
（即自动从构建端的最新缓存加载，无需手工传路径。）

## 与 jpman CLI 的分工

| 维度 | jpman（构建端） | client（消费端） |
|---|---|---|
| 入口 | `bash bin/jpman` / `jpman.ps1` | `pip install -e .` 后 `invoke` / Python import |
| 构建镜像 | ✅ `rebuild / rebuild-all` | ❌ 只消费 |
| 镜像缓存 save/load | ✅ 双路 | ✅ load 单向（从 tar 恢复） |
| wsl-export / keepalive | ✅ 支持 | ❌ |
| ML 模型管理 (omlmd/olot) | ✅ 支持 | ❌ |
| podman-compose 后端 | ✅ Tier 1 | ❌ 仅 SDK + CLI fallback |
| podman-py SDK 作为一等公民 | 可选依赖 `.[full]` | **强制核心依赖** |
| 面向用户 | 人类驾驶员（日常操作） | 自动化集成 / 其他应用嵌入调用 |

## 核心能力速览

1. **两层后端自动降级**：podman-py SDK（优先）→ CLI fallback（`podman.exe` 子进程）
2. **rootless 三必需硬编码**：`--device /dev/fuse` + `--security-opt label=disable` + `--cgroupns=host`，严禁 `--privileged`（见 [06-run-discipline.md](06-run-discipline.md)）
3. **Windows 11 × WSL2 跨平台 SDK 连接**：WSL9P / Podman Machine / tcp 多候选自动探测（见 [03-windows-wsl.md](03-windows-wsl.md)）
4. **opt-in 工作负载栈**：`quant.*`（[10-quant-overlay.md](10-quant-overlay.md)）/ `xmnn.*`（[11-xmnn-overlay.md](11-xmnn-overlay.md)）/ `monetize.*`（[12-monetize-overlay.md](12-monetize-overlay.md)），podman-compose 子进程层