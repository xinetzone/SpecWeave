# .agents/docs 与 docs 分离方案 — 产品需求文档

## Overview
- **Summary**：基于第一性原理和七概念方法论，设计一个渐进式迁移方案，将 `.agents/docs/` 中面向人类阅读的文档逐步迁移到根目录 `docs/`，同时保留 agent 路由必读文件，减少 agent 的识别压力
- **Purpose**：解决当前 `.agents/docs/` 中人类文档与智能体专属文档混放导致的 agent 认知开销问题，实现"路径角色化"——路径名本身承担"谁该读"的信号
- **Target Users**：AI Agent（减少识别压力）、项目维护者（提升文档可发现性）、开发者（提升知识获取效率）

## Goals
- 建立清晰的文档分类矩阵：将 `.agents/docs/` 中所有文件标记为"Agent必留"或"人类迁移"
- 设计分批次渐进迁移路线图，每批次可独立验证、可回滚
- 制定标准化迁移操作流程（迁移→更新引用→验证→提交）
- 迁移完成后，`docs/` 成为人类文档主入口，`.agents/docs/` 仅保留 agent 路由必读文件

## Non-Goals (Out of Scope)
- 不改变文档实质内容（如修改Wiki正文），仅做结构性迁移
- 不涉及 vendor/ 子模块的文档迁移
- 不重新设计 learning Wiki 的 8 主题分类体系
- 不创建新的文档内容，仅做位置调整

## Background & Context

### 当前状态
- `.agents/docs/` 包含 679 个知识条目、69 个 Wiki、8 主题分类体系，体量巨大
- 人类文档与智能体专属文档混放，agent 需要通过决策表判断"该读哪个"
- 根目录 `docs/` 仅包含 `DEPRECATED.md`，处于废弃状态
- `global-core-rules.md` 中已声明路径解析规则：所有 `docs/` 引用解析为 `.agents/docs/`

### 核心问题（第一性原理分析）
1. **路径歧义**：`docs/` 相对路径在不同文件中解析结果不同（根 `docs/` vs `.agents/docs/`）
2. **认知开销**：agent 需要执行 5 条归类规则判断文件类型，token 浪费
3. **边界模糊**：部分文件同时被 agent 引用和人类阅读，归类困难
4. **信号混乱**：空的根 `docs/` + 矛盾声明 = agent 困惑"是不是漏读了"

### 七概念方法论应用
- **R（复盘）**：回顾历史决策——之前将人类文档迁移到 `.agents/docs/` 是为了统一容器，但导致了路径歧义
- **I（洞察）**：核心洞察——文档的本质区分维度是"受众"（人类 vs agent），而非"来源"（原 `docs/` vs `.agents/`）
- **E（萃取）**：萃取可复用模式——路径角色化原则：路径名直接反映受众
- **C（原子提交）**：每批次迁移独立提交，可回滚
- **A（原子化）**：按主题分批迁移，每批不超过 100 个文件
- **F（第一性原理）**：文档的价值由受众和触发机制决定，而非存储位置
- **V（对抗性审查）**：迁移前验证链接，迁移后验证路由不中断

## Functional Requirements
- **FR-1**：建立文档分类矩阵，将 `.agents/docs/` 下所有文件标记为"Agent必留"或"人类迁移"
- **FR-2**：设计分批次渐进迁移路线图，5-7 批完成，每批不超过 100 个文件
- **FR-3**：制定标准化迁移操作流程：迁移文件 → 更新路径引用 → 运行 check-links.py 验证 → 更新 context-routing.md → 提交原子 commit
- **FR-4**：更新全局核心规则中的路径解析规则，反映新的文档分布
- **FR-5**：更新 AGENTS.md 中的文档边界声明，与新结构一致

## Non-Functional Requirements
- **NFR-1**：迁移过程中 agent 路由不得中断——每批迁移完成后必须验证路由表引用正确
- **NFR-2**：链接有效性——所有内部链接迁移后必须有效
- **NFR-3**：原子性——每批迁移独立提交，可回滚
- **NFR-4**：渐进式——允许随时暂停迁移，当前状态保持可用

## Constraints
- **Technical**：现有路径解析规则（`docs/` → `.agents/docs/`）在迁移期间需临时保留，迁移完成后切换
- **Dependencies**：依赖 `check-links.py` 脚本进行链接验证
- **Timeline**：无硬性时间要求，按批次渐进执行

## Assumptions
- 迁移过程中不会有新的文档写入 `.agents/docs/`
- `check-links.py` 脚本可正常运行
- 所有迁移文件的 frontmatter `source` 字段已正确标注溯源

## Acceptance Criteria

### AC-1：文档分类矩阵建立
- **Given**：`.agents/docs/` 目录结构完整
- **When**：对所有文件进行分类判定
- **Then**：每个文件明确标记为"Agent必留"或"人类迁移"，形成分类清单
- **Verification**：`human-judgment`（审查分类清单的完整性和准确性）

### AC-2：迁移路线图设计
- **Given**：分类矩阵已建立
- **When**：按主题和依赖关系分组
- **Then**：形成 5-7 批迁移计划，每批不超过 100 个文件，包含依赖关系说明
- **Verification**：`human-judgment`（审查路线图的合理性）

### AC-3：第一批迁移执行
- **Given**：迁移流程已定义
- **When**：执行第一批文件迁移
- **Then**：文件成功移动到 `docs/`，路径引用更新，`check-links.py` 验证通过，路由表更新，原子提交完成
- **Verification**：`programmatic`（check-links.py 输出无错误）

### AC-4：路径解析规则更新
- **Given**：所有批次迁移完成
- **When**：更新全局核心规则
- **Then**：路径解析规则改为"`.agents/docs/` 仅包含 agent 必读文件，`docs/` 包含人类文档"，根 `docs/` 不再标记为废弃
- **Verification**：`human-judgment`（审查规则更新的准确性）

### AC-5：AGENTS.md 文档边界声明更新
- **Given**：所有批次迁移完成
- **When**：更新 AGENTS.md
- **Then**：文档边界声明反映新的物理结构
- **Verification**：`human-judgment`（审查声明与物理现实一致）

## Open Questions
- [ ] 是否需要保留 `.agents/docs/` 中的部分人类文档作为 agent 的参考资料？
- [ ] 迁移完成后，`docs/` 和 `.agents/docs/` 的路径引用策略如何调整？
- [ ] 是否需要更新 `DEPRECATED.md` 文件的内容？

---

**Spec 版本**：v1.0  
**创建日期**：2026-07-15  
**来源**：用户请求 `/spec 第一性原理+七概念+ .agents/docs 太混乱了，考虑后续不断的萃取和迭代成人类可读文档，并逐步迁移到 docs`