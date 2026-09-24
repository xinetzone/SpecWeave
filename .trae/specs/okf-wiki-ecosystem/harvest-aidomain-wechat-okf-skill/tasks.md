# Tasks

## Task 1: 建立账号与公开范围清单
- **Priority**: high
- **Status**: completed
- **Depends On**: None
- **Description**: 核验截图账号“爱域研究社”，登记公开入口、采集时点、发现渠道、授权边界和停止条件；建立去重 manifest 与 `not-collected` 清单。
- **Test Requirements**:
  - **TR-1.1 (rule)**：manifest 含账号名、入口、时间、归属证据和公开性判定。
  - **TR-1.2 (rule)**：受限、未确认归属和访问失败条目均有原因记录。
- **Completion Evidence**: `source-manifest.md` 已登记账号“爱域研究社”、公开范围、停止条件及 `SRC-001`；URL 可公开访问，标题、发布时间和作者归属信号已由独立浏览器核验。

## Task 2: 执行七概念 R 阶段事实采集
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 1
- **Description**: 按公开入口批量发现文章，采集最小必要元数据和正文；为日期、数字、定义、步骤及引述建立连续 F 编号，分离作者观点；对 P0 声明执行权威核验。
- **Test Requirements**:
  - **TR-2.1 (rule)**：每篇纳入文章至少有 URL、标题、归属证据和 F 编号覆盖。
  - **TR-2.2 (rule)**：P0 声明有权威 URL 或“单源/待核验”标记，不伪造来源。
  - **TR-2.3 (rule)**：facts 文件不混入无来源推测。
- **Completion Evidence**: `facts.md` 已登记 F-001 至 F-016，区分页面事实与作者观点；`verification.md` 已完成日期、结构数量和叙事时间量词的 P0 核验，未找到独立来源的项目均标记为 `single-source/flagged`。

## Task 3: 完成 I 阶段知识地图与三层拆分
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 2
- **Description**: 输出事实层、机制层、可迁移路径层知识地图；执行操作可复现性两问，决定是否创建 `examples/`；为每篇 concepts 绑定 F 编号和洞察四元组。
- **Test Requirements**:
  - **TR-3.1 (rubric)**：三层边界清晰、无事实与洞察混层，评分 ≥1.5/2。
  - **TR-3.2 (rule)**：每篇 concepts 有 F 编号映射；无可复现操作时不创建空 examples。
- **Completion Evidence**: `knowledge-map.md` 完成事实层、机制层和可迁移路径层拆分，G2 评分 1.7/2；`examples-decision.md` 两问均为“否”，未创建空 `examples/`。

## Task 4: 生成 OKF Wiki bundle 与索引
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 3
- **Description**: 按 `references/ → concepts/ → examples/（如有）→ index/log` 顺序生成原创教程、核验记录、时效状态和主题索引；更新父级 toctree 与计数。
- **Test Requirements**:
  - **TR-4.1 (rule)**：不包含逐篇全文镜像；正文具体声明均可回溯。
  - **TR-4.2 (rule)**：frontmatter、sources、status、stale_after 和三级 toctree 完整。
  - **TR-4.3 (rule)**：双份 F 编号集合一致，链接和索引计数可达。
- **Completion Evidence**: `projects/awesome-okf-xs/doc/bundles/sheke/relationships/aidomain-wechat-relationship-practice/` 已生成根 index、concepts、references、log；未创建 examples；UTF-8、toctree 和 bundles index 五面对账均通过。

## Task 5: 萃取自动化 Skill 设计与实现
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 4
- **Description**: 使用 skill-creator 与 extraction-cmd 方法论，创建主权区 Skill；包含触发描述、公开性决策树、MCP/脚本双方案、dry-run、幂等、失败清单、Why 解释、OKF 输出契约和安全检查清单。不得修改 vendor 资产。
- **Test Requirements**:
  - **TR-5.1 (rule)**：SKILL.md ≤500 行且含完整触发词、决策树、Why、边界和验证清单。
  - **TR-5.2 (rule)**：Skill 明确禁止绕过登录/验证码/邀请码和全文复制。
  - **TR-5.3 (rule)**：至少 3 个测试提示已保存，覆盖正常公开采集、受限内容和幂等重跑。
- **Completion Evidence**: `.agents/skills/wechat-public-okf/SKILL.md`（151 行）、`evals/evals.json`（3 个评测提示）和 `.meta/toml/.agents/skills/wechat-public-okf/SKILL.toml` 已落盘。

## Task 6: 独立审查与机械验证
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 4, Task 5
- **Description**: 独立上下文审查 bundle 与 Skill；执行 UTF-8、链接、toctree、F 编号、敏感路径、frontmatter、计数和触发评测；失败项回写修复队列。
- **Test Requirements**:
  - **TR-6.1 (rule)**：所有 AC 均有独立证据；失败检查点均形成 pending 修复项。
  - **TR-6.2 (rubric)**：教程可信度、可读性和可迁移性评分 ≥1.5/2。
  - **TR-6.3 (rubric)**：Skill 三类测试提示均遵守公开性与版权边界，评分 ≥1.5/2。
- **Completion Evidence**: 独立审查已通过；`review.md` 记录 AC-1 至 AC-7 的逐项证据，AC-4 评分 `1.7/2`、AC-7 评分 `2.0/2`。OKF UTF-8、toctree、bundle 计数门禁全部通过；F-001–F-016 双向集合一致；Skill 为 155 行，评测集含公开转化、受限停止、幂等重跑 3 条提示；未发现 P0-P3 或阻塞项，未创建 pending 修复任务。

## Task Dependencies
- `Task 1 → Task 2 → Task 3 → Task 4`
- `Task 4 → Task 5`
- `Task 4 + Task 5 → Task 6`

## Parallelizable Work
- Task 5 的 Skill 骨架研究可在 Task 4 的文档生成完成后立即开始，但最终输出契约必须对齐 Task 4。
- Task 2 的 P0 核验可按文章主题分组并行，所有组共享同一 F 编号登记规则。
