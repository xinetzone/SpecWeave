# offline-delivery - 客户离线交付链路

> 一句话：把**预构建载荷 wheel + 基镜像**变成客户可自持的**离线交付包**——本应用负责**底座镜像**（cp314 base env + torch + 依赖面，不含 XMNN）的构建归档、载荷暂存、离线打包与端到端冒烟；交付物本身零 Python、零仓库外引用。

## 定位与关系

本应用是 `apps/containers/` 下**完全自包含**的应用（禁止依赖 `client/` 与 `shared/`）；
该链路此前寄居在 `apps/containers/client/overlays/xmnn-runtime/`，2026-09-21 迁出为本独立应用，详见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)。

| 关系 | 对象 | 说明 |
|------|------|------|
| 消费 | `../workspace/dist/xmnn-*.whl` + `localhost/jupyter-podman-rootless:latest` | 预构建**载荷** wheel（`stage` 暂存到产品 `release/payload/`，随交付包发出、**不进底座构建上下文**）与基镜像（由 [../jupyter-podman-rootless/](../jupyter-podman-rootless/README.md) 产出，本应用不改动） |
| 产出 | `products/xmnn-runtime/release/` | 客户侧交付骨架：自包含 compose + `xmnnctl` / `xmnnctl.ps1` + `payload/`（载荷 wheel 与派生 `Dockerfile`）；`release/artifacts/` 内为**底座镜像**归档 `xmnn-runtime-base-<形态>.tar.gz` 与 `release.json`（schema v2）校验清单 |

> **底座 / 载荷分离**（2026-09-21 起）：底座镜像 `localhost/xmnn-runtime:base-<形态>`（无 `:latest`）
> 承载依赖面与 torch，**不含 XMNN**；客户侧 `xmnnctl load` 先幂等导入底座，再用随包载荷派生构建
> `localhost/xmnn-runtime:<交付版本>`。收益口径：**换 whl 只需重发约 177 MB 的载荷，而不必重传
> 约 1.1 GB 的底座归档**。

## 目录结构

```
offline-delivery/
├── bin/                     ← relpack（bash）/ relpack.ps1（pwsh7）
├── products/xmnn-runtime/   ← 首个产品：product.env / deps.txt / Containerfile / scripts / smoke / release（含 payload）
├── docs/                    ← 人类文档：索引 + 概述 + 快速开始
├── .agents/                 ← AI 资产：规则主题 delivery-pipeline + 变更日志
└── tests/                   ← 交付骨架与 CLI 静态守卫测试（pytest）
```

## 快速开始

```bash
cd apps/containers/offline-delivery
bin/relpack stage                 # 暂存 ../workspace/dist 最新 xmnn-*.whl 到 release/payload/
bin/relpack deps                  # 校验载荷依赖集与 products/xmnn-runtime/deps.txt 一致（变化须重发底座）
bin/relpack build --torch cpu     # 构建底座镜像 localhost/xmnn-runtime:base-cpu（不含 xmnn 载荷，无 :latest）
bin/relpack pack                  # 导出 release/artifacts/xmnn-runtime-base-cpu.tar.gz + release.json（schema v2）
bin/relpack smoke                 # 经交付骨架 load → up → 容器内 10 项守卫 → down
bin/relpack version               # 打印产品名/形态/底座 ref 与 Id/载荷/归档名
```

Windows 原生（PowerShell 7.4+，容器命令经 `wsl.exe` 桥接到 bash 版）：

```powershell
pwsh bin/relpack.ps1 stage
pwsh bin/relpack.ps1 deps
pwsh bin/relpack.ps1 build --torch cpu
pwsh bin/relpack.ps1 pack
pwsh bin/relpack.ps1 smoke
pwsh bin/relpack.ps1 version
```

前置条件（WSL 发行版、`podman`、`smoke` 另需 `podman-compose`、基镜像在场）与逐命令预期输出见 [docs/01-quickstart.md](docs/01-quickstart.md)。

## 命令表

| 命令 | 作用 | 关键参数 |
|------|------|---------|
| `version` | 打印产品名、形态、底座 ref 与 Id、载荷版本与 wheel 名、归档名 | —（无子命令选项） |
| `stage` | 暂存最新 `xmnn-*.whl` 到 `products/<产品>/release/payload/`（随交付包发出，不进底座构建上下文） | `--wheel PATH` |
| `deps` | 校验（或 `--write` 重写）载荷依赖集 `products/<产品>/deps.txt`；不一致即 fail-fast | `--write` |
| `build` | 构建**底座**镜像并打形态 tag `<IMAGE_NAME>:base-<形态>`（不含载荷，无 `:latest`） | `--torch cpu\|cu130`、`--base-image REF`、`--pip-mirror official\|tuna\|aliyun`、`--no-cache` |
| `pack` | 导出底座归档与 `release.json`（schema v2） | `--version V` |
| `smoke` | 以交付骨架为唯一入口做端到端验证（`load → up → smoke → down`） | `--version V` |

全局参数：`-p\|--product <产品名>`（默认 `xmnn-runtime`），对所有子命令生效；
覆盖优先级为 CLI 旗标 > 环境变量（`BASE_IMAGE` / `PIP_MIRROR` / `TORCH_FLAVOR`）> `product.env`。

完整文档入口：[docs/README.md](docs/README.md)；AI 硬约束见 [AGENTS.md](AGENTS.md) 与 [.agents/rules/delivery-pipeline.md](.agents/rules/delivery-pipeline.md)。