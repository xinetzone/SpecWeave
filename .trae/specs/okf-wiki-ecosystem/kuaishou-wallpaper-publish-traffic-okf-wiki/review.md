# 对抗审查报告（V 阶段）

> 审查对象：`projects/awesome-okf-xs/doc/bundles/sheke/industry/kuaishou-wallpaper-publish-traffic/`（16 文件）
> 审查时点：2026-11-01 ｜ 审查视角：事实溯源 / 结构规范 / 读者可用性 / 时效边界
> 结论：**通过（判定 `status: flagged`）**。四视角未发现阻断性缺陷；已修复门禁拦截项 3 处（计数漂移）；唯一确定未通过项（图片数量三口径冲突 C6）与全部缺口均以「已知边界」显式披露，未静默照搬。

## 一、四视角对抗审查

### 视角 1 · 事实溯源（魔鬼代言人：信源只是一段视频的机器转写，凭什么信？）

| 攻击点 | 结论 | 处置 |
|---|---|---|
| 信源是原始文本还是二手转写？ | ❌ **信源为本地离线 ASR 转写，非原始文本**——页面正文无知识性文字（`js_content` 仅约 3588 字符），唯一内容为 242.67 秒视频；且首轮转写被截断（止于 137.547 秒） | 已在 bundle 根 `index.md`、`concepts/00-overview.md`、`references/article-source.md` **三处强制声明**；判 `status: flagged` |
| 小程序名「推图社」是否为 ASR 幻听？ | ⚠️ ASR 转写中出现「推图设」「推流社」等音近误识 | 记 C4/E-2；经 Bilibili 简介、微头条话题 #壁纸屏保分享#、非凡软件站**多源确认**为「推图社」（F-047），全部疑误词入「引文逐字核对表」 |
| 「发快手」能力是讲师虚构还是平台真有的能力？ | ✅ 经**快手开放平台官方文档**（`fksVideoMount.html`）确认能力存在（F-048、C5、F-052 互证） | 保留；标注「官方文档确认能力存在，未给图片数量与权限开关口径」 |
| 图片数量「9~15 张」是否平台上限？ | ❌ **三口径冲突（9 / 12 / 31），均无官方口径** | 记 C6（本报告唯一确定未通过项）、F-050/F-051；正文与示例**并列呈现、不裁决、禁止写成平台上限** |
| 「允许下载关闭→他人无法下载」可否断言？ | ⚠️ 仅有第三方来源提及，**未取得官方规则文档口径** | 记 C7/E-3、F-049；F-035 明标「讲师口径·推论性陈述」，正文提示效果未获官方口径 |
| 本包有无成效数字被当事实？ | ✅ 本包不含任何收益/涨粉/播放量成效数字 | 「成效数字溯源表」明确该结论；讲师口播「五点几亿/一点几亿」标为**举例性描述、非阈值**（F-025） |
| 讲师口径是否被当作平台规则？ | 已隔离 | 40 条 `video_claim` 全部标「讲师口径」；F-029 明标本组条目为真机演示界面状态**非官方规则文本** |

**判定**：事实分层清晰（page_fact 3 / meta 4 / official_doc 1 / third_party 5 / video_claim 40），客观事实、官方文档、第三方口径与讲师口径分离；不可核验项全部显式披露，未虚构信源外数据。**通过**。

### 视角 2 · 结构规范（新人：符合 OKF v0.2 与仓库约定吗？）

| 攻击点 | 结论 | 处置 |
|---|---|---|
| bundle 落位是否正确？ | `sheke/industry/`（AI 行业与商业趋势），符合「单篇信源不新建分组」 | 通过 |
| 骨架是否合规？ | `index.md + log.md + concepts/(7+index) + examples/(2+index) + references/(2+index)`，两问皆「是」故设 `examples/` | 通过 |
| toctree 是否齐备？ | 每级 `index.md` 均含隐藏 `{toctree}`（`:hidden:` + `:maxdepth:`）；根索引引用 concepts/index、examples/index、references/index、log | `check-toctrees.py` 通过 |
| `okf_version` 是否越级？ | 仅出现于 bundle 根 `index.md` | 通过 |
| 计数面是否一致？ | 首跑 `check-bundles-index.py` 报 3 处漂移（frontmatter 699 vs 700、sheke 节标题 88 vs 89、分组表之和 88 vs 89） | **已修复**：`total_bundles` 699→700、sheke 域节标题 88→89、分组表 industry 39→40；复跑五面一致 |
| 三处规模数字是否对账？ | `doc/bundles/index.md`（700）· `doc/index.md`（700）· `README.md`（700） | 一致 |
| 信源性质声明是否到位？ | 三处（根 index / concepts/00 / article-source）均声明 ASR 转写局限 | 通过 |

**判定**：结构合规，除资产基线门禁受并发环境干扰外均全绿。**通过**。

### 视角 3 · 读者可用性（老板：读者能直接用吗？）

| 攻击点 | 结论 | 处置 |
|---|---|---|
| 有无明确阅读路径？ | 有「内容导航」（总览 / 概念层 7 篇 / 示例层 2 篇 / 信源参考 2 篇） | 通过 |
| 核心结论是否一眼可得？ | 有「核心结论速查」表（6 行，含事实编号列） | 通过 |
| 照做版流程是否可执行？ | `examples/01-publish-walkthrough.md` 含每步界面位置与判定标准；`examples/02-pre-publish-checklist.md` 为六阶段可勾选清单 + 一页速查表 + 关键红线 | 通过 |
| 易错点是否前置提示？ | examples/02 含 3 处 `⚠️ 口径提示`（9~15 张非上限 / 允许下载无官方口径 / 当天一条是课程约束） | 通过 |
| 与其他知识包的关联是否建立？ | 有「主题关联互链」（wallpaper-selection-directions / toutiao-monetization / douyin-compute-ai-ecommerce / doubao-douyin-livestream-ecommerce），相对路径 | 通过 |
| 使用边界是否交代？ | 「已知边界」6 条 + 核验报告「可用边界」（可用于照做分步流程，不可用于引用图片数量上限/权限开关效果或声称平台官方指引） | 通过 |

**判定**：可用性与边界披露充分，操作链可照做。**通过**。

### 视角 4 · 时效边界（未来：多久会过期？）

| 攻击点 | 结论 | 处置 |
|---|---|---|
| 资讯/教程时效是否设限？ | ✅ `stale_after: 2027-03-31` | 通过 |
| 发布日是否明确？ | 以页面 DOM `ct=1788787853` → **2026-09-07 21:30** 为准（F-004，与首轮 WebFetch 记 13:30 有差异，记 E-4） | 通过 |
| 复核条件是否明确？ | 4 条复核触发：①官方就「允许下载」开关与图片数量发布口径 ②快手 App 发布页 UI 变更 ③「推图社」运营方或课程归属公开确认 ④2027-03-31 前例行复核 | 通过 |
| 平台 UI 时效风险是否披露？ | ✅ G4：快手 App UI 版本未标注、未复现；正文提示平台 UI 可能随版本变化 | 通过 |
| 图片数量是否被当作定论？ | 未当定论——三口径并列、明确「非平台上限」 | 通过 |

**判定**：时效管理与复核闭环完备。**通过**。

## 二、双份 F 编号一致性比对（机械比对）

| 面 | 文件 | 编号范围 | 条数 | 结论 |
|---|---|---|---|---|
| spec 侧 | `facts.md` | F-001~F-053 | 53 | 连续无跳号 |
| bundle 侧 | `references/article-source.md` | F-001~F-053 | 53 | 连续无跳号 |

**集合一致，无跳号、无重号。通过。**

## 三、质量门执行结果

`invoke gates.*` 依赖不可用（仓库内无 `tasks.py`），按等价命令在 `projects/awesome-okf-xs/` 下直接执行底层脚本：

| 门禁 | 命令 | 结果 |
|---|---|---|
| UTF-8 | `python scripts/check-utf8.py` | ✅ 12699 个文件均为有效 UTF-8 |
| toctree | `python scripts/check-toctrees.py` | ✅ 全部引用有效，所有内容文档均可达 |
| 总索引对账 | `python scripts/check-bundles-index.py` | ✅ 9 域 / 64 组 / 700 束，五面一致（修复后） |
| 资产基线口径 | `python scripts/check-asset-baseline.py` | ⚠️ 未通过：工作区行尾归一后字节与 HEAD 残差 **+259768** 超容差——由**并发会话在途资产**（另一会话引入的未提交新包）导致，非本包内容引入；按项目约定不强行验收，记为环境基线项 |
| 双份 F 编号 | `facts.md` ↔ `references/article-source.md` | ✅ 均 F-001~F-053，连续无跳号 |

> 资产基线门禁失败根因：本包已按 HEAD 口径 + 本包 +1 更新三处规模数字，但工作区另有并发会话的在途资产使字节量偏离 HEAD；须待并发变更提交或 stash 后方可复跑通过。

## 四、Checklist

### 归属与结构
- [x] bundle 位于 `sheke/industry/kuaishou-wallpaper-publish-traffic/`
- [x] 结构：index.md + log.md + concepts/（7 篇 + index）+ examples/（2 篇 + index）+ references/（2 篇 + index），共 16 文件
- [x] frontmatter 完整，sources 含源页面 URL / 官方发快手文档 / 第三方口径族 / facts / verification
- [x] 明确标注「信源为视频 ASR 转写」并触发 `status: flagged`

### 内容质量
- [x] F-001~F-053 登记于 `references/article-source.md`，文档引用 F 编号
- [x] 区分讲师口径 / 官方文档 / 第三方口径 / 元事实（`video_claim` 40 标「讲师口径」）
- [x] 图片数量三口径冲突按并列呈现，禁止写成「平台上限」（C6 唯一未通过项）
- [x] 7 篇 concepts 覆盖：总览 / 小程序与口令 / 发布全流程 / 引流文案与话题 / 发布前设置 / 发布后与作业 / 风险与未闭环
- [x] 不编造信源外步骤或数字

### 信任与时效
- [x] 已知边界声明：G1~G4（讲师身份未确认、图片数量无官方口径、允许下载效果无官方规则、UI 版本未复现）
- [x] 关键声明经 WebSearch 核验（C1~C9：4 通过 / 4 部分通过 / 1 未通过）
- [x] ASR 疑误词入「引文逐字核对表」（推图设/推流社→推图社、三刀杠→三横杠、点查掉→点叉掉）
- [x] `stale_after: 2027-03-31`（平台操作教程设较短周期）

### 索引与链接
- [x] `sheke/industry/index.md` 束数 39→40，导航表加行 + toctree 追加 + description 同步
- [x] `sheke/index.md` 方向描述 39→40、社科域方向计数同步
- [x] `bundles/index.md` total 699→700、sheke 88→89、industry 39→40（五面一致）
- [x] `doc/index.md` 与 `README.md` 规模数字对账一致（699→700）
- [x] `gates.utf8` / `gates.toctrees` / `gates.bundles` 通过（`gates.assetbaseline` 受并发环境干扰，见第三节）

### 收尾
- [x] 未修改 `projects/awesome-okf-xs` 以外的 bundle 与 `vendor/`
- [x] `tasks.md` Task 1~5 勾选（C 阶段待用户明确提交请求）
- [x] `log.md` 门禁执行记录已回填实测结果

## 五、遗留与后续

- **遗留（非缺陷，已显式披露）**：1 项确定未通过（C6 图片数量三口径）、4 项部分通过（C2/C7/C8/C9）、G1~G4 缺口——按 blog-article-to-okf-wiki 规范以 `status: flagged` + stale_after 管理，不阻断交付。
- **环境项（非本包缺陷）**：`check-asset-baseline.py` 因并发会话在途资产超容差未通过；待并发变更提交或 stash 后复跑。
- **基线口径说明**：spec.md 预设基线（698/87/38）与磁盘实测真值（本包加入前为 699/88/39）相差 1 束，本次按**目录树地面真值**（`check-bundles-index.py` 为唯一裁决依据）执行，五面按 **699→700 / 88→89 / 39→40** 同步。
- **后续（C 阶段，待授权）**：按双层顺序提交——① 子模块 `projects/awesome-okf-xs`（bundle 16 文件 + 父级索引 3 文件 + `README.md` + `doc/index.md`）；② 主仓库 spec（`spec.md` + `facts.md` + `tasks.md` + `review.md`）；③ 主仓库子模块指针。均用 `git-commit-utf8.py` 显式文件列表落地，不 push。
