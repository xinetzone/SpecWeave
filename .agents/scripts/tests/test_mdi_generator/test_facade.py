import json
from pathlib import Path

from mdi.generator import MDIGenerator

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent.parent


class TestMDIGeneratorFacade:

    def test_supported_languages(self):
        langs = MDIGenerator.supported_languages()
        assert "python" in langs
        assert "typescript" in langs
        assert "openapi" in langs
        assert "mcp" in langs
        assert "markdown" in langs
        assert "cli" in langs
        assert "pytest" in langs
        assert "jest" in langs

    def test_invalid_language_raises(self):
        import pytest
        with pytest.raises(ValueError):
            MDIGenerator(lang="invalid_lang")

    def test_generate_python_from_doc(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="python")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) > 0
        assert any(f.suffix == ".py" for f in files)

    def test_generate_typescript(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="typescript")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) > 0
        assert any(f.suffix == ".ts" for f in files)

    def test_generate_openapi(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="openapi")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) == 1
        spec = json.loads(files[0].read_text(encoding="utf-8"))
        assert "openapi" in spec

    def test_generate_mcp(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="mcp")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) == 1
        tools = json.loads(files[0].read_text(encoding="utf-8"))
        assert isinstance(tools, list)

    def test_generate_markdown(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="markdown")
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) == 1
        assert files[0].suffix == ".md"

    def test_generate_cli(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="cli")
        files = gen.generate(sample_webapi_doc, tmp_path)
        cli_py = [f for f in files if f.name == "cli.py"]
        assert len(cli_py) > 0

    def test_generate_pytest(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="pytest")
        files = gen.generate(sample_webapi_doc, tmp_path)
        test_py = [f for f in files if f.name.startswith("test_") and f.suffix == ".py"]
        assert len(test_py) >= 1
        conftest = [f for f in files if f.name == "conftest.py"]
        assert len(conftest) == 1

    def test_generate_jest(self, sample_webapi_doc, tmp_path):
        gen = MDIGenerator(lang="jest")
        files = gen.generate(sample_webapi_doc, tmp_path)
        test_js = [f for f in files if f.name.endswith(".test.js")]
        assert len(test_js) >= 1
        config = [f for f in files if f.name == "jest.config.js"]
        assert len(config) == 1

    def test_generate_file(self, tmp_path):
        skill_path = PROJECT_ROOT / ".agents/skills/link-check-cmd/SKILL.md"
        if skill_path.exists():
            out_dir = tmp_path / "out"
            gen = MDIGenerator(lang="python")
            files = gen.generate_file(skill_path, out_dir)
            assert len(files) > 0
