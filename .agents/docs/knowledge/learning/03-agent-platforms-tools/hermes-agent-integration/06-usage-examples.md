---
id: "hermes-agent-integration-06-usage-examples"
title: "06 调用方式示例"
source: "hermes-agent 插件文档 v2.5.0 + hermes-okf v0.5.9 Wiki（Quick-Start）+ SpecWeave 现状"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-integration/06-usage-examples.toml"
type: "Wiki Tutorial"
description: "调用方式示例：hermes plugins install、hermes okf、Hermes 会话内工具调用、with_context 召回"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "覆盖 Hermes 插件生命周期命令、hermes-okf 记忆命令、会话内工具调用与 with_context 记忆召回的完整调用示例"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 06 调用方式示例

> **⚠️ 所有命令为示例，落地前以官方文档为准并验证。**

## 6.1 插件生命周期命令

```bash
# 查看插件（交互式面板 / 列表）
hermes plugins
hermes plugins list

# 启用 / 禁用（加入允许/拒绝列表）
hermes plugins enable specweave
hermes plugins disable some-plugin

# 安装（从 Git shorthand 或完整 URL）
hermes plugins install owner/repo
hermes plugins install https://github.com/owner/repo.git --enable

# 更新（git pull --ff-only）
hermes plugins update specweave

# 卸载
hermes plugins remove specweave
```

> 安装/卸载后需**重启 Hermes**（如 `hermes gateway restart`）使改动生效。

## 6.2 hermes-okf 记忆命令

```bash
# 安装与注册（自动配置 config.yaml）
pip install hermes-okf
hermes-okf install-plugin

# 校验配置（15 项检查）
hermes-okf validate-config

# 记忆设置向导（bundle 路径 / agent id）
hermes memory setup

# 启动 Hermes
hermes

# Hermes 会话内检索记忆
hermes okf show config/agent
hermes okf list --type Decision
hermes okf search "SpecWeave"
hermes okf snapshot --note "里程碑"
hermes okf restore
```

## 6.3 Hermes 会话内工具调用

集成后，在 Hermes 会话内可直接让 Agent 调用 SpecWeave 工具。以复盘工具为例：

```
用户：请对最近一次里程碑做一次复盘
Agent：（识别到 specweave_retrospective 工具匹配，生成调用）
```

工具调用由模型按 tool schema 生成参数并触发 handler，返回 JSON 结果进入会话上下文。

## 6.4 with_context 记忆召回

hermes-okf 提供 `with_context` 用于在代码/会话中召回记忆（示例，需验证）：

```python
from hermes_okf import HermesMemoryMixin

class MyAgent(HermesMemoryMixin):
    def run(self):
        # 召回与当前任务相关的历史记忆
        context = self.with_context("SpecWeave 复盘模式")
        print(context)
        # ... 使用 context 继续
```

也可用装饰器记忆决策/工具（示例，需验证）：

```python
@memorize_decision("采用 OKF 作为记忆层")
def choose_memory():
    return "okf"

@memorize_tool
def some_tool(...):
    ...
```

> 对多数用户推荐**插件方式**（`hermes-okf install-plugin`），装饰器用于高级/自定义场景。

## 6.5 端到端流程示例

```bash
# 1. 安装记忆层
pip install hermes-okf
hermes-okf install-plugin
hermes-okf validate-config

# 2. 安装 SpecWeave 插件
hermes plugins install <owner>/specweave-hermes --enable

# 3. 确认配置
cat ~/.hermes/config.yaml   # plugins.enabled 含 specweave 与 hermes-okf

# 4. 启动 Hermes
hermes

# 5. 会话内调用能力 + 记忆持久化
hermes okf search "历史决策"
```

## 6.6 相关章节

- 配置：[配置文件设置](03-configuration.md)
- 转换：[数据格式转换方法](04-data-conversion.md)
- 排查：[常见问题及解决方案](07-troubleshooting.md)
