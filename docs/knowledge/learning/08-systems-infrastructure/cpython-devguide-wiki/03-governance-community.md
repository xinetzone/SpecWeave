---
id: cpython-devguide-03
title: "03 - 治理与社区"
date: 2026-08-19
tags: [cpython, governance, community, triage, security, ai-policy, communication]
source:
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/08-systems-infrastructure/cpython-devguide-wiki/03-governance-community.toml"
  - devguide.python.org
  - github.com/python/cpython
  - external/libs/python/devguide
maturity: L1-draft
---
# 03 - 治理与社区

本章讲解CPython社区的运作方式：沟通渠道、Issue分类处理、核心团队结构、安全政策、AI工具使用指南。理解社区规则比技术能力更能决定你的贡献体验。

## 沟通渠道

### Discourse（主论坛）

CPython核心开发讨论主要发生在 [discuss.python.org](https://discuss.python.org)，按类别组织：

| 类别 | 用途 | 参与人 |
|------|------|--------|
| **Core Development** | 核心开发流程讨论、PR/Issue讨论、政策变更 | Core Devs + 贡献者 |
| **PEPs** | PEP提案讨论和评审 | 所有人 |
| **Ideas** | 新功能想法、语言改进建议（非正式） | 所有人 |
| **Help** | 求助、使用问题（注意：不是CPython贡献帮助） | 用户社区 |
| **Committers** | Core Devs专属讨论（私有类别） | Core Devs only |
| **Typing** | 类型系统相关讨论 | 类型SIG |
| **Release** | 版本发布相关通知和讨论 | RMs + Core Devs |
| **PSF** | Python软件基金会事务 | PSF成员 |

### 其他沟通渠道

| 渠道 | 地址 | 用途 |
|------|------|------|
| **Discord** | [Python Discord](https://discord.gg/python) `#core-dev`频道 | 实时聊天、快速问题 |
| **IRC** | `#python-dev` on libera.chat | 传统实时聊天（与Discord桥接） |
| **GitHub Issues** | [github.com/python/cpython/issues](https://github.com/python/cpython/issues) | Bug报告、Feature请求 |
| **GitHub PRs** | [github.com/python/cpython/pulls](https://github.com/python/cpython/pulls) | 代码审查 |
| **Stack Overflow** | [python](https://stackoverflow.com/questions/tagged/python)标签 | 使用问题（不适合贡献讨论） |
| **Blogs** | [Planet Python](https://planetpython.org/) | 社区博客聚合 |
| **Python-Dev邮件列表** | mail.python.org/pipermail/python-dev/ | 历史邮件列表（已迁移到Discourse） |

> 💡 **新手建议**：贡献相关问题优先在GitHub Issue/PR中讨论。复杂的设计问题在Discourse的Core Development或Ideas类别讨论。Discord/IRC适合快速问题，但重要决策应在有存档的渠道（Discourse/GitHub）讨论。

### 跨文化沟通指南

CPython社区是全球分布式社区，参与者来自不同文化背景。遵循以下原则：

1. **积极倾听**：先理解对方的观点再回复，不要急于反驳
2. **确认理解**：用自己的话复述对方观点，确认没有误解
3. **避免反问句**：在非母语环境下，反问句容易被误读为攻击性表达。直接说你的想法
4. **耐心对待新人**：每个人都有第一次贡献的时候
5. **就事论事**：讨论技术问题时不要人身攻击或质疑动机
6. **使用清晰英语**：社区通用语言是英语，使用简单清晰的句子，避免俚语和文化特有表达
7. **接受不同意见**：不是所有讨论都会达成共识，RM或SC会做最终决定

### 行为准则（Code of Conduct）

CPython社区遵循 [PSF Code of Conduct](https://www.python.org/psf/conduct/)，核心原则：

- 开放、体贴、尊重
- 不接受骚扰、歧视、攻击性言论
- 违反者可被举报至PSF工作小组，可能导致被禁言或封禁

举报渠道：<conduct-wg@python.org>

## Issue Triage（分类处理）

Issue Tracker位于 [github.com/python/cpython/issues](https://github.com/python/cpython/issues)。

### 标签系统

**类型标签（type-）**：

| 标签 | 含义 |
|------|------|
| `type-bug` | 确认的bug行为异常 |
| `type-crash` | 解释器crash（段错误等） |
| `type-feature` | 新功能请求 |
| `type-security` | 安全漏洞 |
| `type-performance` | 性能问题 |
| `type-refactoring` | 代码重构（无行为变更） |
| `type-documentation` | 文档问题 |
| `type-behavior` | 行为变更讨论 |

**组件标签**：

| 标签 | 含义 |
|------|------|
| `stdlib` | 标准库（Python模块） |
| `extension-modules` | C扩展模块 |
| `interpreter-core` | 解释器核心 |
| `docs` | 文档 |
| `tests` | 测试 |
| `build` | 构建系统 |
| `C API` | C API |
| `asyncio` | asyncio模块 |
| `typing` | 类型系统 |

**OS标签**：`OS-windows`, `OS-mac`, `OS-linux`, `OS-freebsd`, `OS-android`, `OS-ios`

**特殊标签**：

| 标签 | 含义 |
|------|------|
| `easy` | 适合新贡献者的Issue |
| `good first issue` | GitHub标准的新友好标签（CPython使用`easy`为主） |
| `needs backport to X.Y` | 需要回溯到X.Y版本 |
| `DO-NOT-MERGE` | PR暂不合并（等待依赖、讨论等） |
| `skip issue` | PR不需要关联Issue（纯文档等小修改） |
| `skip news` | PR不需要NEWS条目 |
| `sprint` | Sprint活动相关 |
| `awaiting review` | 等待Core Dev review |
| `awaiting change` | 等待作者修改 |
| `awaiting merge` | 等待合并（已approve） |
| `stale` | 长时间无活动 |
| `invalid` | 非有效Issue |
| `wontfix` | 决定不修复 |
| `duplicate` | 重复Issue |

### Triage Team（分类团队）

**角色**：
- 为新Issue添加正确标签
- 确认bug是否可复现
- 请求更多信息（版本号、复现代码等）
- 关闭重复/无效Issue
- 将Issue分配给合适的Core Dev
- 标记easy issue

**如何加入Triage Team**：
1. 持续贡献5-10个以上有质量的PR
2. 在Issue区活跃，帮助分类和回复
3. 在Discourse或直接向Core Dev表达加入意愿
4. 由现有Triage成员推荐即可加入

### Triaging工作流

```
新Issue提交
    │
    ├── 是bug报告？
    │   ├── 能复现？ → 添加type-bug标签，请求更多信息或确认
    │   ├── 是已知问题？ → 标记duplicate，关闭并链接原Issue
    │   ├── 不可复现？ → 请求完整复现代码和版本信息
    │   └── 非bug？ → 解释原因，按需关闭
    │
    ├── 是feature请求？
    │   ├── 小改进？ → 添加type-feature，等待讨论
    │   ├── 大变更？ → 引导到Discourse/PEP流程
    │   └── 不合理？ → 解释原因关闭
    │
    └── 是文档问题？
        └── 添加type-documentation标签
```

## 核心团队（Core Team）

### 组织结构

```
                    ┌─────────────────────┐
                    │  Steering Council   │
                    │  (SC) PEP 13 · 5人   │
                    │   最终治理决策权      │
                    └──┬──────┬──────┬─────┘
                       │      │      │
        ┌──────────────┘      │      └──────────────┐
        │                     │                     │
┌───────▼───────┐   ┌─────────▼─────────┐   ┌──────▼───────┐
│ Release       │   │  Working Groups   │   │  PSRT         │
│ Managers(RM)  │   │  (WG)             │   │  安全响应团队   │
│ 版本管理+发布  │   │  专项工作组        │   │  私有漏洞处理   │
└───────┬───────┘   └─────────┬─────────┘   └──────┬───────┘
        │                     │                     │
        └──────────────────────┼─────────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Core Developers     │
                    │  拥有PR合并权         │
                    │  投票权              │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Dev-in-Residence     │
                    │  全职CPython维护者     │
                    │  处理triage和backlog  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Triage Team         │
                    │  Issue/PR分类        │
                    └──────────────────────┘
```

### Steering Council (SC)

- **依据**：PEP 13定义
- **人数**：5人
- **产生方式**：由Core Devs选举产生，每届任期
- **权力**：
  - 最终裁决PEP争议
  - 任命/罢免RM
  - 决定项目治理结构变更
  - 否决（但极少使用）
- **原则**：尽量少干预，让社区自组织运作

### Core Developers（核心开发者）

- **权力**：
  - 合并PR到main和维护分支
  - 投票选举SC
  - 提名和投票新Core Dev
  - 参与PEP讨论
- **责任**：
  - Review PR
  - 确保代码质量
  - 帮助新贡献者
  - 参与社区决策

### Release Managers（RM）

- 每个MINOR版本（如3.13, 3.14）有专属RM
- **职责**：
  - 管理feature freeze时间线
  - 决定哪些bug fix可以backport
  - 管理RC和final发布流程
  - 执行版本发布
- **权限**：对各自版本分支有最终决定权

### Developer-in-Residence（驻站开发者）

- PSF资助的全职岗位
- **职责**：
  - 处理PR backlog
  - 协助triage
  - 处理技术性维护任务
  - 帮助新贡献者
  - 不负责新功能开发

### 如何成为Core Developer

没有正式的申请流程，是一个自然成长的过程：

1. **持续贡献**：提交高质量PR（通常20+个有实质内容的PR）
2. **参与Review**：在他人PR上提供有价值的review意见
3. **参与讨论**：在Issue、Discourse上参与技术讨论
4. **帮助Triage**：帮助分类Issue、回复问题
5. **获得提名**：现有Core Dev提名你
6. **投票通过**：Core Devs私下投票，多数通过后邀请加入

> 💡 **关键认知**：成为Core Dev是持续贡献的**自然结果**，不是目标。专注于做出好的贡献，认可会自然到来。

### Core Workflow工具

| 工具 | 用途 | 谁操作 |
|------|------|--------|
| **bedevere** | PR自动化机器人（标签、CLA检查、标题验证） | 自动 |
| **blurb** | NEWS条目管理工具 | 贡献者 |
| **miss-islington** | 自动backport机器人 | 自动（Core Dev添加标签后触发） |
| **cherry_picker** | 手动backport工具（冲突时） | Core Dev/贡献者 |
| **clabot** | CLA签署检查机器人 | 自动 |
| **the-knights-who-say-ni** | 检查NEWS条目是否添加 | 自动 |

## 安全政策

### PSRT（Python Security Response Team）

- 由经验丰富的Core Devs组成的安全团队
- 负责处理所有CPython安全漏洞报告
- 私有渠道：<security@python.org>
- **绝对不要**在公开Issue/GitHub/Discourse中报告安全漏洞！

### 安全披露流程

```
发现安全漏洞
    │
    ├── 发送邮件到 security@python.org（加密可选）
    │
    ├── PSRT确认、评估严重性
    │
    ├── 修复在私有仓库开发（不公开）
    │
    ├── 预通知Linux发行版和主要用户（embargo期）
    │
    ├── 修复合入所有受影响分支
    │
    ├── 发布新版本 + 公开安全公告（通常在预安排的日期）
    │
    └── 分配CVE编号
```

### 安全分支

- 所有处于security模式的分支都接受安全修复
- 安全修复的backport由PSRT决定
- 安全修复PR通常在合并前是私有的（防止漏洞利用）

### SBOM（Software Bill of Materials）

CPython从3.12+版本开始提供SBOM，列出所有组件和依赖，用于合规和漏洞追踪。

## AI工具使用指南

CPython社区已经就AI辅助编码工具的使用制定了政策。核心原则：**提交者对代码负全部责任**。

### 核心原则

> 你提交的代码，**你**完全负责。AI工具生成的代码与你手写的代码适用完全相同的质量标准。

### 可接受的使用

AI工具可以用于以下场景：
- **编写注释和文档字符串**：帮助表达更清晰
- **理解现有代码**：解释复杂逻辑、梳理调用关系
- **补充知识**：了解最佳实践、学习不熟悉的API
- **生成测试用例模板**：生成测试框架，你填充具体断言
- **代码补全**：IDE中的自动补全（如Copilot建议一行代码）

### 不可接受的使用

- **绕过测试**：用AI生成"看起来对"的代码但不实际验证
- **删除功能**：AI可能"优化"掉它不理解的必要代码
- **未审查直接提交**：将AI输出不加理解直接提交为PR
- **批量生成PR**：用AI批量生成大量低质量PR（视为spam）
- **替代思考**：用AI做设计决策而不是辅助决策
- **生成安全相关代码**：加密、认证、内存管理等关键代码不依赖AI

### 使用AI的要求

如果你在贡献中使用了AI工具：

1. **逐行审查**：审查AI生成的每一行代码，确保你理解它做什么
2. **能够解释**：你必须能够向reviewer解释每一行代码的作用和原因
3. **测试加倍严格**：AI生成的代码可能包含微妙的bug，测试要更全面
4. **建议披露**：虽然不是强制要求，但建议在PR描述中说明使用了AI辅助，透明度有助于review
5. **质量不打折**：AI生成的代码必须满足与手写代码完全相同的质量标准

### 适用于所有贡献的质量原则

无论是否使用AI，每个PR都应：
- 正确解决问题
- 包含适当的测试
- 遵循代码风格
- 有清晰的commit message
- 原子性（一个PR解决一个问题）
- 不引入不必要的复杂性

## 其他Python实现

CPython不是唯一的Python实现，但它是参考实现，其他实现通常与CPython保持兼容：

| 实现 | 特点 | 主要用途 |
|------|------|----------|
| **PyPy** | JIT编译，运行速度快 | 高性能计算、长时间运行服务 |
| **GraalPy** | 基于GraalVM，与Java互操作 | 多语言互操作场景 |
| **Jython** | 运行在JVM上，与Java互操作 | Java平台集成（仅支持Python 2.7/3.8早期） |
| **IronPython** | 运行在.NET上，与C#互操作 | .NET平台集成 |
| **MicroPython** | 微控制器和嵌入式系统 | IoT、嵌入式设备 |
| **CircuitPython** | MicroPython分支，教育导向 | 硬件编程教育 |

> 💡 CPython是参考实现，语言特性的权威定义以CPython行为为准。其他实现需追赶CPython的功能。

---

## 下一步

👉 [04 - 最佳实践与反模式：10个常见陷阱、PR检查清单与成长路径](04-best-practices-anti-patterns.md)
