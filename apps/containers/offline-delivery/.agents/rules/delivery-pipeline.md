---
id: "offline-delivery-delivery-pipeline"
title: "离线交付流水线硬约束"
source: "AGENTS.md#P0 约束速览"
---
# 离线交付流水线硬约束

> 唯一规则主题：`apps/containers/offline-delivery` 的交付流水线（stage → build → pack → smoke）。
> 命令面与语义以 `bin/relpack` / `bin/relpack.ps1` 与 [AGENTS.md](../../AGENTS.md) 为准。

## §1 交付骨架零 Python / 零 `../` 契约与「纯移动」纪律

- `products/<产品>/release/` 是**客户可见契约**：客户侧仅需 Podman/Docker + 骨架本身，零 Python、零联网、零仓库外引用。
- 骨架内所有文件（`xmnnctl`、`xmnnctl.ps1`、`compose*.yaml`、`.env.example`、`README.md`、`artifacts/.gitignore`、`workspace/.gitkeep`）
  **逐字保持不变**（含行尾）；迁移必须用 `git mv` 保留历史，禁止顺带改端口、改凭证键、新增 GPU 覆盖或调整命令面。
- 唯一允许改写的例外：「开发仓库便捷壳」相关表述——须指向本应用 `bin/relpack`（该便捷壳随迁移删除）。
- 骨架内**禁止**出现指向仓库其他文件的相对路径（`../`）；`compose.yaml` 不得出现 `extends` 或 `build`
  （镜像一律来自本地归档，`pull_policy: never`）。
- 违反后果：客户拿到包后无法在无仓库环境下启动。改骨架前先读骨架自身的 `README.md` 与上文契约。

## §2 CRLF shebang 守卫（`pack` 前置 fail-fast）

- 无扩展名的 shebang 脚本（`xmnnctl`、`bin/relpack`、`bin/lib/*`）一旦被 CRLF 检出，
  Linux/WSL 首行报 `'/usr/bin/env: bash\r': No such file or directory`；内核先解析 shebang，脚本内自救无效。
- 守卫位置：`pack` **在导出归档之前**扫描骨架与 CLI 内所有 shebang 脚本，命中 CR 立即非零退出，
  **不产出坏字节**（绝不先打包再报错）。
- 修法（唯一正确路径）：`git add --renormalize .`（依赖仓库根 `.gitattributes` 中
  `**/relpack`、`**/relpack.ps1`、`**/xmnnctl`、`**/xmnnctl.ps1` 的 `text eol=lf` 显式规则）。
- 新增无扩展名 CLI 时必须同步在根 `.gitattributes` 增一行 `text eol=lf`，否则 `text=auto` 会在
  Windows 检出时写回 CRLF。

## §3 版本语义

- 交付版本默认取**暂存 wheel 的版本**（从 `xmnn-<版本>-cp314-...whl` 文件名解析，如 `1.2.1.dev0`）。
- GA/正式交付必须用 `pack --version V` **显式指定**，不依赖 wheel 名推断（避免 dev 后缀流入客户交付）。
- 同一版本只能对应一份归档；归档名固定 `xmnn-runtime-<版本>.tar.gz`，`release.json` 的
  `version` / `archive.file` / `wheel.version` 三者必须自洽。

## §4 形态感知 tag（`<IMAGE_NAME>:<形态>` + `:latest` 别名）

- `build` 产出**双 tag**：`<IMAGE_NAME>:<形态>`（形态感知，内容即身份）与 `<IMAGE_NAME>:latest`（通用别名，兼容历史引用）。
- 形态白名单仅 `cpu|cu130`；缺省来自 `products/<产品>/product.env` 的 `TORCH_DEFAULT`；
  `--torch` 单次覆盖同时改变 tag（杜绝「装 cu130、标 cpu」）。
- 禁止只打 `:latest`（CPU 与 cu130 内容不同却标签相同，会导致 `up --skip-build` 跑错镜像）。

## §5 归档原子性

- 导出链固定：`podman save <tag>` → `gzip -1` → `gzip -t` 校验 → **原子 `mv`** 落盘到 `release/artifacts/`。
- 先写临时文件、校验通过再 `mv`：任何中断都只能留下临时文件，**绝不在交付目录留截断归档**。
- `release.json` 中的 `archive.sha256` / `archive.size_bytes` 必须取自校验后的最终文件。

## §6 `release.json` 字段契约与 torch 标签双键回退

- 字段集（除 `pack_tool` 外与迁移前逐字一致）：`schema_version` / `product` / `version` / `wheel` /
  `image` / `archive` / `built_at` / `source_commit` / `pack_tool`；`pack_tool` 改为本应用标识。
- torch 版本读取顺序：镜像 LABEL `org.specweave.torch-version`（新键）**优先**，
  缺失时回退 `org.specweave.torch-cpu`（旧键）；两者皆缺时如实记 `null` 并告警，**不得臆测**。
- 改字段属客户契约变更：须同步骨架 `README.md`、本文档与 `docs/`，并补守卫测试。

## §7 禁依赖 `client` / `shared`；外部输入仅两项

- 本应用**禁止**引用 `apps/containers/client/` 与 `apps/containers/shared/` 的任何路径或代码
  （含 `overlays/_shared`、`jpman_client`、`jpman_common`、`invoke`）。
- 外部输入仅：① `../workspace/dist/<WHEEL_GLOB>`（预构建 wheel）；② 基镜像 `BASE_IMAGE_DEFAULT`
  （`localhost/jupyter-podman-rootless:latest`，由 `jupyter-podman-rootless` 应用产出）。
- 产品差异（镜像名、Containerfile 名、wheel glob、wheel 源目录、基镜像默认、torch 缺省、骨架目录名）
  **只允许**写在 `products/<产品>/product.env`；CLI 内不得内嵌 `xmnn` 等产品常量。
- 新增第二个交付产品 = 只新增 `products/<名>/`（含 `product.env` 与 Containerfile/脚本/冒烟/`release/`）
  并在文档登记，**CLI 代码零改动**。

## §8 Windows 一律 pwsh7，容器命令经 `wsl.exe` 桥接

- Windows 原生一律使用 `bin/relpack.ps1`（pwsh 7.4+）；**禁止** Windows PowerShell 5.1。
- 跨平台差异只在「容器命令在何处执行」一处：pwsh 版把容器子命令经
  `wsl.exe -d <发行版> -- bash <bin/relpack> <args>` 桥接给 bash 版，**不做逻辑分叉**。
- WSL 发行版优先级：`OFFLINE_DELIVERY_WSL_DISTRO` → `XMNN_WSL_DISTRO` → `COMPOSE_WSL_DISTRO` → `podman-machine-default`。
- 宿主侧参数校验、日志与失败指引须与 bash 版同形；`.ps1` 提交前须过 `.agents/scripts/check-pwsh7-compliance.py`。