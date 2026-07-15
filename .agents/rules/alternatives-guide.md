---
id: "rules-alternatives-guide"
title: "替代方案指南"
source: "AGENTS.md#规则体系"
x-toml-ref: "../../.meta/toml/.agents/rules/alternatives-guide.toml"
---
# 替代方案指南

本指南是硬编码治理规则体系的核心文档，针对每种硬编码类型提供推荐的替代方案与具体实施步骤。遵循本指南可有效消除代码中的硬编码问题，提升项目的可维护性、可配置性与可移植性。

## 规范说明

硬编码（Hardcoding）是指在源代码中直接写入具体数值、字符串或配置信息，而非通过外部化方式引用。硬编码会导致以下问题：

- **可维护性下降**：修改一个配置值需要改动多处代码并重新编译部署。
- **可移植性不足**：环境差异（开发、测试、生产）无法通过统一机制切换。
- **安全风险**：敏感信息（密钥、密码）嵌入代码，容易泄露至版本控制系统。
- **国际化困难**：UI 文本与业务逻辑耦合，无法支持多语言。

本指南为每种硬编码类型提供标准化的替代方案，遵循"先识别、后迁移、新代码零容忍"的治理原则。

## 类型与替代方案映射表

| 硬编码类型 | 类型标识 | 典型表现 | 推荐替代方案 | 优先级 |
|---|---|---|---|---|
| 配置参数 | `HARD-CFG` | 超时时间、重试次数、缓存大小、开关阈值等以字面量写入代码 | [配置文件管理](alternatives-guide/01-config-files.md) | P0 |
| 业务常量 | `HARD-NUM` | 状态码、类型标识、费率、比例等固定数值散落各处 | [常量定义与枚举](alternatives-guide/03-constants-enums.md) | P0 |
| URL/端点 | `HARD-URL` | API 地址、服务端点、第三方回调 URL 直接写在请求代码中 | [配置文件](alternatives-guide/01-config-files.md) + [环境变量](alternatives-guide/02-env-vars.md) | P0 |
| 路径 | `HARD-PATH` | 文件路径、目录路径以字符串字面量出现在代码中 | [常量定义](alternatives-guide/03-constants-enums.md)集中管理 | P1 |
| 错误/提示信息 | `HARD-STR` | 异常消息、日志模板、用户提示以字符串直接内联 | [消息字典](alternatives-guide/04-message-dictionary.md)（支持国际化） | P1 |
| UI 文本 | `HARD-STR` | 按钮文案、标签文本、占位符等直接写在 UI 模板中 | [国际化资源文件](alternatives-guide/05-i18n.md)（i18n） | P2 |
| 正则模式 | `HARD-REGEX` | 正则表达式字面量散落在验证函数中 | [模式常量库](alternatives-guide/06-regex-patterns.md) | P2 |
| 颜色/样式 | `HARD-STYLE` | CSS 色值、字体大小、间距数值直接写在样式定义中 | [设计令牌](alternatives-guide/07-design-tokens.md)（Design Tokens） | P2 |
| 编码值 | `HARD-ENC` | 字符编码名称、MIME 类型、协议常量以字符串出现 | [常量定义](alternatives-guide/03-constants-enums.md)（引用标准） | P2 |

## 文档导航

| 章节 | 说明 |
|------|------|
| [01 配置文件管理（YAML/JSON/TOML）](alternatives-guide/01-config-files.md) | 配置文件管理（YAML/JSON/TOML） |
| [02 环境变量](alternatives-guide/02-env-vars.md) | 环境变量 |
| [03 常量定义与枚举](alternatives-guide/03-constants-enums.md) | 常量定义与枚举 |
| [04 资源文件/消息字典](alternatives-guide/04-message-dictionary.md) | 资源文件/消息字典 |
| [05 国际化资源文件（i18n）](alternatives-guide/05-i18n.md) | 国际化资源文件（i18n） |
| [06 正则模式常量库](alternatives-guide/06-regex-patterns.md) | 正则模式常量库 |
| [07 主题变量/设计令牌](alternatives-guide/07-design-tokens.md) | 主题变量/设计令牌 |
| [08 项目模板与脚手架结构](alternatives-guide/08-project-scaffold.md) | 项目模板与脚手架结构 |
| [09 迁移策略（渐进式）](alternatives-guide/09-migration-strategy.md) | 迁移策略（渐进式） |
| [10 附录：硬编码检测清单](alternatives-guide/10-detection-checklist.md) | 附录：硬编码检测清单 |

---

## 相关模式

- [检查与恢复模式](../docs/retrospective/patterns/code-patterns/check-and-restore.md)
- [三级问题解决](../docs/retrospective/patterns/methodology-patterns/governance-strategy/three-level-problem-solving.md)
- [Dry-run优先原则](../docs/retrospective/patterns/methodology-patterns/tools-automation/dry-run-first.md)
