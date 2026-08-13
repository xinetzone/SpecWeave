#!/usr/bin/env python3
"""
Caffemodel 格式转换工具
=====================
在 BVLC 标准 Caffe 与 caffe-ffi 的 caffemodel 二进制格式之间双向转换。

问题背景
--------
caffe-ffi 的 caffe.proto 中 LayerParameter 的参数字段编号与 BVLC 标准 Caffe 不同。
主要原因是 caffe-ffi 在标准字段基础上新增了多个自定义层参数（LeakyReLU、L2Norm、
InstanceNorm、MarginRanking、Im2col、BatchReindex、Filter、SigmoidCrossEntropyLoss、
Upsample 等），并且在 V2 参数字段区（field 100+）进行了重排，导致 field ≥100 的
param 字段编号整体偏移。

核心差异（LayerParameter V2 param 字段）
----------------------------------------
下表列出标准 BVLC 与 caffe-ffi 之间 field 编号不同的参数字段：

  标准 BVLC 字段名          标准field  caffe-ffi field  说明
  ─────────────────────────────────────────────────────────────────
  transform_param           100        (不存在)         caffe-ffi已移除
  loss_param                101        140              后移
  accuracy_param            102        144              后移
  argmax_param              103        172              后移
  concat_param              104        150              后移
  contrastive_loss_param    105        187              后移
  convolution_param         106        106              ✅ 相同
  data_param                107        179              后移
  dropout_param             108        149              后移
  dummy_data_param          109        185              后移
  eltwise_param             110        151              后移
  exp_param                 111        165              后移
  hdf5_data_param           112        181              后移
  hdf5_output_param         113        182              后移
  hinge_loss_param          114        161              重命名为hinge_param
  image_data_param          115        180              后移
  infogain_loss_param       116        188              后移
  inner_product_param       117        117              ✅ 相同
  lrn_param                 118        155              后移
  memory_data_param         119        183              后移
  mvn_param                 120        168              后移
  pooling_param             121        121              ✅ 相同
  power_param               122        163              后移
  relu_param                123        123              ✅ 相同
  sigmoid_param             124        145              后移
  softmax_param             125        125              ✅ 相同
  slice_param               126        153              后移
  tanh_param                127        146              后移
  threshold_param           128        162              后移
  window_data_param         129        184              后移
  python_param              130        186              后移
  prelu_param               131        147              后移
  spp_param                 132        173              后移
  reshape_param             133        152              后移
  log_param                 134        166              后移
  flatten_param             135        135              ✅ 相同
  reduction_param           136        169              后移
  embed_param               137        174              后移
  tile_param                138        170              后移
  batch_norm_param          139        139              ✅ 相同
  elu_param                 140        148              后移
  bias_param                141        141              ✅ 相同
  scale_param               142        142              ✅ 相同
  input_param               143        143              ✅ 相同
  crop_param                144        154              后移
  parameter_param           145        178              后移
  recurrent_param           146        156              后移
  swish_param               147        167              后移
  clip_param                148        164              后移
  norm_param                149        190              ★ 核心差异字段

注意：param 子消息内部的字段编号（如 ConvolutionParameter.num_output=1）在两个
版本中完全一致，无需重映射。LayerParameter 的基础字段（field 1-11: name, type,
bottom, top, blobs, param, loss_weight 等）编号也一致。只有 LayerParameter 的
field ≥100（param 字段本身）需要编号重映射。

转换策略（极简方案）
--------------------
只解析到两层深度，其他字节原样复制：
  1. NetParameter（顶层）：
     - 逐字段扫描，field 100 (V2 layers) 的每个元素进入 LayerParameter 处理
     - field 2 (V1 layers) 原样复制（V1LayerParameter 关键字段编号兼容）
     - 其他字段（name, input, input_shape, state 等）原样复制
  2. LayerParameter（V2 层参数）：
     - 逐字段扫描，field < 100 的原样复制（name/type/bottom/top/blobs 等兼容）
     - field ≥ 100 的应用映射表重编号，payload 字节原样复制（子消息内部兼容）
     - transform_param (field 100) 在 BVLC→caffe-ffi 方向跳过（caffe-ffi 中不存在）
     - caffe-ffi 独有字段在反向转换时跳过
  3. 不递归解析任何更深层嵌套（ConvolutionParameter、BlobProto、FillerParameter 等），
     因为它们的内部字段编号在两个版本中完全一致，原样复制即可。

用法
----
  # BVLC 标准 caffemodel → caffe-ffi 格式
  python convert_caffemodel.py bvlc_model.caffemodel caffe_ffi_model.caffemodel --to caffe-ffi

  # caffe-ffi 格式 → BVLC 标准 caffemodel
  python convert_caffemodel.py caffe_ffi_model.caffemodel bvlc_model.caffemodel --to bvlc

  # 验证：往返转换后文件二进制一致
  python convert_caffemodel.py input.caffemodel output.caffemodel --to caffe-ffi --verify
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Protobuf wire-type constants
# ──────────────────────────────────────────────────────────────────────────────
WIRE_VARINT = 0
WIRE_FIXED64 = 1
WIRE_LENDELIM = 2
WIRE_FIXED32 = 5

# ──────────────────────────────────────────────────────────────────────────────
# Field number mapping tables
# ──────────────────────────────────────────────────────────────────────────────
# BVLC standard → caffe-ffi mapping for V2 LayerParameter param fields (field ≥ 100)
# Only fields where numbers differ are listed. Fields with same numbers are omitted.
# Value = None means the field is dropped (does not exist in target format).

BVLC_TO_CAFFE_FFI: dict[int, int | None] = {
    100: None,   # transform_param → removed in caffe-ffi
    101: 140,    # loss_param
    102: 144,    # accuracy_param
    103: 172,    # argmax_param
    104: 150,    # concat_param
    105: 187,    # contrastive_loss_param
    107: 179,    # data_param
    108: 149,    # dropout_param
    109: 185,    # dummy_data_param
    110: 151,    # eltwise_param
    111: 165,    # exp_param
    112: 181,    # hdf5_data_param
    113: 182,    # hdf5_output_param
    114: 161,    # hinge_loss_param → hinge_param
    115: 180,    # image_data_param
    116: 188,    # infogain_loss_param
    118: 155,    # lrn_param
    119: 183,    # memory_data_param
    120: 168,    # mvn_param
    122: 163,    # power_param
    124: 145,    # sigmoid_param
    126: 153,    # slice_param
    127: 146,    # tanh_param
    128: 162,    # threshold_param
    129: 184,    # window_data_param
    130: 186,    # python_param
    131: 147,    # prelu_param
    132: 173,    # spp_param
    133: 152,    # reshape_param
    134: 166,    # log_param
    136: 169,    # reduction_param
    137: 174,    # embed_param
    138: 170,    # tile_param
    140: 148,    # elu_param
    144: 154,    # crop_param
    145: 178,    # parameter_param
    146: 156,    # recurrent_param
    147: 167,    # swish_param
    148: 164,    # clip_param
    149: 190,    # norm_param (★ core difference: 149→190)
}

# Reverse: caffe-ffi → BVLC standard
CAFFE_FFI_TO_BVLC: dict[int, int | None] = {v: k for k, v in BVLC_TO_CAFFE_FFI.items() if v is not None}

# Fields that exist only in caffe-ffi (no BVLC equivalent) → skip during reverse conversion
CAFFE_FFI_ONLY: set[int] = {
    157,  # leaky_relu_param
    158,  # l2_norm_param
    159,  # instance_norm_param
    160,  # margin_ranking_param
    171,  # im2col_param
    175,  # batch_reindex_param
    176,  # filter_param
    177,  # sigmoid_cross_entropy_loss_param
    189,  # upsample_param
}

# ──────────────────────────────────────────────────────────────────────────────
# Wire-format I/O primitives
# ──────────────────────────────────────────────────────────────────────────────

def _read_varint(data: bytes, pos: int) -> tuple[int, int]:
    """Read a protobuf varint starting at pos. Returns (value, new_pos)."""
    result = 0
    shift = 0
    while pos < len(data):
        b = data[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            return result, pos
        shift += 7
        if shift > 63:
            raise ValueError(f"Varint too long at offset {pos}")
    raise ValueError(f"Unexpected EOF while reading varint at offset {pos}")


def _encode_varint(value: int) -> bytes:
    """Encode an integer as a protobuf varint."""
    parts: list[int] = []
    while value > 0x7F:
        parts.append((value & 0x7F) | 0x80)
        value >>= 7
    parts.append(value & 0x7F)
    return bytes(parts)


def _make_tag(field_number: int, wire_type: int) -> bytes:
    """Encode a protobuf tag (field_number << 3 | wire_type)."""
    return _encode_varint((field_number << 3) | wire_type)


def _parse_tag(tag_value: int) -> tuple[int, int]:
    """Parse a tag value into (field_number, wire_type)."""
    return (tag_value >> 3, tag_value & 0x07)


# ──────────────────────────────────────────────────────────────────────────────
# Field value reader: reads one complete field value and returns its raw bytes
# ──────────────────────────────────────────────────────────────────────────────

WIRE_TYPE_LEN = {
    WIRE_VARINT: None,   # varint: variable length, determined by reading
    WIRE_FIXED64: 8,
    WIRE_LENDELIM: None, # length-delimited: length prefix + payload
    WIRE_FIXED32: 4,
}

def _read_field_raw(data: bytes, pos: int) -> tuple[bytes, int, int, int]:
    """
    Read one complete protobuf field starting at pos.
    Returns (raw_bytes, field_no, wire_type, new_pos).
    raw_bytes includes the tag and the complete value.
    """
    start = pos
    tag_val, pos = _read_varint(data, pos)
    field_no, wire_type = _parse_tag(tag_val)

    if wire_type == WIRE_VARINT:
        _, pos = _read_varint(data, pos)  # consume value
    elif wire_type == WIRE_FIXED64:
        pos += 8
    elif wire_type == WIRE_FIXED32:
        pos += 4
    elif wire_type == WIRE_LENDELIM:
        length, pos = _read_varint(data, pos)
        pos += length
    else:
        raise ValueError(f"Unknown wire type {wire_type} for field {field_no} at offset {start}")

    return data[start:pos], field_no, wire_type, pos


# ──────────────────────────────────────────────────────────────────────────────
# Core conversion
# ──────────────────────────────────────────────────────────────────────────────

def _convert_net(data: bytes, field_map: dict[int, int | None]) -> bytes:
    """
    Convert a serialized NetParameter message.
    Only processes field 100 (V2 layers) and field 2 (V1 layers);
    all other fields are copied verbatim.
    """
    out = bytearray()
    pos = 0

    while pos < len(data):
        raw, field_no, wire_type, pos = _read_field_raw(data, pos)

        if field_no == 100 and wire_type == WIRE_LENDELIM:
            # V2 LayerParameter entry — remap its param fields
            # raw = tag + length_prefix + payload; extract payload
            tag_end = len(_encode_varint((100 << 3) | WIRE_LENDELIM))
            # Re-parse to find payload boundaries properly
            p = pos - (len(raw) - tag_end)  # start of length varint
            length, payload_start = _read_varint(data, p)
            payload = data[payload_start:payload_start + length]

            new_payload = _convert_layer(payload, field_map)
            new_tag = _make_tag(100, WIRE_LENDELIM)
            new_len = _encode_varint(len(new_payload))
            out.extend(new_tag)
            out.extend(new_len)
            out.extend(new_payload)
        else:
            # All other fields (including field 2 V1 layers, name, input, etc.) — copy verbatim
            out.extend(raw)

    return bytes(out)


def _convert_layer(data: bytes, field_map: dict[int, int | None]) -> bytes:
    """
    Convert a serialized LayerParameter (V2) message.
    Fields < 100 are copied verbatim. Fields ≥ 100 are renumbered according to field_map.
    All payload bytes are copied verbatim (no deep recursion).
    """
    out = bytearray()
    pos = 0

    while pos < len(data):
        raw, field_no, wire_type, pos = _read_field_raw(data, pos)

        if field_no >= 100:
            # Apply field number mapping
            if field_no in field_map:
                new_field = field_map[field_no]
                if new_field is None:
                    # Field dropped (e.g., transform_param in BVLC→caffe-ffi)
                    continue
                # Reconstruct the field with new tag but same value bytes
                tag_end = 0
                # Determine how many bytes the old tag occupies
                test_pos = pos - len(raw)
                old_tag_val, _ = _read_varint(data, test_pos)
                # Compute old tag length by re-encoding old tag value
                old_tag_bytes = _encode_varint(old_tag_val)
                tag_end = len(old_tag_bytes)

                # Value bytes = raw[tag_end:]
                value_bytes = raw[tag_end:]
                new_tag = _make_tag(new_field, wire_type)
                out.extend(new_tag)
                out.extend(value_bytes)
            elif field_map is CAFFE_FFI_TO_BVLC and field_no in CAFFE_FFI_ONLY:
                # caffe-ffi-only field, no BVLC equivalent → skip
                continue
            else:
                # Field number unchanged → copy verbatim
                out.extend(raw)
        else:
            # Fields 1-99 (name, type, bottom, top, blobs, param, etc.) → copy verbatim
            out.extend(raw)

    return bytes(out)


# ──────────────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────────────

def convert_bvlc_to_caffe_ffi(data: bytes) -> bytes:
    """Convert a BVLC standard caffemodel to caffe-ffi format."""
    return _convert_net(data, BVLC_TO_CAFFE_FFI)


def convert_caffe_ffi_to_bvlc(data: bytes) -> bytes:
    """Convert a caffe-ffi caffemodel to BVLC standard format."""
    return _convert_net(data, CAFFE_FFI_TO_BVLC)


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert caffemodel between BVLC standard and caffe-ffi formats",
    )
    parser.add_argument("input", type=Path, help="Input caffemodel path")
    parser.add_argument("output", type=Path, help="Output caffemodel path")
    parser.add_argument(
        "--to",
        choices=["caffe-ffi", "bvlc"],
        required=True,
        help="Target format: 'caffe-ffi' (BVLC→caffe-ffi) or 'bvlc' (caffe-ffi→BVLC)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify round-trip: convert to target then back, check binary equality",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    src = args.input.read_bytes()
    print(f"Read {len(src):,} bytes from {args.input}")

    if args.to == "caffe-ffi":
        dst = convert_bvlc_to_caffe_ffi(src)
        direction = "BVLC standard → caffe-ffi"
    else:
        dst = convert_caffe_ffi_to_bvlc(src)
        direction = "caffe-ffi → BVLC standard"

    args.output.write_bytes(dst)
    print(f"Wrote {len(dst):,} bytes to {args.output} ({direction})")

    if args.verify:
        if args.to == "caffe-ffi":
            back = convert_caffe_ffi_to_bvlc(dst)
        else:
            back = convert_bvlc_to_caffe_ffi(dst)
        if back == src:
            print("✅ Round-trip verification PASSED (binary identical after back-conversion)")
        else:
            # Find first difference
            min_len = min(len(src), len(back))
            first_diff = next(
                (i for i in range(min_len) if src[i] != back[i]),
                min_len,
            )
            print(f"⚠️  Round-trip MISMATCH: original {len(src):,} bytes vs back-converted {len(back):,} bytes")
            print(f"   First difference at byte offset {first_diff}")
            print(f"   Original byte:  0x{src[first_diff]:02x}" if first_diff < len(src) else "   (original shorter)")
            print(f"   Back byte:      0x{back[first_diff]:02x}" if first_diff < len(back) else "   (back shorter)")


if __name__ == "__main__":
    main()
