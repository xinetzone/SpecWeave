---
id: "jupyter-podman-client-xmnn-overlay"
title: "工作负载叠加层：xmnn-dev（xmnn.*）"
source: "README.md#13-工作负载叠加层xmnn-devxmnn-命令opt-in"
---
# 工作负载叠加层：xmnn-dev（xmnn.* 命令，opt-in）

第二个声明式工作负载栈：XMNN **源码调试 + wheel 打包**开发环境。容器内具备
LLVM/Clang 22.1.8 + CMake/Ninja/ccache + Nuitka 4.2.1 工具链；运行时把
`npu_tvm`、`npuusertools`、`models` 三个宿主源码目录 bind 挂载进容器，
SSH/Jupyter（`Python 3.14 (xmnn dev)` 内核，cp314 GIL）即可直接调试挂载源码，
并能一键编译 TVM、用 Nuitka 打出 `xmnn-*.whl`（产物落 workspace/dist）。

```bash
pip install -e ".[compose]"           # 与 quant.* 同一个可选依赖
invoke xmnn.build                     # 构建参数（pip/conda 源、基底）默认读 .env
invoke xmnn.up --skip-build           # 启动栈：SSH 2223 / Jupyter 8890
invoke xmnn.smoke                     # 工具链守卫 + 源码挂载检查
invoke xmnn.build-tvm                 # 可选：栈内编译 build/libtvm.so（已存在则跳过）
invoke xmnn.wheel                     # Nuitka 全流程打包，wheel 落 workspace/dist
invoke xmnn.down                       # 停止清理（ccache / Jupyter 登录态 / SSH host key 卷默认保留）
```

- **构建参数单一事实源（C15）**：`invoke xmnn.build` 与 `up` 的内联构建都读 `.env`
  的 `PIP_MIRROR` / `CONDA_MIRROR` / `BASE_IMAGE` / `TORCH_FLAVOR`（无前缀，与
  compose 段 `${KEY:-默认}` 同键）——三处同值才共享层缓存。换镜像源请写 `.env`
  而非 `--pip-mirror`（CLI 旗标对 `up`/compose 不可见），见
  [02-invoke-reference.md](02-invoke-reference.md#参数契约)。

- **构建执行者唯一（C16）**：`xmnn.up` 恒 `up -d --no-build`，镜像只由内核构建。
  默认 `xmnn.up` 内联构建一次即起容器；`--skip-build` 不做任何构建，故要求本地
  已有镜像（缺失立即 Exit 1，指引 `xmnn.up` / `xmnn.build`）。compose 的
  `build:` 段仅服务裸 `podman-compose` 路径。

- **端口默认 2223/8890**：与 quant 栈错开，两个栈可并行运行。
- **compose 公共段继承（extends）**：rootless 三必需、凭证四变量、公共
  labels/restart 与 `network_mode: bridge` 统一在
  [../_shared/base-rootless.yaml](../overlays/_shared/base-rootless.yaml)
  （三栈共享单一事实源），栈 compose.yaml 以 extends 继承，只保留栈专属
  image/build/ports/四个 bind/调试 env/组件 label；`xmnn-ccache`、`xmnn-jupyter`、
  `xmnn-ssh-host-keys` 命名卷等栈专属卷仍在栈文件声明。
- **Jupyter 登录态持久化（C22）**：命名卷 `xmnn-jupyter` 挂容器内
  `/home/devuser/.local/share/jupyter`（cookie/notebook 签名密钥所在目录，
  镜像内属主 1000:1000/mode 700，新卷 copy-up 属主实测保持），普通
  `down/up` 重建后浏览器旧标签页**免重登**；仅 `down --volumes` 与
  `xmnn-ccache` 一并清除。修复前重建即轮换密钥，旧标签页 Terminal/notebook
  请求在浏览器侧被中止（服务端零日志），排障见
  [04 速查 C-I6](04-troubleshooting-guide.md)。同时 `invoke xmnn.up` 成功横幅
  打印「直达」URL（`/lab?token=...`，免登录，token 勿外传）——token 取 `.env`
  预设值，留空则**回读容器内自动生成值**（C24，见下文「凭证」段）。
- **SSH host key 持久化**：命名卷 `xmnn-ssh-host-keys` 挂容器内
  `/var/lib/jpman/ssh-host-keys`，`down/up` 重建容器**不再轮换主机指纹**，
  客户端 `known_hosts` 无需反复 `ssh-keygen -R` 清理（未挂载时基底 entrypoint
  回退「容器层生成 + 重建即轮换」并打 WARN；卷名与落点同客户交付栈
  `overlays/xmnn-runtime/release/compose.yaml`）。仅 `down --volumes` 与
  上述两卷一并清除（删后指纹轮换属预期）。
- **源码路径**：默认挂载仓库根 `external/chaos/{npu_tvm,npuusertools,models}`；
  可在 `.env` 用 `NPU_TVM_PATH` / `NPUUSERTOOLS_PATH` / `MODELS_PATH`
  覆盖（invoke 路径做存在性硬校验）。TVM 全量编译在 9p 上较慢，可把路径
  指向 WSL 原生克隆。
- **Windows 原生自动桥接**：同 quant.*（默认桥接 `podman-machine-default`；
  `COMPOSE_WSL_DISTRO` 可指其他发行版，`none` 关闭并回退门禁）。
- **两个过程：镜像构建（有网） → 离线开发（无网）**：过程一在有网侧
  `invoke xmnn.build` + `invoke xmnn.save`（导出 tar.gz + manifest/SHA256 归档）
  ——镜像自足性由**构建期离线完备性守卫**（`smoke/_toolchain_guards.py` §7）实测
  断言（编译/打包前端可解析 + pyproject 声明的全部运行时依赖已装），缺口
  在有网侧 fail-fast；过程二在无网侧 `invoke xmnn.load --path <归档>` 导入 →
  `invoke xmnn.up --offline`（等价 `.env` 里 `XMNN_OFFLINE=1`）→ `build-tvm` /
  `wheel` / `verify-wheel.sh` 全部离线可用（脚本内已无联网点）。离线是
  **全链路**语义：不构建（追加 `--no-build`）、镜像缺失 fail-fast 给中文指引、
  容器内打包禁网硬失败（numpy/scipy 不再 pip 兜底、Nuitka 不自动下载）；无网侧
  **不补装依赖**，缺项一律回过程一。无网**从零构建镜像**仍不支持（构建期
  apt/mamba/pip 均需联网）。
- **对 external/chaos/ai 零依赖**：打包脚本与元数据自包含于叠加层；
  外部源码树只读挂载且**全程只读**（2026-09-21 起 `build-wheel.sh` 不再向任何
  `__init__.py` 注入/还原 AST 兼容层：ast 遗留节点改由运行期补丁兜底——
  `_xmnn_bootstrap.py` 经 `.pth` 启动钩子 + `xmnn/vta_compat.apply_ast_compat()`，
  故无 `.bak_*`、无「注入态」中间态，SIGKILL/OOM 不污染工作树）。
- **GPU 与 torch 可选能力（C18·C19·C20·C25，默认全关）**：两者**分属两个正交维度**——
  **运行期维度（设备透传）只由 `up --gpu` 决定，构建期维度（torch 形态）只由
  `build --torch` 决定**，因此**没有也不该有 `build --gpu`**：透传只改 compose
  文件集（`--device` + 只读库 bind），**不动镜像内容**，构建期没有 GPU 相关对象可改
  （镜像内唯一与 GPU 相关的差异是 torch 形态，已由 `--torch` 承担）。
  ① **GPU（运行期）** —— 仅 `invoke xmnn.up --gpu` 才追加 GPU 覆盖文件，设备由
  `GPU_DEVICE` 决定（`/` 开头=宿主机设备路径，否则=CDI
  引用如 `nvidia.com/gpu=all`，与根 `invoke run --gpu` 同键同语义）；**未设/空时自动
  探测** `/dev/dri → /dev/dxg`（C19，不再是「回退 `/dev/dri`」——WSL2 无 `/dev/dri`，
  缺省直接透传会 `stat` 失败 exit 125）；探测/校验在 **podman 宿主侧**执行，失败
  fail-fast 给中文指引。WSL2 形态自动改用 `compose.gpu.wsl.yaml`（`/dev/dxg` +
  三条只读 bind：单文件 `libcuda.so.1`、单文件 `libdxcore.so` 与
  `/usr/lib/wsl/drivers` 目录，**不设 `LD_LIBRARY_PATH`**）。② **torch（构建期）** —— 仅
  `invoke xmnn.build --torch cpu|cu130`（或 `.env TORCH_FLAVOR=`）才在 base env
  `/opt/conda` 装 `torch==2.14.0`（白名单取值，索引 `download.pytorch.org/whl/<flavor>`；
  cu130 是当前唯一与 CPU 侧同 pin 的 CUDA 索引）；形态落 `/opt/xmnn-torch-flavor`，
  构建期守卫 §8 断言「声明 vs 实物」。**cu130 形态同时提供 CUDA 编译器工具链
  nvcc（C25，2026-09-20 起）**：容器内 `nvcc -V` 可用（命令 `/usr/local/bin/nvcc`
  包装器 → `/usr/local/cuda` 农场，`CUDA_HOME=/usr/local/cuda`），可编译 + 链接
  `.cu`（`-lcudart` 可用）；编译器 pin **13.4.92**（基座 Ubuntu 26.04 / glibc 2.43
  与 CUDA 13.0 的 crt 头规格冲突，13.0 系实测编不过），**`""`/`cpu` 形态零 CUDA
  编译器**；构建期守卫 §9 以「真编译 + 真链接最小 `.cu`」实测（不做假通过）。
  注意 `nvidia-smi` **不在**容器内（属运行期 WSL 形态，另案）。细节见
  [.agents/rules/xmnn-overlay.md](../.agents/rules/xmnn-overlay.md) §11.6。
  flavor **不参与镜像 tag**，改后须重建镜像；
  但 **形态会写进归档名**（C20）：`save` 读镜像 LABEL 命名
  `...-torch-<形态>-<id>-<时间戳>.tar.gz`，`load` 按 `.env TORCH_FLAVOR` 挑归档并在
  形态不符时 Exit(1)——同一 tag 的 cpu / cu130 归档由此可辨识，避免无网侧静默导入错形态。
  ③ **两维度可自由组合：`invoke xmnn.up --gpu --offline` 可用**（2026-09-20 实测）——
  `--offline` 只禁构建（强制跳过构建 + 本地镜像存在性预检），与 GPU 解析**零耦合**
  （设备探测是纯宿主侧 `test -e`，离线不需任何网络）；`up` 的形参面本就是能力并集
  （详见 [.agents/rules/xmnn-overlay.md](../.agents/rules/xmnn-overlay.md) §11.3）。
  离线侧完整序列：无网机 `invoke xmnn.load --path <归档>` →
  `invoke xmnn.up --gpu --offline`；CUDA 版 torch 属**镜像内容**，只能在有网侧
  `build --torch cu130 && save` 备好，离线侧不补装。
  详细用法见 [overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md#gpu-与-torch-可选能力默认全关c18c19c20)，
  WSL2 实测矩阵与排障见 [04-troubleshooting-guide.md](04-troubleshooting-guide.md) W-I16。

## 启动后连接：Jupyter 与 SSH

`invoke xmnn.up` 成功后打印**可直接复制的命令与地址**（`SSH ssh -p 2223
devuser@localhost` / `Jupyter localhost:8890`），两个服务由容器内 supervisord
托管；密码/token
取决于 `.env` 的凭证四变量（随
[_shared/base-rootless.yaml](../overlays/_shared/base-rootless.yaml)
统一注入，留空即容器首启自动生成）：

**`up` 会等 Jupyter 真正应答才算就绪（C21）**：`up -d` 返回只代表**容器**在跑，
rootless 端口转发器在容器起的瞬间就 accept 宿主端口，而容器内 jupyter 首次
listen 需数十秒（实测 66s）。窗口期内打开浏览器会得到 `ERR_EMPTY_RESPONSE`
（**不是** `ECONNREFUSED`），故 `up` 收尾按**应用层 HTTP 应答**轮询宿主端口：
就绪打印「Jupyter 已就绪（addr → HTTP status）」；超过 120s 未应答**不判失败**，
只提示「容器已在运行，稍后刷新浏览器即可」并给出 `invoke xmnn.logs`。四栈
共享同一实现（内核 `up_stack`），无需逐栈处理。手工自检见
[04-troubleshooting-guide.md](04-troubleshooting-guide.md) W-I18。

| 服务 | 地址 | 凭证 |
|---|---|---|
| JupyterLab | http://localhost:8890 | `JUPYTER_TOKEN`（留空自动生成 32 位） |
| SSH | `ssh -p 2223 devuser@localhost` | `USER_PASSWORD`（留空自动生成 16 位）；亦可设 `SSH_PUBLIC_KEY` 免密 |

**SSH 会话自带源码调试环境（C30）**：`PYTHONPATH`/`TVM_LIBRARY_PATH`/
`LD_LIBRARY_PATH`/`NPU_TOOLS_ROOT`/`XMNN_TOOLS_ROOT` 由 compose `environment`
注入容器与 Jupyter 内核，而 **sshd 派生的 SSH 会话不继承容器 config env**，
故镜像内 `setup-ssh-env.sh` 另以 `/etc/profile.d/50-xmnn-dev-env.sh`（login
shell）+ `sshd_config` 的 `SetEnv`（覆盖 `ssh host "cmd"` 非交互形态）双通道
补齐——`ssh -p 2223` 进去即可直接 `import tvm, xmnn`，无需手工 `export`。
注意 SSH 默认落在 **main env**（cp314t，无 numpy），调试/打包请用
`/opt/conda/bin/python` 或先 `conda activate base`。

**自动生成的凭证会由 `up` 横幅回读打印（C24）**：`.env` 的
`USER_PASSWORD`/`JUPYTER_TOKEN` 留空时，值由容器内 entrypoint 用 `pwgen`
生成并只写进**容器启动日志**，因此 `invoke xmnn.up` 收尾会从容器日志**头部**
回读实际值并打印：

```
        密码    devuser / <自动生成的 16 位密码>
        直达    http://localhost:8890/lab?token=<自动生成的 32 位 token>
```

`up` 横幅看不到（容器未运行、或该容器是 C24 之前启动的）时再查日志：

```bash
invoke xmnn.logs   # 找「[IMPORTANT] devuser password: ...」与「Token: ...」
                   # Ctrl+C 仅退出日志跟踪，不影响容器运行
```

> `invoke xmnn.logs` 默认 `--tail=100` 只看日志**尾部**，而凭证横幅位于启动
> 日志**头部**——长启动日志下横幅会被挤出窗口；`up` 的回读因此固定从头部取
> 300 行。若非要在 logs 里找，可 `podman logs <容器> | head -n 300`。
>
> **日志驱动必须是 podman 可读的 `k8s-file`**（基段已声明，C24）：本机发行版
> 默认 `log_driver = journald`，而 WSL 嵌套 systemd 命名空间下 `podman logs`
> 读 journald 返回**空**（0 字节，日志只在宿主 `journalctl` 里），会同时让
> 凭证回读与 `invoke xmnn.logs` 失效。若发现 `podman logs` 输出为空而容器
> 明明在跑，先确认驱动：`podman inspect <容器> --format
> '{{.HostConfig.LogConfig.Type}}'` 应为 `k8s-file`；旧驱动下启动的容器需
> `invoke xmnn.down && invoke xmnn.up` 重建一次才生效。

已在 `.env` 预设凭证时，直接用预设值登录（日志不再打印随机值横幅）；
此时 `invoke xmnn.up` 横幅同样会打印带 token 的「直达」URL，点开即免登录。
回读只读取容器运行时状态，**不会回写 `.env`**。

> 普通 `down/up` 重建不影响登录态（`xmnn-jupyter` 命名卷持久化，C22）；
> 若执行过 `down --volumes` 或升级到 C22 之前的版本，旧标签页会被踢回登录，
> `Ctrl+Shift+R` 硬刷新后重登即可——这是密钥轮换的预期表现，不是 Terminal/
> 权限故障，判别步骤见 [04 速查 C-I6](04-troubleshooting-guide.md)。

### JupyterLab

1. 浏览器打开 http://localhost:8890，粘贴 token 登录；或直接访问
   `http://localhost:8890/lab?token=<JUPYTER_TOKEN>`。
2. 新建/打开 Notebook 时内核务必选 **Python 3.14 (xmnn dev)**——该内核
   argv 指向 `/opt/conda/bin/python`（cp314 **GIL**），且内核环境已内嵌
   三源码树的 `PYTHONPATH`，tvm/vta/xmnn 从挂载源码导入；其余内核不具备
   这条源码调试链路。
3. 工作根目录即容器内 `/workspace`：源码在 `npu_tvm/`、`npuusertools/`、
   `models/`，wheel 产物在 `dist/`；宿主侧改代码容器内即时生效，无需重建。

### SSH

**步骤 1：确认栈已启动**

```bash
invoke xmnn.ps     # 应见 xmnn 服务 Up，端口行含 0.0.0.0:2223->22/tcp
```

**步骤 2：准备认证凭证（密码 / 公钥二选一）**

方式 A——密码认证（开箱即用）：

- `.env` 的 `USER_PASSWORD` 留空时，容器首启随机生成 16 位密码，从
  `invoke xmnn.logs` 输出中找 `[IMPORTANT] devuser password: <密码>` 横幅；
- 已在 `.env` 预设 `USER_PASSWORD` 则直接用预设值登录（此时不打印随机密码横幅）。

方式 B——公钥免密（推荐长期使用）：

```bash
# 本机还没有密钥对时先生成（已有 ~/.ssh/id_ed25519.pub 可跳过）
ssh-keygen -t ed25519                       # 提示全程回车即可
cat ~/.ssh/id_ed25519.pub                   # Windows: type %USERPROFILE%\.ssh\id_ed25519.pub
```

把 `.pub` 文件的**完整一行**（形如 `ssh-ed25519 AAAAC3... user@host`）填入
client 目录 `.env` 的 `SSH_PUBLIC_KEY=`，然后重建栈使之生效——公钥由
entrypoint 在容器**启动时**写入 `~devuser/.ssh/authorized_keys`（权限 600），
仅 restart 不会重新读取 `.env`：

```bash
invoke xmnn.down && invoke xmnn.up --skip-build
```

**步骤 3：发起连接（首次登录确认主机指纹）**

```bash
ssh -p 2223 devuser@localhost
```

- 首次连接出现 `Are you sure you want to continue connecting (yes/no)?`
  时输入 `yes`，主机指纹写入 `~/.ssh/known_hosts`；密码认证随后输入密码，
  终端中密码无回显属正常现象。
- Windows 10 1809+/11 在 PowerShell 或 Windows Terminal 中执行**同一命令**
  即可（系统自带 OpenSSH 客户端）；若提示找不到 `ssh`，于
  **设置 → 应用 → 可选功能**中添加「OpenSSH 客户端」，或直接在 WSL2
  终端内连接。
- 经 Windows 自动桥接启动时栈在 `podman-machine-default` 内，但端口经
  WSL2 localhost 转发，地址仍是 `localhost:2223`，无需指定 WSL IP。

**步骤 4：验证已进入 xmnn 容器**

```bash
whoami                          # 输出 devuser
ls /workspace                   # 应见 npu_tvm  npuusertools  models  dist
/opt/conda/bin/python -c "import tvm; print(tvm.__file__)"
# 应输出 /workspace/npu_tvm/python/tvm/... —— 证明走的是挂载源码而非 site-packages
```

**登录后的环境要点**

- 登录 shell 默认处于 **main env（cp314t）**；编译/打包/源码调试请显式用
  `/opt/conda/bin/python`（与 Jupyter 的 xmnn dev 内核同源，cp314 GIL），
  打包脚本则直接 `bash /opt/xmnn-builder/scripts/build-wheel.sh`。
- `GRANT_SUDO=yes`（默认）时 devuser 具备免密 sudo（`sudo <命令>`）。

**简化日常连接：ssh config 与 VSCode**

在 `~/.ssh/config` 新增以下段落后即可用 `ssh xmnn-dev` 直连；VSCode
**Remote - SSH** 扩展的远程资源管理器中也会出现该主机，连接后可直接编辑
`/workspace/npu_tvm` 等挂载源码：

```
Host xmnn-dev
    HostName localhost
    Port 2223
    User devuser
```

**常见问题**

| 现象 | 原因与处理 |
|---|---|
| `Connection refused` / 连接被拒 | 栈未运行或端口非默认：先 `invoke xmnn.ps` 核对；`.env` 改过 `XMNN_SSH_PORT` 时，`-p` 与 ssh config 的 `Port` 同步替换 |
| `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!` | 2026-09-20 起已挂载 `xmnn-ssh-host-keys` 持久卷，普通 `down/up` 重建**不再**轮换指纹——出现该告警只剩三种情形：① 主动执行过 `down --volumes` / `podman volume rm`（删卷即轮换，属预期）；② 记录被旧容器（挂载前）写过，与当前卷内指纹本就不同；③ 换了宿主端口（`[localhost]:<port>` 记录按端口分别保存）。处理：核对容器内指纹 `ssh-keygen -lf /var/lib/jpman/ssh-host-keys/ssh_host_ed25519_key` 确认为本栈后，`ssh-keygen -R '[localhost]:2223'`（改过端口则替换端口号）清除旧记录重连 |
| `Permission denied (publickey,password)` | 密码：回 `invoke xmnn.logs` 核对横幅；公钥：确认 `.env` 中是**完整一行**公钥且改后做过 `down && up`；另确认用户名是 `devuser` |
| Windows 找不到 `ssh` 命令 | 安装可选功能「OpenSSH 客户端」，或改用 WSL2 终端执行连接命令 |
| 连上后 `import tvm` / `import xmnn` 报 `ModuleNotFoundError` | 两个独立成因（C30）：① **SSH 会话缺调试环境变量**——sshd 派生的会话不继承容器 config env，`ssh host "cmd"` 又不读任何 shell 启动文件，故 `PYTHONPATH` 为空、挂载树里的 tvm/vta/xmnn 找不到（**不是** site-packages）；镜像内 `setup-ssh-env.sh` 已用 `/etc/profile.d` + sshd `SetEnv` 双通道补齐，老镜像 `invoke xmnn.build && invoke xmnn.up --skip-build` 或按 [04-troubleshooting-guide.md](04-troubleshooting-guide.md) **C-I9** 在会话内一行 `export` 逃生；② 误用 main env 的 python（无 numpy）——调试/打包改用 `/opt/conda/bin/python` 或先 `conda activate base`，也可直接用 Jupyter 的 `Python 3.14 (xmnn dev)` 内核 |

### 端口与平台

- 端口可用 `.env` 的 `XMNN_SSH_PORT` / `XMNN_JUPYTER_PORT` 改写；默认
  2223/8890 与 quant 2222/8888、monetize 2224/8892、xmnnrt 2225/8893
  错开，多栈可并行运行。
- Windows 原生 CPython 经自动桥接启动时，栈运行在 `podman-machine-default`
  内，浏览器与 SSH 客户端仍访问**本机 localhost**（WSL2 localhost 转发）；
  栈本身在 WSL2 发行版内或 Linux/macOS 上启动时同理。

完整说明（双 ABI 布局、打包流程、参数表、排障）：
[overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md)。
对应 AI 硬约束：[.agents/rules/xmnn-overlay.md](../.agents/rules/xmnn-overlay.md)（C12）。