"""``mp-archiver`` 命令行入口。"""

import argparse
import json
import platform
import sys
from pathlib import Path

import httpx
from pydantic import SecretStr

from . import __version__
from .adapters.health import probe_service
from .adapters.wechat_download_api import (
    AccountNotFoundError,
    BizUnavailableError,
    EndpointDiscoveryError,
    WechatDownloadApiAdapter,
)
from .adapters.wechat_payload import (
    ApiRetError,
    CredentialExpiredError,
    PayloadError,
)
from .adapters.official_api import (
    OfficialApiConfigError,
    OfficialApiPermissionError,
)
from .config import get_settings
from .core.article_archive import fetch_articles
from .core.list_sync import sync_article_list
from .core.official_probe import (
    probe_network,
    resolve_article_identity,
    run_full_probe,
)
from .core.official_sync import sync_official_articles
from .core.pipeline import run_pipeline
from .core.validation import check_metadata_completeness
from .db import connect, get_account_biz_by_alias, init_db
from .exporters.rag import export_rag_jsonl
from .exporters.report import generate_report
from .http_client import RateLimitedClient
from .logging_utils import configure_logging, redact


def _cmd_init_db(args: argparse.Namespace) -> int:
    settings = get_settings()
    conn = connect(settings.db_path)
    init_db(conn)
    print(f"[ok] 数据库已初始化：{settings.db_path}")
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    failures = 0

    print(f"mp-archiver {__version__}")
    print(f"[ok] Python {platform.python_version()} on {platform.system()}")
    print(f"[ok] 配置已加载（日志级别 {settings.log_level}，互动数据采集：{settings.fetch_metrics}）")

    try:
        conn = connect(settings.db_path)
        init_db(conn)
        print(f"[ok] SQLite 可用：{settings.db_path}")
    except OSError as exc:
        failures += 1
        print(f"[fail] 数据库不可用：{exc}")

    try:
        settings.archive_root.mkdir(parents=True, exist_ok=True)
        probe = settings.archive_root / ".write-probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        print(f"[ok] 归档目录可写：{settings.archive_root}")
    except OSError as exc:
        failures += 1
        print(f"[fail] 归档目录不可写：{exc}")

    # 采集服务连通性探测（服务未部署时仅告警，不影响本地环境结论）
    print(f"[..] 探测采集服务：{settings.exporter_url}")
    probe = probe_service(
        settings.exporter_url,
        token=settings.exporter_token.get_secret_value(),
        timeout=min(settings.timeout, 8.0),
        proxy=settings.proxy_url,
    )
    if probe.status == "up":
        print(f"[ok] 采集服务在线：{probe.detail}")
        if probe.capabilities:
            print("     OpenAPI 暴露的相关能力路径（适配器对接依据）：")
            for capability in probe.capabilities:
                print(f"       - {capability}")
        print("[warn] 登录态/目标号搜索/首页列表验证需扫码授权，见 deploy/README.md；账号级检查随 Task 4 适配器落地")
    elif probe.status == "auth_required":
        print(f"[warn] 采集服务需要授权（{probe.detail}）；请按 deploy/README.md 扫码登录或配置 Token")
    else:
        print(f"[warn] 采集服务未响应：{probe.detail}")
        print("       尚未部署或未启动时可忽略；启动方式见 deploy/README.md")

    if failures:
        print(f"[fail] doctor 发现 {failures} 项问题")
        return 1
    print("[ok] 本地环境自检通过")
    return 0


def _cmd_list(args: argparse.Namespace) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    conn = connect(settings.db_path)
    init_db(conn)

    print(f"[..] 连接采集服务并发现端点：{settings.exporter_url}")
    try:
        with RateLimitedClient(settings) as client:
            adapter = WechatDownloadApiAdapter.build(
                client,
                base_url=settings.exporter_url,
                search_override=settings.exporter_search_path,
                history_override=settings.exporter_history_path,
            )
            print(
                "[ok] 端点已发现："
                f"search={adapter.surface.search.path}，"
                f"history={adapter.surface.history.path}"
            )
            print(f"[..] 开始同步公众号：{args.account}")
            report = sync_article_list(
                conn,
                adapter,
                name=args.account,
                max_pages=args.max_pages,
                full_reconcile=not args.no_reconcile,
            )
    except CredentialExpiredError as exc:
        print(f"[fail] 登录态失效：{exc}")
        print("       请按 deploy/README.md 第 3/5 节用专用订阅号重新扫码")
        return 2
    except AccountNotFoundError as exc:
        print(f"[fail] {exc}")
        return 3
    except BizUnavailableError as exc:
        print(f"[fail] {exc}")
        return 4
    except EndpointDiscoveryError as exc:
        print(f"[fail] 端点发现失败：{exc}")
        return 4
    except (ApiRetError, PayloadError) as exc:
        print(f"[fail] 采集服务返回异常：{exc}")
        return 1
    except (httpx.TimeoutException, httpx.TransportError) as exc:
        print(f"[fail] 无法连接采集服务：{exc.__class__.__name__}: {exc}")
        print("       请确认容器已启动（docker compose ps），详见 deploy/README.md")
        return 4

    print(
        f"[ok] 同步完成：{report.account_name}（biz={report.biz}）"
        f" 翻页 {report.pages}，新增 {report.inserted}，更新 {report.updated}，"
        f"跳过非图文 {report.skipped_non_article}"
    )
    if report.completed:
        print(f"[ok] 已到达历史尾页；对账标记不可见文章 {report.hidden_marked} 篇")
    else:
        print("[warn] 因 max-pages 截断，未到达历史尾页，本次未执行下架对账")

    completeness = check_metadata_completeness(conn, report.biz)
    rates = "，".join(f"{k} 非空率 {v:.1%}" for k, v in completeness.rates().items())
    tag = "[ok]" if completeness.ok else "[warn]"
    print(f"{tag} 元数据完整性（共 {completeness.total} 篇）：{rates}")
    return 0


def _cmd_fetch(args: argparse.Namespace) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    conn = connect(settings.db_path)
    init_db(conn)

    # 直连微信图床/文章页：剥离仅属于本地采集服务的 Bearer Token，
    # 避免把本地凭证发送到 mp.weixin.qq.com 域
    public_settings = settings.model_copy(update={"exporter_token": SecretStr("")})
    if args.fetch_metrics:
        public_settings = public_settings.model_copy(update={"fetch_metrics": True})
    scope = f"（最多 {args.limit} 篇）" if args.limit else ""
    metric_scope = "，含互动数据采集" if public_settings.fetch_metrics else ""
    print(f"[..] 归档公众号「{args.account}」待采集文章{scope}{metric_scope}")
    try:
        with RateLimitedClient(public_settings) as client:
            report = fetch_articles(
                conn,
                client,
                args.account,
                settings.archive_root,
                include_failed=args.include_failed,
                limit=args.limit,
                settings=public_settings,
            )
    except LookupError as exc:
        print(f"[fail] {exc}")
        return 3

    if report.total == 0:
        print("[ok] 没有符合条件的待采集文章（已全部归档或尚未执行 list）")
        return 0
    print(
        f"[ok] 归档结束：共 {report.total} 篇，成功 {report.downloaded}，"
        f"跳过 {report.skipped}（已删除/违规），失败 {report.failed}"
    )
    if public_settings.fetch_metrics:
        print(
            f"[ok] 互动数据：采集成功 {report.interactions_collected} 篇、"
            f"评论 {report.comments_collected} 条；"
            f"缺凭证跳过 {report.interactions_skipped} 篇；"
            f"失败 {report.interactions_failed} 篇"
            + ("（失败不影响正文归档，可稍后重跑）" if report.interactions_failed else "")
        )
    if report.image_failures:
        print(
            f"[warn] {report.image_failures} 张正文图片下载失败，"
            "已在各文章 metadata.json 登记例外并保留远程引用，可稍后重跑 fetch 补齐"
        )
    for item in report.items:
        if item.state == "failed":
            print(f"  [fail] {item.title}：{item.error}")
        elif item.state == "skipped":
            print(f"  [skip] {item.title}：{item.error}")
    return 1 if report.failed else 0


def _print_fetch_summary(report, *, metrics_enabled: bool) -> None:
    """复用 fetch 命令的归档结果打印格式。"""
    if report.total == 0:
        print("[ok] 正文阶段：没有符合条件的待采集文章（新增为零，已全部归档）")
        return
    print(
        f"[ok] 正文阶段结束：共 {report.total} 篇，成功 {report.downloaded}，"
        f"跳过 {report.skipped}（已删除/违规），失败 {report.failed}"
    )
    if metrics_enabled:
        print(
            f"[ok] 互动数据：采集成功 {report.interactions_collected} 篇、"
            f"评论 {report.comments_collected} 条；"
            f"缺凭证跳过 {report.interactions_skipped} 篇；"
            f"失败 {report.interactions_failed} 篇"
            + ("（失败不影响正文归档，可稍后重跑）" if report.interactions_failed else "")
        )
    if report.image_failures:
        print(
            f"[warn] {report.image_failures} 张正文图片下载失败，"
            "已在各文章 metadata.json 登记例外并保留远程引用，可稍后重跑补齐"
        )
    for item in report.items:
        if item.state == "failed":
            print(f"  [fail] {item.title}：{item.error}")
        elif item.state == "skipped":
            print(f"  [skip] {item.title}：{item.error}")


def _run_pipeline_command(args: argparse.Namespace, *, full: bool) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    conn = connect(settings.db_path)
    init_db(conn)

    if args.fetch_metrics:
        settings = settings.model_copy(update={"fetch_metrics": True})

    mode_label = "全量回溯+对账" if full else "增量同步"
    stages = "列表 → 正文/富媒体" + (" → 互动" if settings.fetch_metrics else "")
    print(f"[..] {mode_label}公众号「{args.account}」：{stages}")

    try:
        report = run_pipeline(
            conn,
            settings,
            args.account,
            full=full,
            include_failed=getattr(args, "include_failed", False),
            fetch_limit=args.limit,
            max_pages=getattr(args, "max_pages", None),
            no_reconcile=getattr(args, "no_reconcile", False),
        )
    except CredentialExpiredError as exc:
        print(f"[fail] 登录态失效：{exc}")
        print("       请按 deploy/README.md 第 3/5 节用专用订阅号重新扫码")
        return 2
    except AccountNotFoundError as exc:
        print(f"[fail] {exc}")
        return 3
    except (BizUnavailableError, EndpointDiscoveryError) as exc:
        print(f"[fail] {exc}")
        return 4
    except LookupError as exc:
        print(f"[fail] {exc}")
        return 3
    except (ApiRetError, PayloadError) as exc:
        print(f"[fail] 采集服务返回异常：{exc}")
        return 1
    except (httpx.TimeoutException, httpx.TransportError) as exc:
        print(f"[fail] 无法连接采集服务：{exc.__class__.__name__}: {exc}")
        print("       请确认容器已启动（docker compose ps），详见 deploy/README.md")
        return 4

    lr = report.list
    if lr.caught_up:
        print(
            f"[ok] 列表增量追平（翻页 {lr.pages}，新增 {lr.inserted}，"
            f"更新 {lr.updated}）；未扫描到尾页，不做下架对账"
        )
    else:
        tail = "已到历史尾页" if lr.completed else "未到历史尾页（截断）"
        print(
            f"[ok] 列表同步完成（{tail}）：翻页 {lr.pages}，新增 {lr.inserted}，"
            f"更新 {lr.updated}，跳过非图文 {lr.skipped_non_article}，"
            f"对账标记不可见 {lr.hidden_marked} 篇"
        )
    if full and lr.completed:
        completeness = check_metadata_completeness(conn, lr.biz)
        rates = "，".join(f"{k} 非空率 {v:.1%}" for k, v in completeness.rates().items())
        tag = "[ok]" if completeness.ok else "[warn]"
        print(f"{tag} 元数据完整性（共 {completeness.total} 篇）：{rates}")

    _print_fetch_summary(report.fetch, metrics_enabled=settings.fetch_metrics)
    return 1 if report.has_fetch_failures else 0


def _cmd_sync(args: argparse.Namespace) -> int:
    """增量：列表 catch-up 追平 + 仅归档 pending 新文章。"""
    return _run_pipeline_command(args, full=False)


def _cmd_run(args: argparse.Namespace) -> int:
    """全量回溯+校验；--full 为显式确认开关，防止误触发长任务。"""
    if not args.full:
        print("[fail] run 执行全量回溯需显式添加 --full；日常增量请使用："
              "mp-archiver sync -a <账号>")
        return 1
    return _run_pipeline_command(args, full=True)


def _cmd_sync_official(args: argparse.Namespace) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    conn = connect(settings.db_path)
    init_db(conn)

    app_id = settings.wechat_app_id.strip()
    app_secret = settings.wechat_app_secret.get_secret_value().strip()
    if not app_id or not app_secret:
        print("[skip] 未配置 MP_ARCHIVER_WECHAT_APP_ID/APP_SECRET，官方源不启用（无请求发出）")
        print("       接口边界与配置方式见 deploy/README.md 第 11 节")
        return 0

    public_settings = settings.model_copy(
        update={
            "exporter_token": SecretStr(""),
            "wechat_app_id": app_id,
            "wechat_app_secret": SecretStr(app_secret),
        }
    )
    try:
        with RateLimitedClient(public_settings) as client:
            report = sync_official_articles(
                conn, public_settings, client, account_alias=args.account
            )
    except OfficialApiPermissionError as exc:
        print(f"[warn] 官方接口无权限：{redact(str(exc))}")
        print("       48001：当前官方文档仅列认证服务号；认证订阅号以后台接口权限页与实测为准")
        print("       历史全量请以 R2 采集服务为主；官方源已自动停用，不影响其他流程")
        return 0
    except OfficialApiConfigError as exc:
        print(f"[fail] {exc}")
        return 3
    except ApiRetError as exc:
        hint = ""
        if exc.ret == 40164:
            hint = "（请在公众号后台将本机出口 IP 加入白名单）"
        elif exc.ret == 40125:
            hint = "（请检查 AppSecret 是否正确）"
        elif exc.ret == 45009:
            hint = "（接口频率/配额限制，请稍后再试）"
        print(f"[fail] 官方接口调用失败 ret={exc.ret}{hint}：{redact(exc.errmsg)}")
        return 4
    except PayloadError as exc:
        print(f"[fail] 官方接口响应无法解析：{redact(str(exc))}")
        return 4
    except json.JSONDecodeError:
        print("[fail] 官方接口返回非 JSON 内容（可能被网关/代理拦截），请检查网络与代理配置")
        return 4
    except (httpx.TimeoutException, httpx.TransportError) as exc:
        print(f"[fail] 无法连接官方接口：{exc.__class__.__name__}: {redact(str(exc))}")
        return 4

    print(
        f"[ok] 官方源同步完成（biz={report.biz}）：翻页 {report.pages}，"
        f"新增 {report.inserted}，与 R2 去重合并 {report.updated}，"
        f"跳过已删除 {report.skipped_deleted}，平台群发总数 {report.total_groups}"
    )
    if report.quota_reached:
        print("[warn] 已达当日调用安全阈值，剩余内容次日再同步；配额状态见 data/official_api_quota.json")
    return 0


_STAGE_ICONS = {"ok": "[ok]", "warn": "[warn]", "fail": "[fail]", "skip": "[skip]"}


def _cmd_official_doctor(args: argparse.Namespace) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    conn = connect(settings.db_path)
    init_db(conn)

    print("官方接口联调探针（TR-8.1）：配置 → 网络 → token → batchget → biz 一致性")
    print("提示：探针不写库、不下载正文；batchget 实页探测消耗 1 次当日配额计数\n")

    public_settings = settings.model_copy(update={"exporter_token": SecretStr("")})
    with RateLimitedClient(public_settings) as client:
        if args.network_only:
            stages = [probe_network(client)]
        else:
            report = run_full_probe(
                public_settings, client,
                account_alias=args.account, conn=conn,
            )
            stages = report.stages

    for stage in stages:
        print(f"{_STAGE_ICONS.get(stage.status, '[?]')} [{stage.stage}] {stage.message}")
        for detail in stage.details:
            print(f"       - {detail}")

    failures = [s for s in stages if s.status == "fail"]
    warns = [s for s in stages if s.status == "warn"]
    print()
    if failures:
        print(f"[fail] {len(failures)} 个阶段失败，按上述提示处置后重跑本命令")
        return 1
    if warns:
        print(f"[warn] {len(warns)} 个告警，链路未完全确认；按提示补齐后重跑")
        return 0
    if args.network_only:
        print("[ok] 网络预检通过；配置 AppID/AppSecret 后执行完整探针："
              "mp-archiver official-doctor -a <账号别名>")
    else:
        print("[ok] 全部阶段通过；可执行小样本正式同步："
              f"mp-archiver sync-official -a {args.account}")
    return 0


def _cmd_export_rag(args: argparse.Namespace) -> int:
    """离线导出已归档文章为 RAG JSONL（不发起任何网络请求）。"""
    settings = get_settings()
    configure_logging(settings.log_level)
    conn = connect(settings.db_path)
    init_db(conn)

    account_biz = None
    if args.account:
        account_biz = get_account_biz_by_alias(conn, args.account)
        if account_biz is None:
            print(f"[fail] 未找到公众号「{args.account}」，请先执行 list 同步列表")
            return 3

    out_path = Path(args.out) if args.out else settings.export_root / "rag.jsonl"
    scope = f"账号「{args.account}」" if args.account else "全部账号"
    mode = "原文（不清洗）" if args.no_clean else "清洗后纯文本"
    print(f"[..] 导出 RAG JSONL：{scope}，{mode} → {out_path}")

    report = export_rag_jsonl(
        conn,
        settings.archive_root,
        out_path,
        account_biz=account_biz,
        clean=not args.no_clean,
        with_raw=args.with_raw,
        limit=args.limit,
    )

    print(
        f"[ok] 导出完成：{report.exported}/{report.total} 篇已写入 "
        f"（其中空正文 {report.empty_text} 篇，仍保留元数据条目）"
    )
    if not args.no_clean:
        print(
            f"[ok] 模板噪声清洗：删除引导/装饰行 {report.removed_noise_lines}，"
            f"折叠相邻重复行 {report.collapsed_duplicates}，"
            f"裁剪文末平台推荐块 {report.trimmed_tail_lines}"
        )
    if args.with_raw:
        print("[ok] 已追加 text_raw 字段（清洗前原文），可逐行对照评阅")
    for item in report.items:
        if item.state == "failed":
            print(f"  [fail] {item.title}：{item.error}")
    if report.has_failures:
        print("[warn] 存在读取失败条目（DB 标记 downloaded 但归档文件缺失/损坏）；"
              "重跑 fetch 补齐后重新导出即可")
        return 1
    return 0


def _cmd_report(args: argparse.Namespace) -> int:
    """离线生成分析报表（CSV 明细 + 单文件 HTML，不发起任何网络请求）。"""
    settings = get_settings()
    configure_logging(settings.log_level)
    conn = connect(settings.db_path)
    init_db(conn)

    account_biz = None
    if args.account:
        account_biz = get_account_biz_by_alias(conn, args.account)
        if account_biz is None:
            print(f"[fail] 未找到公众号「{args.account}」，请先执行 list 同步列表")
            return 3

    out_dir = Path(args.out) if args.out else settings.export_root / "report"
    print(f"[..] 生成分析报表 → {out_dir}（report.html + report.csv）")
    result = generate_report(conn, out_dir, account_biz=account_biz, top_n=args.top)
    d = result.data

    print(
        f"[ok] 报表已生成：文章 {d.total_articles} 篇（有发布时间 {d.timed_articles}，"
        f"无时间 {d.missing_time}）"
    )
    print(
        f"     原创占比 "
        + (f"{d.original_ratio:.1%}（{d.original_count}/{d.timed_articles}）"
           if d.original_ratio is not None else "无数据")
        + f"；合集 {len(d.album_top)} 个"
    )
    if d.downloaded_total:
        print(
            f"     含音视频 {d.with_av}/{d.downloaded_total} 篇"
            f"（音频 {d.with_audio}、视频 {d.with_video}，分母为已归档文章）"
        )
    else:
        print("     含音视频占比：暂无已归档文章（执行 fetch 后即可统计）")
    print(f"[ok] HTML（离线可开）：{result.html_path}")
    print(f"[ok] CSV 明细（Excel 可开）：{result.csv_path}")
    return 0


def _cmd_resolve_biz(args: argparse.Namespace) -> int:
    settings = get_settings()
    configure_logging(settings.log_level)
    print("解析文章链接中的 __biz（短链需联网抓取一次，不写库、不产生微信配额消耗）\n")
    with RateLimitedClient(settings) as client:
        try:
            identity = resolve_article_identity(client, args.url)
        except PayloadError as exc:
            print(f"[fail] {redact(str(exc))}")
            return 4
        except Exception as exc:  # httpx 传输族
            print(f"[fail] 请求失败：{exc.__class__.__name__}: {redact(str(exc))}")
            return 4

    from urllib.parse import quote
    encoded = quote(identity["biz"], safe="")
    print(f"[ok] 提取来源：{identity['source']}")
    print(f"[ok] __biz（解码形态）：{identity['biz']}")
    print(f"[ok] __biz（编码形态）：{encoded}")
    if identity["mid"]:
        print(f"     mid={identity['mid']} idx={identity['idx'] or '-'} "
              f"sn={identity['sn'][:4]}…（已脱敏）")
    print("\n请将以下一行填入项目根 .env 的 MP_ARCHIVER_WECHAT_OFFICIAL_BIZ= 后：")
    print(f"MP_ARCHIVER_WECHAT_OFFICIAL_BIZ={encoded}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="mp-archiver", description="微信公众号全量内容归档工具")
    parser.add_argument("--version", action="version", version=f"mp-archiver {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init-db", help="初始化 SQLite 元数据库").set_defaults(func=_cmd_init_db)
    sub.add_parser("doctor", help="环境与依赖自检").set_defaults(func=_cmd_doctor)

    p_list = sub.add_parser("list", help="按名称同步公众号全量文章列表")
    p_list.add_argument("-a", "--account", required=True, help="公众号昵称或微信号")
    p_list.add_argument("--max-pages", type=int, default=None, help="最多翻页数（调试用；截断不做下架对账）")
    p_list.add_argument("--no-reconcile", action="store_true", help="翻到尾页后也不执行不可见文章对账")
    p_list.set_defaults(func=_cmd_list)

    p_fetch = sub.add_parser("fetch", help="归档文章正文与正文图片（四件套）")
    p_fetch.add_argument("-a", "--account", required=True, help="公众号昵称或微信号（需已执行 list）")
    p_fetch.add_argument("--limit", type=int, default=None, help="本次最多归档篇数（默认全部待采集）")
    p_fetch.add_argument("--include-failed", action="store_true", help="同时重试此前 failed 的文章")
    p_fetch.add_argument(
        "--fetch-metrics",
        action="store_true",
        help="同时采集评论与阅读/点赞等互动指标（需配置互动凭证，见 deploy/README.md）",
    )
    p_fetch.set_defaults(func=_cmd_fetch)

    p_sync = sub.add_parser(
        "sync",
        help="增量同步：列表追平新文章并归档正文/富媒体（日常调度使用）",
    )
    p_sync.add_argument("-a", "--account", required=True, help="公众号昵称或微信号")
    p_sync.add_argument("--limit", type=int, default=None,
                        help="本次最多归档新文章篇数（默认全部新增）")
    p_sync.add_argument(
        "--fetch-metrics", action="store_true",
        help="同时采集评论与阅读/点赞等互动指标（需配置互动凭证，见 deploy/README.md 第 8 节）",
    )
    p_sync.set_defaults(func=_cmd_sync)

    p_run = sub.add_parser(
        "run",
        help="全量回溯+下架对账+归档（需显式 --full 确认；首次建库或周期校验使用）",
    )
    p_run.add_argument("-a", "--account", required=True, help="公众号昵称或微信号")
    p_run.add_argument(
        "--full", action="store_true",
        help="显式确认执行全量回溯（完整翻到尾页并做不可见文章对账）",
    )
    p_run.add_argument("--include-failed", action="store_true",
                       help="同时重试此前 failed 的文章")
    p_run.add_argument("--limit", type=int, default=None,
                       help="本次最多归档篇数（默认全部待采集）")
    p_run.add_argument(
        "--fetch-metrics", action="store_true",
        help="同时采集评论与阅读/点赞等互动指标（需配置互动凭证，见 deploy/README.md 第 8 节）",
    )
    p_run.add_argument("--no-reconcile", action="store_true",
                       help="即使到尾页也不执行不可见文章对账")
    p_run.add_argument("--max-pages", type=int, default=None,
                       help="调试用：限制列表翻页数（截断不做对账）")
    p_run.set_defaults(func=_cmd_run)

    p_official = sub.add_parser(
        "sync-official",
        help="可选：自有认证号官方接口同步已发布图文（freepublish/batchget）",
    )
    p_official.add_argument(
        "-a", "--account", required=True,
        help="账号别名（与 list/fetch 一致；用于解析 biz 与归档归属）",
    )
    p_official.set_defaults(func=_cmd_sync_official)

    p_doctor_official = sub.add_parser(
        "official-doctor",
        help="官方接口真实联调分阶段探针（TR-8.1：配置/网络/token/batchget/biz 核对）",
    )
    p_doctor_official.add_argument(
        "-a", "--account", default="",
        help="账号别名（与 sync-official 一致；未做过 R2 同步时可留空，配合显式 biz 配置）",
    )
    p_doctor_official.add_argument(
        "--network-only", action="store_true",
        help="仅做网络可达性预检（无需任何凭证）",
    )
    p_doctor_official.set_defaults(func=_cmd_official_doctor)

    p_export = sub.add_parser(
        "export-rag",
        help="离线导出已归档文章为 RAG JSONL 语料（纯文本+元数据，不触网）",
    )
    p_export.add_argument("-a", "--account", default=None,
                          help="仅导出指定公众号（默认全部账号）")
    p_export.add_argument("-o", "--out", default=None,
                          help="输出文件路径（默认 exports/rag.jsonl，整体覆盖）")
    p_export.add_argument("--no-clean", action="store_true",
                          help="关闭模板噪声清洗，输出未清洗纯文本")
    p_export.add_argument("--with-raw", action="store_true",
                          help="同时写入 text_raw 字段（清洗前原文），供前后对照评阅")
    p_export.add_argument("--limit", type=int, default=None,
                          help="调试用：最多导出篇数")
    p_export.set_defaults(func=_cmd_export_rag)

    p_report = sub.add_parser(
        "report",
        help="离线生成分析报表（CSV 明细 + 单文件 HTML，五项统计，不触网）",
    )
    p_report.add_argument("-a", "--account", default=None,
                          help="仅统计指定公众号（默认全部账号）")
    p_report.add_argument("-o", "--out", default=None,
                          help="输出目录（默认 exports/report/，整体覆盖）")
    p_report.add_argument("--top", type=int, default=10,
                          help="合集 Top N（默认 10）")
    p_report.set_defaults(func=_cmd_report)

    p_resolve = sub.add_parser(
        "resolve-biz",
        help="从公众号文章链接（含 /s/ 短链）解析 __biz，用于配置 OFFICIAL_BIZ",
    )
    p_resolve.add_argument("url", help="公众号文章链接（在本地执行，勿含他人敏感链接外发）")
    p_resolve.set_defaults(func=_cmd_resolve_biz)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args) or 0)


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
