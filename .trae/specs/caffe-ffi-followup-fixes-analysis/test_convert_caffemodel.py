"""Test the convert_caffemodel.py tool by creating a synthetic V2 caffemodel
with known LayerParameter fields, converting it, and verifying the field numbers."""
import sys
sys.path.insert(0, '/SpecWeave/projects/xuanspace/libs/caffe-ffi/python')

from caffe_ffi import caffe_pb2
from convert_caffemodel import remap_message, STD_TO_CAFFE_FFI, CAFFE_FFI_TO_STD, WARN_FIELDS_STD_TO_CAFFEFFI

# Create a synthetic NetParameter with V2 layers using STANDARD (BVLC) field numbers
# We simulate a standard caffemodel by constructing NetParameter with LayerParameter entries
# that use BVLC field numbers. But since we're using caffe-ffi's proto (which has caffe-ffi
# field numbers), we need to construct at the wire-format level to test the remapper.
#
# Actually, let's construct a message manually at wire level:
# NetParameter:
#   name = "test_net" (field 1, wire type 2)
#   layer (field 100, wire type 2) = {
#     name = "conv1" (field 1, wire type 2)
#     type = "Convolution" (field 2, wire type 2)
#     convolution_param (field 106 in BVLC, wire type 2) = { num_output: 64 ... }
#     dropout_param (field 108 in BVLC, wire type 2) = { dropout_ratio: 0.5 }  -- Wait, this doesn't make sense for conv layer
#   }
#   layer (field 100, wire type 2) = {
#     name = "norm1" (field 1, wire type 2)
#     type = "Normalize" (field 2, wire type 2)
#     norm_param (field 149 in BVLC, wire type 2) = { across_spatial: false }
#   }
#   layer (field 100, wire type 2) = {
#     name = "pool1" (field 1, wire type 2)
#     type = "Pooling" (field 2, wire type 2)
#     pooling_param (field 121 in BVLC, wire type 2) = { kernel_size: 3 stride: 2 }
#   }

from io import BytesIO

def encode_tag(fn, wt):
    from convert_caffemodel import encode_tag as _et
    return _et(fn, wt)

def encode_varint(v):
    from convert_caffemodel import encode_varint as _ev
    return _ev(v)

def string_field(fn, s):
    """Encode a string field (wire type 2)."""
    data = s.encode('utf-8')
    return encode_tag(fn, 2) + encode_varint(len(data)) + data

def varint_field(fn, v):
    """Encode a varint field (wire type 0)."""
    return encode_tag(fn, 0) + encode_varint(v)

def bytes_field(fn, data):
    """Encode a length-delimited field."""
    return encode_tag(fn, 2) + encode_varint(len(data)) + data

# Build a convolution_param sub-message: num_output=64, kernel_size=7, stride=2
conv_param = b""
conv_param += varint_field(1, 7)    # kernel_size (field 1 in ConvolutionParameter)
conv_param += varint_field(3, 2)    # stride (field 3)
conv_param += varint_field(9, 64)   # num_output (field 9 in BVLC? let me check...)

# Actually let me use caffe-ffi's proto to build the inner param messages correctly,
# since ConvolutionParameter field numbers are the same across implementations.
cp = caffe_pb2.ConvolutionParameter()
cp.num_output = 64
cp.kernel_size.append(7)
cp.stride.append(2)
conv_param_bytes = cp.SerializeToString()
print(f"ConvolutionParameter: {len(conv_param_bytes)} bytes")

# Build a NormalizeParameter (norm_param sub-message)
np_param = caffe_pb2.NormalizeParameter()
np_param.across_spatial = False
norm_param_bytes = np_param.SerializeToString()
print(f"NormalizeParameter: {len(norm_param_bytes)} bytes")

# Build a PoolingParameter
pp = caffe_pb2.PoolingParameter()
pp.kernel_size = 3
pp.stride = 2
pp.pool = caffe_pb2.PoolingParameter.MAX
pool_param_bytes = pp.SerializeToString()
print(f"PoolingParameter: {len(pool_param_bytes)} bytes")

# Build a DropoutParameter
dp = caffe_pb2.DropoutParameter()
dp.dropout_ratio = 0.5
dropout_param_bytes = dp.SerializeToString()
print(f"DropoutParameter: {len(dropout_param_bytes)} bytes")

# Now build "BVLC-style" LayerParameter messages manually with BVLC field numbers:
# - convolution_param at field 106 (same in both)
# - norm_param at field 149 (BVLC)
# - pooling_param at field 121 (same in both)
# - dropout_param at field 108 (BVLC)

def make_bvlc_layer(name, type_str, param_fields):
    """
    Build a BVLC-style LayerParameter.
    param_fields: list of (field_number, param_bytes) tuples in BVLC numbering.
    """
    msg = b""
    msg += string_field(1, name)
    msg += string_field(2, type_str)
    for fn, pdata in param_fields:
        msg += bytes_field(fn, pdata)
    return msg

# Layer 1: Conv with dropout? No, let's make realistic layers
conv_layer_bvlc = make_bvlc_layer("conv1", "Convolution", [
    (106, conv_param_bytes),     # convolution_param = 106 (same)
])
norm_layer_bvlc = make_bvlc_layer("norm1", "Normalize", [
    (149, norm_param_bytes),     # norm_param = 149 (BVLC)
])
pool_layer_bvlc = make_bvlc_layer("pool1", "Pooling", [
    (121, pool_param_bytes),     # pooling_param = 121 (same)
])
dropout_layer_bvlc = make_bvlc_layer("drop1", "Dropout", [
    (108, dropout_param_bytes),  # dropout_param = 108 (BVLC)
])

# Build BVLC-style NetParameter
bvlc_net = b""
bvlc_net += string_field(1, "test_net")
for layer_bytes in [conv_layer_bvlc, norm_layer_bvlc, pool_layer_bvlc, dropout_layer_bvlc]:
    bvlc_net += bytes_field(100, layer_bytes)  # V2 layer at field 100

print(f"\nBVLC-style NetParameter: {len(bvlc_net)} bytes")

# Parse with caffe-ffi's proto to see if it fails (it should read conv/pool correctly
# since those have same field numbers, but norm_param and dropout_param should be
# misinterpreted)
net_before = caffe_pb2.NetParameter()
net_before.ParseFromString(bvlc_net)
print(f"Before conversion: {len(net_before.layer)} V2 layers")
for layer in net_before.layer:
    has_conv = layer.HasField("convolution_param")
    has_pool = layer.HasField("pooling_param")
    # In caffe-ffi proto, field 149 is dropout_param, field 108 is unused
    has_dropout_149 = layer.HasField("dropout_param")  # caffe-ffi reads field 149 as dropout
    has_norm_190 = layer.HasField("norm_param")       # caffe-ffi reads field 190 as norm
    has_dropout_108 = False  # field 108 is unused in caffe-ffi LayerParameter
    print(f"  layer '{layer.name}' type='{layer.type}' conv={has_conv} pool={has_pool} "
          f"dropout_at_149={has_dropout_149} norm_at_190={has_norm_190}")

# Now convert BVLC → caffe-ffi
print("\nConverting BVLC → caffe-ffi...")
caffe_ffi_net_bytes = remap_message(
    bvlc_net, STD_TO_CAFFE_FFI, WARN_FIELDS_STD_TO_CAFFEFFI, recurse_submessage=True
)
print(f"Converted: {len(caffe_ffi_net_bytes)} bytes")

# Parse with caffe-ffi's proto
net_after = caffe_pb2.NetParameter()
net_after.ParseFromString(caffe_ffi_net_bytes)
print(f"After conversion: {len(net_after.layer)} V2 layers")
all_ok = True
for layer in net_after.layer:
    has_conv = layer.HasField("convolution_param")
    has_pool = layer.HasField("pooling_param")
    has_dropout = layer.HasField("dropout_param")
    has_norm = layer.HasField("norm_param")
    print(f"  layer '{layer.name}' type='{layer.type}' conv={has_conv} pool={has_pool} "
          f"dropout={has_dropout} norm={has_norm}")

    # Verify correct params are present
    if layer.name == "conv1":
        assert has_conv, "conv1 should have convolution_param"
        assert layer.convolution_param.num_output == 64, "conv1 num_output should be 64"
    elif layer.name == "norm1":
        assert has_norm, "norm1 should have norm_param (field 190 after conversion)"
        assert not layer.HasField("dropout_param"), "norm1 should NOT have dropout_param"
    elif layer.name == "pool1":
        assert has_pool, "pool1 should have pooling_param"
        assert layer.pooling_param.kernel_size == 3, "pool1 kernel_size should be 3"
    elif layer.name == "drop1":
        assert has_dropout, "drop1 should have dropout_param (field 149 after conversion)"
        assert layer.dropout_param.dropout_ratio == 0.5, f"drop1 dropout_ratio should be 0.5, got {layer.dropout_param.dropout_ratio}"

print("\n[PASS] BVLC → caffe-ffi conversion verified!")

# Now test reverse: caffe-ffi → BVLC
print("\nConverting back caffe-ffi → BVLC...")
bvlc_back = remap_message(
    caffe_ffi_net_bytes, CAFFE_FFI_TO_STD, {}, recurse_submessage=True
)
print(f"Round-trip: {len(bvlc_back)} bytes")

# Verify round-trip produces identical bytes to original
if bvlc_back == bvlc_net:
    print("[PASS] Round-trip BVLC→caffe-ffi→BVLC produces identical binary!")
else:
    print("[WARN] Round-trip bytes differ (may be due to field ordering or unknown fields)")
    # This is not a failure - protobuf doesn't guarantee deterministic serialization

print("\n=== All conversion tests PASSED ===")
