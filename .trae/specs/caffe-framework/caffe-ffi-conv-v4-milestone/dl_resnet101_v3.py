#!/usr/bin/env python3
"""Download real ResNet-101 caffemodel (Kaiming He naming) into
/root/.caffe_test_data/models/. Tries multiple authoritative sources.
"""
import os
import sys
import ssl
import urllib.request

TARGET_DIR = "/root/.caffe_test_data/models/"
TARGET = os.path.join(TARGET_DIR, "resnet101.caffemodel")

SOURCES = [
    # HuggingFace mirrors of bvlc_resnet101
    ("https://huggingface.co/deepgis/resnet/resolve/main/resnet101.caffemodel", "caffemodel"),
    ("https://huggingface.co/awinml/resnet-101-caffe/resolve/main/resnet101.caffemodel", "caffemodel"),
    # BVLC model zoo gist hosting
    ("https://raw.githubusercontent.com/BVLC/caffe/rc/models/bvlc_resnet101/readme.md", "probe"),
    # Known mirror (Baidu/other) - placeholder
    ("https://github.com/ruotianluo/ResNet-Caffe/raw/master/ResNet-101-model.caffemodel", "caffemodel"),
    ("https://github.com/arunvishnu/ResNet_Caffe/raw/master/ResNet-101-model.caffemodel", "caffemodel"),
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def probe(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="HEAD")
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            return r.status, r.headers.get("Content-Length")
    except Exception as e:
        return None, type(e).__name__


def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    # First probe the BVLC readme to learn the canonical URL
    print("=== Probe BVLC resnet101 readme ===")
    st, ct = probe(SOURCES[2][0])
    print(f"  {SOURCES[2][0]} -> {st} {ct}")
    for url, kind in SOURCES:
        if kind == "probe":
            continue
        print(f"Trying: {url}")
        tmp = TARGET + ".part"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp, open(tmp, "wb") as f:
                while True:
                    chunk = resp.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            size = os.path.getsize(tmp)
            head = open(tmp, "rb").read(4)
            print(f"  downloaded {size} bytes, magic={head.hex()}")
            if size < 100 * 1024 * 1024:
                print("  too small, skipping")
                os.unlink(tmp)
                continue
            os.rename(tmp, TARGET)
            print(f"SUCCESS: {TARGET} ({os.path.getsize(TARGET)} bytes)")
            return 0
        except Exception as e:
            print(f"  failed: {type(e).__name__}: {e}")
            if os.path.exists(tmp):
                os.unlink(tmp)
    print("ALL SOURCES FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())