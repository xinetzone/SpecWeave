---
id: "karpathy-llm-coding-guidelines-code-examples"
title: "真实代码正反例"
category: learning
tags: [karpathy, llm, coding, agent, guidelines, examples, python, anti-patterns]
date: "2026-07-02"
status: stable
author: "multica-ai"
summary: "真实世界代码示例演示四条原则，每个示例展示LLM常见错误做法和正确做法，涵盖隐藏假设、过度抽象、顺手重构、模糊目标等场景。"
source: "https://github.com/multica-ai/andrej-karpathy-skills/blob/main/EXAMPLES.md"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/karpathy-llm-coding-guidelines/02-code-examples.toml"
---
# 真实代码正反例

以下是来自官方仓库的真实世界代码示例，演示四条原则的应用。每个示例展示了 LLM 常见的错误做法（❌）和正确做法（✅）。

---

## 原则一：编码前先思考（Think Before Coding）

### 示例 1：隐藏假设

**用户请求：** "添加导出用户数据的功能"

#### ❌ LLM 常见做法（错误假设）

```python
def export_users(format='json'):
    """Export all users to a file."""
    users = User.query.all()
    
    if format == 'json':
        with open('users.json', 'w') as f:
            json.dump([u.to_dict() for u in users], f)
    elif format == 'csv':
        with open('users.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'email', 'name'])
            writer.writeheader()
            writer.writerows([u.to_dict() for u in users])
    
    return f"Exported {len(users)} users"
```

**问题：**
- 假设要导出**所有**用户（分页呢？隐私问题呢？）
- 没问就假设了文件保存位置
- 假设了要导出哪些字段
- 没检查实际数据结构就假设了 CSV 字段名

#### ✅ 正确做法（呈现假设并提问）

```
在实现之前，我需要澄清几点：
1. **范围**：导出所有用户还是筛选后的子集？（有隐私影响）
2. **方式**：你说的"导出"是指：
   - 浏览器下载文件？
   - 后台任务+邮件通知？
   - 返回数据的 API 端点？
3. **字段**：哪些用户字段？（有些可能是敏感信息）
4. **数据量**：通常有多少用户？（影响实现方式）

最简单的方案：添加一个返回分页 JSON 的 API 端点。
文件导出需要更多信息。
你倾向于哪种方式？
```

---

### 示例 2：多种理解方式

**用户请求：** "让搜索更快"

#### ❌ LLM 常见做法（默默选择一种）

```python
# 不加询问就加了缓存、数据库索引、异步处理
@lru_cache(maxsize=1000)
async def search(query: str) -> List[Result]:
    # ... 200 行优化代码
```

#### ✅ 正确做法（列出选项）

```
"让搜索更快"可能有几种含义：
1. **更快的响应时间**（< 100ms 而不是 500ms）
   - 添加数据库索引
   - 缓存高频查询
   - 预计工作量：2 小时
2. **支持更多并发搜索**（吞吐量）
   - 添加 async/await
   - 连接池
   - 预计工作量：4 小时
3. **更快的感知速度**（用户体验）
   - 立即显示部分结果
   - 渐进式加载
   - 预计工作量：3 小时

当前典型查询耗时约 500ms。
哪种对你的场景最重要？
```

---

## 原则二：简约至上（Simplicity First）

### 示例 1：过度抽象

**用户请求：** "添加一个计算折扣的函数"

#### ❌ LLM 常见做法（过度工程化）

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Protocol, Union
from dataclasses import dataclass

class DiscountStrategy(ABC):
    @abstractmethod
    def calculate(self, amount: float) -> float:
        pass

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage: float):
        self.percentage = percentage
    
    def calculate(self, amount: float) -> float:
        return amount * (self.percentage / 100)

class FixedDiscount(DiscountStrategy):
    def __init__(self, fixed_amount: float):
        self.fixed_amount = fixed_amount
    
    def calculate(self, amount: float) -> float:
        return min(self.fixed_amount, amount)

@dataclass
class DiscountConfig:
    strategy: DiscountStrategy
    min_purchase: float = 0.0
    max_discount: float = float('inf')

class DiscountCalculator:
    def __init__(self, config: DiscountConfig):
        self.config = config
    
    def apply_discount(self, amount: float) -> float:
        if amount < self.config.min_purchase:
            return 0
        discount = self.config.strategy.calculate(amount)
        return min(discount, self.config.max_discount)

# 简单计算需要 30+ 行设置代码
```

#### ✅ 正确做法（简单直接）

```python
def calculate_discount(amount: float, percent: float) -> float:
    """Calculate discount amount. percent should be 0-100."""
    return amount * (percent / 100)

# 使用
discount = calculate_discount(100.0, 10.0)  # 减 $10
```

**什么时候加复杂度？** 只有当你真的需要多种折扣类型时再加。如果以后有这个需求，到时候再重构。

---

### 示例 2：添加未要求的功能

**用户请求：** "把用户偏好保存到数据库"

#### ❌ LLM 常见做法（多余功能）

```python
class PreferenceManager:
    def __init__(self, db, cache=None, validator=None):
        self.db = db
        self.cache = cache or InMemoryCache()
        self.validator = validator or DefaultValidator()
    
    def save(self, user_id: int, prefs: dict, 
             merge: bool = True, 
             validate: bool = True,
             notify: bool = False) -> bool:
        """Save preferences with optional merging, validation, and notifications."""
        
        if validate:
            errors = self.validator.validate(prefs)
            if errors:
                raise ValidationError(errors)
        
        existing = self.get(user_id) if merge else {}
        
        if merge:
            existing.update(prefs)
            prefs = existing
        
        self.db.execute(
            "UPDATE users SET preferences = ? WHERE id = ?",
            (json.dumps(prefs), user_id)
        )
        
        if self.cache:
            self.cache.set(f"prefs:{user_id}", prefs)
        
        if notify:
            self.notify_preference_change(user_id, prefs)
        
        return True
    
    def notify_preference_change(self, user_id: int, prefs: dict):
        # 又一个没人要求的 30 行功能
        pass
```

#### ✅ 正确做法（只做要求的事）

```python
def save_preferences(db, user_id: int, preferences: dict):
    """Save user preferences to database."""
    db.execute(
        "UPDATE users SET preferences = ? WHERE id = ?",
        (json.dumps(preferences), user_id)
    )
```

**以后需要时再加：** 缓存（性能有问题时）、验证（出现坏数据时）、合并（需求出现时）。

---

## 原则三：精确编辑（Surgical Changes）

### 示例 1：顺手重构

**用户请求：** "修复空邮箱导致验证器崩溃的 bug"

#### ❌ LLM 常见做法（改得太多）

```diff
  def validate_user(user_data):
-     # Check email format
-     if not user_data.get('email'):
+     """Validate user data."""
+     email = user_data.get('email', '').strip()
+     
+     # Validate email
+     if not email:
          raise ValueError("Email required")
-     
-     # Basic email validation
-     if '@' not in user_data['email']:
+     if '@' not in email or '.' not in email.split('@')[1]:
          raise ValueError("Invalid email")
      
-     # Check username
-     if not user_data.get('username'):
+     # Validate username
+     username = user_data.get('username', '').strip()
+     if not username:
          raise ValueError("Username required")
+     if len(username) < 3:
+         raise ValueError("Username too short")
+     if not username.isalnum():
+         raise ValueError("Username must be alphanumeric")
      
      return True
```

**问题：**
- 超出 bug 修复范围"改进"了邮箱验证
- 添加了没人要求的用户名验证
- 改了注释
- 加了 docstring

#### ✅ 正确做法（精确修改）

```diff
  def validate_user(user_data):
      # Check email format
-     if not user_data.get('email'):
+     email = user_data.get('email', '')
+     if not email or not email.strip():
          raise ValueError("Email required")
      
      # Basic email validation
-     if '@' not in user_data['email']:
+     if '@' not in email:
          raise ValueError("Invalid email")
      
      # Check username
      if not user_data.get('username'):
          raise ValueError("Username required")
      
      return True
```

**只改了：** 修复空邮箱处理的特定几行代码。

---

### 示例 2：风格漂移

**用户请求：** "给上传函数添加日志"

#### ❌ LLM 常见做法（把整个文件都格式化了）

```diff
- def upload_file(file_path, destination):
+ def upload_file(file_path: str, destination: str) -> bool:
+     """Upload file to destination with logging."""
+     logger.info(f"Uploading {file_path} to {destination}")
+     
      try:
-         with open(file_path, 'rb') as f:
-             data = f.read()
-         
-         response = requests.post(destination, files={'file': data})
-         
-         if response.status_code == 200:
-             return True
-         else:
-             return False
+         with open(file_path, "rb") as f:
+             data = f.read()
+         response = requests.post(destination, files={"file": data})
+         success = response.status_code == 200
+         
+         if success:
+             logger.info(f"Upload successful: {file_path}")
+         else:
+             logger.error(f"Upload failed: {file_path}, status={response.status_code}")
+         
+         return success
      except Exception as e:
-         print(f"Error: {e}")
+         logger.exception(f"Upload error for {file_path}: {e}")
          return False
```

**问题：**
- 改了引号风格（单引号→双引号）
- 加了没人要求的类型提示
- 加了 docstring
- 重新格式化了空白
- 改了布尔返回逻辑

#### ✅ 正确做法（匹配现有风格）

```diff
+ import logging
+ 
+ logger = logging.getLogger(__name__)
+ 
  def upload_file(file_path, destination):
+     logger.info(f'Starting upload: {file_path}')
      try:
          with open(file_path, 'rb') as f:
              data = f.read()
          
          response = requests.post(destination, files={'file': data})
          
          if response.status_code == 200:
+             logger.info(f'Upload successful: {file_path}')
              return True
          else:
+             logger.error(f'Upload failed: {file_path}, status={response.status_code}')
              return False
      except Exception as e:
-         print(f"Error: {e}")
+         logger.exception(f'Upload error: {file_path}')
          return False
```

**匹配了：** 单引号、无类型提示、现有布尔模式、空格风格。

---

## 原则四：目标驱动（Goal-Driven Execution）

### 示例 1：模糊 vs 可验证

**用户请求：** "修复认证系统"

#### ❌ LLM 常见做法（模糊方法）

```
我会通过以下步骤修复认证系统：
1. 审查代码
2. 识别问题
3. 进行改进
4. 测试改动
[然后在没有清晰成功标准的情况下开始修改]
```

#### ✅ 正确做法（可验证的目标）

```
要"修复认证"，我需要先定义成功标准。
具体要解决什么问题？
如果问题是"用户改密码后仍然保持登录状态"：
计划：
1. 写测试：改密码 → 验证旧会话失效
   验证：测试失败（重现 bug）
2. 实现：改密码时失效会话
   验证：测试通过
3. 检查边界情况：多个活跃会话、并发修改
   验证：额外测试通过
4. 验证无回归：现有认证测试仍然通过
   验证：完整测试套件全绿
当前认证测试覆盖率：[显示覆盖率]
你遇到的具体认证问题是什么？
```

---

### 示例 2：带验证的多步骤任务

**用户请求：** "给 API 添加限流"

#### ❌ LLM 常见做法（一次性全上）

```python
# 一个 300 行的提交就实现了完整的限流，包括 Redis、
# 多种策略、配置系统、监控
# 没有清晰的验证步骤
```

#### ✅ 正确做法（增量式，每步带验证）

```
限流实现计划：
1. 添加基础内存限流（单端点）
   验证：
   - 测试：100 次请求 → 前 10 次成功，其余返回 429
   - 手动：curl 端点 11 次，看到限流错误
2. 提取为中间件（应用到所有端点）
   验证：
   - 测试：限流应用到 /users 和 /posts
   - 现有端点测试仍然通过
3. 添加 Redis 后端（多服务器支持）
   验证：
   - 测试：应用重启后限流计数保持
   - 测试：两个应用实例共享限流计数器
4. 添加配置（每个端点不同速率）
   验证：
   - 测试：/search 允许 10/分钟，/users 允许 100/分钟
   - 配置文件正确解析
每一步都可以独立验证和部署。
从第 1 步开始？
```

---

### 示例 3：测试优先验证

**用户请求：** "分数相同时排序出问题"

#### ❌ LLM 常见做法（不重现就修复）

```python
# 不确认 bug 就立即改排序逻辑
def sort_scores(scores):
    return sorted(scores, key=lambda x: (-x['score'], x['name']))
```

#### ✅ 正确做法（先重现）

```python
# 1. 首先，写一个能重现问题的测试
def test_sort_with_duplicate_scores():
    """测试多个项目分数相同时的排序。"""
    scores = [
        {'name': 'Alice', 'score': 100},
        {'name': 'Bob', 'score': 100},
        {'name': 'Charlie', 'score': 90},
    ]
    
    result = sort_scores(scores)
    
    # Bug：相同分数时顺序不确定
    # 运行这个测试多次，结果应该一致
    assert result[0]['score'] == 100
    assert result[1]['score'] == 100
    assert result[2]['score'] == 90
# 验证：运行测试 10 次 → 因顺序不一致而失败

# 2. 现在用稳定排序修复
def sort_scores(scores):
    """按分数降序排序，分数相同时按名称升序。"""
    return sorted(scores, key=lambda x: (-x['score'], x['name']))
# 验证：测试一致通过
```

---

## 反模式总结

| 原则 | 反模式 | 正确做法 |
|------|--------|---------|
| 编码前思考 | 默默假设文件格式、字段、范围 | 明确列出假设，要求澄清 |
| 简约至上 | 单次折扣计算就用策略模式 | 一个函数，直到确实需要复杂度 |
| 精确编辑 | 修 bug 时改引号、加类型提示 | 只改修复报告问题所需的行 |
| 目标驱动 | "我会审查并改进代码" | "为 bug X 写测试 → 让它通过 → 验证无回归" |

---

## 核心洞察

那些"过度复杂"的例子并不是明显错误的——它们遵循了设计模式和最佳实践。问题在于**时机**：它们在需要之前就添加了复杂度，这会：

- 让代码更难理解
- 引入更多 bug
- 实现时间更长
- 更难测试

而"简单"版本：
- 更容易理解
- 实现更快
- 更容易测试
- 当确实需要复杂度时，可以以后再重构

> **好代码是简单地解决今天的问题，而不是提前解决明天的问题。**
