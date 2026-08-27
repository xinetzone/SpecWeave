---
id: "torch-dev-extra-index-cuda-assertion"
title: "ADR: torch-dev 双索引下载与 CUDA 硬断言决策"
x-toml-ref: ""
category: "decisions"
tags: ["devcontainer", "torch-dev", "pip-mirror", "cuda", "extra-index", "silent-downgrade", "verify", "镜像构建"]
date: "2026-08-20"
status: accepted
author: ""
summary: "记录 torch-dev 镜像构建中为解决 files.pythonhosted.org IPv6 不可达而引入 --extra-index-url 双索引下载，以及对抗审查后补充的 CUDA 编译版本硬断言，防止主索引故障时静默降级为 CPU 版 torch"
source: "torch-dev-mirror-build-retrospective-20260820"
---
# ADR: torch-dev 双索引下载与 CUDA 硬断言决策

## 背景

`devcontainer-base:torch-dev` 变体镜像（onnx-quantized → torch-dev 链）安装 free-threading PyTorch（cp314t，CUDA cu130）时，`files.pythonhosted.org` 的 IPv6 地址不可达（IPv6 12 秒无响应，IPv4 正常），导致 `cuda_bindings-13.3.1-cp314t` wheel 下载失败，构建中断。

本次决策围绕两个问题：①如何在不依赖不可达主索引的情况下完成依赖下载；②如何防止"备用源静默降级"这一新引入风险的逃逸。

---

## DM-001: 采用 `--extra-index-url` 双索引下载，以阿里云 PyPI 为备用源

**结论**：扩展 `pip_install_group` 支持 `--index-url` + `--extra-index-url` 参数，torch-dev 以 `https://download.pytorch.org/whl/cu130` 为主索引、`https://mirrors.aliyun.com/pypi/simple/` 为备用源。
**状态**：✅ 已实施（提交 6be62c82）

### 决策理由

| 维度 | 分析 |
|------|------|
| 根因 | `files.pythonhosted.org` IPv6 不可达（F05），IPv4 正常（F06）；`download.pytorch.org`（CloudFront）IPv6 可达（F08） |
| 主索引 | PyTorch 官方 cu130 索引，提供 torch/torchvision 主 wheel（526MB） |
| 备用源 | 阿里云 PyPI 镜像（IPv4 可达），提供 `cuda_bindings` 等 PyPI 侧依赖兜底 |
| 验证 | `cuda_bindings-13.3.1-cp314t` 经阿里云成功下载（F12），镜像构建成功 8.22GB，torch 2.13.0+cu130（F13/F15） |

### 影响范围

- `pip_install_group` 新增 `--extra-index-url` 参数解析（install-helpers.sh）
- torch-dev Dockerfile 安装组传入双索引
- 共享 helper 通过 `COPY` 覆盖基础层文件使参数生效（临时补丁，全链重建后移除）

### 备选方案对比

| 方案 | 结果 |
|------|------|
| 仅轮询重试主索引 | ❌ IPv6 不可达是确定性网络问题，重试无效 |
| 直接切换 index-url 为阿里云 | ❌ 阿里云无 cu130 构建（仅 CPU 2.9.1），torch 会静默装错版本 |
| **双索引（主+备用）** | ✅ 主索引负责 CUDA 版本，备用源兜底 PyPI 依赖 |

---

## DM-002: CUDA 编译版本硬断言，防止备用源静默降级

**结论**：在 torch-dev Dockerfile Stage 3 增加 `torch.version.cuda` 硬断言，检测到 CPU 构建（版本为空）时构建 FAIL，而非 SKIP。
**状态**：✅ 已实施

### 决策理由

| 维度 | 分析 |
|------|------|
| 风险 | 阿里云镜像仅有 CPU 版 torch 2.9.1（无 cu130 构建，F21），若主索引故障，pip 合并取最高版本会静默安装 CPU 版 |
| 现有防线缺陷 | verify.sh `verify_all_slim_gpu` 中 CUDA 不可用时打印 `[SKIP]` + `sys.exit(0)`（F24），会放过所有 GPU 相关错误——构建"成功"但运行时 CUDA 不可用 |
| 断言依据 | 构建环境无 GPU，`torch.cuda.is_available()` 恒为 False 不可用；`torch.version.cuda`（编译时 CUDA 版本）在 CUDA 构建返回非空（如 13.0），CPU 构建返回 None——可精确区分 |
| 验证 | 实测：真实 CUDA torch → PASS（`torch.version.cuda=13.0`）；模拟 CPU（None）→ 正确 FAIL |

### 影响范围

- torch-dev Dockerfile Stage 3 新增 P1 断言块
- 不影响 verify.sh（保持共享函数不动，仅变体层加固）
- 下游 ai-dev 继承 torch-dev 时自动获得该防线

### 备选方案对比

| 方案 | 结果 |
|------|------|
| 修改 verify.sh 的 SKIP 为 FAIL | ❌ 影响所有 GPU/ML 变体（onnx-pytorch 等），范围过大 |
| **变体层硬断言 torch.version.cuda** | ✅ 仅 torch-dev 生效，单一职责，不波及其他变体 |
| 锁定版本 `torch==2.13.0+cu130` | 🔄 后续行动项（A-2），与断言互补（防 beta 漂移） |

---

## DM-003: 镜像构建"下载层 + 验证层"双保险原则

**结论**：网络/镜像修复必须同步补充验证层断言——下载层解决"装得上"，验证层兜住"装得对"。
**状态**：✅ 已采纳（方法论沉淀）

### 决策理由

| 维度 | 分析 |
|------|------|
| 洞察 | 下载层的 `--extra-index-url` 是绕行而非根治——`files.pythonhosted.org` IPv6 根因仍在（F05 复测仍不可达） |
| 反常识 | 直觉认为"修好下载=修好问题"；实际下载层修复只覆盖当前一个包，验证层 `[SKIP]+exit(0)` 才是静默失败的关键入口 |
| 模式 | E-1：镜像依赖「主索引+备用源」双通道下载（extra-index mirror fallback）——含验证层断言步骤 |

### 影响范围

- 后续所有涉及多索引下载的镜像变体（onnx-dev/ai-dev 等）必须同步补验证断言
- 沉淀为可复用模式 E-1，归档至本 ADR

---

## 参考链接

- [里程碑复盘报告](../../../../docs/retrospective/reports/milestone/torch-dev-mirror-build-retrospective-20260820.md)
- [torch-dev Dockerfile](../../../../apps/docker-images/devcontainer-base/variants/torch-dev/Dockerfile)
- [install-helpers.sh](../../../../apps/docker-images/devcontainer-base/variants/shared/lib/install-helpers.sh)
- [verify.sh](../../../../apps/docker-images/devcontainer-base/variants/shared/lib/verify.sh)
