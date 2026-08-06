"""环境预检验证脚本：检查 caffe_ffi C++ 扩展加载与核心接口。"""
import sys


def main() -> int:
    print("Python:", sys.version.split()[0])
    try:
        import caffe_ffi

        print("caffe_ffi version:", caffe_ffi.__version__)
    except Exception as exc:  # noqa: BLE001
        print("caffe_ffi import FAILED:", exc)
        return 1

    # 检查 C++ 扩展已加载（非 Python-only stub）
    try:
        from caffe_ffi import _caffe_ffi  # noqa: F401

        print("FFI_EXT_OK: c++ extension loaded")
    except Exception as exc:  # noqa: BLE001
        print("FFI_EXT_MISSING:", exc)

    # 核心接口
    from caffe_ffi import read_net, Net  # noqa: F401

    print("INTERFACE_OK: read_net / Net importable")
    print("Blob:", caffe_ffi.Blob)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())