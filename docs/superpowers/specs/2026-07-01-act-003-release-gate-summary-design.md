# ACT-003 发布判断摘要模板（与 Excel 学习脚本联动）设计文档

## 1. 背景

目前已完成 ACT-002：对 `.xlsx` 测试报告进行解析并导出“学习摘要报告”（多章节、偏全面）。在实际使用中，“是否能发版”往往需要一页式结论给决策者快速确认，而不需要打开完整学习报告。

因此需要新增一个“发布判断摘要模板”，并与现有脚本 `.agents/scripts/analyze-xlsx-test-report.py` 联动，直接生成一页式 Markdown 摘要文件，用于快速决策与复测规划。

## 2. 目标与非目标

### 2.1 目标

- 产出独立的一页式 Markdown 摘要（单独文件），包含发布决策所需的最小信息集
- 支持脚本一键生成摘要文件（模板化渲染，可覆盖默认模板）
- 支持只生成摘要（不生成全量学习报告），避免不必要的产物
- 通过脚本级测试确保摘要输出的结构稳定、关键字段不丢失

### 2.2 非目标

- 不做语义聚类/问题描述深度抽取（属于“增强解析”方向）
- 不修复全局断链与历史文档治理（属于“链接治理”方向）
- 不修改 ACT-002 的核心指标提取口径（仅新增“摘要输出层”）

## 3. 推荐方案

采用“模板 + 脚本联动”方案：

- 新增一个摘要模板文件，固定摘要结构与字段口径
- 在 `analyze-xlsx-test-report.py` 增加摘要渲染函数与 CLI 参数，复用既有 `extract_report_context()` 的输出上下文，不新增解析逻辑

## 4. 交付物与文件结构

### 4.1 新增文件

- `docs/retrospective/templates/release-gate-summary-template.md`
  - 一页式发布判断摘要模板（Markdown）

### 4.2 修改文件

- `.agents/scripts/analyze-xlsx-test-report.py`
  - 增加摘要渲染能力与 CLI 参数
- `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
  - 增加摘要输出相关测试

## 5. 摘要内容结构（模板规范）

摘要模板固定包含以下区块（顺序不变）：

1. `结论摘要`
   - 发布判断（建议发布/不建议发布/需人工判断）
   - 门槛（固定口径）
   - 差距（自动生成）
2. `核心指标`
   - 总用例、Pass、Fail、NoTest、Block、DI、严重问题数
3. `Top 风险`
   - 取 `risk_clusters` 前 3-5 条
4. `阻塞项（可选）`
   - 当 `decision != 建议发布` 时给出阻塞解释（复用 gap + 模块结论 TopN）
5. `复测建议（固定规则生成）`
   - 基于风险聚类映射为建议项（例如 音频/预览传输/存储回放/弱网/升级稳定性/功能主表）

模板需要包含 frontmatter，字段固定如下：

- `title`
- `report_type = "release-gate-summary"`
- `source`
- `format = "markdown"`
- `date`
- `status = "generated"`

## 6. 脚本接口设计（CLI 与渲染）

### 6.1 新增 CLI 参数

在现有参数基础上新增：

- `--summary-output <path>`
  - 指定生成摘要文件路径
- `--summary-template <path>`
  - 指定摘要模板路径（可选）
  - 默认值：`docs/retrospective/templates/release-gate-summary-template.md`
- `--summary-only`
  - 仅生成摘要文件，不生成全量学习报告

### 6.2 渲染函数

新增函数（命名固定）：

- `render_release_summary(context: dict, template_path: Path | None = None) -> str`
  - 输入：复用 `extract_report_context(input_path)` 的输出
  - 输出：按摘要模板渲染后的 Markdown 文本

### 6.3 行为规则

- 若仅提供 `--output`：保持现有行为（生成全量学习摘要报告）
- 若提供 `--summary-output`：
  - 额外生成摘要文件
  - 默认与全量报告同时生成
- 若提供 `--summary-only`：
  - 必须同时提供 `--summary-output`
  - 仅生成摘要，不生成全量报告
- 若摘要模板不存在：返回非零退出码，并在 stderr 输出“模板不存在”错误

## 7. 复测建议映射规则（最小规则集）

用 `risk_clusters`（前 3-5 条）映射为复测建议清单：

- `音频` → `复测音频：底噪/回声/啸叫/吞字/连续性`
- `预览传输` → `复测预览：弱网/长时预览/帧率与延迟/同步性`
- `存储回放` → `复测存储：TF 卡兼容/卡录首检/回放稳定/文件可用性`
- `弱网` → `复测网络：穿墙/丢包/重连/码率自适应`
- `升级稳定性` → `复测升级：升级成功率/断电恢复/版本回滚`
- 其他（如 `01功能测试`/`00接口测试`/`03性能测试`）→ `复测模块：<label>（优先复核 FAIL/Block 用例）`

## 8. 测试策略与验收标准

### 8.1 测试策略

新增脚本测试，覆盖：

- `render_release_summary()` 输出包含关键区块标题
- 摘要中包含发布判断、门槛、DI、严重问题数等关键字段
- CLI 在 `--summary-output` 模式下能写出摘要文件
- CLI 在 `--summary-only` 模式下不生成全量报告文件

### 8.2 验收标准

满足以下全部条件即可验收：

1. 新增模板文件存在且结构固定
2. `analyze-xlsx-test-report.py` 支持 `--summary-output/--summary-template/--summary-only`
3. 针对现有真实样本 `.xlsx` 能生成摘要文件，且包含：
   - 发布判断、门槛、差距
   - DI 与严重问题数
   - Top 风险
   - 复测建议
4. `.agents/scripts/tests/test_analyze_xlsx_test_report.py` 全部通过

## 9. 兼容性与边界

- 不改变现有全量报告模板与字段（向后兼容）
- 摘要依赖的字段全部来自现有 `extract_report_context()` 输出，避免新增解析耦合
- 若未来引入语义聚类，仅扩展 `context` 字段与摘要模板，不反向破坏 CLI 行为
