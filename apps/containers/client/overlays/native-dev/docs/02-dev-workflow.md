---
id: "native-dev-dev-workflow"
title: "开发调试工作流、性能提示与冒烟测试"
source: "README.md#开发调试工作流"
---
# 开发调试工作流、性能提示与冒烟测试

## 开发调试工作流

- **改代码即时生效**：tvm/vta/xmnn 经 `PYTHONPATH` 从 `/workspace` 挂载树
  导入（不是 site-packages），宿主侧改代码容器内立即生效；Jupyter 用
  `Python 3.14 (native dev)` 内核。
- **SSH 会话同样带调试环境**（C30）：`PYTHONPATH` / `TVM_LIBRARY_PATH` /
  `LD_LIBRARY_PATH` / `NPU_TOOLS_ROOT` / `XMNN_TOOLS_ROOT` 由 compose
  `environment` 注入容器与 Jupyter 内核，SSH 会话则另由镜像内
  `/etc/profile.d/50-native-dev-env.sh` + `sshd_config` 的 `SetEnv` 双通道补齐
  （sshd 不继承容器 config env；`ssh host "cmd"` 又不读任何 shell 启动文件），
  因此 `ssh -p 2223 devuser@localhost` 进去即可直接 `import tvm, xmnn`。
- **注意解释器**：SSH 默认落在 **main env**（cp314t，未装 numpy），
  调试/打包请显式用 `/opt/conda/bin/python`，或先 `conda activate base`
  （base = cp314 GIL，带 numpy/tvm/xmnn）。报 `No module named 'xmnn'`
  或 `'numpy'` 都是选错解释器所致，见
  [docs/04 排障速查 C-I9](../../../docs/04-troubleshooting-guide.md)。
- **TVM 库加载**：`TVM_LIBRARY_PATH=/workspace/npu_tvm/build` 与
  `LD_LIBRARY_PATH`（build、build/vta、main/lib）由 compose 注入，
  libtvm.so 及其 LLVM 依赖无需手工配置。
- **wheel 产物**：`/workspace/dist/`（即默认 `apps/containers/client/workspace/dist/`，
  宿主可见；该目录被 client `.gitignore` 忽略）。
- **编译缓存**：Nuitka C 编译缓存在命名卷 `native-ccache`（/root/.ccache），
  重复打包自动命中；`--clean` 仅当次禁用 ccache，不清缓存。
- **登录态缓存**：Jupyter cookie/notebook 密钥在命名卷 `native-jupyter`
  （/home/devuser/.local/share/jupyter），普通 down/up 重建免重登；
  仅 `down --volumes` 清除。
- **SSH 指纹缓存**：主机密钥在命名卷 `native-ssh-host-keys`
  （/var/lib/jpman/ssh-host-keys），普通 down/up 重建指纹不变；
  仅 `down --volumes` 清除。
- **临时目录**：`/workspace/temp` 由 `NATIVE_TEMP_PATH` 绑定到宿主根工作区
  `.temp`（默认按本仓布局推导：invoke 取仓库根上溯四级、裸 compose 九级，
  本工作区均为 `/media/pc/data/ai/.temp`）；该目录缺失不报错，invoke 侧
  幂等 mkdir。⚠️ 它**覆盖 `/workspace` 下的同名子目录**——容器内
  `/workspace/temp` 从此不再是宿主 `client/workspace/temp`（宿主侧文件不受
  影响，仅容器内不可见）；换检出位置请显式设 `NATIVE_TEMP_PATH` 绝对路径。

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
机器内存不足用 `invoke native.wheel --jobs 4`。

## 冒烟测试

| 脚本 | 何时跑 | 内容 |
|---|---|---|
| `smoke/_toolchain_guards.py` | 镜像构建期（root+devuser）/ `native.smoke` / `podman run --rm` | 双 ABI（base GIL on、main cp314t）、LLVM 22.1/clang/cmake/ninja/ccache/patchelf/gdb、nuitka 4.2.2 且运行解释器在 `getSupportedPythonVersions()` 内、builder 资产、7 个 LLVM 依赖库 SONAME 实测、**§7 离线完备性**（编译/打包前端可解析 + pyproject 声明的 19 依赖全部已装，守卫自身不联网） |
| `smoke/smoke_mounts.py` | 栈运行时（`native.smoke`/compose exec） | 三挂载点可见；libtvm 存在时 import tvm/vta/xmnn 来自 /workspace + tvm.build('llvm') 向量加；缺席时跳过并 exit 0 |
