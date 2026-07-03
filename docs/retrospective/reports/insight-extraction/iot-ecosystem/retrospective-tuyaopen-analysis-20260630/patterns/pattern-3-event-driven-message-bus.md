---
id: "tuyaopen-pattern-3-event-driven"
title: "模式 3：事件驱动架构（消息总线）"
source: "insight-extraction.md#模式-3事件驱动架构消息总线"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-tuyaopen-analysis-20260630/patterns/pattern-3-event-driven-message-bus.toml"
---
# 模式 3：事件驱动架构（消息总线）

**模式名称**：事件驱动架构

**核心理念**：
> 通过消息总线解耦各模块，实现异步、松耦合的模块协作，适用于嵌入式 AI 应用。

**适用场景**：
- 嵌入式 AI 应用多模块协作
- 需要异步处理用户输入和 AI 响应
- 需要支持多渠道输入（Telegram/Discord/Feishu）

**实现步骤**：

```markdown
1. **定义消息总线**
   - 消息类型：INBOUND（用户输入）、OUTBOUND（AI 响应）、TOOL_CALL（工具调用）
   - 消息格式：标准化的 JSON 结构
   - 订阅机制：模块注册消息处理器

2. **模块集成**
   - Bot 模块：订阅 OUTBOUND，发送 INBOUND
   - Agent Loop：订阅 INBOUND，发送 OUTBOUND
   - Tool Registry：订阅 TOOL_CALL，执行并返回

3. **线程模型**
   - 主线程：Agent Loop 处理
   - Bot 线程：渠道监听和消息发送
   - Tool 线程：硬件操作执行

4. **队列机制**
   - 消息队列：tal_queue（FIFO）
   - 优先级队列：紧急消息优先处理
   - 缓冲机制：避免消息丢失
```

**关键文件示例**：
- `bus/message_bus.h`：总线接口定义
- `agent/agent_loop.c`：主循环实现
- `channels/<bot>.c`：渠道集成

**效果验证**：
- 支持 3+ 渠道并行处理
- 模块解耦，易于扩展
- 异步处理，响应及时

**局限性**：
- 消息队列占用内存
- 异步调试复杂度较高
- 需要合理的线程数量控制

**可复用场景**：
- 嵌入式 AI 应用多模块协作
- 需要支持多渠道输入的应用
- 需要异步处理的 IoT 应用

---

**[返回洞察萃取索引](../../insight-extraction.md)**