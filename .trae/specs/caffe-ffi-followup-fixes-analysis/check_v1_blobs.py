"""Check V1 blob shapes for InceptionV1 classifier layer."""
from caffe_ffi import caffe_pb2

model = '/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models/inceptionv1.caffemodel'
m = caffe_pb2.NetParameter()
with open(model, 'rb') as f:
    m.ParseFromString(f.read())

# Find the classifier/inner product layer
for i, l in enumerate(m.layers):
    if 'classifier' in l.name.lower() or 'fc' in l.name.lower() or 'loss3' in l.name.lower():
        print(f'V1 layer[{i}] name={l.name} type={l.type} blobs={len(l.blobs)}')
        for j, b in enumerate(l.blobs):
            if b.HasField('shape') and b.shape.dim:
                shape = list(b.shape.dim)
            else:
                shape = [b.num, b.channels, b.height, b.width]
                shape = [d for d in shape if d != 0]
            print(f'  blob[{j}] shape={shape} data_size={len(b.data)} double_data_size={len(b.double_data)}')
            if b.data:
                print(f'    first 5 values: {list(b.data[:5])}')
        print()

# Also show the first few layers with blobs for reference
print('--- All layers with blobs (first 10) ---')
count = 0
for i, l in enumerate(m.layers):
    if l.blobs:
        if b.HasField('shape') and b.shape.dim:
            shape = list(b.shape.dim)
        else:
            shape = [l.blobs[0].num, l.blobs[0].channels, l.blobs[0].height, l.blobs[0].width]
            shape = [d for d in shape if d != 0]
        print(f'  [{i}] {l.name} type={l.type} blobs={len(l.blobs)} blob[0]shape={shape}')
        count += 1
        if count >= 10:
            break
