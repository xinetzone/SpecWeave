#!/usr/bin/env python3
"""RQ-1 verification: standard BVLC `norm_param` (NormalizeParameter) parsing.

Checks:
  1. LayerParameter has a field named `norm_param` of type NormalizeParameter.
  2. A standard prototxt containing `norm_param { ... }` parses without error
     and the parameter is readable.
  3. `l2_norm_param` (field 158) remains backward compatible.
  4. Field number recorded (caffe-ffi uses 190; BVLC/caffex standard uses 149).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent  # specs
                       / "caffe-comprehensive-comparison-test"))

ROOT = Path(__file__).resolve().parent.parent.parent.parent  # -> SpecWeave
sys.path.insert(0, str(ROOT / "projects" / "xuanspace" / "libs" / "caffe-ffi" / "python"))

from caffe_ffi import caffe_pb2  # noqa: E402

failures = []

# --- 1. field exists ---
field = caffe_pb2.LayerParameter.DESCRIPTOR.fields_by_name.get("norm_param")
if field is None:
    failures.append("LayerParameter does not contain field 'norm_param'")
else:
    print(f"[OK] field 'norm_param' present: number={field.number} "
          f"type={field.message_type.full_name if field.message_type else field.type}")
    norm_num = field.number

l2 = caffe_pb2.LayerParameter.DESCRIPTOR.fields_by_name.get("l2_norm_param")
if l2 is None:
    failures.append("LayerParameter does not contain field 'l2_norm_param'")
else:
    print(f"[OK] field 'l2_norm_param' present: number={l2.number}")

# --- 2. parse standard prototxt with norm_param ---
PROTO = """
layer {
  name: "norm1"
  type: "Normalize"
  bottom: "data"
  top: "norm_out"
  norm_param {
    across_spatial: false
    channel_shared: true
    eps: 1e-10
  }
}
"""
np_ = caffe_pb2.NetParameter()
from google.protobuf import text_format  # noqa: E402
try:
    text_format.Parse(PROTO, np_)
    lp = np_.layer[0]
    if lp.HasField("norm_param"):
        print(f"[OK] parsed norm_param: across_spatial={lp.norm_param.across_spatial} "
              f"channel_shared={lp.norm_param.channel_shared} eps={lp.norm_param.eps}")
    else:
        failures.append("prototxt parsed but norm_param field not set")
except Exception as e:  # noqa: BLE001
    failures.append(f"parse failed: {e}")

# --- 3. l2_norm_param backward compat ---
PROTO_L2 = """
layer {
  name: "l2n"
  type: "L2Norm"
  bottom: "data"
  top: "l2_out"
  l2_norm_param { axis: 1 eps: 1e-5 }
}
"""
np2 = caffe_pb2.NetParameter()
try:
    text_format.Parse(PROTO_L2, np2)
    if np2.layer[0].HasField("l2_norm_param"):
        print("[OK] l2_norm_param backward compatible")
    else:
        failures.append("l2_norm_param not set after parse")
except Exception as e:  # noqa: BLE001
    failures.append(f"l2 parse failed: {e}")

# --- 4. binary round-trip of norm_param ---
try:
    data = np_.SerializeToString()
    np3 = caffe_pb2.NetParameter()
    np3.ParseFromString(data)
    if np3.layer[0].HasField("norm_param"):
        print("[OK] binary round-trip preserves norm_param")
    else:
        failures.append("binary round-trip lost norm_param")
except Exception as e:  # noqa: BLE001
    failures.append(f"binary round-trip failed: {e}")

print()
if failures:
    print("FAILURES:")
    for f in failures:
        print("  -", f)
    sys.exit(1)
print("RQ-1 verification PASSED")