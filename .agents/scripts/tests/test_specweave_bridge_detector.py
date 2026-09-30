"""specweave-bridge 工作区检测模块单元测试（双信号识别）。

被测对象为 ``specweave-bridge-skeleton/``（Hermes 插件规范源码，零第三方依赖），
覆盖：

- detector.py 主信号（AGENTS.md + 「启动协议」关键词）
- detector.py 兼容信号（.agents/ 且 roles/ 与 skills/ 同时存在）
- 通用技能目录误报回归（仅 skills/ 不判定，如 ~/.agents/skills）
- find_specweave_root 向上递归与「就近命中」语义
- detect_subregion 子区域判定
- __init__.py 中按识别信号分流的启动协议 brief 注入
- 打包一致性（plugin.yaml 与 _constants.PLUGIN_VERSION）

加载机制复用 install.py._load_plugin 的方式：以包形式从骨架目录加载插件
模块（注册 sys.modules 并设置 __path__），保证 ``from . import detector``
相对导入可用，无需将带连字符的骨架目录加入 sys.path。
"""

import importlib.util
import sys
from pathlib import Path

# .agents/scripts/tests/test_xxx.py → parents[3] 为仓库根
REPO_ROOT = Path(__file__).resolve().parents[3]
SKELETON_DIR = REPO_ROOT / "specweave-bridge-skeleton"


def _load_skeleton_pkg():
    """以包方式加载插件骨架（与 install.py._load_plugin 同机制）。"""
    name = "specweave_bridge_skeleton"
    if name in sys.modules:
        return sys.modules[name]
    init = SKELETON_DIR / "__init__.py"
    spec = importlib.util.spec_from_file_location(name, init)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    mod.__path__ = [str(SKELETON_DIR)]
    spec.loader.exec_module(mod)
    return mod


_PKG = _load_skeleton_pkg()
detector = _PKG.detector
_CONST = _PKG._constants


def _make_agents_md(path: Path, keyword: bool = True) -> None:
    """在 path 下写入测试用 AGENTS.md（含/不含「启动协议」关键词）。"""
    content = (
        "# 测试入口\n\n## 启动协议\n\n按步骤执行。\n"
        if keyword
        else "# 测试入口\n\n普通项目说明。\n"
    )
    (path / "AGENTS.md").write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# is_specweave_workspace / detect_workspace_signal —— 双信号判定
# ---------------------------------------------------------------------------


class TestWorkspaceSignals:
    def test_agents_md_with_keyword_hits_primary_signal(self, tmp_path):
        _make_agents_md(tmp_path, keyword=True)
        assert detector.is_specweave_workspace(str(tmp_path)) is True
        assert (
            detector.detect_workspace_signal(str(tmp_path))
            == _CONST.SIGNAL_AGENTS_MD
        )

    def test_agents_md_without_keyword_and_no_agents_dir(self, tmp_path):
        _make_agents_md(tmp_path, keyword=False)
        assert detector.is_specweave_workspace(str(tmp_path)) is False
        assert detector.detect_workspace_signal(str(tmp_path)) is None

    def test_missing_agents_md_and_agents_dir(self, tmp_path):
        assert detector.is_specweave_workspace(str(tmp_path)) is False

    def test_agents_dir_with_roles_and_skills_hits_compat_signal(self, tmp_path):
        (tmp_path / ".agents" / "roles").mkdir(parents=True)
        (tmp_path / ".agents" / "skills").mkdir()
        assert detector.is_specweave_workspace(str(tmp_path)) is True
        assert (
            detector.detect_workspace_signal(str(tmp_path))
            == _CONST.SIGNAL_AGENTS_DIR
        )

    def test_agents_dir_with_skills_only_is_not_workspace(self, tmp_path):
        # 回归：仅含单一 skills/ 的通用技能管理器目录（如 ~/.agents/skills）
        # 不判定为兼容工作区，避免用户主目录误判
        (tmp_path / ".agents" / "skills").mkdir(parents=True)
        assert detector.is_specweave_workspace(str(tmp_path)) is False
        assert detector.detect_workspace_signal(str(tmp_path)) is None

    def test_agents_dir_with_roles_only_is_not_workspace(self, tmp_path):
        (tmp_path / ".agents" / "roles").mkdir(parents=True)
        assert detector.is_specweave_workspace(str(tmp_path)) is False

    def test_agents_dir_with_unrelated_subdirs_is_not_workspace(self, tmp_path):
        # .agents/ 存在但无 roles/skills 特征子目录（如仅 docs/scripts）
        (tmp_path / ".agents" / "docs").mkdir(parents=True)
        (tmp_path / ".agents" / "scripts").mkdir()
        assert detector.is_specweave_workspace(str(tmp_path)) is False

    def test_empty_agents_dir_is_not_workspace(self, tmp_path):
        (tmp_path / ".agents").mkdir()
        assert detector.is_specweave_workspace(str(tmp_path)) is False

    def test_agents_md_without_keyword_falls_back_to_compat_signal(self, tmp_path):
        # AGENTS.md 存在但无关键词 + .agents/roles+skills 存在 → 兼容信号
        _make_agents_md(tmp_path, keyword=False)
        (tmp_path / ".agents" / "roles").mkdir(parents=True)
        (tmp_path / ".agents" / "skills").mkdir()
        assert (
            detector.detect_workspace_signal(str(tmp_path))
            == _CONST.SIGNAL_AGENTS_DIR
        )

    def test_primary_signal_wins_over_compat_signal(self, tmp_path):
        _make_agents_md(tmp_path, keyword=True)
        (tmp_path / ".agents" / "roles").mkdir(parents=True)
        (tmp_path / ".agents" / "skills").mkdir()
        assert (
            detector.detect_workspace_signal(str(tmp_path))
            == _CONST.SIGNAL_AGENTS_MD
        )

    def test_nonexistent_path_is_not_workspace(self, tmp_path):
        missing = tmp_path / "no-such-dir"
        assert detector.is_specweave_workspace(str(missing)) is False
        assert detector.detect_workspace_signal(str(missing)) is None


# ---------------------------------------------------------------------------
# find_specweave_root —— 向上递归 + 就近命中
# ---------------------------------------------------------------------------


class TestFindSpecweaveRoot:
    def test_finds_root_workspace_from_nested_dir(self, tmp_path):
        _make_agents_md(tmp_path, keyword=True)
        nested = tmp_path / "apps" / "my-app"
        nested.mkdir(parents=True)
        assert detector.find_specweave_root(str(nested)) == str(
            tmp_path.resolve()
        )

    def test_finds_compat_workspace_from_nested_dir(self, tmp_path):
        (tmp_path / ".agents" / "skills").mkdir(parents=True)
        (tmp_path / ".agents" / "roles").mkdir()
        nested = tmp_path / "sub" / "deep"
        nested.mkdir(parents=True)
        assert detector.find_specweave_root(str(nested)) == str(
            tmp_path.resolve()
        )

    def test_nearest_workspace_wins(self, tmp_path):
        # 外层主信号工作区 + 内层兼容工作区 → 就近命中内层
        _make_agents_md(tmp_path, keyword=True)
        inner = tmp_path / "packages" / "legacy"
        (inner / ".agents" / "roles").mkdir(parents=True)
        (inner / ".agents" / "skills").mkdir()
        deep = inner / "src"
        deep.mkdir()
        assert detector.find_specweave_root(str(deep)) == str(inner.resolve())

    def test_no_workspace_returns_none(self, tmp_path):
        # 注：假设沙箱目录的各级父目录均非 SpecWeave 工作区（常规 CI/开发机成立）
        sandbox = tmp_path / "plain" / "dir"
        sandbox.mkdir(parents=True)
        assert detector.find_specweave_root(str(sandbox)) is None


# ---------------------------------------------------------------------------
# detect_subregion —— 子区域判定
# ---------------------------------------------------------------------------


class TestDetectSubregion:
    def _make_root(self, tmp_path) -> str:
        _make_agents_md(tmp_path, keyword=True)
        return str(tmp_path.resolve())

    def test_apps_subregion(self, tmp_path):
        root = self._make_root(tmp_path)
        cwd = tmp_path / "apps" / "my-app"
        cwd.mkdir(parents=True)
        assert detector.detect_subregion(str(cwd), root) == "apps"

    def test_vendor_nested_subregion(self, tmp_path):
        root = self._make_root(tmp_path)
        cwd = tmp_path / "vendor" / "flexloop" / "apps" / "chaos"
        cwd.mkdir(parents=True)
        assert detector.detect_subregion(str(cwd), root) == "vendor"

    def test_root_itself_has_no_subregion(self, tmp_path):
        root = self._make_root(tmp_path)
        assert detector.detect_subregion(root, root) is None

    def test_inside_root_but_not_in_subregion_returns_none(self, tmp_path):
        # 位于 root 下但不属于 apps/projects/vendor → None
        root = self._make_root(tmp_path)
        sibling = tmp_path / "docs"
        sibling.mkdir()
        assert detector.detect_subregion(str(sibling), root) is None

    def test_outside_root_returns_none(self, tmp_path):
        root = self._make_root(tmp_path)
        other = tmp_path.parent / "specweave-bridge-outside-probe"
        other.mkdir(exist_ok=True)
        try:
            assert detector.detect_subregion(str(other), root) is None
        finally:
            other.rmdir()


# ---------------------------------------------------------------------------
# 启动协议 brief 注入 —— 按信号分流
# ---------------------------------------------------------------------------


class TestStartupBriefInjection:
    def test_root_workspace_gets_startup_brief(self, tmp_path, monkeypatch):
        _make_agents_md(tmp_path, keyword=True)
        monkeypatch.chdir(tmp_path)
        out = _PKG._on_pre_llm_call()
        assert out is not None
        assert "[SpecWeave 启动协议]" in out["context"]

    def test_compat_workspace_gets_compat_brief(self, tmp_path, monkeypatch):
        (tmp_path / ".agents" / "roles").mkdir(parents=True)
        (tmp_path / ".agents" / "skills").mkdir()
        monkeypatch.chdir(tmp_path)
        out = _PKG._on_pre_llm_call()
        assert out is not None
        assert "[SpecWeave 兼容模式]" in out["context"]

    def test_no_workspace_no_injection(self, tmp_path, monkeypatch):
        # 注：假设沙箱各级父目录均非 SpecWeave 工作区
        monkeypatch.chdir(tmp_path)
        assert _PKG._on_pre_llm_call() is None


# ---------------------------------------------------------------------------
# 仓库真实环境回归 + 打包一致性
# ---------------------------------------------------------------------------


class TestRepoIntegration:
    def test_repo_root_detected_as_root_workspace(self):
        assert detector.is_specweave_workspace(str(REPO_ROOT)) is True
        assert (
            detector.detect_workspace_signal(str(REPO_ROOT))
            == _CONST.SIGNAL_AGENTS_MD
        )

    def test_nested_compat_workspace_detected(self):
        # vendor/flexloop/apps/chaos 含 .agents/roles|skills，无「启动协议」AGENTS.md
        chaos = REPO_ROOT / "vendor" / "flexloop" / "apps" / "chaos"
        if not chaos.is_dir():  # submodule 未初始化时跳过
            return
        assert (
            detector.detect_workspace_signal(str(chaos))
            == _CONST.SIGNAL_AGENTS_DIR
        )

    def test_find_repo_root_from_skeleton(self):
        assert detector.find_specweave_root(str(SKELETON_DIR)) == str(
            REPO_ROOT.resolve()
        )


class TestPackaging:
    def test_plugin_yaml_version_matches_constants(self):
        plugin_yaml = (SKELETON_DIR / "plugin.yaml").read_text(
            encoding="utf-8"
        )
        version_lines = [
            line.strip()
            for line in plugin_yaml.splitlines()
            if line.strip().startswith("version:")
        ]
        assert version_lines == [f"version: {_CONST.PLUGIN_VERSION}"]
