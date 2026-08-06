# caffex vs caffe-ffi 技术差距分析 - 实施计划

## [x] Task 1: 事实采集 - caffex 代码库全面扫描
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 枚举 caffex include/caffe/layers/ 所有层头文件
  - 枚举 caffex src/caffe/layers/ 所有层实现文件(.cpp/.cu)
  - 读取核心头文件 blob.hpp/layer.hpp/net.hpp/solver.hpp
  - 枚举 include/caffe/util/ 工具模块
  - 枚举 python/caffe/ Python接口文件
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: 算子头文件数量 >= 75
  - `programmatic` TR-1.2: CUDA实现文件数量 >= 56
  - `programmatic` TR-1.3: Solver/solver_factory.hpp 存在
- **Notes**: 包含 cudnn_* 加速层、base_* 基类、loss层基类

## [x] Task 2: 事实采集 - caffe-ffi 代码库全面扫描
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 枚举 caffe-ffi include/caffe_ffi/layers/ 所有层头文件
  - 枚举 caffe-ffi src/caffe_ffi/layers/ 所有层实现文件
  - 读取核心头文件 blob.hpp/layer.hpp/net.hpp/common.hpp
  - 枚举 python/caffe_ffi/ Python接口文件
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 算子头文件数量 = 21
  - `programmatic` TR-2.2: 无 .cu CUDA文件
  - `programmatic` TR-2.3: 无 solver.hpp
- **Notes**: 注意零拷贝/COW特有方法：ShareData/ShareDiff/cpu_mutable_data/BatchShareData

## [x] Task 3: 洞察分析 - 多维度系统性对比
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**: 
  - 算子维度：分类对比（Vision/Activation/Loss/Common/Data/Neuron/RNN等）
  - 架构维度：模板(Dtype) vs 固定类型(float)、SyncedMemory vs TVM Tensor、shared_ptr vs ObjectPtr
  - 功能模块维度：Solver/GPU/数据层/Python Layer/工具模块等
  - 接口维度：Blob/Layer/Net类API对比、Python API暴露范围
  - 构建系统维度：CMake结构对比
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-5
- **Test Requirements**:
  - `human-judgement` TR-3.1: 每个维度的对比有具体文件引用支撑
  - `programmatic` TR-3.2: 算子diff清单精确列出缺失项
  - `human-judgement` TR-3.3: 架构差异分析指出设计意图（推理引擎vs完整框架）
- **Notes**: 遵循七概念方法论R→I→E链路，G1事实无因果词、G2洞察含四元组

## [x] Task 4: 差距萃取 - 缺失算子分级清单
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 分类列出caffex有但caffe-ffi缺失的算子
  - 按P0(推理核心CNN必需)/P1(常用辅助)/P2(冷门/训练专用)分级
  - P0判定标准：ResNet/VGG/MobileNet等经典推理模型需要
  - P1判定标准：常见推理场景可能用到
  - P2判定标准：训练专用/极少使用/已废弃
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `human-judgement` TR-4.1: 每个缺失算子标注分类和优先级
  - `human-judgement` TR-4.2: P0算子清单可支撑经典CNN模型推理
  - `programmatic` TR-4.3: 缺失算子总数 = caffex总数 - caffe-ffi已实现数 - 排除项（cudnn/base/训练专用）
- **Notes**: cudnn_*层是GPU加速实现不算独立算子；base_*是基类不算算子；python_layer是Python自定义层功能

## [x] Task 5: 差距萃取 - 结构优化建议与接口分析
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 代码组织结构优化建议（目录分层、util模块、命名空间等）
  - 接口兼容性差异分析（与原版Caffe proto的兼容性、Python API差异）
  - 功能模块缺失的路线图建议（哪些应补、哪些不应补）
  - 识别caffex中值得借鉴的设计模式
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `human-judgement` TR-5.1: 每条建议有明确的改进方向和理由
  - `human-judgement` TR-5.2: 明确区分"必须补全"vs"刻意不实现"的设计决策
- **Notes**: caffe-ffi的零拷贝/COW设计是创新点，不应被caffex的旧设计束缚

## [x] Task 6: 报告生成 - 最终技术分析报告
- **Priority**: high
- **Depends On**: Task 4, Task 5
- **Description**: 
  - 整合所有分析结果，生成结构化Markdown报告
  - 报告章节：概述→项目简介→算子对比→架构对比→功能模块对比→Python接口对比→缺失算子清单(分级)→结构优化建议→接口改进建议→总结
  - 保存至 `.trae/specs/caffex-vs-caffe-ffi-gap-analysis/`
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `human-judgement` TR-6.1: 报告结构完整、数据准确、建议可操作
  - `programmatic` TR-6.2: 报告文件写入正确路径
