# 对抗审查报告（V 阶段）

> 审查对象：`projects/awesome-okf-xs/doc/bundles/sheke/industry/douyin-compute-ai-ecommerce/`（9 文件）
> 审查时点：2026-10-31 ｜ 审查视角：事实溯源 / 结构规范 / 读者可用性 / 时效边界
> 结论：**通过（判定 `status: flagged`）**。四视角未发现阻断性缺陷；已修复门禁拦截项 3 处（计数漂移），遗留项均以「已知边界」显式披露；源文 1 项确定数据错误已勘误（禁止静默照搬）。

## 一、四视角对抗审查

### 视角 1 · 事实溯源（魔鬼代言人：凭什么信这些数字？）

| 攻击点 | 结论 | 处置 |
|---|---|---|
| 廊坊「40 个数据中心」是否可信？ | ❌ **确定数据错误**：官方一致口径为 **36 个**（廊坊市政府、河北日报、新华网、河北省政府网、人民日报） | 记 E1；正文与速查表以 **36 个** 呈现并标注「源文作 40 个」；核验报告单列勘误，**不静默照搬** |
| 廊坊—北京时延 2—3 毫秒来源是否可考？ | ⚠️ 数字有《廊坊日报》2026-06-15、人民网河北支持，但源文标注「廊坊市政府网站」同期另作「1 毫秒」 | 记 E2；数字保留、来源标注不采信为唯一锚点，并列记录多口径 |
| 十强服务商「7 家」是否有独立源？ | ⚠️ 河北省人民政府网 2026-01 作 **6 家** | 记 E3；6 家/7 家两说并列，记录时点差异，不裁决 |
| 双 11 增幅 94% 可跨口径引用吗？ | ⚠️ 94% 为「首日」口径且单源；「开门红」口径（10/15–18）多源一致为 **78%** | 记 E4；双口径并列（首日 94% 单源 / 开门红 78% 多源），提示统计窗口差异 |
| Anew Labs 中文名唯一吗？ | ⚠️ 源文作「新生探途」，另译「新生实验室」 | 记 E5；两说并列，均指同一实体，不裁决 |
| 公司注册/投资额是否可复核？ | ✅ 天眼查/企查查转引、环评公示、官方业绩公告多处印证（C1~C4、C8~C14、C16~C19） | 保留，标注转述层级与核验编号 |
| 作者分析是否被当作事实？ | 已隔离 | F-002、F-026、F-031~F-036 标 `author_claim`；速查表依据列注明「作者观点」 |

**判定**：事实分层清晰（page_fact 28 / author_claim 8），客观事实与作者观点分离；不可核验项全部显式披露，未虚构博文外数据。**通过**。

### 视角 2 · 结构规范（新人：符合 OKF v0.2 与仓库约定吗？）

| 攻击点 | 结论 | 处置 |
|---|---|---|
| bundle 落位是否正确？ | `sheke/industry/`（AI 行业与商业趋势），符合「单篇博文不新建分组」 | 通过 |
| 骨架是否合规？ | `index.md + log.md + concepts/(3+index) + references/(2+index)`，无 `examples/`（两问皆否） | 通过 |
| toctree 是否齐备？ | 每级 `index.md` 均含隐藏 `{toctree}`（`:hidden:` + `:maxdepth:`）；根索引引用 concepts/index、references/index、log | `check-toctrees.py` 通过 |
| `okf_version` 是否越级？ | 仅出现于 bundle 根 `index.md` | 通过 |
| 计数面是否一致？ | 首跑 `check-bundles-index.py` 报 3 处漂移（frontmatter 694 vs 695、sheke 节标题 85 vs 86、分组表之和 85 vs 86） | **已修复**：`total_bundles` 694→695、sheke 域节标题 85→86、分组表 industry 36→37；复跑五面一致 |
| 三处规模数字是否对账？ | `doc/bundles/index.md`（695）· `doc/index.md`（695）· `README.md`（695） | `check-asset-baseline.py` 通过 |

**判定**：结构合规，门禁全绿。**通过**。

### 视角 3 · 读者可用性（老板：读者能直接用吗？）

| 攻击点 | 结论 | 处置 |
|---|---|---|
| 有无明确阅读路径？ | 有「阅读路径」表（想了解→读） | 通过 |
| 核心结论是否一眼可得？ | 有「核心结论速查」表（8 行，含核验列） | 通过 |
| 与其他知识包的关联是否建立？ | 有「主题关联」表（doubao-douyin-livestream-ecommerce / volcengine-ecosystem / qianwen-go-my-apps / big-tech-pontzi-track-selection 等 6 个），相对路径 | 通过 |
| 使用边界是否交代？ | 「已知边界」+ 核验报告「可用边界」（可用于理解算力基建布局与 AI 电商落地路径，不可用于引用数据中心数量/十强家数/双 11 单一口径或断言新设公司业务定位） | 通过 |

**判定**：可用性与边界披露充分。**通过**。

### 视角 4 · 时效边界（未来：多久会过期？）

| 攻击点 | 结论 | 处置 |
|---|---|---|
| 资讯时效是否设限？ | ✅ `stale_after: 2026-12-31` | 通过 |
| 发布日是否明确？ | 博文有明确日期 2026-10-30，按页面实测登记（F-001） | 通过 |
| 复核条件是否明确？ | 4 条复核触发：①官方就新设公司业务定位发布说明 ②廊坊数据中心/算力官方口径更新 ③双 11 完整经营数据公开 ④2026-12-31 前例行复核 | 通过 |
| 双 11 经营数据是否被当作定论？ | 未当定论——标为平台口径、部分单源（G5），提示统计窗口不一、不可跨口径比较 | 通过 |

**判定**：时效管理与复核闭环完备。**通过**。

## 二、双份 F 编号一致性比对（机械比对）

| 面 | 文件 | 编号范围 | 条数 | 结论 |
|---|---|---|---|---|
| spec 侧 | `facts.md` | F-001~F-036 | 36 | 连续无跳号 |
| bundle 侧 | `references/article-source.md` | F-001~F-036 | 36 | 连续无跳号 |

**集合一致，无跳号、无重号。通过。**

## 三、质量门执行结果

`invoke gates.*` 依赖不可用，按等价命令在 `projects/awesome-okf-xs/` 下直接执行底层脚本：

| 门禁 | 命令 | 结果 |
|---|---|---|
| UTF-8 | `python scripts/check-utf8.py` | ✅ 12620 个文件均为有效 UTF-8 |
| toctree | `python scripts/check-toctrees.py` | ✅ 全部引用有效，所有内容文档均可达 |
| 总索引对账 | `python scripts/check-bundles-index.py` | ✅ 9 域 / 64 组 / 695 束，五面一致（修复后） |
| 资产基线口径 | `python scripts/check-asset-baseline.py` | ✅ 校验通过（total_bundles 单一真相源 695，三处一致） |
| Python 红线 | `pytest tests/unit/test_no_future_annotations.py -q` | ✅ 11 passed |

## 四、Checklist

### 归属与结构
- [x] bundle 位于 `sheke/industry/douyin-compute-ai-ecommerce/`
- [x] 结构：index.md + concepts/（3 篇 + index）+ references/（2 篇 + index）+ log.md，无 examples/（商业分析/战略资讯性质）
- [x] frontmatter 完整，sources 指向博文 URL 并注明公众号/作者
- [x] 明确标注「商业分析/战略资讯，非源码教程」

### 内容质量
- [x] F-001~F-036 登记于 `references/article-source.md`，文档引用 F 编号
- [x] 区分客观事实与作者观点（F-002、F-026、F-031~F-036 标 `author_claim`）
- [x] 源文确定数据错误（廊坊数据中心 40）按官方口径 36 呈现并标注源文口径（E1）
- [x] 3 篇 concepts 覆盖：新设公司与时间线 / 算力基建与投资 / AI 电商落地与转化
- [x] 不编造博文外数据

### 信任与时效
- [x] 已知边界声明：G1~G6（业务定位未披露、口径不全、可复核性缺口、AI 渗透无量化、经营数据部分单源、多为转引）
- [x] 关键声明经 WebSearch 核验（C1~C19：15 通过 / 3 部分通过 / 1 未通过）
- [x] `stale_after: 2026-12-31`（资讯类设较短周期）

### 索引与链接
- [x] `sheke/industry/index.md` 束数 36→37，导航表加行 + toctree 追加 + description 同步
- [x] `sheke/index.md` 方向描述 36→37、社科域方向计数同步
- [x] `bundles/index.md` total 694→695、sheke 85→86、industry 36→37（五面一致）
- [x] `doc/index.md` 与 `README.md` 三处规模数字对账一致（694→695）
- [x] `gates.utf8` / `gates.toctrees` / `gates.bundles` / `gates.assetbaseline` / Python 红线通过

### 收尾
- [x] 未修改 `vendor/`、`projects/awesome-okf-xs` 以外的其他 bundle
- [x] `tasks.md` Task 1~5 勾选（C 阶段待用户明确提交请求）
- [x] `log.md` 门禁执行记录已回填实测结果

## 五、遗留与后续

- **遗留（非缺陷，已显式披露）**：3 项部分通过（C5/C7/C15）、G1~G6 缺口——按 blog-article-to-okf-wiki 规范以 `status: flagged` + stale_after 管理，不阻断交付。
- **后续（C 阶段，待授权）**：按双层顺序提交——① 子模块 `projects/awesome-okf-xs`（bundle 9 文件 + 父级索引 3 文件 + `README.md` + `doc/index.md`）；② 主仓库 spec（`spec.md` + `facts.md` + `tasks.md` + `review.md`）；③ 主仓库子模块指针。均用 `git-commit-utf8.py` 显式文件列表落地，不 push。
