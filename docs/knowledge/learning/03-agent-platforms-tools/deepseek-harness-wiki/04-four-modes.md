---
id: deepseek-harness-wiki-04
title: DeepSeek Harness Wiki - 四种运行模式
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
date: 2026-08-16
tags:
  - deepseek
  - agent
  - harness
  - modes
  - standard
  - code-mode
  - minimal
  - creator
category: learning
maturity: L1
---

# 04 四种运行模式

DeepSeek Harness 提供四种预设运行模式，每种模式对应不同的插件树与工具集，面向不同的使用场景。本章详细介绍这四种模式的能力差异与适用场景。

## 模式总览对比

| 模式 | 核心能力 | 适用场景 | 启动方式 |
|------|----------|----------|----------|
| **Standard（标准模式）** | 完整编程 Agent 能力：文件编辑、Shell 执行、文件与网页搜索、Skills、计划管理、目标追踪、子 Agent 委派、工作流编排 | 日常写代码、通用编程任务、默认使用场景 | Web UI 默认模式，或 `--profile web` |
| **Code（代码模式 / PTC）** | Standard 全部能力 + 程序化工具调用（Programmatic Tool Calling），模型通过 TypeScript 编排多步操作 | 多步操作密集场景，希望减少轮次往返、提升执行效率 | Web UI 模式切换，或启动时指定 |
| **Minimal（极简模式）** | 仅保留两个工具：持久化 `bash` 和 `str_replace_editor` | 模型基准评测、需要极简可控环境的研究场景 | `--profile minimal` |
| **Creator（创造模式）** | Standard 全部能力 + 运行时自省、内存中试验插件、Preset 编写指导 | 定制 Agent 形态、开发插件、自定义 Profile | Web UI 模式切换，或 `--profile creator` |

每种模式本质上是不同的 Profile 配置，对应不同的 Bundle 组合与补丁叠加，切换模式不需要修改代码，仅需切换配置。

## Standard 模式：完整编程 Agent

Standard 模式是 dsh 的默认模式，提供开箱即用的完整编程 Agent 能力清单。

### 完整能力清单

| 能力类别 | 具体功能 |
|----------|----------|
| **文件操作** | 文件读取、写入、编辑、目录遍历、文件搜索（grep/find）、str_replace_editor 精确替换 |
| **Shell 执行** | 持久化 Bash 终端、命令执行、PTY 伪终端支持、工作目录切换 |
| **搜索能力** | 代码库内全文搜索、网页搜索、内容检索 |
| **Skills 系统** | 可复用技能模块、技能调用、技能组合 |
| **计划管理** | 任务拆解、步骤规划、进度追踪、计划调整 |
| **目标追踪** | 长期目标维护、子目标分解、目标完成状态管理 |
| **子 Agent 委派** | 将子任务委派给独立的子 Agent 执行、子任务结果回收 |
| **工作流编排** | 多步骤工作流定义、条件分支、循环执行 |
| **权限控制** | 敏感操作审批、操作权限分级、会话级权限配置 |

### 何时使用 Standard 模式

- 日常软件开发任务（写代码、改 Bug、重构）
- 代码库分析与理解
- 文档生成与维护
- 通用自动化任务
- 大多数常规使用场景

Standard 模式平衡了能力完整性与使用便捷性，是首次使用 dsh 时的推荐起点。

## Code 模式（PTC - 程序化工具调用）

Code 模式（又称 PTC 模式，Programmatic Tool Calling）是 dsh 针对多步密集操作场景优化的特殊模式。

### 核心机制

在传统 ReAct 模式下，Agent 每调用一次工具就需要一次完整的模型请求往返：
1. 模型思考要做什么
2. 输出一个工具调用
3. 等待工具执行
4. 拿到结果后再次思考下一步
5. 重复...

一个包含 5 次工具调用的序列需要 5 轮模型请求，产生大量往返开销。

Code 模式下，模型不再逐个输出工具调用，而是**编写一段 TypeScript 代码，将多个工具调用编排进一次程序中**。这段代码由 dsh 运行时执行，可以：
- 顺序调用多个工具
- 使用变量传递中间结果
- 进行条件判断与循环
- 处理错误与异常

原本需要 5 轮往返的操作序列，在 Code 模式下只需要 1 次模型请求生成代码，随后一次性执行完成。

### 典型场景示例

例如「找出所有测试文件并运行失败的测试」这一任务：

**传统模式流程（N 轮往返）**：
1. 调用 `find` 查找测试文件 → 拿到文件列表
2. 逐个读取测试文件内容 → 分析哪些测试可能失败
3. 运行测试命令 → 拿到失败结果
4. 分析失败日志 → 定位问题
5. 修改代码 → 再次运行测试验证

**Code 模式流程（1 轮生成代码 + 批量执行）**：
模型直接生成一段 TypeScript：
```typescript
const testFiles = await fs.glob('**/*.test.ts');
const results = [];
for (const file of testFiles) {
  const { exitCode, stdout } = await shell.exec(`npx jest ${file}`);
  if (exitCode !== 0) {
    results.push({ file, error: stdout });
  }
}
return results;
```

运行时一次性执行完所有步骤，最后将结果返回给模型做总结。

### 适用场景

- 批量文件处理（批量重命名、批量格式转换）
- 多步骤数据处理流水线
- 重复执行相似操作的场景
- 需要复杂控制流（条件、循环）的任务
- 对延迟敏感、希望减少轮次开销的场景

## Minimal 模式：极简评测环境

Minimal 模式是为模型基准测试与研究场景设计的极简配置。

### 能力说明

Minimal 模式仅暴露两个核心工具：

1. **持久化 `bash`**：一个持续存在的 Shell 会话，可以执行任意命令
2. **`str_replace_editor`**：基于字符串替换的文件编辑器，支持查看、创建、精确修改文件

除此之外，不加载任何其他插件：
- 无 Skills 系统
- 无子 Agent 委派
- 无网页搜索
- 无计划管理
- 无工作流编排
- 无高级权限审批

### 为什么需要 Minimal 模式

在模型评测（Benchmark）场景下，过多的工具和复杂的循环逻辑会引入额外变量，导致：
- 不同模型在不同工具集下表现不可比
- 复杂插件逻辑可能干扰模型本身能力的测量
- 难以复现实验结果

Minimal 模式提供了一个**最小且标准化**的工具面：
- 任何能使用工具调用的模型都可以在这个环境下运行
- 工具数量固定且简单，便于控制变量
- 环境干净，易于复现
- 与主流基准评测框架（如 SWE-bench）的工具设置对齐

### 启动方式

Minimal 模式通常用于无头（Headless）批量评测：

```bash
npx @deepseek-ai/dsh --profile minimal "你的评测任务"
```

## Creator 模式：定制与插件开发

Creator 模式是为希望自定义 Agent 形态、开发插件的高级用户设计的模式。

### 额外能力

在 Standard 模式全部能力的基础上，Creator 模式额外提供：

| 能力 | 说明 |
|------|------|
| **运行时自省** | 可以查看当前加载的插件树、事件流、服务注册表，实时观察内部状态 |
| **内存试插件** | 不需要重启，可以在内存中临时加载、卸载、试验插件代码，立即看到效果 |
| **Preset 编写指导** | 模型会主动帮助你编写 Profile 配置、Bundle 定义、补丁文件，给出定制建议 |
| **插件调试工具** | 提供插件开发辅助工具、事件监听、服务调用追踪 |

### 典型使用流程

使用 Creator 模式定制新形态 Agent 的流程：

1. 启动 Creator 模式：`npx @deepseek-ai/dsh web --profile creator`
2. 在对话中描述你想要的 Agent 形态（如「我想要一个专门做代码审查的 Agent，不需要文件写入权限，但要能调用静态分析工具」）
3. 模型会帮你生成对应的 Profile 配置和补丁
4. 在内存中试验加载这些配置，实时调整
5. 满意后将配置保存到 `~/.dsh/profiles/` 下，成为一个新的可用模式

### 适用场景

- 开发新的 dsh 插件
- 定制团队内部使用的专用 Agent 形态
- 调试插件与配置问题
- 学习理解 dsh 的内部机制
- 探索新的 Agent 交互模式

## 模式切换方法

### Web UI 中切换

在 Web UI 界面中：
1. 找到输入框附近的模式选择器（通常显示当前模式名称，如「Standard」）
2. 点击下拉菜单，选择想要切换的模式
3. 模式切换立即生效，后续对话将在新模式下运行

> 注意：切换模式不会丢失当前会话历史，但会话中已发生的工具调用不受影响。

### 命令行指定 Profile

启动时通过 `--profile` 参数指定模式：

```bash
# 启动 Standard 模式（Web UI）
npx @deepseek-ai/dsh web --profile web

# 启动 Minimal 模式（无头）
npx @deepseek-ai/dsh --profile minimal "任务描述"

# 启动 Creator 模式
npx @deepseek-ai/dsh web --profile creator
```

实际上，四种内置模式本质上就是四个预置的 Profile 名称。你也可以创建自己的自定义 Profile，实现第五种、第六种模式。自定义 Profile 的方法将在后续章节介绍。

## 如何选择合适的模式

| 你的需求 | 选择模式 |
|----------|----------|
| 日常写代码、完成通用编程任务 | Standard（默认） |
| 需要大量批量操作、重复步骤，觉得轮次太慢 | Code |
| 做模型评测、需要干净可控的基准环境 | Minimal |
| 想开发插件、定制自己的 Agent 形态 | Creator |

如果不确定用什么，从 Standard 模式开始就好——它覆盖了 90% 以上的日常使用场景。当你明确感受到某个场景的痛点时，再尝试对应模式。

---

← [03 快速上手](03-quickstart-first-task.md) | → [05 核心架构](05-architecture-everything-plugin.md)
