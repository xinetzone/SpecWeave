from __future__ import annotations

from typing import Any

from .constants import (
    _ERROR_COLUMN_MAP,
    _ERROR_TABLE_KEYWORDS,
    _PARAM_COLUMN_MAP,
    _PARAM_TABLE_KEYWORDS,
    _RESPONSE_COLUMN_MAP,
    _RESPONSE_TABLE_KEYWORDS,
    _match_column,
    ErrorCode,
    Parameter,
    Response,
)


class TableParserMixin:
    def _classify_and_parse_table(self, table_block: dict) -> dict[str, Any] | None:
        header = table_block.get("header", [])
        rows = table_block.get("rows", [])
        alignments = table_block.get("alignments", [])
        line = table_block.get("line", 0)

        if not header:
            self._warn("表格缺少表头", line)
            return None

        header_text = " ".join(header).lower()

        param_cols = self._try_match_columns(header, _PARAM_COLUMN_MAP, "name")
        response_cols = self._try_match_columns(header, _RESPONSE_COLUMN_MAP, "status_code")
        error_cols = self._try_match_columns(header, _ERROR_COLUMN_MAP, "code")

        table_type = "generic"
        parsed_items: list[Any] = []

        is_error_table = bool(error_cols and "message" in error_cols)

        if param_cols:
            table_type = "parameter"
            parsed_items = self._parse_parameter_table_with_cols(header, rows, line, param_cols)
        elif is_error_table:
            table_type = "error"
            parsed_items = self._parse_error_table_with_cols(header, rows, line, error_cols)
        elif response_cols:
            table_type = "response"
            parsed_items = self._parse_response_table_with_cols(header, rows, line, response_cols)
        elif any(kw in header_text for kw in _PARAM_TABLE_KEYWORDS):
            table_type = "parameter"
            parsed_items = self._parse_parameter_table(header, rows, line)
        elif any(kw in header_text for kw in _ERROR_TABLE_KEYWORDS):
            table_type = "error"
            parsed_items = self._parse_error_table(header, rows, line)
        elif any(kw in header_text for kw in _RESPONSE_TABLE_KEYWORDS):
            table_type = "response"
            parsed_items = self._parse_response_table(header, rows, line)

        return {
            "type": table_type,
            "header": header,
            "rows": rows,
            "alignments": alignments,
            "parsed_items": parsed_items,
            "line": line,
        }

    def _try_match_columns(
        self, header: list[str], column_map: dict[str, set[str]], required_key: str
    ) -> dict[str, int] | None:
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            col = _match_column(h, column_map)
            if col:
                col_map[col] = i
        if required_key in col_map:
            return col_map
        return None

    def _parse_parameter_table(
        self, header: list[str], rows: list[list[str]], line: int
    ) -> list[Parameter]:
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            col = _match_column(h, _PARAM_COLUMN_MAP)
            if col:
                col_map[col] = i
        if "name" not in col_map:
            self._warn(f"参数表缺少name列，表头: {header}", line)
            return []
        return self._parse_parameter_table_with_cols(header, rows, line, col_map)

    def _parse_parameter_table_with_cols(
        self, header: list[str], rows: list[list[str]], line: int, col_map: dict[str, int]
    ) -> list[Parameter]:
        params: list[Parameter] = []
        for row_idx, row in enumerate(rows):
            if len(row) < len(header):
                self._warn(
                    f"参数表第{row_idx + 1}行列数不匹配（期望{len(header)}列，实际{len(row)}列），跳过",
                    line,
                )
                continue
            if len(row) > len(header):
                row = row[:len(header)]
            name = row[col_map["name"]].strip()
            if not name:
                continue
            ptype = row[col_map["type"]].strip() if "type" in col_map else "string"
            required = False
            if "required" in col_map:
                req_val = row[col_map["required"]].strip().lower()
                required = req_val in ("yes", "true", "是", "必填", "required", "y")
            desc = row[col_map["description"]].strip() if "description" in col_map else ""
            default = row[col_map["default"]].strip() if "default" in col_map else None
            if default == "":
                default = None
            location = row[col_map["location"]].strip() if "location" in col_map else "body"
            params.append(Parameter(
                name=name,
                type=ptype,
                required=required,
                description=desc,
                default=default,
                location=location,
            ))
        return params

    def _parse_response_table(
        self, header: list[str], rows: list[list[str]], line: int
    ) -> list[Response]:
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            col = _match_column(h, _RESPONSE_COLUMN_MAP)
            if col:
                col_map[col] = i
        if "status_code" not in col_map:
            self._warn(f"响应表缺少status_code列，表头: {header}", line)
            return []
        return self._parse_response_table_with_cols(header, rows, line, col_map)

    def _parse_response_table_with_cols(
        self, header: list[str], rows: list[list[str]], line: int, col_map: dict[str, int]
    ) -> list[Response]:
        responses: list[Response] = []
        for row_idx, row in enumerate(rows):
            if len(row) < len(header):
                self._warn(f"响应表第{row_idx + 1}行列数不匹配，跳过", line)
                continue
            if len(row) > len(header):
                row = row[:len(header)]
            code_val = row[col_map["status_code"]].strip()
            desc = row[col_map["description"]].strip() if "description" in col_map else ""
            try:
                status_code: str | int = int(code_val) if code_val.isdigit() else code_val
            except (ValueError, TypeError):
                status_code = code_val
            responses.append(Response(status_code=status_code, description=desc))
        return responses

    def _parse_error_table(
        self, header: list[str], rows: list[list[str]], line: int
    ) -> list[ErrorCode]:
        col_map: dict[str, int] = {}
        for i, h in enumerate(header):
            col = _match_column(h, _ERROR_COLUMN_MAP)
            if col:
                col_map[col] = i
        if "code" not in col_map:
            self._warn(f"错误码表缺少code列，表头: {header}", line)
            return []
        return self._parse_error_table_with_cols(header, rows, line, col_map)

    def _parse_error_table_with_cols(
        self, header: list[str], rows: list[list[str]], line: int, col_map: dict[str, int]
    ) -> list[ErrorCode]:
        errors: list[ErrorCode] = []
        for row_idx, row in enumerate(rows):
            if len(row) < len(header):
                self._warn(f"错误码表第{row_idx + 1}行列数不匹配，跳过", line)
                continue
            if len(row) > len(header):
                row = row[:len(header)]
            code_val = row[col_map["code"]].strip()
            message = row[col_map["message"]].strip() if "message" in col_map else ""
            desc = row[col_map["description"]].strip() if "description" in col_map else ""
            try:
                code: str | int = int(code_val) if code_val.isdigit() else code_val
            except (ValueError, TypeError):
                code = code_val
            errors.append(ErrorCode(code=code, message=message, description=desc))
        return errors
