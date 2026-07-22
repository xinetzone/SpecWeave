---
version: 1.0
---

# caffeproto 系统性升级：以 reference 为蓝本 Spec

## Why

`external/chaos/caffe` 是 caffeproto 最小化 Caffe protobuf 库的早期版本，缺少 `external/ffi/tvm-book/tests/caffeproto`（reference）中的多项成熟能力：自动化 proto 生成脚本、TVM Relax 算子模块、模型标准化工具、BN-Scale 融合逻辑、L2 归一化支持、以及完善的文档体系。需以 reference 为蓝本进行系统性升级，使两个目录保持结构和能力对齐。

## What Changes

### 新增文件（从 reference 复制/适配）
- `gen_proto.py` — 自动化 proto 代码生成脚本（含 protoc 版本检测、grpc_tools 支持、生成后验证）
- `python/utils.py` — TVM Relax nn.Module 算子实现（Conv2D、ConvTranspose2D、L2Norm）
- `python/caffe_utils.py` — 模型结构标准化工具（unity_struct、unity_inputs、convert_num_to_name）
- `python/caffe_fuse.py` — BN+Scale 融合逻辑
- `python/test_l2norm.py` — L2 归一化算子完整测试套件
- `python/protos/caffe_pb2.py` — 副本 proto 绑定（与 python/caffe_pb2.py 保持同步）

### 修改文件
- `README.md` — **BREAKING** 升级为 `index.md` 风格的综合文档：新增 gen_proto.py 快速生成方式、添加新算子四步法指南、多方式生成说明、代码风格规范
- `CMakeLists.txt` — 简化：用 `protobuf_generate_python` 替代自定义 `generate_proto_python()` 函数，对齐 reference 的简洁风格
- `protos/caffe.proto` — 同步 reference 中的 NormalizeParameter 定义和 norm_param 字段

### 不变文件
- `conanfile.py` — 与 reference 一致，无需修改
- `.conanrc` — 与 reference 一致，无需修改

## Impact

- Affected specs: `caffeproto-l2-normalize`（reference 侧已完成，本次为目标侧同步）
- Affected code: `external/chaos/caffe/` 下 6 个新增文件 + 3 个修改文件

## ADDED Requirements

### Requirement: 自动化 Proto 生成脚本
系统 SHALL 提供 `gen_proto.py` 脚本，支持自动查找 protoc、版本一致性检查、代码生成和验证。

#### Scenario: 用户执行 gen_proto.py
- **WHEN** 用户运行 `python gen_proto.py`
- **THEN** 脚本自动查找 protoc（优先 grpc_tools），检查版本兼容性，生成 caffe_pb2.py 到 `python/` 和 `python/protos/`，并验证生成代码可正常导入

### Requirement: TVM Relax 算子模块
系统 SHALL 在 `python/utils.py` 中提供 Conv2D、ConvTranspose2D、L2Norm 三个 TVM Relax nn.Module 实现。

#### Scenario: 用户导入 L2Norm 模块
- **WHEN** 用户执行 `from utils import L2Norm`
- **THEN** L2Norm 类可用，支持 cross-channel 和 across-spatial 两种归一化模式，支持 channel_shared 和独立 scale 参数

### Requirement: 模型标准化工具
系统 SHALL 在 `python/caffe_utils.py` 中提供 unity_struct、unity_inputs、convert_num_to_name 三个模型标准化函数。

#### Scenario: 用户调用 unity_struct
- **WHEN** 用户传入包含旧式 input/input_dim 字段的 NetParameter
- **THEN** 返回标准化后的 NetParameter，旧字段已清除，输入层显式化，名称统一

### Requirement: BN+Scale 融合
系统 SHALL 在 `python/caffe_fuse.py` 中提供 fuse_network 函数，将相邻的 BatchNorm+Scale 层融合为单个 BatchNorm 层。

#### Scenario: 用户调用 fuse_network
- **WHEN** 用户传入包含相邻 BN+Scale 层的 init_net 和 predict_net
- **THEN** 返回融合后的网络，Scale 层被移除，BN 层参数已更新为融合后的值

### Requirement: 完善文档体系
系统 SHALL 在 `README.md` 中提供与 reference `index.md` 对齐的完整文档，包括多方式生成说明、添加新算子四步法、代码风格规范。

#### Scenario: 新开发者查阅 README.md
- **WHEN** 新开发者打开 README.md
- **THEN** 可找到：依赖安装（3 种方式）、代码生成（3 种方式）、添加新算子四步法、代码风格参考

## MODIFIED Requirements

### Requirement: CMakeLists.txt 简化
**Before**: 使用自定义 `generate_proto_python()` 函数，含 `add_custom_command` 和 `add_custom_target`
**After**: 使用 CMake 内置 `protobuf_generate_python` 函数，代码更简洁，与 reference 对齐

## Non-Functional Requirements

- **NFR-1**: 新增文件与 reference 对应文件内容一致（仅路径适配，不修改逻辑）
- **NFR-2**: `protos/caffe.proto` 同步后两端 proto 定义一致
- **NFR-3**: `python/caffe_pb2.py` 和 `python/protos/caffe_pb2.py` 保持同步
- **NFR-4**: 不引入新的第三方依赖（仅使用 reference 已有的依赖）
- **NFR-5**: 文档使用中文，代码注释使用中文

## Constraints

- **Technical**: 保持与 reference 的 `dataclass + nn.Module` 代码风格一致
- **Dependencies**: protobuf >= 3.x, tvm (relax, 可选，仅 utils.py 需要), numpy
- **Path**: 所有文件位于 `external/chaos/caffe/` 目录下

## Acceptance Criteria

### AC-1: 文件结构对齐
- **Given**: 升级后的 `external/chaos/caffe/`
- **When**: 与 `external/ffi/tvm-book/tests/caffeproto/` 对比
- **Then**: 核心文件结构一致（gen_proto.py、python/utils.py、python/caffe_utils.py、python/caffe_fuse.py、python/test_l2norm.py 均存在）

### AC-2: gen_proto.py 可运行
- **Given**: 已安装 protobuf 和 protoc
- **When**: 运行 `python gen_proto.py`
- **Then**: 代码生成成功，caffe_pb2.py 被更新到正确位置，验证通过

### AC-3: Proto 定义一致
- **Given**: 升级后的 `protos/caffe.proto`
- **When**: 与 reference 的 `protos/caffe.proto` 对比
- **Then**: NormalizeParameter 消息定义和 norm_param 字段完全一致

### AC-4: 测试可运行
- **Given**: 已安装 protobuf
- **When**: 运行 `python test_l2norm.py`
- **Then**: protobuf 相关测试全部通过（TVM 相关测试在无 TVM 环境时 SKIP）

### AC-5: 文档完整
- **Given**: 升级后的 `README.md`
- **When**: 与 reference 的 `index.md` 对比
- **Then**: 包含多方式生成说明、添加新算子四步法、代码风格规范