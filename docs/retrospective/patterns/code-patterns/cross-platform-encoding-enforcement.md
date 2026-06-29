+++
id = "cross-platform-encoding-enforcement"
domain = "code"
layer = "code"
maturity = "L2"
validation_count = 1
reuse_count = 0
documentation_level = "detailed"
source = "docs/retrospective/reports/project-governance/dependency-governance/retrospective-vendor-flexloop-governance-adjustment-20260629/insight-extraction.md"

[bindings]
rules = []
references = []
skills = []
related_patterns = ["structured-lightweight-logging", "dual-channel-tiered-logging"]
+++

# 跨平台输出编码强制设置：避免 Windows GBK 崩溃

## 模式概述

Python 命令行工具在 Windows 环境中运行时，如果输出包含非 ASCII 字符（如 emoji、中文），可能因为系统默认编码为 GBK/CP936 而抛出 UnicodeEncodeError。解决方案是在脚本入口处显式强制 UTF-8 编码，不依赖系统默认设置。

## 问题现象

在 Windows PowerShell 中运行包含 emoji 状态标记的 Python 脚本：

```python
print("✅ 检查通过")
print("❌ 检查失败")
```

报错：
```
UnicodeEncodeError: 'gbk' codec can't encode character '\u2705' in position 0: illegal multibyte sequence
```

根本原因：Windows 系统默认编码在很多地区仍是 GBK/CP936，Python 的 `print()` 默认使用系统编码输出，而 GBK 不支持 emoji 等 Unicode 字符。

## 解决方案

### 方案A：包装器脚本设置编码（推荐）

不修改目标脚本，创建一个包装器（wrapper）脚本，在调用目标脚本前设置编码环境变量：

```python
#!/usr/bin/env python3
"""check-vendor.py - 向后兼容包装，设置 UTF-8 编码后调用主脚本。"""
import os
import subprocess
import sys
from pathlib import Path


def main():
    script_dir = Path(__file__).resolve().parent
    target = script_dir / "repo-check.py"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    args = [sys.executable, "-X", "utf8", str(target), "vendor"] + sys.argv[1:]
    sys.exit(subprocess.run(args, env=env).returncode)


if __name__ == "__main__":
    main()
```

**关键设置**：
1. `PYTHONIOENCODING=utf-8` 环境变量：强制 stdin/stdout/stderr 使用 UTF-8 编码
2. `-X utf8` 命令行参数：Python 3.7+ 启用 UTF-8 模式（等价于设置 `PYTHONUTF8=1`）
3. 两者同时设置，兼容性最好

### 方案B：在脚本入口处重新配置 stdout

如果不想用包装器，可以直接在目标脚本开头设置：

```python
#!/usr/bin/env python3
import sys
import io

# 强制 stdout/stderr 使用 UTF-8 编码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
else:
    # Python 3.6 及以下兼容
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
```

### 方案C：ASCII 安全输出策略（最保守）

如果工具需要在最广泛的终端环境中运行（包括不支持 Unicode 的老旧终端），状态输出优先使用 ASCII 字符而非 emoji：

| 用途 | ❌ 避免（emoji） | ✅ 推荐（ASCII） |
|------|----------------|----------------|
| 成功 | ✅、🟢、💚 | `[OK]`、`[PASS]` |
| 失败 | ❌、🔴、💔 | `[FAIL]`、`[ERROR]` |
| 警告 | ⚠️、🟡 | `[WARN]` |
| 信息 | ℹ️、🔵 | `[INFO]` |
| 子模块 | 📦 | `[SUB]` |
| 文件 | 📄 | `[FILE]` |
| 目录 | 📂 | `[DIR]` |

ASCII 标记示例：
```python
print("[OK] 检查通过")
print("[FAIL] 检查失败")
print("[WARN] 发现警告")
print("[INFO] 提示信息")
```

## Windows 兼容性检查清单

开发 Python 命令行工具时，必须验证的 Windows 兼容点：

- [ ] 输出编码：设置了 `PYTHONIOENCODING=utf-8` 或在脚本内 reconfigure
- [ ] 路径分隔符：使用 `pathlib.Path` 或 `os.path.join()`，不硬编码 `/` 或 `\\`
- [ ] 换行符：使用 `os.linesep` 或让 Python 自动处理（文本模式下 `\n` 会自动转换）
- [ ] 子进程创建：Windows 下设置 `creationflags=subprocess.CREATE_NO_WINDOW` 避免弹出控制台窗口
- [ ] 文件路径：Windows 路径长度限制（MAX_PATH=260），必要时使用长路径前缀 `\\?\`
- [ ] Shell 调用：Windows 下 `shell=True` 的行为与 Unix 不同，尽量避免使用
- [ ] 环境变量：Windows 环境变量名不区分大小写，且用 `;` 分隔 PATH（Unix 用 `:`）
- [ ] 信号处理：Windows 不支持 SIGTERM/SIGHUP，只支持 SIGINT（Ctrl+C）

## subprocess 调用 Windows 兼容模板

```python
import subprocess
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    env: Optional[Dict[str, str]] = None,
    timeout: int = 60,
) -> subprocess.CompletedProcess:
    """跨平台运行子进程命令。"""
    run_env = os.environ.copy()
    run_env["PYTHONIOENCODING"] = "utf-8"
    if env:
        run_env.update(env)

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NO_WINDOW

    return subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        env=run_env,
        timeout=timeout,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=creationflags,
    )
```

**关键点**：
1. `text=True` + `encoding="utf-8"`：明确指定输出编码为 UTF-8，不依赖系统默认
2. `errors="replace"`：遇到无法解码的字符时用 `?` 替换，而不是抛出异常
3. `creationflags=CREATE_NO_WINDOW`：Windows 下不弹出额外控制台窗口

## 验证方法

在 Windows 环境中验证编码兼容性：

1. **直接运行测试**：在 PowerShell/CMD 中运行脚本，观察是否有 UnicodeEncodeError
2. **管道测试**：将输出重定向到文件，`python script.py > output.txt 2>&1`，检查文件内容是否正确
3. **CI 测试**：在 Windows CI runner（如 GitHub Actions windows-latest）上运行测试
4. **编码强制测试**：临时设置 `set PYTHONIOENCODING=ascii`（Windows）或 `export PYTHONIOENCODING=ascii`（Unix），运行脚本确认不会崩溃（应使用 errors=replace 降级）

## 反模式

### 反模式1：假设 UTF-8 无处不在

```python
# ❌ 错误：依赖系统默认编码，在 Windows GBK 环境崩溃
print("✅ 所有检查通过")
```

### 反模式2：用 emoji 作为关键逻辑标记

```python
# ❌ 错误：emoji 不仅有编码问题，在不同终端渲染还可能不一致
if line.startswith("✅"):
    handle_success(line)
```

应该用明确的文本标记或结构化输出：

```python
# ✅ 正确：用文本状态字段，emoji 仅作为可选装饰
status = "OK"  # 或 "FAIL" / "WARN"
print(f"[{status}] 检查结果")
```

## 与其他模式的关系

- 应用于 [structured-lightweight-logging](structured-lightweight-logging.md)：日志输出时需要考虑编码兼容性
- 应用于 [dual-channel-tiered-logging](dual-channel-tiered-logging.md)：双通道日志的人类可读通道在 Windows 下需要正确编码
- 补充 [path-discipline](../methodology-patterns/tools-automation/path-discipline.md)：路径规范处理路径分隔符问题，本模式处理输出编码问题，都是跨平台开发的必要防护
