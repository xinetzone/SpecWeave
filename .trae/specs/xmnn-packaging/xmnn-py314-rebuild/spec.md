# XMNN Python 3.14 Wheel & Docker 镜像重构 - 产品需求文档

## Overview

- **Summary**: 将 xmnn-whl-builder 的构建从 Python 3.13 (cp313 ABI) 迁移到 Python 3.14 (cp314/cp314t ABI)，移除所有 Python 3.13 降级补丁，产出符合 `requires-python = ">=3.14"` 声明的 wheel 和 Docker 镜像。
- **Purpose**: 当前 Dockerfile 故意反转 PATH 使用 base env 的 Python 3.13，build-wheel.sh 通过 sed 将版本检查降级到 3.13，产出 cp313 wheel——与 pyproject.toml 声明的 `>=3.14` 和用户硬性要求矛盾。Nuitka 4.1 已声明支持 Python 3.14，需验证 cp314t free-threading 兼容性并完成迁移。
- **Target Users**: 使用 xmnn-whl-builder 镜像进行 NPU 推理开发的工程师；依赖 `/opt/xmnn-dist/` wheel 的下游 runtime 镜像。

## Goals

- 最终镜像内 `python --version` 输出 Python 3.14.x
- 产出的 wheel 文件 ABI 标签为 `cp314` 或 `cp314t`
- verify-wheel.sh 全部验证项 PASS（含 tvm.build LLVM 计算验证）
- 将 base env 从 Python 3.13 升级到 3.14 cp314（GIL enabled），PATH 保持 base first + main second（base 提供 cp314 Python，main 提供 clang/LLVM 工具链）
- 移除 build-wheel.sh 中的 sed 版本降级补丁
- Jupyter kernel 注册逻辑适配双环境布局（base env cp314 提供 xmnn 运行时，main env cp314t 提供 Jupyter 服务）
- 从零构建完整基础镜像链（conda → conda-llvm → onnx-dev → onnx-quantized）

## Non-Goals

- 不修改 npu_tvm / npuusertools 源码（bind mount 只读挂载，AST PREAMBLE 注入机制保持不变）
- 不升级或更换 Nuitka 之外的编译工具链（clang/LLVM/cmake/ninja 版本保持基础镜像现状）
- 不改变 wheel 包结构（_libs/ 自包含、RPATH=$ORIGIN、bootstrap .pth 等机制不变）
- 不引入 PyTorch 到 xmnn-whl-builder（保持 nofollow-import-to 排除）
- 不修改 CMakeLists.txt 的 Python 版本要求（保持 `>=3.14`，不再降级）

## Background & Context

### 问题根因（I 阶段洞察）

基础镜像 `devcontainer-base:onnx-quantized-latest` 包含双 conda 环境：

| 环境路径 | 原始 Python 版本 | GIL 状态 | 工具链 |
|---|---|---|---|
| `/opt/conda` (base) | 3.13.13 | GIL enabled (`Py_GIL_DISABLED=0`) | 无 clang/llvm/cmake |
| `/opt/conda/envs/main` | 3.14.7 | free-threading (`Py_GIL_DISABLED=1`, cp314t) | clang/llvm/cmake/ninja/ccache |

历史构建因 Nuitka 4.1.3 对 Python 3.14 free-threading 的 C 编译失败（`allocator.h:606: error: use of undeclared identifier 'op'`），采取了三层降级：
1. Dockerfile PATH 反转为 `/opt/conda/bin` 在前（强制 python=3.13）
2. build-wheel.sh sed 将 CMakeLists.txt `VERSION_LESS "3.14"` 改为 `"3.13"`
3. build-wheel.sh sed 将 pyproject.toml `requires-python = ">=3.14"` 改为 `">=3.13"`

### Spike 验证结果（F+V 阶段）

| 方案 | 结果 | 详情 |
|---|---|---|
| cp314t free-threading (main env) | ❌ 失败 | Nuitka 4.1.3 C 编译 `allocator.h:606: error: use of undeclared identifier 'op'` |
| cp314 GIL mode (base env 升级) | ✅ 成功 | base env 升级为 Python 3.14.0 cp314，复用 main env clang 22.1.8，Nuitka 编译生成 `tvm.cpython-314-x86_64-linux-gnu.so` |

**最终方案**：通过 `conda install -n base -c conda-forge "python=3.14=*_cp314"` 将 base env 升级为 Python 3.14 cp314（GIL enabled），PATH 保持 base first + main second，CC/CXX 指向 main env 的 clang 实现跨环境编译。

### 第一性原理分析（F 阶段）

核心问题拆解：
- **本质需求**：wheel 必须在 Python 3.14 上可安装、可导入、可运行
- **ABI 选择**：Python 3.14 有两种 ABI——cp314（GIL）和 cp314t（free-threading）。基础镜像 main env 已提供 cp314t
- **Nuitka 兼容性**：Nuitka 4.1（2026-06-16 发布）官方声明支持 Python 3.4-3.14，包含大量 3.14 兼容性修复，但未明确声明 free-threading 支持
- **工具链位置**：clang/llvm/cmake 仅在 main env，因此无论用哪个 Python，PATH 都需包含 main env bin

**初始方案**（Spike 前）：直接使用 main env Python 3.14t（free-threading），PATH 恢复为 main env 在前，升级 Nuitka 到最新版本，验证 cp314t 编译可行性。

**最终方案**（Spike 后）：Nuitka 4.1.3 无法编译 cp314t（allocator.h:606），在 base env 通过 `conda install -n base -c conda-forge "python=3.14=*_cp314"` 升级为非 free-threading Python 3.14（cp314 GIL），工具链仍从 main env 引用（CC/CXX 指向 main env clang，LD_LIBRARY_PATH 包含 main env lib）。PATH 为 base first + main second。

### 环境约束

- Windows 主机无 Docker Desktop，使用 Podman 5.7.1（WSL2 Fedora 43 VM）
- WSL2 VM 实际可用资源：16 CPU，15GB RAM，1TB disk（满足 Nuitka `--jobs=8` ~15GB 内存需求）
- 构建时需从零构建完整基础镜像链（conda → conda-llvm → onnx-dev → onnx-quantized）
- 构建上下文必须为 `external/chaos/`（bind mount source 解析依赖）

## Functional Requirements

- **FR-1**: Dockerfile BUILD 阶段使用 base env Python 3.14 cp314（GIL enabled）作为默认 `python`（PATH 中 `/opt/conda/bin` 在前），main env bin 在 PATH 第二位提供 clang/LLVM/cmake/ninja 工具链
- **FR-2**: Dockerfile FINAL 阶段使用 base env Python 3.14 cp314（GIL enabled）作为默认 `python`，与 BUILD 阶段 PATH 布局一致
- **FR-3**: build-wheel.sh 不再通过 sed 修改 CMakeLists.txt 和 pyproject.toml 的版本要求
- **FR-4**: build-wheel.sh 在 Python 3.14 环境下完成 tvm/vta/xmnn 的 Nuitka 编译
- **FR-5**: 构建产出的 wheel 文件名包含 `cp314` 或 `cp314t` ABI 标签
- **FR-6**: FINAL 阶段 `pip install` wheel 后运行 verify-wheel.sh 全部 PASS
- **FR-7**: Jupyter kernel 注册适配双环境布局——kernel argv 指向 base env cp314 Python（xmnn 安装位置），Jupyter 服务本身运行在 main env cp314t；kernel.json 动态检测 CONDA_PREFIX 和 JUPYTER_BIN 路径
- **FR-8**: `/opt/xmnn-dist/` 保留 wheel 副本供下游镜像使用
- **FR-9**: build.sh 支持 Podman（自动检测容器引擎或通过环境变量指定）
- **FR-10**: 基础镜像链（conda → conda-llvm → onnx-dev → onnx-quantized）成功构建

## Non-Functional Requirements

- **NFR-1**: Nuitka 编译使用 ccache 缓存，增量构建应命中缓存（首次全量编译除外）
- **NFR-2**: 构建脚本保持中文注释风格，与现有代码库一致
- **NFR-3**: Podman machine 内存调整为 ≥8GB 以支持 Nuitka 并行编译（`--jobs=8`）
- **NFR-4**: 构建失败时提供清晰的错误诊断信息和排查建议
- **NFR-5**: 所有变更遵循现有 Dockerfile 规范（`.agents/rules/dockerfile.md`）

## Constraints

- **Technical**:
  - 必须使用 Podman（Windows 无 Docker）
  - 构建上下文必须为 `external/chaos/`
  - 基础镜像双 conda 环境布局不可更改（基础镜像由其他团队维护）
  - Nuitka 编译内存需求 ~15GB（`--jobs=8`），Podman machine 需 ≥8GB RAM
  - 不修改 npu_tvm/npuusertools 源码
- **Business**:
  - 用户硬性要求："保证一定是 python314"
  - 最终镜像需兼容 JupyterLab 工作流
- **Dependencies**:
  - Nuitka ≥ 4.1（PyPI 最新版）
  - devcontainer-base:onnx-quantized-latest（需构建）
  - Podman machine 运行中且资源充足

## Assumptions

- ~~Nuitka 4.1+ 能成功编译 Python 3.14t free-threading 代码~~（Spike 验证结果：Nuitka 4.1.3 对 cp314t 编译失败，allocator.h:606；已回退到 cp314 GIL 模式，base env 升级为 Python 3.14.0 cp314）
- 基础镜像 conda-llvm 的 `python=*=*cp314t` 锁定在 Nuitka 升级后仍可正常工作
- Podman 支持 `# syntax=docker/dockerfile:1.7-labs` 的 BuildKit bind mount 语法
- verify-wheel.sh 无需修改即可在 Python 3.14 环境下运行（其检查项与 Python 版本无关）
- AST PREAMBLE 注入机制在 Python 3.14 下已验证有效（历史构建中已使用）

## Acceptance Criteria

### AC-1: Wheel ABI 为 Python 3.14

- **Type**: `rule`
- **Given**: xmnn-whl-builder 镜像构建完成
- **When**: 检查 `/opt/xmnn-dist/` 目录下的 wheel 文件名
- **Then**: 文件名包含 `cp314` 或 `cp314t`（如 `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl` 或 `cp314t`）
- **Pass Condition**: wheel 文件名匹配正则 `cp314t?`，且不包含 `cp313`
- **Evidence**: `ls /opt/xmnn-dist/*.whl` 输出 + wheel 文件名

### AC-2: 容器 Python 版本为 3.14.x

- **Type**: `rule`
- **Given**: xmnn-whl-builder 最终镜像
- **When**: 执行 `python --version`
- **Then**: 输出 `Python 3.14.x`（x 为任意补丁版本号）
- **Pass Condition**: `python --version` 输出以 `Python 3.14.` 开头
- **Evidence**: `podman run --rm xmnn-whl-builder:latest python --version` 输出

### AC-3: verify-wheel.sh 全部验证 PASS

- **Type**: `rule`
- **Given**: 最终镜像中 wheel 已 pip install
- **When**: 执行 `bash /app/verify-wheel.sh`
- **Then**: 所有验证项输出 PASS，脚本退出码为 0
- **Pass Condition**: verify-wheel.sh 退出码 = 0，无 FAIL/ERROR
- **Evidence**: verify-wheel.sh 完整输出日志

### AC-4: 无 Python 3.13 降级机制残留

- **Type**: `rule`
- **Given**: 修改后的 Dockerfile 和 build-wheel.sh
- **When**: 检查源码中是否存在 Python 3.13 降级逻辑
- **Then**: Dockerfile 通过 `py314-base` 阶段将 base env 升级为 Python 3.14 cp314（GIL enabled），PATH 中 `/opt/conda/bin` 在前（base env cp314 Python），main env bin 在第二位提供工具链；build-wheel.sh 不含 `VERSION_LESS "3.13"` 或 `requires-python = ">=3.13"` 的 sed 替换
- **Pass Condition**: grep 搜索 `3.13`/`cp313` 在 Dockerfile 和 build-wheel.sh 中无降级相关命中（注释中说明历史原因的除外）；Dockerfile 包含 `conda install -n base "python=3.14=*_cp314"` 和 GIL 状态断言
- **Evidence**: grep 命令输出 + 文件审查

### AC-5: 基础镜像链完整构建

- **Type**: `rule`
- **Given**: Podman 环境
- **When**: 执行 `podman images` 检查
- **Then**: 存在 `devcontainer-base:latest`、`devcontainer-base:conda-llvm-latest`、`devcontainer-base:onnx-dev-latest`、`devcontainer-base:onnx-quantized-latest` 四个镜像
- **Pass Condition**: 四个镜像均存在且 none 为 `<none>` 悬空镜像
- **Evidence**: `podman images` 输出

### AC-6: wheel 副本保留在 /opt/xmnn-dist/

- **Type**: `rule`
- **Given**: 最终镜像
- **When**: 检查 `/opt/xmnn-dist/` 目录
- **Then**: 存在且仅存在一个 xmnn wheel 文件
- **Pass Condition**: `ls /opt/xmnn-dist/xmnn-*.whl` 返回恰好一个文件
- **Evidence**: `podman run --rm --entrypoint ls xmnn-whl-builder:latest -la /opt/xmnn-dist/` 输出

### AC-7: Jupyter kernel 正确注册并指向 Python 3.14

- **Type**: `rule`
- **Given**: 最终镜像
- **When**: 执行 `jupyter kernelspec list` 并检查 kernel.json 的 argv
- **Then**: xmnn-whl-builder kernel 存在，argv[0] 指向 Python 3.14 解释器
- **Pass Condition**: kernelspec list 包含 xmnn-whl-builder；kernel.json 中 python 路径的 `--version` 输出 3.14.x
- **Evidence**: `jupyter kernelspec list` 输出 + kernel.json 内容 + `python --version` 验证

### AC-8: 构建方案鲁棒性

- **Type**: `rubric`
- **Dimension**: 方案对 Nuitka free-threading 兼容性风险的应对能力
- **Scale**: 1-5
- **Anchors**:
  - 1 = 直接尝试全量构建，失败后无预案
  - 3 = 有 spike 验证但回退方案不明确
  - 5 = 先 spike 验证 Nuitka cp314t，有明确的 cp314 GIL 回退方案，且回退方案经预验证可行
- **Pass Threshold**: >= 4
- **Evidence**: spike 验证记录 + 回退方案文档

### AC-9: demo 模型精度正确

- **Type**: `rule`
- **Given**: Python 3.14 cp314 构建的 xmnn wheel
- **When**: 在 SIM_VTA2.0 仿真目标上编译并推理 models/demo/ 下所有模型
- **Then**: 编译成功，量化输出与浮点模型输出的余弦相似度 > 0.99
- **Models**:
  - `demo/caffe/resnet50` (Caffe ResNet-50, 224x224, a8w8)
  - `demo/onnx/yolov5s` (ONNX YOLOv5s, 640x640)
  - `demo/pytorch/resnet18` (PyTorch ResNet-18, 224x224)
  - `demo/two_inputs` (PyTorch 双输入 CNN, 32x32)
- **Pass Condition**: 所有模型编译成功且 accuracy_xmnn 无异常，输出层余弦相似度 > 0.99
- **Evidence**: accuracy result.csv + 编译/推理日志

### AC-10: debug caffe 模型精度正确

- **Type**: `rule`
- **Given**: Python 3.14 cp314 构建的 xmnn wheel
- **When**: 在 SIM_VTA2.0 仿真目标上编译并推理 models/debug/caffe_demo/ 模型
- **Then**: 编译成功，量化输出与浮点模型输出的余弦相似度 > 0.99
- **Model**: `debug/caffe_demo` (fgvsirfeature_ssd.caffemodel, 32x32, BGR, uint8, a8w8)
- **Pass Condition**: 编译成功且 accuracy_xmnn 无异常，输出层余弦相似度 > 0.99
- **Evidence**: accuracy result.csv + 编译/推理日志

## Open Questions

- [x] Nuitka 最新版本号是多少？4.1 是否确实修复了 `allocator.h:606` free-threading 编译错误？→ Nuitka 4.1.3 对 cp314 GIL 模式可编译（experimental 警告），对 cp314t free-threading 仍然失败
- [x] 若 cp314t 编译失败，回退方案中在 base env 安装非 free-threading Python 3.14 是否会与 conda-llvm 的 `python=*=*cp314t` 锁定冲突？→ 不冲突，base env 和 main env 是独立 conda 环境，base env 升级为 cp314 GIL 不影响 main env cp314t
- [x] Podman machine 内存从 2GB 调整到 ≥8GB 是否需要重新初始化 machine（WSL2 .vhdx 扩展）？→ WSL2 实际可用 15GB RAM，无需调整
