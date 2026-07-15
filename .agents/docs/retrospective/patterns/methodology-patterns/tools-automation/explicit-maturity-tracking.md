---
id: "explicit-maturity-tracking"
source: "../../../reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/suggestions/meta-sug-03-pattern-maturity-tracking.md"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/tools-automation/explicit-maturity-tracking.toml"
---
# 成熟度显式追踪实践（Explicit Maturity Tracking）

## 模式类型
方法论模式

## 成熟度
L1 实验性（1 次成功案例：断链修复复盘萃取5个模式，全部显式标记成熟度）

## 适用场景
管理可复用知识资产（模式、洞察、方法论、最佳实践），追踪其从想法到标准化的演进过程。

## 问题背景

知识管理中最常见的问题是**过度自信**：把"刚萃取出来的洞察"当成"经过验证的最佳实践"，导致：
- L1想法被当作L3标准推广，在不适用场景中失效
- 团队不知道哪些可以放心复用，哪些需要先验证
- 知识演进过程不可见，无法判断知识的"信用分"
- 知识写出来就被当作"定论"，缺少持续验证和升级机制

## 核心实践：遵循全局统一的 L1-L4 分级

项目已有统一的成熟度分级标准（定义于 [patterns/README.md](../../README.md#模式成熟度评估标准)），本模式不重新定义级别，而是强调**必须显式标记、动态更新**：

| 等级 | 名称 | 量化条件 | 使用建议 |
|------|------|---------|---------|
| **L1** | 实验性 | `validation_count = 1` | 可参考，但使用时需保持警惕，建议先小范围验证 |
| **L2** | 已验证 | `validation_count ≥ 2` | 可以复用，但需注意适用场景边界 |
| **L3** | 可复用 | `reuse_count ≥ 1` 且 `validation_count ≥ 2` | 放心复用，可作为模板和检查清单基础 |
| **L4** | 标准化 | 已集成至 CI/工具链 | 强制执行的标准规范 |

## 显式追踪的四重价值

1. **避免过度自信**：不会把L1想法当成L3最佳实践，每一条知识都有"信用分"
2. **复用决策依据**：L3模式放心复用，L1模式需要先验证，降低试错成本
3. **知识演进可视化**：看到知识资产如何从L1→L2→L3→L4逐步成熟，形成正反馈
4. **信用积累机制**：每个模式的`validation_count`（验证次数）和`reuse_count`（复用次数）就是它的信用分

## Frontmatter 标准字段

每个模式/洞察文件必须在TOML frontmatter中包含以下字段：

```toml
maturity = "L1"           # L1/L2/L3/L4
validation_count = 1      # 验证次数（实战中证明有效的次数）
reuse_count = 0           # 复用次数（被其他任务/场景引用的次数）
source = "..."            # 首次萃取来源
documentation_level = "basic|standard|comprehensive"
```

### 升级规则

- **L1→L2**：在第2个真实场景中验证成功，`validation_count` 更新为 ≥2
- **L2→L3**：被其他任务（非原作者/非原场景）复用成功，`reuse_count` ≥1
- **L3→L4**：已集成至CI/工具链，有自动化验证保障
- 如果L2+模式在新场景中失效，需补充反例和适用边界，但不一定降级（除非发现根本缺陷）

## 成熟度更新表

每次复盘后更新受影响模式的成熟度，格式示例：

| 模式 ID | 成熟度变化 | 验证/复用次数 | 触发事件 |
|---------|-----------|-------------|---------|
| dry-run-first | L3 → L4 | — | 集成至CI检查门禁 |
| three-part-retrospective | L2 → L3 | reuse +1 | 被Mermaid渲染修复复盘复用 |
| relative-depth-adjustment | L1 → L2 | validation +1 | 首次实战验证成功 |

## 与其他成熟度模型的关系

| 模型 | 适用对象 | 级别数 | 关注点 |
|------|---------|--------|--------|
| **全局标准**（patterns/README.md） | **所有可复用资产** | 4级（L1-L4） | 统一的分级定义和量化条件，本模式遵循此标准 |
| `methodology-five-level-maturity.md` | **组织/团队整体方法论** | 5级（L1-L5） | 组织级复盘-洞察-萃取体系的成熟度（CMMI风格） |
| `toolchain-maturity.md` | **工具链治理能力** | 5级（L1-L5） | 工具从手动到CI门禁的演进阶段 |

三个模型视角不同，不冲突：本模式描述的是**个体资产层面**如何显式追踪和更新成熟度，遵循全局L1-L4标准；组织级和工具链级模型是宏观评估框架。

## 检查清单

- [ ] 每个模式/洞察文件是否都有`maturity`字段？
- [ ] maturity标记是否与实际`validation_count`/`reuse_count`一致？
- [ ] 新增模式是否默认标记为L1？
- [ ] 模式验证成功后是否及时更新`validation_count`和`maturity`？
- [ ] 被其他任务复用后是否更新`reuse_count`并升级至L3？
- [ ] 集成至工具链后是否升级至L4？

## 反例警示

| 问题 | 后果 |
|------|------|
| 不标记成熟度 | 使用者不知道可信度，L1想法被误用 |
| 所有模式默认L3 | 过度自信，在不适用场景中失效 |
| 成熟度只升不降（即使发现根本缺陷） | 失效模式继续误导使用者 |
| 不记录validation_count | 无法客观判断成熟度，凭感觉升级 |
| 定义与全局标准不一致的分级体系 | 造成混淆，跨模式比较困难 |

## 与现有模式的关系

- `methodology-five-level-maturity.md`：组织级五级成熟度评估框架
- `toolchain-maturity.md`：工具链五级成熟度模型
- `insight-library-evolution.md`：洞察库演进模型，本模式提供成熟度标记标准
- `three-tier-knowledge-sedimentation.md`：三层知识沉淀，不同层级知识可对应不同成熟度要求
- `auto-generate-threshold.md`：自动化阈值判断（30%），与本模式共同支撑模式库的批量管理
