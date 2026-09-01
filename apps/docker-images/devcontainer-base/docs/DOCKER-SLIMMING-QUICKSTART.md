# Docker GPU/ML 镜像瘦身快速上手指南

> **版本**: 1.0 | **更新日期**: 2026-08-19 | **适用范围**: 所有 GPU/ML 变体（torch-dev/ai-dev/llm-agent 等）
>
> **深入阅读**: 完整方法论见 [docker-gpu-slimming-sop.md](../../../../docs/retrospective/patterns/code-patterns/docker-gpu-slimming-sop.md) | 实例参考 [torch-dev/SLIMMING-GUIDE.md](../variants/torch-dev/SLIMMING-GUIDE.md)

---

## 🚀 5分钟快速开始

新建 GPU/ML 变体时，只需在 Dockerfile 中遵循**同层清理 + 框架验证**两个核心原则：

### Step 1：复制框架脚本（S2层开头）

```dockerfile
# 瘦身框架（清理函数 + 验证函数 + R2分析脚本）
COPY shared/lib/cleanup.sh /usr/local/share/variant-framework/cleanup.sh
COPY shared/lib/verify.sh /usr/local/share/variant-framework/verify.sh
COPY --chmod=755 shared/scripts/r2-dtneeded-analysis.sh \
    /usr/local/share/variant-framework/r2-dtneeded-analysis.sh
```

### Step 2：pip install 同层调用清理（S2层核心）

```dockerfile
RUN --mount=type=cache,target=/root/.cache/pip \
    source /usr/local/share/variant-framework/logging.sh && \
    source /usr/local/share/variant-framework/cleanup.sh && \
    variant_stage_header "Install YOUR_FRAMEWORK" && \
    pip install --no-cache-dir your-packages && \
    cleanup_binaries && \        # ✅ strip共享库 + 删除静态库（~500MB）
    cleanup_torch_dev && \       # ✅ R1+R2 CUDA冗余库清理（~280MB）
    ensure_user_bashrc && \      # ✅ 精准权限修复（无CoW膨胀）
    ensure_profile_d_executable
```

### Step 3：验证后清理 pycache（S3层末尾）

```dockerfile
RUN source /usr/local/share/variant-framework/logging.sh && \
    source /usr/local/share/variant-framework/cleanup.sh && \
    source /usr/local/share/variant-framework/verify.sh && \
    verify_all_slim_gpu && \    # ✅ 一键7项验证（CPU+GPU+删除/保留+devuser）
    cleanup_post_tests          # ✅ 必须最后调用，清理测试产生的pycache
```

**完成！** 构建即可自动获得瘦身效果。

---

## 📂 可用脚本与函数速查

### 共享脚本位置

| 脚本 | 路径 | 用途 |
|------|------|------|
| R2 DT_NEEDED 分析脚本 | [variants/shared/scripts/r2-dtneeded-analysis.sh](../variants/shared/scripts/r2-dtneeded-analysis.sh) | 动态依赖分析，安全删除冗余CUDA库 |
| 清理函数库 | [variants/shared/lib/cleanup.sh](../variants/shared/lib/cleanup.sh) | `cleanup_binaries`/`cleanup_torch_dev`/`cleanup_post_tests` |
| 验证函数库 | [variants/shared/lib/verify.sh](../variants/shared/lib/verify.sh) | `verify_all_slim_gpu`/`verify_gpu_smoke`/`verify_slim_delete_preserve` |

### cleanup.sh 关键函数

| 函数 | 调用时机 | 节省 | 说明 |
|------|---------|------|------|
| `cleanup_binaries` | pip install 同层 | ~500MB | strip `.so`，删除 `.a` 静态库、`.bc` bitcode |
| `cleanup_torch_dev` | pip install 同层 | ~280MB | R1删除明显冗余 + R2基于DT_NEEDED删除延迟加载库 |
| `cleanup_post_tests` | S3层所有验证**之后** | ~10-30MB | 清理测试产生的 `__pycache__`、`.pyc` |
| `ensure_user_bashrc` | pip install 同层 | （避免CoW） | 精准修复devuser bashrc权限，不做全目录chmod |

### verify.sh 关键函数

| 函数 | 用途 | 验证项 |
|------|------|--------|
| `verify_all_slim_gpu` | **首选，一键调用** | CPU matmul/softmax + CUDA matmul/attention + 删除项不存在 + 保留项存在 + devuser可import torch |
| `verify_gpu_smoke` | 单独GPU冒烟 | CUDA matmul + flash attention + tensor device迁移 |
| `verify_slim_delete_preserve` | 删除/保留断言 | 断言已删除文件不存在 + 保留文件存在 |

> 💡 **非GPU变体安全**：`verify_all_slim_gpu` 自动检测 torch 是否安装，未安装时跳过GPU验证，不会报错。

---

## 🔧 r2-dtneeded-analysis.sh 用法

R2深度瘦身使用DT_NEEDED动态依赖分析，**不要凭文件名盲目删除**。

### 容器内分析模式（推荐首次使用）

```bash
# 进入运行中的容器
docker exec -it <container> bash

# 分析模式：扫描依赖关系，输出删除建议（不实际删除）
bash /usr/local/share/variant-framework/r2-dtneeded-analysis.sh --analyze

# 确认安全后执行删除
bash /usr/local/share/variant-framework/r2-dtneeded-analysis.sh --delete

# 验证删除后功能正常
bash /usr/local/share/variant-framework/r2-dtneeded-analysis.sh --verify

# 一键全流程（analyze → delete → verify）
bash /usr/local/share/variant-framework/r2-dtneeded-analysis.sh --all
```

### 添加新删除项

编辑 [r2-dtneeded-analysis.sh](../variants/shared/scripts/r2-dtneeded-analysis.sh) 中两个数组：

```bash
# 绝对不能删除的保护项（硬依赖）
PROTECTED_PATTERNS=(
    "libcublas.so"          # CUDA BLAS核心
    "libcudnn.so.9"         # cuDNN核心
    "libnccl.so"            # 多卡通信（即使单卡，torch硬依赖）
    "libcusparseLt.so"      # sparse LA，torch硬依赖
    "torchgen/"             # torch运行时import
    # 添加你的保护项...
)

# 经DT_NEEDED验证可安全删除的项
SAFE_DELETE_PATTERNS=(
    "nvidia/cu13/lib/libcusolverMg.so.12"    # 多GPU分布式求解器
    "nvshmem_bootstrap_mpi"                   # HPC集群插件
    "libnvperf_"                              # Nsight性能分析
    # 添加你的删除项...
)
```

**添加规则**：
1. 必须先 `--analyze` 确认 DT_NEEDED 中无硬依赖
2. 在容器内运行 `--delete && --verify` 验证功能
3. 验证通过后再写入脚本默认清单

---

## ⚠️ 必须遵守的铁律（踩坑总结）

### ❌ 绝对禁止的操作

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| **跨层strip/chmod**（pip install在一层，strip在下一层） | CoW写时复制膨胀+1~2GB | cleanup_binaries必须在pip install**同一RUN层** |
| **`chmod -R 755 /opt/conda`** | CoW膨胀~1.2GB | 用`ensure_user_bashrc`精准修复，仅改需要的文件 |
| **`strip --strip-all`** | 移除动态符号表，dlopen失败 | 只用`strip --strip-unneeded` |
| **strip nvidia/目录下CUDA库** | CUDA JIT编译可能崩溃 | cleanup_binaries不碰nvidia/目录，R2单独处理 |
| **仅凭文件名判断可删除**（如torchgen/听起来像构建工具） | 运行时import失败：`ModuleNotFoundError` | 必须DT_NEEDED分析+import验证 |
| **清理在验证之前**（cleanup_all在smoke tests前） | 测试产生的pycache无法被清理 | cleanup_post_tests必须在**所有验证最后** |
| **单独RUN chmod +x** | 增加不必要镜像层 | 用`COPY --chmod=755`复制时设权限 |

### ✅ 必须做的检查

- [ ] `cleanup_binaries` 和 `cleanup_torch_dev` 在 pip install **同一层**
- [ ] `cleanup_post_tests` 在 S3 层**最后一行**
- [ ] 没有 `chmod -R /opt/conda` 命令
- [ ] 构建后运行容器验证：`python -c "import torch; print(torch.cuda.is_available())"`
- [ ] devuser可import：`su - devuser -c "python -c 'import torch'"`

---

## 📋 构建命令速查

### 构建单个变体（含slim标签）

```bash
cd apps/docker-images/devcontainer-base/variants

# 构建torch-dev-slim（自动依赖链构建）
bash build.sh torch-dev --tag slim --no-cache

# 构建所有变体的slim版本
bash build.sh --all --tag slim
```

### 镜像体积对比

```bash
# 构建后查看体积
docker images devcontainer-base --format "table {{.Tag}}\t{{.Size}}"

# 对比slim和latest差异
docker history devcontainer-base:torch-dev-slim --no-trunc | head -20
```

### 容器内冒烟测试

```bash
# 启动容器
docker run --gpus all --rm -it devcontainer-base:torch-dev-slim bash

# 一键验证（容器内）
bash /usr/local/share/variant-framework/r2-dtneeded-analysis.sh --verify

# 手动验证Python
python -c "
import torch, sys
print(f'PyTorch: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'GIL enabled: {sys._is_gil_enabled()}')
x = torch.randn(64,128,device='cuda') @ torch.randn(128,32,device='cuda')
print(f'CUDA matmul OK: shape={x.shape}')
"
```

---

## 🐛 常见问题排查

### 构建失败：`cleanup_torch_dev: command not found`

**原因**：COPY了旧版cleanup.sh（无cleanup_torch_dev函数）。

**解决**：确保COPY行指向最新shared/lib/cleanup.sh：
```dockerfile
COPY shared/lib/cleanup.sh /usr/local/share/variant-framework/cleanup.sh
```

### 运行时报错：`ModuleNotFoundError: No module named 'torchgen'`

**原因**：R2删除了`torchgen/`目录（听起来像构建工具，实际是运行时依赖）。

**解决**：在`PROTECTED_PATTERNS`中添加`torchgen/`，重建镜像。

### slim镜像CUDA报错：`libcusolverMg.so: cannot open shared file`

**原因**：你的代码确实用到了分布式多GPU线性代数（罕见，单卡不触发）。

**解决**：
1. 在`SAFE_DELETE_PATTERNS`中删除对应条目
2. 或使用`torch-dev-latest`完整版标签

### 镜像构建后体积仍很大

**排查清单**：
1. 确认`cleanup_binaries`被调用（检查构建日志有`[CLEANUP] Stripping shared libraries`）
2. 确认没有`chmod -R /opt/conda`（搜索Dockerfile）
3. 确认`--no-cache-dir`在pip install参数中
4. 确认`cleanup_post_tests`在最后

---

## 📚 延伸阅读

| 文档 | 适合人群 | 内容 |
|------|---------|------|
| [docker-gpu-slimming-sop.md](../../../../docs/retrospective/patterns/code-patterns/docker-gpu-slimming-sop.md) | 方法论学习者 | 完整四步法SOP、第一性原理分析、反模式详解 |
| [torch-dev/SLIMMING-GUIDE.md](../variants/torch-dev/SLIMMING-GUIDE.md) | torch-dev维护者 | torch-dev专用瘦身记录、删除/保留清单、技术原理 |
| [shared/lib/cleanup.sh](../variants/shared/lib/cleanup.sh) | 脚本维护者 | 清理函数源码和注释 |
| [shared/scripts/r2-dtneeded-analysis.sh](../variants/shared/scripts/r2-dtneeded-analysis.sh) | R2分析执行者 | DT_NEEDED分析脚本源码，4种模式详解 |
| [build-test.md](../.agents/rules/build-test.md) | CI/CD维护者 | 构建测试规范 |

---

## 📊 瘦身效果参考（torch-dev实例）

| 阶段 | 体积 | 节省 | 关键操作 |
|------|------|------|---------|
| 未优化初始构建 | 10.2 GB | — | pip install无任何清理 |
| R1基础瘦身 | 8.3 GB | -1.9 GB | strip + 删除明显冗余 + 消除CoW |
| R2深度瘦身 | 8.15 GB | -0.15 GB | DT_NEEDED分析删除延迟加载库 |
| **总计** | **8.15 GB** | **-2.05 GB (20%)** | 功能无损失 |
