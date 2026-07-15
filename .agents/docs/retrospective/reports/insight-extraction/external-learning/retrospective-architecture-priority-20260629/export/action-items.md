---
id: "architecture-priority-export-action-items"
title: "三、下一步行动建议"
source: "export-suggestions.md#三下一步行动建议"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-architecture-priority-20260629/export/action-items.toml"
---
# 三、下一步行动建议

> **Spec 生命周期说明**：`.trae/specs/` 是 Spec 工作区（不成熟、开发中的 Spec），按主题分类组织任务；当 Spec 成熟实施后，最终归档到 `.agents/` 对应子目录（commands/、rules/、protocols/、capabilities/、skills/ 等），成为正式规范体系的一部分。`.trae/specs/` 保留实施过程的完整记录（spec.md、tasks.md、checklist.md），`.agents/` 存放稳定可引用的L1/L2层正式文档。

## ✅ 已全部完成（P0+P1+P2模块6）

1. ✅ **完成本次复盘原子化**（2026-06-29）
2. ✅ **创建 P0 模块1任务**：在 `.agents/capabilities/` 下创建能力注册中心（2026-06-30）
3. ✅ **实施 P0模块1**：已创建 `.agents/capabilities/` 目录（ARCHITECTURE.md、ONBOARDING-TEMPLATE.md、REGISTRY-TEMPLATE.md、README.md）+ `.agents/ONBOARDING.md` + `.agents/capability-registry.md`（2026-06-30）
4. ✅ **实施 P0模块2**：已完成6个指令集SKILL化（atomic-commit-cmd、atomization-cmd、retrospective-cmd、insight-cmd、export-report-cmd、mermaid-cmd）（2026-06-30）
5. ✅ **更新 skill-development.md**：已补充指令集和脚本Skill化的具体规范（五要素模型、双方案模式、资产盘点、验证清单等）（2026-06-30）
6. ✅ **实施 P0模块3（Agent Onboarding协议）**：已创建 `.agents/protocols/onboarding-protocol.md`（2026-06-30）
7. ✅ **沉淀 6 个可复用模式到模式库**：全部完成
   - P-ARCH-001（渐进式披露架构）→ `.agents/capabilities/ARCHITECTURE.md`
   - P-ARCH-002（Markdown即接口）→ `docs/retrospective/patterns/methodology-patterns/ai-collaboration/markdown-as-interface.md`
   - P-ARCH-003（瓶颈优先重构法）→ `docs/retrospective/patterns/methodology-patterns/governance-strategy/bottleneck-first-refactoring.md`
   - P-ARCH-004（不重构清单）→ `docs/retrospective/patterns/methodology-patterns/governance-strategy/no-touch-list.md`
   - P-ARCH-005（架构决策三角验证）→ `docs/retrospective/patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md`
   - P-ARCH-006（元能力依赖倒置）→ `docs/retrospective/patterns/architecture-patterns/meta-capability-inversion.md`
8. ✅ **第一批5个高频脚本Skill化**（link-check-cmd、docgen-cmd、ci-check-cmd、atomization-finalize-cmd、check-duplication-cmd）（2026-07-01）
9. ✅ **质量保障（计划外增量）**：单元测试补充（282个用例）、性能基准测试（20个benchmark）、Windows编码兼容性修复（6处）、YAML注释规则Bug修复（2026-07-01）
10. ✅ **P2模块6：规范分层治理**（2026-07-01）
    - 在 `.agents/README.md` 中明确Core/Tools双层治理模型
    - 定义分层原则（定位/变更频率/依赖方向/测试要求/面向对象/代码含量6维度）
    - 明确15个Core目录和3个Tools目录的归属
    - 制定6条跨层引用规则（含commands/、tools/的特殊定位澄清）
    - 提供6题边界判定清单用于新增文件分类
    - 阐明三层正交关系：受众分层（.agents/docs）×信息粒度（L0/L1/L2）×职责分层（Core/Tools）
    - 更新目录树图标注[Core]/[Tools]标记，补充capabilities/、rules/、config/等缺失目录
    - 添加TOML frontmatter和changelog记录

## ⏳ 后续待执行（P2+P3长期）

| 优先级 | 行动项 | 触发条件 |
|--------|-------|---------|
| P2 | **模块7：模型路由层** | 多模型API可用时，在SKILL.md frontmatter增加model_hint字段 |
| P2 | **模块8：资源调度框架** | 多Agent并发场景落地时，实施self-management资源分配 |
| P2 | **第二批脚本Skill化** | 根据实际使用频率重新评估优先级，封装下一批高频脚本 |
| P3 | **REGISTRY自动生成** | 当SKILL数量超过20个手动维护困难时，用docgen聚合frontmatter自动生成 |
| P3 | **asset-inventory登记** | 下次资产盘点时登记本报告为知识资产 |

## 执行原则（经验总结）

- **每完成一个模块，更新本报告**：✅ 已在路线图章节标记完成状态并补充偏差分析
- **严格遵循渐进式披露**：✅ SKILL.md控制在500行以内，原文档保留为深度参考
- **每个SKILL以forum-posting为样板**：✅ 五要素模型完整性通过check-skill-quality.py验证
- **使用三角验证**：✅ 重构过程中通过代码状态、测试结果、使用体验三源验证
- **Spec生命周期管理**：P0模块未走.trae/specs/流程直接实施，后续大模块应先建Spec再实施
- **预留质量保障时间**：架构重构约30%工时应预留于测试、边界验证、跨平台兼容（本次经验）
