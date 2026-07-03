---
id: "vendor-interfaces"
title: "03 交互接口规范"
source: "VENDOR-INTEGRATION.md#interfaces"
x-toml-ref: "../../.meta/toml/.agents/vendor-integration/03-interfaces.toml"
---
# 03 交互接口规范

## 第4章 交互接口规范

与 flexloop 的交互有五种标准方式，每种方式均有明确的正例和反例。

### 4.1 文档引用

✅ **正确做法**：
- 使用相对路径引用 SpecWeave 内部文档：`[AgentForge案例](../cases/agentforge-adoption.md)`
- 使用相对路径引用 flexloop 内文档（只读参考）：`[flexloop Python 规则](../../vendor/flexloop/apps/chaos/.agents/rules/python.md)`
- 链接文本使用描述性名称，便于读者理解

❌ **错误做法**：
- 使用本地绝对路径：`file:///d:/spaces/SpecWeave/vendor/flexloop/...`（在不同机器/克隆位置会断链）
- 在 flexloop 的 Markdown 文件中添加指向 SpecWeave 的链接（形成反向依赖，破坏单向依赖原则）
- 将 flexloop 文档复制到 SpecWeave 后不标注来源（信息失同步风险）

### 4.2 脚本复用（萃取）与条件导入

与 flexloop 代码交互有两种方式：脚本萃取（推荐用于稳定功能）和条件导入（适用于可选功能）。

**方式一：脚本萃取（推荐）**

✅ **正确做法**：
- 将 flexloop 中有普遍价值的脚本**复制**到 `.agents/scripts/`
- 适配 SpecWeave 代码风格、命名规范、路径处理、导入方式
- 使用 `.agents/scripts/lib/` 共享库，不重复实现已有功能
- 在文件头部注释标注来源：`# Source: vendor/flexloop/apps/chaos/.agents/scripts/xxx.py`
- 在 TOML frontmatter 使用 `source = "vendor/flexloop/apps/chaos/.agents/scripts/xxx.py"`
- 为萃取后的代码编写测试用例，验证在 SpecWeave 环境中正常工作

❌ **错误做法**：
- 直接 import vendor/flexloop/ 内的 Python 模块（应使用条件导入方式，见 4.5）
- 通过 `sys.path.insert` 永久添加 vendor 路径到 Python 模块搜索路径
- 直接调用 vendor/ 内脚本执行（应使用沙箱工具，见 4.6）
- 复制脚本后不做适配，保留 flexloop 特有的路径和导入

**方式二：条件导入**

对于需要直接调用 flexloop 模块且允许子模块未初始化时优雅降级的场景，使用条件导入（详见 4.5 节）。

### 4.3 模式参考

✅ **正确做法**：
- 通过案例文档（如 [agentforge-adoption.md](../cases/agentforge-adoption.md)）对照说明模式差异
- 保持两套规则体系各自独立，不要求对方遵循己方规范
- 在 SpecWeave 文档中说明"flexloop 是如何实现的"作为参考

❌ **错误做法**：
- 直接复制 flexloop 的规则文件到 `.agents/rules/` 不做适配
- 要求 flexloop 遵循 SpecWeave 规范（两个项目独立演进）
- 将 flexloop 的特定实现作为 SpecWeave 的强制标准

### 4.4 禁止行为清单

以下行为严格禁止：

- ❌ 在 `vendor/flexloop/` 内创建/修改文件后不 commit 就提交到 SpecWeave 主仓库（允许开发但必须先 push）
- ❌ 裸 import vendor. 模块（无 try/except 保护，必须使用条件导入）
- ❌ 将 `vendor/` 路径加入 sys.path 永久（条件导入临时添加后恢复除外）
- ❌ 在主项目测试中遍历或收集 vendor/ 下的测试用例
- ❌ 将 flexloop 作为 pip 包安装到主项目 .venv 虚拟环境
- ❌ 在 SpecWeave 的 CI 流水线中运行 flexloop 的测试套件

### 4.5 条件导入

通过 `lib/vendor_sandbox.py` 提供的 `conditional_import()` 和 `FLEXLOOP_AVAILABLE` 标志，可以安全地导入 flexloop 模块。当子模块未初始化或不可用时，导入会返回 `None`，调用方需优雅降级。

```python
from lib.vendor_sandbox import conditional_import, FLEXLOOP_AVAILABLE

if FLEXLOOP_AVAILABLE:
    taolib_cli = conditional_import("apps.chaos.src.taolib.cli")
    if taolib_cli is not None:
        # 使用 flexloop 功能
        pass
# FLEXLOOP_AVAILABLE 为 False 时优雅降级
```

✅ **正确做法**：
- 始终先检查 `FLEXLOOP_AVAILABLE` 标志
- 使用 `conditional_import()` 而非直接 import
- 对返回 `None` 的情况做好降级处理
- 导入失败时不影响 SpecWeave 核心功能运行

❌ **错误做法**：
- 裸 `import vendor.flexloop.xxx` 或 `from vendor.flexloop.xxx import yyy`
- 不检查 `FLEXLOOP_AVAILABLE` 就直接调用导入的模块
- 条件导入失败时抛出异常导致程序崩溃
- 永久修改 `sys.path` 指向 vendor 目录

### 4.6 沙箱运行规范

运行 flexloop 脚本必须使用 `lib/vendor_sandbox.py` 提供的沙箱工具，限制写入范围和环境变量，避免污染 SpecWeave 主环境。

```python
from lib.vendor_sandbox import run_flexloop_script
result = run_flexloop_script(".agents/scripts/check_gitignore.py", ["--fix"])
if result.returncode == 0:
    print("成功")
```

✅ **正确做法**：
- 使用 `run_flexloop_script()` 在隔离环境中执行 flexloop 脚本
- 脚本路径相对于 `vendor/flexloop/` 目录
- 检查 `returncode` 判断执行结果
- 沙箱自动限制文件写入范围为 SpecWeave 允许的目录

❌ **错误做法**：
- 直接 `subprocess.run()` 调用 vendor/ 内脚本
- cd 到 vendor/flexloop/ 后直接执行脚本而不使用沙箱
- 允许 flexloop 脚本写入 SpecWeave 主权区任意位置
- 在沙箱外运行 flexloop 脚本修改主项目环境
---

## 相关模式

- [双模式子模块治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/dual-mode-submodule-governance.md)
- [Vendor生命周期治理](../../docs/retrospective/patterns/methodology-patterns/governance-strategy/vendor-lifecycle-governance.md)
- [子模块元数据外部化](../../docs/retrospective/patterns/architecture-patterns/submodule-metadata-externalization.md)
---

← 上一章: [02 边界划分与协作原则](02-boundaries-principles.md) | **[返回索引](../VENDOR-INTEGRATION.md)** | 下一章: [04 版本控制与子模块流程](04-versioning-workflows.md) →
