# okw 命令签名与退出码对照（2026-10-13 对照 parser.py 实证）

事实源：`apps/dev-tools/openkylin-wsl-devkit/src/okw/cli/parser.py`（命令面以此为最终准）；领域行为见同目录 `src/okw/*.py`。okw 版本 0.1.0，入口点 `okw = okw.cli:main`。

## 发行版生命周期（无子命令组）

| 命令 | 签名 | 要点 |
|---|---|---|
| list | `okw list` | 列出发行版，`*` 标默认；末尾打印默认发行版星标保护快照 |
| status | `okw status <name>` | 不存在退出 1 |
| import | `okw import <image> --name <名称> --location <目录> [--version 2]` | 导入前校验 gzip 魔数 `1F 8B`，不符直接受控报错；超时 600 秒；注入 `WSL_UTF8=1`；失败 stderr 打印排障三问（位置漂移/内存不足/解压纯 tar） |
| export | `okw export <name> --output <文件>` | wsl --export 封装，600 秒 |
| unregister | `okw unregister <name> --yes` | 破坏性；无 `--yes` 返回退出码 2 且零写入 |
| exec | `okw exec <name> [--] <cmd...>` | 非交互；发行版不存在退出 1；空命令退出 2；建议用 `--` 分隔 |
| verify | `okw verify <name>` | 五步环境验收（os-release/用户/UID/systemd/包数）；包数基线参考 405，`dpkg -l` 含表头 5 行 |
| scaffold | `okw scaffold {deb,dput}` | 见下 |
| ref | `okw ref [series|wsl-troubleshoot|okbs|verify]` | 无主题打印可选列表；只读 |

### scaffold deb

`okw scaffold deb --project <名> [--series yangtze|nile|huanghe|1.0|2.0|3.0] [--version 0.1.0] [--output-dir .]`

### scaffold dput

`okw scaffold dput --openkylin-id <ID> [--output <文件>]`——无 `--output` 只打印片段，不写盘。

## podman 子命令组（发行版内 rootless Podman）

标准链：`preflight` → `install --yes` → `verify`。

| 子命令 | 签名 | 行为边界 |
|---|---|---|
| preflight | `okw podman preflight <name>` | 纯只读：不 apt update、不写文件、不动星标；APT 索引缺失标 UNKNOWN 并给行动建议；映射冲突会在 install 阶段拒绝追加 |
| install | `okw podman install <name> --yes` | root 身份：apt update+复查候选 → 装 4 个直接包（podman/uidmap/slirp4netns/fuse-overlayfs）→ 仅在标准区间 [100000,165536) 无冲突且文件无畸形时追加 subuid/subgid → 默认用户身份跑 rootless verify。不改软件源/wsl.conf/星标；漏 `--yes` 只打印 4 条副作用清单，退出码 2 |
| verify | `okw podman verify <name> [--smoke-image <LOCAL_IMAGE>]` | 默认用户身份只读检查映射/unshare/`podman info --rootless`，默认不跑容器；`--smoke-image` 必须本地已存在，缺失直接 FAIL，严禁隐式拉取 |

## compose 子命令组（xuan-compose/xc 下游引导）

前置：rootless Podman 已 verify 通过。标准链：`preflight` → `install --yes --source` → `verify [--smoke]`。

| 子命令 | 签名 | 行为边界 |
|---|---|---|
| preflight | `okw compose preflight <name> [--source <本地目录\|URL\|包名>]` | 只读不下载；uv/Python3.14/xc shim 缺失标 UNKNOWN（install 可补）；结构门与 rootless 门失败为 FAIL；本地源校验 pyproject.toml，Windows 路径自动转 `/mnt/<drive>` |
| install | `okw compose install <name> --yes --source <源> [--editable]` | 缺 uv 装到 `~/.local/bin`（免 root）→ `uv python install 3.14` 托管独立解释器 → `uv tool install` 装 xuan-compose 并生成 `xc`/`xuan-compose` 双 shim（已装则 --force 幂等）→ 双 shim `version --short` 验收。本地源默认拷贝安装，`--editable` 仅限本地源；漏 `--yes` 零写入退出 2 |
| verify | `okw compose verify <name> [--smoke]` | 只读核对双 shim 版本一致与 rootless 上下文；`--smoke` 在 /tmp 隔离目录写最小 compose.yaml 跑 `xc config --quiet`（内部触达 podman info），不起容器不拉镜像，结束即清理 |

源格式三选一：本地目录 / `git+https` 等 URL / PEP503 包名；okw 不内置任何默认源。

## image 子命令组（openKylin 开发容器镜像）

标准链：`build` → `verify`；均在指定发行版内以 **root 身份**执行。

| 子命令 | 签名 | 行为边界 |
|---|---|---|
| build | `okw image build <name> [--tag 3.0] [--base-image localhost/openkylin:3.0] [--pull-base] [--no-cache] [--context <目录>]` | 产物标签为 `localhost/openkylin-dev:<tag>`；podman 可用性 → 基底本地存在校验（默认禁拉，仅 `--pull-base` 放行）→ 构建上下文同步到发行版内 /tmp（Windows 路径自动转换）→ `podman build --format docker` |
| verify | `okw image verify <name> [--image localhost/openkylin-dev:3.0] [--no-boot]` | 本地存在（禁拉）→ P1–P8 静态探针（`--entrypoint /bin/bash`）→ 后台启动等 HEALTHCHECK → 服务探针（SSH/Jupyter 进程、22/8888、Jupyter HTTP 200）→ 清理；`--no-boot` 仅静态探针 |

容器操作全程 `--pull=never`，使用 G3 运行契约参数。

## 通用退出码（podman/compose/image 子命令组）

- `0`：全部 PASS / 操作成功。
- `1`：存在 FAIL（按报告中文指引修复后重试）；生命周期命令的运行时失败。
- `2`：用法错误；preflight/verify 仅 UNKNOWN；install 未提供 `--yes`（零写入）；`okw image`/`okw podman`/`okw compose` 空叶子命令回打帮助。

## 本机调用速记（PowerShell 7，PATH 裁剪环境）

```powershell
$py = "<USER_HOME>\AppData\Local\Programs\Python\Python314\python.exe"
& $py -m okw list
& $py -m okw import .\openKylin-3.0-wsl-amd64.wsl --name openKylin-3.0 --location D:\WSL\openKylin-3.0
& $py -m pytest -q   # cwd 必须在 apps\dev-tools\openkylin-wsl-devkit
```
