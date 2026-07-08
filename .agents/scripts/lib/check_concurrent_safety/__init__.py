"""并发模块安全检查器 - 六维检查法。

检查维度：
1. TIMEOUT   超时：锁/等待操作是否设置超时
2. IDEMPOTENT 幂等：追加操作是否有去重检查
3. BOUNDARY  边界：热路径是否存在O(n)线性查找
4. DEFENSIVE 防御：可变参数/返回值是否做防御性拷贝
5. CONFIG    配置：并发参数是否硬编码不可配置
6. I18N      国际化：业务逻辑中是否存在脆弱的中文匹配
"""

from .models import ConcurrencyIssue, FileReport
from .scanner import scan_python_file, collect_python_files

__all__ = ["ConcurrencyIssue", "FileReport", "scan_python_file", "collect_python_files"]
