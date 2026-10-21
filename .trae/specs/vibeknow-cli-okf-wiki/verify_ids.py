#!/usr/bin/env python3
"""V 阶段机械校验：文档中出现的源码标识符是否真实存在于信源仓库。

用法：python verify_ids.py
- 扫描 bundle 内所有 .md，提取形如 `Ident` / `pkg.Ident` / `funcName()` 的标识符候选
- 过滤掉英文常用词与本教程自造词
- 在信源仓库（Go 源码 + 仓库自带 md）里逐个 Grep，报告未命中的候选
"""
import re
import subprocess
import sys
from pathlib import Path

SRC = Path(r"d:\spaces\SpecWeave\external\dao\flows\vibeknow\cli")
BUNDLE = Path(
    r"d:\spaces\SpecWeave\projects\awesome-okf-xs\doc\bundles\jishu\ai\products\vibeknow-cli"
)

# 文档里出现但**不是**源码标识符的词：英文常用词、Markdown 关键字、本教程自造术语
STOP = {
    # 通用英语
    "the", "and", "for", "with", "not", "but", "you", "are", "this", "that", "from",
    "when", "what", "why", "how", "all", "any", "one", "two", "three", "four", "five",
    "six", "seven", "eight", "nine", "ten", "has", "have", "had", "can", "will",
    "would", "should", "could", "must", "may", "might", "does", "did", "done",
    "get", "set", "put", "add", "new", "old", "use", "used", "using", "via", "per",
    "etc", "vs", "ok", "yes", "no", "n/a", "todo", "note", "notes", "see", "also",
    "only", "same", "each", "more", "less", "most", "least", "very", "much", "many",
    "here", "there", "then", "than", "them", "they", "its", "it", "in", "on", "at",
    "by", "as", "is", "be", "so", "we", "i", "if", "or", "up", "out", "own", "few",
    "into", "over", "under", "again", "still", "never", "always", "sometimes",
    # 本教程自造/中英混排标签
    "vibeknow", "cli", "go", "json", "yaml", "http", "https", "url", "urls", "api",
    "mp", "html", "utf", "uuid", "hmac", "sha", "ttl", "id", "ids", "ok",
    "dry", "run", "exit", "code", "codes", "flag", "flags", "env", "var", "vars",
    "stdin", "stdout", "stderr", "text", "ndjson", "sha256", "hex", "base64",
    "tty", "pty", "ci", "cd", "os", "db", "ui", "qa", "x", "y", "z", "e", "f", "g",
    "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "u", "v", "w", "b", "c",
    "d", "i", "j", "a", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    # Markdown / frontmatter 关键字
    "yaml", "toml", "frontmatter", "toctree", "maxdepth", "hidden", "md", "py",
    "sh", "bash", "go", "jsonl", "yml", "txt",
    # 英文普通词（文档叙述里出现但不是标识符）
    "run", "runs", "render", "renders", "rendering", "create", "creates",
    "export", "exports", "download", "downloads", "status", "list", "lists",
    "wait", "waits", "edit", "edits", "set", "pause", "resume", "script",
    "preset", "presets", "style", "styles", "image", "images", "video", "videos",
    "engine", "mode", "modes", "language", "voice", "voices", "theme", "themes",
    "page", "pages", "aspect", "bgm", "avatar", "prompt", "documents", "document",
    "work", "works", "session", "sessions", "task", "tasks", "job", "jobs",
    "ledger", "run", "agent", "agents", "skill", "skills", "command", "commands",
    "flag", "subcommand", "subcommands", "option", "options", "parameter",
    "parameters", "argument", "arguments", "value", "values", "path", "paths",
    "file", "files", "directory", "directories", "name", "names", "key", "keys",
    "field", "fields", "type", "types", "level", "levels", "size", "sizes",
    "state", "states", "status", "event", "events", "channel", "channels",
    "format", "formats", "output", "outputs", "input", "inputs", "result",
    "results", "payload", "payloads", "token", "tokens", "secret", "secrets",
    "hash", "hashes", "queue", "worker", "workers", "timeout", "timeouts",
    "interval", "seconds", "minute", "minutes", "hour", "hours", "day", "days",
    "source", "sources", "target", "targets", "context", "scope", "boundary",
    "boundaries", "reason", "reasons", "case", "cases", "table", "tables",
    "step", "steps", "part", "parts", "way", "ways", "point", "points",
    "line", "lines", "page", "code", "note", "warning", "hint", "hints",
    "error", "errors", "failure", "failures", "success", "successful",
    "example", "examples", "reference", "references", "concept", "concepts",
    "summary", "overview", "detail", "details", "action", "actions",
    "decision", "decisions", "rule", "rules", "law", "laws",
}

# 明确要在源码里找的标识符（人工精选，覆盖文档中所有源码符号）
IDENT = re.compile(r"\b([A-Z][A-Za-z0-9_]{2,})\b")   # Go 导出标识符
FUNC = re.compile(r"\b([a-z][A-Za-z0-9_]{3,})\(\)")   # 小写函数调用形式


def collect_tokens():
    tokens = set()
    for md in BUNDLE.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for m in IDENT.finditer(text):
            tokens.add(m.group(1))
        for m in FUNC.finditer(text):
            tokens.add(m.group(1))
    return {t for t in tokens if t not in STOP and not t.startswith("F_")}


def grep_source(token):
    # 只搜源码与仓库自带 md，排除 vendor/第三方目录
    r = subprocess.run(
        ["git", "grep", "-l", "-w", "--", token],
        cwd=str(SRC), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    if r.returncode == 0 and r.stdout.strip():
        return True
    return False


def main():
    tokens = sorted(collect_tokens())
    missing = [t for t in tokens if not grep_source(t)]
    print(f"候选标识符总数: {len(tokens)}")
    print(f"信源未命中: {len(missing)}")
    for t in missing:
        print(f"  MISSING: {t}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
