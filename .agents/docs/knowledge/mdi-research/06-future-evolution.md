---
id: mdi-future-evolution
title: MDI研究报告 - 未来演进方向
source: "mdi-research-report.md#7-未来演进方向"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/mdi-research/06-future-evolution.toml"
---

# 未来演进方向

## 短期规划（v1.1）

- [ ] 支持JSON Schema引用（`$ref`），增强类型表达能力
- [ ] CLI专用测试生成器（替代HTTP风格的pytest生成）
- [ ] Watch模式：文件变更时自动重新生成代码
- [ ] 预提交钩子集成，自动验证MDI文档

## 中期规划（v1.2-v2.0）

- [ ] 插件系统，支持自定义Generator和Validator
- [ ] Markdown → MDI自动转换工具（从现有API文档迁移）
- [ ] MDI Studio可视化编辑器（Web UI）
- [ ] 与OpenAPI的双向转换（MDI↔OpenAPI）
- [ ] AsyncAPI Profile支持（消息队列/事件驱动API）

## 长期愿景

MDI的长期目标是成为"开发者友好的接口定义首选格式"，在AI原生开发时代发挥独特价值：

1. **AI协作原生**：LLM可以直接读写MDI格式，降低人机协作成本
2. **文档即真理**：消除文档与代码不一致的问题，MDI文件是Single Source of Truth
3. **渐进式结构化**：从自由格式到严格规范，支持团队不同成熟度阶段
4. **生态互通**：作为"源格式"与OpenAPI/AsyncAPI/Protobuf等生态无缝衔接

---

**下一步阅读**：
- [结论](07-conclusion.md) - 核心建议与采用决策
- [返回版本控制最佳实践](05-versioning-best-practices.md)
- [返回索引](../mdi-research-report.md)
