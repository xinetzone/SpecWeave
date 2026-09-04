---
name: math-east-west-dialogue-okf-wiki-spec
version: 1.0.0
created: 2026-09-01
source: "国内外数学经典公共领域原文与公开学术信源（Project Gutenberg / Internet Archive / ctext.org / MacTutor / Clay Mathematics Institute / Gallica / Euler Archive 等，经 Web 调研实际验证）"
methodology: seven-concepts 场景4（知识沉淀）R→I→E→V→C
content-sensitivity: Public（数学经典原文多属公共领域，解读为公开学术知识）
target-repo: projects/awesome-okf-xs（git submodule，用户明确指定在其内生成）
---

# 中西数学对读 OKF Wiki 教程 — 产品需求文档

## Overview

- **Summary**：在 `projects/awesome-okf-xs/doc/bundles/kexue/math/` 分组下新建 `east-west-dialogue`（中西数学对读）知识包，系统调研与整理中国算学传统与西方数学传统在关键思想节点上的**平行发展、独立贡献、接触交流与互鉴融合**，以 OKF v0.2 规范组织为中文 wiki 教程。
- **Purpose**：库内已有 `kexue/math/classics-reading`（国外数学经典，欧几里得→布尔巴基）与 `guoxue/suanxue/suanjing-reading`（中国算经，《九章》→宋元→明清）两个独立知识包，但缺乏将两大传统**置于同一视角对读**的整合教程。本知识包不重复已有内容，而以「比较—交流—互鉴」为主线，回答：中西数学在哪些思想节点上平行抵达？哪些路径分歧？何时接触？怎样互鉴？读者如何利用中西对读加深理解？
- **Target Users**：
  - 已读或计划读既有两束、希望从比较视角获得更深理解的读者；
  - 对数学史比较研究（Needham 问题、文化数学观）感兴趣的跨学科读者；
  - 需要可信信源索引与教学路径的教育者、内容创作者。

## Goals

- 在 `kexue/math/east-west-dialogue/` 建立符合 OKF v0.2 的完整知识包：`concepts/`（概念与对读解读）、`examples/`（对读示范与比较分析）、`references/`（信源登记簿）三层结构 + `facts.md`（R 阶段事实）+ `insights.md`（I 阶段洞察）+ `log.md`。
- 全景覆盖六大对读主题：① 几何与度量（《几何原本》vs《九章·方田》《周髀》勾股）② 数论与代数（丢番图 vs 《九章·方程》/大衍求一）③ 极限与无穷小（阿基米德穷竭法 vs 刘徽割圆术）④ 符号化与抽象（花剌子米代数 vs 天元术/四元术）⑤ 公理化与算法化（欧氏演绎 vs 中国算法传统）⑥ 接触与互鉴（《几何原本》汉译、李善兰-伟烈亚力合作、现代中国数学国际化）。
- 每个对读主题提供四层结构：**西方节点**（著作/人物/思想，链 classics-reading）→ **中国平行**（著作/人物/思想，链 suanjing-reading）→ **比较分析**（路径差异、优先权、思想特征）→ **对读示范**（同一问题在两种传统中的解法对照）。
- 提供可操作的阅读方法论：中西数学对读的入门路径、比较阅读策略、跨传统阅读计划、代表性命题的双向解读示范。
- 遵循 seven-concepts 场景4 链路：R（事实采集，信源全部经实际访问验证）→ I（洞察，四元组）→ E（萃取 ≥2 个可迁移比较阅读模式）→ V（对抗审查）→ C（原子提交建议，提交前经用户确认）。

## Non-Goals

- **不重复既有两束内容**：本知识包是「比较视角的整合层」，不复制 classics-reading 或 suanjing-reading 的单传统解读正文，而是以相对链接指向它们。
- **不覆盖 20 世纪中叶以后的现代数学**（如格罗滕迪克以后、华罗庚-陈省身等现代中国数学家），聚焦"古典—近代"对读谱系。
- **不做数学百科/定理大全**：对读服务于"理解思想差异与交流"这一主线，不替代系统教科书。
- **不大段复制原著原文**：仅收录少量公共领域代表性命题/段落选段用于对读示范。
- **不自动执行 git commit**：文件与验证完成后，原子提交需用户明确确认。
- **不修改 OKF 规范本体**（meta/okf-spec）与既有知识包内容（仅更新导航索引）。
- **不修改子项目构建配置**（doc/conf.py）与 .agents/ 规范。

## Background & Context

- OKF bundles 采用「技术域 → 分组 → 知识包」三级结构。`kexue/`（科学）域现有 `chemistry/`（7 束中西双线索）、`physics/`（2 束中西双线索）、`math/`（1 束国外经典）三个分组，中西对读是 chemistry 与 physics 的既定范式。
- 总索引导航已预告「跨学科读者：国学/算学 ↔ 科学/数学 中西数学对读」，本知识包兑现这一承诺。
- `kexue/math/classics-reading`（国外经典，14 concepts + 3 examples + 4 references）与 `guoxue/suanxue/suanjing-reading`（中国算经，14 concepts + 8 examples + 4 references）已完整交付，是本知识包的直接信源与链接对象。
- `kexue/chemistry` 的中西双线索组织方式（西方四元典 + 中国三典籍，对读结构）是本任务的直接范式。
- OKF v0.2 合规三要件：① 每个非保留 `.md` 含可解析 YAML frontmatter 且有非空 `type`；② 保留文件（index.md/log.md）遵循结构；③ bundle 根 index.md 可含 `okf_version: "0.2"`。
- 子项目工具链：在 `projects/awesome-okf-xs/` 下运行 `invoke build`（Sphinx 构建，须 0 警告 0 错误）与 `invoke gates.all`（UTF-8 + toctree 完整性 + bundles 计数对账）。
- 文档工程已启用 `dollarmath`/`amsmath`（支持 `$...$`、`$$...$$` LaTeX 公式）与 mermaid 围栏图。

## Functional Requirements

- **FR-1（知识包结构）**：新建 `doc/bundles/kexue/math/east-west-dialogue/` 知识包目录，含 bundle 根 `index.md`（含 `okf_version: "0.2"`）、`log.md`、`facts.md`、`insights.md`，及 `concepts/`、`examples/`、`references/` 三个子目录（各含 `index.md`）。
- **FR-2（对读方法论概念）**：concepts/ 包含 ≥3 篇方法论概念文档，覆盖：为什么做中西数学对读（价值与方法论）、比较阅读策略（如何同时利用两束既有内容）、跨传统阅读路径设计。
- **FR-3（六大对读主题概念）**：concepts/ 包含 6 篇对读主题概念文档：① 几何与度量对读 ② 数论与代数对读 ③ 极限与无穷小对读 ④ 符号化与抽象对读 ⑤ 公理化与算法化对读 ⑥ 接触与互鉴对读。每篇含四层结构（西方节点→中国平行→比较分析→对读示范指引），大量使用相对链接指向 classics-reading 与 suanjing-reading 对应文档。
- **FR-4（对读示范）**：examples/ 包含 ≥3 篇：① 勾股定理中西双源对读（《几何原本》I.47 vs《周髀算经》勾股术）② 线性方程组对读（《九章·方程》vs 高斯消元/莱布尼茨）③ 极限思想对读（阿基米德穷竭法 vs 刘徽割圆术）。每篇含原文选段（公共领域）、双方解法逐步对照、现代数学语言统一解读、差异分析。
- **FR-5（信源登记簿）**：references/ 包含 ≥3 篇信源登记：① 中西原文与译本联合信源（整合两既有 references 并补充比较研究专用信源）② 比较研究与数学史著作（Needham SCC vol.3、Martzloff、Chemla、吴文俊、林力娜等）③ 与库内知识包交叉引用（链 classics-reading、suanjing-reading、psi-math、3b1b、katex、sympy）。
- **FR-6（R 阶段事实库）**：facts.md 登记 ≥30 条零推测事实（对读关键事实：双方年代、人物、著作、优先权节点、交流事件年份等），每条可归因到 references 信源；事实陈述无因果推断词（G1）。
- **FR-7（I 阶段洞察与 E 阶段模式）**：insights.md 包含 ≥4 条四元组洞察（现象+根因+影响+建议，G2）；知识包内含 ≥2 个可迁移比较阅读模式（触发条件+核心步骤+反模式+迁移示例，G3），如"同题双源对读法""思想路径分岔图法"。
- **FR-8（导航更新）**：更新 `kexue/math/index.md`（新增 east-west-dialogue 知识包行 + toctree 条目 + 束数 1→2）、`bundles/index.md`（kexue 域统计 2 束→3 束；math 分组描述更新；总束数 378→379）。
- **FR-9（frontmatter 合规）**：每个概念/示例/信源文档 frontmatter 含 `type`（必填）、`title`、`description`、`tags`、`sources`（信源归因）、`generated`/`verified`（actor 约定）、`status: draft`、`stale_after`；`generated.by` 使用 `agent:seven-concepts-cmd` 或等价生产者标识。
- **FR-10（交叉链接网络）**：与库内相关知识包建立密集相对链接：classics-reading（每篇对读主题链向对应西方概念）、suanjing-reading（每篇对读主题链向对应中国概念）、viz/3b1b、zhexue/psi/psi-math、document/katex、data/pydata/sympy 等。

## Non-Functional Requirements

- **NFR-1（构建质量）**：在 `projects/awesome-okf-xs/` 下 `invoke clean && invoke build` 必须 0 错误 0 警告；`invoke gates.all` 全部通过（UTF-8 无 BOM、toctree 无断链无孤立文档、bundles 计数对账一致）。
- **NFR-2（信源可信）**：references 中登记的外部 URL 必须在调研中实际访问验证（HTTP 可达且内容匹配），不可凭记忆编造；不可验证的 URL 不得写入。
- **NFR-3（事实准确）**：所有年代、作者、书名、优先权、交流事件信息与权威信源一致；对抗审查（V）阶段对事实性陈述逐条证伪，遗留错误数为 0。
- **NFR-4（语言与命名）**：正文为规范现代汉语；文件名 kebab-case 纯英文无中文；Markdown 交叉引用一律相对路径，禁止 `file:///` 绝对路径。
- **NFR-5（数学表达兼容）**：数学符号以 Unicode 与 LaTeX（`$...$`）为主，复杂公式用代码块或文字展开；不依赖未启用的 Sphinx 数学扩展，以构建 0 警告为硬约束。
- **NFR-6（原子化交付）**：文档遵循单一职责（一篇一主题），行动项/提交满足原子化（G4）：单一职责、可独立验证。
- **NFR-7（不重复原则）**：本知识包正文不复制既有两束内容，比较分析以链接+概括+差异聚焦为主，避免信息冗余。

## Constraints

- **Technical**：产出物位于 git submodule `projects/awesome-okf-xs/` 内（第一方子项目，允许子模块内开发）；使用该子项目自身工具链（`invoke build`/`invoke gates.*`，工作目录需在子项目根）；遵循子项目 AGENTS.md 与 frontmatter 规范；Sphinx/myst_parser 构建约束（裸日期由 conf.py 钩子自动加引号，无需手工处理）。
- **Business**：公共领域/公开信源内容（Public），标准工作流；Spec 产物位于主权区 `.trae/specs/classics-knowledge/math-east-west-dialogue-okf-wiki/`，最终知识包位于子项目 `doc/bundles/kexue/math/`。
- **Dependencies**：网络调研能力（WebSearch/WebFetch）可用；`projects/awesome-okf-xs/` 子模块已初始化（已确认可读）；`invoke` 命令可用；既有 classics-reading 与 suanjing-reading 两束已完整交付（已确认可链接）。
- **合规**：古籍原文与国外公共领域经典均为公共领域；现代研究仅作信源登记与事实引用，不大段摘录受版权保护的译文。

## Assumptions

- 读者已读或可同时参考 classics-reading 与 suanjing-reading 两束既有内容，本知识包是「比较整合层」而非入门层。
- 「中西数学对读」聚焦古典—近代谱系（古希腊—中国先秦至明清—欧洲近代），不覆盖 20 世纪中叶后现代数学。
- 公共领域数字信源（Gutenberg、Internet Archive、Gallica、Euler Archive、ctext.org、MacTutor 等）在调研时点稳定可达；若个别 URL 失效，以同文献的替代权威馆藏登记。
- 知识包初版 `status: draft`（未经人工独立核验），与既有知识包做法一致。

## Acceptance Criteria

### AC-1: 知识包目录结构与位置（rule）
- **Given**：任务完成
- **When**：检查 `projects/awesome-okf-xs/doc/bundles/kexue/math/east-west-dialogue/`
- **Then**：存在 `index.md`（bundle 根）、`log.md`、`facts.md`、`insights.md`，及 `concepts/`、`examples/`、`references/` 三个子目录且各含 `index.md`；concepts 文档 ≥9 篇（3 方法论 + 6 对读主题）、examples ≥3 篇、references ≥3 篇。
- **Pass Condition**：目录与文件全部存在，数量满足下限。
- **Evidence**：目录列表（LS/Glob）与文件计数。

### AC-2: OKF v0.2 frontmatter 合规（rule）
- **Given**：知识包内全部 Markdown 文件
- **When**：检查 frontmatter
- **Then**：每个非保留 `.md` 含可解析 YAML frontmatter 且 `type` 非空；bundle 根 `index.md` 含 `okf_version: "0.2"`；概念/示例/信源文档含 `title`/`description`/`tags`/`sources`/`generated`/`status`/`stale_after` 字段；`index.md`/`log.md` 遵循保留文件结构。
- **Pass Condition**：逐文件检查全部满足；无 `file:///` 链接。
- **Evidence**：frontmatter 抽查记录 + grep 检查结果。

### AC-3: 导航与 toctree 完整性（rule）
- **Given**：知识包创建并更新导航
- **When**：运行 `invoke gates.toctrees` 与 `invoke gates.bundles`（工作目录 `projects/awesome-okf-xs`）
- **Then**：无断链、无孤立文档、bundle 根 index 完整；`kexue/math/index.md` 含 east-west-dialogue 导航行与 toctree 条目；`bundles/index.md` 的 kexue 域统计与总数更新一致（math 分组 2 束；总计 379 束）。
- **Pass Condition**：两条 gates 命令退出码 0 且输出 0 broken；索引统计数字一致。
- **Evidence**：invoke 命令输出 + 索引文件 diff。

### AC-4: Sphinx 构建与质量门通过（rule）
- **Given**：全部文档完成
- **When**：运行 `invoke clean && invoke build` 与 `invoke gates.all`
- **Then**：构建 0 错误 0 警告；UTF-8 检查通过；bundles 计数对账通过。
- **Pass Condition**：两条命令均成功退出，输出无 warning/error。
- **Evidence**：命令输出日志。

### AC-5: 信源真实可达与事实可溯（rule）
- **Given**：references/ 登记的外部信源与 facts.md 事实
- **When**：抽样实际访问外部 URL 并核对 facts 归因
- **Then**：references 中登记的外部 URL 100% 经调研访问验证；facts.md ≥30 条事实每条可归因到信源 id，无无来源事实；无凭记忆编造的 URL 或书目信息。
- **Pass Condition**：外部 URL 验证记录完整；facts 条目 100% 有信源归因。
- **Evidence**：facts.md 信源 id 映射 + Web 调研记录。

### AC-6: 六大对读主题覆盖与四层结构（rule）
- **Given**：concepts/ 对读主题文档
- **When**：核对覆盖矩阵
- **Then**：六大主题（几何度量/数论代数/极限无穷小/符号化抽象/公理化算法化/接触互鉴）均有专文；每篇含四层结构（西方节点→中国平行→比较分析→对读示范指引）；西方节点链向 classics-reading 对应文档、中国平行链向 suanjing-reading 对应文档。
- **Pass Condition**：覆盖矩阵逐主题勾选无缺项；每篇四层结构完整；交叉链接全部为相对路径且可达。
- **Evidence**：覆盖矩阵（insights.md 附）+ 文档内容核对 + 链接抽查。

### AC-7: 不重复既有内容（rule）
- **Given**：本知识包全部正文
- **When**：与 classics-reading 和 suanjing-reading 比对
- **Then**：本知识包不复制两既有束的单传统解读正文段落；比较分析以链接+概括+差异聚焦为主；每处引用既有内容处有相对链接指向源文档。
- **Pass Condition**：无整段复制；交叉链接覆盖率 ≥80%（每篇至少 2 条指向既有束）。
- **Evidence**：文档比对 + 链接统计。

### AC-8: 对读示范质量（rubric）
- **Dimension**：对读示范的数学准确性与比较深度——双方解法是否逐步对照、现代数学统一解读是否准确、差异分析是否有洞察。
- **Scale**: 1-5
- **Anchors**：1 = 仅罗列双方解法无对照；3 = 有对照但差异分析浅；5 = 逐步对照精确、现代统一解读准确、差异分析揭示思想特征。
- **Pass Threshold**：≥ 4
- **Evidence**：examples/ 对读示范文档（V 阶段评审评分）。

### AC-9: 比较分析洞察力（rubric）
- **Dimension**：六大对读主题的比较分析是否讲清"路径差异、优先权、思想特征"，而非简单并置。
- **Scale**: 1-5
- **Anchors**：1 = 仅并置双方事实无分析；3 = 有比较但泛泛；5 = 路径差异分析深刻、有思想史洞见、能指导读者理解数学多样性。
- **Pass Threshold**：≥ 4
- **Evidence**：concepts/ 六大对读主题文档（V 阶段评审评分）。

### AC-10: 方法论闭环质量（rubric）
- **Dimension**：seven-concepts 链路产物质量——facts 零因果词（G1）、insights 四元组完整（G2）、模式可迁移（G3：触发条件+步骤+反模式+迁移示例）。
- **Scale**: 1-5
- **Anchors**：1 = facts/insights 缺失或模式无反模式；3 = 形式齐全但模式泛化不可迁移；5 = G1/G2/G3 全过，≥2 个模式可直接迁移到其他学科对读场景。
- **Pass Threshold**：≥ 4
- **Evidence**：facts.md、insights.md 与模式章节（V 阶段评审评分）。

## Open Questions

- [x] 覆盖范围：已确认——六大对读主题，古典—近代谱系。
- [x] 教程形态：已确认——比较视角的整合层，不重复既有两束。
- [x] 产出位置：已确认——`kexue/math/east-west-dialogue/`，与 classics-reading 同分组。
- [ ] 知识包完成并通过验证后，是否执行原子提交（C 阶段）？默认**不自动提交**，待用户确认提交信息后执行。
