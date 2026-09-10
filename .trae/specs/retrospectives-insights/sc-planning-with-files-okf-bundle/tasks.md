# Tasks

- [ ] Task 1: 场景识别与链路选择(S0)
  - [ ] SubTask 1.1: 输出 CMD_START 日志(session=sc-20260908-planning-with-files)
  - [ ] SubTask 1.2: 场景识别——场景4 知识沉淀(R→I→E→V→C),depth=standard
  - [ ] SubTask 1.3: 链路选择——R(事实采集)→I(洞察)→E(模式萃取)→V(对抗审查)→C(入库)

- [ ] Task 2: R 阶段 — 文章事实采集(G1)
  - [ ] SubTask 2.1: 采集项目元数据事实(名称 OthmanAdi/planning-with-files、作者 OthmanAdi、GitHub 23k+ Star、MIT 许可证、2026 年 1 月发布、v2.43.0)
  - [ ] SubTask 2.2: 采集 Manus 收购事件事实(Meta 2025 年 12 月 20 亿美元收购、8 个月营收破亿、方法论开源)
  - [ ] SubTask 2.3: 采集 Context Window 4 类痛点事实(TodoWrite 上下文重置时消失、50 次工具调用后目标漂移、失败不记录、上下文塞满越跑越慢)
  - [ ] SubTask 2.4: 采集 3-File Pattern 事实(task_plan.md 跟踪阶段进度、findings.md 存储研究发现、progress.md 会话日志测试结果)
  - [ ] SubTask 2.5: 采集 RAM-Disk 原理映射事实(Context Window=RAM 易失有限、Filesystem=Disk 持久无限、重要东西写到磁盘、Manus 原话引用)
  - [ ] SubTask 2.6: 采集 Hooks 6 个自动动作事实(创建 task_plan.md、重读计划、更新进度、存储发现、记录错误、验证完成度)
  - [ ] SubTask 2.7: 采集 4 大核心规则事实(先建计划再开工、2-Action 规则、记录所有错误、绝不重复失败)
  - [ ] SubTask 2.8: 采集 5 种 IDE 安装方式事实(Claude Code 插件、手动 clone、Git 子模块、Legacy Skills、Cursor/其他 IDE)
  - [ ] SubTask 2.9: 采集社区生态事实(devis 面试优先、multi-manus-planning 多项目并行、plan-cascade 多级编排、agentfund-skill 众筹、buzhangsan/skill-manager 双语管理器 31k+ Skill)
  - [ ] SubTask 2.10: 采集实测对比事实(不用:15 轮遗忘/重复踩坑/结构混乱;用了:21 轮 15 分钟全程清晰/勾选框/progress.md 整理)
  - [ ] SubTask 2.11: G1 质量门检查——全文无因果推断词,纯客观描述,≥20 条事实

- [ ] Task 3: I 阶段 — 核心洞察提炼(G2)
  - [ ] SubTask 3.1: 洞察1 四元组——AI Agent 瓶颈在工程化方法而非模型能力(现象:50 次后目标漂移;根因:Context Window 是易失 RAM;影响:复杂任务不可靠;建议:文件系统外存)
  - [ ] SubTask 3.2: 洞察2 四元组——RAM-Disk 范式映射是上下文工程底层原理(现象:3-File Pattern 朴素有效;根因:Context=RAM 易失,Filesystem=Disk 持久;影响:跨模型跨工具通用;建议:重要信息写磁盘)
  - [ ] SubTask 3.3: 洞察3 四元组——Hooks 自动化降低对 AI 自觉性依赖(现象:4 规则需 AI 自觉遵守;根因:无自动触发规则形同虚设;影响:可靠性取决于 AI 服从性;建议:关键节点自动触发)
  - [ ] SubTask 3.4: G2 质量门检查——每条洞察四元组完整(现象+根因+影响+建议)

- [ ] Task 4: E 阶段 — 可迁移模式萃取(G3)
  - [ ] SubTask 4.1: 萃取模式1:3-File Pattern(文件系统外存模式)——触发场景:多步骤 AI Agent 任务(≥3 步);核心步骤:创建三文件→每阶段更新→停止前验证;反模式:单文件混杂/不更新进度/不验证完成度;迁移验证:SpecWeave spec/tasks/checklist 已验证
  - [ ] SubTask 4.2: 萃取模式2:Hooks 自动化模式——触发场景:需 AI 在关键节点执行固定动作;核心步骤:识别关键节点→编写 Hook 脚本→自动触发;反模式:依赖 AI 自觉/过度自动化/无回退机制;迁移验证:SpecWeave 阶段守卫可改造为 Hooks
  - [ ] SubTask 4.3: G3 质量门检查——每个模式含触发场景+核心步骤+反模式+迁移验证

- [ ] Task 5: V 阶段 — 对抗审查
  - [ ] SubTask 5.1: 魔鬼代言人视角——质疑 20 亿归因过度简化、文件膨胀风险、Hooks 误触发风险
  - [ ] SubTask 5.2: 新人视角——3-File Pattern 学习成本低但 Hooks 配置复杂,需 quickstart 指南
  - [ ] SubTask 5.3: 老板视角——ROI 评估(5 分钟安装成本 vs 可靠性提升)、长期维护成本
  - [ ] SubTask 5.4: 未来视角——Context Window 扩大(1M context)后方法论长效性判断
  - [ ] SubTask 5.5: 审查意见汇总,修正模式文档中的反模式与边界条件

- [ ] Task 6: C 阶段 — OKF bundle 入库
  - [ ] SubTask 6.1: 创建 `planning-with-files/index.md`——OKF v0.2 frontmatter(type: group)+ 束简介 + toctree 引用全部子文档
  - [ ] SubTask 6.2: 创建 `planning-with-files/facts.md`——R 阶段事实清单(≥20 条,G1 通过)
  - [ ] SubTask 6.3: 创建 `planning-with-files/insights.md`——I 阶段 3 条核心洞察(G2 通过)
  - [ ] SubTask 6.4: 创建 `planning-with-files/patterns.md`——E 阶段 1-2 个模式 + V 阶段审查记录(G3 通过)
  - [ ] SubTask 6.5: 创建 `planning-with-files/log.md`——CMD-LOG 执行日志(S0-S5 各阶段事件)
  - [ ] SubTask 6.6: 更新 `jishu/ai/index.md` 分组导航表,新增 planning-with-files 条目

- [ ] Task 7: 质量验证
  - [ ] SubTask 7.1: 验证所有文件遵循 OKF v0.2 frontmatter 规范(type 必填)
  - [ ] SubTask 7.2: 验证中文正文 + kebab-case 英文文件名
  - [ ] SubTask 7.3: 验证 Markdown 交叉引用使用相对路径(无 file:/// 绝对路径)
  - [ ] SubTask 7.4: 验证 toctree 引用全部子文档(index.md 引用 facts/insights/patterns/log)
  - [ ] SubTask 7.5: 验证 frontmatter sources 字段标注文章来源(微信文章 URL + GitHub 仓库 URL)

# Task Dependencies

- Task 1 → Task 2(场景识别后才能开始 R 阶段)
- Task 2 → Task 3(G1 通过后才能进入 I 阶段,事实不清则洞察无据)
- Task 3 → Task 4(G2 通过后才能进入 E 阶段,洞察不完整则模式不可复用)
- Task 4 → Task 5(G3 通过后才能进入 V 阶段,模式不完整则审查无的放矢)
- Task 5 → Task 6(V 审查修正后才能入库)
- Task 6 → Task 7(入库后验证 OKF 合规性)
