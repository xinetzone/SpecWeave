---
id: "python314-cpython-wiki-10"
title: "Python 3.14 实战示例"
source: "https://docs.python.org/zh-cn/3.14/"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/10-foundational-knowledge/python314-cpython-wiki/10-practical-examples.toml"
---
# Python 3.14 实战示例

本章提供 Python 3.14 新特性的实战示例，每个示例包含目标、代码、预期输出和注意事项。

---

## 示例 1：延迟注解迁移实战

**目标**：将使用 `from __future__ import annotations` 的旧代码迁移到 PEP 649 延迟注解。

```python
# ❌ 旧代码（Python 3.10-3.13 风格）
# from __future__ import annotations  # 删除这行

from typing import get_type_hints

class Node:
    """链表节点——前向引用在 3.14 中自然工作"""
    def __init__(self, value: int, next: Node | None = None):
        self.value = value
        self.next = next

    def __repr__(self) -> str:
        return f"Node({self.value})"

# 创建链表
head = Node(1, Node(2, Node(3)))
print(head)  # Node(1)

# 访问注解：不再需要 get_type_hints()，直接访问即可
print(Node.__init__.__annotations__)
# {'value': <class 'int'>, 'next': None | Node, 'return': <class 'NoneType'>}

# get_type_hints() 仍然可用
hints = get_type_hints(Node.__init__)
print(hints)
# {'value': <class 'int'>, 'next': None | Node, 'return': <class 'NoneType'>}

# 使用 annotationlib 获取不同格式
import annotationlib
from annotationlib import Format

string_anns = annotationlib.get_annotations(Node.__init__, format=Format.STRING)
print(string_anns)
# {'value': 'int', 'next': 'Node | None', 'return': 'None'}
```

---

## 示例 2：t-strings 安全 SQL 查询构建器

**目标**：使用 t-strings 构建防 SQL 注入的查询。

```python
from string.templatelib import Template, Interpolation

class SafeSQL:
    """SQL 查询参数化包装器"""
    def __init__(self, template: Template):
        self.sql_parts = []
        self.params = []
        for part in template:
            if isinstance(part, str):
                self.sql_parts.append(part)
            else:
                self.sql_parts.append("?")
                self.params.append(part.value)
        self.sql = "".join(self.sql_parts)

    def __repr__(self):
        return f"SafeSQL(sql={self.sql!r}, params={self.params!r})"

def sql(template: Template) -> SafeSQL:
    """SQL 模板标签函数"""
    return SafeSQL(template)

# 使用 t-strings 构建安全查询
user_id = 42
name_search = "Alice"

query = sql(t"SELECT id, name, email FROM users WHERE id = {user_id} AND name LIKE {name_search}")
print(query)
# SafeSQL(sql='SELECT id, name, email FROM users WHERE id = ? AND name LIKE ?',
#         params=[42, 'Alice'])

# 模拟执行
# cursor.execute(query.sql, query.params)  ← 安全！
```

---

## 示例 3：自由线程多线程性能基准

**目标**：对比 GIL 模式和自由线程模式下的 CPU 密集型多线程性能。

> ⚠️ 运行要求：需要 `python3.14t` 或使用 `PYTHON_GIL=0 python3.14` 运行

```python
import threading
import time
import sys

def is_free_threaded():
    """检测是否在自由线程模式下运行"""
    if hasattr(sys, '_is_gil_enabled'):
        return not sys._is_gil_enabled()
    return False

def cpu_bound_task(n: int) -> int:
    """CPU 密集型任务：素数计数"""
    count = 0
    for num in range(2, n):
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            count += 1
    return count

def benchmark(workers: int, task_size: int = 50000):
    """多线程基准测试"""
    threads = []
    results = [0] * workers

    def worker(idx):
        results[idx] = cpu_bound_task(task_size)

    start = time.perf_counter()
    for i in range(workers):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start
    return elapsed, sum(results)

if __name__ == "__main__":
    ft = is_free_threaded()
    print(f"自由线程模式: {ft}")
    print(f"{'线程数':>6} | {'耗时(s)':>8} | {'加速比':>6}")
    print("-" * 32)

    # 单线程基线
    t1, r1 = benchmark(1)
    print(f"{1:>6} | {t1:>8.3f} | {1.0:>6.2f}x")

    # 多线程
    for n in [2, 4, 8]:
        elapsed, _ = benchmark(n)
        speedup = t1 / elapsed
        print(f"{n:>6} | {elapsed:>8.3f} | {speedup:>6.2f}x")

    # GIL 模式下：多线程不会比单线程快（甚至更慢）
    # 自由线程模式下：接近线性加速（1.7-1.9x @ 2线程, 3.2-3.8x @ 4线程）
```

**预期输出对比**：

```
# GIL 模式（python3.14）
自由线程模式: False
线程数 |  耗时(s) |  加速比
--------------------------------
     1 |    0.523 |   1.00x
     2 |    0.541 |   0.97x
     4 |    0.568 |   0.92x
     8 |    0.591 |   0.89x

# 自由线程模式（python3.14t）
自由线程模式: True
线程数 |  耗时(s) |  加速比
--------------------------------
     1 |    0.548 |   1.00x
     2 |    0.291 |   1.88x
     4 |    0.158 |   3.47x
     8 |    0.095 |   5.77x
```

---

## 示例 4：多解释器并行计算

**目标**：使用 `concurrent.interpreters` 进行真并行计算。

```python
import concurrent.interpreters as interpreters
import time

def worker_script(n: int, channel_id: int) -> str:
    """生成在子解释器中执行的代码"""
    return f"""
import concurrent.interpreters as interp
ch = interp.channel({channel_id})

# CPU 密集计算
total = 0
for i in range({n}):
    total += i * i

ch.send(total)
ch.close()
"""

def benchmark_interpreters(workers: int, task_size: int = 1000000):
    """使用子解释器并行计算"""
    ch = interpreters.channel()
    interps = [interpreters.create() for _ in range(workers)]

    start = time.perf_counter()
    for interp in interps:
        interp.exec(worker_script(task_size, ch.id))

    results = []
    for _ in range(workers):
        results.append(ch.recv())
    elapsed = time.perf_counter() - start

    ch.close()
    for interp in interps:
        interp.close()

    return elapsed, sum(results)

if __name__ == "__main__":
    print(f"{'解释器数':>8} | {'耗时(s)':>8}")
    print("-" * 25)

    for n in [1, 2, 4]:
        elapsed, total = benchmark_interpreters(n)
        print(f"{n:>8} | {elapsed:>8.3f} (total={total})")
```

---

## 示例 5：Zstandard 压缩对比

**目标**：对比 zstd 与 gzip/bz2/lzma 的压缩性能。

```python
import compression.zstd as zstd
import gzip
import bz2
import lzma
import time
import os

def compress_ratio(original: int, compressed: int) -> float:
    return compressed / original * 100

def benchmark(name, compress_fn, decompress_fn, data):
    # 压缩
    c_start = time.perf_counter()
    for _ in range(10):
        compressed = compress_fn(data)
    c_time = (time.perf_counter() - c_start) / 10

    # 解压
    d_start = time.perf_counter()
    for _ in range(10):
        decompressed = decompress_fn(compressed)
    d_time = (time.perf_counter() - d_start) / 10

    assert decompressed == data
    ratio = compress_ratio(len(data), len(compressed))
    print(f"{name:12} | 压缩: {c_time*1000:6.1f}ms | "
          f"解压: {d_time*1000:6.1f}ms | 大小: {ratio:5.1f}%")

# 准备测试数据
text = b"Hello World! Python 3.14 is great! " * 5000
random_data = os.urandom(100_000)

print("=== 可压缩文本（140KB）===")
benchmark("zstd(3)",    lambda d: zstd.compress(d, 3),   zstd.decompress, text)
benchmark("gzip(6)",    lambda d: gzip.compress(d, 6),   gzip.decompress, text)
benchmark("bz2(9)",     lambda d: bz2.compress(d, 9),    bz2.decompress,  text)
benchmark("lzma(6)",    lambda d: lzma.compress(d, 6),   lzma.decompress, text)

print("\n=== 随机数据（100KB，低可压缩性）===")
benchmark("zstd(3)",    lambda d: zstd.compress(d, 3),   zstd.decompress, random_data)
benchmark("gzip(6)",    lambda d: gzip.compress(d, 6),   gzip.decompress, random_data)
benchmark("bz2(9)",     lambda d: bz2.compress(d, 9),    bz2.decompress,  random_data)
```

---

## 示例 6：asyncio 任务内省

**目标**：使用 asyncio 新的内省工具调试异步程序。

```python
import asyncio
import os

async def fetch_data(url: str):
    """模拟网络请求"""
    await asyncio.sleep(0.5)
    return f"data from {url}"

async def process_url(url: str):
    data = await fetch_data(url)
    return data.upper()

async def main():
    print(f"PID: {os.getpid()}")
    print("运行中... 在另一个终端运行:")
    print(f"  python -m asyncio ps {os.getpid()}")
    print()

    # 创建多个并发任务
    urls = [f"https://api.example.com/{i}" for i in range(5)]
    tasks = [asyncio.create_task(process_url(url)) for url in urls]

    # 给你时间运行 ps 命令
    await asyncio.sleep(1)

    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 示例 7：UUID v7 作为数据库主键

**目标**：使用 UUID v7 生成按时间排序的主键。

```python
import uuid
import time
from dataclasses import dataclass

@dataclass
class User:
    id: uuid.UUID  # UUID v7
    name: str
    email: str

def create_user(name: str, email: str) -> User:
    """创建用户，UUID v7 包含创建时间信息"""
    return User(
        id=uuid.uuid7(),  # 按时间排序的 UUID
        name=name,
        email=email,
    )

# 创建用户
users = []
for i in range(5):
    time.sleep(0.001)  # 确保时间戳不同
    users.append(create_user(f"User{i}", f"user{i}@example.com"))

# UUID v7 按字符串排序 = 按创建时间排序
print("按 UUID 排序（即按创建时间排序）：")
for user in sorted(users, key=lambda u: u.id):
    print(f"  {user.id} - {user.name}")

# 从 UUID v7 提取时间戳
uid = users[0].id
timestamp = uid.time  # Unix 毫秒时间戳
print(f"\n{users[0].name} 创建于: {timestamp}ms (Unix epoch)")
```

---

## 示例 8：pdb 远程附加调试

**目标**：在程序运行中用 pdb 附加到进程进行调试。

```python
import time
import sys

def process_item(n):
    result = n * n
    if n == 100:
        # 在这里触发断点，等待调试器
        print(f"\nPID: {os.getpid()}")
        print("运行: python -m pdb -p {os.getpid()}")
        import pdb
        pdb.set_trace()
    return result

def main():
    data = []
    for i in range(1000):
        data.append(process_item(i))
        if i % 100 == 0:
            print(f"Processed {i}/1000...")
        time.sleep(0.01)

if __name__ == "__main__":
    import os
    main()
```

**调试步骤**：
1. 运行脚本
2. 当脚本暂停在 pdb.set_trace() 时，在另一个终端执行 `python -m pdb -p <PID>`
3. 可以检查变量、单步执行、修改变量

---

- [上一章：迁移指南](09-migration-guide.md) ←
- [下一章：FAQ 与排障](11-faq-troubleshooting.md) →
