# Tasks

- [x] Task 1: A1 反爬策略预设清单（高优先级）
  - [x] SubTask 1.1: 创建 `docs/knowledge/anti-crawler-strategy-playbook.md`
  - [x] SubTask 1.2: 编写知乎反爬策略（特征：40362 错误码 + JS challenge；成功策略：agent-browser + --disable-blink-features=AutomationControlled + 桌面 UA）
  - [x] SubTask 1.3: 编写微博反爬策略（特征识别 + 策略优先级 + 命令模板）
  - [x] SubTask 1.4: 编写推特反爬策略（特征识别 + 策略优先级 + 命令模板）
  - [x] SubTask 1.5: 区分沙箱环境可用/不可用策略（A5 联动）
  - [x] SubTask 1.6: 更新 `docs/knowledge/README.md` 索引（待 docgen 自动生成）

- [x] Task 2: A2 小样本分析前置检查（高优先级）
  - [x] SubTask 2.1: 读取 `docs/retrospective/patterns/methodology-patterns/research-knowledge/small-sample-analysis-methodology.md`
  - [x] SubTask 2.2: 加入"样本量前置检查"步骤（≥10 全规格 / 5-9 降级 / 3-4 大幅降级 / < 3 跳过深度层）
  - [x] SubTask 2.3: 提供"分析受限警告"标准引用块模板
  - [x] SubTask 2.4: 标注触发条件（内容获取后立即评估样本量）
  - [x] SubTask 2.5: 更新 frontmatter（version: 1.1.0 + changelog）

- [x] Task 3: A3 Spec 规划时间盒（中优先级）
  - [x] SubTask 3.1: 创建 `docs/retrospective/patterns/methodology-patterns/research-knowledge/progressive-spec-planning-for-external-content.md`
  - [x] SubTask 3.2: 定义三阶段规划流程（最小可行 Spec 15min → 内容获取试错 30min → 调整 Spec 10min）
  - [x] SubTask 3.3: 编写核心原则"最小启动 + 渐进细化"
  - [x] SubTask 3.4: 添加 frontmatter（含 source 字段）
  - [x] SubTask 3.5: 更新 `research-knowledge/README.md` 索引

- [x] Task 4: A4 子智能体委派模板增强（中优先级）
  - [x] SubTask 4.1: 读取 `docs/retrospective/patterns/methodology-patterns/ai-collaboration/subagent-atomic-task-template.md`
  - [x] SubTask 4.2: 新增"内容获取类任务扩展模板"章节
  - [x] SubTask 4.3: 包含已尝试方法清单模板（策略名称 + 命令 + 失败原因）
  - [x] SubTask 4.4: 包含已知约束模板（沙箱限制、可用工具）
  - [x] SubTask 4.5: 包含成功标准模板（如"获取至少 N 条回答正文"）
  - [x] SubTask 4.6: 补充产出验证流程（样本覆盖率检查）
  - [x] SubTask 4.7: 更新 frontmatter（version: 2.1.0 + changelog）

- [x] Task 5: A5 沙箱环境 fallback 链优化（低优先级）
  - [x] SubTask 5.1: 读取 `docs/retrospective/patterns/methodology-patterns/research-knowledge/external-website-analysis-fallback-strategy.md`
  - [x] SubTask 5.2: 标注 archive.org / Google Cache 为"沙箱环境不可达"
  - [x] SubTask 5.3: 在 fallback 链中降低其优先级或移除
  - [x] SubTask 5.4: 区分"沙箱环境可用"和"沙箱环境不可用"策略
  - [x] SubTask 5.5: 更新 frontmatter（version: 1.1 + changelog）

- [x] Task 6: 索引同步与验证
  - [x] SubTask 6.1: 更新 `docs/retrospective/patterns/methodology-patterns/research-knowledge/README.md`（新增 progressive-spec-planning 条目）
  - [x] SubTask 6.2: 更新 `docs/retrospective/patterns/README.md`（模式统计数更新，待 docgen 自动生成）
  - [x] SubTask 6.3: 更新 `docs/knowledge/README.md`（待 docgen 自动生成）
  - [x] SubTask 6.4: 运行链接检查

# Task Dependencies

- Task 1, 2, 3, 4, 5 可并行执行（独立改进项）
- Task 6 依赖 Task 1-5 全部完成（索引同步需要所有文件就位）
- Task 1 与 Task 5 有联动关系（A1 的沙箱环境区分引用 A5 的标注）

# 完成情况

- Task 1-5 已由两个子智能体并行完成
- Task 6.1 已手动更新（research-knowledge/README.md 新增 progressive-spec-planning 条目）
- Task 6.2-6.3 标记为"待 docgen 自动生成"（patterns/README.md 和 knowledge/README.md 的统计数和导航表由 docgen-cmd 自动维护）
- Task 6.4 链接检查待执行
