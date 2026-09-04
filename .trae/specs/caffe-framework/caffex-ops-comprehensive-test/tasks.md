# Caffex 算子库全面测试 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 扩展测试工具框架 (utils.py)
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 扩展 `tests/ops/utils.py`，添加正确性验证、性能计时、内存检测的基础设施
  - 添加 numpy 参考实现对比函数 `_assert_op_correct`
  - 添加性能计时器上下文管理器 `Timer` 类
  - 添加内存检测工具函数 `_check_memory_usage`（使用 tracemalloc）
  - 添加测试结果收集器，用于后续报告生成
  - 固定随机种子确保可重复性
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, NFR-1, NFR-5
- **Test Requirements**:
  - `programmatic` TR-1.1: 工具函数可正确导入，Timer 类可正常计时（误差<5%）
  - `programmatic` TR-1.2: _assert_op_correct 在差异超阈值时抛出 AssertionError
  - `programmatic` TR-1.3: 内存检测函数可正常运行并返回内存使用数据
  - `human-judgement` TR-1.4: 代码结构清晰，符合现有代码风格
- **Notes**: 保持与现有 API 兼容，不破坏原有 _test_op 函数

## [x] Task 2: 创建 Docker 测试运行脚本
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 在 `docker/origin/` 目录下创建 `run_ops_tests.sh` 脚本
  - 脚本功能：启动 runtime 容器、安装 pytest/pytest-cov/tracemalloc 依赖、挂载 tests/ops/ 目录、运行测试、收集结果
  - 在 Dockerfile 中（或运行时）添加 pytest 等测试依赖安装
  - 创建 `tests/ops/requirements.txt`（如需要）
  - 支持参数：--test-type=correctness|performance|memory|edge|all（默认 all）
- **Acceptance Criteria Addressed**: AC-1, FR-1, NFR-4
- **Test Requirements**:
  - `programmatic` TR-2.1: 脚本可执行，能正确启动容器并进入测试环境
  - `programmatic` TR-2.2: 容器内 pytest --version 可正常运行
  - `programmatic` TR-2.3: tests/ops/ 目录可正确挂载到容器内
  - `human-judgement` TR-2.4: 脚本有帮助信息和错误处理
- **Notes**: 使用 docker run --rm 方式运行，不修改镜像本身；依赖在运行时 pip install

## [x] Task 3: 为激活函数类算子添加正确性+边缘测试（ReLU/Sigmoid/Tanh/PReLU/Power/ELU等）
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 修改以下测试文件：test_relu.py, test_sigmoid.py, test_tanh.py, test_prelu.py, test_power.py
  - 添加 numpy 参考实现（如 ReLU: np.maximum(x, 0)）
  - 添加正确性断言：对比 Caffe 输出与 numpy 输出
  - 添加边缘测试用例：零输入、全负值、极值（1e6, -1e6）、单元素(1,1,1,1)、2D输入
  - 注意：ELU 在 layers.py 中如果存在则添加，否则跳过
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 所有激活函数测试在常规输入下通过（atol=1e-6）
  - `programmatic` TR-3.2: 零输入、极值、单元素等边缘用例有测试覆盖
  - `programmatic` TR-3.3: 2D 和 4D 输入形状都能正确处理
- **Notes**: 逐算子修改，保持原有测试函数不变，添加新的 test_* 函数

## [x] Task 4: 为卷积/池化类算子添加正确性+边缘测试
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 修改 test_convolution.py, test_deconvolution.py, test_pooling.py
  - 添加 numpy 参考实现或简单手动计算验证
  - 卷积可使用简单核（如全1核）验证
  - 池化验证输出形状和最大值/平均值正确性
  - 添加边缘测试：kernel=1x1, stride=kernel_size, padding=same/valid, 1x1特征图
  - 反卷积验证输出形状正确
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 卷积/池化常规输入下数值正确（atol=1e-5）
  - `programmatic` TR-4.2: 不同 kernel_size/stride/padding 组合测试覆盖
  - `programmatic` TR-4.3: 输出形状符合预期

## [x] Task 5: 为归一化/正则化类算子添加正确性+边缘测试
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 修改 test_batchnorm.py, test_lrn.py, test_dropout.py, test_scale.py
  - BatchNorm: 验证归一化公式，可设置 gamma=1, beta=0 简化验证
  - LRN: 验证输出形状和基本数值范围
  - Dropout: 验证训练/测试模式差异（测试模式输出=输入）
  - Scale: 验证 alpha*X + beta 公式正确性
  - 添加边缘测试：单通道、单元素、常数输入
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: BatchNorm/Scale 线性部分数值正确
  - `programmatic` TR-5.2: Dropout 在 TEST 模式下恒等映射
  - `programmatic` TR-5.3: 各算子输出形状正确

## [x] Task 6: 为形状/重排类算子添加正确性+边缘测试
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 修改 test_concat.py, test_slice.py, test_reshape.py, test_flatten.py, test_permute.py, test_crop.py
  - Concat: 沿不同轴拼接，验证形状和数值
  - Slice: 验证切片后的形状和数值对应
  - Reshape/Flatten: 验证重塑后元素总数不变，数值顺序正确
  - Permute: 验证轴置换后形状和数值正确
  - Crop: 验证裁剪形状和数值
  - 添加边缘测试：沿axis=0/1/2/3拼接，空维度？（如果支持），单维度
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 所有形状类算子数值正确（形状操作无精度损失，atol=0）
  - `programmatic` TR-6.2: 不同 axis 参数组合测试覆盖
  - `programmatic` TR-6.3: 元素总数/数值顺序保持一致

## [x] Task 7: 为其他算子（Eltwise/InnerProduct/Softmax/Reduction/Embed等）添加测试
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 修改 test_eltwise.py, test_inner_product.py, test_softmax.py, test_reduction.py, test_embed.py
  - Eltwise: 验证 sum/prod/amax 等操作与 numpy 对应
  - InnerProduct: 验证全连接层计算（Y = XW + b）
  - Softmax: 验证输出和为1，数值正确
  - Reduction: 验证 sum/mean/asum 等归约操作
  - Embed: 验证嵌入层查找正确性
- **Acceptance Criteria Addressed**: AC-2, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 所有算子在常规输入下数值正确
  - `programmatic` TR-7.2: Softmax 输出概率和为1（误差<1e-5）
  - `programmatic` TR-7.3: Eltwise 不同操作类型覆盖

## [x] Task 8: 添加性能基准测试
- **Priority**: medium
- **Depends On**: Task 1, Task 3-7
- **Description**: 
  - 创建 `tests/ops/test_performance.py` 或在各算子测试中添加性能测试
  - 为每个算子定义标准测试形状（如卷积: (1,3,224,224)，全连接: (1,2048)）
  - 每个算子预热1次，运行10次，记录平均时间和标准差
  - 性能数据按算子类型分组，输出排名表格
  - 标记为慢速测试（@pytest.mark.slow），默认不运行，使用 --runslow 触发
- **Acceptance Criteria Addressed**: AC-3, NFR-2
- **Test Requirements**:
  - `programmatic` TR-8.1: 每个算子都有性能测试函数
  - `programmatic` TR-8.2: 性能数据包含 mean、std、num_runs
  - `programmatic` TR-8.3: 性能测试可独立运行（pytest -m slow）
- **Notes**: 性能测试在开发时可跳过，完整测试时运行

## [x] Task 9: 添加内存使用检测
- **Priority**: medium
- **Depends On**: Task 1
- **Description**: 
  - 创建 `tests/ops/test_memory.py`
  - 使用 tracemalloc 跟踪每个算子前后内存变化
  - 每个算子连续运行5次，检测内存是否持续增长（泄漏特征）
  - 记录峰值内存使用
  - 对于多输入算子也要覆盖
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-9.1: 内存测试可运行，每个算子都有检测
  - `programmatic` TR-9.2: 输出内存统计（前/后/差值/峰值）
  - `human-judgement` TR-9.3: 识别异常内存增长（如适用）

## [x] Task 10: 运行完整测试套件，收集结果
- **Priority**: high
- **Depends On**: Task 2, Task 3-9
- **Description**: 
  - 使用 Task 2 创建的脚本在 Docker 中运行完整测试套件
  - 运行所有测试类型：正确性、边缘、性能、内存
  - 收集 pytest 输出、coverage 报告、性能数据、内存数据
  - 保存原始测试日志到 docker/origin/test-results/ 目录
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, NFR-2
- **Test Requirements**:
  - `programmatic` TR-10.1: docker 脚本可成功启动并运行所有测试
  - `programmatic` TR-10.2: pytest 退出码记录，失败用例完整保存
  - `programmatic` TR-10.3: 测试执行时间不超过30分钟（不含性能测试）

## [x] Task 11: 生成结构化测试报告
- **Priority**: high
- **Depends On**: Task 10
- **Description**: 
  - 创建 `docker/origin/OPS_TEST_REPORT.md` 测试报告
  - 报告章节：
    1. 测试概述（环境、时间、覆盖算子列表）
    2. 测试结果摘要（总览表格：通过/失败/跳过数量）
    3. 正确性测试结果（通过率、失败详情、数值精度问题说明）
    4. 性能基准报告（平均时间表、性能排名、图表数据）
    5. 内存使用分析（内存统计表、泄漏检测结果）
    6. 边缘情况与兼容性测试结果
    7. 问题清单（失败用例根因分析、复现步骤、影响范围）
    8. 修复建议与后续工作
- **Acceptance Criteria Addressed**: AC-7, NFR-3
- **Test Requirements**:
  - `human-judgement` TR-11.1: 报告结构完整，包含所有要求章节
  - `human-judgement` TR-11.2: 报告数据与实际测试结果一致
  - `human-judgement` TR-11.3: 失败用例有清晰描述和复现步骤

## [x] Task 12: 问题定位与修复验证
- **Priority**: medium
- **Depends On**: Task 11
- **Description**: 
  - 对测试报告中的失败用例进行根因分析
  - 区分：测试代码问题 vs 算子实现问题 vs 环境/配置问题
  - 测试代码问题：修复测试（如参考实现错误、阈值不合理）
  - 算子实现问题：记录详细复现步骤和现象（不修改 caffex/ 源码）
  - 修复后运行回归测试，验证问题已解决
  - 更新测试报告的问题清单状态
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgement` TR-12.1: 每个失败用例都有根因分类和记录
  - `programmatic` TR-12.2: 修复后的测试重新运行通过
  - `human-judgement` TR-12.3: 算子实现bug有清晰的复现步骤和最小复现用例
- **Notes**: 严格遵守不修改 caffex/ 目录源码的约束；算子bug记录在报告中即可
