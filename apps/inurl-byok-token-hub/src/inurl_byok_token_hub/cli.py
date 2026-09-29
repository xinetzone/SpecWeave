"""命令行入口：serve / catalog / route / compress / vault / smoke / launcher。

运行期命令建议统一走 ``conda run -n py314 ...``（本机默认 python 为 3.13.12，
不满足 ``requires-python >= 3.14``）。
"""

import json
from pathlib import Path

import typer
import uvicorn
from fastapi.testclient import TestClient

from .config import Settings, default_config_path, load_settings
from .logging_utils import get_logger
from .models import STRATEGIES, CompressionLevel
from .providers.transport import HttpResponse, MockTransport
from .storage import DEFAULT_LOCK_TIMEOUT, SingleInstanceLock

app = typer.Typer(add_completion=False, help="inurl BYOK Token Hub 复刻（Python 3.14+）")
logger = get_logger("cli")

LAUNCHER_NOTE = """启动器说明（与原产品供应链行为的关键差异）：

原产品 byok-launch.bat / byok-launch.sh 会在每次运行时
  1) 用 curl 重新拉取云端 local-agent.js 并执行（闭源、运行时下载）；
  2) 把统一令牌与主密钥内嵌进启动器。

本复刻**不做**上述任何一件事：
  - 不在运行时下载或执行任何远端代码；
  - 不在脚本中内嵌令牌或主密钥；
  - 停止服务请使用 Ctrl-C 或按 PID 精确终止，不要使用
    `taskkill /f /im node.exe` 这类会误杀其他进程的命令。

启动方式：
  conda run -n py314 inurl-byok-token-hub serve
"""


def _settings(
    config: Path | None = None,
    host: str | None = None,
    port: int | None = None,
    data_dir: Path | None = None,
) -> Settings:
    path = Path(config) if config else default_config_path()
    return load_settings(path, host=host, port=port, data_dir=data_dir)


@app.command()
def serve(
    config: Path | None = typer.Option(None, "--config", help="配置文件路径"),
    host: str | None = typer.Option(None, "--host", help="监听地址（仅允许回环）"),
    port: int | None = typer.Option(None, "--port", help="监听端口"),
    data_dir: Path | None = typer.Option(None, "--data-dir", help="运行期数据目录"),
) -> None:
    """启动本地代理与控制台（默认 http://127.0.0.1:3003/v1）。"""
    settings = _settings(config, host, port, data_dir)
    from .api.app import create_app

    application = create_app(settings)
    lock = SingleInstanceLock(Path(settings.data_dir) / "byok.pid")
    try:
        lock.acquire(timeout=DEFAULT_LOCK_TIMEOUT)
    except Exception as exc:  # noqa: BLE001
        typer.secho(f"启动失败：{exc}", fg=typer.colors.RED)
        raise typer.Exit(1) from exc
    typer.secho(f"监听 {settings.base_url}（控制台 /console/login）", fg=typer.colors.GREEN)
    try:
        uvicorn.run(application, host=settings.host, port=settings.port, log_level="warning")
    finally:
        lock.release()


@app.command()
def catalog(
    config: Path | None = typer.Option(None, "--config"),
    capability: str = typer.Option("", "--capability", help="按能力过滤：text/code/image/video/audio"),
) -> None:
    """打印目录统计与条目。"""
    settings = _settings(config)
    from .services.catalog_service import CatalogService

    service = CatalogService.load(settings)
    typer.echo(
        f"providers={len(service.list_providers())} "
        f"free={service.free_count} paid={service.paid_count} "
        f"hidden={service.hidden_count} models={len(service.list_models())}"
    )
    if capability:
        from .models import Capability

        try:
            rows = service.by_capability(Capability(capability))
        except Exception as exc:  # noqa: BLE001
            typer.secho(f"{exc}", fg=typer.colors.YELLOW)
            raise typer.Exit(1) from exc
        for row in rows:
            typer.echo(f"  {row.id}\t{row.provider_id}\tfree={row.free}")


@app.command()
def route(
    model: str = typer.Argument("inurl", help="逻辑别名或真实模型 id"),
    strategy: str = typer.Option("latency_first", "--strategy"),
    combo: str = typer.Option("", "--combo", help="以 > 分隔的策略回退链"),
    config: Path | None = typer.Option(None, "--config"),
    user: str = typer.Option("", "--user", help="用户 id（缺省取第一个注册用户）"),
) -> None:
    """干跑路由决策（不发起真实调用）。"""
    settings = _settings(config)
    from .services.hub import build_hub

    hub = build_hub(settings)
    target = user or _first_user_id(hub)
    if not target:
        typer.secho("尚无注册用户，请先注册并录入密钥", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    try:
        plan = hub.router.plan(target, model, strategy=strategy, combo=combo)
    except Exception as exc:  # noqa: BLE001
        typer.secho(f"路由失败：{exc}", fg=typer.colors.RED)
        raise typer.Exit(1) from exc
    typer.echo(f"alias={plan.alias} capability={plan.capability} strategy={'>'.join(plan.strategy_seq)}")
    for index, candidate in enumerate(plan.candidates):
        typer.echo(
            f"  [{index}] {candidate.provider_id}\t{candidate.model_id}\t"
            f"latency={candidate.latency_ms:.1f}ms success={candidate.success_rate:.2f}"
        )


@app.command()
def compress(
    level: str = typer.Argument("standard", help="lite/standard/aggressive/ultra/rtk"),
    text: str = typer.Option("", "--text", help="待压缩文本；缺省使用内置样例"),
) -> None:
    """试压缩，输出估算压缩率与保护对象。"""
    from .services.compression_service import compress_prompt

    sample = text or (
        "请把这段内容压缩一下。\n\n"
        "```python\nprint('hello world')\n```\n\n"
        "参考 https://example.com/docs?x=1 与 {\"a\": 1, \"b\": [2, 3]}。\n\n"
        "这是一段重复的描述，这是一段重复的描述，这是一段重复的描述。"
    )
    result = compress_prompt(sample, CompressionLevel(level))
    typer.echo(f"level={result.level.value} 原始={result.original_length} 压缩后={result.compressed_length}")
    typer.echo(f"实际压缩率={result.estimated_ratio:.2%} 厂商自述估算={result.claimed_ratio}")
    typer.echo(f"保护对象={','.join(result.protected)} refused={result.refused}")
    typer.echo("--- 压缩结果 ---")
    typer.echo(result.text)


@app.command()
def vault(
    action: str = typer.Argument("list", help="list/add/remove"),
    provider_id: str = typer.Option("", "--provider", help="厂商 id"),
    api_key: str = typer.Option("", "--api-key", help="明文 Key（仅内存使用，不落盘）"),
    quota: int = typer.Option(0, "--quota", help="手填额度；0 表示不填"),
    config: Path | None = typer.Option(None, "--config"),
    user: str = typer.Option("", "--user", help="用户 id"),
    password: str = typer.Option("", "--password", help="解锁口令"),
) -> None:
    """密钥库管理（明文 Key 只经内存，落盘仅密文）。"""
    settings = _settings(config)
    from .services.hub import build_hub

    hub = build_hub(settings)
    target = user or _first_user_id(hub)
    if not target:
        typer.secho("尚无注册用户", fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    if action == "list":
        for row in hub.vault.list_keys(target):
            typer.echo(
                f"  {row.id}\t{row.provider_id}\t{row.status.value}\t"
                f"quota={row.quota_total}/{row.quota_used}"
            )
        return
    if action == "add":
        if not provider_id or not api_key:
            typer.secho("add 需要 --provider 与 --api-key", fg=typer.colors.RED)
            raise typer.Exit(1)
        if password:
            hub.unlock(target, password)
        master = hub.master_key(target)
        record = hub.vault.add_key(
            target, provider_id, api_key, master, quota_total=(quota or None)
        )
        typer.secho(f"已录入 {record.provider_id}（id={record.id}）", fg=typer.colors.GREEN)
        return
    if action == "remove":
        removed = hub.vault.remove_key(target, provider_id)
        typer.echo(f"已删除 {removed} 条")
        return
    typer.secho(f"未知动作 {action}", fg=typer.colors.RED)
    raise typer.Exit(1)


@app.command()
def strategies() -> None:
    """列出 19 种路由策略。"""
    from .models import STRATEGY_LABELS

    for name in STRATEGIES:
        typer.echo(f"  {name}\t{STRATEGY_LABELS[name]}")


@app.command()
def launcher() -> None:
    """打印启动器说明（含与原产品供应链行为的关键差异）。"""
    typer.echo(LAUNCHER_NOTE)


@app.command()
def smoke(
    config: Path | None = typer.Option(None, "--config"),
    data_dir: Path | None = typer.Option(None, "--data-dir", help="临时数据目录"),
) -> None:
    """端到端冒烟：全 mock、零真实密钥跑通全流程。"""
    import tempfile

    target_dir = Path(data_dir) if data_dir else Path(tempfile.mkdtemp(prefix="byok-smoke-"))
    settings = load_settings(
        Path(config) if config else default_config_path(), data_dir=target_dir
    )
    steps: list[tuple[str, bool, str]] = []

    def step(name: str, ok: bool, detail: str = "") -> None:
        steps.append((name, ok, detail))
        mark = "PASS" if ok else "FAIL"
        color = typer.colors.GREEN if ok else typer.colors.RED
        typer.secho(f"[{mark}] {name} {detail}", fg=color)

    from .api.app import create_app
    from .services.hub import build_hub

    hub = build_hub(settings)

    # 1. 注册
    result = hub.tokens.register("smoke@local", "smoke-password", vault=hub.vault)
    user = result.user
    step("注册并下发统一令牌/恢复密语", result.token.startswith("byok_live_"), f"token={result.token[:14]}…")

    # 2. 解锁
    hub.unlock(user.id, "smoke-password")
    step("口令解锁密钥库", hub.is_unlocked(user.id))

    # 3. 选三个具备 text 能力且 OpenAI 兼容的厂商
    from .models import Capability, ProviderProtocol

    picks: list[tuple[str, str]] = []
    for entry in hub.catalog.by_capability(Capability.TEXT):
        provider = hub.catalog.provider(entry.provider_id)
        if provider is None or provider.protocol is not ProviderProtocol.OPENAI_COMPAT:
            continue
        if any(p[0] == entry.provider_id for p in picks):
            continue
        picks.append((entry.provider_id, entry.id))
        if len(picks) == 3:
            break
    step("选出 3 个文本候选厂商", len(picks) == 3, str([p[0] for p in picks]))

    master = hub.master_key(user.id)
    for provider_id, _model_id in picks:
        hub.vault.add_key(user.id, provider_id, f"sk-mock-{provider_id}", master)
    step("E2EE 录入 3 个厂商密钥", len(hub.vault.list_keys(user.id)) == 3)

    # 4. 落盘不含明文
    dumped = hub.store.raw_text()
    step("落盘数据不含明文 Key", "sk-mock-" not in dumped)

    # 5. 启动应用（mock 传输：429 → 503 → 200）
    transport = MockTransport(
        responses=[
            HttpResponse(status_code=429, json_body={"error": {"message": "rate limited"}}),
            HttpResponse(status_code=503, json_body={"error": {"message": "unavailable"}}),
            HttpResponse(
                status_code=200,
                json_body={
                    "id": "chatcmpl-mock",
                    "model": picks[-1][1],
                    "choices": [
                        {"index": 0, "message": {"role": "assistant", "content": "mock 回答"}, "finish_reason": "stop"}
                    ],
                    "usage": {"prompt_tokens": 11, "completion_tokens": 7},
                },
            ),
        ]
    )
    application = create_app(settings, hub=hub, transport=transport)
    client = TestClient(application)
    headers = {"Authorization": f"Bearer {result.token}"}

    # 6. /v1/models
    resp = client.get("/v1/models", headers=headers)
    models_ok = resp.status_code == 200 and any(d["id"] == "inurl" for d in resp.json()["data"])
    step("GET /v1/models 返回别名与真实模型", models_ok)

    # 7. 聊天（含故障切换）
    resp = client.post(
        "/v1/chat/completions",
        headers=headers,
        json={"model": "inurl", "messages": [{"role": "user", "content": "你好"}]},
    )
    chat_ok = resp.status_code == 200
    detail = ""
    if chat_ok:
        body = resp.json()
        detail = f"provider={body['_route']['provider']} failover={body['_route']['failover']}"
        chat_ok = body["choices"][0]["message"]["content"] == "mock 回答" and body["_route"]["failover"] == 2
    step("POST /v1/chat/completions 经 429/503 切换后成功", chat_ok, detail)

    # 8. 用量 +1
    step("用量台账 +1", hub.usage.total_calls(user.id) == 1)

    # 9. 鉴权矩阵
    step("无令牌访问 /v1/models 为 401", client.get("/v1/models").status_code == 401)
    step("无效令牌为 401", client.get("/v1/models", headers={"Authorization": "Bearer byok_live_bad"}).status_code == 401)
    step("随机路径为 401", client.get("/api/definitely-not-exist").status_code == 401)
    admin_resp = client.get("/api/admin/modules", headers=headers)
    step("非管理员访问后台为 403", admin_resp.status_code == 403)
    step(
        "后台裸 JSON 为 {'error':'forbidden'}",
        admin_resp.json() == {"error": "forbidden"},
    )
    step("公开 /api/ads 无鉴权 200", client.get("/api/ads").status_code == 200)
    step("公开 /api/news 无鉴权 200", client.get("/api/news").status_code == 200)
    step("公开 /api/catalog 无鉴权 200", client.get("/api/catalog").status_code == 200)
    step("公开 /api/billing/plans 无鉴权 200", client.get("/api/billing/plans").status_code == 200)

    # 10. 管理员后台
    admin_token = hub.admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    step("管理员访问后台 200", client.get("/api/admin/modules", headers=admin_headers).status_code == 200)

    # 11. video/audio 不可用
    resp = client.post(
        "/v1/chat/completions",
        headers=headers,
        json={"model": "inurl-video", "messages": [{"role": "user", "content": "x"}]},
    )
    step(
        "inurl-video 明确不可用",
        resp.status_code in {422, 503} and "没有支持该类别的厂商" in json.dumps(resp.json(), ensure_ascii=False),
        f"status={resp.status_code}",
    )

    failed = [name for name, ok, _ in steps if not ok]
    typer.echo("")
    if failed:
        typer.secho(f"冒烟失败 {len(failed)} 项：{failed}", fg=typer.colors.RED)
        raise typer.Exit(1)
    typer.secho(f"冒烟全部通过（{len(steps)} 项），数据目录 {target_dir}", fg=typer.colors.GREEN)


def _first_user_id(hub) -> str:
    rows = hub.store.users.all()
    return rows[0].id if rows else ""


def main() -> None:
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
