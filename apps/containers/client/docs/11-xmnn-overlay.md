---
id: "jupyter-podman-client-xmnn-overlay"
title: "工作负载叠加层：xmnn-dev（xmnn.*）"
source: "README.md#13-工作负载叠加层xmnn-devxmnn-命令opt-in"
---
# 工作负载叠加层：xmnn-dev（xmnn.* 命令，opt-in）

第二个声明式工作负载栈：XMNN **源码调试 + wheel 打包**开发环境。容器内具备
LLVM/Clang 22.1.8 + CMake/Ninja/ccache + Nuitka 4.1.3 工具链；运行时把
`npu_tvm`、`npuusertools`、`models` 三个宿主源码目录 bind 挂载进容器，
SSH/Jupyter（`Python 3.14 (xmnn dev)` 内核，cp314 GIL）即可直接调试挂载源码，
并能一键编译 TVM、用 Nuitka 打出 `xmnn-*.whl`（产物落 workspace/dist）。

```bash
pip install -e ".[compose]"           # 与 quant.* 同一个可选依赖
invoke xmnn.build --pip-mirror tuna --conda-mirror tuna
invoke xmnn.up                        # 启动栈：SSH 2223 / Jupyter 8890
invoke xmnn.smoke                     # 工具链守卫 + 源码挂载检查
invoke xmnn.build-tvm                 # 可选：栈内编译 build/libtvm.so（已存在则跳过）
invoke xmnn.wheel                     # Nuitka 全流程打包，wheel 落 workspace/dist
invoke xmnn.down                       # 停止清理（ccache 卷默认保留）
```

- **端口默认 2223/8890**：与 quant 栈错开，两个栈可并行运行。
- **源码路径**：默认挂载仓库根 `external/chaos/{npu_tvm,npuusertools,models}`；
  可在 `.env` 用 `NPU_TVM_PATH` / `NPUUSERTOOLS_PATH` / `MODELS_PATH`
  覆盖（invoke 路径做存在性硬校验）。TVM 全量编译在 9p 上较慢，可把路径
  指向 WSL 原生克隆。
- **Windows 原生自动桥接**：同 quant.*（默认桥接 `podman-machine-default`；
  `COMPOSE_WSL_DISTRO` 可指其他发行版，`none` 关闭并回退门禁）。
- **对 external/chaos/ai 零依赖**：打包脚本与元数据自包含于叠加层；
  外部源码树只读挂载，打包中的临时 AST 注入会无条件还原。

完整说明（双 ABI 布局、打包流程、参数表、排障）：
[overlays/xmnn-dev/README.md](../overlays/xmnn-dev/README.md)。
对应 AI 硬约束：[.agents/rules/xmnn-overlay.md](../.agents/rules/xmnn-overlay.md)（C12）。