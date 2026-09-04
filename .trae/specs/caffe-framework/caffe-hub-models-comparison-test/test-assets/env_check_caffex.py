import sys
import json

out = {
    "python": sys.version.split()[0],
    "platform": sys.platform,
}

try:
    import numpy as np
    out["numpy"] = np.__version__
except Exception as e:
    out["numpy_error"] = f"{type(e).__name__}: {e}"

try:
    import caffe
    out["caffe"] = getattr(caffe, "__version__", "?")
    out["caffe_root"] = caffe.__file__
    out["pb_available"] = bool(getattr(caffe, "proto", None) is not None)
    out["net_constructor"] = True
except Exception as e:
    out["caffe_error"] = f"{type(e).__name__}: {e}"

print(json.dumps(out, ensure_ascii=False, indent=2))