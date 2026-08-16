---
id: deepseek-harness-wiki-08
title: DeepSeek Harness Wiki - 模型配置与多模型支持
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
date: 2026-08-16
tags:
  - deepseek
  - agent
  - harness
  - model
  - configuration
  - provider
  - deepseek-v4
  - thinking
  - vision
category: learning
maturity: L1
---

# 08 模型配置与多模型支持

DeepSeek Harness 的设计哲学是「模型无关」——默认深度优化 DeepSeek V4 系列，但不绑定任何单一厂商。通过统一的模型抽象层，你可以无缝切换不同供应商的模型，甚至为不同任务配置专用模型。本章详细介绍 dsh 的模型配置体系。

## 默认 DeepSeek 模型配置

首次启动 dsh 时，系统会自动配置两个默认模型，无需手动填写任何参数即可使用。

### deepseek-v4-pro：旗舰 Agent 优化模型

`deepseek-v4-pro` 是 DeepSeek 专为 Agent 场景优化的旗舰模型，也是 dsh 的默认模型。

**默认参数配置：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| **上下文窗口** | 1,000,000 tokens | 1M 超长上下文，足以处理整个大型代码库 |
| **单次输出上限** | 256,000 tokens | 支持超长连贯输出，适合长文档生成或大规模重构 |
| **推理档位** | `high` | 深度思考模式，优先保证推理质量 |
| **工具调用优化** | 开启 | 针对工具调用格式做了专项优化，错误率更低 |
| **思考强度** | 支持 low/high/max 三档调节 | 根据任务需要动态调整思考深度 |

**适用场景：**
- 复杂代码重构、架构设计
- 多步骤长任务规划与执行
- 需要深度推理的调试问题
- 对准确性要求高的生产级任务
- 多 Agent 协作场景下的主控 Agent

### deepseek-v4-flash：快速省成本模型

`deepseek-v4-flash` 是速度更快、成本更低的轻量版模型，适合日常高频任务。

**默认参数配置：**

| 参数 | 默认值 | 说明 |
|------|--------|------|
| **上下文窗口** | 1,000,000 tokens | 与 Pro 版相同的上下文容量 |
| **单次输出上限** | 256,000 tokens | 同样支持长输出 |
| **推理档位** | `high` | 默认同样使用 high 档位，但响应速度更快 |
| **思考强度** | 支持 low/high/max 三档调节 |
| **相对速度** | ~3-5x | 比 Pro 版快 3 到 5 倍 |
| **相对成本** | ~1/5 | 成本约为 Pro 版的五分之一 |

**适用场景：**
- 日常代码补全、简单 bug 修复
- 文件浏览、代码搜索、快速问答
- 对成本敏感的批量任务
- 子 Agent 委派的简单子任务
- 快速原型验证、试验性任务

### 三档思考强度调节

无论是 Pro 还是 Flash，dsh 都支持三档思考强度（thinking effort），你可以在会话过程中随时切换：

| 档位 | 说明 | 典型场景 | Token 开销 |
|------|------|----------|------------|
| **low** | 快速响应，思考过程简短，直接给出答案 | 简单问答、代码补全、文件操作 | 低 |
| **high** | 默认档位，平衡思考深度与速度，有完整推理过程 | 日常编程、问题排查、大多数任务 | 中 |
| **max** | 极致深度思考，会进行多轮自我反思和验证，不惜 Token 成本也要给出最优解 | 复杂架构设计、疑难 bug 调试、高风险代码修改、数学/逻辑难题 | 高（可能是 high 的 2-3 倍） |

**切换方式：**
1. **UI 切换**：在会话界面右上角的模型选择器旁边，有思考强度下拉菜单，点击即可切换
2. **指令切换**：在对话中直接说「用 max 思考强度来做这个」或者「切到 low 档快速回答」
3. **配置文件**：在 `settings.yaml` 中为特定模型设置默认思考强度

思考强度的切换是即时生效的，不需要重启会话或重新加载模型。对于特别重要的任务，你可以先在 low 档快速探索方向，确认方向正确后再切到 max 档做最终实现。

## API Key 配置与凭证安全

模型配置的第一步是设置 API Key。dsh 在凭证安全方面做了专门设计，不会在界面或配置文件中暴露你的密钥。

### Settings → Models 配置界面

打开 Web UI 后，点击左下角的 **Settings** 齿轮图标，选择 **Models** 标签页，进入模型配置界面。

界面布局：
- 左侧是已配置的 Provider 列表，按供应商分组
- 右侧是选中 Provider 的详细配置，包括 API Key 输入框、模型列表、高级设置
- 顶部有 **Add provider** 按钮用于添加新供应商，**Add a custom provider** 用于添加自定义供应商

### API Key 脱敏显示机制

当你在界面输入 API Key 并点击保存后：
1. 真实密钥会立即被加密存储
2. 界面上只会显示一个脱敏的描述符，类似 `sk-****abcd` 或者 `DeepSeek API Key (stored)`
3. 即使你刷新页面、重启服务，也无法再从界面看到完整密钥
4. 如果需要更换 Key，直接输入新 Key 覆盖即可

这种设计避免了你的密钥被旁观者看到，也防止了在截图、屏幕共享时意外泄露密钥。

### .credentials.yaml 安全存储

所有 API Key 真实存储位置是 `~/.dsh/.credentials.yaml`，这是一个独立于其他配置的凭证文件。

**文件特性：**
- 文件权限自动设置为 `0600`（仅所有者可读写）
- 内容采用本地加密存储，不是明文
- 不会被 `--dump-config` 命令导出
- 不会出现在日志或错误信息中
- 与 `settings.yaml` 分离，分享配置时不会意外带上密钥

**文件结构示例（加密后）：**

```yaml
version: 1
credentials:
  deepseek:
    type: api_key
    ref: dsk_encrypted_abc123xyz...
  anthropic:
    type: api_key
    ref: sk_encrypted_def456uvw...
```

在 `settings.yaml` 中，模型配置只引用凭证 ID，不存储真实密钥：

```yaml
providers:
  deepseek:
    type: deepseek
    credentialRef: deepseek
    models:
      - id: deepseek-v4-pro
        # ... 其他模型参数
```

> **安全提示**：请妥善保管 `~/.dsh/.credentials.yaml` 文件，不要将其提交到版本控制系统或分享给他人。如果需要迁移配置，建议在新机器上重新输入 Key，而不是直接复制这个文件。

### 通过环境变量配置

除了在界面输入，你也可以通过环境变量提供 API Key，适合 CI/CD 或无头模式使用：

```bash
# DeepSeek
export DEEPSEEK_API_KEY=sk-xxx

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-xxx

# OpenAI
export OPENAI_API_KEY=sk-xxx
```

环境变量优先级高于 `.credentials.yaml` 中存储的 Key。

## 内置多 Provider 添加

dsh 预置了五大主流模型供应商的快速配置入口，点击 **Add provider** 即可看到：

| 内置 Provider | 配置项 | 备注 |
|---------------|--------|------|
| **Anthropic** | API Key | 自动加载 Claude 系列模型（Opus/Sonnet/Haiku） |
| **OpenAI** | API Key、Organization ID（可选） | 自动加载 GPT-4o、GPT-4 Turbo、o1 等模型 |
| **Bedrock** | AWS Access Key、Secret Key、Region | 通过 AWS Bedrock 调用 Claude、Llama 等模型 |
| **Azure** | API Key、Endpoint、Deployment ID | Azure OpenAI 服务，需要按部署配置模型 |
| **Vertex AI** | Google Cloud 凭证、Project ID、Location | Google Vertex AI，支持 Gemini 系列 |

### 添加 Anthropic 示例

1. 点击 **Add provider** → 选择 **Anthropic**
2. 在 API Key 输入框填入你的 Anthropic API Key（`sk-ant-...`）
3. 点击 **Fetch available models** 自动拉取可用模型列表
4. （可选）调整默认模型、上下文窗口、思考强度等参数
5. 点击 **Save** 保存

保存后立即生效，不需要重启。你可以在模型选择下拉菜单中看到新添加的 Claude 模型。

### 添加 Bedrock/Azure/Vertex 注意事项

对于云厂商的托管服务（Bedrock/Azure/Vertex），除了 API Key 外还需要注意：

- **Bedrock**：确保你的 AWS 账号已经在对应 Region 开通了想要使用的模型访问权限，并且 IAM 用户有 `bedrock:InvokeModel` 权限
- **Azure**：需要先在 Azure Portal 部署模型，获取 Deployment ID，Deployment 名称可以和模型名不同
- **Vertex AI**：需要先安装 Google Cloud CLI 并完成认证，或者创建 Service Account Key

## 自定义 Provider 配置步骤

如果你需要接入自建网关、第三方代理、或者 dsh 没有预置的小众模型供应商，可以使用 **Add a custom provider** 功能。

### 必填配置项

添加自定义 Provider 需要填写以下信息：

| 字段 | 说明 | 示例 |
|------|------|------|
| **Provider ID** | 小写字母、数字、连字符组成的唯一标识 | `my-gateway`、`local-llm`、`ollama` |
| **Base URL** | API 端点地址 | `https://api.my-gateway.com/v1`、`http://localhost:11434/v1` |
| **Protocol** | API 协议类型 | `openai-chat`（默认，兼容 OpenAI Chat Completions/Responses API）、`anthropic-messages` |
| **API Key** | 认证密钥（如果需要） | 留空表示无认证 |
| **Models** | 至少添加一个模型 | 见下文 |

### 添加模型

点击 **Add model** 添加模型，每个模型需要填写：

| 字段 | 说明 |
|------|------|
| **Model ID** | 模型在 API 中的 ID，会直接传给 provider |
| **Display name** | 在 UI 中显示的名称（可选，默认用 Model ID） |
| **Context window** | 上下文窗口大小（tokens） |
| **Max output tokens** | 单次输出上限（tokens） |
| **Capabilities** | 模型能力：文本输入、图像输入、工具调用、推理等 |
| **Default thinking effort** | 默认思考强度 |

### Fetch available models 自动拉取

如果你的自定义 Provider 兼容 OpenAI 格式，可以点击 **Fetch available models** 按钮，dsh 会自动调用 `/models` 接口拉取模型列表，并尝试自动填充上下文窗口等参数。你只需要检查确认即可，不用手动一个个添加。

### 配置示例：接入 Ollama 本地模型

以 Ollama 为例，演示如何添加本地运行的模型：

1. 确保 Ollama 已启动，并且已经拉取了模型（比如 `ollama pull qwen2.5-coder:32b`）
2. 点击 **Add a custom provider**
3. 填写配置：
   - Provider ID: `ollama`
   - Base URL: `http://localhost:11434/v1`
   - Protocol: `openai-chat`
   - API Key: 留空（Ollama 默认不需要认证）
4. 点击 **Fetch available models**，会自动列出所有本地已拉取的模型
5. 调整每个模型的上下文窗口等参数（Ollama 默认可能返回 4k，需要手动改成实际大小）
6. 点击 **Save** 保存

配置完成后，你就可以像使用云模型一样使用本地 Ollama 模型了，所有工具调用、子 Agent、Trajectory 等功能完全一致。

## 视觉模型配置注意事项

dsh 支持多模态模型的图像输入，但出于安全和兼容性考虑，默认添加的模型（包括自定义 Provider 拉取的模型）都按纯文本处理。如果模型支持视觉，需要手动开启。

### 开启视觉输入

在 `~/.dsh/settings.yaml` 中找到对应模型的配置，添加 `input: [text, image]` 字段：

```yaml
providers:
  openai:
    credentialRef: openai
    models:
      - id: gpt-4o
        displayName: GPT-4o
        contextWindow: 128000
        maxOutputTokens: 16384
        input: [text, image]  # 添加这一行开启视觉
        capabilities:
          - tool_use
          - thinking
```

修改后需要重启 dsh 服务才能生效。

### 视觉使用方式

开启后，你可以通过以下方式向 Agent 发送图片：
1. **拖拽上传**：直接将图片文件拖入输入框
2. **粘贴图片**：从剪贴板粘贴截图（Ctrl+V / Cmd+V）
3. **引用本地文件**：说「看一下这个截图 ./screenshot.png」
4. **网页图片**：提供图片 URL，Agent 可以通过浏览器工具获取

### 视觉使用注意事项

1. **Token 消耗**：图片会消耗大量 Token（一张 1024x1024 图片约消耗 1000+ tokens），注意成本
2. **隐私安全**：图片会被发送给模型提供商，不要上传敏感图片
3. **模型支持**：不是所有模型都支持视觉，确保你使用的模型确实有多模态能力，否则请求会失败
4. **工具调用兼容性**：视觉输入和工具调用可以同时使用，Agent 可以看图片然后调用工具处理

## V4 Pro 与 Harness 协同

DeepSeek V4 Pro 是专门为 Harness 这类 Agent 框架优化的模型，与 dsh 有深度协同。

### 为什么 V4 Pro 是默认选择

1. **工具调用精度**：V4 Pro 在工具调用格式上做了专项训练，工具调用参数错误率比通用模型低 60% 以上
2. **长上下文稳定性**：在 1M 上下文窗口内，即使接近满窗口，工具调用和推理质量也不会明显下降
3. **Agent 专用能力**：原生支持计划、目标管理、子 Agent 委派等 Agent 场景，不需要在提示词中反复强调格式
4. **思考模式适配**：三档思考强度与模型内部的推理深度控制精准对应，不是简单的「多生成一点 CoT」
5. **错误自修复**：当工具调用出错或返回意外结果时，V4 Pro 能更好地理解错误并自我纠正，而不是陷入死循环

### Minimal 模式用于 Code Agent 基准测试

在做模型评测或对比时，推荐使用 Minimal 模式 + V4 Pro 的组合：

- **Minimal 模式**只提供两个工具：持久化 `bash` 和 `str_replace_editor`（文件编辑），没有其他额外能力
- 这是 SWE-bench、HumanEval 等标准 Code Agent 基准测试使用的标准工具集
- 可以排除工具差异带来的干扰，公平对比不同模型的真实代码能力
- dsh 会自动记录完整的工具调用序列和结果，可以直接导出为基准测试格式

**启动 Minimal 模式：**

```bash
npx @deepseek-ai/dsh web --profile minimal
```

或者在 Creator 模式中切换 preset。

## OpenAI Responses API 与 Codex 适配

dsh 原生支持 OpenAI Responses API，这也是它能无缝兼容 Codex 的基础。

### Responses API 原生支持

传统 OpenAI 模型使用 Chat Completions API，而 Codex 和新一代模型推荐使用 Responses API。dsh 的模型抽象层同时支持两种协议：

- **openai-chat**：Chat Completions API，兼容 GPT-4 等旧模型
- **openai-responses**：Responses API，原生支持 Codex、GPT-4o 等新特性

当你添加 OpenAI Provider 时，dsh 会自动为支持 Responses API 的模型使用新协议，不需要手动配置。

Responses API 的优势：
- 原生支持多轮工具调用的状态管理
- 内置推理内容（reasoning）分离
- 更好的流式输出控制
- 支持 Web 搜索、代码解释器等内置工具（虽然 dsh 不依赖这些）

### Codex 一键配置

dsh 提供了一键配置 Codex 的脚本，不需要手动添加自定义 Provider：

```bash
npx @deepseek-ai/dsh setup-codex
```

脚本会自动：
1. 检测你是否已经安装并配置了 Codex CLI
2. 读取 Codex 的配置（包括 API Key）
3. 在 dsh 中添加 OpenAI Provider 并配置 Codex 模型
4. 设置适当的工具和参数默认值

配置完成后，你就可以在 dsh 中使用 Codex 模型，同时享受 dsh 的 Trajectory、插件、多模型切换等能力。下一章我们会详细介绍与 Codex/Claude Code 的生态互操作。

理解了模型配置，你就可以根据任务需要灵活切换模型，平衡质量、速度和成本。下一章我们将深入 dsh 的工具系统与 Capability Seam 抽象，理解为什么说「一次替换，全局生效」。

---

← [07 会话日志](07-session-log-observability.md) | → [09 工具系统](09-tools-capability-seam.md)
