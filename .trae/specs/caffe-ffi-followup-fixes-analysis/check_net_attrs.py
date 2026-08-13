"""Quick check of Net object attributes and conv1 weights."""
from caffe_ffi import io
import numpy as np

proto = '/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models/inceptionv1.prototxt'
model = '/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models/inceptionv1.caffemodel'

net = io.read_net(proto, model)
print('Net attributes:', [a for a in dir(net) if not a.startswith('__')])
print()

# Check layers by their accessible names
print('Checking layer access methods...')
# Try to access conv1/7x7_s2 weights
try:
    # Check if there's a method to list layers
    if hasattr(net, 'layers'):
        print(f'net.layers: {type(net.layers)}, len={len(net.layers)}')
    if hasattr(net, '_layers'):
        print(f'net._layers: {type(net._layers)}, len={len(net._layers)}')
    if hasattr(net, 'params'):
        print(f'net.params: {type(net.params)}')
        for k in list(net.params.keys())[:5]:
            print(f'  param[{k}]: {len(net.params[k])} blobs')
    if hasattr(net, 'blobs'):
        print(f'net.blobs: {type(net.blobs)}')
except Exception as e:
    print(f'Error: {e}')
    import traceback; traceback.print_exc()

# Run forward
print('\nRunning forward...')
dummy = np.random.randn(1, 3, 224, 224).astype(np.float32)
out = net.forward({'data': dummy})
for k, v in out.items():
    arr = np.array(v)
    print(f'{k}: shape={arr.shape} nan={np.any(np.isnan(arr))} inf={np.any(np.isinf(arr))}')
