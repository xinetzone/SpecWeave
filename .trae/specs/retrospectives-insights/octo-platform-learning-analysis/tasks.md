# 明略科技 Octo 平台学习与 Wiki 教程文档 - 实施计划

## [x] Task 1: 创建 Wiki 教程文档基础框架与目录导航

- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `docs/knowledge/learning/` 目录下创建 `octo-platform-wiki.md` 文件
  - 添加符合项目规范的 YAML frontmatter（title/source/date/tags 字段）
  - 创建完整的目录导航系统，包含所有章节的 Markdown 锚点链接
  - 在文档开头添加原文链接与 GitHub 开源组织链接（https://github.com/Mininglamp-OSS）
- **Acceptance Criteria Addressed**: Wiki 教程文档创建（文档基础信息完整 / 目录导航系统可用 / 原文与项目链接可访问）
- **Test Requirements**:
  - `programmatic` TR-1.1: 文件存在于正确路径 `docs/knowledge/learning/octo-platform-wiki.md`
  - `programmatic` TR-1.2: frontmatter 包含所有必填字段（title/source/date/tags），使用 YAML 格式
  - `human-judgement` TR-1.3: 目录导航结构完整，所有章节锚点链接可跳转
  - `programmatic` TR-1.4: 文档包含原文微信公众号 URL 与 GitHub 开源组织 URL
- **Notes**: 参考 `text-to-cad-wiki.md` 与 `the-agency-project-wiki.md` 的文档结构和格式

## [x] Task 2: 编写项目背景与定位章节

- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 介绍 Agent 等数字劳动力爆发的行业背景
  - 阐述明略科技将 Octo 打造为 Private AI 时代组织基础设施的定位
  - 说明传统 IM 工具在多 Agent 协作中的三大局限（信息淹没、难以追溯、协作拓扑失控）
  - 引出 Octo 想解决的三个层次问题：连接（IM 入口）、干活（Matter 承载）、沉淀（Taste 进化）
  - 适当引用原文中"Octo 想要把 Octo 平台打造成为 Private AI 时代的组织基础设施"等关键描述
- **Acceptance Criteria Addressed**: 项目背景与定位章节（行业背景阐述清晰 / 核心问题阐述清晰）
- **Test Requirements**:
  - `human-judgement` TR-2.1: 行业背景阐述准确，体现 Agent 数字劳动力趋势
  - `human-judgement` TR-2.2: Octo 定位清晰，明确 Private AI 时代组织基础设施的角色
  - `human-judgement` TR-2.3: 三大局限说明到位，与传统 IM 形成对比
  - `human-judgement` TR-2.4: 三个层次问题（连接/干活/沉淀）逻辑递进清晰
- **Notes**: 引用原文中"Agent，不应只活在对话框里"作为章节引入

## [ ] Task 3: 编写 O.C.T.O. 四维度框架章节

- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 详解 O（Open，开放生态）：不同 Runtime Agent（OpenClaw、Codex、Claude Code、Cursor）以 Bot 身份接入获得统一身份
  - 详解 C（Context，共享上下文）：IM 讨论收敛为结构化知识，项目上下文跨 Agent 共享，任务过程可追溯
  - 详解 T（Taste，偏好进化）：实战反馈沉淀为偏好，主人的品味和判断方式被结构化留存与调用
  - 详解 O（Orchestration，多 Agent 编排）：六种协作模式对应六种信息拓扑
  - 阐述 Matter 作为共同基座承载 Context、Taste、Orchestration 的关系
  - 说明没有 Matter 时各维度的散落状态
- **Acceptance Criteria Addressed**: O.C.T.O. 四维度框架章节（四维度定义清晰 / 四维度关系阐述）
- **Test Requirements**:
  - `human-judgement` TR-3.1: 四个维度定义准确，与原文一致
  - `human-judgement` TR-3.2: 每个维度配有原文中的具体说明或示例
  - `human-judgement` TR-3.3: Matter 作为基座的关系阐述清晰
  - `human-judgement` TR-3.4: 没有 Matter 时的散落状态说明到位
- **Notes**: 使用表格清晰展示四维度对比

## [x] Task 4: 编写 Matter 事项设计章节

- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 说明普通 IM 信息淹没问题（今天讨论方案，明天消息刷屏，一周后大海捞针）
  - 阐述 Matter 将每个任务沉淀为可追溯的"决策卡"设计
  - 详解 Matter 包含的要素：任务缘起（Brief）、过程时间线（Timeline）、关键产出、人的反馈、验收结论
  - 说明 Matter 作为组织决策资产的价值（为什么选 A、放弃 B 的判断来自谁）
  - 阐述 Matter 中反馈如何成为 Agent 学习组织偏好的原材料
- **Acceptance Criteria Addressed**: Matter 事项设计章节（Matter 价值阐述 / Matter 结构清晰）
- **Test Requirements**:
  - `human-judgement` TR-4.1: 信息淹没问题阐述引起共鸣
  - `human-judgement` TR-4.2: "决策卡"概念解释清晰
  - `human-judgement` TR-4.3: Matter 五要素完整说明
  - `human-judgement` TR-4.4: 组织决策资产价值阐述到位
- **Notes**: 使用 Mermaid 时序图或流程图展示 Matter 的生命周期

## [x] Task 5: 编写 Taste 偏好进化章节

- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 说明当前 Agent 自我成长有限的现状（配置文件、工具说明、角色设定）
  - 阐述"偏好对齐必须在实战中完成"的设计思路
  - 详解人的打回、修改、确认如何成为 Bot 学习素材
  - 说明隐性判断（"这个感觉不对"、"这个角度不准"）向可复用偏好沉淀的过程
  - 阐述 Taste 如何让 Agent 越用越懂团队的做事方式
  - 说明下次类似任务时偏好自动进入上下文的机制
- **Acceptance Criteria Addressed**: Taste 偏好进化章节（Taste 形成机制清晰 / Taste 价值阐述）
- **Test Requirements**:
  - `human-judgement` TR-5.1: 实战沉淀思路阐述清晰
  - `human-judgement` TR-5.2: 隐性判断向偏好沉淀的过程说明到位
  - `human-judgement` TR-5.3: Taste 价值（越用越懂团队）表达准确
  - `human-judgement` TR-5.4: 偏好自动进入上下文的机制说明清晰
- **Notes**: 用具体例子说明 Taste 的形成过程

## [x] Task 6: 编写六种协作模式章节

- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 引入"多个 Agent 协作 ≠ 多叫几个 Bot 进群"的观点
  - 详解六种协作模式（建议使用表格对比）：
    - Solo：单干模式，领队独自完成简单明确任务
    - Roundtable：圆桌讨论，领队主持下多 Agent 围绕同一议题公开讨论
    - Critic：生成-验证模式，一个生成一个审核，验证方有否决权
    - Pipeline：流水线模式，A→B→C 严格串行，产出作为下一步输入
    - Split：分头干模式，任务拆成互不可见子块各自处理后领队合并
    - Swarm：撒网竞选模式，同一任务交多个 Agent 独立完成（互盲），领队择优
  - 每种模式说明：适用场景、信息流转方式、参与者可见性、典型用例
  - 对比 Octo 协作模式与飞书/Slack 群聊的差异
  - 阐述"该互见时互见，该互盲时互盲"的隔离设计
- **Acceptance Criteria Addressed**: 六种协作模式章节（六种模式定义完整 / 每种模式信息拓扑清晰 / 与传统群聊对比）
- **Test Requirements**:
  - `human-judgement` TR-6.1: 六种模式定义完整准确
  - `human-judgement` TR-6.2: 每种模式四要素（场景/流转/可见性/用例）齐全
  - `human-judgement` TR-6.3: 隔离设计（互见/互盲）说明清晰
  - `human-judgement` TR-6.4: 与传统群聊对比到位
- **Notes**: 使用表格对比六种模式，便于快速查阅

## [x] Task 7: 编写产品四层结构章节

- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 解析 Octo 的产品四层结构：
    - 结构层：Space（空间）/Category（分类）/Channel（频道）/Thread（话题）的协作关系组织
    - 入口层：私聊（一对一对话通道）+ 语音输入（持续进化的系统，结合上下文修正转写）
    - 环境接入层：浏览器插件（Cmd+K 接入外部工具，自动带入链接/标题/选中文本）
    - 行为约束层：GROUP.md（Bot 行为准则，"进什么庙念什么经"的切换机制）
  - 每层说明：设计目的、核心机制、实际价值
  - 强调语音输入不仅是 STT，还能语音 @他人、修改已有内容、删掉前面输入
  - 强调 GROUP.md 切换时同一只 Bot 立即调整工作模式
  - 提及多端补全：Web、移动端、浏览器插件、CLI
- **Acceptance Criteria Addressed**: 产品四层结构章节（四层结构清晰 / 各层设计要点阐述 / GROUP.md 机制清晰）
- **Test Requirements**:
  - `human-judgement` TR-7.1: 四层结构划分清晰
  - `human-judgement` TR-7.2: 每层三要素（目的/机制/价值）完整
  - `human-judgement` TR-7.3: 语音输入的进化系统特性说明到位
  - `human-judgement` TR-7.4: GROUP.md 切换机制说明清晰
- **Notes**: 使用 Mermaid 架构图展示四层结构

## [x] Task 8: 编写 Private AI 与 Trustworthy AI 章节章节

- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 阐述 Private AI 理念：
    - 不仅是本地化部署，更是数据主权、知识主权、协作主权的回归
    - Octo 通过 CLI 接入端侧模型与本地环境
    - 上下文、决策过程、执行结果留在端侧
    - 聊天数据、协作产出、Bot 记忆完全跑在自己服务器上
  - 阐述 Trustworthy AI 理念：
    - 三大特征：开源、白盒、可审计
    - "能力可以流动，但数据不外流"的设计原则
    - "协作可以展开，但控制权留在组织内部"
  - 阐述企业长期竞争力来源：Context、Taste、Skill 无法被复制
  - 阐述个人价值放大：Taste—"我品故我在"
- **Acceptance Criteria Addressed**: Private AI 与 Trustworthy AI 章节章节（Private AI 理念清晰 / Trustworthy AI 理念清晰）
- **Test Requirements**:
  - `human-judgement` TR-8.1: Private AI 三大主权（数据/知识/协作）阐述清晰
  - `human-judgement` TR-8.2: 端侧接入实现方式说明到位
  - `human-judgement` TR-8.3: Trustworthy AI 三大特征说明准确
  - `human-judgement` TR-8.4: 企业长期竞争力与个人 Taste 价值阐述深刻
- **Notes**: 引用原文"我品故我在"作为章节亮点

## [x] Task 9: 编写关键术语表

- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 整理文章中的专业术语及其定义
  - 至少包含：Octo、Matter、Taste、Runtime Agent、Bot、A2A、GROUP.md、Private AI、Trustworthy AI、Open Agent、Closed Agent、Space/Category/Channel/Thread、Cmd+K 等
  - 每个术语配简洁明确的定义
  - 使用表格形式组织，便于查阅
- **Acceptance Criteria Addressed**: 关键术语表（术语表完整）
- **Test Requirements**:
  - `human-judgement` TR-9.1: 术语数量至少 12 个
  - `human-judgement` TR-9.2: 每个术语定义准确简洁
  - `programmatic` TR-9.3: 使用 Markdown 表格格式
- **Notes**: 术语表放在文档后部，便于读者查阅

## [x] Task 10: 编写 FAQ 常见问题章节

- **Priority**: medium
- **Depends On**: Task 9
- **Description**:
  - 整理至少 6 个常见问题及解答：
    - Q1: Octo 适合什么场景使用？什么规模的企业适合？
    - Q2: Octo 与飞书/Slack 内置 AI 工具的本质差异是什么？
    - Q3: Octo 如何实现私有化部署？需要什么基础设施？
    - Q4: Octo 支持哪些 Runtime Agent？如何接入自定义 Agent？
    - Q5: 六种协作模式如何选择？什么任务用什么模式？
    - Q6: Taste 偏好沉淀机制如何避免学到错误偏好？
    - Q7: GROUP.md 如何编写？有哪些必备字段？
  - 解答清晰准确，引用原文内容作为依据
- **Acceptance Criteria Addressed**: FAQ 常见问题章节（FAQ 实用性）
- **Test Requirements**:
  - `human-judgement` TR-10.1: 至少 6 个 FAQ 问题
  - `human-judgement` TR-10.2: 问题覆盖六大主题（场景/对比/部署/接入/模式/Taste）
  - `human-judgement` TR-10.3: 解答清晰准确，有原文依据
- **Notes**: FAQ 应具有实际参考价值

## [ ] Task 11: 编写相关资源链接章节

- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - GitHub 开源组织地址：https://github.com/Mininglamp-OSS
  - 原文微信公众号链接：https://mp.weixin.qq.com/s/rB51LZBmrUNTPDAjw017qA
  - 明略科技可信 AI 方向相关资源（如适用）
  - 相关多 Agent 协作协议资源（如 A2A、MCP 等，如适用）
  - 资源分类清晰，便于查阅
- **Acceptance Criteria Addressed**: 相关资源链接章节（资源链接有效）
- **Test Requirements**:
  - `programmatic` TR-11.1: GitHub 链接正确（https://github.com/Mininglamp-OSS）
  - `programmatic` TR-11.2: 原文链接正确
  - `human-judgement` TR-11.3: 资源分类清晰
- **Notes**: 链接需可访问

## [x] Task 12: 更新知识库索引 README.md

- **Priority**: high
- **Depends On**: Task 11
- **Description**:
  - 在 `docs/knowledge/README.md` 的 learning 分类表格中新增 octo-platform-wiki 条目
  - 条目包含：标题、摘要、日期（2026-07-04）、标签（octo、mininglamp、private-ai、agent-collaboration、a2a、matter、taste、orchestration、multi-agent、trustworthy-ai）
  - 遵循现有索引格式，保持表格结构与其他条目一致
- **Acceptance Criteria Addressed**: 知识库索引更新（索引条目格式一致）
- **Test Requirements**:
  - `programmatic` TR-12.1: README.md 中 learning 分类新增了 octo-platform-wiki 条目
  - `human-judgement` TR-12.2: 摘要准确概括教程内容
  - `human-judgement` TR-12.3: 标签设置合理
  - `programmatic` TR-12.4: 表格格式与现有条目一致
- **Notes**: 严格遵循现有索引格式

# Task Dependencies

- Task 1 → 无依赖（基础框架）
- Task 2 → Task 1（依赖框架）
- Task 3 → Task 2（依赖背景章节）
- Task 4 → Task 3（依赖四维度章节引出 Matter）
- Task 5 → Task 4（依赖 Matter 章节引出 Taste）
- Task 6 → Task 5（依赖 Taste 章节引出协作模式）
- Task 7 → Task 6（依赖协作模式章节）
- Task 8 → Task 7（依赖产品结构章节）
- Task 9 → Task 8（术语表汇总前面概念）
- Task 10 → Task 9（FAQ 引用前面内容）
- Task 11 → Task 10（资源链接章节）
- Task 12 → Task 11（索引更新依赖文档完成）

# Parallelizable Work

- Task 9（术语表）与 Task 10（FAQ）可适度并行，但建议顺序执行以保持术语一致性
- Task 11（资源链接）与 Task 12（索引更新）可并行，但 Task 12 依赖文档主体完成
