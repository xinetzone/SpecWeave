---
id: p2-16-large-opensource-ai-workflow
title: 大型开源项目 AI 协作工作流模式（PyTorch/Helion 范例）
source: d:\spaces\chaos\hub\pytorch\AGENTS.md + d:\spaces\chaos\hub\helion\AGENTS.md
source_type: composite
category: scripts
tags:
  - ai-collaboration
  - workflow
  - pytorch
  - helion
  - opensource
  - testing
  - debugging
archive_status: archived
archive_priority: P2
created_at: 2026-08-02T12:40:00Z
updated_at: 2026-08-02T12:50:00Z
version: v0.1.0
reviewer: chaos-coordinator
review_notes: approved - 汇总 PyTorch/Helion 范例，AI 协作工作流实用
summary: 为 PyTorch、Helion 等大型开源项目编写 AGENTS.md/CLAUDE.md，指导 AI 助手高效协作的工作流模式（bug 复现、测试、调试、lint、PR 准备）
target_path: D:\spaces\SpecWeave\.agents\docs\knowledge\scripts\p2-16-large-opensource-ai-workflow.md
archived_at: 2026-08-02T04:55:51Z
source_version: v0.1.0
archive_version: v0.1.0
last_error: 
archive_history:
  - 2026-08-02T04:55:51Z archived from d:\spaces\chaos\.agents\knowledge\temp\scripts\p2-16-large-opensource-ai-workflow.md to D:\spaces\SpecWeave\.agents\docs\knowledge\scripts\p2-16-large-opensource-ai-workflow.md
---

# 大型开源项目 AI 协作工作流模式

在大型开源仓库（如 PyTorch、Triton/Helion DSL）中使用 AI 助手时，需要通过 AGENTS.md 明确约束工作流，避免 AI 执行危险操作（全量测试、网络安装、构建失败等）。

## AGENTS.md 核心要素

### 1. 边界声明（首要约束）
```markdown
- This is the only AGENTS.md, there are no recursive AGENTS.md
- Do NOT run setup.py, you do not have a working build environment
- Do NOT run pre-commit, it is not setup
- Do NOT attempt to install dependencies, you do not have Internet access
- Do NOT create summary files unless explicitly asked
- Do not run `git commit`; users handle commits/branches.
```

### 2. Bug 修复工作流
```
1. 先创建独立复现文件，验证 bug 确实存在
2. 用该文件验证修复有效
3. 找到合适的测试文件，遵循本地测试惯例添加测试
4. 只运行单个测试用例，禁止运行全量测试
```

**示例命令**：
```bash
python test/test_torch.py TestTorch.test_dir    # PyTorch：运行单个测试
pytest test/test_examples.py::TestExamples::test_attention_block_pointer -x -vv -s  # Helion
```

### 3. 测试执行规范

| 场景 | 正确做法 | 错误做法 |
|------|----------|----------|
| 调试迭代 | 运行单个测试，用 `-k` 过滤 | 运行全量测试套件 |
| 失败调试 | `pytest -x -vv -s`（遇错即停，详细输出） | 无参数直接 pytest |
| 输出捕获 | `-s` 显示 stderr/stdout（查看代码生成日志） | 不使用 `-s` 导致看不到错误 |
| 长输出 | 管道到文件 `... -s 2>&1 | tee /tmp/out` | 直接在终端滚动查看 |

### 4. Lint/格式化
```bash
# PyTorch
lintrunner -a    # 自动应用修复

# Helion (Ruff)
./lint.sh              # 自动格式化和修复问题
./lint.sh fix          # 提交前执行
```

> 注意：CI 使用 Ruff + Pyright/Mypy 等类型检查器。

### 5. 测试框架使用规范

**PyTorch 测试基类**：
```python
from torch.testing._internal.common_utils import run_tests, TestCase

class TestFeature(TestCase):
    def test_something(self):
        # Tensor 相等性使用 assertEqual
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    run_tests()
```

**Helion 测试要点**：
- 测试放在 `test/` 目录，命名 `test_<feature>.py`
- 使用 golden file（filecheck-style）时，添加对应的 `test_<feature>.expected`
- 使用 `helion._testing` 中的辅助函数（`check_example`, `TestCase.assertExpectedJournal`）
- 更新 goldens：`EXPECTTEST_ACCEPT=1 pytest ...`
- 运行时需 CUDA、PyTorch nightly、Triton dev 构建环境，保持单测快速（<30s）

### 6. 有用的环境变量

| 变量 | 用途 | 注意事项 |
|------|------|----------|
| `HELION_USE_DEFAULT_CONFIG=1` | 跳过 autotuning，快速迭代 | **禁止**用于全量测试，会改变执行路径 |
| `HELION_LOGS=all\|+all` | 启用详细日志 | |
| `HELION_PRINT_OUTPUT_CODE=1` | 打印生成的代码 | 调试 codegen 问题必备 |
| `HELION_DEBUG_DTYPE_ASSERTS=1` | 启用 dtype 断言 | 代码生成 bug 排查 |
| `EXPECTTEST_ACCEPT=1` | 自动更新 golden files | 验证后再提交 |

### 7. PR 准备流程（PyTorch 模式）
```bash
git stash -u
git reset --hard $(cat /tmp/orig_work.txt)  # 重置到 LOCAL 分支，不要 fetch
git stash pop
# 解决冲突（如有）
```

### 8. 项目特定编码规范（Helion 示例）
- Python 3.10+，启用 `from __future__ import annotations`
- Ruff formatter，行宽 88，双引号
- 导入由 Ruff/isort 排序，单行单导入
- 导入模式：`import helion; import helion.language as hl`（**不要** `import helion as hl`）
- 模块/文件：snake_case；测试 `test_*.py`；示例 `*.py` 带 `main()`
- Kernel 内禁止 `print()`；使用 logging 或 host-side 代码
- Tile 索引保持维度；`i = hl.tile(...); x[i]` 保持 ranks

## CLAUDE.md/AGENTS.md 设计原则

1. **先说不能做什么**：网络安装、全量测试、随意 commit 等危险操作必须在文件最开头禁止
2. **提供可复制的命令**：所有命令给出完整可执行示例，不要让 AI 猜
3. **说明为什么**：对约束给出原因（如"全量测试耗时过长"、"环境变量会改变执行路径"）
4. **测试基类/辅助函数**：给出标准的 import 路径和用法示例
5. **环境变量清单**：列出调试用的关键 env var 及其副作用
6. **目录职责**：明确测试放哪里、示例怎么写、文档在哪构建
7. **项目特定陷阱**：如 Helion 的 tile 索引规则、PyTorch 的 reset 流程

## 典型文件结构

```
project-root/
├── AGENTS.md          # AI 协作唯一指南（禁止递归 AGENTS.md）
├── CLAUDE.md          # 可选：补充（如测试片段）
├── helion/            # 核心包
├── test/              # PyTest 测试 + golden files (*.expected)
├── examples/          # 可运行示例（每个脚本必须定义 main()）
├── docs/              # Sphinx 文档（输出到 site/）
├── benchmarks/        # 基准测试
├── scripts/           # 工具脚本
└── lint.sh            # 格式化入口
```

---

**来源参考**：
- [PyTorch AGENTS.md](file:///d:/spaces/chaos/hub/pytorch/AGENTS.md)
- [PyTorch CLAUDE.md](file:///d:/spaces/chaos/hub/pytorch/CLAUDE.md)
- [Helion AGENTS.md](file:///d:/spaces/chaos/hub/helion/AGENTS.md)
