"""CLI 各子命令测试（全 mock，不触网）。

覆盖：init-db / doctor / list / fetch / export-rag / report / resolve-biz /
sync-official / official-doctor 的正常路径与异常→退出码分支、输出文案、
参数接线与现场保留提示（AC-10 / TR-8.1）。
"""

import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import httpx
import pytest

from mp_archiver.adapters.health import ServiceProbe
from mp_archiver.adapters.official_api import (
    OfficialApiConfigError,
    OfficialApiPermissionError,
)
from mp_archiver.adapters.wechat_download_api import (
    AccountNotFoundError,
    BizUnavailableError,
    EndpointDiscoveryError,
)
from mp_archiver.adapters.wechat_payload import (
    ApiRetError,
    CredentialExpiredError,
    PayloadError,
)
from mp_archiver.core.article_archive import FetchItem, FetchReport
from mp_archiver.core.list_sync import SyncReport
from mp_archiver.core.official_probe import ProbeReport, StageResult
from mp_archiver.core.official_sync import OfficialSyncReport
from mp_archiver.core.pipeline import PipelineReport
from mp_archiver.exporters.rag import RagExportItem, RagExportReport
from mp_archiver.exporters.report import ReportData, ReportResult


def _cli_env(monkeypatch, tmp_path):
    """与 test_cli_pipeline 一致的 CLI 环境准备（隔离库/归档目录/日志/限速）。"""
    from mp_archiver import cli as cli_module

    cli_module.get_settings.cache_clear()
    monkeypatch.setenv("MP_ARCHIVER_EXPORTER_TOKEN", "")
    monkeypatch.setenv("MP_ARCHIVER_DB_PATH", str(tmp_path / "cli.db"))
    monkeypatch.setenv("MP_ARCHIVER_ARCHIVE_ROOT", str(tmp_path / "arc"))
    monkeypatch.setenv("MP_ARCHIVER_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MIN", "0")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MAX", "0")


def _fake_surface():
    return SimpleNamespace(
        search=SimpleNamespace(path="/api/searchbiz"),
        history=SimpleNamespace(path="/api/getmsg"),
    )


def _patch_adapter(monkeypatch, *, raises=None, surface=None):
    """替换 cli.WechatDownloadApiAdapter：build 返回带 surface 的假适配器或抛错。"""
    from mp_archiver import cli as cli_module

    surface = surface or _fake_surface()

    class _FakeAdapter:
        @staticmethod
        def build(client, *, base_url, search_override="", history_override=""):
            if raises is not None:
                raise raises
            return SimpleNamespace(surface=surface)

    monkeypatch.setattr(cli_module, "WechatDownloadApiAdapter", _FakeAdapter)


def _list_report(**overrides) -> SyncReport:
    base = dict(
        account_name="意识食谱", biz="BIZ==", pages=2, inserted=3, updated=1,
        skipped_non_article=0, hidden_marked=0, completed=True, final_offset=0,
    )
    base.update(overrides)
    return SyncReport(**base)


def _install(monkeypatch, name, *, returns=None, raises=None, calls=None):
    """将 cli 模块内符号替换为返回固定值/抛指定异常的假函数。"""
    from mp_archiver import cli as cli_module

    def fake(*args, **kwargs):
        if calls is not None:
            calls.append((args, kwargs))
        if raises is not None:
            raise raises
        return returns

    monkeypatch.setattr(cli_module, name, fake)
    return fake


# ---- init-db ---------------------------------------------------------

def test_init_db_creates_five_tables(monkeypatch, tmp_path, capsys):
    """init-db 退出 0，且 articles/media/comments/metrics/sync_state 五表存在。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    assert cli_module.main(["init-db"]) == 0
    assert "数据库已初始化" in capsys.readouterr().out

    conn = cli_module.connect(tmp_path / "cli.db")
    tables = {
        row["name"]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    }
    conn.close()
    assert {"articles", "media", "comments", "metrics", "sync_state"} <= tables


# ---- doctor ----------------------------------------------------------

def test_doctor_local_ok_service_up(monkeypatch, tmp_path, capsys):
    """本地自检通过 + 采集服务在线（含能力路径）→ 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "probe_service", returns=ServiceProbe(
        "up", "OpenAPI 文档可访问", ("/api/login", "/api/searchbiz"),
    ))

    assert cli_module.main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert "本地环境自检通过" in out
    assert "- /api/login" in out
    assert "SQLite 可用" in out and "归档目录可写" in out


@pytest.mark.parametrize("probe,expect", [
    (ServiceProbe("auth_required", "服务在线但需要授权：/health 返回 401"),
     "采集服务需要授权"),
    (ServiceProbe("down", "无法连接 http://127.0.0.1:5000"),
     "采集服务未响应"),
])
def test_doctor_service_unavailable_only_warns(monkeypatch, tmp_path, capsys,
                                               probe, expect):
    """采集服务不可达/需授权：仅告警，本地结论不受影响 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "probe_service", returns=probe)

    assert cli_module.main(["doctor"]) == 0
    out = capsys.readouterr().out
    assert expect in out
    assert "本地环境自检通过" in out


def test_doctor_local_failure_exits_one(monkeypatch, tmp_path, capsys):
    """数据库不可用等本地检查失败 → 退出 1 并汇总问题数。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "connect", raises=OSError("disk full"))
    _install(monkeypatch, "probe_service", returns=ServiceProbe("up", "在线"))

    assert cli_module.main(["doctor"]) == 1
    out = capsys.readouterr().out
    assert "数据库不可用" in out and "doctor 发现 1 项问题" in out


def test_doctor_archive_dir_not_writable_exits_one(monkeypatch, tmp_path, capsys):
    """归档目录不可写（被同名文件占用）→ 计入失败并退出 1。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    (tmp_path / "arc").write_text("occupied", encoding="utf-8")  # mkdir 将失败
    _install(monkeypatch, "probe_service", returns=ServiceProbe("up", "在线"))

    assert cli_module.main(["doctor"]) == 1
    out = capsys.readouterr().out
    assert "归档目录不可写" in out and "doctor 发现 1 项问题" in out


# ---- list ------------------------------------------------------------

def test_list_success_prints_endpoints_and_completeness(monkeypatch, tmp_path,
                                                        capsys):
    """列表同步成功：端点发现输出、完成文案、元数据完整性行 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _patch_adapter(monkeypatch)
    calls = []
    _install(monkeypatch, "sync_article_list",
             returns=_list_report(completed=True), calls=calls)

    assert cli_module.main(["list", "-a", "意识食谱", "--max-pages", "3"]) == 0
    out = capsys.readouterr().out
    assert "端点已发现：search=/api/searchbiz，history=/api/getmsg" in out
    assert "已到达历史尾页" in out and "元数据完整性" in out
    _, kwargs = calls[0]
    assert kwargs["max_pages"] == 3 and kwargs["full_reconcile"] is True


def test_list_truncated_warns_no_reconcile(monkeypatch, tmp_path, capsys):
    """--no-reconcile/截断：未达尾页提示；同时验证 full_reconcile 接线为 False。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _patch_adapter(monkeypatch)
    calls = []
    _install(monkeypatch, "sync_article_list",
             returns=_list_report(completed=False), calls=calls)

    assert cli_module.main(["list", "-a", "意识食谱", "--no-reconcile"]) == 0
    out = capsys.readouterr().out
    assert "未到达历史尾页" in out
    _, kwargs = calls[0]
    assert kwargs["full_reconcile"] is False


@pytest.mark.parametrize("exc,code", [
    (CredentialExpiredError(200013, "expired"), 2),
    (AccountNotFoundError("未找到公众号"), 3),
    (BizUnavailableError("拿不到 biz"), 4),
    (EndpointDiscoveryError("端点发现失败"), 4),
    (ApiRetError(3, "服务异常"), 1),
    (PayloadError("响应不是 JSON"), 1),
    (httpx.TimeoutException("timed out"), 4),
])
def test_list_error_exit_codes(monkeypatch, tmp_path, capsys, exc, code):
    """list 各异常→退出码映射（含登录态失效/账号不存在/端点失败/返回异常/超时）。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _patch_adapter(monkeypatch, raises=exc)
    assert cli_module.main(["list", "-a", "x"]) == code


# ---- fetch -----------------------------------------------------------

def test_fetch_success_with_limit_and_metrics(monkeypatch, tmp_path, capsys):
    """fetch 成功：--limit 范围文案、成功计数、互动数据行 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    calls = []
    report = FetchReport(
        biz="BIZ==", total=2, downloaded=2,
        interactions_collected=2, comments_collected=7, interactions_skipped=1,
    )
    _install(monkeypatch, "fetch_articles", returns=report, calls=calls)

    assert cli_module.main([
        "fetch", "-a", "意识食谱", "--limit", "2", "--fetch-metrics",
    ]) == 0
    out = capsys.readouterr().out
    assert "（最多 2 篇）" in out and "含互动数据采集" in out
    assert "成功 2" in out and "评论 7 条" in out
    assert calls[0][1]["limit"] == 2


def test_fetch_no_pending_exits_zero(monkeypatch, tmp_path, capsys):
    """无待采集文章：直接提示并退出 0（不再打印计数明细）。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "fetch_articles", returns=FetchReport(biz="BIZ=="))

    assert cli_module.main(["fetch", "-a", "意识食谱"]) == 0
    assert "没有符合条件的待采集文章" in capsys.readouterr().out


def test_fetch_failed_and_image_failures(monkeypatch, tmp_path, capsys):
    """存在失败条目：逐篇 [fail] 输出、图片失败告警 → 退出 1。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    report = FetchReport(
        biz="BIZ==", total=3, downloaded=1, failed=1, skipped=1, image_failures=2,
        items=(
            FetchItem(1, "坏文章", "failed", error="500 服务器错误"),
            FetchItem(2, "已删文章", "skipped", error="content_deleted"),
        ),
    )
    _install(monkeypatch, "fetch_articles", returns=report)

    assert cli_module.main(["fetch", "-a", "意识食谱"]) == 1
    out = capsys.readouterr().out
    assert "[fail] 坏文章：500 服务器错误" in out
    assert "[skip] 已删文章：content_deleted" in out
    assert "2 张正文图片下载失败" in out


def test_fetch_aborted_prints_banner_with_limit_note(monkeypatch, tmp_path,
                                                     capsys):
    """熔断中止：abort 横幅 + 现场保留提示 + --limit 未选入注记 → 退出 4。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    report = FetchReport(
        biz="BIZ==", total=5, downloaded=1, failed=1, aborted=True,
        abort_reason="[risk_control] 文章页 HTTP 403",
        pending_in_account=9,
        items=(FetchItem(1, "风控篇", "failed", error="403"),),
    )
    _install(monkeypatch, "fetch_articles", returns=report)

    assert cli_module.main(["fetch", "-a", "意识食谱", "--limit", "5"]) == 4
    out = capsys.readouterr().out
    assert "[abort] 批次提前中止" in out
    assert "剩余 4 篇保持 pending 未发请求" in out
    assert "另有 5 篇 pending 本批未选入" in out
    assert "现场已保留" in out


def test_fetch_unknown_account_exits_three(monkeypatch, tmp_path, capsys):
    """账号 LookupError（未执行 list）→ 退出 3。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "fetch_articles", raises=LookupError("未找到公众号"))

    assert cli_module.main(["fetch", "-a", "不存在的号"]) == 3
    assert "未找到公众号" in capsys.readouterr().out


# ---- sync/run 编排异常分支（补齐 pipeline 未覆盖的退出码） -----------

@pytest.mark.parametrize("exc,code", [
    (LookupError("未找到公众号"), 3),
    (ApiRetError(3, "服务异常"), 1),
    (PayloadError("解析失败"), 1),
    (httpx.TransportError("connect failed"), 4),
    (BizUnavailableError("无 biz"), 4),
])
def test_pipeline_error_exit_codes(monkeypatch, tmp_path, exc, code):
    """run_pipeline 抛异常时 sync 命令的退出码映射（LookupError/返回异常/传输错误）。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "run_pipeline", raises=exc)
    assert cli_module.main(["sync", "-a", "x"]) == code


def test_pipeline_summary_prints_image_failures_and_skipped(monkeypatch,
                                                            tmp_path, capsys):
    """sync/run 正文阶段摘要：图片失败告警与逐篇 [skip] 行 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    report = PipelineReport(
        account="意识食谱", mode="incremental",
        list=_list_report(caught_up=True),
        fetch=FetchReport(
            biz="BIZ==", total=2, downloaded=1, skipped=1, image_failures=1,
            items=(FetchItem(1, "已删文章", "skipped", error="content_deleted"),),
        ),
    )
    _install(monkeypatch, "run_pipeline", returns=report)

    assert cli_module.main(["sync", "-a", "意识食谱"]) == 0
    out = capsys.readouterr().out
    assert "1 张正文图片下载失败" in out
    assert "[skip] 已删文章：content_deleted" in out


# ---- sync-official ---------------------------------------------------

def test_sync_official_not_configured_skips(monkeypatch, tmp_path, capsys):
    """未配置 AppID/AppSecret：官方源跳过且无请求 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    assert cli_module.main(["sync-official", "-a", "意识食谱"]) == 0
    out = capsys.readouterr().out
    assert "官方源不启用（无请求发出）" in out


def test_sync_official_success_with_quota_reached(monkeypatch, tmp_path, capsys):
    """配置完整且同步成功、配额触顶：打印统计与次日再同步提示 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    monkeypatch.setenv("MP_ARCHIVER_WECHAT_APP_ID", "wx0123456789abcdef")
    monkeypatch.setenv("MP_ARCHIVER_WECHAT_APP_SECRET", "0" * 32)
    _install(monkeypatch, "sync_official_articles", returns=OfficialSyncReport(
        biz="BIZ==", pages=1, inserted=2, updated=1,
        skipped_deleted=0, total_groups=3, quota_reached=True,
    ))

    assert cli_module.main(["sync-official", "-a", "意识食谱"]) == 0
    out = capsys.readouterr().out
    assert "官方源同步完成（biz=BIZ==）" in out and "新增 2" in out
    assert "已达当日调用安全阈值" in out


def _official_env(monkeypatch, tmp_path):
    """配置完整的官方源环境，供 sync-official 异常分支测试复用。"""
    _cli_env(monkeypatch, tmp_path)
    monkeypatch.setenv("MP_ARCHIVER_WECHAT_APP_ID", "wx0123456789abcdef")
    monkeypatch.setenv("MP_ARCHIVER_WECHAT_APP_SECRET", "0" * 32)


def test_sync_official_permission_denied_warns_exits_zero(monkeypatch, tmp_path,
                                                          capsys):
    """48001 无权限：仅告警、官方源自动停用 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _official_env(monkeypatch, tmp_path)
    _install(monkeypatch, "sync_official_articles",
             raises=OfficialApiPermissionError("errcode=48001"))

    assert cli_module.main(["sync-official", "-a", "意识食谱"]) == 0
    out = capsys.readouterr().out
    assert "官方接口无权限" in out and "48001" in out


def test_sync_official_config_error_exits_three(monkeypatch, tmp_path, capsys):
    """无法解析 biz 等配置错误 → 退出 3。"""
    from mp_archiver import cli as cli_module

    _official_env(monkeypatch, tmp_path)
    _install(monkeypatch, "sync_official_articles",
             raises=OfficialApiConfigError("无 biz"))

    assert cli_module.main(["sync-official", "-a", "意识食谱"]) == 3
    assert "无 biz" in capsys.readouterr().out


@pytest.mark.parametrize("ret,hint", [
    (40164, "IP 加入白名单"),
    (40125, "AppSecret 是否正确"),
    (45009, "频率/配额限制"),
    (40013, ""),
])
def test_sync_official_api_ret_hints(monkeypatch, tmp_path, capsys, ret, hint):
    """官方接口 ret 分支：40164/40125/45009 给出对应处置提示 → 退出 4。"""
    from mp_archiver import cli as cli_module

    _official_env(monkeypatch, tmp_path)
    _install(monkeypatch, "sync_official_articles",
             raises=ApiRetError(ret, "boom"))

    assert cli_module.main(["sync-official", "-a", "意识食谱"]) == 4
    out = capsys.readouterr().out
    assert f"ret={ret}" in out
    if hint:
        assert hint in out


@pytest.mark.parametrize("exc,expect", [
    (PayloadError("响应无法解析"), "官方接口响应无法解析"),
    (json.JSONDecodeError("bad json", "", 0), "官方接口返回非 JSON 内容"),
    (httpx.TimeoutException("timed out"), "无法连接官方接口：TimeoutException"),
    (httpx.TransportError("connect failed"), "无法连接官方接口：TransportError"),
])
def test_sync_official_parse_and_transport_errors(monkeypatch, tmp_path,
                                                  capsys, exc, expect):
    """解析失败/非 JSON/传输错误 → 退出 4，且错误分类文案各自可辨。"""
    from mp_archiver import cli as cli_module

    _official_env(monkeypatch, tmp_path)
    _install(monkeypatch, "sync_official_articles", raises=exc)

    assert cli_module.main(["sync-official", "-a", "意识食谱"]) == 4
    out = capsys.readouterr().out
    assert expect in out  # 四类异常各自对应专属文案，非笼统的 "[fail]"


# ---- official-doctor -------------------------------------------------

def test_official_doctor_network_only_ok(monkeypatch, tmp_path, capsys):
    """--network-only 网络预检通过 → 退出 0 并提示后续完整探针。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "probe_network",
             returns=StageResult("network", "ok", "链路可达", ("细节一",)))

    assert cli_module.main(["official-doctor", "--network-only"]) == 0
    out = capsys.readouterr().out
    assert "[ok] [network] 链路可达" in out and "- 细节一" in out
    assert "网络预检通过" in out


def test_official_doctor_full_probe_passed(monkeypatch, tmp_path, capsys):
    """完整探针全部阶段通过 → 退出 0 并给出正式同步引导。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    report = ProbeReport(stages=[
        StageResult("config", "ok", "配置正常"),
        StageResult("batchget", "ok", "首页探测成功"),
    ])
    _install(monkeypatch, "run_full_probe", returns=report)

    assert cli_module.main(["official-doctor", "-a", "意识食谱"]) == 0
    out = capsys.readouterr().out
    assert "全部阶段通过" in out and "sync-official -a 意识食谱" in out


def test_official_doctor_warn_exits_zero(monkeypatch, tmp_path, capsys):
    """存在告警阶段：提示链路未完全确认 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    report = ProbeReport(stages=[StageResult("token", "warn", "形态异常")])
    _install(monkeypatch, "run_full_probe", returns=report)

    assert cli_module.main(["official-doctor", "-a", "意识食谱"]) == 0
    assert "1 个告警" in capsys.readouterr().out


def test_official_doctor_fail_exits_one(monkeypatch, tmp_path, capsys):
    """存在失败阶段：汇总失败数 → 退出 1。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    report = ProbeReport(stages=[
        StageResult("config", "fail", "未配置 AppID"),
        StageResult("network", "ok", "链路可达"),
    ])
    _install(monkeypatch, "run_full_probe", returns=report)

    assert cli_module.main(["official-doctor", "-a", "意识食谱"]) == 1
    assert "1 个阶段失败" in capsys.readouterr().out


# ---- export-rag ------------------------------------------------------

def test_export_rag_with_raw_and_failures(monkeypatch, tmp_path, capsys):
    """--with-raw 追加字段提示与逐篇 [fail]、汇总告警 → 退出 1。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "get_account_biz_by_alias", returns="BIZ==")
    out_path = tmp_path / "exports" / "rag.jsonl"
    report = RagExportReport(
        out_path=out_path, total=3, exported=2, empty_text=1, failed=1,
        cleaned=False, with_raw=True, removed_noise_lines=4,
        collapsed_duplicates=1, trimmed_tail_lines=2,
        items=(RagExportItem(9, "缺失文章", "failed", error="文件不存在"),),
    )
    calls = []
    _install(monkeypatch, "export_rag_jsonl", returns=report, calls=calls)

    assert cli_module.main([
        "export-rag", "-a", "意识食谱", "--no-clean", "--with-raw",
    ]) == 1
    out = capsys.readouterr().out
    assert "原文（不清洗）" in out
    assert "[ok] 已追加 text_raw 字段" in out
    assert "[fail] 缺失文章：文件不存在" in out
    assert "存在读取失败条目" in out
    assert calls[0][1]["account_biz"] == "BIZ=="
    assert calls[0][1]["clean"] is False and calls[0][1]["with_raw"] is True


def test_export_rag_unknown_account_exits_three(monkeypatch, tmp_path, capsys):
    """指定账号在库中不存在 → 退出 3。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    assert cli_module.main(["export-rag", "-a", "查无此号"]) == 3
    assert "未找到公众号" in capsys.readouterr().out


# ---- report ----------------------------------------------------------

def test_report_without_downloaded_shows_placeholder(monkeypatch, tmp_path,
                                                     capsys):
    """无已归档文章：原创占比显示「无数据」、音视频显示占位文案 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    calls = []
    result = ReportResult(
        html_path=tmp_path / "report" / "report.html",
        csv_path=tmp_path / "report" / "report.csv",
        data=ReportData(account_label="全部账号", total_articles=3,
                        timed_articles=0, missing_time=3, downloaded_total=0),
    )
    _install(monkeypatch, "generate_report", returns=result, calls=calls)

    assert cli_module.main(["report"]) == 0
    out = capsys.readouterr().out
    assert "无数据" in out and "暂无已归档文章" in out
    assert "report.html" in out and "report.csv" in out
    assert calls[0][1]["account_biz"] is None and calls[0][1]["top_n"] == 10


def test_report_with_downloaded_shows_av_ratio(monkeypatch, tmp_path, capsys):
    """有已归档文章：打印含音视频占比明细 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "get_account_biz_by_alias", returns="BIZ==")
    calls = []
    result = ReportResult(
        html_path=tmp_path / "r.html", csv_path=tmp_path / "r.csv",
        data=ReportData(account_label="意识食谱", total_articles=4,
                        timed_articles=3, missing_time=1, original_count=2,
                        downloaded_total=2, with_audio=1, with_video=1,
                        with_av=1),
    )
    _install(monkeypatch, "generate_report", returns=result, calls=calls)

    assert cli_module.main(["report", "-a", "意识食谱", "--top", "5"]) == 0
    out = capsys.readouterr().out
    assert "含音视频 1/2 篇" in out and "原创占比 66.7%" in out
    assert calls[0][1]["account_biz"] == "BIZ==" and calls[0][1]["top_n"] == 5


def test_report_unknown_account_exits_three(monkeypatch, tmp_path, capsys):
    """指定账号在库中不存在 → 退出 3。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    assert cli_module.main(["report", "-a", "查无此号"]) == 3
    assert "未找到公众号" in capsys.readouterr().out


# ---- resolve-biz -----------------------------------------------------

def test_resolve_biz_prints_identity_and_env_line(monkeypatch, tmp_path,
                                                  capsys):
    """解析成功：打印来源、biz 两种形态、脱敏 mid/sn 与 .env 待填行 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "resolve_article_identity", returns={
        "biz": "MzAxMjM0NTY3OA==", "mid": "1000000001",
        "idx": "1", "sn": "abcdef123456", "source": "页面 og:url",
    })

    assert cli_module.main([
        "resolve-biz", "https://mp.weixin.qq.com/s/abc",
    ]) == 0
    out = capsys.readouterr().out
    assert "提取来源：页面 og:url" in out
    assert "MP_ARCHIVER_WECHAT_OFFICIAL_BIZ=MzAxMjM0NTY3OA%3D%3D" in out
    assert "mid=1000000001 idx=1 sn=abcd…（已脱敏）" in out


def test_resolve_biz_without_mid_skips_desensitized_line(monkeypatch, tmp_path,
                                                         capsys):
    """仅提取到 biz（无 mid）：不打印脱敏参数行 → 退出 0。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "resolve_article_identity", returns={
        "biz": "MzAxMjM0NTY3OA==", "mid": "", "idx": "", "sn": "",
        "source": "页面 var biz",
    })

    assert cli_module.main(["resolve-biz", "https://mp.weixin.qq.com/s/x"]) == 0
    out = capsys.readouterr().out
    assert "提取来源：页面 var biz" in out
    assert "已脱敏" not in out


@pytest.mark.parametrize("exc", [
    PayloadError("无法提取 __biz"),
    RuntimeError("connection reset"),
])
def test_resolve_biz_failure_exits_four(monkeypatch, tmp_path, capsys, exc):
    """解析失败（PayloadError 或传输类异常）→ 退出 4。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install(monkeypatch, "resolve_article_identity", raises=exc)

    assert cli_module.main(["resolve-biz", "https://mp.weixin.qq.com/s/y"]) == 4
    assert "[fail]" in capsys.readouterr().out


# ---- __main__ 入口 ---------------------------------------------------

def test_python_m_module_entrypoint_returns_exit_code(monkeypatch, tmp_path, capsys):
    """`python -m mp_archiver` 入口：子命令返回值经 `raise SystemExit(main())` 转为退出码。

    刻意不用 ``--help``：argparse 会在 ``main()`` 内部就抛 SystemExit，包装行
    ``raise SystemExit(main())`` 的「int 返回值 → 退出码」路径永远走不到，
    即便把该行改成裸 ``main()`` 用例也照样通过。此处改用真正返回 0 的子命令，
    使包装行的语义（返回值即退出码）被真实锁定。
    """
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    monkeypatch.setattr(sys, "argv", ["mp-archiver", "init-db"])
    with pytest.raises(SystemExit) as ei:
        runpy.run_module("mp_archiver", run_name="__main__")

    assert ei.value.code == 0
    assert (tmp_path / "cli.db").is_file()  # 子命令副作用真实发生
    assert "数据库已初始化" in capsys.readouterr().out