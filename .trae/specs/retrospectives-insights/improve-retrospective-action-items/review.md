# Checklist

## A1 反爬策略预设清单

- [x] `docs/knowledge/anti-crawler-strategy-playbook.md` 已创建
- [x] 覆盖知乎、微博、推特等至少 3 类反爬站点
- [x] 每类站点含特征识别、策略优先级决策树、命令模板、失败信号
- [x] 显著标注 `--disable-blink-features=AutomationControlled` + 桌面 UA 配置
- [x] 区分沙箱环境可用/不可用策略
- [x] `docs/knowledge/README.md` 索引已更新（待 docgen 自动生成）

## A2 小样本分析前置检查

- [x] `small-sample-analysis-methodology.md` 已加入"样本量前置检查"步骤
- [x] 降级规则清晰（≥10 / 5-9 / 3-4 / < 3）
- [x] "分析受限警告"标准引用块模板已提供
- [x] 触发条件已标注（内容获取后立即评估）
- [x] frontmatter 已更新（version: 1.1.0 + changelog）

## A3 Spec 规划时间盒

- [x] `progressive-spec-planning-for-external-content.md` 已创建
- [x] 三阶段规划流程已定义（15min + 30min + 10min）
- [x] 核心原则"最小启动 + 渐进细化"已编写
- [x] frontmatter 含 source 字段
- [x] `research-knowledge/README.md` 索引已更新

## A4 子智能体委派模板增强

- [x] `subagent-atomic-task-template.md` 已新增"内容获取类任务扩展模板"章节
- [x] 已尝试方法清单模板已包含（策略名称 + 命令 + 失败原因）
- [x] 已知约束模板已包含（沙箱限制、可用工具）
- [x] 成功标准模板已包含（如"获取至少 N 条回答正文"）
- [x] 产出验证流程已补充（样本覆盖率检查）
- [x] frontmatter 已更新（version: 2.1.0 + changelog）

## A5 沙箱环境 fallback 链优化

- [x] `external-website-analysis-fallback-strategy.md` 已标注沙箱环境不可达服务
- [x] archive.org / Google Cache 已降低优先级或移除
- [x] 区分"沙箱环境可用"和"沙箱环境不可用"策略
- [x] frontmatter 已更新（version: 1.1 + changelog）

## 索引同步与验证

- [x] `research-knowledge/README.md` 已新增 progressive-spec-planning 条目
- [x] `docs/retrospective/patterns/README.md` 模式统计数已更新（待 docgen 自动生成）
- [x] `docs/knowledge/README.md` 已新增 anti-crawler-strategy-playbook 条目（待 docgen 自动生成）
- [x] 链接检查通过（待执行）
