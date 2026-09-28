---
id: "native-dev-troubleshooting"
title: "排障速查表"
source: "README.md#排障"
---
# 排障速查表

| 现象 | 处理 |
|---|---|
| `invoke native.*` Windows 原生报门禁 Exit(1) | 自动桥接不可用时回退（无 wsl.exe/发行版缺失/`COMPOSE_WSL_DISTRO=none`）；正常路径自动桥接 `podman-machine-default`，无需手动操作 |
| `up -d` 报 `conmon exited prematurely` + `address already in use`（exit 125，2223/8890），常发生在裸 compose 与 invoke 交替后 | **跨控制平面标签分歧 + 孤儿 rootlessport**（详见 W-I10）；`invoke native.up --skip-build` 的 preflight 三道自动恢复（残留 down / 跨平面优雅 down / 孤儿端口定点 kill）；日常纪律是同一栈固定单一控制平面。仍失败才查宿主占用（`netstat -ano \| findstr 2223`）或改 `.env` 端口 |
| build-tvm 报 dmlc-core 缺失 | 宿主 npu_tvm 树执行 `git submodule update --init` 后重试；**该步需联网**，属过程一预备（源码随归档一起在联网侧备好），无网侧无法补齐 |
| build-tvm 之前报 `variable-sized object may not be initialized`（VTA FSIM 的 VLA） | 已由 2026-09-15 引入系统 gcc/g++ 作编译前端修复（Clang 22 拒 VLA+初始化器、GCC 允许）；env `CC`/`CXX` 可覆盖回退 clang |
| build-wheel 开头报 libtvm.so 缺失（exit 2） | 先 `invoke native.build-tvm`，或把含 build/ 的完整 npu_tvm 挂到 NPU_TVM_PATH |
| Nuitka Killed / OOM | `invoke native.wheel --jobs 4`，machine 分配 ≥8 GB 内存 |
| wheel CMake FATAL：LLVM dependency glob 空 | 守卫会打印 libdir 实际 SONAME；按提示核对 CMakeLists 7 个 glob（conda 库版本漂移） |
| up 后 aardvark-dns / user scope bus 报错 | 已用 `network_mode: bridge` 规避；若复现检查该行未被删除 |
| 裸 compose 后 `client/workspace/` 出现 npu_tvm/npuusertools/models 空目录 | podman-compose 1.6 对相对 source + create_host_path 的 host 端预创建副产物，**真实挂载不受影响**（冒烟以 `/workspace/...` 路径前缀断言）；down 后 `rmdir` 即可。用 `invoke native.up`（注入绝对路径）不会产生 |
| Jupyter 保存 notebook 报 `[Errno 13] Permission denied: '/workspace/.ipynb_checkpoints/...'` | rootless + 9p/drvfs 下容器内 root 预建的 checkpoint 目录在容器视角为 0:0 755，而 Jupyter 以 devuser(1000) 运行无 w 位。`invoke native.up`/`native.build` 经编排层 `ensure_workspace_checkpoint_writable` 幂等 `chmod 777` 该**单一目录**（不改属主、不递归、不碰源码树）；手工救急：宿主侧 `chmod 777 apps/containers/client/workspace/.ipynb_checkpoints` |
| 打包后外部源码出现 `.bak_tvm/.bak_vta/.bak_xmnn` 或 `__init__.py` 被改写 | 2026-09-21 起 `build-wheel.sh` **全程只读源码树**：不再向 `__init__.py` 注入/还原 AST 兼容层，ast 遗留节点改由运行期补丁提供（`_xmnn_bootstrap.py` 的 `.pth` 启动钩子 + `xmnn/vta_compat.apply_ast_compat()`），故不会再产生 `.bak_*`，也不存在「注入态残留」。若仍见到残留，说明跑的是旧镜像产物：`git checkout -- <file>` 还原并 `rm .bak_*`，再 `invoke native.build && invoke native.down && invoke native.up --skip-build` 重建镜像 |
| Terminal/SSH/notebook `import tvm` 报 `ImportError: cannot import name 'NameConstant' from 'ast'` | CPython 3.12+ 移除 ast 遗留节点，tvm 源码树 `py_converter.py` 在**导入期**引用它们，任何运行期补丁都晚于导入。2026-09-28 起 Layer 5 `install-ast-bootstrap.sh` 已把 `_xmnn_bootstrap.py` + `xmnn_bootstrap.pth` 烤入 base/main 两解释器（守卫 §11 双端断言）。旧镜像救急：`podman exec -u root native-dev bash -c 'for sp in /opt/conda/lib/python3.14/site-packages /opt/conda/envs/main/lib/python3.14t/site-packages; do cp /opt/native-builder/_xmnn_bootstrap.py $sp/; printf "import _xmnn_bootstrap\n" > $sp/xmnn_bootstrap.pth; done'`；根治：`invoke native.build && invoke native.down && invoke native.up --skip-build` 重建镜像 |
| conda 求解慢/失败 | `--conda-mirror tuna`（或 aliyun）；pip 侧 `--pip-mirror tuna` |
| 容器内 `import tkinter` 报 `ImportError: libtk8.6.so: cannot open shared object file` | 基底深度清理**删了 tk/tcl 文件但保留 conda-meta 记录**（腐坏态：常规 `mamba install tk` 被判「已安装」空转）；**native-dev 镜像已由 Layer 4.5 恢复**（Tk 8.6 + libX11），重建镜像后即可用。其它镜像（基底/onnx/monetize）遇到时按 `scripts/install-gui-libs.sh` 同法处理：先 `rm /opt/conda/conda-meta/tk-*.json`，再 `mamba install "tk=8.6.13" xorg-libx11`——**必须精确版本**（latest 为 tk 9.0，soname 不匹配会继续报错）；弹窗还需 `--gui`（socket 透传） |
| 离线 `up --offline` 报本地无镜像（Exit 1） | 无网侧确实没有镜像。到**有网侧**先 `invoke native.save`，把 `.image-cache/` 里的归档（tar.gz + manifest）拷过来，再 `invoke native.load --path <归档.tar.gz>`。归档自带 SHA256，拷贝损坏会在 load 步暴露而不是启动后诡异失败 |
| 离线 `native.wheel` 报 numpy/scipy 缺失或缺 gcc（exit 2） | 离线**不允许** pip 兜底。需回有网侧把依赖补进镜像（基底 env 或 `PIP_MIRROR` 构建期安装）后重新 `native.save`；不要在无网侧改镜像或手工 pip（无网必失败） |
| 离线 `up` 仍尝试构建镜像 | 检查开关是否真的生效：`--offline` 必须写在 `up` 之后（`invoke native.up --offline`），或 `.env` 里 `NATIVE_OFFLINE=1`；若同时写了 `--no-offline` 会覆盖 `.env` 的开启项 |
