# Tasks

> 执行链路：`R → I → E → V → 索引收尾`（C 阶段待用户明确提交请求）。
> 产出位于子模块 `projects/awesome-okf-xs/doc/bundles/sheke/industry/doubao-douyin-livestream-ecommerce/`，spec 位于主仓库 `.trae/specs/okf-wiki-ecosystem/doubao-douyin-livestream-ecommerce-blog-okf-wiki/`。

- [x] Task 1: R 阶段——信源获取、事实采集与 P0 核验
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: None
  - **Completion Evidence**:
    - 信源获取：WebFetch 被微信反爬拦截，改用 `agent-browser open` + `eval 'document.querySelector("#js_content").innerText'` 提取全文，`get title` 校验标题一致。
    - 事实登记：`facts.md` 与 bundle `references/article-source.md` 双份登记 **F-001~F-043**（连续无跳号），六组 A~F；`type` 分 `page_fact` / `reporter_test` / `author_claim`，观点条目标 `[观点]`。
    - P0 核验：WebSearch 完成 **C1~C17**（9 项多源通过、8 项未能核验）、**E1~E4** 口径差异、**G1~G10** 缺口；据此判 `status: flagged`，报告见 `references/verification.md`。
  - **Description**: 提取博文全文 → 逐条抄录为 F 编号事实（标记事实/实测/观点）→ 对核心声明做多源核验 → 输出核验报告与缺口清单。

- [x] Task 2: I 阶段——骨架判定与三层拆分
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 1
  - **Completion Evidence**:
    - 操作可复现性两问皆"否"（无读者可照做的安装/配置/代码流程；价格对比为不可复现单次实测）→ **不设 `examples/`**。
    - 三层拆分：① 事件/时间线层；② 转化与补贴机制层；③ 竞争格局层 → 对应 3 篇 concepts。
    - 机制层判断（F-026 补贴归因、F-039~F-043 共同趋势）显式标「观点」，未混入客观事实。
  - **Description**: 按两问确定骨架，按语义层级设计 concepts 结构。

- [x] Task 3: E 阶段——信源先行生成 bundle（9 文件）
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 2
  - **Completion Evidence**:
    - 生成 `index.md`（frontmatter `type: bundle`、`status: flagged`、`stale_after: 2026-12-31`、sources 三源）+ `log.md` + `concepts/`（`index.md` + 3 篇）+ `references/`（`index.md` + `article-source.md` + `verification.md`）。
    - 每级 `index.md` 含 `{toctree}`（`:hidden:` + `:maxdepth:`）；`okf_version` 仅出现于 bundle 根 `index.md`。
    - 顶部 `⚠️ flagged` 提示块、主题关联表、阅读路径表、核心结论速查表（含核验列）、已知边界、时效表齐备。
  - **Description**: 信源先行（先 F 编号再行文），生成完整 bundle 骨架与内容。

- [x] Task 4: V 阶段——四视角对抗审查 + 双份 F 编号比对 + 机械门禁
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 3
  - **Completion Evidence**:
    - 四视角审查（事实溯源 / 结构规范 / 读者可用性 / 时效边界）结论与处置见 `review.md`。
    - 双份 F 编号比对：`facts.md` 与 `references/article-source.md` 均为 F-001~F-043，连续无跳号，集合一致。
    - 机械门禁（`invoke gates.*` 依赖不可用，按等价命令直接执行底层脚本）5 门全绿：`check-utf8.py`（12580 文件）、`check-toctrees.py`、`check-bundles-index.py`（9 域/63 组/692 束五面一致）、`check-asset-baseline.py`、`pytest tests/unit/test_no_future_annotations.py`（11 passed）。
    - 修复记录：首跑 `check-bundles-index.py` 报 2 处计数漂移（sheke 节标题 83 vs 84、分组表之和 83 vs 84）→ 修正域节标题与 industry 分组行束数后复跑通过。
  - **Description**: 以对抗视角攻击产出，修复发现项，跑通全部质量门，结果回填 `log.md`。

- [x] Task 5: 索引收尾（父级导航与计数面同步）
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 4
  - **Completion Evidence**:
    - `doc/bundles/index.md` 五面同步：`total_bundles` 691→**692**、prose 计数、mermaid sheke 83→**84**、域节标题 83 束→**84 束**、分组表 industry 35→**36** 并追加包条目。
    - `doc/bundles/sheke/index.md`：方向描述 35→**36**、分组导航表 Industry 行追加条目（36 束）。
    - 三处规模数字对账一致：`doc/index.md`（692）、`README.md`（badge/正文/表行/合计 692）、`doc/bundles/index.md`（692）。
  - **Description**: 完成 bundle 落位所需的全部父级索引与计数更新，保证规模数字单一真相源一致。

- [ ] Task 6: C 阶段——双层原子提交（待用户明确请求）
  - **Status**: pending ｜ **Priority**: medium ｜ **Depends On**: Task 5
  - **Completion Evidence**: —
  - **Description**: ① 子模块 `projects/awesome-okf-xs` 内显式文件列表提交（bundle 9 文件 + 三层父级索引 + README + doc/index）；② 主仓库提交 spec；③ 主仓库更新子模块指针。使用 `python .agents\scripts\git-commit-utf8.py -m "<type>(<scope>): <中文描述>" <显式文件列表>`，不 push。

# Task Dependencies

- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 depends on Task 3
- Task 5 depends on Task 4
- Task 6 depends on Task 5（且需用户明确提交请求）
