---
version: 1.0
---

# XMNN Runtime cp314 重新打包 - 产品需求文档

## Overview
- **Summary**: 重新打包 `xmnn-runtime-1.2.1-fix-cp314.tar.gz` 运行时分发包，在打包流程中集成 ONNX（YOLOv5s）和 Caffe（ResNet50）两类模型的编译验证与精度测试，确保打包产物在模型编译和推理精度方面均达到质量标准，最终生成包含编译日志和精度测试结果的完整打包报告。
- **Purpose**: 确保发布的 cp314 版本 runtime 包能够正确编译所有支持的模型格式（ONNX、Caffe）且无编译错误/警告，同时量化编译后模型与原始浮点模型的推理精度一致性，为下游用户提供可信赖的运行时环境。
- **Target Users**: NPU 工具链开发人员、模型部署工程师、QA 验证团队

## Goals
- 基于现有 Nuitka 编译流水线重新构建 cp314（Python 3.14）版本的 XMNN runtime
- 确保 `models/onnx/yolov5s` 和 `models/caffe/resnet50` 两个模型在打包环境中能够端到端编译成功
- 编译过程零错误、零警告（或可解释的已知警告需在报告中说明）
- 对两个模型执行精度验证，量化与原始浮点模型的误差（余弦相似度、MSE、MAE）
- 所有精度指标满足预设阈值（输出层余弦相似度 ≥ 0.99，内部关键节点余弦相似度 ≥ 0.95）
- 生成结构完整的打包报告（含构建日志、编译日志、精度测试结果汇总）
- 最终产物为 `xmnn-runtime-1.2.1-fix-cp314.tar.gz`（OCI 容器镜像格式）

## Non-Goals (Out of Scope)
- 不修改 TVM/VTA/XMNN 的核心编译逻辑或量化算法
- 不新增对 PyTorch 模型的编译验证（本次仅覆盖 ONNX 和 Caffe）
- 不进行板端（硬件）部署和性能测试（仅在仿真环境 SIM_VTA2.0_PRO 下验证）
- 不修改 Docker 基础镜像或 LLVM 版本
- 不对 autolibs（自动调优日志）进行重新调优
- 不发布推送到远程镜像仓库

## Background & Context
- **现有产物**: `external/xmhub/notebook/xmnn/dist/xmnn-runtime-1.2.1-fix-cp314.tar.gz` 是一个 OCI layout 格式的容器镜像归档，包含基于 Python 3.14 的 XMNN 运行时环境
- **构建流水线**: notebook 目录下使用 Invoke + Docker 实现四阶段构建：CMake 构建 → TVM Nuitka 编译 → VTA Nuitka 编译 → XMNN Nuitka 编译 → wheel 打包
- **模型验证工具**: npuusertools 提供 `compile.py`（模型编译）、`accuracy.py`（精度对比测试）、`infer.py`（推理）等命令行工具
- **模型配置**:
  - ONNX: `models/onnx/yolov5s` 使用 YOLOv5s 模型，输入 [1,3,640,640]，目标平台 SIM_VTA2.0_PRO，量化类型 a8w8
  - Caffe: `models/caffe/resnet50` 使用 ResNet-50 模型，输入 [1,3,224,224]，目标平台 SIM_VTA2.0_PRO，量化类型 a8w8
- **已有约束**: 17 条不可变约束（见 `notebook/.agents/constraints.md`），包括 TVM_FFI=ctypes、Nuitka 必须 --clang、容器内执行编译等

## Functional Requirements
- **FR-1**: 环境准备与依赖检查
  - 验证 Docker 环境可用，构建镜像 `nuitka-gcc-llvm` 已就绪（如缺失则构建）
  - 验证 npu_tvm CMake 构建产物完整性（libtvm.so 等）
  - 验证 Python 3.14 环境在容器内可用

- **FR-2**: 重新执行 Nuitka 编译流水线
  - 执行 `inv build` 完成 CMake 构建阶段
  - 执行 `inv nuitka` 完成 TVM/VTA/XMNN 三组件的 Nuitka 编译
  - 编译过程中完整记录 stdout/stderr 日志
  - 验证生成的 .so 文件存在且非空

- **FR-3**: 模型编译验证（ONNX - YOLOv5s）
  - 在打包环境容器内执行 `python compile.py -n yolov5s`
  - 捕获编译全程日志，检查是否有 ERROR 级别的日志输出
  - 检查是否有未预期的 WARNING（已知可接受警告需白名单化）
  - 验证编译产物 `network.xmnn` 和 `param.bin` 生成且非空
  - 验证编译过程无 Python 异常抛出

- **FR-4**: 模型编译验证（Caffe - ResNet50）
  - 在打包环境容器内执行 `python compile.py -n resnet50`
  - 捕获编译全程日志，同 FR-3 的错误/警告检查标准
  - 验证编译产物 `network.xmnn` 和 `param.bin` 生成且非空
  - 验证编译过程无 Python 异常抛出

- **FR-5**: 精度测试验证（ONNX - YOLOv5s）
  - 在打包环境容器内执行 `python accuracy.py -n yolov5s`
  - 收集所有节点的精度指标：余弦相似度、MSE、MAE
  - 验证输出层余弦相似度 ≥ 0.99
  - 验证内部关键节点（conv2d/dense/batch_matmul）余弦相似度 ≥ 0.95
  - 精度不达标时记录详细差异数据用于分析
  - 保存精度测试 CSV 结果文件

- **FR-6**: 精度测试验证（Caffe - ResNet50）
  - 在打包环境容器内执行 `python accuracy.py -n resnet50`
  - 同 FR-5 的精度指标收集和阈值验证标准
  - 保存精度测试 CSV 结果文件

- **FR-7**: Runtime 镜像打包
  - 基于验证通过的 wheel 和运行时依赖构建/更新运行时容器镜像
  - 导出为 OCI layout 格式的 tar.gz 包
  - 验证 tar.gz 结构完整性（包含 blobs/、index.json、manifest.json、oci-layout）

- **FR-8**: 打包报告生成
  - 汇总 Nuitka 编译阶段日志（关键步骤摘要 + 完整日志路径）
  - 汇总两个模型的编译日志（错误/警告统计、关键信息）
  - 汇总两个模型的精度测试结果（指标表格、阈值验证结果、异常节点列表）
  - 包含环境信息（Python 版本、Nuitka 版本、LLVM 版本、镜像 tag）
  - 包含最终产物校验信息（文件大小、SHA256）
  - 报告格式为 Markdown，保存到 `notebook/.agents/reports/` 目录

## Non-Functional Requirements
- **NFR-1**: 编译日志必须完整保留，不得截断或过滤关键信息
- **NFR-2**: 精度测试使用校准数据集第一个样本进行验证，确保可复现
- **NFR-3**: 整个打包流程可通过单一命令序列复现
- **NFR-4**: 任何编译错误或精度不达标必须立即终止流程并标记失败，不得跳过
- **NFR-5**: 报告中的数值指标必须精确到小数点后 6 位
- **NFR-6**: 所有日志和中间产物保留在容器挂载目录中，便于事后排查

## Constraints
- **Technical**:
  - 所有编译操作必须在 Docker 容器（`nuitka-gcc-llvm` 镜像）内执行，宿主机仅做编排
  - Python 版本为 3.14（cp314）
  - Nuitka 编译必须使用 `--clang` 和 `--module` 参数
  - TVM FFI 模式必须为 `ctypes`（排除 Cython）
  - 容器 I/O 使用 `sys.stdout.buffer.write()` 处理 bytes 输出，避免 Windows GBK 编码问题
- **Business**:
  - 打包产物需与现有 1.2.1-fix 版本保持接口兼容
  - 不破坏现有已验证功能
- **Dependencies**:
  - Docker 环境可用且运行正常
  - npu_tvm 源码完整，CMake 可正常配置
  - npuusertools 下的模型文件（onnx/caffe）完整
  - 宿主机可挂载源码目录到容器
- **Environment**:
  - 宿主操作系统为 Windows（PowerShell 环境）
  - 容器内操作系统为 Linux x86_64

## Assumptions
- Docker Desktop 已在 Windows 上安装并运行
- `inv image-build` 已在之前执行过，`nuitka-gcc-llvm` 镜像存在（如不存在会自动构建）
- npu_tvm 源码可正常通过 CMake 配置和编译
- onnx 和 caffe 模型文件完整且未损坏
- 精度验证的可接受阈值（余弦相似度 ≥ 0.99/0.95）是基于历史版本的经验值
- SIM_VTA2.0_PRO 仿真环境在容器内可正常运行（无需实际硬件）

## Acceptance Criteria

### AC-1: Docker 环境与基础镜像就绪
- **Given**: 宿主系统已安装 Docker 且服务正常运行
- **When**: 执行 `docker images | grep nuitka-gcc-llvm`
- **Then**: 镜像存在且 tag 为 `nuitka-gcc-llvm`；如不存在，执行 `inv image-build` 可成功构建
- **Verification**: `programmatic`

### AC-2: Nuitka 编译流水线成功完成
- **Given**: Docker 镜像就绪，源码目录挂载正确
- **When**: 在 notebook/ 目录执行 `inv build` 和 `inv nuitka`
- **Then**: 三个 .so 文件（tvm.cpython-314-*.so、vta.cpython-314-*.so、xmnn.cpython-314-*.so）均生成且非空；wheel 文件在 `xmnn/dist/` 下生成；Nuitka 编译过程无 ERROR 日志
- **Verification**: `programmatic`

### AC-3: ONNX (YOLOv5s) 模型编译无错误无警告
- **Given**: Nuitka 编译产物已在容器内安装
- **When**: 容器内执行 `cd /work/npuusertools && python compile.py -n yolov5s`
- **Then**: 退出码为 0；日志中无 ERROR 级别输出；无未预期的 WARNING（白名单内警告除外）；`network.xmnn` 和 `param.bin` 文件生成且大小 > 0
- **Verification**: `programmatic`

### AC-4: Caffe (ResNet50) 模型编译无错误无警告
- **Given**: Nuitka 编译产物已在容器内安装
- **When**: 容器内执行 `cd /work/npuusertools && python compile.py -n resnet50`
- **Then**: 退出码为 0；日志中无 ERROR 级别输出；无未预期的 WARNING；`network.xmnn` 和 `param.bin` 文件生成且大小 > 0
- **Verification**: `programmatic`

### AC-5: ONNX (YOLOv5s) 精度测试通过
- **Given**: YOLOv5s 模型编译成功
- **When**: 容器内执行 `cd /work/npuusertools && python accuracy.py -n yolov5s`
- **Then**: 退出码为 0；输出层（output 节点）余弦相似度 ≥ 0.99；所有内部 conv2d/dense 节点余弦相似度 ≥ 0.95；精度结果 CSV 文件生成
- **Verification**: `programmatic`

### AC-6: Caffe (ResNet50) 精度测试通过
- **Given**: ResNet50 模型编译成功
- **When**: 容器内执行 `cd /work/npuusertools && python accuracy.py -n resnet50`
- **Then**: 退出码为 0；输出层余弦相似度 ≥ 0.99；所有内部 conv2d/dense 节点余弦相似度 ≥ 0.95；精度结果 CSV 文件生成
- **Verification**: `programmatic`

### AC-7: Runtime tar.gz 包结构完整
- **Given**: 所有模型编译和精度验证通过
- **When**: 导出并检查 `xmnn-runtime-1.2.1-fix-cp314.tar.gz`
- **Then**: 文件存在且大小合理（预期 > 100MB）；`tar -tzf` 列出内容包含 `oci-layout`、`index.json`、`manifest.json`、`blobs/sha256/` 结构
- **Verification**: `programmatic`

### AC-8: 打包报告完整生成
- **Given**: 打包流程全部完成
- **When**: 检查报告文件
- **Then**: 报告为 Markdown 格式；包含环境信息、Nuitka 编译摘要、两个模型编译日志摘要（错误/警告统计）、两个模型精度结果表格（含阈值对比）、产物 SHA256 校验值；报告保存路径为 `notebook/.agents/reports/packaging-report-YYYYMMDD.md`
- **Verification**: `human-judgment`

### AC-9: 可复现性验证
- **Given**: 完整打包流程已成功执行一次
- **When**: 清理中间产物后重新执行关键步骤
- **Then**: 模型编译和精度测试结果一致（允许日志时间戳等非确定性差异）
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要将精度阈值固化到自动化脚本中，还是仅在报告中人工判定？
- [ ] 现有 runtime 镜像的导出脚本在哪里？是否已有 `inv export` 类似命令，还是需要手动 docker save/export？
- [ ] 编译 WARNING 的白名单如何确定？是否需要基于历史成功构建的 WARNING 列表建立基线？
- [ ] 打包报告的模板格式是否有现有参考？
- [ ] 如果精度测试不达标，是否需要自动触发问题诊断流程（如逐层对比分析），还是仅报告失败即可？
