# Task4 — 智能体最小循环实现

> 时长：2–3 课时 | 难度：★★★★☆ | 前置：[Task1](task-1-env.md)、[Task2](task-2-docs.md)
> 🎯 **目标**：写出一个能对话的最小智能体，跑通"输入 → 思考 → 输出"。

---

## 一、操作步骤

### 步骤 1：配置 API 密钥（先做这个！）

在**项目根目录**建两个文件：

**`.env`**（真实密钥，**绝不提交**）：
```bash
LLM_API_KEY=sk-你的真实密钥
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

> 💡 用国内模型也行（如混元、DeepSeek、通义），把 `LLM_BASE_URL` 和 `LLM_MODEL` 换成对应的即可。老师会告诉你用哪个。
>
> 🎁 **换厂商只改 `.env`，代码一个字都不用动。** 这是本项目最重要的一条工程习惯——**配置和代码分离**。
> 主流厂商和本地模型都提供"OpenAI 兼容端点"，所以同一份代码能连所有家：
>
> | 你想用 | `LLM_BASE_URL` | `LLM_MODEL` | 备注 |
> |---|---|---|---|
> | OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` | 需真实 Key |
> | DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | 老师会给 |
> | 通义千问 | 阿里云兼容端点 | `qwen-plus` | 老师会给 |
> | **本地 ollama** | `http://localhost:11434/v1` | `qwen2.5:7b` | **无需真实 Key**，`LLM_API_KEY` 随便填（如 `ollama`） |
>
> ⚠️ **不要为了"支持多家"去写一个 provider 抽象类**。厂商之间的差异已经被它们自己抹平了，你再写一层只是多一个出错的地方。**改环境变量就够了。**

**`.env.example`**（模板，**要提交**，给别人看该配哪些变量）：
```bash
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

> 🚨 **再确认一次** `.gitignore` 里有 `.env`。这一步做错，你的密钥几分钟内就会被爬虫扫走。

> 📸〔截图位 S4-1〕.env 与 .env.example 两个文件
> 文件名建议：shots/S4-1-密钥配置.png
> 需要显示：项目根目录下两个文件并列（.env 内容可打码）

---

### 步骤 2：写最小循环 `agent.py`

> 📦 **不想从空白文件开始？** 可以用模板：把 `templates/agent.py` 和 `templates/.env.example`
> 复制到项目根目录，然后只实现标了 `TODO` 的函数。
> 模板把 `get_client()`、`ask_simple()`、`main()` 这些样板代码写好了，
> 你只需要写**核心逻辑**（Task4 阶段先让 `ask()` 临时调用 `ask_simple()` 跑通流程即可）。
> 详见 [`templates/README.md`](../templates/README.md)。
>
> ⚠️ **用不用模板都不影响评分**——Task7 会现场抽问你代码为什么这么写。
> 用了模板却讲不清 `ask()` 的循环逻辑，一样拿不到分。

在项目根目录建 `agent.py`：

```python
"""一个最小的 AI 智能体实现。

本模块实现了 Agent Loop 的核心循环：
输入 -> 思考 -> (工具调用) -> 观察 -> 输出

示例:
    >>> from agent import ask
    >>> ask("你好")
    '你好！有什么可以帮你的吗？'
"""

import os

from dotenv import load_dotenv
from openai import OpenAI

# 从 .env 读取配置（不会把密钥写死在代码里）
load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
)

MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


def ask(question: str) -> str:
    """向智能体提一个问题，返回它的回答。

    Args:
        question: 用户的问题文本。

    Returns:
        智能体的回答文本。

    Raises:
        ValueError: 当 API 密钥未配置时。
    """
    if not os.getenv("LLM_API_KEY"):
        raise ValueError("未配置 LLM_API_KEY，请检查 .env 文件")

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个乐于助人的助手，回答请简洁。"},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("智能体已启动，输入问题开始对话（输入 quit 退出）\n")
    while True:
        user_input = input("你: ").strip()
        if user_input.lower() in {"quit", "exit", "退出"}:
            print("再见！")
            break
        if not user_input:
            continue
        print(f"智能体: {ask(user_input)}\n")
```

**几个要点**：
- `load_dotenv()` 把 `.env` 里的变量读进环境变量，代码里用 `os.getenv()` 取——**密钥永远不出现在代码里**
- 每个函数都写了 **docstring**（三引号里的说明）。这不是装饰：Task5 的 autodoc 会把它们自动抽成 API 文档，而且验收会检查它非空且有内容
- `if __name__ == "__main__":` 是 Python 惯例，让这个文件既能被 import，也能直接运行

> 📸〔截图位 S4-2〕agent.py 完整代码
> 文件名建议：shots/S4-2-agent代码.png
> 需要显示：编辑器中的 agent.py，含 docstring

---

### 步骤 3：运行测试

```bash
python agent.py
```

试试输入几个问题：
```
你: 你好
智能体: 你好！有什么可以帮你的吗？

你: 用一句话解释什么是智能体
智能体: 智能体是一个能感知环境并采取行动以达成目标的程序。

你: quit
再见！
```

> 📸〔截图位 S4-3〕智能体成功对话
> 文件名建议：shots/S4-3-运行成功.png
> 需要显示：终端中一问一答的对话记录

**截图留存**，这是 TR-4.1 的验收证据。

---

## 二、常见报错

| 报错 | 原因 | 解决 |
|---|---|---|
| `ValueError: 未配置 LLM_API_KEY` | `.env` 不存在或变量名拼错 | 检查 `.env` 在**项目根目录**，变量名是 `LLM_API_KEY` |
| `openai.AuthenticationError` | 密钥错误或过期 | 检查密钥；确认没有多余空格/引号 |
| `openai.APIConnectionError` | 网络不通或 base_url 错 | 检查网络；确认 `LLM_BASE_URL` 正确 |
| `openai.NotFoundError` / `model not found` | 模型名写错 | 找老师确认可用模型名 |
| `ModuleNotFoundError: No module named 'dotenv'` | 没装 python-dotenv | `pip install python-dotenv` |
| 中文乱码 | 终端编码 | Windows 下执行 `chcp 65001`；或设 `PYTHONIOENCODING=utf-8` |
| 卡住不动 | 网络超时 | 等待或检查网络；可加 `timeout=30` 参数 |

---

## 三、完成标志（自检）

- [ ] `.env` 有真实密钥，`.env.example` 有模板
- [ ] `.gitignore` 含 `.env`（**再查一遍**）
- [ ] `agent.py` 能运行，能一问一答
- [ ] 每个函数都有非空的 docstring
- [ ] 我截图了对话成功的画面

**对应验收标准**：TR-4.1（运行无异常、返回合理内容）

---

## 四、想一想（为 Task5 做准备）

现在你的智能体只能靠模型自己的知识回答。如果问它"现在几点"，它答不上来——因为模型不知道当前时间。

**怎么让它知道？** 这就是 Task5 要做的：给它工具。

---
[← 上一个：Task3 CI 部署](task-3-ci.md) | [返回手册目录](README.md) | [下一个：Task5 工具调用 →](task-5-tools.md)
