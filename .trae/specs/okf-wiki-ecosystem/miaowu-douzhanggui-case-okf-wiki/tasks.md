# Tasks

## Task 1: 内容敏感度预检与归属/骨架判定
- **Priority**: high
- **Status**: completed
- **Depends On**: None
- **Description**: 判定信源公开性；确定 bundle 归属位置（候选位置对照 + 同主题查重）；执行操作可复现性两问，决定是否设 `examples/`。
- **Test Requirements**:
  - **TR-1.1 (rule)**：公开性结论有 URL 参数与访问过程证据。
  - **TR-1.2 (rule)**：归属落到既有分组，不新建分组；查重覆盖同主题关键词。
  - **TR-1.3 (rule)**：两问皆否时不得创建空 `examples/`。
- **Completion Evidence**: 结论为公开内容（无访问控制参数、无登录墙）；归属 `jishu/ai/ecosystems/miaowu/miaowu-douzhanggui-case/`，检索 `miaowu|秒悟|Meoo|豆掌柜|拼豆` 无同主题束；两问皆「否」，未建 `examples/`。

## Task 2: R 阶段——事实采集与编号登记
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 1
- **Description**: 单通道采集正文；登记 S1–S5 信源台账；机械登记 F-001–F-060 编号事实，分层 `page_fact`/`author_claim`，标注 `verified`/`single-source`/`derived`。
- **Test Requirements**:
  - **TR-2.1 (rule)**：F 编号连续无跳号，双份登记（bundle source-ledger 与 spec facts）一致。
  - **TR-2.2 (rule)**：全部事实标注信源与状态；无来源推测不入表。
  - **TR-2.3 (rule)**：同库既有束不得充当对 S1 的独立第三方核验。
- **Completion Evidence**: `references/source-ledger.md` 登记 S1–S5 与 F-001–F-060；`facts.md` 镜像一致；§3 显式声明 S2–S4 不构成独立核验；识别 7 项放弃核验项。

## Task 3: I 阶段——洞察冻结与骨架落位
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 2
- **Description**: 冻结四元组洞察（现象/根因/影响/建议），完成 concepts 三/四层拆分；判断 `examples/` 取舍。
- **Test Requirements**:
  - **TR-3.1 (rule)**：每条洞察具备完整四元组。
  - **TR-3.2 (rule)**：concepts 与 facts 分层，事实不混入洞察。
- **Completion Evidence**: 冻结 5 条四元组洞察（观察式需求发现 / 工具层降摩擦≠业务闭环 / 免费试用关键在交换条件 / 成交含隐性维护成本 / 单源证明存在不证明可复制），落于 `concepts/03-deal-boundaries-and-insights.md`。

## Task 4: E 阶段——模式萃取与 bundle 落盘
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 3
- **Description**: 按 `references/ → concepts/ → index/log` 顺序生成原创教程；萃取可迁移模式；更新父级索引与计数。
- **Test Requirements**:
  - **TR-4.1 (rule)**：不复制全文镜像；具体声明均可回溯 F 编号。
  - **TR-4.2 (rule)**：每篇 concepts/references 有 frontmatter；`sources`/`status`/`stale_after` 完整。
  - **TR-4.3 (rule)**：三级 toctree 可达，索引计数与目录树一致。
- **Completion Evidence**: 生成 `index.md`+`log.md`+`concepts/`（index + 4 篇）+`references/`（index + 2 篇）；萃取模式 A「观察式需求发现法」与模式 B「免费试用换反馈的转化法」；更新 7 个索引文件的计数面。

## Task 5: V 阶段——P0 核验与对抗审查
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 4
- **Description**: 对身份、时间线自洽、数量与规模口径、平台能力声明、可外推性边界逐项核验；产出分项结论与汇总。
- **Test Requirements**:
  - **TR-5.1 (rule)**：每项核验有证据与状态（✅/⚠️/❌）。
  - **TR-5.2 (rule)**：汇总计数与分项编号自洽。
  - **TR-5.3 (rule)**：不可核验项显式标注单源边界，不伪造来源。
- **Completion Evidence**: `references/verification.md` 记录 19 项 P0 核验，汇总 **9✅ / 9⚠️ / 1❌**（❌ 为核验项 17「可复制到第二三家」）；据此在根索引设「阅读前必知的三件事」。

## Task 6: C 阶段——索引计数对账与质量门
- **Priority**: high
- **Status**: completed
- **Depends On**: Task 4, Task 5
- **Description**: 完成五面计数对账（frontmatter/计数行/域节标题/分组表/toctree）；运行 UTF-8、toctree、bundles 计数、资产基线、链接与 Python 红线门禁。
- **Test Requirements**:
  - **TR-6.1 (rule)**：`check-bundles-index.py` 五面一致通过。
  - **TR-6.2 (rule)**：`check-toctrees.py`、`check-utf8.py`、`check-asset-baseline.py` 通过。
  - **TR-6.3 (rule)**：新建束相对链接全部可解析（`check-links.py`）。
- **Completion Evidence**: `check-bundles-index.py` 通过（**9 域 / 63 组 / 693 束**）；`check-toctrees.py` 全部引用有效；`check-utf8.py` 12590 文件有效；`check-asset-baseline.py` 基线口径一致（HEAD 锚定、三处规模数字 693 一致）；`check-links.py` 41 个本地引用全部有效（收尾时修正 6 处 `concepts/` 下相对链接层级 `../`→`../../`）；`tests/unit/test_no_future_annotations.py` 11 passed。

## Task Dependencies
- `Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6`

## Parallelizable Work
- Task 5 的分项核验可按主题分组并行，共享同一证据与状态标注规则。
- Task 6 的四个机械门禁可并行运行，但计数对账须在 Task 4 索引更新完成后启动。

## Out of Scope
- Git 提交（子模块内部提交 + 主仓库 spec + 子模块指针更新）需用户显式授权，不在本 Spec 执行范围。
