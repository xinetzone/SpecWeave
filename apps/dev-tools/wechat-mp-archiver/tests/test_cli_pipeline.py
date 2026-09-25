"""CLI sync / run 命令测试（Task 9，全 mock，不触网）。

覆盖：参数接线（全量/增量/重试/限流/互动开关）、--full 显式确认门、
退出码 0/1/2/3/4、输出文案。
"""

import pytest

from mp_archiver.adapters.wechat_download_api import (
    AccountNotFoundError,
    EndpointDiscoveryError,
)
from mp_archiver.adapters.wechat_payload import CredentialExpiredError
from mp_archiver.core.article_archive import FetchItem, FetchReport
from mp_archiver.core.list_sync import SyncReport
from mp_archiver.core.pipeline import PipelineReport


def _cli_env(monkeypatch, tmp_path):
    from mp_archiver import cli as cli_module

    cli_module.get_settings.cache_clear()
    monkeypatch.setenv("MP_ARCHIVER_EXPORTER_TOKEN", "")
    monkeypatch.setenv("MP_ARCHIVER_DB_PATH", str(tmp_path / "cli.db"))
    monkeypatch.setenv("MP_ARCHIVER_ARCHIVE_ROOT", str(tmp_path / "arc"))
    monkeypatch.setenv("MP_ARCHIVER_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MIN", "0")
    monkeypatch.setenv("MP_ARCHIVER_REQUEST_DELAY_MAX", "0")


def _list_report(**overrides) -> SyncReport:
    base = dict(
        account_name="意识食谱", biz="BIZ==", pages=1, inserted=0, updated=0,
        skipped_non_article=0, hidden_marked=0, completed=True, final_offset=0,
    )
    base.update(overrides)
    return SyncReport(**base)


def _install_pipeline(monkeypatch, *, report=None, raises=None):
    """替换 cli.run_pipeline 并记录调用参数。"""
    from mp_archiver import cli as cli_module

    calls = []

    def fake_run_pipeline(conn, settings, account, **kwargs):
        calls.append({"account": account, **kwargs})
        if raises is not None:
            raise raises
        return report

    monkeypatch.setattr(cli_module, "run_pipeline", fake_run_pipeline)
    return calls


def _empty_fetch() -> FetchReport:
    return FetchReport(biz="BIZ==")


def test_sync_incremental_zero_new_exits_zero(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    report = PipelineReport(
        account="意识食谱", mode="incremental",
        list=_list_report(caught_up=True),
        fetch=_empty_fetch(),
    )
    calls = _install_pipeline(monkeypatch, report=report)

    code = cli_module.main(["sync", "-a", "意识食谱"])
    out = capsys.readouterr().out

    assert code == 0
    assert calls[0]["full"] is False
    assert calls[0]["include_failed"] is False
    assert "增量追平" in out and "新增 0" in out
    assert "没有符合条件的待采集文章" in out


def test_sync_with_limit_and_metrics(monkeypatch, tmp_path):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    fetch = FetchReport(
        biz="BIZ==", total=2, downloaded=2,
        interactions_collected=2, comments_collected=6,
    )
    report = PipelineReport(
        account="意识食谱", mode="incremental",
        list=_list_report(caught_up=True, pages=1, inserted=2),
        fetch=fetch,
    )
    calls = _install_pipeline(monkeypatch, report=report)

    code = cli_module.main([
        "sync", "-a", "意识食谱", "--limit", "3", "--fetch-metrics",
    ])
    assert code == 0
    assert calls[0]["fetch_limit"] == 3


def test_pipeline_fetch_aborted_exits_4_with_banner(monkeypatch, tmp_path, capsys):
    """sync/run 路径正文阶段熔断：横幅可见且退出码 4（Task 12 P2-8）。"""
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    fetch = FetchReport(
        biz="BIZ==",
        total=5,
        downloaded=0,
        failed=1,
        items=(FetchItem(
            article_id=7, title="风控篇", state="failed",
            error="[risk_control] 文章页 HTTP 403（疑似账号/IP 级风控）",
        ),),
        aborted=True,
        abort_reason="[risk_control] 文章页 HTTP 403（疑似账号/IP 级风控）",
        pending_in_account=4,
    )
    report = PipelineReport(
        account="意识食谱", mode="incremental",
        list=_list_report(caught_up=True),
        fetch=fetch,
    )
    _install_pipeline(monkeypatch, report=report)

    code = cli_module.main(["sync", "-a", "意识食谱"])
    out = capsys.readouterr().out

    assert code == 4
    assert "[abort]" in out
    assert "剩余 4 篇保持 pending" in out
    assert "重跑" in out


def test_run_requires_full_flag(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    calls = _install_pipeline(monkeypatch, report=None)

    code = cli_module.main(["run", "-a", "意识食谱"])
    out = capsys.readouterr().out
    assert code == 1 and "--full" in out
    assert calls == []  # 未确认时不执行编排


def test_run_full_success_with_reconcile(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    report = PipelineReport(
        account="意识食谱", mode="full",
        list=_list_report(pages=3, inserted=2, hidden_marked=1, completed=True),
        fetch=FetchReport(biz="BIZ==", total=2, downloaded=2),
    )
    calls = _install_pipeline(monkeypatch, report=report)

    code = cli_module.main([
        "run", "-a", "意识食谱", "--full", "--include-failed",
        "--no-reconcile",
    ])
    out = capsys.readouterr().out

    assert code == 0
    assert calls[0]["full"] is True
    assert calls[0]["include_failed"] is True
    assert calls[0]["no_reconcile"] is True
    assert "历史尾页" in out and "对账标记不可见 1" in out
    assert "元数据完整性" in out  # 全量到尾页后打印校验


def test_run_fetch_failure_exits_one(monkeypatch, tmp_path, capsys):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    report = PipelineReport(
        account="意识食谱", mode="incremental",
        list=_list_report(caught_up=True, inserted=1),
        fetch=FetchReport(
            biz="BIZ==", total=1, failed=1,
            items=(FetchItem(1, "坏文章", "failed", error="500 服务器错误"),),
        ),
    )
    _install_pipeline(monkeypatch, report=report)

    code = cli_module.main(["sync", "-a", "意识食谱"])
    out = capsys.readouterr().out
    assert code == 1 and "坏文章" in out and "500" in out


@pytest.mark.parametrize("exc,code", [
    (CredentialExpiredError(200013, "expired"), 2),
    (AccountNotFoundError("未找到公众号"), 3),
    (EndpointDiscoveryError("端点发现失败"), 4),
])
def test_sync_error_exit_codes(monkeypatch, tmp_path, capsys, exc, code):
    from mp_archiver import cli as cli_module

    _cli_env(monkeypatch, tmp_path)
    _install_pipeline(monkeypatch, raises=exc)
    assert cli_module.main(["sync", "-a", "x"]) == code
