"""skill-auto-loader 单元测试。

覆盖 models、discovery、parser、cache、report、cli 六个模块的核心功能。
按依赖顺序预加载模块到 sys.modules，避免 lib/ 包导入链导致的 sys.path 污染问题。
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
CLI_PATH = SCRIPTS_DIR / "cli.py"
AGENTS_SCRIPTS_DIR = PROJECT_ROOT / ".agents" / "scripts"

_MODULE_FILES = {
    "models": SCRIPTS_DIR / "models.py",
    "discovery": SCRIPTS_DIR / "discovery.py",
    "parser": SCRIPTS_DIR / "parser.py",
    "cache": SCRIPTS_DIR / "cache.py",
    "report": SCRIPTS_DIR / "report.py",
    "cli": SCRIPTS_DIR / "cli.py",
}

_MODULE_LOAD_ORDER = ["models", "discovery", "parser", "cache", "report", "cli"]


def _ensure_agents_scripts_in_path():
    agents_str = str(AGENTS_SCRIPTS_DIR)
    if agents_str not in sys.path:
        sys.path.insert(0, agents_str)


def _ensure_scripts_in_path():
    scripts_str = str(SCRIPTS_DIR)
    while scripts_str in sys.path:
        sys.path.remove(scripts_str)
    sys.path.insert(0, scripts_str)


def load_module(name: str):
    """按依赖顺序加载目标模块，预注册到 sys.modules 避免路径冲突。

    核心机制：Python 导入时先查 sys.modules 缓存，再查 sys.path。
    在加载会触发 lib 导入的 parser/cache/report/cli 之前，
    先把它们依赖的 models/discovery/parser 等预加载到 sys.modules，
    这样即使 lib 包的导入链将 lib/ 插入 sys.path[0] 造成污染，
    后续的 from models import ... 等语句也会命中 sys.modules 缓存，
    不会去 sys.path 搜索，从而避免导入 lib/cache.py 或 lib/cli.py。
    """
    if name in sys.modules:
        return sys.modules[name]

    _ensure_agents_scripts_in_path()
    _ensure_scripts_in_path()

    target_idx = _MODULE_LOAD_ORDER.index(name)
    for i, mod_name in enumerate(_MODULE_LOAD_ORDER):
        if i >= target_idx:
            break
        if mod_name in sys.modules:
            continue
        file_path = _MODULE_FILES[mod_name]
        spec = importlib.util.spec_from_file_location(mod_name, str(file_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module {mod_name} from {file_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = module
        spec.loader.exec_module(module)

    file_path = _MODULE_FILES[name]
    spec = importlib.util.spec_from_file_location(name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module {name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    _ensure_scripts_in_path()
    return module


def _purge_target_modules():
    target_mods = set(_MODULE_LOAD_ORDER)
    for mod_name in list(sys.modules.keys()):
        if mod_name in target_mods:
            del sys.modules[mod_name]


@pytest.fixture(autouse=True)
def _isolate_modules():
    """每个测试前清理模块缓存，确保测试隔离。"""
    _purge_target_modules()
    _ensure_scripts_in_path()
    yield
    _purge_target_modules()
    _ensure_scripts_in_path()


# ==================== Models 测试 ====================


class TestModels:
    """测试数据模型（models.py）。"""

    def test_skill_metadata_creation(self):
        """创建 SkillMetadata，确认字段正确。"""
        models = load_module("models")
        SkillMetadata = models.SkillMetadata
        SkillStatus = models.SkillStatus

        meta = SkillMetadata(
            name="test-skill",
            skill_path="path/to/SKILL.md",
            source="local",
            description="A test skill",
            version="1.0.0",
            status=SkillStatus.OK,
            issues=["issue1"],
            raw_metadata={"key": "value"},
        )

        assert meta.name == "test-skill"
        assert meta.skill_path == "path/to/SKILL.md"
        assert meta.source == "local"
        assert meta.description == "A test skill"
        assert meta.version == "1.0.0"
        assert meta.status == SkillStatus.OK
        assert meta.issues == ["issue1"]
        assert meta.raw_metadata == {"key": "value"}

    def test_skill_metadata_to_dict(self):
        """确认 to_dict() 返回可 JSON 序列化的字典，枚举值转为字符串。"""
        models = load_module("models")
        SkillMetadata = models.SkillMetadata
        SkillStatus = models.SkillStatus

        meta = SkillMetadata(
            name="test-skill",
            skill_path="path/to/SKILL.md",
            source="vendor",
            description="Test",
            status=SkillStatus.WARNING,
            issues=["missing section"],
        )

        data = meta.to_dict()

        assert isinstance(data, dict)
        assert data["name"] == "test-skill"
        assert data["status"] == "warning"
        assert data["source"] == "vendor"
        assert data["issues"] == ["missing section"]

        json_str = json.dumps(data, ensure_ascii=False)
        loaded = json.loads(json_str)
        assert loaded == data

    def test_scan_result_stats(self):
        """确认 add_stats() 统计计算正确（ok/warning/error 数量）。"""
        models = load_module("models")
        SkillMetadata = models.SkillMetadata
        SkillStatus = models.SkillStatus
        ScanResult = models.ScanResult

        result = ScanResult()
        result.skills.append(SkillMetadata(name="s1", skill_path="s1", source="local", status=SkillStatus.OK))
        result.skills.append(SkillMetadata(name="s2", skill_path="s2", source="local", status=SkillStatus.OK))
        result.skills.append(SkillMetadata(name="s3", skill_path="s3", source="local", status=SkillStatus.WARNING))
        result.skills.append(SkillMetadata(name="s4", skill_path="s4", source="local", status=SkillStatus.ERROR))
        result.conflicts.append({"name": "dup", "count": 2, "files": ["a", "b"]})

        stats = result.add_stats()

        assert stats["total"] == 4
        assert stats["ok"] == 2
        assert stats["warning"] == 1
        assert stats["error"] == 1
        assert stats["conflicts"] == 1

    def test_scan_error_to_dict(self):
        """确认 ScanError.to_dict() 正确序列化为字典。"""
        models = load_module("models")
        ScanError = models.ScanError

        err = ScanError(
            file_path="test/SKILL.md",
            error_type="missing_name",
            message="Name field is required",
            suggestion="Add name field",
        )

        data = err.to_dict()

        assert isinstance(data, dict)
        assert data["file_path"] == "test/SKILL.md"
        assert data["error_type"] == "missing_name"
        assert data["message"] == "Name field is required"
        assert data["suggestion"] == "Add name field"

        json_str = json.dumps(data, ensure_ascii=False)
        loaded = json.loads(json_str)
        assert loaded == data


# ==================== Discovery 测试 ====================


class TestDiscovery:
    """测试技能发现模块（discovery.py）。"""

    def test_default_scan_finds_vendor_skills(self):
        """默认扫描发现 vendor 下至少 9 个技能。"""
        discovery = load_module("discovery")
        discover_skill_files = discovery.discover_skill_files

        files = discover_skill_files(PROJECT_ROOT)

        vendor_files = [(p, s) for p, s in files if s == "vendor"]
        assert len(vendor_files) >= 9, f"Expected at least 9 vendor skills, found {len(vendor_files)}"

    def test_discovery_excludes_templates(self):
        """确认不包含 SKILL-TEMPLATE 文件。"""
        discovery = load_module("discovery")
        discover_skill_files = discovery.discover_skill_files

        files = discover_skill_files(PROJECT_ROOT)

        for path, _ in files:
            assert "SKILL-TEMPLATE" not in path.name, f"Template file should be excluded: {path}"

    def test_extra_dirs_parameter(self, tmp_path):
        """使用临时目录创建测试 SKILL.md，确认 extra_dirs 能发现它。"""
        discovery = load_module("discovery")
        discover_skill_files = discovery.discover_skill_files

        extra_dir = tmp_path / "custom-skills" / "my-skill"
        extra_dir.mkdir(parents=True)
        skill_md = extra_dir / "SKILL.md"
        skill_md.write_text("---\nname: my-custom-skill\ndescription: A custom skill\n---\n# My Skill\n", encoding="utf-8")

        project_root = tmp_path
        files = discover_skill_files(project_root, extra_dirs=["custom-skills"])

        assert len(files) >= 1
        found_paths = [str(p) for p, _ in files]
        assert any("my-skill" in p for p in found_paths)


# ==================== Parser 测试 ====================


class TestParser:
    """测试 Frontmatter 解析模块（parser.py）。"""

    def _create_skill_md(self, tmp_path: Path, frontmatter: str | None, body: str = "") -> Path:
        """在临时目录创建 SKILL.md 测试文件。"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        content = ""
        if frontmatter is not None:
            content = f"---\n{frontmatter}\n---\n"
        content += body
        skill_file.write_text(content, encoding="utf-8")
        return skill_file

    def test_parse_valid_skill_md(self, tmp_path):
        """解析最小合法 SKILL.md（含 name 和 description frontmatter），返回 status=OK。"""
        parser = load_module("parser")
        models = load_module("models")
        parse_skill_file = parser.parse_skill_file
        SkillStatus = models.SkillStatus

        skill_file = self._create_skill_md(
            tmp_path,
            "name: valid-skill\ndescription: A valid skill",
            "# Valid Skill\n\nInput\nDependencies\nDeployment\nError Handling\nChangelog\n",
        )

        meta, errors = parse_skill_file(skill_file, "local", PROJECT_ROOT, mode="relaxed")
        _ensure_scripts_in_path()

        assert meta is not None
        assert len(errors) == 0
        assert meta.name == "valid-skill"
        assert meta.description == "A valid skill"
        assert meta.status == SkillStatus.OK

    def test_parse_missing_name(self, tmp_path):
        """创建无 name 的 frontmatter，返回 error（missing_name）。"""
        parser = load_module("parser")
        models = load_module("models")
        parse_skill_file = parser.parse_skill_file
        SkillStatus = models.SkillStatus

        skill_file = self._create_skill_md(
            tmp_path,
            "description: Missing name",
            "# Skill without name\n",
        )

        meta, errors = parse_skill_file(skill_file, "local", PROJECT_ROOT)
        _ensure_scripts_in_path()

        assert len(errors) == 1
        assert errors[0].error_type == "missing_name"
        assert meta is not None
        assert meta.status == SkillStatus.ERROR

    def test_parse_missing_frontmatter(self, tmp_path):
        """创建无 frontmatter 的文件，返回 error（missing_frontmatter）。"""
        parser = load_module("parser")
        parse_skill_file = parser.parse_skill_file

        skill_dir = tmp_path / "no-frontmatter"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("# No Frontmatter\n\nJust content without metadata.\n", encoding="utf-8")

        meta, errors = parse_skill_file(skill_file, "local", PROJECT_ROOT)
        _ensure_scripts_in_path()

        assert meta is None
        assert len(errors) == 1
        assert errors[0].error_type == "missing_frontmatter"

    def test_strict_mode_warnings(self, tmp_path):
        """只有 name/description 但正文无推荐章节时，strict 模式返回 WARNING，relaxed 模式返回 OK。"""
        parser = load_module("parser")
        models = load_module("models")
        parse_skill_file = parser.parse_skill_file
        SkillStatus = models.SkillStatus

        skill_file = self._create_skill_md(
            tmp_path,
            "name: minimal-skill\ndescription: Minimal skill only",
            "# Minimal Skill\n\nThis is a minimal skill with no recommended sections.\n",
        )

        meta_strict, errors_strict = parse_skill_file(skill_file, "local", PROJECT_ROOT, mode="strict")
        _ensure_scripts_in_path()
        meta_relaxed, errors_relaxed = parse_skill_file(skill_file, "local", PROJECT_ROOT, mode="relaxed")
        _ensure_scripts_in_path()

        assert meta_strict is not None
        assert meta_strict.status == SkillStatus.WARNING
        assert len(meta_strict.issues) > 0

        assert meta_relaxed is not None
        assert meta_relaxed.status == SkillStatus.OK
        assert len(meta_relaxed.issues) == 0

    def test_parse_all_skills_no_duplicates(self):
        """全量解析无冲突（已知当前数据无冲突）。"""
        parser = load_module("parser")
        parse_all_skills = parser.parse_all_skills

        result = parse_all_skills(PROJECT_ROOT, mode="relaxed")
        _ensure_scripts_in_path()

        assert len(result.conflicts) == 0, f"Expected no conflicts, found: {result.conflicts}"
        assert len(result.skills) >= 9


# ==================== Cache 测试 ====================


class TestCache:
    """测试增量缓存模块（cache.py）。"""

    def test_cache_save_and_load(self, tmp_path):
        """首次解析后保存缓存，再次加载缓存数据一致。"""
        cache = load_module("cache")
        save_cache = cache.save_cache
        load_cache = cache.load_cache

        parser = load_module("parser")
        parse_all_skills = parser.parse_all_skills

        result = parse_all_skills(PROJECT_ROOT, mode="relaxed")
        _ensure_scripts_in_path()
        cache_path = tmp_path / "test-cache.json"

        save_cache(cache_path, result, "relaxed")
        assert cache_path.exists()

        loaded = load_cache(cache_path)
        assert loaded is not None
        assert loaded["version"] == "1.0"
        assert loaded["mode"] == "relaxed"
        assert "files" in loaded
        assert len(loaded["files"]) == len(result.skills)

    def test_cache_hit_on_second_run(self, tmp_path):
        """第二次运行命中缓存。"""
        cache = load_module("cache")
        get_cached_or_parse = cache.get_cached_or_parse
        save_cache = cache.save_cache

        parser = load_module("parser")
        parse_all_skills = parser.parse_all_skills

        result1 = parse_all_skills(PROJECT_ROOT, mode="relaxed")
        _ensure_scripts_in_path()
        cache_path = tmp_path / "test-cache.json"
        save_cache(cache_path, result1, "relaxed")

        _ensure_scripts_in_path()
        result2 = get_cached_or_parse(
            project_root=PROJECT_ROOT,
            mode="relaxed",
            use_cache=True,
            cache_path=cache_path,
            verbose=False,
        )
        _ensure_scripts_in_path()

        assert len(result2.skills) == len(result1.skills)

        skill_names_1 = sorted(s.name for s in result1.skills)
        skill_names_2 = sorted(s.name for s in result2.skills)
        assert skill_names_1 == skill_names_2

    def test_cache_invalidation(self, tmp_path):
        """修改文件 mtime/size 后该文件被重新解析。"""
        cache = load_module("cache")
        get_cached_or_parse = cache.get_cached_or_parse

        test_skill_dir = tmp_path / "test-skills" / "test-skill"
        test_skill_dir.mkdir(parents=True)
        skill_file = test_skill_dir / "SKILL.md"
        skill_file.write_text(
            "---\nname: test-cache-skill\ndescription: Version 1\n---\n# Test\nInput\nDependencies\nDeployment\nError Handling\nChangelog\n",
            encoding="utf-8",
        )

        project_root = tmp_path
        _ensure_scripts_in_path()
        result1 = get_cached_or_parse(
            project_root=project_root,
            extra_dirs=["test-skills"],
            mode="relaxed",
            use_cache=True,
            cache_path=tmp_path / ".cache.json",
            verbose=False,
        )
        _ensure_scripts_in_path()

        assert len(result1.skills) >= 1
        skill1 = next((s for s in result1.skills if s.name == "test-cache-skill"), None)
        assert skill1 is not None
        assert skill1.description == "Version 1"

        time.sleep(0.1)
        skill_file.write_text(
            "---\nname: test-cache-skill\ndescription: Version 2\n---\n# Test\nInput\nDependencies\nDeployment\nError Handling\nChangelog\n",
            encoding="utf-8",
        )

        _ensure_scripts_in_path()
        result2 = get_cached_or_parse(
            project_root=project_root,
            extra_dirs=["test-skills"],
            mode="relaxed",
            use_cache=True,
            cache_path=tmp_path / ".cache.json",
            verbose=False,
        )
        _ensure_scripts_in_path()

        skill2 = next((s for s in result2.skills if s.name == "test-cache-skill"), None)
        assert skill2 is not None
        assert skill2.description == "Version 2"


# ==================== Report 测试 ====================


class TestReport:
    """测试报告生成模块（report.py）。"""

    def test_generate_json_report(self, tmp_path):
        """生成 JSON 后用 json.load() 读取验证结构正确。"""
        report = load_module("report")
        generate_json_report = report.generate_json_report

        parser = load_module("parser")
        parse_all_skills = parser.parse_all_skills

        result = parse_all_skills(PROJECT_ROOT, mode="relaxed")
        _ensure_scripts_in_path()
        output_path = tmp_path / "skill-registry.json"

        generate_json_report(result, output_path)

        assert output_path.exists()
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "scan_time" in data
        assert "skills" in data
        assert "errors" in data
        assert "conflicts" in data
        assert "stats" in data
        assert "total" in data["stats"]
        assert "ok" in data["stats"]
        assert isinstance(data["skills"], list)

    def test_generate_markdown_report(self, tmp_path):
        """生成 Markdown 后检查包含关键标题。"""
        report = load_module("report")
        generate_markdown_report = report.generate_markdown_report

        parser = load_module("parser")
        parse_all_skills = parser.parse_all_skills

        result = parse_all_skills(PROJECT_ROOT, mode="relaxed")
        _ensure_scripts_in_path()
        output_path = tmp_path / "skill-registry.md"

        generate_markdown_report(result, output_path)

        assert output_path.exists()
        content = output_path.read_text(encoding="utf-8")

        assert "# Skill Registry Index" in content
        assert "Vendor Skills" in content or "Local Skills" in content


# ==================== CLI 测试 ====================


class TestCLI:
    """测试命令行接口（cli.py）。

    CLI 测试使用 subprocess 在独立进程中运行，避免 sys.path 问题。
    """

    def test_cli_help(self):
        """运行 --help，退出码 0，输出包含 Usage 或帮助信息。"""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(PROJECT_ROOT),
        )

        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert "usage" in output.lower() or "帮助" in output or "Usage" in output

    def test_cli_version(self):
        """--version 输出 0.1.0。"""
        result = subprocess.run(
            [sys.executable, str(CLI_PATH), "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(PROJECT_ROOT),
        )

        assert result.returncode == 0
        assert "0.1.0" in result.stdout

    def test_cli_default_run(self, tmp_path):
        """默认运行成功，退出码 0。"""
        output_path = tmp_path / "test-output.json"

        result = subprocess.run(
            [
                sys.executable,
                str(CLI_PATH),
                "--force",
                "--mode",
                "relaxed",
                "--no-cache",
                "--output",
                str(output_path),
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(PROJECT_ROOT),
        )

        assert result.returncode == 0, f"CLI failed with stderr: {result.stderr}\nstdout: {result.stdout}"
        assert output_path.exists()

        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "stats" in data
        assert data["stats"]["total"] >= 9
