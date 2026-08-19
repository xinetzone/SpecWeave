# Docker镜像瘦身最佳实践指南

> **版本**：v1.0 | **日期**：2026-08-19 | **成熟度**：L2-validated（实战验证）
>
> 基于 `devcontainer-base` 项目 `torch-dev-slim` 镜像瘦身实战（10.2GB→8.15GB/-20%），总结出可复用的Docker镜像瘦身方法论、核心技术和架构模式。

---

## 目录

- [效果速览](#效果速览)
- [适用范围](#适用范围)
- [核心原理：理解COW膨胀](#核心原理理解cow膨胀)
- [Part 1：基础瘦身（通用所有镜像）](#part-1基础瘦身通用所有镜像)
- [Part 2：GPU/ML镜像瘦身四步法](#part-2gpuml镜像瘦身四步法)
  - [Step 1：分析定位](#step-1分析定位)
  - [Step 2：R1基础瘦身](#step-2r1基础瘦身)
  - [Step 3：R2深度瘦身（DT_NEEDED分析法）](#step-3r2深度瘦身dt_needed分析法)
  - [Step 4：验证交付](#step-4验证交付)
  - [Dockerfile集成模板](#dockerfile集成模板)
- [Part 3：多变体框架化架构](#part-3多变体框架化架构)
- [反模式汇总（踩坑手册）](#反模式汇总踩坑手册)
- [实战案例](#实战案例)
- [快速参考卡](#快速参考卡)
- [参考资料](#参考资料)

---

## 效果速览

| 镜像 | 瘦身前 | 瘦身后 | 减少 | 关键手段 |
|------|--------|--------|------|---------|
| `torch-dev-slim` | 10.2GB | 8.15GB | **-2.05GB (-20%)** | R1基础瘦身+R2 DT_NEEDED分析+CoW层序优化 |
| 其中R1贡献 | - | - | ~-1.9GB | strip(~508MB)+nvrtc.alt/nvperf/nvshmem/triton-amd(~180MB)+CoW优化(避免+2GB膨胀) |
| 其中R2贡献 | - | - | ~-150MB | cusolverMg(100MB)+cudnn-jit(29MB)+nvshmem插件+protoc+triton-bin |

> 💡 **5分钟快速上手**：如果你是第一次做Docker瘦身，先看 [DOCKER-SLIMMING-QUICKSTART.md](DOCKER-SLIMMING-QUICKSTART.md) 快速入门，遇到具体问题再回来查阅本指南。

## 适用范围

**✅ 适用**：
- 包含PyTorch/TensorFlow/CUDA/cuDNN等GPU/ML框架的Docker镜像（>8GB）
- 基于conda/pip安装大量二进制包的开发/CI镜像
- 有2个及以上变体（variant）的Docker项目
- 需要系统性瘦身但不确定哪些文件可安全删除

**❌ 不适用**：
- distroless/scratch极简运行时镜像（已无冗余）
- 生产运行时镜像（通常已精简至<3GB，功能完整性要求极高）
- 单阶段、<50行的简单Dockerfile（收益不值得复杂度）

---

## 核心原理：理解COW膨胀

Docker镜像使用OverlayFS联合挂载，每个`RUN`指令产生一个新层。这是镜像"越瘦越胖"反直觉现象的根源：

> **Copy-on-Write（COW）机制**：对低层已有文件的任何内容修改（写入/截断/**属性变更**如chmod/chown）都会在当前层创建该文件的完整副本，原文件保留在低层。

**典型反直觉案例**：
```
Stage 4创建Python二进制：35MB
Stage 7（上层）strip后：5.8MB
净结果：+5.8MB（而非-29MB！）
原因：Stage 4的35MB + Stage 7的5.8MB = 40.8MB（两层叠加）
```

**只有whiteout删除（`rm -rf`产生`.wh.`标记）不复制文件数据，安全且不增加体积。**

这一原理决定了所有瘦身操作必须遵守一条铁律：

> ⚠️ **P7同层修改原则**：所有strip/rm/chmod等修改操作必须与文件创建在同一个`RUN`层完成，禁止跨层修改。

---

## Part 1：基础瘦身（通用所有镜像）

适用于所有Docker镜像的基础清理，预期收益：**-300MB~1GB**。

### 1.1 缓存清理（必做）

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends <packages> && \
    rm -rf /var/lib/apt/lists/*    # apt缓存

RUN pip install --no-cache-dir <packages>   # 或用BuildKit缓存挂载：
# RUN --mount=type=cache,target=/root/.cache/pip pip install <packages>

RUN conda install <packages> && \
    conda clean -afy    # conda包缓存+索引缓存
```

### 1.2 冗余文件清理

```bash
# 删除静态库（运行时不需要）
find /opt/conda -name "*.a" -not -path "*/gcc/*" -not -path "*/sysroot/*" -delete 2>/dev/null || true

# 删除bitcode（编译时用，运行时不需要）
find /opt/conda -name "*.bc" -delete 2>/dev/null || true

# 删除man/doc文档
rm -rf /usr/share/man /usr/share/doc /usr/share/info

# 删除__pycache__（验证后执行，见Step 4）
find /opt/conda -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /opt/conda -name "*.pyc" -delete 2>/dev/null || true
```

### 1.3 共享库strip（注意安全范围）

```bash
# ✅ 安全：普通C扩展共享库
find /opt/conda/envs/main/lib -name "*.so*" -type f \
  -exec strip --strip-unneeded {} \; 2>/dev/null || true

# ⚠️ 谨慎：CUDA核心库不要strip（可能影响kernel JIT）
# ❌ 不要：find /opt/conda -path "*/nvidia/*" -name "*.so" -exec strip --strip-all {} \;

# ✅ 安全：Triton工具链二进制
find /opt/conda/envs/main/lib/python*/site-packages/triton/backends/nvidia/bin \
  -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
```

**strip参数选择**：
- `--strip-unneeded`：移除未引用的符号，保留动态符号表（**推荐**）
- `--strip-all`：移除所有符号包括.dynamic段，会导致dlopen失败（**禁止用于.so**）

### 1.4 权限修复：精准替代chmod -R

```dockerfile
# ❌ 错误：chmod -R触发全量COW复制（可能+2GB）
RUN chmod -R 755 /opt/conda

# ✅ 正确：精准权限修复，只修改需要修改的文件
RUN touch /home/devuser/.bashrc && chown devuser:devuser /home/devuser/.bashrc && \
    find /etc/profile.d -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
```

### 1.5 COPY权限设置

```dockerfile
# ❌ 错误：额外RUN层chmod（COW膨胀）
COPY scripts/analyze.sh /usr/local/bin/analyze.sh
RUN chmod +x /usr/local/bin/analyze.sh

# ✅ 正确：COPY时设置权限（零额外层）
COPY --chmod=755 scripts/analyze.sh /usr/local/bin/analyze.sh
```

---

## Part 2：GPU/ML镜像瘦身四步法

对于包含CUDA/PyTorch等大框架的GPU/ML镜像，需要更系统化的方法。核心流程：

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Step 1     │    │  Step 2     │    │  Step 3     │    │  Step 4     │
│ 分析定位    │───▶│ R1基础瘦身  │───▶│ R2深度瘦身  │───▶│ 验证交付    │
│ (du+history)│    │ (确定项)    │    │ (DT_NEEDED) │    │ (7项清单)   │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │                  │
       ▼                  ▼                  ▼                  ▼
   输出：体积分布    输出：-1.5~2GB    输出：-100~200MB   输出：可交付镜像
```

### Step 1：分析定位（先量后减）

**目标**：精准定位体积来源，避免盲目删除。

#### 镜像层分析

```bash
# 查看各层大小，定位异常大层
docker history <image> --format "{{.Size}}\t{{.CreatedBy}}" | head -20
```

关注：
- 安装pip/conda包的层（通常最大）
- 清理/权限修复层（正常应<1MB，>100MB说明COW膨胀）
- `chmod -R`/`chown -R`出现的层（COW膨胀信号）

#### 目录体积分布

```bash
docker run --rm <image> bash -c "
  du -sh /opt/conda/envs/main/lib/python*/site-packages/torch 2>/dev/null
  du -sh /opt/conda/envs/main/lib/python*/site-packages/nvidia 2>/dev/null
  du -sh /opt/conda/envs/main/lib/python*/site-packages/triton 2>/dev/null
  du -sh /opt/conda/pkgs 2>/dev/null
  du -sh /opt/conda/envs/main/lib 2>/dev/null
"
```

#### 细粒度扫描大库

```bash
# 列出site-packages/nvidia下所有>20MB的.so文件
docker run --rm <image> bash -c "
  SP=\$(python -c 'import site; print(site.getsitepackages()[0])')
  find \$SP/nvidia -name '*.so*' -size +20M -exec du -sh {} \; | sort -rh
"
```

**典型输出**：
```
224M  .../nvidia/cusparse/lib/libcusparseLt.so.0     ← 🔴 硬依赖，保留
186M  .../nvidia/nccl/lib/libnccl.so.2               ← 🔴 硬依赖，保留
109M  .../nvidia/cu13/lib/libnvrtc.alt.so.13         ← 🟢 R1可删
100M  .../nvidia/cu13/lib/libcusolverMg.so.12        ← 🟡 R2可删（需验证）
 60M  .../nvidia/cu13/lib/libnvperf_host.so          ← 🟢 R1可删
 38M  .../nvidia/nvshmem/lib/libnvshmem_host.so.3    ← 🔴 硬依赖，保留
 29M  .../nvidia/cudnn/lib/libcudnn_engines_runtime_compiled.so.9  ← 🟡 R2可删
```

---

### Step 2：R1基础瘦身（确定项，-1.5~2GB）

**原则**：只删除高确定性冗余项（跨平台后端、性能分析工具、备用库、设备端编译产物）。

#### R1标准删除清单

| 删除项 | 典型大小 | 为什么可删 |
|--------|---------|-----------|
| `nvidia/cu13/lib/libnvrtc.alt.so*` | ~110MB | NVRTC备用构建，标准libnvrtc.so已满足 |
| `nvidia/cu13/lib/libnvperf_*` | ~60MB | Nsight Compute性能分析库，运行时不链接 |
| `nvidia/nvshmem/lib/libnvshmem_device.bc` | ~25MB | 设备端bitcode，编译时用，运行时不需要 |
| `nvidia/nvshmem/lib/libnvshmem_device.a` | ~8MB | NVSHMEM静态库，运行时不需要 |
| `triton/backends/amd/` | ~3-5MB | AMD GPU后端，N卡镜像不需要 |
| 静态库`.a`（非编译器必需） | ~50MB | 排除gcc/sysroot/libnpymath后删除 |

#### R1必须在pip install同层执行

```dockerfile
# ✅ 正确：同层完成安装+strip+清理+权限修复
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cu130 && \
    cleanup_binaries && \           # strip共享库+删除静态库
    cleanup_torch_dev && \          # R1+R2 CUDA冗余库清理
    ensure_user_bashrc && \         # 精准权限修复
    ensure_profile_d_executable     # 精准权限修复
```

参考实现：[cleanup.sh](../variants/shared/lib/cleanup.sh) 的 `cleanup_binaries()` 和 `cleanup_torch_dev()` R1部分。

---

### Step 3：R2深度瘦身（DT_NEEDED分析法）

**原则**：基于动态链接依赖分析，区分硬依赖与延迟加载库，只删除验证安全的项。预期收益：**-100~200MB**。

#### DT_NEEDED分析法原理

ELF共享库通过`.dynamic`段的`DT_NEEDED`条目声明硬依赖。`readelf -d`可以列出这些硬依赖：

```bash
readelf -d <core_library.so> | grep NEEDED
```

共享库的"引用"有三种语义：

| 类别 | DT_NEEDED | dlopen引用 | 可删除性 |
|------|-----------|-----------|---------|
| **硬依赖** | ✅ 出现 | 可能也有 | ❌ 不可删除（启动即失败） |
| **延迟加载** | ❌ 不出现 | ✅ 特定路径 | ⚠️ 条件删除（验证后决定） |
| **未引用** | ❌ 不出现 | ❌ 无引用 | ✅ 可安全删除 |

#### 操作步骤

```bash
# 1. 找到核心ELF文件
SP=$(python -c 'import site; print(site.getsitepackages()[0])')
CORE_LIBS=$(find $SP/torch/lib -name "libtorch_cuda*.so" -o -name "libtorch_python*.so" 2>/dev/null)

# 2. 提取所有DT_NEEDED硬依赖列表，去重
for lib in $CORE_LIBS; do
    readelf -d "$lib" 2>/dev/null | grep NEEDED | awk '{print $5}' | tr -d '[]'
done | sort -u > /tmp/hard_deps.txt

echo "=== 硬依赖库（必须保留）==="
cat /tmp/hard_deps.txt
```

#### 三层分类决策

对每个>20MB的.so文件：

```
文件大小 > 20MB?
├─ 否 → 跳过（节省不值得风险）
└─ 是 → readelf检查核心库DT_NEEDED
   ├─ 在DT_NEEDED中 → 🔴 硬依赖，保留
   └─ 不在DT_NEEDED中 → strings搜索dlopen引用
      ├─ 无任何引用 → 🟢 安全删除
      └─ 有dlopen引用 → 功能验证后决定
         ├─ 验证通过（删除后功能正常）→ 🟡 条件删除（记录已知限制）
         └─ 验证失败 → 🔴 保留
```

#### 判定规则脚本

```bash
CANDIDATE="libcusolverMg.so.12"

if grep -q "$CANDIDATE" /tmp/hard_deps.txt; then
    echo "[$CANDIDATE] HARD DEPENDENCY - KEEP"
elif strings $SP/torch/lib/libtorch_cuda.so 2>/dev/null | grep -q "$CANDIDATE"; then
    echo "[$CANDIDATE] DLOPEN-Loaded - CHECK FALLBACK"
    # 进一步检查：dlopen失败时是否有fallback
else
    echo "[$CANDIDATE] UNREFERENCED - SAFE TO DELETE"
fi
```

#### R2标准删除清单（已验证）

| 删除项 | 大小 | DT_NEEDED | 验证结果 |
|--------|------|-----------|---------|
| `nvidia/cu13/lib/libcusolverMg.so.12` | 100MB | ❌ 不在 | ✅ 单卡场景安全（多GPU分布式专用） |
| `nvidia/cudnn/lib/libcudnn_engines_runtime_compiled.so.9` | 29MB | ❌ 不在 | ✅ JIT引擎（precompiled覆盖标准shape） |
| `nvidia/nvshmem/lib/nvshmem_bootstrap_mpi.so*` | ~1MB | ❌ 不在 | ✅ MPI集群bootstrap（WSL2不用） |
| `nvidia/nvshmem/lib/nvshmem_transport_ib*.so*` | ~3MB | ❌ 不在 | ✅ InfiniBand传输（消费级GPU不用） |
| `nvidia/cu13/lib/libnvblas.so.13` | <1MB | ❌ 不在 | ✅ NVBLAS drop-in替换（不用） |
| `torch/bin/protoc*` | ~10MB | N/A | ✅ protobuf编译器（运行时用Python库） |

#### R2禁止删除清单（硬依赖）

| 保留项 | 大小 | 原因 |
|--------|------|------|
| `nvidia/cusparse/lib/libcusparseLt.so.0` | 224MB | DT_NEEDED硬依赖，libtorch_cuda.so直接链接 |
| `nvidia/nccl/lib/libnccl.so.2` | 186MB | DT_NEEDED硬依赖，分布式通信必需 |
| `nvidia/nvshmem/lib/libnvshmem_host.so.3` | 38MB | DT_NEEDED硬依赖 |
| `torchgen/`目录 | 2.4MB | `torch.utils._python_dispatch`运行时import |
| `nvidia/cublas/lib/libcublasLt.so*` | ~400MB | cuBLAS核心库 |
| `nvidia/cudnn/lib/libcudnn_engines_precompiled.so*` | ~235MB | cuDNN预编译引擎 |
| `nvidia/cu13/lib/libnvrtc.so*`（非.alt） | ~40MB | NVRTC标准版本，Triton编译kernel必需 |

> ⚠️ **torchgen/陷阱**：虽然名字含"gen"看似代码生成工具，但`torch.utils._python_dispatch`运行时`import torchgen`。**不要仅凭文件名判断用途！**

#### 使用框架脚本

参考实现 [r2-dtneeded-analysis.sh](../variants/shared/scripts/r2-dtneeded-analysis.sh) 支持4种模式：

```bash
bash r2-dtneeded-analysis.sh --analyze   # 仅分析，输出DT_NEEDED报告
bash r2-dtneeded-analysis.sh --delete    # 执行安全删除
bash r2-dtneeded-analysis.sh --verify    # 验证功能正常
bash r2-dtneeded-analysis.sh --all       # 一键全流程（analyze→delete→verify）
```

---

### Step 4：验证交付（7项清单）

每轮瘦身（R1和R2）后，必须执行以下全部验证：

```bash
#!/bin/bash
set -e

echo "=== [1/7] 核心模块导入 ==="
python -c "import torch; import torchvision; print(f'torch={torch.__version__}, cuda={torch.cuda.is_available()}')"

echo "=== [2/7] CUDA基础算子（matmul） ==="
python -c "
import torch
x = torch.randn(256, 256, device='cuda')
y = torch.matmul(x, x)
assert y.shape == (256, 256)
print(f'matmul OK, device={y.device}')
"

echo "=== [3/7] 卷积+自动微分 ==="
python -c "
import torch, torch.nn.functional as F
x = torch.randn(1, 3, 32, 32, device='cuda', requires_grad=True)
w = torch.randn(16, 3, 3, 3, device='cuda', requires_grad=True)
y = F.conv2d(x, w); y.sum().backward()
assert x.grad is not None and w.grad is not None
print('conv2d+autograd OK')
"

echo "=== [4/7] MLP+CrossEntropy（触发cuDNN） ==="
python -c "
import torch, torch.nn as nn
model = nn.Sequential(nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 10)).cuda()
x = torch.randn(32, 128, device='cuda')
y = model(x)
loss = nn.CrossEntropyLoss()(y, torch.randint(0, 10, (32,), device='cuda'))
loss.backward()
print(f'MLP OK, loss={loss.item():.4f}')
"

echo "=== [5/7] 删除项确认（不应存在） ==="
SP=$(python -c 'import site; print(site.getsitepackages()[0])')
for f in "nvidia/cu13/lib/libnvrtc.alt.so.13" "nvidia/cu13/lib/libnvperf_host.so" \
         "nvidia/cu13/lib/libcusolverMg.so.12" "triton/backends/amd"; do
  [ -e "$SP/$f" ] && { echo "FAIL: $f still exists!"; exit 1; }
done
echo "Deleted items verified absent"

echo "=== [6/7] 保留项确认（必须存在） ==="
for f in "nvidia/cusparse/lib/libcusparseLt.so.0" "nvidia/nccl/lib/libnccl.so.2" \
         "torchgen/__init__.py"; do
  [ ! -e "$SP/$f" ] && { echo "FAIL: $f missing!"; exit 1; }
done
echo "Preserved items verified present"

echo "=== [7/7] devuser权限验证 ==="
su - devuser -c "python -c 'import torch; print(torch.cuda.is_available())'"

echo "All validations PASSED ✓"
```

> ⚠️ **顺序铁律**：安装 → 清理R1/R2 → 验证 → `cleanup_post_tests`（清理pycache）。验证在清理之后、pycache清理之前，顺序不可颠倒。

---

### Dockerfile集成模板

以下是GPU/ML变体Dockerfile中瘦身调用的标准模板（使用框架化函数）：

```dockerfile
# ══════════════════════════════════════════════════════════════
# S1：基础安装层（从base镜像继承 + 变体专属安装）
# ══════════════════════════════════════════════════════════════
FROM devcontainer-base:latest AS S1
# ... pip/conda install 变体专属包 ...

# ══════════════════════════════════════════════════════════════
# S2：清理瘦身层（同层执行，调用框架函数）
# ══════════════════════════════════════════════════════════════
FROM S1 AS S2

# 1. 复制框架脚本（COPY --chmod避免额外RUN层）
COPY shared/lib/cleanup.sh /usr/local/share/variant-framework/cleanup.sh
COPY shared/lib/verify.sh /usr/local/share/variant-framework/verify.sh
COPY --chmod=755 shared/scripts/r2-dtneeded-analysis.sh \
    /usr/local/share/variant-framework/r2-dtneeded-analysis.sh

# 2. 同层执行：source框架 + 安装 + 清理 + 精准权限
RUN . /usr/local/share/variant-framework/cleanup.sh && \
    . /usr/local/share/variant-framework/verify.sh && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu130 && \
    cleanup_binaries && \
    cleanup_torch_dev && \
    ensure_user_bashrc && \
    ensure_profile_d_executable

# ══════════════════════════════════════════════════════════════
# S3：框架级验证层（验证后清理pycache）
# ══════════════════════════════════════════════════════════════
RUN . /usr/local/share/variant-framework/cleanup.sh && \
    . /usr/local/share/variant-framework/verify.sh && \
    verify_all_slim_gpu && \
    cleanup_post_tests
```

完整示例：[torch-dev/Dockerfile](../variants/torch-dev/Dockerfile)

---

## Part 3：多变体框架化架构

当Docker项目超过2个变体时，应将共性逻辑提取到共享框架中，消除代码重复和调用遗漏。

### 为什么要框架化

多变体Docker项目的典型退化路径：
1. 单Dockerfile → 没问题
2. 新增变体，复制Dockerfile → **代码重复**
3. 修复bug只改了一个变体 → **一致性问题**
4. 新增清理函数，每个变体都要COPY+调用 → **调用遗漏**（如忘记调用`cleanup_binaries`导致10.2GB大镜像）
5. 脚本权限用`RUN chmod +x` → **CoW膨胀**

### 三层目录结构

```
variants/
├── shared/                    # 框架层（所有变体共享）
│   ├── lib/                   # L1: bash函数库（source引入）
│   │   ├── cleanup.sh         #   清理函数：cleanup_binaries/cleanup_torch_dev/cleanup_post_tests
│   │   └── verify.sh          #   验证函数：verify_all_slim_gpu/verify_slim_delete_preserve
│   ├── scripts/               # L2: 可执行脚本（COPY --chmod=755）
│   │   └── r2-dtneeded-analysis.sh  # R2 DT_NEEDED分析脚本（--analyze/--delete/--verify/--all）
│   └── config/                # L3: 配置文件（包列表/环境变量/版本约束）
│       └── conda-env.yml      #   （可选）
├── onnx-quantized/Dockerfile  # 变体层：只声明变体特性+调用框架
├── torch-dev/Dockerfile       # 变体层：只声明变体特性+调用框架
└── conda-llvm/Dockerfile      # 变体层：只声明变体特性+调用框架
```

### 函数库设计原则

| 原则 | 做法 | 理由 |
|------|------|------|
| **分层设计** | 通用函数（cleanup_binaries）+ 专项函数（cleanup_torch_dev）+ 后处理（cleanup_post_tests） | 通用函数覆盖80%场景，专项函数处理20%变体差异 |
| **安全跳过** | verify函数检测前置条件，不适用时SKIP返回0（非FAIL） | 变体Dockerfile可无条件调用，无需if-else守卫 |
| **COPY权限** | `COPY --chmod=755`而非`RUN chmod +x` | 避免额外RUN层导致CoW膨胀 |
| **自描述命名** | `cleanup_<scope>`/`verify_<scope>` | Dockerfile读起来像文档 |
| **快速失败** | 验证失败`{ echo "[FAIL]"; exit 1; }` | build-time立即失败，不生成问题镜像 |

### 验证函数安全设计示例

```bash
# shared/lib/verify.sh
verify_all_slim_gpu() {
    echo "=== GPU/ML Slim Validation ==="

    # 安全检查：torch未安装时自动跳过（非GPU变体安全）
    if ! /opt/conda/envs/main/bin/python -c "import torch" 2>/dev/null; then
        echo "  [SKIP] torch not installed - skipping GPU validation"
        return 0
    fi

    # CPU冒烟测试
    # GPU冒烟测试
    # 删除/保留断言验证
    # devuser权限验证
}
```

这意味着任何变体（包括非GPU的）都可以无条件调用`verify_all_slim_gpu`，非GPU变体会自动跳过GPU验证部分。

### 迁移指南：从单Dockerfile到框架化

**Step 1**：识别共性逻辑
```bash
grep -h "RUN\|COPY" variants/*/Dockerfile | sort | uniq -c | sort -rn | head -20
# 出现≥2次的RUN命令就是提取候选
```

**Step 2**：创建目录结构
```bash
mkdir -p variants/shared/{lib,scripts,config}
```

**Step 3**：逐变体迁移（一次一个，验证通过再迁下一个）
- 推荐从最复杂的变体开始（GPU/ML变体）
- 每次迁移后`docker build`验证功能正常
- 对比新旧镜像大小

参考实现：[variants/shared/](../variants/shared/)

---

## 反模式汇总（踩坑手册）

### ❌ 反模式1：跨层strip/chmod触发COW膨胀

```dockerfile
RUN pip install torch torchvision       # 低层：4GB
RUN strip --strip-unneeded /opt/conda/envs/main/lib/*.so  # 上层：COW复制！
RUN chmod -R 755 /opt/conda             # 上层：COW复制~2.2GB！
```
**后果**：strip节省的500MB被COW完全抵消，chmod -R额外+2GB。
**正确做法**：同层完成所有修改（见Part 2 Dockerfile模板）。

### ❌ 反模式2：仅凭文件名/目录名判断可删除

```bash
rm -rf /opt/conda/.../site-packages/torchgen/
# ModuleNotFoundError: No module named 'torchgen'
```
**后果**：`torch.utils._python_dispatch`运行时import torchgen。
**正确做法**：删除前①检查DT_NEEDED和import引用 ②执行核心功能冒烟测试。

### ❌ 反模式3：盲目strip CUDA核心库

```bash
find /opt/conda -path "*/nvidia/*" -name "*.so" -exec strip --strip-all {} \;
```
**后果**：移除.dynamic符号表→dlopen失败；CUDA JIT kernel launch崩溃。
**正确做法**：只strip明确安全的库（conda/envs/main/lib普通C扩展、Triton二进制），不碰nvidia/目录。

### ❌ 反模式4：验证在清理之前（顺序颠倒）

```dockerfile
RUN cleanup_torch_dev && \
    python -c "import torch; print('OK')"  # 产生__pycache__!
```
**后果**：验证产生的.pyc文件留在最终镜像中。
**正确做法**：安装 → 清理R1/R2 → 验证 → cleanup_post_tests。

### ❌ 反模式5：跳过功能验证直接交付

```dockerfile
RUN pip install torch && cleanup_torch_dev
# 不知道删除的库是否影响功能
```
**后果**：运行时才报错（如分布式训练时发现cusolverMg缺失）。
**正确做法**：每次清理后运行7项验证清单。

### ❌ 反模式6：RUN chmod +x设置脚本权限

```dockerfile
COPY script.sh /usr/local/bin/script.sh
RUN chmod +x /usr/local/bin/script.sh   # 额外层！
```
**后果**：chmod修改属性触发COW，上层复制完整文件副本。
**正确做法**：`COPY --chmod=755 script.sh /usr/local/bin/script.sh`。

### ❌ 反模式7：验证函数在不适用场景报错

```bash
verify_gpu() { python -c "import torch; ..."; }
# 非GPU变体会报错退出build
```
**后果**：非GPU变体需要if-else守卫，Dockerfile变复杂。
**正确做法**：函数内部检测前置条件，不满足则SKIP返回0。

### ❌ 反模式8：一次删除大量库后统一验证

```bash
rm libA.so libB.so libC.so libD.so ...
# 如果失败，无法定位罪魁祸首
```
**正确做法**：R1批量删除高确定性项；R2逐组（≤3个）删除并验证。

### ❌ 反模式9：删除后只做import验证不做算子测试

```bash
python -c "import torch; print('OK')"   # 不足
```
**后果**：延迟加载库在import时不触发，运行算子时才崩溃。
**正确做法**：import + CPU matmul + CUDA matmul + attention/conv2d冒烟。

---

## 实战案例

### 案例：torch-dev-slim瘦身全记录（10.2GB→8.15GB）

**R1阶段**：
- 调用`cleanup_binaries`：strip共享库（~508MB）
- 删除nvrtc.alt（~110MB）、nvperf（~60MB）、nvshmem_device.bc（~25MB）、triton-amd（~5MB）
- 消除chmod -R导致的COW膨胀（避免~2GB损失）
- **R1合计**：~-1.9GB

**R2阶段**（DT_NEEDED分析）：
- `readelf -d libtorch_cuda.so`分析硬依赖
- 删除libcusolverMg.so.12（100MB）——DT_NEEDED无引用，单卡dlopen不触发
- 删除libcudnn_engines_runtime_compiled.so.9（29MB）——precompiled引擎覆盖标准shape
- 删除nvshmem插件（4MB）、protoc（10MB）、strip triton-bin（10MB）
- **R2合计**：~-150MB

**V阶段验证**：
- 7项验证清单全部通过
- torchgen/陷阱在验证阶段被拦截（回滚删除）
- CPU/CUDA matmul、conv2d+autograd、MLP+CrossEntropy、devuser权限全部OK

**最终结果**：10.2GB → 8.15GB（-2.05GB/-20%），功能完整。

---

## 快速参考卡

### 常用命令速查

```bash
# 分析镜像层大小
docker history <image> --format "{{.Size}}\t{{.CreatedBy}}" | head -20

# 扫描大.so文件
docker run --rm <image> bash -c "
  SP=\$(python -c 'import site; print(site.getsitepackages()[0])')
  find \$SP/nvidia -name '*.so*' -size +20M -exec du -sh {} \; | sort -rh"

# DT_NEEDED分析
readelf -d libtorch_cuda.so | grep NEEDED | awk '{print $5}' | tr -d '[]'

# 构建slim镜像
docker build --target production -t <image>:slim -f variants/<name>/Dockerfile .
```

### 关键函数速查

| 函数 | 位置 | 作用 |
|------|------|------|
| `cleanup_binaries()` | shared/lib/cleanup.sh | strip+.a/.bc删除（所有变体必调） |
| `cleanup_torch_dev()` | shared/lib/cleanup.sh | R1+R2 CUDA冗余清理（GPU变体） |
| `cleanup_post_tests()` | shared/lib/cleanup.sh | 验证后清理pycache |
| `verify_all_slim_gpu()` | shared/lib/verify.sh | CPU+GPU+删除/保留+devuser验证（自动跳过非GPU） |
| `r2-dtneeded-analysis.sh` | shared/scripts/ | R2深度分析（--analyze/--delete/--verify/--all） |

### 7条铁律

1. **同层修改**：strip/chmod/rm必须与文件创建在同一RUN层
2. **先量后减**：瘦身前先du+history分析，不盲目删除
3. **两轮渐进**：R1确定项→R2 DT_NEEDED分析，不一步到位
4. **不碰CUDA核心**：nvidia/下libcublas/libcudnn/libnccl等不strip
5. **验证即闭环**：每次删除后立即7项验证，不跳过
6. **顺序铁律**：安装→清理→验证→post_tests清理，顺序不可颠倒
7. **框架复用**：多变体项目必须提取shared框架，消除重复

---

## 参考资料

| 文件 | 说明 |
|------|------|
| [DOCKER-SLIMMING-QUICKSTART.md](DOCKER-SLIMMING-QUICKSTART.md) | 5分钟快速上手指南（速查表+FAQ） |
| [shared/lib/cleanup.sh](../variants/shared/lib/cleanup.sh) | 清理函数库参考实现 |
| [shared/lib/verify.sh](../variants/shared/lib/verify.sh) | 验证函数库参考实现 |
| [shared/scripts/r2-dtneeded-analysis.sh](../variants/shared/scripts/r2-dtneeded-analysis.sh) | DT_NEEDED分析脚本 |
| [torch-dev/Dockerfile](../variants/torch-dev/Dockerfile) | GPU/ML变体Dockerfile完整示例 |
| [torch-dev/SLIMMING-GUIDE.md](../variants/torch-dev/SLIMMING-GUIDE.md) | torch-dev-slim专项指南 |
