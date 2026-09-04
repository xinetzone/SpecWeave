#!/usr/bin/env python3
"""Environment check for caffe-ffi (py314) inside the caffe-ffi-jupyter container."""
import sys
import json

out = {"python": sys.version.split()[0], "platform": sys.platform}
try:
    import numpy as np
    out["numpy"] = np.__version__
except Exception as e:  # noqa: BLE001
    out["numpy_error"] = str(e)

try:
    import caffe_ffi
    out["caffe_ffi"] = getattr(caffe_ffi, "__version__", "?")
    from caffe_ffi import _ffi_api
    out["ffi_available"] = bool(_ffi_api.is_available())
    # locate the native extension to confirm it is loaded
    import caffe_ffi._ffi_api as m
    out["ffi_module_file"] = getattr(m, "__file__", None)
except Exception as e:  # noqa: BLE001
    out["caffe_ffi_error"] = f"{type(e).__name__}: {e}"

print(json.dumps(out, ensure_ascii=False, indent=2))