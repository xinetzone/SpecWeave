---
id: "milestone-torch-dev-mirror-build-20260820"
title: "torch-dev 镜像构建里程碑复盘报告"
date: "2026-08-20"
completion_date: "2026-08-20"
type: "Report"
description: "torch-dev 镜像构建里程碑复盘报告"
status: "stable"
source: 'd:\spaces\SpecWeave\apps\docker-images\devcontainer-base\variants\torch-dev（Dockerfile + shared/lib/install-helpers.sh + shared/lib/verify.sh）'
milestone-name: "torch-dev 镜像构建与 files.pythonhosted.org IPv6 下载问题修复"
time-range: "2026-08-20"
methodology: "七概念方法论（R→I→E→V→C 链路，里程碑复盘场景）"
quality-gates:
  G1: "事实无因果词 ✅"
  G2: "洞察四元组完整 ✅"
  G3: "模式可迁移验证 ✅"
  G4: "行动项原子化 ✅"
  V: "对抗审查4视角、8项实测、采纳3条修正 ✅"
tags: ["里程碑复盘", "七概念", "devcontainer", "镜像构建", "torch-dev", "IPv6", "pip镜像", "对抗审查"]
generated:
  by: "process:docs-to-okf-conversion"
  at: "2026-08-22T00:00:00Z"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00Z"
stale_after: "2027-08-22"
---

<!-- meta_type: retrospective -->

# torch-dev 镜像构建里程碑复盘报告

> **方法论编排**：七概念 R→I→E→V→C 链路（里程碑复盘场景）
> **复盘对象**：devcontainer-base:torch-dev 变体镜像构建，及构建中暴露的 `files.pythonhosted.org` IPv6 不可达下载问题修复
> **复盘日期**：2026-08-20
> **session**：sc-20260820-torch-dev-mirror
> **基础链**：conda-llvm → onnx-dev → onnx-quantized → torch-dev

---

## 一、里程碑总览

| 指标 | 数值 |
|---|---|
| 目标镜像 | `devcontainer-base:torch-dev-latest` |
| 镜像 ID | `e0bbf3914a90` |
| 镜像大小 | 8.22 GB |
| 构建耗时 | 1181s（Stage 3 PyTorch 安装 + 冒烟测试 1169s） |
| 镜像内 torch | 2.13.0+cu130 |
| 镜像内 torchvision | 0.28.0+cu130 |
| 镜像内 GIL | off（free-threading cp314t） |
| 修复方式 | `pip_install_group` 扩展 `--extra-index-url` + 阿里云备用源 |

---

## 二、R 阶段：事实清单（25 条）

> G1 质量门：✅ 通过（25 条事实均为客观描述，无"因为/所以/导致/错误/失误"等因果推断词）

| 编号 | 事实 |
|------|------|
| F01 | 构建目标为 `devcontainer-base:torch-dev-latest`，位于 `variants/torch-dev/` |
| F02 | 构建环境为 WSL2 Ubuntu，使用 podman 构建 |
| F03 | 依赖链为 conda-llvm → onnx-dev → onnx-quantized → torch-dev |
| F04 | 基础层 `install-helpers.sh` 的 `pip_install_group` 原始版本不支持 `--extra-index-url` 参数 |
| F05 | `files.pythonhosted.org` 解析出 IPv6 地址，IPv6 连接 12 秒无响应 |
| F06 | `files.pythonhosted.org` IPv4 地址正常响应（HTTP 可达） |
| F07 | `cuda_bindings-13.3.1-cp314-cp314t` wheel 因 F05 下载失败，中断构建 |
| F08 | `download.pytorch.org` 使用 CloudFront，IPv6 当前可达（HTTP/2 200） |
| F09 | `pip_install_group` 扩展支持 `--index-url` 与 `--extra-index-url` 参数解析 |
| F10 | torch-dev Dockerfile 传入 `--index-url https://download.pytorch.org/whl/cu130` 与 `--extra-index-url https://mirrors.aliyun.com/pypi/simple/` |
| F11 | torch-dev Dockerfile 显式 `COPY shared/lib/install-helpers.sh` 覆盖基础层文件 |
| F12 | `cuda_bindings` 通过阿里云备用源成功下载 |
| F13 | 镜像构建成功，ID `e0bbf3914a90`，大小 8.22GB |
| F14 | 构建总耗时 1181s，其中 Stage 3 安装与冒烟测试 1169s |
| F15 | 镜像内 torch 版本为 2.13.0+cu130 |
| F16 | 镜像内 torchvision 版本为 0.28.0+cu130 |
| F17 | 镜像内 Python 为 free-threading cp314t，GIL 状态 off |
| F18 | 镜像内 matmul 计算验证通过（shape 断言 OK） |
| F19 | 镜像内量化 API 验证通过（继承自 onnx-quantized） |
| F20 | 镜像内 `install-helpers.sh` sha256 与宿主机文件一致（`b67b9272…`），下游无 helper 漂移 |
| F21 | 阿里云 simple index 中 torch 最高版本为 2.9.1（cp314t），无任何 `+cu130` 本地版本构建 |
| F22 | 阿里云 simple index 中 `cuda-bindings` 存在 13.4.0b1 beta 版本 |
| F23 | torch 2.13.0 对 `cuda-bindings` 的依赖约束为 `<14,>=13.0.3` |
| F24 | verify.sh 第 364-366 行：CUDA 不可用时打印 `[SKIP]` 并 `sys.exit(0)` |
| F25 | pip 全局配置 index-url 为阿里云，retries=5，timeout=120 |

---

## 三、I 阶段：核心洞察（3 条）

> G2 质量门：✅ 通过（每条洞察含四元组：陈述/证据/反常识/行动）

### 洞察 I-1：下载层的绕行修复只是治标，验证层缺陷才是静默失败的关键

| 维度 | 内容 |
|------|------|
| **陈述** | `--extra-index-url` 备用源解决了 `cuda_bindings` 这一包的下载，但 `files.pythonhosted.org` IPv6 不可达的根因仍在（F05 复测仍不可达）；真正能兜住"装错版本/漏装"的防线在验证层，而 verify.sh 的 CUDA 检查在不可用时 `[SKIP]+exit(0)`（F24）会放过所有 GPU 相关错误 |
| **证据** | F05（IPv6 复测仍不可达）、F07（cuda_bindings 下载失败）、F12（备用源成功）、F24（verify.sh SKIP 逻辑） |
| **反常识** | 直觉认为"修好下载=修好问题"；实际上下载层修复只覆盖当前这一个包，若未来主索引故障导致 CPU 版 torch 被安装，验证层 `[SKIP]+exit(0)` 会让构建"成功"，用户直到运行时才发现 CUDA 不可用 |
| **下次行动** | 在 Stage 3 增加 `torch.version.cuda` 硬断言，CUDA 缺失时构建 FAIL 而非 SKIP |

### 洞察 I-2：`--extra-index-url` 的合并语义在正常网络下无害，主索引故障时即成为静默降级通道

| 维度 | 内容 |
|------|------|
| **陈述** | pip 将 `--index-url` 与 `--extra-index-url` 的候选版本合并后取最高版本；阿里云仅有 CPU 版 torch 2.9.1（F21），若主索引不可达，pip 会静默选择 CPU 版完成安装，且版本满足约束（F23） |
| **证据** | F21（阿里云无 cu130 构建）、F23（依赖约束 `<14,>=13.0.3` 过宽）、F22（cuda-bindings beta 版同样满足约束） |
| **反常识** | `--extra-index-url` 双索引在演示/验证时全部正常（主索引可达），风险窗口隐藏在"主索引故障"这一极端场景；而该场景正是当初引入备用源要解决的场景 |
| **下次行动** | 锁定 torch/torchvision/cuda-bindings 精确版本，杜绝 beta 漂移与静默降级 |

### 洞察 I-3：COPY 覆盖共享文件的"临时补丁"模式会导致 helper 版本漂移

| 维度 | 内容 |
|------|------|
| **陈述** | torch-dev 通过显式 `COPY install-helpers.sh`（F11）覆盖基础层文件使 `--extra-index-url` 生效，当前 sha256 一致无漂移（F20），但修改源头 `shared/lib/install-helpers.sh` 才是正解；COPY 补丁使依赖链各层持有不同版本 helper |
| **证据** | F04（基础层原始不支持 extra-index）、F11（COPY 覆盖）、F20（本次无漂移）、Dockerfile 注释（"Remove after next full rebuild"） |
| **反常识** | COPY 覆盖"立即可用"且本次零漂移，容易让人误以为它与源头修改等价；实际任何中间层重建都可能回到旧行为，形成"每层一个补丁"的隐性版本分歧 |
| **下次行动** | 全链重建时移除 COPY 补丁，将 `--extra-index-url` 支持合并入源头 `install-helpers.sh` |

---

## 四、E 阶段：可复用模式（1 个）

> G3 质量门：✅ 通过（模式可迁移至其他镜像构建变体）

### 模式 E-1：镜像依赖「主索引+备用源」双通道下载（extra-index mirror fallback）

| 要素 | 内容 |
|------|------|
| **触发场景** | 主索引（pytorch.org / PyPI）某依赖因网络问题（如 IPv6 不可达）下载失败，需要备用源 |
| **核心步骤** | ①扩展 pip 安装辅助函数支持 `--index-url` 与 `--extra-index-url` 参数；②Dockerfile 传入双索引（主索引为官方、备用源为国内镜像）；③若基础层不含新参数，显式 `COPY` 覆盖共享 helper；④验证层添加 CUDA/版本硬断言（防静默降级）；⑤构建后 `pip freeze` 固化解析清单 |
| **反模式** | 只看主索引日志误判全局网络不可达；只改共享文件不做 COPY 覆盖导致修改不生效；修复下载层后不补验证层断言（静默降级无拦截） |
| **迁移验证** | 已在本变体验证（cuda_bindings 经备用源成功拉取、torch cu130 正常安装、5 项冒烟通过）；可迁移至 onnx-dev / ai-dev / 任何 pip 多索引镜像构建 |

---

## 五、V 阶段：对抗审查记录

> V 门：✅ 通过（4 视角审查、8 项实测、发现 3 级风险、采纳 3 条修正建议）

### 5.1 审查视角与发现

| 视角 | 发现 | 风险级 |
|------|------|--------|
| 魔鬼代言人 | 阿里云无 cu130 构建，主索引故障时静默降级 CPU torch 2.9.1（V4） | 🔴 P1 |
| 魔鬼代言人 | cuda-bindings 阿里云存在 13.4.0b1 beta，满足约束可被选中（V2） | 🟠 P2 |
| 魔鬼代言人 | `--index-url`+`--extra-index-url` 合并取最高版本，时间上解析不同版本（V1/V6） | 🟡 P3 |
| 新人 | COPY 覆盖 hack 导致 helper 版本漂移，靠注释记忆（V5） | 🟡 P3 |
| 老板 | 双索引构建可复现性受损、备用源供应链信任（V6/V7） | 🟡 P3 |
| 未来 | 下游 ai-dev 继承无漂移（sha256 一致）✅（V8） | 无 |

### 5.2 实测验证

| # | 验证项 | 结果 |
|---|--------|------|
| E1 | torch 来源与版本 | ✅ 2.13.0+cu130，来自主索引 |
| E2 | cuda-bindings 版本 | ✅ 13.3.1（非 beta） |
| E3 | 默认 pip 源 | 全局 index-url=阿里云 |
| V1 | 阿里云 torch 版本 | ⚠️ 最高 2.9.1，无 cu130 |
| V1b | 阿里云 cuda-bindings | ⚠️ 13.4.0b1 beta |
| V3 | download.pytorch.org IPv6 | ✅ 当前可达 |
| V3b | files.pythonhosted.org IPv6（根因） | ❌ 仍不可达 |
| V8 | 下游 helper 继承 | ✅ sha256 一致 |

### 5.3 采纳的修正建议（3 条）

1. **【P1】CUDA 断言防静默降级**：Stage 3 增加 `assert torch.version.cuda`，CUDA 缺失时 FAIL
2. **【P2】锁定版本**：`torch==2.13.0+cu130`、`torchvision==0.28.0+cu130`、`cuda-bindings==13.3.1`
3. **【P3】固化解析清单**：构建后 `pip freeze` 写入 build-info

---

## 六、A 阶段：原子行动项（4 项）

> G4 质量门：✅ 通过（每项单一职责、可独立验证）

| 编号 | 行动项 | 风险级 | 验收标准 |
|------|--------|--------|---------|
| A-1 | torch-dev Dockerfile Stage 3 增加 `torch.version.cuda` 硬断言 | P1 | CUDA 缺失时构建 exit≠0 |
| A-2 | 锁定 `torch==2.13.0+cu130` / `torchvision==0.28.0+cu130` / `cuda-bindings==13.3.1` | P2 | `pip show` 版本精确匹配 |
| A-3 | 构建后 `pip freeze` 固化到 build-info | P3 | build-info 含完整解析清单 |
| A-4 | 全链重建时移除 torch-dev COPY 补丁，extra-index 支持合并入源头 helper | P3 | 无 COPY 覆盖层，sha256 仍一致 |

---

## 七、C 阶段：提交记录

| 提交 | 类型 | 说明 |
|------|------|------|
| 待提交 | feat(devcontainer) | pip_install_group 扩展 --extra-index-url + torch-dev 备用源接入（F09-F12） |
| 待提交 | docs(devcontainer) | 本里程碑复盘报告归档 + README 索引更新 |

---

## 八、质量门汇总

| 质量门 | 检查内容 | 结果 |
|:------:|---------|:----:|
| G1 | 事实无因果词（25 条） | ✅ |
| G2 | 洞察四元组完整（3 条） | ✅ |
| G3 | 模式可迁移（E-1 跨变体验证） | ✅ |
| G4 | 行动项原子化（4 项） | ✅ |
| V | 对抗审查有实质内容（4 视角、8 实测、采纳 3 条） | ✅ |

## 九、经验教训

1. **修复须"下载层 + 验证层"双保险**：网络修复解决"装得上"，验证断言兜住"装得对"；只有下载层修复会在主索引故障时产生静默 CPU 降级
2. **备用源引入时同步锁版本**：`--extra-index-url` 合并取最高版本，锁定精确版本是防止 beta/CPU 漂移的必要配套
3. **共享文件修改走源头，不用 COPY 补丁**：COPY 覆盖是临时 hack，全链重建时必须收敛回源头，避免 helper 版本漂移
4. **对抗审查能发现正常验证测不到的风险**：5 项冒烟全过不意味着没有 P1 缺陷，V 阶段 8 项实测揪出静默降级通道
