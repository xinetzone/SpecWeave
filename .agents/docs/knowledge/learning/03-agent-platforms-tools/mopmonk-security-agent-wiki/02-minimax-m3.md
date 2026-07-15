---
id: "mopmonk-security-agent-wiki-02"
title: "MiniMax M3基座：国产开源的六边形战士"
source: "../mopmonk-security-agent-wiki.md#34-minimax-m3基座国产开源的六边形战士"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/mopmonk-security-agent-wiki/02-minimax-m3.toml"
---
### 3.4 MiniMax M3基座：国产开源的六边形战士

MopMonk选择的基座模型是**MiniMax M3**，这是来自上海AI公司MiniMax（稀宇科技）发布的开源大模型。M3被称为"六边形战士"，因为它同时集齐了三大前沿能力，而这是当时第一个也是唯一一个同时具备这三项能力的开源权重模型：

| 能力 | 说明 | 对漏洞挖掘的价值 |
|---|---|---|
| **前沿编程能力** | 代码理解、生成、调试能力达到开源模型第一梯队 | 能读懂数百万行代码，理解复杂逻辑，构造正确的PoC输入 |
| **1M超长上下文** | 基于MSA（MiniMax Sparse Attention）稀疏注意力架构，支持100万token上下文窗口 | 能直接"看"完整个大型代码库，不会出现"翻到后面忘记前面"的情况 |
| **原生多模态** | 从Step 0就进行多模态混合训练，支持图像、视频输入和桌面操作 | 在长周期Agent任务中保持高稳定性，处理复杂的执行反馈 |

#### MiniMax M3的关键基准成绩（官方发布）：

| 基准测试 | M3成绩 | 测试内容 |
|---|---|---|
| **SWE-Bench Pro** | **59.0%** | 软件工程任务——真实GitHub issue解决 |
| **Terminal-Bench 2.1** | **66.0%** | 命令行环境中的复杂真实任务 |
| **MCP Atlas** | **74.2%** | 工具调用和MCP协议能力 |
| SWE-fficiency | 34.8% | 代码修复效率 |
| KernelBench Hard | 28.8% | 内核级编程任务 |

值得注意的是，M3在SWE-Bench Pro上的59.0%甚至超过了GPT-5.5的58.6%——这也是它能支撑起MopMonk漏洞挖掘任务的基础。M3的MSA稀疏注意力架构是一个关键创新：它通过更精确的KV分块和算子级优化，在100万上下文长度下，每token计算量仅为上一代模型的1/20，prefill阶段提速9倍以上，解码阶段提速15倍以上。这意味着长上下文不仅是"能用"，而且是"高效能用"。

MopMonk团队在技术报告中明确说明，选择M3是因为它结合了：长上下文能力、MoE架构的有效容量、高效稀疏注意力、强大的代码能力，以及在长周期Agent任务中的稳定执行。
