#!/usr/bin/env python3
"""
SDK Caffemodel 批量转换入口脚本
=================================
自动扫描 external/chaos/sdk_full_test/ 目录（以及可选的其他 sdk_* 目录），
递归查找所有 .caffemodel 文件，批量转换为 caffe-ffi 兼容格式，并生成汇总报告。

用法：
  # 仅转换 sdk_full_test（默认）
  python convert_sdk_models.py

  # 转换所有 sdk_* 目录
  python convert_sdk_models.py --all

  # 指定输出目录
  python convert_sdk_models.py -o playground/caffemodel-conversion

  # 仅扫描不转换（dry-run）
  python convert_sdk_models.py --dry-run

  # 指定要扫描的SDK目录列表
  python convert_sdk_models.py --sdk-dirs sdk_full_test,sdk_caffe,sdk_test3
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from batch_convert_caffemodels import (  # noqa: E402
    ConvertResult, find_caffemodels, process_model, format_size
)

WORKSPACE_ROOT = SCRIPT_DIR.parent.parent.parent
CHAOS_ROOT = WORKSPACE_ROOT / "external" / "chaos"
DEFAULT_SDK_DIRS = ["sdk_full_test"]
ALL_SDK_DIRS = ["sdk_full_test", "sdk_caffe", "sdk_test", "sdk_test2", "sdk_test3"]


def find_sdk_dirs(specified: list[str] | None, all_dirs: bool) -> list[Path]:
    dirs_to_scan = ALL_SDK_DIRS if all_dirs else (specified or DEFAULT_SDK_DIRS)
    result = []
    for d in dirs_to_scan:
        p = CHAOS_ROOT / d
        if p.exists():
            result.append(p)
        else:
            print(f"⚠️  目录不存在，跳过: {p}")
    return result


def scan_dir(sdk_path: Path, out_dir: Path | None, target: str,
             dry_run: bool, max_size: int | None, do_verify: bool) -> list[ConvertResult]:
    """Scan one SDK directory and convert all models."""
    models = find_caffemodels(sdk_path, max_size=max_size)
    print(f"  找到 {len(models)} 个 .caffemodel 文件")

    results = []
    caffe_ffi_available = False
    if do_verify:
        try:
            import caffe_ffi  # noqa: F401
            caffe_ffi_available = True
        except ImportError:
            print("  ⚠️  caffe-ffi 不可用，跳过加载验证")

    for i, model_path in enumerate(models, 1):
        rel = model_path.relative_to(sdk_path)
        size_mb = model_path.stat().st_size / 1024 / 1024
        print(f"  [{i}/{len(models)}] {rel} ({size_mb:.1f}MB)... ", end="", flush=True)
        r = process_model(model_path, out_dir, target, do_verify, dry_run, caffe_ffi_available)
        status_icon = {
            "converted": "✅", "already_compatible": "🔵", "scanned": "📋",
            "skipped": "⏭️", "error": "❌"
        }.get(r.status, "?")
        print(f"{status_icon} {r.status}" + (f" ({r.convert_time_ms:.0f}ms)" if r.convert_time_ms else ""))
        if r.error:
            print(f"      Error: {r.error}")
        results.append(r)
    return results


def result_to_dict(r: ConvertResult) -> dict:
    d = asdict(r)
    d["rel_path"] = str(Path(r.source).name)
    d["size_mb"] = round(r.source_size / 1024 / 1024, 1)
    d["time_ms"] = r.convert_time_ms or 0
    d["note"] = "; ".join(r.notes) if r.notes else (r.error or "")
    d["model_format"] = r.format
    return d


def main():
    parser = argparse.ArgumentParser(description="SDK Caffemodel 批量转换工具")
    parser.add_argument("--all", action="store_true", help="扫描所有 sdk_* 目录")
    parser.add_argument("--sdk-dirs", default=None, help="逗号分隔的SDK目录名列表")
    parser.add_argument("-o", "--output-dir", default=None, help="转换后模型输出根目录")
    parser.add_argument("-r", "--report-dir", default=None, help="报告输出目录")
    parser.add_argument("--dry-run", action="store_true", help="仅扫描不转换")
    parser.add_argument("--max-size", type=int, default=None, help="跳过大文件（字节）")
    parser.add_argument("--to", choices=["caffe-ffi", "bvlc"], default="caffe-ffi", help="目标格式")
    parser.add_argument("--verify", action="store_true", help="转换后验证模型可加载（需要caffe-ffi）")
    args = parser.parse_args()

    specified = [s.strip() for s in args.sdk_dirs.split(",")] if args.sdk_dirs else None
    sdk_paths = find_sdk_dirs(specified, args.all)

    if not sdk_paths:
        print("❌ 没有找到有效的SDK目录")
        sys.exit(1)

    default_out = WORKSPACE_ROOT / "playground" / "caffemodel-conversion"
    output_root = Path(args.output_dir) if args.output_dir else default_out
    report_root = Path(args.report_dir) if args.report_dir else output_root
    output_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("SDK Caffemodel 批量转换工具")
    print(f"工作区: {WORKSPACE_ROOT}")
    print(f"扫描目录数: {len(sdk_paths)}")
    for p in sdk_paths:
        print(f"  - {p.name}")
    print(f"输出目录: {output_root}")
    print(f"报告目录: {report_root}")
    print(f"目标格式: {args.to}")
    print(f"模式: {'DRY-RUN（仅扫描）' if args.dry_run else '转换'}")
    print("=" * 70)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    all_results: dict[str, list[dict]] = {}
    total_models = total_converted = total_native = total_errors = total_skipped = 0
    total_input_size = total_output_size = 0
    t_start = time.time()

    for sdk_path in sdk_paths:
        sdk_name = sdk_path.name
        print(f"\n📂 {sdk_name}")
        sdk_output = output_root / sdk_name if not args.dry_run else None
        if sdk_output:
            sdk_output.mkdir(parents=True, exist_ok=True)
        results = scan_dir(sdk_path, sdk_output, args.to, args.dry_run, args.max_size, args.verify)
        result_dicts = [result_to_dict(r) for r in results]
        all_results[sdk_name] = result_dicts

        total_models += len(results)
        for r in results:
            total_input_size += r.source_size
            if r.status == "converted":
                total_converted += 1
                if r.output_size:
                    total_output_size += r.output_size
            elif r.status == "already_compatible":
                total_native += 1
                total_output_size += r.source_size
            elif r.status == "error":
                total_errors += 1
            elif r.status == "skipped":
                total_skipped += 1

    t_elapsed = time.time() - t_start

    # Generate summary report
    _write_summary(all_results, total_models, total_converted, total_native,
                   total_errors, total_skipped, total_input_size, total_output_size,
                   t_elapsed, sdk_paths, report_root, timestamp, args.to, args.dry_run)

    print(f"\n{'='*70}")
    print("📊 汇总结果")
    print(f"  总模型数: {total_models}")
    print(f"  已转换: {total_converted}")
    print(f"  原生兼容: {total_native}")
    print(f"  跳过: {total_skipped}")
    print(f"  错误: {total_errors}")
    if not args.dry_run:
        print(f"  总输入: {format_size(total_input_size)}")
        print(f"  总输出: {format_size(total_output_size)}")
    print(f"  总耗时: {t_elapsed:.2f}s")
    print(f"{'='*70}")


def _write_summary(all_results, total, converted, native, errors, skipped,
                   in_size, out_size, elapsed, sdk_paths, report_root,
                   timestamp, target_format, dry_run):
    summary = {
        "timestamp": datetime.now().isoformat(),
        "target_format": target_format,
        "dry_run": dry_run,
        "sdk_dirs": [p.name for p in sdk_paths],
        "total_models": total,
        "converted": converted,
        "native_compatible": native,
        "skipped": skipped,
        "errors": errors,
        "total_input_size": in_size,
        "total_output_size": out_size,
        "elapsed_seconds": round(elapsed, 2),
        "per_directory": all_results,
    }
    json_path = report_root / f"summary_{timestamp}.json"
    md_path = report_root / f"summary_{timestamp}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=str)

    md = []
    md.append("# SDK Caffemodel 批量转换汇总报告\n")
    md.append(f"| 项目 | 值 |")
    md.append(f"|------|-----|")
    md.append(f"| 生成时间 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |")
    md.append(f"| 目标格式 | **{target_format}** |")
    md.append(f"| 模式 | {'DRY-RUN（仅扫描）' if dry_run else '转换'} |")
    md.append(f"| 扫描目录数 | {len(sdk_paths)} |")
    md.append(f"| 总模型数 | {total} |")
    md.append(f"| 已转换 | {converted} |")
    md.append(f"| 原生兼容 | {native} |")
    md.append(f"| 跳过 | {skipped} |")
    md.append(f"| 错误 | {errors} |")
    if not dry_run:
        md.append(f"| 总输入 | {format_size(in_size)} |")
        md.append(f"| 总输出 | {format_size(out_size)} |")
    md.append(f"| 耗时 | {elapsed:.2f}s |\n")

    md.append("## 各目录统计\n")
    md.append("| 目录 | 模型数 | 转换 | 原生 | 跳过 | 错误 |")
    md.append("|------|--------|------|------|------|------|")
    for name, results in all_results.items():
        c = sum(1 for r in results if r["status"] == "converted")
        n = sum(1 for r in results if r["status"] == "already_compatible")
        s = sum(1 for r in results if r["status"] == "skipped")
        e = sum(1 for r in results if r["status"] == "error")
        md.append(f"| {name} | {len(results)} | {c} | {n} | {s} | {e} |")
    md.append("")

    for name, results in all_results.items():
        md.append(f"### {name}\n")
        if not results:
            md.append("（无caffemodel文件）\n")
            continue
        md.append("| # | 文件 | 格式 | 大小 | 状态 | 耗时 |")
        md.append("|---|------|------|------|------|------|")
        for i, r in enumerate(results, 1):
            icon = {"converted": "✅", "already_compatible": "🔵", "scanned": "📋",
                    "skipped": "⏭️", "error": "❌"}.get(r["status"], "?")
            md.append(f"| {i} | {Path(r['source']).name} | {r.get('format','?')} | "
                      f"{r['source_size']/1024/1024:.1f}MB | {icon} {r['status']} | "
                      f"{r.get('convert_time_ms',0) or 0:.0f}ms |")
        md.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"\n📄 汇总报告: {md_path}")


if __name__ == "__main__":
    main()
