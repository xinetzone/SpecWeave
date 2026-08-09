---
id: "hermes-agent-wiki-05-messaging-gateway"
title: "05 消息网关"
source: "hermes-agent user-guide/messaging/index.md + user-guide/messaging/relay.md + profiles.md"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/hermes-agent-wiki/05-messaging-gateway.toml"
type: "Wiki Tutorial"
description: "Hermes Agent 消息网关：约 28 平台支持、单进程多平台、gateway setup/start、跨平台连续性、relay、与 CLI 共享核心"
status: "stable"
category: "learning"
tags: ["hermes", "gateway", "messaging", "relay", "platforms"]
date: "2026-08-09"
author: "seven-concepts knowledge-scenario"
summary: "Hermes 网关用单一进程运行约 28 个消息平台（Telegram/Discord/Slack/WeCom/Feishu 等），通过 gateway setup/start 配置启动；跨平台会话连续、语音备忘录可转写，并可经 relay 连接器接管平台凭据"
last_verified: "2026-08-09"
wiki_version: "1.0"
---
# 05 消息网关

## 5.1 网关是什么

**消息网关（messaging gateway）** 是 Hermes Agent 面向聊天平台的服务化前端：它把同一个代理核心（agent core）接入 Telegram、Discord、Slack、WhatsApp 等即时通讯平台，让代理能直接在用户习惯的聊天应用里对话、接收指令、执行任务。

关键点：CLI、网关、TUI、桌面应用**共享同一个代理核心**——网关不是独立的代理，而是同一核心的不同接入前端。因此你在 CLI 里配置的模型、provider、工具集、推理设置，网关会继承同一份配置（`gateway-config.yaml` 中的 per-channel 覆盖除外，见 5.5）。

## 5.2 支持的平台

网关支持约 **28 个聊天平台**（官方文档所列，持续扩张）。下表为官方文档的平台能力对比（✅=支持，—=不支持），含语音、图片、文件、线程、回复、输入状态、流式等能力：

| 平台 | 语音 | 图片 | 文件 | 线程 | 回复 | 输入状态 | 流式 |
|------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Telegram | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Discord | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Slack | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Google Chat | — | ✅ | ✅ | ✅ | — | ✅ | — |
| WhatsApp | — | ✅ | ✅ | — | — | ✅ | ✅ |
| WhatsApp Cloud API | ✅ | ✅ | ✅ | — | — | ✅ | — |
| Signal | — | ✅ | ✅ | — | — | ✅ | — |
| SMS | — | — | — | — | — | — | — |
| Email | — | ✅ | ✅ | ✅ | — | — | — |
| Home Assistant | — | — | — | — | — | — | — |
| Mattermost | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ |
| Matrix | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| DingTalk | — | ✅ | ✅ | — | ✅ | — | ✅ |
| Feishu/Lark | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| WeCom | ✅ | ✅ | ✅ | — | — | — | — |
| WeCom Callback | — | — | — | — | — | — | — |
| Weixin | ✅ | ✅ | ✅ | — | — | ✅ | — |
| BlueBubbles | — | ✅ | ✅ | — | ✅ | ✅ | — |
| Photon (iMessage) | ✅ | ✅ | ✅ | — | ✅ | ✅ | — |
| QQ | ✅ | ✅ | ✅ | — | — | ✅ | — |
| Yuanbao | ✅ | ✅ | ✅ | — | — | ✅ | ✅ |
| Microsoft Teams | — | ✅ | — | ✅ | — | ✅ | — |
| LINE | — | ✅ | ✅ | — | — | ✅ | — |
| ntfy | — | — | — | — | — | — | — |
| Raft | — | — | — | — | — | — | — |
| IRC | — | — | — | — | — | — | — |
| Buzz | — | ✅ | — | ✅ | — | — | — |
| SimpleX | ✅ | ✅ | ✅ | — | — | ✅ | — |

> 以上平台列表与能力矩阵直接取自官方 `user-guide/messaging/index.md`。不同版本的平台清单可能微调，以发行版文档为准。

## 5.3 单一网关进程运行多平台

网关的设计是**一个进程同时服务多个平台**：你无需为每个平台单独启动一个服务，只需配置并启动一个 gateway，它就会并行接入你启用的所有平台（不同平台可用不同的 bot token，甚至用不同模型与 persona）。

典型启动流程：

```bash
hermes gateway setup        # 交互式配置所有消息平台
hermes gateway start        # 启动默认网关服务
hermes gateway start --system  # 以系统服务方式启动（需 sudo，示例/需验证）
```

配置以平台为单位写入 `~/.hermes/gateway-config.yaml`；不同 profile 可运行各自独立的网关（见 [04 配置体系](./04-configuration.md) 的 profiles 部分）。

## 5.4 跨平台对话连续性

网关提供会话（session）管理与跨平台连续性：同一用户的对话上下文被持久化，用户在不同平台或不同时间继续对话时，代理能记住前文。网关还会把会话存入统一的 SQLite 状态库（`state.db`，含 FTS5 全文搜索），供后续检索。

**语音备忘录转写**：网关支持语音转文字（voice transcription），用户发送的语音消息可被转写为文本后交给代理处理（对应 `stt` 配置）。

## 5.5 每通道模型与 persona 覆盖

从**单一网关**即可让不同通道运行不同模型和人格：例如在 `#daily` 用廉价快速模型、在 `#dev` 用前沿模型加专属提示词。做法是在 `gateway-config.yaml` 中为平台配置 `channel_overrides`（通道覆盖）。这类覆盖是网关特有的，不影响 CLI 会话。

## 5.6 relay 连接器

**relay（中继）** 不是聊天平台本身，而是一套**连接器系统**（`gateway/relay/`，官方标记为 experimental/实验性）。它通过外部连接器接管平台的凭据，前端接入 Discord、Telegram、Slack、WhatsApp 等平台。其能力（媒体、原生审批/澄清提示、回复、线程、输入状态、流式）在握手（handshake）时按连接器协商，而非像原生平台那样固定。

适用场景：当平台凭据由外部服务持有、或希望复用 Hermes 之外的连接基础设施时，用 relay 代替原生接入。详见[集成章节](../hermes-agent-integration/README.md)之外的官方 relay 文档。

## 5.7 安全与操作要点

- **token 锁定**：网关可用 token 锁定机制防止误用/越权（示例/需验证——官方文档提及 token locks）
- **服务管理**：网关可注册为持久化服务（system service），崩溃自动重启
- **工具通知**：网关支持工具进度通知、澄清问题（clarify questions）等会话内交互
- **后台会话**：支持后台会话（background sessions）与网关代理缓存（gateway agent cache）

| 上一章 | 目录 | 下一章 |
|--------|------|--------|
| [04 配置体系](./04-configuration.md) | [README](./README.md) | [06 工具与工具集](./06-tools-toolsets.md) |
