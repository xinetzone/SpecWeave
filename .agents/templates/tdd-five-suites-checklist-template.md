---
id: "templates-tdd-five-suites-checklist"
title: "TDD测试五件套执行清单（静态分析/检查器开发专用）"
source: "retrospective-concurrent-safety-checker-20260708"
x-toml-ref: "../../.meta/toml/.agents/templates/tdd-five-suites-checklist-template.toml"
version: "1.0.0"
patterns_applied: ["tdd-static-analysis-five-test-suites", "git-hooks-three-tier-trust", "chain-pre-commit-hooks"]
---
# TDD测试五件套执行清单

> **适用场景**：开发任何静态分析工具、代码检查器、lint规则、pre-commit/CI扫描脚本时使用。
>
> **理论依据**：
> - [tdd-static-analysis-five-test-suites.md](../../docs/retrospective/patterns/methodology-patterns/tools-automation/tdd-static-analysis-five-test-suites.md) — TDD五件套方法论
> - [git-hooks-three-tier-trust.md](../../docs/retrospective/patterns/methodology-patterns/tools-automation/git-hooks-three-tier-trust.md) — 三层信任模型（L1/L2/L3部署）
> - [signal-identification-four-step.md](../../docs/retrospective/patterns/methodology-patterns/tools-automation/signal-identification-four-step.md) — 信号识别四步法（规则设计前置）
>
> **使用方式**：开发新检查器时复制本清单，逐项勾选；每完成一个阶段才能进入下一阶段。

---

## 📋 基本信息

| 字段 | 内容 |
|------|------|
| 检查器名称 | |
| 检测规则/维度 | |
| 计划部署层级 | □ L1 pre-commit □ L2 pre-push □ L3 CI |
| 单文件执行时间预算 | |
| 关联模式文档 | |

---

## 🔒 阶段零：前置准备（必须全部完成）

### 0.1 规则定义（信号识别四步法）

- [ ] **规则翻译**：已将人工审查规则转化为可自动检测的信号（关键词/AST结构/数据流模式）
- [ ] **信号强度评估**：评估每个信号的精确率和召回率，标记强信号（≥95%精确率）和弱信号
- [ ] **消歧策略设计**：对弱信号/易混淆场景，设计了AST消歧策略（参见ast-disambiguation-five-methods）
- [ ] **边界接受**：明确接受边界——哪些场景故意不检测（宁可漏报，不可误报）
- [ ] **误报容忍度**：定义了可接受的误报率（L1: 0 HIGH/MEDIUM误报，LOW误报≤5%；L3: 可容忍少量LOW误报）

### 0.2 部署层级决策（三层信任模型）

- [ ] 已用决策树确定部署层级：
  - 单文件执行时间 < 100ms？
  - 只需要暂存文件增量？
  - 需要全量/跨文件分析？
- [ ] L1检查：总耗时控制在5秒以内
- [ ] L3兜底：所有L1检查都有对应的CI全量扫描兜底
- [ ] 若L1总耗时接近5秒瓶颈，预留了L2扩展空间

---

## ✅ 阶段一：阳性测试（Positive Tests）— 验证召回率

> **目标**：有缺陷的代码必须被检测到。每个规则/维度至少1个阳性用例。

### 1.1 编写阳性用例

- [ ] 为每个检测规则/维度编写了"含有该缺陷"的代码片段
- [ ] 每个阳性用例断言了：issues数量正确、dimension/severity正确、行号定位准确
- [ ] 覆盖了规则的所有变体形式（不同写法、不同导入方式、不同参数组合）
- [ ] 包含了注释中明确标记为"应当被检出"的典型坏味道代码

### 1.2 阳性测试清单

| # | 用例描述 | 期望severity | 编写状态 | 通过状态 |
|---|---------|-------------|---------|---------|
| P1 | | | □ | □ |
| P2 | | | □ | □ |
| P3 | | | □ | □ |
| P4 | | | □ | □ |
| P5 | | | □ | □ |

> 💡 提示：阳性用例数量 ≥ 检测规则数 × 1

---

## ⭐ 阶段二：阴性测试（Negative Tests）— 验证精确率（最重要！）

> **目标**：正确的代码不能被误报。阴性测试是静态分析工具的生命线。
> **铁律**：阳性:阴性 ≥ 1:1，阴性数量不得少于阳性。

### 2.1 编写阴性用例

- [ ] 为每个容易混淆的场景编写了"看起来像问题但实际正确"的代码片段
- [ ] 每个阴性用例断言：issues数量为0（或无对应dimension的issue）
- [ ] 覆盖了AST消歧策略验证（方法名同名不同类、参数类型不同、安全模式等）
- [ ] 包含了"修复误报后"的回归用例（每修一个误报立即添加）
- [ ] 包含了豁免场景（`# nosec`/`# noqa`注释、安全白名单模式）

### 2.2 阴性测试清单

| # | 用例描述（为什么不应报） | 对应的消歧策略 | 编写状态 | 通过状态 |
|---|----------------------|--------------|---------|---------|
| N1 | | | □ | □ |
| N2 | | | □ | □ |
| N3 | | | □ | □ |
| N4 | | | □ | □ |
| N5 | | | □ | □ |

> 🚨 **警告**：如果阴性用例数量少于阳性，停止开发——先补阴性测试！
> 💡 提示：刻意寻找"最容易误报"的代码模式（同名方法、相似结构、边界写法）。

---

## 🔲 阶段三：边界测试（Boundary Tests）— 验证规则边界

> **目标**：在规则临界值处行为符合预期，不产生"边界惊喜"。

### 3.1 边界场景覆盖

- [ ] **阈值边界**：timeout=0/None/-1、字符串长度恰好为阈值/超过1个字符、空列表/单元素
- [ ] **位置边界**：代码在注释中/文档字符串中/多行字符串中
- [ ] **导入边界**：别名导入（`import threading as t`）、from导入、延迟导入
- [ ] **参数边界**：关键字参数vs位置参数、默认参数、可变默认参数
- [ ] **嵌套边界**：嵌套函数/类中的同名方法、闭包变量vs全局变量
- [ ] 每个边界场景都做了明确决策（应报/不应报），并固化为测试断言

### 3.2 边界测试清单

| # | 边界场景 | 预期行为（应报/不应报） | 决策理由 | 编写状态 | 通过状态 |
|---|---------|----------------------|---------|---------|---------|
| B1 | | | | □ | □ |
| B2 | | | | □ | □ |
| B3 | | | | □ | □ |
| B4 | | | | □ | □ |

---

## 💻 阶段四：CLI测试（CLI Tests）— 验证接口契约

> **目标**：命令行接口的所有输出格式、退出码、参数都能正常工作，确保能正确集成到链式pre-commit钩子。

### 4.1 CLI功能覆盖

- [ ] **exit code语义**：干净代码→exit 0，有HIGH/MEDIUM issue→exit 1，warn-only模式→exit 0
- [ ] **输出格式**：text人类可读格式、JSON机器可读格式均有测试
- [ ] **JSON结构**：包含files/summary/dimensions等必要字段，可被CI解析
- [ ] **命令行参数**：所有参数（--json/--verbose/--dim/--warn-only/--fix等）均有测试
- [ ] **环境变量**：SKIP/CHECKER_NAME_SKIP绕过机制、WARN_ONLY降级机制有测试
- [ ] **错误处理**：文件不存在/语法错误/权限不足等异常场景的输出和exit code
- [ ] **增量扫描**：只扫描传入的文件列表（而非硬编码全量扫描），适配L1 pre-commit增量模式

### 4.2 CLI测试清单

| # | 测试场景 | 期望exit code | 期望输出 | 编写状态 | 通过状态 |
|---|---------|--------------|---------|---------|---------|
| C1 | 干净文件扫描 | 0 | "PASS"或无issue | □ | □ |
| C2 | 含缺陷文件扫描 | 1 | 报告issue详情 | □ | □ |
| C3 | JSON输出格式 | 0/1 | 可解析为JSON，结构完整 | □ | □ |
| C4 | SKIP环境变量 | 0 | 输出SKIPPED | □ | □ |
| C5 | WARN_ONLY模式 | 0 | 有issue但不阻断 | □ | □ |
| C6 | 指定--dim维度 | 0/1 | 只检查指定维度 | □ | □ |

---

## 🏭 阶段五：集成测试（Integration Tests）— 真实代码验证

> **目标**：防止"温室花朵"问题——在人造fixture上100分，在真实代码上失效。

### 5.1 真实代码验证

- [ ] **干净代码基线**：选取项目中已通过Code Review的真实文件，扫描结果为0 issue
- [ ] **已知缺陷验证**：选取/构造有已知缺陷的真实代码，能正确检出
- [ ] **全量扫描冒烟**：在项目全量代码上运行一次，记录误报/漏报数量
- [ ] **误报回归**：全量扫描中发现的每个误报，都转化为阴性测试用例
- [ ] **性能验证**：L1检查单文件<100ms，全量pre-commit<5s（在典型项目规模下）
- [ ] **钩子集成验证**：集成到链式pre-commit后，commit被正确阻断/放行

### 5.2 集成测试清单

| # | 验证对象 | 期望结果 | 实际结果 | 状态 |
|---|---------|---------|---------|------|
| I1 | 项目自身干净文件（如scanner.py） | 0 issue | | □ |
| I2 | 已知缺陷fixture文件 | 检出对应issue | | □ |
| I3 | 全量扫描（项目所有Python文件） | 0 HIGH/MEDIUM误报 | | □ |
| I4 | L1性能测试（pre-commit全量） | <5秒 | | □ |
| I5 | git commit触发钩子 | 有缺陷阻断/干净通过 | | □ |
| I6 | CI集成（GitHub Actions） | 正确输出报告 | | □ |

---

## 🚀 阶段六：三层部署验证

### 6.1 L1 pre-commit部署验证

- [ ] 已添加到链式钩子入口（[.githooks/pre-commit](../../.githooks/pre-commit) → [pre_commit.py](../../.agents/scripts/hooks/pre_commit.py)）
- [ ] 只扫描暂存区文件增量（`--files`参数传入staged files）
- [ ] 单文件检查耗时<100ms，总耗时<5s
- [ ] HIGH/MEDIUM issue → exit 1 阻断commit
- [ ] LOW issue → 警告但不阻断（warn-only）
- [ ] 支持`SKIP=checker_name git commit`绕过
- [ ] 输出格式与链式钩子解析兼容

### 6.2 L2 pre-push部署验证（预留/按需）

- [ ] 若需要，已配置pre-push钩子
- [ ] 执行时间<30秒
- [ ] 覆盖相关模块的单元测试/增量全量扫描
- [ ] 失败时exit 1阻断push

### 6.3 L3 CI部署验证

- [ ] 已创建GitHub Actions workflow文件
- [ ] 全量扫描所有文件（不限增量）
- [ ] HIGH issue → 阻断merge
- [ ] MEDIUM issue → 警告不阻断
- [ ] 输出SARIF/JSON格式供PR评论展示
- [ ] 缓存依赖确保CI执行时间<10分钟

---

## 🛡️ 阶段七：回归防护网

> **目标**：确保未来修改不会破坏已有检测能力或引入新误报。

- [ ] **总测试数**：____个（阳性__ + 阴性__ + 边界__ + CLI__ + 集成__）
- [ ] **阳阴比例**：阳性:阴性 = ___:___（必须≥1:1）
- [ ] **全量测试通过**：`pytest tests/` 全部绿
- [ ] **误报修复回归**：每个误报修复都有对应的阴性测试
- [ ] **漏报修复回归**：每个漏报修复都有对应的阳性测试
- [ ] **真实代码零回归**：再次全量扫描干净基线文件，仍为0 issue

### 误报/漏报修复记录

| # | 问题类型 | 描述 | 修复方案 | 添加的回归测试 | 修复后状态 |
|---|---------|------|---------|--------------|-----------|
| F1 | □误报 □漏报 | | | | □ |
| F2 | □误报 □漏报 | | | | □ |
| F3 | □误报 □漏报 | | | | □ |

---

## 📊 上线前最终检查清单

### 必过项（L0门禁）

- [ ] 五件套测试全部编写完成，无遗漏
- [ ] 阴性测试数量 ≥ 阳性测试数量
- [ ] 所有测试通过（pytest全绿）
- [ ] 真实代码集成测试通过（干净代码0 issue）
- [ ] L1单文件性能<100ms，pre-commit总耗时<5s
- [ ] exit code语义正确（0=pass, 1=block）
- [ ] 0 HIGH/MEDIUM误报（L1检查必须满足）
- [ ] 已集成到链式pre-commit钩子
- [ ] CI兜底workflow已配置
- [ ] 支持SKIP环境变量绕过

### 质量项（L1应达标）

- [ ] 边界场景覆盖率≥80%
- [ ] CLI所有参数都有测试覆盖
- [ ] 有至少2个集成测试（干净+缺陷）
- [ ] 输出信息清晰，开发者能理解问题并修复
- [ ] 有相关文档说明检查规则和豁免方式

### 优化项（L2锦上添花）

- [ ] 添加了`--fix`自动修复能力
- [ ] 输出包含修复建议链接
- [ ] 测试覆盖率≥80%
- [ ] 添加了性能基准测试

---

## 🔄 TDD红→绿→重构循环记录

每轮循环记录测试状态变化，确保严格遵循TDD流程：

| 轮次 | 红（写测试→失败） | 绿（最小实现→通过） | 重构（优化→仍绿） | 本轮新增测试数 |
|------|-----------------|-------------------|-----------------|-------------|
| 1 | □ | □ | □ | |
| 2 | □ | □ | □ | |
| 3 | □ | □ | □ | |
| 4 | □ | □ | □ | |
| 5 | □ | □ | □ | |

---

## 📝 开发完成总结

| 指标 | 目标值 | 实际值 |
|------|--------|--------|
| 阳性测试数 | ≥规则数 | |
| 阴性测试数 | ≥阳性数 | |
| 阳阴比例 | ≥1:1 | |
| 总测试数 | | |
| L1单文件耗时 | <100ms | |
| pre-commit总耗时 | <5s | |
| HIGH/MEDIUM误报数 | 0 | |
| CI全量扫描耗时 | <10min | |

### 经验记录

- 本次开发中发现的新误报模式：
- 需要补充到消歧策略库的方法：
- 对五件套方法论的改进建议：

---

## 🔗 关联参考

- [tdd-static-analysis-five-test-suites.md](../../docs/retrospective/patterns/methodology-patterns/tools-automation/tdd-static-analysis-five-test-suites.md) — TDD五件套方法论
- [git-hooks-three-tier-trust.md](../../docs/retrospective/patterns/methodology-patterns/tools-automation/git-hooks-three-tier-trust.md) — Git钩子三层信任模型
- [signal-identification-four-step.md](../../docs/retrospective/patterns/methodology-patterns/tools-automation/signal-identification-four-step.md) — 信号识别四步法
- [ast-disambiguation-five-methods.md](../../docs/retrospective/patterns/code-patterns/ast-disambiguation-five-methods.md) — AST五类消歧法
- [chain-pre-commit-hooks.md](../../docs/retrospective/patterns/code-patterns/chain-pre-commit-hooks.md) — 链式pre-commit钩子架构
- [precision-over-recall.md](../../docs/retrospective/patterns/methodology-patterns/tools-automation/precision-over-recall.md) — 精度优先于召回率
- [.githooks/pre-commit](../../.githooks/pre-commit) — Shell钩子入口
- [pre_commit.py](../../.agents/scripts/hooks/pre_commit.py) — Python链式调度器
