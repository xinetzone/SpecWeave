#!/usr/bin/env python3
"""Raw binary diagnosis of caffemodel: check what top-level fields exist."""
import struct

CAFFEMODEL = "/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets/models/inceptionv1.caffemodel"

with open(CAFFEMODEL, "rb") as f:
    data = f.read()

print(f"File size: {len(data)} bytes")

def read_varint(buf, pos):
    result = 0
    shift = 0
    while pos < len(buf):
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return result, pos

def read_tag(buf, pos):
    """Returns (field_number, wire_type, new_pos)"""
    varint, pos = read_varint(buf, pos)
    field_number = varint >> 3
    wire_type = varint & 0x07
    return field_number, wire_type, pos

def skip_field(buf, pos, wire_type):
    if wire_type == 0:  # varint
        _, pos = read_varint(buf, pos)
    elif wire_type == 1:  # 64-bit
        pos += 8
    elif wire_type == 2:  # length-delimited
        length, pos = read_varint(buf, pos)
        pos += length
    elif wire_type == 5:  # 32-bit
        pos += 4
    else:
        raise ValueError(f"Unknown wire type {wire_type} at pos {pos}")
    return pos

# Count top-level fields
pos = 0
field_counts = {}
layer_count = 0
layers_count = 0
i = 0
while pos < len(data) and i < 10000:
    fn, wt, pos = read_tag(data, pos)
    if fn == 100 and wt == 2:  # layer field (LayerParameter, length-delimited)
        layer_count += 1
    elif fn == 2 and wt == 2:  # layers field (V1LayerParameter, length-delimited)
        layers_count += 1
    field_counts[fn] = field_counts.get(fn, 0) + 1
    try:
        pos = skip_field(data, pos, wt)
    except Exception as e:
        print(f"Parse error at pos {pos}: {e}")
        break
    i += 1

print(f"Top-level field counts (first {i} tags):")
for fn in sorted(field_counts.keys()):
    wt_name = {0:"varint",1:"64bit",2:"len",5:"32bit"}.get("?","?")
    print(f"  field {fn}: {field_counts[fn]} occurrences")
print(f"\nfield 100 (layer, LayerParameter): {layer_count} occurrences")
print(f"field 2 (layers, V1LayerParameter): {layers_count} occurrences")
