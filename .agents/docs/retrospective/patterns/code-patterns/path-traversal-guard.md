---
id: "path-traversal-guard"
source: "../../reports/competitive-analysis/retrospective-tuyaopen-dev-skills-learning-20260630/insight-extraction.md"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/code-patterns/path-traversal-guard.toml"
---
# 路径越界防护：阻断任意路径访问

## 模式概述

当脚本接受用户提供的文件路径参数时，如果不做边界校验，很容易出现“越界访问”：

- 读取/修改 repo_root 之外的文件
- 借助 `..`、符号链接、大小写差异绕过限制

本模式通过“规范化 + 前缀校验”将所有文件访问约束在允许根目录内。

## 触发条件

- CLI/脚本接受任意路径入参（文件、目录、输出路径）
- 脚本运行在高权限环境（CI、管理员终端、自动化代理）
- 需要防范被提示词引导或误操作导致的越界访问

## 允许根目录定义

允许根目录必须明确且可验证，例如：

- repo_root（通过标志文件定位，如 `.git`、`.clang-format`、`pyproject.toml`）
- project_root（通过标志文件定位，如 `app_default.config`）

## 校验规则

给定 `root` 与 `candidate`：

1. 将两者都转换为真实路径（realpath/resolve）
2. 强制 candidate 必须满足：
   - `candidate == root` 或
   - `candidate` 以 `root + os.sep` 为前缀

## Python 参考实现

```python
import os
from pathlib import Path


def is_within(root: Path, candidate: Path) -> bool:
    root_abs = Path(os.path.realpath(root)).resolve()
    cand_abs = Path(os.path.realpath(candidate)).resolve()
    root_str = str(root_abs)
    cand_str = str(cand_abs)
    return cand_str == root_str or cand_str.startswith(root_str + os.sep)
```

## 常见绕过点与应对

| 绕过点 | 风险 | 应对 |
|---|---|---|
| `..` 上跳 | 越界到父目录 | resolve 后再校验前缀 |
| 符号链接 | 链接指向根目录外 | realpath 后再校验前缀 |
| Windows 大小写 | 同一路径大小写不同 | 使用 realpath/resolve 得到规范化路径 |

## 验证清单

- [ ] 传入 `../` 或绝对路径指向 root 外部会被拒绝
- [ ] 符号链接指向 root 外部会被拒绝
- [ ] 错误提示明确说明“必须位于 <root> 内”

