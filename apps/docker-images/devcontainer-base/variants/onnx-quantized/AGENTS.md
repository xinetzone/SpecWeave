# onnx-quantized 变体 - ONNX 量化工具链镜像 AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本目录是 devcontainer-base 变体系列的一个变体，
>         规则继承自 ../AGENTS.md（变体系列入口），后者继承自 ../../AGENTS.md（项目入口）
> 步骤 3：按上下文路由表加载变体特有规范（.agents/rules/dockerfile.md）
> 步骤 3.5：自检 — 确认已理解父级规则与本变体特有约束（尤其 base 环境架构与量化工作流约束）
> 步骤 4：在规范指导下执行任务
> ```

本文件是 onnx-quantized 变体（ONNX 模型量化工具链镜像）的 AI 协作者入口。
进入本目录的任务优先读取本文件；本文件未覆盖的规则回退到父级 [../AGENTS.md](../AGENTS.md)。

## 变体概述

| 属性 | 值 |
|------|-----|
| 变体名称 | `onnx-quantized` |
| 镜像标签 | `devcontainer-base:onnx-quantized-<TAG>`（默认 latest） |
| 基础镜像 | `devcontainer-base:onnx-pytorch-${BASE_TAG}` |
| 依赖链 | base → conda-llvm → onnx-pytorch → **onnx-quantized**（依赖链最长的变体） |
| 核心定位 | ONNX 模型量化/优化/部署工具链（动态/静态 INT8、FP16、QDQ 格式） |
| Python 环境 | conda **base 环境**（`/opt/conda/bin`，Python 3.14.6 普通版，GIL 启用） |
| 继承自带 | PyTorch 2.13.0+cpu、torchvision 0.28.0+cpu、onnx、onnxruntime、onnxsim、onnxscript（来自 onnx-pytorch 层） |
| 本层新增 | onnxconverter-common（FP16 转换）、onnxsim 升级、onnxruntime.quantization 原生 API 激活 |
| 可选扩展 | neural-compressor（Intel，**不预装**，见设计决策） |

## 三条核心约束（改动本变体前必读）

### 1. base 环境架构（与 onnx-dev 变体相反）

- 所有工具位于 conda **base 环境**（`/opt/conda/bin`），`ENV PATH=/opt/conda/bin:...` 置于最前
- Python 3.14.6 **普通版**（GIL 启用）——本变体**不是** free-threading 构建
- 验证命令使用 `/opt/conda/bin/python`（注意区别于 onnx-dev 的 `/opt/conda/envs/main/bin/python`）

### 2. PyTorch 是量化工作流的必需依赖（一等保留）

- 量化校准数据生成、模型导出（`torch.onnx.export` 依赖 onnxscript）均需 PyTorch
- torch/torchvision 以 CPU 版预装（无 CUDA 依赖），**不做缺席负向验证**（与 onnx-dev 相反）
- 版本升级须保持 `+cpu` 后缀（使用 PyTorch CPU index 安装）

### 3. onnxruntime.quantization 是量化主 API

- 动态/静态量化、QDQ 格式、校准全部走 `onnxruntime.quantization` 原生 API
- **neural-compressor 不预装**：其 3.x 已弃用 ONNX 适配器（转向 PyTorch weight-only），作为可选扩展由用户按需 `pip install neural-compressor`
- 量化前模型必须先过 onnxsim 精简（形状推理兼容修复，量化工具链对动态形状敏感）

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则）
  └─ apps/AGENTS.md（应用区入口）
       └─ devcontainer-base/AGENTS.md（项目路由入口）
            └─ variants/AGENTS.md（变体系列入口）
                 └─ onnx-quantized/AGENTS.md ← 本文件（变体级入口）
                      ├─ .agents/rules/dockerfile.md        ← 本变体特有 Dockerfile 规范
                      ├─ Dockerfile                         ← 3 追加阶段构建定义
                      ├─ .env.example                      ← 构建参数模板（含 TORCH_INDEX_URL）
                      ├─ README.md                         ← 发布说明（v1.0.0，25 项验证）
                      ├─ ADVANCED-QUANTIZATION-GUIDE.md    ← 高级量化指南（静态量化/校准/QDQ）
                      └─ QUANTIZATION-BEST-PRACTICES.md    ← 量化最佳实践
```

## 上下文路由表

| 任务类型 | 必读入口 | 说明 |
|---------|---------|------|
| 修改本变体 Dockerfile | [.agents/rules/dockerfile.md](.agents/rules/dockerfile.md) | 基础信息、PATH 优先级、量化包安装、OMP 线程调优、3 阶段结构 |
| 量化操作实践（何时用动态/静态/FP16） | [QUANTIZATION-BEST-PRACTICES.md](QUANTIZATION-BEST-PRACTICES.md) | 量化选型决策、精度-性能权衡、常见陷阱 |
| 高级量化（校准数据集/QDQ/静态 INT8） | [ADVANCED-QUANTIZATION-GUIDE.md](ADVANCED-QUANTIZATION-GUIDE.md) | 静态量化全流程、CalibrationDataReader 编写、QDQ 格式 |
| 变体共享约定（FROM/SHELL/缓存挂载/验证检查点） | [../.agents/rules/variant-conventions.md](../.agents/rules/variant-conventions.md) | 所有变体必须遵循的 Dockerfile 共享约定 |
| 构建本变体 | [../build.sh](../build.sh) + [../.agents/rules/build-orchestration.md](../.agents/rules/build-orchestration.md) | `--variant onnx-quantized`（拓扑排序自动补齐 onnx-pytorch/conda-llvm 依赖） |
| 测试本变体 | [../scripts/test-onnx-quantized.sh](../scripts/test-onnx-quantized.sh) | 25 项测试（包导入/量化/精度对比/服务） |
| 测试规范（L1-L6 六层策略） | [../.agents/rules/testing.md](../.agents/rules/testing.md) | 测试脚本编写规范 |
| 参考上游变体 | [../onnx-pytorch/README.md](../onnx-pytorch/README.md) | PyTorch 安装细节、base 环境架构来源 |
| 对比姊妹变体（纯 ONNX，无 PyTorch） | [../onnx-dev/AGENTS.md](../onnx-dev/AGENTS.md) | main 环境 + free-threading + torch 一等排除（架构正交） |
| 父级回退（变体系列通用规则） | [../AGENTS.md](../AGENTS.md) | 本文件未覆盖时回退 |

## 构建与验证速查

```bash
# 构建（WSL2/Linux，国内镜像源；拓扑排序自动先建 onnx-pytorch/conda-llvm）
bash variants/build.sh --variant onnx-quantized --cn

# 测试已有镜像（25 项：包导入9/量化流程/精度对比/服务5）
bash variants/scripts/test-onnx-quantized.sh --tag latest

# 快速验证量化能力（动态 INT8）
docker run --rm devcontainer-base:onnx-quantized-latest \
  /opt/conda/bin/python -c "from onnxruntime.quantization import quantize_dynamic, QuantType; print('quantize OK')"
```

## 已知设计决策记录

| 决策 | 理由 |
|------|------|
| neural-compressor 不预装 | 其 3.x 已弃用 ONNX 适配器（转向 PyTorch weight-only 量化），作为可选扩展避免拖累镜像体积；ONNX 量化用 onnxruntime 原生 API 完全覆盖 |
| 基于 onnx-pytorch 而非 conda-llvm | 量化校准与模型导出依赖 PyTorch（torch.onnx.export）；依赖链最长但功能最全 |
| OMP_NUM_THREADS=4 + OPENBLAS_NUM_THREADS=1 | 防止量化推理时线程过度订阅（over-subscription）导致性能劣化 |
| 量化前强制 onnxsim 精简 | 量化工具链对动态形状/冗余节点敏感，形状推理兼容修复是量化成功的先决条件 |
| Python 为普通 GIL 版（非 free-threading） | 继承 onnx-pytorch 的 base 环境；量化库生态对 cp314t 支持不完整（参照 onnx-dev 的 onnxoptimizer 教训） |
| 动态 INT8 精度基准 max_diff < 0.21% | v1.0.0 验证记录（Linear 层 10→5，FP32 vs INT8），作为后续升级的回归基线 |
