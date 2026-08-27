# torch-dev-slim 镜像瘦身指南

> **文档版本**: 1.0.0 | **更新日期**: 2026-08-19 | **镜像版本**: devcontainer-base:torch-dev-slim
>
> **适用标签**: `torch-dev-slim`（slim 标签）| **对照标签**: `torch-dev-latest`（完整版）

---

## 📊 镜像体积对比

| 镜像标签 | 体积 | 说明 |
|---------|------|------|
| `devcontainer-base:onnx-quantized-slim` | 3.5 GB | 基础层（ONNX 量化 + LLVM + free-threading） |
| `devcontainer-base:torch-dev-slim`（未优化初始） | **10.2 GB** | 首次构建，未经瘦身 |
| `devcontainer-base:torch-dev-slim`（R1 后） | 8.3 GB | 第一轮基础瘦身（-1.9 GB） |
| `devcontainer-base:torch-dev-slim`（**R2 当前**） | **8.15 GB** | 第二轮深度瘦身（**总计 -2.05 GB**） |
| `devcontainer-base:torch-dev-latest`（对照） | ~10 GB | 完整版（含全部符号、开发工具、所有CUDA库） |

**核心收益**: 从 10.2 GB → 8.15 GB，节省 **2.05 GB（20%）**，功能无损失。

---

## 🔬 瘦身方法论（两轮 R1/R2）

瘦身采用 **七概念方法论**（R-I-F-V-C）指导，分为两轮：

### R1：基础瘦身（-1.9 GB）

第一轮针对明显冗余的文件，基于文件用途分析：

| 策略 | 节省 | 技术细节 |
|------|------|---------|
| `strip --strip-unneeded` 共享库 | ~508 MB | 移除所有 `.so` 文件的调试符号和未引用符号 |
| 删除非必要静态库（`.a`） | ~80 MB | 静态库仅用于链接，运行时不需要 |
| 删除 `libnvrtc.alt.so` | ~40 MB | NVRTC 备用库，标准 `libnvrtc.so` 已足够 |
| 删除 `libnvperf_*` 性能分析库 | ~60 MB | Nsight Perf 分析库，普通开发不需要 |
| 删除 NVSHMEM 设备端 bitcode | ~25 MB | `nvshmem_device.bc`，HPC 多节点通信专用 |
| 删除 Triton AMD 后端 | ~45 MB | ROCm/AMD GPU 后端，本镜像仅支持 CUDA |
| 消除 `chmod -R /opt/conda` CoW 膨胀 | ~1.2 GB | 写时复制机制导致整层复制，改为精准权限修复 |

### R2：深度瘦身（-150 MB 净增）

第二轮基于 **DT_NEEDED 动态依赖分析**（`readelf -d`），区分硬依赖 vs 延迟加载库：

| 删除项 | 大小 | 删除依据 |
|--------|------|---------|
| `libcusolverMg.so.12` | 100 MB | DT_NEEDED 中无硬依赖，多GPU分布式线性代数专用，单卡开发不需要 |
| `libcudnn_engines_runtime_compiled.so.9` | 29 MB | cuDNN JIT 运行时编译引擎，非核心推理路径 |
| NVSHMEM IB/MPI 插件 | ~4 MB | HPC InfiniBand 集群通信插件（`nvshmem_bootstrap_mpi`, `nvshmem_transport_ibdevx` 等） |
| 小型工具库 | ~3 MB | `libnvblas.so`（NVBLAS drop-in）、`libcheckpoint.so`、`libpcsamplingutil.so` 等 |
| `torch/bin/protoc` | ~10 MB | protobuf 编译器，运行时使用 Python protobuf 库 |
| Triton CUDA 工具链 strip | ~5-10 MB | `ptxas`/`nvdisasm`/`cuobjdump` 调试符号移除 |

---

## 🛡️ 保留项说明（对抗验证结论）

瘦身后经过对抗验证（V阶段），以下组件**不可删除**：

| 组件 | 大小 | 保留原因 |
|------|------|---------|
| `torchgen/` 目录 | 2.4 MB | **运行时依赖**：`torch.utils._python_dispatch` import torchgen，删除导致 `ModuleNotFoundError` |
| `libnccl.so.2` | ~120 MB | **DT_NEEDED 硬依赖**：`libtorch_cuda.so` → `libnccl.so.2`，多卡通信必需 |
| `libcusparseLt.so.0` | ~80 MB | **DT_NEEDED 硬依赖**：稀疏矩阵运算，cuSPARSELt 被 CUDA runtime 加载 |
| `libcudnn*.so` 核心库 | ~400 MB | cuDNN 核心算子库，深度学习推理/训练必需 |
| `libcublas.so.12` / `libcublasLt.so.12` | ~300 MB | cuBLAS 基础线性代数，所有 GPU 运算必需 |
| LLVM/Clang 开发头文件 | ~64 MB | TVM/MLIR 等编译器开发需要 |
| `pandoc` | ~156 MB | Jupyter nbconvert 文档转换必需 |
| `clang-include-cleaner` | ~5 MB | clangd 包含诊断必需 |

---

## 🚀 常用命令

### 构建 slim 镜像

```bash
cd apps/docker-images/devcontainer-base

# 国内镜像源构建（推荐）
bash variants/build.sh -v torch-dev -t slim --cn

# 官方源构建
bash variants/build.sh -v torch-dev -t slim

# 完整依赖链构建（首次构建时需要）
bash build-slim-chain.sh
```

### 快速验证镜像

```bash
# CPU 模式快速验证
docker run --rm devcontainer-base:torch-dev-slim \
  /opt/conda/envs/main/bin/python -c "
import sys, torch, torchvision
print(f'torch: {torch.__version__}')
print(f'torchvision: {torchvision.__version__}')
print(f'GIL disabled: {not sys._is_gil_enabled()}')
print(f'CUDA available: {torch.cuda.is_available()}')
"

# GPU 模式验证（需要 --gpus all）
docker run --rm --gpus all devcontainer-base:torch-dev-slim \
  /opt/conda/envs/main/bin/python -c "
import torch
print(f'CUDA: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    x = torch.randn(1024, 1024, device='cuda')
    y = x @ x
    print(f'GPU matmul OK, shape={y.shape}')
"
```

### 启动容器

```bash
# CPU 模式
docker run -d --privileged \
  --name torch-dev-slim \
  -p 2222:22 -p 8888:8888 -p 2375:2375 \
  -e USER_PASSWORD=devpass -e JUPYTER_TOKEN=devtoken \
  -v $(pwd)/workspace:/workspace -w /workspace \
  -v docker-data:/var/lib/docker \
  devcontainer-base:torch-dev-slim

# GPU 模式
docker run -d --privileged --gpus all \
  --name torch-dev-slim \
  -p 2222:22 -p 8888:8888 -p 2375:2375 \
  -e USER_PASSWORD=devpass -e JUPYTER_TOKEN=devtoken \
  -v $(pwd)/workspace:/workspace -w /workspace \
  -v docker-data:/var/lib/docker \
  devcontainer-base:torch-dev-slim
```

### 验证瘦身组件删除/保留状态

```bash
docker run --rm --entrypoint bash devcontainer-base:torch-dev-slim -c "
SP=/opt/conda/envs/main/lib/python3.14t/site-packages
echo '=== Deleted items (should show YES) ==='
echo -n 'libcusolverMg.so.12: '; [ ! -f \$SP/nvidia/cu13/lib/libcusolverMg.so.12 ] && echo YES || echo NO
echo -n 'nvperf libraries:    '; [ ! -f \$SP/nvidia/cu13/lib/libnvperf_host.so ] && echo YES || echo NO
echo -n 'nvrtc.alt.so:        '; [ ! -f \$SP/nvidia/cuda_nvrtc/lib/libnvrtc.alt.so ] && echo YES || echo NO
echo -n 'triton-amd:          '; [ ! -d \$SP/triton/backends/amd ] && echo YES || echo NO
echo -n 'protoc:              '; [ ! -f \$SP/torch/bin/protoc ] && echo YES || echo NO
echo ''
echo '=== Preserved items (should show YES) ==='
echo -n 'libnccl.so.2:        '; [ -f \$SP/nvidia/nccl/lib/libnccl.so.2 ] && echo YES || echo NO
echo -n 'libcusparseLt.so.0:  '; [ -f \$SP/nvidia/cusparselt/lib/libcusparseLt.so.0 ] && echo YES || echo NO
echo -n 'torchgen/:           '; [ -d \$SP/torchgen ] && echo YES || echo NO
echo -n 'pandoc:              '; which pandoc >/dev/null 2>&1 && echo YES || echo NO
echo -n 'llvm-dev headers:    '; [ -d /opt/conda/envs/main/include/llvm ] && echo YES || echo NO
"
```

### 查看镜像瘦身元数据

```bash
docker run --rm --entrypoint cat devcontainer-base:torch-dev-slim \
  /etc/build-info.txt | grep -E 'SLIMMING|TORCH_VERSION|TORCHVISION|SIZE'
```

---

## ⚠️ 已知限制与陷阱

### 1. 不支持多GPU分布式训练（libcusolverMg 删除）

`slim` 版本删除了 `libcusolverMg.so`（100MB），这是 cuSOLVER Mg（多GPU）库。影响：

- ✅ **正常工作**: 单GPU训练、推理、数据并行（使用 NCCL）
- ❌ **不可用**: 多GPU分布式线性代数求解（需要 cusolverMg 的多节点分解）
- **需要时**: 使用 `torch-dev-latest` 完整版，或手动 `pip install nvidia-cusolvermg-cu13`

### 2. 不支持 cuDNN JIT 运行时编译

删除了 `libcudnn_engines_runtime_compiled.so.9`，影响：

- ✅ **正常工作**: 所有预编译 cuDNN 算子（conv2d、pooling、batchnorm 等）
- ❌ **不可用**: cuDNN 运行时 JIT 编译非常规算子（极少见，大多数训练场景不涉及）
- **需要时**: 使用完整版，或 `pip install nvidia-cudnn-cu13`

### 3. 不支持 NVSHMEM HPC 多节点通信

删除了 NVSHMEM InfiniBand 插件：

- ✅ **正常工作**: 单机单卡/多卡（NCCL 保留）
- ❌ **不可用**: InfiniBand 集群的 NVSHMEM 通信
- **适用场景**: 普通开发、单机训练、CI/CD 测试

### 4. 无 protoc 编译器

删除了 `torch/bin/protoc`（10MB）。影响：

- ✅ **正常工作**: PyTorch 导入、模型训练/推理、ONNX 导出（使用 Python protobuf 库）
- ❌ **不可用**: 命令行 `protoc` 编译 `.proto` 文件（需要时 `apt install protobuf-compiler` 即可，<2MB）

### 5. GIL 状态说明

```python
import sys
import torch

# 导入 torch 前检查（构建时验证）:
#   sys._is_gil_enabled() → False（真正的 free-threading）

# 导入 torchvision/triton 后检查:
#   sys._is_gil_enabled() → True（triton C扩展未声明ft-compat）
```

这是 **PyTorch/Triton 生态的已知现状**（与瘦身无关）：
- Triton C 扩展未声明 `Py_mod_gil` 兼容标记，首次加载时 CPython 自动重新启用 GIL
- PyTorch 的 CPU 算子和核心计算仍然是 free-threading 构建，可以安全使用多线程
- 纯 CPU 工作流在不触发 triton JIT 时可保持 GIL 禁用状态

### 6. 被删除的工具无法找回（层已优化）

slim 版本删除的文件已通过 Docker 层合并彻底移除，无法通过 Docker 层缓存找回。需要恢复某组件时：
- **小型工具**（如 protoc）：在容器内 `apt install` 即可
- **CUDA 库**：使用 `pip install nvidia-<package>-cu13` 安装
- **完整开发环境**：切换到 `torch-dev-latest` 标签

---

## 🎯 适用场景对比

| 场景 | 推荐标签 | 理由 |
|------|---------|------|
| CI/CD 自动化测试 | **slim** | 镜像拉取快，磁盘占用小，功能完整 |
| 本地开发（单GPU） | **slim** | 节省 2GB+ 磁盘空间，核心开发功能全保留 |
| 模型训练（单机单卡/多卡） | **slim** | NCCL 保留，数据并行不受影响 |
| ONNX 导出/量化/推理 | **slim** | 完整继承 onnx-quantized 工具链 |
| 多节点分布式训练（HPC/InfiniBand） | latest | 需要 cusolverMg 和 NVSHMEM IB 插件 |
| cuDNN JIT 非常规算子研究 | latest | 需要 runtime_compiled 引擎 |
| 调试 CUDA 内核/性能分析 | latest | 需要 nvperf 等分析库 |
| Proto 文件编译工作流 | slim + apt | protoc 可快速安装 |

---

## 🔧 瘦身技术详解

### CoW（写时复制）优化原则

Docker 的 overlay2 存储驱动采用 CoW 机制。如果在某层 `chmod -R /opt/conda`，Docker 需要复制整个 conda 目录到该层（因为权限位变了），导致层大小爆炸。

**瘦身原则**：
```dockerfile
# ❌ 错误：chmod -R 触发全量 CoW 复制（~1.2GB 膨胀）
RUN chmod -R 755 /opt/conda

# ✅ 正确：只修复实际需要的文件（精准权限修复）
RUN ensure_user_bashrc        # 只处理 ~/.bashrc
RUN ensure_profile_d_executable  # 只处理 /etc/profile.d/*.sh
```

### Strip 共享库原则

```bash
# 移除 .so 文件中未被链接器使用的符号（调试符号、未引用的静态符号）
find /opt/conda -name "*.so*" -type f -exec strip --strip-unneeded {} \; 2>/dev/null || true
```

**注意事项**：
- `--strip-unneeded` 比 `--strip-all` 安全，保留动态链接所需的符号
- 不 strip 可执行文件（某些 entrypoint 需要完整符号表）
- 在 pip install **同层**执行 strip，避免额外 CoW 层

### DT_NEEDED 依赖分析法

判断一个 `.so` 是否可以安全删除的核心方法：

```bash
# 检查 libtorch_cuda.so 的硬依赖
readelf -d /opt/conda/.../torch/lib/libtorch_cuda.so | grep NEEDED

# 输出示例:
#  NEEDED            libc10_cuda.so
#  NEEDED            libcuda.so.1
#  NEEDED            libcudart.so.12
#  NEEDED            libnccl.so.2       ← 硬依赖，不能删
#  NEEDED            libcusparseLt.so.0 ← 硬依赖，不能删
#  （注意：libcusolverMg.so.12 不在列表中 → 可安全删除）
```

**关键区别**：
- **DT_NEEDED 中的库**：动态链接器启动时必须找到，缺失立即报错 → **不能删**
- **dlopen 延迟加载库**：运行时按需加载，有 fallback 处理 → **可删（需验证）**
- **完全未引用的库**：无任何代码加载 → **安全删除**

---

## 📋 功能验证清单

构建后自动化验证（build.sh 内置 5/5 检查）：

| 检查项 | 验证内容 |
|--------|---------|
| 1. torch/torchvision 导入 | 版本号正确，无 ImportError |
| 2. free-threading 标记 | `sys._is_gil_enabled() is False`（构建时验证） |
| 3. onnxoptimizer 排除 | 确认 free-threading 不兼容包未安装 |
| 4. ONNX 量化继承 | `onnxruntime.quantization.quantize_dynamic` 可用 |
| 5. 核心算子正确性 | matmul (4,4)@(4,2) 结果正确 |

手动补充验证（推荐）：
- torch.nn 完整导入（验证 torchgen 未被误删）
- conv2d / autograd / cross_entropy / MLP forward
- GPU 模式下 CUDA 张量运算
- ONNX 导出 → 量化 → 推理全链路

---

## 🔗 相关文档

- [torch-dev README](./README.md) - 完整版使用指南（GPU配置、权限管理、示例代码）
- [onnx-quantized README](../onnx-quantized/README.md) - 基础层说明
- [cleanup.sh](../shared/lib/cleanup.sh) - 瘦身脚本源码（`cleanup_binaries` + `cleanup_torch_dev` 函数）
- [build-slim-chain.sh](../../build-slim-chain.sh) - 完整 slim 依赖链构建脚本
- [Dockerfile](./Dockerfile) - torch-dev 变体 Dockerfile 源码
