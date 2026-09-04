import tvm_ffi, os, glob
print('tvm_ffi version:', tvm_ffi.__version__)
d = os.path.dirname(tvm_ffi.__file__)
print('package dir:', d)
print('core .so files:', [os.path.basename(x) for x in glob.glob(os.path.join(d, '*.so'))])
print('native available:', tvm_ffi.core is not None)
# 简单 FFI 调用验证
n = tvm_ffi.core.Scalar(3)
print('Scalar test ok:', n.value)