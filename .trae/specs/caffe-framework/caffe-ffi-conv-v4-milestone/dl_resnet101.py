#!/usr/bin/env python3
"""Download ResNet-101 caffemodel (real weights) into /root/.caffe_test_data/models/.

Attempts multiple sources in order. Verifies the file is a valid CaffeModel
(> 100MB, not an HTML error page) before accepting.
"""
import os
import sys
import ssl
import urllib.request

TARGET_DIR = "/root/.caffe_test_data/models/"
TARGET = os.path.join(TARGET_DIR, "resnet101.caffemodel")

SOURCES = [
    # NVIDIA box archive (contains ResNet-101.caffemodel inside tar.gz)
    ("https://nvidia.box.com/shared/static/7zog25pu70nxjh2irni49e5ujlg4dl82.gz", "tar.gz"),
    # Common mirrors
    ("https://github.com/arunvishnu/ResNet_Caffe/raw/master/ResNet-101-model.caffemodel", "caffemodel"),
    ("http://dl.caffe.berkeleyvision.org/bvlc_resnet101.caffemodel", "caffemodel"),
]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def is_valid_caffemodel(path):
    if not os.path.exists(path):
        return False
    size = os.path.getsize(path)
    if size < 100 * 1024 * 1024:
        print(f"  size {size} too small (<100MB), likely error page")
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
            if kind == "tar.gz":
                import tarfile
                with tarfile.open(tmp, "r:gz") as tf:
                    member = None
                    for m in tf.getmembers():
                        if m.name.endswith(".caffemodel"):
                            member = m
                            break
                    if member is None:
                        print("  no .caffemodel inside archive")
                        os.unlink(tmp)
                        continue
                    tf.extract(member, TARGET_DIR)
                    os.rename(os.path.join(TARGET_DIR, member.name), TARGET)
                os.unlink(tmp)
            else:
                os.rename(tmp, TARGET)
            if is_valid_caffemodel(TARGET):
                print(f"SUCCESS: {TARGET} ({os.path.getsize(TARGET)} bytes)")
                return 0
            else:
                os.unlink(TARGET)
        except Exception as e:
            print(f"  failed: {type(e).__name__}: {e}")
            if os.path.exists(tmp):
                os.unlink(tmp)
    print("ALL SOURCES FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())