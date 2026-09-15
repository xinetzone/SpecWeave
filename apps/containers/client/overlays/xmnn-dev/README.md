# XMNN 开发与 wheel 打包叠加层（Podman rootless + podman-compose）

> 一句话：在 `localhost/jupyter-podman-rootless:latest` 之上做一层工具链叠加，
> 运行时把 **npu_tvm / npuusertools / models 源码 bind 挂载进容器**，提供
> tvm/vta/xmnn 的源码调试环境（SSH + JupyterLab + xmnn-dev 内核），并在
> 容器内用 **LLVM/Clang 22 + Nuitka 4.1.3** 一键打出 cp314 的
> `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`。

- **镜像**：`localhost/xmnn-dev:latest`（薄叠加；含完整编译工具链，体积大于量化栈）
- **双 Python ABI**：base env `/opt/conda/bin/python` = **cp314 GIL enabled**
  （Nuitka 编译/打包/xmnn-dev 内核，3.14.7）；main env = **cp314t**
  （Jupyter 服务不变）；LLVM/Clang 22.1.8 工具链装在 main env
- **服务**：SSH（容器 22 → 宿主 **2223**）+ JupyterLab（**8890**），
  supervisord 托管，沿用基底 entrypoint
- **源码**：运行时挂载，容器内固定路径 `/workspace/npu_tvm`、
  `/workspace/npuusertools`、`/workspace/models`（镜像构建期零接触源码）
- **编排**：podman-compose（rootless、无 privileged）；AI 硬约束见
  [../../.agents/rules/xmnn-overlay.md](../../.agents/rules/xmnn-overlay.md)

## 包含什么

| 能力 | 实现 |
|---|---|
| C/C++ 工具链 | LLVM/Clang/lld 22.1.8、cmake、ninja、make、ccache（main env，conda-forge） |
| 系统工具 | patchelf（wheel RPATH）、gdb（源码调试） |
| Nuitka 打包栈（base env） | nuitka==4.1.3、scikit-build-core、build、wheel、invoke、ipykernel + 19 个 xmnn 运行时依赖 |
| 打包内核 | `/opt/xmnn-builder/`：pyproject.toml、CMakeLists.txt、bootstrap、build-wheel/build-tvm/verify-wheel 脚本（**自包含，不依赖 external/chaos/ai**） |
| Jupyter 内核 | `Python 3.14 (xmnn dev)`（argv=/opt/conda/bin/python，env 内嵌源码 PYTHONPATH） |
| 构建期守卫 | `/opt/xmnn-dev-smoke/_toolchain_guards.py`（双 ABI + 工具链 + LLVM 库 SONAME 实测） |

## 前置条件

1. podman machine（Windows 即 WSL2 后端）已运行；
2. 本地已有基底镜像，没有则先在 `apps/containers/client` 加载：
   ```bash
   invoke load        # localhost/jupyter-podman-rootless:latest
   ```
3. 宿主存在源码目录（默认仓库根 `external/chaos/`）：
   - `external/chaos/npu_tvm`（TVM 0.19.0 fork；若 `build/libtvm.so`
     已存在可直接打包，否则先 build-tvm——全量编译需先
     `git submodule update --init` 检出 dmlc-core 等子模块）
   - `external/chaos/npuusertools`（xmnn 包 + tools_cpp/autolibs/fonts 数据）
   - `external/chaos/models`（模型目录）
4. **Windows 原生自动桥接**：与 quant.* 相同，Windows 原生 CPython 执行时
   自动桥接到 WSL 发行版（默认 `podman-machine-default`——client 专用
   rootless 发行版，与 flapping 的 Podman Desktop 默认 machine 相互独立、
   镜像存储不互通；`COMPOSE_WSL_DISTRO` 可指定、`none` 关闭回退门禁）。也可手动二选一：
   - WSL2 发行版内（推荐）：
     ```bash
     wsl -d <发行版>
     cd /mnt/d/spaces/SpecWeave/apps/containers/client
     pip install -e ".[compose]"
     ```
   - 或 client 自举容器：`invoke env.run-cmd --cmd 'inv xmnn.up'`

## 路径一：invoke xmnn.*（推荐）

在 `apps/containers/client` 下（WSL2/Linux/macOS）：

```bash
invoke xmnn.build                         # 构建工具链镜像（构建期自动跑双 ABI/SONAME 守卫）
                                         #   --pip-mirror/--conda-mirror tuna|aliyun 可加速
invoke xmnn.up                           # 启动栈（默认随带构建；--skip-build 跳过）
invoke xmnn.ps                           # 服务状态
invoke xmnn.smoke                        # 工具链守卫 + 源码挂载检查（libtvm 缺席时跳过算例段）

invoke xmnn.build-tvm                    # 【可选】栈内编译 TVM（build/libtvm.so 已存在则无需）
invoke xmnn.wheel                        # Nuitka 打包 xmnn whl（tvm 串行→vta/xmnn 并行）
                                         #   --jobs 4 内存紧张时；--clean 禁 ccache 全量重编；
                                         #   --tvm-flags "..." 透传额外 Nuitka 参数
podman-compose -p xmnn-dev exec xmnn \
    bash /opt/xmnn-builder/scripts/verify-wheel.sh   # 10 项隔离验证（临时 venv，不污染源码环境）

invoke xmnn.logs                         # 跟踪日志（Ctrl+C 退出）
invoke xmnn.down                         # 停止清理（workspace/源码保留；ccache 卷保留）
invoke xmnn.down --volumes               # 连 xmnn-ccache 命名卷一起删除
```

启动后访问（凭证可由环境变量覆盖，见 `.env.example`）：

| 服务 | 地址 | 凭证 / 入口 |
|---|---|---|
| JupyterLab | http://localhost:8890 | `JUPYTER_TOKEN`（留空则自动生成）；内核选 **Python 3.14 (xmnn dev)** |
| SSH | `ssh -p 2223 devuser@localhost` | `USER_PASSWORD`（留空自动生成） |

## 路径二：裸 podman-compose

在本目录（`overlays/xmnn-dev/`）下，无需 invoke：

```bash
cp .env.example .env           # 按需修改源码路径/端口/凭证/镜像源
podman-compose up -d           # 首次自动构建
podman-compose exec xmnn bash /opt/xmnn-builder/scripts/build-tvm.sh    # 可选
podman-compose exec xmnn bash /opt/xmnn-builder/scripts/build-wheel.sh
podman-compose down
```

`compose.yaml` 已内置 rootless 三必需（`/dev/fuse`、`label=disable`、
`cgroupns: host`），四个 bind 全部长语法，**无特权容器**；
`network_mode: bridge` 是 2026-09-14 同机实证（machine 无 systemd user bus
时默认项目网络 aardvark-dns 失败），见 compose 文件头注释。

> ⚠️ **控制平面纪律（2026-09-15 实证）**：选定裸 compose 就长期在本目录用
> 裸 compose，**不要与 `invoke xmnn.*`（WSL 桥接，下发 `/mnt/d/...`）交替
> 操作同一栈**——两者给容器打的 `config_files` 标签原文不同（`D:\...` vs
> `/mnt/d/...`），交替执行会被 podman-compose 强制 recreate，并可能留下孤儿
> rootlessport 导致 `up -d` 报 2223/8890 `address already in use`。已经
> 交替翻车时直接 `invoke xmnn.up --skip-build`，编排层 preflight 三道自愈
> （残留 down / 跨平面优雅 down / 孤儿端口定点回收）自动恢复，详见
> [30 秒修复速查表 W-I10](../../docs/04-troubleshooting-guide.md)。

## 开发调试工作流

- **改代码即时生效**：tvm/vta/xmnn 经 `PYTHONPATH` 从 `/workspace` 挂载树
  导入（不是 site-packages），宿主侧改代码容器内立即生效；Jupyter 用
  `Python 3.14 (xmnn dev)` 内核，SSH 进去默认 main env，调试/打包请用
  `/opt/conda/bin/python`（或内核）。
- **TVM 库加载**：`TVM_LIBRARY_PATH=/workspace/npu_tvm/build` 与
  `LD_LIBRARY_PATH`（build、build/vta、main/lib）由 compose 注入，
  libtvm.so 及其 LLVM 依赖无需手工配置。
- **wheel 产物**：`/workspace/dist/`（即默认 `apps/containers/client/workspace/dist/`，
  宿主可见；该目录被 client `.gitignore` 忽略）。
- **编译缓存**：Nuitka C 编译缓存在命名卷 `xmnn-ccache`（/root/.ccache），
  重复打包自动命中；`--clean` 仅当次禁用 ccache，不清缓存。

## 性能提示（9p）

npu_tvm 全量 C++ 编译在 Windows 挂载盘（/mnt/d，9p）上较慢。需要频繁重编
TVM 时，推荐把源码克隆到 WSL 原生文件系统并用变量改挂载：

```bash
# WSL 内
git clone <npu_tvm 仓库> ~/build/npu_tvm && cd ~/build/npu_tvm
git submodule update --init
# client/.env
NPU_TVM_PATH=/root/build/npu_tvm
```

Nuitka 打包内存占用随 `--jobs` 近似线性（jobs=8 约 15GB 峰值）；
机器内存不足用 `invoke xmnn.wheel --jobs 4`。

## 冒烟测试

| 脚本 | 何时跑 | 内容 |
|---|---|---|
| `smoke/_toolchain_guards.py` | 镜像构建期（root+devuser）/ `xmnn.smoke` / `podman run --rm` | 双 ABI（base GIL on、main cp314t）、LLVM 22.1/clang/cmake/ninja/ccache/patchelf/gdb、nuitka 4.1.3、builder 资产、7 个 LLVM 依赖库 SONAME 实测 |
| `smoke/smoke_mounts.py` | 栈运行时（`xmnn.smoke`/compose exec） | 三挂载点可见；libtvm 存在时 import tvm/vta/xmnn 来自 /workspace + tvm.build('llvm') 向量加；缺席时跳过并 exit 0 |

## 参数表（compose 插值 / .env 键）

| 键 | 默认值 | 用途 |
|---|---|---|
| `XMNN_IMAGE_TAG` | `localhost/xmnn-dev:latest` | 镜像标签 |
| `XMNN_CONTAINER_NAME` | `xmnn-dev` | 容器名（project name 固定 xmnn-dev） |
| `XMNN_SSH_PORT` / `XMNN_JUPYTER_PORT` | `2223` / `8890` | 宿主端口（与 onnx 2222/8888 错开） |
| `XMNN_WORKSPACE` | `../../workspace` | 通用工作区 → /workspace（wheel 产物在其 dist/） |
| `NPU_TVM_PATH` | `../../../../../external/chaos/npu_tvm` | TVM 源码宿主路径 |
| `NPUUSERTOOLS_PATH` | `../../../../../external/chaos/npuusertools` | xmnn 源码宿主路径 |
| `MODELS_PATH` | `../../../../../external/chaos/models` | 模型目录宿主路径 |
| `USER_PASSWORD` / `JUPYTER_TOKEN` | 空（自动生成） | 登录凭证 |
| `SSH_PUBLIC_KEY` / `GRANT_SUDO` | 空 / `yes` | SSH 公钥 / devuser sudo |
| `OMP_NUM_THREADS` / `NUITKA_JOBS` | `4` / `8` | 线程与 Nuitka 并发 |
| `PIP_MIRROR` / `CONDA_MIRROR` | `official` | 构建期镜像源（official/aliyun/tuna）。`.env` 值在 `xmnn.up` 的 compose 内联 build 时插值生效；独立 `invoke xmnn.build` 只认 `--pip-mirror/--conda-mirror` 参数 |
| `BASE_IMAGE`（仅 build args） | `localhost/jupyter-podman-rootless:latest` | 基底镜像覆盖 |

## 与相关栈/目录的关系

| 维度 | 本叠加层（xmnn-dev） | onnx-quantized 叠加层 | scratch xmnn-notebook 栈（.temp，不入库） | external/chaos/ai（Docker 谱系） |
|---|---|---|---|---|
| 定位 | **源码开发 + wheel 打包** | ONNX 量化分析 | wheel 消费型 Notebook | 旧一体化参考工程 |
| 源码 | 运行时 bind 挂载（可调试、零修改） | 不挂载 | 不挂载 | BuildKit rw bind + chaos 根构建上下文 |
| 工具链 | 镜像内 LLVM 22 + Nuitka 4.1.3 | ONNX 五包 | 仅 wheel 运行依赖 | Docker 多阶段 + DinD，privileged |
| 对 ai 依赖 | **无（打包内核自包含，仅事实参考）** | 无 | 依赖预构建镜像标签 | — |
| 驱动 | `invoke xmnn.*` / 裸 compose | `invoke quant.*` / 裸 compose | 裸 compose（scratch） | docker compose + 自建 build.sh |

## 排障

| 现象 | 处理 |
|---|---|
| `invoke xmnn.*` Windows 原生报门禁 Exit(1) | 自动桥接不可用时回退（无 wsl.exe/发行版缺失/`COMPOSE_WSL_DISTRO=none`）；正常路径自动桥接 `podman-machine-default`，无需手动操作 |
| `up -d` 报 `conmon exited prematurely` + `address already in use`（exit 125，2223/8890），常发生在裸 compose 与 invoke 交替后 | **跨控制平面标签分歧 + 孤儿 rootlessport**（详见 W-I10）；`invoke xmnn.up --skip-build` 的 preflight 三道自动恢复（残留 down / 跨平面优雅 down / 孤儿端口定点 kill）；日常纪律是同一栈固定单一控制平面。仍失败才查宿主占用（`netstat -ano \| findstr 2223`）或改 `.env` 端口 |
| build-tvm 报 dmlc-core 缺失 | 宿主 npu_tvm 树执行 `git submodule update --init` 后重试 |
| build-tvm 之前报 `variable-sized object may not be initialized`（VTA FSIM 的 VLA） | 已由 2026-09-15 引入系统 gcc/g++ 作编译前端修复（Clang 22 拒 VLA+初始化器、GCC 允许）；env `CC`/`CXX` 可覆盖回退 clang |
| build-wheel 开头报 libtvm.so 缺失（exit 2） | 先 `invoke xmnn.build-tvm`，或把含 build/ 的完整 npu_tvm 挂到 NPU_TVM_PATH |
| Nuitka Killed / OOM | `invoke xmnn.wheel --jobs 4`，machine 分配 ≥8 GB 内存 |
| wheel CMake FATAL：LLVM dependency glob 空 | 守卫会打印 libdir 实际 SONAME；按提示核对 CMakeLists 7 个 glob（conda 库版本漂移） |
| up 后 aardvark-dns / user scope bus 报错 | 已用 `network_mode: bridge` 规避；若复现检查该行未被删除 |
| 裸 compose 后 `client/workspace/` 出现 npu_tvm/npuusertools/models 空目录 | podman-compose 1.6 对相对 source + create_host_path 的 host 端预创建副产物，**真实挂载不受影响**（冒烟以 `/workspace/...` 路径前缀断言）；down 后 `rmdir` 即可。用 `invoke xmnn.up`（注入绝对路径）不会产生 |
| Jupyter 保存 notebook 报 `[Errno 13] Permission denied: '/workspace/.ipynb_checkpoints/...'` | rootless + 9p/drvfs 下容器内 root 预建的 checkpoint 目录在容器视角为 0:0 755，而 Jupyter 以 devuser(1000) 运行无 w 位。`invoke xmnn.up`/`xmnn.build` 经编排层 `ensure_workspace_checkpoint_writable` 幂等 `chmod 777` 该**单一目录**（不改属主、不递归、不碰源码树）；手工救急：宿主侧 `chmod 777 apps/containers/client/workspace/.ipynb_checkpoints` |
| 打包后外部源码出现 `.bak_tvm/.bak_vta/.bak_xmnn` | 直接重跑 `build-wheel.sh` 即可：注入器有四态自愈（残留注入态/截断态配干净 `.bak` 会自动还原）；仅当报「已含 PREAMBLE 但备份缺失」（Exit 2）时才需按提示 `git checkout -- <file>` 人工还原 |
| conda 求解慢/失败 | `--conda-mirror tuna`（或 aliyun）；pip 侧 `--pip-mirror tuna` |
