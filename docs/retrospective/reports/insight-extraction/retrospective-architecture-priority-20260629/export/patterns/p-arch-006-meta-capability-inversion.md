+++
id = "p-arch-006"
name = "元能力依赖倒置"
name_en = "Meta-Capability Inversion"
date = "2026-06-29"
type = "pattern-detail"
maturity = "L2"
source = "export-suggestions.md#p-arch-006"
+++

# P-ARCH-006 元能力依赖倒置

**问题**：编排类/元能力（如自我演进模块）往往被放在早期实现，但它们依赖的原子能力还未标准化。

**解决方案**：正确的实现顺序：
1. 先定义原子能力的标准接口（SKILL.md 规范）
2. 实现核心原子能力（指令集/脚本的SKILL封装）
3. 再在原子能力之上构建编排/元能力

**类比**：微服务架构——先 API 契约，再服务实现，最后服务编排。
