---
id: "inurl-byok-configuration"
title: "环境变量与配置覆盖链"
source: "../README.md"
---
# 环境变量

> 内容迁移自根 README §3。配置加载顺序（见 §2 架构说明）：默认值 → [config.yaml](../config.yaml) → 环境变量 `BYOK_*`。

| 变量 | 作用 |
|---|---|
| `BYOK_*` | 覆盖 `config.yaml` 同名项，如 `BYOK_PORT`、`BYOK_MAX_ATTEMPTS`、`BYOK_HIDE_HIDDEN_PROVIDERS` |
| `AGENT_TOKEN` | 统一令牌（对应原产品手动启动方式） |
| `AGENT_MASTERKEY` | 主密钥（同上） |
| `AUTO_MODELS` | 限定路由模型池（逗号分隔） |
| `AUTO_PROVIDER_ORDER` | 厂商优先级（逗号分隔） |
