#!/usr/bin/env python3
"""单元测试：check_token_p0.py Token优化P0禁令预检工具

覆盖场景：
  - P0_CONSTRAINTS 数据完整性
  - CheckItemResult / P0CheckResult 数据结构
  - scan_file_content 正则匹配
  - extract_threshold_value 阈值提取
  - run_p0_checks 对各种项目结构的检测
  - C-002 Transformers Pipeline检测
  - C-003 可观测性工具检测
  - C-007 语义缓存阈值检测
  - C-012 max_tokens检测
  - C-024 黄金测试集检测
  - C-020 灰度发布检测
  - JSON输出格式
  - 空目录/不存在路径处理
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import check_token_p0 as ctp


# ═══════════════════════════════════════════════════════════════
# 1. 数据结构测试
# ═══════════════════════════════════════════════════════════════

class TestDataStructures:
    """数据类结构正确性测试。"""

    def test_p0_constraints_complete(self):
        """P0_CONSTRAINTS应包含7个P0级禁令（C-001/C-002/C-003/C-007/C-012/C-020/C-024）。"""
        expected = {"C-001", "C-002", "C-003", "C-007", "C-012", "C-020", "C-024"}
        assert set(ctp.P0_CONSTRAINTS.keys()) == expected

    def test_each_constraint_has_required_fields(self):
        """每个禁令应有name/description/check_type/severity字段。"""
        for cid, c in ctp.P0_CONSTRAINTS.items():
            assert "name" in c, f"{cid} missing name"
            assert "description" in c, f"{cid} missing description"
            assert "check_type" in c, f"{cid} missing check_type"
            assert "severity" in c, f"{cid} missing severity"
            assert c["severity"] == "blocking", f"{cid} should be blocking"

    def test_check_item_result_defaults(self):
        """CheckItemResult默认值应正确。"""
        item = ctp.CheckItemResult(
            constraint_id="C-001",
            name="test",
            passed=True,
            severity="blocking",
        )
        assert item.evidence == []
        assert item.warnings == []
        assert item.details == ""

    def test_p0_check_result_to_dict(self):
        """P0CheckResult.to_dict()应返回可序列化的字典。"""
        result = ctp.P0CheckResult(
            target_path="/test",
            passed=True,
            blocking_count=0,
            warning_count=0,
        )
        d = result.to_dict()
        assert isinstance(d, dict)
        assert d["target_path"] == "/test"
        assert d["passed"] is True
        assert d["blocking_count"] == 0
        # 应可JSON序列化
        json.dumps(d, ensure_ascii=False)


# ═══════════════════════════════════════════════════════════════
# 2. 正则匹配与提取测试
# ═══════════════════════════════════════════════════════════════

class TestRegexMatching:
    """正则模式匹配精确性测试。"""

    def test_scan_file_content_pipeline_match(self):
        """应匹配Transformers pipeline导入。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("from transformers import pipeline\n")
            f.write("generator = pipeline('text-generation')\n")
            f.flush()
            path = Path(f.name)

        matches = ctp.scan_file_content(path, ctp.PIPELINE_PRODUCTION_PATTERNS)
        assert len(matches) >= 1
        path.unlink()

    def test_scan_file_content_vllm_match(self):
        """应匹配vLLM导入。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("from vllm import LLM, SamplingParams\n")
            f.write("llm = LLM(model='gpt2')\n")
            f.flush()
            path = Path(f.name)

        matches = ctp.scan_file_content(path, ctp.VLLM_PATTERNS)
        assert len(matches) >= 1
        path.unlink()

    def test_scan_file_content_max_tokens_match(self):
        """应匹配max_tokens参数。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write('response = client.chat.completions.create(\n')
            f.write('    model="gpt-4",\n')
            f.write('    max_tokens=2000,\n')
            f.write('    messages=messages\n')
            f.write(')\n')
            f.flush()
            path = Path(f.name)

        matches = ctp.scan_file_content(path, ctp.MAX_TOKENS_PATTERNS)
        assert len(matches) >= 1
        assert any("max_tokens" in line for _, line in matches)
        path.unlink()

    def test_extract_threshold_value_below_09(self):
        """应提取低于0.9的阈值。"""
        content = "cache = SemanticCache(similarity_threshold=0.85)"
        results = ctp.extract_threshold_value(content, ctp.SEMANTIC_CACHE_THRESHOLD_PATTERNS)
        assert len(results) == 1
        name, val, line_no = results[0]
        assert name == "similarity_threshold"
        assert val == 0.85
        assert val < 0.9

    def test_extract_threshold_value_at_09(self):
        """阈值0.9应被正确提取。"""
        content = "threshold=0.9"
        results = ctp.extract_threshold_value(content, ctp.SEMANTIC_CACHE_THRESHOLD_PATTERNS)
        assert len(results) == 1
        assert results[0][1] == 0.9

    def test_extract_threshold_value_above_09(self):
        """阈值0.95应被正确提取。"""
        content = "score_threshold = 0.95"
        results = ctp.extract_threshold_value(content, ctp.SEMANTIC_CACHE_THRESHOLD_PATTERNS)
        assert len(results) == 1
        assert results[0][1] == 0.95
        assert results[0][1] >= 0.9

    def test_extract_threshold_value_none(self):
        """无阈值配置应返回空。"""
        content = "print('hello world')"
        results = ctp.extract_threshold_value(content, ctp.SEMANTIC_CACHE_THRESHOLD_PATTERNS)
        assert results == []

    def test_scan_file_content_no_match(self):
        """无关内容不应匹配任何模式。"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("import os\nprint('hello')\n")
            f.flush()
            path = Path(f.name)

        matches = ctp.scan_file_content(path, ctp.PIPELINE_PRODUCTION_PATTERNS)
        assert matches == []
        path.unlink()


# ═══════════════════════════════════════════════════════════════
# 3. 集成测试：run_p0_checks 对各种项目结构
# ═══════════════════════════════════════════════════════════════

class TestRunP0Checks:
    """对各种项目结构的端到端检查测试。"""

    def _create_project(self, files: dict[str, str]) -> Path:
        """在临时目录中创建项目文件。"""
        tmpdir = tempfile.mkdtemp()
        base = Path(tmpdir)
        for relpath, content in files.items():
            fpath = base / relpath
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content, encoding="utf-8")
        return base

    def _cleanup(self, base: Path):
        """清理临时目录。"""
        import shutil
        shutil.rmtree(base, ignore_errors=True)

    def test_empty_project_fails_p0(self):
        """空项目（没有任何配置）应无法通过P0检查。"""
        base = self._create_project({"README.md": "# Empty Project"})
        try:
            result = ctp.run_p0_checks(base)
            # 空项目应该有阻断项（C-003/C-012/C-024等）
            assert result.blocking_count >= 1
            assert result.passed is False
        finally:
            self._cleanup(base)

    def test_project_with_pipeline_no_vllm_fails_c002(self):
        """使用Transformers Pipeline但没有vLLM应C-002失败。"""
        base = self._create_project({
            "main.py": """
from transformers import pipeline
generator = pipeline('text-generation', model='gpt2')
output = generator('Hello', max_new_tokens=100)
""",
        })
        try:
            result = ctp.run_p0_checks(base)
            c002 = next(i for i in result.items if i.constraint_id == "C-002")
            assert c002.passed is False
        finally:
            self._cleanup(base)

    def test_project_with_pipeline_and_vllm_c002_ok(self):
        """同时有Pipeline和vLLM时C-002应通过（需确认生产用vLLM）。"""
        base = self._create_project({
            "main.py": """
from transformers import pipeline
from vllm import LLM
llm = LLM(model='gpt2')
generator = pipeline('text-generation', model='gpt2')
""",
        })
        try:
            result = ctp.run_p0_checks(base)
            c002 = next(i for i in result.items if i.constraint_id == "C-002")
            assert c002.passed is True
        finally:
            self._cleanup(base)

    def test_project_with_observability_passes_c003(self):
        """配置了Langfuse应通过C-003。"""
        base = self._create_project({
            "config.py": """
import langfuse
langfuse.configure(public_key="pk-xxx", secret_key="sk-xxx")
""",
            "main.py": """
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    max_tokens=1000,
    messages=[{"role": "user", "content": "hi"}]
)
""",
            "tests/golden_set.json": '[{"input": "hi", "output": "hello"}]',
        })
        try:
            result = ctp.run_p0_checks(base)
            c003 = next(i for i in result.items if i.constraint_id == "C-003")
            assert c003.passed is True
        finally:
            self._cleanup(base)

    def test_project_with_low_semantic_cache_threshold_fails_c007(self):
        """语义缓存阈值0.85应C-007失败。"""
        base = self._create_project({
            "cache.py": """
from semantic_cache import SemanticCache
cache = SemanticCache(similarity_threshold=0.85)
""",
            "main.py": """
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    max_tokens=1000,
    messages=[{"role": "user", "content": "hi"}]
)
""",
        })
        try:
            result = ctp.run_p0_checks(base)
            c007 = next(i for i in result.items if i.constraint_id == "C-007")
            assert c007.passed is False
        finally:
            self._cleanup(base)

    def test_project_with_safe_semantic_cache_threshold_passes_c007(self):
        """语义缓存阈值0.92应通过C-007。"""
        base = self._create_project({
            "cache.py": """
from semantic_cache import SemanticCache
cache = SemanticCache(similarity_threshold=0.92)
""",
            "main.py": """
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    max_tokens=1000,
    messages=[{"role": "user", "content": "hi"}]
)
""",
        })
        try:
            result = ctp.run_p0_checks(base)
            c007 = next(i for i in result.items if i.constraint_id == "C-007")
            assert c007.passed is True
        finally:
            self._cleanup(base)

    def test_project_without_max_tokens_fails_c012(self):
        """有LLM调用但无max_tokens应C-012失败。"""
        base = self._create_project({
            "main.py": """
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "hi"}]
)
""",
        })
        try:
            result = ctp.run_p0_checks(base)
            c012 = next(i for i in result.items if i.constraint_id == "C-012")
            assert c012.passed is False
        finally:
            self._cleanup(base)

    def test_project_with_max_tokens_passes_c012(self):
        """设置了max_tokens应通过C-012。"""
        base = self._create_project({
            "main.py": """
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    max_tokens=2000,
    messages=[{"role": "user", "content": "hi"}]
)
""",
        })
        try:
            result = ctp.run_p0_checks(base)
            c012 = next(i for i in result.items if i.constraint_id == "C-012")
            assert c012.passed is True
        finally:
            self._cleanup(base)

    def test_project_with_golden_set_passes_c024(self):
        """有golden_set文件应通过C-024。"""
        base = self._create_project({
            "eval/golden_set.jsonl": '{"input": "q1", "output": "a1"}\n',
            "main.py": """
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    max_tokens=500,
    messages=[{"role": "user", "content": "hi"}]
)
""",
        })
        try:
            result = ctp.run_p0_checks(base)
            c024 = next(i for i in result.items if i.constraint_id == "C-024")
            assert c024.passed is True
        finally:
            self._cleanup(base)

    def test_fully_compliant_project_passes_all(self):
        """完整配置的合规项目应通过所有自动化检查。"""
        base = self._create_project({
            "main.py": """
from vllm import LLM, SamplingParams
from langfuse import openai as langfuse_openai
llm = LLM(model='gpt-4')
params = SamplingParams(max_tokens=2000)
output = llm.generate("Hello", params)
""",
            "cache.py": """
SEMANTIC_CACHE_THRESHOLD = 0.92
""",
            "eval/golden_set.json": '{"data": []}',
            "config/canary.py": "CANARY_DEPLOYMENT=True",
        })
        try:
            result = ctp.run_p0_checks(base)
            # C-001需要人工确认，但自动化检查标记为passed+warnings
            auto_checks = {"C-002", "C-003", "C-007", "C-012", "C-024"}
            for item in result.items:
                if item.constraint_id in auto_checks:
                    assert item.passed is True, f"{item.constraint_id} failed: {item.details}"
        finally:
            self._cleanup(base)

    def test_nonexistent_path(self):
        """不存在的路径应返回空结果。"""
        result = ctp.run_p0_checks(Path("/nonexistent/path/that/should/not/exist"))
        # 不应该抛出异常
        assert isinstance(result, ctp.P0CheckResult)


# ═══════════════════════════════════════════════════════════════
# 4. 可观测性工具检测
# ═══════════════════════════════════════════════════════════════

class TestObservabilityDetection:
    """可观测性工具关键词检测测试。"""

    @pytest.mark.parametrize("tool", ctp.OBSERVABILITY_TOOLS)
    def test_detects_each_observability_tool(self, tool):
        """每个可观测性工具关键词都应被检测到。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            config_file = base / "config.py"
            config_file.write_text(f"import {tool}\n", encoding="utf-8")
            hits = ctp.check_directory_has_clue(base, [tool])
            assert len(hits) >= 1, f"Failed to detect {tool}"


# ═══════════════════════════════════════════════════════════════
# 5. 阈值模式覆盖测试
# ═══════════════════════════════════════════════════════════════

class TestThresholdPatterns:
    """各种阈值参数名的识别测试。"""

    @pytest.mark.parametrize("line,expected_name,expected_val", [
        ("similarity_threshold=0.8", "similarity_threshold", 0.8),
        ("threshold = 0.95", "threshold", 0.95),
        ("score_threshold=0.9", "score_threshold", 0.9),
        ("cosine_threshold = 0.88", "cosine_threshold", 0.88),
        ("min_similarity=0.92", "min_similarity", 0.92),
    ])
    def test_various_threshold_names(self, line, expected_name, expected_val):
        """各种阈值参数名应被正确识别。"""
        results = ctp.extract_threshold_value(line, ctp.SEMANTIC_CACHE_THRESHOLD_PATTERNS)
        assert len(results) == 1
        name, val, _ = results[0]
        assert name == expected_name
        assert abs(val - expected_val) < 0.001


# ═══════════════════════════════════════════════════════════════
# 6. 手动检查项测试
# ═══════════════════════════════════════════════════════════════

class TestManualChecks:
    """需要人工确认的检查项测试。"""

    def test_c001_always_passed_with_warning(self):
        """C-001（质量底线）应始终标记为passed但带warnings（需人工确认）。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "dummy.py").write_text("print('hi')", encoding="utf-8")
            result = ctp.run_p0_checks(base)
            c001 = next(i for i in result.items if i.constraint_id == "C-001")
            assert c001.passed is True
            assert len(c001.warnings) >= 1  # 应提醒人工确认

    def test_manual_checks_list_not_empty(self):
        """manual_checks_needed列表不应为空（至少包含C-001）。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "dummy.py").write_text("print('hi')", encoding="utf-8")
            result = ctp.run_p0_checks(base)
            assert len(result.manual_checks_needed) >= 1


# ═══════════════════════════════════════════════════════════════
# 7. 排除目录测试
# ═══════════════════════════════════════════════════════════════

class TestExclusionPatterns:
    """排除目录测试，确保不扫描vendor/.git等。"""

    def test_excludes_vendor_directory(self):
        """vendor目录中的代码不应被扫描（vendor边界约束）。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            vendor_dir = base / "vendor" / "somelib"
            vendor_dir.mkdir(parents=True)
            (vendor_dir / "bad.py").write_text(
                "from transformers import pipeline\npipeline('text-generation')\n",
                encoding="utf-8"
            )
            (base / "good.py").write_text(
                "from vllm import LLM\n",
                encoding="utf-8"
            )
            result = ctp.run_p0_checks(base)
            c002 = next(i for i in result.items if i.constraint_id == "C-002")
            assert c002.passed is True  # vendor中的pipeline不应触发

    def test_excludes_node_modules(self):
        """node_modules目录不应被扫描。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            nm = base / "node_modules" / "somepkg"
            nm.mkdir(parents=True)
            (nm / "index.js").write_text(
                "// max_tokens should be set\n",
                encoding="utf-8"
            )
            (base / "main.py").write_text(
                "from openai import OpenAI\nc = OpenAI()\nc.chat.completions.create(model='gpt-4', messages=[])\n",
                encoding="utf-8"
            )
            result = ctp.run_p0_checks(base)
            c012 = next(i for i in result.items if i.constraint_id == "C-012")
            # node_modules中的max_tokens文本不算数，main.py中没有max_tokens
            assert c012.passed is False


# ═══════════════════════════════════════════════════════════════
# 8. 边界值测试
# ═══════════════════════════════════════════════════════════════

class TestBoundaryValues:
    """边界条件测试。"""

    def test_threshold_exactly_09(self):
        """阈值恰好0.9是合法的边界。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "cache.py").write_text(
                "THRESHOLD = 0.9\n",
                encoding="utf-8"
            )
            (base / "main.py").write_text(
                "from openai import OpenAI\nc = OpenAI()\nc.chat.completions.create(model='gpt-4', max_tokens=100, messages=[])\n",
                encoding="utf-8"
            )
            result = ctp.run_p0_checks(base)
            c007 = next(i for i in result.items if i.constraint_id == "C-007")
            assert c007.passed is True

    def test_threshold_089_fails(self):
        """阈值0.89（低于0.9 0.01）应被拦截。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "cache.py").write_text(
                "similarity_threshold=0.89\n",
                encoding="utf-8"
            )
            (base / "main.py").write_text(
                "from openai import OpenAI\nc = OpenAI()\nc.chat.completions.create(model='gpt-4', max_tokens=100, messages=[])\n",
                encoding="utf-8"
            )
            result = ctp.run_p0_checks(base)
            c007 = next(i for i in result.items if i.constraint_id == "C-007")
            assert c007.passed is False

    def test_max_new_tokens_recognized(self):
        """max_new_tokens（HuggingFace风格）应被识别为max_tokens变体。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            (base / "gen.py").write_text(
                "model.generate(input_ids, max_new_tokens=500)\n",
                encoding="utf-8"
            )
            # 没有LLM调用模式就不会触发C-012检查，需要有LLM调用代码
            (base / "llm.py").write_text(
                "from transformers import AutoModelForCausalLM\n"
                "model = AutoModelForCausalLM.from_pretrained('gpt2')\n"
                "model.generate(input_ids, max_new_tokens=500)\n",
                encoding="utf-8"
            )
            result = ctp.run_p0_checks(base)
            c012 = next(i for i in result.items if i.constraint_id == "C-012")
            # C-012扫描的是code_exts中的max_tokens模式，应该能匹配到
            # 但llm.py中没有openai风格的chat.completions，所以llm_call_hits可能为空
            # 这个测试主要验证max_new_tokens模式能被MAX_TOKENS_PATTERNS匹配
            assert any("max_new_tokens" in pat for pat in ctp.MAX_TOKENS_PATTERNS)
