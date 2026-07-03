class TestTableParsing:

    def test_parameter_table(self, parser):
        text = "# API Doc\n\n## Parameters\n\n| Name | Type | Required | Description |\n|------|------|----------|-------------|\n| user_id | int | Yes | User ID |\n| name | string | No | User name |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        param_tables = [t for t in h2.tables if t["type"] == "parameter"]
        assert len(param_tables) == 1
        params = param_tables[0]["parsed_items"]
        assert len(params) == 2
        assert params[0].name == "user_id"
        assert params[0].type == "int"
        assert params[0].required is True
        assert params[1].name == "name"
        assert params[1].required is False

    def test_parameter_table_chinese_headers(self, parser):
        text = "# API\n\n## 参数\n\n| 参数名 | 类型 | 必填 | 说明 | 默认值 |\n|--------|------|------|------|--------|\n| page | int | 否 | 页码 | 1 |\n| size | int | 否 | 每页数量 | 20 |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        param_tables = [t for t in h2.tables if t["type"] == "parameter"]
        assert len(param_tables) == 1
        params = param_tables[0]["parsed_items"]
        assert len(params) == 2
        assert params[0].name == "page"
        assert params[0].default == "1"
        assert params[1].name == "size"
        assert params[1].default == "20"

    def test_response_table(self, parser):
        text = "# API\n\n## Responses\n\n| Code | Description |\n|------|-------------|\n| 200 | Success |\n| 400 | Bad Request |\n| 404 | Not Found |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        resp_tables = [t for t in h2.tables if t["type"] == "response"]
        assert len(resp_tables) == 1
        responses = resp_tables[0]["parsed_items"]
        assert len(responses) == 3
        assert responses[0].status_code == 200
        assert responses[0].description == "Success"
        assert responses[1].status_code == 400

    def test_error_code_table(self, parser):
        text = "# API\n\n## Error Codes\n\n| Error Code | Message | Description |\n|------------|---------|-------------|\n| 10001 | Invalid token | Token expired |\n| 10002 | Permission denied | No access |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        err_tables = [t for t in h2.tables if t["type"] == "error"]
        assert len(err_tables) == 1
        errors = err_tables[0]["parsed_items"]
        assert len(errors) == 2
        assert errors[0].code == 10001
        assert errors[0].message == "Invalid token"

    def test_generic_table(self, parser):
        text = "# Doc\n\n## Comparison\n\n| Feature | Plan A | Plan B |\n|---------|--------|--------|\n| Speed | Fast | Slow |\n| Cost | High | Low |\n"
        doc = parser.parse_text(text)
        h1 = doc.sections[0]
        h2 = h1.subsections[0]
        generic_tables = [t for t in h2.tables if t["type"] == "generic"]
        assert len(generic_tables) == 1
        assert generic_tables[0]["header"] == ["Feature", "Plan A", "Plan B"]
        assert len(generic_tables[0]["rows"]) == 2

    def test_malformed_markdown_no_crash(self, parser):
        text = "# API\n\n## Bad Table\n\n| Name | Type | Description |\n|------|------|-----|\n| id | int |\n| name | string | The name |\n\nNormal text after bad table.\n"
        doc = parser.parse_text(text)
        assert doc is not None
        assert doc.title == "API"
        assert len(doc.warnings) >= 0
