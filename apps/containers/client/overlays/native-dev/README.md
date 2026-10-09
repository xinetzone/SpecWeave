# Native 原生开发与 wheel 打包叠加层（Podman rootless + podman-compose）

> 一句话：在 `localhost/jupyter-podman-rootless:latest` 之上做一层工具链叠加，
> 运行时把 **npu_tvm / npuusertools / models 源码 + 根工作区临时目录 .temp**
> bind 挂载进容器，提供 tvm/vta/xmnn 的源码调试环境（SSH + JupyterLab +
> native-dev 内核），并在容器内用 **LLVM/Clang 22 + Nuitka 4.2.2** 一键打出
> cp314 的 `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`。

- **镜像**：`localhost/native-dev:latest`（薄叠加；含完整编译工具链，体积大于量化栈）
- **双 Python ABI**：base env `/opt/conda/bin/python` = **cp314 GIL enabled**
  （Nuitka 编译/打包/native-dev 内核，3.14.7）；main env = **cp314t**
  （Jupyter 服务不变）；LLVM/Clang 22.1.8 工具链装在 main env
- **服务**：SSH（容器 22 → 宿主 **2223**）+ JupyterLab（**8890**），
  supervisord 托管，沿用基底 entrypoint
- **源码**：运行时挂载，容器内固定路径 `/workspace/npu_tvm`、
  `/workspace/npuusertools`、`/workspace/models`（镜像构建期零接触源码）
- **临时目录**：`NATIVE_TEMP_PATH`（默认根工作区 `.temp`）挂容器内
  `/workspace/temp`，编译/调试临时产物落仓库外 scratch 盘位
- **编排**：podman-compose（rootless、无 privileged）；AI 硬约束见
  [../../.agents/rules/native-overlay.md](../../.agents/rules/native-overlay.md)

## 包含什么

| 能力 | 实现 |
|---|---|
| C/C++ 工具链 | LLVM/Clang/lld 22.1.8、cmake、ninja、make、ccache（main env，conda-forge） |
| 系统工具 | patchelf（wheel RPATH）、gdb（源码调试） |
| Nuitka 打包栈（base env） | nuitka==4.2.2、scikit-build-core、build、wheel、invoke、ipykernel + pyproject 声明的全部 xmnn 运行时依赖 |
| 打包内核 | `/opt/native-builder/`：pyproject.toml、CMakeLists.txt、bootstrap、build-wheel/build-tvm/verify-wheel 脚本（**自包含，不依赖 external/chaos/ai**） |
| Jupyter 内核 | `Python 3.14 (native dev)`（argv=/opt/conda/bin/python，env 内嵌源码 PYTHONPATH） |
| 构建期守卫 | `/opt/native-dev-smoke/_toolchain_guards.py`（双 ABI + 工具链 + LLVM 库 SONAME 实测 + §7 离线完备性） |

## 文档导航

深度内容已按主题原子化到 [docs/](docs/)：

| 文档 | 内容 |
|---|---|
| [01 快速开始](docs/01-quickstart.md) | 前置条件、`invoke native.*` 推荐路径（含凭证与持久化）、裸 podman-compose 路径 |
| [02 开发调试工作流](docs/02-dev-workflow.md) | 源码即时生效、SSH/Jupyter 调试环境、缓存与临时目录、9p 性能提示、冒烟测试 |
| [03 离线交付](docs/03-offline-delivery.md) | 两个过程（有网构建 → 无网开发）、离线开关语义与 `--skip-build` 区别 |
| [04 GPU 与 torch](docs/04-gpu-and-torch.md) | GPU 透传三形态（CDI/DRI/DXG）、torch cpu/cu130 形态、nvcc 13.4.92、归档名形态标记 |
| [05 参数与栈关系](docs/05-params-and-relations.md) | compose 插值 / .env 键全表、与量化/交付等相关栈目录的关系 |
| [06 排障速查](docs/06-troubleshooting.md) | 常见现象与处理（控制平面交替、OOM、离线无镜像、checkpoint 权限等） |
| [07 透传与组合指南](docs/07-passthrough-and-combos.md) | 透传/GPU/torch-gpu/GUI/USB 组合矩阵、全家桶命令、组合排障 |
