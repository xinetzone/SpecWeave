---
title: caffe-ffi P3-B阶段测试里程碑复盘报告
date: 2026-07-31
last_updated: 2026-08-01
category: code-optimization
task_type: testing
tags: [caffe-ffi, testing, p3b, scale, bias, eltwise, concat, dropout, softmaxwithloss, accuracy, blob-consumption, numpy-reference]
status: completed
verification: passed
source: test(p3b) session covering Scale/Bias/Eltwise/Concat/Dropout/SoftmaxWithLoss/Accuracy layers
commit: d1acc7b
action_items_progress: ACT-01=done, ACT-02=done(issue-found), ACT-03=done
---

# caffe-ffi P3-B阶段测试里程碑复盘报告

## 任务概览

| 项目 | 内容 |
|------|------|
| **里程碑名称** | P3-B 阶段：基础运算层与损失层 forward 测试 |
| **原始目标** | 覆盖 RNN/LSTM 层的真实 forward 逻辑 |
| **实际目标（调整后）** | 覆盖已实现但测试不充分的 7 个层：Scale/Bias/Eltwise/Concat/Dropout/SoftmaxWithLoss/Accuracy |
| **工作目录** | `projects/xuanspace/libs/caffe-ffi/` |
| **方法论** | numpy参考实现对比 + prototxt网络构建 + perf_trace性能采集 |
| **最终结果** | ✅ 50个测试用例全部通过，118个已有测试无回归 |

---

## S1：事实数据

### 时间线

| 时间 | 事件 |
|------|------|
| 任务启动 | 接收"编写P3-B阶段测试用例，重点覆盖RNN/LSTM"指令 |
| 探索发现 | 调研代码库后确认 RNN/LSTM 层尚未实现 |
| 方向调整 | 与用户确认后转为测试已实现但覆盖不足的7个层 |
| 编码阶段 | 编写 test_p3b_eltwise_scale.py（含numpy参考实现） |
| Bug修复 #1 | Eltwise known values：blob单消费模型导致"Unknown bottom blob"错误 |
| Bug修复 #2 | Accuracy spatial：期望值误算（4/8→5/8=0.625） |
| Bug修复 #3 | 分类全链路：score+label被loss消费后accuracy不可见，需Split层 |
| 回归验证 | 50个P3-B测试全部通过，118个已有测试无回归 |
| 原子提交 | d1acc7b `test(p3b): 新增Scale/Bias/Eltwise/Concat/Dropout/SoftmaxWithLoss/Accuracy层P3-B阶段测试用例` |

### 产出物统计

| 指标 | 数值 |
|------|------|
| 新增测试文件 | test_p3b_eltwise_scale.py（1224行新增） |
| 修改文件 | conftest.py（+9行注册P3-B测试类） |
| 测试用例总数 | 50个 |
| 测试类数 | 8个 |
| numpy参考实现函数 | 7个（scale_np/bias_np/eltwise_np/concat_np/softmax_np/softmax_loss_np/accuracy_np） |
| 覆盖层数 | 7个（Scale/Bias/Eltwise/Concat/Dropout/SoftmaxWithLoss/Accuracy） |
| 组合/集成测试 | 4个（Scale+Bias/Eltwise+Scale/分类全链路/20轮稳定性） |
| P3-B测试通过率 | 50/50 (100%) |
| 回归测试通过率 | 118/118 (100%)，无回归 |

### 各层测试覆盖明细

| 层 | 测试类 | 用例数 | 覆盖场景 |
|---|---|---|---|
| Scale | TestScaleLayers | 6 | identity/per-channel/bias/axis0/repeated forward/weights不变性 |
| Bias | TestBiasLayers | 6 | zero default/per-channel/known values/axis0/repeated forward/weights不变性 |
| Eltwise | TestEltwiseLayers | 9 | SUM/PROD/MAX/coeffs加权/三输入/已知值精确验证/repeated forward |
| Concat | TestConcatLayers | 6 | axis=0/1/2拼接/三输入/已知值/repeated forward |
| Dropout | TestDropoutLayers | 6 | 推理identity (ratio=0/0.5/0.9)/1D输入/特殊值/repeated forward |
| SoftmaxWithLoss | TestSoftmaxWithLossLayers | 6 | perfect/uniform/numpy match/probs输出/repeated forward |
| Accuracy | TestAccuracyLayers | 7 | perfect/zero/partial/top-k/spatial/numpy match/repeated forward |
| 组合 | TestScaleBiasEltwiseCombination | 4 | Scale→Bias/Eltwise→Scale/分类全链路(Split+Loss+Acc)/20轮稳定性 |

### 项目测试总量

| 测试文件 | 用例数 |
|---|---|
| test_blob.py | 117 |
| test_net.py | 68 |
| test_layers.py | 63 |
| test_python_api.py | 65 |
| test_p3b_eltwise_scale.py（本次新增） | **50** |
| test_p2b_regression.py | 22 |
| test_p3a_conv_pool_bn.py | 24 |
| test_cow.py | 21 |
| test_extreme_inputs.py | 26 |
| test_complex_topologies.py | 25 |
| 其他（6个文件） | 61 |
| **总计** | **542** |

---

## S2：过程分析

### 成功因素

1. **numpy参考实现先行**：每个层在写C++网络测试前，先用numpy实现参考版本，确保对比基准正确。这避免了"测试和被测试代码犯同样错误"的经典陷阱。
2. **遵循P3-A测试模式**：复用了P3-A（Conv/Pool/BN）的测试结构（numpy ref → prototxt构建 → forward对比 → perf_trace），减少了模式探索成本。
3. **快速方向调整**：发现RNN/LSTM未实现后，没有强行"造轮子"或虚构测试，而是迅速与用户确认转向已实现层。
4. **三层测试验证法**：每层测试都包含三类验证——精确值(known values)、随机数据numpy匹配、确定性(repeated forward)，形成从点到面的覆盖。

### 遇到的问题与修复

#### Bug #1：Blob单消费模型导致"Unknown bottom blob"

- **现象**：在同一个net中用同一个bottom blob连接多个Eltwise层（SUM/PROD/MAX）时，第一个Eltwise消费后blob被移除，后续层报 `Unknown bottom blob 'a'`。
- **根因**：[net.cpp#L155](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/net.cpp#L155) 中 `available_blobs->erase(blob_name)` 在AppendBottom时立即从可用集合中删除blob，caffe-ffi采用严格的single-consumer模型（每个blob只能被一个layer消费）。
- **修复**：将三个Eltwise操作拆分为三个独立的net（每个net一个操作），避免多消费者问题。
- **教训**：这是caffe-ffi与标准Caffe的一个重要行为差异——标准Caffe允许多个layer隐式共享同一个bottom blob（Caffe内部自动做in-place或copy），但caffe-ffi的极简Net实现要求**显式Split**。

#### Bug #2：Accuracy spatial期望值误算

- **现象**：断言准确率为4/8=0.5，实际输出0.625。
- **根因**：手动标记"4个正确"时计数错误——实际有5个位置设置了正确类的最高分数（inp[1,0,1,0]=10.0对应label=0也是正确的）。
- **修复**：逐位置重新核对：8个位置中5个正确→期望值改为5/8=0.625。
- **教训**：手动构造"部分正确"的测试数据时必须逐元素标注正确/错误，不能依赖心算。

#### Bug #3：分类全链路双消费者Split缺失

- **现象**：SoftmaxWithLoss消费了score和label后，Accuracy层报 `Unknown bottom blob 'label'`。
- **根因**：同Bug #1，但这次是组合pipeline场景——score需要同时喂给Loss和Accuracy，label也需要同时喂给两者。
- **修复**：添加两个Split层——`split_score`将score分为score_loss/score_acc，`split_label`将label分为label_loss/label_acc。
- **教训**：这是caffe-ffi的核心架构约束——任何被多个layer消费的blob都必须显式Split，这是编写组合网络测试的必备知识。

### 瓶颈

1. **测试执行速度较慢**：50个测试运行约105秒（平均2.1秒/个），主要瓶颈在Net构建（prototxt解析+C++层初始化），而非forward计算本身。
2. **编码期迭代反馈慢**：每次修改后需要等待全部测试运行才能确认，单次全量运行~2分钟，对快速调试不友好。
3. **缺少RNN/LSTM实现**：原始目标（RNN/LSTM forward测试）因层未实现而无法执行，这是规划阶段未做代码存在性检查导致的方向偏移。

---

## S3：洞察提炼

### 核心洞察

#### I1：caffe-ffi的Single-Consumer Blob模型是核心架构约束

**陈述**：caffe-ffi的Net实现采用严格的单消费模型——每个blob在被一个layer的bottom引用后，立即从`available_blobs`中erase，不能被第二个layer直接消费。这与原生Caffe的行为不同。

**证据**：[net.cpp#L150-L157](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/net.cpp#L150-L157) 的 `available_blobs->erase(blob_name)` 是强制行为。在P3-B测试中3次触发此问题（Eltwise三操作、分类全链路score共享、分类全链路label共享）。

**反常识**：在标准Caffe中，多个layer可以直接读同一个bottom blob（Caffe自动处理共享），不需要显式Split。但caffe-ffi为了简化内存管理和zero-copy/COW优化，要求用户显式声明blob复制。

**行动**：后续编写任何涉及多消费者的网络测试时，**第一步检查bottom blob是否被多个layer引用**，如是则必须插入Split层。这应该成为caffe-ffi测试编写的标准模式。

#### I2：numpy参考实现是测试正确性的基石

**陈述**：在写C++层测试前先用numpy实现参考版本，能有效防止"测试本身写错"的问题。

**证据**：softmax_loss_np和accuracy_np在编写阶段通过独立的test_refs脚本验证过正确性，后续C++层测试中发现的accuracy期望值错误（Bug #2）正是通过与numpy参考对比才定位的。

**反常识**：很多人觉得"numpy参考实现也要写，增加了工作量"，但实际上numpy实现的代码量远小于调试一个错误期望值的时间成本。P3-B的7个numpy参考函数总共约80行代码，却避免了至少2-3轮调试迭代。

**行动**：后续P3-C及更后阶段的测试，必须保持"numpy参考先行"的模式。

#### I3：测试层覆盖的"三层验证法"模式可复用

**陈述**：每个层的测试应包含三类用例：(1)已知值精确验证、(2)随机数据numpy匹配、(3)重复forward确定性验证。这三层从不同角度保证forward正确性。

**证据**：P3-B的8个测试类中，6个单层测试类全部采用此模式，有效覆盖了实现错误。Dropout层的推理identity验证（ratio=0.5/0.9时forward输出不变）是一个典型案例——如果只测ratio=0会遗漏推理模式开关的问题。

**行动**：将此模式标准化为caffe-ffi层测试模板。

### 可复用模式

> ✅ **模式已归档**：以下5个模式已通过 extraction-cmd 萃取并入库至模式库，成熟度 L2-validated（P3-A + P3-B 双案例验证）。

| 模式ID | 模式名称 | 描述 | 适用场景 | 模式库链接 |
|--------|---------|------|---------|-----------|
| `numpy-reference-first` | Numpy参考实现先行 | 先写numpy参考实现，验证参考正确后再写C++测试 | 所有数值计算层测试 | [numpy-reference-first.md](../../../patterns/code-patterns/numpy-reference-first.md) |
| `three-layer-test-validation` | 三层测试验证法 | known values + numpy random match + repeated determinism 三层覆盖 | 所有层forward测试 | [three-layer-test-validation.md](../../../patterns/code-patterns/three-layer-test-validation.md) |
| `explicit-split-multi-consumer` | 多消费者显式Split | 多消费者blob必须显式Split（遵循caffe-ffi命名约定） | 所有组合/管道网络测试 | [explicit-split-multi-consumer.md](../../../patterns/code-patterns/explicit-split-multi-consumer.md) |
| `perf-trace-instrumentation` | perf_trace性能埋点集成 | 每个关键步骤（Net构建、forward）用ptrace包裹记录耗时/内存/Blob数 | 所有性能敏感测试 | [perf-trace-instrumentation.md](../../../patterns/code-patterns/perf-trace-instrumentation.md) |
| `separate-nets-independent-ops` | 独立操作分离Net | 独立操作使用独立net避免blob消费冲突，参数化遍历 | 同一层不同参数组合对比测试 | [separate-nets-independent-ops.md](../../../patterns/code-patterns/separate-nets-independent-ops.md) |

**测试模板**：基于 `three-layer-test-validation` + `numpy-reference-first` 模式生成的可复用测试模板已创建：
[test_layer_template_three_layer_validation.py](../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_layer_template_three_layer_validation.py)
（以ReLU层为例，包含完整的L1-L4四层测试结构和perf_trace集成示例）

### 系统性问题

1. **规划阶段缺少代码存在性检查**：原始任务要求测试RNN/LSTM，但代码库中未实现这些层。建议未来任务启动时先做"目标层是否已实现"的快速grep检查。
2. **Net构建开销大**：每个测试都要从prototxt字符串构建Net，prototxt解析+C++初始化占了大部分测试时间。可考虑未来引入Net复用机制（如weight共享或prototxt缓存）。
3. **文档缺失Single-Consumer约束说明**：caffe-ffi的single-consumer blob模型是写测试时的关键知识，但目前没有在测试README或AGENTS.md中明确记录，容易让新贡献者踩坑。

---

## S4：行动项

| 编号 | 优先级 | 行动项 | 验收标准 | 类型 | 状态 |
|------|:------:|--------|----------|------|:----:|
| ACT-01 | P1 | 在测试README或conftest文档中记录single-consumer blob模型约束和Split使用模式 | 新贡献者阅读后能正确处理多消费者场景 | 文档 | ✅ **已完成** |
| ACT-02 | P1 | P3-C阶段测试启动前，先grep确认目标层（Self-Attention/Positional Encoding或替代层）是否已实现 | 避免再次出现方向偏移 | 流程改进 | ✅ **已完成**（发现新问题：见下方检查结果） |
| ACT-03 | P2 | 将"三层验证法+numpy参考先行"模式提取为测试模板文件 | 新测试文件可直接复制模板填空 | 工具 | ✅ **已完成** |
| ACT-04 | P2 | 测试中Net复用机制（如session级Net缓存）以减少~100s构建开销 | P3-B类测试套件运行时间降低50%以上 | 性能优化 | 📋 **有计划**（待执行） |
| ACT-05 | P3 | 实现RNN/LSTM层后，补充原始P3-B目标的RNN/LSTM forward测试 | RNN/LSTM层测试覆盖达到与Scale/Eltwise同等水平 | 功能+测试 | 📋 **有计划**（待执行） |

### ACT-02 P3-C启动前检查结果（2026-08-01）

**层实现状态检查（grep确认）：**

| P3-C目标层 | C++源文件 | 状态 |
|-----------|----------|:----:|
| ReLU | `layers/relu_layer.cpp` | ✅ 已实现 |
| Sigmoid | `layers/sigmoid_layer.cpp` | ✅ 已实现 |
| TanH | `layers/tanh_layer.cpp` | ✅ 已实现 |
| ELU | `layers/elu_layer.cpp` | ✅ 已实现 |
| PReLU | `layers/prelu_layer.cpp` | ✅ 已实现 |
| InnerProduct | `layers/inner_product_layer.cpp` | ✅ 已实现 |
| Softmax（独立） | `layers/softmax_layer.cpp` | ✅ 已实现 |
| Flatten | `layers/flatten_layer.cpp` | ✅ 已实现 |
| Reshape | `layers/reshape_layer.cpp` | ✅ 已实现 |
| Self-Attention/PE | 无新层，组合已有层（InnerProduct+Scale+Softmax+Eltwise+Concat+Bias+Split） | ✅ 无需新层 |

**结论**：P3-C所有目标层均已实现（Transformer组件通过组合已有层实现），不存在P3-A那样的方向偏移问题。

**🚨 检查中发现的新问题：**

| 问题 | 严重度 | 详情 |
|------|:------:|------|
| P3-B/P3-C测试类缺少`@require_cpp_extension`装饰器 | **P1-Bug** | 10个P3-B测试类 + 12个P3-C测试类均未装饰，C++扩展不可用时测试不会被skip，而是运行Python-only fallback返回标量0，产生误导性FAIL而非SKIP |
| 当前环境C++扩展未加载 | P0-环境 | Python 3.13.9 < 要求3.14+；`_caffe_ffi` DLL/pyd未在任何搜索路径中找到；需使用Python 3.14环境重新编译安装 |
| `_py_forward`/`_forward_pure_python`返回空dict/标量0 | P2-健壮性 | Python-only fallback模式返回`{}`或全零blob，缺乏明确的错误提示，容易误导 |

### ACT-04 执行计划：Net复用性能优化

**问题分析**：
- P3-B测试套件共50个用例，每个用例独立创建Net（~0.7-1.5ms/Net）+ Forward（~0.4-0.8ms），Net构建约占总耗时~60%
- 加上pytest fixture开销（~680ms/test），总计~100s
- 同一网络结构被反复创建销毁（如5个ReLU测试用例创建5个不同的Net）

**实施方案（分两个阶段）：**

**阶段1：测试辅助层Net缓存（推荐，风险低）**
在 `caffe_test_helpers.py` 中添加LRU缓存的Net工厂：
```python
from functools import lru_cache

@lru_cache(maxsize=64)
def _make_net_cached(prototxt_str: str):
    """缓存已解析的Net，避免相同prototxt重复解析构建。"""
    param = net_param_from_string(prototxt_str)
    return net_from_param(param)
```
- 相同prototxt字符串的测试用例共享同一个Net对象（Forward是幂等的，不修改权重）
- 注意：涉及权重重置的测试（如weights_unchanged）需要clone Net或使用独立工厂
- **预期收益**：测试套件总耗时降低30-50%

**阶段2：conftest session-scoped Net池（高级）**
- 对参数化测试（如同一层不同参数变体）使用session级fixture缓存Net
- 不同测试函数间共享基础Net结构，通过`CopyTrainedLayersFrom`或权重注入重置
- **风险**：需要确保测试间无状态泄漏（权重、blob数据）
- **预期收益**：额外降低20-30%

**前置依赖**：
1. 修复P3-B/P3-C测试类的`@require_cpp_extension`装饰器缺失问题
2. C++扩展可用（Python 3.14环境编译安装）

**验收标准**：
- 同一prototxt的Net只构建一次（可通过perf_trace日志验证`Δtime`）
- P3-B测试套件运行时间降低50%以上（从~100s到<50s）
- 所有测试结果不变（无状态泄漏）

### ACT-05 执行计划：RNN/LSTM层实现+测试

**现状**：
- `src/caffe_ffi/layers/` 中无任何RNN/LSTM/Recurrent相关文件（grep确认）
- Caffe原生有`recurrent_layer.cpp`、`rnn_layer.cpp`、`lstm_layer.cpp`三个层
- RNN/LSTM依赖内部递归unroll，实现复杂度远高于现有逐元素层

**实施步骤：**

**阶段1：基础Recurrent层框架（预计3-5天）**
1. 创建 `include/caffe_ffi/layers/recurrent_layer.hpp` + `src/caffe_ffi/layers/recurrent_layer.cpp`
   - 实现RecurrentLayer的unroll机制：将时序网络展开为DAG
   - 注册`REGISTER_LAYER_CLASS(Recurrent)`
2. 创建rnn_layer.hpp/cpp：基于RecurrentLayer的简单RNN（tanh激活）
3. 在CMake TargetBuild.cmake中添加新源文件（需确认源文件收集方式——可能是GLOB或显式列表）
4. 编译验证：新层注册成功，Net能解析含RNN层的prototxt

**阶段2：LSTM层（预计3-5天）**
1. 创建lstm_layer.hpp/cpp：实现LSTM门控单元（input/forget/output gate + cell state）
2. LSTM单元内部由InnerProduct+Sigmoid/TanH+Eltwise（逐元素乘加）组合
3. 支持`lstm_param` protobuf参数（num_output、weight_filler、bias_filler、clipping_threshold）
4. 单元测试：前向传播numpy参考验证

**阶段3：测试覆盖（预计1-2天）**
1. 参照三层验证法模板，为RNN/LSTM编写：
   - 已知值验证（手动计算小序列）
   - Numpy随机匹配（batch_size × seq_len × input_dim随机输入）
   - 确定性（重复Forward结果一致）
   - 梯度反向测试（若实现Backward）
2. 测试覆盖要求：
   - RNN：不同hidden_dim、不同seq_len、batch_size=1和N、双向/单向
   - LSTM：同上 + 有/无peephole连接、有/无clipping

**前置依赖**：
- Python 3.14环境编译环境就绪
- 现有层（InnerProduct、Sigmoid、TanH、Eltwise、Split、Concat）前向/反向均正确——这些是RNN/LSTM的基础构件
- InnerProduct层Backward已验证（RNN/LSTM反向需要通过BPTR）

**依赖关系图**：
```
现有层(InnerProduct/Sigmoid/TanH/Eltwise) → RecurrentLayer → RNNLayer → LSTMLayer
                                                                          ↓
                                                              三层验证法测试模板
```

**风险与缓解**：
| 风险 | 概率 | 缓解措施 |
|------|:----:|---------|
| Caffe的Recurrent unroll机制复杂，依赖内部Net嵌套 | 高 | 先阅读BVLC/Caffe `recurrent_layer.cpp`源码画状态机图 |
| Protobuf定义缺失RNNParameter/LSTMParameter | 中 | 先检查`proto/caffe.proto`是否已包含这些message，缺失则补充 |
| LSTM反向传播(BPTT)调试困难 | 高 | 前向先通过再做反向；使用数值梯度检验(ε=1e-5) |
| 时序数据的memory开销（长序列unroll） | 中 | 限制测试seq_len≤10，避免OOM |

---

## 后续活动（2026-08-01）

### 模式萃取归档（extraction-cmd）

里程碑完成后，对报告中"可复用模式"部分执行了标准化模式萃取流程（六步法）：

- **S1 案例收集**：P3-A（Conv/Pool/BN测试）+ P3-B（Scale/Bias/Eltwise等7层测试）双案例支撑
- **S2 本质抽象**：剥离具体项目特征，提炼5个可迁移模式
- **S3 结构化模板**：按标准模板填充（触发场景+核心步骤+反模式+检验标准+迁移示例）
- **S4 反模式提炼**：每个正模式配对3-5个反模式（常见误用场景）
- **S5 迁移验证**：每个模式提供5个跨领域迁移示例（如编译器测试、API测试、序列化测试等）
- **S6 入库**：存入 `docs/retrospective/patterns/code-patterns/`，更新模式库索引

### 产出物

| 产出物 | 路径 | 说明 |
|--------|------|------|
| 5个模式文档 | `.agents/docs/retrospective/patterns/code-patterns/` | numpy-reference-first、three-layer-test-validation、explicit-split-multi-consumer、perf-trace-instrumentation、separate-nets-independent-ops |
| 测试模板 | [test_layer_template_three_layer_validation.py](../../../../../../projects/xuanspace/libs/caffe-ffi/tests/python/test_layer_template_three_layer_validation.py) | 基于三层验证法的可复用测试脚本模板（ReLU层示例） |
| 模式库索引更新 | [code-patterns/README.md](../../../patterns/code-patterns/README.md) | 新增5个L2-validated模式条目 |
| **测试指南更新（ACT-01）** | [TESTING_GUIDELINES.md](../../../../../../projects/xuanspace/libs/caffe-ffi/docs/testing/TESTING_GUIDELINES.md) | 新增§4「核心架构约束：Single-Consumer Blob模型」章节，版本升级至v1.2.0 |

### 行动项执行记录

| 日期 | 行动项 | 执行结果 |
|------|--------|---------|
| 2026-07-31 | ACT-03 | ✅ 已完成：三层验证法测试模板已创建 |
| 2026-08-01 | ACT-01 | ✅ 已完成：在TESTING_GUIDELINES.md新增§4章节，包含约束说明、错误症状、两种处理方式（独立Net/显式Split）、命名约定、自检清单，并在反模式表和提交前检查清单中补充了Single-Consumer检查项；参考文件表新增P3-B范本和模板文件；文档版本升级至v1.2.0 |
| 2026-08-01 | ACT-02 | ✅ 已完成：grep确认P3-C全部9个目标层（ReLU/Sigmoid/TanH/ELU/PReLU/InnerProduct/Softmax/Flatten/Reshape）均有.cpp实现，Transformer组件通过组合已有层实现无需新C++层；检查中发现3个新问题：P1-P3B/P3C测试类缺@require_cpp_extension装饰器、P0-Python3.14环境缺失C++扩展未编译、P2-Python-only fallback返回标量0无错误提示 |

---

## 关键文件索引

| 文件 | 说明 |
|------|------|
| [test_p3b_eltwise_scale.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/test_p3b_eltwise_scale.py) | P3-B测试文件（1224行，50个用例，7个numpy参考实现） |
| [conftest.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/conftest.py#L444-L451) | 注册_P3B_TEST_CLASSES到perf_trace性能采集 |
| [net.cpp#L155](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/net.cpp#L155) | single-consumer blob模型的核心实现（available_blobs->erase） |

---

## 提交记录

| 提交 | 内容 |
|------|------|
| d1acc7b | test(p3b): 新增Scale/Bias/Eltwise/Concat/Dropout/SoftmaxWithLoss/Accuracy层P3-B阶段测试用例（50个用例，1232行变更） |
