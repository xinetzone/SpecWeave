---
id: "conversion-point-debug-tracing"
source: "docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/code-patterns/conversion-point-debug-tracing.toml"
---
> **提炼自**：[insight-extraction.md](../../reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.md) —— MDI项目完成复盘（洞察15）

# 关键转换点DEBUG预埋模式（Conversion Point Debug Tracing）

## 模式类型

代码模式/工程实践模式

## 成熟度

L1 首次提炼（MDI项目Bug#4/#5/#6排查验证，定位时间缩短50%+）

## 适用场景

解析器/编译器/转换器、多阶段数据处理pipeline、ETL流程、复杂业务逻辑处理；当你在开发一个有多个转换阶段、数据在多个环节间流转的系统时。

## 问题背景

复杂数据处理系统的调试痛点：
- 出Bug时不知道数据在哪一步"变坏了"
- 需要临时加print/log语句复现问题
- 复现条件难构造，加了日志可能Bug又不出现了
- 多阶段pipeline中，每个阶段的输入输出不透明，排查需要单步跟踪
- 线上问题无法复现到本地调试环境

常见做法是"Bug出现了再加日志"——这导致需要复现问题，而复现往往是最耗时的环节。

## 核心思想

**在关键转换节点"防御性预埋"结构化DEBUG日志，记录每个阶段的输入/输出/关键中间状态，而非出Bug后临时加日志复现。这能将Bug定位时间缩短50%以上。**

```python
# 反模式：出Bug后才加日志
def parse_parameters(content):
    # Bug: 参数分类错误
    result = do_parse(content)  # 不知道内部发生了什么
    return result

# 正模式：关键节点预埋DEBUG日志
def parse_parameters(content):
    logger.debug(f"[parse_parameters] INPUT content_len={len(content)}, preview={content[:100]}")
    tokens = tokenize(content)
    logger.debug(f"[parse_parameters] AFTER tokenize: {len(tokens)} tokens, types={set(t.type for t in tokens)}")
    classified = classify_by_location(tokens)
    logger.debug(f"[parse_parameters] AFTER classify: path={len(classified.path)}, query={len(classified.query)}, body={len(classified.body)}")
    result = build_params(classified)
    logger.debug(f"[parse_parameters] OUTPUT: {len(result)} params, names={[p.name for p in result]}")
    return result
```

出Bug时，直接查看已有DEBUG输出就能定位是哪个阶段出了问题，无需复现、无需加日志、无需单步调试。

## MDI项目验证

MDI parser.py中，在以下关键转换点预埋了DEBUG日志：
1. **参数分类节点**：记录path/query/body/header参数各有多少个
2. **示例匹配节点**：记录匹配到的example数量、格式类型
3. **响应断言生成节点**：记录生成的断言类型和数量
4. **Directive解析节点**：记录识别到的directive类型和参数

**效果**：Bug#4/#5/#6排查时，直接查看DEBUG输出即可定位根因：
- Bug#4（参数分类错误）：从DEBUG日志发现path参数被错误分类为query
- Bug#5（示例匹配失败）：从DEBUG日志发现代码块语言标识未被识别
- Bug#6（断言生成异常）：从DEBUG日志发现空响应体未正确处理

**量化效果**：每个Bug平均定位时间从预估的20-30分钟缩短至5-10分钟，效率提升60%+。

## 核心规则

### 规则1：识别关键转换节点

不是所有地方都需要加DEBUG日志——只在关键转换点预埋：

| 节点类型 | 应该记录什么 |
|---------|------------|
| **pipeline入口** | 输入大小、格式、关键特征 |
| **阶段转换点** | 阶段名称、输入数量、输出数量、关键分类结果 |
| **分支决策点** | 走了哪个分支、决策依据是什么 |
| **外部调用点** | 调用参数、返回状态、返回数据大小 |
| **pipeline出口** | 输出大小、结构、校验结果 |
| **错误处理路径** | 错误类型、错误上下文、恢复策略 |

### 规则2：结构化DEBUG日志格式

DEBUG日志应该：
- **带明确前缀**：`[function_name/stage_name]` 方便grep过滤
- **记录核心特征而非全部数据**：记录长度、数量、类型、关键字段名，不要把整个对象dump出来（会撑爆日志）
- **包含输入输出对比**：每个阶段记录"进来什么、出去什么"
- **使用DEBUG级别**：不影响正常运行输出，需要时可开启

```python
# Good
logger.debug(f"[classify_params] IN: {len(tokens)} tokens, OUT: path={n_path} query={n_query} body={n_body}")

# Bad - 记录太多数据，日志爆炸
logger.debug(f"[classify_params] tokens={tokens}")

# Bad - 信息不足，看完还是不知道发生了什么
logger.debug("classifying params...")
```

### 规则3：日志不影响业务逻辑

DEBUG日志必须：
- 使用`logger.debug()`而非`print()`
- 不修改任何业务状态
- 即使日志级别关闭也不影响性能（用lazy %格式或f-string但注意在频繁循环中考虑性能）
- 不包含敏感信息（密码、密钥、个人数据）

### 规则4：测试验证日志存在

核心转换点的DEBUG日志应该被测试覆盖吗？不需要直接测试日志输出，但：
- 关键转换点必须有测试覆盖（确保逻辑正确）
- DEBUG日志是辅助调试的，不是功能的一部分
- 如果某个DEBUG日志在排查Bug时发现信息不足，事后补充它

## DEBUG日志速查模板

在多阶段pipeline中，每个阶段函数都应该遵循：

```python
def process_stage_X(input_data):
    # 入口日志
    logger.debug(f"[stage_X] INPUT: type={type(input_data).__name__}, size={len(input_data) if hasattr(input_data, '__len__') else 'N/A'}")
    
    # 阶段处理...
    intermediate = step_a(input_data)
    logger.debug(f"[stage_X] AFTER step_a: {describe(intermediate)}")
    
    result = step_b(intermediate)
    
    # 出口日志
    logger.debug(f"[stage_X] OUTPUT: type={type(result).__name__}, size={len(result) if hasattr(result, '__len__') else 'N/A'}")
    return result
```

## 实施检查清单

- [ ] 是否识别了pipeline中的所有关键转换节点？
- [ ] 每个关键节点入口/出口是否有DEBUG日志？
- [ ] 日志是否记录了核心特征（数量/类型/关键字段）而非完整数据？
- [ ] 日志是否使用标准logger.debug()而非print？
- [ ] 日志前缀是否包含阶段/函数名方便grep？
- [ ] 日志中是否泄露敏感信息？
- [ ] 关键转换点是否有测试覆盖？
- [ ] 最近一个Bug排查时，是否发现某节点日志信息不足需要补充？

## 反例警示

| 错误做法 | 后果 |
|---------|------|
| 所有地方都加DEBUG日志 | 日志爆炸，有用信息淹没在噪音中 |
| 只记录"进入XX函数"不记录数据 | 出Bug时看完日志还是不知道数据状态 |
| 用print()加调试日志 | 忘记删除污染正常输出，且无法控制开关 |
| dump整个大对象到日志 | 日志文件巨大，IO开销大，反而难以阅读 |
| 出Bug才加日志 | 需要复现问题，而复现往往是最耗时的环节 |
| DEBUG日志带副作用（修改状态） | 开DEBUG和关DEBUG行为不一致，产生诡异Bug |

## 与现有模式的关系

- `dual-channel-tiered-logging.md`：双层日志分级模式，本模式聚焦于DEBUG层的内容策略
- `structured-lightweight-logging.md`：结构化轻量日志的格式实践
- `test-first-development.md`：测试先行+预埋DEBUG日志是质量保障的双重防线
- `semi-structured-parsing-complexity-budget.md`：解析器复杂度高，预埋DEBUG日志尤其重要