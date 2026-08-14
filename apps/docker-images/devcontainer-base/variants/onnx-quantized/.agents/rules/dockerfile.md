# onnx-quantized Dockerfile 规范

## 基础信息

- **基础镜像**: `devcontainer-base:onnx-dev-${BASE_TAG}`
- **安装环境**: conda main 环境（`/opt/conda/envs/main`，free-threading cp314t）
- **PATH 优先级**: `/opt/conda/envs/main/bin` → `/opt/conda/bin` → 系统 PATH
- **默认 Python**: `/opt/conda/envs/main/bin/python`（继承自 onnx-dev）
- **激活方式**: Stage 内 `source /opt/conda/etc/profile.d/conda.sh && conda activate main`

## 核心组件

| 组件 | 来源 | 说明 |
|------|------|------|
| ONNX | onnx-dev 继承 | `import onnx`，模型构建用 `onnx.helper`（无 torch） |
| ONNX Runtime | onnx-dev 继承 | `import onnxruntime`，含 quantization 子模块 |
| onnxscript | onnx-dev 继承 | ONNX script 工具 |
| onnxconverter-common | pip 安装（幂等） | `onnxconverter_common.float16` FP16 转换 |
| onnxsim | pip 安装（幂等，多为继承） | `onnxsim` ONNX 模型简化（量化前预处理） |
| neural-compressor | **不预装** | 可选 PyTorch 扩展，需 `pip install neural-compressor torch` 按需自装 |

**排除项（负向验证）**：torch/torchvision（by design）、onnxoptimizer（free-threading 不兼容，CPython #111506）

## 构建参数

| ARG | 默认值 | 说明 |
|-----|--------|------|
| BASE_TAG | latest | 基础镜像标签后缀 |
| APT_MIRROR | official | APT 镜像源 |
| CONDA_MIRROR | bfsu (CN) / official | Conda 镜像源 |
| PIP_MIRROR | aliyun (CN) / official | Pip 镜像源 |

## Stage 结构（3 层追加）

### Stage 1/3: 基础验证 + 计时器初始化
- 验证 onnx/onnxruntime/onnxsim 可导入（main 环境）
- 守卫：free-threading（`sys._is_gil_enabled() is False`）+ torch 缺席（`find_spec('torch') is None`）
- 确认 devuser 和基础服务存在
- 初始化 `/tmp/.onnx-quantized-variant-build-timer`

### Stage 2/3: 安装量化工具包
- `conda activate main` 后 `pip install onnxconverter-common onnxsim`（幂等，多为继承 no-op）
- 使用 `--mount=type=cache,target=/opt/conda/pkgs` + `/root/.cache/pip` 缓存
- 守卫：python 构建串含 `cp314t` + GIL 仍禁用 + torch/onnxoptimizer 缺席
- 清理范围限定 main 环境（`/opt/conda/envs/main/lib`）

### Stage 3/3: build-info + 清理 + 量化冒烟
- 写入 `/etc/devcontainer-variant-onnx-quantized-build-info`
- 8 项验证检查（量化导入/main环境/Jupyter/服务/devuser/free-threading/LLVM/onnx-dev-init.sh）
- 量化冒烟测试（全部纯 ONNX，无 torch）：
  - QSMOKE：helper 构建 Gemm 模型 → onnxsim 精简 → 动态 INT8 量化 → 推理精度对比
  - FP16SMOKE：helper 构建 Gemm+Mul+Add → FP16 转换 → 推理精度对比
  - ORTUNIT：动态/静态 QDQ/QOperator/FP16/体积压缩综合单测
  - QCHECK：量化 API 冒烟
  - NCUNIT：条件块，仅当用户安装 neural-compressor 后运行
- 输出 BUILD TIMING SUMMARY 表

## 量化模式

- **动态量化** (`quantize_dynamic`): 权重 INT8，激活 FP32，无需校准数据
- **静态量化** (`quantize_static`): 权重+激活 INT8，需 CalibrationDataReader
- **FP16 转换** (`float16.convert_float_to_float16`): 所有权重转 FP16
- **QDQ 格式**: `quantize_static(..., quant_format=QuantFormat.QDQ, ...)` 输出 QuantizeLinear/DequantizeLinear 节点

## 服务继承

- SSH (sshd): 端口 22/2222 ✓
- Docker DinD: `/var/run/docker.sock` ✓
- Podman: ✓
- Jupyter: `/opt/conda/envs/main/bin/jupyter` ✓
- Supervisord: ✓

## build-info 路径

`/etc/devcontainer-variant-onnx-quantized-build-info`

包含字段：BUILD_DATE, VARIANT, BASE_IMAGE（=onnx-dev 链）, ONNXRUNTIME_VERSION,
ONNX_VERSION_ACTUAL, NEURAL_COMPRESSOR_VERSION（=not installed）, ONNXCONVERTER_COMMON_VERSION,
ONNXSIM_VERSION, QUANTIZATION_MODES, PYTHON_ENV（free-threading cp314t）,
PACKAGES_INSTALLED, PACKAGES_EXCLUDED（torch/torchvision/onnxoptimizer）等。
