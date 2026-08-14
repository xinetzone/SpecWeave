# onnx-quantized 变体 - ONNX 量化工具链镜像 AI协作者入口 (AGENTS Manifest)

> **启动协议（PRIORITY ZERO — 所有智能体必须遵循）**
>
> ```
> 步骤 1：读取本文件全文
> 步骤 2：确认父级工作区 — 本目录是 devcontainer-base 变体系列的一个变体，
>         规则继承自 ../AGENTS.md（变体系列入口），后者继承自 ../../AGENTS.md（项目入口）
> 步骤 3：按上下文路由表加载变体特有规范（.agents/rules/dockerfile.md）
> 步骤 3.5：自检 — 确认已理解父级规则与本变体特有约束（尤其 main 环境架构、free-threading 与纯 ONNX 约束）
> 步骤 4：在规范指导下执行任务
> ```

本文件是 onnx-quantized 变体（ONNX 模型量化工具链镜像）的 AI 协作者入口。
进入本目录的任务优先读取本文件；本文件未覆盖的规则回退到父级 [../AGENTS.md](../AGENTS.md)。

## 变体概述

| 属性 | 值 |
|------|-----|
| 变体名称 | `onnx-quantized` |
| 镜像标签 | `devcontainer-base:onnx-quantized-<TAG>`（默认 latest） |
| 基础镜像 | `devcontainer-base:onnx-dev-${BASE_TAG}` |
| 依赖链 | base → conda-llvm → onnx-dev → **onnx-quantized** |
| 核心定位 | ONNX 模型量化/优化/部署工具链（动态/静态 INT8、FP16、QDQ 格式，**纯 ONNX 无 PyTorch**） |
| Python 环境 | conda **main 环境**（`/opt/conda/envs/main/bin`，Python 3.14.6 cp314t **free-threading**，GIL 禁用） |
| 继承自带 | onnx、onnxruntime（含 quantization 子模块）、onnxsim、onnxscript（来自 onnx-dev 层） |
| 本层新增 | onnxconverter-common（FP16 转换）、onnxsim（幂等补装）、onnxruntime.quantization 原生 API 激活 |
| 可选扩展 | neural-compressor（Intel，**不预装**，需 PyTorch，见设计决策） |

## 三条核心约束（改动本变体前必读）

### 1. main 环境架构（继承 onnx-dev，与 onnx-pytorch 变体相反）

- 所有量化工具位于 conda **main 环境**（`/opt/conda/envs/main/bin`），`ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:...` 置于最前
- Python 3.14.6 **cp314t free-threading 构建**（GIL 禁用）——`sys._is_gil_enabled() is False` 必须恒成立
- 验证命令使用 `/opt/conda/envs/main/bin/python`（注意区别于 onnx-pytorch 的 `/opt/conda/bin/python`）
- 构建期双守卫：pip 安装后断言 python 构建串含 `cp314t` 且 GIL 仍禁用，否则 FATAL

### 2. PyTorch 一等排除（负向验证，继承 onnx-dev）

- **本镜像无 torch/torchvision**：量化测试模型一律用 `onnx.helper` 纯 ONNX API 构建（Gemm/Relu/Mul/Add 节点），禁止 `torch.onnx.export`
- 构建期守卫断言 `find_spec('torch') is None`，若依赖回拉 torch 则 FATAL
- `onnxoptimizer` 同为排除项（free-threading 不兼容，CPython #111506），同样有缺席断言
- neural-compressor 不预装（3.x 为 PyTorch-only，需 torch）；用户需要时 `pip install neural-compressor torch` 按需自装

### 3. onnxruntime.quantization 是量化主 API

- 动态/静态量化、QDQ 格式、校准全部走 `onnxruntime.quantization` 原生 API
- 量化前模型必须先过 onnxsim 精简（形状推理兼容修复，量化工具链对动态形状敏感）
- 冒烟测试使用固定种子（`np.random.default_rng(42)`）保证确定性，模型权重按 Xavier 风格缩放（`1/sqrt(fan_in)`）保证精度断言稳定

## 嵌套路由关系

```
SpecWeave 根 AGENTS.md（全局规则）
  └─ apps/AGENTS.md（应用区入口）
       └─ devcontainer-base/AGENTS.md（项目路由入口）
            └─ variants/AGENTS.md（变体系列入口）
                 └─ onnx-quantized/AGENTS.md ← 本文件（变体级入口）
                      ├─ .agents/rules/dockerfile.md        ← 本变体特有 Dockerfile 规范
                      ├─ Dockerfile                         ← 3 追加阶段构建定义
                      ├─ .env.example                      ← 构建参数模板
                      ├─ README.md                         ← 发布说明
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
| 构建本变体 | [../build.sh](../build.sh) + [../.agents/rules/build-orchestration.md](../.agents/rules/build-orchestration.md) | `--variant onnx-quantized`（拓扑排序自动补齐 onnx-dev/conda-llvm 依赖） |
| 测试本变体 | [../scripts/test-onnx-quantized.sh](../scripts/test-onnx-quantized.sh) | 24 项测试（free-threading/包导入/纯 ONNX 量化/服务） |
| 测试规范（L1-L7 分层策略） | [../.agents/rules/testing.md](../.agents/rules/testing.md) | 测试脚本编写规范 |
| 参考基础变体 | [../onnx-dev/AGENTS.md](../onnx-dev/AGENTS.md) | main 环境 + free-threading + torch 一等排除的架构来源 |
| 对比姊妹变体（含 PyTorch） | [../onnx-pytorch/README.md](../onnx-pytorch/README.md) | base 环境架构、PyTorch 安装细节（架构正交） |
| 父级回退（变体系列通用规则） | [../AGENTS.md](../AGENTS.md) | 本文件未覆盖时回退 |

## 构建与验证速查

```bash
# 构建（WSL2/Linux，国内镜像源；拓扑排序自动先建 onnx-dev/conda-llvm）
bash variants/build.sh --variant onnx-quantized --cn

# 测试已有镜像（24 项：free-threading/torch缺席/包导入/纯ONNX量化/服务）
bash variants/scripts/test-onnx-quantized.sh --tag latest

# 快速验证量化能力（动态 INT8）
docker run --rm devcontainer-base:onnx-quantized-latest \
  /opt/conda/envs/main/bin/python -c "from onnxruntime.quantization import quantize_dynamic, QuantType; print('quantize OK')"
```

## 已知设计决策记录

| 决策 | 理由 |
|------|------|
| 基于 onnx-dev 而非 onnx-pytorch | 继承 free-threading main 环境与纯 ONNX 生态；量化测试模型用 `onnx.helper` 纯构建，无需 PyTorch |
| neural-compressor 不预装 | 其 3.x 已弃用 ONNX 适配器（转向 PyTorch weight-only 量化），且需 torch；ONNX 量化用 onnxruntime 原生 API 完全覆盖 |
| torch/onnxoptimizer 负向验证 | 守卫依赖回拉；onnxoptimizer 与 free-threading 不兼容（CPython #111506） |
| 冒烟测试纯 ONNX 化（onnx.helper 构建 Gemm/Relu 模型） | 镜像无 torch；Gemm 等价 nn.Linear，Xavier 缩放权重保证量化精度断言稳定 |
| OMP_NUM_THREADS=4 + OPENBLAS_NUM_THREADS=1 | 防止量化推理时线程过度订阅（over-subscription）导致性能劣化 |
| 量化前强制 onnxsim 精简 | 量化工具链对动态形状/冗余节点敏感，形状推理兼容修复是量化成功的先决条件 |
| Python 为 free-threading cp314t | 继承 onnx-dev 的 main 环境；量化链（onnxruntime.quantization/onnxconverter-common/onnxsim）均兼容 |
