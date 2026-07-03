import pytest

from mdi.parser import MDIParser
from mdi.generators import PytestGenerator


class TestPytestGenerator:

    def test_pytest_generate_compiles(self, sample_webapi_doc, tmp_path):
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) > 0
        for f in files:
            if f.suffix == ".py":
                content = f.read_text(encoding="utf-8")
                try:
                    compile(content, str(f), "exec")
                except SyntaxError as e:
                    pytest.fail(f"Python syntax error in generated test {f}: {e}")

    def test_pytest_contains_test_classes(self, sample_webapi_doc, tmp_path):
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        test_files = [f for f in files if f.name.startswith("test_") and f.suffix == ".py"]
        assert len(test_files) >= 1
        content = test_files[0].read_text(encoding="utf-8")
        assert "import pytest" in content
        assert "import requests" in content
        assert "class Test" in content
        assert "def test_" in content
        assert "api_client" in content
        assert "base_url" in content

    def test_pytest_generates_conftest(self, sample_webapi_doc, tmp_path):
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        conftest = [f for f in files if f.name == "conftest.py"]
        assert len(conftest) == 1
        content = conftest[0].read_text(encoding="utf-8")
        assert "@pytest.fixture" in content
        assert "def pytest_addoption" in content
        assert '"--base-url"' in content
        assert "API_BASE_URL" in content
        assert "api_client" in content
        assert "base_url" in content
        assert "import os" in content

    def test_pytest_conftest_supports_api_token(self, sample_webapi_doc, tmp_path):
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        conftest = [f for f in files if f.name == "conftest.py"]
        content = conftest[0].read_text(encoding="utf-8")
        assert '"--api-token"' in content
        assert "API_TOKEN" in content
        assert "Authorization" in content
        assert "Bearer" in content

    def test_pytest_conftest_not_overwritten(self, sample_webapi_doc, tmp_path):
        conftest_path = tmp_path / "conftest.py"
        conftest_path.write_text("# existing conftest", encoding="utf-8")
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert conftest_path.read_text(encoding="utf-8") == "# existing conftest"

    def test_pytest_success_test_asserts_status(self, sample_webapi_doc, tmp_path):
        gen = PytestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        test_files = [f for f in files if f.name.startswith("test_")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "assert response.status_code ==" in content

    def test_pytest_error_tests_for_error_codes(self, tmp_path):
        text = '''---
name: test-api
version: 1.0.0
description: Test
baseUrl: https://api.example.com
type: webapi
---

# Test

```{endpoint} POST /items
:summary: Create item
:param name: string - 名称
:response 201: Created
:error 400: VALIDATION_ERROR - 参数校验失败
:error 409: ALREADY_EXISTS - 资源已存在
```
'''
        doc = MDIParser(profile_type="webapi").parse_text(text)
        gen = PytestGenerator()
        files = gen.generate(doc, tmp_path)
        test_files = [f for f in files if f.name.startswith("test_")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "VALIDATION_ERROR" not in content or "400" in content
        assert "ALREADY_EXISTS" in content
        assert "response.status_code == 409" in content

    def test_pytest_uses_example_request_data(self, tmp_path):
        text = '''---
name: test-api
version: 1.0.0
description: Test
baseUrl: https://api.example.com
type: webapi
---

# Test

```{endpoint} POST /items
:summary: Create item
:param name: string - 名称
:response 201: Created
```

**请求示例：**

```json
{
  "name": "测试项目",
  "priority": "high"
}
```
'''
        doc = MDIParser(profile_type="webapi").parse_text(text)
        gen = PytestGenerator()
        files = gen.generate(doc, tmp_path)
        test_files = [f for f in files if f.name.startswith("test_")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "测试项目" in content

    def test_pytest_checklist_assertions_in_success_test(self, tmp_path):
        text = '''---
name: test-api
version: 1.0.0
description: Test
baseUrl: https://api.example.com
type: webapi
---

# Test

```{endpoint} GET /items/{id}
:summary: Get item
:param id: int - Item ID
:response 200: OK
```

- [ ] 验证状态码为200
- [ ] 响应包含字段`id`
'''
        doc = MDIParser(profile_type="webapi").parse_text(text)
        gen = PytestGenerator()
        files = gen.generate(doc, tmp_path)
        test_files = [f for f in files if f.name.startswith("test_")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "来自文档检查清单" in content
        assert "'id' in data" in content
        assert "response.status_code == 200" in content
