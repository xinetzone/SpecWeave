#!/usr/bin/env python3
"""
批量 caffemodel 格式转换工具
==============================
递归扫描项目目录下所有 .caffemodel 文件，将 BVLC 标准格式批量转换为 caffe-ffi 兼容格式，
并生成详细的转换报告。

功能：
  - 自动识别 V1（field 2）/ V2（field 100）格式
  - V1 格式模型：直接标记为"原生兼容"（caffe-ffi 通过 V1LayerParameter 解析器已支持）
  - V2 格式模型：执行字段编号重映射（norm_param 149→190 等）
  - 往返验证（round-trip）：转换后反向转换应与原始文件二进制一致
  - 可选：使用 caffe-ffi 验证转换后模型可正常加载权重（如 caffe_ffi 可导入）
  - 生成 JSON + Markdown 双格式报告

用法：
  # 扫描并转换（默认模式：BVLC → caffe-ffi）
  python batch_convert_caffemodels.py <root_dir>

  # 指定输出目录和报告路径
  python batch_convert_caffemodels.py <root_dir> -o <output_dir> -r <report_path>

  # 反向转换（caffe-ffi → BVLC）
  python batch_convert_caffemodels.py <root_dir> --to bvlc

  # 仅扫描不转换，输出模型清单
  python batch_convert_caffemodels.py <root_dir> --dry-run

  # 跳过大文件（>100MB）
  python batch_convert_caffemodels.py <root_dir> --max-size 104857600
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# Reuse core conversion logic from convert_caffemodel.py
# ──────────────────────────────────────────────────────────────────────────────

WIRE_VARINT = 0
WIRE_FIXED64 = 1
WIRE_LENDELIM = 2
WIRE_FIXED32 = 5

BVLC_TO_CAFFE_FFI: dict[int, int | None] = {
    100: None, 101: 140, 102: 144, 103: 172, 104: 150, 105: 187,
    107: 179, 108: 149, 109: 185, 110: 151, 111: 165, 112: 181, 113: 182,
    114: 161, 115: 180, 116: 188, 118: 155, 119: 183, 120: 168, 122: 163,
    124: 145, 126: 153, 127: 146, 128: 162, 129: 184, 130: 186, 131: 147,
    132: 173, 133: 152, 134: 166, 136: 169, 137: 174, 138: 170, 140: 148,
    144: 154, 145: 178, 146: 156, 147: 167, 148: 164, 149: 190,
}
CAFFE_FFI_TO_BVLC: dict[int, int | None] = {v: k for k, v in BVLC_TO_CAFFE_FFI.items() if v is not None}
CAFFE_FFI_ONLY: set[int] = {157, 158, 159, 160, 171, 175, 176, 177, 189}


def _read_varint(data: bytes, pos: int) -> tuple[int, int]:
    result = 0; shift = 0
    while pos < len(data):
        b = data[pos]; pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80): return result, pos
        shift += 7
        if shift > 63: raise ValueError(f"Varint too long at offset {pos}")
    raise ValueError(f"Unexpected EOF in varint at offset {pos}")

def _encode_varint(value: int) -> bytes:
    parts: list[int] = []
    while value > 0x7F:
        parts.append((value & 0x7F) | 0x80); value >>= 7
    parts.append(value & 0x7F)
    return bytes(parts)

def _skip_field(data: bytes, pos: int, wire_type: int) -> int:
    if wire_type == WIRE_VARINT:
        _, pos = _read_varint(data, pos)
    elif wire_type == WIRE_FIXED64: pos += 8
    elif wire_type == WIRE_LENDELIM:
        length, pos = _read_varint(data, pos); pos += length
    elif wire_type == WIRE_FIXED32: pos += 4
    else: raise ValueError(f"Unknown wire type {wire_type}")
    return pos

def _transform_layer_bytes(data: bytes, mapping: dict[int, int | None], skip_set: set[int]) -> bytes:
    out = bytearray(); pos = 0
    while pos < len(data):
        try: tag, pos = _read_varint(data, pos)
        except ValueError: break
        field_no = tag >> 3; wire_type = tag & 7
        if field_no < 100:
            if wire_type == WIRE_VARINT:
                val, after = _read_varint(data, pos); hdr = struct.pack('<B', tag) if tag < 128 else _encode_varint(tag)
                out += hdr + _encode_varint(val); pos = after
            elif wire_type == WIRE_FIXED64:
                out += data[pos - (len(_encode_varint(tag))): pos] if tag >= 128 else struct.pack('<B', tag)
                out += data[pos:pos + 8]; pos += 8
            elif wire_type == WIRE_LENDELIM:
                length, after_len = _read_varint(data, pos)
                payload = data[after_len:after_len + length]
                new_tag = field_no
                out += _encode_varint((new_tag << 3) | wire_type) + _encode_varint(length) + payload
                pos = after_len + length
            elif wire_type == WIRE_FIXED32:
                hdr = struct.pack('<B', tag) if tag < 128 else _encode_varint(tag)
                out += hdr + data[pos:pos + 4]; pos += 4
            else: raise ValueError(f"Unknown wire type {wire_type}")
        else:
            if field_no in skip_set:
                pos = _skip_field(data, pos, wire_type); continue
            new_field = mapping.get(field_no, field_no)
            if new_field is None:
                pos = _skip_field(data, pos, wire_type); continue
            if wire_type == WIRE_LENDELIM:
                length, after_len = _read_varint(data, pos)
                payload = data[after_len:after_len + length]
                out += _encode_varint((new_field << 3) | wire_type) + _encode_varint(length) + payload
                pos = after_len + length
            else:
                out += _encode_varint((new_field << 3) | wire_type)
                if wire_type == WIRE_VARINT:
                    val, pos = _read_varint(data, pos); out += _encode_varint(val)
                elif wire_type == WIRE_FIXED64: out += data[pos:pos + 8]; pos += 8
                elif wire_type == WIRE_FIXED32: out += data[pos:pos + 4]; pos += 4
    return bytes(out)

def convert_buffer(data: bytes, target: str = "caffe-ffi") -> bytes:
    mapping = BVLC_TO_CAFFE_FFI if target == "caffe-ffi" else CAFFE_FFI_TO_BVLC
    skip_set = CAFFE_FFI_ONLY if target == "bvlc" else set()
    out = bytearray(); pos = 0
    while pos < len(data):
        try: tag, pos = _read_varint(data, pos)
        except ValueError: break
        field_no = tag >> 3; wire_type = tag & 7
        if field_no == 100 and wire_type == WIRE_LENDELIM:
            length, after_len = _read_varint(data, pos)
            layer_data = data[after_len:after_len + length]
            new_layer = _transform_layer_bytes(layer_data, mapping, skip_set)
            out += _encode_varint((100 << 3) | WIRE_LENDELIM) + _encode_varint(len(new_layer)) + new_layer
            pos = after_len + length
        elif field_no == 2 and wire_type == WIRE_LENDELIM:
            length, after_len = _read_varint(data, pos)
            payload = data[after_len:after_len + length]
            out += _encode_varint((2 << 3) | WIRE_LENDELIM) + _encode_varint(length) + payload
            pos = after_len + length
        else:
            if wire_type == WIRE_VARINT:
                val, after = _read_varint(data, pos); out += _encode_varint(tag) + _encode_varint(val); pos = after
            elif wire_type == WIRE_FIXED64: out += _encode_varint(tag) + data[pos:pos + 8]; pos += 8
            elif wire_type == WIRE_LENDELIM:
                length, after_len = _read_varint(data, pos)
                payload = data[after_len:after_len + length]
                out += _encode_varint(tag) + _encode_varint(length) + payload; pos = after_len + length
            elif wire_type == WIRE_FIXED32: out += _encode_varint(tag) + data[pos:pos + 4]; pos += 4
    return bytes(out)

def detect_format(data: bytes) -> dict:
    v1_count = v2_count = 0; pos = 0; name = None
    while pos < len(data):
        try: tag, pos = _read_varint(data, pos)
        except ValueError: break
        fn = tag >> 3; wt = tag & 7
        if fn == 1 and wt == WIRE_LENDELIM and name is None:
            l, p2 = _read_varint(data, pos); name = data[p2:p2 + l].decode('utf-8', errors='replace'); pos = p2 + l
        elif fn == 2: v1_count += 1; pos = _skip_field(data, pos, wt)
        elif fn == 100: v2_count += 1; pos = _skip_field(data, pos, wt)
        else:
            try: pos = _skip_field(data, pos, wt)
            except ValueError: break
    if v1_count > 0 and v2_count == 0: fmt = "V1"
    elif v2_count > 0 and v1_count == 0: fmt = "V2"
    elif v1_count > 0 and v2_count > 0: fmt = "V1+V2-mixed"
    else: fmt = "unknown"
    return {"format": fmt, "v1_layers": v1_count, "v2_layers": v2_count, "name": name}

def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()[:16]


# ──────────────────────────────────────────────────────────────────────────────
# Batch processing
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ConvertResult:
    source: str
    source_size: int
    source_hash: str
    format: str
    v1_layers: int
    v2_layers: int
    model_name: Optional[str]
    status: str = "pending"  # converted / already_compatible / skipped / error
    output: Optional[str] = None
    output_size: Optional[int] = None
    output_hash: Optional[str] = None
    roundtrip_ok: Optional[bool] = None
    convert_time_ms: Optional[float] = None
    error: Optional[str] = None
    caffe_ffi_load_ok: Optional[bool] = None
    notes: list[str] = field(default_factory=list)


def find_caffemodels(root: Path, max_size: Optional[int] = None) -> list[Path]:
    models = []
    for p in root.rglob("*.caffemodel"):
        if not p.is_file(): continue
        if max_size and p.stat().st_size > max_size: continue
        # Skip build directories and hidden dirs
        parts = set(p.parts)
        if any(part.startswith(".") for part in p.relative_to(root).parts): continue
        if "__pycache__" in parts or "build" in parts: continue
        models.append(p)
    return sorted(models)


def process_model(src: Path, out_dir: Optional[Path], target: str, do_verify: bool,
                   dry_run: bool, caffe_ffi_available: bool) -> ConvertResult:
    result = ConvertResult(
        source=str(src), source_size=src.stat().st_size,
        source_hash="", format="unknown", v1_layers=0, v2_layers=0, model_name=None
    )
    try:
        t0 = time.perf_counter()
        data = src.read_bytes()
        result.source_hash = hashlib.sha256(data).hexdigest()[:16]
        fmt = detect_format(data)
        result.format = fmt["format"]; result.v1_layers = fmt["v1_layers"]
        result.v2_layers = fmt["v2_layers"]; result.model_name = fmt["name"]

        if dry_run:
            result.status = "scanned"
            result.convert_time_ms = round((time.perf_counter() - t0) * 1000, 1)
            return result

        # V1 models are natively compatible (no conversion needed)
        if result.format == "V1":
            result.status = "already_compatible"
            result.notes.append("V1格式已通过V1LayerParameter解析器原生支持")
            result.convert_time_ms = round((time.perf_counter() - t0) * 1000, 1)
            return result

        # V2 models: perform field remapping
        if result.format == "V2":
            converted = convert_buffer(data, target=target)
            result.convert_time_ms = round((time.perf_counter() - t0) * 1000, 1)

            # Round-trip verification
            back = convert_buffer(converted, target=("bvlc" if target == "caffe-ffi" else "caffe-ffi"))
            result.roundtrip_ok = (back == data)

            # Determine output path
            suffix = ".caffe-ffi.caffemodel" if target == "caffe-ffi" else ".bvlc.caffemodel"
            if out_dir:
                rel = src.relative_to(src.parents[0])  # relative to parent
                out_path = out_dir / (src.stem + suffix)
            else:
                out_path = src.with_name(src.stem + suffix)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_bytes(converted)
            result.output = str(out_path)
            result.output_size = len(converted)
            result.output_hash = hashlib.sha256(converted).hexdigest()[:16]

            if not result.roundtrip_ok:
                result.status = "error"
                result.error = "Round-trip verification failed (converted file does not match original after back-conversion)"
                return result

            # Optional: caffe-ffi load verification
            if caffe_ffi_available and target == "caffe-ffi":
                try:
                    import caffe_ffi
                    # Check if corresponding prototxt exists
                    proto_candidates = [
                        src.with_suffix('.prototxt'),
                        src.parent / (src.stem.replace('.caffemodel', '') + '.prototxt'),
                        src.parent / 'deploy.prototxt',
                    ]
                    proto = next((p for p in proto_candidates if p.exists()), None)
                    if proto:
                        net = caffe_ffi.read_net(str(proto), str(out_path))
                        blob_count = sum(1 for _ in net.blob_names())
                        result.caffe_ffi_load_ok = True
                        result.notes.append(f"caffe-ffi加载成功，{blob_count}个blob")
                    else:
                        result.notes.append("未找到prototxt，跳过caffe-ffi加载验证")
                except Exception as e:
                    result.caffe_ffi_load_ok = False
                    result.notes.append(f"caffe-ffi加载失败: {type(e).__name__}")

            result.status = "converted"
            return result

        if result.format == "V1+V2-mixed":
            result.status = "skipped"
            result.notes.append("混合V1+V2格式，暂不支持自动转换")
            result.convert_time_ms = round((time.perf_counter() - t0) * 1000, 1)
            return result

        result.status = "skipped"
        result.notes.append(f"未知格式: {result.format}")
        result.convert_time_ms = round((time.perf_counter() - t0) * 1000, 1)
        return result

    except Exception as e:
        result.status = "error"
        result.error = f"{type(e).__name__}: {e}"
        result.convert_time_ms = round((time.perf_counter() - t0) * 1000, 1) if 't0' in dir() else None
        return result


def format_size(n: int) -> str:
    if n < 1024: return f"{n}B"
    if n < 1024*1024: return f"{n/1024:.1f}KB"
    if n < 1024*1024*1024: return f"{n/1024/1024:.1f}MB"
    return f"{n/1024/1024/1024:.2f}GB"


def generate_report(results: list[ConvertResult], root: Path, target: str, out_path: Path):
    total = len(results)
    converted = [r for r in results if r.status == "converted"]
    compatible = [r for r in results if r.status == "already_compatible"]
    skipped = [r for r in results if r.status == "skipped"]
    errors = [r for r in results if r.status == "error"]
    scanned = [r for r in results if r.status == "scanned"]

    total_in = sum(r.source_size for r in results)
    total_out = sum(r.output_size or 0 for r in converted)
    total_time = sum(r.convert_time_ms or 0 for r in results)

    report = {
        "summary": {
            "root_directory": str(root),
            "target_format": target,
            "total_models": total,
            "converted": len(converted),
            "already_compatible": len(compatible),
            "skipped": len(skipped),
            "errors": len(errors),
            "scanned_only": len(scanned),
            "total_input_size": total_in,
            "total_output_size": total_out,
            "total_time_ms": round(total_time, 1),
        },
        "models": [asdict(r) for r in results],
    }

    json_path = out_path.with_suffix('.json')
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')

    # Markdown report
    md_lines = [
        "# Caffemodel 批量转换报告",
        f"",
        f"| 项目 | 值 |",
        f"|------|-----|",
        f"| 扫描目录 | `{root}` |",
        f"| 目标格式 | **{target}** |",
        f"| 总模型数 | {total} |",
        f"| 已转换 | {len(converted)} |",
        f"| 原生兼容 | {len(compatible)} |",
        f"| 跳过 | {len(skipped)} |",
        f"| 错误 | {len(errors)} |",
        f"| 总输入大小 | {format_size(total_in)} |",
        f"| 总输出大小 | {format_size(total_out)} |",
        f"| 总耗时 | {total_time/1000:.2f}s |",
        f"",
        f"## 详细结果",
        f"",
        f"| # | 文件 | 格式 | 大小 | 状态 | 耗时 | 备注 |",
        f"|---|------|------|------|------|------|------|",
    ]
    for i, r in enumerate(results, 1):
        status_icon = {"converted": "✅", "already_compatible": "🟢", "skipped": "⏭️",
                       "error": "❌", "scanned": "🔍"}.get(r.status, "❓")
        note = r.error or (r.notes[0] if r.notes else "")
        if len(note) > 50: note = note[:47] + "..."
        rel = Path(r.source).name
        md_lines.append(
            f"| {i} | {rel} | {r.format} | {format_size(r.source_size)} | "
            f"{status_icon} {r.status} | {r.convert_time_ms or '-'}ms | {note} |"
        )

    if errors:
        md_lines += ["", "## ❌ 错误详情", ""]
        for r in errors:
            md_lines.append(f"- **{Path(r.source).name}**: {r.error}")

    md_lines += [
        "", "## 字段映射说明", "",
        "| 参数字段 | BVLC field | caffe-ffi field | 处理方式 |",
        "|----------|-----------|----------------|---------|",
        "| convolution_param | 106 | 106 | ✅ 一致，无需转换 |",
        "| pooling_param | 121 | 121 | ✅ 一致，无需转换 |",
        "| inner_product_param | 117 | 117 | ✅ 一致，无需转换 |",
        "| relu_param | 123 | 123 | ✅ 一致，无需转换 |",
        "| softmax_param | 125 | 125 | ✅ 一致，无需转换 |",
        "| norm_param | 149 | 190 | 🔄 重映射 |",
        "| dropout_param | 108 | 149 | 🔄 重映射 |",
        "| lrn_param | 118 | 155 | 🔄 重映射 |",
        "| loss_param | 101 | 140 | 🔄 重映射 |",
        "| transform_param | 100 | (不存在) | ⛔ 丢弃 |",
        "| LeakyReLU/L2Norm/InstanceNorm等 | (不存在) | 157/158/159等 | ⛔ 反向转换时跳过 |",
    ]

    md_path = out_path.with_suffix('.md')
    md_path.write_text("\n".join(md_lines), encoding='utf-8')

    return json_path, md_path


def main():
    parser = argparse.ArgumentParser(description="批量转换 caffemodel 格式")
    parser.add_argument("root", type=Path, help="要扫描的根目录")
    parser.add_argument("-o", "--output-dir", type=Path, default=None,
                        help="转换后文件输出目录（默认与源文件同目录）")
    parser.add_argument("-r", "--report", type=Path, default=Path("conversion_report"),
                        help="报告文件前缀（默认: conversion_report）")
    parser.add_argument("--to", choices=["caffe-ffi", "bvlc"], default="caffe-ffi",
                        help="目标格式（默认: caffe-ffi）")
    parser.add_argument("--dry-run", action="store_true", help="仅扫描不转换")
    parser.add_argument("--no-verify", action="store_true", help="跳过往返验证")
    parser.add_argument("--max-size", type=int, default=None, help="最大文件大小（字节），超过则跳过")
    parser.add_argument("--no-caffe-ffi", action="store_true", help="跳过 caffe-ffi 加载验证")
    args = parser.parse_args()

    root: Path = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: 目录不存在: {root}", file=sys.stderr); sys.exit(1)

    # Check caffe-ffi availability
    caffe_ffi_available = False
    if not args.no_caffe_ffi:
        try:
            import caffe_ffi
            caffe_ffi_available = caffe_ffi.is_available()
            print(f"[INFO] caffe-ffi {caffe_ffi.__version__} 可用 (native={caffe_ffi_available})")
        except ImportError:
            print("[INFO] caffe-ffi 不可用，跳过加载验证")

    print(f"\n🔍 扫描目录: {root}")
    models = find_caffemodels(root, max_size=args.max_size)
    print(f"📁 找到 {len(models)} 个 .caffemodel 文件\n")

    if args.dry_run:
        print("⚠️  DRY RUN 模式 - 仅扫描不转换\n")

    results: list[ConvertResult] = []
    for i, model_path in enumerate(models, 1):
        rel = model_path.relative_to(root) if model_path.is_relative_to(root) else model_path.name
        print(f"  [{i}/{len(models)}] {rel} ({format_size(model_path.stat().st_size)})... ", end="", flush=True)
        r = process_model(model_path, args.output_dir, args.to,
                          do_verify=not args.no_verify, dry_run=args.dry_run,
                          caffe_ffi_available=caffe_ffi_available)
        status_icon = {"converted": "✅", "already_compatible": "🟢", "skipped": "⏭️",
                       "error": "❌", "scanned": "🔍"}.get(r.status, "❓")
        print(f"{status_icon} {r.status}" + (f" ({r.convert_time_ms}ms)" if r.convert_time_ms else ""))
        if r.error: print(f"       ❌ {r.error}")
        results.append(r)

    print(f"\n{'='*60}")
    json_path, md_path = generate_report(results, root, args.to, args.report)
    print(f"📊 JSON报告: {json_path}")
    print(f"📄 Markdown报告: {md_path}")

    converted = sum(1 for r in results if r.status == "converted")
    errors = sum(1 for r in results if r.status == "error")
    print(f"\n✅ 完成: {converted} 个转换, {errors} 个错误")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
