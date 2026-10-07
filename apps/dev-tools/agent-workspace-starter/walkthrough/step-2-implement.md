---
id: "starter-walkthrough-step-2-implement"
title: "演练第 2 步：实施（tree_view.py）"
source: "原创（Agent Workspace Starter）"
created_at: "2026-10-07"
---

# 第 2 步 · 实施（tree_view.py）

## 一、步骤目标

按 `spec.md` 的 FR-1~FR-3 实现单文件工具 `tree_view.py`，然后运行验证输出。

## 二、照抄块：tree_view.py 完整参考实现

> 在项目根新建 `tree_view.py`，粘贴下文全文。仅依赖标准库 `os` / `argparse`（≤60 行）。

```python
#!/usr/bin/env python3
"""tree_view.py —— 扫描指定目录并按缩进输出目录树（仅标准库 os / argparse，Python 3.10+）。"""

import argparse
import os


def render_tree(root, max_depth=None):
    """返回目录树文本行列表；max_depth 为 None 时递归全部层级。"""
    lines = [os.path.basename(os.path.abspath(root)) + "/"]

    def walk(path, depth, prefix):
        if max_depth is not None and depth > max_depth:
            return
        try:
            names = sorted(os.listdir(path))
        except OSError as exc:
            lines.append(f"{prefix}[无法读取: {exc}]")
            return
        for name in names:
            full = os.path.join(path, name)
            is_dir = os.path.isdir(full)
            lines.append(prefix + name + ("/" if is_dir else ""))
            if is_dir:
                walk(full, depth + 1, prefix + "    ")

    walk(root, 1, "    ")
    return lines


def main():
    parser = argparse.ArgumentParser(description="扫描指定目录并按缩进输出目录树")
    parser.add_argument("root", nargs="?", default=".", help="要扫描的目录（默认当前目录）")
    parser.add_argument("--max-depth", type=int, default=None, metavar="N",
                        help="限制展示的层级深度（默认不限）")
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f"错误：目录不存在 -> {args.root}")
        raise SystemExit(2)

    for line in render_tree(args.root, args.max_depth):
        print(line)


if __name__ == "__main__":
    main()
```

## 三、实现要点（对应 FR）

| FR | 实现位置 | 说明 |
|---|---|---|
| FR-1 | `render_tree()` | `sorted(os.listdir)` 逐项输出，目录追加 `/`，每层前缀 4 空格 |
| FR-2 | `walk()` 的 `depth > max_depth` 早退 | `--max-depth N` 只展示前 N 层 |
| FR-3 | `main()` 的 `os.path.isdir` 判断 | 目录不存在打印中文错误并 `SystemExit(2)` |

## 四、操作说明

1. 新建 `tree_view.py`，粘贴 §二 全文并保存（UTF-8）
2. 确认文件内 `import` 仅出现 `argparse` 与 `os`
3. 在项目根执行运行命令：

```bash
python tree_view.py . --max-depth 2
```

## 五、实际运行输出样例

在测试目录 `starter-walkthrough-test/`（内含 `README.md`、`docs/guide.md`、`docs/assets/logo.svg`、`src/main.py`）执行：

```bash
$ python tree_view.py . --max-depth 2
starter-walkthrough-test/
    README.md
    docs/
        assets/
        guide.md
    src/
        main.py
```

> 实测环境：Windows + Python 3.14，退出码 0。`docs/assets/` 与 `src/` 下的更深内容未展开，符合 AC-2。
>
> 说明：本样例目录额外含 `docs/` 子结构，用于演示多层缩进；若你按 spec 的 AC-1 只建 `demo/`（仅 `README.md` + `src/main.py`），输出行数会相应减少，属正常，不影响 AC 判定。

## 六、验收点（可勾选）

- [ ] `tree_view.py` 已存在且非空
- [ ] 仅 `import os` 与 `import argparse`，无第三方依赖
- [ ] `python tree_view.py . --max-depth 2` 输出缩进树
- [ ] 目录名带 `/` 后缀；每层缩进 4 空格
- [ ] 无 traceback