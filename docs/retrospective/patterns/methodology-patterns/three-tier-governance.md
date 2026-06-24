+++
id = "three-tier-governance"
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

# 三层治理模型：原子化→自动化→验证

## 模型概述
文档治理的三层递进模型，三层之间存在严格的依赖关系，必须同时存在才能形成闭环。

## 第一层：原子化
- 目标：将大型文档拆分为独立模块，建立清晰的模块边界
- 方法：按主题拆分，每文件单一职责，保持 50-100 行
- 输出：独立可引用的 .md 文件
- 验证标准：每个文件可被独立理解，无需阅读其他文件

## 第二层：自动化
- 目标：消除手动维护，通过脚本自动生成和维护
- 方法：导航表自动生成（generate-nav.py）、路径迁移（check-move.py）
- 关键：使用 HTML 注释标记（<!-- NAV_TABLE_START -->）定位更新区域
- 验证标准：文档新增/移动/删除后，运行自动化脚本即可完成同步

## 第三层：验证
- 目标：保证链接正确性和内容完整性
- 方法：链接检查器（check-links.py）、规格一致性检查（check-spec-consistency.py）
- 关键：验证必须覆盖所有本地引用，支持模板占位符过滤
- 验证标准：零断链，零误报

## 依赖关系
```
原子化（前提）→ 自动化（手段）→ 验证（保障）
     ↓                ↓               ↓
 模块边界清晰    维护成本趋零    质量可度量
```

## 实施检查清单
- [ ] Layer 1：所有文档已原子化，每个文件 < 200 行
- [ ] Layer 2：导航表自动生成脚本就绪，文件移动工具就绪
- [ ] Layer 3：链接检查器覆盖所有 .md 文件，CI 集成就绪

> 来源：来自 retrospective-insight-optimization-cycle.md 洞察 3
> 关联模块：`.agents/scripts/`、`docs/README.md`