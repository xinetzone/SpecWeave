"""命令行入口：``zhihu-checkin serve`` / ``zhihu-checkin check``。"""

from pathlib import Path
from typing import Optional

import typer

from .config import load_config
from .errors import CheckinHubError

app = typer.Typer(
    add_completion=False,
    help="知乎打卡工作台：本地追踪/打卡 + 固定门 + 半自动发布桥。",
)


def _load(workspace: Optional[Path], **overrides):
    return load_config(
        cli_workspace=workspace,
        host=overrides.get("host"),
        port=overrides.get("port"),
    )


@app.command()
def serve(
    workspace: Optional[Path] = typer.Option(
        None, "--workspace", "-w", help="执行工作台目录（含 tracker.md）"
    ),
    host: Optional[str] = typer.Option(None, "--host", help="监听地址（仅本地）"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="监听端口"),
) -> None:
    """启动本地 Web 工作台。"""
    import uvicorn

    from .web.app import create_app

    try:
        cfg = _load(workspace, host=host, port=port)
        # acquire_lock=True：真实 serve 必须防双开；锁随进程退出由 OS 释放
        fastapi_app = create_app(cfg, acquire_lock=True)
    except CheckinHubError as exc:
        typer.secho(f"启动失败：{exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc

    typer.secho(
        f"工作台目录：{cfg.workspace.root}\n"
        f"访问地址：http://{cfg.host}:{cfg.port}",
        fg=typer.colors.GREEN,
    )
    uvicorn.run(fastapi_app, host=cfg.host, port=cfg.port, log_level="warning")


@app.command()
def check(
    workspace: Optional[Path] = typer.Option(
        None, "--workspace", "-w", help="执行工作台目录（含 tracker.md）"
    ),
) -> None:
    """校验工作区结构并输出中文报告（发布桥健康检查在后续版本接入）。"""
    try:
        cfg = _load(workspace)
    except CheckinHubError as exc:
        typer.secho(f"校验失败：{exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(1) from exc

    ws = cfg.workspace
    typer.secho("工作区校验通过", fg=typer.colors.GREEN)
    typer.echo(f"  目录：{ws.root}")
    typer.echo(f"  tracker：{ws.tracker}")
    typer.echo(f"  local 数据区：{ws.local}")
    typer.echo(f"  发布桥端点：{cfg.webbridge_endpoint}（会话 {cfg.session}）")
    if not ws.is_local_ignored():
        typer.secho(
            "  警告：未在工作区 .gitignore 中发现 local/* 忽略规则，真实数据可能入库！",
            fg=typer.colors.YELLOW,
        )
