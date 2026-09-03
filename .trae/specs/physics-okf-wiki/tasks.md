# Tasks: 国外物理著作原文与解读 OKF Wiki 全面系统重建

> 状态总览：10/10 任务完成（Task 9 的独立审查门由 review.md 记录）

---

## Task 1: R 阶段 — 调研扩充元典信源（13-18 部扩展著作）

- **Status**: completed
- **AC**: AC-1
- **Completion Evidence**: facts.md 扩充至 F-136（F-105~F-136 共 32 条新事实），覆盖 8 部著作（惠更斯《摆钟论》、法拉第《电学实验研究》、普朗克 1900-1901 论文、卡诺《火的动力思考》、居里《放射性物质研究》、德布罗意 1924 论文、玻色 1924 论文、温伯格 1967 论文）+ 6 条门户事实（F-131~F-136）；URL 核验表追加 11 行（WebSearch/WebFetch 核验）；G1 无因果词。

## Task 2: R 阶段 — 新建原文精读束骨架（physics-original-text-reading）

- **Status**: completed
- **AC**: AC-2, AC-6
- **Completion Evidence**: `kexue/physics/physics-original-text-reading/` 含 index.md（okf_version 0.2）、concepts/、examples/、references/、facts.md（28 条）、insights.md、log.md 共 13 个文件；全部 frontmatter 有 type 字段。

## Task 3: I 阶段 — 原文精读束 concepts/examples 内容生成

- **Status**: completed
- **AC**: AC-2, AC-7
- **Completion Evidence**: concepts/ 4 篇方法论（三步法/校勘/符号还原/历史定位）；examples/ 6 篇精读（惠更斯拉丁、法拉第英、卡诺法、普朗克德、爱因斯坦德、吉布斯英）；references/ 2 篇（信源表+引用规则）；在版权译本零引用；4 处转写引文已补注「大意非逐字」。

## Task 4: E 阶段 — 新建量子力学论文精读束（quantum-papers-reading）

- **Status**: completed
- **AC**: AC-3, AC-6
- **Completion Evidence**: 束结构完整（13 文件）；concepts 2 篇 + examples 4 篇（玻尔 1913/海森堡 1925/薛定谔 1926/狄拉克 1928）+ references 2 篇；facts 20 条；van der Waerden 1967 零引用。

## Task 5: E 阶段 — 新建相对论原著精读束（relativity-originals-reading）

- **Status**: completed
- **AC**: AC-3, AC-6
- **Completion Evidence**: 束结构完整（13 文件）；concepts 2 篇 + examples 3 篇（1905/1908/1916）+ references 2 篇；facts 17 条；Einstein Papers 门户用法固化。

## Task 6: E 阶段 — 新建热统经典精读束（thermo-statistical-classics）

- **Status**: completed
- **AC**: AC-3, AC-6
- **Completion Evidence**: 束结构完整（13 文件）；concepts 2 篇 + examples 3 篇（卡诺 1824/玻尔兹曼 1872/吉布斯 1902）+ references 2 篇；facts 17 条；Brush 1964 零引用。

## Task 7: 更新现有 physics-classics-reading 束（元典地图与扩展书单）

- **Status**: completed
- **AC**: AC-1
- **Completion Evidence**: canon-map.md 扩至 21 部（12 核心 + 9 扩充，新增现代前沿线索与 7 类文体分布）；05-extended-canon.md 5 条升级标注 + 法拉第等新增；insights.md 知识地图补 1967-今 行；index.md 描述 12→21 部；log.md 记录扩充。

## Task 8: 更新分组索引与总索引

- **Status**: completed
- **AC**: AC-4
- **Completion Evidence**: kexue/physics/index.md 6 束多线索；kexue/index.md 6 束四线索；bundles/index.md 五面同步（frontmatter 382、计数行、kexue 节 14 束、physics 表行 6）；与并行会话的 383 终态（含其 east-west-dialogue）合流验证五面一致。

## Task 9: V 阶段 — 对抗审查

- **Status**: completed
- **AC**: AC-8
- **Completion Evidence**: 四视角审查记录于各束 log.md「对抗审查（2026-08-31）」节：①物理准确性抽查通过（Planck h=6.55e-27、Bose DOI、Weinberg PRL、de Broglie 答辩日与权威来源一致）；②引文真实性——4 处转写大意引文补注「大意非逐字」，零虚构引文；③OKF 格式——10 个 examples 文件 Malformed YAML（description 弯引号）修复为单引号标量；④版权合规——在版权译本零引用。Rubric 评分：2/2（完整 R→I→E→V→C，各质量门通过）。

## Task 10: C 阶段 — 质量门验证

- **Status**: completed
- **AC**: AC-5
- **Completion Evidence**: 暂存态快照（git checkout-index --prefix，PowerShell 变量形式）三门验证：UTF-8 7399 文件通过；toctrees 全部可达（我的束零问题，剩余 2 项未收录为并行会话 east-west-dialogue WIP 归其对账）；bundles-index 五面一致（382 自洽 / 合并终态 383 一致）；Sphinx dummy 构建退出码 0 零警告。
