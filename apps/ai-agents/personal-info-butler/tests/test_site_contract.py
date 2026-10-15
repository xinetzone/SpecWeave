"""站点契约测试：Sphinx 源目录的结构性不变量。

与 doc/conf.py 的构建期守卫互补：守卫在**构建时**拦截，这里在**测试时**拦截，
让「改页面漏删挂载点」「toctree 漏收录新页面」这类错误在 CI 的 gates job
就暴露，不必等到 build job。
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "doc"
STATIC = DOC / "_static"

REQUIRED_IDS = (
    "composer", "btn-capture", "capture-result",
    "search-input", "btn-search", "item-list",
    "ask-input", "btn-ask", "ask-result",
    "btn-extract", "extract-result",
    "btn-todos", "todos-result",
    "btn-summary", "summary-result",
    "set-api-base", "set-token", "btn-save-settings",
    "status-storage", "status-llm",
    "butler-banner", "btn-reconnect",
    "set-llm-base", "set-llm-key", "set-llm-model",
    "btn-llm-test", "btn-llm-clear", "llm-result",
)


def _markdown_files():
    return sorted(p for p in DOC.rglob("*.md") if "_build" not in p.parts)


def test_doc_dir_exists():
    assert DOC.is_dir(), "Sphinx 源目录 doc/ 是前端与文档的唯一事实来源"
    assert (DOC / "conf.py").is_file()
    assert (DOC / "index.md").is_file()
    assert (DOC / "app.md").is_file()


def test_app_page_provides_all_mount_points():
    text = (DOC / "app.md").read_text(encoding="utf-8")
    missing = [key for key in REQUIRED_IDS if f'id="{key}"' not in text]
    assert not missing, "app.md 缺少前端挂载点：" + ", ".join(missing)


def test_static_assets_exist():
    assert (STATIC / "butler.css").is_file()
    assert (STATIC / "butler.js").is_file()


def test_every_markdown_page_is_in_a_toctree():
    """未进 toctree 的页面会触发 Sphinx 警告，而本站开了 -W，构建直接失败。"""
    # toctree 条目在 index.md 里是独立成行的相对路径（可带可不带 .md）
    referenced = {line.strip().removesuffix(".md") for line in (DOC / "index.md").read_text(encoding="utf-8").splitlines()}
    referenced |= {m.removesuffix(".md") for m in re.findall(r"\]\((\S+?\.md)\)", (DOC / "index.md").read_text(encoding="utf-8"))}

    orphans = []
    for path in _markdown_files():
        rel = path.relative_to(DOC).with_suffix("").as_posix()
        if rel == "index" or rel.endswith("README"):
            continue
        if rel not in referenced:
            orphans.append(rel)
    assert not orphans, "以下页面未被 index.md 的 toctree 收录：" + ", ".join(orphans)


def test_no_hardcoded_backend_host_in_frontend_script():
    """后端地址必须是构建期注入或用户配置，不能写死在前端脚本里。

    保留域名（RFC 2606 的 ``example.com`` / ``example.invalid``）与回环地址属于
    文档占位符，允许出现；否则连「请填 https://你的后端」这样的提示都写不出来。
    """
    script = (STATIC / "butler.js").read_text(encoding="utf-8")
    assert "window.BUTLER_API_BASE" in script, "前端应读取构建期注入的 API 基址"

    reserved = {"example.com", "example.invalid", "localhost", "127.0.0.1"}
    hosts = {host.lower() for host in re.findall(r"https?://([a-z0-9.-]+)", script, flags=re.I)}
    suspicious = sorted(
        host for host in hosts
        if host not in reserved and not host.endswith(".example.com")
    )
    assert not suspicious, "前端脚本不得硬编码后端域名：" + ", ".join(suspicious)


def test_readme_documents_the_two_deploy_channels():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "GitHub Pages" in readme
    assert "schema.sql" in readme


@pytest.mark.parametrize("name", ["pyproject.toml", "requirements.txt", "schema.sql", "Dockerfile", ".env.example"])
def test_deliverables_exist(name):
    assert (ROOT / name).is_file(), f"缺少交付物 {name}"


def test_python_package_uses_scikit_build_core():
    """SpecWeave 主权区约定：Python 子项目统一 scikit-build-core 构建后端。"""
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "scikit_build_core.build" in text


def test_no_secret_defaults_in_env_template():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    for line in text.splitlines():
        if "=" not in line or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition("=")
        assert not value.strip() or key.strip() in {
            "LLM_BASE_URL", "LLM_MODEL", "CORS_ORIGINS"
        }, f"{key} 不应在模板里带默认值"


# -- 前端行为契约（灰盒：只断言可静态观察的不变量） ---------------------------


def test_build_guard_and_test_guard_stay_in_sync():
    """构建期守卫（doc/conf.py 的 _REQUIRED_IDS）与测试期守卫必须覆盖同一组挂载点。

    两份清单各自维护，一旦分叉就会出现「测试全绿但构建报错」或「构建通过但
    测试报错」，两者都会让人误以为另一道防线在管这件事。
    """
    import ast

    module = ast.parse((DOC / "conf.py").read_text(encoding="utf-8"))
    guard = None
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "_REQUIRED_IDS"
            for target in node.targets
        ):
            guard = {ast.literal_eval(element) for element in node.value.elts}
    assert guard is not None, "未能在 doc/conf.py 中找到 _REQUIRED_IDS"

    expected = set(REQUIRED_IDS)
    assert guard == expected, (
        "挂载点清单已分叉——"
        f"仅在 conf.py: {sorted(guard - expected)}；"
        f"仅在本文件: {sorted(expected - guard)}"
    )


def test_workbench_page_is_full_width():
    """工作台是操作界面，右侧目录栏会与内容抢宽，必须在页面级显式关掉。"""
    text = (DOC / "app.md").read_text(encoding="utf-8")
    assert "html_theme.sidebar_secondary.remove: true" in text


def test_connection_state_has_a_single_global_home():
    """连接状态是全局事实：必须在横幅呈现，而不是塞进某个业务面板。

    历史上它被写进「① 随手录入」的结果区，用户会读成「入库失败了」。
    """
    script = (STATIC / "butler.js").read_text(encoding="utf-8")
    assert "butler-banner" in script
    assert "'unconfigured'" in script and "'failed'" in script, "必须区分「没配」与「配了连不上」"
    assert "looksLikeHtml" in script, "必须识别「接口返回网页而非 JSON」这一典型配错"


def test_raw_response_is_quarantined_in_a_details_block():
    """归一化后的文案给人看，原始响应只能进折叠块——不能整页 HTML 糊脸。"""
    script = (STATIC / "butler.js").read_text(encoding="utf-8")
    assert script.count("butler-details") >= 1
    assert script.count("rawBlock") >= 2, "rawBlock 必须既有定义也有调用"
    assert "esc(String(raw)" in script, "原文必须转义后再插入 DOM"


# -- 大模型卡片契约 ----------------------------------------------------------


def test_llm_card_presents_the_model_as_optional():
    """大模型是增强项不是启用项——卡片必须自己说清「不配也能用」。"""
    text = (DOC / "app.md").read_text(encoding="utf-8")
    assert "不配也能用" in text, "不说这句，用户会以为没配就用不了"
    for key in ("set-llm-base", "set-llm-key", "set-llm-model", "btn-llm-test", "btn-llm-clear"):
        assert f'id="{key}"' in text


def test_llm_credentials_are_persisted_before_the_probe():
    """探针靠请求头带凭据，而请求头读的是 settings——顺序反了就验了个空。"""
    script = (STATIC / "butler.js").read_text(encoding="utf-8")
    assert script.index("applyLlmFields(fields)") < script.index("call('/api/llm/test'")


def test_probe_contract_is_documented():
    api = (DOC / "guide" / "api.md").read_text(encoding="utf-8")
    assert "/api/llm/test" in api
    assert "永远返回 200" in api, "「验证结论在响应体里」这件事必须写进契约"
