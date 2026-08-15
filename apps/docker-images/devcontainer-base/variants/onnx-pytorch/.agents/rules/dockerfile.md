# ONNX-PyTorch 变体 Dockerfile 规范

## 基础信息

- **基础镜像**：`devcontainer-base:conda-llvm-${BASE_TAG}`（基于 conda-llvm 变体，默认为 `devcontainer-base:conda-llvm-latest`）
- **依赖链**：`devcontainer-base:latest` → `devcontainer-base:conda-*` → `devcontainer-base:conda-llvm-*` → 本变体
- **Dockerfile 语法版本**：`# syntax=docker/dockerfile:1.7-labs`
- **Conda 路径**：`/opt/conda`（继承自 conda 变体）
- **SHELL 指令**：`["/bin/bash", "-e", "-o", "pipefail", "-c"]`（显式声明，不依赖继承）
- **安装方式**：在 conda **base 环境**直接安装，不创建新环境
- **运行时**：PyTorch **CPU** 版（不安装 CUDA 版），通过专用 wheel 索引安装
- **频道**：**conda-forge** 优先，设置 `channel_priority: strict`

## 核心约束

### 1. PATH 优先级（关键设计决策）

- **必须设置**：`ENV PATH=/opt/conda/bin:${PATH}`
- `/opt/conda/bin` 在 PATH **最前面**，确保 python/pip/torch/onnx/onnxruntime 直接可用
- 默认 `python`/`pip` 指向 conda base 环境的 Python（PyTorch/ONNX 所在环境）
- **Jupyter 服务不受影响**：supervisord 使用 main 环境 `/opt/conda/envs/main/bin/jupyter` 绝对路径启动，独立于 base torch 环境（`/opt/venv` 已在基础镜像中移除）

### 2. PyTorch CPU 安装（强制约束）

- **必须**使用 CPU 专用索引安装，避免误装 CUDA 版（体积巨大且无用）：
  ```
  pip install --no-cache-dir torch torchvision --index-url "${TORCH_INDEX_URL}"
  ```
- `TORCH_INDEX_URL` 默认 `https://download.pytorch.org/whl/cpu`
- 安装后必须验证 `torch.cuda.is_available() == False`，确认是 CPU 版

### 3. ONNX 生态安装

在 Stage 3/4 安装 ONNX 生态工具（普通 PyPI，受 `PIP_MIRROR` 控制）：
```
pip install --no-cache-dir onnx onnxruntime onnx-simplifier onnxoptimizer onnxscript
```

### 4. 继承基础镜像设置（禁止覆盖）

以下指令由基础镜像/conda/conda-llvm 变体设置，**不得在 onnx-pytorch Dockerfile 中重新定义**：

- `ENTRYPOINT`（保持 `/usr/bin/tini -- /usr/local/bin/entrypoint.sh`）
- `CMD`（保持 `[]`）
- `USER`（构建过程用 root，最终用户由基础镜像决定）
- `WORKDIR`（保持 `/workspace`）
- `HEALTHCHECK`（保持基础镜像的健康检查）
- `EXPOSE`、`VOLUME`（保持基础镜像声明）
- conda 基础配置（.condarc、conda-init.sh 等已由 conda 变体配置完成）

### 5. 激活脚本

- **主要方式**：通过 `ENV PATH=/opt/conda/bin:$PATH` 直接生效，无需手动 source
- **备选脚本**：`/etc/profile.d/onnx-pytorch-init.sh`
  - 权限：`chmod +x`
  - 功能：source conda.sh，如 conda bin 不在 PATH 则添加
  - 用途：向后兼容、登录 shell 场景
- **原始 conda-init.sh 保留**：`/etc/profile.d/conda-init.sh` 仍然存在，行为与 conda 变体一致（不自动激活 base）

### 6. BuildKit 缓存挂载（必须）

安装 PyTorch 的 Stage 2/4 **必须**使用 BuildKit cache 挂载加速：
```dockerfile
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    ...
```

## 追加层 4 阶段结构

ONNX-PyTorch 变体在 conda-llvm 变体之上，追加 **4 个阶段**（编号 ONXS1-ONXS4）：

### Stage 1/4：Conda 频道配置 + PATH 设置 + 计时器初始化

- 验证基础 conda-llvm 安装存在（`/opt/conda/bin/conda --version`）
- 设置 conda-forge 频道优先级：
  - `conda config --system --add channels conda-forge`
  - `conda config --system --set channel_priority strict`
- 验证 PATH 已包含 `/opt/conda/bin`（ENV 设置已生效）
- 验证基础镜像关键组件存在（devuser、/opt/conda、llvm-config；`/opt/venv` 已在基础镜像移除，不在验证列表）
- 初始化追加层计时器：`/tmp/.onnx-pytorch-variant-build-timer`
- 输出 `[TIMER] Stage 1/4 ...`
- 注意：执行 conda 命令前必须 `source /opt/conda/etc/profile.d/conda.sh`

### Stage 2/4：PyTorch CPU 安装

- **必须**使用 `--mount=type=cache,target=/opt/conda/pkgs,sharing=locked`
- 执行流程：
  1. `source /opt/conda/etc/profile.d/conda.sh`
  2. `conda activate base`
  3. `pip install --no-cache-dir torch torchvision --index-url "${TORCH_INDEX_URL}"`
- 安装后验证关键包版本：
  - `torch.__version__`、`torchvision.__version__`
  - `torch.cuda.is_available()`（应为 `False`）
- 输出 `[TIMER] Stage 2/4 ...`

### Stage 3/4：ONNX 生态安装 + onnx-pytorch-init.sh + 权限验证

- 安装 ONNX 生态：
  ```
  pip install --no-cache-dir onnx onnxruntime onnx-simplifier onnxoptimizer onnxscript
  ```
- 创建 `/etc/profile.d/onnx-pytorch-init.sh`（使用 heredoc）：
  - source `/opt/conda/etc/profile.d/conda.sh`
  - 尝试 `conda activate base`（容错）
  - 检查 PATH 是否已包含 `/opt/conda/bin`，如未包含则添加
- 设置 `/opt/conda` 权限：
  - `chown -R root:root /opt/conda`
  - `chmod -R a+rX /opt/conda`
  - 确保 bin 目录下可执行文件有执行权限
- 快速可用性检查：torch、onnx、onnxruntime 均可导入
- 恢复 devuser 对 `.bashrc` 的所有权
- 输出 `[TIMER] Stage 3/4 ...`

### Stage 4/4：构建元数据 + 清理 + 最终验证 + PyTorch/ONNX 冒烟 + 汇总表

- 写入构建信息：`/etc/devcontainer-variant-onnx-pytorch-build-info`
  - 包含：BUILD_DATE、VARIANT=onnx-pytorch、BASE_IMAGE=devcontainer-base:conda-llvm-${BASE_TAG}、TORCH_VERSION_ACTUAL、TORCHVISION_VERSION_ACTUAL、ONNX_VERSION_ACTUAL、ONNXRUNTIME_VERSION_ACTUAL、CUDA_AVAILABLE（应为 False）、CONDA_VERSION、PATH_PRIORITY、PACKAGES_INSTALLED 等
- 清理：
  - `conda clean -ya`
  - `pip cache purge`（venv 的 pip + conda 的 pip）
  - `apt-get clean`
  - 删除 `/tmp/*`、`/var/tmp/*`、`/var/lib/apt/lists/*`
- **[VALIDATION CHECKPOINT]** 10 项验证：
  1. `bash -n /etc/profile.d/onnx-pytorch-init.sh`（脚本语法）
  2. `torch` 导入 + 版本输出
  3. `torchvision` 导入 + 版本输出
  4. `onnx` 导入 + 版本输出
  5. `onnxruntime` 导入 + 版本输出
  6. `torch.cuda.is_available() == False`（CPU 版确认）
  7. Jupyter 可通过 main 环境绝对路径 `/opt/conda/envs/main/bin/jupyter` 使用（supervisord 实际路径）
  8. docker、supervisord 仍存在（服务未被破坏）
  9. devuser 可访问 PyTorch/ONNX（`su - devuser -c "..."`）
  10. LLVM 工具链仍继承自 conda-llvm 基础（llvm-config、clang）
- **[FINAL VERIFICATION - PYTORCH+ONNX SMOKE]**：
  - torch 张量运算冒烟（`(a+b)*2` 结果校验）
  - 用 torch 将简单模块导出为 ONNX
  - 用 onnxruntime CPU provider 加载并推理，结果与 torch 期望一致
  - 验证工具链实际可用（不仅仅是存在）
- 输出 **BUILD TIMING SUMMARY** 表格（4个追加阶段的耗时）
- 清理计时器文件
- 输出构建完成提示（包含验证命令）
- 输出 `[TIMER] Stage 4/4 ...`

## 构建参数

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | conda-llvm 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna（继承自 conda 变体） |
| `CONDA_MIRROR` | `tuna` | Conda 源：tuna/official（继承自 conda 变体） |
| `PIP_MIRROR` | `aliyun` | Pip 源：aliyun/tuna/official（继承自 conda 变体） |
| `TORCH_INDEX_URL` | `https://download.pytorch.org/whl/cpu` | PyTorch CPU 版 wheel 索引 |

## 服务继承

conda-llvm 变体和基础镜像的所有服务在 onnx-pytorch 变体中**保持完全可用**：

- **sshd**：SSH 服务（端口 22）
- **dockerd**：Docker DinD（端口 2375）
- **podman**：Podman rootless（按需）
- **jupyter**：Jupyter Notebook/Lab（端口 8888）
  - **关键**：由 supervisord 以 main 环境绝对路径 `/opt/conda/envs/main/bin/jupyter` 启动
  - **不受 PATH 变更影响**，始终正常运行
- **supervisord**：进程管理，配置不变

## 构建元数据位置

构建完成后，镜像中应存在以下元数据文件：
- `/etc/devcontainer-build-info`（来自基础镜像）
- `/etc/devcontainer-variant-conda-build-info`（来自 conda 变体）
- `/etc/devcontainer-variant-conda-llvm-build-info`（来自 conda-llvm 变体）
- `/etc/devcontainer-variant-onnx-pytorch-build-info`（本变体新增）

## 日志/输出规范

- 阶段开始：`echo "########################################################################"` 和 `# [ONNX-PYTORCH VARIANT STAGE N/4] ...`
- 动作标记：`[ACTION]`、`[INFO]`、`[OK]`、`[WARN]`、`[ERROR]`
- 计时器：`[TIMER] Stage N/4 (...) took Xs | ONNX-PyTorch variant cumulative: Ys`
- 验证框：使用 `┌─┐││└─┘` 边框绘制 `[VALIDATION CHECKPOINT]`
- 冒烟测试框：使用 `┌─┐││└─┘` 边框绘制 `[FINAL VERIFICATION - PYTORCH+ONNX SMOKE]`
- 汇总表：使用 `╔═╗║║╠═╣╚═╝` 边框绘制 BUILD TIMING SUMMARY
- 错误处理：`[ERROR]` 后必须 `exit 1`
- 构建完成提示：包含验证命令 `python -c "import torch,onnx,onnxruntime;print(torch.__version__,onnx.__version__,onnxruntime.__version__)"`

## conda 命令执行规范

在 RUN 指令中执行 conda 相关命令时，**必须**先 source conda.sh：

```dockerfile
RUN source /opt/conda/etc/profile.d/conda.sh && \
    conda activate base && \
    pip install ...
```

ENV 设置的 PATH 已经包含 `/opt/conda/bin`，所以 `conda`/`pip` 命令直接可用，但 `conda activate` 需要 shell 函数，因此仍需 source conda.sh。
