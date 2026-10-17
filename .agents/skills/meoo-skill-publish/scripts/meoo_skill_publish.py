#!/usr/bin/env python3
"""Meoo 技能市场发布三件套：package / relay / verify（纯标准库）。

- package: 校验技能暂存目录（frontmatter/name 一致/包外引用扫描），打根级确定性 ZIP，
  输出 .b64 载荷与逐文件 sha256 清单。
- relay:   仅绑定 127.0.0.1 的临时中继。GET 任意路径回传 b64（带 CORS）；
  POST /dump?name=xxx 把浏览器回流的二进制原样落盘。
- verify:  比较"线上回流 ZIP"与"本地发布 ZIP"的条目集合及逐文件 SHA256。
"""

import argparse
import base64
import hashlib
import json
import re
import sys
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
OUT_OF_PACKAGE_PATTERNS = [re.compile(p) for p in (r"\.\./", r"file:///")]
FIXED_ZIP_DATE = (2026, 1, 1, 0, 0, 0)


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_frontmatter(skill_md):
    text = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        die("SKILL.md 缺少 YAML 头信息（平台要求 --- 包裹的 frontmatter）")
    frontmatter = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip().strip("\"'")
    if not frontmatter.get("name"):
        die("frontmatter 缺少 name 字段")
    return frontmatter


def scan_out_of_package(src):
    hits = []
    for md in sorted(src.rglob("*.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        for number, line in enumerate(text.splitlines(), 1):
            for pattern in OUT_OF_PACKAGE_PATTERNS:
                if pattern.search(line):
                    snippet = line.strip()[:100]
                    hits.append(f"{md.relative_to(src)}:{number}: {snippet}")
    return hits


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def cmd_package(args):
    src = Path(args.src).resolve()
    if not (src / "SKILL.md").is_file():
        die(f"{src} 下没有 SKILL.md（暂存目录根级必须直接包含 SKILL.md）")
    frontmatter = read_frontmatter(src / "SKILL.md")
    if frontmatter["name"] != src.name:
        die(f"frontmatter name={frontmatter['name']} 与目录名 {src.name} 不一致")

    hits = scan_out_of_package(src)
    for hit in hits:
        print(f"WARN 包外引用疑似: {hit}")
    if args.strict and hits:
        die("--strict 模式下存在包外引用疑似项，停止打包")

    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in src.rglob("*") if p.is_file())
    if not any(p.relative_to(src).as_posix() == "SKILL.md" for p in files):
        die("ZIP 必须根级包含 SKILL.md")

    manifest = {"skill_name": frontmatter["name"], "version": frontmatter.get("version"), "files": []}
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            rel = path.relative_to(src).as_posix()
            data = path.read_bytes()
            info = zipfile.ZipInfo(rel, FIXED_ZIP_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
            manifest["files"].append({"path": rel, "size": len(data), "sha256": sha256_hex(data)})

    zip_bytes = out.read_bytes()
    manifest["zip"] = {"path": str(out), "size": len(zip_bytes), "sha256": sha256_hex(zip_bytes)}
    out.with_name(out.name + ".manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    out.with_name(out.name + ".b64").write_text(
        base64.encodebytes(zip_bytes).decode("ascii"), encoding="utf-8"
    )
    print(json.dumps(
        {"ok": True, "zip": str(out), "bytes": len(zip_bytes), "files": len(files), "warnings": len(hits)},
        ensure_ascii=False,
    ))


def zip_index(path):
    index = {}
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            data = archive.read(name)
            index[name] = {"size": len(data), "sha256": sha256_hex(data)}
    return index


def cmd_verify(args):
    online = zip_index(Path(args.online).resolve())
    expect = zip_index(Path(args.expect).resolve())
    identical = set(online) == set(expect)
    for name in sorted(set(online) | set(expect)):
        same = online.get(name) == expect.get(name)
        identical = identical and same
        label = "OK  " if same else "DIFF"
        left = online.get(name, {}).get("sha256", "<missing>")[:12]
        right = expect.get(name, {}).get("sha256", "<missing>")[:12]
        print(f"{label} {name}  online={left} expect={right}")
    summary = {"ok": identical, "online_entries": len(online), "expect_entries": len(expect)}
    print(json.dumps(summary, ensure_ascii=False))
    raise SystemExit(0 if identical else 1)


class RelayHandler(BaseHTTPRequestHandler):
    b64_path = None
    received_dir = None

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        data = Path(self.b64_path).read_bytes()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        query = parse_qs(urlparse(self.path).query)
        raw_name = query.get("name", ["dump.bin"])[0]
        name = Path(raw_name).name or "dump.bin"
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        received = Path(self.received_dir)
        received.mkdir(parents=True, exist_ok=True)
        (received / name).write_bytes(body)
        payload = json.dumps({"ok": True, "name": name, "bytes": len(body)}).encode("utf-8")
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


def cmd_relay(args):
    RelayHandler.b64_path = str(Path(args.b64).resolve())
    RelayHandler.received_dir = str(Path(args.received_dir).resolve())
    if not Path(RelayHandler.b64_path).is_file():
        die(f"b64 载荷不存在: {RelayHandler.b64_path}")
    server = ThreadingHTTPServer(("127.0.0.1", args.port), RelayHandler)
    print(f"RELAY_READY http://127.0.0.1:{args.port} b64={RelayHandler.b64_path}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def build_parser():
    parser = argparse.ArgumentParser(description="Meoo 技能市场发布三件套 package/relay/verify")
    sub = parser.add_subparsers(dest="command", required=True)

    p_package = sub.add_parser("package", help="校验暂存目录并打根级确定性 ZIP")
    p_package.add_argument("--src", required=True, help="暂存技能目录（根级直接含 SKILL.md）")
    p_package.add_argument("--out", required=True, help="输出 ZIP 路径")
    p_package.add_argument("--strict", action="store_true", help="存在包外引用疑似项即失败")
    p_package.set_defaults(func=cmd_package)

    p_relay = sub.add_parser("relay", help="127.0.0.1 临时中继（GET 回 b64 / POST 收回流文件）")
    p_relay.add_argument("--b64", required=True, help="package 产出的 .zip.b64")
    p_relay.add_argument("--received-dir", required=True, help="POST 回流文件落盘目录")
    p_relay.add_argument("--port", type=int, default=8765)
    p_relay.set_defaults(func=cmd_relay)

    p_verify = sub.add_parser("verify", help="逐文件 SHA256 比对线上 ZIP 与本地 ZIP")
    p_verify.add_argument("--online", required=True, help="从市场下载回流的 ZIP")
    p_verify.add_argument("--expect", required=True, help="本地发布用 ZIP")
    p_verify.set_defaults(func=cmd_verify)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
