---
id: "offline-delivery-quickstart"
title: "快速开始"
source: "../bin/relpack --help"
---
# 快速开始

从零跑通 `stage → deps → build → pack → smoke`，更新交付（只换 whl），并新增第二个交付产品。
命令一律在应用根 `apps/containers/offline-delivery/` 执行。

## 1. 前置条件

| 项 | 要求 | 校验 |
|----|------|------|
| 宿主工作区 | Windows + PowerShell 7.4+（或 Linux/macOS 的 bash 4+） | `pwsh -v` |
| WSL 发行版 | 默认 `podman-machine-default`，可用 `OFFLINE_DELIVERY_WSL_DISTRO` 覆盖 | `wsl.exe -l -v` |
| podman | WSL 内可用（`build`/`pack`/`smoke` 需要） | `wsl.exe -d <发行版> -- podman info` |
| podman-compose | **仅 `smoke` 需要** | `wsl.exe -d <发行版> -- podman-compose --version` |
| 基镜像 | `localhost/jupyter-podman-rootless:latest` 已存在（底座镜像的基座） | `podman images \| grep jupyter-podman-rootless` |
| 预构建 wheel | `../workspace/dist/xmnn-*.whl` 存在（= `apps/containers/workspace/dist`） | `ls ../workspace/dist` |
| `unzip` 或 `bsdtar` | **仅 `deps` 需要**（读 wheel 的 `METADATA`）；缺失时 `deps` 告警跳过校验而非硬失败 | `unzip -v` |

> 本应用零 Python：不需要 `pip install`，不引入 `invoke` / `podman-py`。
> 缺基镜像时请先在 [jupyter-podman-rootless](../../jupyter-podman-rootless/README.md) 侧产出或加载，本应用不负责重建。

## 2. 逐命令与预期输出

### `version` —— 先自检产品参数

```bash
bin/relpack version
```

预期输出含产品名、形态、底座 ref 与 Id、载荷版本、载荷 wheel 名与归档名（形态取自 `product.env`
的 `TORCH_DEFAULT`，wheel 名取自载荷区；尚未 `stage` 时提示「载荷区为空」但不报错，
底座 Id 在 podman 不可用或底座未构建时如实标注）。

### `stage` —— 暂存载荷 wheel

```bash
bin/relpack stage                  # 取 ../workspace/dist 中最新的 xmnn-*.whl
bin/relpack stage --wheel ../workspace/dist/xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl
```

选择顺序：`--wheel` 显式 > `WHEEL_DIST` 下最新 mtime > 复用已暂存 > 非零退出并给出上游指引。
预期输出形如 `[ OK ] 已暂存 ../workspace/dist 最新 wheel → products/xmnn-runtime/release/payload/xmnn-1.2.1.dev0-...whl`；
同名同 size 同 mtime 时跳过拷贝。**载荷区同时只保留一个 whl**（旧 whl 被清理），
且该 wheel **随交付包发出、不进底座镜像构建上下文**。

### `deps` —— 校验载荷依赖集（底座依赖面的唯一事实源）

```bash
bin/relpack deps                   # 校验：载荷 wheel 的 Requires-Dist 无条件项 vs products/xmnn-runtime/deps.txt
bin/relpack deps --write           # 重写 deps.txt（保留头部注释块，仅更新来源 wheel / sha256 / 生成时间）
```

- 取出规则：`Requires-Dist` 中**不含分号**的条目（无环境 marker、无 extra 的无条件运行时依赖），
  排序去重后与 `products/xmnn-runtime/deps.txt` 比对；`torch` 由 Containerfile Layer 1 精确 pin，不在清单内。
- 预期输出形如 `[ OK ] 依赖集一致：products/xmnn-runtime/deps.txt（20 项无条件依赖）`。
- 不一致时打印差异清单（`<` 仅 deps.txt；`>` 仅载荷 whl）并**非零退出**：
  **依赖面变化必须重发底座镜像**（`deps --write` → `build` → 重新 `pack`）——派生安装走
  `--no-index --no-deps`，底座缺依赖时不会补装，故障要到客户运行期才暴露。
- 缺 `unzip`/`bsdtar` 时仅告警并跳过校验（既不静默通过也不阻断流水线）。

### `build` —— 构建底座镜像（不含载荷）

```bash
bin/relpack build --torch cpu                     # 底座 tag：<IMAGE_NAME>:base-cpu（无 :latest）
bin/relpack build --torch cu130 --no-cache        # CUDA 13.0 形态 + 跳过缓存
bin/relpack build --base-image localhost/jupyter-podman-rootless:latest \
                  --pip-mirror tuna                # 镜像源：official | tuna | aliyun
```

构建上下文为产品目录（`Containerfile.xmnn-runtime` + `deps.txt` + `scripts/` + `smoke/`；
**不含任何 wheel**）；构建参数 `BASE_IMAGE` / `PIP_MIRROR` / `TORCH_FLAVOR`。
预期输出结尾形如 `[ OK ] 底座镜像已构建：localhost/xmnn-runtime:base-cpu（不含 xmnn 载荷；载荷由交付侧派生装入）`。
四层结构与底座守卫（6 项，root/devuser 双跑）由 Containerfile 自带，**任一失败即构建失败**
（不会产出半成品 tag）：双 ABI / deps.txt 逐条已装 / `pip check` 无新冲突 / torch 形态与实物一致 /
内核双可见 / **反断言 `import xmnn` 必须失败**。

### `pack` —— 导出底座归档

```bash
bin/relpack pack                        # 版本默认取暂存载荷 wheel 版本（1.2.1.dev0）
bin/relpack pack --version 1.2.1        # GA 正式交付：显式指定
```

流程：① 交付骨架 CRLF shebang 守卫（命中即 fail-fast）→ ② 载荷唯一性与依赖集一致性守卫
（不一致即非零退出，并给出「对齐依赖集 → 重建底座 → 重新 pack」三步修法）→ ③ 底座镜像改挂到
`<IMAGE_NAME>:base-<形态>` → ④ `podman save | gzip -1` → `gzip -t` → 原子 `mv` → ⑤ 写 `release.json`。

预期产物：

```
products/xmnn-runtime/release/artifacts/xmnn-runtime-base-cpu.tar.gz
products/xmnn-runtime/release/artifacts/release.json
```

`release.json` 为 **schema v2**：`schema_version`（`"2"`）/ `product` / `version` /
`payload`（`file`、`version`、`size_bytes`、`sha256`）/ `image`（`ref`、`id`、`torch_version`、
`torch_flavor`、`abi`）/ `archive`（`file`、`size_bytes`、`sha256`）/ `built_at` / `source_commit` /
`pack_tool`。顶层 `version` 即**载荷版本**（= 客户派生镜像的 tag），`image.ref`/`image.id` 描述**底座**。

### `smoke` —— 经交付骨架端到端验证

```bash
bin/relpack smoke
```

以交付骨架为**唯一入口**：骨架内 `./xmnnctl init`（缺 `.env` 时）→ `./xmnnctl load`
（幂等导入底座 + 校验载荷 sha256 + 派生构建，构建内跑 10 项载荷守卫与 `pip check`）→ `./xmnnctl up`
→ `./xmnnctl smoke`（容器内 `/opt/xmnnrt-smoke/_runtime_smoke.py` 10 项守卫）→ `./xmnnctl down`。
预期末行形如「smoke 通过：交付骨架 load（底座导入 + 载荷派生）→ up → 10 项守卫 → down 全部成功」，
退出码 0，容器已停止。任一步失败即非零退出并打印可执行指引（`down` 无论成败都会尝试收尾）。

### Windows 原生等价形式

```powershell
pwsh bin/relpack.ps1 version
pwsh bin/relpack.ps1 stage
pwsh bin/relpack.ps1 deps
pwsh bin/relpack.ps1 build --torch cpu
pwsh bin/relpack.ps1 pack --version 1.2.1
pwsh bin/relpack.ps1 smoke
```

参数校验与日志在宿主侧完成，容器子命令经
`wsl.exe -d <发行版> -- bash bin/relpack <args>` 桥接给 bash 版；两端命令面等价
（Windows 原生另有 `-Deps` 等价于 `deps` 子命令、`-Write` 等价于 `deps --write`）。

## 3. 常见失败与处置

| 现象 | 原因 | 处置 |
|------|------|------|
| `暂存区为空 / 找不到 xmnn-*.whl` | `../workspace/dist` 无 wheel | 先在上游产出 wheel，或 `stage --wheel <绝对路径>` |
| `载荷区有 N 个 wheel（须恰一个）` | `release/payload/` 内残留旧 whl | 清掉多余 whl 后重试（`stage` 只保留最新一个） |
| `载荷依赖集与 deps.txt 不一致`（`deps` 或 `pack` 前置守卫） | 载荷 wheel 声明的无条件依赖与 `deps.txt` 不同 | **依赖面变化必须重发底座**：`deps --write` → `build` → 重新 `pack`；差异清单已打印（`<` 仅 deps.txt；`>` 仅载荷 whl） |
| `未找到 unzip 或 bsdtar`（[WARN]） | 缺解压工具，无法读 wheel 元数据 | 安装 `unzip` 或 `bsdtar` 后重试；本次校验被跳过（不是通过，也未阻断） |
| `基镜像不存在` | 基镜像未加载 | 在 jupyter-podman-rootless 侧产出后 `podman load` |
| `podman: command not found` / `Cannot connect to Podman` | WSL 发行版未运行或 podman 缺失 | 启动 `podman machine`；用 `OFFLINE_DELIVERY_WSL_DISTRO` 指定正确发行版 |
| `podman-compose 未安装`（仅 smoke） | 缺 smoke 依赖 | 在 WSL 内安装 podman-compose，或先跑 `pack` 验证 |
| `'/usr/bin/env: bash\r'` | 骨架/CLI 被检出为 CRLF | 在仓库根执行 `git add --renormalize .` 后重跑 |
| `端口 8893/2225 被占用` | 上次 smoke 未清理或他进程占用 | `./xmnnctl down` 清理；或释放端口后重跑 |
| `gzip: ... unexpected end of file` | 归档传输/磁盘中断 | 删除 `artifacts/` 内临时文件后重新 `pack`（原子 `mv` 保证不留截断归档） |
| `release.json` 中 torch 版本为 null | 镜像缺少 torch LABEL | 确认底座镜像由本应用 `build` 产出（LABEL 齐全） |
| `load` 报「载荷 wheel 的 sha256 与交付清单不符」 | 载荷文件在拷贝中损坏，或手工替换的 whl 与清单不配套 | 重新完整获取交付包；只换 whl 时须用交付方随清单配套下发的文件（见「更新交付（只换 whl）」） |
| `load` 报「交付包与镜像不匹配…Id 不一致」 | `artifacts/` 内底座归档与 `release.json` 不是同一批 | 重新完整获取交付包（两者必须成套）；底座已换版时 `load` 会自动跳过 Id 相同的导入 |
| `load` 报「版本不一致：.env 的 XMNN_VERSION=… 交付清单 version=…」 | `.env` 版本与清单顶层 `version`（载荷版本）不一致 | 清单为权威：按报错把 `.env` 的 `XMNN_VERSION` 改成清单版本后重试（派生镜像 tag 即该版本） |
| `load` 报「派生构建失败」 | ① 磁盘空间不足（派生镜像另需约 0.18 GB）；② 载荷依赖未在底座满足 | ① 清理磁盘后重跑 `load`（幂等，已完成的步骤自动跳过）；② 见下一行 |
| 派生构建日志中 `pip check` 报**以 `xmnn` 开头**的冲突行 | 载荷声明的依赖在底座缺失或版本不符（底座与载荷不匹配，属交付方制品问题） | 把报错原文反馈给对接人员；交付方需 `deps --write` 后重建底座并重新发版。注：不以 `xmnn` 开头的冲突行（如基镜像自带 conda×ruamel-yaml 债务）与本次交付无关，构建照常继续 |
| `load` 报「缺少派生构建文件 payload/Dockerfile」 | 交付包不完整或 `payload/` 被改动 | 重新获取交付包；`payload/Dockerfile` **请勿改动或删除** |

## 4. 更新交付（只换 whl）

底座（依赖面 + torch）不变、只升级 XMNN 载荷时，**不必重传约 1.1 GB 的底座归档**，
只重发约 177 MB 的载荷即可：

1. 厂商侧：`bin/relpack stage`（把新 whl 暂存到 `release/payload/`，旧 whl 被清理）→
   `bin/relpack deps`（**依赖面变化必须重发底座**：不一致时先 `deps --write` 再 `build`）→
   `bin/relpack pack --version <新版本>`（重算载荷 sha256 并重写 `release.json`；底座不变则
   `image.id` 不变）→ 只把 `payload/` 与 `artifacts/release.json` 发给客户即可
   （底座归档 `xmnn-runtime-base-<形态>.tar.gz` 无需重传）。
2. 客户侧：用新 whl 替换 `payload/` 内的旧文件——目录内**同时只应有一个**
   `xmnn-<版本>-cp314-cp314-linux_x86_64.whl`（旧的要删掉，避免误装；
   `payload/Dockerfile` 保留不动）→ 把 `.env` 的 `XMNN_VERSION` 改成交付方给的新版本号
   （`load` 会与清单核对，不一致直接报错并提示正确值）→ `./xmnnctl load`
   （底座 Id 与清单一致，**跳过归档导入**，只做载荷 sha256 校验与派生构建，约 1-3 分钟）
   → `./xmnnctl up` 以新载荷的镜像重建容器（`workspace/` 与凭证不受影响）。
3. 若交付方**同时**更新了底座（如 `deps.txt` 变化导致重发），把新版 `artifacts/`（归档 + 清单）
   与 `payload/` 一起替换后再 `load`——脚本检测到底座 Id 变化时会自动导入新归档。

> `load` 全流程幂等：中断或失败后重跑即可，已完成的步骤（含底座导入）自动跳过。

## 5. 新增第二个交付产品

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
   `deps.txt`（底座依赖面清单：先 `deps --write` 从载荷 wheel 生成，再在 Containerfile 中以
   `pip install -r deps.txt` 安装）、`scripts/`（构建期脚本）、`smoke/`（底座守卫 + 载荷守卫脚本）。
3. 迁入或新建 `release/` 交付骨架（自包含 compose + `xmnnctl`/`xmnnctl.ps1` +
   `.env.example` + `artifacts/.gitignore` + `workspace/.gitkeep`），并新建载荷目录
   `release/payload/`（`payload/.gitignore` 忽略 `*.whl`、`payload/.keep` 占位，
   `payload/Dockerfile` 为交付侧派生构建入口），遵守
   [delivery-pipeline.md](../.agents/rules/delivery-pipeline.md) §1「对外契约冻结与零 `../`」。
4. 所有命令加 `-p|--product <产品名>` 即可驱动新产品（默认仍为 `xmnn-runtime`）：
   `bin/relpack -p <产品名> stage|deps|build|pack|smoke`。
5. 在 `docs/README.md`、[00-overview.md](00-overview.md) 与本文件登记新产品，
   并在 `../.agents/CHANGELOG.md` 追加条目。

> 若发现必须改 CLI 才能支持新产品，说明产品常量泄漏到了代码里——先按
> [delivery-pipeline.md](../.agents/rules/delivery-pipeline.md) §7 把常量收回 `product.env`，再重试。