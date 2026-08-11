---
id: "hermes-agent-integration-05-auth-permission"
title: "05 权限认证流程"
source: "hermes-agent 插件文档 v2.5.0 + SpecWeave 现状"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/05-auth-permission.toml"
type: "Wiki Tutorial"
description: "权限认证流程：插件 name 消毒、路径安全、manifest_version、HERMES_HOME、API key 环境变量、project 插件权限"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Hermes 插件的安全机制：名称消毒、路径穿越防护、manifest_version 校验、环境变量密钥与 project 插件权限开启"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 05 权限认证流程

## 5.1 集成涉及的安全要点

| 关注点 | 说明 |
|--------|------|
| 插件名安全 | 防止路径穿越/恶意名称 |
| 安装路径 | 限制在 `~/.hermes/plugins/` 内 |
| manifest_version | 校验清单 schema 版本 |
| HERMES_HOME | 配置目录隔离 |
| API key | 环境变量管理密钥 |
| project 插件权限 | 项目级插件需显式开启 |

## 5.2 插件 name 消毒与路径安全

Hermes 在安装插件时会消毒插件名并校验路径：

- **拒绝**包含 `/`、`\`、`..` 的插件名（防止路径穿越）
- 校验解析后的路径**必须**在 `~/.hermes/plugins/` 内
- 使用 `http://` 与 `file://` URL scheme 会触发安全警告

**对 SpecWeave 的要求**：SpecWeave 插件的 `plugin.yaml` 中 `name` 必须是安全的短标识（如 `specweave`），不能包含路径分隔符或 `..`。

## 5.3 manifest_version 校验

- `plugin.yaml` 中的 `manifest_version` 是插件清单 schema 版本（当前恒为 `1`）
- 若插件声明的 `manifest_version` **高于**安装器支持的版本，安装会被**拒绝**并提示升级 Hermes
- 若插件缺少 `plugin.yaml`，安装器会用仓库名作为插件名并继续（不推荐）

**实践**：SpecWeave 插件保持 `manifest_version: 1`，与当前 Hermes 兼容。

## 5.4 HERMES_HOME 目录隔离

- 默认配置目录 `~/.hermes`
- 通过 `HERMES_HOME` 重定向可隔离多个配置/插件环境
- 生产环境建议用独立 `HERMES_HOME` 隔离 SpecWeave 插件与个人插件

```bash
export HERMES_HOME=/path/to/specweave-hermes-home
```

## 5.5 API key 环境变量管理

SpecWeave 的某些能力需要密钥（如论坛、智能家居、vendor 的 zhihu 技能等）。密钥通过环境变量注入，不写入代码或插件目录：

```bash
# 示例（需验证对应服务要求）
export ZHIHU_ACCESS_SECRET="..."
export HOME_ASSISTANT_TOKEN="..."
export APIARIO_API_KEY="..."   # model provider 示例
```

> **安全原则**：密钥不进仓库、不进 plugin.yaml、不进 `~/.hermes/config.yaml`，一律用环境变量。SpecWeave 的 [数据安全规则](../../../../../rules/README.md) 同样适用。

## 5.6 project 插件权限开启

项目级插件 `./.hermes/plugins` 默认需手动开启权限才能加载：

1. 在项目根目录创建 `./.hermes/plugins/` 并放入插件
2. 在 Hermes 配置/CLI 中开启 project 插件权限（按官方指引，需验证）
3. 将插件加入 `plugins.enabled`

**适用**：团队共享 SpecWeave 插件能力。

## 5.7 安全清单

- [ ] 插件 `name` 不含 `/`、`\`、`..`
- [ ] 插件安装路径在 `$HERMES_HOME/plugins/` 内
- [ ] `manifest_version` 与 Hermes 兼容
- [ ] 密钥全部走环境变量，不入库/不入配置
- [ ] project 插件已显式开启权限
- [ ] http/file scheme 插件源已确认可信

## 5.8 相关章节

- 配置：[配置文件设置](03-configuration.md)
- 调用：[调用方式示例](06-usage-examples.md)
- 排查：[常见问题及解决方案](07-troubleshooting.md)
