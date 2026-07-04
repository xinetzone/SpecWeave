---
id: "harness-engineering-wiki-03"
title: "六大工程模式"
source: "https://mp.weixin.qq.com/s/0w_xMwto4sLx6J_85OhWQw?from=industrynews&color_scheme=light#rd"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/harness-engineering-wiki/03-six-patterns.toml"
date: "2026-07-04"
category: "learning"
---

# 六大工程模式

## 模式索引表

| 编号 | 模式名 | 解决的核心问题 |
|------|--------|---------------|
| 1 | 双阶段架构（Init+Exec） | 长任务Context膨胀、跨会话失忆 |
| 2 | 工具签名即文档 | 工具选错、参数误用 |
| 3 | Sub-Agent隔离 | 通才Agent"逛超市"、工具间干扰 |
| 4 | 上下游反压 | 错误累积、无效工作不被拦截 |
| 5 | 智能体审智能体 | 自我评估偏见、同Context复现错误 |
| 6 | 熵管理与文档园丁 | 系统腐化、文档过期、技术债累积 |

---

## 模式1：双阶段架构（Initializer + Executor）

### 核心思想
将任务执行拆分为两个独立阶段，不共享Context，只通过Workspace文件接力。这是Anthropic Claude Code的核心实践。

### 工作流程
1. **Initializer（初始化器）**：
   - 接收用户任务，充分理解需求
   - 写出详细的plan.md到Workspace
   - 任务目标、分步执行计划、验收标准、文件约定
   - **写完即退出，不执行任何实际操作**
2. **Executor（执行器）**：
   - 新的Context，只读取plan.md
   - 按计划逐步执行
   - 执行过程中更新Workspace状态
   - 遇到问题时可以参考plan，但不共享Init阶段的思考过程

### 为什么有效
- Context不膨胀：Init阶段的思考过程不污染Exec阶段
- 可回放：plan.md是决策记录，任何时候都能回看当初为什么这么规划
- 跨Context接力：会话中断后，新的Executor读取plan.md就能继续
- 职责分离：规划和执行分离，减少执行中的决策干扰

---

## 模式2：工具签名即文档

### 核心思想
工具本身的签名就是最好的文档，不需要额外写"如何使用工具"的文档。LangChain实测此模式显著提升工具调用准确率。

### 实践要点
1. **命名**：工具名使用**动词短语**，清晰表达"做什么"
   - ✅ 好：`parse_resume`、`score_match`、`book_meeting_room`
   - ❌ 差：`resume`、`match`、`room`
2. **参数Schema**：每个字段的description必须说清：
   - 这个参数是做什么的
   - **什么时候用**
   - **什么时候不用**
   - 取值范围/格式要求
3. **返回值**：结构稳定，有明确的schema，不要返回自由格式文本

### 示例对比
差的签名：
```python
def match(resume, jd, threshold):
    """匹配简历和JD"""
```

好的签名：
```python
def score_candidate_fit(
    resume_text: str,
    jd_text: str,
    minimum_score: float = Field(
        description="最低通过分数，0-100。初筛用60，终面推荐用80，人才库入库用50"
    )
) -> MatchResult:
    """
    计算候选人与JD的匹配度。
    仅用于简历筛选阶段，不要用于offer谈判阶段的薪资评估。
    """
```

---

## 模式3：Sub-Agent隔离

### 核心思想
每个Sub-Agent有独立的Context Window，只看到自己需要的工具，主Agent只接收结构化输出。

### 隔离维度
1. **Context隔离**：每个Sub-Agent启动时是全新的Context，不加载其他Agent的对话历史
2. **工具隔离**：人岗匹配Agent只看到4个工具，招聘沟通Agent只看到5个工具，互相看不到对方的工具
3. **Prompt隔离**：每个Agent有自己专属的精简Prompt（80-90行），不是600行的大一统Prompt
4. **输出隔离**：Sub-Agent只返回结构化结果（如JSON），不返回自由对话，主Agent不需要过滤废话

### 为什么有效
- 决策空间小：每个Agent只需要在3-5个工具中选择，选错率大幅下降
- 关注点集中：Prompt精简，模型不会读到无关指令
- 可复用：专才Agent可以在多个场景复用（如人岗匹配Agent可同时用于校招和社招）
- 易调试：哪个Agent出问题就查哪个，不用在大一统Context里大海捞针

---

## 模式4：上下游反压

### 核心思想
上游给出确定性设置和一致上下文，下游通过测试/Lint/CI拒绝无效工作，错误信号回传上游修正。这类似软件工程中的"防御性编程"和"快速失败"。

### 反压链路
```
上游（Orchestrator/规划层）
  ↓ 给出：确定性任务设置 + 完整一致上下文
执行层（Executor/工具调用）
  ↓ 产出：代码/操作结果
下游（Linter/Test/CI）
  ↓ 检查：规则校验、测试运行、格式检查
  ↓ 不通过→错误信号回传（包含：为什么错+正确做法）
上游修正 → 重新执行 → 再次检查
```

### Linter错误信息是上下文工程
Linter输出不仅要告诉Agent"错了"，还要：
1. **解释为什么**：这个规则存在的原因，违反会导致什么问题
2. **给出正确做法**：具体应该怎么改，示例代码
3. **指向相关文档**：如果有更详细的规范，给出参考链接

反例：`SyntaxError: invalid syntax`（没用，Agent不知道怎么改）
正例：`错误：函数名必须使用snake_case（你用了camelCase: parseResume）。原因：项目规范要求所有Python函数使用snake_case，见docs/development-standards.md第3节。正确写法：parse_resume`

---

## 模式5：智能体审智能体

### 核心思想
换一个全新的Context做Review，Reviewer只看git diff+规则文档，设定为"怀疑态度的Senior Reviewer"。同样的Context再评估只会复现同一个偏见。

### 为什么需要换Context
- **确认偏误**：如果Agent在同一个Context里自己审自己，会倾向于认为自己之前的决定是对的
- **锚定效应**：之前的思考过程会锚定判断，难以发现问题
- **视角盲区**："只缘身在此山中"，跳出来才能看到全局

### Reviewer配置
- **人设**：经验丰富、态度严谨、略带怀疑的Senior工程师
- **输入**：
  - 只给git diff（不要给整个代码base）
  - 只给相关的规则文档（不要给全部文档）
  - 明确告诉Reviewer："你的任务是找出问题，不是夸奖"
- **输出**：结构化的审查意见，按严重程度分级（blocker/major/minor/nit）

---

## 模式6：熵管理与文档园丁

### 核心思想
后台Agent定期扫描过期文档、检测架构漂移、提交清理PR。持续小额还债，不要等技术债爆雷。垃圾回收做成定时任务。

### 园丁要做什么
1. **文档扫描**：
   - 检测死链
   - 发现超过N天没更新的文档，提醒负责人
   - 识别文档与代码不一致的地方
2. **架构漂移检测**：
   - 代码是否违反了AGENTS.md中的规则
   - 是否有重复代码（DRY检查）
   - 依赖是否有未使用的
3. **垃圾回收**：
   - 清理超过保留期的临时文件
   - 归档已完成的spec记录
   - 压缩过时的日志
4. **小额持续还债**：
   - 每次只改一点点，不搞"大重构"
   - 做成定时任务（如每天凌晨跑一次）
   - 自动提交PR，让人review后合并
