---
id: "myst-migration-12-myst-nb-executable-docs"
title: "MyST-NB与可执行文档专题分析"
source: "report.md#12-MyST-NB与可执行文档专题分析 + MyST-NB官方文档研究 + Executable Books生态分析"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/reports/standards-tools/myst-to-agentspec-migration-analysis/12-myst-nb-executable-docs.toml"
---
## 12. MyST-NB与可执行文档专题分析

### 12.1 本章引言

MyST-NB是Executable Books项目开发的Sphinx/docutils扩展，它将Jupyter notebook的可执行能力带入MyST Markdown生态，开创了"计算性叙事（Computational Narrative）"这一文档新范式。与传统静态文档不同，MyST-NB允许文档中包含可执行代码块，代码运行结果（文本、图表、数学公式、甚至Markdown内容）可以动态嵌入文档任意位置，实现"代码即文档、文档可运行、结果可复现"。

在Agent Spec场景中，MyST-NB的思想极具启发性——Spec文档中的API示例不再是静态的代码片段，而是可以实际运行验证的活文档；性能数据不再是手动更新的硬编码值，而是由基准测试代码动态生成；MCP工具的测试用例可以直接嵌入Spec文档，实现"文档即测试套件"。

然而，如[第5章](05-architecture-compatibility.md)所分析，MyST-NB依赖完整的Sphinx/docutils/Jupyter生态，总代码量12万行以上，与SpecWeave当前基于markdown-it-py的3500行轻量架构存在根本性冲突。本章将系统分析MyST-NB的核心能力，评估其在Agent Spec场景的适配性，并提出"灵感借鉴而非直接引入"的轻量实现方案。

### 12.2 MyST-NB核心能力详解

#### 12.2.1 code-cell指令：可执行代码块

`{code-cell}`是MyST-NB最核心的指令，用于定义可执行代码块：

````markdown
```{code-cell} python3
:tags: [raises-exception, remove-output]
print("Hello, MyST-NB!")
```
````

**核心选项与标签：**

| 选项/标签 | 作用 |
|---|---|
| `language`/位置参数 | 指定代码语言（kernel语言），如python3、javascript等 |
| `raises-exception` | 标记此代码块预期会抛出异常，执行失败不视为错误 |
| `remove-input` | 渲染时隐藏代码输入，只显示输出 |
| `remove-output` | 渲染时隐藏代码输出，只显示输入 |
| `hide-input` | 折叠代码输入（可展开查看） |
| `hide-output` | 折叠代码输出（可展开查看） |
| `skip-execution` | 跳过执行此代码块 |

#### 12.2.2 glue变量绑定机制

`glue`是MyST-NB最具特色的功能，允许在代码中存储变量，然后在文档任意位置引用：

```python
# 代码中绑定变量
from myst_nb import glue
import matplotlib.pyplot as plt

avg_latency = 45.2
qps = 1200
glue("avg_latency", avg_latency)
glue("qps", qps)

fig, ax = plt.subplots()
ax.plot([1,2,3], [4,5,6])
glue("latency_chart", fig, display=False)
```

然后在Markdown中引用：

```markdown
平均延迟为 {glue}`avg_latency` 毫秒，支持QPS {glue}`qps`。

{glue:figure}`latency_chart`
: 延迟对比图
```

**glue支持的四种格式：**

| 指令/Role | 用途 |
|---|---|
| `{glue}`key`` | 内联显示简单值（文本、数字） |
| `{glue:text}`key`` | 格式化文本显示 |
| `{glue:figure}`key`` | 显示图片/图表对象 |
| `{glue:math}`key`` | 显示LaTeX数学公式 |
| `{glue:md}`key`` | 显示Markdown内容 |

glue还支持跨notebook引用：`{glue}`other_notebook.ipynb::key``。

#### 12.2.3 inline eval内联计算

当设置`nb_execution_mode=inline`时，MyST-NB支持`{eval}`角色在Markdown文本中直接嵌入计算结果：

````markdown
```{code-cell} python3
:tags: [remove-input]
radius = 5
```

半径为{eval}`radius`的圆，面积为{eval}`3.14159 * radius**2`。
````

这使自然语言叙述中的数值可以直接由代码计算，避免手动更新错误。

#### 12.2.4 执行缓存与五种执行模式

MyST-NB使用jupyter-cache管理执行结果，支持五种执行模式：

| 模式 | 行为 |
|---|---|
| `off` | 不执行任何代码块 |
| `force` | 强制重新执行所有代码块，忽略缓存 |
| `auto` | 默认模式，仅执行新增或变更的代码块（基于内容hash） |
| `cache` | 严格使用缓存，缓存不存在则报错 |
| `inline` | 执行代码块+启用{eval}内联计算 |

jupyter-cache将执行结果存储在数据库中，确保相同输入产生相同输出，支持文档构建的可复现性。

#### 12.2.5 text-based notebook格式

MyST-NB支持一种特殊的Markdown格式（text-based notebook），通过frontmatter和`+++`分隔符将Markdown文件转化为Jupyter notebook格式：

````markdown
---
file_format: mystnb
kernelspec:
  name: python3
---

# 这是一个Markdown cell

```{code-cell}
print("这是一个code cell")
```

+++

这是另一个Markdown cell

```{code-cell}
print("这是另一个code cell")
```
````

这种格式结合了Markdown的易编辑性和Jupyter notebook的可执行性，兼容jupytext双向转换。

#### 12.2.6 三级配置体系

MyST-NB支持三级配置体系，灵活控制执行行为：

1. **全局配置（conf.py）**：`nb_execution_mode`、`nb_execution_timeout`、`nb_output_stderr`等
2. **文件级配置（frontmatter）**：在单个文件的YAML frontmatter中覆盖全局配置
3. **Cell级配置（tags/选项）**：通过raises-exception、skip-execution等标签控制单个cell

```python
# conf.py全局配置
nb_execution_mode = "auto"
nb_execution_timeout = 60
nb_execution_excludepatterns = ["*-draft.md"]
```

#### 12.2.7 其他有用特性

- **`{nb-exec-table}`指令**：自动生成文档中所有code-cell的执行统计表（执行时间、状态等）
- **格式支持**：直接解析.md/.ipynb/.myst三种格式
- **stderr处理**：可配置stderr的显示行为（show/remove/warn/error）
- **执行超时**：可全局或 per-cell 配置执行超时时间

### 12.3 MyST-NB在Agent Spec场景的适配性分析

#### 12.3.1 高价值适配场景

MyST-NB的核心概念与Agent Spec场景有多个高度契合点：

**场景1：API示例可执行验证**

当前Spec文档中的API示例是静态代码，无法保证正确性。使用code-cell（或轻量版{exec}）后：

````markdown
### 调用示例

```{exec} python
:tags: [remove-input]
import requests
resp = requests.post("http://localhost:8000/api/users", 
                     json={"name": "test"})
print(f"状态码: {resp.status_code}")
print(f"响应: {resp.json()}")
```
````

CI中自动执行这些示例，验证文档示例与实际API行为一致，防止文档过时。

**场景2：MCP工具测试用例嵌入**

MCP工具的Spec文档可以直接内嵌测试用例：

````markdown
### Tool: calculate_sum

计算两个数的和

```{exec} python
:tags: [raises-exception]
# 测试正常情况
result = mcp.call("calculate_sum", a=1, b=2)
assert result == 3

# 测试类型错误
try:
    mcp.call("calculate_sum", a="1", b=2)
except TypeError:
    print("正确抛出TypeError")
```
````

文档即测试套件，无需维护独立的测试文件。

**场景3：性能数据动态绑定**

性能基准测试结果通过glue动态绑定：

````markdown
```{exec} python
:tags: [remove-input]
import timeit
from executable_docs import engine

def benchmark():
    # ... 基准测试代码 ...
    return avg_latency, qps

latency, qps = benchmark()
engine.glue("avg_latency_ms", round(latency, 2))
engine.glue("max_qps", qps)
```

该接口平均延迟为 {eval-inline}`avg_latency_ms` 毫秒，
最大支持QPS约为 {eval-inline}`max_qps`。
````

性能数据由实际运行的基准测试生成，避免手动更新错误。

**场景4：错误场景真实演示**

使用raises-exception标签展示真实错误响应：

````markdown
```{exec} python
:tags: [raises-exception, remove-input]
resp = requests.post("/api/users", json={})  # 缺少必填字段
resp.raise_for_status()  # 这会抛出异常
```
````

读者看到的是真实的错误响应，而非手写模拟。

#### 12.3.2 冲突点与不适配性

尽管概念高度契合，MyST-NB在以下方面与SpecWeave架构存在冲突：

| 冲突点 | MyST-NB设计 | SpecWeave需求 |
|---|---|---|
| **依赖重量** | Sphinx/docutils/Jupyter 12万行+ | markdown-it-py 3500行轻量架构 |
| **执行模型** | Jupyter kernel长驻进程、ZMQ通信 | 轻量subprocess按需执行、快速启动 |
| **范式定位** | Sphinx构建时批量执行 | Agent运行时按需解析+CI验证 |
| **缓存机制** | jupyter-cache数据库式缓存 | 简单文件hash缓存（JSON文件足够） |
| **格式复杂度** | text-based notebook + +++分隔 + kernelspec | 简单Directive语法，无需完整notebook语义 |
| **跨notebook引用** | 支持其他.ipynb文件的glue引用 | Spec场景下跨文档引用需求低 |

**结论**：MyST-NB的设计面向"学术出版物/技术书籍的可执行文档"，是构建时批量执行的重量级方案；而SpecWeave需要的是"开发时CI验证+运行时Agent解析"的轻量级方案。直接引入MyST-NB是用牛刀杀鸡，得不偿失。

### 12.4 借鉴MyST-NB思想的轻量实现方案

基于以上分析，我们提出"灵感借鉴而非直接引入"策略，在markdown-it-py架构上实现精简版可执行文档能力。

#### 12.4.1 {exec}指令设计（code-cell轻量版）

**设计目标**：不依赖Jupyter kernel，基于subprocess实现轻量代码执行。

**语法设计：**

````markdown
```{exec} [language]
:option: value
:tags: [tag1, tag2]

代码内容
```
````

**支持的选项：**

| 选项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `timeout` | int | 30 | 执行超时秒数 |
| `tags` | list | [] | 标签列表 |
| `cwd` | string | 文档所在目录 | 执行工作目录 |
| `env` | dict | {} | 额外环境变量 |

**支持的标签：**

| 标签 | 说明 |
|---|---|
| `raises-exception` | 预期抛出异常，非0退出码视为成功 |
| `remove-input` | 渲染时隐藏代码输入 |
| `remove-output` | 渲染时隐藏代码输出 |
| `skip-execution` | 不执行此块，视为普通代码块 |

**与MyST-NB code-cell的差异：**
- 不依赖Jupyter kernel，直接subprocess调用语言解释器
- 不支持notebook状态共享（每个exec块独立进程）
- 初期仅支持Python（可扩展到Node.js等）
- 不支持+++分隔的text-based notebook格式

#### 12.4.2 {glue-simple}变量绑定（glue轻量版）

**设计目标**：基于Python exec()的轻量变量存储与替换，无需复杂的序列化。

**代码中绑定：**

```python
# 在{exec}块内
from specweave.exec import glue

glue("key", value)  # 支持str/int/float/bool/dict/list
```

**文档中引用：**

- 内联文本：`{glue-simple}`key``
- 后续{exec}块可读取之前绑定的变量（同一文档内顺序执行）

**与MyST-NB glue的差异：**
- 仅支持简单数据类型，不支持matplotlib图表对象（图表建议用Mermaid或图片链接）
- 不支持{glue:figure}/{glue:math}/{glue:md}，仅支持{glue-simple}文本内联
- 不支持跨文档引用
- 变量存储在内存中，文档执行完毕即释放

#### 12.4.3 {eval-inline}内联表达式评估

**设计目标**：安全的内联表达式计算，避免任意代码执行。

**语法：**

```markdown
计算结果：{eval-inline}`1 + 2 * 3`
引用glue变量：{eval-inline}`avg_latency * 2`
```

**安全设计：**
- 使用受限的eval环境，禁用__builtins__
- 仅允许访问glue绑定的变量
- 禁止赋值、import、函数定义等操作
- 表达式复杂度限制（防止ReDoS）

**与MyST-NB {eval}的差异：**
- 仅支持简单算术表达式和glue变量引用
- 不支持任意Python表达式
- 不需要inline执行模式，可与其他模式共存

#### 12.4.4 执行缓存机制

**设计目标**：简单高效的文件hash缓存，无需数据库。

**缓存键**：sha256(代码内容 + language + 选项JSON)
**缓存值**：JSON文件，包含stdout/stderr/returncode/执行时间/glue变量更新
**缓存位置**：`.specweave/exec_cache/<hash>.json`
**缓存失效**：代码内容变更时自动失效；可配置`--force-exec`参数强制重新执行

**与jupyter-cache的差异：**
- 使用文件系统JSON文件，无需SQLite数据库
- 不跟踪notebook内核状态，仅缓存单个代码块结果
- 实现简单，代码量<100行

### 12.5 概念验证代码示例

以下是轻量可执行文档引擎的PoC实现（约200行Python代码）：

```python
"""
specweave_exec.py - 轻量可执行文档引擎（概念验证）
借鉴MyST-NB思想，基于subprocess实现，无Jupyter依赖
"""
import subprocess
import hashlib
import json
import ast
import os
from pathlib import Path
from typing import Any, Dict, Optional, List


class GlueVar:
    """glue变量包装器"""
    def __init__(self, value: Any):
        self.value = value
    
    def __repr__(self):
        return repr(self.value)


class ExecutableDocEngine:
    def __init__(self, doc_path: Path, cache_dir: Optional[Path] = None,
                 force_exec: bool = False):
        self.doc_path = Path(doc_path)
        self.doc_dir = self.doc_path.parent
        self.cache_dir = cache_dir or self.doc_dir / ".specweave" / "exec_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.force_exec = force_exec
        self.glue_vars: Dict[str, Any] = {}
        
        # 注入glue函数到执行环境
        self.exec_globals = {
            "__builtins__": __builtins__,
            "glue": self._glue,
        }
    
    def _glue(self, key: str, value: Any):
        """绑定变量（在{exec}块内调用）"""
        self.glue_vars[key] = value
        print(f"[glue] {key} = {value}")
    
    def _compute_cache_key(self, code: str, language: str, options: dict) -> str:
        content = json.dumps({
            "code": code,
            "language": language,
            "options": options
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def exec_block(self, code: str, language: str = "python",
                   timeout: int = 30, tags: Optional[List[str]] = None,
                   cwd: Optional[str] = None) -> dict:
        """执行一个{exec}代码块"""
        tags = tags or []
        
        if "skip-execution" in tags:
            return {"skipped": True, "output": ""}
        
        raises_exception = "raises-exception" in tags
        working_dir = cwd or str(self.doc_dir)
        
        # Python代码：在同一进程中exec（支持glue变量共享）
        if language == "python":
            return self._exec_python(code, timeout, raises_exception, tags)
        else:
            # 其他语言：subprocess执行
            return self._exec_subprocess(code, language, timeout, 
                                         raises_exception, working_dir, tags)
    
    def _exec_python(self, code: str, timeout: int, 
                     raises_exception: bool, tags: List[str]) -> dict:
        """Python代码内执行（支持glue变量在块间共享）"""
        cache_key = self._compute_cache_key(code, "python", 
                                           {"timeout": timeout, "tags": tags})
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not self.force_exec and cache_file.exists():
            cached = json.loads(cache_file.read_text())
            self.glue_vars.update(cached.get("glue_updates", {}))
            return cached
        
        import io
        import sys
        from contextlib import redirect_stdout, redirect_stderr
        
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(compile(code, str(self.doc_path), "exec"), self.exec_globals)
            success = True
            exc_info = None
        except Exception as e:
            success = not raises_exception
            exc_info = f"{type(e).__name__}: {e}"
        
        result = {
            "success": success,
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "exception": exc_info,
            "glue_updates": dict(self.glue_vars),
            "remove_input": "remove-input" in tags,
            "remove_output": "remove-output" in tags,
        }
        
        cache_file.write_text(json.dumps(result, default=str, ensure_ascii=False))
        return result
    
    def _exec_subprocess(self, code: str, language: str, timeout: int,
                         raises_exception: bool, cwd: str, tags: List[str]) -> dict:
        """子进程执行其他语言（简化实现，支持Node.js等）"""
        lang_map = {
            "javascript": ["node", "-e"],
            "js": ["node", "-e"],
            "bash": ["bash", "-c"],
            "shell": ["bash", "-c"],
        }
        
        cmd_prefix = lang_map.get(language)
        if not cmd_prefix:
            return {"success": False, "error": f"不支持的语言: {language}"}
        
        cache_key = self._compute_cache_key(code, language, {"timeout": timeout})
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not self.force_exec and cache_file.exists():
            return json.loads(cache_file.read_text())
        
        try:
            result = subprocess.run(
                cmd_prefix + [code],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            success = (result.returncode == 0) != raises_exception
            output = {
                "success": success,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "remove_input": "remove-input" in tags,
                "remove_output": "remove-output" in tags,
            }
        except subprocess.TimeoutExpired:
            output = {"success": False, "error": f"执行超时（{timeout}秒）"}
        
        cache_file.write_text(json.dumps(output, ensure_ascii=False))
        return output
    
    def eval_inline(self, expr: str) -> Any:
        """安全评估内联表达式"""
        try:
            parsed = ast.parse(expr, mode="eval")
            
            for node in ast.walk(parsed):
                if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign,
                                    ast.FunctionDef, ast.ClassDef, ast.Call)):
                    if isinstance(node, ast.Call):
                        if not (isinstance(node.func, ast.Name) and 
                               node.func.id in self.glue_vars):
                            raise ValueError(f"不允许函数调用: {node.func.id}")
                    else:
                        raise ValueError(f"不允许的操作: {type(node).__name__}")
            
            return eval(compile(parsed, "<inline>", "eval"),
                       {"__builtins__": {}}, self.glue_vars)
        except Exception as e:
            return f"<eval错误: {e}>"
```

**使用示例：**

```python
# 使用示例
if __name__ == "__main__":
    engine = ExecutableDocEngine(Path("example.md"))
    
    # 执行代码块1
    result1 = engine.exec_block("""
from specweave_exec import glue
import time
start = time.time()
s = sum(range(1000))
glue("total", s)
glue("avg_latency", 42.5)
print(f"Sum: {s}")
""")
    print("=== 代码块1输出 ===")
    print(result1["stdout"])
    
    # 执行内联计算
    print(f"=== 内联计算 ===")
    print(f"平均值的2倍: {engine.eval_inline('avg_latency * 2')}")
    print(f"总和: {engine.eval_inline('total')}")
```

### 12.6 可行性评级和实施建议

#### 12.6.1 可行性评级

| 维度 | 评级 | 说明 |
|---|---|---|
| **概念适配性** | ⭐⭐⭐⭐⭐（最高） | code-cell/glue/inline eval思想与Agent Spec场景高度契合 |
| **技术可行性** | ⭐⭐⭐⭐（高） | 轻量实现PoC仅约200行代码，无复杂依赖 |
| **架构兼容性** | ⭐⭐⭐⭐⭐（最高） | 完全基于现有markdown-it-py架构，可作为插件扩展 |
| **性能影响** | ⭐⭐⭐（中等） | Executable Profile性能下降20-25%，但作为可选Profile不影响日常开发 |
| **维护成本** | ⭐⭐⭐⭐（高） | 代码量小，逻辑简单，维护成本低 |
| **生态兼容** | ⭐⭐（低） | 轻量实现与Jupyter/MyST-NB不完全兼容，但Spec场景不需要完全兼容 |
| **安全风险** | ⭐⭐⭐（中等） | 代码执行有风险，但可通过沙箱/超时/CI环境隔离缓解 |
| **综合评级** | **中等可行** | 概念高度适配但直接引入过重，建议借鉴思想自建轻量实现 |

**最终可行性结论：** ✅ **推荐实施（P1优先级）**

MyST-NB的"计算性叙事"思想对Agent Spec场景有显著价值，且轻量实现的技术门槛低、维护成本小、架构兼容性好。建议不引入完整MyST-NB生态，而是借鉴其核心思想，在markdown-it-py架构上实现精简版{exec}/{glue-simple}/{eval-inline}作为可选的Executable Profile。

#### 12.6.2 分阶段实施建议

**阶段1（P1，2-3周）：核心能力实现**
- {exec}指令解析与执行（Python，subprocess）
- {glue-simple}变量绑定
- {eval-inline}内联表达式（受限环境）
- 文件hash缓存机制
- raises-exception/remove-input/remove-output/skip-execution标签支持
- CLI命令：`specweave exec <file.md>` 执行文档中的{exec}块

**阶段2（P2，3-4周）：CI集成与工具链**
- CI模式：退出码反映执行成功/失败，可集成到PR检查
- 安全沙箱：Docker容器化执行选项
- 多语言支持：Node.js、Bash等
- 错误报告优化：友好的执行失败提示
- LLM辅助生成：根据{interface}自动生成{exec}示例框架

**阶段3（P3，4-6周）：文档站点集成**
- mystmd前端集成：可点击运行的代码块
- {exec-table}执行统计指令
- 文档间glue变量引用（有限支持）
- 执行结果可视化（简单表格、ASCII图）

#### 12.6.3 风险与缓解措施

| 风险 | 概率 | 影响 | 缓解措施 |
|---|---|---|---|
| 代码执行安全漏洞 | 中 | 高 | CI环境Docker沙箱；本地执行需确认；禁用危险函数；超时限制 |
| 缓存一致性问题 | 低 | 中 | 缓存键包含代码hash；提供--force-exec选项；定期清理缓存 |
| 文档执行速度慢 | 中 | 中 | 缓存机制避免重复执行；CI并行执行；非exec场景不启用 |
| 多状态共享复杂 | 低 | 低 | 初期仅支持同文档顺序执行；不做复杂状态管理 |
| 团队误用导致文档复杂 | 中 | 中 | 编写明确的使用规范；示例代码审查；仅在必要场景使用 |

---
