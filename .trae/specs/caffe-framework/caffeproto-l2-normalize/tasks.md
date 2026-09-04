# caffeproto L2归一化算子支持 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 在 caffe.proto 中添加 NormalizeParameter 消息和 norm_param 字段
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 caffe.proto 的 PReLUParameter 消息定义之后添加 `NormalizeParameter` 消息
  - 字段：`across_spatial`(optional bool, ID 1, default false)、`scale_filler`(optional FillerParameter, ID 2)、`channel_shared`(optional bool, ID 3, default false)、`eps`(optional float, ID 4, default 1e-10)
  - 在 LayerParameter 的 `window_data_param` 字段之后添加 `norm_param`(optional NormalizeParameter, ID 149)
  - 更新 LayerParameter 注释中的 next available layer-specific ID 为 150（last added: norm_param）
  - 保持 proto2 语法，字段编号不与现有字段冲突
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: protoc 编译 caffe.proto 无错误
  - `programmatic` TR-1.2: 生成的 Python 代码中可访问 NormalizeParameter 类且字段正确
  - `human-judgement` TR-1.3: 消息定义与 Caffe-SSD 社区标准一致，注释清晰
- **Notes**: 参照截图中的配置和 Caffe-SSD 官方 Normalize 层定义；字段编号严格遵循现有顺序，149 是下一个可用 ID

## [x] Task 2: 重新生成 caffe_pb2.py
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 使用 protoc 编译器重新编译 caffe.proto，生成新的 caffe_pb2.py
  - 可使用项目的 CMake 构建流程（cmake --preset conan-release && cmake --build --preset conan-release）或直接调用 protoc
  - 验证生成的文件包含 NormalizeParameter 和 norm_param 字段
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-2.1: 新生成的 caffe_pb2.py 中可 import 并创建 NormalizeParameter 实例
  - `programmatic` TR-2.2: LayerParameter 实例可设置 norm_param 属性
- **Notes**: 如果 CMake 环境不便配置，可使用 `protoc --python_out=python protos/caffe.proto` 直接生成

## [x] Task 3: 在 utils.py 中实现 L2Norm TVM Relax 模块
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 ConvTranspose2D 类之后添加 `L2Norm` 类，使用 @dataclass 装饰器，继承 nn.Module
  - `__post_init__` 中：
    - 根据 channel_shared 决定 scale 参数形状：channel_shared=True 时为 (1,)，False 时为 (num_channels,)
    - 创建 nn.Parameter scale，使用 scale_init 值初始化（通过 constant filler 逻辑）
  - `forward` 方法：
    - 计算 x_sq = x * x
    - 根据 across_spatial 决定 reduce 轴：False 时只 reduce channel 轴(axis=1, keepdims=True)；True 时 reduce 除 batch 外所有轴
    - norm = sqrt(sum(x_sq, axis=reduce_axes, keepdims=True) + eps)
    - x_norm = x / norm
    - 根据 channel_shared 和 NCHW 布局 reshape scale 后相乘
    - 使用 nn.emit 返回结果
  - 支持 NCHW 布局（与现有 Conv2D 一致）
- **Acceptance Criteria Addressed**: [AC-3, AC-5]
- **Test Requirements**:
  - `programmatic` TR-3.1: L2Norm 模块可实例化，scale 参数形状正确
  - `programmatic` TR-3.2: channel_shared=True 时 scale 形状为 (1,)，False 时为 (C,)
  - `human-judgement` TR-3.3: 代码风格与 Conv2D/ConvTranspose2D 一致（dataclass、类型注解、nn.Parameter、nn.emit 用法）
- **Notes**: 可参考 tvm.relax.op 中的 sqrt、sum、multiply、divide 等算子

## [x] Task 4: 添加 protobuf 序列化/反序列化单元测试
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 在 python 目录下创建 `test_caffeproto.py`（或 `tests/` 子目录）
  - 测试函数 `test_normalize_param_serialization`：
    - 创建 LayerParameter，type="Normalize"，设置 norm_param（across_spatial=false, scale_filler.type="constant", scale_filler.value=10.0, channel_shared=false）
    - 序列化为二进制字符串 SerializeToString()
    - 反序列化为新的 LayerParameter 对象 ParseFromString()
    - 断言所有字段值与原始值一致
  - 测试函数 `test_normalize_param_defaults`：
    - 创建空 NormalizeParameter，验证默认值（across_spatial=False, channel_shared=False, eps≈1e-10）
  - 测试函数 `test_network_with_normalize_layer`：
    - 创建包含 Input + Normalize 两层的 NetParameter
    - 序列化/反序列化后验证结构完整
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-4.1: 所有测试函数通过 python 直接执行无 AssertionError
  - `programmatic` TR-4.2: 往返序列化后 across_spatial、scale_filler、channel_shared 值完全一致
  - `programmatic` TR-4.3: text_format 文本格式解析也能正确读取 norm_param
- **Notes**: 使用标准 assert 语句，不依赖 pytest（保持轻量）

## [x] Task 5: 添加 L2Norm TVM 模块数值正确性测试
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 在测试文件中添加 `test_l2norm_forward` 函数
  - 构造 numpy 参考实现：
    - 输入 x 形状 (1, C, H, W)，使用 np.random.randn 生成
    - 计算 L2 范数：沿 channel 轴平方和开根号（加 eps）
    - 归一化后乘以 scale（scale 初始化为固定值如 1.0 或 10.0）
  - 使用 tvm.relax.testing.nn.VM 或 relax.build 构建并运行 L2Norm 模块
  - 断言 TVM 输出与 numpy 参考输出的最大绝对误差 < 1e-5
  - 分别测试 channel_shared=True 和 False 两种情况
  - 验证归一化后每个空间位置的范数等于 scale_init 值
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `programmatic` TR-5.1: channel_shared=False 时数值正确，误差<1e-5
  - `programmatic` TR-5.2: channel_shared=True 时数值正确，误差<1e-5
  - `programmatic` TR-5.3: across_spatial=True 模式下范数计算正确（全局归一化）
- **Notes**: 如果 TVM VM 构建较复杂，可先做形状推断和 op 级别测试

## [x] Task 6: 验证与现有 caffe_utils 兼容性
- **Priority**: medium
- **Depends On**: Task 2, Task 4
- **Description**:
  - 创建包含 Input -> Normalize -> Conv 三层的测试网络
  - 调用 caffe_utils.unity_struct 处理
  - 验证处理后网络中 Normalize 层存在，类型仍为 "Normalize"
  - 验证输入输出 blob 名称被正确标准化（无 in-place 冲突）
  - 测试通过 text_format.Merge 读取包含 Normalize 层的 prototxt 文本
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-6.1: unity_struct 处理包含 Normalize 的网络不抛异常
  - `programmatic` TR-6.2: 处理后 Normalize 层数量和参数不变
  - `programmatic` TR-6.3: text_format 可正确解析包含 norm_param 的文本格式
- **Notes**: 现有 unity_struct 只对 Input 层特殊处理，对其他类型层只做名称标准化，理论上无需修改即可兼容

## [x] Task 7: 综合验证与收尾
- **Priority**: medium
- **Depends On**: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6
- **Description**:
  - 运行所有测试脚本确认全部通过
  - 检查代码风格一致性（类型注解、命名、格式）
  - 确保没有破坏现有功能（验证 Conv2D 等已有模块 import 正常）
  - 更新 index.md 如有必要（记录新增算子支持）
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-3, AC-4, AC-5]
- **Test Requirements**:
  - `programmatic` TR-7.1: 所有新增测试通过
  - `programmatic` TR-7.2: 现有 import 不报错（import utils, import caffe_pb2, import caffe_utils 均正常）
  - `human-judgement` TR-7.3: 代码风格审查通过
