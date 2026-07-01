# ACT-003 发布判断摘要模板（与脚本联动）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增“一页式发布判断摘要”模板，并扩展 `.agents/scripts/analyze-xlsx-test-report.py` 支持生成摘要文件（可仅生成摘要），配套测试保障稳定输出。

**Architecture:** 在不改变现有 `extract_report_context()` 解析口径的前提下，新增 `render_release_summary()` 渲染层与独立摘要模板；通过新增 CLI 参数 `--summary-output/--summary-template/--summary-only` 控制产物；使用 pytest 为渲染与 CLI 行为加回归测试。

**Tech Stack:** Python、pytest、Markdown、现有 `.agents/scripts/tests` 测试体系

---

## 文件结构

### 新增文件

- `docs/retrospective/templates/release-gate-summary-template.md`

### 修改文件

- `.agents/scripts/analyze-xlsx-test-report.py`
- `.agents/scripts/tests/test_analyze_xlsx_test_report.py`

---

### Task 1: 新增一页式摘要模板

**Files:**
- Create: `docs/retrospective/templates/release-gate-summary-template.md`

- [ ] **Step 1: 创建模板内容**

```markdown
---
title: "{title}"
report_type: "release-gate-summary"
source: "{source}"
format: "markdown"
date: "{date}"
status: "generated"
---

# {title}

## 结论摘要

- 发布判断: {release_decision}
- 发布门槛: {release_threshold}
- 当前差距: {release_gap}

## 核心指标

{core_metrics_lines}

## Top 风险

{top_risks_lines}

## 阻塞项

{blockers_lines}

## 复测建议

{retest_suggestions_lines}
```

- [ ] **Step 2: 诊断检查**

Run: `GetDiagnostics(file:///d:/AI/docs/retrospective/templates/release-gate-summary-template.md)`
Expected: 无诊断错误

---

### Task 2: 先写失败测试（渲染与 CLI）

**Files:**
- Modify: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Reference: `.agents/scripts/analyze-xlsx-test-report.py`

- [ ] **Step 1: 写 `render_release_summary()` 的失败测试**

在测试文件追加以下用例（保持同一文件风格）：

```python
def test_render_release_summary_contains_required_sections() -> None:
    report = load_report_module()

    context = {
        "title": "X 测试报告学习摘要",
        "source": "sample.xlsx",
        "date": "2026-07-01",
        "overview_sheet": "测试报告",
        "used_fallback": False,
        "basic_info": {"项目": "X"},
        "workbook_summary": {"sheet_count": 1, "sheets": [{"name": "测试报告", "role": "总表"}]},
        "overall_metrics": {
            "total_cases": 10,
            "pass": 7,
            "fail": 2,
            "notest": 1,
            "block": 0,
            "di": 14,
            "serious_issues": 3,
        },
        "release_judgment": {
            "decision": "不建议发布",
            "threshold": "DI <= 12 且 致命+严重 <= 2",
            "gap": "DI=14，严重问题数=3，均未满足门槛。",
        },
        "module_findings": [{"sheet": "06音频专项测试", "summary": "发现 2 条高风险状态，其中 FAIL=2、NT=0、Block=0。"}],
        "risk_clusters": ["音频", "存储回放", "弱网"],
        "final_conclusion": "当前版本仍存在明显风险，不建议直接发布。",
    }

    markdown = report.render_release_summary(context)
    assert "## 结论摘要" in markdown
    assert "## 核心指标" in markdown
    assert "## Top 风险" in markdown
    assert "## 阻塞项" in markdown
    assert "## 复测建议" in markdown
    assert "DI <= 12" in markdown
    assert "DI=14" in markdown
```

- [ ] **Step 2: 写 CLI 摘要输出的失败测试**

```python
def test_cli_writes_release_summary_only(tmp_path) -> None:
    workbook_path = build_realistic_overview_workbook(tmp_path / "realistic.xlsx")
    full_output_path = tmp_path / "full.md"
    summary_output_path = tmp_path / "summary.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--input",
            str(workbook_path),
            "--output",
            str(full_output_path),
            "--summary-output",
            str(summary_output_path),
            "--summary-only",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert result.returncode == 0
    assert summary_output_path.exists()
    assert not full_output_path.exists()
    content = summary_output_path.read_text(encoding="utf-8")
    assert "report_type: \"release-gate-summary\"" in content
    assert "## 结论摘要" in content
```

- [ ] **Step 3: 跑测试确认红灯**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -q`
Expected: FAIL（`render_release_summary` 未定义 / CLI 参数未识别）

---

### Task 3: 实现摘要渲染与复测建议规则

**Files:**
- Modify: `.agents/scripts/analyze-xlsx-test-report.py`
- Test: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`

- [ ] **Step 1: 增加摘要模板默认路径常量**

```python
DEFAULT_SUMMARY_TEMPLATE = (
    PROJECT_ROOT
    / "docs"
    / "retrospective"
    / "templates"
    / "release-gate-summary-template.md"
)
```

- [ ] **Step 2: 增加复测建议映射函数**

```python
def build_retest_suggestions(risk_clusters: list[str]) -> list[str]:
    mapping = {
        "音频": "复测音频：底噪/回声/啸叫/吞字/连续性",
        "预览传输": "复测预览：弱网/长时预览/帧率与延迟/同步性",
        "存储回放": "复测存储：TF 卡兼容/卡录首检/回放稳定/文件可用性",
        "弱网": "复测网络：穿墙/丢包/重连/码率自适应",
        "升级稳定性": "复测升级：升级成功率/断电恢复/版本回滚",
    }
    result = []
    for label in risk_clusters[:5]:
        result.append(mapping.get(label, f"复测模块：{label}（优先复核 FAIL/Block 用例）"))
    return result
```

- [ ] **Step 3: 增加摘要渲染函数 `render_release_summary()`**

```python
def format_core_metrics_lines(overall_metrics: dict[str, object]) -> str:
    labels = [
        ("总用例", overall_metrics.get("total_cases")),
        ("Pass", overall_metrics.get("pass")),
        ("Fail", overall_metrics.get("fail")),
        ("NoTest", overall_metrics.get("notest")),
        ("Block", overall_metrics.get("block")),
        ("DI", overall_metrics.get("di")),
        ("严重问题数", overall_metrics.get("serious_issues")),
    ]
    return "\n".join(f"- {label}: {value}" for label, value in labels)


def format_top_risks_lines(risk_clusters: list[str]) -> str:
    if not risk_clusters:
        return "- 未识别到明显风险"
    return "\n".join(f"- {item}" for item in risk_clusters[:5])


def format_blockers_lines(context: dict) -> str:
    decision = context["release_judgment"]["decision"]
    if decision == "建议发布":
        return "- 无明显阻塞项"
    lines = [f"- {context['release_judgment']['gap']}"]
    for item in context.get("module_findings", [])[:3]:
        lines.append(f"- {item['sheet']}: {item['summary']}")
    return "\n".join(lines)


def render_release_summary(context: dict, template_path: Path | None = None) -> str:
    resolved_template = template_path or DEFAULT_SUMMARY_TEMPLATE
    if not resolved_template.exists():
        raise FileNotFoundError(f"摘要模板不存在: {resolved_template}")

    template = resolved_template.read_text(encoding="utf-8")
    retest_suggestions = build_retest_suggestions(context.get("risk_clusters", []))

    return template.format(
        title=context["title"],
        source=context["source"],
        date=context["date"],
        release_decision=context["release_judgment"]["decision"],
        release_threshold=context["release_judgment"]["threshold"],
        release_gap=context["release_judgment"]["gap"],
        core_metrics_lines=format_core_metrics_lines(context["overall_metrics"]),
        top_risks_lines=format_top_risks_lines(context.get("risk_clusters", [])),
        blockers_lines=format_blockers_lines(context),
        retest_suggestions_lines="\n".join(f"- {item}" for item in retest_suggestions),
    )
```

- [ ] **Step 4: 跑单测确认转绿（渲染用例）**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py::test_render_release_summary_contains_required_sections -q`
Expected: PASS

---

### Task 4: 实现 CLI 参数与输出逻辑

**Files:**
- Modify: `.agents/scripts/analyze-xlsx-test-report.py`
- Test: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`

- [ ] **Step 1: 增加 CLI 参数解析**

在 `parse_args()` 增加：

```python
parser.add_argument("--summary-output", default=None, help="输出发布判断摘要 Markdown 文件路径")
parser.add_argument("--summary-template", default=str(DEFAULT_SUMMARY_TEMPLATE), help="摘要模板路径")
parser.add_argument("--summary-only", action="store_true", help="仅生成摘要，不生成全量报告")
```

- [ ] **Step 2: 在 `main()` 中实现行为规则**

核心逻辑（保持错误输出到 stderr，返回非零）：

```python
summary_output = Path(args.summary_output) if args.summary_output else None
summary_template = Path(args.summary_template) if args.summary_template else None

if args.summary_only and summary_output is None:
    print("--summary-only 需要与 --summary-output 一起使用", file=sys.stderr)
    return 1

context = extract_report_context(input_path)

if not args.summary_only:
    markdown = render_report(context, template_path=template_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"已生成报告: {output_path}")

if summary_output is not None:
    summary_md = render_release_summary(context, template_path=summary_template)
    summary_output.parent.mkdir(parents=True, exist_ok=True)
    summary_output.write_text(summary_md, encoding="utf-8")
    print(f"已生成摘要: {summary_output}")
```

- [ ] **Step 3: 回跑 CLI 测试确认转绿**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py::test_cli_writes_release_summary_only -q`
Expected: PASS

---

### Task 5: 收尾校验与示例验证

**Files:**
- Verify: `.agents/scripts/analyze-xlsx-test-report.py`
- Verify: `docs/retrospective/templates/release-gate-summary-template.md`

- [ ] **Step 1: 跑脚本测试全集**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -q`
Expected: PASS

- [ ] **Step 2: 重复检测**

Run: `python .agents/scripts/check-duplication.py --path .agents/scripts --threshold 10`
Expected: 通过（无新增≥10行跨文件重复块）

- [ ] **Step 3: 真实样本生成摘要文件**

Run:

```bash
python .agents/scripts/analyze-xlsx-test-report.py --input "d:\AI\.temp\【20260327】单目1M插值3M232测试报告.xlsx" --output "d:\AI\.temp\【20260327】单目1M插值3M232测试报告-脚本版学习报告.md" --summary-output "d:\AI\.temp\【20260327】单目1M插值3M232测试报告-发布判断摘要.md" --summary-only
```

Expected:
- 退出码 `0`
- 生成摘要文件 `d:\AI\.temp\【20260327】单目1M插值3M232测试报告-发布判断摘要.md`
- 摘要包含 `发布判断/发布门槛/当前差距/DI/严重问题数/Top 风险/复测建议`

- [ ] **Step 4: 诊断检查**

Run: `GetDiagnostics(file:///d:/AI/docs/retrospective/templates/release-gate-summary-template.md)`
Expected: 无诊断错误

Run: `GetDiagnostics(file:///d:/AI/.agents/scripts/analyze-xlsx-test-report.py)`
Expected: 无诊断错误

Run: `GetDiagnostics(file:///d:/AI/.agents/scripts/tests/test_analyze_xlsx_test_report.py)`
Expected: 无诊断错误

---

## 自检结论

### Spec 覆盖

- 摘要模板与字段口径：Task 1 覆盖
- `render_release_summary()` 与复测建议规则：Task 3 覆盖
- CLI 参数与行为规则：Task 4 覆盖
- 测试与验收：Task 2、Task 5 覆盖

### 占位符扫描

- 无 TBD/TODO/后续补充
- 所有新增文件、修改文件、命令与期望结果均明确

### 类型与命名一致性

- 渲染函数名固定为 `render_release_summary`
- CLI 参数固定为 `--summary-output/--summary-template/--summary-only`
