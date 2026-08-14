# ONNX-Dev 变体 Dockerfile 规范

## 基础信息

- **基础镜像**：`devcontainer-base:conda-llvm-${BASE_TAG}`（基于 conda-llvm 变体，默认为 `devcontainer-base:conda-llvm-latest`）
- **依赖链**：`devcontainer-base:latest` → `devcontainer-base:conda-llvm-*` → 本变体（conda 中间变体已下线）
- **Dockerfile 语法版本**：`# syntax=docker/dockerfile:1.7-labs`
- **Conda 发行版**：Miniforge3（conda-forge 官方，libmamba solver），路径 `/opt/conda`（继承自基础镜像）
- **默认环境**：conda **main 环境**（`/opt/conda/envs/main`，Python 3.14.6 cp314t free-threading，GIL 默认禁用）
- **SHELL 指令**：`["/bin/bash", "-e", "-o", "pipefail", "-c"]`（显式声明，不依赖继承）
- **安装方式**：pip 安装至 conda **main 环境**（默认用户环境），与默认 Python/Jupyter 共享环境
- **核心约束**：**不含 PyTorch**——torch/torchvision 显式排除 + 构建期负向验证防线

## 核心约束

### 1. PATH 优先级（关键设计决策）

- **必须设置**：`ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}`
- `/opt/conda/envs/main/bin` 在 PATH **最前面**（与 conda-llvm 变体一致，显式重申保持自包含）
- 默认 `python`/`pip` 指向 conda main 环境的 Python 3.14.6（cp314t free-threading，ONNX 工具所在环境）
- **Jupyter 服务不受影响**：supervisord 使用 main 环境 **绝对路径**（`/opt/conda/envs/main/bin/jupyter`）启动，不依赖 PATH

### 2. PyTorch 一等排除约束（强制执行）

- **禁止安装**：`torch`、`torchvision`（以及任何强依赖 torch 的包）
- **负向验证防线（两处强制）**：
  1. Stage 2 安装后：`python -c "import importlib.util as u,sys; sys.exit(0 if u.find_spec('torch') is None else 1)"`——若任何依赖意外拉入 torch，构建立即失败
  2. Stage 4 验证 8/10：torch AND torchvision 同时缺席断言
- 用 `find_spec` 而非 `import torch` 检测：不实际导入（更快、无副作用、不触发 torch 初始化报错歧义）
- **无 TORCH_INDEX_URL 构建参数**（区别于 onnx-pytorch 变体）

### 3. ONNX 生态安装（main 环境，pip 分组）

Stage 2 使用 `pip_install_group` 辅助函数按组安装（结构化日志 + 计时 + 失败诊断）：

| 分组 | 包 | 说明 |
|------|-----|------|
| G1: ONNX Core | onnx, onnxruntime | 模型格式 + CPU 推理引擎 |
| G2: ONNX Tools | onnx-simplifier, onnxoptimizer, onnxscript | 精简/优化/算子编写 |

- 安装目标：`conda activate main` 后 pip 安装（**不是** base 环境）
- 每组使用 `pip install --no-cache-dir --timeout 120 --retries 5 <pkgs>`
- 失败时输出冲突诊断（`pip check` + 已装冲突包列表）并以原退出码终止
- 版本策略：全部 `latest`（跟随 PyPI/conda-forge 最新稳定版），实际版本写入 build-info

### 4. free-threading 完整性 GUARD（Stage 2 安装后强制）

pip 安装可能引入破坏 free-threading 的包，安装后必须断言：
1. `conda list python` 的 build string 仍含 `cp314t`（python 未被降级/替换）
2. `sys._is_gil_enabled() is False`（GIL 仍禁用）

任一断言失败 → `[FATAL]` + `exit 1`。

### 5. 继承基础镜像设置（禁止覆盖）

以下指令由基础镜像/conda-llvm 变体设置，**不得在 onnx-dev Dockerfile 中重新定义**：

- `ENTRYPOINT`、`CMD`、`USER`、`WORKDIR`、`HEALTHCHECK`、`EXPOSE`、`VOLUME`
- conda 配置（.condarc、conda-init.sh 已由基础镜像/conda-llvm 配置完成）
- 中文环境（`zh_CN.UTF-8`/`Asia/Shanghai`）

### 6. 激活脚本

- **主要方式**：通过 `ENV PATH=/opt/conda/envs/main/bin:...` 直接生效，无需手动 source
- **备选脚本**：`/etc/profile.d/onnx-dev-init.sh`
  - 权限：`chmod +x`
  - 功能：source conda.sh，`conda activate main`（容错回退）；若 main bin 不在 PATH 则添加
  - 用途：向后兼容、登录 shell 场景（devuser `.bash_profile` 会 source 它）
- **基础镜像 conda-init.sh 保留**：`/etc/profile.d/conda-init.sh` 激活 main 环境（基础镜像默认行为）

### 7. BuildKit 缓存挂载（必须）

Stage 2 **必须**使用 BuildKit cache 挂载加速：
```dockerfile
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    ...
```

## 追加层 4 阶段结构

ONNX-Dev 变体在 conda-llvm 变体之上追加 **4 个阶段**（计时器标记 ONXDS1-ONXDS3）：

### Stage 1/4：计时器初始化 + 基础验证

- 验证基础 conda 安装存在（`/opt/conda/bin/conda --version`）
- 验证 main 环境存在且 python 为 free-threading（GIL 禁用断言）
- 验证基础镜像关键组件存在（devuser、/opt/conda、/opt/conda/envs/main、llvm-config）
- 初始化追加层计时器：`/tmp/.onnx-dev-variant-build-timer`
- 输出 `[TIMER] Stage 1/4 ...`

### Stage 2/4：ONNX 生态安装（main 环境）+ 双 GUARD + 清理

- **必须**使用 `--mount=type=cache`（conda pkgs + pip cache）
- 执行流程：
  1. `source /opt/conda/etc/profile.d/conda.sh`
  2. `conda activate main`
  3. `pip_install_group` 分两组安装（G1/G2）
  4. 输出已安装版本汇总（onnx/onnxruntime/onnxsim/onnxoptimizer/onnxscript）
  5. **[GUARD] free-threading 完整性检查**（cp314t + GIL 禁用）
  6. **[GUARD] torch/torchvision 缺席负向验证**
  7. 激进清理（pycache/pyc/conda clean/pip cache）
- 输出 `[TIMER] Stage 2/4 ...`

### Stage 3/4：onnx-dev-init.sh + 权限验证 + 清理

- 创建 `/etc/profile.d/onnx-dev-init.sh`（heredoc）：激活 main 环境 + PATH 兜底
- 设置 `/opt/conda` 权限：`chown -R root:root` + `chmod -R a+rX` + bin 可执行
- 快速可用性检查：onnx、onnxruntime 可导入
- 恢复 devuser `.bashrc`/`.bash_profile` 所有权（bash_profile source onnx-dev-init.sh）
- 激进清理
- 输出 `[TIMER] Stage 3/4 ...`

### Stage 4/4：构建元数据 + 清理 + 最终验证 + 纯 ONNX 冒烟 + 汇总表

- `set +o pipefail`（规避 `jupyter --version | head` 的 SIGPIPE 120 退出码）
- 写入构建信息：`/etc/devcontainer-variant-onnx-dev-build-info`
  - 关键字段：`INSTALL_ENV=main (default user env)`、`PYTHON_BUILD=free-threading nogil active`、`PATH_PRIORITY=conda-main-bin-first`、`PACKAGES_INSTALLED=onnx,onnxruntime,onnx-simplifier,onnxoptimizer,onnxscript`、`PACKAGES_EXCLUDED=torch,torchvision (optional; install on demand via pip)` 等
- 清理：conda clean + pip cache purge + apt clean + tmp
- **[VALIDATION CHECKPOINT]** 10 项验证：
  1. `bash -n /etc/profile.d/onnx-dev-init.sh`（脚本语法）
  2. onnx 导入 + 版本
  3. onnxruntime 导入 + 版本
  4. onnx-simplifier 导入
  5. onnxoptimizer 导入
  6. onnxscript 导入
  7. free-threading python（GIL 禁用断言）
  8. **torch AND torchvision 缺席**（负向断言，find_spec）
  9. main 环境 jupyter 可执行 + docker/supervisord 仍存在（服务未被破坏）
  10. devuser 可访问 ONNX 工具 + LLVM 工具链继承（llvm-config/clang）
- **[FINAL VERIFICATION - PURE-ONNX SMOKE]**（无 torch 依赖）：
  - free-threading 运行时断言
  - `onnx.helper` 手工构建 Add 模型 → `onnx.checker` 校验 → 保存
  - `onnxruntime` CPUExecutionProvider 推理，结果与期望一致（[1,2]+[3,4]=[4,6]）
- 输出 **BUILD TIMING SUMMARY** 表格（4 个追加阶段耗时）
- 清理计时器文件
- 输出构建完成提示（包含验证命令）
- 输出 `[TIMER] Stage 4/4 ...`

## 构建参数

| 参数 | 默认值 | 说明 |
|------|-------|------|
| `BASE_TAG` | `latest` | conda-llvm 基础镜像标签 |
| `APT_MIRROR` | `official` | APT 源：official/aliyun/tuna |
| `CONDA_MIRROR` | `bfsu` | Conda 源：bfsu/tuna/aliyun/official |
| `PIP_MIRROR` | `aliyun` | Pip 源：aliyun/tuna/official |

> 注意：`FROM` 之前的 ARG 只在解析 FROM 时生效；FROM 后必须重新声明全部 ARG，否则 Stage 4 写 build-info 时 `${BASE_TAG}` 退化为空值。

## 服务继承

conda-llvm 变体和基础镜像的所有服务在 onnx-dev 变体中**保持完全可用**：

- **sshd**（端口 22）、**dockerd**（DinD，端口 2375）、**podman**（rootless，按需）
- **jupyter**（端口 8888）：使用 main 环境 `/opt/conda/envs/main/bin/jupyter` 绝对路径，由 supervisord 启动，不受 PATH 变更影响
- **supervisord**：进程管理，配置不变

## 构建元数据位置

构建完成后，镜像中应存在以下元数据文件：
- `/etc/devcontainer-build-info`（来自基础镜像）
- `/etc/devcontainer-variant-conda-llvm-build-info`（来自 conda-llvm 变体）
- `/etc/devcontainer-variant-onnx-dev-build-info`（本变体新增）

## 日志/输出规范

- 阶段开始：`echo "########################################################################"` 和 `# [ONNX-DEV VARIANT STAGE N/4] ...`
- 动作标记：`[ACTION]`、`[INFO]`、`[OK]`、`[WARN]`、`[FAIL]`、`[DIAG]`、`[FATAL]`
- 计时器：`[TIMER] Stage N/4 (...) took Xs | ONNX-Dev variant cumulative: Ys`
- 分组安装框：使用 `┌─┐││└─┘` 边框绘制 `[PIP INSTALL]`
- GUARD 框：使用 `┌─┐││└─┘` 边框绘制 `[GUARD]`
- 验证框：使用 `┌─┐││└─┘` 边框绘制 `[VALIDATION CHECKPOINT]`
- 冒烟测试框：使用 `┌─┐││└─┘` 边框绘制 `[FINAL VERIFICATION - PURE-ONNX SMOKE]`
- 汇总表：使用 `╔═╗║║╠═╣╚═╝` 边框绘制 BUILD TIMING SUMMARY
- 错误处理：`[FATAL]` 后必须 `exit 1`；`[FAIL]` 后输出 `[DIAG]` 诊断并以原退出码终止
- 构建完成提示：包含验证命令 `/opt/conda/envs/main/bin/python -c "import onnx,onnxruntime;print(...)"`

## conda 命令执行规范

在 RUN 指令中执行 conda/pip 相关命令时，**必须**先 source conda.sh 并激活 main 环境：

```dockerfile
RUN source /opt/conda/etc/profile.d/conda.sh && \
    conda activate main && \
    pip install ...
```

ENV 设置的 PATH 已包含 `/opt/conda/envs/main/bin`，工具命令直接可用，但 `conda activate` 需要 shell 函数，因此仍需 source conda.sh。
