---
title: "开源工具替代订阅费独立审查"
source: "spec.md"
status: "pending"
---

# 独立审查

审查范围：事实双表、F 引用、frontmatter、toctree、相对链接、敏感信息和计数。

- [x] R1 事实编号连续且双表一致
- [x] R2 五项目与文章结构覆盖完整
- [x] R3 价格、星标和“替代”主张均带证据边界
- [x] R4 examples 明确非实测，不误导为官方结果
- [x] R5 子项目机械门禁通过；未运行 Sphinx/invoke，已在 log.md 记录等效验证范围

结论：通过（文档交付层面）。限制：未执行项目安装、未调用付费 API、未做性能基准或法律审查；bundle 保持 `flagged`。
