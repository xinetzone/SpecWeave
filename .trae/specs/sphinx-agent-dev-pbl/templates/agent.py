"""AI 智能体 —— 学生起始模板（Task4 / Task5）

================================ 使用说明 ================================
这个文件是给你「填空」的，不是给你抄的。

【已经帮你写好的】
  - 依赖导入、API 客户端初始化、命令行交互入口
  - 这些和本任务的学习目标无关，卡在这里纯属浪费时间

【需要你自己写的】——搜索 `TODO` 就能找到全部位置
  - Task4：ask() 函数的核心逻辑
  - Task5：get_time() / calculator() 两个工具 + ask() 的工具循环

【怎么用】
  1. 把本文件复制到你的项目根目录，改名为 agent.py
  2. 按 TODO 顺序逐个实现
  3. 每实现一个就运行一次 `python agent.py` 验证
  4. 手册对应章节：handbook/task-4-agent-loop.md、handbook/task-5-tools.md

【不要做的事】
  - 不要一次把所有 TODO 都写完再测试（出了问题很难定位）
  - 不要把 API Key 直接写在这个文件里（用 .env）
==========================================================================
"""

import datetime
import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------------------------------------------------------
# 配置区（已写好，不用改）
# ---------------------------------------------------------------------------
load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

_client: OpenAI | None = None


def get_client() -> OpenAI:
    """获取 API 客户端（延迟创建）。

    为什么要延迟创建？
      如果在这里直接 `client = OpenAI(...)`，那么当 .env 还没配好时，
      `import agent` 就会直接抛 OpenAIError，你会看到一个很难懂的报错。
      改成函数后，只有真正要调用 API 时才会检查配置 --
      这样你可以先写代码、先跑测试，最后再配密钥。

    Returns:
        配置好的 OpenAI 客户端。

    Raises:
        ValueError: 当 .env 中的 LLM_API_KEY 未配置时。
    """
    global _client
    if not os.getenv("LLM_API_KEY"):
        raise ValueError(
            "未配置 LLM_API_KEY。请检查：\n"
            "  1. 项目根目录下有 .env 文件吗？（可从 .env.example 复制）\n"
            "  2. .env 里 LLM_API_KEY= 后面填了你的密钥吗？"
        )
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
        )
    return _client


# ===========================================================================
# Task5 —— 工具函数
# 提示：先跳过这一节，把下面的 ask_simple() 跑通，再回来做工具
# ===========================================================================


def get_time() -> str:
    """获取当前的日期和时间。

    TODO(Task5-1): 实现这个函数，返回当前时间字符串，格式 "YYYY-MM-DD HH:MM:SS"。

    提示：
      - 用 datetime.datetime.now()
      - 用 .strftime("%Y-%m-%d %H:%M:%S") 格式化
      - 参考手册：handbook/task-5-tools.md 步骤 1

    Returns:
        格式为 "YYYY-MM-DD HH:MM:SS" 的当前时间字符串。
    """
    # TODO: 在这里写你的实现（大约 1 行代码）
    raise NotImplementedError("get_time 还没实现 —— 见手册 Task5 步骤 1")


def calculator(expression: str) -> str:
    """计算一个数学表达式。

    TODO(Task5-2): 实现这个函数，计算传入的算式并返回结果字符串。

    要求（很重要，不是随便算算就行）：
      - 输入的 expression 是字符串，例如 "123 * 456"
      - 返回结果也必须是字符串
      - ⚠️ 禁止使用 eval()！必须用 ast 模块安全求值
        原因：eval 会执行任意代码，有人问它
        "__import__('os').system('rm -rf /')" 就完蛋了

    提示：
      - 用 ast.parse(expression, mode="eval") 解析
      - 写一个递归函数处理 ast.Constant 和 ast.BinOp
      - 支持的运算符：+ - * /
      - 出错时返回 "计算失败: xxx" 而不是抛异常
      - 完整参考实现见手册：handbook/task-5-tools.md 步骤 1

    Args:
        expression: 四则运算表达式，例如 "123 * 456"。

    Returns:
        计算结果字符串，例如 "56088"。
    """
    # TODO: 在这里写你的实现
    # 提示：你需要一个辅助函数来递归求值 AST 节点
    raise NotImplementedError("calculator 还没实现 —— 见手册 Task5 步骤 1")


# ---------------------------------------------------------------------------
# Task5 —— 告诉大模型有哪些工具可用
# ---------------------------------------------------------------------------


def build_tools() -> list[dict[str, Any]]:
    """构造传给大模型的工具描述列表。

    TODO(Task5-3): 返回一个列表，描述 get_time 和 calculator 两个工具。

    每个工具的形状如下（OpenAI 兼容格式）：
        {
            "type": "function",
            "function": {
                "name": "函数名",
                "description": "什么时候该用这个工具（写清楚！）",
                "parameters": {
                    "type": "object",
                    "properties": {...},
                    "required": [...],
                },
            },
        }

    ⚠️ description 写得好不好，直接决定模型会不会正确调用。
    请明确写出"当用户询问 X 时使用"。

    参考：handbook/task-5-tools.md 步骤 2

    Returns:
        工具描述列表。
    """
    # TODO: 在这里构造并返回工具列表
    raise NotImplementedError("build_tools 还没实现 —— 见手册 Task5 步骤 2")


def call_tool(name: str, arguments: dict[str, Any]) -> str:
    """根据工具名执行对应工具，返回结果字符串。

    TODO(Task5-4): 实现工具分发。

    提示：
      - 用 if/elif 或字典映射 {函数名: 函数对象}
      - 找不到工具时返回 "未知工具: xxx"

    参考：handbook/task-5-tools.md 步骤 2

    Args:
        name: 工具函数名。
        arguments: 从大模型解析出的参数字典。

    Returns:
        工具执行结果，统一转成字符串。
    """
    # TODO: 在这里实现工具分发
    raise NotImplementedError("call_tool 还没实现 —— 见手册 Task5 步骤 2")


# ===========================================================================
# Task4 —— 智能体主循环
# ===========================================================================


def ask_simple(question: str) -> str:
    """【Task4 起步版】不带工具的最简问答。

    已经实现好了，作为你的起点。
    先确认这个能跑通，再去实现下面的 ask()。

    Args:
        question: 用户的问题。

    Returns:
        智能体的回答文本。
    """
    if not os.getenv("LLM_API_KEY"):
        raise ValueError(
            "未配置 LLM_API_KEY。请检查：\n"
            "  1. 项目根目录下有 .env 文件吗？（可从 .env.example 复制）\n"
            "  2. .env 里 LLM_API_KEY= 后面填了你的密钥吗？"
        )

    response = get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是一个乐于助人的助手，回答请简洁。"},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


def ask(question: str, max_turns: int = 5) -> str:
    """【Task5 完整版】带工具调用的智能体主循环。

    TODO(Task4-5): 实现完整的 Agent Loop。

    循环逻辑（务必理解后再写，不要照抄）：
        1. 把系统提示 + 用户问题放进 messages 列表
        2. 循环最多 max_turns 次：
           a. 调用 client.chat.completions.create(...)，传入 tools=build_tools()
           b. 取出 msg = response.choices[0].message
           c. 【关键】如果 msg.tool_calls 为空 → 直接 return msg.content
           d. 如果不为空 → 把 msg 追加进 messages，
              然后对每个 tool_call：
                - 解析 call.function.name 和 call.function.arguments
                  （arguments 是 JSON 字符串，要 json.loads）
                - 用 call_tool() 执行
                - 把结果以 {"role": "tool", "tool_call_id": call.id,
                  "content": 结果} 的形状追加进 messages
           e. 回到循环顶部，让模型看到工具结果后继续思考
        3. 超过 max_turns 还没结束 → 抛 RuntimeError

    ⚠️ max_turns 是安全阀，不是可有可无的参数。
    没有它，模型可能陷入"调工具 → 还不满意 → 再调"的死循环，烧光你的额度。

    参考：handbook/task-5-tools.md 步骤 3

    Args:
        question: 用户的问题。
        max_turns: 最大循环轮数，防止无限循环。

    Returns:
        智能体的最终回答文本。

    Raises:
        ValueError: 当 API 密钥未配置时。
        RuntimeError: 当超过最大循环轮数时。
    """
    if not os.getenv("LLM_API_KEY"):
        raise ValueError(
            "未配置 LLM_API_KEY。请检查：\n"
            "  1. 项目根目录下有 .env 文件吗？（可从 .env.example 复制）\n"
            "  2. .env 里 LLM_API_KEY= 后面填了你的密钥吗？"
        )

    # TODO: 在这里实现完整的 Agent Loop
    #
    # 起始代码已经给你了：
    # messages = [
    #     {"role": "system", "content": "你是一个乐于助人的助手。需要实时信息或计算时请调用工具。"},
    #     {"role": "user", "content": question},
    # ]
    # 然后开始你的循环...

    raise NotImplementedError("ask 还没实现 —— 见手册 Task5 步骤 3")

    # 如果 Task4 只做到这里就结束了，可以暂时让 ask() 直接调用 ask_simple：
    # return ask_simple(question)


# ===========================================================================
# 命令行入口（已写好，不用改）
# ===========================================================================

def main() -> None:
    """启动交互式对话循环。"""
    print("智能体已启动，输入问题开始对话（输入 quit 退出）\n")
    while True:
        try:
            user_input = input("你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if user_input.lower() in {"quit", "exit", "退出"}:
            print("再见！")
            break
        if not user_input:
            continue

        try:
            print(f"智能体: {ask(user_input)}\n")
        except NotImplementedError as exc:
            print(f"[未实现] {exc}")
            print("提示：如果你刚开始做 Task4，可以先把 ask() 改成调用 ask_simple()\n")
        except Exception as exc:  # noqa: BLE001
            print(f"[出错] {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
