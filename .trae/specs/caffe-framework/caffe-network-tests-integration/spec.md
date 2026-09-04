# Caffe网络级端到端测试集成 - Product Requirement Document

## Overview
- **Summary**: 将源文件中4个预训练网络（MobileNetV2、AlexNet、ResNet50、InceptionV1/GoogLeNet）的端到端测试从TVM测试框架中提取出来，集成到Caffe纯测试库中，形成与单算子测试并列的网络级测试模块。
- **Purpose**: 补全Caffe算子测试库的覆盖面，不仅验证单算子正确性，也验证完整网络模型的加载、预处理和推理流程。移除TVM依赖后，网络测试成为纯Caffe推理验证。
- **Target Users**: Caffe框架开发者、模型部署工程师、需要验证Caffe模型正确性的用户

## Goals
- 在 `tests/networks/` 目录下创建独立的网络级测试模块，与 `tests/ops/` 单算子测试平级
- 实现4个网络测试：MobileNetV2、AlexNet、ResNet50、InceptionV1(GoogLeNet)
- 使用Python标准库urllib实现模型下载和本地缓存，替代TVM的download_testdata
- 移除所有TVM依赖（tvm/relay/graph_executor等）
- 不继承源文件中AlexNet/InceptionV1的@pytest.mark.skip标记（该skip是TVM bug导致，非Caffe问题）
- 所有文件包含Apache License 2.0头部
- 网络测试验证：模型加载成功、推理执行成功、输出形状正确、输出无NaN/Inf

## Non-Goals (Out of Scope)
- 不添加新的网络模型测试（仅提取源文件中已有的4个）
- 不训练模型，仅使用预训练权重
- 不做精度对比（无TVM参考）
- 不实现GPU测试（使用CPU模式caffe.TEST）
- 不修改caffex/原始Caffe源码
- 不实现模型下载进度条等高级UI特性

## Background & Context
- 前一阶段已完成23个单算子测试的提取，位于 `tests/ops/`
- 源文件 `test_forward.py` 中还有4个网络级端到端测试未提取
- 网络级测试依赖：
  - `download_testdata`（来自tvm.contrib.download）→ 需要替换
  - `_test_network`（调用_run_tvm和_compare_caffe_tvm）→ 需要重构为纯Caffe版本
  - 预训练模型文件（.prototxt + .caffemodel）需从网络下载
- AlexNet和InceptionV1在源文件中有@pytest.mark.skip(reason="TVM issue #13227")，这是TVM前端转换的bug，与Caffe本身无关
- 网络测试是"加载预训练模型→数据预处理→前向推理"流程，与单算子"构造网络→训练初始化→推理"有本质区别

## Functional Requirements
- **FR-1**: 创建 `tests/networks/` 包目录结构（__init__.py, conftest.py, utils.py）
- **FR-2**: 在 utils.py 中实现模型下载函数 `_download_model`，使用urllib，支持本地缓存
- **FR-3**: 在 utils.py 中实现通用ImageNet预处理函数（mean subtraction + scaling）
- **FR-4**: 在 utils.py 中实现 `_test_network` 纯Caffe版本，仅加载模型、执行推理、返回输出，无TVM比较
- **FR-5**: conftest.py 提供 `caffe_model_dir` fixture，管理模型缓存目录（默认~/.caffe_test_data/models/）
- **FR-6**: 创建 test_mobilenetv2.py（输入1x3x224x224，mean+scale预处理）
- **FR-7**: 创建 test_alexnet.py（输入1x3x227x227，仅mean预处理，不skip）
- **FR-8**: 创建 test_resnet50.py（输入1x3x224x224，仅mean预处理）
- **FR-9**: 创建 test_inceptionv1.py（输入1x3x224x224，mean+scale预处理，不skip，注意源文件注释写的是Inceptionv4实际是GoogLeNet/Inceptionv1）
- **FR-10**: 所有网络测试添加 @pytest.mark.slow 标记（因下载+推理耗时较长）
- **FR-11**: 网络测试验证输出有效性：非空、无NaN、无Inf、形状合理

## Non-Functional Requirements
- **NFR-1**: 代码风格遵循ruff+black+isort（行宽120，Python 3.13+）
- **NFR-2**: 模型缓存幂等：已下载的模型不重复下载
- **NFR-3**: 文件命名规范与ops/一致（test_<modelname>.py）
- **NFR-4**: 导入顺序：标准库→第三方→本地模块
- **NFR-5**: 每个测试文件不超过120行（网络测试预处理代码较多）

## Constraints
- **Technical**: Python 3.13+，仅依赖caffe(pycaffe)、numpy、pytest、google.protobuf、urllib（标准库）
- **Business**: 不得引入TVM或其他深度学习框架依赖
- **Dependencies**: 需要网络连接以下载预训练模型（首次运行时）

## Assumptions
- 测试环境中已编译好pycaffe，可以正常import caffe
- 首次运行测试时有网络连接下载模型文件
- 模型文件URL仍然有效（源文件中的URL来自2018-2020年间）
- ~/.caffe_test_data/models/ 目录有写入权限
- 预训练模型的输入层名称为"data"（标准ImageNet预训练模型约定）

## Acceptance Criteria

### AC-1: 目录结构正确创建
- **Given**: tests/目录已存在且包含ops/子目录
- **When**: 完成网络测试模块创建
- **Then**: tests/networks/ 目录存在，包含 __init__.py、conftest.py、utils.py 和4个test_*.py文件
- **Verification**: `programmatic`
- **Notes**: 共7个文件

### AC-2: utils.py 无TVM依赖且包含必需函数
- **Given**: networks/utils.py已创建
- **When**: 检查导入和函数定义
- **Then**: 无任何tvm/relay/graph_executor/download_testdata导入；包含 _download_model、_preprocess_imagenet、_test_network 函数
- **Verification**: `programmatic`

### AC-3: 模型下载使用标准库且支持缓存
- **Given**: _download_model函数
- **When**: 调用下载同一URL两次
- **Then**: 第一次下载文件到缓存目录，第二次直接返回本地路径不重新下载
- **Verification**: `programmatic`
- **Notes**: 使用urllib.request，缓存目录由fixture提供

### AC-4: 4个网络测试文件全部创建
- **Given**: networks/目录
- **When**: 列出test_*.py文件
- **Then**: test_mobilenetv2.py、test_alexnet.py、test_resnet50.py、test_inceptionv1.py 均存在
- **Verification**: `programmatic`

### AC-5: 网络参数与源文件一致
- **Given**: 4个测试文件
- **When**: 对比源文件中的预处理参数和模型URL
- **Then**:
  - MobileNetV2: mean=[103.939,116.779,123.68], scale=58.8, input=(1,3,224,224)
  - AlexNet: mean=[103.939,116.779,123.68], scale=1.0, input=(1,3,227,227)
  - ResNet50: mean=[103.939,116.779,123.68], scale=1.0, input=(1,3,224,224)
  - InceptionV1: mean=[103.939,116.779,123.68], scale=58.8, input=(1,3,224,224)
  - 模型URL与源文件一致
- **Verification**: `programmatic`

### AC-6: AlexNet和InceptionV1无skip标记
- **Given**: test_alexnet.py和test_inceptionv1.py
- **When**: 检查@pytest.mark.skip装饰器
- **Then**: 两个文件的测试函数均无@pytest.mark.skip装饰器
- **Verification**: `programmatic`
- **Notes**: 源文件中的skip是因TVM bug #13227，纯Caffe测试不需要

### AC-7: 所有文件包含Apache License头部
- **Given**: networks/下所有.py文件
- **When**: 检查文件头部
- **Then**: 每个文件开头包含"Licensed to the Apache Software Foundation"
- **Verification**: `programmatic`

### AC-8: Python语法验证通过
- **Given**: 所有7个.py文件
- **When**: 使用py_compile或ast.parse检查
- **Then**: 无语法错误
- **Verification**: `programmatic`

### AC-9: 所有测试函数有@pytest.mark.slow标记
- **Given**: 4个测试文件
- **When**: 检查测试函数装饰器
- **Then**: 每个test_forward_*函数都有@pytest.mark.slow标记
- **Verification**: `programmatic`

### AC-10: caffex/源码未被修改
- **Given**: vendor/caffe/caffex/目录
- **When**: 检查git状态
- **Then**: caffex/工作树干净，无未提交修改
- **Verification**: `programmatic`

## Open Questions
- [ ] 是否需要提供离线模型放置路径说明（用户可手动下载模型放到缓存目录避免测试时下载）？
- [ ] 网络推理结果是否需要做基本的形状校验（如输出应为1x1000类别概率）？
