# Caffe算子测试库提取 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 创建目标目录结构和包初始化文件
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `d:\spaces\SpecWeave\projects\xuanspace\vendor\caffe\tests\ops\` 目录
  - 创建 `__init__.py` 文件（包含 Apache License 头部）
  - 创建 `conftest.py` 配置 pytest 公共 fixture（测试数据目录等）
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录存在且包含 __init__.py
  - `programmatic` TR-1.2: __init__.py 包含 Apache License 2.0 声明
  - `human-judgement` TR-1.3: conftest.py 合理配置测试临时目录，不再依赖 ~/.tvm_test_data
- **Notes**: 使用 pytest 的 tmp_path fixture 或在 conftest 中定义 session 级别的测试目录

## [x] Task 2: 创建公共工具模块 utils.py
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 提取源文件中所有 Caffe 相关的辅助函数到 utils.py
  - 重构 _test_op 函数，移除 TVM 执行和 _compare_caffe_tvm 调用
  - 函数包括：_create_dir、_list_to_str、_gen_filename_str、_save_prototxt、_save_solver、_save_caffemodel、_gen_model_files、_siso_op、_miso_op、_simo_op、_run_caffe、_test_op
  - 移除所有 TVM 相关导入
  - 调整 CURRENT_DIR 使用 pytest 配置的测试目录
- **Acceptance Criteria Addressed**: AC-1, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: utils.py 包含上述所有函数，函数签名与源文件一致
  - `programmatic` TR-2.2: utils.py 中无任何 tvm/relay/graph_executor 导入
  - `programmatic` TR-2.3: _test_op 函数仅执行 Caffe 推理，返回 caffe_out，不调用 TVM
  - `programmatic` TR-2.4: 文件头部包含 Apache License
  - `human-judgement` TR-2.5: 导入顺序符合标准库→第三方→本地模块规范
- **Notes**: _test_op 重构后只需要生成模型文件、运行 Caffe、返回输出；调用方自行决定是否验证

## [x] Task 3: 提取基础算子测试 - 激活函数类（ReLU、Sigmoid、TanH、PReLU、Dropout）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 test_relu.py
  - 创建 test_sigmoid.py
  - 创建 test_tanh.py
  - 创建 test_prelu.py
  - 创建 test_dropout.py
  - 每个文件包含对应的 _test_<op> 辅助函数和 test_forward_<OpName> 测试函数
  - 从 utils 导入所需工具函数
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 5个测试文件均存在，命名正确
  - `programmatic` TR-3.2: 每个文件导入 from utils import ... 而非 TVM 模块
  - `programmatic` TR-3.3: 所有测试参数组合与源文件一致（ReLU 2个用例，Sigmoid 1个，TanH 4个，PReLU 3个，Dropout 2个）
  - `programmatic` TR-3.4: 每个文件头部包含 Apache License
  - `human-judgement` TR-3.5: 每个文件不超过 80 行

## [x] Task 4: 提取基础算子测试 - 归一化/线性代数类（BatchNorm、LRN、Scale、Power、Flatten、InnerProduct）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 test_batchnorm.py
  - 创建 test_lrn.py
  - 创建 test_scale.py
  - 创建 test_power.py
  - 创建 test_flatten.py
  - 创建 test_inner_product.py（注意源文件中注释标题误写为 Flatten）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 6个测试文件均存在
  - `programmatic` TR-4.2: 测试参数组合完整（BatchNorm 2个，LRN 5个，Scale 2个，Power 6个，Flatten 2个，InnerProduct 3个）
  - `programmatic` TR-4.3: 无 TVM 导入
  - `human-judgement` TR-4.4: 代码风格一致

## [x] Task 5: 提取卷积/池化类算子测试（Convolution、Deconvolution、Pooling）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 test_convolution.py（5个测试用例，含group卷积）
  - 创建 test_deconvolution.py（5个测试用例，含group反卷积）
  - 创建 test_pooling.py（6个测试用例：MAX/AVE 各3种配置）
  - 注意 Pooling 使用 P.Pooling.MAX/P.Pooling.AVE 枚举值
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 3个测试文件存在
  - `programmatic` TR-5.2: Convolution 包含5种参数配置（含不同pad/kernel/stride/dilation/group组合）
  - `programmatic` TR-5.3: Deconvolution 包含5种参数配置（含convolution_param嵌套字典和group参数）
  - `programmatic` TR-5.4: Pooling 包含 MAX 和 AVE 两种池化类型，各3种配置（kernel_size/kernel_h-w/global_pooling）
  - `programmatic` TR-5.5: 正确导入 P（params as P）用于 Pooling 枚举
  - `human-judgement` TR-5.6: 长参数列表格式清晰

## [x] Task 6: 提取数据操作类算子测试（Concat、Crop、Slice、Reshape、Permute）
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 创建 test_concat.py（3个测试用例，多输入）
  - 创建 test_crop.py（7个测试用例，双输入，多axis/offset配置）
  - 创建 test_slice.py（4个测试用例，多输出ntop）
  - 创建 test_reshape.py（8个测试用例，各种reshape_param配置）
  - 创建 test_permute.py（6个测试用例，各种维度排列）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 5个测试文件存在
  - `programmatic` TR-6.2: Concat 测试多输入list，axis=0和axis=1
  - `programmatic` TR-6.3: Crop 覆盖 axis=0/1/2 和不同 offset 配置
  - `programmatic` TR-6.4: Slice 使用 ntop 参数触发 _simo_op
  - `programmatic` TR-6.5: Reshape 覆盖dim中0/-1特殊值、axis、num_axes参数
  - `programmatic` TR-6.6: Permute 覆盖6种维度排列顺序
  - `human-judgement` TR-6.7: 多输入/多输出算子的边界情况处理正确

## [x] Task 7: 提取逐元素/归约/嵌入类算子测试（Eltwise、Softmax、Reduction、Embed）
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 创建 test_eltwise.py（8个测试用例，2-6输入，不同operation和coeff）
  - 创建 test_softmax.py（4个测试用例，不同axis）
  - 创建 test_reduction.py（大量测试用例，SUM/ASUM/SUMSQ/MEAN四种操作）
  - 创建 test_embed.py（8个测试用例，1-4维输入，bias_term True/False）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 4个测试文件存在
  - `programmatic` TR-7.2: Eltwise 覆盖 operation=0/1/2（PROD/SUM/MAX）和coeff参数
  - `programmatic` TR-7.3: Softmax 覆盖不同 axis（0/1/2）
  - `programmatic` TR-7.4: Reduction 覆盖 SUM/ASUM/SUMSQ/MEAN 四种操作、不同axis、coeff参数
  - `programmatic` TR-7.5: Embed 覆盖 1D/2D/3D/4D 输入和bias_term开关
  - `human-judgement` TR-7.6: Reduction 测试用例虽多但组织清晰，不超过文件行数限制

## [x] Task 8: 验证所有文件无 TVM 依赖且代码风格正确
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - 全局搜索所有输出文件，确认无 tvm/relay/graph_executor/download_testdata 导入
  - 检查所有文件的 License 头部
  - 检查文件行数不超过限制
  - 验证导入顺序
- **Acceptance Criteria Addressed**: AC-3, AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-8.1: grep 搜索 "import tvm\|from tvm\|relay\|graph_executor\|download_testdata" 返回零结果
  - `programmatic` TR-8.2: 统计 ops 目录下 .py 文件数量为 26 个（__init__ + conftest + utils + 23个算子测试）
  - `programmatic` TR-8.3: 每个 .py 文件第一行（或第二行，在shebang后）包含 "Licensed to the Apache Software Foundation"
  - `human-judgement` TR-8.4: 抽查3个文件确认代码风格（行宽、导入顺序、命名规范）
- **Notes**: 此任务是验证门禁，不通过则回到对应任务修复
