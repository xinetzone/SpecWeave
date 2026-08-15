---
id: "docs-tech-release-onnx-pytorch-v1-1"
title: "onnx-pytorch v1.1.0 发布说明"
category: "tech"
date: "2026-08-15"
source: "apps/docker-images/devcontainer-base/variants/onnx-pytorch/RELEASE.md"
---

# onnx-pytorch v1.1.0 发布清单（Release Manifest）

> 本清单基于已构建并验证通过的 `devcontainer-base:onnx-pytorch-latest`（**v1.1.0**）镜像生成。
> 运行时元数据源：容器内 `/etc/devcontainer-variant-onnx-pytorch-build-info`（构建时自动写入）。
> 验证依据：[test-onnx-pytorch.sh](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/scripts/test-onnx-pytorch.sh) **23 项测试全部 PASS（0 FAIL）**（2026-08-15）。
> 源文件：[variants/onnx-pytorch/RELEASE.md](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-pytorch/RELEASE.md)

## 1. 镜像标识

| 项目 | 值 |
|------|-----|
| 镜像名称 | `devcontainer-base` |
| 变体标签 | `onnx-pytorch-latest`（滚动） |
| 完整引用 | `devcontainer-base:onnx-pytorch-latest` |
| 镜像大小 | 1.45 GiB（1,448,248,185 bytes） |
| 架构 | x86_64 (amd64) |
| 基础系统 | Ubuntu 26.04 LTS |
| 基础镜像 | `devcontainer-base:conda-llvm-${BASE_TAG}` |

## 2. 发布元数据

| 项目 | 值 |
|------|-----|
| 版本 | **v1.1.0**（架构适配版） |
| 变体层构建日期 | 2026-08-14T16:20:50Z（UTC）/ 2026-08-15 00:20:50 CST |
| 构建环境 | WSL2 / Linux + Docker BuildKit |
| 构建命令 | `bash variants/build.sh --variant onnx-pytorch --cn` |
| 验证状态 | ✅ 23/23 测试通过（0 FAIL） |
| Build-Info 路径 | `/etc/devcontainer-variant-onnx-pytorch-build-info` |
| torch 环境 | conda **base 环境**（`/opt/conda/bin`，Python 3.13.13，**GIL 启用**） |
| Jupyter 环境 | conda **main 环境**（`/opt/conda/envs/main/bin`，Python 3.14.6 free-threading，GIL 禁用） |
| PATH 优先级 | `conda-bin-first`（`/opt/conda/bin` 置于最前，torch/onnx 直达） |

## 3. v1.1.0 变更总结（v1.0.x → v1.1.0）

**核心变更**：适配 conda-llvm 基础镜像布局迁移（jupyter 服务移至 main 环境），新增架构守卫与生态完整性测试，补齐 AGENTS.md/RELEASE.md 发布资产。

### 3.1 变更清单

| 类别 | 变更 | 说明 |
|------|------|------|
| **缺陷修复** | VALIDATE 7/10 jupyter 路径 | 原硬编码 `/opt/conda/bin/jupyter`（基础镜像迁移后不存在，导致构建 exit 127）；改为 supervisord 实际使用的 `/opt/conda/envs/main/bin/jupyter` |
| **测试增强** | 20 → 23 项 | 新增 T21 GIL 启用守卫、T22 ONNX 生态完整导入（onnxsim/onnxoptimizer/onnxscript）、T23 devuser 功能验证 |
| **资产补齐** | AGENTS.md / RELEASE.md | 新增变体级 AI 入口（含 base 环境 GIL 启用架构约束）；本发布清单 |
| **文档修正** | README / .agents 规则 | `/opt/venv` 与 `/opt/conda/bin/jupyter` 过时引用 → main 环境 jupyter 绝对路径 |
| **构建同步** | build.sh 验证命令 | 新增 GIL 启用正向断言 + ONNX 生态导入验证 |

### 3.2 关键架构事实（v1.1.0 确立）

| 环境 | Python | GIL | 角色 |
|------|--------|-----|------|
| base（`/opt/conda/bin`） | 3.13.13 | **启用** | torch/onnx/onnxruntime 训练导出环境（PATH 优先） |
| main（`/opt/conda/envs/main/bin`） | 3.14.6 cp314t | 禁用（free-threading） | Jupyter 服务（supervisord 绝对路径启动） |

- **架构正交**：本变体用 base 环境（GIL 启用）承载 torch 生态；onnx-dev/onnx-quantized 用 main 环境（free-threading）承载纯 ONNX 生态。
- **onnxoptimizer 本变体保留**（base GIL 启用无兼容问题），与 onnx-dev/onnx-quantized 的排除策略形成直接对比。

## 4. 版本矩阵（实测值）

| 组件 | 实际版本 | 环境 | 类型 |
|------|---------|------|------|
| Python | 3.13.13（标准构建，GIL 启用） | base | torch 运行时 |
| Python | 3.14.6（cp314t free-threading） | main | Jupyter 服务 |
| PyTorch | 2.13.0+cpu | base | 深度学习框架 |
| torchvision | 0.28.0+cpu | base | 视觉工具包 |
| ONNX | 1.22.0 | base | 模型格式 |
| ONNX Runtime | 1.28.0 | base | 推理引擎 |
| ONNX Script | 0.7.1 | base | 脚本工具 |
| ONNX Simplifier | v0.7.3 | base | 模型简化 |
| onnxoptimizer | 0.4.2 | base | 图优化（本变体保留） |
| Conda | 26.3.2 | - | 包管理器 |
| LLVM / Clang | 22.1.8 | main | 编译工具链（继承 conda-llvm） |
| CUDA | **不可用**（False，CPU 构建） | - | by design |

> `PACKAGES_INSTALLED=torch,torchvision,onnx,onnxruntime,onnx-simplifier,onnxoptimizer,onnxscript`
> `PYTHON_ENV=conda-base` / `INSTALL_ENV=base` / `PATH_PRIORITY=conda-bin-first`
> `ACTIVATION_SCRIPT=/etc/profile.d/onnx-pytorch-init.sh`（login shell 后备兼容）

## 5. 依赖链

```
devcontainer-base:${BASE_TAG}    # 基础镜像（Ubuntu 26.04 + SSH + Docker DinD + Jupyter + Miniforge3）
        │
        ▼ (FROM)
devcontainer-base:conda-llvm-*   # LLVM 22.1.8 / Clang / CMake / Ninja
        │
        ▼ (FROM)
devcontainer-base:onnx-pytorch-* # 本镜像（PyTorch CPU + ONNX 生态追加层）
```

- 依赖链上的 `conda-llvm` 在本地存在时可直接 `docker build -f variants/onnx-pytorch/Dockerfile` 跳过全链重建（本 v1.1.0 即采用此路径构建）。
- 跨变体工作流：本镜像 `torch.onnx.export` 导出的 `.onnx` 移交 `onnx-quantized` 变体量化。

## 6. 构建参数（本次构建值）

| 参数 | 本次值 | 默认值 |
|------|-------|--------|
| `BASE_TAG` | `latest` | `latest` |
| `APT_MIRROR` | `aliyun`（--cn） | `official` |
| `CONDA_MIRROR` | `tuna`（--cn） | `official` |
| `PIP_MIRROR` | `aliyun`（--cn） | `official` |
| `TORCH_INDEX_URL` | `https://download.pytorch.org/whl/cpu` | 同上 |

## 7. 验证结果（23 项测试，2026-08-15）

| 层级 | 测试范围 | 用例 | 结果 |
|------|---------|------|------|
| L1 工具链 | torch/torchvision/onnx/onnxruntime 版本、CUDA 缺席 | T1-T6 | ✅ |
| L2 导出与推理 | torch 张量 op、ONNX 导出、ORT 推理 | T7-T9 | ✅ |
| L3 服务继承 | sshd / dockerd DinD / jupyter / supervisord / devuser | T10-T16 | ✅ |
| L4 环境纯净 | `/opt/venv` 移除、PATH 优先级 | T17-T18 | ✅ |
| L5 构建信息 | build-info、.condarc | T19-T20 | ✅ |
| **L6 新增守卫** | **T21 GIL 启用（base 标准构建）、T22 ONNX 生态完整导入、T23 devuser 功能** | T21-T23 | ✅ |

**汇总**：`TOTAL: 23 | PASSED: 23 | FAILED: 0`

> 运行验证：`bash variants/scripts/test-onnx-pytorch.sh --tag latest`

## 8. 使用方式

```bash
# 交互式进入容器
docker run -it --rm --privileged devcontainer-base:onnx-pytorch-latest bash

# 快速验证 torch + ONNX + ORT
docker run --rm devcontainer-base:onnx-pytorch-latest \
  /opt/conda/bin/python -c "import torch,onnx,onnxruntime;print(torch.__version__,onnx.__version__,onnxruntime.__version__)"

# 开发模式（SSH + Jupyter + DinD）
docker run -d --privileged -p 2222:22 -p 8888:8888 -p 2375:2375 \
  -e USER_PASSWORD=devpass -e JUPYTER_TOKEN=devtoken \
  -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
  devcontainer-base:onnx-pytorch-latest

# 查看构建元数据
docker run --rm devcontainer-base:onnx-pytorch-latest \
  cat /etc/devcontainer-variant-onnx-pytorch-build-info
```

## 9. 使用注意

1. **Python 路径**：torch/onnx 位于 conda **base 环境**（`/opt/conda/bin/python`），PATH 已优先。
2. **Jupyter 服务**：由 supervisord 以 main 环境绝对路径 `/opt/conda/envs/main/bin/jupyter` 启动，与 base torch 环境解耦，不受 PATH 变更影响。
3. **CPU 版 PyTorch**：`torch.cuda.is_available() == False`（CPU 专用索引安装），不含 CUDA 支持。
4. **量化工作流**：本镜像完成训练/导出后，将 `.onnx` 拷入 `onnx-quantized` 变体执行 INT8/FP16 量化（onnxoptimizer 图优化可在本镜像先行完成）。
5. **网络**：PyTorch CPU wheel 默认从 `https://download.pytorch.org/whl/cpu` 下载；不可达时设 `TORCH_INDEX_URL=https://mirrors.tuna.tsinghua.edu.cn/pytorch-wheels/cpu`。

## 10. 变更记录

| 日期 | 变更 |
|------|------|
| 2026-08-15 | **v1.1.0 发布**：修复 jupyter 路径（base→main 环境，exit 127）；测试增强 20→23 项（GIL 启用守卫/生态导入/devuser）；新增 AGENTS.md 与 RELEASE.md；README/.agents 规则过时引用修正；build.sh 验证命令同步。23/23 测试通过 |
| 此前 | v1.0.x：基于 conda-llvm（PyTorch CPU + ONNX 生态），jupyter 路径假设 `/opt/conda/bin`（基础镜像迁移前成立） |

## 11. 相关文档

- [onnx-pytorch 变体 README](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-pytorch/README.md)
- [变体 AGENTS.md（AI 入口）](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-pytorch/AGENTS.md)
- [onnx-quantized 发布清单（量化下游变体）](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-quantized/RELEASE.md)
- [onnx-dev 变体 README（纯 ONNX 架构对偶）](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/onnx-dev/README.md)
- [conda-llvm 变体 README（依赖上游）](https://gitcode.com/daoCollective/SpecWeave/blob/main/apps/docker-images/devcontainer-base/variants/conda-llvm/README.md)
