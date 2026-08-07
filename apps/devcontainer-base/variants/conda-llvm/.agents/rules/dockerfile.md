# Conda-LLVM 变体 Dockerfile 规范

## 基础信息

- **基础镜像**：`devcontainer-base:conda-${BASE_TAG}`（基于 conda 变体，默认为 `devcontainer-base:conda-latest`）
- **Dockerfile 语法版本**：`# syntax=docker/dockerfile:1.7-labs`
- **Conda 路径**：`/opt/conda`（继承自 conda 变体）
- **LLVM 版本**：固定为 `${LLVM_VERSION}`（默认 `22.1.8`）
- **SHELL 指令**：`["/bin/bash", "-e", "-o", "pipefail", "-c"]`（显式声明，不依赖继承）
- **安装方式**：在 conda **base 环境**直接安装，不创建新环境
- **频道**：**conda-forge** 优先，设置 `channel_priority: strict`

## 核心约束

### 1. PATH 优先级（关键设计决策）

- **必须设置**：`ENV PATH=/opt/conda/bin:${PATH}`
- `/opt/conda/bin` 在 PATH **最前面**，确保 llvm-config/clang/cmake/ninja 直接可用
- 这是 conda-llvm 变体与 conda 变体的**关键区别**：
  - conda 变体：venv 优先，conda 不在默认 PATH
  - conda-llvm 变体：conda bin 优先，LLVM 工具开箱即用
- **Jupyter 服务不受影响**：supervisord 使用 `/opt/venv/bin/jupyter` **绝对路径**启动，不依赖 PATH

### 2. 版本一致性（强制执行）

以下 LLVM 相关包**必须统一锁定到 `${LLVM_VERSION}`**：
- `llvmdev=${LLVM_VERSION}`
- `clangdev=${LLVM_VERSION}`
- `clang=${LLVM_VERSION}`
- `clang-tools-extra=${LLVM_VERSION}`
- `lld=${LLVM_VERSION}`
- `lldb=${LLVM_VERSION}`

以下构建工具安装最新版本（不锁定版本）：
- `cmake`
- `ninja`
- `make`

### 3. 继承基础镜像设置（禁止覆盖）

以下指令由基础镜像/conda 变体设置，**不得在 conda-llvm Dockerfile 中重新定义**：

- `ENTRYPOINT`（保持 `/usr/bin/tini -- /usr/local/bin/entrypoint.sh`）
- `CMD`（保持 `[]`）
- `USER`（构建过程用 root，最终用户由基础镜像决定）
- `WORKDIR`（保持 `/workspace`）
- `HEALTHCHECK`（保持基础镜像的健康检查）
- `EXPOSE`、`VOLUME`（保持基础镜像声明）
- conda 基础配置（.condarc、conda-init.sh 等已由 conda 变体配置完成）

### 4. 激活脚本

- **主要方式**：通过 `ENV PATH=/opt/conda/bin:$PATH` 直接生效，无需手动 source
- **备选脚本**：`/etc/profile.d/conda-llvm-init.sh`
  - 权限：`chmod +x`
  - 功能：source conda.sh，如 conda bin 不在 PATH 则添加
  - 用途：向后兼容、登录 shell 场景
- **原始 conda-init.sh 保留**：`/etc/profile.d/conda-init.sh` 仍然存在，行为与 conda 变体一致（不自动激活 base）

### 5. BuildKit 缓存挂载（必须）

安装 LLVM 工具链的 Stage 2/4 **必须**使用 BuildKit cache 挂载加速：
```dockerfile
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    ...
```

## 追加层 4 阶段结构

Conda-LLVM 变体在 conda 变体的 5 个阶段之上，追加 **4 个阶段**（编号 LLVS1-LLVS4）：

### Stage 1/4：Conda 频道配置 + PATH 设置 + 计时器初始化

- 验证基础 conda 安装存在（`/opt/conda/bin/conda --version`）
- 设置 conda-forge 频道优先级：
  - `conda config --system --add channels conda-forge`
  - `conda config --system --set channel_priority strict`
- 验证 PATH 已包含 `/opt/conda/bin`（ENV 设置已生效）
- 验证基础镜像关键组件存在（devuser、/opt/venv、/opt/conda）
- 初始化追加层计时器：`/tmp/.llvm-variant-build-timer`
- 输出 `[TIMER] Stage 1/4 ...`
- 注意：执行 conda 命令前必须 `source /opt/conda/etc/profile.d/conda.sh`

### Stage 2/4：LLVM 工具链安装

- **必须**使用 `--mount=type=cache,target=/opt/conda/pkgs,sharing=locked`
- 执行流程：
  1. `source /opt/conda/etc/profile.d/conda.sh`
  2. `conda activate base`
  3. `conda install -y -c conda-forge` 安装所有包：
     - llvmdev, clangdev, clang, clang-tools-extra, lld, lldb（版本锁定）
     - cmake, ninja, make（最新版）
- 安装后验证关键包版本（conda list 或直接运行命令）
- 输出 `[TIMER] Stage 2/4 ...`

### Stage 3/4：符号链接 + conda-llvm-init.sh + 权限验证

- 检查 llvm-config 是否在 PATH 中，如不在则创建符号链接：
  - 搜索 `/opt/conda/bin` 下的 `llvm-config*`
  - 如有版本化的 llvm-config（如 llvm-config-22），创建 `llvm-config` 符号链接
- 创建 `/etc/profile.d/conda-llvm-init.sh`（使用 heredoc）：
  - source `/opt/conda/etc/profile.d/conda.sh`
  - 尝试 `conda activate base`（容错）
  - 检查 PATH 是否已包含 `/opt/conda/bin`，如未包含则添加
- 设置 `/opt/conda` 权限：
  - `chown -R root:root /opt/conda`
  - `chmod -R a+rX /opt/conda`
  - 确保 bin 目录下可执行文件有执行权限
- 快速可用性检查：llvm-config, clang, cmake, ninja, make 均可执行
- 恢复 devuser 对 `.bashrc` 的所有权
- 输出 `[TIMER] Stage 3/4 ...`

### Stage 4/4：构建元数据 + 清理 + 最终验证 + 汇总表

- 写入构建信息：`/etc/devcontainer-variant-conda-llvm-build-info`
  - 包含：BUILD_DATE、VARIANT、BASE_IMAGE、LLVM_VERSION_REQUESTED/ACTUAL、CLANG_VERSION、CMAKE_VERSION、NINJA_VERSION、CONDA_VERSION、PATH_PRIORITY、PACKAGES_INSTALLED 等
- 清理：
  - `conda clean -ya`
  - `pip cache purge`（venv 的 pip + conda 的 pip）
  - `apt-get clean`
  - 删除 `/tmp/*`、`/var/tmp/*`、`/var/lib/apt/lists/*`
- **[VALIDATION CHECKPOINT]** 9 项验证：
  1. `bash -n /etc/profile.d/conda-llvm-init.sh`（脚本语法）
  2. `llvm-config` 可执行 + 版本输出
  3. `clang`/`clang++` 可执行 + 版本输出
  4. `cmake` 可执行 + 版本输出
  5. `ninja` 可执行 + 版本输出
  6. `make` 可执行 + 版本输出
  7. `/opt/venv` 存在且 Jupyter 可通过绝对路径使用
  8. docker、supervisord 仍存在（服务未被破坏）
  9. devuser 可访问 LLVM 工具（`su - devuser -c "..."`）
- **[FINAL VERIFICATION - HELLO WORLD COMPILE]**：
  - 编写简单 C++ 程序，使用 clang++ 编译并运行
  - 验证工具链实际可用（不仅仅是存在）
- 输出 **BUILD TIMING SUMMARY** 表格（4个追加阶段的耗时）
- 清理计时器文件
- 输出构建完成提示（包含验证命令）
- 输出 `[TIMER] Stage 4/4 ...`

## 构建参数

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | conda 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna（继承自 conda 变体） |
| `CONDA_MIRROR` | `tuna` | Conda 源：tuna/official（继承自 conda 变体） |
| `PIP_MIRROR` | `aliyun` | Pip 源：aliyun/tuna/official（继承自 conda 变体） |
| `LLVM_VERSION` | `22.1.8` | LLVM/Clang 统一版本号 |

## 服务继承

conda 变体和基础镜像的所有服务在 conda-llvm 变体中**保持完全可用**：

- **sshd**：SSH 服务（端口 22）
- **dockerd**：Docker DinD（端口 2375）
- **podman**：Podman rootless（按需）
- **jupyter**：Jupyter Notebook/Lab（端口 8888）
  - **关键**：使用 `/opt/venv/bin/jupyter` **绝对路径**，由 supervisord 启动
  - **不受 PATH 变更影响**，始终正常运行
- **supervisord**：进程管理，配置不变

## 构建元数据位置

构建完成后，镜像中应存在以下元数据文件：
- `/etc/devcontainer-build-info`（来自基础镜像）
- `/etc/devcontainer-variant-conda-build-info`（来自 conda 变体）
- `/etc/devcontainer-variant-conda-llvm-build-info`（本变体新增）

## 日志/输出规范

- 阶段开始：`echo "########################################################################"` 和 `# [CONDA-LLVM VARIANT STAGE N/4] ...`
- 动作标记：`[ACTION]`、`[INFO]`、`[OK]`、`[WARN]`、`[ERROR]`
- 计时器：`[TIMER] Stage N/4 (...) took Xs | LLVM variant cumulative: Ys`
- 验证框：使用 `┌─┐││└─┘` 边框绘制 `[VALIDATION CHECKPOINT]`
- 编译测试框：使用 `┌─┐││└─┘` 边框绘制 `[FINAL VERIFICATION - HELLO WORLD COMPILE]`
- 汇总表：使用 `╔═╗║║╠═╣╚═╝` 边框绘制 BUILD TIMING SUMMARY
- 错误处理：`[ERROR]` 后必须 `exit 1`
- 构建完成提示：包含验证命令 `llvm-config --version && clang --version && cmake --version`

## conda 命令执行规范

在 RUN 指令中执行 conda 相关命令时，**必须**先 source conda.sh：

```dockerfile
RUN source /opt/conda/etc/profile.d/conda.sh && \
    conda activate base && \
    conda install -y -c conda-forge ...
```

ENV 设置的 PATH 已经包含 `/opt/conda/bin`，所以 `conda` 命令直接可用，但 `conda activate` 需要 shell 函数，因此仍需 source conda.sh。
