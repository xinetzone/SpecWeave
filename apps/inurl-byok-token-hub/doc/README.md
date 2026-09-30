---
id: "inurl-byok-docs-index"
title: "inurl BYOK Token Hub 文档索引"
source: "../README.md"
---
# inurl BYOK Token Hub 文档

BYOK 统一令牌枢纽复刻：E2EE 密钥保险库 + 逻辑别名路由 + 本地三协议代理 + 用量计费。

本目录由应用根 [README.md](../README.md) 原子化而来，每篇文档一个主题，可独立引用。

## 文档目录

| 文档 | 主题 | 源 README 章节 |
|---|---|---|
| [00-overview.md](00-overview.md) | 项目定位、能力版图、复刻边界声明、源知识包与勘误落地 | 文首 / §10 |
| [01-quickstart.md](01-quickstart.md) | 环境要求、安装、冒烟、启动服务与全部 CLI 子命令 | §1 |
| [02-architecture.md](02-architecture.md) | 分层架构、目录职责与分层约束（测试守护） | §2 |
| [03-configuration.md](03-configuration.md) | 环境变量与配置覆盖链 | §3 |
| [04-api-reference.md](04-api-reference.md) | 本地代理 / 账户密钥库 / 公开 / 管理员后台 / 控制台五组接口 | §4 |
| [05-auth-and-errors.md](05-auth-and-errors.md) | 鉴权与错误语义（401/403/错误体逐字对齐源文档） | §5 |
| [06-data-model.md](06-data-model.md) | Provider / ModelEntry / EscrowRecord / VaultKeyRecord / RouteDecision | §6 |
| [07-testing-and-build.md](07-testing-and-build.md) | 测试命令、覆盖率口径与构建后端 | §7 |
| [08-assumptions-and-differences.md](08-assumptions-and-differences.md) | A1–A24 假设与差异（默认值 / 溯源 / 风险 / 代码定位） | §8 |
| [09-security-boundaries.md](09-security-boundaries.md) | 安全边界六条（必读） | §9 |

## 常用入口

- 最快跑通：[01-quickstart.md](01-quickstart.md)
- 接入代理前必读：[05-auth-and-errors.md](05-auth-and-errors.md)、[09-security-boundaries.md](09-security-boundaries.md)
- 理解实现取舍与复刻差异：[08-assumptions-and-differences.md](08-assumptions-and-differences.md)
