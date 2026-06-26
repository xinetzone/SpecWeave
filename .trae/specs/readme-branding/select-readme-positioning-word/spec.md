# README 定位关键词选型 Spec

## Why
`d:\AI\README.md` 当前缺少一个具有品牌辨识度的核心定位词。需要像 DeepSeek、Midjourney、Notion 那样——一个复合/自创的独特词汇，既能高度概括项目本质，又具备品牌记忆点和行业辨识度。

## What Changes
- 为 README.md 选定一个品牌级定位关键词，放置在标题下方作为项目标识
- 该词应为复合词或自创词，兼具语义精准性和品牌独特性

## Impact
- Affected specs: 无
- Affected code: `d:\AI\README.md`

## 项目本质提炼

本项目的核心可浓缩为三个维度：

| 维度 | 关键词 | 说明 |
|------|--------|------|
| 内容形态 | Spec（规范） | 角色定义、协作协议、工作流、规则体系 |
| 组织方式 | Weave（编织） | 多智能体角色交织协作，协议与工作流彼此关联 |
| 治理属性 | Pact（契约） | AGENTS.md 全局契约，角色能力边界，协作约定 |

## 候选词分析

### 候选词一览

| 候选词 | 构成 | 语义 | 品牌感 | 记忆度 |
|--------|------|------|--------|--------|
| **SpecWeave** | Spec + Weave | 规范之网——将角色、协议、工作流编织成可演进的体系 | 高，独特且具象 | 高，有画面感 |
| **AgentPact** | Agent + Pact | 智能体契约——强调角色间的约定与边界 | 高，有故事感 | 高，Pact 有分量 |
| **AgentCraft** | Agent + Craft | 智能体工艺——强调工程方法论 | 中，Craft 较通用 | 中 |
| **ProtoForge** | Protocol + Forge | 协议锻造——与已有 AgentForge 案例呼应 | 高，有家族品牌感 | 中，Proto 可能歧义 |

### 逐词深度评估

**SpecWeave**（推荐）

- 语义拆解：Spec（Specification，规范体系）+ Weave（编织，交织）= "将规范编织为一体"
- 精准对应项目的三个层次：
  - 纵向上，角色→协议→工作流→规则层层交织
  - 横向上，orchestrator/architect/developer/reviewer/tester 角色彼此协作
  - 时间上，八模块自我演进体系形成持续迭代的"生长中的织物"
- 品牌联想：织物（fabric）在技术领域有积极的隐喻传统——如 "fabric of the internet"、"data fabric"、"security fabric"
- 中英兼容：中文可译为"规范之网"或"织范"，英文 SpecWeave 可直接作为品牌名
- 排他性：Google 搜索无重名项目，GitHub 无同名仓库

**AgentPact**

- 语义拆解：Agent（智能体）+ Pact（契约、盟约）= "智能体之间的契约体系"
- 与 AGENTS.md 中"全局契约"（AGENTS Manifest）形成直接语义呼应
- 强调治理性和约束力，政治/法律隐喻赋予庄重感
- 中文译为"智能体契约"自然且有力
- 局限：Pact 侧重"约定"维度，未能覆盖"编织/生长/演进"的动态特性

**AgentCraft**

- 语义拆解：Agent（智能体）+ Craft（工艺、技艺）= "智能体开发的工艺之道"
- 强调工程方法和最佳实践
- 局限：Craft 在技术领域已被广泛使用（Minecraft、Warcraft 等），区分度不足

**ProtoForge**

- 语义拆解：Protocol（协议）+ Forge（锻造）= "协议的锻造工坊"
- 与已有 `AgentForge` 复用案例形成品牌家族
- 局限：Proto 在软件工程中通常指 Prototype（原型），可能引起歧义；Forge 更侧重"制造"而非"规范治理"

## 推荐方案：**SpecWeave**

### 推荐理由

1. **语义全覆盖**：同时命中"规范"（Spec）和"体系性关联"（Weave）两个核心维度，AgentPact 只覆盖契约维度，AgentCraft 只覆盖工程维度。

2. **品牌辨识度**：复合词结构类似 DeepSeek、DreamWeaver、CodeWeaver，朗朗上口且易于记忆。中文"织范"音韵简洁，可作中文品牌名。

3. **隐喻延展性**：编织隐喻可自然延伸出丰富的品牌叙事——
   - "每一条规范都是一根丝线，编织在一起才成为可依赖的体系"
   - "角色如经纬，协议如针法，工作流如图样"
   - "自我演进模块让这张网具有生命力——破损处自修复，薄弱处自强化"

4. **视觉化潜力**：编织/网状结构天然适合 Logo 设计和视觉表达。

5. **行业定位清晰**：Spec 明确指向 Specification/规范领域，不会与通用 AI 项目混淆。

## ADDED Requirements
### Requirement: README 品牌定位词
系统应在 README.md 标题下方显著位置展示品牌级定位词 **SpecWeave**，以独特且专业的复合词概括项目本质。

#### Scenario: 读者首次浏览 README
- **WHEN** 读者打开 README.md
- **THEN** 在标题区域看到 "SpecWeave" 作为项目品牌标识，附带简短中文释义（如"规范之网"），立即理解项目是将多智能体规范编织为有机体系的框架

#### Scenario: 搜索引擎检索
- **WHEN** 用户在搜索引擎中输入 "SpecWeave"
- **THEN** 结果唯一指向本项目，不存在同名竞品混淆
