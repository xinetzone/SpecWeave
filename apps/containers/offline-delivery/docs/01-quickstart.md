---
id: "offline-delivery-quickstart"
title: "快速开始"
source: "../bin/relpack --help"
---
# 快速开始

从零跑通 `stage → build → pack → smoke`，并新增第二个交付产品。
命令一律在应用根 `apps/containers/offline-delivery/` 执行。

## 1. 前置条件

| 项 | 要求 | 校验 |
|----|------|------|
| 宿主工作区 | Windows + PowerShell 7.4+（或 Linux/macOS 的 bash 4+） | `pwsh -v` |
| WSL 发行版 | 默认 `podman-machine-default`，可用 `OFFLINE_DELIVERY_WSL_DISTRO` 覆盖 | `wsl.exe -l -v` |
| podman | WSL 内可用（`build`/`pack`/`smoke` 需要） | `wsl.exe -d <发行版> -- podman info` |
| podman-compose | **仅 `smoke` 需要** | `wsl.exe -d <发行版> -- podman-compose --version` |
| 基镜像 | `localhost/jupyter-podman-rootless:latest` 已存在 | `podman images \| grep jupyter-podman-rootless` |
| 预构建 wheel | `../workspace/dist/xmnn-*.whl` 存在（= `apps/containers/workspace/dist`） | `ls ../workspace/dist` |

> 本应用零 Python：不需要 `pip install`，不引入 `invoke` / `podman-py`。
> 缺基镜像时请先在 [jupyter-podman-rootless](../../jupyter-podman-rootless/README.md) 侧产出或加载，本应用不负责重建。

## 2. 逐命令与预期输出

### `version` —— 先自检产品参数

```bash
bin/relpack version
```

预期输出含产品名、镜像名、形态 tag、交付版本、wheel 名（形态 tag 取自 `product.env`
的 `TORCH_DEFAULT`，wheel 名取自暂存区；尚未 `stage` 时提示「暂存区为空」但不报错）。

### `stage` —— 暂存 wheel

```bash
bin/relpack stage                  # 取 ../workspace/dist 中最新的 xmnn-*.whl
bin/relpack stage --wheel ../workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl
```

选择顺序：`--wheel` 显式 > `WHEEL_DIST` 下最新 mtime > 复用已暂存 > 非零退出并给出上游指引。
预期输出形如 `[ OK ] 已暂存 xmnn-1.2.1.dev0-...whl → products/xmnn-runtime/wheels/`；
同名同 size 同 mtime 时跳过拷贝。**暂存区同时只保留一个 whl**（旧 whl 被清理）。

### `build` —— 构建运行时镜像

```bash
bin/relpack build --torch cpu                     # 形态 tag：<IMAGE_NAME>:cpu + :latest
bin/relpack build --torch cu130 --no-cache        # CUDA 13.0 形态 + 跳过缓存
bin/relpack build --base-image localhost/jupyter-podman-rootless:latest \
                  --pip-mirror tuna                # 镜像源：official | tuna | aliyun
```

构建上下文为产品目录；构建参数 `BASE_IMAGE` / `PIP_MIRROR` / `TORCH_FLAVOR`。
预期输出结尾形如 `[ OK ] localhost/xmnn-runtime:cpu`、`[ OK ] localhost/xmnn-runtime:latest`。
构建期 10 项硬验证由 Containerfile 自带，**任一失败即构建失败**（不会产出半成品 tag）。

### `pack` —— 导出离线归档

```bash
bin/relpack pack                        # 版本默认取暂存 wheel 版本（1.2.1.dev0）
bin/relpack pack --version 1.2.1        # GA 正式交付：显式指定
```

流程：① 交付骨架 CRLF shebang 守卫（命中即 fail-fast）→ ② 镜像改挂到
`<IMAGE_NAME>:<版本>` → ③ `podman save | gzip -1` → `gzip -t` → 原子 `mv`
→ ④ 写 `release.json`。

预期产物：

```
products/xmnn-runtime/release/artifacts/xmnn-runtime-1.2.1.tar.gz
products/xmnn-runtime/release/artifacts/release.json
```

`release.json` 含 `schema_version` / `product` / `version` /
`wheel`（`file`、`version`、`size_bytes`）/ `image`（`ref`、`id`、`torch_cpu`、`abi`）/
`archive`（`file`、`size_bytes`、`sha256`）/ `built_at` / `source_commit` / `pack_tool`。

### `smoke` —— 经交付骨架端到端验证

```bash
bin/relpack smoke
```

以交付骨架为**唯一入口**：把本地镜像改挂到交付版本 tag → 骨架内 `./xmnnctl init`（缺 `.env` 时）
→ `up` → 容器内 `/opt/xmnnrt-smoke/_runtime_smoke.py` 10 项守卫 → `down`。
预期末行形如「10 项守卫全部通过」，退出码 0，容器已停止。任一步失败即非零退出并打印可执行指引。

### Windows 原生等价形式

```powershell
pwsh bin/relpack.ps1 version
pwsh bin/relpack.ps1 stage
pwsh bin/relpack.ps1 build --torch cpu
pwsh bin/relpack.ps1 pack --version 1.2.1
pwsh bin/relpack.ps1 smoke
```

参数校验与日志在宿主侧完成，容器子命令经
`wsl.exe -d <发行版> -- bash bin/relpack <args>` 桥接给 bash 版；两端命令面等价。

## 3. 常见失败与处置

| 现象 | 原因 | 处置 |
|------|------|------|
| `暂存区为空 / 找不到 xmnn-*.whl` | `../workspace/dist` 无 wheel | 先在上游产出 wheel，或 `stage --wheel <绝对路径>` |
| `基镜像不存在` | 基镜像未加载 | 在 jupyter-podman-rootless 侧产出后 `podman load` |
| `podman: command not found` / `Cannot connect to Podman` | WSL 发行版未运行或 podman 缺失 | 启动 `podman machine`；用 `OFFLINE_DELIVERY_WSL_DISTRO` 指定正确发行版 |
| `podman-compose 未安装`（仅 smoke） | 缺 smoke 依赖 | 在 WSL 内安装 podman-compose，或先跑 `pack` 验证 |
| `'/usr/bin/env: bash\r'` | 骨架/CLI 被检出为 CRLF | 在仓库根执行 `git add --renormalize .` 后重跑 |
| `端口 8893/2225 被占用` | 上次 smoke 未清理或他进程占用 | `./xmnnctl down` 清理；或释放端口后重跑 |
| `gzip: ... unexpected end of file` | 归档传输/磁盘中断 | 删除 `artifacts/` 内临时文件后重新 `pack`（原子 `mv` 保证不留截断归档） |
| `release.json` 中 torch 版本为 null | 镜像缺少 torch LABEL | 确认镜像由本应用 `build` 产出（LABEL 六键齐全） |

## 4. 新增第二个交付产品

CLI 代码**零改动**；只需新增产品目录并在文档登记：

1. 创建 `products/<产品名>/`，落 `product.env`（唯一产品常量来源）：

   ```ini
   PRODUCT=<产品名>
   IMAGE_NAME=localhost/<镜像名>
   CONTAINERFILE=Containerfile.<产品名>
   WHEEL_GLOB=<wheel 通配>
   WHEEL_DIST=../workspace/dist
   BASE_IMAGE_DEFAULT=localhost/jupyter-podman-rootless:latest
   TORCH_DEFAULT=cpu
   RELEASE_DIR=release
   ```

2. 在 `products/<产品名>/` 内落：镜像定义（`Containerfile.*` + `.dockerignore`）、
   `scripts/`（构建期脚本）、`smoke/`（构建期守卫脚本）、`wheels/.gitignore`（暂存区占位）。
3. 迁入或新建 `release/` 交付骨架（自包含 compose + `xmnnctl`/`xmnnctl.ps1` +
   `.env.example` + `artifacts/.gitignore` + `workspace/.gitkeep`），遵守
   [delivery-pipeline.md](../.agents/rules/delivery-pipeline.md) §1「纯移动与零 `../`」。
4. 所有命令加 `-p|--product <产品名>` 即可驱动新产品（默认仍为 `xmnn-runtime`）：
   `bin/relpack -p <产品名> stage|build|pack|smoke`。
5. 在 `docs/README.md`、[00-overview.md](00-overview.md) 与本文件登记新产品，
   并在 `../.agents/CHANGELOG.md` 追加条目。

> 若发现必须改 CLI 才能支持新产品，说明产品常量泄漏到了代码里——先按
> [delivery-pipeline.md](../.agents/rules/delivery-pipeline.md) §7 把常量收回 `product.env`，再重试。