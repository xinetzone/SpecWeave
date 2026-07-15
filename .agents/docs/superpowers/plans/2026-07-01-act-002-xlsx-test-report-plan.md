# ACT-002 Excel 测试报告解析与 Markdown 导出 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为“测试报告学习 + 导出 Markdown”场景落地一个最小可复用闭环，新增 `.xlsx` 解析脚本和固定 Markdown 模板，并用真实样本完成验证。

**Architecture:** 采用“脚本层 + 模板层”的双文件最小拆分：脚本负责读取 `.xlsx`、识别总表、提取状态统计与风险证据、渲染 Markdown；模板负责约束固定输出章节。实现以 `openpyxl` 为核心，先为关键行为补充脚本级测试，再通过真实样本跑通 CLI、输出 Markdown 并执行重复代码检测。

**Tech Stack:** Python、pytest、openpyxl、Markdown、现有 `.agents/scripts/tests` 测试体系

---

## 文件结构

### 新增文件

- `.agents/scripts/analyze-xlsx-test-report.py`
  - CLI 入口，负责加载工作簿、识别总表、抽取状态统计、构建结论、渲染 Markdown
- `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
  - 覆盖总表识别、降级统计、Markdown 渲染和 CLI 输出
- `docs/retrospective/templates/xlsx-test-report-template.md`
  - 固定输出章节模板，约束 frontmatter、结论摘要、工作簿结构、总体结果、风险聚类、最终判断

### 参考文件

- `docs/superpowers/specs/2026-07-01-act-002-xlsx-test-report-design.md`
- `.agents/scripts/add-frontmatter.py`
- `.agents/scripts/check-duplication.py`
- `.agents/scripts/tests/test_frontmatter.py`

### 验证文件

- `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- `.agents/scripts/analyze-xlsx-test-report.py`
- `docs/retrospective/templates/xlsx-test-report-template.md`

---

### Task 1: 先写脚本级测试，锁定最小行为

**Files:**
- Create: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Reference: `.agents/scripts/tests/test_frontmatter.py`
- Reference: `docs/superpowers/specs/2026-07-01-act-002-xlsx-test-report-design.md`

- [ ] **Step 1: 新建测试文件骨架与导入**

```python
from pathlib import Path
import subprocess
import sys

import openpyxl

import analyze_xlsx_test_report as report
```

- [ ] **Step 2: 写一个最小工作簿工厂，生成“标准总表 + 专项页”样本**

```python
def build_standard_workbook(path: Path) -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "测试报告"
    ws.append(["项目", "IPC-232"])
    ws.append(["设备型号", "单目1M插值3M232"])
    ws.append(["固件版本", "1.0.0"])
    ws.append(["APP版本", "6.0.0"])
    ws.append(["总用例", 10])
    ws.append(["Pass", 7])
    ws.append(["Fail", 2])
    ws.append(["NoTest", 1])
    ws.append(["Block", 0])
    ws.append(["DI", 14])
    ws.append(["严重问题数", 3])

    audio = wb.create_sheet("音频专项")
    audio.append(["模块", "现象", "状态"])
    audio.append(["音频", "底噪明显", "FAIL"])
    audio.append(["音频", "回声轻微", "NT"])

    preview = wb.create_sheet("预览稳定性")
    preview.append(["模块", "现象", "状态"])
    preview.append(["预览", "长时预览正常", "PASS"])
    preview.append(["预览", "弱网卡顿", "FAIL"])

    wb.save(path)
    return path
```

- [ ] **Step 3: 写“标准总表识别 + 指标提取”失败测试**

```python
def test_extract_report_context_with_standard_overview(tmp_path):
    workbook_path = build_standard_workbook(tmp_path / "sample.xlsx")
    context = report.extract_report_context(workbook_path)

    assert context["overview_sheet"] == "测试报告"
    assert context["overall_metrics"]["total_cases"] == 10
    assert context["overall_metrics"]["pass"] == 7
    assert context["overall_metrics"]["fail"] == 2
    assert context["overall_metrics"]["notest"] == 1
    assert context["overall_metrics"]["block"] == 0
    assert context["overall_metrics"]["di"] == 14
    assert context["overall_metrics"]["serious_issues"] == 3
```

- [ ] **Step 4: 写“未识别总表时触发降级统计”失败测试**

```python
def test_extract_report_context_falls_back_to_status_scan(tmp_path):
    workbook_path = tmp_path / "fallback.xlsx"
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "功能测试"
    ws.append(["模块", "状态"])
    ws.append(["预览", "PASS"])
    ws.append(["音频", "FAIL"])
    ws.append(["存储", "NT"])
    wb.save(workbook_path)

    context = report.extract_report_context(workbook_path)

    assert context["overview_sheet"] is None
    assert context["used_fallback"] is True
    assert context["overall_metrics"]["pass"] == 1
    assert context["overall_metrics"]["fail"] == 1
    assert context["overall_metrics"]["notest"] == 1
```

- [ ] **Step 5: 写“Markdown 渲染包含关键章节”失败测试**

```python
def test_render_report_contains_required_sections():
    context = {
        "title": "示例报告",
        "source": "sample.xlsx",
        "date": "2026-07-01",
        "basic_info": {"项目": "IPC-232"},
        "workbook_summary": {"sheet_count": 2, "sheets": [{"name": "测试报告", "role": "总表"}]},
        "overall_metrics": {"total_cases": 10, "pass": 7, "fail": 2, "notest": 1, "block": 0, "di": 14, "serious_issues": 3},
        "release_judgment": {"decision": "不建议发布", "threshold": "DI <= 12 且 致命+严重 <= 2", "gap": "DI 和严重问题数均超标"},
        "module_findings": [{"sheet": "音频专项", "summary": "音频风险集中在底噪与回声"}],
        "risk_clusters": ["音频", "预览传输"],
        "final_conclusion": "当前版本不满足发布门槛。",
        "used_fallback": False,
    }

    markdown = report.render_report(context)

    assert "## 结论摘要" in markdown
    assert "## 基本信息" in markdown
    assert "## 工作簿结构" in markdown
    assert "## 总体结果" in markdown
    assert "## 风险聚类" in markdown
    assert "## 最终判断" in markdown
```

- [ ] **Step 6: 写 CLI 端到端测试，确保能产出 Markdown 文件**

```python
def test_cli_writes_markdown_output(tmp_path):
    workbook_path = build_standard_workbook(tmp_path / "cli.xlsx")
    output_path = tmp_path / "report.md"

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "analyze-xlsx-test-report.py"),
            "--input",
            str(workbook_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert result.returncode == 0
    assert output_path.exists()
    assert "示例报告" not in output_path.read_text(encoding="utf-8")
    assert "## 最终判断" in output_path.read_text(encoding="utf-8")
```

- [ ] **Step 7: 运行测试，确认当前失败**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -q`
Expected: FAIL，提示 `analyze_xlsx_test_report` 模块不存在或目标函数未定义

---

### Task 2: 实现解析脚本的最小骨架与核心函数

**Files:**
- Create: `.agents/scripts/analyze-xlsx-test-report.py`
- Test: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Reference: `.agents/scripts/add-frontmatter.py`

- [ ] **Step 1: 创建脚本骨架、CLI 参数和模板加载入口**

```python
#!/usr/bin/env python3
"""解析 .xlsx 测试报告并导出 Markdown 摘要。"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

import openpyxl

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE = PROJECT_ROOT / "docs" / "retrospective" / "templates" / "xlsx-test-report-template.md"
STATUS_WORDS = ("PASS", "FAIL", "NT", "BLOCK")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="解析 .xlsx 测试报告并导出 Markdown")
    parser.add_argument("--input", required=True, help="输入 .xlsx 文件路径")
    parser.add_argument("--output", required=True, help="输出 Markdown 文件路径")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE), help="Markdown 模板路径")
    return parser.parse_args()
```

- [ ] **Step 2: 实现工作簿读取、总表识别和状态统计函数**

```python
def load_workbook(input_path: Path):
    if not input_path.exists():
        raise FileNotFoundError(f"输入文件不存在: {input_path}")
    try:
        return openpyxl.load_workbook(input_path, data_only=True)
    except Exception as exc:
        raise RuntimeError(f"无法读取工作簿: {input_path}") from exc


def detect_overview_sheet(workbook) -> str | None:
    for sheet in workbook.worksheets:
        if "测试报告" in sheet.title:
            return sheet.title
    return None


def count_status_words(sheet) -> dict[str, int]:
    counts = {"pass": 0, "fail": 0, "notest": 0, "block": 0}
    mapping = {"PASS": "pass", "FAIL": "fail", "NT": "notest", "BLOCK": "block"}
    for row in sheet.iter_rows(values_only=True):
        for cell in row:
            value = str(cell).strip().upper() if cell is not None else ""
            if value in mapping:
                counts[mapping[value]] += 1
    return counts
```

- [ ] **Step 3: 实现总表键值提取与降级聚合**

```python
def extract_key_value_metrics(sheet) -> dict[str, int | None]:
    key_map = {
        "总用例": "total_cases",
        "PASS": "pass",
        "FAIL": "fail",
        "NOTEST": "notest",
        "BLOCK": "block",
        "DI": "di",
        "严重问题数": "serious_issues",
    }
    metrics = {value: None for value in key_map.values()}
    for row in sheet.iter_rows(values_only=True):
        if len(row) < 2:
            continue
        key = str(row[0]).strip().upper() if row[0] is not None else ""
        if key in key_map and isinstance(row[1], (int, float)):
            metrics[key_map[key]] = int(row[1])
    return metrics


def fallback_metrics(workbook) -> dict[str, int | None]:
    merged = {"total_cases": 0, "pass": 0, "fail": 0, "notest": 0, "block": 0, "di": None, "serious_issues": None}
    for sheet in workbook.worksheets:
        counts = count_status_words(sheet)
        merged["pass"] += counts["pass"]
        merged["fail"] += counts["fail"]
        merged["notest"] += counts["notest"]
        merged["block"] += counts["block"]
    merged["total_cases"] = merged["pass"] + merged["fail"] + merged["notest"] + merged["block"]
    return merged
```

- [ ] **Step 4: 实现工作簿结构摘要、风险聚类和发布判断**

```python
def summarize_workbook(workbook) -> dict:
    sheets = []
    for sheet in workbook.worksheets:
        role = "总表" if "测试报告" in sheet.title else "专项页"
        sheets.append({"name": sheet.title, "role": role, "rows": sheet.max_row, "cols": sheet.max_column})
    return {"sheet_count": len(sheets), "sheets": sheets}


def build_risk_clusters(workbook) -> list[str]:
    risks = []
    for sheet in workbook.worksheets:
        title = sheet.title
        status_counts = count_status_words(sheet)
        if status_counts["fail"] + status_counts["notest"] == 0:
            continue
        if "音频" in title:
            risks.append("音频")
        elif "预览" in title or "直播" in title:
            risks.append("预览传输")
        elif "回放" in title or "TF" in title or "存储" in title:
            risks.append("存储回放")
        elif "WIFI" in title.upper() or "弱网" in title:
            risks.append("弱网")
        else:
            risks.append(title)
    return list(dict.fromkeys(risks))[:5]


def build_release_judgment(metrics: dict[str, int | None]) -> dict[str, str]:
    threshold = "DI <= 12 且 致命+严重 <= 2"
    di = metrics.get("di")
    serious = metrics.get("serious_issues")
    if di is None or serious is None:
        return {"decision": "需人工判断", "threshold": threshold, "gap": "缺少 DI 或严重问题数"}
    if di <= 12 and serious <= 2:
        return {"decision": "建议发布", "threshold": threshold, "gap": "已满足门槛"}
    return {"decision": "不建议发布", "threshold": threshold, "gap": f"DI={di}，严重问题数={serious}"}
```

- [ ] **Step 5: 实现上下文组装与 Markdown 渲染**

```python
def extract_report_context(input_path: Path) -> dict:
    workbook = load_workbook(input_path)
    overview_name = detect_overview_sheet(workbook)
    overview_sheet = workbook[overview_name] if overview_name else None
    metrics = extract_key_value_metrics(overview_sheet) if overview_sheet else fallback_metrics(workbook)
    used_fallback = overview_sheet is None or metrics["total_cases"] is None
    if used_fallback:
        metrics = fallback_metrics(workbook)

    context = {
        "title": f"{input_path.stem}：全面学习与结论提炼",
        "source": str(input_path),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "overview_sheet": overview_name,
        "used_fallback": used_fallback,
        "basic_info": {"项目": input_path.stem},
        "workbook_summary": summarize_workbook(workbook),
        "overall_metrics": metrics,
        "release_judgment": build_release_judgment(metrics),
        "module_findings": [],
        "risk_clusters": build_risk_clusters(workbook),
        "final_conclusion": build_release_judgment(metrics)["decision"],
    }
    return context


def render_report(context: dict, template_path: Path | None = None) -> str:
    template = (template_path or DEFAULT_TEMPLATE).read_text(encoding="utf-8")
    return template.format(
        title=context["title"],
        source=context["source"],
        date=context["date"],
        basic_info_lines="\n".join(f"- {k}: {v}" for k, v in context["basic_info"].items()),
        workbook_summary_lines="\n".join(f"- {item['name']}: {item['role']}，{item['rows']} 行，{item['cols']} 列" for item in context["workbook_summary"]["sheets"]),
        overall_metrics_lines="\n".join(f"- {k}: {v}" for k, v in context["overall_metrics"].items()),
        release_decision=context["release_judgment"]["decision"],
        release_threshold=context["release_judgment"]["threshold"],
        release_gap=context["release_judgment"]["gap"],
        risk_clusters_lines="\n".join(f"- {item}" for item in context["risk_clusters"]) or "- 无明显风险聚类",
        final_conclusion=context["final_conclusion"],
        fallback_notice="> 注：未识别标准总表，以下结论基于状态词降级统计。\n" if context["used_fallback"] else "",
    )
```

- [ ] **Step 6: 实现 CLI `main()` 和输出写文件**

```python
def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)
    template_path = Path(args.template)
    try:
        context = extract_report_context(input_path)
        markdown = render_report(context, template_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown, encoding="utf-8")
        print(f"已生成报告: {output_path}")
        return 0
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 7: 运行测试，确认新增实现通过**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -q`
Expected: PASS

---

### Task 3: 写固定 Markdown 模板，收敛输出章节

**Files:**
- Create: `docs/retrospective/templates/xlsx-test-report-template.md`
- Reference: `docs/retrospective/templates/retrospective-report-template.md`
- Test: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`

- [ ] **Step 1: 新建模板 frontmatter 与标题骨架**

```markdown
---
title: "{title}"
report_type: "summary"
source: "{source}"
format: "markdown"
date: "{date}"
status: "completed"
---

# {title}

{fallback_notice}
```

- [ ] **Step 2: 填写固定章节，确保和设计文档一致**

```markdown
## 结论摘要

- 发布判断: {release_decision}
- 发布门槛: {release_threshold}
- 当前差距: {release_gap}

## 基本信息

{basic_info_lines}

## 工作簿结构

{workbook_summary_lines}

## 总体结果

{overall_metrics_lines}

## 风险聚类

{risk_clusters_lines}

## 最终判断

{final_conclusion}
```

- [ ] **Step 3: 回跑渲染测试，确认模板可被脚本消费**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py::test_render_report_contains_required_sections -q`
Expected: PASS

---

### Task 4: 补齐模块结论、异常处理和真实样本验证

**Files:**
- Modify: `.agents/scripts/analyze-xlsx-test-report.py`
- Modify: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Verify: `d:\AI\.temp\【20260327】单目1M插值3M232测试报告.xlsx`

- [ ] **Step 1: 在脚本中补“重点模块结论”提取函数**

```python
def collect_module_findings(workbook) -> list[dict[str, str]]:
    findings = []
    for sheet in workbook.worksheets:
        counts = count_status_words(sheet)
        risk_count = counts["fail"] + counts["notest"] + counts["block"]
        if risk_count == 0:
            continue
        findings.append(
            {
                "sheet": sheet.title,
                "summary": f"发现 {risk_count} 条高风险状态，其中 FAIL={counts['fail']}、NT={counts['notest']}、Block={counts['block']}",
            }
        )
    return findings[:5]
```

- [ ] **Step 2: 把 `module_findings` 接入上下文和模板渲染**

```python
context["module_findings"] = collect_module_findings(workbook)
```

```python
module_findings_lines="\n".join(
    f"- {item['sheet']}: {item['summary']}" for item in context["module_findings"]
) or "- 未提取到重点模块结论",
```

```markdown
## 模块结论

{module_findings_lines}
```

- [ ] **Step 3: 增补错误处理测试，覆盖缺文件和非法工作簿**

```python
def test_extract_report_context_raises_for_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        report.extract_report_context(tmp_path / "missing.xlsx")


def test_cli_returns_nonzero_for_invalid_workbook(tmp_path):
    workbook_path = tmp_path / "broken.xlsx"
    workbook_path.write_text("not an xlsx", encoding="utf-8")
    output_path = tmp_path / "broken.md"

    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "analyze-xlsx-test-report.py"),
            "--input",
            str(workbook_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert result.returncode == 1
    assert not output_path.exists()
```

- [ ] **Step 4: 运行脚本处理真实样本**

Run: `python .agents/scripts/analyze-xlsx-test-report.py --input "d:\AI\.temp\【20260327】单目1M插值3M232测试报告.xlsx" --output "d:\AI\.temp\【20260327】单目1M插值3M232测试报告-脚本版学习报告.md"`
Expected: 退出码 `0`，生成 Markdown 文件，且包含 `## 结论摘要`、`## 模块结论`、`## 最终判断`

- [ ] **Step 5: 对真实输出做快速抽样核对**

Run: `GetDiagnostics(file:///d:/AI/.temp/%E3%80%9020260327%E3%80%91%E5%8D%95%E7%9B%AE1M%E6%8F%92%E5%80%BC3M232%E6%B5%8B%E8%AF%95%E6%8A%A5%E5%91%8A-%E8%84%9A%E6%9C%AC%E7%89%88%E5%AD%A6%E4%B9%A0%E6%8A%A5%E5%91%8A.md)`
Expected: 无诊断错误；人工抽样确认核心指标与此前人工报告大体一致

---

### Task 5: 收尾验证，确保不引入低级质量回退

**Files:**
- Verify: `.agents/scripts/analyze-xlsx-test-report.py`
- Verify: `.agents/scripts/tests/test_analyze_xlsx_test_report.py`
- Verify: `docs/retrospective/templates/xlsx-test-report-template.md`

- [ ] **Step 1: 跑脚本测试全集**

Run: `pytest .agents/scripts/tests/test_analyze_xlsx_test_report.py -q`
Expected: PASS

- [ ] **Step 2: 对新增脚本执行重复代码检测**

Run: `python .agents/scripts/check-duplication.py --path .agents/scripts --threshold 10`
Expected: 不新增跨文件重复块；若发现超过阈值的重复，再回到实现阶段抽共享函数

- [ ] **Step 3: 检查新增文件诊断**

Run: `GetDiagnostics(file:///d:/AI/.agents/scripts/analyze-xlsx-test-report.py)`
Expected: 无诊断错误

Run: `GetDiagnostics(file:///d:/AI/.agents/scripts/tests/test_analyze_xlsx_test_report.py)`
Expected: 无诊断错误

Run: `GetDiagnostics(file:///d:/AI/docs/retrospective/templates/xlsx-test-report-template.md)`
Expected: 无诊断错误

---

## 自检结论

### Spec 覆盖

- 设计文档要求新增 1 个脚本和 1 个模板：由 Task 2、Task 3 覆盖
- 设计文档要求支持标准总表识别与降级统计：由 Task 1、Task 2、Task 4 覆盖
- 设计文档要求覆盖错误处理与真实样本验证：由 Task 4 覆盖
- 设计文档要求形成可验证闭环：由 Task 5 覆盖

### 占位符扫描

- 计划未使用 `TODO`、`TBD`、`后续补充` 等占位词
- 所有新增文件路径、测试文件和验证命令已明确
- 所有关键步骤均给出了实际代码片段或精确命令

### 类型与命名一致性

- 计划统一使用 `extract_report_context()`、`render_report()`、`build_release_judgment()` 等函数名
- 测试文件、脚本文件、模板文件名称与设计文档一致
- `overall_metrics`、`risk_clusters`、`module_findings` 等字段在测试、实现和模板中保持同名
