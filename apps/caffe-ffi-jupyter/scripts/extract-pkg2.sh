#!/bin/bash
set -e
CONDA_BLD="/opt/conda/envs/caffe-ffi/conda-bld/linux-64"
_PKG=$(ls -t "$CONDA_BLD"/caffe-ffi-*.conda 2>/dev/null | head -1)
echo "Package: $_PKG"
echo ""

mkdir -p /tmp/pkg-inspect
cd /tmp/pkg-inspect
rm -rf *

echo "=== Extracting .conda using Python ==="
python << 'PYEOF'
import zipfile, tarfile, os, sys, subprocess

pkg_path = "/opt/conda/envs/caffe-ffi/conda-bld/linux-64/caffe-ffi-0.1.0-py314h2bc3f7f_0.conda"
extract_dir = "/tmp/pkg-inspect"

with zipfile.ZipFile(pkg_path, 'r') as z:
    print("Zip contents:", z.namelist())
    z.extractall(extract_dir)

# Find pkg tarball
for f in os.listdir(extract_dir):
    if f.startswith('pkg-') and (f.endswith('.tar.zst') or f.endswith('.tar.gz')):
        pkg_tar = os.path.join(extract_dir, f)
        print(f"Extracting: {f}")
        # Use tar command with zstd support
        subprocess.run(['tar', '--zstd', '-xf', pkg_tar, '-C', extract_dir], check=True)
        break

print("\n=== Full package tree ===")
for root, dirs, files in os.walk(extract_dir):
    # Skip hidden dirs and __pycache__
    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
    level = root.replace(extract_dir, '').count(os.sep)
    indent = '  ' * level
    print(f'{indent}{os.path.basename(root)}/')
    subindent = '  ' * (level + 1)
    for file in sorted(files):
        fpath = os.path.join(root, file)
        size = os.path.getsize(fpath)
        print(f'{subindent}{file} ({size} bytes)')
PYEOF
