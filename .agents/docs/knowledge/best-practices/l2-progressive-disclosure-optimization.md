---
id: "l2-progressive-disclosure-optimization"
date: "2026-07-12"
type: "best-practice"
source: "spec-loader.py audit验证 + 多场景加载实测"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/best-practices/l2-progressive-disclosure-optimization.toml"
title: "L2 渐进式披露机制优化建议"
---
# L2 渐进式披露机制优化建议

## 1. 背景与现状

L2 渐进式披露运行时规范加载器（[spec_loader.py](../../../scripts/lib/spec_loader.py) + [spec-loader.py](../../../scripts/spec-loader.py)）已实现四层按需加载架构（L0入口→L1a核心规则→L1b索引→L2详细规范），当前支持 20 种任务类型路由、39 个规范文件、-v 详细性能日志追踪（路由匹配/L2解析/预算决策全链路DEBUG）。

### 1.1 当前架构实测数据（2026-07-12 一期优化后）

| 任务类型 | L0 | L1a | L1b | L2 | 总文件 | 总字符 | L2占比 |
|---------|----|-----|-----|----|-------|-------|-------|
| 代码审查（execution） | 1 | 2 | 0 | 2 | 5 | 10,141 | 34% |
| 原子提交 | 1 | 2 | 0 | 3 | 6 | 25,989 | 74% |
| 原子化拆分 | 1 | 2 | 0 | 3 | 6 | 22,544 | 71% |
| 知识图谱 | 1 | 2 | 0 | 1 | 4 | 16,679 | 60% |
| 第一性原理 | 1 | 2 | 0 | 1 | 4 | 11,249 | 41% |
| 复盘 | 1 | 2 | 0 | 2 | 5 | 17,395 | 62% |
| 多类型匹配（开发+测试+审查） | 1 | 2 | 0 | 5 | 8 | 19,020 | 65% |
| 无匹配兜底 | 1 | 2 | 0 | 1 | 4 | 12,534 | 47% |
| 代码审查（planning含L1b） | 1 | 2 | 3 | 2 | 8 | 24,955 | 14% |

**关键发现**：
- **四层架构生效**：执行阶段仅加载L0(1)+L1a(2)=3个基线文件（~6.6KB），相比优化前L0+L1=6个文件（~21KB），基线压缩68%
- L1b（3个索引文件~15KB）仅在planning/startup阶段加载，执行阶段完全跳过
- L2按需加载效果显著：最轻场景~10KB（代码审查），最重~26KB（原子提交），无匹配兜底~12.5KB
- 相比一次性加载全部规范（39个文件~150KB+），上下文压缩比达 **83%~93%**

---

## 2. 已识别问题与优化建议

### P0 - 高优先级（影响核心机制正确性）

#### 2.1 L1层粒度过粗，全量加载必要性不足 ✅ 已完成

**问题（已修复）**：优化前L1固定加载5个文件合计约19.5KB，其中`context-routing.md`与代码中`TASK_ROUTING`字典重复、`skills/README.md`包含完整Skill清单在执行阶段不必要。

**已实施**：

1. **L1a/L1b拆分**：
   - L1a（核心规则，~5KB始终加载）：`global-core-rules.md` + `capability-boundaries.md`（启动协议和边界规则）
   - L1b（索引，~15KB按需加载）：`context-routing.md` + `capability-registry.md` + `skills/README.md`（仅planning/startup阶段加载）
2. **stage参数**：`load_for_task()`新增`stage`参数（`execution`/`planning`/`startup`），执行阶段自动跳过L1b
3. **实测效果**：执行阶段基线从~21KB降至~6.6KB（L0+L1a=3个文件），基线压缩68%

**后续优化方向（未实施）**：
- TASK_ROUTING字典与context-routing.md仍存在双维护问题，考虑从Markdown文件动态解析路由表（列入第三阶段路线图）

#### 2.2 缺失路由的命令集无法按需加载 ✅ 已完成

**问题（已修复）**：优化前3个commands指令集缺少对应的Skill门面或L2路由覆盖，导致触发时上下文不完整。

**已实施**：
- 新增`first_principles`路由类型（TASK_ROUTING），加载`commands/first-principles.md` + 配套rules/workflows
- 为`file_creation`和`adversarial_review`路由补充`rules/ai-coding-guidelines.md`，确保通用编码规则被加载
- 当前20个任务类型路由覆盖全部10个commands指令集

**后续优化方向（未实施）**：
- 为尚未创建Skill门面的命令集（file-creation、adversarial-review等）补充轻量级Skill门面

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

#### 2.4 无匹配任务兜底策略薄弱 ✅ 部分完成

**问题（已部分修复）**：优化前无匹配时仅加载L0+L1（21KB），不加载任何通用规则。

**已实施**：
- **通用兜底L2**：无匹配时自动加载`rules/ai-coding-guidelines.md`，兜底场景从21KB降至~12.5KB（L0+L1a+通用规范）
- **WARNING提示**：输出`任务类型无匹配 | 输入=... | 路由数=N | 将加载通用兜底规范`日志
- **FALLBACK_L2_SPECS常量**：集中管理兜底文件列表，方便后续扩展

**未实施（后续优化）**：
- 模糊匹配推荐Top-3最接近的任务类型（编辑距离/语义相似度）
- CLI模式下交互式确认"是否是指XX任务？"
- 更丰富的通用兜底规则集（除ai-coding-guidelines外补充其他通用规范）

#### 2.5 vendor三层路由未集成

**问题**：AGENTS.md启动协议步骤2.1明确了"SpecWeave→vendor→flexloop"三层嵌套路由，但当前SpecLoader仅处理SpecWeave项目根目录的规范，无vendor区域嵌套路由能力。任务类型预检（步骤2.0）也未集成到加载器中。

**建议**：
1. 加载器初始化时检测 `vendor/AGENTS.md` 是否存在，自动构建嵌套路由树
2. TASK_ROUTING支持vendor子模块的任务类型前缀（如`flexloop:chaos_test`）
3. audit命令递归审计vendor子模块路由完整性

---

### P2 - 低优先级（增强功能与可观测性）

#### 2.6 缓存仅内存级，跨会话不持久 ✅ 已完成

**问题（已修复）**：优化前SpecLoader的`_loaded`字典仅在实例生命周期内缓存，每次新会话都重新读取所有文件。

**已实施**：

1. **基于mtime的磁盘缓存**：将规范文件路径+mtime+大小+字符数缓存到`.agents/.cache/spec-loader.json`
2. **原子写入**：通过临时文件+os.replace实现缓存文件原子写入，避免并发写入损坏
3. **版本化缓存**：缓存key包含`CACHE_VERSION`（当前v2），版本不匹配自动失效
4. **批量读取优化**：`_read_spec_file_batch()`实现MEM-HIT→DISK-HIT→STALE→MISS→MISSING五级分类
5. **CLI管理命令**：`cache-stats`查看命中率统计、`cache-clear`清除磁盘缓存
6. **verbose日志**：命中率和各类命中计数在DEBUG日志中输出（`[批量读取]` 汇总行）
7. **`use_disk_cache`参数**：支持`--no-cache` CLI参数关闭磁盘缓存

#### 2.7 加载性能指标缺失 ✅ 已完成

**问题**：当前日志只输出字符数，缺少文件读取耗时、各层加载耗时占比、缓存命中率统计、路由匹配详情、预算决策过程等排查信息。

**已实施**（verbose/-v模式下DEBUG日志输出）：

1. **分层耗时**：每层加载后输出 `[TIMER] 步骤X/X 完成 | 耗时=Nms | 文件=N个 | 字符=N`
2. **路由匹配详情**：每个任务类型的关键词扫描输出命中/未命中、位置权重、精确匹配加分、最终权重、排名详情
   - `[路由匹配] 命中 | type=xxx | keyword="xxx" | pos=N | position_weight=0.xxx | exact_bonus=0.0 | total_weight=2.xxx`
   - `[路由匹配] 权重排序详情:` → 逐行列出排名/权重/位置
3. **L2解析详情**：类型处理（主/辅）、去重跳过、角色跳过原因、优先级重排前后对比、解析总耗时
   - `[L2解析] 类型处理完成 | type=xxx | role=主类型 | 新增文件=N | 耗时=Nms`
   - `[L2解析] 辅助类型跳过角色文件 | type=xxx | path=xxx | 原因=角色互斥`
4. **文件级预算决策链**：max_chars限载时每个文件的完整决策过程
   - `[预算] max_chars=N | L0+L1基线=Nc | L2可用预算=Nc`
   - `[L2#N] 预算检查 | path=xxx | 当前=Nc (XX%) | 剩余=Nc | 预估=Nc(stat(filename)) | 加载后预估=Nc | 将超限=True/False`
   - `[L2#N] 文件超出剩余预算，跳过 | path=xxx | 预估=Nc | 剩余=Nc | 超限比=XX% | 决策=SKIP`
   - `[L2#N] 加载成功 | path=xxx | 实际=N字符(预估偏差=±N) | 累计=Nc(XX%) | 耗时=Nms`
5. **批量读取效率**：`MEM-HIT/DISK-HIT/STALE/MISS/MISSING`分类统计、快速路径覆盖率、阶段耗时分解
6. **汇总行**：`L0=N | L1a=N | L1b=N | L2=N | 总文件=N | 总字符=N | 主类型=xxx | 缓存命中=N | 缺失=N | 限载跳过=N`

**日志级别策略**：
- **默认（WARNING）**：仅输出错误、80%预算预警、无匹配警告、加载完成汇总
- **-v/verbose（DEBUG）**：输出上述全部详细性能日志到stderr
- **编程调用**：`SpecLoader(..., verbose=True)` 自动设置DEBUG级别；若外部已配置logging则自动传播不重复添加handler

#### 2.8 规范依赖声明与自动解析缺失

**问题**：当前L2文件列表是硬编码的（如code_review加载workflows/code-review.md + roles/reviewer.md），但规范文件之间可能存在隐式依赖：
- workflows/code-review.md 可能引用了 rules/ 下的评审规则
- skills/ 下的SKILL.md 可能依赖 commands/ 下的指令集

这些依赖没有显式声明，路由配置遗漏时会导致上下文缺失。

**建议**：
1. 在L2规范文件frontmatter中添加`depends_on`字段声明前置依赖
2. SpecLoader加载L2时递归解析依赖，自动补全缺失的前置规范
3. audit命令检查依赖链完整性，检测循环依赖

#### 2.9 max_chars限载策略过于粗暴 ✅ 已完成

**问题（已修复）**：优化前max_chars达到上限时直接break，可能截断正在加载的L2文件（如SKILL.md只加载了一半），导致Agent收到不完整上下文。

**已实施**：

1. **文件级原子性**：max_chars按文件粒度检查——加载前用`os.stat().st_size`预估文件大小，加载后会超限则整个文件跳过（SKIP），不截断内容
2. **优先级排序**：L2文件按目录优先级排序（commands/ > skills/ > workflows/ > roles/ > rules/），高优先级指令集/Skill优先加载
3. **80%预警**：加载进度达到80%预算时输出WARNING日志，提示"上下文预算即将用尽"
4. **逐文件决策日志**：verbose模式下每个L2文件输出完整决策链——预算检查→预估大小→超限判定→SKIP/加载→实际字符数→预估偏差
5. **统计汇总**：限载跳过文件数在最终汇总行`限载跳过=N`中体现

#### 2.10 与Agent启动协议的自动集成缺失

**问题**：当前SpecLoader是独立CLI工具，Agent启动时不会自动调用。AGENTS.md的启动协议（步骤1-3.5）需要Agent手动执行，容易遗漏。

**建议**：
1. 创建`.agents/hooks/session-start.py`启动钩子，Agent会话启动时自动调用SpecLoader加载L0+L1
2. 在ONBOARDING.md中明确"第一步调用spec-loader.py startup"
3. 将加载器集成到ci-check中，作为CI门禁的一环验证路由完整性

---

## 3. 优化路线图

### 第一阶段（立即修复）
- [x] 2.2 为3个缺失Skill门面的命令集补充路由覆盖（已完成：新增`first_principles`路由，`file_creation`/`adversarial_review`补充`rules/ai-coding-guidelines.md`）
- [x] 2.4 无匹配任务加载通用兜底规则集（已完成：无匹配时加载`rules/ai-coding-guidelines.md`，兜底场景从21KB降至~12.5KB）
- [x] 2.9 max_chars改为文件级原子性（已完成：按优先级排序加载，80%预算预警，超预算跳过低优先级文件而非截断）

### 第二阶段（近期优化）
- [x] 2.1 L1拆分L1a/L1b，将基线从21KB降至7KB（已完成：L1a=~5KB始终加载，L1b=~15KB按需加载，执行阶段基线~6.6KB）
- [ ] 2.3 多类型匹配主类型判定+角色互斥
- [x] 2.7 加载性能指标输出（已完成：verbose模式下路由匹配/L2解析/预算决策/批量效率全链路DEBUG日志）
- [ ] 2.10 Agent启动钩子自动加载L0+L1

### 第三阶段（中长期演进）
- [ ] 2.5 vendor三层嵌套路由集成
- [x] 2.6 基于mtime的磁盘缓存（已完成：.agents/.cache/spec-loader.json持久缓存，mtime失效，命中率统计）
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

**优化目标**（一期优化后实际数据）：
- ✅ 单任务平均上下文 < 18KB（execution阶段7种典型任务均值~17.6KB，相比优化前32KB降低45%）
- ✅ 无匹配兜底场景 ~12.5KB（已达成<15KB目标，相比优化前21KB降低40%）
- ✅ 路由覆盖率100%（20个任务类型覆盖全部10个commands指令集）
- ✅ audit零缺失文件（`✅ 所有 41 个规范文件均存在`）

**待达成的二期目标**：
- 多类型主类型判定+角色互斥（2.3）后，多类型场景从~19KB进一步降至~15KB
- vendor三层嵌套路由（2.5）支持flexloop等子模块
- 规范依赖自动解析（2.8）消除硬编码依赖

---

## 5. 相关文件索引

| 文件 | 职责 |
|------|------|
| [spec_loader.py](../../../scripts/lib/spec_loader.py) | L2加载器核心库（SpecLoader类、TASK_ROUTING、四层加载、磁盘缓存、日志） |
| [spec-loader.py](../../../scripts/spec-loader.py) | CLI入口（task/layer/list-types/audit/cache-stats/cache-clear/warmup子命令） |
| [.agents/.cache/spec-loader.json](../../../.cache/spec-loader.json) | 磁盘缓存文件（mtime+字符数持久化，自动版本化失效） |
| [docgen.py](../../../scripts/docgen.py) | stats子命令自动统计核心指标 |
| [context-routing.md](../../../context-routing.md) | L1b上下文路由表（与TASK_ROUTING需保持同步） |
| [02-skills.md](../../../capability-registry/02-skills.md) | Skill注册索引（L1b能力注册中心分册） |
| [global-core-rules.md](../../../global-core-rules.md) | L1a全局核心规则（始终加载） |
| [capability-boundaries.md](../../../capability-boundaries.md) | L1a能力边界声明（始终加载） |
| [ONBOARDING.md](../../../ONBOARDING.md) | L0入口速查（始终加载） |
