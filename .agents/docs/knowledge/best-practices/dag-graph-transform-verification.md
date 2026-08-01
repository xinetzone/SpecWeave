---
id: "dag-graph-transform-verification"
title: "DAG图变换算法验证最佳实践"
date: "2026-08-01"
category: "best-practices"
tags: ["dag", "graph-transform", "visualization", "verification", "caffe", "insert-splits", "in-place"]
source: "../../retrospective/reports/code-optimization/retrospective-caffe-ffi-viz-insert-splits-20260801/README.md"
x-toml-ref: "../../../../.meta/toml/.agents/docs/knowledge/best-practices/dag-graph-transform-verification.toml"
related_patterns: ["graph-transform-validator-architecture", "protobuf-text-minimal-parser"]
---

# DAG图变换算法验证最佳实践

> 源自 caffe-ffi InsertSplits DAG可视化脚本开发复盘

## 核心洞察

### 洞察1：算法忠实移植——索引体系优先于字符串Key

**陈述**：验证图变换算法（如Split插入、算子融合、Layout转换）最可靠的方式是在独立环境中用不同语言忠实移植算法逻辑，第一原则是复制其索引体系（用整数元组而非字符串key），不要做"看起来等价"的简化。

**问题背景**：
移植C++ InsertSplits算法到Python时，直觉认为"同名blob就是同一个东西"，用blob名字符串作为消费者映射的key。但在Caffe的in-place计算模型中，同名blob在不同layer输出时代表不同的计算阶段——最后一个producer才是后续layer实际消费的版本。用字符串做key会丢失这个时序语义，导致in-place层后的fan-out计数错误。

**关键证据**：
- C++ InsertSplits使用`(layer_idx, top_idx)`二元组而非blob名字符串作为生产者标识
- 初始Python实现用blob名做key，导致`fc1_out` fan-out显示为3而非实际的2（fc1→relu1 in-place后实际消费者是fc2/fc3，共2个）
- 修正为使用`(layer_idx, top_idx)`元组追踪每个top输出，配合`blob_to_last_top`随in-place更新后，in-place场景的消费者计数与C++完全一致
- 10个测试用例中，DoubleInplace（双层in-place）和DataAndInplace（组合场景）是最能暴露实现差异的用例

**反常识**：
> 直觉上"同名即等价"在有状态/时序语义的DAG中不成立。名字相同但产生时间不同的blob是不同的实体——in-place计算会覆盖前一个同名blob的内容，后续layer消费的是最后一次产生的版本。

**实践规则**：
1. 移植任何涉及DAG/数据流的C++算法到Python/其他语言时，第一原则是**复制其索引体系**
2. 生产者追踪必须使用`(producer_node_idx, output_idx)`元组，不能简化为字符串名称
3. 必须有专门的in-place更新逻辑：每遇到一个in-place层，更新`blob_name → (producer_idx, output_idx)`映射指向当前层
4. 必须包含双层in-place（如fc→relu→relu双层in-place）测试用例

---

### 洞察2：零依赖最小解析器适用于验证工具

**陈述**：对于格式明确的配置文件（如prototxt/ONNX text/TF text），实现一个最小化解析器（只提取关心的字段）比引入完整protobuf/ONNX依赖更适合作为验证/调试工具。

**问题背景**：
一般认为"不要自己写解析器，用现成库"，但对于验证工具而言：(1)完整protobuf库引入了编译依赖；(2)验证只需要DAG拓扑信息，不需要解析所有param字段；(3)手写的最小解析器完全可控，行为可预测。

**关键证据**：
- Tokenizer仅识别5种token类型（str/num/ident/{/}），约70行代码
- Parser仅提取5个字段（name/input/bottom/top/loss_weight），嵌套param块通过skip逻辑跳过，约65行代码
- 整个解析器约140行，覆盖了10个不同结构的测试用例
- 无需安装protobuf Python包，无版本兼容性问题，零第三方依赖

**决策框架**：当满足以下条件时，优先手写最小解析器：
| 条件 | 判断 |
|------|------|
| 需要提取的字段数 | ≤5个 |
| 是否需要解析嵌套参数块 | 可以跳过（关心拓扑不关心参数） |
| 运行环境约束 | 需要零依赖/开箱即用（CI/调试脚本/验证工具） |
| 输入格式规范 | 语法明确（protobuf text/类似格式） |
| 是否需要完整模型语义 | 否（只关心拓扑/结构） |

**实践规则**：
1. 先列出"我真正需要哪些字段"，如果字段数≤5且嵌套可跳过，手写最小解析器
2. Tokenizer设计控制在5种token类型以内：字符串（带引号）、数字、标识符、左括号、右括号
3. 提供`_skip_block_at()`深度计数`{`/`}`对，跳过不需要的嵌套参数块
4. 无引号的裸词一律归为`ident`（标识符/字段名/枚举值），字符串值必须有引号——这是protobuf text format的核心规则

**反模式警示**：
- ❌ 将裸标识符（如`layer`、`ReLU`、`input_shape`）分类为字符串类型——protobuf text format中，字符串值必须有引号，无引号的词是标识符
- ❌ 尝试解析所有嵌套块——最小解析器的核心价值就是跳过不需要的块
- ❌ 引入完整protobuf/ONNX依赖仅为解析拓扑结构——验证工具不需要完整模型语义

---

### 洞察3：分析阶段独立化——单一数据源原则

**陈述**：将图分析（Pass 1：消费者计数/可达性分析）从图变换（Pass 2：插入Split/节点改写）中解耦出来，第一阶段必须输出结构化数据对象供所有下游消费，禁止每个消费者各自重实现分析逻辑。

**问题背景**：
初始实现中Pass 1逻辑内嵌在`simulate_insert_splits`中，`print_dag_table`和`print_fanout_analysis`使用独立的简化消费者映射，导致in-place场景显示错误数据——"为什么警告说fan-out=3但只插了1个split？"这种不一致会让调试者产生极大困惑。

**关键证据**：
- 提取`analyze_fanout()`独立函数，返回`FanoutAnalysis`数据类后，该函数同时服务于：
  1. simulate的Pass 2输入（决定在哪里插入Split层）
  2. before表格的fan-out标记（显示⚠警告）
  3. fan-out分析表的精确数据（列出每个blob的消费者）
- 三个消费者使用同一份Pass 1数据，保证了"看到的警告"与"实际插入split的决策"完全一致

**DRY原则在分析-变换流水线中的特殊重要性**：
如果分析逻辑（"哪些blob需要split"）和展示逻辑（"哪些blob标记为⚠"）使用不同代码路径，两者的不一致会造成调试信息失真。调试者看到的警告与工具实际行为不匹配，会浪费大量时间排查不存在的问题。

**实践规则**：
1. 任何"先分析再变换"的两阶段（或多阶段）算法，第一阶段必须输出**结构化数据类**（dataclass）
2. 分析结果必须是**单一数据源**：变换逻辑、可视化逻辑、验证逻辑都消费同一份分析结果对象
3. 禁止在可视化/验证代码中独立实现"简化版"分析逻辑——即使看起来很简单
4. 数据类字段设计要同时满足变换和可视化的需求，避免后续为了可视化再回补分析逻辑

---

## 检查清单

在开发DAG图变换验证工具时，逐项检查：

- [ ] 算法移植是否使用了与源语言一致的索引体系（整数元组而非字符串key）？
- [ ] 是否有专门的in-place/覆盖更新逻辑追踪生产者？
- [ ] 是否包含了线性链（无变换）、单fan-out、in-place链、双层in-place、显式已有变换（幂等）、组合场景测试用例？
- [ ] 如果做解析器，是否先确认了需要提取的字段≤5个？
- [ ] Tokenizer是否正确区分了带引号字符串和裸标识符？
- [ ] 分析阶段是否独立为返回结构化数据类的函数？
- [ ] 变换、可视化、验证是否消费同一份分析结果？
- [ ] before/after可视化视图的列是否对齐，同一实体名称是否可追溯？

## 适用场景

- 深度学习框架图变换Pass验证（Caffe/TVM/ONNX/TensorFlow）
- 编译器IR变换验证（LLVM Pass/MLIR）
- 工作流引擎DAG变换调试
- 任意有向图结构变换算法的可视化验证

## 案例来源

- **项目**：caffe-ffi InsertSplits DAG可视化脚本
- **脚本**：`projects/xuanspace/libs/caffe-ffi/scripts/viz_insert_splits.py`（1047行，零第三方依赖）
- **测试**：10个内置测试用例全部通过
