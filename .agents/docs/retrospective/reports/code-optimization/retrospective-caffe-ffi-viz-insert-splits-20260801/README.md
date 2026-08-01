---
title: caffe-ffi InsertSplits DAG可视化脚本开发里程碑复盘
date: 2026-08-01
last_updated: 2026-08-01
category: code-optimization
task_type: tooling
tags: [caffe-ffi, insert-splits, dag, visualization, protobuf, python, graph-transform, testing-tools]
status: completed
verification: passed
source: InsertSplits DAG visualizer Python script development session
session_id: sc-20260801-viz-insert-splits
methodology: seven-concepts R→I→E→C milestone retrospective
---

# caffe-ffi InsertSplits DAG可视化脚本开发里程碑复盘

## 任务概览

| 项目 | 内容 |
|------|------|
| **里程碑名称** | InsertSplits DAG可视化Python脚本 |
| **原始需求** | 生成一个Python脚本，自动解析proto文件并可视化DAG结构以验证InsertSplits逻辑 |
| **工作目录** | `projects/xuanspace/libs/caffe-ffi/` |
| **产出文件** | `scripts/viz_insert_splits.py`（1047行） |
| **方法论** | protobuf文本格式解析 + C++ InsertSplits两遍算法Python移植 + 文本DAG表格 + Graphviz DOT导出 + 10个内置验证用例 |
| **最终结果** | ✅ 脚本交付，10/10内置测试用例全部通过，零第三方依赖 |

---

## S1：事实数据（R阶段）

### 时间线

| 序号 | 事件 |
|------|------|
| F1 | 用户需求：生成Python脚本，解析proto文件并可视化DAG结构验证InsertSplits逻辑 |
| F2 | 此前已完成工作：InsertSplits C++实现（net.cpp L97-390），C++单元测试（test_insert_splits.cpp），InsertSplits在Net::Init中集成（net.cpp L422） |
| F3 | 确定脚本架构：proto解析 → DAG构建 → 消费者计数（Pass 1）→ split预测（Pass 2）→ 可视化 |
| F4 | 实现`_tokenize`函数：自定义tokenizer，识别str(quoted)/num/ident/{/}五种token类型 |
| F5 | 初始tokenizer将裸标识符（如layer、input_shape）分类为str类型 |
| F6 | 修正tokenizer：裸词分类为ident（非str），修复layer字段检测 |
| F7 | PowerShell中`python -c`传入多行proto文本时遭遇转义问题 |
| F8 | 创建临时调试文件`_debug_parse.py`绕过inline脚本转义问题 |
| F9 | 实现`parse_prototxt`：提取name/input/layer{name,type,bottom,top,loss_weight}字段，嵌套param块通过`_skip_block_at`跳过 |
| F10 | 出现`ValueError: too many values to unpack`：`for i, layer in net.layers`漏写enumerate |
| F11 | 修复枚举bug，改为`for i, layer in enumerate(net.layers)` |
| F12 | 实现`simulate_insert_splits`两遍算法：Pass 1消费者计数 + Pass 2重写bottoms并插入Split层 |
| F13 | 实现`_make_split_layer`、`_split_layer_name`、`_split_blob_name`命名辅助函数，命名规则与C++`ConfigureSplitLayer`对齐：`{blob}_{producer}_{blob_idx}_split_{k}` |
| F14 | 实现`print_dag_table`文本表格可视化，标记高fan-out blob（⚠）和自动插入的Split层（==>） |
| F15 | 发现DAG before表格中fan-out计数错误：in-place层（如ReLU in-place）后同一名blob的消费者数被累计到首次producer上，显示fc1_out fan-out=3而非实际的2 |
| F16 | 将Pass 1逻辑提取为独立的`analyze_fanout()`函数，返回`FanoutAnalysis`数据类 |
| F17 | `print_dag_table`和`print_fanout_analysis`改为接收`FanoutAnalysis`参数，使用正确的last-producer语义进行fan-out计算 |
| F18 | 修复后fc1_out（fc1产生）显示1个消费者（relu1），fc1_out（relu1产生，in-place）显示2个消费者（fc2, fc3），与C++行为一致 |
| F19 | 发现代码中有重复的`_skip_block_at`函数和未使用的`_producer_map`变量 |
| F20 | 删除重复函数和未使用变量（dead code清理） |
| F21 | 长split blob名称（如fc1_out_relu1_0_split_0）在表格中被截断 |
| F22 | 增加`_trunc`辅助函数处理超长名称（末尾加…），调整表格列宽至120字符 |
| F23 | 实现10个内置测试用例：TwoConsumer/InplaceTwoConsumer/LinearChain/InputLayerThreeConsumer/ExplicitSplit/LossWeight/DoubleInplace/DataAndInplace/Empty/BadRef |
| F24 | 实现`verify_case`函数：验证自动插入Split层数量和名称与预期一致 |
| F25 | 实现`to_dot`函数：生成Graphviz DOT格式，before/after双cluster对比 |
| F26 | 实现CLI（argparse）：支持file/--case/--all/--dot/--mode/--verify/--quiet参数 |
| F27 | 运行`python scripts/viz_insert_splits.py --verify`，10个用例全部通过 |
| F28 | 删除临时调试文件`_debug_parse.py`和测试生成的`dag_dataandinplace.dot` |
| F29 | 最终验证：`py_compile`语法检查通过，10/10测试用例通过 |

### 产出物统计

| 指标 | 数值 |
|------|------|
| 新增文件 | `scripts/viz_insert_splits.py` |
| 文件行数 | 1047行 |
| 第三方依赖 | 0个（仅标准库：argparse/sys/textwrap/dataclasses/typing） |
| 核心函数 | 10个（_tokenize/parse_prototxt/analyze_fanout/simulate_insert_splits/print_dag_table/print_fanout_analysis/to_dot/verify_case/run_case/main） |
| 数据类 | 3个（Layer/NetSpec/FanoutAnalysis） |
| 内置测试用例 | 10个 |
| 支持模式 | 2种（caffe-ffi外部input/native Caffe Input层） |
| 可视化输出 | 文本DAG表格 + Fan-out分析表 + Graphviz DOT导出 |
| CLI参数 | 7个（file/--case/--all/--dot/--mode/--verify/--quiet） |
| 测试通过率 | 10/10 (100%) |

### 内置测试用例覆盖矩阵

| 用例名 | 测试场景 | 预期Split数 | 自动Split名称 |
|--------|----------|------------|--------------|
| TwoConsumer | 外部input→fc1+fc2（fan-out=2） | 1 | data_input_0_split |
| InplaceTwoConsumer | fc1→relu1(in-place)→fc2+fc3 | 1 | fc1_out_relu1_0_split |
| LinearChain | fc1→relu(in-place)→fc2（线性链，无fan-out） | 0 | — |
| InputLayerThreeConsumer | Input层→fc1+fc2+fc3（fan-out=3） | 1 | data_data_0_split |
| ExplicitSplit | 用户已有显式Split层（幂等性） | 0 | — |
| LossWeight | loss_weight:1.0作为额外消费者 | 1 | fc1_out_fc1_0_split |
| DoubleInplace | fc1→relu1(x)→relu2(x)→fc2+fc3（双层in-place） | 1 | x_relu2_0_split |
| DataAndInplace | 外部input fan-out + in-place fan-out 组合 | 2 | data_input_0_split, fc1_out_relu1_0_split |
| Empty | 仅有input无layer | 0 | — |
| BadRef | 引用不存在的blob | 抛ValueError | — |

### Bug修复记录

| Bug编号 | 现象 | 修复动作 |
|---------|------|---------|
| B1 | 裸标识符（layer/input_shape等）被分类为str而非ident，导致layer无法被解析 | 修改`_tokenize`裸词分类逻辑，无引号的单词归为ident |
| B2 | PowerShell inline python -c传多行proto文本转义失败 | 创建`_debug_parse.py`临时文件调试（后续已删除） |
| B3 | `for i, layer in net.layers`漏写enumerate导致ValueError | 添加enumerate |
| B4 | 初始fan-out分析使用简单blob名→消费者映射，in-place层后同blob名消费者被错误累计到首个producer | 提取`analyze_fanout()`独立函数，使用(layer_idx, top_idx)元组追踪每个top输出，blob_to_last_top随in-place更新 |
| B5 | 代码中存在重复的`_skip_block_at`函数 | 删除重复定义 |
| B6 | 长split blob名称在表格中溢出列宽 | 添加`_trunc`函数+调整列宽至120字符 |

---

## S2：核心洞察（I阶段）

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S3 | event=CONCEPT_COMPLETED | session=sc-20260801-viz-insert-splits | concept=R | facts=29
```

### 洞察1：图变换算法可视化验证的核心是算法忠实移植

**陈述**：验证图变换算法（如InsertSplits）最可靠的方式是在独立环境中用不同语言忠实移植算法逻辑，通过对比变换前后的DAG结构来验证正确性。

**证据**：
- C++ InsertSplits使用(layer_idx, top_idx)二元组而非blob名字符串作为生产者标识（F15→F17）
- 初始Python实现用blob名做key导致in-place层消费者计数偏差（B4）
- 提取`analyze_fanout()`精确复制Pass 1语义后，in-place场景的消费者计数与C++完全一致（F18）
- 10个测试用例中，DoubleInplace（双层in-place）和DataAndInplace（组合场景）是最能暴露实现差异的用例（F23-F24）

**反常识**：直觉上"同名blob就是同一个东西"，但在Caffe的in-place计算模型中，同名blob在不同layer输出时代表不同的计算阶段——最后一个producer才是后续layer实际消费的版本。用字符串做key会丢失这个时序语义。

**下次行动**：移植任何涉及DAG/数据流的C++算法到Python时，第一原则是复制其索引体系（用整数元组而非字符串key），不要做"看起来等价"的简化。

### 洞察2：零依赖原型解析器是验证工具的可行路径

**陈述**：对于格式明确的配置文件（如prototxt），实现一个最小化解析器（只提取关心的字段）比引入完整protobuf依赖更适合作为验证工具。

**证据**：
- `_tokenize`仅5种token类型（str/num/ident/{/}），约70行代码（F4）
- `parse_prototxt`仅提取5个字段（name/input/bottom/top/loss_weight），嵌套param块通过`_skip_block_at`跳过，约65行代码（F9）
- 整个解析器约140行，覆盖了10个不同结构的测试用例（F23, F27）
- 无需安装protobuf Python包，无版本兼容性问题

**反常识**：一般认为"不要自己写解析器，用现成库"，但对于验证工具而言：(1)完整protobuf库引入了编译依赖；(2)验证只需要DAG拓扑信息，不需要解析所有param字段；(3)手写的最小解析器完全可控，行为可预测。

**下次行动**：为验证/调试目的编写解析工具时，先列出"我真正需要哪些字段"，如果字段数≤5且嵌套可跳过，手写最小解析器比引入重依赖更高效。

### 洞察3：Pass 1独立化为可复用分析函数的价值

**陈述**：将图分析（Pass 1：消费者计数）从图变换（Pass 2：插入Split）中解耦出来，使分析结果可被可视化、验证、调试等多个下游消费。

**证据**：
- 初始实现中Pass 1逻辑内嵌在`simulate_insert_splits`中，`print_dag_table`和`print_fanout_analysis`使用独立的简化消费者映射，导致in-place场景显示错误数据（F15, B4）
- 提取`analyze_fanout()`后，该函数同时服务于：(1)simulate的Pass 2输入；(2)before表格的fan-out标记；(3)fan-out分析表的精确数据（F16-F17）
- 三个消费者使用同一份Pass 1数据，保证了"看到的警告"与"实际插入split的决策"完全一致

**反常识**：DRY原则在分析-变换流水线中尤其关键——如果分析逻辑（"哪些blob需要split"）和展示逻辑（"哪些blob标记为⚠"）使用不同代码路径，两者的不一致会让调试者产生困惑："为什么警告说fan-out=3但只插了1个split？"

**下次行动**：任何"先分析再变换"的两阶段算法，第一阶段必须输出结构化数据对象供所有下游消费，禁止每个消费者各自重实现分析逻辑。

---

G2质量门检查：3条洞察均包含四元组（陈述+证据+反常识+下次行动）。通过 ✅。

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S4 | event=GATE_PASSED | session=sc-20260801-viz-insert-splits | gate=G2 | result=pass
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S5 | event=CONCEPT_COMPLETED | session=sc-20260801-viz-insert-splits | concept=I | insights=3
```

---

## S3：模式萃取（E阶段）

### 模式1：图变换验证工具的"解析-分析-变换-可视化"四段式架构

**触发场景**：需要验证一个DAG/图变换算法（如split插入、op融合、layout转换）的正确性，且目标环境运行成本高（需要编译、依赖重）。

**核心步骤**：

1. **最小解析器（Parser）**：只提取拓扑结构所需字段（节点名/类型/输入边/输出边/权重标记），跳过所有嵌套参数块。token类型控制在5种以内（字符串/数字/标识符/括号）。
2. **分析阶段独立化（Analyzer）**：将Pass 1（消费者计数/可达性分析/类型推断等）提取为独立函数，返回结构化数据类（dataclass），供变换和可视化共同消费。禁止在可视化代码中重实现分析逻辑。
3. **变换模拟（Transformer）**：忠实移植源算法两遍逻辑，使用与源语言一致的索引体系（整数元组而非字符串key），保持命名规则一致。
4. **双视图可视化（Visualizer）**：BEFORE视图展示原始DAG+fan-out警告（⚠标记），AFTER视图展示变换后DAG+自动插入节点高亮（==>标记），两张表结构完全一致便于diff。

**关键设计约束**：
- 零第三方依赖（仅标准库）
- 内置测试用例≥8个，必须覆盖：线性链（无变换）、单fan-out、in-place链、双层in-place、显式已有变换（幂等）、权重触发、错误引用、组合场景
- before/after表格列对齐，同一blob在两张表中名称完全可追溯
- 错误处理与源算法对齐（源算法FATAL的场景也抛异常）

**反模式**：
- ❌ 用字符串key替代整数索引追踪图节点（in-place场景会丢失时序语义）
- ❌ 可视化代码中独立实现简化版分析逻辑（分析与变换使用不同数据→显示与实际不一致）
- ❌ 引入完整protobuf/ONNX等重依赖仅为解析拓扑（验证工具不需要完整模型语义）
- ❌ 测试用例只覆盖"正常"fan-out场景，不覆盖in-place链

**迁移验证**：此模式可迁移至：(1)ONNX图变换验证；(2)TVM Relay pass可视化；(3)TensorFlow GraphDef优化pass调试；(4)任意编译器IR变换验证。核心不变量是"分析阶段独立化"和"索引体系忠实移植"。

### 模式2：Protobuf文本格式最小解析器

**触发场景**：需要从.prototxt文件中提取少量字段用于分析/可视化/验证，且不希望引入protobuf Python包依赖。

**核心步骤**：

1. **Tokenizer（约70行）**：
   - 跳过空白和#注释
   - 识别引号字符串（支持`"`和`'`，处理`\`转义）→ `('str', val)`
   - 识别`{`和`}`→ `('{', '{')`/`('}', '}')`
   - 识别带冒号token：`key:value`拆为`('ident', key)` + `('num'|'ident', value)`；`key:`拆为`('ident', key)`
   - 剩余裸词：try float→`('num', val)`，else→`('ident', val)`
2. **Nested-block skipper（约10行）**：`_skip_block_at(tokens, pos)`深度计数`{`/`}`对，跳过嵌套参数块（如`inner_product_param{...}`）
3. **Field extractor（约60行）**：在token流中查找关心的`ident`字段名，提取其后的`str`/`num`值；遇到`layer {`时进入layer子解析

**反模式**：
- ❌ 将裸标识符（如`layer`、`ReLU`、`input_shape`）分类为字符串类型——protobuf text format中，字符串值必须有引号，无引号的词是标识符/枚举/字段名
- ❌ 尝试解析所有嵌套块——最小解析器的核心价值就是跳过不需要的块

**迁移验证**：此模式可迁移至解析任意protobuf text format配置文件（Caffe/ONNX text/TF text/TensorRT text等），只要所需字段≤5个且嵌套参数可跳过。

---

G3质量门检查：
- 模式1触发场景明确，核心步骤4步，反模式4条，迁移验证列举4个可迁移领域 ✅
- 模式2触发场景明确，核心步骤3步（含代码行数参考），反模式2条，迁移验证覆盖所有protobuf text format场景 ✅
- 两个模式均非仅适用于当前InsertSplits场景，具有跨领域迁移性 ✅

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S6 | event=GATE_PASSED | session=sc-20260801-viz-insert-splits | gate=G3 | result=pass
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S7 | event=CONCEPT_COMPLETED | session=sc-20260801-viz-insert-splits | concept=E | patterns=2
```

---

## S4：原子行动项（C阶段）

| # | 行动项 | 验收标准 | 优先级 |
|---|--------|---------|--------|
| A1 | 脚本`scripts/viz_insert_splits.py`已交付至工作目录 | 文件存在，`python -m py_compile`通过，`--verify` 10/10通过 | ✅ 已完成 |
| A2 | 对真实caffe网络prototxt文件进行端到端验证 | 用一个实际网络（如LeNet/AlexNet的train_val.prototxt）运行脚本，确认DAG可视化输出正确 | 待执行（需用户提供prototxt） |
| A3 | 将脚本集成到C++单元测试CI中作为交叉验证参考 | 在CI中运行`--verify`确保C++ InsertSplits修改后Python模拟结果不回归 | 低（可选） |

---

## S5：质量门汇总

| 质量门 | 检查内容 | 结果 |
|--------|---------|------|
| G1 | 事实清单无因果推断词 | ✅ 通过 |
| G2 | 洞察四元组完整（陈述+证据+反常识+行动） | ✅ 通过（3条洞察均完整） |
| G3 | 模式可迁移（触发场景+步骤+反模式+迁移验证） | ✅ 通过（2个模式均满足） |
| G4 | 行动项原子化（单一职责+可验证） | ✅ 通过（A1已完成，A2/A3待执行，各自独立可验证） |

---

## S6：交付物清单

| 文件 | 说明 |
|------|------|
| [viz_insert_splits.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/scripts/viz_insert_splits.py) | InsertSplits DAG可视化主脚本（1047行，零依赖） |
| 本报告 | 里程碑复盘报告（.agents/docs/retrospective/reports/code-optimization/retrospective-caffe-ffi-viz-insert-splits-20260801/） |

---

## 附录：脚本使用速查

```bash
# 验证所有内置测试用例
python scripts/viz_insert_splits.py --verify

# 可视化特定测试用例（含before/after DAG表和fan-out分析）
python scripts/viz_insert_splits.py --case DoubleInplace

# 可视化所有内置用例
python scripts/viz_insert_splits.py --all

# 分析外部prototxt文件
python scripts/viz_insert_splits.py path/to/net.prototxt

# 同时生成Graphviz DOT文件（可用dot -Tpng渲染）
python scripts/viz_insert_splits.py path/to/net.prototxt --dot

# 使用原生Caffe语义（Input层而非外部input）
python scripts/viz_insert_splits.py --mode native --case InputLayerThreeConsumer
```

```
[CMD-LOG] | level=INFO | cmd=seven-concepts | step=S8 | event=CHAIN_COMPLETED | session=sc-20260801-viz-insert-splits | chain=R→I→E→C | gates_passed=4 | insights=3 | patterns=2 | action_items=3 | status=completed
```