# Tasks

> 执行链路：`R → I → E → V → 索引收尾`（C 阶段待用户明确提交请求）。
> 产出位于子模块 `projects/awesome-okf-xs/doc/bundles/sheke/industry/kuaishou-wallpaper-publish-traffic/`，spec 位于主仓库 `.trae/specs/okf-wiki-ecosystem/kuaishou-wallpaper-publish-traffic-okf-wiki/`。

- [x] Task 1: R 阶段——信源获取、事实采集与 P0 核验
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: None
  - **Completion Evidence**:
    - 信源获取（降级通道）：WebFetch 直取微信公众号《快手发布-视频教程》页面 HTML（约 346 万字符）后实测发现 **`js_content` 仅约 3588 字符、正文无知识性文字**——唯一内容为 **242.67 秒**（4 分 02 秒）`video_iframe`（`data-mpvid=wxv_4684122996708737027`，544×308）与两则红字警示。故取证降级为：提取视频地址 → 本地下载（`.temp/kuaishou-wx/video.mp4`，不随包发布）→ 本地离线 ASR（`local-asr`，Intel AIPC）转写音轨。
    - ASR 求全：首轮全片转写止于 **137.547 秒**，与总长 242.67 秒不符（疑截断）→ 改用**三段拼合**（全片首段 + `-ss 140 -t 60` 桥接段 20.156s + `-ss 190` 尾段 25.127s）确认全文覆盖，三段原文落 `article-source.md`。
    - 事实登记：`facts.md` 登记 **F-001~F-053**（连续无跳号），九组 A~I；口径分布 `page_fact` 3 / `meta` 4 / `official_doc` 1 / `third_party` 5 / `video_claim` 40，**无 `reporter_test`**。
    - P0 核验：WebSearch 完成 **C1~C9**（**4 项通过** C1/C3/C4/C5、**4 项部分通过** C2/C7/C8/C9、**1 项未通过** C6）、**E1~E4** 口径差异与勘误、**G1~G4** 缺口；据此判 `status: flagged` + `stale_after: 2027-03-31`。
  - **Description**: 提取信源（页面 + 视频音轨）→ 逐条抄录为 F 编号事实（区分页事实/师资口径/官方文档/第三方）→ 对核心声明做多源核验 → 输出核验结论、勘误清单与缺口登记。

- [x] Task 2: I 阶段——骨架判定与三层拆分
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 1
  - **Completion Evidence**:
    - 操作可复现性两问皆「是」（① 有读者可照做的分步操作链，含具体按钮位置与设置项；② 讲师真机演示可对照复现，保留项为无独立第二人复现、UI 版本未标注）→ **设 `examples/`**。
    - 三层拆分：① 小程序与口令层；② 快手端发布层（流程 / 文案 / 设置）；③ 发布后与边界层 → 对应 concepts 七篇。
    - 讲师口径（`video_claim` 40 条）与官方文档（F-048）、第三方口径（F-047、F-049~F-052）、元事实（F-004、F-005、F-029、F-053）分层显式标注，未混同。
  - **Description**: 按两问确定骨架（含 examples/），按语义层级设计 concepts 结构。

- [x] Task 3: E 阶段——信源先行生成 bundle（16 文件）
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 2
  - **Completion Evidence**:
    - 先写 `references/`（`article-source.md` F-001~F-053 + `verification.md` C1~C9/E1~E4/G1~G4 + `index.md`），再写 `concepts/`（7 篇 + `index.md`），再写 `examples/`（2 篇 + `index.md`），最后写 bundle 根 `index.md` + `log.md`；合计 **16 文件**。
    - `sources` 结构、`sources` 含源页面 URL / 官方发快手文档 / 第三方口径族 / facts / verification；`status: flagged`、`stale_after: 2027-03-31`。
    - `okf_version: "0.2"` 仅出现于 bundle 根 `index.md`；每级 `index.md` 含隐藏 `{toctree}`。
    - **信源性质三处强制声明**（bundle 根 `index.md` / `concepts/00-overview.md` / `references/article-source.md`）：信源为本地离线 ASR 转写而非原始文本，存在音近误识风险。
    - 顶部 `⚠️ flagged` 提示块、类别计数表、核心结论速查表（含事实编号列）、内容导航、已知边界、主题关联互链表齐备。
  - **Description**: 信源先行（先 F 编号再行文），生成完整 bundle 骨架与内容；ASR 局限按规范三处声明。

- [x] Task 4: V 阶段——四视角对抗审查 + 双份 F 编号比对 + 机械门禁
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 3
  - **Completion Evidence**:
    - 四视角审查（事实溯源 / 结构规范 / 读者可用性 / 时效边界）结论与处置见 `review.md`。
    - 双份 F 编号比对：`facts.md` 与 `references/article-source.md` 均为 **F-001~F-053**，连续无跳号，集合一致。
    - 机械门禁（`invoke gates.*` 依赖不可用时按等价命令直接执行底层脚本）：`check-utf8.py` ✅ 12699 文件有效 UTF-8、`check-toctrees.py` ✅ 全部引用有效、`check-bundles-index.py` ✅ 9 域/64 组/**700 束**五面一致、`check-asset-baseline.py` ⚠️ 因**并发会话在途资产**致行尾归一残差超容差（非本包引入，环境基线项，未强行验收）。
    - 勘误落实：图片数量三口径（9/12/31）并列不裁决、不写「平台上限」；「当天只发一条」明示为作业约束非平台规则；「允许下载关闭」明示效果未获官方口径。
  - **Description**: 以对抗视角攻击产出，修复发现项，跑通质量门，结果回填 `log.md`。

- [x] Task 5: 索引收尾（父级导航与计数面同步）
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 4
  - **Completion Evidence**:
    - 基线口径：按**磁盘实测真值 + 本包 +1** 计算（`check-bundles-index.py` 以目录树为唯一地面真值）；实测真值较 spec.md 预设基线（698/87/38）**多 1 束**（仓库在本包加入前已存在 1 束未计入预设的改动），故五面按 **699→700 / 88→89 / 39→40** 同步。
    - `sheke/industry/index.md`：束数 39→**40**（导航表加行 + toctree 追加 + description 更新）。
    - `sheke/index.md`：industry 描述 39→**40**、社科域方向计数 39→**40**。
    - `doc/bundles/index.md` 五面同步：`total_bundles` 699→**700**、sheke 域 88→**89**、industry 分组 39→**40**、mermaid 域节文字 88→**89**、toctree 追加 `kuaishou-wallpaper-publish-traffic/index`。
    - `doc/index.md`（2 处）与 `README.md`（badge + 正文 + 域表 + 合计行 + 精选推荐表）计数同步至 **700**。
    - 首跑 `check-bundles-index.py` 报 3 处计数漂移（frontmatter 699 vs 700、sheke 节标题 88 vs 89、分组表之和 88 vs 89）→ 按目录树真值修复后复跑 ✅ 五面一致。
  - **Description**: 完成 bundle 落位所需的全部父级索引与计数更新，保证规模数字单一真相源一致。

- [ ] Task 6: C 阶段——双层原子提交
  - **Status**: pending ｜ **Priority**: medium ｜ **Depends On**: Task 5（且需用户明确提交请求）
  - **Completion Evidence**（用户授权后回填）:
    - ① 子模块 `projects/awesome-okf-xs`：显式文件列表提交 bundle 16 文件 + 父级索引 3 文件 + `README.md` + `doc/index.md`。
    - ② 主仓库 spec：提交 `spec.md` + `facts.md` + `tasks.md` + `review.md`。
    - ③ 主仓库子模块指针：更新 `projects/awesome-okf-xs` gitlink。
    - 均以 `python .agents\scripts\git-commit-utf8.py -m "<type>(<scope>): <中文描述>" <显式文件列表>` 落地，不 push。
  - **Description**: ① 子模块内显式文件列表提交；② 主仓库提交 spec；③ 主仓库更新子模块指针。不 push。

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4
- Task 6 depends on Task 5（且需用户明确提交请求）
