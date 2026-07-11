---
id: "adversarial-review-prompt-pattern"
source:
  -   - "external: 不存在-docs/retrospective/reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/insight-extraction.md#洞察2"
  -   - "external: 不存在-docs/knowledge/learning/02-agent-engineering-methodology/vibe-coding-prompts-learning-analysis.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/adversarial-review-prompt-pattern.toml"
maturity: "L2"
validation_count: 2
reuse_count: 0
tags: ["提示词工程", "对抗式审查", "代码审查", "Prompt模式", "Vibe Coding", "多Agent", "攻击者视角", "质量保障", "AI协作"]
related_patterns:
  -   - "first-principles-prompt-pattern"
  -   - "tdd-static-analysis-five-test-suites"
---
> **来源**：从卡兹克"Vibe Coding两大神级Prompt"文章提炼，经[vibe-coding-prompts-learning-analysis复盘](../../../reports/insight-extraction/external-learning/retrospective-vibe-coding-prompts-learning-analysis-20260704/insight-extraction.md#洞察2)系统化验证。文章作者卡兹克实战验证（AIHOT项目40个Agent并发审查，发现OOM死循环、未来时间污染、性能炸弹等关键BUG）。

# 对抗式审查 Prompt 模式（Adversarial Review Prompt Pattern）

## 模式类型
方法论模式（AI协作/提示词工程/质量保障）

## 成熟度
L2 已验证（2次验证来源：卡兹克AIHOT项目40-Agent实战审查 + Vibe Coding Prompt文章系统化分析）

## 适用场景

| 场景 | 适用度 | 说明 |
|------|--------|------|
| 代码审查/BUG狩猎 | ✅✅✅ 核心场景 | 多Agent从攻击者视角找边界BUG |
| 上线前质量门禁 | ✅✅✅ 核心场景 | 保证AI生成代码稳健上线 |
| 安全审计/渗透测试思路 | ✅✅ 强烈推荐 | 模拟恶意用户构造攻击输入 |
| 架构评审 | ✅✅ 推荐 | 从破坏性角度检验架构韧性 |
| 文档审查 | ✅✅ 推荐 | 找逻辑漏洞、事实错误、论证薄弱点 |
| 方案评审 | ✅ 推荐 | 质疑假设、找反例 |
| 简单脚本/一次性代码 | ⚠️ 不必使用 | 投入产出比低 |
| 创意写作/灵感发散 | ❌ 不适用 | 对抗思维会抑制创造力 |

## 问题背景

AI写代码的核心矛盾：
- **第一性原理**能帮AI找到好方案、定位根因，但**无法保证代码稳健上线**
- AI"自审"有根本性盲区——自己写的代码自己审，和人类一样有**确认偏差**（confirmation bias）
- 单Agent审查时，Agent倾向于"证明代码正确"而非"找出代码问题"
- 边界条件、异常输入、极端场景是AI自审最容易遗漏的地方

典型AI自审遗漏的BUG类型：
- OOM死循环：大输入触发内存爆掉→被杀→重试→再爆
- 时间污染：时区错误导致"未来时间"数据污染整条链路
- 性能炸弹：异常输入触发指数级计算
- 缓存穿透：异常数据导致探活机制假阳性
- 安全漏洞：未校验输入导致注入攻击

这些BUG的共同特征：**正常路径走不出来，只有站在"搞破坏"的角度才能发现。**

## 核心规则

### Prompt 标准形式

**Claude Code（Ultracode动态工作流）**：
```
开启 Ultracode(动态工作流,会有 N 个 Agent 进行并发)来对之前开发的功能进行对抗式审查
```

**Codex（多Agent模式）**：
```
开启多 Agent 帮我进行对抗性审查
```

**通用形式**：
```
从恶意用户/攻击者的角度，对以下代码/方案进行对抗式审查，找出所有可能的边界问题、安全漏洞和崩溃路径。
```

### 核心机制：多Agent并发 + 攻击者视角

```mermaid
flowchart TD
    A["代码/方案完成"] --> B["启动多个Agent并发审查"]
    B --> C1["🔴 安全攻击者Agent<br/>构造注入/越权/数据泄露"]
    B --> C2["🟡 性能攻击者Agent<br/>构造大输入/并发/死循环"]
    B --> C3["🟢 边界攻击者Agent<br/>构造空值/极端值/异常格式"]
    B --> C4["🔵 时序攻击者Agent<br/>构造竞态/重试/超时场景"]
    C1 --> D["汇总审查结果"]
    C2 --> D
    C3 --> D
    C4 --> D
    D --> E{"发现问题？"}
    E -->|"是"| F["修复→重新审查"]
    E -->|"否"| G["✅ 通过审查"]
    F --> B
    style B fill:#87CEEB
    style C1 fill:#ffcccc
    style C2 fill:#ffe4b5
    style C3 fill:#ccffcc
    style C4 fill:#e6ccff
    style G fill:#90EE90
```

### 四大攻击者角色定义

| 攻击者角色 | 攻击目标 | 典型攻击手法 | 典型发现 |
|-----------|---------|------------|---------|
| **安全攻击者** | 数据安全、权限控制 | SQL注入、XSS、越权访问、敏感数据泄露 | 未校验输入、权限绕过 |
| **性能攻击者** | 系统稳定性、资源消耗 | 大文件上传、并发请求、递归死循环、正则回溯 | OOM死循环、性能炸弹、DoS漏洞 |
| **边界攻击者** | 输入校验、异常处理 | 空值、超长字符串、特殊字符、未来/过去时间、格式错误 | 未来时间污染、空指针、类型错误 |
| **时序攻击者** | 并发安全、重试机制 | 竞态条件、重复提交、超时重试、部分失败 | 缓存穿透、数据不一致、重试风暴 |

### 对抗式审查 vs 单Agent自审对比

| 维度 | 单Agent自审 | 多Agent对抗式审查 |
|------|-----------|-----------------|
| 审查视角 | "证明代码正确" | "证明代码有问题" |
| 思维模式 | 防御性（检查有没有明显错误） | 进攻性（构造攻击来击穿系统） |
| 边界覆盖 | 常规边界 | 极端+恶意边界 |
| BUG发现率 | 低（确认偏差） | 高（攻击者无偏见） |
| 时间成本 | 低 | 中高（多Agent并发） |
| 适用阶段 | 开发中快速检查 | 上线前/定期全局审查 |

### 与第一性原理的闭环关系

```mermaid
flowchart LR
    FP["🔵 第一性原理<br/>（生成层）"] -->|"找到好方案<br/>定位根因"| DEV["开发实现"]
    DEV --> AR["🔴 对抗式审查<br/>（验证层）"]
    AR -->|"发现问题"| FP
    AR -->|"通过"| SHIP["✅ 稳定上线"]
    FP -->|"做对的事"| VALUE["价值交付"]
    AR -->|"把事做对"| VALUE
    style FP fill:#87CEEB
    style AR fill:#ffcccc
    style SHIP fill:#90EE90
```

- **第一性原理**：保证**做对的事**——方向正确、根因被真正定位
- **对抗式审查**：保证**把事做对**——实现稳健、边界被覆盖、能稳定上线
- 二者构成"生成-验证"完整闭环

## 实施步骤

### 步骤1：选择审查时机
- **功能完成后、上线前**：必须执行对抗式审查
- **定期全局审查**：每2-3周对整个项目做一次"从第一性原理出发的对抗式审查"
- **重大重构后**：重构影响范围大，必须审查
- **新模型上线后**：可用对抗式审查测试新模型能力，同时发现技术债

### 步骤2：定义审查范围
- 明确审查目标（特定功能/模块/整个项目）
- 明确审查维度（安全/性能/边界/时序，或全部）
- 提供代码上下文（仓库路径、相关文件、架构说明）

### 步骤3：启动多Agent对抗审查
- Claude Code：使用"开启Ultracode...进行对抗式审查"
- Codex：使用"开启多Agent帮我进行对抗性审查"
- 通用场景：明确要求Agent从攻击者视角构造异常输入

### 步骤4：收集并分类问题
- 按严重程度分类（P0崩溃/P1严重/P2一般/P3建议）
- 按问题类型分类（安全/性能/边界/时序）
- 每个问题附带：攻击路径、复现条件、影响范围

### 步骤5：修复并回归
- 修复发现的问题
- 对修复后的代码重新执行对抗式审查（回归验证）
- 直到所有P0/P1问题修复，P2问题评估后决定是否阻塞上线

### 步骤6：定期全局审查实践
- 周期：每2-3周
- 方式：让Agent从最底层原理出发，并发审查架构、依赖关系、代码质量、文档对应
- 附加价值：同时测试新模型能力，每次都能挑出之前没注意到的技术债和潜在风险

## 验证案例

### 案例1：AIHOT项目对抗式审查（40个Agent并发）
- **工具**：Claude Code Ultracode动态工作流
- **规模**：近40个Agent并发审查，跑了很久
- **发现的关键BUG**：
  1. **OOM死循环**：后台worker处理大任务时内存爆掉→被杀→自动重试→又爆→无限循环。对抗路径：恶意用户提交50MB HTML搞崩worker→从入口到崩溃全链路审查。后来真的看到过100MB的HTML
  2. **未来时间污染BUG**：某信源文章发布时间因时区错误显示为未来时间，排到精选信息流最前面，污染推送→RSS→日报整条链路。自审完全想不到，但攻击者视角会问"如果发布时间是未来怎么办？"
  3. **HTML清洗模块性能炸弹**：异常HTML触发性能问题
  4. **翻译模块同类隐患**：与HTML清洗类似的边界隐患
  5. **部署探活缓存穿透假阳性**：探活机制被异常数据干扰
- **效果**：作者称"自从用了对抗式审查，对自己代码和项目的信心变得很强"

### 案例2：全局定期审查（第一性原理+对抗式审查组合）
- **周期**：每2-3周
- **方式**："从第一性原理出发的对抗式审查"
- **覆盖**：架构、依赖关系、代码质量、文档对应
- **附加价值**：测试新模型能力 + 发现技术债 + 发现潜在风险
- **验证**：每次都能挑出之前没注意到的问题

## 在本项目（SpecWeave）中的应用场景

| 应用场景 | 具体用法 |
|---------|---------|
| 检查脚本审查 | 写完`.agents/scripts/`下的检查脚本后，从"绕过检查"角度对抗式审查 |
| 模式文件验证 | 新模式入库前，从"误用/滥用/边界情况"角度审查 |
| 规范制定审查 | 新规范制定后，从"恶意合规"（表面符合但实质违反）角度审查 |
| CI流水线安全 | 审查CI脚本是否有注入、权限泄露等安全问题 |
| 文档断链检测 | 从"各种断链场景"角度审查链接检查工具的覆盖率 |
| 定期全局审视 | 每2-3周对整个.agents/体系做一次对抗式审查 |

## 反模式

| 反模式 | 为什么错误 | 正确做法 |
|--------|----------|---------|
| 只用单Agent做"对抗式审查" | 单Agent无法真正并发多角度攻击，容易遗漏 | 必须多Agent并发，每个Agent扮演不同攻击者角色 |
| 对抗式审查替代第一性原理 | 对抗式审查找问题但不保证方向对，可能"正确地做错事" | 第一性原理+对抗式审查形成闭环 |
| 审查后不做回归验证 | 修复可能引入新问题 | 修复后必须重新执行对抗式审查 |
| 只在上线前做审查 | 问题发现越晚修复成本越高 | 开发过程中就做小范围对抗审查，上线前做全面审查 |
| 对抗审查只看代码不看架构 | 架构级问题比代码级问题影响更大 | 定期全局审查必须覆盖架构层面 |

## 与其他模式的关系

| 关联模式 | 关系类型 | 关系说明 |
|---------|---------|---------|
| [first-principles-prompt-pattern.md](first-principles-prompt-pattern.md) | 互补闭环 | 第一性原理管"生成好方案"，对抗式审查管"验证方案稳健"，二者构成"生成-验证"闭环 |
| [tdd-static-analysis-five-test-suites.md](../tools-automation/tdd-static-analysis-five-test-suites.md) | 互补 | TDD五套测试是自动化验证，对抗式审查是AI驱动的智能验证，二者互补 |
| [dual-quality-gate-subagent.md](../governance-strategy/dual-quality-gate-subagent.md) | 思想同源 | 双质量门禁与对抗式审查共享"多重验证"的质量保障理念 |
| [triangular-source-verification.md](../retrospective-knowledge/triangular-source-verification.md) | 思想同源 | 三源验证和多Agent对抗审查都强调"多角度交叉验证" |
| [multi-agent-parallel-execution.md](../../architecture-patterns/multi-agent-parallel-execution.md) | 实现基础 | 多Agent并行执行是对抗式审查的技术基础 |

## Changelog

- 2026-07-08 | create | 初始版本，基于卡兹克文章和vibe-coding-prompts-learning-analysis复盘提炼，L2成熟度
