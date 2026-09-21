---
id: "offline-delivery-overview"
title: "项目概述"
source: "../README.md"
---
# 项目概述

**定位**：厂商侧**离线交付链路**——把预构建载荷 wheel 与基镜像变成客户可自持的离线交付包。
本应用同时是**交付物自身的构建方**：镜像定义、打包器、交付骨架三者同居一处，由交付方独立演进。
镜像按**底座 / 载荷分离**组织：底座（依赖面 + torch，**不含 XMNN**）在厂商侧构建归档，载荷 wheel 随交付包发出、由客户侧 `xmnnctl load` 派生装入。

## 制品流

```
厂商侧（apps/containers/offline-delivery）
  ../workspace/dist/xmnn-*.whl ──► stage ──► products/xmnn-runtime/release/payload/xmnn-*.whl
  （预构建载荷 wheel）              │            （随交付包发出，不进构建上下文）
                                    └─► deps ──► products/xmnn-runtime/deps.txt（依赖面事实源）
                                                 │
  localhost/jupyter-podman-rootless:latest ──► build ──► localhost/xmnn-runtime:base-<形态>
  （基镜像，底座基座）                                     （底座：cp314 GIL + torch + 依赖 + ipykernel，
                                                            底座守卫 6 项，无 :latest）
                                                 │
                                                 └─► pack ──► release/artifacts/<镜像名末段>-base-<形态>.tar.gz
                                                              release/artifacts/release.json（schema v2）

交付包（products/xmnn-runtime/release/）＝ 骨架 + artifacts/（底座归档 + 清单）+ payload/（wheel + 派生 Dockerfile）

客户侧（交付包根目录，./xmnnctl）
  xmnnctl load ─┬─ 幂等导入底座（比对 release.json.image.id，已在则跳过）
                └─ 校验载荷 sha256 ─► 派生构建 localhost/xmnn-runtime:<交付版本>
                                      （payload/Dockerfile：pip install --no-index --no-deps；
                                        载荷守卫 10 项 + pip check 在 RUN 内，失败即无 tag）
  xmnnctl up ──► 启动服务（镜像 tag = .env 的 XMNN_VERSION，compose.yaml 逐字未变）
  bin/relpack smoke ──► 以交付骨架为唯一入口：load → up → 容器内 10 项守卫 → down
```

- **输入**：预构建载荷 wheel（`../workspace/dist/xmnn-*.whl`）+ 基镜像（`localhost/jupyter-podman-rootless:latest`）——仅此两项。
- **中间（厂商侧）**：底座镜像 `localhost/xmnn-runtime:base-<形态>`（`cpu|cu130`，**无 `:latest`**；
  实测约 2.47 GB，其归档约 1.1 GB）；
  镜像内经底座守卫（6 项）硬断言「依赖面齐全」且「`import xmnn` 必须失败」——底座内为「无工具链、零源码挂载、不含载荷」的干净运行时。
- **中间（客户侧）**：由 `payload/` 内 wheel 派生的交付镜像 `localhost/xmnn-runtime:<交付版本>`（增量约 0.18 GB，约 1-3 分钟；派生构建失败即不产出 tag）。
- **输出**：① 客户 `release/` 交付骨架（自包含 compose + `xmnnctl`/`xmnnctl.ps1` + `payload/`）；
  ② 底座归档 `<镜像名末段>-base-<形态>.tar.gz` 与校验清单 `release.json`（schema v2：`payload` / `image` / `archive` 三块，含**双 sha256**）。
- **客户侧**：只需 Podman（或 Docker）与交付骨架，按骨架 `README.md` 执行 `init → load → up`，无需 Python、无需联网。
- **分线收益**：底座（依赖面，变化极慢）与载荷（约 177 MB wheel，随每个交付版本变化）解耦后，
  换 whl 只需重发载荷而**不必重传约 1.1 GB 的底座归档**；代价是客户侧 `load` 需具备镜像构建能力（约 +0.18 GB、1-3 分钟）。
  反之 **`deps.txt`（依赖面）变化必须重发底座**。旧口径中「4 GB」指 cu130 形态镜像，非本链路的常规交付体积。

## 与组内其它应用的边界

| 应用 | 与本应用的关系 | 边界 |
|------|---------------|------|
| [jupyter-podman-rootless](../../jupyter-podman-rootless/README.md)（构建端） | **上游（底座基座）**：提供基镜像 `localhost/jupyter-podman-rootless:latest`，本应用以其为 `FROM` 构建**底座镜像** | 本应用只消费该镜像，不改其任何内容、不做基镜像重建；底座守卫仅对基镜像自带的 conda×ruamel-yaml 单条冲突按收窄模式放行 |
| `../workspace/dist`（载荷 wheel 上游） | **上游（载荷）**：提供预构建 wheel `xmnn-*.whl`（由 xmnn-dev 栈的打包任务产出） | 本应用只读取 `dist`（`WHEEL_DIST` 可覆盖），不负责 wheel 打包；wheel 只作为**载荷**随交付包发出，不进底座构建上下文 |
| [client](../../client/README.md)（消费端） | **无依赖（且禁止依赖）** | 交付链路已于 2026-09-21 从 `client/overlays/xmnn-runtime/` 迁出；本应用不引用 client 的任何路径或代码 |
| [shared](../../shared/pyproject.toml)（组内共享包） | **无依赖（且禁止依赖）** | 本应用零 Python，不 import `jpman_common` |

> 迁移原因：交付物原本寄居消费端，构建一份客户交付物要拖着整个 client 与 shared；
> 交付物应有自己的产品参数、版本语义与发布节奏。

## 目录结构

```
offline-delivery/
├── AGENTS.md                ← 应用级 AI 路由入口（启动协议 + 路由表 + P0 约束）
├── README.md                ← 人类入口
├── .gitignore               ← 载荷 wheel 与镜像归档不入 git（保留 .gitignore / .keep 例外）
├── bin/
│   ├── relpack              ← bash CLI（WSL / Linux / macOS）
│   ├── lib/                 ← 流水线共享片段（载荷暂存 / deps 校验 / CRLF 守卫 / 清单写出）
│   └── relpack.ps1          ← pwsh7 CLI（Windows 原生，经 wsl.exe 桥接 bash 版）
├── products/
│   └── xmnn-runtime/        ← 首个产品
│       ├── product.env      ← 产品参数单一事实源（CLI 不内嵌产品常量）
│       ├── deps.txt         ← 底座依赖面唯一事实源（载荷 wheel 的无条件运行时依赖）
│       ├── Containerfile.xmnn-runtime / .dockerignore
│       ├── scripts/         ← torch 形态安装 + 内核注册
│       ├── smoke/           ← 底座守卫 _base_guards.py（构建期 6 项）+ 载荷守卫 _runtime_smoke.py（交付期 10 项）
│       └── release/         ← 客户交付骨架（零 Python、零 ../ 引用）
│           ├── xmnnctl / xmnnctl.ps1 / compose*.yaml / .env.example
│           ├── artifacts/   ← 底座归档 <镜像名末段>-base-<形态>.tar.gz + release.json（schema v2）
│           └── payload/     ← 载荷 wheel（不入 git）+ 派生构建 Dockerfile
├── docs/                    ← 本文档集
├── .agents/                 ← AI 资产（rules/delivery-pipeline.md + CHANGELOG）
└── tests/                   ← 交付骨架与 CLI 静态守卫测试
```

**产品分层**：`bin/` 是应用级工具（不含任何产品常量），`products/<产品名>/` 承载单产品全部资产。
新增第二个交付产品只需新增 `products/<名>/` 并在文档登记，CLI 代码零改动
（步骤见 [01-quickstart.md](01-quickstart.md)）。