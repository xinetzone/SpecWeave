+++
id = "root-cause-diagnosis"
domain = "methodology"
layer = "methodology"
maturity = "L1"
validation_count = 1
reuse_count = 0
documentation_level = "basic"
source = "docs/retrospective/reports/project-governance/retrospective-session-agents-md-violation-20260624/insight-extraction.md#洞察2"

[bindings]
rules = ["docs/AGENTS.md"]
references = ["docs/retrospective/patterns/methodology-patterns/review-insight-export-loop.md"]
skills = []
+++

> **来源**：从 `retrospective-session-agents-md-violation-20260624` 洞察 2「表层修正循环」萃取

# 根因诊断模式

## 一、来源

本轮会话中，智能体在生成产出物时连续触发了三重错误（格式/路径/结构），用户每轮指出一个问题，智能体每轮只修正被指出的那一个。经过 3 轮表层修正后，用户直接要求「按 AGENTS.md 来」，智能体才读取 AGENTS.md——此时一次读取 + 一次全量重写就修复了所有问题。

这个模式揭示了 AI 智能体的一个默认行为倾向：**纠错反馈是症状信号，但智能体的默认响应是「修症状」而非「诊根因」**。

## 二、核心思想

当收到用户纠错反馈时，智能体不应立即修正被指出的具体问题，而应首先执行「根因诊断」——追溯「为什么我犯了这些错误？我缺少了什么知识？我应该先读什么文件？」。只有在确认知识完整后，才执行修正操作。

```
用户纠错 → 暂停修正 → 根因诊断 → 读取缺失文档 → 全量修正 → 验证
```

与默认的「修症状」模式对比：

```
用户纠错 → 立即修正当前症状 → 用户再纠错 → 再修正 → ...（循环）
              ↑ 质量差                         |
              └─────────────────────────────────┘
```

## 三、操作步骤

```mermaid
flowchart TD
    A["收到用户纠错反馈"] --> B["暂停：不立即修改文件"]
    B --> C["诊断 1：我犯了什么类型的错误？<br/>格式 / 路径 / 结构 / 内容 / 逻辑"]
    C --> D["诊断 2：这些错误的共同特征是什么？<br/>是否指向同一个知识缺口？"]
    D --> E{"诊断 3：我缺少了什么文档？<br/>AGENTS.md / 模板 / 范例 / 规范"}
    E --> F["读取缺失文档"]
    F --> G["评估：当前产出物有多少比例需要重做？"]
    G --> H{"是否需要全量重写？"}
    H -->|"是（>50%）"| I["全量重写"]
    H -->|"否（<50%）"| J["增量修正"]
    I --> K["验证：新产出物是否符合所有规范？"]
    J --> K
```

## 四、诊断检查清单

收到纠错反馈后，依次检查以下问题：

| # | 检查项 | 如果答案为「是」 |
|---|--------|----------------|
| 1 | 我是否在本次会话开始时读取了 AGENTS.md？ | 否 → 立即读取 |
| 2 | 我输出的文件格式是否与项目规范（如 Marp/Markdown/特定模板）一致？ | 否 → 查阅对应模板 |
| 3 | 我输出的文件路径是否遵循项目目录约定？ | 否 → 查阅目录命名规范 |
| 4 | 我的文档结构是否遵循项目的原子化/模块化模板？ | 否 → 查阅现有范例 |
| 5 | 我的文件命名是否使用了 kebab-case 等约定格式？ | 否 → 查阅命名规范 |
| 6 | 是否存在多个 Skill 被同时加载且语义重叠的情况？ | 是 → 确认只有正确的 Skill 生效 |

## 五、使用原则

1. **纠错触发即诊断**：任何用户纠错反馈都应触发诊断步骤，即使反馈只涉及一个症状
2. **诊断先于修正**：在完成检查清单之前，不执行任何文件修改操作
3. **全量优于增量**：若诊断发现多个输出维度偏离规范，优先全量重写而非逐个修补
4. **诊断结果需透明**：在修正完成后，向用户说明诊断的根因和修正策略

## 六、验证标准

根因诊断模式有效的标志是：单次纠错后，**残留错误数为 0**。如果用户连续纠错 2 次以上，说明根因诊断未被触发或诊断不充分。

| 轮次 | 修正动作 | 触及根因？ | 残留错误数 |
|------|---------|-----------|-----------|
| 第 3 轮 | 修格式 | 否 | 2 |
| 第 4 轮 | 修路径 | 否 | 2 |
| 第 5 轮 | 读 AGENTS.md → 全量重写 | 是 | 0 |

> **关联模块**：
> - `docs/retrospective/reports/project-governance/retrospective-session-agents-md-violation-20260624/`
> - `docs/retrospective/patterns/methodology-patterns/review-insight-export-loop.md`
> - `docs/knowledge/troubleshooting/agents-md-startup-protocol-skipped.md`
