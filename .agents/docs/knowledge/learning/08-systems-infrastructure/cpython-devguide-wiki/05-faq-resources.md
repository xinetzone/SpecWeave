---
id: cpython-devguide-05
title: "05 - FAQ与资源"
date: 2026-08-19
tags: [cpython, faq, glossary, resources, directory-map, reference]
source:
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/cpython-devguide-wiki/05-faq-resources.toml"
  - devguide.python.org
  - github.com/python/cpython
  - external/libs/python/devguide
maturity: L1-draft
---
# 05 - FAQ与资源

本章收集常见问题、术语表、源码目录速查、推荐阅读路径和外部资源链接，作为贡献过程中的参考手册。

## 常见问题（FAQ）

### 贡献入门 Q&A

**Q: 我需要懂C语言才能贡献吗？**
A: 不需要！CPython的标准库（`Lib/`目录）绝大部分是纯Python代码，文档（`Doc/`）和测试（`Lib/test/`）也完全不需要C。只有修改解释器核心（`Objects/`、`Python/`、`Modules/`中的C扩展）才需要C语言知识。大多数新贡献者从文档、测试、标准库bug修复开始。

**Q: 第一次贡献从哪里开始？**
A: 推荐路径：1) 在GitHub上搜索`label:easy`的Issue；2) 从文档typo修复开始；3) 修复你在使用Python时遇到的小bug。先阅读00和01章，然后直接动手做第一个PR。

**Q: 贡献CPython需要花钱吗？**
A: 完全免费。你只需要一台电脑、网络连接和一个GitHub账户。GitHub Codespaces每月有免费额度，本地开发也只需要免费的编译器工具链。

**Q: CLA是什么？必须签吗？**
A: CLA（Contributor License Agreement）是贡献者许可协议，确认你有权贡献你的代码并授权PSF使用。你只需要签署一次（用GitHub账户登录签署），之后所有PR自动通过CLA检查。签署CLA不转让你的版权，你保留代码的著作权。

**Q: PR提交后多久能得到review？**
A: 时间不定，通常几天到一周。简单的文档PR可能很快被review，复杂的C层变更可能需要更长时间。如果超过两周没有任何回应，可以在PR中礼貌地@提及相关模块的Core Dev或在Discourse上询问。周三的"PR Day"是集中review的时间。

**Q: 我可以提交新的语法/语言特性吗？**
A: 新语法和语言级特性需要通过PEP（Python Enhancement Proposal）流程，不是直接提交PR。先在Discourse的Ideas类别讨论你的想法，获得社区反馈后再考虑写PEP。通常不建议新贡献者从语言级变更开始。

**Q: 可以用AI工具辅助编码吗？**
A: 可以，但你对提交的代码负全部责任。必须逐行审查AI生成的代码，理解每一行，测试充分。建议在PR中披露AI的使用。详见03章AI工具使用指南。

### 技术 Q&A

**Q: 为什么开发必须用pydebug版本？**
A: pydebug模式（`--with-pydebug`或`build.bat -e -d`）启用了大量内部断言检查（`assert()`），这些断言在release模式下被完全移除。pydebug还启用了内存分配调试，可以检测缓冲区溢出、use-after-free等内存错误。不用pydebug版本可能漏掉明显的bug，导致你本地"测试通过"但CI失败。

**Q: 编译后的Python可执行文件在哪里？**
A:
- Unix/Linux: 在源码根目录，直接运行 `./python`
- macOS: 在源码根目录，运行 `./python.exe`（注意是`.exe`后缀，避免与`Python/`目录名冲突）
- Windows: 在源码根目录，运行 `.\python.bat`（不要直接执行`PCbuild\amd64\python_d.exe`，python.bat会正确设置PYTHONPATH等环境）

**Q: 为什么编译后找不到某些模块（如_sqlite3、_ssl）？**
A: 这些是C扩展模块，依赖系统上的开发库。编译时如果缺少对应的开发包，这些模块会静默跳过（编译日志中会有WARNING）。解决方案：
- Ubuntu/Debian: 安装对应的`-dev`包（`libsqlite3-dev`、`libssl-dev`等），然后重新编译
- macOS: `brew install sqlite3 openssl@3.0`，可能需要设置`PKG_CONFIG_PATH`
- Windows: `PCbuild\build.bat -e` 会自动下载外部依赖的预编译二进制

**Q: 测试失败了怎么办？**
A:
1. 确认你用pydebug版本编译
2. 确认你在源码根目录运行（不要cd到其他目录）
3. 单独运行失败的测试看详细输出：`./python -m test test_MODULE -v`
4. 如果是你修改导致的，修复代码
5. 如果是你没修改的模块失败，可能是环境问题或flaky test：
   - 运行 `./python -m test test_MODULE -v -w`（失败时重试）
   - 多次运行确认是否稳定复现
   - 在PR中说明哪些测试失败看起来与你的修改无关

**Q: 如何调试CPython？**
A:
- Python层面：使用`print()`、`pdb`、`logging`
- C层面：使用gdb（Linux/macOS）或Visual Studio Debugger（Windows）
  - gdb: `gdb --args ./python script.py`，然后`break c_function_name`
  - 查看gdb助手：`python-gdb.py`提供了`py-list`、`py-bt`等命令
- 引用计数调试：pydebug模式下`sys.gettotalrefcount()`可用
- 内存泄漏检测：`./python -m test -R 3:3 test_MODULE`

**Q: 编译时OOM（内存不足）怎么办？**
A: `make -j`默认使用所有核心，可能占用大量内存。减少并行数：
```bash
make -j2  # 使用2个核心
make -j1  # 串行编译，最省内存但最慢
```

**Q: Windows下用WSL编译和原生Windows编译有什么区别？**
A:
- WSL编译的是Linux版本的CPython，生成ELF二进制，在WSL环境中运行
- 原生Windows编译（`PCbuild\build.bat`）生成Windows PE二进制（.exe/.dll）
- 修复平台特定bug时需要在对应平台编译测试
- 大多数stdlib bug在任何平台都可以开发
- WSL下注意设置`git config --global core.autocrlf input`避免换行符问题

### 流程 Q&A

**Q: PR标题格式是什么？**
A: `gh-ISSUENUM: 简短描述`，例如`gh-12345: Fix reference leak in os.scandir()`。使用祈使句（Fix而非Fixed），首字母大写，末尾不加句号。没有关联Issue时（不推荐），可以用`gh-0:`前缀。

**Q: Commit message怎么写？**
A: 和PR标题格式相同：`gh-ISSUENUM: 描述`。描述使用祈使句、首字母大写、无句号、不超过72字符。PR可以包含多个commit，合并时会被squash成一个。

**Q: 什么情况需要NEWS条目？**
A:
- 需要：bug修复、新功能、行为变更、C API变更、安全修复（任何用户可见的变更）
- 不需要：纯文档修改、纯测试修复/补充、typo修正、不影响用户的内部重构、注释/空白清理
- 拿不准就加一条，reviewer会告诉你是否需要

**Q: 修复需要backport到旧版本吗？**
A: 不需要你手动操作。修复合入main后，Core Dev会判断是否需要backport，如果需要会添加`needs backport to X.Y`标签，miss-islington bot自动创建backport PR。有冲突时可能需要你帮忙解决。

**Q: 可以直接PR到维护分支（如3.13）吗？**
A: 不可以。所有修复必须先合入main，然后通过backport流程进入维护分支。直接提交到维护分支的PR会被要求重新提交到main。唯一的例外是security fix，由PSRT直接处理。

**Q: Reviewer要求"changes requested"怎么办？**
A: 按要求修改代码，直接追加commit并push（不要force-push）。在PR中回复说明你做了哪些修改。如果你对某个review意见有不同看法，礼貌地解释你的理由，技术讨论是完全正常的。

**Q: PR合并后Issue会自动关闭吗？**
A: 如果PR描述中包含`Fixes gh-NNNNN`或`Closes gh-NNNNN`，合并时GitHub会自动关闭对应的Issue。如果Issue没有自动关闭，可以手动关闭并链接到PR。

---

## 术语表（Glossary）

| 术语 | 全称/解释 |
|------|-----------|
| **Backport** | 将已合入main的bug fix cherry-pick到维护分支的过程 |
| **BPO** | Bugs Python Org，旧的bug追踪系统（bugs.python.org），已迁移到GitHub Issues。有时在commit中看到`bpo-NNNNN`是旧格式 |
| **Buildbot** | CPython的持续集成测试平台，运行在各种平台和架构上（buildbot.python.org） |
| **Blurb** | 管理NEWS条目的命令行工具（`python -m blurb add`） |
| **CLA** | Contributor License Agreement，贡献者许可协议，首次贡献需签署 |
| **cherry-pick** | Git操作，将一个分支的特定commit应用到另一个分支 |
| **cherry_picker** | 用于backport的Python工具，自动处理cherry-pick和PR创建 |
| **Core Dev** | Core Developer，核心开发者，拥有PR合并权 |
| **CPython** | Python的C语言参考实现，即本wiki讨论的对象 |
| **Discourse** | CPython社区的主论坛（discuss.python.org） |
| **EOL** | End of Life，版本生命周期结束，不再接受任何修复 |
| **Flaky test** | 不稳定测试，有时通过有时失败，通常由时序问题或环境依赖导致 |
| **GHA** | GitHub Actions，GitHub的CI/CD服务 |
| **LTO** | Link-Time Optimization，链接时优化，发布版本使用的编译选项 |
| **main** | CPython的主开发分支，对应下一个MINOR版本 |
| **miss-islington** | 自动backport机器人的名字（源自Monty Python梗） |
| **NEWS entry** | NEWS条目，位于Misc/NEWS.d/目录，描述用户可见的变更，自动生成到What's New文档 |
| **PEP** | Python Enhancement Proposal，Python增强提案，语言和社区重大变更的正式提案流程 |
| **PR** | Pull Request，GitHub上的代码提交请求 |
| **PSF** | Python Software Foundation，Python软件基金会，非营利组织，持有Python商标和版权 |
| **PSRT** | Python Security Response Team，Python安全响应团队，处理安全漏洞 |
| **pydebug** | Python debug构建模式（`--with-pydebug`），启用断言和内存调试 |
| **PyPI** | Python Package Index，Python包索引（pypi.org），第三方包仓库（不属于CPython仓库） |
| **RM** | Release Manager，版本发布管理员，负责特定MINOR版本的发布和backport决策 |
| **SC** | Steering Council，指导委员会，CPython的最高治理机构（5人选举产生） |
| **squash merge** | GitHub的合并策略，将PR的所有commit压缩成一个commit后合入目标分支 |
| **stdlib** | Standard Library，Python标准库（Lib/目录） |
| **Triage** | Issue/PR分类处理，添加标签、确认bug、关闭重复等 |
| **upstream** | 指官方仓库（github.com/python/cpython），相对于个人Fork（origin）而言 |
| **WG** | Working Group，工作组，围绕特定主题（如文档、类型系统、社区）组织的团队 |

---

## CPython源码目录速查

| 目录 | 内容说明 | 主要语言 | 贡献频率 | 新手适合度 |
|------|----------|----------|----------|-----------|
| **Doc/** | 官方文档，使用reStructuredText格式，按主题分为`library/`、`reference/`、`tutorial/`等 | rst | ⭐⭐⭐⭐⭐ 极高 | ⭐⭐⭐⭐⭐ 最适合 |
| **Lib/** | Python标准库，包含所有用Python实现的模块（os, sys, datetime, json, asyncio...） | Python | ⭐⭐⭐⭐⭐ 极高 | ⭐⭐⭐⭐ 适合 |
| **Lib/test/** | Python测试套件，`test_xxx.py`对应`Lib/xxx.py`的测试 | Python | ⭐⭐⭐⭐⭐ 极高 | ⭐⭐⭐⭐⭐ 最适合 |
| **Modules/** | C扩展模块，如`_socket`、`_json`、`_sqlite3`、`_asyncio`等性能关键模块 | C | ⭐⭐⭐ 中等 | ⭐⭐ 需要C基础 |
| **Python/** | 解释器核心：字节码执行循环（ceval.c）、编译器（compile.c）、GC、导入系统 | C | ⭐⭐ 较低 | ⭐ 需深入C |
| **Objects/** | 核心对象类型实现：`int`、`str`、`list`、`dict`、`tuple`、`type`等内置类型 | C | ⭐⭐ 较低 | ⭐ 需深入C |
| **Include/** | 头文件，分为公共C API（`cpython/`、`internal/`）和内部API | C/H | ⭐⭐ 较低 | ⭐ 需C API知识 |
| **Parser/** | Python语法解析器、AST构建、tokenizer | C | ⭐ 低 | ⭐ 需编译原理 |
| **Grammar/** | Python语法定义文件（Python.gram） | PEG语法 | ⭐ 低 | ⭐ 需PEG知识 |
| **PC/** | Windows平台特定代码（启动器、DLL注册、安装程序等） | C | ⭐⭐ 较低 | ⭐⭐ |
| **PCbuild/** | Windows构建系统（build.bat、VS项目文件） | batch/props | ⭐ 低 | ⭐ |
| **Mac/** | macOS平台特定代码（框架构建、IDLE集成等） | C/Python | ⭐ 低 | ⭐⭐ |
| **Programs/** | 可执行入口点：`python.c`、`pip`等 | C | ⭐ 低 | ⭐ |
| **Tools/** | 开发和维护工具：`blurb`、`cherry_picker`、`patchcheck`、构建脚本、wasm工具 | Python/Shell | ⭐⭐ 较低 | ⭐⭐⭐ |
| **Misc/** | NEWS条目、ACKS、其他杂项文件 | rst/text | ⭐⭐⭐⭐ 高 | ⭐⭐⭐⭐⭐ |

> 💡 **新手贡献者优先关注**：`Doc/`、`Lib/test/`、`Misc/` → 然后是`Lib/`。这三个目录贡献门槛最低，也是最活跃的区域。

---

## 推荐阅读路径

### 第1周：新贡献者入门

1. 本wiki 00-05章（约1-2小时阅读）
2. [DevGuide Quick Reference](https://devguide.python.org/) — 官方快速参考
3. [DevGuide Setup and Building](https://devguide.python.org/setup/) — 编译指南
4. [DevGuide Lifecycle of a Pull Request](https://devguide.python.org/pullrequest/) — PR流程
5. **动手实践**：找到一个easy issue或修复一个typo，提交你的第一个PR

### 第1个月：活跃贡献者

1. [DevGuide Helping with the Developer's Guide](https://devguide.python.org/docquality/) — 文档贡献
2. [DevGuide Running & Writing Tests](https://devguide.python.org/testing/) — 测试体系
3. [PEP 8](https://peps.python.org/pep-0008/) — Python代码风格指南
4. [PEP 7](https://peps.python.org/pep-0007/) — C代码风格指南
5. 阅读你感兴趣模块的源码和测试（从Lib/开始）
6. 提交5-10个PR，开始参与他人PR的review

### 第3个月：长期贡献者

1. [PEP 13](https://peps.python.org/pep-0013/) — Python语言治理（SC）
2. [DevGuide CPython's Grammar](https://devguide.python.org/grammar/) — 语法定义
3. [Introducing Python Internals](https://leanpub.com/insidethepythonvirtualmachine) — Python VM内部原理（书籍）
4. [CPython Internals](https://realpython.com/products/cpython-internals-book/) — 深入CPython（书籍）
5. 加入Triage Team，参与Issue分类
6. 选择1-2个模块深入学习，成为该模块的专家

### Core Dev级别

1. [PEP 1](https://peps.python.org/pep-0001/) — PEP目的和指南
2. [PEP 11](https://peps.python.org/pep-0011/) — 平台支持政策
3. [PEP 387](https://peps.python.org/pep-0387/) — 向后兼容政策
4. [DevGuide Garbage Collector](https://devguide.python.org/garbage_collector/) — GC实现
5. 阅读`Python/`和`Objects/`目录的C源码
6. 参与PEP讨论和设计决策

---

## 外部资源链接

### 官方资源

| 资源 | 链接 |
|------|------|
| CPython DevGuide（官方贡献指南） | [devguide.python.org](https://devguide.python.org/) |
| CPython源码仓库 | [github.com/python/cpython](https://github.com/python/cpython) |
| Python官方文档 | [docs.python.org](https://docs.python.org/) |
| Python官方网站 | [python.org](https://www.python.org/) |
| PEP索引 | [peps.python.org](https://peps.python.org/) |
| 社区论坛Discourse | [discuss.python.org](https://discuss.python.org/) |
| Buildbot状态 | [buildbot.python.org](https://buildbot.python.org/) |
| PSF官网 | [python.org/psf](https://www.python.org/psf/) |

### 工具

| 工具 | 用途 | 安装/链接 |
|------|------|----------|
| blurb | NEWS条目管理 | `python -m pip install blurb` |
| cherry_picker | 手动backport | `python -m pip install cherry_picker` |
| pre-commit | Git hooks管理 | `python -m pip install pre-commit` + `pre-commit install` |
| coverage | 代码覆盖率 | `python -m pip install coverage` |
| gh (GitHub CLI) | PR检出、Issue管理 | [cli.github.com](https://cli.github.com/) |
| gdb + python-gdb.py | C层调试 | Linux/macOS内置 |

### 学习资源

| 资源 | 说明 |
|------|------|
| [CPython Internals Book](https://realpython.com/products/cpython-internals-book/) | Anthony Shaw著，深入讲解CPython架构和编译，适合想了解C层的读者 |
| [Inside the Python Virtual Machine](https://leanpub.com/insidethepythonvirtualmachine) | 讲解Python VM字节码执行 |
| [Planet Python](https://planetpython.org/) | Python社区博客聚合，了解社区动态 |
| [pyperformance](https://github.com/python/pyperformance) | Python基准测试套件 |
| [Python Design Discussions](https://discuss.python.org/c/core-dev/26) | Discourse核心开发讨论区 |
| [Real Python](https://realpython.com/) | Python教程和进阶文章 |

### 沟通渠道

| 渠道 | 用途 |
|------|------|
| [GitHub Issues](https://github.com/python/cpython/issues) | Bug报告和Feature请求 |
| [GitHub PRs](https://github.com/python/cpython/pulls) | 代码提交和Review |
| [Discourse Core Dev](https://discuss.python.org/c/core-dev/26) | 核心开发讨论 |
| [Discord #core-dev](https://discord.gg/python) | 实时聊天 |
| `#python-dev` on libera.chat | IRC（与Discord桥接） |
| <security@python.org> | 安全漏洞报告（私有！不要公开） |
| <conduct-wg@python.org> | 行为准则举报 |

---

## Wiki索引

| 文件 | 标题 | 内容摘要 |
|------|------|----------|
| [README.md](./README.md) | Wiki首页 | 目录索引和使用说明 |
| [00-overview.md](./00-overview.md) | 总览：CPython贡献全景图 | TL;DR、贡献者全景图、速查表、三条核心洞察、贡献难度分级 |
| [01-contributor-quickstart.md](./01-contributor-quickstart.md) | 贡献者快速上手 | Codespaces、本地环境搭建（6步）、11步PR流程、跨平台编译、问题排查 |
| [02-development-workflow.md](./02-development-workflow.md) | 深度开发流程 | Git工作流详解、PR生命周期、开发周期与版本管理、测试体系 |
| [03-governance-community.md](./03-governance-community.md) | 治理与社区 | 沟通渠道、Issue Triage、核心团队结构、安全政策、AI使用指南 |
| [04-best-practices-anti-patterns.md](./04-best-practices-anti-patterns.md) | 最佳实践与反模式 | 10个常见反模式、PR检查清单、成长路径、心智模型、实用技巧 |
| [05-faq-resources.md](./05-faq-resources.md) | FAQ与资源 | 常见问题解答、术语表、源码目录地图、阅读路径、外部资源 |

---

## 下一步

👉 [返回Wiki首页](./README.md)
