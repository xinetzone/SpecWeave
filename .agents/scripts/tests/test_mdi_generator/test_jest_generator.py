from mdi.parser import MDIParser
from mdi.generators import JestGenerator


class TestJestGenerator:

    def test_jest_generates_files(self, sample_webapi_doc, tmp_path):
        gen = JestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        assert len(files) >= 1
        test_files = [f for f in files if f.suffix == ".test.js" or f.name.endswith(".test.js")]
        assert len(test_files) >= 1

    def test_jest_contains_describe_and_test(self, sample_webapi_doc, tmp_path):
        gen = JestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        test_files = [f for f in files if f.name.endswith(".test.js")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "const axios = require('axios')" in content
        assert "describe(" in content
        assert "test(" in content
        assert "apiClient" in content
        assert "expect(response.status)" in content

    def test_jest_generates_jest_config(self, sample_webapi_doc, tmp_path):
        gen = JestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        config = [f for f in files if f.name == "jest.config.js"]
        assert len(config) == 1
        content = config[0].read_text(encoding="utf-8")
        assert "testEnvironment" in content
        assert "testMatch" in content

    def test_jest_config_not_overwritten(self, sample_webapi_doc, tmp_path):
        config_path = tmp_path / "jest.config.js"
        config_path.write_text("// existing config", encoding="utf-8")
        gen = JestGenerator()
        gen.generate(sample_webapi_doc, tmp_path)
        assert config_path.read_text(encoding="utf-8") == "// existing config"

    def test_jest_supports_env_vars(self, sample_webapi_doc, tmp_path):
        gen = JestGenerator()
        files = gen.generate(sample_webapi_doc, tmp_path)
        test_files = [f for f in files if f.name.endswith(".test.js")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "process.env.API_BASE_URL" in content
        assert "process.env.API_TOKEN" in content

    def test_jest_success_tests_for_interfaces(self, tmp_path):
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
        gen = JestGenerator()
        files = gen.generate(doc, tmp_path)
        test_files = [f for f in files if f.name.endswith(".test.js")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "post_items_success" in content
        assert "post_items_missing_name" in content
        assert "ALREADY_EXISTS" in content
        assert "response.status).toBe(409)" in content

    def test_jest_uses_semantic_mock_data(self, tmp_path):
        text = '''---
name: test-api
version: 1.0.0
description: Test
baseUrl: https://api.example.com
type: webapi
---

# Test

```{endpoint} POST /users
:summary: Create user
:param email: string - 邮箱
:param name: string - 姓名
:param age: integer - 年龄
:response 201: Created
```
'''
        doc = MDIParser(profile_type="webapi").parse_text(text)
        gen = JestGenerator()
        files = gen.generate(doc, tmp_path)
        test_files = [f for f in files if f.name.endswith(".test.js")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "@example.com" in content
        assert "'Test Name" in content

    def test_jest_uses_example_response_for_assertions(self, tmp_path):
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

**响应示例：**

```json status=200
{
  "id": 1,
  "name": "示例项目"
}
```
'''
        doc = MDIParser(profile_type="webapi").parse_text(text)
        gen = JestGenerator()
        files = gen.generate(doc, tmp_path)
        test_files = [f for f in files if f.name.endswith(".test.js")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "response.data" in content
        assert "toBeDefined()" in content
        assert "'id'" in content
        assert "示例项目" in content

    def test_jest_checklist_assertions_in_success_test(self, tmp_path):
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
        gen = JestGenerator()
        files = gen.generate(doc, tmp_path)
        test_files = [f for f in files if f.name.endswith(".test.js")]
        content = test_files[0].read_text(encoding="utf-8")
        assert "来自文档检查清单" in content or "检查清单" in content
        assert "response.status).toBe(200)" in content
        assert "toHaveProperty" in content
