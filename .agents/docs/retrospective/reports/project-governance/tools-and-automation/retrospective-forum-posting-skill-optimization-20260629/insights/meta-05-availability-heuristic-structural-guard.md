---
id: "meta-availability-heuristic-structural-guard"
title: "Meta洞察5：\"就近直觉\"是系统性认知偏差，需要结构性机制防范"
source: "../insight-extraction.md#发现10就近直觉是一种系统性认知偏差不是粗心大意"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/meta-05-availability-heuristic-structural-guard.toml"
---
# Meta洞察5："就近直觉"是系统性认知偏差，需要结构性机制防范

→ 正式模式：[availability-heuristic-structural-guard.md](../../../../../patterns/methodology-patterns/governance-strategy/availability-heuristic-structural-guard.md)（已入库L1）

## 现象

容易把路由违归因于"粗心"或"没认真看AGENTS.md"，但根因更深层——这不是态度问题，是认知偏差问题。

## 根因：可得性启发（Availability Heuristic）

人类和AI都倾向于使用**最容易获取的信息**（工作目录下的文件、最近读取的内容），而不是**最权威但获取成本更高的信息**（vendor子模块三层路由后的文件、需要主动搜索的资产）。

这是一种系统性认知偏差，不是"粗心大意"，不能靠"下次更认真"来解决。

## 其他类似系统性偏差

| 偏差类型 | 表现 | 影响 |
|---------|------|------|
| 可得性启发（就近直觉） | 优先用手边最容易获取的信息 | 错过vendor等更权威的资产 |
| 近因偏差 | 最近修改/读取的文件更重要 | 忽略历史沉淀的规范 |
| 显著性偏差 | 大文件/显著位置更重要 | 忽略小但关键的规则文件 |
| 确认偏差 | 熟悉的模式优先匹配 | 错误套用旧经验到新场景 |

## 解决方案：结构性防范而非个人警惕

既然是系统性偏差，就必须靠**结构性机制**来防范，而不是靠"更认真"：

1. **预检清单**：启动协议步骤2.0任务类型预检——强制检查vendor资产映射表
2. **自检点**：步骤3.5结构化自检——3个问题确认无遗漏
3. **按任务类型索引**：vendor资产按"做什么事"组织而非"是什么资产"组织，零摩擦命中
4. **自动化门禁**：check-skill-quality.py等脚本自动检测规范合规性，机器不会有认知偏差
5. **模板预装最佳实践**：SKILL-TEMPLATE.md把五要素、检查清单都预置好，不用靠记忆

## 关联洞察

- [finding-01-three-layer-routing-non-symmetric-trigger.md](finding-01-three-layer-routing-non-symmetric-trigger.md) — 就近直觉导致的具体陷阱
- [meta-03-context-compression-cognitive-narrowing.md](meta-03-context-compression-cognitive-narrowing.md) — 上下文压缩放大可得性启发
- [task-type-first-indexing.md](../../../../../patterns/methodology-patterns/governance-strategy/task-type-first-indexing.md) — 任务类型索引是结构性防范手段之一

---
*来源：[forum-posting Skill优化复盘](../README.md)*
