---
status: "draft"
title: "从帛书《老子》视角分析 Xuanspace 并产出项目蓝图与优化建议书 - 独立审查清单"
change-id: "analyze-xuanspace-through-boshu-laozi"
---

# 独立审查清单（Review）

> 对应规格：[spec.md](spec.md) ｜ 实施计划：[tasks.md](tasks.md)
> 用法：实施完成后逐项核验，通过者勾选；未通过者回到 tasks.md 追加修复任务。

## 一、交付物存在性（AC-1）

- [x] 《项目蓝图》文档存在于 `projects/xuanspace/doc/` 且内容非空
- [x] 《优化建议书》文档存在于 `projects/xuanspace/doc/` 且内容非空
- [x] 两份文档均**未添加** YAML frontmatter、以 H1 开头
- [x] 未新建任何 `.meta/toml/` 元数据文件（AC-1 / FR-11 / C-3）

## 二、导航与构建（AC-2 / NFR-2）

- [x] `projects/xuanspace/doc/index.md` 已新增 toctree 分组并登记两份文档
- [x] 现有四个 toctree 的条目与顺序未被破坏
- [x] Sphinx HTML 构建成功
- [x] 构建日志中无指向两份新文档的 orphan / 未收录 warning

## 三、哲学纪律（AC-3 / FR-8）

- [x] 每处《老子》引文均标注版本（马王堆甲本／乙本／今本／郭店楚简本之一）
- [x] 全文无笼统「帛书本」式的引文版本表述（检索命中 0）
- [x] 甲本损掩处已显式标注
- [x] 抽查 ≥3 处引文与 `projects/awesome-okf-xs/doc/bundles/guoxue/laozi/**` 正文逐字一致
- [x] 「道—法—术—器」解构处显式声明「结构类比，非影响关系」，无「老子早就说了」式附会表述

## 四、溯源与事实（AC-4 / FR-9）

- [x] 存在事实清单，条数 ≥25
- [x] 事实清单无因果推断词（因为/导致/因此/所以/使得/从而）——检索命中 0
- [x] 抽查 ≥8 条现状事实陈述，全部带相对路径引用且引用真实存在
- [x] 三条声明一致性线索（`docs/` vs `doc/`、`xs` 子命令数、doc 目录树）**均先核验后使用**，未核验前未作为缺陷断言

## 五、《项目蓝图》质量（AC-8 / AC-11 / FR-1 / FR-2 / FR-6 / FR-7）

- [x] 结构完整：项目定位 → 道—法—术—器四层解构 → 现状能力地图 → 三之位诊断 → 目标态蓝图 → 演进路线
- [x] 四层解构逐层给出「对应实体（带引用） + 承载功能 + 薄弱环节」
- [x] 「三之位」诊断五步齐备（命名二／找关系位／检验非实体性／表述为关系／落地动作）
- [x] 显式命名并规避 ≥1 个反模式
- [x] 「三问检验」自查结果已写入
- [x] rubric 评分：四层解构深度 ≥4（1-5）

## 六、《优化建议书》质量（AC-5 / AC-9 / FR-3 / FR-4 / FR-12）

- [x] 建议按 P0/P1/P2 分级，优先级依据明确
- [x] 每条建议五要素齐备：判据 + 现状证据（相对路径 `#L起-L止`）+ 期望态 + 落地动作 + 验证方式
- [x] 无「正确的废话」条目；每条均可判定为「已做/未做」
- [x] 未在本次落地任何建议（仅产出建议）
- [x] rubric 评分：可执行性与判据强度 ≥4（1-5）

## 七、洞察质量（AC-10 / FR-5）

- [x] 洞察 ≥3 条，每条为完整四元组（陈述 + 证据 + 反常识 + 行动）
- [x] 洞察维度互不重叠
- [x] ≥2 条洞察挑战默认假设
- [x] 每条「反常识点」均有事实支撑
- [x] rubric 评分：洞察质量与反常识性 ≥4（1-5）

## 八、门禁与边界（AC-6 / AC-7 / NFR-3 / NFR-4 / NFR-5）

- [x] `check-links.py` 对新增/修改文件报告 0 断链
- [x] `check_mermaid.py` 校验通过（如含 Mermaid）
- [x] 文档内交叉引用全部为相对路径，无 `file:///`，无 `.temp/` 引用
- [x] `projects/xuanspace` 的 `git status` 变更仅限 `doc/`（两份新文档 + `index.md`）
- [x] `projects/xuanspace` 的 HEAD 与 Task 1 记录的基线一致（`git log -1`），无新增 commit
- [x] 未执行 push / tag
- [x] `projects/awesome-okf-xs` 零变更
- [x] 未回滚或覆盖任何既有他人改动

## 九、语言与可读性（NFR-1 / NFR-6）

- [x] 两份文档均为简体中文；术语在全篇一致
- [x] 标题层级不跳级；表格分隔符与列数一致
- [x] 代码、路径、命令保留英文原样

---

## 核验证据（Task 7 留存）

| 检查项 | 命令 / 方法 | 结果 |
|---|---|---|
| 交付物存在性 | 检查 `projects/xuanspace/doc/` 下 `blueprint.md`、`recommendations.md` | 均存在、以 H1 开头、无 YAML frontmatter；未新建 `.meta/toml/` |
| Sphinx 构建 | `python -m sphinx -b html doc doc/_build/html`（cwd = `projects/xuanspace`） | `构建成功。`，无 WARNING / ERROR；`blueprint.html`、`recommendations.html` 均已产出 |
| 链接门禁 | `python .agents/scripts/check-links.py --path doc`（cwd = `projects/xuanspace`） | 两份新文档 **0 断链**；目录内 33 个断链均为存量（`intro.md`、`quickstart.md`、`okf/*.md`） |
| Mermaid 门禁 | `python .agents/scripts/repo-check.py mermaid --path <临时目录副本>` | `扫描文件: 2, 问题文件: 0, 错误: 0, 警告: 0`，通过 |
| AC-3 版本纪律 | `Select-String -Pattern '帛书本'` 于 `doc/*.md` | 命中 **0** |
| 事实清单 | `blueprint.md` 附录「事实清单（R 阶段）」 | 45 条（≥25），每条带相对路径引用；因果词检索命中 **0** |
| 引文逐字对照 | 比对 `guoxue/laozi/boshu-reading/concepts/04-key-variants.md`、`guoxue/laozi/laozi-works/text/boshu-jia.md`、`guoxue/laozi/laozi-lineage/variants/taboo-heng-chang.md` | 「道可道也，非恒道也」「甲本此句残」「避讳『恒』→『常』」三处一致 |
| 边界核对（xuanspace） | `git status --short` / `git log -1` | ` M doc/index.md`、`?? doc/blueprint.md`、`?? doc/recommendations.md`；HEAD `8db593d` 未变 |
| 只读边界（awesome-okf-xs） | `git status --short` | 16 项均为本次会话之前的既存变更，本次零写入 |
| 禁止项 | 检查 git 历史 | 未执行 commit / push / tag |

> 门禁脚本的已知环境约束：`.agents/scripts/constants.py` 的 `EXCLUDED_DIRS` 含 `projects`，故对 `projects/xuanspace` 的扫描须在 xuanspace 内以相对路径执行（链接检查），或复制到不含 `projects` 的临时目录后执行（Mermaid 检查）。
