# P2-B 阶段 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 实现 C++ Split 层（头文件+实现+注册）
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `include/caffe_ffi/layers/split_layer.hpp`：SplitLayer 类继承 Layer，ExactNumBottomBlobs=1，MinTopBlobs=1（1→N）
  - 创建 `src/caffe_ffi/layers/split_layer.cpp`：
    - Reshape：每个 top blob ReshapeLike(*bottom[0])
    - Forward_cpu：将 bottom[0] 的 cpu_data memcpy 到每个 top[i] 的 cpu_mdata（count 字节数的 float 拷贝）
    - 无 learnable parameters（blobs_ 为空，不需要 LayerSetUp）
    - REGISTER_LAYER_CLASS(Split) 注册
  - 在 `src/caffe_ffi/_caffe_ffi.cc` 添加 `#include "caffe_ffi/layers/split_layer.hpp"` 确保静态链接注册
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: Split 层头文件和实现文件存在，符合现有代码风格（参考 relu_layer.hpp/cpp）
  - `programmatic` TR-1.2: _caffe_ffi.cc 中已添加 include
  - `programmatic` TR-1.3: CMake GLOB 自动包含 split_layer.cpp（无需修改 CMakeLists）
  - `human-judgement` TR-1.4: 代码风格与现有 layer 一致（命名、日志格式、错误检查模式）
- **Notes**: Split 层无 proto 参数（caffe.proto 中无 SplitParameter），不需要 LayerSetUp；Forward 使用 memcpy 而非逐元素拷贝以获得最佳性能

## [ ] Task 2: 重新编译 C++ 扩展并在 Docker 中验证 Split 层可用
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 Docker 容器 `caffe-ffi-jupyter` 中重新编译 caffe-ffi C++ 扩展
  - 验证编译成功，无链接错误
  - 写一个最小验证脚本：创建含 Split 层的简单网络（1 input → Split → 2 tops），确认网络构建成功
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: 编译成功，_caffe_ffi.so/.pyd 包含 Split 层注册
  - `programmatic` TR-2.2: Python 中 `net_from_param` 可创建含 Split 层的网络，无 "Unknown layer type: Split" 错误
- **Notes**: 使用 `pip install -e .` 或 `python -m build` 在容器内编译；需确认容器内的构建命令

## [ ] Task 3: 编写 Split 层多分支网络测试用例（test_split_topologies.py）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建 `tests/python/test_split_topologies.py`，包含 TestSplitLayer 测试类：
    - test_split_1_to_2: 基本 1→2 Split，两个 top 数据完全相同
    - test_split_1_to_3: 1→3 Split + Concat 验证维度正确
    - test_residual_with_split: 真正的残差连接（data→Split→identity 路径 + FC+ReLU 路径→Eltwise SUM→Softmax），输出概率分布有效
    - test_split_three_branch_concat: 三分支→Concat→Softmax
    - test_split_deterministic: Split 网络多次 forward 结果一致
    - test_split_with_inplace_branches: Split 后的分支内部使用 in-place ReLU
    - test_split_in_deep_network: Split 嵌入深层 MLP 中
    - test_split_values_exact_match: 验证 split 后的 top blob 数值与 bottom 完全相等（非近似）
  - 所有测试类加入 conftest.py 的 _P2_TEST_CLASSES 和 _PERF_TEST_CLASSES 集合以启用性能日志
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-3.1: 所有 Split 测试通过
  - `programmatic` TR-3.2: 残差连接网络输出概率之和为 1，shape 正确
  - `programmatic` TR-3.3: Split 后各 top blob 数据与 bottom 完全一致（np.testing.assert_array_equal）
  - `programmatic` TR-3.4: conftest.py 中更新测试类集合
- **Notes**: 残差网络 prototxt 模式：data→Split(data_copy1, data_copy2)→data_copy1→FC→ReLU→branch; data_copy2→identity(直接用); Eltwise SUM(branch, data_copy2)→ip→prob

## [ ] Task 4: 实现性能日志 CSV 导出功能
- **Priority**: high
- **Depends On**: Task 3（需要测试类列表完整）
- **Description**:
  - 修改 `tests/python/conftest.py`：
    - 添加 CSV 文件初始化：在 pytest_configure 或 session 级别 fixture 中创建 `.temp/perf_log_<timestamp>.csv`
    - CSV 列：`timestamp,phase,test_class,test_name,operation,elapsed_ms,delta_mem,delta_blobs,extra`
    - 在 perf_trace context manager 的 finally 块中追加一行 CSV 记录
    - 在 _test_timing_log autouse fixture 的 BEGIN/END 时追加 CSV 记录
    - pytest_sessionfinish 时输出 CSV 文件路径
    - 确保 .temp/ 目录存在（pathlib mkdir）
    - 使用 csv.writer 写入，正确处理 extra 字段中的逗号和特殊字符
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: 运行测试后 .temp/ 目录下生成 CSV 文件
  - `programmatic` TR-4.2: CSV 文件包含表头行和所有 perf_trace 记录
  - `programmatic` TR-4.3: CSV 中 elapsed_ms/delta_mem/delta_blobs 列数值正确
  - `programmatic` TR-4.4: stderr 日志输出不受影响（双通道）
  - `human-judgement` TR-4.5: CSV 可用 Excel/pandas 正常打开，无格式错误
- **Notes**: .temp/ 目录在 .gitignore 中，CSV 文件不会被提交；timestamp 使用 ISO 格式避免覆盖

## [ ] Task 5: 编写 P2-B 极端边界测试用例（test_extreme_boundaries.py）
- **Priority**: high
- **Depends On**: Task 4（CSV 日志需要先就绪）
- **Description**:
  - 创建 `tests/python/test_extreme_boundaries.py`，包含以下测试类：
    - **TestExtremeDimensions**: 超大/超小维度
      - test_large_batch_512: batch=512, feature_dim=64, forward 正确
      - test_large_batch_1024: batch=1024, feature_dim=32（受容器内存限制调整）
      - test_single_element: 1×1 网络（1个sample, 1个feature, 2类输出）
      - test_deep_network_20_layers: 20层 MLP forward 不栈溢出
    - **TestNumericalEdgeCases**: 数值极端输入
      - test_nan_input_no_segfault: NaN 输入不崩溃（允许报错或NaN传播）
      - test_inf_input_no_segfault: Inf 输入不崩溃
      - test_zero_input: 全零输入输出确定性
      - test_negative_input: 全负输入（ReLU后全零路径）
      - test_extreme_weights_large: 权重值 1e6 不溢出（允许 Inf 但不崩溃）
      - test_extreme_weights_tiny: 权重值 1e-6 下溢为零不崩溃
    - **TestShapeChaos**: 混乱形状变化
      - test_alternating_shapes: batch 在 1→1024→1→256→1→512 之间交替
      - test_reshape_then_forward_chain: 多次手动 Reshape blob 后 forward
      - test_empty_forward: 不传 input dict 时的行为（应报错或使用初始数据）
    - **TestLifecycleStress**: 生命周期压力
      - test_create_destroy_50_nets: 创建→forward→销毁 50 个 Net，Δblobs≤2
      - test_shared_weights_across_nets: 同一组权重加载到多个 Net 实例
  - 所有测试类加入 _P2_TEST_CLASSES 以启用性能日志和 CSV 导出
- **Acceptance Criteria Addressed**: AC-4, AC-3
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有极端边界测试通过（NaN/Inf/超大权重测试允许抛异常但不允许 segfault）
  - `programmatic` TR-5.2: 无持续性内存泄漏（生命周期测试 Δblobs≤2）
  - `programmatic` TR-5.3: conftest.py 更新测试类集合
  - `human-judgement` TR-5.4: 测试用例描述清晰，注释说明预期行为
- **Notes**: 超大维度测试参数根据 Docker 容器实际内存调整；NaN/Inf 测试使用 try/except 捕获预期异常，断言不出现进程崩溃

## [ ] Task 6: 在 Docker 中运行完整测试套件验证无回归
- **Priority**: high
- **Depends On**: Task 1-5
- **Description**:
  - 同步所有修改后的文件到 Docker 容器
  - 运行全量测试：`pytest tests/python/ -v`
  - 验证：所有测试通过，1 skip，无新增失败
  - 验证：CSV 文件生成且包含所有性能记录
  - 验证：无内存泄漏（Δblobs=0 at session end）
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: 全部测试通过（P0 247 + P1 65 + P2-A 28 + Split 8 + P2-B ~15 ≈ 363+）
  - `programmatic` TR-6.2: session 结束时无内存泄漏警告
  - `programmatic` TR-6.3: CSV 文件存在且记录数与测试数量匹配
- **Notes**: 运行3次确认稳定性

## [ ] Task 7: 清理临时脚本并原子提交
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 删除所有临时 shell 脚本
  - 在 xuanspace submodule 中按 Conventional Commits 规范原子提交：
    - Commit 1: feat(caffe-ffi): 实现 Split 层支持多分支网络拓扑
    - Commit 2: test(caffe-ffi): 新增Split层多分支/残差网络测试8例
    - Commit 3: test(caffe-ffi): 性能日志CSV导出功能
    - Commit 4: test(caffe-ffi): P2-B极端边界条件测试约15例
  - 验证提交后全量测试仍通过
- **Acceptance Criteria Addressed**: AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 所有提交遵循 Conventional Commits 格式
  - `programmatic` TR-7.2: 每次提交后测试可独立通过
  - `human-judgement` TR-7.3: 提交粒度合理，单一职责
