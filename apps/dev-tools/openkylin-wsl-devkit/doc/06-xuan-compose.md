---
type: "Tutorial"
title: "okw 引导 xuan-compose（xc）指南"
---

# okw 引导 xuan-compose（xc）指南

`okw compose` 是 [`okw podman`](03-podman-rootless.md) 就绪之后的**下游引导层**：在已经具备 rootless Podman 的 openKylin WSL 发行版内，以普通用户身份引导安装 [xuan-compose](https://github.com/xinetzone/xuanspace/tree/main/libs/xuan-compose)（命令名 `xc`，同时提供 `xuan-compose` 别名），并完成只读验收与端到端配置探活。它不负责安装 Podman，也不切换 WSL 默认发行版、不修改软件源、不编辑 `wsl.conf`。

## 许可证边界（先读）

xuan-compose 是 **GPL-2.0-only** 第三方软件，而 okw 自身采用 Apache-2.0 许可证。为避免许可证污染，okw 对 xuan-compose 采取**纯 CLI 聚合引导**，边界如下：

- okw **不 import、不复制、不链接、不分发** xuan-compose 的任何源码或制品；
- okw 仅在你**显式授权**（`install --yes`）后，于你自己的发行版内，按你**亲自指定的来源**（`--source`）通过 [uv](https://docs.astral.sh/uv/) 安装，与 `apt install` 一个 GPL 包的性质相同；
- xuan-compose 的源码与许可证文本以你给定的安装源项目为准。安装帮助、README 与本指南均显著声明该边界。

此外，xuan-compose 要求 **Python ≥ 3.14**，而 openKylin 3.0 的系统 Python 为 3.12。okw 自身保持 Python ≥ 3.10 且**零第三方运行时依赖**，绝不把 xuan-compose 作为自己的依赖；所需的 3.14 解释器由 uv 以 python-build-standalone 形式托管安装到用户 HOME，与系统 Python 完全隔离。

## 前置条件

| 条件 | 说明 |
|---|---|
| WSL2 + openKylin 发行版 | 结构门：发行版已注册、WSL2、`/etc/os-release` 中 `ID=openkylin`、默认用户为非 root |
| rootless Podman 就绪 | 必须先通过 `okw podman verify <name>`；未就绪时 compose 直接 FAIL 并提示先装 Podman |
| 安装源可达 | 本地源码目录（Windows 路径亦可）、`git+https` 等 URL，或 PEP 503 包名；okw **不内置任何默认源** |
| 网络（仅 install 阶段） | 下载 uv（约数十 MB）、托管 CPython 3.14（约 60 MB）及 xuan-compose 依赖；preflight/verify 不联网 |

## 三步流程

```text
okw compose preflight <name> [--source <来源>]
okw compose install  <name> --source <来源> --yes [--editable]
okw compose verify   <name> [--smoke]
```

1. `preflight` **只读**探测结构门、rootless Podman、用户级 uv、uv 托管的 Python 3.14、`xc`/`xuan-compose` 双 shim；给 `--source` 时额外校验本地源的 `pyproject.toml`（URL/包名源不触网，记 UNKNOWN）。uv、Python、shim 缺失记 **UNKNOWN**（install 可自动补齐，不阻断）；结构门与 rootless Podman 失败记 FAIL。
2. `install` 必须显式提供 `--yes` 与 `--source`。省略 `--yes` 时只打印四步副作用清单与 GPL 声明，以退出码 2 中止，**零 WSL 调用、零写入**。
3. `verify` 以默认用户全路径执行双 shim 的 `version --short` 并比对版本一致；加 `--smoke` 时在隔离临时目录跑一次 `xc config --quiet` 端到端探活。

## 安装会执行什么

提供 `--yes` 且 rootless Podman 就绪后，全部操作以**默认普通用户**身份落在其 HOME 下（无 `apt`、无 `sudo`、无 root）：

1. 若 `~/.local/bin/uv` 缺失，经官方脚本 `curl -LsSf <installer> | sh` 把 uv 安装到 `~/.local/bin`（仅用户目录）；uv 已存在则跳过。
2. 获取托管 Python 3.14：uv 本次新装时直接 `uv python install 3.14`；uv 已存在时先 `uv python list` 判定，标准 CPython 3.14 已托管则跳过（不重复下载），自由线程（freethreaded）变体不计入。
3. 执行 `uv tool install [--force] [--editable] --python 3.14 <来源>`，把 xuan-compose 及其依赖装进 3.14 隔离环境，并在 `~/.local/bin` 生成 `xc`、`xuan-compose` 两个 shim；检测到已登记时自动加 `--force` 幂等重装。
4. 以**全路径**执行 `~/.local/bin/xuan-compose version --short` 与 `~/.local/bin/xc version --short`，确认二者均可执行且版本一致。之所以用全路径，是因为非 login shell 的 `PATH` 默认不含 `~/.local/bin`。

安装不宣称事务回滚：uv、Python 或 tool 的部分下载可能已生效；各步骤幂等，修复后直接重跑即可。

## 安装源三形态

`--source` 必填，由 okw 自动归类，无法识别时以用法错误（退出码 2）拒绝且不产生任何 WSL 调用：

| 形态 | 判定示例 | 处理 |
|---|---|---|
| 本地目录 | `D:\path\xuan-compose`、`./libs/xuan-compose`、`~/xc` | Windows 路径自动转为 `/mnt/d/path/xuan-compose`；安装前先 `test -f <目录>/pyproject.toml`，缺失即在任何下载前中止。默认**拷贝安装**，加 `--editable` 才以可编辑模式安装 |
| URL / VCS | `git+https://github.com/owner/repo.git`、`https://…/pkg.tar.gz`、`git@host:org/repo.git` | 原样交给 uv；预检不触网（记 UNKNOWN）。`--editable` 不允许与 URL 源合用 |
| 包名 | `xuan-compose`、`xuan-compose[extra]==1.6.0` | 交给 uv 从包索引解析；为将来发布到 PyPI 预留，当前项目尚未发布 |

### xuan-compose 的真实来源

上表是 okw 支持的三种**通用**来源形态；具体到 xuan-compose，其当前发布事实为（以源码项目为准）：

- xuan-compose **不是独立 Git 仓库**，而是 [`xinetzone/xuanspace`](https://github.com/xinetzone/xuanspace) monorepo 中的子目录 `libs/xuan-compose`，且 monorepo 根有自己的 `pyproject.toml`；
- 项目当前**未发布到 PyPI**，上游 README 的安装方式即在该子目录内本地安装。

因此**已验证、推荐**的来源是本地源码目录（本指南的全部实机验证均使用此源）：

```powershell
# 本地源码目录（Windows 路径自动转为 /mnt/d/...；默认拷贝安装，加 --editable 为可编辑安装）
okw compose preflight openKylin-3.0 --source D:\AI\projects\xuanspace\libs\xuan-compose
okw compose install  openKylin-3.0 --yes    --source D:\AI\projects\xuanspace\libs\xuan-compose
okw compose verify   openKylin-3.0 --smoke
```

若确实要走 VCS，由于包位于 monorepo 子目录，URL 必须携带 `subdirectory` 片段，否则 uv 会解析到 monorepo 根包：

```text
git+https://github.com/xinetzone/xuanspace.git#subdirectory=libs/xuan-compose
```

> 该 VCS 写法需要你对 `xinetzone/xuanspace` 仓库具有访问权限，且**未在本指南的实机流程中验证**；网络受限制时同样适用后文的镜像/代理手段。请以本地源码目录为准。

## 安装形态：拷贝安装与可编辑安装（`--editable`）

本地源支持两种安装形态，实机（openKylin-3.0）均通过 `preflight` / `install` / `verify --smoke` 全链路验证：

| 形态 | 命令 | 包装落点 | 适用场景 |
|---|---|---|---|
| 拷贝安装（默认） | `install --source <本地目录>` | uv 把安装时刻的源码快照装入 tool 隔离环境（`~/.local/share/uv/tools/xuan-compose`），此后源码目录的改动不影响已装工具 | 固定使用、与日常运行环境一致 |
| 可编辑安装 | `install --editable --source <本地目录>` | 不在隔离环境放包体副本，由 scikit-build-core 的 editable finder（site-packages 内 `_editable_skbc_xuan_compose.pth`/`.py`）把导入路径直接指向源码目录的 `src/` | 在源码树上开发调试 xuan-compose |

可编辑形态实测：tool 解释器内 `xuan_compose.__file__` 解析到源码树而非隔离环境，例如源在 `D:\AI\projects\xuanspace\libs\xuan-compose` 时解析为 `/mnt/d/AI/projects/xuanspace/libs/xuan-compose/src/xuan_compose/__init__.py`，模块导入非空、`xc`/`xuan-compose` 双 shim 版本一致。因此在 Windows 侧修改源码后，**重新执行一次 `xc` 命令即按源码树加载新代码**（每次进程启动重新解析导入路径；`xc` 是短命命令而非常驻守护进程，不存在自动热重载）。

monorepo 边界：editable finder 只挂载 `libs/xuan-compose/src` 这一条映射，不会把 monorepo 根枢纽包卷进来；xuan-compose 的运行时依赖仅为 `python-dotenv` 与 `pyyaml`。在发行版内可用以下命令自行核对当前究竟是哪种形态（默认用户身份）：

```bash
~/.local/share/uv/tools/xuan-compose/bin/python -c \
  "import xuan_compose; print(xuan_compose.__file__, xuan_compose.__version__)"
# 拷贝形态：__file__ 位于 .../uv/tools/xuan-compose/lib/python3.14/site-packages/ 下
# 可编辑形态：__file__ 位于源码目录的 src/xuan_compose/__init__.py
```

两种形态相互切换只需重跑 `install`（已登记时 uv 自动 `--force` 幂等重装）：开发时加 `--editable`，回到与日常运行一致的隔离形态时去掉它再装一次即可。

## compose 冒烟（`--smoke`）

`verify --smoke` 不是容器冒烟，而是 **xc ↔ Podman 的配置解析探活**：

1. 前置检查任一为 FAIL 则不执行冒烟，直接报告“前置检查存在 FAIL”；
2. 在 `/tmp/okw-smoke-XXXXXXXX` 创建隔离临时目录，`trap` 保证结束即清理；
3. 写入内容为 `services: {}` 的最小 `compose.yaml`，执行 `xc config --quiet`；
4. xc 在配置解析阶段会探测 Podman 版本并触达 `podman info`，因此能验证整条链路，但**不 `up`/`down`、不起容器、不拉镜像**（脚本中禁止任何 pull 动作）；
5. 实机核对（两种安装形态各跑一次）：冒烟结束后 `podman ps -a` 与 `podman images` 均为空、`/tmp/okw-smoke-*` 已随 `trap` 清理，不留容器、镜像或临时目录。

## 退出码

| 退出码 | 含义 |
|---|---|
| `0` | 检查或安装全部 PASS（verify `--smoke` 时含冒烟通过） |
| `1` | 存在 FAIL；报告包含中文修复指引 |
| `2` | 用法错误（畸形 `--source`、URL 源配 `--editable`）、`preflight`/`verify` 仅有 UNKNOWN，或 `install` 未提供 `--yes`（零写入） |

## 网络问题与镜像指引

install 阶段有三类对外下载，国内网络都可能很慢（实测 GitHub 直链曾低至约 4 KB/s），okw 会按失败阶段给出环境变量提示，但**不会自动改写你的环境、也不内置任何镜像**。可用 uv 官方支持的环境变量分别提速：

| 下载阶段 | 环境变量 | 作用 |
|---|---|---|
| uv 二进制（install.sh 引导） | `UV_DOWNLOAD_URL` | 替换 uv 安装包下载基址（脚本在其后拼接 `/<制品名>`） |
| 托管 CPython 3.14 | `UV_PYTHON_INSTALL_MIRROR` | 替换 python-build-standalone 的 releases 下载前缀 |
| xuan-compose 构建/运行依赖（scikit-build-core、pyyaml、python-dotenv 等） | `UV_DEFAULT_INDEX`（或 `UV_INDEX_URL`） | 替换 PyPI 包索引 |

### Windows 侧正确注入方式（WSLENV 透传）

okw 运行在 Windows，经由非交互的 `wsl --` 在发行版内执行，因此**仅在发行版交互 shell 里 `export` 不会对 okw 生效**（该会话不复用）。okw 会原样继承当前 Windows 会话环境，需用 WSL 的 `WSLENV`（`/u` 表示 Windows→WSL 单向透传，勿加会改写路径的 `/p`）把变量带进去。在运行 install 的同一个 PowerShell 会话中：

```powershell
# 第三方 GitHub 加速前缀 + 清华 PyPI，仅为示例，可用性请自行甄别
$env:WSLENV = "UV_DOWNLOAD_URL/u:UV_PYTHON_INSTALL_MIRROR/u:UV_DEFAULT_INDEX/u"
$env:UV_DOWNLOAD_URL = "https://<你的-github-代理>/https://github.com/astral-sh/uv/releases/download/<UV版本>"
$env:UV_PYTHON_INSTALL_MIRROR = "https://<你的-github-代理>/https://github.com/astral-sh/python-build-standalone/releases/download"
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
okw compose install <发行版> --yes --source <来源>
```

注意：

- `UV_DOWNLOAD_URL` 需与 install.sh 当前拉取的 uv 版本目录一致；脚本也支持版本无关的 `INSTALLER_BASE_URL`（仅替换主机，值形如 `https://<代理>/https://github.com`）。
- GitHub 加速代理为第三方服务，不归属 astral/uv；uv 安装脚本对下载制品有校验和校验，被篡改会直接失败，但仍建议你自行评估可信度。
- 这些变量只影响 uv/安装脚本，okw 自身仍零第三方依赖、不读取也不硬编码任何镜像地址。

## 常见问题

- **提示“rootless Podman 尚未就绪”？** compose 是 podman 的下游。先执行 `okw podman install <name> --yes` 与 `okw podman verify <name>`，通过后再回到 compose。
- **必须装 Python 3.14 吗？会动系统 Python 吗？** xuan-compose 强制要求 3.14，但该解释器由 uv 装在用户 HOME 的独立目录，不修改系统 3.12，也不影响 apt。okw 自身仍在你 Windows 侧的 Python ≥3.10 上运行。
- **`xc: 命令找不到`？** 非 login shell 的 `PATH` 不含 `~/.local/bin`。okw 一律用全路径验收；你在发行版交互式 shell 中可将 `export PATH="$HOME/.local/bin:$PATH"` 加入 `~/.bashrc`，或直接用 `~/.local/bin/xc`。
- **两个 shim 版本不一致？** 报告记 FAIL；重跑 `okw compose install <name> --yes --source …`，uv 会以 `--force` 幂等重装并重建 shim。
- **为什么 `xc version` 报 `1.6.0+xuan.1`，源码 `pyproject.toml` 里却是 `version = "0.1.0"`？** 这是两套用途不同的版本号，并非装错：`pyproject.toml` 的 `0.1.0` 是**打包元数据版本**（项目当前标注 `Development Status :: 3 - Alpha` 的分发基线）；运行时版本取包内 `src/xuan_compose/__init__.py` 的 `__version__ = "1.6.0+xuan.1"`，标识本项目与上游 containers/podman-compose 1.6.0 的对等重构关系。`xc version --short`、`xuan-compose version --short` 与 okw 验收比对显示的都是运行时版本。二者可能不同步，确切取值请以源码这两个位置的当前内容为准。
- **本地源 `pyproject.toml` 校验失败？** 确认 `--source` 指向 xuan-compose 的项目根目录（Windows 路径会自动转 `/mnt/<drive>/...`），且该盘符在发行版内已挂载可访问。
- **GPL 会不会传染我的项目？** okw 只做安装引导、不分发不链接 xuan-compose；你在自己机器上安装并运行一个 GPL 工具不影响你自有代码的许可证。若要再分发 xuan-compose 本身，请遵循其 GPL-2.0-only 条款。

发行版名称可通过 `okw list` 或 `wsl -l -v` 查询。

## 相关页面

- [文档首页](index.md)：工具定位、环境要求与全部主题入口。
- [rootless Podman 指南](03-podman-rootless.md)：compose 的前置条件与三步验收。
- [命令参考](02-command-reference.md)：`okw compose` 的命令速查与退出码。
