---
title: "「如何找到真需求」全面调研 → OKF Wiki 教程"
status: "draft"
version: "1.0"
methodology: "seven-concepts（场景4 知识沉淀：R→I→E，叠加 F 本质剖析 + V 对抗审查）"
content-sensitivity: "public"
---

# 「如何找到真需求」全面调研 → OKF Wiki 教程 Spec

## Why

"真需求 vs 伪需求"是产品、创业与营销的第一性问题：大量失败源于为伪需求造产品。本任务用七概念方法论对"如何找到真需求"做全面调研与分析，跨越西方经典（客户开发 / JTBD / 精益创业 / 设计思维 / Kano / Mom Test）与中文谱系（梁宁《真需求》、痛点-爽点-痒点、俞军产品方法论、国内正反案例），沉淀为 awesome-okf-xs 文档库中的系统化 OKF Wiki 教程，与 marketing 分组现有「营销通识」（marketing-fundamentals）和「先卖后做·需求验证」（sell-before-build-validation）构成"发现 → 验证"闭环。

## 内容敏感度预检（阶段 0）

- 调研对象：公开出版书籍、公开方法论原典、公开商业案例、公开访谈/演讲 → **公开内容（Public）**
- 标准工作流：spec 位于 `.trae/specs/okf-wiki-ecosystem/`，产出物位于 `projects/awesome-okf-xs/doc/bundles/`

## 信源距离预判

- 多源综合调研（非单篇转化）：经典著作/方法论提出者原文为一级信源；百科与二手解读仅作线索，关键声明回到一级信源
- 自媒体/厂商宣称的成效数字一律列 P0 必核验；核验不过降级为"来源宣称"标注或剔除
- 梁宁《真需求》（2024）为版权书籍：只提炼公开访谈/书介中的方法论框架与自有表述，**不逐字转录**正文，遵守摘要替代转录纪律

## 骨架判定（操作可复现性两问）

| 判据 | 结论 |
|------|------|
| ① 是否有读者可照做的流程？ | 有——用户访谈脚本（Mom Test 原则）、JTBD 切换访谈、MVP/假门测试、一周验证计划、需求判别自查清单均可直接复现 |
| ② 是否有步骤顺序/输入输出？ | 有——各方法论均有公开的标准步骤与产出物模板 |

两问均为"是" → 设 **examples/**（实操层）。骨架：index + concepts/（8 篇）+ examples/（4 篇）+ references/（2 篇）+ facts.md + insights.md + log.md。

## 归属判定

**结论：`sheke/marketing/real-needs-discovery/`**

| 候选位置 | 判定 | 理由 |
|---------|------|------|
| `sheke/marketing/`（选定） | ✅ | 科特勒营销体系以"需要/欲望/需求"为第一概念；同组 sell-before-build-validation 是"需求验证"半环，本束是"需求发现 + 真伪判别"半环，构成发现→验证闭环；marketing-fundamentals 为通识，本束为"需求"基石概念深潜，互补不重复 |
| `zhexue/methodology/` | ❌ | 该组收域通用思维模型与学习方法论（第一性原理/费曼学习法）；需求发现是商业域专用方法论，目标读者（创业者/产品/营销）会到社科营销分区查找 |
| `sheke/workplace/` | ❌ | 职场管理分组主题是组织与岗位技能，非客户需求 |
| 新建分组 | ❌ | 单束新建分组属过度工程 |

## What Changes

- 新增 spec：`.trae/specs/okf-wiki-ecosystem/real-needs-discovery-okf-wiki/`（spec.md + tasks.md + 调研中间产物 facts-west.md / facts-cn.md）
- 新增 OKF bundle：`projects/awesome-okf-xs/doc/bundles/sheke/marketing/real-needs-discovery/`（约 19 文件）
- 更新 `sheke/marketing/index.md`：total_bundles 2→3、导航表加行、toctree 追加、description 同步
- 更新 `sheke/index.md`：marketing 行束数 2→3、域 description 同步
- 更新 `bundles/index.md`：total_bundles 575→576、mermaid sheke 46→47、社科域节 46→47、marketing 行 2→3
- **BREAKING**：无破坏性变更（纯新增）

## Impact

- Affected specs：无（独立新增）
- Affected code：`projects/awesome-okf-xs/doc/bundles/` 下新增 1 束 + 三级索引 4 处修改（awesome-okf-xs 为第一方 git submodule，在子模块内开发与提交）

## ADDED Requirements

### Requirement: 概念文档层（concepts/，8 篇）

| 内容层 | 映射篇目 |
|--------|---------|
| 定义层：需要/欲望/需求三分、真需求判别标准、痛点/爽点/痒点 | `00-what-is-real-need.md` |
| 反向层：伪需求类型图谱与认知陷阱（解决方案迷恋、幸存者偏差、补贴幻觉等） | `01-fake-need-taxonomy.md` |
| 全景层：需求发现四路径（问/看/算/试）与方法选型 | `02-discovery-method-map.md` |
| 访谈层：Mom Test 原则、访谈脚本与禁忌 | `03-interview-playbook.md` |
| 框架层：JTBD（雇用产品、switch 访谈、四力模型） | `04-jtbd-framework.md` |
| 验证层：精益创业闭环、MVP 谱系（视频/假门/ concierge/预售） | `05-validation-loop.md` |
| 优先级层：Kano 模型、RICE 等排序工具 | `06-need-prioritization.md` |
| 案例与边界层：正反案例（Dropbox/Airbnb/拼多多 vs Google Glass/Juicero/Quibi/O2O 补贴）与方法适用边界 | `07-cases-and-boundaries.md` |

### Requirement: 实操层（examples/，4 篇）

- `01-interview-script-workshop.md`：用户访谈脚本工作坊（含好/坏问题对照表）
- `02-jtbd-switch-interview.md`：JTBD 切换访谈实操（时间线追问模板）
- `03-one-week-validation-plan.md`：一周需求验证计划（与 sell-before-build 一周法呼应但聚焦发现侧）
- `04-need-self-check-list.md`：真需求判别自查清单（可直接打印使用）

### Requirement: 信源层（references/，2 篇）

- `01-classics-and-authorities.md`：经典书目与权威来源谱系（提出者/年份/核心命题）
- `02-source-verification.md`：调研信源登记 + P0 核验逐项结论（✅/⚠️/❌）

### Requirement: 研究产物（bundle 根）

- `facts.md`：F 编号事实登记簿（合并 facts-west/facts-cn，去重，标注信源与可信度）
- `insights.md`：四元组洞察（事实→洞察→证据→可迁移边界），≥6 条
- `log.md`：更新历史（YYYY-MM-DD 倒序）
- `index.md`：bundle 根索引（frontmatter 含 `okf_version: "0.2"`，toctree 覆盖全部内容文档）

### Requirement: 状态与时效

- `status: stable`——核心方法论均为跨周期经典框架，多源互证
- `stale_after: 2027-10-01`——方法论骨架跨周期有效；案例细节与平台事实标注时点

## 约束

- 所有具体声明引用 F 编号或 sources 脚注；版权书籍内容以"框架提炼 + 自有表述"呈现，禁止逐字转录
- 核验发现的流行误传（如"Dropbox 视频零代码获客百万"类夸张口径）正文呈现核验后正确值并标注流行口径，不静默照搬
- 交叉引用使用相对路径，禁止 `file:///`；正文中文，文件名 kebab-case 纯英文
- 不替任何方法论宣称普适有效性；每个方法标注适用边界与失效条件
- 遵循 awesome-okf-xs AGENTS.md：新增 bundle 后必跑 `invoke gates.toctrees` 与 `invoke gates.bundles`（计数五面对账），构建验证 `invoke build`

## Acceptance Criteria

### AC-1: bundle 结构与 toctree 完整
- **Given**: bundle 已落盘 `sheke/marketing/real-needs-discovery/`
- **When**: 运行 `invoke gates.toctrees`
- **Then**: 全部内容文档被 toctree 覆盖，无断链告警
- **Verification**: `programmatic`

### AC-2: frontmatter 合规与计数对账
- **Given**: bundle 与三级索引已更新
- **When**: 运行 `invoke gates.bundles`
- **Then**: 每个非保留 .md 含可解析 frontmatter 且有非空 `type`；bundles 总计数 575→576 五面对账一致
- **Verification**: `programmatic`

### AC-3: Sphinx 构建通过
- **Given**: bundle 落盘完成
- **When**: 运行 `invoke build`
- **Then**: 构建成功且无本束引入的 ERROR
- **Verification**: `programmatic`

### AC-4: 方法论覆盖度
- **Given**: 读者通读 concepts/
- **When**: 检查覆盖清单
- **Then**: 覆盖 ≥6 个方法论体系（客户开发/JTBD/精益创业/设计思维/Kano/Mom Test/梁宁真需求框架中至少 6 个）与 ≥4 个正反案例，每法标注适用边界
- **Verification**: `human-judgment`

### AC-5: 事实溯源
- **Given**: 读者抽查具体声明
- **When**: 核对数字、年份、引语类声明
- **Then**: 均带 F 编号或 sources 脚注，可在 facts.md/references 查到信源；P0 核验结论已登记
- **Verification**: `human-judgment`

### AC-6: 可操作性
- **Given**: 读者带着真实产品想法
- **When**: 使用 examples/ 四篇
- **Then**: 可直接照做访谈脚本、JTBD 访谈、一周验证计划与自查清单，无需额外补全步骤
- **Verification**: `human-judgment`

### AC-7: 三级索引计数一致
- **Given**: 索引更新完成
- **When**: 核对 bundles/index.md、sheke/index.md、sheke/marketing/index.md
- **Then**: 计数一致（576 / sheke 47 / marketing 3），导航表含新束条目
- **Verification**: `programmatic`

### AC-8: 命名与语言规范
- **Given**: bundle 落盘完成
- **When**: 检查文件名与正文
- **Then**: 文件名 kebab-case 纯英文，正文中文，保留文件名（index/log）用途正确
- **Verification**: `programmatic`

## Open Questions

- [ ] concepts 是否拆出独立"设计思维共情"篇？（倾向：并入 02 方法全景与 03 访谈，避免膨胀）
- [ ] 是否纳入 AI 时代需求发现（合成用户/AI 访谈）？（倾向：在 07 边界篇设小节，标注证据薄弱）

<!-- changelog -->
<!--
- 2026-10-01 | initial | 七概念（R→I→E→V）全面调研「如何找到真需求」→ OKF Wiki 教程
-->
