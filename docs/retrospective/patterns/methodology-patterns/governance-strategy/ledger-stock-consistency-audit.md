---
type: Pattern
id: "ledger-stock-consistency-audit"
source: "retro-20260901-trae-env（Trae 技能台账审计：managedSkills vs 磁盘 skills）+ OKF bundles 索引漏登事件（2026-08-31）"
x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/governance-strategy/ledger-stock-consistency-audit.toml"
maturity: "L2"
validation_count: 2
reuse_count: 1
related_patterns:
  - "dual-env-drift-reconciliation"
  - "data-validation-four-checks"
  - "automated-stats-three-defense-lines"
tags: ["ledger", "inventory-audit", "shadow-assets", "governance", "consistency"]
---
# 台账存量审计：注册清单与磁盘存量的一致性审计法

## 模式类型

治理策略/资产治理模式（注册-存量双轨体系的一致性审计，属治理流程类）

## 成熟度

L2-validated（2 次验证：①Trae 技能台账审计 2026-09-01；②OKF bundles 索引漏登事件 2026-08-31）；已在 ①中复用 1 次（skill-ledger-audit 执行）

## 触发场景

- 当存在「管理台账（注册表/清单文件/索引）+ 磁盘实际存量」双轨的资产体系（技能/插件/依赖/知识包/容器镜像），且资产可经非官方途径落盘时，使用这个模式
- 适用于：台账由客户端/流程部分维护、存在手动放置资产的通道、台账覆盖率长期未审计的体系
- 不适用于：①台账即唯一事实来源且存量完全由台账派生（无漂移通道）；②一次性临时清单（审计成本大于收益）

## 核心做法

1. **双清单导出**：分别导出「台账清单」（如 managedSkills、index.md 登记表）与「磁盘清单」（实际目录扫描），口径对齐（同名归一化）
2. **双向求差集**：台账有而磁盘无 = 幽灵登记；磁盘有而台账无 = 影子资产；计算失配率（影子数/磁盘总数）作为健康度指标
3. **来源追溯**：对每个影子资产追溯落盘途径（官方市场/手动复制/内置分发/早期批次），分类登记而非一刀切
4. **处置决策**：在用资产保留（补登记或接受现状）；确认废弃的清除；**不手动篡改客户端维护的台账文件**（格式/版本风险），通过正规通道补登记
5. **准入约束**：建立「新增资产必须入台账」规则，并对账固化为周期任务

## 反模式（不要这么做）

- ❌ **只信台账不看磁盘**：案例①国际版台账 3 项 vs 磁盘 55 个，94.5% 影子技能脱离管理（升级/清理/禁用操作全部覆盖不到）
- ❌ **只信磁盘/正文不看台账计数**：案例②索引 frontmatter 记 61 组、正文记 63 组、磁盘实存又不同——三方数字互相矛盾，任何一方都不得手填采信，一律以门控重算为准
- ❌ **发现影子资产不追溯来源直接删除**：可能误删正在使用的手动资产（案例①中 17 个国内版影子技能含 load-specweave 等关键装载器）
- ❌ **手动写入客户端维护的台账文件补登记**：绕过客户端的格式/版本校验，可能破坏台账结构

## 检验标准

做完之后怎么知道做对了？

- 标准1：双向差集完整（幽灵登记与影子资产两个方向都查了，不只查单向）
- 标准2：每个影子资产有来源分类与处置结论，无悬置项
- 标准3：失配率已量化（可跨周期对比趋势）
- 标准4：计数类结论以自动化门控重算为准，未手填采信任何一方的既有数字

## 迁移示例

这个模式还能用在什么其他场景？

- 场景1（已验证，知识管理领域）：OKF bundles 索引（台账）与束目录（存量）的对账——门控脚本 check-bundles-index.py 即此模式的工具化形态
- 场景2（非当前领域）：npm 全局包——`npm ls -g` 台账与 node_modules 实际目录、pip list 与 site-packages、conda env 清单与实际环境
- 场景3（跨领域）：图书馆藏书目录与架上实物、企业资产台账与实物盘点——同样是「登记-实存」双轨审计

## 案例记录

| 案例 | 日期 | 台账/存量 | 关键发现 |
|---|---|---|---|
| Trae 技能台账审计 | 2026-09-01 | managedSkills / skills 目录 | 国际版失配率 94.5%（52/55）、国内版 20.7%（17/82）；影子技能来源四分类后全部保留，无误删 |
| OKF bundles 索引漏登 | 2026-08-31 | index.md 登记表 / bundles 目录 | 台账漏登 think/math、suanxue、relationships 3 束；frontmatter(61) 与正文(63) 自相矛盾；以门控重算收敛 |
