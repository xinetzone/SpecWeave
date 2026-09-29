# Task6 — 元文档闭环：让智能体给自己写文档草稿【进阶】

> 时长：1–2 课时 | 难度：★★★★☆ | 前置：[Task5](task-5-tools.md) | 类型：**选做（进阶）**
> 🎯 **目标**：让智能体读取自己的代码，生成一段文档草稿；你审校后并入正式文档。
>
> ⭐ **这是全项目最有想法的部分**：文档不再只由人写，而是人机协作产出。

---

## 一、为什么做这个？（读 1 分钟）

前面 Task5 里，autodoc 已经做到了"代码 → 文档"的**单向自动抽取**。
但那只是把 docstring 搬过去，不能生成"这个功能该怎么用"这种**解释性内容**。

Task6 让智能体自己写：它读自己的代码，产出"功能介绍 + 使用示例"的草稿。
然后**你来审校**——因为 AI 写的草稿经常是错的。

> 🔑 **关键认知**：这个任务的产出不是"省了写文档的力气"，而是**让你看到 AI 会怎么误解你的代码**。
> 那些误解的地方，往往就是你自己也没想清楚的地方。

---

## 二、操作步骤

### 步骤 1：加一个"文档生成"工具

在 `agent.py` 里加：

```python
import inspect


def draft_doc(func_name: str) -> str:
    """生成指定函数的文档草稿。

    读取目标函数的源码与签名，交给大模型写出使用说明草稿。
    注意：草稿可能不准确，必须人工审校后才能并入正式文档。

    Args:
        func_name: 要生成文档的函数名，例如 "calculator"。

    Returns:
        Markdown 格式的文档草稿字符串。
    """
    target = AVAILABLE_FUNCTIONS.get(func_name)
    if target is None:
        return f"未找到函数: {func_name}"

    try:
        source = inspect.getsource(target)
    except OSError:
        source = "（无法读取源码）"

    prompt = (
        f"请为下面这个 Python 函数写一段中文使用说明，包含：\n"
        f"1. 一句话功能描述\n2. 参数说明\n3. 一个使用示例\n"
        f"用 Markdown 格式，不要输出代码以外的东西。\n\n"
        f"```python\n{source}\n```"
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
```

注册进 `AVAILABLE_FUNCTIONS`：

```python
AVAILABLE_FUNCTIONS = {
    "get_time": get_time,
    "calculator": calculator,
    "draft_doc": draft_doc,     # 新增
}
```

> 📸〔截图位 S6-1〕draft_doc 函数实现
> 文件名建议：shots/S6-1-文档生成工具.png
> 需要显示：draft_doc 函数代码

---

### 步骤 2：生成草稿

在项目根目录建 `docs/drafts/`，然后运行：

```bash
python -c "
from agent import draft_doc
print(draft_doc('calculator'))
" > docs/drafts/calculator-draft.md
```

或者直接在对话里：

```
你: 帮我给 calculator 生成文档草稿
```

> 📸〔截图位 S6-2〕生成的文档草稿内容
> 文件名建议：shots/S6-2-AI草稿.png
> 需要显示：AI 生成的 Markdown 草稿内容

---

### 步骤 3：审校并记录差异 ⭐（核心步骤）

新建 `docs/drafts/diff-notes.md`，逐条记录 AI 草稿的问题。

**要求至少 3 条具体差异**：

```markdown
# AI 草稿差异分析

> 说明：对比 `calculator-draft.md`（AI 生成）与最终并入正式文档的版本，
> 记录 AI 在哪里写错了、为什么错、我如何修正。

## 差异 1：AI 说参数可以传非字符串的表达式

- **AI 写法**：`calculator(1 + 2)` 直接传算式
- **问题**：实际函数签名要求 `expression: str`，传数值会报错
- **原因**：AI 没读懂类型注解，只看了函数名在猜
- **修正**：改为 `calculator("1 + 2")`

## 差异 2：AI 没有提到安全性设计

- **AI 写法**：只说"可以计算数学表达式"
- **问题**：完全没提为什么用 `ast` 而不是 `eval()`
- **原因**：AI 看不到设计意图，只能看到代码表面
- **修正**：补充一句"为避免代码注入，采用 AST 安全求值而非 eval"

## 差异 3：AI 编了一个不存在的错误类型

- **AI 写法**：说会抛出 `CalculationError`
- **问题**：代码里根本没有这个异常类，实际是返回"计算失败: xxx"字符串
- **原因**：AI 按常见模式推测，实际代码没这么写
- **修正**：改为"计算失败时返回提示字符串，不抛异常"
```

> 🔑 **重点**：注意差异 2——**AI 看不到你代码背后的设计意图**。
> 这是人类写文档不可替代的地方，也是这个任务最想让你体会到的。

> 📸〔截图位 S6-3〕diff-notes.md 差异分析
> 文件名建议：shots/S6-3-差异分析.png
> 需要显示：至少 3 条差异记录

---

### 步骤 4：审校后并入正式文档

把修正后的草稿并入 `usage.md` 或新建 `docs/snippets.md`，并加进 toctree。

**注意**：并入时要在文件里注明这是人机协作的产出：

```markdown
> 本节内容由 AI 生成初稿（见 `drafts/calculator-draft.md`），
> 经人工审校修正后并入（见 `drafts/diff-notes.md`）。
```

---

### 步骤 5：构建验证

```bash
sphinx-build -b html docs docs/_build/html
```

确认新页面能正常显示，且 CI 推送后也是绿的。

---

## 三、成本控制（如果额度有限）

调用大模型读代码+生成文档比较费 token。如果全班额度紧张，可以：

- **方案 A**：老师选一个函数，全班一起看 AI 草稿，各自写自己的差异分析
- **方案 B**：每组只对**一个**函数做元文档闭环，其他函数跳过
- **方案 C**：把草稿结果缓存下来复用，不重复生成

这些替代方案都被认可，不影响本任务的评分。

---

## 四、常见报错

| 报错 | 原因 | 解决 |
|---|---|---|
| `OSError: could not get source code` | 交互式环境里函数无源码文件 | 确保从 `.py` 文件运行，不用 `python` 交互模式 |
| AI 草稿完全跑偏 | 提示词不够明确 | 在 prompt 里更明确要求"只描述实际行为，不要推测" |
| 生成的 markdown 有代码块嵌套问题 | AI 输出格式不稳 | 人工调整即可——**这本身就是审校工作的一部分** |
| 草稿里出现英文 | 模型没遵循中文要求 | prompt 里强调"用中文"，或换模型 |

---

## 五、完成标志（自检）

- [ ] `draft_doc()` 函数已实现并注册
- [ ] 至少生成了一份文档草稿（`docs/drafts/` 下）
- [ ] `diff-notes.md` 存在，含 **≥3 条**具体差异（问题 + 原因 + 修正）
- [ ] 审校后的内容已并入正式文档，并注明来源
- [ ] 文档站构建成功，新页面可访问
- [ ] 我记录了"AI 草稿 vs 我的最终版"的差异

**对应验收标准**：TR-6.1（跨学科融合深度 ≥4分）、TR-6.2（差异记录 ≥3 条）

---

## 六、如果时间不够

Task6 是**选做**。跳过它不影响主干完成度（AC-1/2/3/5 全部可达）。
但如果你做了，你会得到两样东西：
1. 一个更高分的跨学科融合评价（AC-4）
2. 一次真实的"AI 会怎么误解我的代码"的体验——这个体验比分数更值钱

---
[← 上一个：Task5 工具调用](task-5-tools.md) | [返回手册目录](README.md) | [下一个：Task7 展示与反思 →](task-7-showcase.md)
