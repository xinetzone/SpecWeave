---
id: "docs-tech-release-onnx-quantized-v2"
title: "onnx-quantized v2.0.0 发布说明"
category: "tech"
date: "2026-08-14"
source: "apps/docker-images/devcontainer-base/variants/onnx-quantized/RELEASE.md"
---

# onnx-quantized v2.0.0 发布清单（Release Manifest）

> 本清单基于已构建并验证通过的 `devcontainer-base:onnx-quantized-latest`（**v2.0.0**）镜像生成。
> 运行时元数据源：容器内 `/etc/devcontainer-variant-onnx-quantized-build-info`（构建时自动写入）。
> 验证依据：[test-onnx-quantized.sh](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/scripts/test-onnx-quantized.sh) **24 项测试全部 PASS（0 FAIL）**，连续两轮复跑均通过（2026-08-14）。
> 源文件：[variants/onnx-quantized/RELEASE.md](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-quantized/RELEASE.md)

## 1. 镜像标识

| 项目 | 值 |
|------|-----|
| 镜像名称 | `devcontainer-base` |
| 变体标签 | `onnx-quantized-latest`（滚动） |
| 完整引用 | `devcontainer-base:onnx-quantized-latest` |
| 镜像大小 | 1.15 GiB（1,232,880,320 bytes） |
| 架构 | x86_64 (amd64) |
| 基础系统 | Ubuntu 26.04 LTS |

## 2. 发布元数据

| 项目 | 值 |
|------|-----|
| 版本 | **v2.0.0**（架构迁移版） |
| 变体层构建日期 | 2026-08-14T15:18:20Z（UTC） |
| 构建环境 | WSL2 / Linux + Docker BuildKit |
| 构建命令 | `bash variants/build.sh --variant onnx-quantized --cn` |
| 验证状态 | ✅ 24/24 测试通过（0 FAIL，连续两轮复跑） |
| Build-Info 路径 | `/etc/devcontainer-variant-onnx-quantized-build-info` |
| Python 环境 | conda **main 环境**（Python 3.14.6 cp314t **free-threading**，GIL 禁用） |
| PATH 优先级 | `conda-main-bin-first`（`/opt/conda/envs/main/bin` 置于最前） |

## 3. v2.0.0 变更总结（v1.0.0 → v2.0.0）

**核心变更**：基础镜像从 `onnx-pytorch` 切换为 `onnx-dev`，全面继承 free-threading main 环境架构，**移除 PyTorch 依赖**。

### 3.1 架构迁移对比

| 方面 | v1.0.0（旧） | v2.0.0（新） |
|------|--------------|--------------|
| **基础镜像** | onnx-pytorch（含 PyTorch 2.13.0+cpu） | **onnx-dev**（纯 ONNX 生态） |
| **依赖链** | base → conda-llvm → onnx-pytorch → 本变体 | base → conda-llvm → onnx-dev → 本变体 |
| **Python 环境** | conda base（GIL 启用） | conda **main**（**free-threading cp314t，GIL 禁用**） |
| **Python 路径** | `/opt/conda/bin/python` | `/opt/conda/envs/main/bin/python` |
| **torch** | 2.13.0+cpu 预装 | **缺席**（负向验证守卫，按需 `pip install torch`） |
| **onnxoptimizer** | 0.4.2 预装 | **排除**（free-threading 不兼容，CPython #111506，以 onnxsim 替代图优化） |
| **量化测试模型构建** | `torch.onnx.export` 导出 | **`onnx.helper` 纯 ONNX 构建**（Gemm/Relu 节点） |
| **free-threading 守卫** | 无 | 构建期双断言：python 构建串含 `cp314t` + `sys._is_gil_enabled() is False` |

### 3.2 迁移过程中的关键缺陷修复

| # | 缺陷 | 修复 |
|---|------|------|
| 1 | onnx 1.22.0 `make_tensor` 默认 `raw=False`，bytes 数据被当字符串解析报错 | 全部 30 处调用补 `raw=True`（Dockerfile 冒烟 + 测试脚本 + 指南文档） |
| 2 | Gemm 权重沿用 PyTorch 布局 `[out_dim, in_dim]`，与 ONNX `transB=0` 默认语义冲突，量化时形状推理失败 | 统一改为 `[in_dim, out_dim]` |
| 3 | T23 断言 `grep "CI Quantization Gate"` 与中文 `--help` 输出不匹配 | 改为稳健断言 `grep "ci_quantization_gate.py"` |
| 4 | 镜像内遗留 `/opt/venv` 旧路径 | 构建期删除并加入 T18 缺席验证 |

### 3.3 保持不变项

- 量化主 API：`onnxruntime.quantization`（动态/静态 INT8、QDQ、FP16、校准）
- 基础服务：sshd / dockerd（DinD）/ podman / jupyter / supervisord 全部保留
- neural-compressor 维持**可选不预装**（3.x 已弃用 ONNX 适配器且需 torch，按需 `pip install neural-compressor torch`）

## 4. 版本矩阵（实测值）

| 组件 | 实际版本 | 类型 | 来源 |
|------|---------|------|------|
| Python | 3.14.6 (cp314t free-threading) | 解释器 | 继承 onnx-dev main 环境 |
| ONNX | 1.22.0 | 模型格式 | 继承 onnx-dev |
| ONNX Runtime | 1.28.0（含 quantization 模块） | 推理引擎 | 继承 onnx-dev |
| ONNX Script | 0.7.1 | 脚本工具 | 继承 onnx-dev |
| ONNX Simplifier | v0.7.3 | 模型简化 | 本层幂等补装 |
| ONNX Converter Common | 1.16.0 | FP16 转换 | **本层新增** |
| LLVM / Clang | 22.1.8 | 编译工具链 | 继承 conda-llvm |
| Conda | 26.3.2 | 包管理器 | 继承基础镜像 |
| ~~PyTorch~~ | **缺席**（by design） | - | v2.0.0 移除，按需自装 |
| ~~onnxoptimizer~~ | **缺席**（by design） | - | v2.0.0 排除（free-threading 不兼容） |

> `PACKAGES_INSTALLED=onnx,onnxruntime,onnxconverter-common,onnxsim,onnxscript`
> `PACKAGES_EXCLUDED=torch,torchvision (by design, inherited from onnx-dev; install on demand); onnxoptimizer (free-threading incompatible, CPython #111506)`

## 5. 依赖链（v2.0.0）

```
devcontainer-base:${BASE_TAG}    # 基础镜像（Ubuntu 26.04 + SSH + Docker DinD + Jupyter + Miniforge3 main 环境）
        │
        ▼ (FROM)
devcontainer-base:conda-llvm-*   # LLVM 22.1.8 / Clang / CMake / Ninja（main 环境）
        │
        ▼ (FROM)
devcontainer-base:onnx-dev-*     # 纯 ONNX 生态（onnx/onnxruntime/onnxsim/onnxscript，free-threading，无 PyTorch）
        │
        ▼ (FROM)
devcontainer-base:onnx-quantized-*  # 本镜像（量化工具链追加层）
```

- 构建依赖校验：`build.sh` 通过 `check_dependency_image()` 在构建前校验 onnx-dev 镜像存在，拓扑排序自动补齐依赖链。
- 量化能力：`QUANTIZATION_MODES=dynamic_int8,static_int8,qdq_int8,fp16,calibration`，Provider：`CPUExecutionProvider`。

## 6. 构建参数（本次构建值）

| 参数 | 本次值 | 默认值 |
|------|-------|--------|
| `BASE_TAG` | `latest` | `latest` |
| `APT_MIRROR` | `aliyun`（--cn） | `official` |
| `CONDA_MIRROR` | `tuna`（--cn） | `official` |
| `PIP_MIRROR` | `aliyun`（--cn） | `official` |
| `NEURAL_COMPRESSOR_VERSION` | 未设置（不预装） | 未设置 |
| `ONNXCONVERTER_COMMON_VERSION` | 未设置（latest=1.16.0） | 未设置 |

## 7. 验证结果（24 项测试，2026-08-14）

| 层级 | 测试范围 | 用例 | 结果 |
|------|---------|------|------|
| L1 基础工具链 | free-threading（cp314t/GIL 禁用）、torch+onnxoptimizer 缺席、onnx/ORT 版本 | T1-T4 | ✅ 4/4 |
| L2 量化工具链导入 | onnxconverter_common.float16、ORT transformers.optimizer、neural_compressor（可选） | T5-T7 | ✅ 3/3 |
| L3 量化执行冒烟 | 纯 ONNX 模型构建 + Checker、动态 INT8、静态 QDQ（MinMax 校准）、FP16 转换 + 推理 | T8-T15 | ✅ 全部 |
| L4 服务继承 | sshd / dockerd DinD / jupyter / supervisord 保留 | T16-T17 | ✅ |
| L5 环境纯净 | `/opt/venv` 移除、PATH main 优先 | T18 | ✅ |
| L6 构建信息 | build-info（onnx-dev base + 量化包版本）、.condarc、OpenMP 环境默认值 | T19-T21 | ✅ 3/3 |
| L7 CI 集成 | onnx_quantize_kit 导入、ci_quantization_gate --help、auto_quantize mock（纯 ONNX） | T22-T24 | ✅ 3/3 |

**汇总**：`TOTAL: 24 | PASSED: 24 | FAILED: 0`（初始验证 + 修复 T23 后复验，连续两轮全绿）

> 运行验证：`bash variants/scripts/test-onnx-quantized.sh --tag latest`

## 8. 使用方式

```bash
# 交互式进入容器
docker run -it --rm --privileged devcontainer-base:onnx-quantized-latest bash

# 快速验证量化能力
docker run --rm devcontainer-base:onnx-quantized-latest \
  /opt/conda/envs/main/bin/python -c \
  "from onnxruntime.quantization import quantize_dynamic, QuantType; print('quantize OK')"

# 开发模式（SSH + Jupyter + DinD）
docker run -d --privileged -p 2222:22 -p 8888:8888 -p 2375:2375 \
  -e USER_PASSWORD=devpass -e JUPYTER_TOKEN=devtoken \
  -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
  devcontainer-base:onnx-quantized-latest

# 查看构建元数据
docker run --rm devcontainer-base:onnx-quantized-latest \
  cat /etc/devcontainer-variant-onnx-quantized-build-info
```

## 9. v1 → v2 迁移指引（使用者视角）

1. **Python 路径**：所有 `/opt/conda/bin/python` 引用改为 `/opt/conda/envs/main/bin/python`
2. **依赖 torch 的工作流**：在外部环境导出 `.onnx` 后拷入容器（推荐），或临时 `pip install torch`（会破坏 torch 缺席负向验证，仅建议临时使用）
3. **需要 onnxoptimizer 的场景**：用 `onnxsim`（已内置）替代图优化
4. **多线程收益**：main 环境为 free-threading 构建，量化数据预处理等 CPU 密集流水线可受益于真正的并行执行
5. **自建模型量化**：用 `onnx.helper` 构建（参考变体 README 使用示例），注意 Gemm 权重布局为 `[in_dim, out_dim]` 且 `make_tensor` 需 `raw=True`

## 10. 变更记录

| 日期 | 变更 | 关联 |
|------|------|------|
| 2026-08-14 | **v2.0.0 发布**：基础镜像迁移 onnx-pytorch → onnx-dev，main 环境 free-threading cp314t，移除 torch/onnxoptimizer（负向验证守卫），量化测试模型纯 ONNX 化，修复 make_tensor raw=True / Gemm 权重布局 / T23 断言三项缺陷，24/24 测试通过 | 架构迁移 |
| 此前 | v1.0.0：基于 onnx-pytorch（PyTorch 2.13.0+cpu，base 环境，GIL 启用） | 首次发布 |

## 11. 相关文档

- [onnx-quantized 变体 README](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-quantized/README.md)
- [高级量化指南（静态量化/校准数据集/QDQ）](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-quantized/ADVANCED-QUANTIZATION-GUIDE.md)
- [量化最佳实践](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-quantized/QUANTIZATION-BEST-PRACTICES.md)
- [基础变体 onnx-dev](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-dev/README.md)
- [构建编排规范](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/.agents/rules/build-orchestration.md)
- [测试规范](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/.agents/rules/testing.md)
- [基础镜像 README](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/README.md)
