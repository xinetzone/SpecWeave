---
id: "pytorch-entrypoint-rules"
title: "Entrypoint 启动脚本规范"
source: "AGENTS.md#项目特有约束"
---
# Entrypoint 启动脚本规范（pytorch-base v3.0）

## 基本职责

entrypoint.sh 是容器的入口点（通过 tini 作为 PID 1 管理），负责 conda 环境激活、用户切换、信号转发和交互式横幅（含 GPU 设备信息展示）。

## 日志规范

使用结构化日志，输出到 stderr（不干扰应用 stdout）：

```bash
entry_log_info()  { echo "[entrypoint][INFO]  $(date '+%F %T') | $*" >&2; }
entry_log_warn()  { echo "[entrypoint][WARN]  $(date '+%F %T') | $*" >&2; }
entry_log_error() { echo "[entrypoint][ERROR] $(date '+%F %T') | $*" >&2; }
entry_log_debug() { [ "${ENTRYPOINT_DEBUG:-0}" = "1" ] && echo "[entrypoint][DEBUG] $(date '+%F %T') | $*" >&2; }
entry_log_branch(){ entry_log_info "[BRANCH] >>> $*"; }
```

- `ENTRYPOINT_DEBUG=1` 环境变量启用调试日志
- `ENTRYPOINT_QUIET=1` 环境变量抑制横幅输出（从build-info加载）
- 错误处理使用trap ERR，输出行号、失败命令、上下文信息

## 启动流程（4步）

1. **初始化**：加载build-time配置（`/etc/pytorch-base-build-info`中的PYTORCH_VERSION/PYTHON_VERSION/USE_GPU/CUDA_VERSION等）
2. **Conda环境设置**：
   - 将conda环境pytorch的bin目录 prepend到PATH
   - 设置CONDA_DEFAULT_ENV和CONDA_PREFIX
   - source conda.sh并执行 `conda activate pytorch`
   - 验证Python来自conda环境路径
   - 检查PyTorch三件套（torch/torchvision/torchaudio）是否可导入
   - 检查ONNX Runtime版本和providers（含CUDAExecutionProvider检测）
   - GPU版本获取CUDA版本、设备数、设备名、显存信息
3. **横幅显示**：交互式TTY时显示环境信息：
   - Conda环境名、Python版本
   - PyTorch版本、CUDA版本（torch builtin）
   - GPU设备列表（设备名+显存大小，可用时）；不可用时提示加`--gpus all`
   - torchvision/torchaudio版本
   - ONNX Runtime版本+CUDAExecutionProvider状态
   - 用户、工作目录、快速测试命令
4. **用户切换与命令执行**：
   - root运行时通过gosu切换到ai用户（默认）
   - RUN_AS_USER环境变量可指定目标用户（root则保持root）
   - 修复工作目录权限（root拥有时chown给目标用户）
   - 无命令时exec `/bin/bash -l`（登录shell，自动加载.bashrc中的conda激活）
   - 有命令时exec "$@"执行用户命令

## 关键环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| ENTRYPOINT_DEBUG | 0 | 调试日志开关 |
| ENTRYPOINT_QUIET | 0 | 抑制横幅 |
| RUN_AS_USER | ai | 非root运行时切换到的用户 |

## Conda环境激活机制

采用三层激活确保兼容性：
1. PATH prepend：`ENV_PATH/bin:CONDA_DIR/bin:$PATH`（Dockerfile ENV也设置）
2. profile.d脚本：`/etc/profile.d/conda.sh` 被source
3. .bashrc：登录shell自动source conda.sh和activate环境

## GPU信息探测（v3.0新增）

Banner中展示的GPU信息：
- `TORCH_CUDA_VER`：torch.version.cuda（PyTorch内置CUDA版本）
- `GPU_COUNT`：torch.cuda.device_count()
- `GPU_NAME[i]`：torch.cuda.get_device_name(i)（每张卡名称）
- `GPU_MEM[i]`：get_device_properties(i).total_memory（每张卡显存，GB）
- `CUDAExecutionProvider`：onnxruntime中是否启用GPU provider

无GPU时（`torch.cuda.is_available()=False`）显示友好提示：`not available (run with --gpus all for GPU acceleration)`，不报错。

## 错误处理

- trap ERR捕获错误，输出诊断上下文（PID、uid/gid、用户、工作目录、环境路径、命令参数）
- conda环境不存在时exit 1并列出可用环境
- Python不在PATH中时exit 1
- 目标用户不存在时exit 1并列出可用用户
- gosu不可用时输出WARN（不阻断，用户切换可能失败）
- 三件套（torchvision/torchaudio）或ORT不可导入时不报错（派生镜像可能不完整）

## 反模式

- ❌ 不要用 `su - ai -c "command"`（会创建新login shell丢失环境变量），使用 `gosu ai command`
- ❌ 不要在entrypoint中执行conda install/pip install（构建时完成，entrypoint只做环境激活）
- ❌ 不要忽略exec（直接执行bash而不exec，会导致tini无法正确转发信号）
- ❌ 不要用 `conda run -n pytorch command` 作为默认入口（慢且不直观），直接PATH prepend+activate
- ❌ 不要在无GPU时强制要求CUDA可用（构建环境可能没有GPU，运行时才挂载）
