---
id: "tuyaopen-suggestion-2"
title: "建议 2：完善单元测试覆盖"
source: "export-suggestions.md#建议-2完善单元测试覆盖"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-tuyaopen-analysis-20260630/suggestions/suggestion-2-test-coverage.toml"
---
# 建议 2：完善单元测试覆盖

**问题**：仅有导出脚本测试，缺少核心模块单元测试

**建议方案**：
1. 为 `tal_system/` 模块添加单元测试
2. 为 `llm_proxy` 添加 LLM Mock 测试
3. 为 `message_bus` 添加集成测试
4. 使用 mockcpp 框架（已有工具）

**预期收益**：提升代码质量，降低回归风险

**实施难度**：中（需要测试工程师）

**实施时间**：2-3 周

---

**[返回导出建议索引](../../export-suggestions.md)**