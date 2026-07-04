# Harness Engineering（驾驭工程）系统性学习Wiki - Implementation Plan

## [ ] Task 1: 创建Wiki目录结构与索引页
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建wiki目录：`docs/knowledge/learning/harness-engineering-wiki/`
  - 创建索引页 `harness-engineering-wiki.md`（在learning目录下）
  - 索引页包含完整的文档导航表格
  - 为10个原子文件预留位置
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录结构正确创建，路径符合规范
  - `programmatic` TR-1.2: 索引页存在且包含导航表
  - `human-judgement` TR-1.3: 导航表章节顺序与spec一致
- **Notes**: 参考同目录现有wiki的索引页格式

## [ ] Task 2: 生成00-overview.md（概述与学习目标）
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建概述页，包含背景介绍、Harness Engineering概念引入
  - 明确列出5条学习目标
  - 说明前置知识要求与目标读者
  - 添加完整的文档导航表格
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-2.1: frontmatter使用YAML（---），id/title/source/x-toml-ref字段完整
  - `human-judgement` TR-2.2: 学习目标清晰具体，可衡量
  - `human-judgement` TR-2.3: 导航表链接正确指向各章节
- **Notes**: frontmatter的x-toml-ref路径：`../../../../.meta/toml/docs/knowledge/learning/harness-engineering-wiki/00-overview.toml`

## [ ] Task 3: 生成01-paradigm-evolution.md（范式演进：三代AI工程）
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 阐述三代范式：Prompt Engineering → Context Engineering → Harness Engineering
  - 解释核心公式：Agent = Model + Harness
  - 解读"模型是CPU，Harness是操作系统"类比
  - 记录LangChain Terminal Bench实验数据（30→5名，52.8→66.5分）
  - 描述Agent五层运行时全景图
  - Context Engineering工程化四要素（结构化/分段化/可回放/可审计）
- **Acceptance Criteria Addressed**: AC-1, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: frontmatter格式正确，字段完整
  - `programmatic` TR-3.2: LangChain实验数据准确记录并标注来源
  - `human-judgement` TR-3.3: 三代范式对比表格清晰
  - `human-judgement` TR-3.4: 五层运行时描述准确
- **Notes**: 包含范式对比表格，标注各代的核心问题与形象类比

## [ ] Task 4: 生成02-four-iron-laws.md（四条反直觉铁律）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 铁律一：上下文越少越好（上下文是稀缺资源，精挑细选）
  - 铁律二：专才Agent永远赢过通才Agent（Agent昂贵，Skill廉价）
  - 铁律三：状态要写文件，不要塞上下文（Workspace是真相，Context是工位）
  - 铁律四：能写成Linter的约束，别写成文档（文档是建议，Linter/CI是强制）
  - 每条铁律包含：本能反应 vs Harness真相对比表格、工程启示
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-4.1: frontmatter格式正确
  - `human-judgement` TR-4.2: 四条铁律完整无遗漏
  - `human-judgement` TR-4.3: 每条铁律的对比表格清晰，反直觉点突出
- **Notes**: 这是文章核心精华，需重点呈现反直觉的对比

## [ ] Task 5: 生成03-six-patterns.md（六大工程模式）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 模式1：双阶段架构（Initializer + Executor）- Anthropic Claude Code实践
  - 模式2：工具签名即文档（Tool-Signature-as-Doc）- 动词短语命名、description写清何时用
  - 模式3：Sub-Agent隔离（Context-Isolated Sub-Agent）- 独立Context、只看需要的工具、结构化输出
  - 模式4：上下游反压（Upstream-Downstream Backpressure）- 确定性设置 + Linter/CI反馈回路
  - 模式5：智能体审智能体（Agent-Audits-Agent）- 换Context、怀疑态度、只看diff+规则
  - 模式6：熵管理与文档园丁 - 后台Agent定期扫描、持续小额还债
  - 每个模式包含：解决的核心问题、具体做法、标杆案例
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-5.1: frontmatter格式正确
  - `human-judgement` TR-5.2: 六大模式完整，每个模式的核心问题/做法/案例三要素齐全
  - `human-judgement` TR-5.3: 模式索引表与后续内容对应
- **Notes**: 模式索引表在章节开头，便于快速查阅

## [ ] Task 6: 生成04-wukong-case-study.md（实战案例：悟空AI招聘）
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 7.1 第一版"全能招聘Agent"的问题（13个工具、600+行Prompt、五大病灶）
  - 7.2 第二版"2 Agent + N Skill"专才架构（悟空Orchestrator + 人岗匹配Agent + 招聘沟通Agent）
  - 7.3 五条工程铁律的具体落点表格
  - 7.4 改造前后六个维度对比表格（工具选择/准确率/可调试性/可复用性/上下文消耗/新增需求成本）
  - 7.5 三条血泪经验：
    - 经验一：Agent数量不超过3个，Skill可以无限加
    - 经验二：RPA+Agent接缝处要做"事务边界"（lock文件断点续传）
    - 经验三：对外说话的Agent必须接三层硬护栏（白名单工具/Linter拦截/第二个Agent审稿）
- **Acceptance Criteria Addressed**: AC-4, AC-5
- **Test Requirements**:
  - `programmatic` TR-6.1: frontmatter格式正确
  - `programmatic` TR-6.2: 改造前后对比表格数据准确
  - `human-judgement` TR-6.3: 第一版问题描述具体，病灶分析到位
  - `human-judgement` TR-6.4: 第二版架构描述清晰
  - `human-judgement` TR-6.5: 三层硬护栏表格完整
- **Notes**: 这是全文最重要的实战案例，需包含架构图的文字描述

## [ ] Task 7: 生成05-industry-benchmarks.md（行业标杆地图）
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - Anthropic / Claude Code：Initializer+Executor双阶段、Workspace持久层
  - LangChain / Deep Agents：自我验证+追踪+工具签名优化、不换模型冲进Top 5
  - Mitchell Hashimoto / Ghostty：AGENTS.md作为项目宪法、每条规则对应真实失败、能机器化不留在自然语言
  - Cursor / Cline：内置反馈回路（Linter/Type Check/Test）自动闭环、错误信息写给Agent看
  - 悟空AI招聘（本文案例）：2 Agent + N Skill + Workspace状态文件 + Linter硬护栏
  - 标杆对比表格：团队/产品、最有辨识度的Harness选择、启示
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: frontmatter格式正确
  - `human-judgement` TR-7.2: 五个标杆案例的核心选择描述准确
  - `human-judgement` TR-7.3: 对比表格清晰，启示明确
- **Notes**: 标杆表格作为一面镜子，引导读者自查团队缺失

## [ ] Task 8: 生成06-future-trends.md（未来趋势与六条心法）
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 四大未来趋势（每条含可证伪条件）：
    - 趋势一：从"Prompt工程师"到"Agent工程师"
    - 趋势二：从"工具调用"到"Agent协作协议"（MCP → A2A）
    - 趋势三：从"单Agent完成任务"到"Agent操作系统"（Shell/Scheduler/System Calls/FileSystem/Drivers类比）
    - 趋势四：模型与Harness的"接口标准化"
  - 六条心法表格（序号、心法、一句话注解）
  - 文章结语："为野马造高速公路"的核心隐喻
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-8.1: frontmatter格式正确
  - `human-judgement` TR-8.2: 四大趋势完整，每条含可证伪条件
  - `human-judgement` TR-8.3: 六条心法表格准确
- **Notes**: 可证伪条件是工程判断vs预言的分水岭，需保留

## [ ] Task 9: 生成07-critical-thinking.md（批判性思考与评估）
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 来源可信度评估：
    - 作者背景：涅羽，阿里技术团队
    - 一手来源标注：[1]Mitchell Hashimoto博客、[2]LangChain官方博客、[3]专家博客
    - 诚实声明：第三方数据回溯原始来源，无法核实的已软化或删除
  - 准确性评估：
    - LangChain Terminal Bench数据可验证（一手来源）
    - Anthropic Claude Code实践为行业公认事实
    - 悟空案例数据来自团队内部实测，明确标注"仅代表本场景"
    - "小团队×大代码量"数字已主动软化，不作为确定性引用
  - 权威性评估：
    - 阿里技术公众号背书
    - 引用来源均为行业标杆（Mitchell Hashimoto、LangChain、Anthropic）
    - 实战案例来自钉钉企业级Agent"悟空"生产环境
  - 时效性评估：
    - Harness Engineering是2026年当前热点范式
    - MCP/A2A趋势判断符合行业发展方向
  - 局限性分析：
    - 悟空案例数据为内部实测，无公开基准对比
    - 未提及失败案例或负面经验
    - 缺乏与主流Agent框架（LangChain/AutoGen/CrewAI）的深度对比
  - 与本项目（SpecWeave）的关联映射：
    - AGENTS.md → 项目宪法（对应铁律四/模式6）
    - 阶段守卫/CI检查 → Linter硬护栏（对应铁律四/模式4）
    - .agents/scripts/ → 机器可执行约束（对应铁律四）
    - Workspace概念 → 文件系统状态持久化（对应铁律三）
    - 多角色分工 → 专才Agent架构（对应铁律二/模式3）
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-9.1: frontmatter格式正确
  - `human-judgement` TR-9.2: 评估客观中立，区分事实与观点
  - `human-judgement` TR-9.3: 与本项目的关联映射具体、有实际参考价值
  - `human-judgement` TR-9.4: 局限性分析诚实，不刻意美化
- **Notes**: 这是体现"批判性思考"的核心章节，需保持客观中立

## [ ] Task 10: 生成08-faq.md（常见问题）
- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - Q1: Harness Engineering和Context Engineering有什么区别？
  - Q2: "上下文越少越好"是否意味着应该用小上下文窗口？
  - Q3: "Agent数量不超过3个"是硬性规定吗？复杂系统怎么办？
  - Q4: Skill和Sub-Agent应该如何区分？什么时候该新增Agent？
  - Q5: 我们团队已经有大量AGENTS.md文档了，还需要写Linter吗？
  - Q6: 双阶段架构（Init+Exec）中plan.md应该包含哪些内容？
  - Q7: "智能体审智能体"会不会增加很多成本和延迟？
  - Q8: 小团队如何落地"文档园丁"模式？
  - Q9: Harness Engineering只适用于编程Agent吗？
  - Q10: 如何判断我的团队现在处于哪一代范式？
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-10.1: frontmatter格式正确
  - `human-judgement` TR-10.2: FAQ覆盖读者最可能的疑问（8-10个）
  - `human-judgement` TR-10.3: 答案简明准确，有实际指导意义
- **Notes**: 问题设计要从读者（Agent开发者）的实际困惑出发

## [ ] Task 11: 生成09-resources.md（资源链接）
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - 原始资源：
    - 原文链接（微信公众号）
  - 一手参考资料（文章明确引用）：
    - [1] Mitchell Hashimoto《My AI Adoption Journey》
    - [2] LangChain官方博客《Improving Deep Agents with Harness Engineering》
    - [3] 专家博客《Enterprise Agent Runtime Five-Layer Architecture》
  - 延伸阅读方向（文章提及但未引用）：
    - Mitchell Hashimoto个人网站（mitchellh.com）博客原文
    - Anthropic关于Claude Code的官方技术文章
    - OpenAI工程团队关于内部Agent实践的公开发言
  - 本项目内相关wiki：
    - agent-communication-protocols（MCP/A2A协议相关）
    - agent-skills-wiki（Skill开发规范）
    - zleap-agent-harness-learning-analysis（Workspace-first Harness设计）
    - longcat-agent-learning-wiki（Loop Engineering相关）
    - mopmonk-security-agent-wiki（多Agent安全护栏）
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-11.1: frontmatter格式正确
  - `programmatic` TR-11.2: 所有内部wiki链接使用相对路径，格式正确
  - `human-judgement` TR-11.3: 资源分类清晰，相关资源链接准确
- **Notes**: 文章中标注"未在本文中引用、但读者可自行检索"的资料要明确标注

## [ ] Task 12: 索引页完善与内部链接检查
- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 完善索引页（harness-engineering-wiki.md）的内容：添加摘要、学习目标简述
  - 确保所有原子文件之间的内部链接正确（使用相对路径）
  - 在00-overview.md的导航表中确认所有链接可点击
  - 添加术语表（可放在00-overview.md或单独文件，视长度而定）
- **Acceptance Criteria Addressed**: AC-8, AC-9
- **Test Requirements**:
  - `programmatic` TR-12.1: 所有内部链接使用相对路径，无file:///绝对路径
  - `programmatic` TR-12.2: 术语表包含至少15个关键术语的中英文对照与解释
  - `human-judgement` TR-12.3: 索引页内容完整，不仅是导航表
- **Notes**: 术语表建议放在00-overview.md末尾或单独一个文件，根据实际长度决定

## [ ] Task 13: 元数据自动化修复与TOML文件创建
- **Priority**: high
- **Depends On**: Task 12
- **Description**:
  - 运行fix-x-toml-ref.py自动修复x-toml-ref路径并创建缺失TOML文件
  - 命令：`python .agents/scripts/fix-x-toml-ref.py --dir docs/knowledge/learning/harness-engineering-wiki/ --write --create-toml`
  - 同时处理索引页：`python .agents/scripts/fix-x-toml-ref.py --file docs/knowledge/learning/harness-engineering-wiki.md --write --create-toml`
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-13.1: 命令执行成功，无报错
  - `programmatic` TR-13.2: .meta/toml/镜像路径下创建了11个TOML文件（索引+10个原子文件）
  - `programmatic` TR-13.3: 所有x-toml-ref路径层级正确
- **Notes**: 使用自动化工具，不要手动计算../层级

## [ ] Task 14: 格式规范验证
- **Priority**: high
- **Depends On**: Task 13
- **Description**:
  - 运行文件名规范检查：`python .agents/scripts/check-filename-convention.py docs/knowledge/learning/harness-engineering-wiki/`
  - 运行链接有效性检查：`python .agents/scripts/check-links.py docs/knowledge/learning/harness-engineering-wiki/ --check-external`
  - 检查索引页文件名规范
  - 子代理产出验收5点检查（逐项验证）
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-14.1: 文件名规范检查通过，无中文文件名、无kebab-case违规
  - `programmatic` TR-14.2: 链接检查通过，无断链
  - `human-judgement` TR-14.3: 5点检查全部通过：
    - ✅ frontmatter分隔符正确（--- YAML，不是+++ TOML）
    - ✅ x-toml-ref存在且路径正确
    - ✅ 标题层级从h1开始，无跳级
    - ✅ 文件名合规（kebab-case、纯英文、两位数字前缀）
    - ✅ source溯源字段存在
- **Notes**: 这是提交前必须通过的质量门禁

## [ ] Task 15: 更新知识库索引
- **Priority**: medium
- **Depends On**: Task 14
- **Description**:
  - 更新docs/knowledge/README.md，在learning分类下添加Harness Engineering Wiki条目
  - 确认条目描述准确、链接正确
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-15.1: README.md中添加了新条目
  - `human-judgement` TR-15.2: 条目位置正确（learning分类），描述准确
- **Notes**: 参考现有条目的格式

## [ ] Task 16: 原子提交（内容创作提交）
- **Priority**: high
- **Depends On**: Task 15
- **Description**:
  - 原子提交1：创建Harness Engineering系统性学习Wiki教程
  - Commit message遵循Conventional Commits：`docs(knowledge): 新增Harness Engineering（驾驭工程）系统性学习Wiki，含三代范式、四条铁律、六大模式、悟空招聘Agent完整实战案例`
  - 确保提交只包含本次wiki相关文件，无无关文件混入
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `programmatic` TR-16.1: git status确认只有wiki相关文件被添加
  - `programmatic` TR-16.2: commit message格式正确（type(scope): subject）
  - `human-judgement` TR-16.3: 提交单一职责，只包含wiki内容
- **Notes**: 首次提交为内容创作，原子化拆分已在目录结构中体现，无需单独第二次提交
