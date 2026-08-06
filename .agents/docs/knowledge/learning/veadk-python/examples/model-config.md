---
id: veadk-python-model-config
title: 08 - 模型配置示例
source: d:\AI\.chaos\libs\veadk-python\examples\08_model_config\main.py
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
stage: E
---


# 模型配置示例 (Model Configuration)

## 1. 示例功能介绍

本示例展示如何在 Agent 级别配置模型，包括模型选择、降级 fallback 和额外请求参数。VeADK 采用"每个 Agent 独立配置"的设计理念，无需全局配置——不同的 Agent 可以使用不同的模型、不同的参数，满足各种场景需求。

**演示的核心能力**：
- `model_name` 参数：指定主模型和 fallback 模型列表
- `model_extra_config`：传递额外的请求参数（如禁用 thinking）
- 模型自动降级机制：主模型失败时自动尝试备用模型
- 按 Agent 粒度覆盖默认模型配置

---

## 2. 核心代码展示

完整代码位于 [file:///d:/AI/.chaos/libs/veadk-python/examples/08_model_config/main.py](file:///d:/AI/.chaos/libs/veadk-python/examples/08_model_config/main.py)：

```python
import asyncio

from veadk import Agent, Runner


async def main() -> None:
    agent = Agent(
        name="resilient_agent",
        instruction="You are a concise assistant. Answer in one short sentence.",
        model_name=["doubao-seed-1-6-250615", "deepseek-v3-2-251201"],
        model_extra_config={"extra_body": {"thinking": {"type": "disabled"}}},
    )

    runner = Runner(agent=agent, app_name="model_config")

    answer = await runner.run(
        messages="用一句话解释什么是负载均衡。",
        session_id="demo-session",
    )
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 3. 关键代码行逐行解释

| 行号 | 代码 | 解释 |
|------|------|------|
| 37 | `model_name=["doubao-seed-1-6-250615", "deepseek-v3-2-251201"],` | **模型列表与 Fallback**：<br>- 传入**列表**而非单个字符串，表示"主备模式"<br>- 第一个模型 `doubao-seed-1-6-250615` 是主模型，优先使用<br>- 如果主模型调用失败（如配额耗尽、服务不可用、超时），自动降级到下一个模型 `deepseek-v3-2-251201`<br>- 可以配置多个 fallback，按顺序依次尝试<br>- 如果只传字符串（如 `model_name="doubao-seed-1-6-250615"`），则无 fallback，失败直接报错 |
| 39 | `model_extra_config={"extra_body": {"thinking": {"type": "disabled"}}},` | **额外请求配置**：<br>- `model_extra_config` 是一个字典，会被合并到每次发给模型 API 的请求体中<br>- 这里禁用了模型的"thinking"（思维链）输出，可以获得更快、更便宜的响应<br>- 不同模型支持的 extra_body 参数不同，请参考对应模型的文档 |
| 33-40 | `agent = Agent(...)` | 注意：这里没有配置 `model_provider`、`model_api_base`、`model_api_key`——这些默认从环境变量读取（如 `ARK_API_KEY`）。如果需要为单个 Agent 单独指定 API Key 或接入点，可以添加：<br>- `model_provider="ark"`（或其他 provider）<br>- `model_api_base="https://..."`<br>- `model_api_key="sk-..."` |

### 🔑 三个模型配置旋钮详解

| 参数 | 类型 | 作用 |
|------|------|------|
| `model_name` | `str \| list[str]` | 指定模型名称。列表形式启用 fallback 降级 |
| `model_provider` | `str` | 模型提供商（如 `"ark"`, `"openai"`），默认从环境变量推断 |
| `model_api_base` | `str` | API 端点地址，用于私有部署或第三方兼容接口 |
| `model_api_key` | `str` | 单独为该 Agent 指定 API Key，不使用环境变量 |
| `model_extra_config` | `dict` | 合并到每个请求体中的额外参数 |

### 💡 Fallback 降级机制工作流程

```
用户请求
   ↓
尝试主模型 (model_name[0])
   ├─ 成功 → 返回结果
   └─ 失败 → 尝试下一个模型 (model_name[1])
              ├─ 成功 → 返回结果
              └─ 失败 → 继续尝试下一个...
                           └─ 所有模型都失败 → 抛出异常
```

**什么时候会触发 fallback？**
- 模型返回 5xx 服务端错误
- API 配额耗尽（429 错误，符合条件时）
- 请求超时
- 模型不存在或无权限

### 💡 model_extra_config 常见用途

1. **禁用思维链**：`{"extra_body": {"thinking": {"type": "disabled"}}}` - 更快、更省 token
2. **设置温度**：`{"temperature": 0.1}` - 低温度适合结构化输出、事实性问答
3. **设置最大输出 token**：`{"max_tokens": 100}` - 控制输出长度
4. **启用 JSON 模式**（配合 output_schema 时通常自动设置）

---

## 4. 运行前置条件

### 环境要求
- Python 3.10+
- 已安装 veadk-python 包

### API Key 配置
需要配置至少一个模型提供商的 API Key：

```bash
# 火山引擎方舟（Ark）- 用于访问 doubao 系列模型
$env:ARK_API_KEY = "your-ark-api-key"

# 如需使用 DeepSeek fallback，可能需要配置 DEEPSEEK_API_KEY（或根据 provider 配置）
```

请参考 `.env.example` 了解所有支持的环境变量。

### 依赖安装
```bash
pip install veadk-python
```

---

## 5. 预期运行效果/输出

运行命令：
```bash
cd 08_model_config
python main.py
```

**预期执行流程**：
1. Agent 使用 doubao-seed-1-6 模型尝试回答
2. 由于禁用了 thinking，模型直接输出答案，无思维链
3. 如果 doubao 模型不可用，自动降级到 deepseek-v3
4. 返回一句话解释负载均衡

**预期输出**（示例）：
```
负载均衡是一种将网络流量或工作负载均匀分配到多个服务器上的技术，以避免单点过载、提高系统可用性和响应速度。
```

你可以尝试：
1. 将主模型名改为一个不存在的模型名，观察 fallback 到备用模型的效果
2. 移除 `model_extra_config` 中的 thinking 禁用，观察输出变化（如果模型支持思维链）
3. 调整 `temperature` 等参数观察输出创造性的变化

---

## 6. 延伸学习

- 上一示例：[结构化输出示例](structured-output.md)
- 下一步学习：[A2UI示例](a2ui.md) - 学习 Agent 驱动 UI 的可视化交互
- 相关文档：
  - [模型配置模块详解](../modules/models.md)
  - [配置说明](../getting-started/configuration.md)
  - [最佳实践](../faq/best-practices.md)
