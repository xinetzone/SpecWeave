# 代码模板说明（Task4 / Task5）

> 本目录提供 Task4、Task5 的**起始代码模板**。
> 不是完整答案，是"填空文件"——关键逻辑留给你自己写。

---

## 一、文件说明

| 文件 | 用途 |
|---|---|
| `agent.py` | 智能体主程序模板（复制到项目根目录使用） |
| `.env.example` | 环境变量模板（复制为 `.env` 后填写真实密钥） |

---

## 二、核心设计：三区划分

模板**故意不是完整代码**。我们把内容分成三个区：

### 🟢 预填区（不用管）

```python
import datetime, json, os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

def get_client() -> OpenAI: ...      # 完整的客户端创建逻辑
def ask_simple(question) -> str: ...  # 完整的简单问答
def main() -> None: ...               # 完整的命令行入口
```

**为什么帮你写好？** 这些是样板代码，和 Task4/Task5 的学习目标无关。
让你在这里卡住，属于浪费时间。

### 🔴 留空区（必须自己写）

| 函数 | 对应任务 | 你要写什么 |
|---|---|---|
| `get_time()` | Task5 | 返回当前时间字符串（约 1 行） |
| `calculator()` | Task5 | AST 安全求值（禁止用 `eval`） |
| `build_tools()` | Task5 | 构造工具描述列表 |
| `call_tool()` | Task5 | 工具分发逻辑 |
| `ask()` | Task4+5 | **核心：完整的 Agent Loop** |

这些正是本任务要教给你的能力。搜 `TODO` 可以定位全部位置（共 13 处标记）。

### 🟡 引导区（给你方向，不给答案）

每个留空函数都有：
- 完整的 **docstring**（说明这个函数该做什么）
- **具体提示**（用什么 API、注意什么坑）
- **手册章节引用**（照着手册做就行）

例如 `calculator()` 的提示里明确写了：

> ⚠️ 禁止使用 eval()！必须用 ast 模块安全求值
> 原因：eval 会执行任意代码，有人问它 `__import__('os').system('rm -rf /')` 就完蛋了

**为什么给提示不给答案？** 因为"照着提示自己写出来"和"抄一遍"是两种不同的学习。
前者你会记住那个坑，后者过两天就忘了。

---

## 三、怎么用

### 步骤 1：复制到项目根目录

```bash
cp templates/agent.py .
cp templates/.env.example .
```

### 步骤 2：配好 `.env`

```bash
cp .env.example .env
# 编辑 .env，填入你的真实密钥
```

> 💡 模板做了**延迟初始化**：即使 `.env` 还没配好，`import agent` 也不会崩。
> 你可以先写代码、先做测试，最后再配密钥。

### 步骤 3：先跑通 `ask_simple`

```bash
python agent.py
```

`ask_simple()` 已经实现了，你应该能直接对话。**先确认这一步能跑通**，再往下做。

> 如果你在 Task4 阶段，可以暂时把 `ask()` 的最后一行改成 `return ask_simple(question)`，
> 这样整体流程就能跑通。等做 Task5 时再改回来实现真正的工具循环。

### 步骤 4：逐个实现 TODO

```
搜索 TODO → 实现一个 → 运行测试 → 确认没问题 → 下一个
```

**不要一次写完所有 TODO 再测试。** 出了错你会很难定位是哪个函数的问题。

### 步骤 5：对照手册

| 函数 | 手册位置 |
|---|---|
| `get_time()` / `calculator()` | `handbook/task-5-tools.md` 步骤 1 |
| `build_tools()` / `call_tool()` | `handbook/task-5-tools.md` 步骤 2 |
| `ask()` | `handbook/task-5-tools.md` 步骤 3 |

---

## 四、自检清单

- [ ] `python -m py_compile agent.py` 通过（语法没错）
- [ ] `import agent` 不报错（即使没配 `.env`）
- [ ] `ask_simple("你好")` 能正常回答问题
- [ ] `get_time()` 返回格式正确的时间字符串
- [ ] `calculator("123 * 456")` 返回 `"56088"`
- [ ] `calculator("1 + 1")` 不会因为 `eval` 而执行恶意代码
- [ ] `ask("现在几点")` 会触发工具调用（而不是让模型瞎猜）
- [ ] 搜索 `TODO` 已经全部消除

---

## 五、常见问题

| 现象 | 说明 |
|---|---|
| 运行后显示 `[未实现] xxx 还没实现` | 正常！说明你还没写那个函数，按提示去实现 |
| `ValueError: 未配置 LLM_API_KEY` | 检查 `.env` 是否存在、密钥是否填了 |
| `NotImplementedError` 在 `ask()` 里 | 见"步骤 3"的临时方案：先调用 `ask_simple()` |
| 模型不调用工具、直接瞎编时间 | `build_tools()` 里的 `description` 写得不够明确 |
| 目录里多了个 `__pycache__/` | **正常，不要提交**——见下方 ⬇️ |

### 关于 `__pycache__/`（学生最常问）

只要你 `import agent` 或运行过 `agent.py`，Python 就会自动生成
`__pycache__/agent.cpython-3xx.pyc`。它是**编译缓存**，不是你写的代码。

| 问题 | 答案 |
|---|---|
| 要不要交？ | **不要**。它每次运行都会重新生成，交它没有意义 |
| 要删吗？ | 可以删，删了下次运行会再生成，不影响任何东西 |
| 为什么 `git status` 看不到它？ | 因为 Task1 步骤 5 复制的 [`.gitignore`](../starters/.gitignore) 已排除它 |
| 我的 `git status` 里出现它了 | 说明 `.gitignore` 没复制成功，回到 Task1 步骤 5 重做 |

> ⚠️ **如果你在 `git status` 里看到 `__pycache__/`，这是一个信号**——
> 它说明你的 `.gitignore` 没生效。而同一个文件负责排除 **`.env`**（你的 API 密钥），
> 所以这个问题**必须马上修**，不要拖。先跑 `git status --short` 确认 `.env` 是否也露出来了。

---

## 六、想自己从头写？

完全可以。模板只是**降低起步成本**，不是强制要求。

如果你选择从空白文件开始，建议至少参考模板的这两处：
1. **`get_client()` 的延迟初始化** —— 避免"没配密钥就崩溃"的体验问题
2. **`main()` 的异常处理** —— 把 `NotImplementedError` 单独捕获，方便调试

> 评估时**不检查你是否用了模板**，只看最终代码是否理解正确（Task7 会现场抽问）。
