---
id: caffe-ops-library-extraction
version: "1.0.0"
created: 2026-07-27
source: external/chaos/npu_tvm/tests/python/frontend/caffe/test_forward.py
target: projects/xuanspace/vendor/caffe/tests/ops
---

# Caffe算子测试库提取 - Product Requirement Document

## Overview
- **Summary**: 从 TVM 的 Caffe 前端测试文件中提取纯 Caffe 相关的算子测试代码，移除所有 TVM 依赖，重构为一个结构化、可独立运行的 Caffe 算子测试库。
- **Purpose**: 将原本耦合在 TVM 测试框架中的 Caffe 算子测试用例解耦，形成独立的 Caffe 算子验证库，便于在不依赖 TVM 的环境下测试 Caffe 算子实现的正确性。
- **Target Users**: Caffe 框架开发者、算子实现验证人员、深度学习框架测试工程师。

## Goals
- 从 [test_forward.py](file:///d:/spaces/SpecWeave/external/chaos/npu_tvm/tests/python/frontend/caffe/test_forward.py) 中提取 23 个 Caffe 算子的测试用例
- 完全移除 TVM 相关导入、函数调用和依赖
- 重构为原子化的文件结构：每个算子一个测试文件，公共工具函数独立模块
- 保持原始测试用例的完整性和参数覆盖度
- 确保代码符合 xuanspace 项目规范（Python 3.13+，ruff/black/isort 风格）
- 输出目录：[tests/ops](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/tests/ops)

## Non-Goals (Out of Scope)
- 不修改 caffex/ 原始源码
- 不添加新的算子测试用例（仅提取现有用例）
- 不实现 Caffe 算子本身（仅测试框架）
- 不包含网络级测试（Mobilenetv2、Alexnet、Resnet50、Inceptionv1）——这些依赖外部模型下载，不在本次提取范围内
- 不配置 CI/CD 流水线
- 不编写 C++ 测试代码

## Background & Context
- 源文件是 Apache TVM 项目中用于验证 Caffe 前端正确性的测试脚本
- 源文件同时包含 Caffe 模型构建、Caffe 推理执行、TVM 推理执行和结果比对四部分
- 当前文件结构为单一大文件（1166行），所有算子测试混在一起，维护困难
- 目标位置在 xuanspace vendor/caffe 目录下，该目录已有 caffe-slim 轻量级实现
- Caffe 是开源项目（BSD 2-Clause License），代码可自由提取使用

## Functional Requirements
- **FR-1**: 提取并保留所有 Caffe 算子构建工具函数（_siso_op、_miso_op、_simo_op 等）
- **FR-2**: 提取并保留模型文件生成函数（_save_prototxt、_save_solver、_save_caffemodel 等）
- **FR-3**: 提取并保留 Caffe 推理执行函数（_run_caffe），移除 _run_tvm 和 _compare_caffe_tvm
- **FR-4**: 重构测试流水线函数 _test_op，移除 TVM 执行和比对逻辑，仅保留 Caffe 部分
- **FR-5**: 为每个算子创建独立的测试文件，命名规范为 `test_<op_name_lower>.py`
- **FR-6**: 创建公共工具模块 `utils.py`，存放所有辅助函数
- **FR-7**: 创建 `__init__.py` 使 tests/ops 成为 Python 包
- **FR-8**: 创建 conftest.py 配置 pytest 公共 fixture（如测试数据目录）
- **FR-9**: 保留原始测试用例的所有参数组合和测试数据生成逻辑

## Non-Functional Requirements
- **NFR-1**: 每个测试文件不超过 200 行，保持单一职责
- **NFR-2**: 代码遵循 Python 3.13+ 语法规范，使用 ruff/black/isort 风格
- **NFR-3**: 测试函数命名保持 `test_forward_<OpName>` 格式以便发现
- **NFR-4**: 导入语句按标准库→第三方库→本地模块顺序组织
- **NFR-5**: 移除所有 TVM 相关导入（tvm、tvm.testing、relay、graph_executor、download_testdata）
- **NFR-6**: 文件头部保留 Apache License 声明

## Constraints
- **Technical**: Python 3.13+，依赖 numpy、pytest、protobuf、caffe（pycaffe）
- **Business**: 不修改 vendor/caffe/caffex/ 下的原始 Caffe 源码
- **Dependencies**: 目标环境需已安装 pycaffe（Caffe Python绑定）

## Assumptions
- 目标环境已正确配置 Caffe Python 绑定（import caffe 可用）
- 测试运行时有权限在用户目录下创建临时测试数据文件
- numpy 和 pytest 在目标环境中可用
- google.protobuf 在目标环境中可用

## Acceptance Criteria

### AC-1: 公共工具模块完整性
- **Given**: 源文件中的工具函数已分析完成
- **When**: 创建 utils.py 模块
- **Then**: utils.py 包含 _create_dir、_list_to_str、_gen_filename_str、_save_prototxt、_save_solver、_save_caffemodel、_gen_model_files、_siso_op、_miso_op、_simo_op、_run_caffe、_test_op 函数，且无 TVM 依赖
- **Verification**: `programmatic`
- **Notes**: _test_op 函数需重构为仅执行 Caffe 推理，不调用 TVM

### AC-2: 算子测试文件原子化
- **Given**: utils.py 已创建
- **When**: 为每个算子创建独立测试文件
- **Then**: tests/ops/ 目录下包含 23 个算子测试文件，每个文件对应一个算子，文件名符合 test_<op>.py 规范
- **Verification**: `programmatic`
- **Notes**: 算子列表：BatchNorm、Concat、Convolution、Crop、Deconvolution、Dropout、Eltwise、Flatten、InnerProduct、LRN、Permute、Pooling、Power、PReLU、ReLU、Reshape、Scale、Sigmoid、Slice、Softmax、TanH、Reduction、Embed

### AC-3: TVM 依赖完全移除
- **Given**: 所有文件已创建
- **When**: 扫描所有输出文件
- **Then**: 无任何文件包含 tvm、relay、graph_executor、download_testdata 等 TVM 相关导入或调用
- **Verification**: `programmatic`

### AC-4: 测试用例完整性
- **Given**: 所有算子测试文件已创建
- **When**: 对比源文件中的测试参数
- **Then**: 每个算子的测试用例参数组合（如卷积的 pad/kernel/stride/dilation/group 等各种配置）与源文件完全一致
- **Verification**: `human-judgment`

### AC-5: 包结构正确性
- **Given**: 所有文件已创建
- **When**: 检查目录结构
- **Then**: tests/ops/ 目录包含 __init__.py、conftest.py、utils.py 和 23 个 test_*.py 文件
- **Verification**: `programmatic`

### AC-6: License 声明保留
- **Given**: 所有文件已创建
- **When**: 检查每个 .py 文件头部
- **Then**: 每个 Python 文件头部包含 Apache License 2.0 声明
- **Verification**: `programmatic`

### AC-7: 代码风格符合规范
- **Given**: 所有文件已创建
- **When**: 检查代码风格
- **Then**: 代码行宽不超过 120 字符，导入顺序正确，无未使用导入
- **Verification**: `human-judgment`

## Open Questions
- [ ] 网络级测试（Mobilenetv2等）是否需要后续单独提取？——本次明确排除
- [ ] 测试数据目录是否需要固定位置而非使用 ~/.tvm_test_data？——建议保持原逻辑或使用 pytest tmp_path
- [ ] 是否需要添加 README.md 说明测试库使用方法？——非必须，用户未要求
