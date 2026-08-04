---
id: "echobird-wiki-model-nexus"
title: "Model Nexus 模型中心"
source: "echobird-source-wiki-learning"
category: "learning"
tags: ["echobird", "model-nexus", "model-directory", "api-key"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Model Nexus 模型中心的数据模型（modelDirectory.json 的 providers/relays 结构）、API Key AES-256-GCM 加密、配置一次到处可用的实现机制、官方端点恢复"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 03 Model Nexus 模型中心

## 3.1 模型中心是什么

**Model Nexus（模型中心）** 是 EchoBird 的**统一模型数据中心**，管理所有模型服务的 API Key、Base URL、Model Name、Protocol。它被四大场景（App Manager / My AI Projects / Mother Agent / Local LLM）共享，实现"配置一次，到处可用"。

## 3.2 数据模型：modelDirectory.json

模型的"目录"定义在 `src/data/modelDirectory.json`，包含两类条目：

### providers（模型服务商）

每个服务商包含以下字段：

| 字段 | 含义 |
|------|------|
| `name` | 服务商显示名（如 "DeepSeek"） |
| `url` | 官网地址（点击 ↗ 打开） |
| `baseUrl` | OpenAI 协议 API 地址（预填到添加模型表单） |
| `anthropicUrl` | Anthropic 协议 API 地址（仅当服务商原生提供 `/v1/messages` 时填充） |
| `modelId` | 默认模型 id |
| `modelIds` | 可选，同一端点提供的多个模型 id（点击行显示快速选择下拉） |
| `region` | `cn` 或 `global`，控制中英文环境下默认排序 |

**主要服务商（18+ 个）**：小米、DeepSeek、MiniMax（EN/CN）、GLM 智谱、Z.ai、Kimi（CN/Global）、OpenAI、Google Gemini、优云智算、BytePlus、ERNIE 百度千帆、千问 AI 平台、Anthropic、xAI Grok、腾讯混元、Meta AI、Perplexity、阶跃星辰、Mistral、Cohere、Groq、Together AI、NVIDIA、Agnes AI、火山引擎。

### relays（API 中继/路由）

| 名称 | 说明 |
|------|------|
| OpenRouter | 聚合多家模型的中继 |
| WorldRouter | 推理中继 |
| B.ai | 中继 |
| CC Vibe | 中继（含 Claude/GPT 系列） |

> 中继与直连服务商的差别在于：中继通过单一路由聚合多家模型，适合一次接入多模型。

## 3.3 API Key 加密存储

`model_manager.rs` 负责模型 CRUD 与 API Key 加密，采用 **AES-256-GCM**：

- 加密密钥基于**机器指纹**派生（`get_machine_fingerprint()`），保证加密后的 Key 仅在本机可用
- 机器指纹来源：Windows 读注册表 `HKLM\SOFTWARE\Microsoft\Cryptography\MachineGuid`；macOS 读 `IOPlatformUUID`；Linux 读 `/etc/machine-id`
- 加密后的 Key 带 `enc:v1:` 前缀，写入 `~/.echobird/config/models.json`
- 这样 API Key 不会以明文落盘，且随机器指纹绑定，避免配置文件被拷贝后泄露

## 3.4 "配置一次，到处可用"的实现机制

1. **中心存储**：用户在 Model Nexus 添加模型服务商，配置写入 `~/.echobird/config/models.json`
2. **工具绑定**：通过 `tool_config_manager.rs` 将模型配置写入各工具的原生配置文件（如 `~/.codex/config.toml`、`~/.claude/settings.json`）
3. **协议代理**：Codex Proxy（127.0.0.1:53682）按请求实时读取 `~/.echobird/codex.json` 的当前模型配置，模型切换无需重启工具
4. **场景拾取**：App Manager / My AI Projects / Mother Agent / Local LLM 均从 Model Nexus 读取配置

## 3.5 官方端点恢复机制

`officialEndpoints.ts` 定义各工具的"官方端点"表（`OFFICIAL_ENDPOINTS`），供 App Manager 的 **Restore（恢复）** 按钮使用：

- 当用户把工具从第三方/代理 URL 改回厂商官方地址时，点击 Restore 恢复到官方端点
- 每个工具定义了 `baseUrl`、`anthropicUrl`、`protocol`（openai/anthropic）、`modelId`（仅新安装时作为种子，不覆盖用户已有模型）
- 例：`claudecode` 恢复为 `api.anthropic.com`（anthropic 协议）；`codex` 恢复为 `api.openai.com/v1`（openai 协议）
- **特殊处理**：Kimi 因有 .ai/.cn 双平台，无"官方端点"卡片；OpenClaw/Hermes/OpenCode 等社区开源工具无厂商官方 URL，恢复按钮隐藏

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [02 技术架构深度解析](./02-architecture.md) | [README](./README.md) | → [04 四大核心场景](./04-core-scenarios.md) |