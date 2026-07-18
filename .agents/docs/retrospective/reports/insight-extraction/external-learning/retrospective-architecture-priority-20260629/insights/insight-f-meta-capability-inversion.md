---
id: "architecture-priority-insight-f"
title: "洞察 F：自我演进模块（8模块）的实现时机被重新定义"
source: "insight-extraction.md#洞察-f"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/insights/insight-f-meta-capability-inversion.toml"
---
# 洞察 F：自我演进模块（8模块）的实现时机被重新定义

**现象**：8个自我演进模块（self-insight/self-retrospective等）当前是 L1 规划态，报告中列为"不重构"——等 Skill 体系完善后再实现。

**深层洞察**：
- 之前认为"先有模块定义，再逐步实现每个模块"
- 现在意识到：这些模块的实现**依赖** Skill 体系作为基础设施
- 理由：自我演进模块本质上是"自动化编排多个能力"的元能力——比如 self-retrospective 需要自动调用 retrospective SKILL、insight SKILL、atomization SKILL
- 如果底层 SKILL 还没有标准化的调用接口，自我演进模块无法实现
- 这修正了架构演进顺序：
  ```
  旧认知：模块定义 → 模块实现 → Skill化封装
  新认知：Skill基础设施 → 单个Skill实现 → 自我演进模块编排多个Skill
  ```

**可复用模式**：**元能力依赖倒置（Meta-Capability Inversion）**
> 编排类元能力（如自我演进模块）不应该先于被编排的原子能力实现。正确顺序是：
> 1. 先定义原子能力的标准接口（SKILL.md 规范）
> 2. 实现核心原子能力（指令集/脚本的SKILL封装）
> 3. 再在原子能力之上构建编排/元能力（自我演进模块）
> 
> 这类似于微服务架构：先定义服务间通信标准（API契约），再实现服务，最后做服务编排。
