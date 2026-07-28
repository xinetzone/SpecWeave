# Agentrys AI多智能体芯片设计工作流 - 验证清单（checklist.md）

## R阶段 - 事实采集
- [x] Checkpoint 1: 事实清单包含≥20条客观事实（实际36条）
- [x] Checkpoint 2: 因果词黑名单扫描零命中（无"因为/所以/导致/错误/说明/证明"等判断词）
- [x] Checkpoint 3: 事实覆盖四大架构属性（分层编排/受治理迭代/目标无关性/溯源知识库）
- [x] Checkpoint 4: 事实覆盖五子系统流程（输入设置/前端/验证/后端/Sign-off）
- [x] Checkpoint 5: 事实覆盖核心成果数据（XLOPS/W/fmax/面积/DRC等量化指标）
- [x] Checkpoint 6: 每条事实可溯源到文章原文段落（带#标签分类）
- [x] Checkpoint 7: G1质量门通过，事实清单纯客观无推论

## I阶段 - 洞察提炼
- [x] Checkpoint 8: 核心洞察≥3条（实际4条）
- [x] Checkpoint 9: 每条洞察包含完整四元组（现象陈述/证据Fxx引用/反常识本质/可迁移行动建议）
- [x] Checkpoint 10: 洞察揭示了超越芯片设计领域的通用架构原则
- [x] Checkpoint 11: 反常识要点不是表面总结（揭示收敛契约/跨阶段闭环/信任基础设施/目标-机制分离）
- [x] Checkpoint 12: 行动建议可迁移到AI辅助软件工程/SpecWeave场景
- [x] Checkpoint 13: 与现有"多智能体闭环执行"模式的差异已明确说明（战术层vs战略层，互补关系）
- [x] Checkpoint 14: G2质量门通过，洞察四元组完整且有洞见

## E阶段 - 模式萃取
- [x] Checkpoint 15: 萃取1-2个新模式（非重复模式）——实际萃取2个模式
- [x] Checkpoint 16: 每个模式YAML frontmatter字段完整（id唯一/title/type/date/maturity=L1-draft/source/related_patterns/tags）
- [x] Checkpoint 17: 触发场景清晰，包含"适用于"和"不适用于"边界
- [x] Checkpoint 18: 核心做法3-7步，每步具体可执行
- [x] Checkpoint 19: 反模式≥3个，对等提炼（与正确做法同等详细）
- [x] Checkpoint 20: 检验标准明确（做完怎么知道对了）
- [x] Checkpoint 21: 迁移示例≥1个非芯片/EDA领域场景
- [x] Checkpoint 22: 存储目录分类正确（架构类→architecture-patterns/，治理类→governance-strategy/）
- [x] Checkpoint 23: G3质量门通过，模式可迁移到≥1个跨领域场景
- [x] Checkpoint 24: 与现有模式库grep比对完成，无实质重复

## V阶段 - 对抗审查
- [x] Checkpoint 25: 审查意见总计≥5条，具体有实质内容（非客套话）——实际7条
- [x] Checkpoint 26: 覆盖≥3个审查视角（魔鬼代言人/新人/约束极限）
- [x] Checkpoint 27: ≥2条审查意见被采纳并修正模式文档——实际采纳4条
- [x] Checkpoint 28: V门质量门通过，审查确实暴露了模式盲区并增强了健壮性

## C阶段 - 入库与验证
- [x] Checkpoint 29: 模式文件已写入正确目录
- [x] Checkpoint 30: 对应目录README.md索引已更新，条目格式与现有一致
- [x] Checkpoint 31: related_patterns交叉引用已添加
- [x] Checkpoint 32: link-check.py验证通过，零断链
- [x] Checkpoint 33: 模式成熟度标注为L1-draft（单案例待验证）
- [x] Checkpoint 34: G4质量门通过，入库产物完整可审计
- [x] Checkpoint 35: 执行记录摘要已生成（各阶段产出+质量门通过状态）
