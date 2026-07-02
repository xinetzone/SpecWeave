---
id: "rules-alt-detection-checklist"
title: "10 附录：硬编码检测清单"
source: "alternatives-guide.md#detection-checklist"
x-toml-ref: "../../../.meta/toml/.agents/rules/alternatives-guide/10-detection-checklist.toml"
---
# 10 附录：硬编码检测清单


在代码审查中，以下模式应被标记为硬编码并触发替代方案要求：

| 检测模式 | 示例（应标记） | 正确写法 |
|---|---|---|
| 数字字面量参与业务逻辑 | `if retry_count > 3:` | `if retry_count > config.get("retry.max_attempts"):` |
| 字符串 URL | `requests.get("https://api.example.com/v1/users")` | `requests.get(config.get("services.api.base_url") + "/users")` |
| 文件路径字符串 | `open("data/export.csv")` | `open(os.path.join(DATA_DIR, "export.csv"))` |
| 正则表达式内联 | `re.match(r"^1[3-9]\d{9}$", phone)` | `PHONE_CN_PATTERN.match(phone)` |
| 错误消息内联 | `raise ValueError("订单不存在")` | `raise ValueError(get_error("ORDER_NOT_FOUND", order_id=id))` |
| 色值硬编码 | `color: #2563EB;` | `color: var(--color-primary);` |
---

## 相关模式

- [硬编码治理](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/)
- [三级问题解决](../../../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [检查与恢复模式](../../../docs/retrospective/patterns/code-patterns/check-and-restore.md)
---

← 上一章: [09 迁移策略](09-migration-strategy.md) | **[返回索引](../alternatives-guide.md)**
