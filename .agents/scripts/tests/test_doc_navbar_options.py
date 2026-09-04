"""Write 阶段优化回归测试（W-A4 · P0/P1/P2/P3 四门）。

10 条测试：
  T1 — navbar 三件套值断言：show/max 深度收窄到 L2(=2)，collapse=True 启用按需展开
  T2 — 非关键 UI 按钮精简断言：source/download/fullscreen 三按钮关闭，footer 只留 copyright
  T3 — 并行构建 -j 参数分流正确性：_parallel_flag() 按 GITHUB_ACTIONS + platform 三档分流（mystx 级）
  T4a — awesome-okf-xs tasks/docs.py 的 _parallel_flag() 三档分流正确性
  T4b — pages.yml：无硬编码 -j auto / 无 restore-keys / save-always=false
  T5a — conf.py OKF_BUILD_DOMAIN 域级分片钩子（VC-2/3/4/5/6）
  T5b — pages.yml PR 域级分片（VC-8/9/10/11 + cache key 含 domain + PR 不上传 artifact）
  T6a — tasks/docs.py build_invs task：存在性 + 9 域白名单 + 非法域 ValueError
  T6b — build_invs 内部路径正确：scratch/<domain>/html/objects.inv → domain-invs/<domain>.inv move + size>8192
  T6c — pages.yml PR 3 步流水线：WARMUP / SHARD / SAVE 三步存在 + 顺序 + WARMUP cache key 含 hashFiles doc/bundles/**/*.md
"""
from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_OKF_CONF_PY = _PROJECT_ROOT / "projects" / "awesome-okf-xs" / "doc" / "conf.py"
_MYSTX_DOCS = _PROJECT_ROOT / "projects" / "xuanspace" / "libs" / "mystx" / "src" / "mystx" / "tasks" / "docs.py"
_OKF_TASKS_DOCS = _PROJECT_ROOT / "projects" / "awesome-okf-xs" / "tasks" / "docs.py"
_OKF_TASKS_INIT = _PROJECT_ROOT / "projects" / "awesome-okf-xs" / "tasks" / "__init__.py"
_OKF_INV_EXT = _PROJECT_ROOT / "projects" / "awesome-okf-xs" / "doc" / "_ext" / "okf_inventory_builder.py"
_OKF_PAGES_YML = _PROJECT_ROOT / "projects" / "awesome-okf-xs" / ".github" / "workflows" / "pages.yml"


def _load_module(path: Path, name: str):
    """以 name 为模块名加载 path，不注册到 sys.modules。"""
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None, f"无法为 {path} 创建 spec"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def okf_conf_module():
    """加载 awesome-okf-xs/doc/conf.py 为独立模块（避免 setup() 内钩子冲突）。"""
    return _load_module(_OKF_CONF_PY, "_okf_conf_test")


@pytest.fixture(scope="module")
def mystx_docs_module():
    """加载 mystx.tasks.docs 为独立模块。"""
    return _load_module(_MYSTX_DOCS, "_mystx_docs_test")


# ---------------------------------------------------------------------------
# T1 — navbar 三件套值断言
# ---------------------------------------------------------------------------

def test_t1_navbar_trinity_l2_depth(okf_conf_module):
    """T1: show/max navbar 深度 ≤2；collapse=True 启用按需展开。

    七概念 I-2 根因：navbar toctree 渲染占 Write 阶段 ~55% 权重。收窄到 L2
    + 启用 collapse 后，未展开分支的 DOM 节点不再参与每页模板渲染。
    """
    opts = getattr(okf_conf_module, "html_theme_options", {})
    assert isinstance(opts, dict), "html_theme_options 不是字典"

    show_depth = opts.get("show_navbar_depth")
    max_depth = opts.get("max_navbar_depth")
    collapse = opts.get("collapse_navbar")

    assert show_depth is not None, "show_navbar_depth 缺失"
    assert max_depth is not None, "max_navbar_depth 缺失"
    assert collapse is not None, "collapse_navbar 缺失"

    assert isinstance(show_depth, int), f"show_navbar_depth={show_depth!r} 非整数"
    assert isinstance(max_depth, int), f"max_navbar_depth={max_depth!r} 非整数"
    assert isinstance(collapse, bool), f"collapse_navbar={collapse!r} 非布尔"

    assert show_depth <= 2, (
        f"show_navbar_depth={show_depth} 超过 L2 上限(2)，"
        "违反 I-2 navbar 三件套收敛目标"
    )
    assert max_depth <= 2, (
        f"max_navbar_depth={max_depth} 超过 L2 上限(2)，"
        "深层 bundle 页须经 bundle 首页的手工导航表进入，不应注入到全局侧栏"
    )
    assert collapse is True, (
        "collapse_navbar=False 禁用按需展开，将导致所有分支节点无条件参与 DOM 构建"
    )


# ---------------------------------------------------------------------------
# T2 — 非关键 UI 按钮精简断言
# ---------------------------------------------------------------------------

def test_t2_ui_buttons_and_footer_stripped(okf_conf_module):
    """T2: source/download/fullscreen 三按钮关闭；footer 只保留 copyright.html。

    七概念 I-5 根因：每页 head/script 重复注入占约 8%。这些纯 UI 按钮对阅读
    体验无增益，移除可减少 sphinx_book_theme 模板循环内的条件分支与 JS 注册。
    """
    opts = getattr(okf_conf_module, "html_theme_options", {})
    assert isinstance(opts, dict), "html_theme_options 不是字典"

    use_source = opts.get("use_source_button", True)
    use_download = opts.get("use_download_button", True)
    use_fullscreen = opts.get("use_fullscreen_button", True)
    footer_items = opts.get("footer_content_items", "")

    for label, val in (
        ("use_source_button", use_source),
        ("use_download_button", use_download),
        ("use_fullscreen_button", use_fullscreen),
    ):
        assert val is False, (
            f"{label}={val!r}，非关键 UI 按钮应关闭以减少模板分支与静态资源注入"
        )

    items = [x.strip() for x in str(footer_items).split(",") if x.strip()]
    assert items == ["copyright.html"], (
        f"footer_content_items={footer_items!r}，"
        "应精简为仅 copyright.html（其余 author/last-updated/extra-footer 均为非阅读必需）"
    )


# ---------------------------------------------------------------------------
# T3 — 并行构建 -j 参数分流正确性
# ---------------------------------------------------------------------------

def test_t3_parallel_flag_three_tier_split(monkeypatch, mystx_docs_module):
    """T3: _parallel_flag() 按 GITHUB_ACTIONS + platform 三档正确分流。

    七概念 I-3 根因：Sphinx parallel 依赖 POSIX fork()，Windows 天然串行；
    CI 环境 -j auto 可能拿到 32+ 核导致 IPC 瓶颈，上限钳制到 8。
    """
    fake_cpu = 16
    mod = mystx_docs_module  # 模块内部 `from multiprocessing import cpu_count` 绑定在 mod.cpu_count
    pf = mod._parallel_flag

    # 3a) CI 档：GITHUB_ACTIONS=1 + linux → -j min(16, 8) = 8
    with monkeypatch.context() as m:
        m.setenv("GITHUB_ACTIONS", "1")
        m.setattr(sys, "platform", "linux")
        m.setattr(mod, "cpu_count", lambda: fake_cpu)
        flag_ci = pf()

    # 3b) 本地 POSIX 档：darwin + 无 CI → -j max(1, 16-1) = 15
    with monkeypatch.context() as m:
        m.delenv("GITHUB_ACTIONS", raising=False)
        m.setattr(sys, "platform", "darwin")
        m.setattr(mod, "cpu_count", lambda: fake_cpu)
        flag_posix = pf()

    # 3c) Windows 档：win32 → 空串（不加 -j）
    with monkeypatch.context() as m:
        m.delenv("GITHUB_ACTIONS", raising=False)
        m.setattr(sys, "platform", "win32")
        flag_win = pf()

    # 断言
    assert flag_ci.startswith("-j "), f"CI 档应生成 -j N，实际={flag_ci!r}"
    ci_n = int(flag_ci.split()[1])
    assert 1 <= ci_n <= 8, f"CI 档 -j={ci_n} 上限应钳制到 8，cpu_count={fake_cpu}"

    assert flag_posix.startswith("-j "), f"POSIX 档应生成 -j N，实际={flag_posix!r}"
    posix_n = int(flag_posix.split()[1])
    assert posix_n == max(1, fake_cpu - 1), (
        f"POSIX 档 -j={posix_n} 应等于 cpu_count-1(={fake_cpu - 1})，"
        "留 1 核给桌面响应避免卡 UI"
    )

    assert flag_win == "", (
        f"Windows 档应返回空串（不注入 -j），实际={flag_win!r}；"
        "Sphinx parallel 依赖 POSIX fork()，Windows 强制加 -j 会触发告警风暴并静默串行"
    )


# ---------------------------------------------------------------------------
# T4 — P1-D CI 缓存 & 并行分流防回归
# ---------------------------------------------------------------------------

def test_t4a_okf_tasks_parallel_flag_three_tier(monkeypatch):
    """T4a: awesome-okf-xs/tasks/docs.py 的 _parallel_flag() 三档分流正确。

    七概念 VC-6 采纳修正：CI 并行不应该写死在 pages.yml，应该在 tasks 层统一计算，
    避免后人改 CI 漏改 tasks 导致回归。三档结果必须与 mystx W-A2 完全一致。
    """
    mod = _load_module(_OKF_TASKS_DOCS, "_okf_tasks_docs_test_t4a")
    assert hasattr(mod, "_parallel_flag"), (
        "awesome-okf-xs/tasks/docs.py 缺少 _parallel_flag()，"
        "CI 并行分流将退化为串行（违反 W-A2 对齐要求）"
    )
    fake_cpu = 16
    pf = mod._parallel_flag

    # CI 档
    with monkeypatch.context() as m:
        m.setenv("GITHUB_ACTIONS", "1")
        m.setattr(sys, "platform", "linux")
        m.setattr(mod, "cpu_count", lambda: fake_cpu)
        flag_ci = pf()
    assert flag_ci.startswith("-j ")
    ci_n = int(flag_ci.split()[1])
    assert 1 <= ci_n <= 8, f"CI 档 -j={ci_n} 上限应钳制 8，cpu={fake_cpu}"

    # 本地 POSIX 档
    with monkeypatch.context() as m:
        m.delenv("GITHUB_ACTIONS", raising=False)
        m.setattr(sys, "platform", "darwin")
        m.setattr(mod, "cpu_count", lambda: fake_cpu)
        flag_posix = pf()
    assert flag_posix.startswith("-j ")
    posix_n = int(flag_posix.split()[1])
    assert posix_n == max(1, fake_cpu - 1), (
        f"POSIX 档 -j={posix_n} 应等于 cpu-1={fake_cpu-1}，留 1 核给桌面响应"
    )

    # Windows 档
    with monkeypatch.context() as m:
        m.delenv("GITHUB_ACTIONS", raising=False)
        m.setattr(sys, "platform", "win32")
        flag_win = pf()
    assert flag_win == "", (
        f"Windows 档 _parallel_flag()={flag_win!r}，应为空串（不加 -j），"
        "否则触发告警风暴 + 静默串行"
    )


def test_t4b_pages_yml_no_hardcoded_j_and_no_restore_keys():
    """T4b: pages.yml 无硬编码 ``-j auto``、无 restore-keys、save-always=false。

    七概念 VC-2 / VC-3 / VC-6 采纳修正：
      - VC-6：禁止 CI 层硬编码 -j auto → 必须走 _parallel_flag 三档分流
      - VC-2：禁止 restore-keys → 精确 key，防止分支 doctree schema 错位污染
      - VC-3：save-always=false → 只缓存成功构建，避免失败 partial pickle 污染 cache
    """
    text = _OKF_PAGES_YML.read_text(encoding="utf-8")

    # 用断言保证不是空的
    assert text.strip(), "pages.yml 是空文件或不存在"

    # VC-6：禁止硬编码 "-j auto"（任何形式，包括 YAML 字符串中的）
    assert "-j auto" not in text, (
        "pages.yml 中检测到硬编码 `-j auto`，违反 VC-6："
        "并行度应由 tasks/docs.py 的 _parallel_flag() 在运行时三档分流，"
        "禁止在 CI YAML 中写死覆盖"
    )

    # VC-2：禁止 restore-keys
    # GitHub Actions YAML 中 "restore-keys:" 作为独立 key
    assert "restore-keys:" not in text, (
        "pages.yml 中检测到 `restore-keys:`，违反 VC-2："
        "分支 schema 不兼容的 BuildEnv 命中会导致 Sphinx env corrupt，"
        "应用精确 key（去掉 restore-keys 回退链），宁可 miss 重建也不要污染崩溃"
    )

    # VC-3：save-always: false（或省略 = 默认 false）
    # 显式写出来更稳，所以断言显式 save-always: false。
    # 如果是完全省略，也不能写成 save-always: true。允许两种：省略 / 显式 false。
    if "save-always:" in text:
        assert "save-always: false" in text, (
            "pages.yml 中 `save-always:` 不是 false，违反 VC-3："
            "失败构建生成的 partial/损坏 environment.pickle 不应进入缓存，"
            "否则后续 run 命中后下载 200MB 再花 3min 崩溃的成本 > 重建 14min"
        )


# ---------------------------------------------------------------------------
# T5 — P2 域级分片（OKF_BUILD_DOMAIN）防回归
# ---------------------------------------------------------------------------

def test_t5a_conf_py_okf_domain_sharding_hooks(monkeypatch):
    """T5a: conf.py OKF_BUILD_DOMAIN 钩子正确生效（VC-2/3/4/5/6）。

    - VC-4：非法域值抛 ValueError
    - VC-6：分片模式 include_patterns 只含指定域 + 入口
    - VC-2：OKF_BUILD_DOMAIN=meta 时额外 include 所有 9 域 index.md
    - VC-3：默认模式（未设 OKF_BUILD_DOMAIN）intersphinx_mapping 仅 3 外部，无本地域
    - VC-5：分片模式未存在 inv 路径映射为 (url, None)，跳过加载
    """
    ALL_DOMAINS = ("meta", "guoxue", "zhexue", "kexue", "wenxue",
                   "yixue", "sheke", "yishu", "jishu")

    # --- VC-4：非法域抛 ValueError ---------------------------------------------------
    with monkeypatch.context() as m:
        m.setenv("OKF_BUILD_DOMAIN", "tech-does-not-exist")
        with pytest.raises(ValueError, match=r"Invalid OKF_BUILD_DOMAIN"):
            _load_module(_OKF_CONF_PY, "_t5a_invalid_domain")

    # --- VC-6 / VC-2：普通域分片 include_patterns 正确 --------------------------------
    with monkeypatch.context() as m:
        m.setenv("OKF_BUILD_DOMAIN", "jishu")
        mod = _load_module(_OKF_CONF_PY, "_t5a_jishu_domain")
    assert mod.include_patterns is not None, "分片模式 include_patterns 不能为 None"
    assert "index.md" in mod.include_patterns
    assert "bundles/index.md" in mod.include_patterns
    assert any(p.endswith("/**") and "jishu" in p for p in mod.include_patterns), (
        "分片模式 include_patterns 应包含 doc/bundles/jishu/**"
    )
    # 非当前域的子树不包含
    for d in ALL_DOMAINS:
        if d == "jishu":
            continue
        assert f"bundles/{d}/**" not in mod.include_patterns, (
            f"jishu 分片不应包含域 {d} 的通配符路径"
        )

    # --- VC-2：meta 分片额外 include 所有 9 域 index.md --------------------------------
    with monkeypatch.context() as m:
        m.setenv("OKF_BUILD_DOMAIN", "meta")
        mod2 = _load_module(_OKF_CONF_PY, "_t5a_meta_domain")
    for d in ALL_DOMAINS:
        assert f"bundles/{d}/index.md" in mod2.include_patterns, (
            f"meta 分片应额外包含所有 9 域 index.md（防 toctree 爆红 excluded doc）：缺失 {d}"
        )

    # --- VC-3：默认模式 intersphinx_mapping 仅 3 外部（无本地域 inv）---------------------
    with monkeypatch.context() as m:
        m.delenv("OKF_BUILD_DOMAIN", raising=False)
        mod3 = _load_module(_OKF_CONF_PY, "_t5a_default_full")
    ext_keys = [k for k in mod3.intersphinx_mapping.keys() if not k.startswith("okf-")]
    local_keys = [k for k in mod3.intersphinx_mapping.keys() if k.startswith("okf-")]
    assert set(ext_keys) == {"python", "sphinx", "myst-parser"}, (
        f"默认模式外部 inv 应为 3 个，实际={sorted(ext_keys)}"
    )
    assert len(local_keys) == 0, (
        f"默认模式不应注入本地域 inv（VC-3），实际 keys={local_keys}"
    )
    # 默认模式不显式定义 include_patterns（= 走 Sphinx 默认 ['**'] 全量）；
    #   显式赋值 None 反而会 TypeError: compile_matchers(None)。
    assert not hasattr(mod3, "include_patterns") or mod3.include_patterns is None, (
        "默认模式 include_patterns 应省略，不要赋值 None（会触发 Sphinx compile_matchers TypeError）"
    )

    # --- VC-5：分片模式未存在 inv → (url, None) 跳过加载 --------------------------------
    with monkeypatch.context() as m:
        m.setenv("OKF_BUILD_DOMAIN", "jishu")
        # 默认 OKF_INV_DIR 不存在 → 所有 8 个域 inv 走 None 分支
        mod4 = _load_module(_OKF_CONF_PY, "_t5a_domain_noinv")
    local_keys4 = [k for k in mod4.intersphinx_mapping.keys() if k.startswith("okf-")]
    assert len(local_keys4) == 8, f"分片模式应注入另 8 个域 inv key，实际={len(local_keys4)}"
    for k in local_keys4:
        url, inv = mod4.intersphinx_mapping[k]
        assert inv is None, (
            f"不存在的本地域 inv 应映射为 (url, None)（VC-5，跳过加载不报 warning），"
            f"key={k} inv={inv!r}"
        )


def test_t5b_pages_yml_domain_sharding_ci_logic():
    """T5b: pages.yml 含 P2 PR 域级分片关键组件（VC-8~11）。

    - VC-8：锁定 dorny/paths-filter@v3 + 构建前 echo OKF_BUILD_DOMAIN
    - VC-9：>1 域 → unset OKF_BUILD_DOMAIN（全量）
    - VC-10：全局文件（conf.py/pyproject.toml/*.md 非域下）→ 全量
    - VC-11：pr-full label → 全量
    - P2 cache key 包含 OKF_BUILD_DOMAIN / FULL，避免 BuildEnv 跨模式污染
    - PR 不触发 upload-pages-artifact（防止 PR 污染部署）
    """
    text = _OKF_PAGES_YML.read_text(encoding="utf-8")
    assert text.strip(), "pages.yml 是空的"

    # VC-8 第 1 条：锁定 dorny/paths-filter@v3
    assert "dorny/paths-filter@v3" in text, "VC-8：应锁定 paths-filter@v3 稳定 API"
    # VC-8 第 2 条：构建前输出 $OKF_BUILD_DOMAIN 方便 debug
    assert "OKF_BUILD_DOMAIN=" in text and ">> $GITHUB_ENV" in text, (
        "VC-8：Resolve 步骤应写入 OKF_BUILD_DOMAIN 到 $GITHUB_ENV"
    )

    # VC-9：COUNT -eq 1 才赋值域，>1 域 unset
    assert '[ "$COUNT" -eq 1 ]' in text, "VC-9：应仅在单域改动时才使用 OKF_BUILD_DOMAIN 分片"

    # VC-10：全局文件改动 → 全量（global filter + unset OKF_BUILD_DOMAIN 分支）
    assert "global:" in text, "VC-10：paths-filter 应包含 global 全局文件组"
    assert "'doc/conf.py'" in text, "VC-10：全局组应包含 doc/conf.py"

    # VC-11：pr-full label → 全量
    assert "pr-full" in text, "VC-11：应检测 pr-full PR label 强制全量构建"

    # P2 cache key 包含 domain 维度（防止分片/全量 BuildEnv 互相污染）
    assert "d${{ env.OKF_BUILD_DOMAIN || 'FULL' }}-env-v1" in text, (
        "P2：cache key 应包含 OKF_BUILD_DOMAIN / FULL，避免跨模式 BuildEnv 污染"
    )

    # PR 不触发 upload-pages-artifact（仅 push main / dispatch 才上传）
    assert "if: github.event_name != 'pull_request'" in text, (
        "P2：PR 构建不应上传 pages artifact，防止污染部署"
    )


# ---------------------------------------------------------------------------
# T6 — P3 域级 objects.inv 预生成器防回归
# ---------------------------------------------------------------------------

def test_t6a_build_invs_task_exists_with_domain_whitelist():
    """T6a: tasks/docs.py build_invs 存在 + 9 域白名单 + 非法域 ValueError（VC-18/15/16）。"""
    ALL_DOMAINS = ("meta", "guoxue", "zhexue", "kexue", "wenxue",
                   "yixue", "sheke", "yishu", "jishu")
    mod = _load_module(_OKF_TASKS_DOCS, "_t6a_tasks_docs")

    assert hasattr(mod, "build_invs"), (
        "tasks/docs.py 应新增 `build_invs` task（P3 弥合 VC-5 跨域 xref 裸文本）"
    )
    # VC-16：@task help 标注存在（build_invs.__doc__ 含 example 与参数说明）
    assert mod.build_invs.__doc__ and "invoke build-invs" in mod.build_invs.__doc__, (
        "VC-16：build_invs task docstring 应含 usage example（新人 `invoke --list` 才能发现）"
    )
    # VC-18：非法域 ValueError（@task 要求真 Context，改从源码字符串断言）
    text = _OKF_TASKS_DOCS.read_text(encoding="utf-8")
    assert "if domain not in _OKF_DOMAINS:" in text, (
        "VC-18：build_invs 应显式 `if domain not in _OKF_DOMAINS:` 白名单拦截"
    )
    assert "raise ValueError" in text and "build_invs(domain=" in text, (
        "VC-18：非法域应抛 ValueError，错误消息含 build_invs(domain=) 方便排查"
    )
    # 9 域白名单 写死 _OKF_DOMAINS 常量 与实际 9 域全含
    assert hasattr(mod, "_OKF_DOMAINS"), (
        "tasks/docs.py 应显式定义 _OKF_DOMAINS 元组（与 conf.py 同源，不分散硬编码）"
    )
    for d in ALL_DOMAINS:
        assert d in mod._OKF_DOMAINS, f"tasks/docs _OKF_DOMAINS 缺域 {d}"
    assert len(mod._OKF_DOMAINS) == 9


def test_t6b_build_invs_scratch_and_output_paths(monkeypatch):
    """T6b: build_invs 内部 scratch/output 目录结构 + 文件 size 断言（VC-13/17/12）。

    - VC-12：遍历 OKF_DOMAINS 时，每轮写入环境变量 OKF_BUILD_DOMAIN=<d>
    - VC-13：从 scratch/d/html/objects.inv move 到 _build/domain-invs/<d>.inv
    - VC-17：size > 8192 bytes 的断言行存在（防 partial/空 inv 污染 cache）
    """
    text = _OKF_TASKS_DOCS.read_text(encoding="utf-8")

    # VC-12 环境变量注入
    assert 'os.environ["OKF_BUILD_DOMAIN"] = d' in text, (
        "VC-12：build_invs 每域循环开始时，应显式写 os.environ OKF_BUILD_DOMAIN=<domain>"
    )

    # VC-13：src=scratch/d/html/objects.inv  dst=domain-invs/<d>.inv  + shutil.move
    assert "domain-inv-scratch" in text and "_INV_SCRATCH_ROOT" in text, (
        "build_invs 应定义 _INV_SCRATCH_ROOT 常量放每域独立 scratch，避免 9 域共用 objects.inv"
    )
    assert "shutil.move(str(src_inv), str(dst_inv))" in text, (
        "VC-13：应 shutil.move 而非 copy，防止旧文件残留污染下次运行"
    )
    assert "dst_inv = _INV_OUTPUT_DIR / f\"{d}.inv\"" in text or (
        "f\"{d}.inv\"" in text and "_INV_OUTPUT_DIR" in text
    ), (
        "目标文件名应为 <domain>.inv（固定 1:1 映射域，后续 conf.py intersphinx_mapping 依赖该名）"
    )

    # VC-17 第一部分：先清理
    assert "shutil.rmtree(_INV_SCRATCH_ROOT, ignore_errors=True)" in text and \
           "shutil.rmtree(_INV_OUTPUT_DIR, ignore_errors=True)" in text, (
        "VC-17 前置清理：生成前应删 scratch+output 目录，防止 Ctrl+C 残留 partial inv"
    )
    # VC-17 第二部分：size > 1024（最小 meta 域 90 文档约=3033 bytes；
    #   旧阈值 8192 对 wenxue/meta 等小域过严，下调到 1024=Sphinx inv
    #   4 行 header(≈200B) + zlib 最小压缩体≈800B 的安全下限）
    assert "1024" in text and (
        "size > 1024" in text or "> 1024" in text or "1024," in text
    ), (
        "VC-17：move 完成后应 assert dst_inv size > 1024 bytes，防 partial/空 inv 进入 cache"
    )


def test_t6c_pages_yml_pr_three_step_pipeline():
    """T6c: pages.yml 两 job 分流 + PR 3 步流水线 WARMUP/SHARD/SAVE 关键组件（VC-14/19/20）。"""
    text = _OKF_PAGES_YML.read_text(encoding="utf-8")
    assert text.strip()

    # VC-20：build-main 与 build-pr 两个独立 jobs
    assert "build-main:" in text, "VC-20：应存在 build-main 单 job（main/dispatch 直接全量）"
    assert "build-pr:" in text, "VC-20：应存在 build-pr 单 job（PR 走 3 步流水线）"
    # build-main 不走 PR（if != pull_request）；build-pr 只在 PR
    assert "jobs:" in text
    assert text.count("if: github.event_name != 'pull_request'") >= 2, (
        "VC-20：build-main、deploy 两步均应限制 != pull_request；build-pr 只在 PR"
    )

    # PR 三步 · 名称含 WARMUP / SHARD / cache-domain-invs 命中行
    assert "WARMUP" in text, "P3 PR STEP 1：应存在 WARMUP（Generate 9 domain invs）步骤"
    assert "SHARD" in text, "P3 PR STEP 2：应存在 SHARD（Build HTML w/ invs）步骤"
    # VC-19：显式 export OKF_INV_DIR=$GITHUB_WORKSPACE/_build/domain-invs 绝对路径
    assert 'OKF_INV_DIR="${GITHUB_WORKSPACE}/_build/domain-invs"' in text, (
        "VC-19：SHARD 构建前应以绝对路径 export OKF_INV_DIR，conf.py 基于此目录加载其他域 inv"
    )

    # VC-14：WARMUP cache key 含 doc/bundles/**/*.md（全 md 参与哈希，不放过 facts 变更）
    assert "cache-domain-invs" in text or "dinv-v1" in text, (
        "WARMUP cache id 应与 environment.pickle cache 区分（独立 inv 缓存池）"
    )
    assert "hashFiles('doc/bundles/**/*.md'" in text, (
        "VC-14：WARMUP inv cache key hashFiles 必须包含 doc/bundles/**/*.md 全量 md"
    )
    assert "'doc/conf.py'" in text or '"doc/conf.py"' in text, (
        "WARMUP inv cache key 必须包含 doc/conf.py（mapping 变了 inv header 版本变）"
    )

    # 顺序保证（- name: 步骤行号 WARMUP < SHARD；注释行不计）
    step_lines = [
        (i + 1, ln) for i, ln in enumerate(text.splitlines())
        if ln.lstrip().startswith("- name:")
    ]
    warmup_line = next((lineno for lineno, ln in step_lines if "WARMUP" in ln), 0)
    shard_line = next((lineno for lineno, ln in step_lines if "SHARD" in ln), 0)
    assert 0 < warmup_line < shard_line, (
        f"VC-19：WARMUP step(L{warmup_line}) 必须在 SHARD step(L{shard_line}) 之前，"
        f"否则 SHARD 读取 inv 时 WARMUP 还没写 OKF_INV_DIR"
    )


# ---------------------------------------------------------------------------
# T7 — P4 smoke：conf.py intersphinx_mapping 三工况 0/1/8 定量验证 VC-3/5
# ---------------------------------------------------------------------------

def _p4_load_conf_with_env(monkeypatch, **env_overrides) -> dict:
    """隔离加载 _OKF_CONF_PY，返回其 intersphinx_mapping（monkeypatch 控制 os.environ）。"""
    for k in ("OKF_BUILD_DOMAIN", "OKF_INV_DIR"):
        monkeypatch.delenv(k, raising=False)
    for k, v in env_overrides.items():
        monkeypatch.setenv(k, str(v))

    # 每工况清掉旧模块缓存（避免 importlib 复用前次赋值）
    cache_key = f"_okf_p4_{abs(hash(tuple(sorted(env_overrides.items())))) % 1000000}"
    return _load_module(_OKF_CONF_PY, cache_key).intersphinx_mapping


def _p4_count_local_inv_paths(mapping: dict) -> int:
    """数 okf-* 前缀中 inventory_path 非 None 的数量。"""
    n = 0
    for k, v in mapping.items():
        if not k.startswith("okf-"):
            continue
        if isinstance(v, (tuple, list)) and len(v) >= 2 and v[1] is not None:
            n += 1
    return n


def test_t7_conf_intersphinx_mapping_vc3_vc5_three_regimes(monkeypatch, tmp_path):
    """T7: 三工况定量验证 VC-3（分片模式注入8域本地inv映射）/ VC-5（inv不存在跳过None）。

    Regime A: OKF_BUILD_DOMAIN=jishu + inv_dir不存在 → 0/8 okf-* 含inv_path（VC-5跳过）
    Regime B: 仅放 guoxue.inv → 1/8 okf-* 含inv_path（线性梯度）
    Regime C: 8个域.inv 全存在 → 8/8 okf-* 含inv_path（VC-3全量恢复）
    Regime FULL: 不设 OKF_BUILD_DOMAIN → 0 个 okf-* 本地映射（main 分支行为不变）
    """
    ALL_DOMAINS = ("meta", "guoxue", "zhexue", "kexue", "wenxue",
                   "yixue", "sheke", "yishu", "jishu")
    CURRENT = "jishu"

    # --- Regime FULL（不分片，不应注入任何 okf-* 本地域映射） ---
    with monkeypatch.context() as m:
        mapping_full = _p4_load_conf_with_env(m)
        n_full = sum(1 for k in mapping_full if k.startswith("okf-"))
        assert n_full == 0, (
            f"FULL（无OKF_BUILD_DOMAIN）不应注入 okf-* 本地域映射，实{n_full}"
        )
        # 3 个外部映射（python/sphinx/myst-parser）仍在
        assert all(x in mapping_full for x in ("python", "sphinx", "myst-parser"))

    inv_dir_none = tmp_path / "no_invs_here"   # 不存在 → 走 VC-5 None 跳过

    # --- Regime A：无 inv 目录 → 0/8（VC-5 基线） ---
    with monkeypatch.context() as m:
        mapping_a = _p4_load_conf_with_env(
            m, OKF_BUILD_DOMAIN=CURRENT, OKF_INV_DIR=str(inv_dir_none),
        )
        a_count = _p4_count_local_inv_paths(mapping_a)
        assert a_count == 0, f"Regime A 基线失败：期望0/8 None跳过，实{a_count}"

    # --- Regime B：单域 guoxue.inv 仅一份（> VC-17 8192 bytes）---
    inv_b = tmp_path / "invs_b"
    inv_b.mkdir()
    (inv_b / "guoxue.inv").write_bytes(b"x" * 9000)
    with monkeypatch.context() as m:
        mapping_b = _p4_load_conf_with_env(
            m, OKF_BUILD_DOMAIN=CURRENT, OKF_INV_DIR=str(inv_b),
        )
        b_count = _p4_count_local_inv_paths(mapping_b)
        assert b_count == 1, f"Regime B 单域失败：期望1/8，实{b_count}"
        # 文件名精准 <d>.inv
        assert mapping_b["okf-guoxue"][1] and \
            str(mapping_b["okf-guoxue"][1]).replace("\\", "/").endswith("/guoxue.inv")

    # --- Regime C：8 域 inv 全补齐（除 current jishu）---
    inv_c = tmp_path / "invs_c"
    inv_c.mkdir()
    for d in ALL_DOMAINS:
        if d == CURRENT:
            continue
        (inv_c / f"{d}.inv").write_bytes(b"x" * 9000)
    with monkeypatch.context() as m:
        mapping_c = _p4_load_conf_with_env(
            m, OKF_BUILD_DOMAIN=CURRENT, OKF_INV_DIR=str(inv_c),
        )
        c_count = _p4_count_local_inv_paths(mapping_c)
        assert c_count == 8, (
            f"Regime C 全量恢复失败：期望8/8 okf-* 含inv_path，实{c_count}"
            f"；缺失域：{[d for d in ALL_DOMAINS if d != CURRENT and (f'okf-{d}' not in mapping_c or mapping_c[f'okf-{d}'][1] is None)]}"
        )
    # 0 → 1 → 8 线性梯度全命中 ✓（三工况分别走完 VC-5→部分→VC-3 全量）


# ---------------------------------------------------------------------------
# T8 — 修复 Sphinx 9 inventory builder KeyError：自定义 ext + ns 注册
# ---------------------------------------------------------------------------

def test_t8_inventory_builder_custom_extension_and_ns_registration():
    """T8: Sphinx 9 不再注册 inventory builder 入口点。
    修复三件套（source 级断言避免真跑 sphinx-build）：

    1) conf.py extensions 列表显式引用 `_ext.okf_inventory_builder`（使
       Sphinx setup_extension(L298) 在 preload_builder(L302) 之前注册该
       Builder 到 registry.builders；conf.py `def setup(app)` 在 L309 才
       执行，太晚，会 SphinxError Builder 未注册。
    2) doc/_ext/okf_inventory_builder.py 定义 class OKFInventoryBuilder：
       name="inventory"、format="inventory"（≠"html"→绕过 validate_math_renderer
       中针对 html format 的 math_renderer_name 属性存在性校验）、
       get_target_uri=docname.html、finish() 调 InventoryFile.dump
       写 objects.inv。
    3) tasks/__init__.py ns.add_task(build_invs) 暴露 invoke build-invs
       根命令（否则 CLI 报 No idea what 'build-invs' is!）。
    """
    # --- 断言 1：conf.py extensions 字符串含自定义 ext ---
    conf_text = _OKF_CONF_PY.read_text(encoding="utf-8")
    assert "_ext.okf_inventory_builder" in conf_text, (
        "conf.py extensions 必须显式包含 `_ext.okf_inventory_builder` 字符串引用"
        "（setup_extension 在 preload_builder 之前注册 Builder 到 registry）"
    )

    # --- 断言 2：自定义 Builder ext 存在 ---
    assert _OKF_INV_EXT.is_file(), (
        "自定义 inventory builder ext 文件不存在：doc/_ext/okf_inventory_builder.py"
    )
    ext_mod = _load_module(_OKF_INV_EXT, "_t8_inv_ext")
    assert hasattr(ext_mod, "OKFInventoryBuilder"), (
        "ext 应定义 class OKFInventoryBuilder(Builder)"
    )
    BuilderClass = ext_mod.OKFInventoryBuilder
    assert getattr(BuilderClass, "name", None) == "inventory", (
        "自定义 Builder 必须 name='inventory' 才能匹配 -b inventory CLI"
    )
    # format != "html"：绕过 sphinx.builders.html.validate_math_renderer
    # 对 format=="html" builders 强制 math_renderer_name 属性存在
    assert getattr(BuilderClass, "format", None) != "html", (
        "format 不能='html'，否则 Sphinx 9 validate_math_renderer 在"
        " builder-inited 事件里强制访问 .math_renderer_name 不存在会 AttributeError"
    )
    assert getattr(BuilderClass, "allow_parallel", False) is True, (
        "allow_parallel=True 与其他域分片 -j 并行构建一致"
    )

    # get_target_uri 行为：docname -> docname.html（与 StandaloneHTMLBuilder
    # 完全对齐，保证 intersphinx_mapping 加载后 xref 跳转到正确.html锚点）
    inst_dummy = None
    try:
        inst_dummy = BuilderClass.__new__(BuilderClass)
        uri = BuilderClass.get_target_uri(inst_dummy, "bundles/meta/okf-spec/index")
        assert uri == "bundles/meta/okf-spec/index.html", (
            f"get_target_uri 应返回 docname.html，实={uri!r}"
        )
    finally:
        del inst_dummy

    # finish() 代码路径里含 InventoryFile.dump(...) 调写出 objects.inv
    ext_src = _OKF_INV_EXT.read_text(encoding="utf-8")
    assert "InventoryFile.dump" in ext_src and "objects.inv" in ext_src, (
        "finish() 必须 InventoryFile.dump(self.outdir/objects.inv) 写出"
    )
    # setup(app) 含 add_builder(OKFInventoryBuilder, override=True) override=True
    # 防止未来 Sphinx 又内置 inventory builder 时冲突 ExtensionError
    assert "app.add_builder(OKFInventoryBuilder, override=True)" in ext_src, (
        "setup(app) 必须 override=True 注册，兼容未来 Sphinx 恢复内置 inventory"
    )

    # --- 断言 3：tasks/__init__.py ns 注册 build-invs 根任务 ---
    ns_text = _OKF_TASKS_INIT.read_text(encoding="utf-8")
    assert "ns.add_task(docs.build_invs)" in ns_text, (
        "tasks/__init__.py 必须 ns.add_task(docs.build_invs) 使"
        " `invoke build-invs` CLI 可用（否则报 No idea what 'build-invs' is!）"
    )


