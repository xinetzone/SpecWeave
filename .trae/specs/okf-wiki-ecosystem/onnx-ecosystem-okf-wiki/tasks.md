# ONNX 生态系统 OKF Wiki 教程 - Implementation Plan

## Task Dependencies

```
Phase 0: Setup → Phase 1: R+I (per bundle) → Phase 2: E (per bundle, references→concepts→examples→indexes) → Phase 3: V (per bundle) → Phase 4: Category + Bundles Index → Phase 5: Independent Review
```

Bundle processing order: onnx/ → ir-py/ → optimizer/ → onnxmltools/ → sklearn-onnx/ → tensorflow-onnx/ → onnx-mlir/ → onnx-tensorrt/

Rationale: onnx/ is the core standard that all other bundles reference; ir-py/ is the Python IR that complements the main project; converters follow (optimizers before converters); compiler/backend last (deepest specialty).

---

## Phase 0: Setup & Scaffolding

### Task 1: 创建 ONNX 生态分类目录和 bundle 脚手架
- **Priority**: high
- **Depends On**: None
- **ACs Addressed**: [AC-1, AC-2]
- **Description**:
  - 创建 `bundles/onnx/` 目录及 `index.md`（含 okf_version frontmatter 和生态概览占位）
  - 创建 8 个子 bundle 目录的空脚手架：`onnx/`, `ir-py/`, `optimizer/`, `onnxmltools/`, `sklearn-onnx/`, `tensorflow-onnx/`, `onnx-mlir/`, `onnx-tensorrt/`
  - 每个 bundle 创建 `concepts/`, `examples/`, `references/` 空目录
  - 创建 `.trae/specs/okf-wiki-ecosystem/onnx-ecosystem-okf-wiki/` 下的工作目录
- **Test Requirements**:
  - `rule` TR-1.1: 目录结构存在且完整（1个category + 8个bundle × 3个子目录 = 25个目录）
  - `rule` TR-1.2: category index.md 包含 okf_version: "0.2"

---

## Phase 1: R+I 阶段（事实采集与架构洞察）

### Task 2: onnx/ 核心项目 - R阶段事实采集
- **Priority**: high
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 深度阅读 onnx/ 核心源码模块：
    - Python: `__init__.py`, `helper.py`, `checker.py`, `compose.py`, `parser.py`, `printer.py`, `serialization.py`, `numpy_helper.py`, `utils.py`, `version.py`, `_mapping.py`, `inliner.py`
    - C++: `common/ir.h`, `common/tensor.h`, `common/visitor.h`, `checker.h/cc`, `defs/schema.h/cc`, `defs/function.h/cc`, `defs/parser.h/cc`, `defs/printer.h/cc`, `defs/shape_inference.h/cc`
    - Protobuf: `onnx.proto` (关键 message 定义), `onnx-ml.proto`
    - defs/ 目录结构（math/nn/rnn/controlflow/...）和算子注册机制
  - 提取 ≥50 条编号事实（F-001起），写入 `.trae/specs/okf-wiki-ecosystem/onnx-ecosystem-okf-wiki/onnx/facts.md`
  - 事实覆盖：protobuf 模型结构、Python Helper API、检查器机制、算子注册、形状推断、C++ IR 类层次、序列化/反序列化、版本转换
- **Test Requirements**:
  - `rule` TR-2.1: 事实数量 ≥50 条，编号连续
  - `rule` TR-2.2: 事实无"用于"/"目的是"/"设计为"等推断词（G1 质量门）
  - `rule` TR-2.3: 每个事实标注源码路径和行号

### Task 3: onnx/ 核心项目 - I阶段架构洞察
- **Priority**: high
- **Depends On**: Task 2
- **ACs Addressed**: [AC-7, AC-9]
- **Description**:
  - 基于 facts.md 提炼 4-6 个核心架构洞察（四元组：陈述+证据(F-xxx)+反常识+行动）
  - 设计知识地图：文档分组（架构基础/核心机制/Python API/C++ 核心/工具链）、学习路径、概念文档覆盖的事实编号
  - 写入 `.trae/specs/okf-wiki-ecosystem/onnx-ecosystem-okf-wiki/onnx/insights.md`
- **Test Requirements**:
  - `rule` TR-3.1: 洞察数量 ≥4 条
  - `rule` TR-3.2: 每条洞察包含陈述/证据/反常识/行动四元组（G2 质量门）
  - `rule` TR-3.3: 知识地图覆盖所有计划的 concepts 文档

### Task 4: ir-py/ - R阶段事实采集 + I阶段洞察
- **Priority**: high
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读 ir-py/ 源码：`_core.py`, `_enums.py`, `_io.py`, `_tape.py`, `serde.py`, `tape.py`, `_name_authority.py`（如存在）, `_linked_list.py`（如存在）, `_metadata.py`（如存在）
  - 提取 ≥30 条事实，写入 `.trae/specs/okf-wiki-ecosystem/onnx-ecosystem-okf-wiki/ir-py/facts.md`
  - 提炼 3-4 个洞察 + 知识地图，写入 `insights.md`
- **Test Requirements**:
  - `rule` TR-4.1: 事实 ≥30 条，无推断词
  - `rule` TR-4.2: 洞察 ≥3 条，四元组完整

### Task 5: optimizer/ - R阶段事实采集 + I阶段洞察
- **Priority**: high
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读 optimizer/ 核心源码（识别 Python 入口和 C++ Pass 基类）
  - 提取 ≥20 条事实，写入 facts.md
  - 提炼 3 个洞察 + 知识地图，写入 insights.md
- **Test Requirements**:
  - `rule` TR-5.1: 事实 ≥20 条，无推断词
  - `rule` TR-5.2: 洞察 ≥3 条，四元组完整

### Task 6: onnxmltools/ - R阶段事实采集 + I阶段洞察
- **Priority**: medium
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读 onnxmltools/ Python 源码结构（识别转换器基类和各工具包转换入口）
  - 提取 ≥20 条事实，写入 facts.md
  - 提炼 3 个洞察 + 知识地图，写入 insights.md
- **Test Requirements**:
  - `rule` TR-6.1: 事实 ≥20 条，无推断词
  - `rule` TR-6.2: 洞察 ≥3 条，四元组完整

### Task 7: sklearn-onnx/ - R阶段事实采集 + I阶段洞察
- **Priority**: medium
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读 sklearn-onnx/ Python 源码结构（转换器基类、算子映射、Pipeline 处理）
  - 提取 ≥20 条事实，写入 facts.md
  - 提炼 3 个洞察 + 知识地图，写入 insights.md
- **Test Requirements**:
  - `rule` TR-7.1: 事实 ≥20 条，无推断词
  - `rule` TR-7.2: 洞察 ≥3 条，四元组完整

### Task 8: tensorflow-onnx/ - R阶段事实采集 + I阶段洞察
- **Priority**: medium
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读 tensorflow-onnx/ Python 源码结构（tf2onnx 转换入口、算子映射、图替换）
  - 提取 ≥20 条事实，写入 facts.md
  - 提炼 3 个洞察 + 知识地图，写入 insights.md
- **Test Requirements**:
  - `rule` TR-8.1: 事实 ≥20 条，无推断词
  - `rule` TR-8.2: 洞察 ≥3 条，四元组完整

### Task 9: onnx-mlir/ - R阶段事实采集（分层采样）+ I阶段洞察
- **Priority**: medium
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 分层阅读 onnx-mlir/：文档（docs/）→ 驱动入口（onnx-mlir.cpp）→ 编译流程文档 → Dialect 核心接口
  - 不逐文件阅读全部 C++ 源码，聚焦架构和核心接口
  - 提取 ≥15 条事实，写入 facts.md
  - 提炼 2-3 个洞察 + 知识地图，写入 insights.md
- **Test Requirements**:
  - `rule` TR-9.1: 事实 ≥15 条，覆盖架构/编译流程/运行时
  - `rule` TR-9.2: 洞察 ≥2 条，四元组完整

### Task 10: onnx-tensorrt/ - R阶段事实采集 + I阶段洞察
- **Priority**: medium
- **Depends On**: Task 1
- **ACs Addressed**: [AC-7]
- **Description**:
  - 阅读 onnx-tensorrt/ C++ 源码（parser 核心、OnnxAttrs、ShapedWeights、bfloat16、Status）
  - 提取 ≥15 条事实，写入 facts.md
  - 提炼 2-3 个洞察 + 知识地图，写入 insights.md
- **Test Requirements**:
  - `rule` TR-10.1: 事实 ≥15 条，无推断词
  - `rule` TR-10.2: 洞察 ≥2 条，四元组完整

---

## Phase 2: E 阶段（批量生成 OKF 文档）

> **E 阶段铁律**：references/ 先生成（信源先行），每批 ≤7 文件，index 最后写。

### Task 11: onnx/ - 生成 references/ 信源文档
- **Priority**: high
- **Depends On**: Task 3
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - 基于 facts.md 和 insights.md 的知识地图，生成 5-8 个 references/ 信源文档
  - 每个信源文档覆盖一个核心源码模块，包含关键事实和代码片段
  - 文档列表（参考 CMake 格式）：
    1. `onnx-proto.md` - onnx.proto 核心 message 定义（ModelProto/GraphProto/NodeProto/...）
    2. `helper-api.md` - helper.py 核心 API（make_tensor_value_info/make_node/make_graph/make_model/...）
    3. `checker.md` - checker.py/checker.cc 检查器实现
    4. `op-schema.md` - defs/schema.h/cc 算子注册机制（OpSchema 类）
    5. `cpp-ir.md` - common/ir.h C++ IR 核心类（Graph/Node/Value）
    6. `serialization.md` - serialization.py 序列化/反序列化
    7. `shape-inference.md` - defs/shape_inference 形状推断
    8. `compose-parser-printer.md` - compose.py/parser.py/printer.py 工具模块
- **Test Requirements**:
  - `rule` TR-11.1: 信源文档数量 5-8 个
  - `rule` TR-11.2: 每个信源文档 frontmatter 完整（type: reference）
  - `rule` TR-11.3: 每个信源包含关键事实 F-xxx 引用和源码路径

### Task 12: onnx/ - 生成 concepts/ 概念文档（批次1：架构基础篇，4-5篇）
- **Priority**: high
- **Depends On**: Task 11
- **ACs Addressed**: [AC-3, AC-4, AC-7, AC-9]
- **Description**:
  - 第一批概念文档（架构基础，≤5篇）：
    1. `00-overall-architecture.md` - ONNX 整体架构与生态定位
    2. `01-protobuf-ir.md` - Protobuf IR：ModelProto/GraphProto/NodeProto 等核心 message
    3. `02-tensor-type-system.md` - 张量类型系统（DataType 枚举、TensorProto、Shape）
    4. `03-computation-graph.md` - 计算图模型：Graph、Node、Input/Output、Initializer
    5. `04-opset-versioning.md` - Opset 版本机制与算子域（ai.onnx/ai.onnx.ml/ai.onnx.preview.training）
  - 每篇含：概述、核心机制（配 ASCII 架构图/表格）、代码示例、相关概念链接
- **Test Requirements**:
  - `rule` TR-12.1: 文档数量 4-5 篇
  - `rule` TR-12.2: frontmatter 完整（type: concept, sources 指向 references/ 和 facts 编号）
  - `rule` TR-12.3: 代码示例中引用的 API 在 references/ 信源中有对应事实

### Task 13: onnx/ - 生成 concepts/ 概念文档（批次2：核心机制篇，4-5篇）
- **Priority**: high
- **Depends On**: Task 12
- **ACs Addressed**: [AC-3, AC-4, AC-7, AC-9]
- **Description**:
  - 第二批概念文档（核心机制，≤5篇）：
    1. `05-operator-schema.md` - 算子定义与注册机制（OpSchema、输入输出、类型约束、shape 推断函数）
    2. `06-shape-inference.md` - 形状推断实现机制
    3. `07-model-checker.md` - 模型检查器（Checker）实现
    4. `08-serialization.md` - 序列化/反序列化（load/save、protobuf 编解码）
    5. `09-python-helpers.md` - Python Helper API 详解（make_* 系列函数）
- **Test Requirements**:
  - `rule` TR-13.1: 文档数量 4-5 篇
  - `rule` TR-13.2: frontmatter 完整，sources 正确
  - `rule` TR-13.3: 交叉链接使用 / 开头 bundle-relative 路径

### Task 14: onnx/ - 生成 concepts/ 概念文档（批次3：高级功能篇，3-4篇）+ examples/（3-5篇）
- **Priority**: high
- **Depends On**: Task 13
- **ACs Addressed**: [AC-3, AC-4, AC-7, AC-9]
- **Description**:
  - 第三批概念文档（高级功能，≤4篇）：
    1. `10-graph-compose.md` - 图组合（Compose）与子图处理
    2. `11-parser-printer.md` - 文本解析器与打印器
    3. `12-cpp-core-ir.md` - C++ 核心 IR（ir.h Graph/Node/Value 类层次）
    4. `13-reference-backend.md` - Python 参考后端实现
  - examples/（3-5 篇）：
    1. `build-linear-regression.md` - 从零构建线性回归模型
    2. `load-check-model.md` - 模型加载、检查与形状推断
    3. `graph-transformation.md` - 图遍历与变换实战
    4. `custom-operator.md` - 自定义算子注册示例
    5. `model-compose.md` - 模型组合实战
- **Test Requirements**:
  - `rule` TR-14.1: 概念文档 3-4 篇，示例文档 3-5 篇
  - `rule` TR-14.2: 每篇 example 含可运行的代码示例（基于 facts.md 中验证过的 API）
  - `rule` TR-14.3: frontmatter 完整（example 类型的 sources 指向相关 concepts 和 references）

### Task 15: onnx/ - 生成 index.md 和 log.md
- **Priority**: high
- **Depends On**: Task 14
- **ACs Addressed**: [AC-2, AC-4]
- **Description**:
  - 生成 concepts/index.md、examples/index.md、references/index.md（子目录索引，无 frontmatter）
  - 生成根 index.md（含 okf_version、知识包概述、文档导航）
  - 生成 log.md（变更日志，记录创建日期和各阶段完成情况）
- **Test Requirements**:
  - `rule` TR-15.1: 子目录 index.md 列出对应目录下所有文档
  - `rule` TR-15.2: 根 index.md 含 okf_version: "0.2" frontmatter
  - `rule` TR-15.3: log.md 包含 2026-08-22 日期记录

### Task 16: ir-py/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: high
- **Depends On**: Task 4
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（3-4篇）：_core.py 核心实体、_enums.py 类型定义、_tape.py/serde.py 序列化与图变换
  - concepts/（6-8篇，分两批，每批≤4篇）：IR整体设计/核心实体Model-Graph-Node-Value/类型系统枚举/序列化反序列化serde/Tape图变换/零拷贝张量与mmap/名称管理
  - examples/（2-3篇）：IR构建计算图/图遍历与变换/序列化到protobuf
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-16.1: references 3-4 篇
  - `rule` TR-16.2: concepts 6-8 篇，分批生成
  - `rule` TR-16.3: examples 2-3 篇
  - `rule` TR-16.4: index.md 和 log.md 完整

### Task 17: optimizer/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: medium
- **Depends On**: Task 5
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（2-3篇）：Pass基类/Python API入口/内置优化passes
  - concepts/（5-7篇，分1-2批）：优化器架构/Pass系统/常量折叠/死代码消除/算子融合/命令行API
  - examples/（2篇）：使用预打包优化passes/自定义优化Pass
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-17.1: references 2-3 篇
  - `rule` TR-17.2: concepts 5-7 篇
  - `rule` TR-17.3: examples 2 篇
  - `rule` TR-17.4: index 和 log 完整

### Task 18: onnxmltools/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: medium
- **Depends On**: Task 6
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（2-3篇）：转换器基类/CoreML转换器/LightGBM-XGBoost转换器入口
  - concepts/（5-7篇，分1-2批）：转换工具架构/CoreML转换器/LightGBM转换器/XGBoost转换器/转换器注册/Pipeline转换
  - examples/（2-3篇）：XGBoost模型转ONNX/Pipeline转换实战
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-18.1: references 2-3 篇
  - `rule` TR-18.2: concepts 5-7 篇
  - `rule` TR-18.3: examples 2-3 篇
  - `rule` TR-18.4: index 和 log 完整

### Task 19: sklearn-onnx/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: medium
- **Depends On**: Task 7
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（2-3篇）：转换器核心API/算子映射表/转换入口
  - concepts/（5-7篇，分1-2批）：sklearn-onnx架构/算子映射机制/Pipeline转换/自定义转换器注册/类型推断
  - examples/（2-3篇）：分类器转ONNX/Pipeline完整转换/自定义模型转换
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-19.1: references 2-3 篇
  - `rule` TR-19.2: concepts 5-7 篇
  - `rule` TR-19.3: examples 2-3 篇
  - `rule` TR-19.4: index 和 log 完整

### Task 20: tensorflow-onnx/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: medium
- **Depends On**: Task 8
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（2-3篇）：转换器入口/图优化器/算子映射
  - concepts/（5-7篇，分1-2批）：tf2onnx架构/TF算子到ONNX映射/图替换机制/命令行转换API/动态形状处理
  - examples/（2-3篇）：Keras模型转换/SavedModel转换/自定义算子映射
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-20.1: references 2-3 篇
  - `rule` TR-20.2: concepts 5-7 篇
  - `rule` TR-20.3: examples 2-3 篇
  - `rule` TR-20.4: index 和 log 完整

### Task 21: onnx-mlir/ - 生成 references/ → concepts/ → examples/ → indexes（分层采样）
- **Priority**: medium
- **Depends On**: Task 9
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（2篇）：驱动入口onnx-mlir.cpp/编译流程核心模块
  - concepts/（4-6篇，1批）：整体架构/ONNX Dialect/编译流程ONNX→MLIR→LLVM/运行时接口/编译选项
  - examples/（1-2篇）：编译ONNX模型为共享库/使用Python运行时
  - indexes + log.md
  - 注意：使用分层采样，不逐文件覆盖C++实现细节
- **Test Requirements**:
  - `rule` TR-21.1: references 2 篇
  - `rule` TR-21.2: concepts 4-6 篇
  - `rule` TR-21.3: examples 1-2 篇
  - `rule` TR-21.4: index 和 log 完整

### Task 22: onnx-tensorrt/ - 生成 references/ → concepts/ → examples/ → indexes
- **Priority**: medium
- **Depends On**: Task 10
- **ACs Addressed**: [AC-3, AC-4, AC-7]
- **Description**:
  - references/（2篇）：解析器核心类/ShapedWeights-OnnxAttrs工具类
  - concepts/（3-5篇，1批）：解析器架构/算子支持矩阵/解析器API/插件机制
  - examples/（1-2篇）：使用解析器加载ONNX模型到TensorRT
  - indexes + log.md
- **Test Requirements**:
  - `rule` TR-22.1: references 2 篇
  - `rule` TR-22.2: concepts 3-5 篇
  - `rule` TR-22.3: examples 1-2 篇
  - `rule` TR-22.4: index 和 log 完整

---

## Phase 3: V 阶段（独立验证）

### Task 23: onnx/ - V阶段验证与修复
- **Priority**: high
- **Depends On**: Task 15
- **ACs Addressed**: [AC-4, AC-5, AC-6, AC-7]
- **Description**:
  - 结构检查：所有文件存在、frontmatter 完整
  - Grep API 验证：随机抽取 ≥15 个类名/方法名，在源码中验证存在性
  - 链接检查：所有交叉引用目标文件存在
  - 修复发现的问题
  - 更新 verified 字段
- **Test Requirements**:
  - `rule` TR-23.1: 结构检查 100% 通过
  - `rule` TR-23.2: Grep 验证 ≥15 个 API，命中率 100%
  - `rule` TR-23.3: 链接检查无断链
  - `rule` TR-23.4: 所有问题修复完成

### Task 24: ir-py/ ~ onnx-tensorrt/ - V阶段验证与修复（7个bundle）
- **Priority**: high
- **Depends On**: Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22
- **ACs Addressed**: [AC-4, AC-5, AC-6, AC-7]
- **Description**:
  - 对 7 个 Tier 2/Tier 3 bundle 逐一执行 V 阶段验证
  - 每个 bundle：结构检查 + Grep 验证（≥8 个 API）+ 链接检查 + 修复
  - 可并行委派独立验证
- **Test Requirements**:
  - `rule` TR-24.1: 7 个 bundle 全部通过结构检查
  - `rule` TR-24.2: 每个 bundle Grep 验证 ≥8 个 API，命中率 100%
  - `rule` TR-24.3: 无断链
  - `rule` TR-24.4: 问题修复完成

---

## Phase 4: 分类索引更新

### Task 25: 完善 onnx/ 分类 index.md 并更新 bundles/index.md
- **Priority**: high
- **Depends On**: Task 23, Task 24
- **ACs Addressed**: [AC-1, AC-8]
- **Description**:
  - 完善 `bundles/onnx/index.md`：添加生态关系概览图、各 bundle 简介、推荐学习路径
  - 更新 `bundles/index.md`：新增"🧠 ONNX 机器学习生态"分组，更新 total_bundles 和 groups 计数
- **Test Requirements**:
  - `rule` TR-25.1: category index.md 列出全部 8 个 bundle 并含简要说明
  - `rule` TR-25.2: bundles/index.md 新增 ONNX 分组条目，计数正确

---

## Phase 5: 独立审查

### Task 26: 独立审查（Independent Review）
- **Priority**: high
- **Depends On**: Task 25
- **ACs Addressed**: [AC-1~AC-9]
- **Description**:
  - 委派一个独立 reviewer（fresh context）对所有产出物进行审查
  - Reviewer 检查：结构完整性、frontmatter 合规、API 真实性（抽样 Grep）、链接有效性、文档质量
  - 产出 review.md 报告
  - 如发现 actionable findings，返回 Implement 阶段修复后重新审查
- **Test Requirements**:
  - `rule` TR-26.1: review.md 存在，包含 pass/fail/blocked 结论
  - `rule` TR-26.2: 所有 rule 类型 AC 有独立通过证据
  - `rubric` TR-26.3: 文档质量评分 ≥1.5/2

---

## Task Summary

| Phase | Tasks | 数量 | 说明 |
|-------|-------|------|------|
| Phase 0: Setup | Task 1 | 1 | 目录脚手架 |
| Phase 1: R+I | Task 2-10 | 9 | 8个bundle的事实采集+洞察（onnx/分2个task） |
| Phase 2: E | Task 11-22 | 12 | 8个bundle的文档生成（onnx/分5个task：ref+3批concept+index） |
| Phase 3: V | Task 23-24 | 2 | 8个bundle的验证修复 |
| Phase 4: Index | Task 25 | 1 | 分类索引+总索引更新 |
| Phase 5: Review | Task 26 | 1 | 独立审查 |
| **Total** | | **26** | |
