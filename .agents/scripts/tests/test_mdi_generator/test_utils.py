from mdi.generators.utils import (
    snake_to_pascal,
    snake_to_camel,
    map_python_type,
    map_typescript_type,
    map_json_schema_type,
    make_interface_name,
    sanitize_identifier,
)


class TestUtils:

    def test_snake_to_pascal(self):
        assert snake_to_pascal("user_id") == "UserId"
        assert snake_to_pascal("create_user") == "CreateUser"
        assert snake_to_pascal("hello_world_test") == "HelloWorldTest"
        assert snake_to_pascal("") == ""

    def test_snake_to_camel(self):
        assert snake_to_camel("user_id") == "userId"
        assert snake_to_camel("create_user") == "createUser"

    def test_map_python_type(self):
        assert map_python_type("string") == "str"
        assert map_python_type("integer") == "int"
        assert map_python_type("number") == "float"
        assert map_python_type("boolean") == "bool"
        assert map_python_type("array") == "list"
        assert map_python_type("object") == "dict"
        assert "Optional" in map_python_type("optional string")

    def test_map_typescript_type(self):
        assert map_typescript_type("string") == "string"
        assert map_typescript_type("integer") == "number"
        assert map_typescript_type("boolean") == "boolean"
        assert "undefined" in map_typescript_type("optional string")

    def test_map_json_schema_type(self):
        assert map_json_schema_type("string")["type"] == "string"
        assert map_json_schema_type("integer")["type"] == "integer"
        assert map_json_schema_type("boolean")["type"] == "boolean"
        assert map_json_schema_type("array")["type"] == "array"

    def test_sanitize_identifier(self):
        assert sanitize_identifier("user-id") == "user_id"
        assert sanitize_identifier("123abc").startswith("_")

    def test_make_interface_name(self):
        assert make_interface_name("get_users") == "GetUsers"
        assert make_interface_name("create-user") == "CreateUser"
