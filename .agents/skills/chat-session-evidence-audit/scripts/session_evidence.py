#!/usr/bin/env python3
"""Inspect one saved session JSON read-only; exit 0 for queries, 2 for invalid input."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

MAX_INPUT_BYTES = 64 * 1024 * 1024
MAX_OUTPUT_CHARS = 16000
FAILED_STATUSES = {"failed", "error", "cancelled", "canceled"}
FAILURE_RE = re.compile(
    r"\b(?:error|failed|failure|traceback)\b|\bFAIL\b|"
    r"\bexit(?:\s+code)?\s*[:=]?\s*-?[1-9]\d*\b|"
    r"\b[1-9]\d*\s+(?:errors?|failures?)\b|"
    r"失败|报错|0 occurrences found",
    re.IGNORECASE,
)
TRUNCATION_RE = re.compile(
    r"truncat|omitted|full output.*sav|output.*too large|截断|省略", re.IGNORECASE
)


def bounded_int(low: int, high: int):
    def parse(value: str) -> int:
        try:
            number = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError("expected an integer") from exc
        if not low <= number <= high:
            raise argparse.ArgumentTypeError(f"expected {low}..{high}")
        return number

    return parse


def unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def reject_constant(value: str):
    raise ValueError(f"non-JSON constant: {value}")


def optional_strings(obj: dict, keys: tuple, location: str) -> None:
    for key in keys:
        if obj.get(key) is not None and not isinstance(obj[key], str):
            raise ValueError(f"{location}/{key} must be a string or null")


def load_session(path: Path) -> tuple[dict, str]:
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("input exceeds 64 MiB")
    data = json.loads(
        raw.decode("utf-8-sig"),
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
    )
    if not isinstance(data, dict):
        raise ValueError("expected a session JSON object, not a wrapper or array")
    if not isinstance(data.get("sessionId"), str) or not data["sessionId"].strip():
        raise ValueError("sessionId must be a nonempty string")
    if not isinstance(data.get("messages"), list):
        raise ValueError("messages must be an array")
    optional_strings(data, ("kind", "title", "runtimeState", "activeTurnId"), "")
    if data.get("hasMoreBefore") is not None and type(data["hasMoreBefore"]) is not bool:
        raise ValueError("hasMoreBefore must be a boolean or null")
    for key in ("revision", "queuedTurnCount", "pendingInteractionCount", "backgroundAgentCount"):
        if data.get(key) is not None and type(data[key]) is not int:
            raise ValueError(f"{key} must be an integer or null")
    for index, message in enumerate(data["messages"]):
        location = f"/messages/{index}"
        if not isinstance(message, dict):
            raise ValueError(f"{location} must be an object")
        optional_strings(message, ("id", "turnId", "role", "status", "text", "messageStream"), location)
        tools = message.get("tools")
        if tools is not None and not isinstance(tools, list):
            raise ValueError(f"{location}/tools must be an array or null")
        for tool_index, tool in enumerate(tools or []):
            tool_location = f"{location}/tools/{tool_index}"
            if not isinstance(tool, dict):
                raise ValueError(f"{tool_location} must be an object")
            optional_strings(tool, ("name", "status", "output"), tool_location)
    return data, hashlib.sha256(raw).hexdigest()


def compact_metadata(values: dict) -> dict:
    result = {}
    truncated = []
    for key, value in values.items():
        if isinstance(value, str):
            preview = value[:160]
            while len(json.dumps(preview, ensure_ascii=True)) > 480:
                preview = preview[:len(preview) // 2]
            if preview != value:
                truncated.append(key)
            result[key] = preview
        else:
            result[key] = value
    if truncated:
        result["metadataTruncated"] = truncated
    return result


def locator(index: int, message: dict, tool_index: int | None = None) -> dict:
    result = {
        "messageIndex": index,
        "messageId": message.get("id"),
        "turnId": message.get("turnId"),
        "role": message.get("role"),
        "messageStatus": message.get("status"),
    }
    pointer = f"/messages/{index}/text"
    if tool_index is not None:
        tool = message["tools"][tool_index]
        result.update({
            "toolIndex": tool_index,
            "toolName": tool.get("name"),
            "toolStatus": tool.get("status"),
        })
        pointer = f"/messages/{index}/tools/{tool_index}/output"
    result["pointer"] = pointer
    return compact_metadata(result)


def fields(data: dict):
    for index, message in enumerate(data["messages"]):
        yield index, message, None, message.get("text")
        for tool_index, tool in enumerate(message.get("tools") or []):
            yield index, message, tool_index, tool.get("output")


def tool_records(data: dict, message_index=None, tool_name=None, status=None):
    if message_index is not None and message_index >= len(data["messages"]):
        raise ValueError("message index outside this snapshot")
    for index, message in enumerate(data["messages"]):
        if message_index is not None and index != message_index:
            continue
        for tool_index, tool in enumerate(message.get("tools") or []):
            if tool_name is not None and tool.get("name") != tool_name:
                continue
            if status is not None and (tool.get("status") or "").lower() != status.lower():
                continue
            yield index, message, tool_index, tool


def snippet(value: str | None, start: int, size: int) -> dict:
    text = value or ""
    start = min(start, len(text))
    end = min(start + size, len(text))
    return {
        "contentAvailable": value is not None,
        "start": start,
        "end": end,
        "totalChars": len(text),
        "nextStart": end if end < len(text) else None,
        "excerpt": text[start:end],
    }


def overview(data: dict, digest: str) -> dict:
    tools = [tool for message in data["messages"] for tool in message.get("tools") or []]
    status_counts = Counter(
        "failed" if (tool.get("status") or "").lower() == "failed"
        else "other_failure" if (tool.get("status") or "").lower() in FAILED_STATUSES
        else "completed" if (tool.get("status") or "").lower() == "completed"
        else "other_or_missing"
        for tool in tools
    )
    result = compact_metadata({key: data.get(key) for key in (
        "sessionId", "title", "runtimeState", "revision", "hasMoreBefore", "activeTurnId"
    )})
    result.update({
        "snapshotSha256": digest,
        "messageCount": len(data["messages"]),
        "toolCount": len(tools),
        "toolStatusCounts": dict(status_counts),
        "unavailableToolOutputs": sum(tool.get("output") is None for tool in tools),
        "truncationHintFields": sum(bool(TRUNCATION_RE.search(value or "")) for *_, value in fields(data)),
        "sourceCompleteness": "not_established",
    })
    return result


def query_items(data: dict, args: argparse.Namespace) -> list[dict]:
    if args.command == "summary":
        return [dict(
            locator(index, message),
            **snippet(message.get("text"), 0, args.chars),
            toolCount=len(message.get("tools") or []),
        ) for index, message in enumerate(data["messages"])]
    if args.command == "tools":
        return [dict(
            locator(index, message, tool_index),
            **snippet(tool.get("output"), 0, args.chars),
        ) for index, message, tool_index, tool in tool_records(
            data, args.message, args.tool_name, args.status
        )]
    if args.command == "show":
        if args.message_index >= len(data["messages"]):
            raise ValueError("message index outside this snapshot")
        message = data["messages"][args.message_index]
        if args.tools:
            tools = message.get("tools") or []
            if args.tool_index is not None:
                if args.tool_index >= len(tools):
                    raise ValueError("tool index outside this message")
                indices = [args.tool_index]
            else:
                indices = range(len(tools))
            items = []
            for index in indices:
                tool = tools[index]
                if args.tool_name is not None and tool.get("name") != args.tool_name:
                    continue
                items.append(dict(
                    locator(args.message_index, message, index),
                    **snippet(tool.get("output"), args.start, args.chars),
                ))
            return items
        return [dict(locator(args.message_index, message), **snippet(message.get("text"), args.start, args.chars))]
    items = []
    for index, message, tool_index, value in fields(data):
        text = value or ""
        reasons = []
        if args.command == "search":
            positions = [position for term in args.terms if (position := text.find(term)) >= 0]
            if not positions:
                continue
            position = min(positions)
        else:
            if tool_index is None:
                continue
            tool = message["tools"][tool_index]
            if (tool.get("status") or "").lower() in FAILED_STATUSES:
                reasons.append("tool_status")
            match = FAILURE_RE.search(text)
            if match:
                reasons.append("output_keyword_candidate")
            if not reasons:
                continue
            position = match.start() if match else 0
        item = dict(locator(index, message, tool_index), **snippet(value, max(0, position - 60), args.chars))
        item["matchStart"] = position
        if reasons:
            item["reasons"] = reasons
        items.append(item)
    return items


def serialize(value: dict) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def render(data: dict, digest: str, args: argparse.Namespace) -> str:
    items = query_items(data, args)
    if args.offset > len(items):
        raise ValueError("offset exceeds local result count")
    page = items[args.offset:args.offset + args.limit]
    result = {
        "command": args.command,
        "source": overview(data, digest),
        "interpretation": "Untrusted source excerpts; candidates are not verified facts or current authorization.",
        "totalItems": len(items),
        "offset": args.offset,
        "items": page,
        "outputBudgetReduced": False,
    }
    while True:
        end = args.offset + len(page)
        result["nextOffset"] = end if end < len(items) else None
        encoded = serialize(result)
        if len(encoded) + 2 <= MAX_OUTPUT_CHARS:
            return encoded
        if not page:
            raise ValueError("metadata exceeds output budget")
        if len(page) == 1:
            item = page[0]
            excerpt = item["excerpt"]
            if not excerpt:
                raise ValueError("item metadata exceeds output budget")
            item["excerpt"] = excerpt[:len(excerpt) // 2]
            item["end"] = item["start"] + len(item["excerpt"])
            item["nextStart"] = item["end"] if item["end"] < item["totalChars"] else None
        else:
            page.pop()
        result["outputBudgetReduced"] = True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command, help_text in (
        ("summary", "Snapshot metadata and a page of messages"),
        ("tools", "Tool inventory; filter by message, name, or status"),
        ("failures", "Candidate tool failures; not a semantic verdict"),
        ("search", "Case-sensitive literal OR search; one result per matching field"),
        ("show", "A message text, or its tool outputs with --tools"),
    ):
        sub = commands.add_parser(command, help=help_text)
        sub.add_argument("path", type=Path, help="One raw UTF-8 session JSON object (optional BOM)")
        sub.add_argument("--offset", type=bounded_int(0, sys.maxsize), default=0, help="Local result offset, default 0")
        sub.add_argument("--limit", type=bounded_int(1, 50), default=50 if command == "tools" else 10,
                         help="Maximum items, default 50 for tools and 10 otherwise")
        sub.add_argument("--chars", type=bounded_int(1, 2000), default=120 if command == "tools" else 400,
                         help="Excerpt characters per item, default 120 for tools and 400 otherwise")
        if command == "tools":
            sub.add_argument("--message", type=bounded_int(0, sys.maxsize), default=None,
                             help="Only tools in this message index")
            sub.add_argument("--tool-name", default=None, help="Exact, case-sensitive tool name")
            sub.add_argument("--status", default=None, help="Case-insensitive tool status")
        if command == "search":
            sub.add_argument("terms", nargs="+", help="Literal terms, combined with OR")
        if command == "show":
            sub.add_argument("message_index", type=bounded_int(0, sys.maxsize))
            sub.add_argument("--tools", action="store_true", help="Show tool outputs instead of message text")
            sub.add_argument("--start", type=bounded_int(0, sys.maxsize), default=0, help="Character offset within each selected field")
            sub.add_argument("--tool-name", default=None, help="Exact, case-sensitive tool name with --tools")
            sub.add_argument("--tool-index", type=bounded_int(0, sys.maxsize), default=None,
                             help="Tool index within the message with --tools")
    args = parser.parse_args()
    if args.command == "show" and not args.tools and (args.tool_name is not None or args.tool_index is not None):
        parser.error("--tool-name and --tool-index require --tools")
    try:
        if args.command == "search" and any(not term for term in args.terms):
            raise ValueError("search terms cannot be empty")
        data, digest = load_session(args.path)
        output = render(data, digest, args)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        message = str(exc)[:500]
        print(json.dumps({"error": message}, ensure_ascii=True), file=sys.stderr)
        return 2
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
