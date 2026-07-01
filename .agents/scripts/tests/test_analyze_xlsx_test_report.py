"""analyze-xlsx-test-report.py 的失败测试。"""

import importlib.util
import subprocess
import sys
from pathlib import Path

import openpyxl
import pytest


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "analyze-xlsx-test-report.py"


def load_report_module():
    """按未来脚本路径动态加载模块，当前阶段应因脚本缺失而失败。"""
    spec = importlib.util.spec_from_file_location("analyze_xlsx_test_report", SCRIPT_PATH)
    if spec is None or spec.loader is None or not SCRIPT_PATH.exists():
        raise FileNotFoundError(f"脚本不存在: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def build_realistic_overview_workbook(path: Path) -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "测试报告"
    ws.append(["232单目1M插值3M测试报告"])
    ws.append(["基本信息"])
    ws.append(["设备型号", "232单目"])
    ws.append(["固件版本", "[仅供测试]demo.zip"])
    ws.append(["APP", "小强当家5.0.0.65"])
    ws.append(["测试人员", "李翠"])
    ws.append(["测试完成时间", "2026-04-02"])
    ws.append(["测试结果", "新增用例", "", "所有用例", 489])
    ws.append(["", "Pass", "", "Pass", 380])
    ws.append(["", "Fail", "", "Fail", 26])
    ws.append(["", "NoTest", "", "NoTest", 70])
    ws.append(["", "Block", "", "Block", 13])
    ws.append(["", "新增致命问题", "", "所有致命问题", 0])
    ws.append(["", "新增严重问题", "", "所有严重问题", 11])
    ws.append(["", "最终结果", "", "DI值", 35])

    audio = wb.create_sheet("06音频专项测试")
    audio.append(["模块", "现象", "状态"])
    audio.append(["音频", "底噪明显", "FAIL"])
    audio.append(["音频", "回声轻微", "FAIL"])

    wifi = wb.create_sheet("WiFi穿墙测试")
    wifi.append(["点位", "现象", "状态"])
    wifi.append(["点7", "拉流卡顿", "FAIL"])

    wb.save(path)
    return path


def test_extract_report_context_with_standard_overview(tmp_path) -> None:
    report = load_report_module()
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


def test_extract_report_context_with_realistic_overview_layout(tmp_path) -> None:
    report = load_report_module()
    workbook_path = build_realistic_overview_workbook(tmp_path / "realistic.xlsx")

    context = report.extract_report_context(workbook_path)

    assert context["used_fallback"] is False
    assert context["overall_metrics"]["total_cases"] == 489
    assert context["overall_metrics"]["pass"] == 380
    assert context["overall_metrics"]["fail"] == 26
    assert context["overall_metrics"]["notest"] == 70
    assert context["overall_metrics"]["block"] == 13
    assert context["overall_metrics"]["di"] == 35
    assert context["overall_metrics"]["serious_issues"] == 11
    assert context["release_judgment"]["decision"] == "不建议发布"


def test_extract_report_context_falls_back_to_status_scan(tmp_path) -> None:
    report = load_report_module()
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


def test_render_report_contains_required_sections() -> None:
    report = load_report_module()
    context = {
        "title": "示例报告",
        "source": "sample.xlsx",
        "date": "2026-07-01",
        "basic_info": {"项目": "IPC-232"},
        "workbook_summary": {"sheet_count": 2, "sheets": [{"name": "测试报告", "role": "总表"}]},
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
            "gap": "DI 和严重问题数均超标",
        },
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


def test_cli_writes_markdown_output(tmp_path) -> None:
    workbook_path = build_standard_workbook(tmp_path / "cli.xlsx")
    output_path = tmp_path / "report.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
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
    content = output_path.read_text(encoding="utf-8")
    assert "示例报告" not in content
    assert "## 最终判断" in content


def test_extract_report_context_raises_for_missing_file(tmp_path) -> None:
    report = load_report_module()

    with pytest.raises(FileNotFoundError):
        report.extract_report_context(tmp_path / "missing.xlsx")


def test_cli_returns_nonzero_for_invalid_workbook(tmp_path) -> None:
    workbook_path = tmp_path / "broken.xlsx"
    workbook_path.write_text("not an xlsx", encoding="utf-8")
    output_path = tmp_path / "broken.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
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
    assert "无法读取工作簿" in result.stderr
    assert not output_path.exists()


def test_render_release_summary_function_is_exposed() -> None:
    report = load_report_module()
    assert hasattr(report, "render_release_summary"), "功能缺失: render_release_summary 未实现"


def test_cli_supports_summary_output_and_summary_only_flags(tmp_path) -> None:
    workbook_path = build_standard_workbook(tmp_path / "cli-summary.xlsx")
    output_path = tmp_path / "full.md"
    summary_output = tmp_path / "summary.md"

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--input",
            str(workbook_path),
            "--output",
            str(output_path),
            "--summary-output",
            str(summary_output),
            "--summary-only",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert (
        result.returncode == 0
    ), f"参数未实现: CLI 未支持 --summary-output/--summary-only (stderr={result.stderr.strip()})"
    assert summary_output.exists()
    assert not output_path.exists()
