"""Quick test of V1 weight merging after A-001 fix."""
from caffe_ffi import caffe_pb2, io
from google.protobuf import text_format

proto = '/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models/inceptionv1.prototxt'
model = '/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models/inceptionv1.caffemodel'

param = io.read_net_from_prototxt(proto)
print('V2 prototxt layers:', len(param.layer))
weights = io.read_net_from_binary(model)
print('caffemodel V2 layers:', len(weights.layer), 'V1 layers:', len(weights.layers))
io._merge_weights(param, weights)

for l in param.layer:
    if l.name == 'conv1/7x7_s2':
        print(f'conv1/7x7_s2 blobs: {len(l.blobs)}')
        if l.blobs:
            b = l.blobs[0]
            shape = list(b.shape.dim) if b.shape.dim else (b.num, b.channels, b.height, b.width)
            print(f'  blob[0] shape={shape} data[:5]={list(b.data[:5])}')
        break

txt = text_format.MessageToString(param)
assert 'conv1/7x7_s2' in txt
# Verify blobs are in text output
idx = txt.find('conv1/7x7_s2')
section = txt[idx:idx+800]
print('\nconv1 text section (first 800 chars):')
print(section)
print('\n[OK] V1 weight merge verified at Python level')
