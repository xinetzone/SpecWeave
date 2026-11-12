```{toctree}
:hidden:
:maxdepth: 2

00-overview
01-architecture
02-chat-and-tools
03-operator-loop
04-sentinel
05-memory
06-skills-and-flows
07-hands-accessibility
08-llm-client
09-cli-and-traces
10-engineering-patterns
```

# 概念文档索引

按「入门 → 运行主链路 → 数据与扩展 → 迁移」四层排列。建议至少按顺序读 00、01、03、04，其余按需。

| 层 | 编号 | 文档 | 一句话说明 |
|---|---|---|---|
| 入门 | 00 | [PhonePal 全景](00-overview.md) | 一分钟心智模型、关键数字、能力边界 |
| 入门 | 01 | [分层与依赖](01-architecture.md) | 8 个模块、依赖方向、AppGraph 装配、数据目录 |
| 主链路 | 02 | [一轮聊天](02-chat-and-tools.md) | 系统提示词三段、6 个工具、8 轮工具循环 |
| 主链路 | 03 | [操作循环](03-operator-loop.md) | 观察 → 一步动作 → 反馈、卡死检测、受保护屏幕 |
| 主链路 | 04 | [安全闸门](04-sentinel.md) | deny/ask/allow、17 个确认词、任务级授权与审计 |
| 数据与扩展 | 05 | [记忆](05-memory.md) | Basic Memory 格式、原子写、中文 BM25、howto 沉淀 |
| 数据与扩展 | 06 | [技能与 flow](06-skills-and-flows.md) | 7 个 frontmatter 键、8 种 flow 步骤、校验与坑 |
| 数据与扩展 | 07 | [无障碍手眼](07-hands-accessibility.md) | 截屏节流、黑帧识别、节点压缩、手势执行 |
| 数据与扩展 | 08 | [模型客户端](08-llm-client.md) | 重试、JSON 模式降级、图片编码、密钥脱敏 |
| 数据与扩展 | 09 | [CLI 与轨迹](09-cli-and-traces.md) | 6 个命令、调试桥、三层证据 |
| 迁移 | 10 | [工程模式与边界](10-engineering-patterns.md) | 五条可迁移模式、反模式、它不解决的问题 |
