---
id: "l2-progressive-disclosure-optimization"
date: "2026-07-12"
type: "best-practice"
source: "spec-loader.py audit验证 + 多场景加载实测"
x-toml-ref: "../../../.meta/toml/docs/knowledge/best-practices/l2-progressive-disclosure-optimization.toml"
title: "L2 渐进式披露机制优化建议"
---
# L2 渐进式披露机制优化建议

## 1. 背景与现状

L2 渐进式披露运行时规范加载器（[spec_loader.py](../../../.agents/scripts/lib/spec_loader.py) + [spec-loader.py](../../../.agents/scripts/spec-loader.py)）已实现三层按需加载架构（L0入口→L1索引→L2详细规范），当前支持 20 种任务类型路由、39 个规范文件、-v 详细日志追踪。

### 1.1 当前架构实测数据

| 任务类型 | L0 | L1 | L2 | 总文件 | 总字符 | L2占比 |
|---------|----|----|----|-------|-------|-------|
| 代码审查 | 1 | 5 | 2 | 8 | 24,955 | 14% |
| 原子提交 | 1 | 5 | 3 | 9 | 40,803 | 47% |
| 原子化拆分 | 1 | 5 | 3 | 9 | 37,358 | 43% |
| 知识图谱 | 1 | 5 | 1 | 7 | 31,493 | 32% |
| 多类型匹配（开发+测试+审查） | 1 | 5 | 7 | 13 | 34,895 | 52% |
| 无匹配兜底 | 1 | 5 | 0 | 6 | 21,464 | 0% |

**关键发现**：
- L1层固定加载约19.5KB（5个文件），占单任务加载量的50%~90%
- L2按需加载效果显著：最少仅25KB（无匹配兜底），最多40KB（原子提交）
- 相比一次性加载全部规范（预估>500KB），上下文压缩比达 **87%~95%**

---

## 2. 已识别问题与优化建议

### P0 - 高优先级（影响核心机制正确性）

#### 2.1 L1层粒度过粗，全量加载必要性不足

**问题**：当前L1固定加载5个文件（capability-registry.md、context-routing.md、global-core-rules.md、capability-boundaries.md、skills/README.md）合计约19.5KB。实测发现：
- `context-routing.md`（8KB）主要是任务类型→规范映射表，加载器已有 `TASK_ROUTING` 字典，文件内容与代码重复
- `capability-registry.md` 入口索引文件仅1.1KB，但其子分册（02-skills.md、03-commands.md等）未被L1加载
- `skills/README.md`（5.7KB）包含完整Skill清单，但加载器已内建TASK_ROUTING，内容冗余

**建议**：
1. **L1拆分**：将L1分为 L1a（核心规则，始终加载）和 L1b（索引，按需加载）
   - L1a（~5KB）：global-core-rules.md + capability-boundaries.md（启动协议和边界规则，必须始终加载）
   - L1b（~15KB）：context-routing.md + capability-registry + skills/README.md（仅规划阶段或明确需要时加载）
2. **去重**：TASK_ROUTING 字典与 context-routing.md 内容存在重复，考虑从Markdown文件动态解析路由表，消除双维护

**预期收益**：执行阶段L0+L1基线从21KB降至约7KB，L2加载比例提升至60%+

#### 2.2 缺失路由的命令集无法按需加载

**问题**：当前20种任务类型中，有3个commands目录下的指令集缺少对应的Skill门面或L2路由：
- `commands/first-principles.md`（第一性原理）—— 有路由但无对应Skill门面
- `commands/file-creation.md`（文件创建）—— 有路由但无对应Skill门面
- `commands/adversarial-review.md`（对抗性评审）—— 有路由但无对应Skill门面

当用户触发"第一性原理分析"时，加载器只加载commands/目录的指令文档，没有加载对应的Skill门面（如果后续创建），可能导致执行流程不完整。

**建议**：
1. 为这3个命令集创建轻量级Skill门面（参考现有7个命令门面的模式），或
2. 在TASK_ROUTING中补充对应rules/protocols路径，确保加载完整上下文
3. 在audit命令中新增"覆盖度检查"：验证每个commands/*.md是否至少在一个TASK_ROUTING条目中被引用

---

### P1 - 中优先级（影响使用体验与效率）

#### 2.3 多类型匹配无优先级/去重策略

**问题**：当任务描述匹配多个类型时（如"开发新功能并测试代码审查"同时命中development、testing、code_review），当前加载器简单合并所有L2文件，共加载7个L2规范（34.9KB）。存在以下问题：
- 角色冲突：同时加载developer.md、reviewer.md、tester.md三个角色定义，Agent可能混淆角色定位
- 无优先级：无法区分主要任务类型和辅助任务类型
- 重复规则：rules/ai-coding-guidelines.md在development中加载，但testing/code_review可能也需要类似规则

**建议**：
1. **主类型判定**：按关键词出现位置/频率确定主任务类型，主类型加载完整L2，其他类型仅加载核心1-2个文件
2. **角色互斥**：同一任务中developer/reviewer/tester三角色互斥加载（主要角色+评审规则）
3. **max_chars智能分配**：根据主类型分配字符预算（主类型70%，辅助类型30%）

#### 2.4 无匹配任务兜底策略薄弱

**问题**：当任务描述无法匹配任何类型时（如"一个完全不匹配的任务描述xyz123"），加载器仅加载L0+L1（21KB）并输出WARNING日志，但没有：
- 提示Agent尝试模糊匹配或询问用户
- 提供最接近的任务类型建议
- 加载通用规则集（如ai-coding-guidelines.md）

**建议**：
1. **模糊匹配**：当精确匹配为0时，使用编辑距离/语义相似度推荐Top-3最接近的任务类型
2. **通用兜底L2**：无匹配时默认加载rules/ai-coding-guidelines.md + 通用开发流程，而非纯L0+L1
3. **交互式确认**：CLI模式下询问用户"是否是指XX任务？"

#### 2.5 vendor三层路由未集成

**问题**：AGENTS.md启动协议步骤2.1明确了"SpecWeave→vendor→flexloop"三层嵌套路由，但当前SpecLoader仅处理SpecWeave项目根目录的规范，无vendor区域嵌套路由能力。任务类型预检（步骤2.0）也未集成到加载器中。

**建议**：
1. 加载器初始化时检测 `vendor/AGENTS.md` 是否存在，自动构建嵌套路由树
2. TASK_ROUTING支持vendor子模块的任务类型前缀（如`flexloop:chaos_test`）
3. audit命令递归审计vendor子模块路由完整性

---

### P2 - 低优先级（增强功能与可观测性）

#### 2.6 缓存仅内存级，跨会话不持久

**问题**：SpecLoader的`_loaded`字典仅在实例生命周期内缓存，每次新会话都重新读取所有文件。对于长会话中多次调用load_for_task，虽然内存缓存生效，但跨会话无收益。

**建议**：
1. 基于文件mtime的轻量磁盘缓存：将规范文件路径+mtime+字符数缓存到`.agents/.cache/spec-loader.json`
2. 缓存失效策略：文件mtime变化时自动失效
3. 统计缓存命中率，在verbose日志中输出

#### 2.7 加载性能指标缺失

**问题**：当前日志只输出字符数，缺少：
- 文件读取耗时
- 各层加载耗时占比
- 缓存命中率统计
- 与"全量加载"基准的压缩比

**建议**：在verbose日志中增加性能指标段：
```
[PERF] L0加载: 1ms (1文件, 1.9KB)
[PERF] L1加载: 12ms (5文件, 19.5KB)
[PERF] L2加载: 8ms (3文件, 19.4KB)
[PERF] 总计: 21ms (9文件, 40.8KB) | 压缩比: 92% | 缓存命中: 0/9
```

#### 2.8 规范依赖声明与自动解析缺失

**问题**：当前L2文件列表是硬编码的（如code_review加载workflows/code-review.md + roles/reviewer.md），但规范文件之间可能存在隐式依赖：
- workflows/code-review.md 可能引用了 rules/ 下的评审规则
- skills/ 下的SKILL.md 可能依赖 commands/ 下的指令集

这些依赖没有显式声明，路由配置遗漏时会导致上下文缺失。

**建议**：
1. 在L2规范文件frontmatter中添加`depends_on`字段声明前置依赖
2. SpecLoader加载L2时递归解析依赖，自动补全缺失的前置规范
3. audit命令检查依赖链完整性，检测循环依赖

#### 2.9 max_chars限载策略过于粗暴

**问题**：当前max_chars达到上限时直接break，可能截断重要的L2规范（如正在加载的SKILL.md只加载了一半），导致Agent收到不完整的上下文。

**建议**：
1. **文件级原子性**：max_chars按文件粒度检查，要么加载整个文件，要么跳过，不截断文件内容
2. **优先级排序**：L2文件按优先级排序（commands/ > skills/ > workflows/ > roles/ > rules/），优先加载高优先级文件
3. **预警机制**：达到80%预算时输出WARNING日志，提示上下文即将用尽

#### 2.10 与Agent启动协议的自动集成缺失

**问题**：当前SpecLoader是独立CLI工具，Agent启动时不会自动调用。AGENTS.md的启动协议（步骤1-3.5）需要Agent手动执行，容易遗漏。

**建议**：
1. 创建`.agents/hooks/session-start.py`启动钩子，Agent会话启动时自动调用SpecLoader加载L0+L1
2. 在ONBOARDING.md中明确"第一步调用spec-loader.py startup"
3. 将加载器集成到ci-check中，作为CI门禁的一环验证路由完整性

---

## 3. 优化路线图

### 第一阶段（立即修复）
- [ ] 2.2 为3个缺失Skill门面的命令集补充路由覆盖
- [ ] 2.4 无匹配任务加载通用兜底规则集（ai-coding-guidelines.md）
- [ ] 2.9 max_chars改为文件级原子性，不截断文件

### 第二阶段（近期优化）
- [ ] 2.1 L1拆分L1a/L1b，将基线从21KB降至7KB
- [ ] 2.3 多类型匹配主类型判定+角色互斥
- [ ] 2.7 加载性能指标输出
- [ ] 2.10 Agent启动钩子自动加载L0+L1

### 第三阶段（中长期演进）
- [ ] 2.5 vendor三层嵌套路由集成
- [ ] 2.6 基于mtime的磁盘缓存
- [ ] 2.8 规范依赖声明与自动解析
- [ ] TASK_ROUTING从Markdown动态解析，消除代码与文档双维护

---

## 4. 验证方法

每项优化完成后，通过以下方式验证效果：

```bash
# 1. 路由完整性审计
python .agents/scripts/spec-loader.py audit -v

# 2. 基准加载测试（各任务类型字符数对比）
python .agents/scripts/spec-loader.py task "代码审查" -v
python .agents/scripts/spec-loader.py task "提交代码" -v
python .agents/scripts/spec-loader.py task "复盘项目" -v

# 3. 无匹配兜底测试
python .agents/scripts/spec-loader.py task "随机无关任务xyz" -v

# 4. 多类型匹配测试
python .agents/scripts/spec-loader.py task "开发功能并测试和审查" -v

# 5. 全量加载对比基准（计算压缩比）
# 统计.agents/下所有.md文件总字符数作为分母
```

**优化目标**：
- 单任务平均上下文 < 30KB（当前平均约32KB）
- 无匹配兜底场景 < 15KB（当前21KB）
- 路由覆盖率100%（每个commands/*.md都有对应路由）
- audit零缺失文件

---

## 5. 相关文件索引

| 文件 | 职责 |
|------|------|
| [spec_loader.py](../../../.agents/scripts/lib/spec_loader.py) | L2加载器核心库（SpecLoader类、TASK_ROUTING、日志） |
| [spec-loader.py](../../../.agents/scripts/spec-loader.py) | CLI入口（task/layer/list-types/audit子命令） |
| [docgen.py](../../../.agents/scripts/docgen.py) | stats子命令自动统计核心指标 |
| [context-routing.md](../../../.agents/context-routing.md) | L1上下文路由表（与TASK_ROUTING需保持同步） |
| [02-skills.md](../../../.agents/capability-registry/02-skills.md) | Skill注册索引（L1能力注册中心分册） |
| [ONBOARDING.md](../../../.agents/ONBOARDING.md) | L0入口速查 |
