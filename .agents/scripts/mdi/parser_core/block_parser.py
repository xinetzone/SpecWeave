from __future__ import annotations

from typing import Any

from .constants import (
    _ADMONITION_TYPES,
    _CODE_PURPOSE_KEYWORDS,
    _DIRECTIVE_RE,
    _ERROR_COLUMN_MAP,
    _ERROR_TABLE_KEYWORDS,
    _MERMAID_EDGE_RE,
    _MERMAID_FLOWCHART_RE,
    _MERMAID_NODE_RE,
    _PARAM_COLUMN_MAP,
    _PARAM_TABLE_KEYWORDS,
    _RESPONSE_COLUMN_MAP,
    _RESPONSE_TABLE_KEYWORDS,
    _extract_inline_text,
    _match_column,
    CheckItem,
    CodeBlock,
    DecisionNode,
    ErrorCode,
    Parameter,
    Response,
)


class BlockParserMixin:
    def _tokens_to_blocks(self, tokens: list, body: str) -> list[dict]:
        blocks: list[dict] = []
        i = 0
        while i < len(tokens):
            t = tokens[i]
            line = t.map[0] + 1 if t.map else 0

            if t.type == "front_matter":
                i += 1
                continue

            if t.type == "heading_open":
                level = int(t.tag[1])
                j = i + 1
                heading_text = ""
                while j < len(tokens) and tokens[j].type != "heading_close":
                    if tokens[j].type == "inline":
                        heading_text = _extract_inline_text(tokens[j].children or [], 0, len(tokens[j].children or []))
                    j += 1
                blocks.append({"type": "heading", "level": level, "text": heading_text, "line": line})
                i = j + 1
                continue

            if t.type == "paragraph_open":
                j = i + 1
                ptext = ""
                while j < len(tokens) and tokens[j].type != "paragraph_close":
                    if tokens[j].type == "inline":
                        ptext = _extract_inline_text(tokens[j].children or [], 0, len(tokens[j].children or []))
                    j += 1
                blocks.append({"type": "paragraph", "text": ptext, "line": line})
                i = j + 1
                continue

            if t.type == "fence":
                info = t.info or ""
                content = t.content.rstrip("\n") if t.content else ""
                lang = ""
                meta = ""
                is_directive = False
                directive_name = ""
                directive_args = ""
                directive_options: dict[str, str] = {}
                directive_body = ""

                dm = _DIRECTIVE_RE.match(info.strip())
                if dm:
                    is_directive = True
                    directive_name = dm.group(1).lower()
                    directive_args = dm.group(2).strip()
                    directive_options_raw, directive_body = self._parse_directive_content(content)
                    directive_options: dict[str, str] = {}
                    directive_options_optional: dict[str, bool] = {}
                    for k, (v, is_opt) in directive_options_raw.items():
                        directive_options[k] = v
                        directive_options_optional[k] = is_opt
                    if directive_name in _ADMONITION_TYPES:
                        blocks.append({
                            "type": "admonition",
                            "admonition_type": directive_name,
                            "title": directive_args,
                            "text": directive_body,
                            "options": directive_options,
                            "line": line,
                        })
                        i += 1
                        continue
                    blocks.append({
                        "type": "directive",
                        "directive_name": directive_name,
                        "args": directive_args,
                        "options": directive_options,
                        "options_optional": directive_options_optional,
                        "body": directive_body,
                        "content": content,
                        "line": line,
                    })
                    i += 1
                    continue
                else:
                    if info:
                        parts = info.strip().split(None, 1)
                        lang = parts[0] if parts else ""
                        meta = parts[1] if len(parts) > 1 else ""
                    purpose = self._detect_code_purpose(info, meta)
                    blocks.append({
                        "type": "block_code",
                        "language": lang,
                        "meta": meta,
                        "content": content,
                        "line": line,
                        "purpose": purpose,
                    })
                    i += 1
                    continue

            if t.type == "bullet_list_open" or t.type == "ordered_list_open":
                ordered = t.type == "ordered_list_open"
                start = t.attrs.get("start", 1) if t.attrs else 1
                items, j = self._parse_list_tokens(tokens, i + 1)
                blocks.append({
                    "type": "list",
                    "ordered": ordered,
                    "start": start,
                    "items": items,
                    "line": line,
                })
                i = j + 1
                continue

            if t.type == "blockquote_open":
                j = i + 1
                depth = 1
                quote_parts: list[str] = []
                while j < len(tokens) and depth > 0:
                    if tokens[j].type == "blockquote_open":
                        depth += 1
                    elif tokens[j].type == "blockquote_close":
                        depth -= 1
                        if depth == 0:
                            break
                    elif tokens[j].type == "inline":
                        quote_parts.append(_extract_inline_text(tokens[j].children or [], 0, len(tokens[j].children or [])))
                    j += 1
                quote_text = "\n".join(quote_parts)
                blocks.append({"type": "block_quote", "text": quote_text, "line": line})
                i = j + 1
                continue

            if t.type == "table_open":
                table_data, j = self._parse_table_tokens(tokens, i)
                table_data["line"] = line
                blocks.append(table_data)
                i = j + 1
                continue

            i += 1

        return blocks

    def _parse_list_tokens(self, tokens: list, start: int) -> tuple[list[dict], int]:
        items: list[dict] = []
        i = start
        while i < len(tokens):
            t = tokens[i]
            if t.type in ("bullet_list_close", "ordered_list_close"):
                return items, i
            if t.type == "list_item_open":
                checked: bool | None = None
                is_task = False
                item_text_parts: list[str] = []
                nested_lists: list[dict] = []
                j = i + 1
                while j < len(tokens) and tokens[j].type != "list_item_close":
                    ct = tokens[j]
                    if ct.type == "paragraph_open":
                        k = j + 1
                        while k < len(tokens) and tokens[k].type != "paragraph_close":
                            if tokens[k].type == "inline":
                                children = tokens[k].children or []
                                task_checked, item_text = self._extract_task_item_from_children(children)
                                if task_checked is not None:
                                    is_task = True
                                    checked = task_checked
                                if item_text:
                                    item_text_parts.append(item_text)
                            k += 1
                        j = k
                    elif ct.type in ("bullet_list_open", "ordered_list_open"):
                        nested_ordered = ct.type == "ordered_list_open"
                        nested_items, nj = self._parse_list_tokens(tokens, j + 1)
                        nested_lists.append({
                            "ordered": nested_ordered,
                            "items": nested_items,
                        })
                        j = nj
                    elif ct.type == "inline":
                        children = ct.children or []
                        task_checked, item_text = self._extract_task_item_from_children(children)
                        if task_checked is not None:
                            is_task = True
                            checked = task_checked
                        if item_text:
                            item_text_parts.append(item_text)
                    j += 1
                text = " ".join(item_text_parts).strip()
                if not is_task:
                    checkbox_info = self._extract_checkbox(text)
                    if checkbox_info:
                        is_task = True
                        checked = checkbox_info[0]
                        text = checkbox_info[1]
                items.append({
                    "text": text,
                    "checked": checked if is_task else None,
                    "is_task": is_task,
                    "nested": nested_lists,
                })
                i = j + 1
            else:
                i += 1
        return items, i

    def _extract_task_item_from_children(self, children: list) -> tuple[bool | None, str]:
        has_checkbox = False
        checked = False
        text_parts: list[str] = []
        for child in children:
            if child.type == "html_inline" and "task-list-item-checkbox" in (child.content or ""):
                has_checkbox = True
                if "checked" in (child.content or "").lower():
                    checked = True
            elif child.type == "text":
                txt = child.content
                if has_checkbox and txt.startswith(" "):
                    txt = txt[1:]
                text_parts.append(txt)
            elif child.type == "softbreak" or child.type == "hardbreak":
                text_parts.append("\n")
            elif child.type == "code_inline":
                text_parts.append(f"`{child.content}`")
            elif child.type == "strong_open" or child.type == "strong_close":
                text_parts.append("**")
            elif child.type == "em_open" or child.type == "em_close":
                text_parts.append("*")
        text = "".join(text_parts).strip()
        if has_checkbox:
            return checked, text
        return None, text

    def _extract_checkbox(self, text: str) -> tuple[bool, str] | None:
        for prefix in ("[x] ", "[X] ", "[ ] "):
            if text.startswith(prefix):
                checked = prefix in ("[x] ", "[X] ")
                return checked, text[len(prefix):]
        return None

    def _parse_table_tokens(self, tokens: list, start: int) -> tuple[dict, int]:
        header: list[str] = []
        alignments: list[str | None] = []
        rows: list[list[str]] = []
        i = start + 1
        in_thead = False
        in_tbody = False

        while i < len(tokens):
            t = tokens[i]
            if t.type == "table_close":
                break
            if t.type == "thead_open":
                in_thead = True
            elif t.type == "thead_close":
                in_thead = False
            elif t.type == "tbody_open":
                in_tbody = True
            elif t.type == "tbody_close":
                in_tbody = False
            elif t.type == "tr_open":
                cells: list[str] = []
                j = i + 1
                is_header_row = in_thead
                while j < len(tokens) and tokens[j].type != "tr_close":
                    ct = tokens[j]
                    if ct.type in ("th_open", "td_open"):
                        align = None
                        if ct.attrs:
                            style = ct.attrs.get("style", "")
                            if "center" in style:
                                align = "center"
                            elif "right" in style:
                                align = "right"
                            elif "left" in style:
                                align = "left"
                        cell_text = ""
                        k = j + 1
                        while k < len(tokens) and tokens[k].type not in ("th_close", "td_close"):
                            if tokens[k].type == "inline":
                                cell_text = _extract_inline_text(tokens[k].children or [], 0, len(tokens[k].children or []))
                            k += 1
                        cells.append(cell_text.strip())
                        if is_header_row:
                            alignments.append(align)
                        j = k
                    j += 1
                if is_header_row:
                    header = cells
                else:
                    rows.append(cells)
                i = j
            i += 1

        return {
            "type": "table",
            "header": header,
            "alignments": alignments,
            "rows": rows,
        }, i

    def _parse_directive_content(self, content: str) -> tuple[dict[str, tuple[str, bool]], str]:
        options: dict[str, tuple[str, bool]] = {}
        lines = content.split("\n")
        body_start = 0
        for idx, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                body_start = idx + 1
                break
            if not stripped.startswith(":"):
                body_start = idx
                break
            colon_pos = line.find(":", 1)
            if colon_pos == -1:
                body_start = idx
                break
            raw_key = line[1:colon_pos].strip()
            val = line[colon_pos + 1:].strip()
            is_optional = False
            if raw_key.endswith("?"):
                is_optional = True
                raw_key = raw_key[:-1].strip()
            options[raw_key] = (val, is_optional)
            body_start = idx + 1
        else:
            body_start = len(lines)

        while body_start < len(lines) and not lines[body_start].strip():
            body_start += 1

        body = "\n".join(lines[body_start:]).strip()
        return options, body

    def _detect_code_purpose(self, info: str, meta: str) -> str:
        combined = (info + " " + meta).lower()
        for keyword in _CODE_PURPOSE_KEYWORDS:
            if keyword in combined:
                return keyword
        return ""

    def _infer_code_purpose(self, lang: str, meta: str, content: str) -> str:
        meta_lower = meta.lower()
        lang_lower = (lang or "").lower()
        if "status=" in meta_lower or "status_code=" in meta_lower:
            return "example"
        if lang_lower in ("json",) and content.strip().startswith(("{", "[")):
            return "example"
        if lang_lower in ("python", "py"):
            return "test"
        if lang_lower in ("bash", "sh", "shell", "curl"):
            return "example"
        return ""

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

    def _parse_mermaid_flowchart(self, content: str, pending_lists: list[Any]) -> None:
        m = _MERMAID_FLOWCHART_RE.search(content)
        if not m:
            return
        nodes: dict[str, DecisionNode] = {}
        edges: list[tuple[str, str, str]] = []

        def _first_nonempty(*groups: str | None) -> str:
            for g in groups:
                if g is not None:
                    return g.strip()
            return ""

        def _ensure_node(nid: str, label: str = "") -> None:
            if nid not in nodes:
                nodes[nid] = DecisionNode(id=nid, label=label or nid, edges=[])
            elif label and (not nodes[nid].label or nodes[nid].label == nid):
                nodes[nid].label = label

        for line in content.split("\n"):
            line = line.strip()
            if not line or line.startswith("flowchart"):
                continue
            edge_m = _MERMAID_EDGE_RE.match(line)
            if edge_m:
                src = edge_m.group(1)
                src_label = _first_nonempty(edge_m.group(2), edge_m.group(3), edge_m.group(4), edge_m.group(5), edge_m.group(6))
                label = (edge_m.group(8) or "").strip()
                dst = edge_m.group(9)
                dst_label = _first_nonempty(edge_m.group(10), edge_m.group(11), edge_m.group(12), edge_m.group(13), edge_m.group(14))
                _ensure_node(src, src_label)
                _ensure_node(dst, dst_label)
                edges.append((src, dst, label))
                continue
            node_m = _MERMAID_NODE_RE.match(line)
            if node_m:
                nid = node_m.group(1)
                label = node_m.group(2).strip()
                _ensure_node(nid, label)

        for src, dst, label in edges:
            if src in nodes:
                nodes[src].edges.append((dst, label))
            if dst not in nodes:
                _ensure_node(dst)

        if nodes:
            pending_lists.append({
                "type": "mermaid_flowchart",
                "nodes": list(nodes.values()),
            })
