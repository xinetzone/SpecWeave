---
id: "tuyaopen-pattern-2-llm-adapter"
title: "模式 2：多模型统一接口（LLM 适配器）"
source: "insight-extraction.md#模式-2多模型统一接口llm-适配器"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/insight-extraction/iot-ecosystem/retrospective-tuyaopen-analysis-20260630/patterns/pattern-2-llm-adapter-unified-interface.toml"
---
# 模式 2：多模型统一接口（LLM 适配器）

**模式名称**：多模型统一接口

**核心理念**：
> 通过适配器模式，统一不同 LLM 提供商的 API，实现模型的热插拔和多提供商切换。

**适用场景**：
- AI 应用需要支持多个 LLM 提供商
- 需要在 OpenAI、Anthropic、国产大模型之间切换
- 需要支持自定义 API 端点

**实现步骤**：

```markdown
1. **定义统一接口**
   - 抽象方法：chat_completion, stream_chat, tool_call
   - 参数标准化：model, messages, tools, temperature

2. **实现适配器**
   - OpenAIAdapter：适配 OpenAI/兼容 API
   - AnthropicAdapter：适配 Claude API
   - DeepSeekAdapter：适配国产大模型

3. **配置管理**
   - CLI 配置：set_model_provider, set_api_key, set_model
   - 配置文件：默认配置文件
   - 运行时切换：无需重新编译

4. **错误处理**
   - 统一的错误码映射
   - 重试机制（网络错误、超时）
   - 日志记录和告警
```

**关键代码示例**（MimiClaw）：
- `llm/llm_proxy.h`：统一接口定义
- `llm/llm_proxy.c`：适配器实现
- 支持 OpenAI、Anthropic、兼容 API

**效果验证**：
- 支持 5+ 模型提供商
- 配置切换无需重新编译
- 新模型适配时间 < 1 天

**局限性**：
- 不同模型的特性可能无法完全兼容
- Tool calling 格式可能有差异
- 成本计算需要额外处理

**可复用场景**：
- AI 应用多模型支持
- 需要同时对接多个 LLM 提供商的项目
- 需要支持自定义 API 端点的场景

---

**[返回洞察萃取索引](../insight-extraction.md)**