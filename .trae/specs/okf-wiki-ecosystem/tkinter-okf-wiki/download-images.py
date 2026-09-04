# -*- coding: utf-8 -*-
"""Download 30 upload-images screenshots for tkinter-handbook bundle (scratch)."""
import json, re, os, time, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
RAW_MD = os.path.join(BASE, "raw", "md")
MAP_F = os.path.join(BASE, "raw", "image-map.json")
CHAP_F = os.path.join(BASE, "raw", "tkinter-handbook-chapters.json")
OUT = os.path.join(BASE, "dist", "_static", "bundles", "jishu", "gui", "tkinter-handbook", "images")
os.makedirs(OUT, exist_ok=True)

with open(MAP_F, encoding="utf-8") as f:
    imap = json.load(f)
with open(CHAP_F, encoding="utf-8") as f:
    chapters = json.load(f)

URL_RE = re.compile(r"https://upload-images\.jianshu\.io/upload_images/[^\s)\]]+?\.png")
HDRS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Referer": "https://www.jianshu.com/",
}

total = 0
ok = 0
fail = []
for ch in chapters:
    slug = ch["slug"]
    md_path = None
    for fn in os.listdir(RAW_MD):
        if fn.endswith(slug + ".md"):
            md_path = os.path.join(RAW_MD, fn)
            break
    if not md_path:
        print(f"[MISS-MD] {slug}")
        continue
    with open(md_path, encoding="utf-8") as f:
        text = f.read()
    urls = URL_RE.findall(text)
    seen = set()
    urls = [u for u in urls if not (u in seen or seen.add(u))]
    for u in urls:
        total += 1
        local = imap.get(u)
        if not local:
            fail.append((slug, u, "not in image-map"))
            continue
        dest_name = f"{slug}-{local}"
        dest = os.path.join(OUT, dest_name)
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            ok += 1
            continue
        try:
            req = urllib.request.Request(u, headers=HDRS)
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            if data[:4] != b"RIFF" and data[:8] != b"\x89PNG\r\n\x1a\n":
                fail.append((slug, u, f"bad magic {data[:8]!r}"))
                continue
            with open(dest, "wb") as f:
                f.write(data)
            ok += 1
            print(f"[OK] {dest_name} ({len(data)} bytes)")
            time.sleep(0.3)
        except Exception as e:
            fail.append((slug, u, str(e)))

print(f"\nTOTAL upload URLs: {total}, downloaded/existing: {ok}, failures: {len(fail)}")
for s, u, why in fail:
    print(f"[FAIL] {s} {u} -> {why}")
