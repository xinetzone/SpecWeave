"""示例提取器：从MDI文档的example代码块中提取可执行测试数据。

支持的代码块类型：
- ```json / ```json example: 响应JSON示例，用于断言response.json()
- ```json request / ```json body: 请求JSON示例，用于测试输入
- ```python example: Python测试断言片段，直接嵌入测试函数
- ```js / ```javascript / ```ts / ```typescript example: JS/TS测试断言片段，直接嵌入Jest测试函数
- ```bash / ```curl: curl命令示例，解析为HTTP请求参数
- ```http: HTTP原始请求/响应格式

提取结果按接口组织，pytest/jest生成器优先使用example数据而非mock数据。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from mdi.models import CodeBlock, Interface


@dataclass
class ExtractedExample:
    """从代码块提取的单个测试示例。"""
    example_type: str
    language: str
    purpose: str
    data: Any
    raw_content: str
    meta: dict[str, str] = field(default_factory=dict)


def extract_examples(iface: Interface) -> list[ExtractedExample]:
    """从接口的代码块列表中提取所有可执行测试示例。

    Args:
        iface: 接口定义对象。

    Returns:
        提取的示例列表，按文档顺序排列。
    """
    results: list[ExtractedExample] = []
    for cb in iface.examples:
        ex = _extract_from_codeblock(cb)
        if ex is not None:
            results.append(ex)
    return results


def get_request_example(iface: Interface) -> dict[str, Any] | None:
    """获取接口的请求示例JSON（如果有）。

    优先使用 json request body 示例；若不存在，尝试从 curl 示例中提取 body。
    """
    for ex in extract_examples(iface):
        if ex.example_type == "request_body" and isinstance(ex.data, dict):
            return ex.data
    for ex in extract_examples(iface):
        if ex.example_type == "curl_request" and isinstance(ex.data, dict):
            body = ex.data.get("body")
            if isinstance(body, dict):
                return body
    return None


def get_response_example(iface: Interface, status_code: int | None = None) -> dict[str, Any] | None:
    """获取接口的响应示例JSON（如果有）。

    Args:
        iface: 接口定义。
        status_code: 期望的HTTP状态码。如果指定，优先返回该状态码的示例；否则返回第一个成功响应的示例。
    """
    if status_code is not None:
        for ex in extract_examples(iface):
            if ex.example_type == "response_body" and ex.meta.get("status") == str(status_code):
                return ex.data if isinstance(ex.data, dict) else None
        return None
    for ex in extract_examples(iface):
        if ex.example_type == "response_body" and ex.meta.get("status", "200").startswith("2"):
            return ex.data if isinstance(ex.data, dict) else None
    for ex in extract_examples(iface):
        if ex.example_type == "response_body":
            return ex.data if isinstance(ex.data, dict) else None
    return None


def get_python_assertions(iface: Interface) -> list[str]:
    """获取接口的Python测试断言片段（如果有）。"""
    results: list[str] = []
    for ex in extract_examples(iface):
        if ex.example_type == "python_assertion":
            results.append(ex.raw_content.strip())
    return results


def get_js_assertions(iface: Interface) -> list[str]:
    """获取接口的JavaScript/TypeScript测试断言片段（如果有）。"""
    results: list[str] = []
    for ex in extract_examples(iface):
        if ex.example_type == "js_assertion":
            results.append(ex.raw_content.strip())
    return results


def get_shell_examples(iface: Interface) -> list[str]:
    """获取接口的Shell/Bash CLI示例片段（如果有）。

    从 ```bash example / ```shell example / ```sh example 代码块提取，
    供CLI测试生成器使用。
    """
    results: list[str] = []
    for cb in iface.examples:
        lang = (cb.language or "").lower().strip()
        purpose = (cb.purpose or "").lower().strip()
        if lang in ("bash", "sh", "shell") and purpose in ("example", "test", ""):
            results.append(cb.content.strip())
    for ex in extract_examples(iface):
        if ex.example_type == "shell_example":
            results.append(ex.raw_content.strip())
    return results


def _extract_from_codeblock(cb: CodeBlock) -> ExtractedExample | None:
    lang = (cb.language or "").lower().strip()
    purpose = (cb.purpose or "").lower().strip()
    content = cb.content.strip()
    meta = _parse_meta(cb.meta)

    if not content:
        return None

    if lang in ("json",) or purpose in ("example", "response", "request", "mock", "schema"):
        if lang in ("json",) or _looks_like_json(content):
            return _extract_json_example(lang, purpose, content, meta)

    if lang in ("python", "py") or purpose == "test":
        return ExtractedExample(
            example_type="python_assertion",
            language=lang or "python",
            purpose=purpose,
            data=None,
            raw_content=content,
            meta=meta,
        )

    if lang in ("javascript", "js", "typescript", "ts"):
        return ExtractedExample(
            example_type="js_assertion",
            language=lang or "javascript",
            purpose=purpose or "test",
            data=None,
            raw_content=content,
            meta=meta,
        )

    if lang in ("bash", "sh", "shell", "curl"):
        is_curl = (
            lang == "curl"
            or bool(re.search(r'^[\s]*curl[\s]+', content))
            or bool(re.search(r'https?://\S+', content))
            and ('-X ' in content or '--data' in content or '-d ' in content)
        )
        if is_curl:
            return _extract_curl_example(lang, content, meta)
        return ExtractedExample(
            example_type="shell_example",
            language=lang,
            purpose=purpose or "example",
            data=None,
            raw_content=content,
            meta=meta,
        )

    if lang == "http":
        return _extract_http_example(content, meta)

    if lang in ("python", "py"):
        return ExtractedExample(
            example_type="python_assertion",
            language=lang,
            purpose=purpose or "test",
            data=None,
            raw_content=content,
            meta=meta,
        )

    return None


def _extract_json_example(
    lang: str, purpose: str, content: str, meta: dict[str, str]
) -> ExtractedExample | None:
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None

    example_type = "response_body"
    if purpose in ("request", "mock") or meta.get("part") == "request":
        example_type = "request_body"
    elif purpose in ("schema",):
        example_type = "schema"

    status = meta.get("status", "200")
    if not status.isdigit():
        combined = purpose + " " + " ".join(meta.values())
        for kw in ("200", "201", "204", "400", "401", "403", "404", "500"):
            if kw in combined:
                status = kw
                break

    return ExtractedExample(
        example_type=example_type,
        language=lang or "json",
        purpose=purpose or "example",
        data=data,
        raw_content=content,
        meta={**meta, "status": status},
    )


def _extract_curl_example(lang: str, content: str, meta: dict[str, str]) -> ExtractedExample | None:
    method = "GET"
    url = ""
    headers: dict[str, str] = {}
    body: dict[str, Any] | None = None

    method_match = re.search(r"-X\s+(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)", content, re.IGNORECASE)
    if method_match:
        method = method_match.group(1).upper()

    url_match = re.search(r"curl\s+(?:(?:-[^\s]+)\s+)*(?:['\"])?(https?://\S+?)(?:['\"]|(?:\s+-)|$)", content)
    if not url_match:
        url_match = re.search(r"curl\s+['\"]?(https?://\S+)", content)
    if url_match:
        url = url_match.group(1).rstrip("'\"")

    for h_match in re.finditer(r"-H\s+'([^']+)'|-H\s+\"([^\"]+)\"", content):
        h_val = h_match.group(1) or h_match.group(2)
        if ":" in h_val:
            k, v = h_val.split(":", 1)
            headers[k.strip()] = v.strip()

    data_match = re.search(
        r"(?:-d|--data|--data-raw|--data-binary)\s+'([^']+)'|(?:-d|--data|--data-raw|--data-binary)\s+\"([^\"]+)\"",
        content, re.DOTALL,
    )
    if data_match:
        raw_body = data_match.group(1) or data_match.group(2)
        try:
            body = json.loads(raw_body)
        except json.JSONDecodeError:
            body = None

    return ExtractedExample(
        example_type="curl_request",
        language=lang,
        purpose="curl",
        data={"method": method, "url": url, "headers": headers, "body": body},
        raw_content=content,
        meta=meta,
    )


def _extract_http_example(content: str, meta: dict[str, str]) -> ExtractedExample | None:
    lines = content.splitlines()
    if not lines:
        return None

    first_line = lines[0].strip()
    is_request = first_line.startswith(("GET ", "POST ", "PUT ", "DELETE ", "PATCH ", "HEAD ", "OPTIONS "))
    is_response = first_line.startswith("HTTP/")

    body_text = ""
    headers: dict[str, str] = {}
    sep_idx = 0
    for i, line in enumerate(lines):
        if line.strip() == "":
            sep_idx = i + 1
            break
        if ":" in line and not line.startswith("HTTP/"):
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()

    if sep_idx < len(lines):
        body_text = "\n".join(lines[sep_idx:]).strip()

    body_data: Any = None
    if body_text:
        try:
            body_data = json.loads(body_text)
        except json.JSONDecodeError:
            body_data = body_text

    if is_response:
        status_match = re.match(r"HTTP/[\d.]+\s+(\d+)", first_line)
        status = status_match.group(1) if status_match else "200"
        return ExtractedExample(
            example_type="response_body",
            language="http",
            purpose="example",
            data=body_data,
            raw_content=content,
            meta={**meta, "status": status},
        )

    if is_request:
        parts = first_line.split()
        method = parts[0] if parts else "GET"
        url = parts[1] if len(parts) > 1 else ""
        return ExtractedExample(
            example_type="request_body",
            language="http",
            purpose="request",
            data={"method": method, "url": url, "headers": headers, "body": body_data},
            raw_content=content,
            meta=meta,
        )

    return None


def _parse_meta(meta_str: str) -> dict[str, str]:
    """解析code block meta字符串（如 `json status=201 part=response`）。"""
    result: dict[str, str] = {}
    if not meta_str:
        return result
    for part in meta_str.split():
        if "=" in part:
            k, v = part.split("=", 1)
            result[k.strip().lower()] = v.strip().lower()
    return result


def _looks_like_json(content: str) -> bool:
    stripped = content.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return True
    if stripped.startswith("[") and stripped.endswith("]"):
        return True
    return False
