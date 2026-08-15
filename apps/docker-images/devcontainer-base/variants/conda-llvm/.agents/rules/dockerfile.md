# Conda-LLVM 变体 Dockerfile 规范

## 基础信息

- **基础镜像**：`devcontainer-base:${BASE_TAG}`（直接基于基础镜像，默认为 `devcontainer-base:latest`；conda 中间变体已下线）
- **Dockerfile 语法版本**：`# syntax=docker/dockerfile:1.7-labs`
- **Conda 发行版**：Miniforge3（conda-forge 官方，libmamba solver），路径 `/opt/conda`（继承自基础镜像）
- **默认环境**：conda **main 环境**（`/opt/conda/envs/main`，Python 3.14.6 cp314t free-threading，GIL 默认禁用）
- **LLVM 版本**：固定为 `${LLVM_VERSION}`（默认 `22.1.8`）
- **SHELL 指令**：`["/bin/bash", "-e", "-o", "pipefail", "-c"]`（显式声明，不依赖继承）
- **安装方式**：在 conda **main 环境**（默认用户环境）安装，与默认 Python/Jupyter 共享环境
- **频道**：**conda-forge** 优先（`--override-channels -c conda-forge`），`.condarc` 设置 `channel_priority: strict`

## 核心约束

### 1. PATH 优先级（关键设计决策）

- **必须设置**：`ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}`
- `/opt/conda/envs/main/bin` 在 PATH **最前面**，确保 llvm-config/clang/cmake/ninja 与 Python 3.14t/Jupyter 直接可用
- 工具链与默认用户环境一致——LLVM 工具和默认 python 位于同一环境
- **Jupyter 服务不受影响**：supervisord 使用 main 环境 **绝对路径**（`/opt/conda/envs/main/bin/jupyter`）启动，不依赖 PATH

### 2. 版本一致性与 free-threading 防线（强制执行）

以下 LLVM 相关包**必须统一锁定到 `${LLVM_VERSION}`**：
- `llvmdev=${LLVM_VERSION}`
- `clangdev=${LLVM_VERSION}`
- `clang=${LLVM_VERSION}`
- `lld=${LLVM_VERSION}`
- `python=*=*cp314t`（**显式锁定 free-threading 构建**，回归防线）

以下构建工具安装最新版本（不锁定版本）：
- `cmake`
- `ninja`
- `make`

以下 GCC 运行时库**必须安装**（conda-forge clang 链接器 `x86_64-conda-linux-gnu-ld` 需要 `-lgcc`/`-lstdc++`，缺失会导致用户编译报 `cannot find -lgcc`）：
- `libgcc`
- `libstdcxx-ng`

**lldb 必须排除**：其 python 绑定在 conda-forge 无 cp314t（free-threading）构建，安装会使求解器静默将 python 从 `cp314t` 切换为 `cp314 + python-gil`（GIL 回归）。python 锁定 `*=*cp314t` 后，此类包会使求解直接失败而非静默降级。

安装后必须执行 **free-threading 完整性检查（GUARD）**：
1. `conda list python` 的 build string 必须含 `cp314t`，否则 `exit 1`
2. `python -c "import sys; print(sys._is_gil_enabled())"` 必须返回 `False`，否则 `exit 1`

### 3. 分组安装（conda_install_group 辅助函数）

Stage 2 使用 `conda_install_group` 辅助函数按组安装（结构化日志 + 计时 + 失败诊断）：

| 分组 | 包 | 说明 |
|------|-----|------|
| G1: LLVM Core | llvmdev/clangdev/clang/lld（锁定版本）+ python=`*=*cp314t` | 工具链 + free-threading 防线 |
| G2: Build Tools | cmake/ninja/make | 构建系统工具（latest） |
| G3: GCC Runtime | libgcc/libstdcxx-ng | clang 链接器必需 |

每组使用 `conda install -y --override-channels -c conda-forge <pkgs>`，失败时输出冲突诊断（`conda list` 过滤）并以原退出码终止。

### 4. 继承基础镜像设置（禁止覆盖）

以下指令由基础镜像设置，**不得在 conda-llvm Dockerfile 中重新定义**：

- `ENTRYPOINT`（保持基础镜像入口）
- `CMD`
- `USER`（构建过程用 root，最终用户由基础镜像决定）
- `WORKDIR`
- `HEALTHCHECK`（保持基础镜像的健康检查）
- `EXPOSE`、`VOLUME`（保持基础镜像声明）
- conda 基础配置（conda-init.sh 等已由基础镜像配置完成）

### 5. 激活脚本

- **主要方式**：通过 `ENV PATH=/opt/conda/envs/main/bin:$PATH` 直接生效，无需手动 source
- **备选脚本**：`/etc/profile.d/conda-llvm-init.sh`
  - 权限：`chmod +x`
  - 功能：source conda.sh，`conda activate main`（容错回退 base）
  - 用途：向后兼容、登录 shell 场景
- **基础镜像 conda-init.sh 保留**：`/etc/profile.d/conda-init.sh` 激活 main 环境（基础镜像默认行为）

### 6. BuildKit 缓存挂载（必须）

安装 LLVM 工具链的 Stage 2/4 **必须**使用 BuildKit cache 挂载加速：
```dockerfile
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    ...
```

### 7. 清理规范（静态库豁免）

激进清理时**必须豁免** GCC 运行时静态库（链接器需要）：
```bash
find ... -name "*.a" ! -name "libgcc*" ! -name "libstdc++*" -delete
```
其余清理：strip 二进制、删除 `__pycache__`/`.pyc`、`conda clean -yafq`。

## 追加层 4 阶段结构

Conda-LLVM 变体在基础镜像之上追加 **4 个阶段**（计时器标记 LLVS1-LLVS4）：

### Stage 1/4：PATH 验证 + 计时器初始化

- 验证基础 conda 安装存在（`/opt/conda/bin/conda --version`）
- 验证 main 环境存在及其 python 版本（期望 3.14t）
- 验证 PATH 以 `/opt/conda/envs/main/bin` 开头（ENV 设置已生效）
- 验证基础镜像关键组件存在（devuser、/opt/conda、/opt/conda/envs/main）
- 初始化追加层计时器：`/tmp/.llvm-variant-build-timer`
- 输出 `[TIMER] Stage 1/4 ...`

### Stage 2/4：LLVM 工具链安装（main 环境）+ 激进清理

- **必须**使用 `--mount=type=cache,target=/opt/conda/pkgs,sharing=locked`
- 执行流程：
  1. `source /opt/conda/etc/profile.d/conda.sh`
  2. `conda activate main`
  3. 按 `CONDA_MIRROR`（bfsu/tuna/aliyun/official）重写 `/opt/conda/.condarc`（custom_channels + `default_channels_alias` + strict priority + libmamba solver + 并发参数）
  4. `conda_install_group` 分三组安装（G1/G2/G3，见"分组安装"）
  5. free-threading 完整性检查（GUARD，cp314t + GIL 禁用断言）
  6. 输出已安装工具链版本（含 `lldb: EXCLUDED` 说明行）
  7. 激进清理（strip、删 .a（libgcc/libstdc++ 豁免）、删 pycache、conda clean）
- 输出 `[TIMER] Stage 2/4 ...`

### Stage 3/4：符号链接 + conda-llvm-init.sh + 权限验证

- 检查 llvm-config 是否在 PATH 中，如不在则搜索 `/opt/conda/envs/main/bin`、`/opt/conda/bin` 下的 `llvm-config*` 并创建符号链接
- 创建 `/etc/profile.d/conda-llvm-init.sh`：
  - source `/opt/conda/etc/profile.d/conda.sh`
  - 尝试 `conda activate main`（容错回退 base）
- 设置 `/opt/conda` 权限：
  - `chown -R root:root /opt/conda`
  - `chmod -R a+rX /opt/conda`
  - 确保 bin 目录下可执行文件有执行权限
- 快速可用性检查：llvm-config, clang, cmake, ninja, make 均可执行
- 恢复 devuser 对 `.bashrc` 的所有权
- 输出 `[TIMER] Stage 3/4 ...`

### Stage 4/4：构建元数据 + 清理 + 最终验证 + 汇总表

- `set +o pipefail`（`jupyter --version | head` 会触发 SIGPIPE/退出码 120，属良性，必须豁免）
- 写入构建信息：`/etc/devcontainer-variant-conda-llvm-build-info`
  - 关键字段：`INSTALL_ENV=main (default user env)`、`PATH_PRIORITY=conda-main-bin-first`、`PYTHON_BUILD`（free-threading 断言）、`PACKAGES_INSTALLED`（含 libgcc/libstdcxx-ng，无 lldb）、`PACKAGES_EXCLUDED=lldb(...)`、`ACTIVATION_SCRIPT=/etc/profile.d/conda-init.sh (main env)` 等
- 清理：
  - `conda clean`（Stage 2 已执行）+ `pip cache purge`
  - `apt-get clean`
  - 删除 `/tmp/*`、`/var/tmp/*`、`/var/lib/apt/lists/*`
- **[VALIDATION CHECKPOINT]** 9 项验证：
  1. `bash -n /etc/profile.d/conda-llvm-init.sh`（脚本语法）
  2. `llvm-config` 可执行 + 版本输出
  3. `clang`/`clang++` 可执行 + 版本输出
  4. `cmake` 可执行 + 版本输出
  5. `ninja` 可执行 + 版本输出
  6. `make` 可执行 + 版本输出
  7. Python/Jupyter 来自 main 环境（`/opt/conda/envs/main/bin/python`、`/opt/conda/envs/main/bin/jupyter`）
  8. docker、supervisord 仍存在（服务未被破坏）
  9. devuser 可访问 LLVM 工具（`su - devuser -c "... conda activate main && llvm-config --version ..."`）
- **[FINAL VERIFICATION - HELLO WORLD COMPILE]**：
  - 编写简单 C++ 程序，使用 clang++ 编译并运行（优先 `-stdlib=libstdc++`，失败回退默认）
  - 验证工具链实际可用（不仅仅是存在）
- 输出 **BUILD TIMING SUMMARY** 表格（4个追加阶段的耗时）
- 清理计时器文件
- 输出构建完成提示（包含验证命令）
- 输出 `[TIMER] Stage 4/4 ...`

## 构建参数

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | 基础镜像标签（无中间变体） |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `bfsu` | Conda 源：bfsu/tuna/aliyun/official（变体按此重写 .condarc） |
| `PIP_MIRROR` | `aliyun` | Pip 源：aliyun/tuna/official |
| `LLVM_VERSION` | `22.1.8` | LLVM/Clang 统一版本号 |

> 注意：`FROM` 之前的 ARG 只在构建解析 FROM 时生效；FROM 后必须重新声明全部 ARG，否则 Stage 4 写 build-info 时 `${BASE_TAG}` 退化为空值。

## 服务继承

基础镜像的所有服务在 conda-llvm 变体中**保持完全可用**：

- **sshd**：SSH 服务（端口 22）
- **dockerd**：Docker DinD（端口 2375）
- **podman**：Podman rootless（按需）
- **jupyter**：Jupyter Notebook/Lab（端口 8888）
  - 使用 main 环境（`/opt/conda/envs/main`）的 jupyter，由 supervisord 绝对路径启动
  - **不受 PATH 变更影响**，始终正常运行
- **supervisord**：进程管理，配置不变

## 构建元数据位置

构建完成后，镜像中应存在以下元数据文件：
- `/etc/devcontainer-build-info`（来自基础镜像）
- `/etc/devcontainer-variant-conda-llvm-build-info`（本变体新增）

> conda 中间变体已下线，`/etc/devcontainer-variant-conda-build-info` 不再存在。

## 日志/输出规范

- 阶段开始：`echo "########################################################################"` 和 `# [CONDA-LLVM VARIANT STAGE N/4] ...`
- 动作标记：`[ACTION]`、`[INFO]`、`[OK]`、`[WARN]`、`[FAIL]`、`[DIAG]`、`[FATAL]`
- 计时器：`[TIMER] Stage N/4 (...) took Xs | LLVM variant cumulative: Ys`
- 分组安装框：使用 `┌─┐││└─┘` 边框绘制 `[CONDA INSTALL]`、`[GUARD]`、`[VERIFY]`、`[CLEANUP]`
- 验证框：使用 `┌─┐││└─┘` 边框绘制 `[VALIDATION CHECKPOINT]`
- 编译测试框：使用 `┌─┐││└─┘` 边框绘制 `[FINAL VERIFICATION - HELLO WORLD COMPILE]`
- 汇总表：使用 `╔═╗║║╠═╣╚═╝` 边框绘制 BUILD TIMING SUMMARY
- 错误处理：`[FATAL]` 后必须 `exit 1`；`[FAIL]` 后输出 `[DIAG]` 诊断并以原退出码终止
- 构建完成提示：包含验证命令 `llvm-config --version && clang --version && cmake --version`

## conda 命令执行规范

在 RUN 指令中执行 conda 相关命令时，**必须**先 source conda.sh 并激活 main 环境：

```dockerfile
RUN source /opt/conda/etc/profile.d/conda.sh && \
    conda activate main && \
    conda install -y --override-channels -c conda-forge ...
```

ENV 设置的 PATH 已经包含 `/opt/conda/envs/main/bin`，所以工具命令直接可用，但 `conda activate` 需要 shell 函数，因此仍需 source conda.sh。
