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
os.environ.setdefault('TVM_FFI', 'ctypes')
