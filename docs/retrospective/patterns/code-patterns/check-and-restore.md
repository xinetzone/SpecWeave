+++
id = "check-and-restore"
domain = "code"
layer = "code"
maturity = "L2"
validation_count = 1
reuse_count = 0
documentation_level = "detailed"
source = "forum-bot.py check_login bug fix"
+++

# 检查函数状态恢复模式

## 问题

在浏览器自动化脚本中，状态检查函数（如检查登录状态、检查元素存在）可能需要导航到特定页面执行检测。这种导航会**改变当前页面URL**，导致后续操作在错误的页面上执行。例如：`check_login()`导航到首页检测用户名，但后续代码期望在帖子详情页执行操作。

## 解决方案

遵循"查询与命令分离（CQS）"原则，检查函数应是纯读操作。如果检测过程中不可避免需要导航，则必须：
1. 执行前保存当前状态（URL/DOM状态）
2. 先尝试在当前页面检测（不导航）
3. 如果必须导航，检测完成后自动恢复原状态

## 代码

```python
def check_something(page) -> bool:
    """检查某状态，检测前后不改变页面URL。"""
    saved_url = page.url  # 1. 保存当前状态

    def _detect_in_current_page():
        """优先在当前页面检测，不导航"""
        result = page.evaluate("""() => {
            // 检测逻辑...
            return some_value;
        }""")
        return result

    # 2. 先尝试在当前页面检测
    if saved_url.startswith(BASE_URL):
        page.wait_for_timeout(500)
        result = _detect_in_current_page()
        if result is not None:
            return result

    # 3. 必须导航时，检测后恢复
    page.goto(CHECK_URL, wait_until="domcontentloaded", timeout=15000)
    result = _detect_in_current_page()

    # 4. 恢复原URL
    if page.url != saved_url and saved_url.startswith(BASE_URL):
        try:
            page.goto(saved_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(1000)
        except Exception:
            pass  # 恢复失败不影响检测结果

    return result is not None
```

## 关键设计原则

1. **纯读优先**：能在当前页面检测就不导航。例如Discourse页面中`window.Discourse.User.current()`在任何论坛页面都可用。
2. **保存-检测-恢复**：当必须改变状态才能检测时，三步走确保不污染调用方上下文。
3. **优雅降级**：恢复失败不应抛出异常，因为检测结果本身仍然有效。
4. **防御性编程**：检查`page.url != saved_url`避免不必要的重复导航。

## 反模式

```python
# ❌ 反模式：检查函数强制导航，污染调用方状态
def check_login_bad(page):
    page.goto(HOME_URL)  # 无条件导航！改变了当前页面
    username = page.evaluate("...")
    return username is not None
# 调用方在帖子页面 → check_login后变成首页 → 后续操作全部失败

# ✅ 正确模式：先就地检测，必要时恢复
def check_login_good(page):
    saved_url = page.url
    # 先尝试在当前页面检测...
    # 必须导航时检测完恢复...
```

## 推广场景

此模式不仅适用于浏览器自动化，还适用于：
- **数据库事务**：检查函数不应修改数据，如需修改应使用savepoint回滚
- **文件系统操作**：检查函数不应修改文件属性，如需临时文件应清理
- **API调用**：检查函数不应触发副作用（如发送消息、修改资源）
- **UI状态管理**：getter/selector不应dispatch action

## 来源

[forum-bot.py](file:///d:/spaces/SpecWeave/.agents/scripts/forum-bot.py) — `check_login()` 和 `_get_current_username()` Bug修复

> **关联模式**：
> - [dual-channel-tiered-logging](dual-channel-tiered-logging.md)
