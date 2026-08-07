"""End-to-end A-001 fix verification: create Net with real weights and run forward."""
import sys
import numpy as np

from caffe_ffi import io

proto = '/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models/inceptionv1.prototxt'
model = '/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models/inceptionv1.caffemodel'

print('[1] Loading net via read_net (triggers _merge_weights + C++ NewNetFromProtoString)...')
net = io.read_net(proto, model)
print(f'    net loaded OK: {net}')

# Check conv1 weights via blobs_dict
print('[2] Inspecting conv1 weights via blobs_dict...')
# Check if params/blobs are accessible through the net
print(f'    layer_names (first 5): {net.layer_names[:5]}')
print(f'    blob_names (first 5): {net.blob_names[:5]}')

# Check conv1/7x7_s2 layer
try:
    conv1 = net.layer_by_name('conv1/7x7_s2')
    print(f'    layer_by_name conv1/7x7_s2: {conv1}')
    print(f'    layer type: {type(conv1)}')
    print(f'    layer dir: {[a for a in dir(conv1) if not a.startswith(\"__\")]}')
except Exception as e:
    print(f'    layer_by_name failed: {e}')

# Check blobs
try:
    conv1_blob = net.blob_by_name('conv1/7x7_s2')
    print(f'    blob_by_name conv1/7x7_s2: {conv1_blob}')
except KeyError:
    print('    blob conv1/7x7_s2 not found (intermediate blob name may differ)')

# Run forward pass
print('[3] Running forward pass with random input...')
input_shape = (1, 3, 224, 224)
dummy_input = np.random.randn(*input_shape).astype(np.float32)
out = net.forward({'data': dummy_input})
print(f'    forward OK, output keys={list(out.keys())}')
all_ok = True
for k, v in out.items():
    arr = np.array(v)
    has_nan = np.any(np.isnan(arr))
    has_inf = np.any(np.isinf(arr))
    print(f'    {k}: shape={arr.shape} NaN={has_nan} Inf={has_inf} min={arr.min():.4f} max={arr.max():.4f}')
    if has_nan or has_inf:
        all_ok = False

if all_ok:
    print('\n============================================================')
    print('[OK] A-001 verification PASSED: forward produces finite outputs')
    print('============================================================')
else:
    print('\n[FAIL] forward produced NaN/Inf')
    sys.exit(1)
