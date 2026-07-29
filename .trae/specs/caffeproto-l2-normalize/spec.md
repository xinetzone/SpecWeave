---
version: 1.0
---

# caffeproto L2归一化算子支持 - Product Requirement Document

## Overview
- **Summary**: 为 caffeproto 最小化 Caffe protobuf 库添加 L2 归一化（Normalize）算子的完整支持，包括 Protobuf 协议定义、Python 序列化/反序列化、TVM Relax 计算模块及测试验证。
- **Purpose**: Caffe-SSD 等目标检测网络中广泛使用 Normalize 层（L2 归一化），当前 caffeproto 缺少该算子的协议定义和 TVM 实现，导致无法解析和部署包含 Normalize 层的模型（如 SSD、SqueezeNet 等的 fire9/concat_norm 等层）。
- **Target Users**: tvm-book 项目开发者、需要将 Caffe-SSD 模型转换到 TVM Relax 的研究人员。

## Goals
- 在 `caffe.proto` 中新增 `NormalizeParameter` 消息定义，字段包括 `across_spatial`、`scale_filler`、`channel_shared`
- 在 `LayerParameter` 中注册 `norm_param` 字段（使用下一个可用 ID 149）
- 在 [utils.py](file:///d:/spaces/SpecWeave/external/ffi/tvm-book/tests/caffeproto/python/utils.py) 中实现 L2 归一化的 TVM Relax 算子模块（`L2Norm`）
- 重新生成 `caffe_pb2.py` 以支持新协议
- 添加单元测试验证序列化/反序列化正确性
- 添加集成测试验证与现有 `caffe_utils.py`、`caffe_fuse.py` 的兼容性

## Non-Goals (Out of Scope)
- 不实现完整的 Caffe 推理引擎（仅实现 TVM Relax 模块，供上层转换使用）
- 不支持 L1 归一化或其他归一化变体（仅 L2 Normalize）
- 不修改 `caffe_fuse.py` 的融合逻辑（Normalize 层一般不参与 BN-Scale 融合）
- 不修改 V1LayerParameter 和 V0LayerParameter 中的枚举（保持向后兼容）

## Background & Context
caffeproto 是 tvm-book 项目中用于解析 Caffe 模型的最小 Protobuf 库，当前支持 Conv2D、ConvTranspose2D、BatchNorm、Scale、ReLU、Pooling 等常见算子。用户截图中展示的 Normalize 层是 Caffe-SSD（Single Shot MultiBox Detector）中 ParseNet 风格的 L2 归一化层，配置如下：

```protobuf
layer {
  name: "fire9/concat_norm"
  type: "Normalize"
  bottom: "s_fire9/expand3x3"
  top: "fire9/concat_norm"
  norm_param {
    across_spatial: false
    scale_filler {
      type: "constant"
      value: 10.0
    }
    channel_shared: false
  }
}
```

**计算逻辑定义**：
- 当 `across_spatial=false` 时：对每个空间位置 (h,w) 独立计算跨通道的 L2 范数，然后归一化
- 当 `across_spatial=true` 时：跨通道和空间维度全局计算 L2 范数
- 归一化公式：`y = scale * x / sqrt(sum(x^2) + eps)`，其中 eps 取 1e-10 防止除零
- `scale_filler` 定义了可学习缩放参数的初始化方式（通常 constant=10 或 1）
- `channel_shared=false` 时每个通道有独立 scale，true 时所有通道共享一个 scale

现有代码结构：
- [caffe.proto](file:///d:/spaces/SpecWeave/external/ffi/tvm-book/tests/caffeproto/protos/caffe.proto)：Protobuf 协议定义，LayerParameter next available ID 为 149
- [caffe_pb2.py](file:///d:/spaces/SpecWeave/external/ffi/tvm-book/tests/caffeproto/python/caffe_pb2.py)：protoc 生成的 Python 绑定
- [utils.py](file:///d:/spaces/SpecWeave/external/ffi/tvm-book/tests/caffeproto/python/utils.py)：TVM Relax nn.Module 实现（Conv2D、ConvTranspose2D）
- [caffe_utils.py](file:///d:/spaces/SpecWeave/external/ffi/tvm-book/tests/caffeproto/python/caffe_utils.py)：模型结构标准化工具
- [caffe_fuse.py](file:///d:/spaces/SpecWeave/external/ffi/tvm-book/tests/caffeproto/python/caffe_fuse.py)：BN+Scale 融合逻辑

## Functional Requirements
- **FR-1**: `NormalizeParameter` 消息定义
  - 字段 `across_spatial`：optional bool，默认值 false
  - 字段 `scale_filler`：optional FillerParameter，默认 constant filler（value=1.0）
  - 字段 `channel_shared`：optional bool，默认值 false
  - 字段 `eps`：optional float，默认值 1e-10（防止除零）
- **FR-2**: LayerParameter 中添加 `norm_param` 字段，ID 149，类型为 NormalizeParameter
- **FR-3**: 更新 LayerParameter 注释，标记 next available ID 为 150
- **FR-4**: utils.py 中实现 `L2Norm` nn.Module 类
  - 参数：num_channels（通道数）、eps、channel_shared、scale_init（scale初始化值）
  - forward 方法执行 L2 归一化 + 可学习 scale
  - 支持 NCHW 布局
  - scale 参数使用 nn.Parameter，可学习
- **FR-5**: 重新生成 caffe_pb2.py 使新消息可用
- **FR-6**: 添加单元测试验证 protobuf 序列化/反序列化往返一致性
- **FR-7**: 添加测试验证 L2Norm TVM 模块前向计算的数值正确性
- **FR-8**: 确保 unity_struct 等现有工具函数不排斥 Normalize 层类型

## Non-Functional Requirements
- **NFR-1**: 代码风格与现有 utils.py 中 Conv2D 模块保持一致（dataclass + nn.Module 模式）
- **NFR-2**: 类型注解完整（遵循现有代码使用 `|` 联合类型、Optional 等）
- **NFR-3**: 不引入新的第三方依赖（仅使用现有 protobuf、tvm、numpy）
- **NFR-4**: 向后兼容：不修改任何现有字段编号，不破坏现有算子定义
- **NFR-5**: 数值稳定性：归一化计算中 eps 默认 1e-10，与 Caffe-SSD 实现一致

## Constraints
- **Technical**: 
  - proto2 语法（与现有 caffe.proto 保持一致）
  - Python dataclass + tvm.relax.testing.nn.Module 模式
  - 使用现有 FillerParameter 类型（无需新建）
- **Business**: 无
- **Dependencies**: protobuf >= 3.x, tvm (relax), numpy

## Assumptions
- 开发环境已安装 protoc 编译器和 Python protobuf 库（README 中有安装指南）
- 用户截图中展示的 Normalize 层配置即目标配置（across_spatial=false, scale_filler=constant(10), channel_shared=false）
- eps 值 1e-10 是 Caffe-SSD 社区的标准选择
- 测试时不需要 GPU，CPU 即可验证 Relax 计算正确性

## Acceptance Criteria

### AC-1: Protobuf 协议正确定义
- **Given**: 修改后的 caffe.proto
- **When**: 用 protoc 编译生成 Python 代码
- **Then**: caffe_pb2 中存在 NormalizeParameter 类，包含 across_spatial、scale_filler、channel_shared、eps 四个字段；LayerParameter 存在 norm_param 属性
- **Verification**: `programmatic`
- **Notes**: 验证字段编号正确、默认值正确

### AC-2: 序列化/反序列化往返一致
- **Given**: 创建一个包含 Normalize 层配置的 NetParameter
- **When**: 将其序列化为二进制再反序列化
- **Then**: 反序列化后的 norm_param 字段值与原始值完全一致（across_spatial=false, scale_filler.type="constant", scale_filler.value=10, channel_shared=false）
- **Verification**: `programmatic`

### AC-3: L2Norm TVM 模块计算正确
- **Given**: 构造 L2Norm 模块，输入形状 (1, C, H, W) 的随机张量
- **When**: 执行 forward 计算
- **Then**: 输出每个空间位置的 L2 范数在乘 scale 后接近 scale_init 值（因为归一化后范数=1，乘以 scale 后范数=scale）；数值误差在 1e-5 以内
- **Verification**: `programmatic`

### AC-4: 与现有模型标准化流程兼容
- **Given**: 一个包含 Normalize 层的简单网络
- **When**: 通过 caffe_utils.unity_struct 处理
- **Then**: 处理不会报错，Normalize 层保留在网络中，输入输出名称被正确标准化
- **Verification**: `programmatic`

### AC-5: 代码风格一致
- **Given**: 新增的 utils.py 中 L2Norm 类和测试文件
- **When**: 与现有 Conv2D 实现对比
- **Then**: 代码风格（dataclass、类型注解、nn.Parameter 使用、forward 签名、nn.emit 调用）完全一致
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要支持 across_spatial=true 的场景（截图中为 false）？决定：实现支持，默认 false，但代码中处理两种情况
- [ ] 是否需要在 caffe_fuse.py 中添加 Normalize 相关融合？决定：不需要，Normalize 不参与标准融合模式
