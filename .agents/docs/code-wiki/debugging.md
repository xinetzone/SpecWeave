# 调试指南

本文档记录共享工具库模块的日志配置、异常排查方法和常见问题诊断流程。

---

## 多智能体冲突解决模块（ConflictResolver）

### 日志配置

`ConflictResolver` 支持通过构造函数注入自定义日志函数，便于与上层系统的日志框架集成。

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("conflict_resolver")

def log_fn(msg: str) -> None:
    """将ConflictResolver日志桥接到标准logging"""
    if msg.startswith("[WARNING]"):
        logger.warning(msg)
    else:
        logger.info(msg)

resolver = ConflictResolver(logger=log_fn)
```

**默认行为**：不传入 `logger` 参数时，日志消息被丢弃（静默模式），适合生产环境不产生额外输出。

### 日志消息格式

所有日志消息遵循统一格式：`[动作/级别] [task_id]: 详细描述`。

| 消息前缀 | 级别 | 含义 |
|---|---|---|
| `冲突报告` | INFO | 收到冲突报告，开始处理 |
| `开始仲裁` | INFO | 启动仲裁流程 |
| `能力匹配` | INFO | 能力筛选阶段，列出匹配候选 |
| `仲裁` | INFO | 唯一匹配候选直接分配 |
| `负载校验` | INFO | 负载校验阶段，列出有效候选及负载分布 |
| `[WARNING] 负载校验` | WARNING | 存在负载异常的agent被过滤，列出异常原因 |
| `负载均衡` | INFO | 多候选按最低负载分配，列出并列情况 |
| `历史归属` | INFO | 按模块历史归属原则分配 |
| `全局负载均衡` | INFO | 进入无能力约束的全局负载均衡路径 |
| `默认分配` | INFO | agents不足时默认分配给发起方 |
| `升级` | INFO/ WARNING | 触发升级机制 |
| `[WARNING] 升级` | WARNING | 全异常负载等严重异常导致的升级 |
| `仲裁结果` | INFO | 最终仲裁结论 |

### 决策分支日志链路

一次完整的职责冲突仲裁，日志输出链路如下：

```
冲突报告 [TASK-ID]: 描述 (类型: responsibility)
开始仲裁 [TASK-ID]: 启动仲裁流程
能力匹配 [TASK-ID]: 需'xxx'能力, 总agents=N, 匹配候选=[...]
负载校验 [TASK-ID]: 有效候选M个, 负载分布: {...}
负载均衡 [TASK-ID]: 最低负载=X, winner=agent_id(并列K个), 按能力+负载均衡分配
仲裁结果 [TASK-ID]: status=resolved, winner=agent_id, reason=按能力匹配+负载均衡原则
```

### 负载值校验诊断

负载校验是冲突解决模块最核心的防御逻辑。新增了 `_diagnose_load` 和 `_log_load_validation` 两个辅助方法。

#### 负载异常类型与诊断信息

| 异常类型 | 诊断信息示例 | 处理方式 |
|---|---|---|
| 负载缺失 | `缺失(None)` | agent字典中无`load`键或值为None |
| 类型异常（非数值） | `类型异常(str='high')` | load为字符串等非int/float类型 |
| 类型异常（布尔值） | `类型异常(bool=True)` | load为True/False（bool是int子类，需额外排除） |
| 非数值(NaN) | `非数值(NaN)` | load为float('nan')（通过isinstance检查但0<=NaN<=100为False） |
| 负值 | `负值(-50)` | load小于0 |
| 超范围 | `超范围(150>100)` | load大于100 |

#### 负载校验日志示例

**部分异常（过滤后继续）**：

```
[WARNING] 负载校验 [TASK-001]: 过滤2个负载异常agent: bad_agent[负值(-50)], over_agent[超范围(150>100)]
负载校验 [TASK-001]: 有效候选3个, 负载分布: {'good_agent': 50, 'low_agent': 10, 'mid_agent': 40}
```

**全异常（触发升级）**：

```
[WARNING] 负载校验 [TASK-002]: 过滤3个负载异常agent: b1[负值(-10)], b2[超范围(200>100)], b3[缺失(None)]
[WARNING] 升级 [TASK-002]: 所有3个候选agent负载值均异常: b1[负值(-10)], b2[超范围(200>100)], b3[缺失(None)]
仲裁结果 [TASK-002]: status=escalated, winner=None, reason=无有效负载数据的候选agent
```

### 常见问题排查

#### 问题1：预期应该RESOLVED但返回了ESCALATED

**排查步骤**：

1. 检查日志中是否有 `无agent具备所需能力` —— 说明所有agent的`capabilities`列表中都不包含`required_capability`指定的值
2. 检查日志中是否有 `所有N个候选agent负载值均异常` —— 说明所有匹配agent的load值都不在[0,100]有效范围内
3. 检查日志中是否有 `双方均拒绝` —— 说明`rejected_by`列表中已有双方ID，触发了拒绝升级

**解决方案**：

- 能力问题：确认agent的`capabilities`字段拼写和大小写是否与`required_capability`完全匹配
- 负载问题：检查数据源是否正确生成了int/float类型的load值，范围应在0-100之间
- 拒绝问题：检查是否重复调用`add_rejection()`导致双方都拒绝

#### 问题2：负载最低的agent没有被选中

**排查步骤**：

1. 查看日志中的 `能力匹配` 行，确认该agent是否在匹配候选列表中
2. 查看 `负载校验` 日志中的 `有效候选` 和 `负载分布`，确认该agent是否被过滤
3. 若该agent负载异常，查看 `[WARNING] 负载校验` 行中的具体异常原因

**常见原因**：

- agent的`capabilities`不包含所需能力（被能力过滤排除）
- agent的load值为负值或超100（被负载校验过滤）
- agent的load为布尔值`True`/`False`（在Python中`True==1`，`False==0`，会导致误判，已修复）

#### 问题3：多agent相同最低负载时winner不确定

**排查步骤**：

查看 `负载均衡` 日志中的并列信息：

```
负载均衡 [TASK-003]: 最低负载=30, winner=a1(并列2个, 全部并列: ['a1', 'a2']), 按能力+负载均衡分配
```

**说明**：多个agent负载相同时，Python `min()` 函数返回第一个遇到的最低值元素，winner取决于字典迭代顺序。这在Python 3.7+中是插入顺序确定的，但多进程/分布式环境下不应依赖此行为。如需确定性平局打破，应在调用方增加优先级或历史归属信息。

#### 问题4：技术冲突/资源冲突没有详细日志

技术冲突（`_resolve_technical`）和资源冲突（`_resolve_resource`）目前的日志覆盖度低于职责冲突。如果需要排查这两类冲突的详细决策过程，可以：

1. 在调用`resolve()`前通过`logger`参数注入日志收集器
2. 在`resolve()`入口已有`冲突报告`和`仲裁结果`两条日志，可确认输入输出
3. 如需更细粒度日志，可在对应方法中补充`_log()`调用

### 快速调试脚本

使用以下代码快速验证冲突解决模块的日志输出：

```python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.agents/scripts'))

from lib.collaboration.conflict_resolution import (
    ConflictResolver, ConflictReport, ConflictType, ResolutionStatus
)

def debug_logger(msg):
    print(f"[DEBUG] {msg}")

resolver = ConflictResolver(logger=debug_logger)

agents = {
    "dev1": {"role": "developer", "priority": 2, "load": 30, "capabilities": ["coding"]},
    "dev2": {"role": "developer", "priority": 2, "load": 60, "capabilities": ["coding"]},
}

report = ConflictReport(
    reporter_id="dev1", opponent_id="dev2",
    conflict_type=ConflictType.RESPONSIBILITY,
    description="调试测试", task_id="DEBUG-001",
    required_capability="coding",
)

result = resolver.resolve(report, agents=agents)
print(f"结果: {result.status.value}, winner={result.winner}, reason={result.reason}")
```

也可直接运行演示脚本查看完整日志效果：

```powershell
python .agents/scripts/tests/demo_enhanced_logging.py
```

### 关键修复记录

| 修复日期 | 问题 | 修复方式 | 影响日志 |
|---|---|---|---|
| 2026-07-09 | 无能力匹配agent时错误返回RESOLVED | 无匹配候选时返回ESCALATED | `升级 [task_id]: 无agent具备所需能力` |
| 2026-07-09 | 负载值超出[0,100]范围导致错误比较 | 比较前过滤无效负载，全异常升级 | `[WARNING] 负载校验` / `[WARNING] 升级` |
| 2026-07-09 | bool类型load（True=1/False=0）被误判为有效 | 添加`isinstance(load, bool)`排除 | `类型异常(bool=True/False)` |
| 2026-07-09 | 异常负载无日志难以排查 | 新增`_diagnose_load`和`_log_load_validation` | 全决策分支结构化日志 |
| 2026-07-09 | NaN负载值（float('nan')）通过isinstance检查但诊断为空 | 添加`load != load`检测NaN | `非数值(NaN)` |

### 压力测试

针对生产环境边界情况的压力测试套件位于 [test_conflict_resolution_stress.py](../../scripts/tests/test_conflict_resolution_stress.py)，覆盖以下9类场景：

| 测试类 | 场景 | 关键验证点 |
|---|---|---|
| TestStressLargeScaleAnomaly | 大规模异常污染 | 100-1000个agent池、5%-70%异常率，不崩溃、winner正确、5秒内完成 |
| TestStressAnomalyRateGradient | 异常率梯度测试 | 0%-100%异常率，winner始终为正常agent中负载最低者 |
| TestStressConcurrency | 并发调用测试 | 20线程并发无竞态，结果一致性验证 |
| TestStressRepeatedCalls | 连续调用稳定性 | 1000次重复调用无状态污染，日志收集器无泄漏 |
| TestStressBoundaryValues | 边界值攻击测试 | NaN/Inf/complex/bytes/complex等13种极端值过滤，0/100边界值正确接受 |
| TestStressMixedConflictTypes | 混合冲突类型 | 资源/技术冲突在异常数据下不崩溃 |
| TestStressLogFlood | 日志洪泛测试 | 1000个全异常agent不崩溃，None日志收集器正常工作 |
| TestStressDeterminism | 确定性验证 | 相同异常模式多次调用结果一致 |
| TestStressDefensiveCopy | 深度防御校验 | 1000次调用后输入agents不被修改，report对象不被篡改 |
| TestStressDiagnosticCompleteness | 诊断完整性 | 6种异常类型诊断消息精确匹配 |

运行方式：

```powershell
python -m pytest .agents/scripts/tests/test_conflict_resolution_stress.py -v
```