# ACT-002 风险语义聚类增强 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `.agents/scripts/analyze-xlsx-test-report.py` 增加基于高风险行文本的规则关键词风险聚类，在保持 `risk_clusters` 兼容的同时新增 `risk_cluster_details` 证据层。

**Architecture:** 先在测试中锁定 3 个行为：关键词分类、聚类细节聚合、端到端上下文字段增强；再在脚本中新增 `extract_risk_rows()`、`classify_risk_text()`、`build_risk_cluster_details()`，并让 `build_risk_clusters()` 优先消费文本聚类、未命中时回退到现有 sheet 名称映射。整个改动只触及现有脚本与测试文件，不改 CLI 参数、不改 Markdown 模板。

**Tech Stack:** Python、pytest、openpyxl、现有 `.agents/scripts` CLI 与测试体系

---

## 文件结构

### 修改文件

- `.agents/scripts/analyze-xlsx-test-report.py`
  - 新增风险文本提取、关键词分类、聚类细节聚合与回退逻辑
- `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
  - 新增关键词分类、聚类细节、端到端上下文字段增强测试

### 不修改文件

- `docs/retrospective/templates/xlsx-test-report-template.md`
- `docs/retrospective/templates/release-gate-summary-template.md`

---

### Task 1: 写失败测试，锁定关键词分类与聚类细节

**Files:**
- Modify: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Reference: `.agents/scripts/analyze-xlsx-test-report.py`

- [ ] **Step 1: 写 `classify_risk_text()` 的失败测试**

在测试文件末尾追加以下用例：

```python
def test_classify_risk_text_by_keywords() -> None:
    report = load_report_module()

    assert report.classify_risk_text("底噪明显") == "音频"
    assert report.classify_risk_text("拉流卡顿，画面延迟") == "预览稳定性"
    assert report.classify_risk_text("异常重启后黑屏") == "重启恢复"
    assert report.classify_risk_text("TF卡录像文件损坏") == "存储回放"
    assert report.classify_risk_text("弱网环境下重连失败") == "弱网"
    assert report.classify_risk_text("升级后版本回退") == "升级稳定性"
    assert report.classify_risk_text("普通功能验证通过") is None
```

- [ ] **Step 2: 写 `build_risk_cluster_details()` 的失败测试**

```python
def test_build_risk_cluster_details_aggregates_examples_and_sheets(tmp_path) -> None:
    report = load_report_module()
    workbook_path = tmp_path / "semantic.xlsx"

    wb = openpyxl.Workbook()
    overview = wb.active
    overview.title = "测试报告"
    overview.append(["总用例", 6])
    overview.append(["Pass", 1])
    overview.append(["Fail", 4])
    overview.append(["NoTest", 1])
    overview.append(["Block", 0])

    audio = wb.create_sheet("06音频专项测试")
    audio.append(["模块", "现象", "状态"])
    audio.append(["音频", "底噪明显", "FAIL"])
    audio.append(["音频", "回声轻微", "NT"])

    wifi = wb.create_sheet("WiFi穿墙测试")
    wifi.append(["点位", "现象", "状态"])
    wifi.append(["点7", "弱网环境下重连失败", "FAIL"])
    wifi.append(["点8", "拉流卡顿", "FAIL"])

    wb.save(workbook_path)

    workbook = report.load_workbook(workbook_path)
    details = report.build_risk_cluster_details(workbook, "测试报告")

    assert details[0]["label"] == "弱网"
    assert details[0]["count"] == 1
    assert "WiFi穿墙测试" in details[0]["source_sheets"]
    assert "弱网环境下重连失败" in details[0]["examples"]

    labels = [item["label"] for item in details]
    assert "音频" in labels
    assert "预览稳定性" in labels
```

- [ ] **Step 3: 跑局部测试确认红灯**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -k "classify_risk_text or build_risk_cluster_details" -q`
Expected: FAIL，报错点应为 `classify_risk_text` / `build_risk_cluster_details` 未定义

- [ ] **Step 4: Commit**

```bash
git add .agents/scripts/tests/test_analyze_xlsx_test_report.py
git commit -m "test(reports): lock semantic risk clustering behavior"
```

---

### Task 2: 写端到端失败测试，锁定 `extract_report_context()` 新字段与优先级

**Files:**
- Modify: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Reference: `.agents/scripts/analyze-xlsx-test-report.py`

- [ ] **Step 1: 为真实布局样本补充文本驱动断言**

把现有 `test_extract_report_context_with_realistic_overview_layout()` 追加以下断言：

```python
    assert "risk_cluster_details" in context
    assert context["risk_cluster_details"]
    assert context["risk_clusters"][0] in {"弱网", "音频", "预览稳定性"}
    first_detail = context["risk_cluster_details"][0]
    assert set(first_detail.keys()) == {"label", "count", "examples", "source_sheets"}
```

- [ ] **Step 2: 新增“文本优先于 sheet 名称回退”的失败测试**

```python
def test_extract_report_context_prefers_text_risk_clustering(tmp_path) -> None:
    report = load_report_module()
    workbook_path = tmp_path / "text-priority.xlsx"

    wb = openpyxl.Workbook()
    overview = wb.active
    overview.title = "测试报告"
    overview.append(["总用例", 4])
    overview.append(["Pass", 0])
    overview.append(["Fail", 4])
    overview.append(["NoTest", 0])
    overview.append(["Block", 0])

    generic = wb.create_sheet("01功能测试")
    generic.append(["模块", "现象", "状态"])
    generic.append(["模块A", "异常重启后黑屏", "FAIL"])
    generic.append(["模块B", "弱网环境下重连失败", "FAIL"])
    generic.append(["模块C", "底噪明显", "FAIL"])
    generic.append(["模块D", "TF卡录像文件损坏", "FAIL"])
    wb.save(workbook_path)

    context = report.extract_report_context(workbook_path)

    assert context["risk_clusters"][:4] == ["重启恢复", "弱网", "存储回放", "音频"]
    assert context["risk_cluster_details"][0]["label"] == "重启恢复"
```

- [ ] **Step 3: 跑局部测试确认红灯**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -k "prefers_text_risk_clustering or realistic_overview_layout" -q`
Expected: FAIL，报错点应为 `risk_cluster_details` 缺失或 `risk_clusters` 仍来自旧的 sheet 名映射

- [ ] **Step 4: Commit**

```bash
git add .agents/scripts/tests/test_analyze_xlsx_test_report.py
git commit -m "test(reports): cover semantic clustering context outputs"
```

---

### Task 3: 实现风险文本提取、关键词分类与聚类细节

**Files:**
- Modify: `.agents/scripts/analyze-xlsx-test-report.py`
- Test: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`

- [ ] **Step 1: 在脚本顶部增加风险词典与优先级**

把以下常量加到 `STATUS_VALUE_MAP` 下方：

```python
RISK_KEYWORDS = {
    "重启恢复": ("重启", "死机", "崩溃", "异常恢复", "软启", "断电恢复"),
    "预览稳定性": ("卡顿", "丢帧", "花屏", "黑屏", "拉流失败", "延迟", "不同步"),
    "弱网": ("弱网", "穿墙", "丢包", "重连", "断流", "网络异常"),
    "存储回放": ("TF卡", "录像", "回放", "录制", "文件损坏", "卡录"),
    "音频": ("底噪", "回声", "啸叫", "破音", "吞字", "无声", "杂音"),
    "升级稳定性": ("升级失败", "升级后", "版本回退", "升级重启"),
}
RISK_PRIORITY = (
    "重启恢复",
    "预览稳定性",
    "弱网",
    "存储回放",
    "音频",
    "升级稳定性",
)
```

- [ ] **Step 2: 写最小实现函数**

在 `categorize_risk()` 之前新增：

```python
def extract_risk_rows(sheet) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in sheet.iter_rows(values_only=True):
        values = [normalize_text(cell) for cell in row if normalize_text(cell)]
        if not values:
            continue

        status = None
        for value in values:
            normalized = normalize_metric_key(value)
            if normalized in {"FAIL", "NT", "NOTEST", "NOT TEST", "BLOCK"}:
                status = STATUS_VALUE_MAP[normalized]
                break

        if status is None:
            continue

        text = " ".join(
            value for value in values if normalize_metric_key(value) not in STATUS_VALUE_MAP
        )
        if text:
            rows.append({"sheet": sheet.title, "status": status, "text": text})
    return rows


def classify_risk_text(text: str) -> str | None:
    for label in RISK_PRIORITY:
        for keyword in RISK_KEYWORDS[label]:
            if keyword in text:
                return label
    return None


def build_risk_cluster_details(workbook, overview_sheet: str | None) -> list[dict[str, object]]:
    buckets: dict[str, dict[str, object]] = {}

    for sheet in workbook.worksheets:
        if overview_sheet and sheet.title == overview_sheet:
            continue

        for item in extract_risk_rows(sheet):
            label = classify_risk_text(item["text"])
            if label is None:
                continue
            bucket = buckets.setdefault(
                label,
                {"label": label, "count": 0, "examples": [], "source_sheets": set()},
            )
            bucket["count"] += 1
            if item["text"] not in bucket["examples"] and len(bucket["examples"]) < 3:
                bucket["examples"].append(item["text"])
            bucket["source_sheets"].add(item["sheet"])

    details = []
    for label in RISK_PRIORITY:
        bucket = buckets.get(label)
        if not bucket:
            continue
        details.append(
            {
                "label": bucket["label"],
                "count": bucket["count"],
                "examples": bucket["examples"],
                "source_sheets": sorted(bucket["source_sheets"]),
            }
        )
    return details
```

- [ ] **Step 3: 跑前两组测试确认转绿**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -k "classify_risk_text or build_risk_cluster_details" -q`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add .agents/scripts/analyze-xlsx-test-report.py .agents/scripts/tests/test_analyze_xlsx_test_report.py
git commit -m "feat(reports): add keyword-driven risk cluster details"
```

---

### Task 4: 集成到上下文输出并保留旧逻辑回退

**Files:**
- Modify: `.agents/scripts/analyze-xlsx-test-report.py`
- Test: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`

- [ ] **Step 1: 把 `build_risk_clusters()` 改为优先消费 details**

用以下实现替换当前的 `build_risk_clusters()`：

```python
def build_risk_clusters(workbook, overview_sheet: str | None) -> list[str]:
    details = build_risk_cluster_details(workbook, overview_sheet)
    if details:
        return [item["label"] for item in details[:5]]

    candidates: list[tuple[int, str]] = []
    for sheet in workbook.worksheets:
        if overview_sheet and sheet.title == overview_sheet:
            continue

        counts = count_status_words(sheet)
        if counts["fail"] == 0 and counts["block"] == 0:
            continue

        label = categorize_risk(sheet.title)
        candidates.append((build_risk_score(counts), label))

    candidates.sort(key=lambda item: item[0], reverse=True)
    clusters: list[str] = []
    for _, label in candidates:
        if label not in clusters:
            clusters.append(label)
        if len(clusters) == 5:
            break
    return clusters
```

- [ ] **Step 2: 在 `extract_report_context()` 里输出 `risk_cluster_details`**

把 `extract_report_context()` 的中段改为：

```python
    workbook_summary = summarize_workbook(workbook, overview_name)
    risk_cluster_details = build_risk_cluster_details(workbook, overview_name)
    risk_clusters = (
        [item["label"] for item in risk_cluster_details[:5]]
        if risk_cluster_details
        else build_risk_clusters(workbook, overview_name)
    )
    release_judgment = build_release_judgment(overall_metrics)
```

并在返回字典里加入：

```python
        "risk_cluster_details": risk_cluster_details,
```

- [ ] **Step 3: 跑端到端测试确认转绿**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -k "prefers_text_risk_clustering or realistic_overview_layout" -q`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add .agents/scripts/analyze-xlsx-test-report.py .agents/scripts/tests/test_analyze_xlsx_test_report.py
git commit -m "feat(reports): prefer semantic clustering in report context"
```

---

### Task 5: 全量回归、真实样本验证与收尾

**Files:**
- Verify: `.agents/scripts/analyze-xlsx-test-report.py`
- Verify: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`

- [ ] **Step 1: 跑脚本测试全集**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -q`
Expected: PASS

- [ ] **Step 2: 重复检测**

Run: `python .agents/scripts/check-duplication.py --path .agents/scripts --threshold 10`
Expected: 通过，无新增跨文件重复块

- [ ] **Step 3: 用真实样本回归生成报告与摘要**

Run:

```bash
python .agents/scripts/analyze-xlsx-test-report.py --input "d:\AI\.temp\【20260327】单目1M插值3M232测试报告.xlsx" --output "d:\AI\.temp\【20260327】单目1M插值3M232测试报告-脚本版学习报告.md" --summary-output "d:\AI\.temp\【20260327】单目1M插值3M232测试报告-发布判断摘要.md"
```

Expected:
- 退出码 `0`
- 全量报告与摘要文件都能生成
- `extract_report_context()` 在真实样本上产出非空 `risk_cluster_details`

- [ ] **Step 4: 检查诊断**

Run: `GetDiagnostics(file:///d:/AI/.agents/scripts/analyze-xlsx-test-report.py)`
Expected: 无诊断错误

Run: `GetDiagnostics(file:///d:/AI/.agents/scripts/tests/test_analyze_xlsx_test_report.py)`
Expected: 无诊断错误

- [ ] **Step 5: Commit**

```bash
git add .agents/scripts/analyze-xlsx-test-report.py .agents/scripts/tests/test_analyze_xlsx_test_report.py
git commit -m "test(reports): verify semantic risk clustering end-to-end"
```

---

## 自检结论

### Spec 覆盖

- 风险文本提取与关键词分类：Task 1、Task 3 覆盖
- `risk_cluster_details` 结构化证据层：Task 1、Task 3、Task 4 覆盖
- 文本优先、sheet 名回退：Task 2、Task 4 覆盖
- 不改 CLI / 不改模板：计划中未触碰模板与参数
- 验收与真实样本验证：Task 5 覆盖

### 占位符扫描

- 无 `TBD`、`TODO`、`稍后处理`
- 每一步都含具体代码、命令与预期结果

### 类型与命名一致性

- 新函数名固定为 `extract_risk_rows`、`classify_risk_text`、`build_risk_cluster_details`
- 新字段名固定为 `risk_cluster_details`
- `risk_clusters` 继续保留为 `list[str]`
