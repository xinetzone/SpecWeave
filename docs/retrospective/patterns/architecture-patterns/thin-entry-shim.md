---
id: "thin-entry-shim"
source: "docs/retrospective/reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/architecture-patterns/thin-entry-shim.toml"
---
> **提炼自**：[insight-extraction.md](../../reports/project-reports/retrospective-mdi-project-completion-20260702/insight-extraction.md) —— MDI项目完成复盘（洞察10）

# 薄入口垫片模式（Thin Entry Shim）

## 模式类型

架构/代码模式

## 成熟度

L1 首次提炼（MDI项目14个模块拆分验证，import路径100%不变）

## 适用场景

需要保持向后兼容的代码重构、模块拆分、包结构重组；当重构不能要求所有调用方同步修改时。

## 问题背景

传统重构的最大风险：
- 内部结构重构后，外部import路径全部断裂
- 要求所有调用方同步修改，协调成本高
- 大重构难以分阶段实施，要么全部改完要么不改
- 重构过程中无法保证随时可回滚

## 核心思想

**原文件保留为<30行的薄re-export层，实现外部import路径100%不变，内部结构可彻底重构，未来可平滑过渡。**

## MDI项目验证

- 14个拆分后的模块均保留原文件作为薄入口
- 现有159+测试全部通过，无需修改任何import路径
- CLI命令行调用方式完全不变
- 重构过程随时可以停止，已拆分部分不影响未拆分部分

## 核心规则

### 规则1：薄入口结构

原文件只做re-export，不包含任何业务逻辑：

```python
# 原文件：parser.py（薄入口，<30行）
from .parser.core import Parser
from .parser.tokenizer import tokenize
from .parser.section_builder import build_sections
from .parser.directive_parser import parse_directives

__all__ = ['Parser', 'tokenize', 'build_sections', 'parse_directives']
```

### 规则2：三阶段过渡策略

| 阶段 | 说明 | 时长建议 |
|------|------|---------|
| 阶段1：双轨期 | 新代码从新路径import，旧代码继续用旧路径，薄入口保障兼容 | 1-2个迭代周期 |
| 阶段2：迁移期 | 逐步将旧import迁移到新路径，薄入口保留，添加DeprecationWarning | 2-4个迭代周期 |
| 阶段3：清理期 | 确认无调用方使用旧路径后，删除薄入口文件 | 大版本升级时 |

### 规则3：禁止在薄入口添加逻辑

薄入口必须是纯转发层，严禁在其中添加：
- 业务逻辑
- 条件判断
- 兼容处理逻辑
- 任何超过30行的代码

如果需要兼容逻辑，应在内部模块中处理，薄入口只做符号导出。

### 规则4：测试双覆盖

- 保留原有测试（使用旧import路径）——验证薄入口正确性
- 新增模块内部测试（使用新路径）——验证内部实现正确性
- 两者同时运行，确保重构不破坏任何功能

## 实施检查清单

- [ ] 拆分后是否保留原文件作为薄入口？
- [ ] 薄入口是否<30行且仅做re-export？
- [ ] `__all__`是否正确导出所有公开符号？
- [ ] 原有测试是否无需修改全部通过？
- [ ] 是否规划了三阶段过渡策略？
- [ ] 新代码是否从新路径import？

## 反例警示

| 错误做法 | 后果 |
|---------|------|
| 删除旧文件，要求所有调用方改import | 重构协调成本高，容易遗漏导致线上故障 |
| 在旧文件中保留部分业务逻辑 | 新旧逻辑并存，后续维护混乱 |
| 薄入口做复杂的条件转发 | 入口层变厚，失去"薄"的意义，成为新的上帝文件 |
| 没有过渡阶段直接删除旧路径 | 调用方来不及迁移，版本升级阻力大 |

## 与现有模式的关系

- `pattern-driven-refactoring.md`：薄入口垫片是模式驱动重构的核心子模式
- `dual-interface-repository.md`：类似思想，对外保持稳定接口，内部可自由重构
- `incremental-regression-verification.md`：薄入口让逐模块验证成为可能