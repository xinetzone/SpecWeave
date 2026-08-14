# onnx-quantized Dockerfile 规范

## 基础信息

- **基础镜像**: `devcontainer-base:onnx-pytorch-${BASE_TAG}`
- **安装环境**: conda base 环境（`/opt/conda`）
- **PATH 优先级**: `/opt/conda/bin` 优先于系统 PATH
- **默认 Python**: `/opt/conda/bin/python`（继承自 onnx-pytorch）
- **系统 venv**: `/opt/venv/bin/python` 保留（Jupyter 使用）

## 核心组件

| 组件 | 来源 | 说明 |
|------|------|------|
| PyTorch CPU | onnx-pytorch 继承 | `import torch` |
| ONNX | onnx-pytorch 继承 | `import onnx` |
| ONNX Runtime | onnx-pytorch 继承 | `import onnxruntime`，含 quantization 子模块 |
| onnxconverter-common | pip 安装 | `onnxconverter_common.float16` FP16 转换 |
| onnxruntime-tools | pip 安装 | `onnxruntime_tools.optimizer` BERT优化/量化 |
| neural-compressor | pip 安装 | `neural_compressor` Intel INC，PTQ/QAT |
| onnxsim | pip 安装 | `onnxsim` ONNX 模型简化 |

## 构建参数

| ARG | 默认值 | 说明 |
|-----|--------|------|
| BASE_TAG | latest | 基础镜像标签后缀 |
| APT_MIRROR | official | APT 镜像源 |
| CONDA_MIRROR | tuna (CN) / official | Conda 镜像源 |
| PIP_MIRROR | aliyun (CN) / official | Pip 镜像源 |

## Stage 结构（3 层追加）

### Stage 1/3: 基础验证 + 计时器初始化
- 验证 torch/onnx/onnxruntime 可导入
- 确认 devuser 和基础服务存在
- 初始化 `/tmp/.onnx-quantized-variant-build-timer`

### Stage 2/3: 安装量化工具包
- `pip install onnxconverter-common onnxruntime-tools neural-compressor onnxsim`
- 使用 `--mount=type=cache,target=/opt/conda/pkgs` 缓存
- 验证所有包可导入并输出版本号

### Stage 3/3: build-info + 清理 + 量化冒烟
- 写入 `/etc/devcontainer-variant-onnx-quantized-build-info`
- 8 项验证检查（导入/服务/权限/继承）
- 量化冒烟测试：创建模型→动态INT8量化→验证推理→精度检查→大小对比
- 输出 BUILD TIMING SUMMARY 表

## 量化模式

- **动态量化** (`quantize_dynamic`): 权重 INT8，激活 FP32，无需校准数据
- **静态量化** (`quantize_static`): 权重+激活 INT8，需 CalibrationDataReader
- **FP16 转换** (`float16.convert_float_to_float16`): 所有权重转 FP16
- **QDQ 格式**: `quantize_static(..., calibrate_method=...)` 输出 QDQ 节点
- **INC 高级量化**: `neural_compressor.quantization.fit()` 支持自动精度调优

## 服务继承

- SSH (sshd): 端口 22/2222 ✓
- Docker DinD: `/var/run/docker.sock` ✓
- Podman: ✓
- Jupyter: `/opt/venv/bin/jupyter` (supervisord 管理) ✓
- Supervisord: ✓

## build-info 路径

`/etc/devcontainer-variant-onnx-quantized-build-info`

包含字段：BUILD_DATE, VARIANT, BASE_IMAGE, ONNXRUNTIME_VERSION, TORCH_VERSION,
ONNX_VERSION, NEURAL_COMPRESSOR_VERSION, QUANTIZATION_MODES, PACKAGES_INSTALLED 等。
