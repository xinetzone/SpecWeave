---
id: "hermes-agent-integration-07-troubleshooting"
title: "07 常见问题及解决方案"
source: "hermes-agent 插件文档 v2.5.0 + hermes-okf v0.5.9 Wiki（Troubleshooting）+ 集成实践"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/07-troubleshooting.toml"
type: "Wiki Tutorial"
description: "集成常见问题及解决方案：插件未发现/未启用/schema 不匹配/provider 单实例/Windows 路径/name 冲突/restart"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "覆盖 SpecWeave 接入 Hermes 过程中的常见问题：未发现、未启用、schema 不匹配、单实例限制、Windows 路径、name 冲突、未重启"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 07 常见问题及解决方案

每个问题按"现象 / 原因 / 解决方案"组织。

## 7.1 插件未被 Hermes 发现

- **现象**：Hermes 启动后看不到 SpecWeave 插件
- **原因**：插件不在扫描路径（`~/.hermes/plugins` 等）；或 `HERMES_HOME` 指向了别的目录；或 project 插件权限未开启
- **解决**：
  - 确认插件位于 `$HERMES_HOME/plugins/`
  - 检查 `HERMES_HOME` 环境变量与实际安装路径一致
  - 若是 project 插件，确认已开启权限（见 [权限章节](05-auth-permission.md)）

## 7.2 插件已发现但未加载（未启用）

- **现象**：`hermes plugins list` 显示插件但状态为 disabled
- **原因**：插件默认禁用，未加入 `plugins.enabled` 允许列表
- **解决**：
  ```bash
  hermes plugins enable specweave
  # 或手动编辑 ~/.hermes/config.yaml 的 plugins.enabled
  ```

## 7.3 工具 schema 与模型调用不匹配

- **现象**：模型尝试调用工具但失败，参数校验报错
- **原因**：tool schema 的 `required`/`properties` 与实际 handler 逻辑不一致；或 description 不清晰导致模型误触发
- **解决**：
  - 核对 schema 的必填项与 handler 实际所需参数一致
  - 优化 `description`：写清"何时用、何时不用"
  - 枚举参数用 `enum` 限制取值

## 7.4 Memory Provider 单实例限制

- **现象**：启用多个内存插件互相冲突，或替换失败
- **原因**：Memory Provider / Context Engine 仅支持单实例，同时启用多个会互相覆盖
- **解决**：
  - SpecWeave 能力若无特殊需求，走**通用插件**（不占用单实例名额）
  - 记忆层只保留一个 provider（如 hermes-okf）
  - 若确需自定义记忆，替换 hermes-okf 而非叠加

## 7.5 Windows 路径问题

- **现象**：插件安装/发现失败，路径含反斜杠或盘符问题
- **原因**：Windows 路径分隔符与插件 name 消毒规则冲突；或 `HERMES_HOME` 盘符路径未正确处理
- **解决**：
  - 插件 `name` 只用安全短标识，不含路径分隔符
  - 用正斜杠或正确转义配置路径
  - 显式设置 `$env:HERMES_HOME` 为绝对路径
  - 参考 SpecWeave Windows 下文件名/路径处理经验

## 7.6 插件 name 冲突

- **现象**：自定义插件与已装插件同名，行为被覆盖
- **原因**：插件发现"后加载覆盖同名先加载"，同名插件互相覆盖
- **解决**：
  - 使用唯一插件名（如 `specweave` 而非通用名）
  - 检查不同发现路径（用户级 vs 项目级）是否存在同名
  - 用 `hermes plugins remove` 清理旧版本

## 7.7 修改后未生效（需重启）

- **现象**：改了插件或配置，但 Hermes 行为未变化
- **原因**：安装/移除/配置改动后未重启 Hermes 使改动生效
- **解决**：
  ```bash
  hermes gateway restart   # 如有 gateway
  # 或重新启动 hermes
  ```

## 7.8 插件安装被拒绝（manifest_version）

- **现象**：`hermes plugins install` 报错，提示版本不兼容
- **原因**：插件声明的 `manifest_version` 高于 Hermes 支持
- **解决**：`hermes update` 升级 Hermes，或把插件 `manifest_version` 降至兼容值（当前为 `1`）

## 7.9 hermes-okf 记忆层问题

常见于 hermes-okf 官方 Troubleshooting（详见 [hermes-okf-wiki](../../01-agent-protocols-interfaces/okf-wiki/README.md)）：
- `install-plugin` 命令找不到 → 用 `python -m hermes_okf.cli install-plugin`
- `memory setup` 不显示 provider → 确认插件已加入 `plugins.enabled`
- `show` 显示错误模型 → 同步 `config.yaml` 与 OKF 配置
- Windows 文件名错误 → 检查 bundle 文件命名

## 7.10 相关章节

- 配置：[配置文件设置](03-configuration.md)
- 权限：[权限认证流程](05-auth-permission.md)
- 调用：[调用方式示例](06-usage-examples.md)
