+++
id = "tool-entropy-metrics"
domain = "methodology"
layer = "methodology"
maturity = "L2"
validation_count = 2
reuse_count = 0
documentation_level = "basic"
source = "docs/retrospective/knowledge-extraction.md"

[bindings]
rules = []
references = []
skills = []
+++

# 工具熵减度量体系

## 核心概念
"熵"指系统的手动维护成本。每个工具的目标是定向削减一类特定的熵。度量熵减效果是判断工具价值的核心依据。

## 度量公式
```
熵减收益 = 手动总成本 - 工具开发成本
手动总成本 = 操作频率 × 单次耗时 × 预期生命周期
工具 ROI = 熵减收益 / 工具开发成本
```

## 已实施工具的熵减分析

| 工具 | 削减的熵类型 | 频率 | 单次耗时 | 生命周期 | 手动总成本 | 开发成本 | ROI |
|------|------------|------|---------|---------|-----------|---------|-----|
| check-links.py | 链接断裂熵 | 每日 3 次 | 15 分钟 | 2 年 | 21900 分钟 | 90 分钟 | 243x |
| generate-nav.py | 导航维护熵 | 每周 5 次 | 5 分钟 | 2 年 | 2600 分钟 | 60 分钟 | 43x |
| check-move.py | 路径迁移熵 | 每月 2 次 | 10 分钟 | 2 年 | 480 分钟 | 80 分钟 | 6x |
| check-gitignore.py | 依赖泄漏熵 | 每日 1 次 | 3 分钟 | 2 年 | 2190 分钟 | 40 分钟 | 55x |
| ci-check.ps1 | 检查遗漏熵 | 每日 3 次 | 5 分钟 | 2 年 | 10950 分钟 | 30 分钟 | 365x |

## 熵分类体系

| 熵类型 | 描述 | 典型工具 |
|--------|------|---------|
| 链接断裂熵 | 文件引用失效导致的错误 | check-links.py |
| 导航维护熵 | 手动更新导航表的成本 | generate-nav.py |
| 路径迁移熵 | 文件移动时调整链接的成本 | check-move.py |
| 依赖泄漏熵 | 临时文件被误提交的风险 | check-gitignore.py |
| 检查遗漏熵 | 忘记运行某个检查的风险 | ci-check.ps1 |

## 使用指南
1. 在开发新工具前，先估算"手动总成本"和"工具开发成本"
2. ROI < 3 的工具优先考虑流程改进而非自动化
3. 工具上线后，记录实际频率和耗时，定期校准度量值

> 来源：来自 retrospective-insight-optimization-cycle.md 洞察 5
> 关联模块：`.agents/scripts/`、`docs/retrospective/patterns/methodology-patterns/tool-trigger-mechanism.md`