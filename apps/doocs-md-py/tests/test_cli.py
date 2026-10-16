"""TR-19.1：mdpy CLI 五子命令的退出码与输出契约。

覆盖：帮助输出、render（文件/stdin/输出文件/选项透传/完整文档/与库调用逐字一致/
非法 JSON）、serve（dist 缺失退出 1、回环约束、端口占用递增与上游文案、runner 注入）、
upload（环境变量回退、未知图床、缺文件、配置段读取、URL 打印）、migrate 幂等。

上游事实：packages/md-cli/index.js:15-54（默认 127.0.0.1、默认 8800、占用文案）。
"""

import io
import socket

import pytest

from doocs_md_py.cli import _SUBCOMMANDS, build_parser, main
from doocs_md_py.server.app import resolve_free_port, serve

MARKDOWN = "# 标题\n\n正文 **加粗**。\n"
STUB_CSS = "/* stub code css */\n"


def _stub_fetcher(url: str) -> str:
    """替身代码高亮 CSS 抓取器：隔离网络（真实实现会 httpx 抓 CDN）。"""
    return STUB_CSS


def _noop_runner(app, host: str, port: int) -> None:
    return None


def _make_dist(tmp_path, name: str = "dist"):
    dist = tmp_path / name
    dist.mkdir()
    (dist / "index.html").write_text(
        "<!DOCTYPE html><html><body>hi</body></html>", encoding="utf-8"
    )
    return dist


def _free_port() -> int:
    """取一个当前空闲的回环端口（绑定 0 后立即释放）。"""
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


# ---- 顶层：帮助与子命令集合 ----


def test_help_lists_all_subcommands(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
    out = capsys.readouterr().out
    for name in _SUBCOMMANDS:
        assert name in out


def test_no_args_prints_help_exit_zero(capsys):
    assert main([]) == 0
    assert "mdpy" in capsys.readouterr().out


def test_parser_structure():
    parser = build_parser()
    for name in _SUBCOMMANDS:
        args = parser.parse_args([name])
        assert args.command == name


# ---- render ----


def test_render_matches_library_output(tmp_path, monkeypatch, capsys):
    """CLI render 与库调用 build_rendered_output 结果逐字一致。"""
    from doocs_md_py.render.article import RenderArticleInput, build_rendered_output

    monkeypatch.setattr("doocs_md_py.cli._code_css_fetcher", _stub_fetcher)
    source = tmp_path / "a.md"
    source.write_text(MARKDOWN, encoding="utf-8")

    assert main(["render", "-i", str(source)]) == 0
    out = capsys.readouterr().out

    expected = build_rendered_output(
        RenderArticleInput(markdown=MARKDOWN), code_css_fetcher=_stub_fetcher
    )
    assert out == expected.html


def test_render_with_options_matches_library(tmp_path, monkeypatch, capsys):
    """渲染选项经 CLI 透传后仍与库调用一致（False 落回库默认，不覆盖为 False）。"""
    from doocs_md_py.render.article import RenderArticleInput, build_rendered_output

    monkeypatch.setattr("doocs_md_py.cli._code_css_fetcher", _stub_fetcher)
    source = tmp_path / "a.md"
    source.write_text(MARKDOWN, encoding="utf-8")

    argv = [
        "render",
        "-i",
        str(source),
        "--font-size",
        "18px",
        "--theme-mode",
        "dark",
        "--use-indent",
        "--show-line-number",
    ]
    assert main(argv) == 0
    out = capsys.readouterr().out

    expected = build_rendered_output(
        RenderArticleInput(
            markdown=MARKDOWN,
            font_size="18px",
            theme_mode="dark",
            is_use_indent=True,
            is_show_line_number=True,
        ),
        code_css_fetcher=_stub_fetcher,
    )
    assert out == expected.html


def test_render_reads_stdin_writes_file(tmp_path, monkeypatch):
    monkeypatch.setattr("doocs_md_py.cli._code_css_fetcher", _stub_fetcher)
    monkeypatch.setattr("sys.stdin", io.StringIO(MARKDOWN))
    target = tmp_path / "out" / "a.html"

    assert main(["render", "-o", str(target)]) == 0
    assert target.is_file()
    assert target.read_text(encoding="utf-8").startswith("<")


def test_render_full_document_wraps_doctype(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("doocs_md_py.cli._code_css_fetcher", _stub_fetcher)
    source = tmp_path / "a.md"
    source.write_text(MARKDOWN, encoding="utf-8")

    assert main(["render", "-i", str(source), "--full-document"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("<!DOCTYPE html>")
    assert "<title>" in out
    assert out.rstrip().endswith("</html>")


def test_render_missing_input_exits_two(tmp_path, capsys):
    assert main(["render", "-i", str(tmp_path / "nope.md")]) == 2
    assert "-i/--input" in capsys.readouterr().err


def test_render_invalid_heading_styles_exits_two(tmp_path, capsys):
    source = tmp_path / "a.md"
    source.write_text(MARKDOWN, encoding="utf-8")
    assert main(["render", "-i", str(source), "--heading-styles", "{bad"]) == 2
    assert "heading-styles" in capsys.readouterr().err


# ---- serve ----


def test_serve_defaults():
    args = build_parser().parse_args(["serve"])
    assert args.host == "127.0.0.1"
    assert args.port == 8800


def test_serve_host_flag_parsed():
    args = build_parser().parse_args(["serve", "--host", "0.0.0.0", "--port", "9000"])
    assert (args.host, args.port) == ("0.0.0.0", 9000)


def test_serve_missing_dist_exits_one(tmp_path, capsys):
    assert serve(web_dist=tmp_path / "absent", runner=_noop_runner) == 1
    err = capsys.readouterr().err
    assert "前端静态资产缺失" in err


def test_serve_starts_runner_on_default_loopback(tmp_path, capsys):
    dist = _make_dist(tmp_path)
    port = _free_port()
    calls: list[tuple[str, int]] = []

    assert serve(port=port, web_dist=dist, runner=lambda app, h, p: calls.append((h, p))) == 0
    # AC-14：缺省不绑 0.0.0.0，仅回环
    assert calls == [("127.0.0.1", port)]
    out = capsys.readouterr().out
    assert "doocs/md-py 服务启动中..." in out
    assert "服务已启动" in out


def test_serve_warns_on_non_loopback_host(tmp_path, capsys):
    dist = _make_dist(tmp_path)
    assert serve(host="0.0.0.0", port=_free_port(), web_dist=dist, runner=_noop_runner) == 0
    assert "0.0.0.0" in capsys.readouterr().err


def test_serve_increments_on_occupied_port(tmp_path, capsys):
    dist = _make_dist(tmp_path)
    with socket.socket() as busy:
        busy.bind(("127.0.0.1", 0))
        busy.listen(1)
        taken = busy.getsockname()[1]
        calls: list[int] = []
        assert serve(port=taken, web_dist=dist, runner=lambda app, h, p: calls.append(p)) == 0

    assert calls == [taken + 1]
    # upstream: index.js:21 文案逐字
    assert f"端口 {taken} 被占用，正在寻找可用端口..." in capsys.readouterr().out


def test_resolve_free_port_increments_with_probe():
    taken = {8800, 8801, 8802}
    assert resolve_free_port("127.0.0.1", 8800, probe=lambda h, p: p not in taken) == 8803


def test_resolve_free_port_exhausted_raises():
    with pytest.raises(OSError):
        resolve_free_port("127.0.0.1", 8800, probe=lambda h, p: False, max_attempts=3)


# ---- upload ----


def test_upload_missing_required_args_exits_two(capsys):
    # argparse 标准行为：缺必需参数时 SystemExit(2) 并输出 usage
    with pytest.raises(SystemExit) as exc:
        main(["upload"])
    assert exc.value.code == 2
    assert "required" in capsys.readouterr().err


def test_upload_unknown_provider_exits_two(capsys):
    assert main(["upload", "--provider", "nope", "--file", "x.png"]) == 2
    assert "未知图床标识" in capsys.readouterr().err


def test_upload_missing_file_exits_two(tmp_path, capsys):
    assert main(["upload", "--provider", "default", "--file", str(tmp_path / "x.png")]) == 2
    assert "不存在" in capsys.readouterr().err


def test_upload_provider_from_env(tmp_path, monkeypatch, capsys):
    png = tmp_path / "p.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n")
    monkeypatch.setenv("MD_UPLOAD_PROVIDER", "nope")
    monkeypatch.setenv("MD_UPLOAD_FILE", str(png))

    assert main(["upload"]) == 2
    assert "未知图床标识" in capsys.readouterr().err


def test_upload_missing_config_section_exits_two(tmp_path, capsys):
    png = tmp_path / "p.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n")
    argv = [
        "upload",
        "--provider",
        "github",
        "--file",
        str(png),
        "--config",
        str(tmp_path / "absent.toml"),
    ]
    assert main(argv) == 2
    assert "githubConfig" in capsys.readouterr().err


def test_upload_reads_config_section_and_prints_url(tmp_path, monkeypatch, capsys):
    """配置文件段按 provider.config_key 取用，成功时打印 URL 并返回 0。"""
    import doocs_md_py.uploaders as uploaders

    png = tmp_path / "p.png"
    png.write_bytes(b"\x89PNG\r\n\x1a\n")
    config_file = tmp_path / "config"
    config_file.write_text('[githubConfig]\ntoken = "T"\n', encoding="utf-8")

    seen: dict = {}

    def fake_upload(provider_id, file, config, client):
        seen["provider_id"] = provider_id
        seen["config"] = config
        seen["content_type"] = file.content_type
        return "https://cdn.example/p.png"

    monkeypatch.setattr(uploaders, "file_upload", fake_upload)

    argv = [
        "upload",
        "--provider",
        "github",
        "--file",
        str(png),
        "--config",
        str(config_file),
    ]
    assert main(argv) == 0
    assert capsys.readouterr().out.strip() == "https://cdn.example/p.png"
    assert seen["provider_id"] == "github"
    assert seen["config"] == {"token": "T"}
    assert seen["content_type"] == "image/png"


# ---- migrate ----


def test_migrate_creates_and_updates_db(tmp_path, capsys):
    db_file = tmp_path / "nested" / "test.db"
    assert main(["migrate", "--db", str(db_file)]) == 0
    assert db_file.exists()
    assert "已应用迁移" in capsys.readouterr().out
    # 幂等：第二次无新增
    assert main(["migrate", "--db", str(db_file)]) == 0
    assert "已是最新" in capsys.readouterr().out
