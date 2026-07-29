# Caffex 算子库全面测试 - Product Requirement Document

## Overview
- **Summary**: 在 origin Docker 环境中对 caffex 项目的算子库（tests/ops/）进行全面测试，包括算子正确性验证、性能基准测试、内存使用检测和兼容性测试，生成详细测试报告并对发现的问题进行定位和修复验证。
- **Purpose**: 现有算子测试仅做冒烟测试（验证能运行），缺乏数学正确性验证、性能基准、内存安全检测和边缘情况覆盖。本项目旨在建立完整的算子测试体系，确保 caffex 算子库在各种条件下的正确性、性能和稳定性。
- **Target Users**: caffex 开发者、算法工程师、质量保证团队

## Goals
- 在 origin Docker 环境（caffe-cpu:origin-runtime）中配置完整的测试依赖环境
- 为所有26个算子添加数学正确性验证（与 numpy 参考实现对比）
- 添加性能基准测试，记录各算子在不同输入形状下的执行时间
- 添加内存使用检测，识别内存泄漏和异常内存占用
- 添加边缘情况和边界条件测试（零输入、极值、特殊形状等）
- 生成结构化的测试报告（含通过率、性能数据、内存分析、失败详情）
- 对测试中发现的问题进行定位和修复验证

## Non-Goals (Out of Scope)
- GPU/CUDA 相关测试（origin 环境为 CPU-only）
- 训练相关功能测试（仅推理/前向传播算子测试）
- 不修改 caffex/ 目录下的 BVLC 原始源码（问题修复在 tests/ 层或外层包装层处理）
- 模型级端到端测试（networks/ 目录下的模型测试不在本任务范围）
- 性能优化（只测量性能，不做优化）

## Background & Context
- **项目位置**: 
  - caffex 源码: `projects/xuanspace/vendor/caffe/caffex/`
  - 算子库测试: `projects/xuanspace/vendor/caffe/tests/ops/`
  - origin Docker 环境: `projects/xuanspace/vendor/caffe/docker/origin/`
- **技术栈**: 
  - C++ 实现的 Caffe 框架，Python 绑定（PyCaffe）
  - 测试框架: pytest
  - Docker 环境: Ubuntu 22.04 + Python 3.10 + numpy 1.x + protobuf 3.20.3
- **现有测试覆盖**: 26个算子测试文件，每个文件包含基本的前向传播冒烟测试（ReLU、Convolution、Pooling、BatchNorm、Softmax等）
- **现有测试局限**: 仅验证算子能运行，不验证输出正确性；无性能测量；无内存检测；边缘情况覆盖不足

## Functional Requirements
- **FR-1**: 环境配置 - 在 origin Docker 镜像中安装 pytest、pytest-cov、memory-profiler 等测试依赖，配置测试运行环境
- **FR-2**: 正确性验证 - 为每个算子添加 numpy 参考实现，对比 Caffe 输出与参考实现的数值差异（atol/rtol 阈值）
- **FR-3**: 性能基准测试 - 为每个算子添加上下文管理器计时功能，记录多次运行的平均时间、标准差
- **FR-4**: 内存使用检测 - 使用 tracemalloc 和 memory_profiler 检测算子前后内存变化，识别泄漏
- **FR-5**: 边缘情况测试 - 为每个算子添加边界条件测试：零输入、极值（大/小数值）、单元素批次、非标准形状、不同数据类型
- **FR-6**: 兼容性测试 - 验证算子在不同输入形状（2D/4D）、不同 batch size、不同通道数下的稳定性
- **FR-7**: 测试报告生成 - 生成 Markdown 格式测试报告，包含：通过率统计、性能排名、内存使用分析、失败用例详情
- **FR-8**: 问题定位与验证 - 对失败测试进行根因分析，记录问题现象和定位过程，修复后进行回归验证

## Non-Functional Requirements
- **NFR-1**: 测试可重复性 - 固定随机种子，确保测试结果可复现
- **NFR-2**: 测试执行时间 - 完整测试套件在 Docker 环境中执行时间不超过30分钟
- **NFR-3**: 报告可读性 - 测试报告结构清晰，包含表格、统计摘要和可操作的问题描述
- **NFR-4**: 环境隔离 - 测试在 Docker 容器中运行，不影响宿主机环境
- **NFR-5**: 测试独立性 - 每个测试用例独立运行，不依赖其他测试的状态

## Constraints
- **Technical**: 
  - 必须使用 origin Docker 环境（Ubuntu 22.04 + Python 3.10 + numpy 1.x + protobuf 3.20.3）
  - 不能修改 caffex/ 目录下的 BVLC 原始源码
  - 测试必须在 CPU 模式下运行（无 CUDA）
  - Python 版本固定 3.10，numpy < 2.0，protobuf == 3.20.3
- **Business**: 
  - 测试覆盖所有26个算子，不能遗漏
  - 测试报告需要中文输出
- **Dependencies**: 
  - Docker 环境可用
  - caffe-cpu:origin-runtime 镜像可构建或已存在
  - pytest 及相关插件

## Assumptions
- Docker 已在宿主机安装并可正常运行
- origin Docker 镜像可以成功构建（或已有可用镜像）
- 算子的数学定义明确，可以用 numpy 实现参考版本
- 现有测试框架（utils.py）可以扩展以支持新的测试类型

## Acceptance Criteria

### AC-1: 测试环境正确配置
- **Given**: origin Docker 环境已准备
- **When**: 在容器中安装测试依赖并运行环境检查
- **Then**: pytest 可运行，caffe 模块可正确导入，所有依赖满足版本要求
- **Verification**: `programmatic`
- **Notes**: 通过 verify-caffe.sh 和 pytest --version 验证

### AC-2: 所有算子正确性测试通过
- **Given**: 每个算子都有 numpy 参考实现
- **When**: 运行完整测试套件
- **Then**: 所有算子在常规输入下输出与参考实现的差异在 atol=1e-5, rtol=1e-4 阈值内
- **Verification**: `programmatic`
- **Notes**: 数值精度问题需记录，可适当调整阈值但需说明原因

### AC-3: 性能基准数据完整
- **Given**: 每个算子都有性能计时
- **When**: 运行性能测试
- **Then**: 生成包含每个算子平均执行时间、标准差、相对性能排名的表格
- **Verification**: `programmatic`
- **Notes**: 每个算子至少运行10次取平均，预热1次

### AC-4: 内存检测无严重泄漏
- **Given**: 启用内存检测
- **When**: 运行内存测试
- **Then**: 没有检测到持续增长的内存泄漏（多次运行后内存稳定）
- **Verification**: `programmatic`
- **Notes**: 允许正常的内存分配和释放，检测异常增长

### AC-5: 边缘情况测试覆盖
- **Given**: 每个算子都有边缘情况测试用例
- **When**: 运行边缘测试
- **Then**: 零输入、极值、特殊形状等边界条件下算子行为正确或优雅报错
- **Verification**: `programmatic` + `human-judgment`
- **Notes**: 预期会失败的情况应该抛出明确异常而非崩溃

### AC-6: 兼容性测试通过
- **Given**: 测试不同输入形状和参数配置
- **When**: 运行兼容性测试
- **Then**: 算子在支持的输入形状范围内正常工作，不支持的情况有明确错误提示
- **Verification**: `programmatic`

### AC-7: 测试报告生成完整
- **Given**: 所有测试执行完毕
- **When**: 生成测试报告
- **Then**: 报告包含摘要、通过率、性能表格、内存分析、失败详情、修复建议
- **Verification**: `human-judgment`
- **Notes**: 报告格式为 Markdown，存放在 docker/origin/ 目录下

### AC-8: 发现的问题已定位和验证
- **Given**: 测试中发现失败用例
- **When**: 进行问题定位
- **Then**: 记录问题根因、影响范围、复现步骤；修复后回归测试通过
- **Verification**: `human-judgment`
- **Notes**: 问题记录在测试报告的"问题清单"章节

## Open Questions
- [ ] 是否需要为每个算子实现反向传播（梯度）测试？（当前仅前向传播）
- [ ] 性能测试的基准输入形状如何确定？（统一形状还是按算子特性选择）
- [ ] 内存泄漏检测的阈值是多少？（多少MB的增长算泄漏）
- [ ] 数值精度阈值 atol/rtol 是否需要按算子类型区分？
- [ ] 测试报告是否需要包含历史对比（与之前版本对比）？
