+++
id = "architecture-priority-export-action-items"
date = "2026-06-30"
type = "export-action-items"
source = "export-suggestions.md#三下一步行动建议"
+++

# 三、下一步行动建议

> **Spec 生命周期说明**：`.trae/specs/` 是 Spec 工作区（不成熟、开发中的 Spec），按主题分类组织任务；当 Spec 成熟实施后，最终归档到 `.agents/` 对应子目录（commands/、rules/、protocols/、capabilities/、skills/ 等），成为正式规范体系的一部分。`.trae/specs/` 保留实施过程的完整记录（spec.md、tasks.md、checklist.md），`.agents/` 存放稳定可引用的L1/L2层正式文档。

## 立即执行（今天）

1. ✅ **完成本次复盘原子化**
2. ✅ **创建 P0 模块1任务**：在 `.trae/specs/` 下创建能力注册中心的 Spec（不成熟Spec工作区；成熟后归档至 `.agents/capabilities/`）

## 近期执行（本周）

3. ✅ **实施 P0模块1**：已创建 `.agents/capabilities/` 目录（ARCHITECTURE.md、ONBOARDING-TEMPLATE.md、REGISTRY-TEMPLATE.md、README.md）
4. ✅ **实施 P0模块2**：已完成5个指令集SKILL化（atomic-commit、atomization、retrospective、insight、export-report）
5. ✅ **更新 skill-development.md**：已补充指令集和脚本Skill化的具体规范（五要素模型、双方案模式、资产盘点、验证清单等）

## 中期执行（本月）

6. ✅ **完成剩余指令集SKILL化**：6个命令集门面全部完成（新增mermaid-cmd），另已完成2个完整Skill（forum-posting、home-assistant）
7. ✅ **实施 P0模块3（Agent Onboarding协议）**：已创建 `.agents/protocols/onboarding-protocol.md`
8. **沉淀 6 个可复用模式到模式库**：P-ARCH-001（渐进式披露架构）已通过 `.agents/capabilities/ARCHITECTURE.md` 落地为正式规范；架构决策三角验证已沉淀为 `triangular-source-verification.md`；其余4个模式（Markdown即接口、瓶颈优先重构法、不重构清单、元能力依赖倒置）待沉淀至 `docs/retrospective/patterns/`
9. 第一批5个高频脚本Skill化

## 执行原则

- **每完成一个模块，更新本报告**：在路线图章节标记完成状态
- **严格遵循渐进式披露**：新创建的SKILL.md控制在500行以内，原文档保留为深度参考
- **每个SKILL以forum-posting为样板**：确保五要素模型完整性
- **使用三角验证**：重构过程中持续收集代码状态、使用痛点、标杆对照
- **Spec生命周期管理**：`.trae/specs/` 做开发工作区，成熟实施后归档到 `.agents/` 对应目录，保持 `.agents/` 的正式规范地位
