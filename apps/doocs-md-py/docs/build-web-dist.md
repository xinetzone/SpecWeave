---
title: doocs-md-py 前端产物构建与回退预案
source: d:/AI/.chaos/libs/md（doocs/md v2.1.0，commit 1bdad48d20048bddc8d32afb1b75a6475169f163）+ scripts/build-web-dist.sh / .ps1
date: 2026-10-16
---

# 前端产物（web-dist）构建与回退预案

本应用不含任何前端源码，Web UI 由**上游 `apps/web` 的 Vite 构建产物**镜像而来。产物落在 `src/doocs_md_py/assets/web-dist/`，**体积大、不入库**，仅哈希清单与许可证入库。

- 入库文件（3 个，见 [.gitignore](../.gitignore)）：`.gitkeep`、`MANIFEST.sha256`、`NOTICE`
- 不入库：`web-dist/*`（产物）、`web-dist-build/`（中间工作副本）、`data/`（SQLite 与本地存储）

> **重要**：fresh clone 后 `web-dist/` 内**没有 `index.html` 等产物**。此时 `mdpy render / upload / mcp` 三条路径完全可用；只有 `mdpy serve` 需要先构建产物，否则会以启动错误提示 dist 缺失。详见应用 [README.md](../README.md) 的快速开始。

## 一、前置条件

| 项 | 要求 |
|---|---|
| 上游源树 | `d:/AI/.chaos/libs/md`（默认路径，可用 `MD_SRC` 覆盖），工作树应干净以得到可信 `upstream_worktree_dirty=no` |
| 构建脚本 | [scripts/build-web-dist.sh](../scripts/build-web-dist.sh)（容器内执行）+ [scripts/build-web-dist.ps1](../scripts/build-web-dist.ps1)（Windows 侧入口，需 pwsh 7.4+） |
| 容器路线 | WSL 发行版 `openKylin-3.0` 内 podman 已存在镜像 `localhost/node:22-alpine`（`podman pull docker.m.daocloud.io/library/node:22-alpine` 后 tag；Docker Hub 直连不可达） |
| 依赖工具 | 容器内 `podman` + `rsync`；Windows 原生路线需 node v22.23.3 win-x64 + corepack |
| 版本锚点 | 上游 `package.json` 的 `version=2.1.0`，`upstream_commit=1bdad48d20048bddc8d32afb1b75a6475169f163`；pnpm 由 corepack 固定为 `pnpm@12.6.0` |

## 二、主路线：WSL + podman 容器构建

```bash
# 常规构建（保留工作副本，二次构建更快）
pwsh ./scripts/build-web-dist.ps1            # Windows 侧入口，默认发行版 openKylin-3.0
# 构建后清理 WSL 工作副本（pnpm store 卷保留）
$env:MD_CLEAN='1'; pwsh ./scripts/build-web-dist.ps1
# 指定其它上游源树
$env:MD_SRC='/mnt/d/path/to/md'; pwsh ./scripts/build-web-dist.ps1
```

`.ps1` 只做三件事：校验发行版与脚本存在、把 `.sh` 行尾 CRLF→LF（幂等）、以 `wsl -d <distro> bash -lc` 调用 `.sh`。真正的构建逻辑在 `.sh`：

1. **前置检查**：源树 `apps/web` 存在、`podman`/`rsync` 可用、`localhost/node:22-alpine` 镜像存在；采集 `upstream_commit` 与 `upstream_worktree_dirty`。
2. **源树同步到原生 ext4**：`rsync -a --delete` 到 `~/md-build/workspace`，排除 `node_modules` 与各 app 的 `dist`、`.turbo`。原因是源树位于 Windows drvfs（`/mnt/d`），海量小文件 I/O 极慢；**保留 `.git`**（postinstall 的 `simple-git-hooks` 需要）。
3. **容器内安装 + 构建**：`podman run --rm`，挂载工作副本与 pnpm store **具名卷**（`md-pnpm-store`，原生存储、跨次复用），`HOME=/tmp/home` + `corepack enable` 固定 pnpm 版本，registry 走 `https://registry.npmmirror.com`，随后 `pnpm install --frozen-lockfile` → `pnpm --filter @md/web run build:h5-netlify:only`，并以 `test -f apps/web/dist/index.html` 收口。
4. **产物同步**：清空 `web-dist/` 下除 `.gitkeep`/`NOTICE` 之外的所有内容，再 `cp -r` 拷贝 `apps/web/dist/.`。
5. **许可证与可复现清单**：拷贝上游 `LICENSE`，并按 `find + sort + sha256sum` 生成 `MANIFEST.sha256`（含 `built_at_utc`、`image`、`package_manager`、`build_env` 等溯源字段）。
6. **可选清理**：`MD_CLEAN=1` 时删除工作副本，pnpm store 卷保留。

**同源构建的关键**：`SERVER_ENV=NETLIFY` 且**清空** `VITE_MD_API_URL` / `VITE_SYNC_API_URL`（Vite `loadEnv` 中进程环境变量优先于 `.env` 文件），从而前端以"同源"模式构建、**零源码补丁**接入本应用后端；同时置 `VITE_ACCOUNT_UI_ENABLED` / `VITE_SYNC_UI_ENABLED` / `VITE_UPLOAD_VIA_API` 为 `true`。

**可重入性**：脚本可重复执行；默认保留工作副本与 `node_modules` 以加速二次构建，`MD_CLEAN=1` 时清理。

## 三、回退预案 A：容器/WSL 路线不可用

**触发条件**（本机已实际发生）：WSL 虚拟机被宿主内存回收导致 `wsl.exe 0xc00000fd`，容器路线无法完成。

**处置**：改用 **Windows 原生构建**（本次实际采用，证据见 `MANIFEST.sha256` 的 `node=` 与 `build_note=` 字段）：

| 项 | 本机实测值 |
|---|---|
| 运行时 | `node=v22.23.3 win-x64`（官方 `node-v22.23.3-win-x64.zip`，SHA256 经 **npmmirror 与华为云双镜像交叉校验**） |
| 包管理器 | `pnpm@12.6.0 via corepack`，`--frozen-lockfile --ignore-scripts` |
| registry | `https://registry.npmmirror.com` |
| 构建环境变量 | `SERVER_ENV=NETLIFY`、`VITE_MD_API_URL=`（空，同源）、`VITE_SYNC_API_URL=`（空）、`VITE_ACCOUNT_UI_ENABLED=true`、`VITE_SYNC_UI_ENABLED=true`、`VITE_UPLOAD_VIA_API=true` |
| 构建目标 | 与 `.sh` 一致：`pnpm --filter @md/web run build:h5-netlify:only` |
| 构建时间 | `built_at_utc=2026-10-15T07:06:54Z` |
| 上游洁净度 | `upstream_worktree_dirty=no` |

> 与 `.sh` 的两点差异：① `image=` 字段改为 `node=`；② 因在 Windows 原生环境直接以 corepack 启用 pnpm，安装期使用 `--ignore-scripts`（容器路线保留 git hooks 所需脚本）。
>
> **结论**：两条路线产出的 `MANIFEST.sha256` 除溯源字段外**内容结构一致**，`build_env` 行逐字相同——即"以哪条路线构建"只影响溯源元数据，不影响产物形态。

**核验**：构建完成后按 `MANIFEST.sha256` 逐文件复算 SHA256；任何条目不一致即视为产物不可信，必须重构建而非手工修补。

## 四、回退预案 B：产物异常 / 源树不可用

| 场景 | 处置 |
|---|---|
| 产物异常（`index.html` 缺失、哈希不符、页面白屏） | 产物不入库，**直接删除 `web-dist/` 下全部产物**（保留 `.gitkeep`/`MANIFEST.sha256`/`NOTICE`）后重跑构建；不得手工编辑产物文件 |
| 上游源树缺失或版本不符 | 从 `https://github.com/doocs/md` 拉取 commit `1bdad48d20048bddc8d32afb1b75a6475169f163` 到 `MD_SRC`（`MANIFEST.sha256` 的 `upstream=`/`upstream_commit=` 即权威锚点），再按第二节或第三节构建 |
| 上游已升级、需要换基线 | 先复核 [contract-differences.md](contract-differences.md) 与 [contract-mapping.md](contract-mapping.md) 的差异台账，再构建并在本文件与 `MANIFEST.sha256` 同步新 `upstream_commit` |
| 需要完全离线部署 | 先在有网环境完成构建，再把 `/mnt/ai` 等大容量位置作为产物中转；产物最终仍须落在 `src/doocs_md_py/assets/web-dist/`（未被版本控制跟踪，需随交付包一并打包） |
| 仅需后端能力（无 Web UI） | 不构建产物：`mdpy render` / `mdpy upload` / `mdpy mcp` 与 API 的 `dist` 无关；`mdpy serve` 会给出 dist 缺失的启动错误 |

## 五、MANIFEST.sha256 字段说明

| 字段 | 含义 |
|---|---|
| `upstream` / `upstream_commit` / `upstream_worktree_dirty` | 上游仓库地址、精确 commit、构建时工作树是否有改动 |
| `built_at_utc` | 构建时刻（UTC） |
| `node=` 或 `image=` | 构建运行时的二选一溯源（Windows 原生 / 容器） |
| `package_manager` / `npm_registry` | pnpm 版本与来源与包源 |
| `build_env` / `build_env2` | 构建环境变量集合（同源模式的关键证据） |
| `build_note` | 本次实测的路线说明（当前记录 Windows 原生回退原因） |
| `license` | WTFPL-2.0，版权归 doocs/md 上游贡献者 |
| `# SHA256` 之后 | 逐文件哈希（排序稳定，可直接 `sha256sum -c` 复算） |

## 六、构建产物与运行时的关系

- `mdpy serve` 通过 [web_dist.py](../src/doocs_md_py/server/web_dist.py) 同源托管该目录：命中哈希资产给长缓存，其余路径回退 `index.html`（SPA）（见 [contract-differences.md](contract-differences.md) 的 CD-6）。
- 前端以同源模式构建后，账密/同步/上传等能力直接打到本应用 API，无需额外反代配置。
- 产物目录只读消费，**运行时不得写入**；应用自身的本地数据落在 `data/`（SQLite 与 `data/uploads`）。
