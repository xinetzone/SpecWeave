---
status: "in_progress"
version: 1.1
source: "https://vibeknow.com"
session: "sc-20261021-vibeknow-research"
---
# VibeKnow 视频专家全面调研复盘 - Implementation Plan

> 链路：R（事实采集）→ I（洞察）→ E（萃取）→ V（对抗审查）→ C（原子提交）
> 质量门：G1 事实门 → G2 洞察门 → G3 模式门 → G4 交付门；V 门强制不可跳过

## Task 1: R 阶段事实采集
- **Status**: `completed`
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 五维度并行采集：产品功能全景 / 技术架构与 CLI / 商业化与竞品 / 口碑与风险 / 官方口径基线
  - 每条事实输出统一格式：`F-xxx | 事实陈述 | 来源URL | 访问日期`
  - 采集契约：禁因果词、禁评价、关键数据（数字/URL/命令/版本）完整、附证据缺口
- **Acceptance Criteria Addressed**: AC-1, AC-3
- **Test Requirements**:
  - `rule` TR-1.1: 五维度均有覆盖，任一维度不得为 0 条事实
  - `rule` TR-1.2: 每条原始事实带来源 URL，URL 可解析
- **Notes**: 采用 4 路后台子代理并行采集，主上下文只做编排与整合。实际落盘 106 条事实（PRO-01~25 / TEC-01~31 / COM-01~25 / RP-01~25），分 4 份附录文件；官方口径基线并入 COM/RP 两段，未单列第五维度

## Task 2: G1 质量门——事实合并、去重与降因果化
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 合并去重为统一编号事实清单（建议按 PRO / TEC / COM / RP 四个前缀分段编号）
  - 剥离因果词与评价词，保留原始数值、命令、版本、URL
  - 编制「数据冲突登记表」（同指标多值并陈，不裁决）与「未获取项清单 G-xxx」
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3
- **Test Requirements**:
  - `rule` TR-2.1: 事实条数 ≥20，逐条含来源 URL 与访问日期
  - `rule` TR-2.2: 因果/评价词命中数为 0（引述原文除外并标注）
  - `rule` TR-2.3: 冲突登记与缺口清单各自独立成表
- **Notes**: G1 不通过不得进入 I 阶段。已通过：106 条事实（远超 ≥20 门槛）、逐条含来源 URL + 访问日期 2026-10-21；因果词全文扫描命中 8 处，逐条甄别后确认均为缺口表描述与分析性论证（I 阶段文本），事实陈述本身无因果词违规；冲突登记 8 项（C-1~C-8）、缺口登记 24 项（E-1~E-13 商业化 + G-1~G-11 口碑）各自独立成表

## Task 3: I 阶段——四元组洞察
- **Status**: `completed`
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 产出 ≥3 条洞察，每条含「陈述 / 证据引用事实编号 / 反常识 / 可执行行动」
  - 维度互不重叠，覆盖产品定位、机制设计、证据强度三向
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `rule` TR-3.1: 洞察条数 ≥3，四要素逐条齐备
  - `rule` TR-3.2: 每条证据引用编号在事实清单中可查
  - `rubric` TR-3.3: 洞察维度覆盖度；scale 1-5；anchors 1=单维度堆叠、3=两维度、5=≥3 维度且互不重叠；threshold >= 4
- **Notes**: G2 不通过不得进入 E 阶段。已通过：4 条洞察（≥3 门槛），维度覆盖「产品差异化定位 / 商业机制设计 / Agent 工程契约 / 证据强度」四向互不重叠；每条含四要素齐备，证据编号均在 106 条事实清单中可查

## Task 4: E 阶段——模式萃取与入库
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 3
- **Description**:
  - 萃取 1 个可迁移模式，落 `docs/retrospective/patterns/methodology-patterns/governance-strategy/<id>.md`
  - 结构：frontmatter + 问题陈述 + 解决方案（含 Mermaid 流程）+ 适用/不适用场景 + ≥3 反模式 + 检验标准 + ≥1 跨域迁移 + 验证来源
  - 同步登记：`.meta/toml/.../<id>.toml` 伴生 TOML、`governance-strategy/index.md` toctree 条目、README 索引表刷新
- **Acceptance Criteria Addressed**: AC-5, AC-7
- **Test Requirements**:
  - `rule` TR-4.1: 模式文档含触发条件、核心步骤、≥3 反模式、检验标准、≥1 跨域迁移、成熟度标注 L1-draft
  - `rule` TR-4.2: 伴生 TOML 存在且字段与 frontmatter 一致；toctree 条目与实体文件一一对应
  - `rubric` TR-4.3: 模式结构完整度与迁移潜力；scale 1-5；anchors 1=仅一句话总结、3=含步骤与反模式但缺检验标准或迁移、5=五要素齐备；threshold >= 4
- **Notes**: 单案例必须标注 L1-draft，待非同谱系第二案例验证后升级。已通过：模式 `agent-cli-charge-authority-resume`「Agent 原生 CLI 扣费-授权-续跑三元契约」，L1-draft / validation_count=1 / reuse_count=0；含触发条件、6 步核心做法（配 Mermaid 流程图）、6 反模式、6 问检验标准、3 个跨域迁移、同层去重划界（与 `code-patterns/cli-as-api-design` 分工）。
  **层级偏离说明**：原定落 `governance-strategy/`，实际落 `tools-automation/`。理由：模式对象是 CLI 工具契约，同层已有 `dry-run-first` / `capability-precondition-pairing` / `tool-failure-three-tier-degradation` 等 CLI 工具域相邻模式，语义归属更贴切；且需与 `code-patterns/cli-as-api-design` 划界（后者已覆盖多格式输出 ⊕ 结构化错误 ⊕ 退出码约定 ⊕ 会话持久化，本模式增量聚焦扣费-授权分离 + 可续跑中间态 + 授权型开关禁入可共享配置）。该偏离在模式 frontmatter `maturity_note` 与报告第六章两处显式登记。伴生 TOML、toctree 条目、README 索引表三处登记均已完成。

## Task 5: V 阶段——四视角对抗审查与修正回归
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 四视角（魔鬼代言人 / 新人 / 老板 / 未来）各出 ≥1 条意见，总计 ≥5 条具体意见
  - 记录「意见 / 性质 / 处置 / 回写位置」，采纳项 ≥2 条并落到报告或模式文档
  - 失败项回写后重跑相关质量门（回归验证）
- **Acceptance Criteria Addressed**: AC-6, AC-9
- **Test Requirements**:
  - `rule` TR-5.1: 意见条数 ≥5 且可定位到具体报告章节
  - `rule` TR-5.2: 采纳并回写的意见 ≥2 条，含回写位置引用
  - `rubric` TR-5.3: 审查覆盖度与修正闭环；scale 1-5；anchors 1=形式化表态、3=四视角齐备但意见笼统、5=≥5 条具体可复现意见且 ≥2 条回写闭环；threshold >= 4
- **Notes**: V 门强制；F 后必 V（本链路不含 F，但知识沉淀场景 V 仍为强制门）。已通过：4 视角共 10 条具体意见（魔鬼代言人 3 / 新人 2 / 老板 3 / 未来 2），采纳 9 条 + 部分采纳 1 条（评分参照系——不强行给出无同口径依据的竞品分数对照，改补 65 分构成说明与最弱环节定位），回写位置逐条记录于报告第十三章

## Task 6: 报告落盘与索引刷新
- **Status**: `completed`
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 落 `docs/retrospective/reports/competitive-analysis/retrospective-vibeknow-video-expert-20261021/`：README.md（主报告）+ index.md（toctree）+ facts-*.md（事实附录）
  - 主报告骨架对齐 openKylin-20261014：执行摘要 / 画像 / 方法 / 事实清单 / 洞察 / 萃取 / 详细评估 / 评分与风险 / 适用性 / 待验证 / 对抗审查记录 / 质量门记录 / 参考来源 / CMD-LOG
  - 跑 `python .agents/scripts/docgen.py theme-dashboards` 与 `update-spec-readme` 刷新看板
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `rule` TR-6.1: 报告目录位于根 `docs/` 下且含 index.md toctree，toctree 条目均可解析
  - `rule` TR-6.2: 主题看板与全局 spec 看板已登记本次 spec
  - `rule` TR-6.3: 内部交叉引用为相对路径，无 `file:///`，无 `.agents/docs/` 残留
- **Notes**: 落盘前执行「落盘前三查」。已落盘：主报告 README.md（14 章）+ index.md（toctree 含 README + 4 份 facts 附录）+ 4 份事实附录；上级 `competitive-analysis/index.md` toctree 与 `competitive-analysis/README.md`「最近归档」表已登记；模式层 `tools-automation/index.md` toctree + `tools-automation/README.md` 索引表已刷新。内部引用全部为相对路径，无 `file:///`、无 `.agents/docs/` 残留

## Task 7: 原子提交交付
- **Status**: `in_progress`
- **Priority**: medium
- **Depends On**: Task 6
- **Description**:
  - 路径级点名暂存本次产出物（禁止 `git add .`）
  - Conventional Commits 提交（`type(scope): 中文主体`），Windows 端 UTF-8 防乱码
  - 提交后 `git cat-file -p HEAD` 复验提交内容与信息
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `rule` TR-7.1: 单次提交仅含本次调研产出物，无无关文件
  - `rule` TR-7.2: 提交信息符合 Conventional Commits 且主体为中文
  - `rule` TR-7.3: `git show --stat HEAD` 显示的变更集合与产出物集合一致
- **Notes**: 默认不推送

# Task Dependencies

- Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7，严格串行
- G1–G4 为阶段硬门，未通过不得推进到下一阶段
- 需求变更须回到 spec.md 对齐，不在 tasks.md 内静默扩范围
