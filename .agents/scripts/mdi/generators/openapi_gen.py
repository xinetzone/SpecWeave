"""OpenAPI 3.0导出器。

生成标准OpenAPI 3.0规范JSON文件，适用于Web API场景。
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parents[2]
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from mdi.models import MDIDocument, Interface, Parameter, Response
from mdi.generators.base import BaseGenerator
from mdi.generators.utils import map_json_schema_type, make_interface_name, sanitize_identifier


class OpenAPIGenerator(BaseGenerator):
    """OpenAPI 3.0规范生成器。"""

    def _generate(self, doc: MDIDocument, output_dir: Path) -> list[Path]:
        spec = self._build_openapi_spec(doc)
        content = json.dumps(spec, ensure_ascii=False, indent=2)

        module_name = sanitize_identifier(
            doc.frontmatter.get("name", "openapi")
        ).replace("-", "_")
        file_path = output_dir / f"{module_name}_openapi.json"
        self._write_file(file_path, content)
        return [file_path]

    def _build_openapi_spec(self, doc: MDIDocument) -> dict[str, Any]:
        """构建OpenAPI 3.0规范结构。"""
        fm = doc.frontmatter

        info = {
            "title": fm.get("title", doc.title or "API Documentation"),
            "version": str(fm.get("version", "1.0.0")),
            "description": fm.get("description", doc.description or ""),
        }

        servers = []
        base_url = fm.get("baseUrl") or fm.get("baseurl")
        if base_url:
            servers.append({"url": base_url})
        else:
            servers.append({"url": "/"})

        paths: dict[str, Any] = {}
        schemas: dict[str, Any] = {}

        for iface in doc.interfaces:
            path_item = self._build_path_item(iface, schemas)
            path_key = iface.path or "/"
            method = (iface.method or "get").lower()
            if path_key not in paths:
                paths[path_key] = {}
            paths[path_key][method] = path_item

        spec: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": info,
            "servers": servers,
            "paths": paths,
        }

        if schemas:
            spec["components"] = {"schemas": schemas}

        return spec

    def _build_path_item(
        self, iface: Interface, schemas: dict[str, Any]
    ) -> dict[str, Any]:
        """构建单个path item。"""
        operation: dict[str, Any] = {
            "summary": iface.summary or iface.name,
            "description": iface.description or "",
            "operationId": sanitize_identifier(iface.name).replace("-", "_"),
        }

        if iface.tags:
            operation["tags"] = iface.tags

        parameters: list[dict[str, Any]] = []
        request_body: dict[str, Any] | None = None

        path_params = set(re.findall(r"\{(\w+)\}", iface.path or ""))
        method = (iface.method or "get").upper()
        methods_without_body = {"GET", "DELETE", "HEAD", "OPTIONS"}

        for param in iface.parameters:
            param_schema = self._param_to_schema(param)

            param_name = param.name
            if param_name in path_params:
                parameters.append({
                    "name": param_name,
                    "in": "path",
                    "required": True,
                    "description": param.description,
                    "schema": param_schema,
                })
            elif param.location in ("path", "query", "header", "cookie"):
                parameters.append({
                    "name": param_name,
                    "in": param.location,
                    "required": param.required,
                    "description": param.description,
                    "schema": param_schema,
                })
            elif method in methods_without_body and param.location == "body":
                parameters.append({
                    "name": param_name,
                    "in": "query",
                    "required": param.required,
                    "description": param.description,
                    "schema": param_schema,
                })
            else:
                if request_body is None:
                    request_body = {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "properties": {}}
                            }
                        },
                    }
                props = request_body["content"]["application/json"]["schema"]["properties"]
                props[param_name] = param_schema
                if param.required:
                    if "required" not in request_body["content"]["application/json"]["schema"]:
                        request_body["content"]["application/json"]["schema"]["required"] = []
                    request_body["content"]["application/json"]["schema"]["required"].append(param_name)

        if iface.request_body:
            body_param = iface.request_body
            body_schema = self._param_to_schema(body_param)
            schema_name = make_interface_name(f"{iface.name}Request")
            schemas[schema_name] = body_schema
            request_body = {
                "required": body_param.required,
                "description": body_param.description,
                "content": {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{schema_name}"}
                    }
                },
            }

        if parameters:
            operation["parameters"] = parameters
        if request_body and method not in methods_without_body:
            operation["requestBody"] = request_body

        responses: dict[str, Any] = {}
        for resp in iface.responses:
            status_key = str(resp.status_code)
            resp_obj: dict[str, Any] = {
                "description": resp.description or "",
            }
            if resp.schema:
                resp_obj["content"] = {
                    "application/json": {"schema": resp.schema}
                }
            responses[status_key] = resp_obj

        if not responses:
            responses["200"] = {"description": "Successful response"}

        operation["responses"] = responses
        return operation

    def _param_to_schema(self, param: Parameter) -> dict[str, Any]:
        """将Parameter转换为JSON Schema。"""
        schema = map_json_schema_type(param.type)
        if param.description:
            schema["description"] = param.description
        if param.default is not None:
            schema["default"] = self._parse_default(param.default, param.type)
        return schema

    def _parse_default(self, default_str: str, type_str: str | None) -> Any:
        """解析默认值字符串为对应类型。"""
        if default_str is None:
            return None
        type_lower = (type_str or "").lower()
        if type_lower in ("boolean", "bool"):
            return default_str.lower() in ("true", "yes", "1")
        if type_lower in ("integer", "int"):
            try:
                return int(default_str)
            except ValueError:
                return default_str
        if type_lower in ("number", "float"):
            try:
                return float(default_str)
            except ValueError:
                return default_str
        return default_str
