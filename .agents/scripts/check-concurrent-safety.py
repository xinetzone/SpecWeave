#!/usr/bin/env python3
"""并发模块安全检查脚本入口。

八维检查法：
1. TIMEOUT    超时：锁/等待操作是否设置超时
2. IDEMPOTENT 幂等：追加操作是否有去重保护
3. BOUNDARY   边界：热路径是否存在O(n)线性查找
4. DEFENSIVE  防御：可变默认参数/内部状态是否做防御性拷贝
5. CONFIG     配置：并发阈值/超时是否可配置
6. I18N       国际化：业务逻辑是否直接匹配中文字面量（含in操作符、字典key中文）
7. DEADLOCK   死锁顺序：多锁获取顺序是否一致，防止死锁
8. LEAK       资源泄漏：线程池/进程池是否正确关闭

用法:
    python check-concurrent-safety.py                          # 扫描 scripts 目录
    python check-concurrent-safety.py -f <file.py>             # 检查单个文件
    python check-concurrent-safety.py --path <dir>             # 检查指定目录
    python check-concurrent-safety.py -d TIMEOUT               # 仅检查超时维度
    python check-concurrent-safety.py --fail-on-error          # 有error级问题时返回非零退出码
    python check-concurrent-safety.py --fail-on-warn           # CI严格模式：warn也返回非零
    python check-concurrent-safety.py --json                   # JSON输出
"""

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.check_concurrent_safety.cli import main

if __name__ == "__main__":
    main()
