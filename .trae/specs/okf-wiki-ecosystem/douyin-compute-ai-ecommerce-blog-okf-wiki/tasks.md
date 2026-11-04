# Tasks

> 执行链路：`R → I → E → V → 索引收尾`（C 阶段待用户明确提交请求）。
> 产出位于子模块 `projects/awesome-okf-xs/doc/bundles/sheke/industry/douyin-compute-ai-ecommerce/`，spec 位于主仓库 `.trae/specs/okf-wiki-ecosystem/douyin-compute-ai-ecommerce-blog-okf-wiki/`。

- [x] Task 1: R 阶段——信源获取、事实采集与 P0 核验
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: None
  - **Completion Evidence**:
    - 信源获取：WebFetch 直取微信公众号《抖音突然成立大批公司，准备放手一搏》（电商派Pro，作者李响，2026-10-30）全文，本次未被微信反爬拦截（无需回退 `agent-browser`）。
    - 事实登记：`facts.md` 登记 **F-001~F-036**（连续无跳号），七组 A~G；`type` 分 `page_fact`（28）/ `author_claim`（8），无 `reporter_test`。
    - P0 核验：WebSearch 完成 **C1~C19**（15 项多源通过、3 项部分通过、1 项未通过）、**E1~E5** 口径差异与勘误、**G1~G6** 缺口；据此判 `status: flagged`。
  - **Description**: 提取博文全文 → 逐条抄录为 F 编号事实（区分客观事实与作者观点）→ 对核心数字/日期/官方表态/成效数字做多源核验 → 输出核验结论与缺口清单。

- [x] Task 2: I 阶段——骨架判定与三层拆分
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 1
  - **Completion Evidence**:
    - 操作可复现性两问皆"否"（全文为公司注册信息、投资金额、平台经营数据与作者分析，无读者可照做的安装/配置/代码流程）→ **不设 `examples/`**。
    - 三层拆分：① 公司与时间线层；② 算力基建与投资层；③ AI 电商落地与转化层 → 对应 3 篇 concepts。
    - 作者判断（F-002、F-026、F-031~F-036）显式标「作者观点」，未混入客观事实。
  - **Description**: 按两问确定骨架，按语义层级设计 concepts 结构。

- [x] Task 3: E 阶段——信源先行生成 bundle（9 文件）
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 2
  - **Completion Evidence**:
    - 先写 `references/`（`article-source.md` F-001~F-036 + `verification.md` C1~C19/E1~E5/G1~G6 + `index.md`），再写 `concepts/`（3 篇 + `index.md`），最后写 bundle `index.md` + `log.md`。
    - `okf_version: "0.2"` 仅出现于 bundle 根 `index.md`；每级 `index.md` 含隐藏 `{toctree}`。
    - 顶部 `⚠️ flagged` 提示块、主题关联表、阅读路径表、核心结论速查表（含核验列）、已知边界、时效表齐备。
  - **Description**: 信源先行（先 F 编号再行文），生成完整 bundle 骨架与内容。

- [x] Task 4: V 阶段——四视角对抗审查 + 双份 F 编号比对 + 机械门禁
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 3
  - **Completion Evidence**:
    - 四视角审查（事实溯源 / 结构规范 / 读者可用性 / 时效边界）结论与处置见 `review.md`。
    - 双份 F 编号比对：`facts.md` 与 `references/article-source.md` 均为 F-001~F-036，连续无跳号，集合一致。
    - 机械门禁（`invoke gates.*` 依赖不可用时按等价命令直接执行底层脚本）：`check-utf8.py` ✅ 12620 文件、`check-toctrees.py` ✅、`check-bundles-index.py` ✅ 9/64/695 五面一致、`check-asset-baseline.py` ✅、Python 红线 ✅ 11 passed。
    - 勘误落实：源文「数据中心 40 个」→ 正文呈现官方口径 **36 个** 并标注源文口径。
  - **Description**: 以对抗视角攻击产出，修复发现项，跑通全部质量门，结果回填 `log.md`。

- [x] Task 5: 索引收尾（父级导航与计数面同步）
  - **Status**: completed ｜ **Priority**: high ｜ **Depends On**: Task 4
  - **Completion Evidence**:
    - `sheke/industry/index.md`：束数 36→**37**（导航表加行 + toctree 追加 + description 更新）。
    - `sheke/index.md`：industry 描述 36→**37**、社科域 85→**86**。
    - `doc/bundles/index.md` 五面同步：`total_bundles` 694→**695**、sheke 域 85→**86**、industry 分组 36→**37**。
    - `doc/index.md` 与 `README.md`：库规模 694→**695**。
  - **Description**: 完成 bundle 落位所需的全部父级索引与计数更新，保证规模数字单一真相源一致。

- [ ] Task 6: C 阶段——双层原子提交
  - **Status**: pending ｜ **Priority**: medium ｜ **Depends On**: Task 5（且需用户明确提交请求）
  - **Completion Evidence**（用户授权后回填）:
    - ① 子模块 `projects/awesome-okf-xs`：显式文件列表提交 bundle 9 文件 + 父级索引 3 文件 + `README.md` + `doc/index.md`。
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
