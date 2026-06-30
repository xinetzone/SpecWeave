+++
id = "structured-lightweight-logging"
domain = "code"
layer = "code"
maturity = "L2"
validation_count = 1
reuse_count = 0
documentation_level = "basic"
source = "docs/retrospective/reports/project-governance/process-and-compliance/retrospective-stage-guardrails-logging-20260629/insight-extraction.md"

[bindings]
rules = [".agents/rules/stage-guardrails.md"]
references = [".agents/protocols/pre-document-reading.md", ".agents/scripts/check-stage-guardrails.py"]
skills = []
+++

# 结构化轻量日志格式

## 模式概述

AI Agent执行过程中的可观测性最小实现方案。使用统一前缀+键值对+JSON上下文的单行格式，既便于人类阅读，又便于机器解析，无需引入重量级日志基础设施。

## 格式规范

```
[PREFIX-LOG] | level=<LEVEL> | event=<EVENT> | stage=<STAGE> | role=<ROLE> | session=<SESSION_ID> | msg=<MESSAGE> | ctx=<COMPRESSED_JSON>
```

### 字段设计原则

| 字段 | 必填 | 设计理由 |
|------|-----|---------|
| `[PREFIX-LOG]` | ✅ | 前缀标识日志类型（如SG-LOG/PDR-LOG），grep时一行命令即可过滤 |
| `level` | ✅ | DEBUG/INFO/WARN/ERROR四级，控制输出详略和告警阈值 |
| `event` | ✅ | 事件类型枚举，是日志分析脚本的主要匹配依据 |
| `stage` | ✅ | 关联到开发阶段/流程节点，支持按阶段聚合分析 |
| `role` | ✅ | 记录执行角色，多角色协作时定位问题来源 |
| `session` | ✅ | 会话标识，跨会话日志分析时隔离不同任务 |
| `msg` | ✅ | 中文人类可读消息，不依赖工具即可理解 |
| `ctx` | ❌ | 压缩JSON上下文（单行无换行），存结构化数据供机器解析 |

### 分隔符选择

使用`|`作为字段分隔符而非空格或逗号，原因：
- `|`在自然语言文本中出现频率极低，不易产生歧义
- `|`视觉上清晰分隔各字段
- 正则匹配简单：`([^|]+?)\s*` 即可提取字段值

## 事件枚举设计

每种日志类型（前缀）对应一个封闭的事件枚举集合，如：

- SG-LOG（阶段守卫）：STAGE_ENTER, DOC_CHECK, DOC_READ, BOUNDARY_PASS, INTERCEPT, JUMP_REQUEST, JUMP_APPROVED, STAGE_EXIT, ERROR...
- PDR-LOG（前置文档读取）：PDR_START, PDR_DOC_READ, PDR_DOC_MISSING, PDR_CONFIRM, PDR_ERROR...

事件命名采用`NOUN_VERB`大写下划线风格，语义清晰，grep友好。

## 解析实现

一条正则即可解析：

```python
LOG_LINE_RE = re.compile(
    r'\[(SG-LOG|PDR-LOG)\]\s*\|\s*'
    r'level=(\w+)\s*\|\s*'
    r'event=(\w+)\s*\|\s*'
    r'stage=(\w+)\s*\|\s*'
    r'role=(\w+)\s*\|\s*'
    r'session=([^|]+?)\s*\|\s*'
    r'msg=([^|]+?)(?:\s*\|\s*ctx=(.+))?$'
)
```

ctx字段用`json.loads()`解析，失败时降级为raw存储。

## 与重量级方案的对比

| 维度 | 结构化轻量日志 | 企业级方案（OTEL/ELK） |
|------|--------------|---------------------|
| 部署成本 | 零（正则+JSON即可） | 高（需部署Collector/Storage/UI） |
| 实时性 | 事后离线分析 | 实时告警 |
| 分布式追踪 | 不支持 | 支持 |
| 指标聚合 | 手动脚本统计 | 自动聚合+仪表盘 |
| 适用规模 | 单项目/单团队 | 多服务/多团队 |
| 学习成本 | 5分钟理解格式 | 需要学习整套API |

## 日志级别使用约定

| 级别 | 标识 | 使用场景 | 是否入交接文档 |
|------|------|---------|-------------|
| DEBUG | 🔍 | 细粒度调试（边界校验详情、条件判断分支） | 否 |
| INFO | ℹ️ | 正常流程节点（进入/退出/读取完成/审批通过） | 否 |
| WARN | ⚠️ | 异常但可恢复（拦截、文档缺失标注风险、审批拒绝） | **是** |
| ERROR | ❌ | 严重错误（未审批跳转、高风险缺失继续执行、绕过检测） | **是** |

## 输出要求

1. **即时输出**：事件发生时立即输出，不得延迟到阶段结束批量输出
2. **单行输出**：每条日志必须在一行内，ctx JSON压缩为单行
3. **中文消息**：msg字段使用中文，ctx键名使用英文
4. **不替代交互**：日志是辅助排查工具，不替代面向用户的正式输出

## 实施检查清单
- [ ] 定义日志前缀（如[XXX-LOG]）
- [ ] 定义事件类型枚举（封闭集合）
- [ ] 定义必填字段和可选ctx字段
- [ ] 每个事件类型提供模板+真实示例
- [ ] 编写解析正则（可参考check-stage-guardrails.py）
- [ ] 提供--demo模式的自检样例（包含正常+异常场景）

> 来源：来自 retrospective-stage-guardrails-logging-20260629 洞察3
> 关联模式：[three-layer-rule-enforcement.md](../methodology-patterns/governance-strategy/three-layer-rule-enforcement.md)
