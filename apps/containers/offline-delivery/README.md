# offline-delivery - 客户离线交付链路

> 一句话：把**预构建 wheel + 基镜像**变成客户可自持的**离线交付包**——本应用负责镜像构建、离线打包与端到端冒烟；交付物本身零 Python、零仓库外引用。

## 定位与关系

本应用是 `apps/containers/` 下**完全自包含**的应用（禁止依赖 `client/` 与 `shared/`）；
该链路此前寄居在 `apps/containers/client/overlays/xmnn-runtime/`，2026-09-21 迁出为本独立应用，详见 [.agents/CHANGELOG.md](.agents/CHANGELOG.md)。

| 关系 | 对象 | 说明 |
|------|------|------|
| 消费 | `../workspace/dist/xmnn-*.whl` + `localhost/jupyter-podman-rootless:latest` | 预构建 wheel（`stage` 暂存到产品 `wheels/`）与基镜像（由 [../jupyter-podman-rootless/](../jupyter-podman-rootless/README.md) 产出，本应用不改动） |
| 产出 | `products/xmnn-runtime/release/` | 客户侧交付骨架：自包含 compose + `xmnnctl` / `xmnnctl.ps1`；`release/artifacts/` 内为归档 `xmnn-runtime-<版本>.tar.gz` 与 `release.json` 校验清单 |

## 目录结构

```
offline-delivery/
├── bin/                     ← relpack（bash）/ relpack.ps1（pwsh7）
├── products/xmnn-runtime/   ← 首个产品：product.env / Containerfile / scripts / smoke / wheels / release
├── docs/                    ← 人类文档：索引 + 概述 + 快速开始
├── .agents/                 ← AI 资产：规则主题 delivery-pipeline + 变更日志
└── tests/                   ← 交付骨架与 CLI 静态守卫测试（pytest）
```

## 快速开始

```bash
cd apps/containers/offline-delivery
bin/relpack stage                 # 暂存 ../workspace/dist 最新 xmnn-*.whl 到产品 wheels/
bin/relpack build --torch cpu     # 构建运行时镜像（双 tag：<IMAGE_NAME>:cpu + :latest）
bin/relpack pack                  # 导出 release/artifacts/xmnn-runtime-<版本>.tar.gz + release.json
bin/relpack smoke                 # 经交付骨架 init → up → 容器内 10 项守卫 → down
bin/relpack version               # 打印产品名/镜像名/形态 tag/交付版本/wheel 名
```

Windows 原生（PowerShell 7.4+，容器命令经 `wsl.exe` 桥接到 bash 版）：

```powershell
pwsh bin/relpack.ps1 stage
pwsh bin/relpack.ps1 build --torch cpu
pwsh bin/relpack.ps1 pack
pwsh bin/relpack.ps1 smoke
pwsh bin/relpack.ps1 version
```

前置条件（WSL 发行版、`podman`、`smoke` 另需 `podman-compose`、基镜像在场）与逐命令预期输出见 [docs/01-quickstart.md](docs/01-quickstart.md)。

## 命令表

| 命令 | 作用 | 关键参数 |
|------|------|---------|
| `version` | 打印产品名、镜像名、形态 tag、交付版本、wheel 名 | —（无子命令选项） |
| `stage` | 暂存最新 `xmnn-*.whl` 到 `products/<产品>/wheels/` | `--wheel PATH` |
| `build` | 构建运行时镜像并打形态 tag + `:latest` 别名 | `--torch cpu\|cu130`、`--base-image REF`、`--pip-mirror official\|tuna\|aliyun`、`--no-cache`、`--wheel PATH` |
| `pack` | 导出离线归档与 `release.json` | `--version V` |
| `smoke` | 以交付骨架为唯一入口做端到端验证 | `--version V` |

全局参数：`-p\|--product <产品名>`（默认 `xmnn-runtime`），对所有子命令生效；
覆盖优先级为 CLI 旗标 > 环境变量（`BASE_IMAGE` / `PIP_MIRROR` / `TORCH_FLAVOR`）> `product.env`。

完整文档入口：[docs/README.md](docs/README.md)；AI 硬约束见 [AGENTS.md](AGENTS.md) 与 [.agents/rules/delivery-pipeline.md](.agents/rules/delivery-pipeline.md)。