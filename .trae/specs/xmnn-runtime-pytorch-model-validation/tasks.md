# XMNN Runtime PyTorch 模型支持验证 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 安装 xmnn-runtime wheel 包并验证模块导入
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 安装 `xmnn-runtime-1.2.1-fix-cp314.tar.gz` wheel 包
  - 验证 tvm、vta、xmnn 模块导入是否正常
  - 验证核心 API（compile_xmnn、infer_xmnn）是否可用
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: wheel 包安装成功返回 0
  - `programmatic` TR-1.2: import tvm, vta, xmnn 无错误
  - `programmatic` TR-1.3: compile_xmnn 和 infer_xmnn 函数可调用
- **Notes**: 需要在正确的 Python 3.14 环境中执行

## [ ] Task 2: 验证 PyTorch ResNet18 模型编译
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 使用 compile_xmnn API 编译 ResNet18 模型
  - 检查编译产物是否生成（中间表示文件）
  - 验证编译过程无错误输出
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: compile_xmnn 调用返回成功
  - `programmatic` TR-2.2: 编译产物目录存在且包含预期文件
  - `programmatic` TR-2.3: 编译日志无 ERROR 级别输出
- **Notes**: 需要设置正确的环境变量和模型路径

## [ ] Task 3: 验证 PyTorch ResNet18 模型推理
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 使用 infer_xmnn API 执行 ResNet18 模型推理
  - 检查推理输出文件是否生成
  - 验证推理过程无错误输出
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-3.1: infer_xmnn 调用返回成功
  - `programmatic` TR-3.2: 输出目录存在且包含 output0.txt
  - `programmatic` TR-3.3: 推理日志无 ERROR 级别输出
- **Notes**: 需要准备测试输入数据

## [ ] Task 4: 验证 ResNet18 模型精度
- **Priority**: high
- **Depends On**: Task 3
- **Description**: 
  - 加载原始 PyTorch ResNet18 模型
  - 使用相同输入执行原始模型推理
  - 计算 NPU 推理结果与原始模型结果的余弦相似度
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-4.1: 余弦相似度 ≥ 0.99
  - `programmatic` TR-4.2: 输出结果形状与原始模型一致
  - `programmatic` TR-4.3: 输出结果数据类型正确
- **Notes**: 需要处理输入数据的预处理（mean/std）

## [ ] Task 5: 验证双输入模型编译
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 使用 compile_xmnn API 编译 two_inputs 模型
  - 验证多输入配置（input_0、input_1）正确处理
  - 检查编译产物是否生成
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-5.1: compile_xmnn 调用返回成功
  - `programmatic` TR-5.2: 编译产物目录存在且包含预期文件
  - `programmatic` TR-5.3: 编译日志无 ERROR 级别输出
- **Notes**: 双输入模型的 config.toml 使用 input_0/input_1 配置

## [ ] Task 6: 验证双输入模型推理
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 使用 infer_xmnn API 执行双输入模型推理
  - 验证多输入数据正确处理
  - 检查推理输出文件是否生成
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: infer_xmnn 调用返回成功
  - `programmatic` TR-6.2: 输出目录存在且包含输出文件
  - `programmatic` TR-6.3: 推理日志无 ERROR 级别输出
- **Notes**: 需要准备两个输入数据文件

## [ ] Task 7: 验证双输入模型精度
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 加载原始双输入模型
  - 使用相同输入执行原始模型推理
  - 计算 NPU 推理结果与原始模型结果的余弦相似度
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 余弦相似度 ≥ 0.99
  - `programmatic` TR-7.2: 输出结果形状与原始模型一致
- **Notes**: 需要注意两个输入的不同形状

## [ ] Task 8: 生成支持情况报告
- **Priority**: medium
- **Depends On**: Task 1-7
- **Description**: 
  - 汇总所有验证步骤的结果
  - 记录验证过程中发现的问题
  - 生成详细的 Markdown 格式支持情况报告
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgment` TR-8.1: 报告包含所有验证步骤的详细结果
  - `human-judgment` TR-8.2: 报告包含精度数据和问题记录
  - `human-judgment` TR-8.3: 报告结构清晰，便于阅读
- **Notes**: 报告应包含验证环境、步骤、结果、问题和建议
