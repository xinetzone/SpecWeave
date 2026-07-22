"""
Package runtime initialization script.
Installed to site-packages/ by Dockerfile, loaded via .pth file.
Sets up library paths and environment variables for the package.

Usage:
    1. Rename this file to _<your_package>_init.py (e.g., _xmnn_init.py)
    2. Rename pkg_init.pth to <your_package>_init.pth (e.g., xmnn_init.pth)
    3. Update the _pkg_init.pth to import the renamed module
    4. Update Dockerfile COPY paths accordingly
"""
import os

_pkg_dir = os.path.dirname(__file__)
_libs_dir = os.path.join(_pkg_dir, 'tvm', '_libs')

if os.path.isdir(_libs_dir):
    current = os.environ.get('LD_LIBRARY_PATH', '')
    if _libs_dir not in current:
        os.environ['LD_LIBRARY_PATH'] = (
            f'{_libs_dir}:{current}' if current else _libs_dir
        )

os.environ.setdefault('VTA_HW_PATH', os.path.join(_pkg_dir, 'vta'))
os.environ.setdefault('TVM_LIBRARY_PATH', _libs_dir)
