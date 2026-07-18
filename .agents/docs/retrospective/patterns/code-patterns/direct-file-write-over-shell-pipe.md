---
id: "direct-file-write-over-shell-pipe"
source: "../../../knowledge/operations/windows-powershell-pipe-utf8.md"
x-toml-ref: "../../../../../.meta/toml/.agents/docs/retrospective/patterns/code-patterns/direct-file-write-over-shell-pipe.toml"
---
# 文档生成直写文件优先：避免 Windows PowerShell 文本管道编码污染

## 模式概述

当脚本会生成 Markdown、报告、README、JSON 摘要等文本产物时，一个常见但隐蔽的问题是：

- 脚本 stdout 本身是正确的
- 一旦通过 shell 文本管道写文件，内容就可能被错误转码
- 在 Windows PowerShell 下，中文尤其容易出现“终端可执行、文件却乱码”的现象

本模式主张：**文档生成场景优先让 Python 直接写目标文件，不依赖 shell 文本管道承接 stdout。**

## 触发条件

- Python 脚本会生成 README、Markdown 报告、知识库条目、配置模板等文本文件
- 输出内容包含中文或其他非 ASCII 字符
- 运行环境包含 Windows PowerShell
- 原本打算使用 `python script.py | Set-Content out.md` 之类的方式落盘

## 反模式

### 反模式 1：用 PowerShell 文本管道直接写中文文档

```powershell
python .agents/scripts/lib/__init__.py | Set-Content .agents/scripts/lib/README.md
```

风险：

- PowerShell 管道会把 stdout 当作“文本流”处理中转
- 控制台编码、PowerShell 编码和子进程输出编码一旦不一致，就会污染中文内容
- 终端显示乱码和文件实际乱码可能同时发生，也可能只发生其一，排查成本高

### 反模式 2：只看终端，不验证目标文件

如果只看到终端乱码，不能立刻断定文件也坏了；反过来，终端看起来正常也不能保证文件一定正确。  
必须直接读取目标文件验证关键中文片段。

## 推荐做法

### 方案 A：脚本内部直接写文件（首选）

如果脚本本身就知道目标路径，直接在 Python 内完成：

```python
from pathlib import Path

content = generate_report()
Path("README.md").write_text(content, encoding="utf-8")
```

优点：

- 不经过 shell 文本管道
- 文件编码由脚本显式控制
- 责任边界清晰，生成与写回在同一处完成

### 方案 B：外层包装器调用生成函数并直接写文件（推荐）

如果原脚本只负责“生成内容”，而不负责“写文件”，可在外层包装器里直接写：

```powershell
python -X utf8 -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path(r'd:/AI/.agents/scripts'))); import lib; Path(r'd:/AI/.agents/scripts/lib/README.md').write_text(lib.generate_api_docs(), encoding='utf-8')"
```

适用场景：

- 历史脚本默认只打印 stdout
- 不想修改原脚本对外行为
- 需要在 CI、自动化脚本或一次性维护命令中安全落盘

### 方案 C：子进程捕获 stdout 后由 Python 写文件

若必须从另一个 Python 进程捕获输出，确保子进程也显式开启 UTF-8：

```python
import subprocess
import sys
from pathlib import Path

r = subprocess.run(
    [sys.executable, "-X", "utf8", "d:/AI/.agents/scripts/lib/__init__.py"],
    capture_output=True,
    text=True,
    encoding="utf-8",
    errors="strict",
)

if r.returncode != 0:
    raise SystemExit(r.returncode)

Path("d:/AI/.agents/scripts/lib/README.md").write_text(r.stdout, encoding="utf-8")
```

## 实现要点

- 对“文件编码”负责的代码必须显式指定 `encoding="utf-8"`
- 如果存在子进程边界，优先追加 `-X utf8`
- shell 只负责调度命令，不负责承接最终文档内容
- 文档生成命令最好同时提供：
  - 预览模式：打印 stdout
  - 落盘模式：直接写文件

## 判断准则

以下任一条件满足，就优先使用“直写文件”而非“shell 管道写文件”：

- 输出包含中文、emoji、特殊符号
- 生成物需要进入 Git 仓库
- 文档会被后续脚本再次读取或解析
- 工具需要跨平台运行

## 验证清单

- [ ] 在 Windows PowerShell 下生成的目标文件可被 `utf-8` 正常读取
- [ ] 关键中文标题和摘要在文件中保持正确
- [ ] 不依赖 `| Set-Content` 之类的文本管道写回
- [ ] 若使用子进程捕获，子进程已显式启用 UTF-8 输出

## 已知适用案例

### 案例 1：`.agents/scripts/lib/README.md` 重生成

- `lib/__init__.py` 可直接执行输出 API 文档
- 通过 PowerShell 文本管道写回时出现中文污染
- 最终采用 Python 直接 `write_text(..., encoding='utf-8')` 的方式稳定恢复

## 与其他模式的关系

- [cross-platform-encoding-enforcement.md](cross-platform-encoding-enforcement.md)：解决“stdout 自身编码”问题
- [script-json-output-contract.md](script-json-output-contract.md)：解决“输出可编排性”问题

本模式进一步关注：**即便 stdout 正常，shell 文本管道仍可能在落盘阶段破坏文档内容。**

## 边界与选型

本模式主要解决的是：**文档/报告在“写入目标文件”这一跳是否稳定。**

典型信号：

- 直接运行脚本能打印正确中文
- 但执行 `python script.py | Set-Content out.md` 后文件出现乱码
- 终端显示和文件内容的正确性不一致
- 问题集中在 PowerShell 文本管道、`Set-Content`、shell 中转层

优先使用本模式的场景：

- 目标产物是 README、Markdown、报告、知识库条目、配置模板
- 你已经确认脚本本身能产出正确文本
- 真正不稳定的是“如何把文本落盘”

不应由本模式单独解决的场景：

- 脚本一执行就因中文/emoji 输出崩溃
- 子进程还没写文件，只是在 stdout/stderr 阶段就报编码错误

遇到后一类场景时，应优先使用 [cross-platform-encoding-enforcement.md](cross-platform-encoding-enforcement.md)：

- 先让脚本本身具备稳定的 UTF-8 输出能力
- 再决定文档应通过“直接写文件”而非“shell 管道”落盘

简化决策顺序如下：

1. **脚本能否稳定打印？**
   - 不能：先用 `cross-platform-encoding-enforcement`
2. **打印正常后，文件是否仍被管道污染？**
   - 会：改用本模式，直接写文件
3. **是否还需要结构化输出供编排器解析？**
   - 需要：再叠加 [script-json-output-contract.md](script-json-output-contract.md)
