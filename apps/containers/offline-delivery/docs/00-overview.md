---
id: "offline-delivery-overview"
title: "项目概述"
source: "../README.md"
---
# 项目概述

**定位**：厂商侧**离线交付链路**——把预构建 wheel 与基镜像变成客户可自持的离线交付包。
本应用同时是**交付物自身的构建方**：镜像定义、打包器、交付骨架三者同居一处，由交付方独立演进。

## 制品流

```
../workspace/dist/xmnn-*.whl ─┐
                              ├─► stage（暂存 wheel 到产品 wheels/）
localhost/jupyter-podman-     │
  rootless:latest（基镜像）────┴─► build（构建运行时镜像，双 tag）
                                        │
                                        ├─► pack ──► release/artifacts/xmnn-runtime-<版本>.tar.gz
                                        │            release/artifacts/release.json
                                        └─► smoke ─► release/ 骨架：init → up → 容器内 10 项守卫 → down
```

- **输入**：预构建 wheel（`../workspace/dist/xmnn-*.whl`）+ 基镜像（`localhost/jupyter-podman-rootless:latest`）——仅此两项。
- **中间**：运行时镜像 `<IMAGE_NAME>:<形态>`（`cpu|cu130`）+ `:latest` 别名；镜像内为「无工具链、零源码挂载」的干净运行时。
- **输出**：① 客户 `release/` 交付骨架（自包含 compose + `xmnnctl`/`xmnnctl.ps1`）；
  ② 离线归档 `xmnn-runtime-<版本>.tar.gz` 与校验清单 `release.json`（sha256 / 尺寸 / wheel 版本 / torch 版本）。
- **客户侧**：只需 Podman（或 Docker）与交付骨架，按骨架 `README.md` 执行 `init → load → up`，无需 Python、无需联网。

## 与组内其它应用的边界

| 应用 | 与本应用的关系 | 边界 |
|------|---------------|------|
| [jupyter-podman-rootless](../../jupyter-podman-rootless/README.md)（构建端） | **上游**：提供基镜像 `localhost/jupyter-podman-rootless:latest` | 本应用只消费该镜像，不改其任何内容、不做基镜像重建 |
| `../workspace/dist`（预构建 wheel 来源） | **上游**：提供预构建 wheel `xmnn-*.whl` | 本应用只读取 `dist`（`WHEEL_DIST` 可覆盖），不负责 wheel 打包 |
| [client](../../client/README.md)（消费端） | **无依赖（且禁止依赖）** | 交付链路已于 2026-09-21 从 `client/overlays/xmnn-runtime/` 迁出；本应用不引用 client 的任何路径或代码 |
| [shared](../../shared/pyproject.toml)（组内共享包） | **无依赖（且禁止依赖）** | 本应用零 Python，不 import `jpman_common` |

> 迁移原因：交付物原本寄居消费端，构建一份客户交付物要拖着整个 client 与 shared；
> 交付物应有自己的产品参数、版本语义与发布节奏。

## 目录结构

```
offline-delivery/
├── AGENTS.md                ← 应用级 AI 路由入口（启动协议 + 路由表 + P0 约束）
├── README.md                ← 人类入口
├── .gitignore               ← wheel 与镜像归档不入 git（保留两处 .gitignore 例外）
├── bin/
│   ├── relpack              ← bash CLI（WSL / Linux / macOS）
│   └── relpack.ps1          ← pwsh7 CLI（Windows 原生，经 wsl.exe 桥接 bash 版）
├── products/
│   └── xmnn-runtime/        ← 首个产品
│       ├── product.env      ← 产品参数单一事实源（CLI 不内嵌产品常量）
│       ├── Containerfile.xmnn-runtime / .dockerignore
│       ├── scripts/         ← torch 形态安装 + 内核注册
│       ├── smoke/           ← 构建期 10 项硬验证脚本
│       ├── wheels/          ← whl 暂存区（仅保留一个 whl，不入 git）
│       └── release/         ← 客户交付骨架（零 Python、零 ../ 引用）
├── docs/                    ← 本文档集
├── .agents/                 ← AI 资产（rules/delivery-pipeline.md + CHANGELOG）
└── tests/                   ← 交付骨架与 CLI 静态守卫测试
```

**产品分层**：`bin/` 是应用级工具（不含任何产品常量），`products/<产品名>/` 承载单产品全部资产。
新增第二个交付产品只需新增 `products/<名>/` 并在文档登记，CLI 代码零改动
（步骤见 [01-quickstart.md](01-quickstart.md)）。