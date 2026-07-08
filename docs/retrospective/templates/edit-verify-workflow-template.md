> **来源**：从 `docs/retrospective/patterns/methodology-patterns/ai-collaboration/edit-verify-separation.md` 十、警示四条血的教训 提炼
> **更新**：2026-07-08 初版创建，整合数据漂移检查清单（data-drift-checklist.md）与四条元层教训；补全frontmatter+TOML双星同步完整示例，新增第12项递归自举验证检查项；frontmatter/TOML示例替换为edit-verify-separation模式实际值，补充路径计算规则和fix-x-toml-ref.py自动修复工具说明

# 编辑-验证分离工作流模板

> **适用场景**：任何文档编辑/重构/原子化/归档/模式化操作，尤其是AI辅助的结构化编辑。
>
> **核心口诀**：编辑完，停一下，跑脚本，数一遍。对模式文件也一样。

```markdown
# 编辑-验证分离执行记录

**任务名称**：{填写任务名称，如"XX复盘报告原子化"}
**编辑对象**：{填写编辑的文件/目录，如"docs/retrospective/reports/xxx/"}
**操作类型**：{拆分/重组/格式调整/模式归档/资产更新/其他}
**执行日期**：{YYYY-MM-DD}

---

## 阶段一：编辑操作（Edit Phase）

**目标**：完成结构性变更，不修改任何数字、事实陈述、技术描述。

### 编辑操作清单

- [ ] 按{原子化拆分/重组目标}完成文档结构变更
- [ ] 更新所有内部链接和交叉引用
- [ ] 保持frontmatter完整性（id/title/source/tags/status等字段）
- [ ] 调整章节编号保持连续性
- [ ] 同步更新README/索引文件的文件清单
- [ ] 编辑过程中不修改任何量化数据（数字保持原样进入验证阶段）

### 编辑阶段完成自检

- [ ] 结构符合目标（拆分/重组/格式调整完成）
- [ ] 运行链接检查（check-links.py），无断链
- [ ] 格式规范（frontmatter完整、标题层级正确）
- [ ] 无明显内容丢失（对比前后行数和关键段落）

> **🔔 阶段切换声明**：结构编辑已完成，即将进入内容验证阶段。
> （思维模式从"结构化转换"切换到"批判性审查"）

---

## 阶段二：内容验证（Verify Phase）

**目标**：系统性审查文档内容准确性，发现并修正数据漂移、事实错误和逻辑矛盾。

### Step 1：量化数据提取

- [ ] 全文扫描所有量化数据（行数、数量、比例、百分比、时间、版本号）
- [ ] 记录每个数字的文件名、行号、上下文
- [ ] 分类标记：源代码行数 / 测试数量 / 文件数量 / 时间跨度 / 比例百分比 / 合计总计

### Step 2：溯源核对（四查法）

| 验证项 | 方法 | 结果 |
|--------|------|------|
| 常量/配置值 | 读取源文件验证 | □ 通过 □ 修正：____ |
| 代码规模（行数） | `Get-ChildItem ... | Measure-Object -Line` 实时统计 | □ 通过 □ 修正：____ |
| 测试用例数量 | `Select-String -Pattern "def test_" | Measure-Object` 实时计数 | □ 通过 □ 修正：____ |
| 其他量化数据 | 对应脚本/命令实时获取 | □ 通过 □ 修正：____ |

**⚠️ 特别提醒**：不要信任来源文档中的任何数字——包括你正在引用的洞察文档、模式文件、上次的复盘报告。所有数字必须实时获取。

### Step 3：计算验证

- [ ] **合计验证**：所有"合计/总计/小计"重新独立计算（分项相加），对比文档值
  - 分项1：{name} = {value}
  - 分项2：{name} = {value}
  - 分项3：{name} = {value}
  - 计算合计：{sum} = {v1}+{v2}+{v3} = {calculated}
  - 文档合计：{document_value} → □ 一致 □ 修正为{calculated}
- [ ] **比例验证**：百分比/占比重新计算（分子÷分母）
- [ ] **单位一致性**：检查数字单位是否统一
- [ ] **合理性检查**：负数、不可能值、比例失调标记审查

### Step 4：跨文档一致性交叉检查

- [ ] 全文搜索每个关键指标的所有出现位置，检查值是否一致
- [ ] README/索引文件中的数字与正文同步
- [ ] frontmatter中的统计数字与正文一致
- [ ] 同一任务的多个文档（复盘报告/洞察文档/README/模式文件）数字全部统一

### Step 5：可复用资产额外验证（如编辑对象具有放大效应）

> **触发条件**：如果编辑对象属于以下任何一类，**必须**执行本步骤额外验证：
>
> | 资产类型 | 典型路径 | 放大效应 |
> |---------|---------|---------|
> | 模式文件 | `patterns/**/*.md` | 错误被所有引用该模式的下游文档复制 |
> | 检查清单 | `assets/*checklist*.md`、`templates/*checklist*` | 案例数字每次使用时被看到、被引用 |
> | 模板文件 | `templates/*.md` | 示例数据被复制到每个套用模板的新文档 |
> | 脚本/工具 | `.agents/scripts/*.py` 等 | 硬编码常量/阈值/默认路径错误影响每次执行结果 |
> | 资产清单/索引 | `assets/asset-inventory.md`、各目录`README.md` | 统计数字（模式数量、成熟度分布）成为他人引用依据 |
> | 规范/规则文件 | `.agents/**/*.md`、`AGENTS.md` | 量化规则（如"覆盖率≥80%"）被当成硬性标准执行 |
> | 导航/路由文件 | `.agents/context-routing.md`等 | 统计/列表信息被作为入口索引使用 |
> | **TOML元数据文件** | `.meta/toml/**/*.toml` | 自动化工具（pattern-maturity.py等）依赖元数据统计模式成熟度，字段错误导致统计失真 |
>
> **核心判断原则**：如果这份文档会被其他人**引用、复制、当作基准、套用模板、自动解析**，它就是可复用资产，必须额外验证。**不确定时，按"是"处理。**

> ⚠️ **灭火者自带火种**：创建/更新"防止错误"的文档时，你的思维模式是"搬运正确方法"而非"审查内容对错"——这恰恰是数据漂移的温床。
>
> 🪤 **典型陷阱**：frontmatter是结构化数据，不是"格式细节"。正文更新了L2但frontmatter的maturity还停留在L1——这种漂移人眼几乎看不到，自动化工具读到的是错误值。（2026-07-08 edit-verify-separation.md 实际踩坑案例）

- [ ] **分类确认**：本编辑对象属于上述哪类（可多选）：□ 模式 □ 检查清单 □ 模板 □ 脚本 □ 索引/清单 □ 规范 □ 导航 □ TOML元数据 → 如有勾选，继续以下检查
- [ ] **frontmatter完整性验证**（如编辑Markdown资产文件）：
  - [ ] 必填字段齐全：`id`、`title`、`source`、`maturity`
  - [ ] 模式文件额外字段：`x-toml-ref`（指向对应TOML文件）、`validation_count`、`reuse_count`、`related_patterns`
  - [ ] **frontmatter与正文一致性**：maturity/title等字段与正文描述一致（如正文写L2，frontmatter不能是L1）
  - [ ] source字段路径正确且可访问

  **frontmatter完整示例**（edit-verify-separation.md 实际frontmatter）：

      ---
      id: "edit-verify-separation"
      title: "编辑-验证分离模式"
      source: "docs/retrospective/reports/task-reports/retrospective-concurrent-report-atomization-20260708/insight-extraction.md#洞察3"
      x-toml-ref: "../../../../../.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/edit-verify-separation.toml"
      maturity: "L2"
      validation_count: 3
      reuse_count: 0
      related_patterns:
        - "data-validation-four-checks"
        - "source-anchor-verification-protocol"
        - "batched-creation-independent-review"
      tags: ["ai-collaboration", "quality-assurance", "workflow", "verification", "edit-verify"]
      ---

  > **x-toml-ref路径计算规则**：从md文件所在目录回到项目根需要N层`../`，然后加上`.meta/toml/`加上md文件相对于项目根的路径（扩展名改为.toml）。
  > 例如：`docs/retrospective/patterns/methodology-patterns/ai-collaboration/xxx.md` → 5层目录 → `../../../../../` + `.meta/toml/docs/retrospective/patterns/methodology-patterns/ai-collaboration/xxx.toml`
  >
  > **💡 自动修复**：忘记添加或路径写错时，运行以下命令自动修复并创建缺失TOML：
  > ```bash
  > python .agents/scripts/fix-x-toml-ref.py --dir <目标目录> --write --create-toml
  > ```

- [ ] **TOML元数据同步**（如编辑模式文件）：
  - [ ] 对应`.meta/toml/`路径下存在同名TOML文件
  - [ ] TOML文件中`id`与frontmatter完全一致（唯一标识符，必须匹配）
  - [ ] TOML文件中`title`/`category`/`date`/`version`字段完整
  - [ ] 新建模式时同步创建TOML文件（不要留空）
  - [ ] `reuse_count`/`validation_count`如有更新需同步两边

  **TOML双星同步示例**（与上述frontmatter配对的实际TOML文件）：

      id = "edit-verify-separation"
      title = "编辑-验证分离模式"
      category = "retrospective/patterns/methodology-patterns/ai-collaboration"
      date = "2026-07-08"
      version = "1.2"

  > **💡 双星同步原则**：模式文件frontmatter与TOML元数据文件是"双星系统"——必须同步创建/更新。`id`是唯一标识符必须完全一致；`x-toml-ref`是连接两者的轨道。CI中的版本涟漪检测器（check-version-ripple.py）会自动检测：①x-toml-ref指向不存在的文件（error级）；②id不一致（error级）。

- [ ] **数字溯源到原始来源**：所有示例数字追溯到**最原始数据源**（源代码/原始复盘报告）核对，禁止从中间文档（洞察文档、其他模式）直接复制
- [ ] **计算独立重算**：合计/百分比/比例重新独立计算，不信任任何来源文档的计算结果
- [ ] **跨资产一致性**：同一案例/数据出现在多个可复用资产中时，全部对齐（如同一案例在模式A和模式B中数字一致）
- [ ] **脚本常量验证**（如编辑脚本）：检查脚本中的硬编码路径、阈值、默认值、正则模式是否与当前项目实际一致
- [ ] **索引统计验证**（如编辑清单/索引/README）：统计数字（数量、成熟度分布、合计）通过脚本重新生成或手动逐项核对
- [ ] **规范数值验证**（如编辑规范）：规则中的量化阈值（覆盖率、行数限制、时间要求）确认是否仍适用当前项目状态
- [ ] **元层自查**：已确认本资产文件中的所有示例数据/常量/统计/frontmatter字段已通过验证阶段——生产防错工具的操作本身也是编辑操作
- [ ] **案例日期标注**：验证案例中的数据标注获取日期：{YYYY-MM-DD}（代码会演进，数字会过时）
- [ ] **递归自举验证**（如编辑检查脚本/验证规则）：新创建或修改的验证规则/检查脚本必须先应用于自身，验证通过后方可合入。运行`python .agents/scripts/check-version-ripple.py --bootstrap`可执行自举验证（权威值一致性+其他脚本旧版引用扫描）

---

## 验证问题报告

| 级别 | 位置 | 问题描述 | 修正后的值 | 修正状态 |
|------|------|---------|-----------|---------|
| 🔴 Error | {file:line} | {描述，如"visitor行数465与代码实际840不符"} | 840行 | □ 已修正 |
| 🔴 Error | | | | □ 已修正 |
| 🟡 Warning | | {可疑值/无法自动验证} | | □ 需人工确认 |
| 🔵 Info | | {一致性问题/建议更新} | | □ 已修正 |

**数据漂移统计**：共发现 {N} 处数据漂移，其中 Error {E} 处，Warning {W} 处，Info {I} 处。

---

## 最终验证确认

- [ ] Step 1-4 全部检查项通过
- [ ] 如涉及模式/资产编辑，Step 5 全部检查项通过
- [ ] 所有🔴 Error和🟡 Warning已修正或确认
- [ ] 跨文档数字一致（复盘报告、洞察文档、README、模式文件统一）
- [ ] 重新运行链接检查（check-links.py），无断链
- [ ] 关键功能描述/事实陈述与源代码一致

### 用户确认（重要文档必填）

> "已完成AI主动验证，{N}处数据漂移已修正，核心数据已与源代码核对（{核心指标1}={value1}, {核心指标2}={value2}, 合计={sum}），请确认关键结论是否准确。"

用户确认：□ 确认通过 □ 需要进一步调整：{说明}

---

## ⚠️ 四条血的教训（每次编辑前必读）

1. **次要文件不次要** —— 钩子脚本、配置文件、工具类等"配角"经常被漏统计。漏一个200行的文件，合计数就偏差200。统计必须全量枚举。

2. **双重错误最难防** —— 分项错+加法错形成"错上加错"的自洽假象（如1893+600=2493≠2565）。永远不信任来源合计数，必须重新独立计算。

3. **🚨 灭火者自带火种** —— 创建"防止数据漂移"的模式/检查清单时，你的思维是"搬运正确方法"而非"审查内容对错"，这正是漂移温床。验证是普适的，没有例外区。

4. **"看起来合理"最危险** —— 465行对一个visitor完全合理，但实际是840行。合理性关闭审查本能。数字对不对靠脚本不靠感觉。只要没被实时命令验证过，它就是可疑的。

---

## 关联资源

| 资源 | 说明 |
|------|------|
| 编辑-验证分离模式 | `patterns/methodology-patterns/ai-collaboration/edit-verify-separation.md` |
| 量化数据验证四查法 | `patterns/methodology-patterns/governance-strategy/data-validation-four-checks.md` |
| 数据漂移检查清单 | `assets/data-drift-checklist.md`（含9处典型漂移案例库） |
| checklist模板 | `templates/checklist-template.md` |
```

> **关联模块**：
> - `patterns/methodology-patterns/ai-collaboration/edit-verify-separation.md`（本模板的模式来源）
> - `patterns/methodology-patterns/governance-strategy/data-validation-four-checks.md`（验证阶段核心方法）
> - `assets/data-drift-checklist.md`（配套检查清单+案例库）
> - `templates/checklist-template.md`（通用检查清单模板）
