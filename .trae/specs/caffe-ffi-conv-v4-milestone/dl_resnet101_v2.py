#!/usr/bin/env python3
"""Download a real ResNet-101 caffemodel compatible with resnet101.prototxt.

The prototxt uses Kaiming He naming (res{2-5}{a-c}_branch{1,2{a,b,c}}).
Tries additional mirrors known to host this exact model.
"""
import os
import sys
import ssl
import urllib.request

TARGET_DIR = "/root/.caffe_test_data/models/"
TARGET = os.path.join(TARGET_DIR, "resnet101.caffemodel")

SOURCES = [
    # soeaver/caffe-model hosts converted ResNet models
    ("https://github.com/soeaver/caffe-model/raw/master/ResNet/ResNet-101.caffemodel", "caffemodel"),
    # KaimingHe deep-residual-networks (raw)
    ("https://github.com/KaimingHe/deep-residual-networks/raw/master/ResNet-101-deploy.caffemodel", "caffemodel"),
    # common dl mirror
    ("http://dl.caffe.berkeleyvision.org/bvlc_resnet101.caffemodel", "caffemodel"),
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def is_valid(path):
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    if size < 100 * 1024 * 1024:
        print(f"  size {size} too small (<100MB)")
        return False
    return True


def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    for url, kind in SOURCES:
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
            print(f"  downloaded {size} bytes")
            os.rename(tmp, TARGET)
            if is_valid(TARGET):
                print(f"SUCCESS: {TARGET} ({os.path.getsize(TARGET)} bytes)")
                return 0
            os.unlink(TARGET)
        except Exception as e:
            print(f"  failed: {type(e).__name__}: {e}")
            if os.path.exists(tmp):
                os.unlink(tmp)
    print("ALL SOURCES FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())