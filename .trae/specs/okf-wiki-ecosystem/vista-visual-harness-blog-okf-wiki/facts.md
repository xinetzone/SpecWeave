---
type: facts
title: "VISTA 视觉 Harness 博文事实集"
status: "draft"
source: "微信公众号「量子位 / QbitAI」《何恺明团队发布多模态Harness框架》(2026-10-09)；权威源 arXiv:2610.02200"
date: "2026-10-20"
---

# 事实集（Facts）

> 信源：微信公众号「量子位（QbitAI / 关注前沿科技）」《何恺明团队发布多模态Harness框架》，作者 henry（发自 凹非寺），发布于 2026-10-09（页面 `var ct = "1791513671"` = 2026-10-09 10:41 北京时间）。
> 编号规则：F-001 ~ F-044 为**博文事实**（F 段）；F-045 ~ F-140 为**权威核验补充事实**（V 段，来自 arXiv 论文原文、项目页、GitHub 仓库（固定 commit `c97c354f`）、ARC Prize 官方方法学、作者主页与 ARC-AGI-3 技术报告）。P0=必核验；P1=选核验；P2=可单源。作者观点显式标注"作者观点"。
> 双份登记：本文件与 bundle `references/article-source.md` 的 F 编号集合必须完全一致（V 阶段机械比对）。

## 一、博文客观事实（F-001 ~ F-030）

| F编号 | 类别 | 声明 | 原文位置 | 核验级别 |
|-------|------|------|---------|---------|
| F-001 | 事件 | 何恺明团队在论文《VISTA: A Visual Harness for Reasoning in an Interactive World》中提出一套视觉原生的 Harness——VISTA | 开头 | P0 |
| F-002 | 能力 | VISTA 让现有多模态模型直接观察环境、保存原始画面，并在推理时随时回看、放大和检查细节，无需从头训练 | 开头 | P0 |
| F-003 | 对比 | 相比传统将环境抽象成文字或代码的做法，VISTA 保留原始的视觉信息 | §视觉原生的脚手架 | P0 |
| F-004 | 机制 | 模型可根据眼下的问题，将过去看过的画面重新调入上下文，参与当前的判断与推理 | §视觉原生的脚手架 | P0 |
| F-005 | 概念 | 基于这套方法，视觉经验成为模型随时调用、反复检查的上下文，多模态模型有了围绕视觉记忆搭建的原生脚手架 | §视觉原生的脚手架 | P1 |
| F-006 | 数字 | 搭配 VISTA，Claude Opus 5.0 完成 ARC-AGI-3 全部 25 个公开游戏，相对人类动作效率得分达到满分 100 | 开头 | P0 |
| F-007 | 数字 | 所用游戏动作数比首次游玩的人类基线少 57.4% | 开头 | P0 |
| F-008 | 数字 | 换成 GPT-5.6 Sol，同样全部通关，得分达到 99 | 开头 | P0 |
| F-009 | 事件 | 团队还在浏览器游戏、迷宫和连线题中验证了这套方法 | 开头 | P0 |
| F-010 | 计划 | 团队将更接近物理世界的具身任务列为后续研究方向 | 开头 | P0 |
| F-011 | 背景 | 去年 11 月，Anthropic 曾以长时间编程任务为例，介绍了 Harness 如何帮助模型跨越多个上下文窗口、持续推进任务 | §视觉原生的脚手架 | P0 |
| F-012 | 机制 | 该 Harness 通过任务清单记录尚未完成的事项，通过进度文件和代码记录保存已经完成的工作 | §视觉原生的脚手架 | P0 |
| F-013 | 观点 | 主要通过文字和代码保存任务状态的 Harness，在一定程度上推动了这一波 Agent 能力的爆发（作者观点） | §视觉原生的脚手架 | P2 |
| F-014 | 问题 | 在真实环境里，光有文字记忆不够——模型不仅要记住物体的位置、朝向，还要理解每次动作前后环境究竟发生了哪些变化 | §视觉原生的脚手架 | P1 |
| F-015 | 问题 | 模型第一次看到一张图时，未必知道哪个细节会在后面变得重要 | §视觉原生的脚手架 | P1 |
| F-016 | 问题 | 视觉信息很难提前用一份文字笔记完整记录下来，更难保证后续执行任务时记录的信息依然够用 | §视觉原生的脚手架 | P1 |
| F-017 | 做法 | 在 ARC-AGI-3 这类基准中，已有思路是先把画面转换成由数字组成的文本网格，再让模型编写程序模拟环境规则、验证行动方案 | §视觉原生的脚手架 | P0 |
| F-018 | 问题 | 环境越复杂，物体的外观、空间关系和动态变化就越难被完整转化成文字和代码；交互历史变长后，早期画面会被逐渐移出上下文或被文字摘要替代 | §视觉原生的脚手架 | P0 |
| F-019 | 问题 | 研究问题：如何在不额外训练基础模型的情况下，让智能体在推理需要时重新检查过去看到的视觉信息 | §视觉原生的脚手架 | P0 |
| F-020 | 机制 | VISTA 把环境返回的每一帧原样存到上下文之外，包括动作过程中的动画中间帧，模型需要时再取回来 | §具体实现 | P0 |
| F-021 | 机制 | 在 ARC-AGI-3 评测中，它既能比较不同时刻的画面，也能放大局部，检查小方块上的朝向标记 | §具体实现 | P0 |
| F-022 | 概念 | 文字笔记记录模型当前的理解，原始画面保留供它重新判断的证据 | §具体实现 | P0 |
| F-023 | 概念 | 研究将这种机制称为对交互历史的显式注意力——模型根据正在思考的问题，选择哪些视觉信息重新进入上下文 | §具体实现 | P0 |
| F-024 | 组件 | VISTA 设计三个核心组件：视觉观测、无损视觉记忆、主动视觉检查，分别负责让模型看清画面、保存历史、按需回看 | §具体实现 | P0 |
| F-025 | 数字 | 视觉观测负责将环境画面提供给模型：在 ARC-AGI-3 实验中，VISTA 会将官方提供的 64×64 画面放大为 512×512 的 PNG 图像，同时保留物体的颜色、外观和空间关系 | §具体实现 | P0 |
| F-026 | 机制 | 无损视觉记忆：每次执行动作后完整保存环境返回的所有画面，包括动作过程中的动画中间帧，并按照回合号和帧号建立索引 | §具体实现 | P0 |
| F-027 | 能力 | 主动视觉检查：通过 inspect 工具，模型可以指定某个历史回合调出对应画面，也可以裁剪、放大局部区域检查细节；还可以一次调出多帧画面，对比动作前后的变化 | §具体实现 | P0 |
| F-028 | 机制 | 执行流程：每回合开始先观察当前画面和可用动作，再结合此前经验判断环境状态并提出下一步行动假设；信息不足则调用工具回看历史画面、放大局部区域，甚至读取具体像素信息 | §具体实现 | P0 |
| F-029 | 机制 | 找到证据后模型不直接行动，而是先预测本次操作可能带来什么变化；动作执行完毕后将实际结果与预测对比，检查判断是否正确，并据此修正对游戏规则的理解 | §具体实现 | P0 |
| F-030 | 机制 | VISTA 引入两份文字笔记：GUIDE.md 记录不同关卡之间可以复用的规则和经验；WORKING.md 记录当前关卡的状态、进度和后续计划 | §具体实现 | P0 |

## 二、博文其余客观事实（F-031 ~ F-044）

| F编号 | 类别 | 声明 | 原文位置 | 核验级别 |
|-------|------|------|---------|---------|
| F-031 | 机制 | 上下文接近上限时，模型先整理交接摘要，再进入新的上下文窗口继续执行；此前的文字笔记、动作历史和视觉档案都会保留下来 | §具体实现 | P0 |
| F-032 | 机制 | 完整方案中，每次执行动作后框架默认只向模型展示最后一帧；动作过程中的中间画面统一保存在视觉档案里，等模型需要时再主动调取 | §具体实现 | P0 |
| F-033 | 观点 | 这样既保留了完整的视觉信息，也避免大量历史图片持续占用上下文空间（作者观点） | §具体实现 | P2 |
| F-034 | 观点 | VISTA 并没有为此额外训练一个新模型：环境理解、行动规划和推理仍由现成的多模态模型完成，Harness 负责执行工具调用、保存视觉历史，并在模型需要时提供相应证据（作者观点） | §具体实现 | P1 |
| F-035 | 观点 | VISTA 改变的不是模型本身，而是模型获取、保存和使用视觉信息的方式（作者观点） | §具体实现 | P1 |
| F-036 | 数字 | GameWorld：使用相同的 GPT-5.6 Sol 模型，相比官方基础框架，VISTA 在 170 项任务中将成功率从 40.0% 提高到 63.3% | §实验验证 | P0 |
| F-037 | 数字 | AI GameStore：在 10 个游戏中，综合得分从 47.3 升至 140.3，其中人类中位数被归一化为 100 | §实验验证 | P0 |
| F-038 | 数字 | BabyVision：在选取的 39 道迷宫与连线题上，准确率从 41.0% 提高到 63.2% | §实验验证 | P0 |
| F-039 | 观点 | BabyVision 这组任务只有静态图片，模型也能通过放大局部、检查像素改善判断（作者观点） | §实验验证 | P1 |
| F-040 | 观点 | 同一套 VISTA 框架只需少量适配，就能用于不同的游戏与谜题（作者观点） | §实验验证 | P1 |
| F-041 | 观点 | 保存原始画面、让模型按需回看，可以进一步发挥现有多模态模型的能力（作者观点） | §实验验证 | P2 |
| F-042 | 名单 | 论文的三位共同第一作者为 Qiushi Han、胡珂雅（Keya Hu）和 Linlu Qiu，另外两位作者为 Cathy Wu 和何恺明 | §作者介绍 | P0 |
| F-043 | 名单 | Qiushi Han（Josh Han）现为 MIT 运筹研究中心博士生，导师为 Cathy Wu | §作者介绍 | P1 |
| F-044 | 名单 | Keya Hu 现为 MIT 电气工程与计算机科学系博士生，由何恺明和 Jacob Andreas 联合指导，本科毕业于上海交通大学 ACM 班 | §作者介绍 | P1 |

## 三、权威核验补充事实（F-045 ~ F-140）

| F编号 | 类别 | 声明 | 来源 | 核验级别 |
|-------|------|------|------|---------|
| F-045 | 事实 | 论文 arXiv:2610.02200 于 2026-10-01 17:59:45 UTC 提交（v1），分类 cs.AI / cs.CV，类型 Tech report，许可 CC BY 4.0 | arXiv abs 页 | ✅ P0 通过 |
| F-046 | 名单 | 论文作者为 Qiushi Han、Keya Hu、Linlu Qiu、Cathy Wu、Kaiming He，机构 Massachusetts Institute of Technology；论文脚注标注前三位为共同第一作者（*Co-first authors*），项目页渲染为 *co-leads* | arXiv abs 页 + 项目页 | ✅ P0 通过 |
| F-047 | 数字 | 论文摘要原文给出 ARC-AGI-3 结果：Claude Opus 5.0 的 Relative Human Action Efficiency 分数从 40.68 提升到完美的 100.00，模型完成全部 25 个公开游戏，所用动作数比首次游玩的人类参与者少 57.4% | arXiv 摘要 + §4.2 + 表1/表2 | ✅ P0 通过（对应 F-006/F-007） |
| F-048 | 数字 | 论文 §4.2 给出动作数口径：VISTA 共用 7,302 个动作，比人类参考的 17,135 个动作少 57.4% | arXiv §4.2 + 表2 Total 行 | ✅ P0 通过 |
| F-049 | 数字 | GPT-5.6 Sol 同样完成全部 25 个游戏，RHAE 得分 99.00（最大推理强度） | arXiv §1 + 表1 + 表2题注 | ✅ P0 通过（对应 F-008） |
| F-050 | 组件 | 论文 §3.1 的三个组件官方名称为：visual observations（视觉观测）、lossless visual memory（无损视觉记忆）、visual inspection（视觉检查）；图 3c 标注为 model-directed visual inspection | arXiv §3.1 + 图3题注 | ✅ P0 通过（对应 F-024；博文用"主动视觉检查"，论文作"视觉检查"——见勘误 E-1） |
| F-051 | 机制 | 论文 §3.1：无损视觉记忆保存环境返回的每一帧（含中间动画帧）原始形式，每帧按回合号与帧号索引，且独立于模型当前上下文保留而始终可用 | arXiv §3.1 + §1 | ✅ P0 通过（对应 F-026） |
| F-052 | 机制 | 论文 §3.1：视觉检查在时间维度可取任意早期回合的多帧以比较状态、重放动作的中间动画帧；在空间维度可请求任意矩形区域的放大视图；另有 read_pixels 工具返回精确 RGB 值 | arXiv §3.1 + 附录 A.4 算法1 | ✅ P0 通过（对应 F-027） |
| F-053 | 机制 | 论文 §3.2：GUIDE.md 记录对游戏的理解及跨关卡仍可能有用的信息，WORKING.md 作为当前状态的草稿本；附录 A.2 补充 GUIDE.md 存放跨关卡与跨会话的可复用知识，WORKING.md 存放当前关卡的临时状态与计划 | arXiv §3.2 + 附录 A.2 | ✅ P0 通过（对应 F-030） |
| F-054 | 机制 | 论文 §3.2：Harness 是纯机械的，不涉及任何被训练的模型——它执行模型请求的工具调用、返回图像或像素值，并对无效请求报错 | arXiv §3.2 | ✅ P0 通过（对应 F-034） |
| F-055 | 数字 | 论文 §4.3 消融默认值：Agent 接收当前渲染状态的 512×512 PNG 图像，由官方 64×64 帧 8× 最近邻放大得到 | arXiv §4.3 + 图7b 题注 | ✅ P0 通过（对应 F-025；项目页另提到单元格间一像素网格线，论文未载） |
| F-056 | 数字 | GameWorld 含 34 个浏览器游戏、跨 5 类题材共 170 项任务；成功率定义为 170 项任务的完成比例，VISTA 为 63.3%，官方实现 40.0%，新玩家 55.3%，此前最好成绩 20.0% | arXiv §5.1 + §5.2 + 图11 | ✅ P0 通过（对应 F-036） |
| F-057 | 数字 | AI GameStore 含 10 个公开浏览器游戏；每个游戏的原始分按对应公开人类中位数归一化为 100 后取几何平均，VISTA 为 140.3，官方实现 47.3，此前最好成绩 9.0 | arXiv §5.1 + 附录 A.3 公式5/6 + 图11 | ✅ P0 通过（对应 F-037） |
| F-058 | 数字 | BabyVision 中 VISTA 评估的是两个 Visual Tracking 子类型的 39 道题（20 道迷宫 + 19 道连线），准确率从官方实现的 41.0% 提升到 63.2%，新玩家 92.3%，此前最好成绩 25.7%；BabyVision 全集为 388 项任务、22 个子类 | arXiv §5.1 + §5.2 + 附录 A.6 + 图11 | ✅ P0 通过（对应 F-038；39 为评估子集，全集 388） |
| F-059 | 概念 | 论文 §3.1/§4.4 使用 "explicit attention mechanism over the interaction history" 表述该机制，§4.4 称其为 re-attention mechanism | arXiv §3.1 + §4.4 | ✅ P0 通过（对应 F-023） |
| F-060 | 概念 | 论文摘要称 VISTA "gives a general-purpose multimodal model long-horizon vision" | arXiv 摘要 | ✅ P0 通过 |
| F-061 | 问题 | 论文 §4.2/§4.3：ARC-AGI-3 的既有做法通常把每帧表示为文本网格、以整数颜色索引逐行编码，并常用基于代码的世界模型——智能体把环境抽象成可执行、可校验的符号程序 | arXiv §4.2 + §4.3 | ✅ P0 通过（对应 F-017） |
| F-062 | 问题 | 论文 §1/§3：随上下文填满，早期观察可能被移出上下文或被文字摘要替代 | arXiv §1 + §3 | ✅ P0 通过（对应 F-018） |
| F-063 | 数字 | 论文 §4.1：VISTA 实例化两个闭源通用多模态模型后端——Claude Opus 5.0（经 Claude Code CLI，extra-high 推理强度）与 GPT-5.6 Sol（经 Codex CLI，max 推理强度）；§4.3 另用开源权重后端 GLM-5.3 Flash 320B（RHAE 66.93） | arXiv §4.1 + §4.3 + 附录 A.1 | ✅ P0 通过 |
| F-064 | 数字 | 论文 §4.2 给出 VISTA 的动作数与人类参考对照：7,302 vs 17,135；官方实现（GPT-5.6 Sol）的 RHAE 为 13.33、共 10,619 个动作 | arXiv §4.2 + 附录 A.1 | ✅ P0 通过 |
| F-065 | 数字 | 论文 §4.3 消融阶梯（累积各组件后 RHAE）：13.33 → 47.32 → 51.66 → 65.82 → 70.05 → 94.10 → 99.00 | arXiv §4.3 | ✅ P0 通过 |
| F-066 | 数字 | 论文另有 3D 重渲染变体：ARC-AGI-3 上 RHAE 84.12，用 20,640 个动作 | arXiv §4.3/§4.4 | ✅ P0 通过 |
| F-067 | 数字 | 论文附录 B.1 给出多次运行波动：ARC-AGI-3 Sol 99.00/98.90/99.23（99.04±0.17）；GameWorld 成功率 63.33±2.37%、进度 79.30±2.14%；BabyVision 准确率 63.23±3.00% | arXiv 附录 B.1 | ✅ P0 通过（补博文缺失的方差口径） |
| F-068 | 观点 | 论文 §6 局限：所用模型在公开基准之后发布，无法排除这些游戏被纳入训练数据的可能；在 ARC-AGI-3 私有集等新游戏上评估才是更强的泛化检验 | arXiv §6 | ✅ P0 通过（**博文完全未提此局限**——见勘误 E-3） |
| F-069 | 计划 | 论文 §7：未来工作可在更复杂逼真的任务上评估，例如更接近物理世界的具身任务 | arXiv §7 | ✅ P0 通过（对应 F-010） |
| F-070 | 事实 | 论文 §3.1 明确只有三组件，无独立的"显式注意力"组件；§3.2 说明默认每次动作后只向 Agent 呈现最后一帧，中间帧全部归档 | arXiv §3.1 + §3.2 + 附录 A.2/A.4 算法1 | ✅ P0 通过（对应 F-032） |
| F-071 | 事实 | 论文全文 64 条参考文献中，唯一 Anthropic 出处是「Introducing Claude Opus 5」模型公告；**未引用** Anthropic 的任何 harness 博文 | arXiv 参考文献列表 | ✅ P0 通过（对应 F-011 的归因边界——见勘误 E-2） |
| F-072 | 事实 | Anthropic《Effective harnesses for long-running agents》发布于 2025-11-26，内容包括用 feature_list.json 特性清单记录待办、claude-progress.txt 进度文件与 git 提交保存已完成工作 | anthropic.com/engineering/effective-harnesses-for-long-running-agents | ✅ P0 通过（对应 F-011/F-012，博文"去年 11 月"表述成立） |
| F-073 | 事实 | ARC-AGI-3 的 Relative Human Action Efficiency（RHAE）是官方指标：单关得分 = (人类基线动作数 / AI 动作数)²，单关上限为人类基线的 1.15 倍，未通关关卡计 0；游戏分为各关得分的加权平均（以关卡序号为权重），总分为各游戏分的平均 | docs.arcprize.org/methodology | ✅ P0 通过（补博文未解释的口径） |
| F-074 | 数字 | ARC-AGI-3 数据集构成：公开演示集 25 个、半私有集 55 个、完全私有集 55 个；私有集刻意与公开集分布外（"significantly more difficult for both humans and AI, and are intentionally out-of-distribution relative to the public set"）；与 ARC-AGI-2 约 10:1 的公私比不同，ARC-AGI-3 反转了这个比例 | arXiv:2603.24621 表1 + §3.6 | ✅ P0 通过（补"25"的权威出处） |
| F-075 | 事实 | VISTA 代码已开源：github.com/joshhhhhan/VISTA，MIT License；运行要求 Linux x86_64 + Python 3.12 + Docker Engine + Codex CLI 0.145.0 或 Claude Code 2.1.220，ARC-AGI-3 批量运行另需 tmux；提供 online / competition / offline 三种操作模式 | github.com/joshhhhhan/VISTA README + pyproject.toml | ✅ P0 通过（**博文未提代码已开源**） |
| F-076 | 事实 | ARC Prize 官方记分卡可独立核验：Opus 5.0 对应 RHAE 100，GPT-5.6 Sol 对应 RHAE 99；三个基准的官方实现基线、GameWorld 与 BabyVision 的出处分别为 GameWorld(ECCV 2026)、AI GameStore(arXiv:2602.17594)、BabyVision(ICML 2026) | arcprize.org/scorecards + 各基准论文 | ✅ P0 通过 |
| F-077 | 数字 | 论文表 1 系统级对比（25 个公开游戏）：官方实现（无程序合成）——GPT-5.6 Sol **max** 13.33、Opus 5.0 **high** 40.68（表注 †：由官方公布的 25 局逐局分数计算得出，非重跑）；程序合成类——Schema 95.35、Schema 回退行 Opus 4.8→Fable 5 **max** 98.98、ewma_sv_v1.6 98.97、Retrodict 99.86、Tycho 100.00；VISTA（无程序合成）——GPT-5.6 Sol **max** 99.00、Opus 5.0 **xhigh** 100.00 | arXiv §4.2 表 1 | ✅ P0 通过 |
| F-078 | 概念 | 论文表 1 题注与 §1/§4.2 的定位声明："VISTA is, to our knowledge, the first system to achieve perfect or near-perfect performance **without program synthesis**"；§1/§4.2 另表述为 "the first **vision-based** system to achieve perfect or near-perfect performance on ARC-AGI-3 without program synthesis"；§4.2 同时指出 Opus 5.0 的 100.00 是 "matching other state-of-the-art systems" | arXiv §1 + §4.2 表 1 题注 | ✅ P0 通过 |
| F-079 | 数字 | 论文 §4.3 消融六步的真实标签与得分：官方实现（文本网格）13.33、10,619 动作 → **(i) 图像观测**（以渲染 PNG 替代文本网格）47.32 → **(ii) 提高动作与时间上限**（每局至多 2,000 动作、48 小时，取代官方停止标准）51.66 → **(iii) 连续对话**（最小 agent harness，连续会话 + 模型原生 compaction）65.82 → **(iv) 双笔记**（GUIDE.md + WORKING.md，并鼓励建立紧凑可复用的游戏模型）70.05 → **(v) 无损视觉记忆 + 模型引导的视觉检查** 94.10 → **(vi) 精确像素读出**（数值 RGB）99.00；配置 (i)–(iv) 按官方协议每次动作自动获得至多 7 帧，(v)–(vi) 改为只给最后一帧并可主动检视；论文注明 (i) 的低动作数部分源于许多 run 在完成游戏前即触及动作/时间上限 | arXiv §4.3 + 附录 A.2 + 图 5 题注 | ✅ P0 通过 |
| F-080 | 数字 | 成本与 token 口径（论文 §4.3）：每帧图像观测约 **308** 个图像 token，而等效 64×64 文本网格约 **4K** 文本 token；含 7 帧的请求约 28K token（文本）vs 约 2.2K（图像）；单局平均 token 用量 **71.9M**（文本网格）vs **30.7M**（图像观测）；**780K** 上下文为 105.7M token/局，**200K** 为 30.7M，降至 **100K** 时 RHAE 仅降 **0.4** 而 token 用量约减半；输入图像放大倍率 **4×** 比默认 **8×** 少用 **75%** 图像 token 且性能相当，**2×** 会降低性能 | arXiv §4.3 + 图 6b/图 7b | ✅ P0 通过 |
| F-081 | 数字 | 人类参考样本构成：GameWorld 的两名人类玩家**均为计算机科学研究生**，各自尝试全部 170 项任务，预算与智能体相同（每任务 100 个动作），其中一名新手此前无相关经验；BabyVision 人类准确率为 Maze 子类 **95.0%**、连线子类 **89.5%**，图 11 的 **92.3%** 为两子类按权重平均；AI GameStore 的人类参考来自 Prolific 参与者（平均年龄 38…），取人类中位数归一化为 100 | arXiv 附录 A.6 + §5.1 | ✅ P0 通过 |
| F-082 | 数字 | 官方项目页（2026-08-05 blogpost 版本）的数字与论文不同：Opus 5.0 共用 **7,542** 个动作、"**56%** fewer than humans"、GPT-5.6 Sol 平均局分 **98.27**、官方实现 Opus 5.0(high) 基线 **30.16** | vista-research.github.io 排行榜与说明 | ✅ P0 通过 |
| F-083 | 机制 | 工具集完整签名（附录 A.4 算法 1）：`inspect(question, views) -> images`，其中 `view = {label, turn, frame=final, region=full}`、`region = {x, y, w, h}`，每个 view 返回一张图；另有 `read_pixels`（返回选中像素的精确 RGB 数值）与 `history`（无损保存并允许 Agent 主动回看任意历史帧） | arXiv 附录 A.4 算法 1 + §3.1 | ✅ P0 通过 |
| F-084 | 事实 | ARC-AGI-3 基准规格与官方榜政策：每帧为 **64×64** 网格、每格取自 **16** 种颜色之一、每个环境**至少 6 关**、动作空间含 **Undo**（回到上一状态）；ARC Prize 明确 "we will **never report public set scores** of any system on the official leaderboard"、公开集评估 "is emphatically **not a valid measure of progress towards AGI**"、社区榜分数**自报且不予核验**，官方另开源一个以人类回放即可在全部公开环境上取得 100% 的 harness | arXiv:2603.24621 §2.3/§3.4/§4.3.1/§4.3.2 | ✅ P0 通过 |
| F-085 | 数字 | 论文图 11 与附录 B.1 的补充数值：GameWorld **进度**指标 VISTA 79.3%、官方实现 62.9%、新玩家 64.1%（此前最好 39.8%）；AI GameStore 三次运行的原始聚合值 **119.99 / 148.58 / 140.06**（对应正文的 140.3 为官方"先按局平均原始分再归一化聚合"协议下的代表值，波动约 ±14） | arXiv 图11 + 附录 B.1 | ✅ P0 通过 |
| F-086 | 事实 | 源码仓库坐标：`github.com/joshhhhhan/VISTA`，MIT License，**无任何 release tag**；提交历史仅 2 个（经 GitHub API 核验；本地为 depth=1 浅克隆，无法本地数出提交总数）：`900aa3380e4f1120436d83b2ce1115a38ac29bf9`（2026-09-05，Initial release）与 `c97c354f0a8948256545a3e8850a1848f8e5b8c1`（2026-10-04，update）。本束源码事实一律固定在后者 | GitHub API + 本地固定 commit | ✅ P0 通过 |
| F-087 | 数字 | 仓库规模（对固定 commit 脚本计数，排除 .git）：工作树文件 **104** 个，其中 `.py` **82**、`.sh` **8**、`.md` **5**、Dockerfile **2**；Python 总行数 **18,754**（`len(read().splitlines())` 求和） | 固定 commit 工作树脚本计数 | ✅ P0 通过 |
| F-088 | 数字 | 源码分层（同一计数口径）：`src/vista/core/` 14 个 .py / 3,647 行；`src/vista/backends/` 6 个 / 691 行；`src/vista/benchmarks/` 四个子包——arc3 7 个 / 1,291 行、aigamestore 6 个 / 1,546 行、babyvision 8 个 / 1,369 行、gameworld 9 个 / 1,308 行；`src/vista/` 根目录 3 个 .py（`__init__.py`、`__main__.py`、`cli.py`） | 固定 commit 脚本计数 | ✅ P0 通过 |
| F-089 | 数字 | 符号规模（AST 与正则双口径一致）：`def`/`async def` 定义 **705** 处（其中 `async def` **7** 处），去重函数名 **465** 个；`class` 定义 **90** 处，去重类名 **84** 个 | 固定 commit AST + 正则双口径 | ✅ P0 通过 |
| F-090 | 事实 | 打包与入口：`pyproject.toml` 声明包名 `vista-arc3`、版本 `0.1.0`、`requires-python = ">=3.12,<3.13"`、构建后端 setuptools；`[project.scripts]` 四个入口——`vista`=`vista.cli:main`、`vista-gameworld`=`vista.benchmarks.gameworld.cli:main`、`vista-aigamestore`=`vista.benchmarks.aigamestore.cli:main`、`vista-babyvision`=`vista.benchmarks.babyvision.cli:main` | src/vista/../pyproject.toml | ✅ P0 通过 |
| F-091 | 事实 | 运行依赖全部固定版本：`arc-agi==0.9.9`、`arcengine==0.9.3`、`numpy==2.5.1`、`pillow==12.2.0`、`python-dotenv==1.2.2`、`requests==2.34.2`、`urllib3==2.7.0`、`jsonschema>=4.23,<5`；可选 extras：gameworld（`playwright==1.45.0`、PyYAML、Jinja2）、aigamestore（`playwright==1.45.0`）、babyvision（`regex>=2024.11`，官方答案抽取依赖其递归分组）、dev（`ruff==0.16.3`） | pyproject.toml | ✅ P0 通过 |
| F-092 | 事实 | CLI 入口 `src/vista/cli.py`：`--profile` 必填，取值 `("arc3","gameworld","aigamestore","babyvision")`；`--backend` 必填，取值 `("codex","claude")`；**非 arc3 的 profile 强制要求 `--backend codex`**（否则 `parser.error`） | src/vista/cli.py:15-26 | ✅ P0 通过 |
| F-093 | 事实 | `--operation-mode` 三态 `offline`/`online`/`competition`（批量协调器 `arc3/batch.py`，默认 `competition`）；单局 harness 只接受 `online`/`offline`（默认 `online`）；`offline` 需通过 `ENVIRONMENTS_DIR` 供给本地游戏文件 | src/vista/benchmarks/arc3/batch.py:455-459；arc3/*/harness.py | ✅ P0 通过 |
| F-094 | 事实 | 官方端点与鉴权：`.env.example` 声明 `ARC_API_KEY` 与 `ARC_BASE_URL=https://three.arcprize.org`；非 offline 模式缺少 `ARC_API_KEY` 即报错终止；`.env` 另有可选的 `CLAUDE_CODE_OAUTH_TOKEN`（及为竞争模式池化的 `_2`/`_3` 变体） | .env.example；arc3/batch.py:921；arc3/*/harness.py | ✅ P0 通过 |
| F-095 | 事实 | VISTA 工具集恰为**八个**（`VISTA_TOOLS` 常量，gameworld 与 aigamestore 两个 profile 各自定义且内容一致）：`inspect`、`read_pixels`、`history`、`read_guide`、`write_guide`、`read_working`、`write_working`、`save_compact_checkpoint`；另有 ARC-AGI-3 专有的动作工具 `play`，合计九个 | src/vista/benchmarks/{gameworld,aigamestore}/profiles.py | ✅ P0 通过 |
| F-096 | 事实 | `inspect` 工具 schema：`question`（必填，字符串，1–1024 字符）与 `views`（必填数组，1–16 项）；每个 view 必填 `label`（1–128 字符）与 `turn`（0–999999），可选 `frame`（0–999999，缺省取该回合末帧）与 `region`（`{x,y,width,height}`，坐标上限 `display_size-1`） | src/vista/core/tools.py:62-127 | ✅ P0 通过 |
| F-097 | 事实 | `inspect` 的 region 与 ARC 的 ACTION6 **共用同一套 `display_size × display_size` 坐标系**（工具描述原文："select a rectangular region in the same standard {display_size}x{display_size} coordinates used by ACTION6"）；被裁剪区域按比例放大到 `display_size × display_size`，工具描述明示 "without smoothing"（即最近邻，不插值） | src/vista/core/tools.py:95-97；arc3/claude/tools.py:100-102 | ✅ P0 通过 |
| F-098 | 事实 | `read_pixels` 语义：把选定 region 等分为 `rows × columns` 格，**取每格中心像素**采样；输出为"一个 RGB 符号调色板 + 每采样行一条紧凑行字符串"；每次调用上限 64 个 view、合计 4096 个采样点；`rows`/`columns` 均为必填，上限 `display_size` | src/vista/core/tools.py:130-179；core/session.py:645-685 | ✅ P0 通过 |
| F-099 | 事实 | 像素读出为**量化**读出：`quantize_rgb(color, bits)` 把每个通道舍入到 `bits` 位精度，默认 `pixel_readout_color_bits = 4`（每通道 16 级）；调色板作用域默认 `pixel_readout_palette_scope = "call"`（每次调用重建），符号表 `PIXEL_READOUT_SYMBOLS` 长度 **64** | src/vista/core/support.py:43-59,69-70,523-560 | ✅ P0 通过 |
| F-100 | 事实 | `play` 工具（ARC-AGI-3）：**每次调用执行且仅执行一个游戏动作**，并计为一个 game action；返回结果含"动作后的最终画面、该动作归档的帧数、之后可用的动作集合"；模型观察该结果后才能执行下一次动作 | src/vista/benchmarks/arc3/claude/tools.py:86-104 | ✅ P0 通过 |
| F-101 | 事实 | ARC-AGI-3 动作集语义：`RESET` 初始化/重启；`ACTION1`–`ACTION4` 通常对应上/下/左/右；`ACTION5` 为交互类动作；`ACTION6` 为**坐标动作**（鼠标点击）；`ACTION7` 为 **Undo**；UI 绑定为 ACTION1=W/↑、ACTION2=S/↓、ACTION3=A/←、ACTION4=D/→、ACTION5=Space/F、ACTION6=鼠标点击、ACTION7=Ctrl/Cmd+Z | src/vista/benchmarks/arc3/claude/tools.py:92-102 | ✅ P0 通过 |
| F-102 | 事实 | 帧档案落盘命名：`visuals/turn_%06d_frame_0<ext>`（通用会话，落盘后 `chmod 0o400` 只读）与 `screenshots/turn_%03d_frame_%02d.png`（ARC-AGI-3 harness）；即论文所述"按回合号与帧号索引"的实现形式 | src/vista/core/support.py:297-301,114-115；arc3/claude/controller.py:801 | ✅ P0 通过 |
| F-103 | 事实 | 单局工作目录内容（`bind()` 建立）：`visuals/`（mode 0700）、`GUIDE.md`、`WORKING.md`（mode 0600）、`working_memory_provenance.json`、`compact_recovery.jsonl`，以及五个状态标记文件 `compact_checkpoint.requested`、`compact_checkpoint.ready`、`compact_restore.pending`、`compact_guide.snapshot`、`retry_boundary.pending`；`GUIDE.md` 初始内容为 `"No reliable model yet.\n"` | src/vista/core/support.py:112-125 | ✅ P0 通过 |
| F-104 | 事实 | `display_size` **由实际供给的画面尺寸推导**：`TaskContext` 取所有 visuals 的最大边长、缺省 1024；ARC-AGI-3 控制器取 `GRID_SIZE * render_scale`（64 × 8 = **512**），与论文的 512×512 一致；core 层 `DEFAULT_DISPLAY_SIZE = 1024` | src/vista/core/support.py:102-104；arc3/claude/controller.py:216；core/tools.py:13 | ✅ P0 通过 |
| F-105 | 事实 | 帧渲染为**最近邻放大**：`render_frame_image` 在 `scale != 1` 时用 `Image.Resampling.NEAREST` 放大；ARC-AGI-3 默认 `GRID_SIZE = 64`、`RENDER_SCALE = 8`、`DEFAULT_RENDER_GRID = True` | src/vista/benchmarks/arc3/render.py:37-39；arc3/claude/harness.py:58-61 | ✅ P0 通过 |
| F-106 | 事实 | ARC-AGI-3 16 色调色板：`palette.py` 的 `FALLBACK_COLOR_MAP` 把索引 0–15 映射为白/灰阶/黑/品红/粉/红/青/浅蓝/黄/橙/深红/绿/紫等十六色，`COLOR_MAP` 优先取 ARC SDK 的 `SDK_COLOR_MAP`，缺失时回落到该表 | src/vista/benchmarks/arc3/palette.py:16-37 | ✅ P0 通过 |
| F-107 | 事实 | 工具白名单：`core/dispatcher.py` 允许派发的工具集合为 `{"save_compact_checkpoint","inspect","read_pixels","history","play"}`，其余工具名不被派发；压缩边界后另有次序约束 | src/vista/core/dispatcher.py:91-97 | ✅ P0 通过 |
| F-108 | 事实 | 压缩策略**按后端分叉**：`CompactionMode` 枚举含 `native` 与 `checkpoint-handoff`；Claude 走 `run_task_with_native_context`（原生压缩，自动压缩窗口 1,000,000、90% 触发），Codex 走 `run_task_with_compact_checkpoints`（注入 `save_compact_checkpoint` 指令完成交接） | src/vista/core/profiles.py:26-28；backends/claude/lifecycle.py:30-40；backends/codex/lifecycle.py:34-44 | ✅ P0 通过 |
| F-109 | 数字 | Codex 侧压缩预算常量：`DEFAULT_MODEL_CONTEXT_WINDOW = 272000`（适用 `gpt-5.4/5.5/5.6-` 前缀）、`FALLBACK_MODEL_CONTEXT_WINDOW = 128000`、`CHECKPOINT_HARD_CONTEXT_RESERVE = 32000`、`CHECKPOINT_TURN_HEADROOM = 40000`、`MIN_NORMAL_AUTO_COMPACT_LIMIT = 16000` | src/vista/backends/codex/runner.py:44-49 | ✅ P0 通过 |
| F-110 | 事实 | 模型与推理强度默认值：Codex 侧 `DEFAULT_MODEL = "gpt-5.6-sol"`、`DEFAULT_REASONING_EFFORT = "max"`、`CODEX_EFFORT_LEVELS = ('minimal','low','medium','high','xhigh','max','ultra')`；Claude 侧 `DEFAULT_CLAUDE_MODEL = 'opus'`、`DEFAULT_CLAUDE_EFFORT = 'xhigh'`、`CLAUDE_EFFORT_LEVELS = ('low','medium','high','xhigh','max')`；竞争模式默认 Claude effort 为 `xhigh` | src/vista/benchmarks/arc3/codex/harness.py:54-56；backends/claude/runner.py:49-51；arc3/batch.py:74 | ✅ P0 通过 |
| F-111 | 数字 | ARC-AGI-3 回合上限：harness 的 `DEFAULT_MAX_STEPS = 2000`（与论文的"2,000 total actions"一致）、`DEFAULT_MAX_INVALID_RETRIES = 15` | src/vista/benchmarks/arc3/claude/harness.py:62-63 | ✅ P0 通过 |
| F-112 | 事实 | 25 个公开游戏的 ID 列表 `STANDARD_GAME_ORDER` 恰含 **25** 项：bp35、sk48、lf52、wa30、sp80、re86、su15、vc33、ka59、dc22、ls20、tn36、g50t、sc25、tu93、s5i5、cn04、tr87、ar25、m0r0、r11l、lp85、ft09、cd82、sb26 | src/vista/benchmarks/arc3/batch.py:77 | ✅ P0 通过 |
| F-113 | 事实 | 上游版本锚点：`arc3/profile.py` 固定 `RELEASE_REVISION = '900aa3380e4f1120436d83b2ce1115a38ac29bf9'`（仓库首个发布提交）；babyvision 固定 `BABYVISION_REVISION = '7f92fd4b1dc1c68b7b936a9bc09c68b4a944a55a'`；gameworld 固定 `GAMEWORLD_REVISION = 'f2883c34e377c8b73fdb503a4a8e87be12310df7'` 与 `GAMES_REVISION = 'a23b4370c3f99df6fa4ee01ea0299fdab9668b86'` | src/vista/benchmarks/arc3/profile.py:8；babyvision/dataset.py:21；gameworld/upstream.py:14-15 | ✅ P0 通过 |
| F-114 | 事实 | BabyVision 任务集：代码定义 `TASK_SETS = {'full','visual-tracking','tracking48'}`，默认 `DEFAULT_TASK_SET = 'tracking48'`（含 Maze、Connect the lines、Lines Observation 三子类）；README 给出复现论文 39 题的命令 `--subtypes 'Maze\|Connect the lines'` | src/vista/benchmarks/babyvision/dataset.py:32-45；README.md:184-188 | ✅ P0 通过 |
| F-115 | 事实 | AI GameStore 侧：`PUBLIC_GAMES = tuple(range(1, 11))`（10 个公开游戏）、`normalized_score(raw_score, human_median)` 实现"按人类中位数归一化"、`PROTOCOL = 'aigamestore-segmented-input'`、`SEGMENTS_PER_DECISION = 5`、`SEGMENT_SECONDS = 0.2`、`MAX_DECISIONS = 120` | src/vista/benchmarks/aigamestore/environment.py:35-39,295-315 | ✅ P0 通过 |
| F-116 | 事实 | GameWorld 侧：`PRIMARY_STEPS = 100`（每任务 100 步预算，与论文"人类每任务 100 动作预算"一致）、`COMPUTER_USE_PROTOCOL = 'gameworld-computer-use'` | src/vista/benchmarks/gameworld/upstream.py:16-17 | ✅ P0 通过 |
| F-117 | 事实 | MCP 与凭证隔离：Claude 后端通过 MCP（`SERVER_NAME = 'game'`、`DEFAULT_PROTOCOL_VERSION = '2025-06-18'`）把工具暴露给 CLI；`FORBIDDEN_SUBPROCESS_CREDENTIALS = ('CLAUDE_CODE_OAUTH_TOKEN','ANTHROPIC_API_KEY','ARC_API_KEY')` 明确禁止把凭证带入子进程 | src/vista/backends/claude/mcp_bridge.py:12-15 | ✅ P0 通过 |
| F-118 | 事实 | 核心提示词（`core/prompts/claude.md`）全文三句契约："Build and use a compact, revisable model of the game and its current state. Update it as new evidence changes what is supported." / "Before each registered game action, briefly state what you expect to see. Afterward, briefly state all visible changes, expected or not." / "Keep concise, durable, revisable game understanding in `GUIDE.md`; use `WORKING.md` as a scratchpad when useful." | src/vista/core/prompts/claude.md:1-7 | ✅ P0 通过 |
| F-119 | 事实 | 恢复与终止：`INFRASTRUCTURE_TERMINATION_REASONS` 共 5 项（compact_recovery_failed、controller_error、environment_response_missing、retry_boundary_interrupt_failed、visual_transport_failed）；`MAX_COMPACT_CYCLES_WITHOUT_ACTION = 3`、`MAX_RUNTIME_RECOVERIES_PER_STEP = 8`、`MAX_DECISION_LEASE_RECOVERIES_PER_STEP = 5`、`PROVIDER_5XX_BACKOFF_SECONDS = (10,30,60,120)`、`CAPACITY_RETRY_DELAYS = (10.0,20.0,40.0)` | src/vista/benchmarks/arc3/claude/harness.py:71；backends/claude/lifecycle.py:12-21；backends/session.py:16 | ✅ P0 通过 |
| F-120 | 事实 | 环境超时：`ENV_CONNECT_TIMEOUT_SECONDS = 10`、`ENV_READ_TIMEOUT_SECONDS = 120`、`ENV_CONNECT_RETRIES = 3`、`MAX_TASK_TIMEOUT_SECONDS = 2000000`；`ArcHTTPAdapter` 的 docstring 为 "Use fresh connections and never replay a submitted game action." | src/vista/core/timeouts.py:3-6；arc3/http.py:17-32 | ✅ P0 通过 |
| F-121 | 事实 | `save_compact_checkpoint` 的职责划分（工具描述原文）："replacement GUIDE.md only when the durable game model materially changed; continuation state that cannot be recovered from GUIDE.md and the current ..."——即**仅在持久模型实质变化时才替换 GUIDE.md**，其余交接状态写入 WORKING.md | src/vista/core/tools.py:237-243 | ✅ P0 通过 |
| F-122 | 事实 | 压缩后强制次序：`core/dispatcher.py` 在压缩边界后要求先调用 `save_compact_checkpoint`（"Save the compact checkpoint before using another tool."），否则拒绝其他工具 | src/vista/core/dispatcher.py:65-74 | ✅ P0 通过 |
| F-123 | 事实 | 论文三组件与源码的对应：visual observations ↔ ARC 控制器每回合渲染帧；lossless visual memory ↔ `visuals/` 帧档案；visual inspection ↔ `inspect`/`read_pixels`/`history` 三工具 | 论文 §3.1 + 源码交叉 | ✅ P0 通过 |
| F-124 | 事实 | 论文附录 A.4 算法 1 的 `inspect(question, views) -> images` 与源码签名一致；`view = {label, turn, frame=final, region=full}`、`region = {x,y,w,h}` 四个字段在源码 schema 中逐字段对应，且源码额外给出取值上限（label 128 字符、question 1024 字符、views 16 项） | 论文附录 A.4 + src/vista/core/tools.py:62-127 | ✅ P0 通过 |
| F-125 | 事实 | 论文 §4.3 六步消融与源码配置的对应：(i) 图像观测 ↔ `render_frame_image`；(ii) 动作/时间上限 ↔ `DEFAULT_MAX_STEPS = 2000`；(iii) 连续对话 ↔ `run_task_with_native_context` / `run_task_with_compact_checkpoints`；(iv) 双笔记 ↔ 四个 read/write 工具 + `GUIDE.md`/`WORKING.md`；(v) 无损记忆 + 视觉检查 ↔ `visuals/` 档案 + `inspect`/`read_pixels`；(vi) 精确像素读出 ↔ `read_pixels` | 论文 §4.3 + 源码交叉 | ✅ P0 通过 |
| F-126 | 事实 | ARC-AGI-3 动作空间的**准确口径**（更正）：ARC-AGI-3 技术报告 §2.3.2 原文为 "Each environment offers a different action space, which is a subset of: Five key actions, plus an Undo action (reverting to the previous state); One action to select (e.g. click on) a cell from the 64x64 grid by specifying its coordinates"——即除五个关键动作与 Undo 外，**还有一类坐标选择动作**；本束先前 F-084 遗漏该类 | arXiv:2603.24621 §2.3.2 | ✅ P0 通过（勘误 E-10） |
| F-127 | 事实 | 论文与源码的上下文口径不一致：论文 §4.3 称消融默认 200K 上下文，源码 `DEFAULT_MODEL_CONTEXT_WINDOW = 272000`（回落 128000），二者口径不同，引用时须注明来源 | 论文 §4.3 + src/vista/backends/codex/runner.py:44-45 | ✅ P0 通过（勘误 E-11） |
| F-128 | 事实 | `save_compact_checkpoint` 在源码中是**跨后端通用工具**（属八件套之一），而 Claude 与 Codex 用**不同机制**触发它（原生压缩 vs 注入式交接指令）——论文 §3.2 未区分这一点 | src/vista/core/profiles.py:26-28；backends/{claude,codex}/lifecycle.py | ✅ P0 通过 |
| F-129 | 事实 | 论文谱系坐标：VISTA 论文 arXiv:2610.02200（2026-10-01）；ARC-AGI-3 技术报告 arXiv:2603.24621；GameWorld（ECCV 2026）；AI GameStore arXiv:2602.17594；BabyVision（ICML 2026）；Anthropic harness 博文 2025-11-26；VISTA 项目页 blogpost 2026-08-05 | 各文献原始出处 | ✅ P0 通过 |
| F-130 | 事实 | 源码覆盖面边界：源码只覆盖 25 个公开局（`STANDARD_GAME_ORDER` 与 `ArcHTTPAdapter` 均无私有/半私有集适配）；BabyVision 默认任务集 `tracking48`（48 题、三子类）多于论文评估的 39 题（Maze + Connect the lines 两子类） | src/vista/benchmarks/arc3/batch.py:77；babyvision/dataset.py:32-45 | ✅ P0 通过 |
| F-131 | 事实 | 契约层构成（`core/contracts.py`）：9 个冻结 dataclass——`Visual`:44、`Observation`:94、`ObservationBundle`:117、`PublicTask`:173、`ToolSpec`:186、`ToolReply`:258、`ToolBinding`:283、`SubmissionSpec`:289、`ToolExecution`:323；3 个 StrEnum——`Effect`:18、`Capability`:26、`EvidenceKind`:37 | src/vista/core/contracts.py | ✅ P0 通过 |
| F-132 | 事实 | 固定版本与镜像常量：`PINNED_CLAUDE_VERSION = '2.1.220'`（backends/claude/runner.py:45）与 `DEFAULT_PINNED_CLAUDE_BIN`（:46）、`PINNED_CODEX_CLI_VERSION = 'codex-cli 0.145.0'`（backends/codex/runner.py:27）与 `DEFAULT_PINNED_CODEX_BIN`（:28）、`PLAYER_IMAGE` 分别为 `'arc3-claude-player:0.1'`（claude/runner.py:41）与 `'arc3-codex-player:0.1'`（codex/runner.py:22） | backends/{claude,codex}/runner.py | ✅ P0 通过 |
| F-133 | 数字 | 并发与调度默认值（`arc3/batch.py:71-75`）：`DEFAULT_CONCURRENCY = 2`、`DEFAULT_CLAUDE_CONCURRENCY = 2`、`DEFAULT_CLAUDE_WORKERS_PER_ACCOUNT = 2`、`SCHEDULER_POLL_SECONDS = 5.0` | src/vista/benchmarks/arc3/batch.py | ✅ P0 通过 |
| F-134 | 事实 | 竞争模式相关符号：`CompetitionConfig`:107、`CompetitionGameResult`:122、`ClaudeAccountSchedule`:129、`RuntimeProbeController`:133、`CompetitionEnvironmentFactory`:404、`claude_worker_slots`:262、`claude_account_schedule`:286、`pop_claude_scheduled_game`:306（arc3/batch.py）；`ClaudeRateLimitEvent`:16、`ClaudeCredentialLease`:52、`ClaudeCredentialPool`:86、`rate_limit_event_from_message`:33、`DEFAULT_DRAIN_UTILIZATION = 0.9`、`DEFAULT_CAPACITY_POLL_SECONDS = 5.0`（backends/claude/quota.py） | src/vista/benchmarks/arc3/batch.py；backends/claude/quota.py | ✅ P0 通过 |
| F-135 | 事实 | `history` 工具存在**两套语义不同的实现**：通用 `TaskContext._history_reply`（core/support.py:664）参数为 `start`/`end`/`limit`，返回 `{"events": [...], "truncated": bool}`；ARC-AGI-3 控制器 `_history`（arc3/claude/controller.py:576）参数为 `view`（**必填**，取值 `attempts`/`events`）+ `start_turn`/`end_turn`/`limit`。`attempts`/`events` 视图选择器仅 ARC-AGI-3 具备，`start`/`end` 区间参数仅通用实现具备 | src/vista/core/support.py:664；arc3/claude/controller.py:576 | ✅ P0 通过（勘误 E-15） |
| F-136 | 事实 | AI GameStore 动作集：`KEY_VALUES` 含 **11** 项（UP、DOWN、LEFT、RIGHT、SPACE、Z、SHIFT、W、A、S、D），据此派生 `TAP_ACTIONS` 11 项、`HOLD_ACTIONS` 11 项、`MODEL_ACTIONS` 23 项（并入 `NOOP`） | src/vista/benchmarks/aigamestore/environment.py:46-61 | ✅ P0 通过（勘误 E-16） |
| F-137 | 数字 | 人类参考样本量：GameWorld 为**两名**计算机科学研究生（其中一名新手），各自尝试全部 170 项任务、预算每任务 100 动作；BabyVision 为 **16 名**成人（Maze 95.0%、连线 89.5%、加权 92.3%）；AI GameStore 为 **106 名** Prolific 参与者（平均年龄 38…），取人类中位数 | arXiv:2603.24621 附录 A.6 与论文 §5.1/附录 A.6 | ✅ P0 通过 |
| F-138 | 数字 | ARC-AGI-3 逐局动作数示例：论文表 2 中 `ar25` 为 **256** 个动作（公开局中动作数最多者之一），对应源码 `STANDARD_GAME_ORDER` 中的 `ar25` | arXiv:2610.02200 表 2 | ✅ P0 通过 |
| F-139 | 事实 | BabyVision 答案与评测协议：`ANSWER_TYPES = ('blank','choice')`；`EVALUATOR = 'last-boxed-answer + normalized-exact-match; official llm-judge as a separate labeled step'`；官方答案抽取依赖 `regex` 引擎的递归分组（故 babyvision extra 固定 `regex>=2024.11`） | src/vista/benchmarks/babyvision/dataset.py:28；babyvision/profiles.py:21-24 | ✅ P0 通过 |
| F-140 | 事实 | `validate_palette_indices` 对越界颜色索引抛出异常（arc3/palette.py:59） | src/vista/benchmarks/arc3/palette.py | ✅ P0 通过 |

## 四、勘误说明（源文与论文/权威源的差异）

- **E-1（组件名译法，⚠️ 轻微）**：博文称第三组件为"主动视觉检查"，论文 §3.1 的**组件名**是 "visual inspection"（视觉检查），图 3c 作 "model-directed visual inspection"。
  - **须精确区分**：论文确实使用 actively 一词——§3.1 "we provide the agent with tools to **actively inspect** visual information in space and across time"，摘要 "The model can **actively retrieve** these observations"。因此"主动"并非杜撰，问题只在于**组件名**的译法与论文原词不一致（博文的"主动视觉检查"读起来像论文的组件名）。
  - **处置**：正文一律按论文组件名呈现，并在首处标注博文用词，不宣称"论文未用主动"。
- **E-2（归因越界，⚠️ 需修正）**：博文把"去年 11 月 Anthropic 介绍 Harness"作为 VISTA 的直接脉络前史叙述。Anthropic 该文确实存在且日期为 2025-11-26（对应博文"去年 11 月"，成立），但 **VISTA 论文并未引用该文**，其 64 条参考文献中唯一的 Anthropic 出处是 Claude Opus 5 模型公告。博文的"脉络承接"是作者的叙事关联，不是论文主张。正文须区分"博主叙述的脉络"与"论文实际引用"。
- **E-3（关键局限缺失，❌ 重大）**：博文完全没有提及论文 §6 的局限——所用模型在公开基准之后发布，无法排除这些游戏已被纳入训练数据；作者明确指出需在 ARC-AGI-3 私有集上评估才是更强的泛化检验。这是解读"满分 100"时不可省略的前提，正文必须补入并置于显著位置。
- **E-4（数字口径省略，⚠️ 需补充）**：博文给出"57.4%"与"99"但未说明多次运行波动。论文附录 B.1 显示 GameWorld 成功率 63.33±2.37%、BabyVision 准确率 63.23±3.00%、ARC-AGI-3 Sol 99.04±0.17。正文补入方差口径。
- **E-5（基线遗漏，⚠️ 需补充）**：博文只说"满分 100"，未给出官方实现的基线值。论文表 1 给出官方实现的 Opus 5.0 RHAE 为 40.68、GPT-5.6 Sol 为 13.33，正文须呈现基线→VISTA 的提升幅度，否则"满分"缺乏参照系。
- **E-6（评测范围补充，⚠️ 信息补全而非纠错）**：博文原文已写"在 BabyVision **选取的** 39 道迷宫与连线题上"，本身已把 39 限定为所选子集，**不构成误读**。本项的实际价值是补上被省略的全集规模：BabyVision 为 388 项任务 / 22 个子类，VISTA 评估其中 39 题（20 迷宫 + 19 连线）。正文按论文精确表述。
- **E-7（遗漏开源资产，⚠️ 需补充）**：博文未提 VISTA 代码已开源（MIT License，github.com/joshhhhhan/VISTA）及运行环境要求。正文补入，这是读者可行动性最高的信息。
- **E-15（工具语义，⚠️ 需分述）**：本束曾把 `history` 合并描述为"`attempts`/`events` 视图 + `start`/`end` 区间"。源码实为**两套语义不同的实现**——通用 `TaskContext._history_reply`（`core/support.py:664`）用 `start`/`end`/`limit`，返回 `{"events": [...], "truncated": bool}`；ARC-AGI-3 控制器 `_history`（`arc3/claude/controller.py:576`）用**必填** `view`（`attempts`/`events`）+ `start_turn`/`end_turn`/`limit`。`attempts`/`events` 选择器仅 ARC-AGI-3 具备，`start`/`end` 区间参数仅通用实现具备（ARC-AGI-3 用 `start_turn`/`end_turn`）[F-135]。正文已拆为两行分别说明。
- **E-16（计数，⚠️ 需更正）**：本束曾写 AI GameStore 动作为"10 个按键"。源码 `KEY_VALUES` 实为 **11** 项（UP、DOWN、LEFT、RIGHT、SPACE、Z、SHIFT、W、A、S、D），派生 `TAP_ACTIONS` 11、`HOLD_ACTIONS` 11、`MODEL_ACTIONS` **23**（并入 `NOOP`）[F-136]。正文已更正。
- **E-8（项目页未链接 arXiv，⚠️ 时序）**：官方项目页 vista-research.github.io 标注 "Aug 5, 2026" 且未链接 VISTA 的 arXiv（arXiv 上线为 2026-10-01）；arXiv 摘要 Comments 字段记载"本稿早期版本曾发布于 2026-08-05 的 blogpost"。项目页与论文的数字存在系统性差异（项目页：7,542 动作 / 56% / Sol RHAE 98.27 / 官方基线 30.16；论文：7,302 / 57.4% / 99.00 / 40.68）。本束一律以**论文口径**为准，并标注项目页差异来源。

## 五、单一信源 / 弱信源提示

- F-013、F-033、F-035、F-041 为作者观点，仅单源（量子位博文），核验级别 P2，不作事实结论使用。
- F-043、F-044 的作者身份描述经 MIT ORC 名录、作者个人主页、MIT CSAIL 名录交叉核验；其中 Qiushi Han 在 MIT ORC 名录上以 "Josh Han" 登记（邮箱 joshhan@mit.edu 与论文通讯邮箱一致）。
- 论文称三位共同第一作者（co-first authors），项目页渲染为 co-leads，属同一事实的两种表述。
- 博文作者署名"henry（发自 凹非寺）"为量子位惯用署名，页面 `nick_name` 在 HTML 中为 GBK 编码，解析得到"量子位"，账号别名为 `QbitAI`。
- 本束不收录 ARC-AGI-3 私有/半私有游戏环境（不在任何公开仓库中，需 API key 授权获取），仅引用其公开构成数据。
