# P2-B 阶段：Split层实现 + 性能日志CSV导出 + 极端边界测试 - Product Requirement Document

## Overview
- **Summary**: P2-A 阶段发现 caffe-ffi 缺少 Split 层实现，导致同一 blob 无法被多个 layer 消费（无法构建真正的多分支/残差网络）；同时 P1/P2 的性能日志仅输出到 stderr，无法进行趋势分析。本阶段需要：(1) 实现 C++ Split 层；(2) 编写显式 Split 层多分支网络测试；(3) 将性能日志导出为 CSV；(4) 规划并编写 P2-B 极端边界测试用例。
- **Purpose**: 填补 caffe-ffi 的 Split 层能力缺口，使多分支/残差网络拓扑可正确执行；将性能数据持久化支持趋势分析；补充极端场景测试覆盖。
- **Target Users**: caffe-ffi 开发者和测试人员，使用测试框架验证 C++ 扩展正确性。

## Goals
- **G1**: 实现 Split 层 C++ 代码（1个bottom → N个top，纯数据拷贝），注册到 LayerRegistry
- **G2**: 编写显式 Split 层的多分支网络测试（残差连接、三分支等），验证拓扑正确执行
- **G3**: 将 P1/P2 测试的 perf_trace 性能数据导出为 CSV 文件（含 Δtime/Δmem/Δblobs/test_name 等字段）
- **G4**: 规划并编写 P2-B 极端边界测试用例（超大维度、NaN/Inf 输入、零输入、极端权重等）
- **G5**: 所有测试通过，无回归、无内存泄漏

## Non-Goals (Out of Scope)
- 不实现自动 Split 层插入（在 Net::Init 中自动检测多 consumer blob 并插入 Split）
- 不实现 Split 层零拷贝优化（需解决 COW 机制或 in-place 静态检测问题，待性能 profiling 证明必要后作为 Future Work 实现）
- 不实现多 GPU 并行（caffe-ffi 当前无 GPU 后端）
- 不实现 Python 多线程高并发测试（Python GIL + caffe-ffi 非线程安全，需额外保护）
- 不修改 Caffe protobuf 定义（Split 层无需专属 Parameter）
- 不做 Split 层性能优化（memcpy 初始版本正确性优先）

## Background & Context
- **当前网络构建机制**：[net.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/net.cpp) 的 `AppendBottom` 在消费 blob 后将其从 `available_blobs` 中 erase（L155），每个非 in-place blob 只能被一个 layer 消费。
- **Split 层语义**：Caffe 原生 Split 层接收 1 个 bottom blob，输出 N≥2 个 top blob，每个 top 是 bottom 的完整拷贝（ReshapeLike + memcpy）。这使后续每个 consumer layer 都有独立的 blob 引用，解决了 consume-once 限制。
- **性能日志现状**：[conftest.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/conftest.py) 中 `perf_trace` 通过 `logging.StreamHandler(sys.stderr)` 输出到 stderr，测试结束后数据丢失。
- **现有测试覆盖**：P0(247例) + P1(65例) + P2-A(28例) = 340例通过，覆盖基础API、边界条件、简单拓扑、动态形状、大规模forward。
- **P2-A 发现的限制**：无 Split 层时，多分支网络只能通过多 Input layer 绕过，无法测试真实的残差连接（同一数据走两条路径后相加）。

## Functional Requirements
- **FR-1**: Split 层 C++ 实现（初始版本使用 memcpy 保证正确性）
  - 1 个 bottom blob，N≥1 个 top blob（N=1 时等价于 identity passthrough，N≥2 时拷贝数据到每个 top）
  - Reshape：每个 top blob reshape 为与 bottom 相同的形状（count 字节数）
  - Forward_cpu：将 bottom 数据 memcpy 到每个 top blob（cpu_data → cpu_mdata，count*sizeof(float) 字节）
  - 无 learnable parameters（blobs_ 为空，不需要 LayerSetUp）
  - 精确约束：ExactNumBottomBlobs=1, MinTopBlobs=1
  - 使用 REGISTER_LAYER_CLASS(Split) 注册到 LayerRegistry
  - 头文件位于 `include/caffe_ffi/layers/split_layer.hpp`
  - 实现文件位于 `src/caffe_ffi/layers/split_layer.cpp`
  - 在 `_caffe_ffi.cc` 添加 `#include "caffe_ffi/layers/split_layer.hpp"` 确保静态链接注册
  - **零拷贝优化（Future Work，本阶段不实现）**：
    - **可行性结论**：技术上可行但当前阶段不建议，正确性优先
    - **Blob基础能力**：Blob底层使用TVM FFI Tensor（引用计数ObjectPtr），理论上支持共享；但当前`set_data()`/`set_diff()`均为memcpy而非Tensor共享，`Reshape()`总是分配新Tensor，无ShareData/ShareDiff API
    - **核心风险：in-place数据污染**：ReLU/Dropout等层支持in-place操作（`bottom[0] == top[0]`），通过`cpu_data()`返回的mutable指针直接写内存；若Split多个top共享同一Tensor，一个分支的in-place写入会污染其他分支数据
    - **可选方案评估**：
      - *Copy-on-Write (COW)*：Blob增加共享标记+引用计数，non-const `cpu_data()`时触发深拷贝；需修改Blob核心API，侵入性大；当前`bottom[0]->cpu_data()`即使只读也调用non-const版本（传入`Blob*`而非`const Blob*`），会导致不必要拷贝
      - *静态拓扑分析*：Net::Init时扫描Split后分支是否含in-place层，无in-place则零拷贝；需修改Net初始化逻辑，动态网络场景下不安全
      - *memcpy（本阶段选择）*：与Caffe原版行为一致，实现简单无正确性风险；性能开销在推理场景下可接受（非训练场景无backward的diff拷贝）
    - **触发条件**：待性能profiling（CSV日志分析）证明Split memcpy是热点瓶颈后，再实现COW或静态分析方案

- **FR-2**: Split 层测试用例（test_split_topologies.py）
  - 基础 Split：1→2 split，验证两个 top blob 数据完全一致
  - 三分支 Split：1→3 split + Concat 验证
  - 真残差连接：data → Split → (identity path + FC+ReLU path) → Eltwise SUM → 输出
  - Split + 多层级联：Split 后每个分支独立深层网络
  - Split 确定性：同一输入多次 forward 结果一致
  - Split + in-place 混用：Split 后的分支内部使用 in-place ReLU
  - N=1 Split 退化情况：1→1 split 等价于 passthrough

- **FR-3**: 性能日志 CSV 导出
  - 在 conftest.py 中添加 FileHandler，将 perf 日志同时写入 CSV 文件
  - CSV 文件路径：`tests/python/.temp/perf_log_<timestamp>.csv`（按项目规范放 .temp/）
  - CSV 列：`timestamp,test_class,test_name,operation,elapsed_ms,delta_mem,delta_blobs,extra_fields`
  - perf_trace context manager 在退出时写入一行 CSV 记录
  - _test_timing_log autouse fixture 在 BEGIN/END 时也写入记录
  - pytest_sessionfinish 时输出 CSV 文件路径汇总

- **FR-4**: P2-B 极端边界测试用例（test_extreme_boundaries.py）
  - 超大输入维度：batch=1024, feature_dim=4096（受内存限制调整）
  - 极小维度：1×1 网络、标量-like 输入
  - NaN 输入：forward 不崩溃（行为可预期：NaN传播或报错）
  - Inf 输入：forward 不崩溃
  - 零输入（全零）：输出确定性
  - 极端权重值：极大权重(1e6)、极小权重(1e-6)、零权重
  - 极深网络：20+层 MLP forward
  - 空 forward（不传 input dict，依赖初始 blob 数据）
  - 多次 Reshape 后 forward（极端 shape 变化序列）
  - Net 对象生命周期：创建→forward→删除→再创建 循环稳定性

## Non-Functional Requirements
- **NFR-1**: Split 层实现遵循现有代码风格（参考 relu_layer.cpp/eltwise_layer.cpp）
- **NFR-2**: 所有新增 C++ 代码需有对应的头文件，遵循现有 include 模式
- **NFR-3**: CSV 导出不影响现有 stderr 日志输出（双通道）
- **NFR-4**: 极端测试中内存检测阈值适当放宽（超大 batch 可能有临时分配），但不允许持续性泄漏
- **NFR-5**: 新增文件遵循项目临时文件规范（.temp/ 目录用于运行时产物）
- **NFR-6**: 所有测试必须通过 Docker 容器环境验证（caffe-ffi-jupyter 容器）

## Constraints
- **Technical**: C++17, tvm-ffi, existing CMake build system, no GPU, protobuf caffe.proto
- **Build**: 需在 Docker 容器中重新编译 C++ 扩展以测试 Split 层
- **Dependencies**: pytest, numpy（已在环境中）
- **Project rules**: 临时脚本/日志文件放 `.temp/`；提交遵循 Conventional Commits；代码遵循现有风格

## Assumptions
- caffe.proto 中已有 SplitParameter 定义（标准 Caffe proto 包含），无需修改 proto 文件
- Docker 容器 `caffe-ffi-jupyter` 可正常运行且 conda 环境 `caffe-ffi` 可用
- Split 层无需 backward（当前 caffe-ffi 仅实现推理 forward，无训练 backward）
- 超大维度测试可能因 Docker 容器内存限制而调整参数，不追求极端 OOM

## Acceptance Criteria

### AC-1: Split 层正确实现
- **Given**: 已编译安装包含 Split 层的 caffe-ffi C++ 扩展
- **When**: 构建包含显式 Split 层的多分支网络并执行 forward
- **Then**: 网络构建无 "Unknown bottom blob" 错误，所有 top blob 数据与 bottom 一致，多分支/残差网络输出正确
- **Verification**: `programmatic`

### AC-2: Split 层测试全部通过
- **Given**: test_split_topologies.py 中所有测试用例
- **When**: 在 Docker 容器中运行 pytest
- **Then**: 所有 Split 相关测试通过，残差连接网络输出正确概率分布
- **Verification**: `programmatic`

### AC-3: 性能日志 CSV 文件生成
- **Given**: 运行 P1/P2 测试套件
- **When**: 测试执行完毕
- **Then**: 在 `tests/python/.temp/` 下生成包含所有 perf_trace 记录的 CSV 文件，列齐全，数据与 stderr 日志一致
- **Verification**: `programmatic`

### AC-4: P2-B 极端边界测试通过
- **Given**: test_extreme_boundaries.py 中所有测试用例
- **When**: 在 Docker 容器中运行 pytest
- **Then**: 所有测试通过（NaN/Inf 测试允许报错但不允许 segfault），无持续性内存泄漏
- **Verification**: `programmatic`

### AC-5: 无回归
- **Given**: 完整测试套件（P0+P1+P2-A+Split测试+P2-B）
- **When**: 运行全部测试
- **Then**: 所有测试通过，Δblobs=0，无新增内存泄漏
- **Verification**: `programmatic`

### AC-6: 代码风格一致性
- **Given**: 新增 C++ 和 Python 文件
- **When**: Code review
- **Then**: 代码风格与现有代码一致（命名、缩进、日志格式、错误处理模式）
- **Verification**: `human-judgment`

## Open Questions
- [ ] caffe.proto 中是否有 SplitParameter？需要验证（如果没有则用空参数）
- [ ] CMakeLists.txt 是否自动扫描 layers/ 目录下的新 .cpp 文件？还是需要手动添加？
- [ ] Docker 容器重新编译 C++ 扩展的流程是什么？（editable install 还是 conda build？）
- [ ] 超大维度测试的安全上限是多少？（Docker 容器内存限制）
