# bundles 学科分类重构（全库物理重组）Spec

> 方法论：七概念场景3（重构优化）I→F→A→V→C；session `sc-20260901-bundles-discipline-reclassify`
> 前置变更：[bundles-grouping-refactor](../bundles-grouping-refactor/spec.md)（已完成，28 组→10 技术域；本变更在其基础上按学科逻辑二次重组）

## Why

`awesome-okf-xs/doc/bundles/` 现有 **17 域 / 75 组 / 363 束**，分类依据是「技术生态」而非「学科逻辑」，导致：

- **人文内容杂糅于巨型域**：`think/` 域塞入 51 束 / 26 组，儒释道法墨易医、数学、声乐、两性关系、性学、职场无关内容混居一处，无学科边界
- **学科内容碎片化**：中医内容分散在 `tcm/`（5 束）与 `think/`（黄帝内经、道医、医心方、养生、房中 5 组）；数学经典分裂在 `science/`（无）与 `think/math`、`think/suanxue`
- **查找路径反直觉**：用户按「国学/科学/哲学/文学」的学科心智模型无法定位内容

用户决策（已确认）：
1. **全库物理重构**——363 束全部按学科归类，技术内容归入「技术」超类
2. **增设辅助学科域**——四分类无法容纳的内容（中医、声乐、职场、两性、性学、养生、Ψhē）设辅助域，不强行扭曲
3. **广义国学**——国学 = 中国传统学术整体（经史子集 + 中国化佛学 + 中国算学）

## I 阶段洞察（重构本质）

| # | 陈述 | 证据 | 反常识 | 行动 |
|---|------|------|--------|------|
| I-1 | 现有分类的第一维度是「内容来源生态」（哪个开源项目/哪类典籍），而非「知识学科」 | 17 域中 14 个为技术生态域；think 域按书名/学派平铺 26 组 | 技术域分类对技术内容是合理的，问题只在人文侧——但用户选择全库统一学科逻辑，技术域降为「技术」超类下的二级分组 | 建立「学科域→分组」两级结构，技术生态域整体降级为技术域内分组 |
| I-2 | 人文 61 束中约 30 束属广义国学，四分类中「哲学」「文学」近乎空置（西方哲学 0 束、文学仅 1 束） | think 域清单：儒道释法墨易等 30 束归国学；psi 4 束；classics 1 束 | 四分类虽不平衡，但作为导航骨架仍成立——空置类目是内容现状的如实反映，不是分类缺陷 | 保留四主类作一级域，不以内容多寡合并类目 |
| I-3 | 上次域层重构（28组→10域）修复 1804 处链接且零断链，证明「整子树 git mv + 两类链接批量修复」工艺可复用 | bundles-grouping-refactor 提交 c02bb5e/929bda7/fd124f7 | 本次全部 17 域中 16 域移动（仅 meta 锚点不动），链接修复量预计高于上次 | 复用上次的迁移工艺与验证门（gates.all + dummy build） |

## F 阶段设计（目标分类体系）

**公理**：①每个束有且仅有一个学科归属；②目录结构即学科导航；③技术内容保持生态分组不拆散；④锚点（meta）路径不变。

### 目标结构：8 学科域 + 1 规范锚点（9 域 / 43 组 / 363 束）

| 学科域 | 目录 | 收录分组（现路径 → 新路径） | 束数 |
|---|---|---|---|
| 📜 国学 | `guoxue/` | think/{confucian, confucius, laozi, zhuangzi, mozi, yinyangjia, zhouyi, hetu-luoshu, legalism, huangdi, buddhism, guiguzi, daojia, yangming, suanxue} → `guoxue/<组名>/`（组名不变） | 30 |
| 💭 哲学 | `zhexue/` | think/psi → `zhexue/psi/` | 4 |
| 🔬 科学 | `kexue/` | science/chemistry → `kexue/chemistry/`；science/physics → `kexue/physics/`；think/math → `kexue/math/` | 10 |
| ✒️ 文学 | `wenxue/` | think/classics → `wenxue/classics/` | 1 |
| 🌿 医学与养生 | `yixue/` | tcm → `yixue/tcm/`（含 guide.md/changelog.md 一并迁入）；think/{huangdi-neijing, medicine, daoyi, yangsheng, fangzhong} → `yixue/<组名>/` | 10 |
| 👥 社会科学 | `sheke/` | workplace → `sheke/workplace/`；think/{relationships, sexology} → `sheke/<组名>/` | 14 |
| 🎤 艺术 | `yishu/` | think/vocal → `yishu/vocal/` | 1 |
| ⚙️ 技术 | `jishu/` | {ai, document, build, comm, containers, ml, data, viz, rust, web, python, terminal} → `jishu/<域名>/`（原域降为组，内部结构不变） | 292 |
| 📐 规范（锚点） | `meta/` | 路径不变 | 1 |

**归属裁决说明**：
- 佛学（buddhism）→ 国学：已中国化的汉传佛教经典，按用户确认的广义国学收录
- 算学（suanxue）→ 国学；西方数学经典（think/math）→ 科学
- 黄帝阴符经（huangdi）→ 国学（道藏典籍）；黄帝内经（huangdi-neijing）→ 医学
- 房中（fangzhong）→ 医学与养生（医家性医学/养生传统，与道医、养生同域）；性学经典（sexology，现代性学著作）→ 社会科学
- Ψhē 理论（psi）→ 哲学（自指递归哲学体系）
- 声乐（vocal）→ 艺术；职场（workplace）、两性关系（relationships）→ 社会科学
- okf-spec → meta 锚点不动（库规范本体，非学科内容）

**目录命名**：学科域用拼音 kebab-case（guoxue/kexue/zhexue/wenxue/yixue/sheke/yishu/jishu），与库内既有拼音组名（daojia/daoyi/suanxue）一致；域 `index.md` 标题用中文。

## What Changes

- **物理迁移**：`git mv` 将 42 个分组移入 8 个新学科域；`think/`、`tcm/`、`workplace/`、`science/` 4 域及 12 个技术顶层域解散（技术域降为 `jishu/` 下分组）
- **新建 8 个学科域 `index.md`**（`type: group`，含学科说明与域内分组导航 + toctree）
- **删除 4 个旧域索引**：`think/index.md`、`tcm/index.md`、`workplace/index.md`、`science/index.md`（内容并入对应新学科域索引）；12 个技术域索引随目录移动成为 `jishu/` 下组索引（保留）
- **修复全部跨组链接**：根绝对链接 `](/<旧域或组>/...` → 新路径（预计 ~1700-2200 处）；相对跨组链接 `](../...` 按新层级调整（预计 ~200 处）；组内相对链接不受影响（整子树迁移）
- **重写根索引** `bundles/index.md`：学科导航（8 域 + 锚点）、生态关系概览图、推荐入门路径、toctree；frontmatter 计数更新为 363 束 / 43 组 / 9 域
- **更新 `doc/index.md`**：修正现陈旧的「297 束 / 14 域 / 37 组」为实际值
- **更新 `doc/bundles/.gitignore`**：`!build/` → `!jishu/build/`（build 移入 jishu 后保持可跟踪）
- **原子提交**：沿用上次三段式（重命名批 → 链接修复批 → 索引批），Conventional Commits 中文主题

## Impact

- **Affected specs**: [bundles-grouping-refactor](../bundles-grouping-refactor/spec.md)（本变更取代其 10 技术域顶层结构）；OKF v0.2 bundle 组织规范（`projects/awesome-okf-xs/.agents/rules/frontmatter.md` §11 交叉引用）
- **Affected code/文件**:
  - `doc/bundles/` 全部 16 个被移动域（363 束中除 meta 1 束外全部）
  - `doc/bundles/index.md`（重写）、`doc/index.md`（计数）、`doc/bundles/.gitignore`
  - 8 个新学科域 `index.md`；4 个旧域索引删除
  - 各束/组 `index.md`、`log.md` 中的跨组链接
- **不受影响**: Sphinx `conf.py`（toctree 仍指向 `bundles/index`）；束内部文档内容；`meta/` 锚点；`tasks/`、`scripts/` 门控脚本（无需改动，仅消费）
- **风险**:
  - 子模块存在并行会话写共享索引 → 遵守 add/commit 分离纪律，提交前 `git diff --cached --name-only` + `git show :<file>` 核验暂存 blob
  - `think/yangming` 等目录若有他方未暂存改动 → 绝不 add/reset 非己方文件

## ADDED Requirements

### Requirement: 学科域目录体系
系统 SHALL 在 `doc/bundles/` 下建立 8 个学科域目录，将 42 个分组物理归入对应域，映射关系如上表；`meta/` 锚点路径不变。

#### Scenario: 学科目录创建成功
- **WHEN** 执行迁移任务
- **THEN** `doc/bundles/` 顶层仅存 9 个目录（8 学科域 + meta），每个学科域含 `index.md` 与已归位的分组

#### Scenario: 学科归属唯一
- **WHEN** 检查任一束的新路径
- **THEN** 该束仅出现在一个学科域下，无重复、无遗漏（363 束总数不变）

### Requirement: 学科域索引
系统 SHALL 为每个学科域创建 `index.md`（`type: group`），含：学科定义与收录边界说明、域内分组导航表、`{toctree}` 隐藏树引用全部组索引；原 `think/`、`tcm/` 域索引中的领域描述按学科拆分并入对应新域索引。

#### Scenario: 域索引可导航
- **WHEN** 读者打开任一学科域索引
- **THEN** 可经导航表直达域内每一组，toctree 无孤立文档

### Requirement: 跨组链接修复
系统 SHALL 修复迁移引入的全部断链：
- 根绝对链接 `](/<旧路径>/...` → `](/<新路径>/...`
- 相对跨组链接按新层级调整
- 组内相对链接不修改（整子树迁移）
- `meta/` 相关引用路径不变

#### Scenario: 迁移后零断链
- **WHEN** 运行 `invoke gates.toctrees` 与全量 Markdown 链接检查
- **THEN** 0 断链、0 孤立文档

### Requirement: 索引一致性
系统 SHALL 使根索引、Sphinx 入口与磁盘一致：
- `bundles/index.md`：学科导航 + frontmatter 计数（363 束 / 43 组 / 9 域，以 `invoke gates.bundles` 重算值为准，禁止手填）
- `doc/index.md`：修正陈旧计数为实际值

#### Scenario: 计数对账通过
- **WHEN** 运行 `invoke gates.bundles`
- **THEN** frontmatter / 计数行 / 域节标题 / 分组表束数列 / toctree 五面与目录树三角一致

### Requirement: 等价性验证
系统 SHALL 验证重构等价性：
- 每束内容文档无内容变更（仅路径变化），抽样哈希核对
- `sphinx-build -b dummy -E doc _build/dummy` 无致命错误
- `invoke gates.all`（utf8 + toctrees + bundles）全绿
- `git status` 仅含预期移动/新增/修改/删除，无意外丢失

## MODIFIED Requirements

### Requirement: 根索引（bundles/index.md）
原「17 技术域导航」修改为「8 学科域 + 1 锚点导航」；生态关系概览图与推荐入门路径按学科体系重绘。

### Requirement: Sphinx 入口（doc/index.md）
原陈旧计数（297 束 / 14 域 / 37 组）修改为实际盘点值（以门控重算为准）。

### Requirement: .gitignore 例外项
`!build/` 修改为 `!jishu/build/`，确保 build 分组移入 `jishu/` 后仍被 git 跟踪（`git check-ignore` 验证）。

## REMOVED Requirements

### Requirement: 17 域技术生态顶层结构
**Reason**: 技术生态分类使人文内容杂糅于 think 巨型域，不符合学科心智模型
**Migration**: 42 分组物理移入 8 学科域；技术域降为 `jishu/` 下分组（内部结构不变）；`think/`、`tcm/`、`workplace/`、`science/` 四域索引删除，描述内容并入新学科域索引；全部跨组链接按新路径修复
