# Checklist

## S0 场景识别与链路选择

- [ ] CMD_START 日志已输出(session=sc-20260908-planning-with-files)
- [ ] 场景已识别:场景4 知识沉淀(R→I→E→V→C)
- [ ] 链路已选择:R→I→E→V→C,depth=standard

## R 阶段 — 事实采集(G1 质量门)

- [ ] facts.md 包含≥20 条客观事实
- [ ] 事实覆盖项目元数据(名称/作者/Star/许可证/发布时间/版本)
- [ ] 事实覆盖 Manus 收购事件(Meta 2025.12/20 亿美元/8 个月营收破亿)
- [ ] 事实覆盖 Context Window 4 类痛点(TodoWrite 消失/目标漂移/失败不记录/上下文塞满)
- [ ] 事实覆盖 3-File Pattern 三文件职责(task_plan/findings/progress)
- [ ] 事实覆盖 RAM-Disk 原理映射(Context=RAM/Filesystem=Disk/重要东西写磁盘)
- [ ] 事实覆盖 Hooks 6 个自动动作(创建计划/重读/更新进度/存储发现/记录错误/验证完成度)
- [ ] 事实覆盖 4 大核心规则(先建计划/2-Action/记录错误/绝不重复失败)
- [ ] 事实覆盖 5 种 IDE 安装方式(Claude Code 插件/手动 clone/Git 子模块/Legacy Skills/Cursor)
- [ ] 事实覆盖社区生态(devis/multi-manus-planning/plan-cascade/agentfund-skill/buzhangsan/skill-manager)
- [ ] 事实覆盖实测对比数据(不用:15 轮遗忘;用了:21 轮 15 分钟清晰)
- [ ] G1 通过:全文无因果推断词("因为"/"导致"/"所以"),纯客观描述

## I 阶段 — 核心洞察(G2 质量门)

- [ ] insights.md 包含 3 条核心洞察
- [ ] 洞察1 四元组完整(AI Agent 瓶颈在工程化方法:现象+根因+影响+建议)
- [ ] 洞察2 四元组完整(RAM-Disk 范式映射:现象+根因+影响+建议)
- [ ] 洞察3 四元组完整(Hooks 自动化降低 AI 自觉性依赖:现象+根因+影响+建议)
- [ ] G2 通过:每条洞察四元组完整,无缺失元素

## E 阶段 — 模式萃取(G3 质量门)

- [ ] patterns.md 包含 1-2 个结构化模式
- [ ] 模式1(3-File Pattern)含触发场景(多步骤任务≥3 步)
- [ ] 模式1 含核心步骤(创建三文件→每阶段更新→停止前验证)
- [ ] 模式1 含反模式(单文件混杂/不更新进度/不验证)
- [ ] 模式1 含迁移验证(SpecWeave spec/tasks/checklist 已验证)
- [ ] 模式2(Hooks 自动化)含触发场景(关键节点固定动作)
- [ ] 模式2 含核心步骤(识别节点→编写 Hook→自动触发)
- [ ] 模式2 含反模式(依赖自觉/过度自动化/无回退)
- [ ] 模式2 含迁移验证(SpecWeave 阶段守卫可改造)
- [ ] G3 通过:每个模式含触发场景+核心步骤+反模式+迁移验证

## V 阶段 — 对抗审查

- [ ] 魔鬼代言人视角已执行(20 亿归因简化/文件膨胀/Hooks 误触发)
- [ ] 新人视角已执行(Hooks 配置复杂,需 quickstart)
- [ ] 老板视角已执行(ROI 评估/长期维护成本)
- [ ] 未来视角已执行(Context Window 扩大后长效性)
- [ ] 审查意见已融入 patterns.md 的反模式与边界条件

## C 阶段 — OKF bundle 入库

- [ ] `planning-with-files/index.md` 已创建,含 OKF v0.2 frontmatter(type: group)
- [ ] `planning-with-files/facts.md` 已创建,含 R 阶段事实清单
- [ ] `planning-with-files/insights.md` 已创建,含 I 阶段核心洞察
- [ ] `planning-with-files/patterns.md` 已创建,含 E 阶段模式 + V 阶段审查记录
- [ ] `planning-with-files/log.md` 已创建,含 CMD-LOG 执行日志
- [ ] index.md 的 toctree 引用全部子文档(facts/insights/patterns/log)
- [ ] `jishu/ai/index.md` 分组导航表已更新,新增 planning-with-files 条目

## OKF 合规性验证

- [ ] 所有文件遵循 OKF v0.2 frontmatter 规范(type 必填)
- [ ] 正文使用中文,文件名使用 kebab-case 英文
- [ ] Markdown 交叉引用使用相对路径(无 file:/// 绝对路径)
- [ ] frontmatter sources 字段标注文章来源(微信文章 URL + GitHub 仓库 URL)
- [ ] frontmatter tags 字段包含相关标签(planning-with-files/context-engineering/ai-agent 等)
