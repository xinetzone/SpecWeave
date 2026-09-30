---
id: "inurl-byok-architecture"
title: "架构与分层"
source: "../README.md"
---
# 架构与分层

> 内容迁移自根 README §2。

```
config/       配置（默认值 → config.yaml → 环境变量 BYOK_*）
models/       数据模型（pydantic v2，frozen）
crypto/       E2EE：PBKDF2-SHA256(100000) → AES-256-GCM
storage/      JSON 表仓库 + 原子写 + 跨平台单实例锁
services/     token / vault / catalog / router / strategies / compression
              health / usage / billing / chat / ops / hub
providers/    transport 抽象 + OpenAI兼容 / Anthropic / Gemini 三协议适配器
api/          FastAPI：/v1 代理、/api 账户与公开、/api/admin 后台
web/          Jinja2 精简控制台（服务端渲染，无前端构建链）
cli/          Typer 命令行
```

> 注：上表为包内逻辑分层；源码实际位于 `src/inurl_byok_token_hub/` 下（如 `crypto.py`、`config.py`、`cli.py` 位于包根，其余分层对应同名子包）。

## 分层约束

分层约束由 [tests/test_audit.py](../tests/test_audit.py)::test_layer_boundaries 守护：

- `services` 不得反向依赖 `api`/`web`/`cli`；
- `models` 不得依赖 `services`/`api`；
- 外部调用**必须**经 `providers.transport` 抽象，适配器中禁止直接使用 httpx。
