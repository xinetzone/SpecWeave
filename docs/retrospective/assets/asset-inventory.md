> **来源**：从 `docs/retrospective/knowledge-extraction.md` 七、资产清单与复用指南 拆分

# 资产清单与复用指南

## 可直接复用的文件

| 文件 | 复用方式 | 适配工作量 |
|------|---------|-----------|
| `check-gitignore.py` | 修改 `REQUIRED_RULES` 和 `TEMP_PATHS` 列表 | 低（5 分钟） |
| `check-spec-consistency.py` | 修改正则模式适配不同文档格式 | 中（30 分钟） |
| `dependency-management.md` | 直接引用或按需裁剪 | 低（5 分钟） |
| `app-development-workflow.md` | 修改应用类型与门禁条件，复用三阶段结构 | 中（30 分钟） |
| `handoff.md`（交接协议） | 直接采用 YAML 格式与交接流程 | 低（5 分钟） |
| `task-template.md` | 直接使用 | 零 |
| `handoff-template.md` | 直接使用 | 零 |
| `directory-readme-template.md` | 填充目录树和模块说明 | 低（5 分钟） |
| 复盘报告模板（3.2 节） | 填充项目数据 | 中（1 小时） |
| `retrospective-report-system-planning.md` | 直接引用增量式需求扩展与四层闭环架构洞察 | 低（5 分钟） |
| `check-action-items.py` | 修改扫描目录路径，直接运行 | 零 |
| `check-retrospective-index.py` | 修改 `dirs_to_check` 列表适配其他索引体系 | 低（5 分钟） |
| `root-cause-diagnosis.md` | 直接复用 | 零 |

## 需实例化后复用的模式

| 模式 | 实例化方式 | 典型产出 |
|------|-----------|---------|
| 三段式检查工具架构 | 填充解析器 + 检查逻辑 | 新的验证脚本 |
| 感知→检查→报告模型 | 定义感知维度 + 检查规则 | 领域特定检查工具 |
| Spec-driven 开发流程 | 编写 spec/tasks/checklist | 新项目的规格文档 |
| 复盘→洞察→导出闭环 | 按模板填充数据 | 项目复盘报告 |
| 文档体系原子化重构方法论 | 执行内容审计→原子化拆分→模块化归类→索引生成 | 模块化文档体系 |
| 事实表述一致性闭环 | 执行问题识别→方向确认→增量修正→全局搜索→边界判定 | 一致的文档表述 |
| 正交验证策略 | 应用于多优化迭代 | 验证计划 |
| 功能模块设计五要素标准结构 | 填充技术架构+关键实现步骤+资源需求+时间节点+预期成果指标 | 功能模块规划文档 |
| 四层闭环架构（感知→认知→执行→治理） | 将功能模块按四层归类，建立数据流闭环 | 自我治理系统设计 |
| 双区开发模型（.temp/ → apps/ 迁移） | 定义非正式区路径、正式区路径、质量门禁条件 | 新实体的开发工作流规范 |
| 生命周期协议三阶段结构 | 填充三阶段的进入条件、执行规范、退出标准、门禁条件 | 生命周期管理协议文档 |
| 目录创建"三件套"模式（目录+README+规范+索引同步） | 填充目录内容与规范定义 | 新顶级目录的完整交付物 |
| 短指令模式库 | 填充新经验证的指令模式 | 指令模式参考文档 |
| 五类资产覆盖原则 | 按 5 类知识形态覆盖（概念/模式/脚本/报告/索引） | 知识产出质量控制参考文档 |
| 引用即触发 | 用户通过选中行号触发实施，消除需求歧义 | 复盘报告执行参考文档 |
| 结构阅读先行 | 扩展前完整阅读包结构，同概念域追加、异概念域新建 | 已建立约定驱动的模块扩展决策 |
| 两栖定位模型 | 通过资产清单+泛化路径图+落地案例三支柱实现双重定位 | 积累大量可复用资产的项目的定位升级 |
| 差异驱动重构 | 逐段对比→标注重复/相似/独有→分类提取→回归验证 | 两个及以上功能重叠文件的合并重构 |
| 渐进式模板化 | 硬编码验证→模板分离→多类型扩展三阶段 | 将硬编码内容转化为可复用模板 |
| 复盘加速效应 | 高频批次复盘→低延迟改进→知识转化率递增 | 长时间密集开发会话中的知识管理 |
| 双阶段加工策略 | 大型文档先横切（原子化）再纵切（模块化）的固定先后顺序 | >200 行文档的深度加工 |
| 入口-容器分离原则 | README 最大精简、AGENTS 路由级保留、.agents/ 全量承载 | 入口文件技术细节过载时的精简迁移 |
| 根因诊断模式 | 纠错反馈触发后先诊断知识缺口再修正，避免表层修正循环 | 智能体输出偏离项目规范时的纠错场景 |
| 源文档降级模式 | 大型文档原子化后不删除源文档，降级为引用导航页 | 大型文档原子化拆分后的收尾处理 |
| 赛事增长飞轮模型 | 将参赛步骤映射为产品增长触点，设计赛产品一体化增长引擎 | AI 产品冷启动、工具型用户增长 |
| 「可控的不可控」UGC 传播杠杆 | 通过精细化规则引导用户自主传播，控制边界而非控制行为 | 社交媒体 UGC 传播、品牌活动 |
| 「有意图的摩擦」设计原则 | 区分战略转化节点与无意义操作障碍，保留有价值的摩擦点 | 增长设计转化节点评估 |
| 赛事漏斗孔径设计 | 每层设定最优「筛孔径」，逐层收敛，层级差异化评审 | 赛事运营、评审流程设计 |

## 需按场景适配的决策框架

| 框架 | 适配方式 | 产出 |
|------|---------|------|
| 目录命名决策矩阵 | 填充项目自身的目录结构 | 项目目录规范 |
| 临时依赖管理决策矩阵 | 调整文件类型和存放位置 | 项目依赖管理规范 |
| 元文档处理决策矩阵 | 扩展元文档类型和关键词 | 文档检查配置 |
| 语义匹配阈值决策矩阵 | 按项目语言和场景调整 | 检查工具配置 |

## 项目复盘报告索引

| 报告 | 关联项目 | 关键洞察 |
|------|---------|---------|
| `retrospective-report-create-apps-directory.md` | apps/ 应用开发工作空间创建 | 双区开发模型、生命周期协议三阶段结构、目录创建三件套模式 |
| `retrospective-insight-create-apps-directory-meta-analysis.md` | 单项目全流程协作元洞察 | 拒批精度决定修订成本、四阶段闭环从报告到执行流、自举式知识增长、零延迟行动、短指令低摩擦协作 |
| `retrospective-report-teams-module.md` | 团队管理模块创建 | 约定驱动创建、规范层纵深防御、自举规范 |
| `retrospective-report-cofounder-improvement-execution.md` | 联合创始改进建议执行 | 声明即校验模式、知识形态三阶跃迁 |
| `retrospective-meta-analysis-cross-project.md` | 跨项目元分析 | 高频模式、顽固问题、演化趋势、资产增长率 |
| `retrospective-report-insight-opportunities-implementation.md` | 洞察报告潜在机会实施 | 洞察→实施零延迟、引用即触发、五类资产覆盖原则 |
| `retrospective-session-agents-md-violation-20260624/` | AGENTS.md 启动协议违反复盘 | 系统级提示与项目级协议的优先级竞争、表层修正循环、多 Skill 执行路径竞争 |
| `retrospective-trae-contest-faq-analysis-20260624/` | TRAE AI 创造力大赛 FAQ 分析 | 赛事增长飞轮、抖音传播杠杆、「有意图的摩擦」设计原则；已萃取 4 个方法论模式：赛事增长飞轮模型、「可控的不可控」UGC 传播杠杆、「有意图的摩擦」设计原则、赛事漏斗孔径设计 |
| `retrospective-specweave-contest-advantage-analysis-20260624/` | 竹简悟道 + SpecWeave 双作品参赛策略分析（真实参赛对齐 v11） | 14 项差异化优势、14 条叙事洞察（含双作品交叉叙事/ TRAE Rules 产品根基/竞争规模12,000+验证/标准化Prompt同质化/HTML差异战场/四维评审权重策略）、双作品策略（竹简悟道主+SpecWeave辅80/20资源分配）、全流程行动清单 |→ 萃取为方法论模式 `multi-source-intelligence-iteration.md` |

> **关联模块**：
> - `patterns/code-patterns/three-tier-check-tool.md`
> - `patterns/architecture-patterns/perception-check-report-model.md`
> - `patterns/architecture-patterns/lifecycle-protocol-three-phase.md`
> - `patterns/methodology-patterns/spec-driven-development.md`
> - `patterns/methodology-patterns/review-insight-export-loop.md`
> - `patterns/methodology-patterns/document-system-refactoring.md`
> - `patterns/methodology-patterns/fact-statement-consistency-loop.md`
> - `patterns/methodology-patterns/dual-zone-development-model.md`
> - `templates/directory-readme-template.md`
> - `frameworks/directory-naming-matrix.md`
> - `frameworks/dependency-management-matrix.md`
> - `frameworks/meta-document-processing-matrix.md`
> - `frameworks/semantic-match-threshold-matrix.md`
> - `reports/retrospective-report-create-apps-directory.md`
> - `reports/retrospective-report-teams-module.md`
> - `reports/retrospective-report-cofounder-improvement-execution.md`
> - `concepts/pattern-maturity-levels.md`
> - `patterns/methodology-patterns/short-command-patterns.md`
> - `reports/retrospective-meta-analysis-cross-project.md`
> - `patterns/methodology-patterns/five-category-asset-coverage.md`
> - `patterns/methodology-patterns/reference-as-trigger.md`
> - `reports/retrospective-report-insight-opportunities-implementation.md`
> - `patterns/methodology-patterns/contest-growth-flywheel.md`
> - `patterns/methodology-patterns/controlled-uncontrollable-ugc-rules.md`
> - `patterns/methodology-patterns/intentional-friction-design.md`
> - `patterns/methodology-patterns/contest-funnel-aperture.md`
> - `patterns/methodology-patterns/multi-source-intelligence-iteration.md`
