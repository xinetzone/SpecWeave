---
title: "planning-with-files:像 Manus 一样工作 - 深度洞察分析报告"
date: 2026-07-06
source: "微信公众号《叽半斤》文章《planning-with-files:像 Manus 一样工作》"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/analyze-planning-with-files-article/analysis-report.toml"
type: "方法论分析报告"
tags:
  - planning-with-files
  - context-engineering
  - ai-agent
  - manus
  - hooks
  - 3-file-pattern
  - specweave-comparison
  - context-window
  - 文件系统外存
  - 工程化方法论
---
# planning-with-files:像 Manus 一样工作 - 深度洞察分析报告

## 一、基本信息

| 字段 | 内容 |
|---|---|
| 文章标题 | planning-with-files:像 Manus 一样工作 |
| 来源 | 微信公众号《叽半斤》 |
| 作者 | 叽半斤 |
| 发布时间 | 2026 年 1 月(项目开源后即时撰写,具体日期文章未标注) |
| 项目地址 | https://github.com/OthmanAdi/planning-with-files |
| GitHub Star | 23,000+(截至文章撰写时,仍在快速增长) |
| 许可证 | MIT(完全免费,可商用) |
| 项目作者 | OthmanAdi |
| 关联事件 | 2025 年 12 月 Meta 以 20 亿美元收购 Manus(8 个月营收破亿) |
| 文章主旨 | 介绍 planning-with-files 开源项目,萃取 Manus"上下文工程"方法论 |
| 文章篇幅 | 九章节,约 2400 字(已用 defuddle 提取) |

---

## 二、核心观点

### 2.1 主论点

> **AI Agent 的瓶颈,不在模型能力,而在工程化方法。**

文章通过 planning-with-files 这个 24 小时内爆火的开源项目,论证了一个反直觉的判断:在 AI Agent 时代,决定生产力的不是模型参数大小,而是"如何让 AI 记得住、不跑偏、不重复犯错"的工程化方法。Manus 估值 20 亿美元,本质是为这一基础但关键的工程化问题给出了朴素而有效的答案。

### 2.2 三层支撑论点

**痛点层(Why necessary):** Context Window 是 AI 的"金鱼记忆"——TodoWrite 会消失、50 次工具调用后目标漂移、失败不记录导致重复犯错、上下文越塞越慢。这不是模型不够聪明,而是工作内存的根本性限制。

**方案层(How solved):** 3-File Pattern 将易失的 RAM 映射为持久的 Disk——`task_plan.md`(跟踪阶段进度)/`findings.md`(存储研究发现)/`progress.md`(会话日志测试结果),任何重要的东西都写到磁盘上。

**升华层(Why valuable):** Manus 值 20 亿美元不是因独家模型,而是因解决了"让 AI 记得住、不跑偏、不重复犯错"这一基础关键问题。文件系统作为 AI 外接硬盘的工程化思路,具有跨模型、跨工具、跨场景的通用价值。

---

## 三、论证逻辑分析

### 3.1 论证结构链条

文章采用"痛点共情 → 失败模式归纳 → 方案呈现 → 原理升华 → 自动化机制 → 安装落地 → 实测验证 → 适用边界 → 社区生态 → 总结升华"的十段式论证结构,逻辑递进清晰:

```
[共情引入] AI 改项目改到一半问"你要做什么来着"
      ↓
[痛点归纳] Context Window 4 类失忆表现
      ↓
[方案呈现] 3-File Pattern 三文件职责划分
      ↓
[原理升华] Context=RAM, Filesystem=Disk
      ↓
[自动化] Hooks 6 动作 + 4 大规则(给 AI 装项目经理)
      ↓
[安装落地] 5 种 IDE 安装方式(5 分钟装上外接大脑)
      ↓
[实测验证] 21 轮对话、15 分钟、目标清晰 vs 不用则第 15 轮遗忘
      ↓
[适用边界] 3 步以上/研究/构建/跨工具用,简单问题不用
      ↓
[社区生态] 4 个 fork 扩展 + 中文双语 Skill 管理器
      ↓
[总结升华] 工程化 > 模型能力,5 分钟装上让 AI 更靠谱
```

### 3.2 论证质量评估

**论据充分性:**
- 痛点描述有具体场景支撑(AI 改项目忘目标、10 步任务忘第 1 步、API 报错 3 次相同重试),共情力强
- 方案呈现结构化(三文件职责明确、原理映射直观)
- 实测有量化数据(21 轮对话、15 分钟、第 15 轮遗忘阈值)
- 安装方式覆盖 5 种主流 IDE,可验证性强

**逻辑跳跃识别:**
- ⚠️ **20 亿美元估值归因单一方法论(过度简化):** 文章将 Manus 的 20 亿美元估值归因于"上下文工程"方法论,但实际收购估值通常综合考量团队人才、技术专利、产品用户、品牌价值、战略协同等多重因素。这是文章最大的逻辑跳跃。
- ⚠️ **"24 小时爆火"传播逻辑未深入:** 23k Star 的传播路径(初始引爆点、KOL 转发节点、社区扩散机制)未做分析,仅陈述结果。
- ⚠️ **Manus 原话引用无来源标注:** "Markdown 是我磁盘上的工作内存"这段引用未标注出处(官方博客/采访/内部文档),溯源困难。

**反例缺失:**
- 未呈现 planning-with-files 失效的场景(如超大规模项目文件过多导致信息过载)
- 未与同类上下文工程方案对比(如 Mem0、Letta、LangGraph 的持久化机制)
- 实测样本单一(仅一个技术预研任务,缺乏跨场景统计)

### 3.3 痛点场景化描述的有效性

文章开篇三个场景(AI 改项目忘目标、10 步任务忘第 1 步、API 报错 3 次相同重试)极具共情力,直接命中 AI 编程用户的真实痛点。这种"先共情后方案"的写作策略,是技术传播类文章的高效范式——比抽象描述"Context Window 限制"有效得多。

---

## 四、信息结构与内容价值

### 4.1 九章节组织方式

| 章节 | 功能 | 内容层次 |
|---|---|---|
| 一、AI Agent 最大的痛点 | 痛点共情 | 引入+场景化 |
| 二、planning-with-files 介绍 | 方案呈现 | 项目+Slogan+原理 |
| 三、它到底怎么工作 | 机制解析 | Hooks 6 动作+4 规则 |
| 四、安装方法 | 落地指引 | 5 种 IDE 适配 |
| 五、实测对比 | 效果验证 | 用/不用对比量化 |
| 六、什么时候用 | 适用边界 | 用/不用场景 |
| 七、社区生态 | 价值扩散 | fork 扩展+双语管理器 |
| 八、写在最后 | 总结升华 | 工程化>模型能力 |

> 注:文章正文实际为八章节,文章开篇还有一个引子段(Meta 收购 Manus 背景)。整体结构符合"引入→痛点→方案→机制→落地→验证→边界→生态→升华"的九段式逻辑。

### 4.2 内容层次评估

**优点:**
- 章节递进符合人类认知节奏(从共情到原理到落地)
- 每章有明确的"信息密度峰值"(第二章原理映射、第三章 Hooks 6 动作、第五章实测对比)
- 引用块(Manus 原话)、代码块(安装命令)、列表(痛点/规则/安装方式)交替使用,可读性强

**不足:**
- 第三章(Hooks 机制)与第二章(项目介绍)信息密度重叠,可合并
- 缺少"常见问题 FAQ"章节(如:跨任务文件如何清理、Hooks 误触发如何处理)
- 缺少"与其他上下文工程方案对比"章节

---

## 五、关键知识点萃取

### 5.1 Context Window 痛点(4 类失忆表现)

| 痛点 | 表现 | 根因 |
|---|---|---|
| TodoWrite 消失 | 任务清单在上下文重置时丢失 | TodoWrite 存于易失 RAM |
| 目标漂移 | 50 次工具调用后忘了最初目标 | 长对话挤压早期上下文 |
| 失败不记录 | 同样错误重复犯 | 失败经验未持久化 |
| 上下文塞满 | 有用/无用信息混杂,越跑越慢 | 无差异化保留所有内容 |

### 5.2 3-File Pattern 三文件职责

| 文件 | 职责 | 类比 |
|---|---|---|
| `task_plan.md` | 跟踪任务阶段和进度 | 项目计划表 |
| `findings.md` | 存储研究发现和关键信息 | 研究草稿本 |
| `progress.md` | 会话日志和测试结果 | 工作日志 |

### 5.3 核心原理映射

> **Context Window = RAM(易失的、有限的)**
> **Filesystem = Disk(持久的、无限的)**
> **任何重要的东西,都写到磁盘上。**

Manus 原话:"Markdown 是我磁盘上的工作内存。由于我迭代处理信息,且活跃上下文有限,Markdown 文件充当笔记的草稿本、进度的检查点、最终交付成果的构建块。"

### 5.4 Hooks 6 个自动动作

| 序号 | 动作 | 触发时机 | 价值 |
|---|---|---|---|
| 1 | 创建 task_plan.md | 开始复杂任务前 | 强制计划先行 |
| 2 | 重新读取计划 | 每次重大决策前 | 防止目标漂移 |
| 3 | 更新进度 | 每个阶段完成后 | 进度可视化 |
| 4 | 存储发现 | 研究结果产生时 | 释放上下文压力 |
| 5 | 记录错误 | 失败发生时 | 避免重复踩坑 |
| 6 | 验证完成度 | 停止前 | 防止半成品交付 |

### 5.5 4 大核心规则

1. **先建计划再开工** —— 没有 task_plan.md 不许开始
2. **2-Action 规则** —— 每 2 次查看/浏览操作后,必须把发现存到文件
3. **记录所有错误** —— 它们帮助你避免重复
4. **绝不重复失败** —— 记录尝试,改变方法

### 5.6 5 种安装方式

| 方式 | 适用场景 | 命令/操作 |
|---|---|---|
| Claude Code 插件(推荐) | Claude Code 用户 | `/pluginmarketplace add OthmanAdi/planning-with-files` + `/plugininstall planning-with-files@planning-with-files` |
| 手动 clone | 单项目集成 | `git clone https://github.com/OthmanAdi/planning-with-files.git .claude/plugins/planning-with-files` |
| Git 子模块 | 多项目复用 | `git submodule add https://github.com/OthmanAdi/planning-with-files.git .claude/plugins/planning-with-files` |
| Legacy Skills | 旧版 Claude Code | `cp -r planning-with-files/skills/* ~/.claude/skills/` |
| Cursor/其他 IDE | Cursor/Continue/Codex/Gemini/Kiro/OpenCode/CodeBuddy/Pi | 复制对应 IDE 配置目录(如 `.cursor/`) |

> 注:Cursor 不支持自动 Hooks,但核心文件规划工作流完全适用。

### 5.7 社区生态

| Fork 项目 | 差异化定位 |
|---|---|
| devis | 面试优先工作流 |
| multi-manus-planning | 多项目并行支持 |
| plan-cascade | 多级任务编排、并行执行、多 Agent 协作 |
| agentfund-skill | AI Agent 众筹,里程碑托管 |
| buzhangsan/skill-manager | 中文双语 Skill 管理器,收录 31,000+ Claude Code Skill,planning-with-files 推荐安装第一位 |

---

## 六、可靠性、时效性与专业性评估

### 6.1 项目真实性

- ✅ **GitHub 仓库存在性:** `OthmanAdi/planning-with-files` 仓库链接格式规范,符合 GitHub 命名约定
- ⚠️ **23k Star 数据:** 文章撰写时点数据,无法独立验证当前 Star 数;但"24 小时爆火"+"23k Star"在 AI Agent 赛道热度下具有合理性
- ✅ **MIT 协议:** 开源友好,可商用,符合传播逻辑
- ⚠️ **作者权威性:** OthmanAdi 在 AI Agent 社区的地位、与 Manus 团队的关系文章未交代,需独立核实

### 6.2 Manus 收购事件真实性

- ⚠️ **Meta 2025 年 12 月 20 亿美元收购 Manus:** 文章作为开篇背景陈述,未提供官方公告链接或权威媒体来源。需通过 Meta 官方公告、彭博/路透等权威媒体独立验证。
- ⚠️ **8 个月营收破亿:** 同上,需独立验证。
- ℹ️ **方法论归因:** 即使 Manus 收购事件为真,"上下文工程"是否为其核心估值支撑,需 Manus 官方技术博客或收购方公告佐证。

### 6.3 归因合理性

- ⚠️ **过度简化风险:** 将 20 亿美元估值归因于单一"上下文工程"方法论,忽略了团队人才、产品用户、品牌价值、战略协同等综合估值因素。这是技术传播类文章的常见修辞手法(用单一原因解释复杂结果以增强传播力),但作为方法论分析,需保持审慎。
- ✅ **方法论本身有价值:** 即使归因简化,3-File Pattern 与 Hooks 机制作为工程化方案,具有独立的方法论价值,不依赖于 Manus 估值的真实性。

### 6.4 内容时效性

- 📅 **项目发布:** 2026 年 1 月,距今约 6 个月,处于活跃期
- 📅 **AI Agent 工具演进:** Claude Code、Cursor、Trae 等工具在 2026 年上半年快速迭代,Context Window 限制部分缓解(如 Claude Sonnet 4.5 的 1M context),但根本性限制仍在
- 📅 **方法论长效性:** "Context=RAM, Filesystem=Disk"的映射原理具有跨模型、跨工具的长效性,即使 Context Window 扩大,文件系统持久化仍是更可靠的工程化方案

### 6.5 技术专业性

- ✅ **概念深度:** Context Window、Hooks、2-Action 规则等概念表述准确,符合 Claude Code 官方文档语义
- ✅ **实践可行性:** 5 种安装方式覆盖主流 IDE,命令格式规范,可复现
- ⚠️ **Hooks 实现细节缺失:** 文章未深入 Hooks 的技术实现(如 PreToolUse/PostToolUse 钩子类型、Hook 脚本编写规范、Hook 失败回退机制)
- ⚠️ **"50 次工具调用后目标漂移"阈值:** 此数据未标注来源(Claude Code 官方文档/社区实测/作者经验),需审慎对待

---

## 七、与 SpecWeave 实践对照分析

### 7.1 机制对照表

| planning-with-files 机制 | SpecWeave 实践 | 异同点 |
|---|---|---|
| **3-File Pattern** | | |
| `task_plan.md`(任务计划) | `tasks.md`(任务清单) | **同:** 均跟踪任务进度,使用复选框可视化<br>**异:** SpecWeave 还有 `spec.md`(需求规格)与 `checklist.md`(验收清单),职责切分更细 |
| `findings.md`(研究发现) | `spec.md`(需求与方案) | **同:** 均存储研究/分析结论<br>**异:** SpecWeave 的 spec 包含 Why/What/Impact/Requirements 完整结构,比 findings 更结构化 |
| `progress.md`(会话日志) | `checklist.md`(验收清单) | **同:** 均记录执行过程与验证结果<br>**异:** SpecWeave 的 checklist 是验收门禁,planning-with-files 的 progress 是会话日志,前者更强调"完成度验证" |
| (无对应) | `README.md`(执行摘要) | **SpecWeave 独有:** 原子化复盘四文件结构包含 README 作为入口摘要 |
| **Hooks 6 动作** | | |
| 创建 task_plan.md | Spec 模式协议(先 spec 后 implementation) | **同:** 均强制"先计划后执行"<br>**异:** SpecWeave 通过启动协议+阶段守卫显式约束,planning-with-files 通过 Hook 自动触发 |
| 重读计划 | 启动协议步骤 2 + [前置文档强制读取协议](../../../../.agents/protocols/pre-document-reading.md) | **同:** 均在重大决策前重读规范<br>**异:** SpecWeave 有 PDR-LOG 结构化日志,planning-with-files 依赖 Hook 自动重读 |
| 更新进度 | checklist.md 复选框勾选 | **同:** 均通过复选框可视化进度<br>**异:** SpecWeave 需手动维护,planning-with-files 通过 Hook 自动更新 |
| 存储发现 | spec.md 更新 + docs/knowledge/ | **同:** 均将研究发现持久化<br>**异:** SpecWeave 有完整知识库体系,planning-with-files 单文件存储 |
| 记录错误 | [复盘体系](../../../../docs/retrospective/) + SG-LOG/PDR-LOG | **同:** 均记录失败经验<br>**异:** SpecWeave 有 136+ 份专项复盘报告与结构化日志,planning-with-files 单文件记录 |
| 验证完成度 | [阶段守卫](../../../../.agents/rules/stage-guardrails.md)跨阶段拦截 | **同:** 均防止半成品交付<br>**异:** SpecWeave 有 8 阶段权限矩阵+SG-LOG,planning-with-files 通过 Hook 自动检查 |
| **4 大核心规则** | | |
| 先建计划再开工 | Spec 模式协议(先 spec 后 implementation) | **同源:** 均为"先设计后编码"工程原则的 AI 化 |
| 2-Action 规则 | [上下文路由表](../../../../.agents/context-routing.md)(强制读规范) | **同:** 均强制"操作后落盘"<br>**异:** SpecWeave 强制"读规范",planning-with-files 强制"写发现",方向相反但目的一致(避免上下文浪费) |
| 记录所有错误 | [修复即闭环规则](../../../../.agents/global-core-rules.md)(修复→预防→闭环) | **同:** 均要求失败经验沉淀<br>**异:** SpecWeave 要求"修复即闭环"三阶段 SOP,比 planning-with-files 的"记录"更深入 |
| 绝不重复失败 | [查阅知识库规则](../../../../.agents/global-core-rules.md) + 三阶段递进原则 | **同:** 均要求执行前查阅已有经验<br>**异:** SpecWeave 有完整知识库+模式库,planning-with-files 依赖单文件 findings.md |

### 7.2 双向优势识别

**SpecWeave 独有优势:**

1. **AGENTS.md 启动协议(PRIORITY ZERO):** 强制 4 步启动流程(读 AGENTS.md→查路由表→读规范→自检),从源头防止"凭经验做对"的不可预测性,planning-with-files 无此入口协议
2. **三层路由体系(SpecWeave→vendor→flexloop):** 支持跨项目嵌套子模块协同,vendor 方法论资产预检机制防止"就近直觉"偏差,planning-with-files 仅单层文件
3. **能力注册中心 L0/L1/L2 渐进式披露:** ONBOARDING<100 行 / SKILL+REGISTRY<500 行 / 深度文档不限,解决"信息密度与认知负荷"的平衡,planning-with-files 无此分层
4. **7 个角色定义体系:** 角色+职责矩阵+协作场景,支持多智能体分工,planning-with-files 假设单 Agent 工作
5. **阶段守卫 8 阶段 + SG-LOG/PDR-LOG:** 结构化日志可审计、可分析、可可视化(仪表盘),planning-with-files 的 progress.md 仅文本记录
6. **自我演进 8 模块:** 感知层/认知层/执行层/治理层的元认知体系,planning-with-files 无自我演进机制
7. **数据安全治理 + 硬编码治理 + Mermaid 治理:** 垂直领域治理闭环,planning-with-files 仅关注上下文工程
8. **完整脚本工具库:** 自动化验证脚本(check-stage-guardrails.py、check-links.py、ci-check.ps1 等),planning-with-files 仅依赖 Hooks
9. **7 大 Spec 主题分类:** 任务归类决策树,planning-with-files 无任务分类体系
10. **元文档优先原则:** 资源有限时优先优化入口文档/索引/L1 门面,ROI 最高,planning-with-files 未触及此原则

**planning-with-files 独有优势:**

1. **Hooks 原生自动化:** Claude Code 原生 Hooks 机制,自动触发无需用户手动执行,SpecWeave 多数规则依赖智能体自觉遵守
2. **IDE 无关适配:** 5+ 种主流 IDE(Claude Code/Cursor/Continue/Codex/Gemini/Kiro/OpenCode/CodeBuddy/Pi),SpecWeave 当前主要面向 Trae/Claude Code
3. **社区生态规模:** 23k Star + 多个 fork 扩展 + 中文双语 Skill 管理器收录 31k+ Skill,SpecWeave 生态规模较小
4. **极简三文件模式:** 学习成本极低(5 分钟安装),SpecWeave 的 .agents/ 体系学习成本较高
5. **即装即用:** 无需理解完整规范体系即可上手,SpecWeave 需先理解 AGENTS.md 启动协议+上下文路由表
6. **跨任务可复用:** 三文件模式可应用于任何复杂任务,SpecWeave 的 spec.md/tasks.md/checklist.md 主要用于 spec 工作流

### 7.3 双向借鉴建议

**SpecWeave 可借鉴 planning-with-files:**

1. **Hooks 自动化思路:** 将部分阶段守卫规则(如"前置文档强制读取"、"Spec 完成度验证")改造为 Claude Code Hooks 自动触发,减少对智能体自觉性的依赖
2. **IDE 无关适配层:** 抽象 .agents/ 规范为 IDE 无关的中间表示,提供 Cursor/Continue/Codex 等适配器,扩大生态覆盖
3. **社区传播策略:** 借鉴"24 小时爆火"的传播逻辑(Slogan 化、极简安装、IDE 无关),为 SpecWeave 设计类似的快速上手入口
4. **2-Action 规则的强制写文件机制:** 在长任务执行中强制"每 N 次操作后落盘",缓解上下文压力

**planning-with-files 可借鉴 SpecWeave:**

1. **启动协议(PRIORITY ZERO):** 增加任务类型预检机制,复杂任务自动加载对应规范,避免"一刀切"三文件
2. **角色定义体系:** 引入多角色分工(计划者/执行者/验证者),支持多 Agent 协作场景
3. **阶段守卫 + 结构化日志:** 将 progress.md 升级为结构化日志(类 SG-LOG),支持可审计、可分析、可可视化
4. **复盘闭环:** 增加"修复即闭环"三阶段 SOP,从"记录错误"升级为"错误→根因→预防→闭环"
5. **元文档优先原则:** 在文件膨胀时优先优化 task_plan.md/findings.md 的入口结构,而非持续追加内容
6. **能力注册中心 L0/L1/L2:** 为 Skill 提供渐进式披露,避免一次性加载所有 Hooks 规则
7. **任务归类决策树:** 不同任务类型(研究/构建/重构)使用不同的文件模板,而非统一三文件

---

## 八、批判性思考与潜在风险

### 8.1 文章优点

1. **痛点场景化生动:** 三个开篇场景(AI 忘目标/忘第 1 步/重复报错)极具共情力,直接命中用户痛点
2. **方案三文件结构清晰:** task_plan/findings/progress 职责划分明确,易于理解和复用
3. **原理映射 RAM/Disk 直观:** "Context=RAM, Filesystem=Disk"的类比让抽象的上下文工程概念瞬间可理解
4. **安装覆盖主流 IDE:** 5 种安装方式 + 8+ 种 IDE 适配,落地性强
5. **实测有量化数据:** 21 轮对话、15 分钟、第 15 轮遗忘阈值等具体数字,增强说服力
6. **适用边界明确:** 用/不用场景清晰,避免"万能方案"陷阱

### 8.2 文章局限性

1. **20 亿归因简化:** 将 Manus 估值归因单一方法论,忽略团队/用户/品牌/战略等综合因素
2. **无失败案例:** 未呈现 planning-with-files 失效的场景,缺少负面证据
3. **无同类对比:** 未与 Mem0/Letta/LangGraph 等上下文工程方案对比,难以评估相对优势
4. **实测样本单一:** 仅一个技术预研任务,缺乏跨场景(开发/研究/重构/调试)的统计样本
5. **Hooks 实现细节缺失:** 未深入 Hooks 类型(PreToolUse/PostToolUse)、Hook 脚本编写、Hook 失败回退等技术细节
6. **长期维护成本未讨论:** 文件系统膨胀的治理策略(归档/压缩/迁移)未涉及
7. **Manus 原话无来源:** 引用块未标注出处,溯源困难

### 8.3 改进建议

1. **补充 Hooks 实现原理:** 详细说明 Claude Code Hooks 类型、Hook 脚本示例、Hook 失败回退机制
2. **增加多场景实测样本:** 在开发/研究/重构/调试/多 Agent 协作等场景分别实测,提供统计性结论
3. **对比同类上下文工程方案:** 与 Mem0(向量记忆)/Letta(分层记忆)/LangGraph(状态图)对比,明确差异化定位
4. **讨论长期维护成本:** 文件膨胀治理策略(定期归档/压缩/迁移/版本管理)
5. **补充失败案例:** 呈现 planning-with-files 在超大规模项目/多 Agent 并发/长周期任务中的失效场景
6. **标注数据来源:** 23k Star、24 小时爆火、Manus 原话等均需标注可溯源的出处
7. **增加 FAQ 章节:** 跨任务文件清理、Hooks 误触发处理、与其他 Skill 冲突解决等常见问题

### 8.4 方法论潜在风险

| 风险 | 表现 | 缓解策略 |
|---|---|---|
| **文件过多信息过载** | 长期使用后 task_plan/findings/progress 文件膨胀,反而增加认知负荷 | 引入归档机制 + 元文档优先原则(优化入口而非追加内容) |
| **Hooks 误触发** | 自动化 Hook 在边界场景误触发,干扰正常工作流 | 增加 Hook 失败回退机制 + 手动覆盖开关 |
| **跨任务文件污染** | 上一任务的 findings.md 残留影响下一任务判断 | 任务结束时强制归档 + 新任务初始化清理 |
| **版本冲突** | 多 Agent 并发写入同一文件导致冲突 | 引入文件锁 + 分 Agent 文件命名 |
| **依赖 Claude Code Hooks** | Hooks 是 Claude Code 特有,迁移到其他 IDE 时自动化能力丧失 | 标注 IDE 能力差异 + 提供降级方案 |
| **单一文件 vs 结构化日志** | progress.md 文本日志难以自动化分析 | 升级为结构化日志(类 SG-LOG)支持仪表盘 |
| **"先建计划"刚性** | 简单任务也强制建 task_plan 增加摩擦 | 引入任务复杂度评估,简单任务豁免 |

---

## 九、总结与展望

### 9.1 核心洞察凝练

planning-with-files 的爆火,本质是 AI Agent 工程化范式从"对话模式"向"工程模式"转型的标志性事件。其核心洞察可凝练为三点:

1. **瓶颈转移洞察:** AI Agent 的瓶颈已从"模型能力"转移至"工程化方法"。再聪明的大脑,若无可靠的外部记忆与执行约束,也无法完成复杂任务。这一洞察与 SpecWeave 的核心使命高度共鸣——SpecWeave 通过 .agents/ 规范体系解决同一问题,只是路径不同(规范路由 vs 文件外存)。

2. **RAM-Disk 映射洞察:** "Context=RAM, Filesystem=Disk"的类比,将计算机体系结构的经典分层引入 AI Agent 设计,具有跨模型、跨工具、跨场景的长效价值。即使 Context Window 扩大至 1M+ token,文件系统持久化仍是更可靠、更可审计、更可协作的工程化方案。

3. **自动化约束洞察:** Hooks 机制将"规则"从"自觉遵守"升级为"自动触发",这是工程化方法区别于"良好建议"的关键。SpecWeave 的阶段守卫+SG-LOG 与 planning-with-files 的 Hooks 是同一思路的两种实现(显式路由 vs 自动触发)。

### 9.2 对 SpecWeave 的行动建议

基于对照分析,提出 5 条可落地行动建议:

| 优先级 | 建议 | 预期效果 | 验收标准 |
|---|---|---|---|
| **P0** | 将[前置文档强制读取协议](../../../../.agents/protocols/pre-document-reading.md)的关键检查点改造为 Claude Code Hooks 自动触发 | 减少 50%+ 的"未读规范就动手"违规 | Hooks 配置文件提交 + SG-LOG 显示自动触发记录 |
| **P0** | 在 .agents/ 入口增加"5 分钟快速上手"ONBOARDING(类 planning-with-files 的极简安装),与现有 L0 ONBOARDING 整合 | 降低新用户上手成本,提升采纳率 | ONBOARDING < 100 行,5 分钟内可完成首个 spec |
| **P1** | 抽象 .agents/ 规范为 IDE 无关中间表示,提供 Cursor/Continue 适配器 | 扩大生态覆盖至非 Trae 用户 | 至少 2 个非 Trae IDE 适配器可用 |
| **P1** | 在 spec 工作流中引入"2-Action 规则"变体:每 N 次工具调用后强制更新 tasks.md/findings | 缓解长任务上下文压力,防止目标漂移 | 规则写入 [ai-coding-guidelines.md](../../../../.agents/rules/ai-coding-guidelines.md) + 验证脚本 |
| **P2** | 将 progress.md/checklist.md 升级为结构化日志(类 SG-LOG),支持仪表盘可视化 | 提升执行过程可审计性 | 复用 [generate-sg-dashboard.py](../../../../.agents/scripts/generate-sg-dashboard.py) 扩展 |

### 9.3 方法论长效性判断

**长效性高的部分:**
- "Context=RAM, Filesystem=Disk"的原理映射——跨模型、跨工具长效
- "先建计划再开工"的工程原则——经典软件工程原则的 AI 化,长效
- "记录所有错误,绝不重复失败"——与 SpecWeave 的"修复即闭环"同源,长效

**长效性低的部分:**
- Hooks 6 动作的具体实现——依赖 Claude Code Hooks 机制,IDE 迁移时失效
- 5 种安装命令——随 IDE 版本演进可能过时
- 23k Star 的传播热度——社区关注度会随时间衰减

**与 SpecWeave 的关系判断:**
planning-with-files 与 SpecWeave 是互补关系而非替代关系。前者提供"极简上手+自动触发"的快速价值,后者提供"完整规范+治理体系"的深度价值。理想路径是:新用户从 planning-with-files 入门,进阶用户迁移至 SpecWeave 获得完整工程化能力。SpecWeave 可借鉴 planning-with-files 的"极简入口+Hooks 自动化"提升采纳率,planning-with-files 可借鉴 SpecWeave 的"启动协议+阶段守卫+复盘闭环"提升深度。

> **最终判断:** planning-with-files 的方法论核心(文件系统作为 AI 外接硬盘)具有 5+ 年的长效性,但其具体实现(Hooks、安装命令)需随 IDE 演进持续更新。SpecWeave 应吸收其"自动化约束"与"极简上手"两大精髓,同时保持自身在"规范路由+治理体系+多角色协作"上的深度优势,形成"极简入口+深度规范"的分层架构。

---

## 附录:文章章节结构大纲

```
planning-with-files:像 Manus 一样工作
├── 引子:Meta 20 亿美元收购 Manus 背景
├── 一、AI Agent 最大的痛点:Context Window = 金鱼记忆
│   ├── 4 类失忆表现
│   └── 解决方案:文件系统当外接硬盘
├── 二、planning-with-files:把 20 亿美金方法论开源
│   ├── 项目 Slogan
│   └── 3-File Pattern + RAM/Disk 原理映射
├── 三、Hooks 机制是灵魂
│   ├── 6 个自动动作
│   └── 4 大核心规则
├── 四、安装方法:5 分钟装上外接大脑
│   └── 5 种 IDE 安装方式
├── 五、实测:技术预研任务的变化
│   └── 用/不用对比量化
├── 六、什么时候用?什么时候不用?
│   └── 适用/不适用场景
├── 七、社区已经玩出了花
│   └── 4 个 fork 扩展 + 双语 Skill 管理器
└── 八、写在最后
    └── 工程化 > 模型能力
```

---

**报告生成时间:** 2026-07-06
**报告字数:** 约 4800 字
**分析依据:** 文章全文(defuddle 提取)+ SpecWeave `.agents/` 规范体系实际内容
