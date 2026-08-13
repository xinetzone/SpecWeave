# caffe-ffi Conv v4 优化里程碑收官 - 产品需求文档

## Overview
- **Summary**: 完成 Conv v4 OpenMP 并行优化的里程碑收官工作，包括：里程碑复盘报告、生产部署配置建议、InceptionV1 batch=16 抖动问题诊断与缓解、sdk_full_test 全量模型性能回归测试与最终报告。
- **Purpose**: 将 Conv v4 优化成果从研究阶段推进到可交付状态，输出生产级部署指南，验证在 SDK 真实模型（fgvsirfeature 人脸特征提取、fgvsirfeature_ssd 人脸检测）上的性能表现，并通过方法论编排（R→I→E→A→C）完成里程碑闭环。
- **Target Users**: caffe-ffi 推理引擎使用者、SDK 部署工程师、性能优化团队。

## Goals
- 产出 Conv v4 优化里程碑复盘报告（七概念方法论 R→I→E→C 链路）
- 生成生产环境部署配置建议（延迟敏感 vs 吞吐优先场景明确参数组合）
- 诊断并缓解 InceptionV1 batch=16 下的延迟抖动问题（OMP_SCHEDULE 调优 + 内存预分配）
- 对 sdk_full_test 中的 SDK 真实模型（fgvsirfeature、fgvsirfeature_ssd）执行全量性能回归测试
- 生成最终交付报告，包含所有模型的性能数据、配置建议、已知问题

## Non-Goals (Out of Scope)
- 不进行新的 Conv 层算法优化（v4 为最终版本）
- 不修改 caffe-ffi 核心 C++ 代码逻辑（仅参数调优与脚本/文档产出）
- 不处理 GPU/异构计算场景（纯 CPU OpenMP 优化）
- 不进行模型量化/剪枝等模型级优化
- 不修改 vendor/ 下的第三方依赖代码

## Background & Context
- Conv v4 优化策略：沿输出通道(M)维度分块并行，最小分块32通道，GEMM+Bias融合，im2col单线程
- 已验证模型：ResNet-50 (53 Conv, 224×224)、InceptionV1 (57 Conv, 224×224)、ResNet-101 (104 Conv, 224×224)
- 已完成环境变量修复：OMP_WAIT_POLICY=PASSIVE 已在 [build_and_bench_v5.sh](file:///d:/spaces/SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/build_and_bench_v5.sh#L22-L27) 全局导出
- 稳定性测试发现：batch=16时InceptionV1 CV%达18.6%，尾延迟比2.33x，存在显著抖动；OMP=2时出现0.90x减速（小GEMM线程开销>收益）
- SDK 真实模型：fgvsirfeature（人脸嵌入，120×120输入，~64 Conv，通道数16→32→64→128→256渐进式残差网络）、fgvsirfeature_ssd（人脸检测SSD，小模型）
- 方法论：使用七概念编排（场景1+场景2混合链路）R→I→E→[F→V]→A→C

## Functional Requirements
- **FR-1**: 里程碑复盘报告（事实→洞察→模式→原子行动项）
- **FR-2**: 生产部署配置建议文档（延迟敏感/吞吐优先/通用均衡三种Profile）
- **FR-3**: InceptionV1 batch=16 抖动诊断脚本（测试 static/dynamic/guided 调度 + 内存预分配策略）
- **FR-4**: sdk_full_test 全量回归测试脚本（支持 fgvsirfeature/fgvsirfeature_ssd + 已有3个标准模型）
- **FR-5**: 一键执行脚本 build_and_bench_v6.sh（整合编译+诊断+全量测试+报告生成）
- **FR-6**: 最终性能报告（Markdown格式，含数据表、配置建议、稳定性评级）

## Non-Functional Requirements
- **NFR-1**: 所有测试结果可复现（固定随机种子、隔离环境变量、子进程隔离）
- **NFR-2**: 正确性保证：OMP=1 vs OMP=N 输出差异 max_abs_diff < 1e-4
- **NFR-3**: 稳定性指标完整：CV%、P50/P95/P99 分位延迟、尾延迟比 P99/P50
- **NFR-4**: 文档可读性：部署建议包含复制即用的 export 命令块和决策树
- **NFR-5**: 脚本幂等性：可重复执行不产生副作用

## Constraints
- **Technical**: 容器内执行（Docker caffe-ffi 环境），Python 3.10+，OpenMP + OpenBLAS
- **Business**: 不破坏现有功能，所有变更向后兼容
- **Dependencies**: caffe-ffi 已编译的 _caffe_ffi.so、SDK 模型文件（已转换为 caffe-ffi 格式）

## Assumptions
- Docker 容器可正常启动且 caffe-ffi build 目录存在最新编译产物
- fgvsirfeature.caffemodel 已在容器内可用（或可从 sdk_full_test 目录挂载）
- fgvsirfeature 输入尺寸为 1×3×120×120（prototxt 已确认）
- 网络可访问 GitHub 下载 ResNet 系列 prototxt（如需）
- 容器内有 8 个可用 CPU 核心（与之前测试一致）

## Acceptance Criteria

### AC-1: 里程碑复盘报告完整性
- **Given**: Conv v4 优化所有实验数据已就绪
- **When**: 按照七概念方法论 R→I→E→C 链路执行复盘
- **Then**: 产出包含事实清单（≥20条客观事实，无因果词）、3条核心洞察（四元组完整）、1-2个可迁移模式、3-5个原子行动项的复盘报告
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 事实通过G1门（无因果推断词）、洞察通过G2门（四元组完整）、模式通过G3门（有反模式）

### AC-2: 生产部署配置建议
- **Given**: 三模型稳定性与扩展性数据已收集
- **When**: 分析不同业务场景的最优配置组合
- **Then**: 产出三种Profile的配置建议：①延迟敏感型（batch=1，OMP线程数、BLAS线程数、等待策略、调度策略）②吞吐优先型（batch=N，参数组合）③通用均衡型；每种Profile包含CV%预期、尾延迟比预期、适用场景、复制即用命令
- **Verification**: `human-judgment`（配置合理性、可操作性）+ `programmatic`（配置与benchmark数据一致）

### AC-3: InceptionV1 抖动缓解
- **Given**: InceptionV1 batch=16 在 OMP=4 下 CV%=41.2%，尾延迟比 2.33x
- **When**: 测试 OMP_SCHEDULE=static/dynamic/guided 和 OMP_WAIT_POLICY=ACTIVE/PASSIVE 组合，以及预热轮次/内存预分配策略
- **Then**: 找到能将 CV% 降低到 15% 以下的配置组合，或明确根因并给出缓解建议；如无法消除抖动，给出是否使用4线程的明确建议
- **Verification**: `programmatic`（CV%数值对比测试）

### AC-4: sdk_full_test 全量模型测试
- **Given**: SDK模型（fgvsirfeature、fgvsirfeature_ssd）prototxt 和 caffemodel 可用
- **When**: 运行包括5个模型（ResNet-50、InceptionV1、ResNet-101、fgvsirfeature、fgvsirfeature_ssd）的全量benchmark
- **Then**: 所有模型在推荐配置下成功推理，OMP=1 vs OMP=4正确性验证通过（max_diff<1e-4），输出完整性能数据表
- **Verification**: `programmatic`（脚本退出码0、正确性检查PASS、数据表完整）

### AC-5: 一键脚本 v6 完整性
- **Given**: 所有诊断和测试脚本已就位
- **When**: 执行 build_and_bench_v6.sh
- **Then**: 依次完成：编译→模型准备→正确性验证→抖动诊断→全量回归→报告生成；全局环境变量（OMP_NUM_THREADS=4、OPENBLAS_NUM_THREADS=1、OMP_WAIT_POLICY=PASSIVE）正确导出；最终报告保存为 Markdown 文件
- **Verification**: `programmatic`（脚本执行exit 0、所有步骤输出PASS、报告文件存在且内容完整）

### AC-6: 最终交付报告
- **Given**: 所有测试数据已收集
- **When**: 汇总输出最终报告
- **Then**: 报告包含：执行摘要、模型性能对比表、部署配置建议（3种Profile）、InceptionV1抖动分析结论、已知问题与限制、后续优化方向
- **Verification**: `human-judgment`（报告结构清晰、结论有据可查、建议可操作）

## Resolved Decisions
- [x] fgvsirfeature_ssd 小模型纳入测试，用于验证并行降级策略（通道数<32时自动减少线程数）
- [x] SDK模型caffemodel自动从 `playground/caffemodel-conversion/sdk_full_test/` 复制到容器内测试目录
- [x] 内存预分配策略：采用预热+Blob预分配方式（加大warmup至20-50次迭代，warmup阶段使用不同输入数据touch所有内存页，验证caffe-ffi blob内存复用效果）；不做系统级malloc调优
