---
id: "longcat-agent-learning-wiki-02"
title: "Claude Code接入LongCat-2.0配置指南"
source: "https://mp.weixin.qq.com/s/ymt9W64FD5IwCDNeQFuheA"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/longcat-agent-learning-wiki/02-claude-code-integration.toml"
---

## 三、Claude Code接入LongCat-2.0配置指南

### 3.1 前置准备

在开始配置之前，需要确保：

- 已安装Claude Code（Anthropic官方CLI编程工具）
- 拥有LongCat平台的API Key

### 3.2 获取API Key

首先访问LongCat平台的API密钥管理页面：

```
https://longcat.chat/platform/api_keys
```

在该页面创建API Key，获取后妥善保存。这个Key将用于替代Claude Code默认的Anthropic API认证。

### 3.3 环境变量配置

在Claude Code的配置文件中，设置以下环境变量，将默认的Anthropic API端点指向LongCat服务：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "你的_LongCat_API_Key",
    "ANTHROPIC_BASE_URL": "https://api.longcat.chat/anthropic",
    "ANTHROPIC_MODEL": "LongCat-2.0",
    "ANTHROPIC_SMALL_FAST_MODEL": "LongCat-2.0",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "LongCat-2.0",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "LongCat-2.0",
    "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "131072",
    "CLAUDE_CODE_AUTO_COMPACT_WINDOW": "1000000",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
  },
  "permissions": {
    "allow": [],
    "deny": []
  }
}
```

### 3.4 配置参数详解

| 参数 | 值 | 说明 |
|------|------|------|
| `ANTHROPIC_AUTH_TOKEN` | 你的LongCat API Key | 替代Anthropic原生API Key，使用LongCat平台的认证令牌 |
| `ANTHROPIC_BASE_URL` | `https://api.longcat.chat/anthropic` | 将API请求重定向到LongCat服务器，使用Anthropic兼容接口 |
| `ANTHROPIC_MODEL` | `LongCat-2.0` | 指定使用的模型名称 |
| `ANTHROPIC_SMALL_FAST_MODEL` | `LongCat-2.0` | 轻量快速模型也指向LongCat-2.0（避免回退到其他模型） |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `LongCat-2.0` | 默认Sonnet级模型指向LongCat-2.0 |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `LongCat-2.0` | 默认Opus级模型指向LongCat-2.0 |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | `131072` | 最大输出token数（128K） |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | `1000000` | 自动压缩窗口大小（1M），匹配LongCat-2.0的最大上下文 |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | `1` | 禁用非必要网络流量，减少不必要的API调用 |

### 3.5 配置要点

1. **三个模型变量统一指向LongCat-2.0**：`ANTHROPIC_SMALL_FAST_MODEL`、`ANTHROPIC_DEFAULT_SONNET_MODEL`、`ANTHROPIC_DEFAULT_OPUS_MODEL` 都设置为 `LongCat-2.0`，确保所有场景下都使用同一模型，避免Claude Code内部切换模型时回退到Anthropic原生接口。

2. **上下文窗口匹配**：`CLAUDE_CODE_AUTO_COMPACT_WINDOW` 设置为 `1000000`（1M），与LongCat-2.0支持的最大上下文保持一致，充分利用其长上下文能力。

3. **禁用非必要流量**：`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` 设为 `1`，减少非必要的API调用，进一步降低token消耗。

### 3.6 验证配置

配置完成后，启动Claude Code，如果终端显示可以直接调用LongCat-2.0，说明配置成功。可以尝试发起一个简单的编程任务来验证模型是否正常工作。