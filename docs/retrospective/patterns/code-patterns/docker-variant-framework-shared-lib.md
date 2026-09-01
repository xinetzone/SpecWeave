---
id: "docker-variant-framework-shared-lib"
title: "Docker多变体框架化模式（共享库/脚本/验证三层分离）"
type: "code-pattern"
maturity: "L2-validated"
maturity_note: "基于devcontainer-base 4+变体实战（onnx-quantized/onnx-dev/torch-dev/conda-llvm），从单Dockerfile演进到shared/lib+scripts+三层验证架构"
date: 2026-08-19
source:
  - "retrospective-devcontainer-slim-images-20260819（Phase 2框架化沉淀）"
  - "apps/docker-images/devcontainer-base/variants/shared/（框架参考实现）"
related_patterns:
  - "docker-image-variant-incremental-inheritance.md"
  - "docker-gpu-slimming-sop.md"
  - "docker-build-four-layer-verification.md"
  - "checklist-to-assertion-conversion.md"
tags: ["docker", "dockerfile", "variant", "framework", "shared-library", "bash", "verification", "multi-arch", "slim"]
validation_count: 1
reuse_count: 0
---

# Docker多变体框架化模式（共享库/脚本/验证三层分离）

> **一句话总结**：当Docker项目超过2个变体（variant）时，将清理函数、验证函数、专项分析脚本提取到`shared/`目录分三层组织（lib函数库 + scripts可执行脚本 + config配置），变体Dockerfile只声明变量和调用框架函数，彻底消除代码重复。

## 触发场景

- Docker项目有2个及以上变体（如base/onnx/torch/gpu等），Dockerfile之间存在大量重复的安装/清理/验证代码
- 新增一个变体需要复制粘贴50+行已有代码，容易遗漏关键步骤
- 某个清理/修复逻辑在多个Dockerfile中重复，修改一处需要同步修改所有变体
- 验证逻辑（smoke test/import check）在各变体中重复实现，标准不一致
- 发现"忘记调用cleanup_binaries"这类遗漏错误（因验证函数未在变体Dockerfile中复制）

**不适用于**：
- 单变体Docker项目（无重复问题，不需要框架化）
- 简单Dockerfile（<50行，无复杂清理/验证逻辑）
- 完全独立的不同镜像（无共享基础层/安装逻辑）

## 问题本质

多变体Docker项目的常见演进路径：

1. **阶段0**：单个Dockerfile，所有逻辑内联，没问题
2. **阶段1**：新增变体，复制Dockerfile修改部分内容 → **代码重复**
3. **阶段2**：修复bug时只改了一个变体，其他变体遗留相同bug → **一致性问题**
4. **阶段3**：新增清理/验证函数，每个变体都要COPY+调用 → **调用遗漏**
5. **阶段4**：脚本权限设置用`RUN chmod +x`增加额外层 → **CoW膨胀**

根本矛盾：**多变体的共性逻辑（清理/验证/安装框架）和变体特性（具体包/专项测试）未分离**，导致重复→不一致→遗漏的链式问题。

## 核心做法

### 目录结构（三层分离）

```
variants/
├── shared/                    # 框架层（所有变体共享）
│   ├── lib/                   # L1: bash函数库（source引入，不直接执行）
│   │   ├── cleanup.sh         #   清理函数集合（cleanup_binaries/cleanup_all/cleanup_torch_dev/cleanup_post_tests）
│   │   └── verify.sh          #   验证函数集合（verify_smoke_basic/verify_gpu_smoke/verify_slim_delete_preserve/verify_all_slim_gpu）
│   ├── scripts/               # L2: 可执行脚本（COPY --chmod=755，直接运行）
│   │   └── r2-dtneeded-analysis.sh  # R2 DT_NEEDED深度分析脚本（4模式）
│   └── config/                # L3: 配置文件（包列表/环境变量/版本约束）
│       └── conda-env.yml      #   （可选：conda环境定义）
├── onnx-quantized/
│   └── Dockerfile             # 变体层：只声明变体特性+调用框架
├── torch-dev/
│   └── Dockerfile             # 变体层：只声明变体特性+调用框架
└── conda-llvm/
    └── Dockerfile             # 变体层：只声明变体特性+调用框架
```

### Dockerfile框架集成模板

```dockerfile
# ══════════════════════════════════════════════════════════════
# S1：基础安装层（从base镜像继承 + 变体专属安装）
# ══════════════════════════════════════════════════════════════
FROM devcontainer-base:latest AS S1
# ... 变体专属安装步骤（pip/conda/apt install）...

# ══════════════════════════════════════════════════════════════
# S2：清理瘦身层（调用框架函数，零重复代码）
# ══════════════════════════════════════════════════════════════
FROM S1 AS S2

# 1. 首先复制框架脚本（权限在COPY时设置，避免额外RUN chmod层）
COPY shared/lib/cleanup.sh /usr/local/share/variant-framework/cleanup.sh
COPY shared/lib/verify.sh /usr/local/share/variant-framework/verify.sh
COPY --chmod=755 shared/scripts/r2-dtneeded-analysis.sh /usr/local/share/variant-framework/r2-dtneeded-analysis.sh

# 2. source框架函数库
RUN . /usr/local/share/variant-framework/cleanup.sh && \
    . /usr/local/share/variant-framework/verify.sh && \
    \
    # 3. 框架通用清理（所有变体必须调用）
    cleanup_binaries && \
    \
    # 4. 变体专项清理（按需调用，非通用）
    # cleanup_torch_dev && \    # GPU/ML变体启用
    # cleanup_onnx_dev && \     # ONNX变体启用（未来扩展）
    \
    # 5. 框架通用验证
    verify_all_slim_gpu && \
    \
    # 6. 变体专项验证（每个变体独有）
    echo -n "  [VERIFY] devuser torch import... " && \
    su - devuser -c "python -c 'import torch;print(\"torch OK\")'" >/dev/null 2>&1 \
        && echo "[OK]" || { echo "[FAIL]"; exit 1; } && \
    \
    # 7. 测试后清理（pycache等）——必须在所有VERIFY之后
    cleanup_post_tests

# ══════════════════════════════════════════════════════════════
# S3：元数据层（标签+声明）
# ══════════════════════════════════════════════════════════════
FROM scratch AS metadata
LABEL org.opencontainers.image.title="devcontainer-base:<variant>-slim" \
      org.opencontainers.image.slimmed="R1+R2+strip+cow-optimized"
```

### 函数库设计原则

#### lib/cleanup.sh：清理函数分层设计

```bash
#!/bin/bash
# shared/lib/cleanup.sh - 框架清理函数库
# 原则：函数粒度适中——通用函数处理80%场景，专项函数处理20%变体差异

# L1-通用：所有变体必须调用的基础清理
cleanup_binaries() {
    echo "[CLEANUP] cleanup_binaries..."
    # strip共享库、删除静态库/bitcode、清理apt缓存
    find /opt/conda -name "*.so" -exec strip --strip-unneeded {} \; 2>/dev/null || true
    find /opt/conda -name "*.a" -delete 2>/dev/null || true
    find /opt/conda -name "*.bc" -delete 2>/dev/null || true
    # ...
}

# L2-专项：按变体类型选择调用
cleanup_torch_dev() {
    echo "[CLEANUP] cleanup_torch_dev..."
    _del_torch "nvidia/cu13/lib/libcusolverMg.so.12"
    _del_torch "nvidia/cudnn/lib/libcudnn_engines_runtime_compiled.so.9"
    # R1确定项删除
    # 调用r2-dtneeded-analysis.sh做深度分析
    /usr/local/share/variant-framework/r2-dtneeded-analysis.sh --delete
}

# L3-后处理：验证后清理（pycache等）
cleanup_post_tests() {
    find /opt/conda -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find /opt/conda -name "*.pyc" -delete 2>/dev/null || true
}
```

#### lib/verify.sh：验证函数安全设计

```bash
#!/bin/bash
# shared/lib/verify.sh - 框架验证函数库
# 原则：验证函数必须安全——非适用场景自动SKIP而非FAIL

verify_all_slim_gpu() {
    verify_validation_header "GPU/ML Slim Validation (SOP Step 4)"

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

verify_slim_delete_preserve() {
    # 断言关键项已删除/已保留——build-time回归防护
    local deleted_ok=0
    # 检查应删除项不存在
    for item in "${DELETED_ITEMS[@]}"; do
        if [ -e "$target/$item" ]; then
            echo "  [FAIL] Item should have been deleted: $item"; return 1
        fi
    done
    # 检查应保留项存在
    for item in "${PRESERVED_ITEMS[@]}"; do
        if [ ! -e "$target/$item" ]; then
            echo "  [FAIL] Item should have been preserved: $item"; return 1
        fi
    done
}
```

### 关键设计决策

| 决策 | 做法 | 理由 |
|------|------|------|
| **COPY权限设置** | 用`COPY --chmod=755`而非`RUN chmod +x` | 避免额外RUN层导致CoW膨胀 |
| **函数vs脚本** | 通用可组合逻辑→lib函数库；专项独立工具→scripts | 函数支持source+组合调用；脚本支持独立执行和--flag参数 |
| **非适用场景** | verify函数检测前置条件，不满足则SKIP返回0 | 变体Dockerfile可无条件调用框架函数，无需if-else守卫 |
| **函数命名** | `cleanup_<scope>`/`verify_<scope>` | 自描述命名，变体Dockerfile读起来像文档 |
| **错误处理** | 验证失败`{ echo "[FAIL]"; exit 1; }` | build-time立即失败，不生成有问题的镜像 |

## 反模式

### ❌ 反模式1：每个变体Dockerfile内联复制清理代码

```dockerfile
# 错误：每个Dockerfile都重复相同的清理逻辑
RUN find /opt/conda -name "*.a" -delete && \
    find /opt/conda -name "*.bc" -delete && \
    strip --strip-unneeded ... && \
    # ... 30行重复代码 ...
# 问题：修复一个清理逻辑要改所有变体Dockerfile，容易遗漏
```

**正确做法**：提取到`shared/lib/cleanup.sh`，各变体调用`cleanup_binaries`。

### ❌ 反模式2：RUN chmod +x设置脚本权限

```dockerfile
# 错误：额外RUN层只为chmod
COPY shared/scripts/analyze.sh /usr/local/bin/analyze.sh
RUN chmod +x /usr/local/bin/analyze.sh
# 问题：chmod修改文件属性触发CoW，上层复制完整文件副本
```

**正确做法**：`COPY --chmod=755 source target`，复制时设置权限，零额外层。

### ❌ 反模式3：验证函数在不适用场景报错而非跳过

```bash
# 错误：非GPU变体调用GPU验证直接报错
verify_gpu_smoke() {
    python -c "import torch; torch.randn(3,3).cuda()"
    # 如果torch未安装，直接报错退出build
}
# 问题：非GPU变体需要if-else守卫，Dockerfile变复杂
```

**正确做法**：函数内部检测前置条件：
```bash
verify_all_slim_gpu() {
    if ! python -c "import torch" 2>/dev/null; then
        echo "  [SKIP] not a GPU variant"; return 0
    fi
    # GPU验证逻辑...
}
```

### ❌ 反模式4：cleanup在verify之前调用（清理顺序错误）

```dockerfile
# 错误：先清理后验证
RUN cleanup_all && verify_all
# 问题：verify产生的__pycache__无法被cleanup清理
```

**正确做法**：严格按SOP顺序：安装 → 清理R1/R2 → 验证 → post_tests清理。

### ❌ 反模式5：框架脚本COPY路径在RUN之后

```dockerfile
# 错误：使用脚本但没先COPY
RUN cleanup_torch_dev  # cleanup_torch_dev函数在cleanup.sh中
COPY shared/lib/cleanup.sh ...  # 太晚了！
```

**正确做法**：S2层第一步是COPY所有框架文件，然后source+调用。

## 迁移指南：从单Dockerfile到框架化

### Step 1：识别共性逻辑

```bash
# 在多变体Dockerfile中找重复行
grep -h "RUN\|COPY" variants/*/Dockerfile | sort | uniq -c | sort -rn | head -20
# 出现≥2次的RUN命令就是提取候选
```

### Step 2：创建shared/目录结构

```bash
mkdir -p variants/shared/{lib,scripts,config}
touch variants/shared/lib/cleanup.sh
touch variants/shared/lib/verify.sh
chmod +x variants/shared/scripts/*.sh
```

### Step 3：逐变体迁移（一次一个，验证通过后再迁移下一个）

```bash
# 1. 迁移第一个变体（推荐从最复杂的开始，如GPU/ML变体）
# 2. docker build验证功能正常
# 3. 迁移第二个变体
# 4. 对比旧新镜像大小/功能
# 5. 删除旧的重复代码
```

## 实战案例

### 案例1：devcontainer-base从3变体到框架化（2026-08-19）

**迁移前**：3个变体Dockerfile各含50-80行清理/验证代码，重复率>70%。

**关键事件**：torch-dev变体忘记调用`cleanup_binaries`导致10.2GB大镜像，暴露了代码重复带来的调用遗漏问题。

**迁移后**：
- `shared/lib/cleanup.sh`：4个清理函数（cleanup_binaries/cleanup_torch_dev/cleanup_all/cleanup_post_tests）
- `shared/lib/verify.sh`：3个验证函数（verify_slim_delete_preserve/verify_gpu_smoke/verify_all_slim_gpu），含非GPU安全跳过
- `shared/scripts/r2-dtneeded-analysis.sh`：DT_NEEDED分析4模式
- 变体Dockerfile：S2层从60+行减少到15行（COPY+source+调用框架+专项验证）

**收益**：新增变体只需调用`verify_all_slim_gpu`，自动获得CPU+GPU+删除保留+权限验证，无需复制任何验证代码。

## 关键参考

| 参考 | 说明 |
|------|------|
| [variants/shared/](../../../../apps/docker-images/devcontainer-base/variants/shared) | 本项目框架参考实现 |
| [docker-gpu-slimming-sop.md](docker-gpu-slimming-sop.md) | GPU/ML瘦身SOP（本框架的功能实现依据） |
| [docker-image-variant-incremental-inheritance.md](docker-image-variant-incremental-inheritance.md) | Docker变体增量继承模式 |
| [docker-cow-same-layer-modification.md](docker-cow-same-layer-modification.md) | CoW同层修改原则（COPY --chmod避免chmod层的依据） |
| [checklist-to-assertion-conversion.md](checklist-to-assertion-conversion.md) | 检查清单到断言转换模式（verify_delete_preserve的设计依据） |
