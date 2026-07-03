from __future__ import annotations

import re
from typing import Any

from .constants import (
    _HTTP_METHODS,
    _METHOD_PATH_RE,
    CheckItem,
    CodeBlock,
    ErrorCode,
    Interface,
    MDIDocument,
    Parameter,
    Response,
    Section,
)


class DirectiveParserMixin:
    def _detect_webapi(self, doc: MDIDocument) -> bool:
        fm_type = doc.frontmatter.get("type", "")
        if isinstance(fm_type, str) and fm_type.lower() == "webapi":
            return True
        has_base_url = "baseurl" in doc.frontmatter or "baseUrl" in doc.frontmatter
        if has_base_url:
            return True
        return False

    def _extract_interfaces(self, doc: MDIDocument) -> None:
        def _walk(sections: list[Section]) -> None:
            for section in sections:
                self._extract_interfaces_from_section(section, doc)
                _walk(section.subsections)
        _walk(doc.sections)

    def _extract_interfaces_from_section(self, section: Section, doc: MDIDocument) -> None:
        if section.level != 3:
            return
        method = ""
        path = ""
        name = section.title
        m = _METHOD_PATH_RE.search(section.title)
        if m:
            method = m.group(1)
            path = m.group(2)
            name = section.title.replace(m.group(0), "").strip() or path
        else:
            m2 = _METHOD_PATH_RE.search(section.content)
            if m2:
                method = m2.group(1)
                path = m2.group(2)
        if not method or not path:
            return
        parameters: list[Parameter] = []
        responses: list[Response] = []
        errors: list[ErrorCode] = []
        examples: list[CodeBlock] = []
        for table in section.tables:
            if table["type"] == "parameter":
                parameters.extend(table.get("parsed_items", []))
            elif table["type"] == "response":
                responses.extend(table.get("parsed_items", []))
            elif table["type"] == "error":
                errors.extend(table.get("parsed_items", []))
        for cb in section.code_blocks:
            if cb.purpose in ("example", "mock", "request", "response"):
                examples.append(cb)
        self._infer_param_locations(parameters, path, method)
        iface = Interface(
            name=name,
            method=method,
            path=path,
            description=section.content[:200] if section.content else "",
            parameters=parameters,
            responses=responses,
            errors=errors,
            examples=examples,
        )
        doc.interfaces.append(iface)

    def _extract_interfaces_from_directives(self, blocks: list[dict], doc: MDIDocument) -> None:
        for idx, block in enumerate(blocks):
            if block.get("type") != "directive":
                continue
            dname = block.get("directive_name", "")
            if dname not in ("endpoint", "command"):
                continue
            is_command = (dname == "command")
            args = block.get("args", "")
            options = block.get("options", {})
            options_optional = block.get("options_optional", {})
            body = block.get("body", "")
            line = block.get("line", 0)

            parts = args.split(None, 1)
            if is_command:
                method = parts[0].lower() if parts else ""
            else:
                method = parts[0].upper() if parts else ""
            path = parts[1] if len(parts) > 1 else ""
            if not method:
                kind = "command" if is_command else "endpoint"
                self._warn(f"{kind} directive缺少名称: {args}", line)
                continue
            if not path:
                if is_command:
                    path = ""
                else:
                    self._warn(f"endpoint directive缺少路径/命令名: {args}", line)
                    continue

            summary = options.get("summary", "")
            description = body
            tags_str = options.get("tags", "")
            tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []

            parameters: list[Parameter] = []
            responses: list[Response] = []
            errors: list[ErrorCode] = []
            examples: list[CodeBlock] = []
            check_items: list[CheckItem] = []

            for opt_key, opt_val in options.items():
                if opt_key in ("summary", "tags", "deprecated", "name"):
                    continue
                is_optional = options_optional.get(opt_key, False)
                if opt_key.startswith("param"):
                    param = self._parse_directive_param(opt_key, opt_val, is_optional, line)
                    if param:
                        parameters.append(param)
                elif opt_key.startswith("query"):
                    param_name = opt_key[5:].strip() if len(opt_key) > 5 else ""
                    if param_name:
                        param = self._parse_directive_param(f"param {param_name}", opt_val, is_optional, line)
                        if param:
                            param.location = "query"
                            parameters.append(param)
                elif opt_key.startswith("path"):
                    param_name = opt_key[4:].strip() if len(opt_key) > 4 else ""
                    if param_name:
                        param = self._parse_directive_param(f"param {param_name}", opt_val, is_optional, line)
                        if param:
                            param.location = "path"
                            param.required = True
                            parameters.append(param)
                elif opt_key.startswith("body"):
                    param_name = opt_key[4:].strip() if len(opt_key) > 4 else ""
                    if param_name:
                        param = self._parse_directive_param(f"param {param_name}", opt_val, is_optional, line)
                        if param:
                            param.location = "body"
                            parameters.append(param)
                    elif opt_key == "body":
                        pass
                elif opt_key.startswith("header"):
                    param_name = opt_key[6:].strip() if len(opt_key) > 6 else ""
                    if param_name:
                        param = self._parse_directive_param(f"param {param_name}", opt_val, is_optional, line)
                        if param:
                            param.location = "header"
                            parameters.append(param)
                elif opt_key.startswith("arg"):
                    param_name = opt_key[3:].strip() if len(opt_key) > 3 else ""
                    if param_name:
                        param = self._parse_directive_param(f"param {param_name}", opt_val, False, line)
                        if param:
                            param.location = "arg"
                            param.required = True
                            parameters.append(param)
                elif opt_key.startswith("flag"):
                    flag_parts = opt_key[4:].strip() if len(opt_key) > 4 else ""
                    flag_names = [a.strip() for a in flag_parts.split(",") if a.strip()]
                    if flag_names:
                        primary_name = flag_names[0].lstrip("-").replace("-", "_")
                        desc = opt_val.split(" - ", 1)[-1].strip() if " - " in opt_val else opt_val.strip()
                        default_match = re.search(r'\(default:\s*(true|false)\)', desc, re.IGNORECASE)
                        flag_default = "true" if default_match and default_match.group(1).lower() == "true" else "false"
                        param = Parameter(
                            name=primary_name,
                            type="boolean",
                            required=False,
                            description=desc,
                            default=flag_default,
                        )
                        param.location = "flag"
                        if len(flag_names) > 1:
                            param.extra_data = {"aliases": flag_names}
                        else:
                            param.extra_data = {"aliases": flag_names}
                        parameters.append(param)
                elif opt_key.startswith("option"):
                    opt_parts = opt_key[6:].strip() if len(opt_key) > 6 else ""
                    opt_names = [a.strip() for a in opt_parts.split(",") if a.strip()]
                    if opt_names:
                        primary_name = opt_names[0].lstrip("-").replace("-", "_")
                        param = self._parse_directive_param(f"param {primary_name}", opt_val, is_optional, line)
                        if param:
                            param.location = "option"
                            param.extra_data = {"aliases": opt_names}
                            parameters.append(param)
                elif opt_key.startswith("response"):
                    resp = self._parse_directive_response(opt_key, opt_val, line)
                    if resp:
                        responses.append(resp)
                elif opt_key.startswith("error"):
                    err = self._parse_directive_error(opt_key, opt_val, line)
                    if err:
                        errors.append(err)
                elif opt_key.startswith("exit"):
                    exit_code_str = opt_key[4:].strip()
                    try:
                        exit_code = int(exit_code_str) if exit_code_str else 0
                    except ValueError:
                        exit_code = 1
                    exit_desc = opt_val.strip()
                    if exit_desc:
                        errors.append(ErrorCode(
                            code=exit_code,
                            message=exit_desc.split(" - ", 1)[0].strip() if " - " in exit_desc else exit_desc[:50],
                            description=exit_desc,
                        ))

            existing_error_codes = {int(e.code) for e in errors if isinstance(e.code, int) or (isinstance(e.code, str) and e.code.isdigit())}
            for resp in responses:
                code_int = None
                try:
                    code_int = int(resp.status_code)
                except (ValueError, TypeError):
                    continue
                if code_int >= 400 and code_int not in existing_error_codes:
                    errors.append(ErrorCode(
                        code=code_int,
                        message="",
                        description=resp.description or f"HTTP {code_int}",
                    ))
                    existing_error_codes.add(code_int)

            context_hint = ""
            parent_heading_level = 0
            for prev in reversed(blocks[:idx]):
                if prev.get("type") == "heading":
                    parent_heading_level = prev.get("level", 3)
                    break
            for nxt in blocks[idx + 1:]:
                if nxt.get("type") == "directive":
                    break
                if nxt.get("type") == "heading":
                    lvl = nxt.get("level", 3)
                    if parent_heading_level > 0 and lvl <= parent_heading_level:
                        break
                    heading_text = nxt.get("text", "").lower()
                    if "example" in heading_text or "示例" in heading_text or "样例" in heading_text:
                        context_hint = "example"
                    elif "request" in heading_text or "请求" in heading_text:
                        context_hint = "request"
                    elif "response" in heading_text or "响应" in heading_text:
                        context_hint = "response"
                    continue
                if nxt.get("type") == "paragraph":
                    ptext = nxt.get("text", "")
                    if "请求" in ptext or "request" in ptext.lower():
                        context_hint = "request"
                    elif "响应" in ptext or "response" in ptext.lower():
                        context_hint = "response"
                    elif "示例" in ptext or "example" in ptext.lower():
                        context_hint = "example"
                    continue
                if nxt.get("type") == "list" and nxt.get("ordered") is False:
                    for item in nxt.get("items", []):
                        if item.get("is_task"):
                            check_items.append(CheckItem(
                                text=item.get("text", ""),
                                checked=bool(item.get("checked", False)),
                                line=nxt.get("line", 0),
                            ))
                    continue
                if nxt.get("type") == "block_code":
                    lang = nxt.get("language", "")
                    meta = nxt.get("meta", "")
                    content = nxt.get("content", "")
                    purpose = nxt.get("purpose", "") or self._detect_code_purpose(lang, meta)
                    if not purpose:
                        purpose = self._infer_code_purpose(lang, meta, content)
                    if not purpose and context_hint:
                        purpose = context_hint
                    if purpose == "example" and context_hint in ("request", "response"):
                        purpose = context_hint
                    if purpose in ("example", "mock", "request", "response", "test", "schema"):
                        cb = CodeBlock(language=lang, meta=meta, content=content, purpose=purpose)
                        examples.append(cb)

            if is_command:
                name = options.get("name", "") or method
            else:
                name = options.get("name", "") or path
            self._infer_param_locations(parameters, path, method)
            iface = Interface(
                name=name,
                method=method,
                path=path,
                summary=summary,
                description=description,
                parameters=parameters,
                responses=responses,
                errors=errors,
                examples=examples,
                check_items=check_items,
                tags=tags,
            )
            doc.interfaces.append(iface)

    def _parse_directive_param(self, key: str, val: str, is_optional: bool, line: int) -> Parameter | None:
        name = key[5:].strip() if key.startswith("param") else key.strip()
        if not name:
            return None
        required = not is_optional
        ptype = "string"
        default = None
        desc = ""

        def _strip_optional(t: str) -> tuple[str, bool]:
            t = t.strip()
            opt = False
            if t.endswith("?"):
                t = t[:-1].strip()
                opt = True
            return t, opt

        type_match = re.match(r'^(\S+)\s*=\s*(.+?)\s*-\s*(.*)$', val)
        if type_match:
            raw_type = type_match.group(1)
            ptype, type_opt = _strip_optional(raw_type)
            if type_opt:
                required = False
            default = type_match.group(2).strip()
            desc = type_match.group(3).strip()
        else:
            type_match2 = re.match(r'^(\S+)\s*-\s*(.*)$', val)
            if type_match2:
                raw_type = type_match2.group(1)
                ptype, type_opt = _strip_optional(raw_type)
                if type_opt:
                    required = False
                desc = type_match2.group(2).strip()
            else:
                eq_match = re.match(r'^(.+?)\s*=\s*(.*)$', val)
                if eq_match:
                    default = eq_match.group(1).strip()
                    desc = eq_match.group(2).strip()
                else:
                    desc = val.strip()
        return Parameter(
            name=name,
            type=ptype,
            required=required,
            description=desc,
            default=default,
        )

    def _parse_directive_response(self, key: str, val: str, line: int) -> Response | None:
        code_str = key[8:].strip() if key.startswith("response") else key.strip()
        try:
            status_code: str | int = int(code_str) if code_str.isdigit() else code_str
        except (ValueError, TypeError):
            status_code = code_str
        desc = val.strip()
        schema_type = None
        schema_match = re.match(r'^(\w+)\s*-\s*(.*)$', val)
        if schema_match:
            schema_type = schema_match.group(1).strip()
            desc = schema_match.group(2).strip()
        return Response(status_code=status_code, description=desc)

    def _parse_directive_error(self, key: str, val: str, line: int) -> ErrorCode | None:
        code_str = key[5:].strip() if key.startswith("error") else key.strip()
        try:
            code: str | int = int(code_str) if code_str.isdigit() else code_str
        except (ValueError, TypeError):
            code = code_str
        msg = ""
        desc = val.strip()
        msg_match = re.match(r'^(.+?)\s*-\s*(.*)$', val)
        if msg_match:
            msg = msg_match.group(1).strip()
            desc = msg_match.group(2).strip()
        return ErrorCode(code=code, message=msg, description=desc)

    def _infer_param_locations(self, params: list[Parameter], path: str, method: str = "GET") -> None:
        import re as _re
        path_param_names = set(_re.findall(r'\{(\w+)\}', path))
        path_param_set = set()

        query_methods = {"GET", "HEAD", "DELETE", "OPTIONS"}
        default_loc = "query" if method.upper() in query_methods else "body"

        for p in params:
            if p.name in path_param_names:
                p.location = "path"
                p.required = True
                path_param_set.add(p.name)
            elif p.location == "body":
                p.location = default_loc

        body_duplicates = [i for i, p in enumerate(params) if p.location == "body" and p.name in path_param_set]
        for i in reversed(body_duplicates):
            params.pop(i)
