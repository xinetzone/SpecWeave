---
id: "data-drift-checklist"
title: "数据漂移检查清单（归档/模式化专用）"
source: "../reports/task-reports/retrospective-concurrent-report-atomization-20260708/insight-extraction.md"
x-toml-ref: "../../../../.meta/toml/.agents/docs/retrospective/assets/data-drift-checklist.toml"
maturity: "L2"
tags: ["governance", "data-validation", "checklist", "data-drift", "verification", "archiving"]
related_patterns:
  -   - "../patterns/methodology-patterns/governance-strategy/data-validation-four-checks.md"
  -   - "../patterns/methodology-patterns/ai-collaboration/edit-verify-separation.md"
---
# 数据漂移检查清单（归档/模式化专用）

> **适用场景**：复盘报告归档、洞察模式化、模式库更新、资产清单同步等任何涉及文档编辑和数据搬运的操作完成后。
>
> **核心警示**：模式文件和归档文档不是数据漂移的免疫区——搬运数据时必须重新验证。

---

## 一、检查流程总览

```
提取数字 → 溯源核对 → 计算验证 → 一致性交叉检查 → 模式/资产额外验证
   ↓           ↓           ↓            ↓                 ↓
 Step 1      Step 2      Step 3       Step 4            Step 5
```

---

## 二、标准检查项

### Step 1：量化数据提取

- [ ] **全文扫描数字**：提取文档中所有量化数据（行数、数量、比例、百分比、时间、版本号）
- [ ] **标记数字位置**：记录每个数字所在的文件名、行号、上下文
- [ ] **分类数据类型**：区分「源代码行数」「测试数量」「文件数量」「时间跨度」「比例/百分比」「合计/总计」

### Step 2：溯源核对（四查法）

- [ ] **查常量定义**：数字若来自常量/配置，直接读取源文件验证
- [ ] **查核心实现**：数字若描述代码规模，用 `wc -l`（PowerShell: `Get-Content | Measure-Object -Line`）实时统计
- [ ] **查测试用例**：测试数量用搜索计数（如 `grep -c "def test_"`）实时统计，不信文档中的数字
- [ ] **查量化数据**：所有数字必须通过脚本/命令实时获取，禁止信任来源文档中的数字

### Step 3：计算验证

- [ ] **合计验证**：所有"合计""总计""小计"数字，必须重新独立计算（分项相加），不能信任来源文档的加法结果
- [ ] **比例验证**：百分比/占比必须重新计算（分子÷分母），不能信任来源文档的比例
- [ ] **单位一致性**：检查数字单位是否统一（行数vs文件数、秒vs分钟）
- [ ] **合理性检查**：负数、不可能值（如行数超过文件大小）、比例失调（如测试数是代码数的10倍）需标记审查

### Step 4：跨文档一致性交叉检查

- [ ] **同指标全文档搜索**：对每个关键指标，全文搜索所有文档中出现的位置，检查值是否一致
- [ ] **README/索引同步**：如果正文中的数字已更新，检查README和索引文件是否同步更新
- [ ] **frontmatter同步**：检查文档frontmatter中的统计数字是否与正文一致
- [ ] **跨报告一致性**：同一任务的多个文档（复盘报告、洞察文档、README、模式文件）中的数字必须全部统一

### Step 5：可复用资产额外验证（本清单的核心增强项）

> **触发条件**：如果编辑对象属于以下8类中的任何一类，**必须**执行本步骤：
>
> | 资产类型 | 典型路径 | 放大效应 |
> |---------|---------|---------|
> | 模式文件 | `patterns/**/*.md` | 错误被引用该模式的下游文档复制 |
> | 检查清单 | `assets/*checklist*.md`、`templates/*checklist*` | 案例数字每次使用时成为错误示范 |
> | 模板文件 | `templates/*.md` | 示例数据被复制到每个套用模板的新文档 |
> | 脚本/工具 | `.agents/scripts/*.py` 等 | 硬编码常量/阈值错误影响每次执行 |
> | 资产清单/索引 | `assets/asset-inventory.md`、各目录`README.md` | 统计数字成为他人引用依据 |
> | 规范/规则文件 | `.agents/**/*.md`、`AGENTS.md` | 量化阈值被当成硬性标准执行 |
> | 导航/路由文件 | `.agents/context-routing.md`等 | 入口信息作为智能体启动上下文 |
> | **TOML元数据文件** | `.meta/toml/**/*.toml` | 自动化工具依赖元数据统计成熟度，字段错误导致统计失真 |
>
> **判断原则**：文档会被引用/复制/当作基准/套用/自动解析 → 是可复用资产。不确定时，按"是"处理。
>
> 🪤 **隐蔽陷阱**：frontmatter是结构化数据，不是"格式细节"。正文L2但frontmatter maturity=L1——人眼几乎看不到，工具读到的是错误值。（2026-07-08实际踩坑案例）

- [ ] **分类确认**：编辑对象属于上述哪类（可多选）：□ 模式 □ 检查清单 □ 模板 □ 脚本 □ 索引/清单 □ 规范 □ 导航 □ TOML元数据 → 如有勾选，继续
- [ ] **frontmatter完整性验证**（Markdown资产文件必查）：
  - [ ] 必填字段：`id`、`title`、`source`、`maturity` 齐全
  - [ ] 模式文件额外字段：`x-toml-ref`、`validation_count`、`reuse_count`、`related_patterns` 齐全
  - [ ] **frontmatter与正文一致性**：maturity/title等字段与正文描述一致（正文写L2，frontmatter不能是L1）
  - [ ] source字段路径正确且可访问
- [ ] **TOML元数据同步**（模式文件必查）：
  - [ ] 对应`.meta/toml/`路径下存在同名TOML文件
  - [ ] TOML文件中`id`/`title`/`category`/`date`与frontmatter一致
  - [ ] 新建模式时同步创建TOML文件（不要留空）
- [ ] **数字溯源到原始来源**：所有示例数字/常量追溯到**最原始数据源**（源代码/原始复盘报告），禁止从中间文档（洞察文档、其他模式）直接复制
- [ ] **计算独立重算**：合计/百分比/统计值必须**重新独立计算**，不能信任来源文档的计算结果
- [ ] **跨资产一致性**：同一案例/数据出现在多个可复用资产中时，全部对齐
- [ ] **脚本常量验证**（脚本类）：硬编码路径、阈值、默认值、正则模式与当前项目一致
- [ ] **索引统计验证**（清单/索引/README类）：数量、成熟度分布、合计通过脚本重新生成或逐项核对
- [ ] **规范数值验证**（规范类）：量化阈值（覆盖率、行数限制等）确认仍适用当前项目
- [ ] **元层自查**：问自己"我现在正在创建/更新一个可复用资产，我是否已执行验证阶段？包括frontmatter和TOML？"——生产防错工具的操作本身也是编辑
- [ ] **案例日期标注**：验证案例中的数据标注获取日期（代码会演进，数字会过时）

---

## 三、典型数据漂移案例库（9处漂移实录）

> 以下是2026-07-08并发安全检查器报告原子化任务中发现的9处数据漂移，作为典型警示案例，供后续对照参考。

### 案例背景

- **任务**：并发安全检查器（concurrent-checker）复盘报告原子化拆分
- **初始状态**：原子化拆分成功，28个链接全部有效，pre-commit检查通过，AI认为任务完成
- **验证阶段发现**：以下9处数据漂移，均为编辑阶段未验证直接搬运导致

### 9处漂移明细

| 编号 | 漂移位置 | 错误值 | 正确值 | 漂移类型 | 根因 |
|------|---------|--------|--------|---------|------|
| D1 | report_analyzer.py 行数 | 465行 | 840行 | 源代码行数 | 旧文档中的数字过时，代码已迭代 |
| D2 | 总核心代码行数 | 1893行 | 1226行 | 合计计算 | 分项变化后合计未重算，反向错误 |
| D3 | 测试用例总数 | 33个 | 48个 | 测试数量 | 旧文档中的数字过时，测试已新增 |
| D4 | 测试代码行数 | ~600行 | 902行 | 源代码行数 | 测试数增加后行数未更新 |
| D5 | 合计行数（含钩子+测试） | ~2565行 | ~2334行 | 合计计算 | 分项错误导致合计错误，且加法本身有误（1893+600=2493≠2565） |
| D6 | README索引中测试数 | 33个 | 48个 | 跨文档一致性 | 正文已更新但README索引未同步更新 |
| D7 | visitor.py 行数（正文多处） | 多处不一致 | 840行 | 跨文档一致性 | 同一指标在文档不同位置数值不同 |
| D8 | hooks/concurrent_check.py 行数 | 未统计 | 206行 | 文件遗漏 | 钩子文件未纳入行数统计，导致合计偏差 |
| D9 | 模式文件数据复制（元层漂移） | 7处漂移、2565行 | 9处漂移、2334行 | 模式文件验证缺失 | 创建模式文件时直接复制洞察文档中的错误数据，未重新验证 |

### 漂移分类统计

| 漂移类型 | 数量 | 占比 | 防御措施 |
|---------|------|------|---------|
| 源代码行数过时 | 3处（D1、D4、D8） | 33% | Step 2：实时wc -l统计 |
| 合计/总计计算错误 | 2处（D2、D5） | 22% | Step 3：独立重新计算 |
| 测试数量过时 | 1处（D3） | 11% | Step 2：grep实时计数 |
| 跨文档不一致 | 2处（D6、D7） | 22% | Step 4：全文搜索一致性 |
| 模式文件复制错误（元层） | 1处（D9） | 11% | Step 5：可复用资产额外验证（8类资产全覆盖+frontmatter/TOML检查） |

### 核心教训

1. **D8最易被忽略**：钩子/脚本/配置文件等"次要文件"经常被遗漏统计，但它们是系统的一部分
2. **D5是双重错误**：不仅分项数字错误，连加法本身也算错了（1893+600=2493，但文档写2565）——永远不要信任手算或来源文档的加法
3. **D9是元层教训**：创建模式文件来"解决数据漂移问题"时，模式文件自身也复制了数据漂移——验证是普适的，没有例外
4. **"看起来合理"不等于正确**：465行对一个AST visitor来说完全合理，但实际是840行

---

## 四、快速验证命令速查（PowerShell）

```powershell
# 统计Python文件行数
Get-ChildItem -Path <path> -Filter *.py -Recurse | ForEach-Object { (Get-Content $_.FullName | Measure-Object -Line).Lines } | Measure-Object -Sum | Select-Object -ExpandProperty Sum

# 统计测试函数数量
Get-ChildItem -Path <test-path> -Filter *.py -Recurse | Select-String -Pattern "def test_" | Measure-Object | Select-Object -ExpandProperty Count

# 全文搜索某个数字的所有出现位置
Get-ChildItem -Path <doc-path> -Filter *.md -Recurse | Select-String -Pattern "<number>" | ForEach-Object { "$($_.Path):$($_.LineNumber): $($_.Line.Trim())" }
```

---

## 五、验证完成标准

- [ ] Step 1-4 全部检查项通过
- [ ] 如果涉及模式/资产编辑，Step 5 全部检查项通过
- [ ] 所有发现的数据漂移已修正
- [ ] 跨文档数字一致（复盘报告、洞察文档、README、模式文件全部统一）
- [ ] 已运行 `check-links.py` 验证链接有效性
- [ ] 在提交信息中标注"已通过数据漂移检查清单验证"

---

## 六、关联资源

| 资源 | 链接 |
|------|------|
| 量化数据验证四查法 | [data-validation-four-checks.md](../patterns/methodology-patterns/governance-strategy/data-validation-four-checks.md) |
| 编辑-验证分离模式 | [edit-verify-separation.md](../patterns/methodology-patterns/ai-collaboration/edit-verify-separation.md) |
| 原始复盘报告 | [retrospective-report.md](../reports/task-reports/retrospective-concurrent-report-atomization-20260708/retrospective-report.md) |
| 洞察萃取文档 | [insight-extraction.md](../reports/task-reports/retrospective-concurrent-report-atomization-20260708/insight-extraction.md) |
| 资产清单 | [asset-inventory.md](asset-inventory.md) |
