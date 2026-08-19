---
id: "docker-gpu-slimming-sop"
title: "GPU/ML Docker镜像瘦身SOP"
type: "code-pattern"
maturity: "L2-validated"
maturity_note: "基于torch-dev-slim实战验证(10.2GB→8.15GB/-20%)，DT_NEEDED分析法经过readelf+import双重验证"
date: 2026-08-19
source:
  - "retrospective-devcontainer-slim-images-20260819（torch-dev-slim两轮瘦身实战，2026-08-19）"
  - "apps/docker-images/devcontainer-base/variants/shared/lib/cleanup.sh（cleanup_torch_dev R1+R2参考实现）"
related_patterns:
  - "docker-deep-slim-8step.md"
  - "docker-cow-same-layer-modification.md"
  - "docker-apt-layer-slimming.md"
  - "docker-build-four-layer-verification.md"
  - "docker-image-variant-incremental-inheritance.md"
tags: ["docker", "slimming", "gpu", "cuda", "pytorch", "dt-needed", "cow", "sop", "ml", "image-optimization"]
validation_count: 1
reuse_count: 0
---

# GPU/ML Docker镜像瘦身SOP

> **一句话总结**：两轮渐进瘦身（R1确定项 + R2 DT_NEEDED分析）+ CoW层序零成本 + 7项验证清单，安全可预测地缩减GPU/ML镜像体积。

## 触发场景

- 包含PyTorch/TensorFlow/CUDA/cuDNN等GPU/ML框架的Docker镜像体积过大（>8GB）
- 新增ML变体镜像（在基础镜像之上追加pip/conda安装大框架）
- 需要对已有GPU镜像做系统性瘦身，但不确定哪些.so文件可安全删除
- Dockerfile审查中检查CUDA/ML镜像是否存在COW膨胀、冗余库等问题

**不适用于**：
- CPU-only镜像（使用[docker-deep-slim-8step.md](docker-deep-slim-8step.md)即可）
- 生产运行时镜像（通常已精简至<3GB，且对功能完整性要求极高）
- 从头构建的基础镜像（无ML框架，无CUDA冗余库问题）

## 前置依赖

执行本SOP前，必须已掌握：
1. [P7同层修改原则](docker-cow-same-layer-modification.md)——所有strip/rm/chmod必须在文件创建层完成
2. [Docker镜像深度压缩8步法](docker-deep-slim-8step.md)——基础清理（apt/pip/conda缓存、__pycache__、静态库、man/doc）
3. 镜像内可用`readelf`、`ldd`、`du`、`find`、`strip`等工具

---

## 核心流程：四步法

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

---

## Step 1：分析定位（先量后减）

**目标**：精准定位体积来源，避免盲目删除。

### 1.1 镜像层分析

```bash
# 查看各层大小，定位异常大层
docker history <image> --format "{{.Size}}\t{{.CreatedBy}}" | head -20
```

关注：
- 安装pip/conda包的层（通常最大）
- 清理/权限修复层（正常应<1MB，>100MB说明COW膨胀）
- chmod -R/chown -R出现的层（COW膨胀信号）

### 1.2 目录体积分布

```bash
# 启动容器，统计大目录
docker run --rm <image> bash -c "
  du -sh /opt/conda/envs/main/lib/python*/site-packages/torch 2>/dev/null
  du -sh /opt/conda/envs/main/lib/python*/site-packages/nvidia 2>/dev/null
  du -sh /opt/conda/envs/main/lib/python*/site-packages/triton 2>/dev/null
  du -sh /opt/conda/pkgs 2>/dev/null
  du -sh /opt/conda/envs/main/lib 2>/dev/null
"
```

### 1.3 细粒度扫描CUDA库

```bash
# 列出site-packages/nvidia下所有>20MB的.so文件
docker run --rm <image> bash -c "
  SP=\$(python -c 'import site; print(site.getsitepackages()[0])')
  find \$SP/nvidia -name '*.so*' -size +20M -exec du -sh {} \; | sort -rh
"
```

**输出示例**：
```
224M  .../nvidia/cusparse/lib/libcusparseLt.so.0
186M  .../nvidia/nccl/lib/libnccl.so.2
109M  .../nvidia/cu13/lib/libnvrtc.alt.so.13    ← R1可删
100M  .../nvidia/cu13/lib/libcusolverMg.so.12   ← R2可删（需DT_NEEDED验证）
 60M  .../nvidia/cu13/lib/libnvperf_host.so     ← R1可删
 38M  .../nvidia/nvshmem/lib/libnvshmem_host.so.3 ← 保留（硬依赖）
 29M  .../nvidia/cudnn/lib/libcudnn_engines_runtime_compiled.so.9 ← R2可删
```

---

## Step 2：R1基础瘦身（确定项，-1.5~2GB）

**原则**：只删除高确定性冗余项（跨平台后端、性能分析工具、备用库、设备端编译产物）。

### 2.1 共享库strip（~500MB）

> ⚠️ 必须在`pip install`同层执行，见[P7原则](docker-cow-same-layer-modification.md)。

```bash
# 在pip install torch的同一RUN层中
find /opt/conda/envs/main/lib -name "*.so*" -type f \
  -exec strip --strip-unneeded {} \; 2>/dev/null || true
```

- 对C扩展共享库使用`--strip-unneeded`（保留动态符号表），不能用`--strip-all`
- **不要strip CUDA核心库**（libcublas/libcudnn/libcufft等），可能影响kernel JIT
- strip Triton工具链二进制通常安全：
  ```bash
  find /opt/conda/envs/main/lib/python*/site-packages/triton/backends/nvidia/bin \
    -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
  ```

### 2.2 R1标准删除清单

| 删除项 | 典型大小 | 为什么可删 |
|--------|---------|-----------|
| `nvidia/cu13/lib/libnvrtc.alt.so*` | ~110MB | NVRTC备用构建，标准libnvrtc.so已满足 |
| `nvidia/cu13/lib/libnvperf_*` | ~60MB | Nsight Compute性能分析库，运行时不链接 |
| `nvidia/nvshmem/lib/libnvshmem_device.bc` | ~25MB | 设备端bitcode，编译时用，运行时不需要 |
| `nvidia/nvshmem/lib/libnvshmem_device.a` | ~8MB | NVSHMEM静态库，运行时不需要 |
| `triton/backends/amd/` | ~3-5MB | AMD GPU后端，N卡镜像不需要 |
| 静态库`.a`（非编译器必需） | ~50MB | 排除gcc/sysroot/libnpymath后删除 |

参考实现见 [cleanup.sh](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/variants/shared/lib/cleanup.sh) 的`cleanup_torch_dev()` R1部分。

### 2.3 CoW层序优化（零成本，避免-1~2GB膨胀）

这一步**不删除文件**，但防止镜像因COW机制膨胀1-2GB：

```dockerfile
# ❌ 错误：跨层chmod -R触发COW
RUN pip install torch torchvision --index-url ...
RUN chmod -R 755 /opt/conda          # 这层新增~2.2GB!

# ✅ 正确：同层完成所有清理
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch torchvision --index-url ... && \
    cleanup_binaries && \           # strip共享库
    cleanup_torch_dev && \          # R1+R2 CUDA清理
    ensure_user_bashrc && \         # 精准权限修复（替代chmod -R）
    ensure_profile_d_executable     # 精准权限修复
```

**精准权限修复函数**（替代chmod -R）：
```bash
ensure_user_bashrc() {
  touch /home/devuser/.bashrc && chown devuser:devuser /home/devuser/.bashrc
}
ensure_profile_d_executable() {
  find /etc/profile.d -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true
}
```

---

## Step 3：R2深度瘦身（DT_NEEDED分析，-100~200MB）

**原则**：基于动态链接依赖分析，区分硬依赖与延迟加载库，只删除验证安全的项。

### 3.1 DT_NEEDED分析法（核心技术）

#### 原理

ELF共享库通过`.dynamic`段的`DT_NEEDED`条目声明硬依赖。`readelf -d`可以列出这些硬依赖：

```bash
readelf -d <core_library.so> | grep NEEDED
```

- **DT_NEEDED中出现**→ 硬依赖，删除后`import torch`立即失败（dlopen fatal error）
- **不在DT_NEEDED中**→ 可能是延迟加载（dlopen按需加载）或完全无用，需进一步验证

#### 操作步骤

```bash
# 1. 找到核心库
SP=$(python -c 'import site; print(site.getsitepackages()[0])')
CORE_LIB=$SP/torch/lib/libtorch_cuda.so

# 2. 提取DT_NEEDED硬依赖列表
readelf -d $CORE_LIB | grep NEEDED | awk '{print $5}' | tr -d '[]'

# 3. 对每个候选大库，检查是否在硬依赖中
# 示例：检查libcusolverMg
readelf -d $CORE_LIB | grep -c "libcusolverMg"   # 0=不在硬依赖中
# 对比：检查libcusparseLt
readelf -d $CORE_LIB | grep -c "libcusparseLt"   # 1=硬依赖，不能删
```

#### 三层分类决策

对每个>20MB的.so文件，按以下决策树分类：

```
文件大小 > 20MB?
├─ 否 → 跳过（节省不值得风险）
└─ 是 → readelf检查核心库DT_NEEDED
   ├─ 在DT_NEEDED中 → 🔴 硬依赖，保留
   └─ 不在DT_NEEDED中 → strings搜索引用
      ├─ 无任何引用 → 🟢 安全删除
      └─ 有dlopen引用 → 功能验证后决定
         ├─ 验证通过（删除后功能正常）→ 🟡 条件删除（记录已知限制）
         └─ 验证失败 → 🔴 保留
```

### 3.2 R2标准删除清单（基于torch-dev-slim实战）

| 删除项 | 大小 | DT_NEEDED | 验证结果 |
|--------|------|-----------|---------|
| `nvidia/cu13/lib/libcusolverMg.so.12` | 100MB | ❌ 不在 | ✅ 单卡场景安全（多GPU分布式专用） |
| `nvidia/cudnn/lib/libcudnn_engines_runtime_compiled.so.9` | 29MB | ❌ 不在 | ✅ JIT引擎（precompiled覆盖标准shape） |
| `nvidia/nvshmem/lib/nvshmem_bootstrap_mpi.so*` | ~1MB | ❌ 不在 | ✅ MPI集群bootstrap（WSL2不用） |
| `nvidia/nvshmem/lib/nvshmem_transport_ib*.so*` | ~3MB | ❌ 不在 | ✅ InfiniBand传输（消费级GPU不用） |
| `nvidia/cu13/lib/libnvblas.so.13` | <1MB | ❌ 不在 | ✅ NVBLAS drop-in替换（不用） |
| `nvidia/cu13/lib/libcheckpoint.so` | ~1MB | ❌ 不在 | ✅ checkpoint工具（不用） |
| `nvidia/cu13/lib/libpcsamplingutil.so` | <1MB | ❌ 不在 | ✅ PC采样工具（不用） |
| `torch/bin/protoc*` | ~10MB | N/A | ✅ protobuf编译器（运行时用Python protobuf库） |

### 3.3 R2禁止删除清单（硬依赖）

| 保留项 | 大小 | 原因 |
|--------|------|------|
| `nvidia/cusparse/lib/libcusparseLt.so.0` | 224MB | DT_NEEDED硬依赖，libtorch_cuda.so直接链接 |
| `nvidia/nccl/lib/libnccl.so.2` | 186MB | DT_NEEDED硬依赖，分布式通信必需 |
| `nvidia/nvshmem/lib/libnvshmem_host.so.3` | 38MB | DT_NEEDED硬依赖（libtorch_nvshmem.so→此处） |
| `torchgen/`目录 | 2.4MB | `torch.utils._python_dispatch`运行时import |
| `nvidia/cublas/lib/libcublasLt.so*` | ~400MB | cuBLAS核心库，硬依赖 |
| `nvidia/cudnn/lib/libcudnn_engines_precompiled.so*` | ~235MB | cuDNN预编译引擎，标准算子必需 |
| `nvidia/cu13/lib/libnvrtc.so*`（非.alt） | ~40MB | NVRTC标准版本，Triton编译kernel必需 |

> ⚠️ **torchgen/陷阱**：虽然名字含"gen"看似代码生成工具，但`torch.utils._python_dispatch`运行时`import torchgen`，删除后导致`ModuleNotFoundError`。**不要仅凭文件名判断用途！** 必须执行实际import验证。

---

## Step 4：验证交付（7项清单）

### 4.1 瘦身验证清单

每轮瘦身（R1和R2）后，必须执行以下全部验证：

```bash
#!/bin/bash
# slim-validate.sh — GPU镜像瘦身验证脚本
set -e

echo "=== [1/7] 核心模块导入 ==="
python -c "import torch; import torchvision; print(f'torch={torch.__version__}, cuda={torch.cuda.is_available()}')"

echo "=== [2/7] CUDA基础算子 ==="
python -c "
import torch
x = torch.randn(256, 256, device='cuda')
y = torch.matmul(x, x)
assert y.shape == (256, 256), f'matmul shape mismatch: {y.shape}'
print(f'matmul OK, device={y.device}')
"

echo "=== [3/7] 卷积+自动微分 ==="
python -c "
import torch
import torch.nn.functional as F
x = torch.randn(1, 3, 32, 32, device='cuda', requires_grad=True)
w = torch.randn(16, 3, 3, 3, device='cuda', requires_grad=True)
y = F.conv2d(x, w)
loss = y.sum()
loss.backward()
assert x.grad is not None and w.grad is not None
print(f'conv2d+autograd OK')
"

echo "=== [4/7] 交叉熵+MLP前向（含cudnn） ==="
python -c "
import torch
import torch.nn as nn
model = nn.Sequential(nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, 10)).cuda()
x = torch.randn(32, 128, device='cuda')
y = model(x)
loss = nn.CrossEntropyLoss()(y, torch.randint(0, 10, (32,), device='cuda'))
loss.backward()
print(f'MLP+CrossEntropy OK, loss={loss.item():.4f}')
"

echo "=== [5/7] 删除项确认（不应存在） ==="
SP=$(python -c 'import site; print(site.getsitepackages()[0])')
for f in \
  "nvidia/cu13/lib/libnvrtc.alt.so.13" \
  "nvidia/cu13/lib/libnvperf_host.so" \
  "nvidia/cu13/lib/libcusolverMg.so.12" \
  "triton/backends/amd"; do
  if [ -e "$SP/$f" ]; then
    echo "FAIL: $f still exists!"; exit 1
  fi
done
echo "Deleted items verified absent"

echo "=== [6/7] 保留项确认（必须存在） ==="
for f in \
  "nvidia/cusparse/lib/libcusparseLt.so.0" \
  "nvidia/nccl/lib/libnccl.so.2" \
  "torchgen/__init__.py"; do
  if [ ! -e "$SP/$f" ]; then
    echo "FAIL: $f missing!"; exit 1
  fi
done
echo "Preserved items verified present"

echo "=== [7/7] 镜像体积 ==="
du -sh /opt/conda/envs/main/lib/python*/site-packages/torch 2>/dev/null
du -sh /opt/conda/envs/main/lib/python*/site-packages/nvidia 2>/dev/null
echo "All validations PASSED ✓"
```

### 4.2 devuser权限验证

```bash
# 验证非root用户也能正常使用
su - devuser -c "python -c 'import torch; print(torch.cuda.is_available())'"
```

### 4.3 无__pycache__残留

```bash
# 验证测试后清理了pyc缓存
find /opt/conda -name "__pycache__" -type d 2>/dev/null | wc -l   # 预期: 0
```

---

## Dockerfile集成模板

以下是GPU/ML变体Dockerfile中瘦身调用的标准模板：

```dockerfile
# ── S2层：ML框架安装 + 同层瘦身（核心！）────────────────────
# 必须在pip install的同一RUN层完成所有清理，禁止跨层
COPY shared/lib/cleanup.sh /usr/local/share/variant-framework/cleanup.sh
COPY shared/lib/verify.sh /usr/local/share/variant-framework/verify.sh
COPY --chmod=755 shared/scripts/r2-dtneeded-analysis.sh \
    /usr/local/share/variant-framework/r2-dtneeded-analysis.sh
RUN --mount=type=cache,target=/root/.cache/pip \
    source /usr/local/share/variant-framework/logging.sh && \
    source /usr/local/share/variant-framework/cleanup.sh && \
    variant_stage_header "Install PyTorch + CUDA" && \
    PIP_INDEX="https://download.pytorch.org/whl/cu130" && \
    pip install --no-cache-dir torch torchvision --index-url "$PIP_INDEX" && \
    # ── 瘦身（必须在同层，禁止移到后续RUN）──
    cleanup_binaries && \       # strip .so + 删除非必要.a静态库 (~500MB)
    cleanup_torch_dev && \      # R1+R2 CUDA冗余库清理 (~280MB)
    # ── 精准权限修复（替代chmod -R /opt/conda，避免CoW膨胀）──
    ensure_user_bashrc && \
    ensure_profile_d_executable

# ── S3层：框架级GPU/ML slim验证（验证后清理pycache）──────────
RUN source /usr/local/share/variant-framework/logging.sh && \
    source /usr/local/share/variant-framework/cleanup.sh && \
    source /usr/local/share/variant-framework/verify.sh && \
    verify_all_slim_gpu && \              # CPU+GPU冒烟+删除/保留断言+devuser
    cleanup_post_tests   # 验证后清理__pycache__和临时文件
```

---

## 反模式

### ❌ 反模式1：跨层strip/chmod触发COW膨胀

```dockerfile
# 错误：strip和chmod在pip install的下一层执行
RUN pip install torch torchvision       # 低层：4GB
RUN strip --strip-unneeded /opt/conda/envs/main/lib/*.so  # 上层：COW复制！
RUN chmod -R 755 /opt/conda             # 上层：COW复制~2.2GB！
```

后果：strip节省的500MB被COW膨胀完全抵消，chmod -R额外增加~2GB。正确做法见Step 2.3。

### ❌ 反模式2：仅凭文件名/目录名判断可删除

```bash
# 错误：torchgen/听起来像构建工具就删了
rm -rf /opt/conda/.../site-packages/torchgen/
# 后果：ModuleNotFoundError: No module named 'torchgen'
# 原因：torch.utils._python_dispatch运行时import torchgen
```

正确做法：删除前必须①检查是否有import引用 ②执行import验证。

### ❌ 反模式3：盲目strip CUDA核心库

```bash
# 错误：对所有.so执行strip --strip-all
find /opt/conda -name "*.so" -exec strip --strip-all {} \;
```

后果：
- CUDA kernel JIT编译可能依赖符号表信息，导致kernel launch失败
- `--strip-all`移除动态符号表，导致dlopen失败
- 即使使用`--strip-unneeded`，对CUDA核心库（libcublas/libcudnn）strip仍有风险

正确做法：只strip明确知道安全的库（conda/envs/main/lib下的普通C扩展、Triton工具链二进制），不碰nvidia/目录下的CUDA库。

### ❌ 反模式4：跳过功能验证直接交付

```dockerfile
# 错误：清理完成后不验证
RUN pip install torch && cleanup_torch_dev
# 直接构建，不知道删除的库是否影响功能
```

后果：cusolverMg删除后如果有代码依赖（如分布式训练），运行时才报错。正确做法见Step 4——每次清理后立即运行7项验证。

### ❌ 反模式5：验证在清理之前（顺序颠倒）

```dockerfile
# 错误：先清理再验证，验证产生的pycache无法清理
RUN cleanup_torch_dev && \
    python -c "import torch; print('OK')"  # 这产生__pycache__!
```

后果：验证步骤导入模块时生成__pycache__，但清理已在验证前完成，.pyc文件留在最终镜像中。正确顺序：**安装→清理→验证→post-tests清理**。

---

## 检验标准

构建完成后，以下全部必须通过：

### 体积检查

| 指标 | 命令 | 预期 |
|------|------|------|
| 清理层无大层 | `docker history <image> \| grep -v "MB\|GB" \| head` | 清理/权限层<1MB |
| torch包大小 | `du -sh $SP/torch` | 比瘦身前减少>100MB |
| nvidia包大小 | `du -sh $SP/nvidia` | 比瘦身前减少>200MB |
| 无__pycache__ | `find / -name "__pycache__" 2>/dev/null \| wc -l` | 0 |
| 无.pyc残留 | `find / -name "*.pyc" 2>/dev/null \| wc -l` | 0 |

### 功能检查

- [ ] `import torch` 成功，版本正确
- [ ] `torch.cuda.is_available()` 返回True
- [ ] CUDA张量matmul执行成功（不触发cuSolverMg缺失错误）
- [ ] conv2d + autograd 反向传播成功
- [ ] MLP + CrossEntropyLoss 训练step成功（触发cuDNN路径）
- [ ] devuser身份import torch成功（权限正确）
- [ ] 所有已删除项确认不存在
- [ ] 所有保留硬依赖确认存在

### CoW检查

- [ ] 没有跨层`chmod -R`或`chown -R`大目录
- [ ] strip操作在pip install同层完成
- [ ] 最终层仅含rm操作（无strip/chmod/purge）

---

## 参考实现

| 文件 | 说明 |
|------|------|
| [cleanup.sh - cleanup_torch_dev()](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/variants/shared/lib/cleanup.sh#L302-L398) | R1+R2清理函数参考实现（97行） |
| [cleanup.sh - cleanup_binaries()](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/variants/shared/lib/cleanup.sh#L124-L160) | strip+静态库删除参考实现 |
| [torch-dev/Dockerfile](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/variants/torch-dev/Dockerfile) | torch-dev变体Dockerfile（瘦身集成示例） |
| [torch-dev/SLIMMING-GUIDE.md](file:///d:/spaces/SpecWeave/apps/docker-images/devcontainer-base/variants/torch-dev/SLIMMING-GUIDE.md) | torch-dev-slim专项瘦身指南 |

## 成熟度

L2-validated — 在torch-dev-slim镜像中完整验证：
- **R1基础瘦身**：strip(~508MB) + nvrtc.alt/nvperf/nvshmem-bitcode/triton-amd(~180MB) + CoW层序优化，-1.9GB
- **R2深度瘦身**：DT_NEEDED分析后删除cusolverMg(100MB)+cudnn-jit(29MB)+nvshmem插件(4MB)+protoc(10MB)+strip triton-bin(~10MB)，-150MB
- **V阶段验证**：7项验证清单全部通过，torchgen/陷阱在V阶段被拦截
- **总效果**：10.2GB → 8.15GB（-2.05GB/-20%），功能完整

## 交叉引用

- 基础模式：
  - [docker-deep-slim-8step.md](docker-deep-slim-8step.md)（通用镜像8步压缩法，本SOP是GPU/ML场景的扩展）
  - [docker-cow-same-layer-modification.md](docker-cow-same-layer-modification.md)（P7同层修改原则，CoW层序优化的理论基础）
  - [docker-build-four-layer-verification.md](docker-build-four-layer-verification.md)（四层验证流水线）
- 来源复盘：
  - [retrospective-devcontainer-slim-images-20260819](../reports/build-engineering/retrospective-devcontainer-slim-images-20260819/README.md)（本SOP的实战来源）
