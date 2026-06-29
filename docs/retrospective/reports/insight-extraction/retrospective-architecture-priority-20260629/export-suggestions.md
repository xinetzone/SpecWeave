+++
id = "architecture-priority-export-suggestions"
date = "2026-06-29"
type = "export-suggestions"
source = "README.md#知识沉淀+行动建议"
+++

# 知识沉淀路径与行动建议

## 一、可复用模式萃取

从本次架构评估中萃取 6 个可复用模式，建议沉淀至模式库：

| 模式 ID | 模式名称 | 成熟度 | 适用场景 | 沉淀路径 |
|---------|---------|--------|---------|---------|
| P-ARCH-001 | 渐进式披露架构（Progressive Disclosure Architecture） | L2 | 规范/能力体系入口设计 | `docs/retrospective/patterns/architecture/progressive-disclosure.md` |
| P-ARCH-002 | Markdown即接口（Markdown-as-Interface） | L3 | Skill/能力封装设计 | `docs/retrospective/patterns/architecture/markdown-as-interface.md` |
| P-ARCH-003 | 瓶颈优先重构法（Bottleneck-First Refactoring） | L2 | 架构重构优先级排序 | `docs/retrospective/patterns/architecture/bottleneck-first.md` |
| P-ARCH-004 | 不重构清单（No-Touch List） | L3 | 架构评估范围控制 | `docs/retrospective/patterns/architecture/no-touch-list.md` |
| P-ARCH-005 | 架构决策三角验证（Architecture Triangulation） | L2 | 架构决策证据采集 | `docs/retrospective/patterns/architecture/arch-triangulation.md` |
| P-ARCH-006 | 元能力依赖倒置（Meta-Capability Inversion） | L2 | 元能力/编排能力实现时机 | `docs/retrospective/patterns/architecture/meta-capability-inversion.md` |

### 模式详细说明

#### P-ARCH-001 渐进式披露架构

**问题**：成熟的规范体系文档量巨大，新 Agent 入门需要读取大量文档，浪费上下文窗口。

**解决方案**：三层入口架构：
- L0 入口层（<100行）：ONBOARDING.md——身份+能力速查+路由表
- L1 索引层（<500行/能力）：SKILL.md——触发词+决策树+核心步骤+安全清单
- L2 深度层（不限）：原规范文档——完整参考手册

**正反例**：
- ✅ Firecrawl agent-onboarding 设计
- ✅ SKILL-TEMPLATE 五要素模型
- ❌ 当前 PDR 协议要求"全量读取所有前置文档"

---

#### P-ARCH-002 Markdown即接口

**问题**：Markdown 文档是叙事结构（适合人类阅读），但 Agent 需要接口结构（可调用）。

**解决方案**：用 Markdown 表达接口结构——SKILL.md 同时满足人类可读和机器可调用：
- frontmatter：结构化元数据（id、触发词、参数类型）
- 触发词描述：自然语言触发条件（Agent-First）
- 决策树：明确的分支判断逻辑
- 核心步骤：可执行的操作序列
- 安全检查清单：执行前后的验证点

**成熟度**：L3（有 forum-posting 成功实例，有 SKILL-TEMPLATE 模板）

---

#### P-ARCH-003 瓶颈优先重构法

**问题**：架构重构时容易陷入"先改最容易的"或"全面重构"两个极端。

**解决方案**：
1. 用成熟度分层模型（L0缺失/L1规划/L2起步/L3可用/L4成熟）评估各层
2. 找到全局瓶颈（最低成熟度的层）
3. 所有重构围绕解除瓶颈展开
4. 瓶颈解除后重新评估找下一个瓶颈
5. 非瓶颈层的优化推迟

**本次应用**：能力发现层 L0 缺失 → 先建注册中心（P0模块1）

---

#### P-ARCH-004 不重构清单

**问题**：架构评估容易陷入"重构癖"，什么都想改，导致范围蔓延。

**解决方案**：架构评估必须输出三类清单：
- ✅ 重构清单（按优先级排序，每个有理由）
- ❌ 不重构清单（每个项必须说明为什么不动）
- ⏸️ 暂缓清单（条件不满足时不动，明确触发条件）

**本次应用**：6个不重构项（阶段守卫、角色体系、工作流、协议层、硬编码规则、自我演进模块）

---

#### P-ARCH-005 架构决策三角验证

**问题**：架构决策容易基于单一视角（只看代码/只凭感觉/只抄标杆），导致偏差。

**解决方案**：架构决策必须同时覆盖三个视角：
1. **代码视角（What is）**：读代码/看文件，了解当前实际状态
2. **使用视角（What hurts）**：实际使用中的痛点和摩擦点
3. **标杆视角（What good looks like）**：外部优秀实践作为参照

**缺少任何一个的后果**：
- 缺标杆：不知道好的设计是什么样
- 缺使用痛点：变成象牙塔架构
- 缺代码实际：变成空中楼阁

---

#### P-ARCH-006 元能力依赖倒置

**问题**：编排类/元能力（如自我演进模块）往往被放在早期实现，但它们依赖的原子能力还未标准化。

**解决方案**：正确的实现顺序：
1. 先定义原子能力的标准接口（SKILL.md 规范）
2. 实现核心原子能力（指令集/脚本的SKILL封装）
3. 再在原子能力之上构建编排/元能力

**类比**：微服务架构——先 API 契约，再服务实现，最后服务编排。

---

## 二、知识沉淀路径

### 应更新的现有文档

| 目标文档 | 更新内容 | 优先级 |
|---------|---------|--------|
| [.agents/README.md](file:///d:/spaces/SpecWeave/.agents/README.md) | 在路线图中加入架构重构 P0 模块规划 | P0 |
| [.agents/rules/skill-development.md](file:///d:/spaces/SpecWeave/.agents/rules/skill-development.md) | 补充「命令集Skill化」「脚本Skill化」规范 | P1 |
| [docs/retrospective/patterns/README.md](file:///d:/spaces/SpecWeave/docs/retrospective/patterns/README.md) | 新增 6 个架构模式索引 | P1 |
| [docs/retrospective/assets/asset-inventory.md](file:///d:/spaces/SpecWeave/docs/retrospective/assets/asset-inventory.md) | 登记本报告为知识资产 | P2 |

### 应新建的文档（P0模块实施时创建）

| 新文档 | 所属模块 | 创建时机 |
|--------|---------|---------|
| `.agents/capabilities/ONBOARDING.md` | P0模块1 | 模块1实施时 |
| `.agents/capabilities/REGISTRY.md` | P0模块1 | 模块1实施时 |
| `.agents/skills/retrospective/SKILL.md` | P0模块2 | 模块2实施时 |
| `.agents/skills/insight/SKILL.md` | P0模块2 | 模块2实施时 |
| `.agents/skills/atomization/SKILL.md` | P0模块2 | 模块2实施时 |
| `.agents/skills/export-report/SKILL.md` | P0模块2 | 模块2实施时 |
| `.agents/skills/atomic-commit/SKILL.md` | P0模块2 | 模块2实施时 |
| `.agents/protocols/agent-onboarding.md` | P0模块3 | 模块3实施时 |

---

## 三、下一步行动建议

### 立即执行（今天）

1. ✅ **完成本次复盘原子化**（当前任务）
2. 📋 **创建 P0 模块1任务**：在 `.trae/specs/` 下创建能力注册中心的 spec

### 近期执行（本周）

3. **实施 P0模块1**：创建 `.agents/capabilities/` 目录、ONBOARDING.md、REGISTRY.md
4. **实施 P0模块2**：先做 retrospective 和 export-report 两个指令集的SKILL化（高频使用）
5. **更新 skill-development.md**：补充指令集和脚本Skill化的具体规范

### 中期执行（本月）

6. 完成剩余 3 个指令集SKILL化
7. 实施 P0模块3（Agent Onboarding协议）
8. 沉淀 6 个可复用模式到模式库
9. 第一批5个高频脚本Skill化

### 执行原则

- **每完成一个模块，更新本报告**：在路线图章节标记完成状态
- **严格遵循渐进式披露**：新创建的SKILL.md控制在500行以内，原文档保留为深度参考
- **每个SKILL以forum-posting为样板**：确保五要素模型完整性
- **使用三角验证**：重构过程中持续收集代码状态、使用痛点、标杆对照
