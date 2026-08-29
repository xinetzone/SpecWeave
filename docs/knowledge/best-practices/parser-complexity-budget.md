---
id: "parser-complexity-budget"
title: "Parser 复杂度预算 Checklist"
x-toml-ref: "../../../../.meta/toml/.agents/docs/knowledge/best-practices/parser-complexity-budget.toml"
category: "best-practices"
tags: ["parser", "复杂度预算", "semi-structured-parsing", "三层架构", "边界case", "TDD", "checklist"]
date: "2026-07-03"
status: "stable"
author: ""
summary: "基于MDI项目parser.py（1465行）重构复盘的经验总结：处理半结构化数据（Markdown/自然语言/配置文件）的Parser应预留2-3倍于Generator的时间/代码量预算，遵循三层架构拆分，并先写20+边界case测试。"
---
# Parser 复杂度预算 Checklist

> 基于MDI项目parser.py（1465行）重构复盘的经验总结：Markdown等半结构化格式的解析复杂度常被系统性低估，本checklist帮助你在Parser开发前做好预算规划，避免"上帝文件"反模式。

## 核心洞察：半结构化解析复杂度被系统性低估

**洞察来源**：MDI项目复盘（洞察7）

IDL工具开发中，Parser常被误判为"简单格式转换"，但Markdown作为半结构化格式，其解析复杂度远高于JSON/YAML等结构化格式——人类编写的Markdown存在大量"看似合理但需特殊处理"的边界场景。

**关键数据**：
- parser.py达1465行，为MDI最大模块（占核心代码16%）
- 3个Parser相关Bug中有2个为section构建与递归终止等基础逻辑错误
- Parser模块Bug密度是Generator模块的3-5倍

---

## Parser 开发前 Checklist

### 🔴 预算阶段（开工前必须确认）

- [ ] **代码量预算**：Parser代码量预留为Generator的2-3倍
  - 反例：初始预估parser≈300行，实际1465行（5倍差距）
  - 建议：JSON/YAML等结构化格式→1.5倍，Markdown/自然语言→2.5-3倍
- [ ] **时间预算**：Parser开发+测试时间预留为Generator的2-3倍
  - 边界case处理占Parser开发时间的60%以上
- [ ] **三层架构设计**：初始即按三层拆分，不做"上帝文件"
  - ✅ `constants.py`：token类型、正则、常量定义
  - ✅ `tokenizer/block_parser.py`：词法分析/块级解析
  - ✅ `directive_parser/semantic.py`：语法分析/语义构建
  - ✅ `parser_facade.py`：对外门面（thin-entry-shim）
- [ ] **薄入口垫片预留**：即使初始单文件实现，也保留未来拆分包的垫片接口

### 🟠 测试先行阶段（写代码前写测试）

- [ ] **先写20+边界case测试**，覆盖以下场景：
  - [ ] 空文档/仅空白字符文档
  - [ ] 仅frontmatter无正文
  - [ ] 标题跳级（H1→H3）
  - [ ] 深层嵌套（H4/H5及以上）
  - [ ] 嵌套代码块（四反引号包裹三反引号）
  - [ ] 管道符转义（表格单元格内`\|`）
  - [ ] 泛型类型参数（`array<string>`、`object`）
  - [ ] 中文/特殊字符frontmatter
  - [ ] Directive空body/无参数/带空格参数名
  - [ ] CLI带flag/可选参数/默认值
  - [ ] 参数描述内含inline code（反引号）
  - [ ] Tab与空格混合缩进
  - [ ] Directive代码块嵌套
  - [ ] 多连续空行
  - [ ] 损坏/格式错误的frontmatter容错
  - [ ] Directive与传统格式混合
  - [ ] 非HTTP方法（CMD/CLI等）
- [ ] **每个关键转换点预埋DEBUG日志**（参考conversion-point-debug-tracing模式）：
  - [ ] Token识别阶段：记录识别到的token类型和位置
  - [ ] Section构建阶段：记录层级关系
  - [ ] Directive解析阶段：记录参数解析结果
  - [ ] 语义模型构建阶段：记录最终输出
- [ ] **真实文档冒烟测试集**：选3-5个真实世界文档做批量解析测试

### 🟡 编码阶段（写代码时遵守）

- [ ] **依赖方向单向**：constants → tokenizer → semantic → facade，无反向依赖
- [ ] **每个文件<300行**：超过即按职责拆分
- [ ] **错误容忍而非崩溃**：遇到格式错误时产生warning并继续解析，不抛异常中断
- [ ] **所有warning收集到doc.warnings**：不打印到stderr，统一收集便于批量验证
- [ ] **递归终止条件显式检查**：嵌套解析必须有深度上限和终止条件
- [ ] **状态机处理复杂语法**：Directive参数等多状态语法用显式状态机而非正则贪心匹配

### 🟢 验收阶段（完成后验证）

- [ ] **所有边界case测试通过**（20+个）
- [ ] **真实文档批量解析无崩溃**（至少5个真实文档）
- [ ] **文件大小门禁通过**：无>800行模块
- [ ] **DEBUG日志可追溯**：出Bug时无需临时加日志，从已有DEBUG输出即可定位
- [ ] **薄入口垫片向后兼容**：外部import路径100%不变
- [ ] **warning而非crash**：所有格式错误产生warning而非抛出异常

---

## 三层架构参考实现（Parser标准拆分模式）

```
mdi/parser_core/
├── __init__.py
├── constants.py          # Token类型、正则表达式、常量（<100行）
├── block_parser.py       # 块级解析：标题/表格/代码块/列表（<300行）
├── directive_parser.py   # Directive语法解析：状态机处理参数（<300行）
└── parser_facade.py      # 对外门面：MDIParser类，组装各层（<200行）

mdi/parser.py             # 薄入口垫片（<30行）——re-export from parser_core
```

**依赖方向**：
```
constants.py → block_parser.py → directive_parser.py → parser_facade.py → parser.py (shim)
```

---

## 关键反模式警示

| 反模式 | 后果 | 规避方案 |
|--------|------|---------|
| 初始追求"完美架构"过度设计 | 进度缓慢，架构不符合实际需求 | 两阶段模式：先跑通MVP，测试兜底后重构 |
| Parser与Generator并行开发 | Parser返工导致Generator连锁修改 | Parser稳定后再开发Generator |
| 正则表达式贪心匹配复杂语法 | 边界case漏处理、回溯性能问题 | 显式状态机+逐字符解析 |
| 格式错误直接抛异常 | 批量解析时单个坏文件导致全部失败 | warning收集+容错继续解析 |
| 无DEBUG日志预埋 | Bug定位需反复复现加日志 | 关键转换点预埋结构化DEBUG |
| 单文件超过800行 | Bug密度非线性上升（3-5倍） | 超过500行即规划拆分 |

---

## 相关模式与参考

- **架构模式**：[three-layer-parser-generator](../../retrospective/patterns/architecture-patterns/three-layer-parser-generator.md)
- **方法论模式**：[semi-structured-parsing-complexity-budget](../../retrospective/patterns/methodology-patterns/tools-automation/semi-structured-parsing-complexity-budget.md)
- **工程模式**：[conversion-point-debug-tracing](../../retrospective/patterns/code-patterns/conversion-point-debug-tracing.md)
- **重构模式**：[thin-entry-shim](../../retrospective/patterns/architecture-patterns/thin-entry-shim.md)、[pattern-driven-refactoring](../../retrospective/patterns/methodology-patterns/tools-automation/pattern-driven-refactoring.md)
- **项目模式**：[two-phase-development](../../retrospective/patterns/methodology-patterns/governance-strategy/two-phase-development.md)
- **MDI实战复盘**：[insight-extraction.md](../../retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.md)（洞察7：半结构化解析复杂度）

---

## Changelog

<!-- changelog -->
- 2026-07-03 | docs | v1.0：初始版本，基于MDI项目parser.py（1465行）复盘提炼，包含预算/测试/编码/验收四阶段checklist
