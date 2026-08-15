# torch-dev Dockerfile 规范

## 基础信息

- **基础镜像**: `devcontainer-base:onnx-quantized-${BASE_TAG}`
- **安装环境**: conda main 环境（`/opt/conda/envs/main`，free-threading cp314t）
- **PATH 优先级**: `/opt/conda/envs/main/bin` → `/opt/conda/bin` → 系统 PATH
- **默认 Python**: `/opt/conda/envs/main/bin/python`（继承自 onnx-quantized）
- **激活方式**: Stage 内 `source /opt/conda/etc/profile.d/conda.sh && conda activate main`
- **Jupyter kernel**: **不在此变体注册**（kernel 注册属于下游 ai-dev 变体职责）

## 核心组件

| 组件 | 来源 | 说明 |
|------|------|------|
| ONNX | onnx-quantized 继承 | `import onnx` |
| ONNX Runtime | onnx-quantized 继承 | `import onnxruntime`，含 quantization 子模块 |
| onnxsim | onnx-quantized 继承 | `import onnxsim`，模型简化 |
| onnxconverter-common | onnx-quantized 继承 | `onnxconverter_common.float16` FP16 转换 |
| onnxscript | onnx-quantized 继承 | ONNX script 工具 |
| **torch** | **pip 安装（PyTorch 索引）** | `import torch`，cp314t free-threading 构建 |
| **torchvision** | **pip 安装（PyTorch 索引）** | `import torchvision`，与 torch 版本匹配 |

**排除项（负向验证）**：onnxoptimizer（free-threading 不兼容，CPython #111506）

## 构建参数

| ARG | 默认值 | 说明 |
|-----|--------|------|
| BASE_TAG | latest | 基础镜像标签后缀 |
| APT_MIRROR | official | APT 镜像源 |
| CONDA_MIRROR | bfsu (CN) / official | Conda 镜像源 |
| PIP_MIRROR | aliyun (CN) / official | Pip 镜像源 |
| TORCH_CUDA_INDEX | cu130 | PyTorch CUDA 索引（cu130/cu128/cpu） |

## Stage 结构（3 层追加）

### Stage 1/3: 基础验证 + 计时器初始化
- 验证 onnx-quantized 父层组件（main 环境 + free-threading + 量化工具链）
- **关键守卫**：
  - free-threading 已启用（`sys._is_gil_enabled() is False`）
  - torch **缺席**（父层 onnx-quantized 不含 torch，验证干净基础）
  - onnxoptimizer **缺席**（free-threading 不兼容）
- 验证 onnxruntime.quantization API 可导入
- 确认 devuser 和基础服务（docker/supervisord）存在
- 初始化 `/tmp/.torch-dev-variant-build-timer`

### Stage 2/3: PyTorch 安装 + 守卫 + 清理
- `conda activate main` 后使用 `pip_install_group` 辅助函数：
  - 从 `https://download.pytorch.org/whl/${TORCH_CUDA_INDEX}` 安装 torch + torchvision
  - 分组结构化日志、超时重试（120s timeout, 5 retries）、冲突诊断（pip check）
- 使用 `--mount=type=cache,target=/opt/conda/pkgs` + `/root/.cache/pip` 缓存
- **安装后守卫**：
  - python 构建串含 `cp314t`
  - GIL 仍禁用（free-threading 完整性）
  - torch **present**（正向验证，与 Stage 1 翻转）
  - torchvision **present**
  - onnxoptimizer **still absent**（未被依赖拉入）
- 设置 main env bin 可执行权限
- 清理范围限定 main 环境（`/opt/conda/envs/main/lib`）+ conda/pip 缓存

### Stage 3/3: build-info + PyTorch 冒烟 + 计时汇总
- 写入 `/etc/devcontainer-variant-torch-dev-build-info`
- 8 项验证检查（torch导入/main环境/Jupyter/服务/devuser/free-threading/LLVM/量化栈继承）
- PyTorch 冒烟测试（6项核心算子正确性）：
  - TSMOKE-1: matmul（(64,128)@(128,32) → (64,32)）
  - TSMOKE-2: conv2d（(1,3,32,32) * (16,3,3,3) padding=1 → (1,16,32,32)）
  - TSMOKE-3: autograd（Linear 反向传播，梯度形状正确）
  - TSMOKE-4: softmax + cross_entropy（loss 为标量且 > 0）
  - TSMOKE-5: 基础 tensor ops（arange/sum/mul 正确性）
  - TSMOKE-6: MLP forward（Sequential(16→32→ReLU→4) → (4,4)）
- 输出 BUILD TIMING SUMMARY 表（3个追加层分别计时）
- 最终清理（apt/tmp/__pycache__）

## 与 onnx-pytorch 的架构差异

| 维度 | onnx-pytorch | torch-dev |
|------|--------------|-----------|
| **Python 环境** | conda base | conda main |
| **Python 版本** | 3.13.x (标准 GIL) | 3.14.6t (free-threading) |
| **GIL 状态** | 启用（`sys._is_gil_enabled() is True`） | 禁用（`sys._is_gil_enabled() is False`） |
| **torch 安装位置** | `/opt/conda/lib/python3.13/site-packages/` | `/opt/conda/envs/main/lib/python3.14/site-packages/` |
| **Python 路径** | `/opt/conda/bin/python` | `/opt/conda/envs/main/bin/python` |
| **onnxoptimizer** | ✅ 预装 | ❌ 排除（free-threading 不兼容） |
| **下游变体** | 无（平行变体） | ai-dev（直接基础） |

## 服务继承

- SSH (sshd): 端口 22/2222 ✓
- Docker DinD: `/var/run/docker.sock` ✓
- Podman: ✓
- Jupyter: `/opt/conda/envs/main/bin/jupyter` ✓
- Supervisord: ✓

## build-info 路径

`/etc/devcontainer-variant-torch-dev-build-info`

包含字段：BUILD_DATE, VARIANT, BASE_IMAGE（=onnx-quantized 链）, INSTALL_ENV（=main）,
PYTHON_VERSION, PYTHON_BUILD（=cp314t free-threading）, TORCH_VERSION, TORCHVISION_VERSION,
TORCH_CUDA_INDEX, TORCH_CUDA_AVAILABLE, ONNX_VERSION, ONNXRUNTIME_VERSION,
PACKAGES_INSTALLED（torch,torchvision）, PACKAGES_INHERITED（onnx,onnxruntime,onnxconverter-common,onnxsim,onnxscript）,
PACKAGES_EXCLUDED（onnxoptimizer）, KERNEL_REGISTERED（=false）, DOWNSTREAM_VARIANTS（=ai-dev）等。
