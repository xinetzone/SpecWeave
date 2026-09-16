#!/usr/bin/env python3
"""olot_car.py - KServe ModelCar pack/extract helper for Jupyter container.

Wraps olot Python API with oras-py backend for zero-external-dependency
ModelCar image packaging inside the container.

Usage:
  oloot_car.py pack --base BASE_IMAGE --target TARGET_IMAGE [options] FILES...
  oloot_car.py extract --source SOURCE_IMAGE --output OUTPUT_DIR [options]
"""

import argparse
import logging
import shutil
import sys
import tempfile
from pathlib import Path


def _parse_kv_pairs(pairs):
    result = {}
    for p in pairs or []:
        if "=" not in p:
            print(f"[ERROR] Invalid key=value pair: {p}", file=sys.stderr)
            sys.exit(1)
        k, v = p.split("=", 1)
        result[k.strip()] = v.strip()
    return result


def cmd_pack(args):
    from olot.basics import oci_layers_on_top
    from olot.backend.oras_py import oras_py_pull, oras_py_push, is_oras_py

    if not is_oras_py():
        print("[ERROR] oras-py backend not available. Install: pip install olot[oras-py]", file=sys.stderr)
        sys.exit(1)

    model_files = [Path(f) for f in args.files]
    for mf in model_files:
        if not mf.exists():
            print(f"[ERROR] Model file not found: {mf}", file=sys.stderr)
            sys.exit(1)

    modelcard = Path(args.modelcard) if args.modelcard else None
    if modelcard and not modelcard.exists():
        print(f"[ERROR] ModelCarD file not found: {modelcard}", file=sys.stderr)
        sys.exit(1)

    if modelcard and modelcard in model_files:
        model_files = [f for f in model_files if f != modelcard]
        print("[WARN] Removed modelcard from model_files (it is passed via --modelcard)")

    root_dir = Path(args.root_dir) if args.root_dir else None
    if root_dir:
        for mf in model_files:
            try:
                mf.resolve().relative_to(root_dir.resolve())
            except ValueError:
                print(f"[ERROR] Model file {mf} is not under root_dir {root_dir}", file=sys.stderr)
                sys.exit(1)

    labels = _parse_kv_pairs(args.label)
    annotations = _parse_kv_pairs(args.annotation)
    insecure = args.plain_http

    work_dir = Path(tempfile.mkdtemp(prefix="olot-car-"))
    print(f"[olot] Work directory: {work_dir}")
    print(f"[olot] Pulling base image: {args.base}")

    try:
        oras_py_pull(args.base, work_dir, insecure=insecure, tls_verify=not insecure)
        print(f"[olot] Adding {len(model_files)} model layer(s)...")

        kwargs = {}
        if labels:
            kwargs["labels"] = labels
        if annotations:
            kwargs["annotations"] = annotations
        if root_dir:
            kwargs["root_dir"] = root_dir

        oci_layers_on_top(
            ocilayout=work_dir,
            model_files=model_files,
            modelcard=modelcard,
            **kwargs,
        )
        print(f"[olot] Pushing to: {args.target}")
        oras_py_push(work_dir, args.target, insecure=insecure, tls_verify=not insecure)
        print(f"[olot] SUCCESS: ModelCar image pushed to {args.target}")
    except Exception as e:
        print(f"[olot] ERROR: {e}", file=sys.stderr)
        logging.getLogger("olot").exception("Pack failed")
        sys.exit(1)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def cmd_extract(args):
    from olot.basics import crawl_ocilayout_blobs_to_extract
    from olot.backend.oras_py import oras_py_pull, is_oras_py

    if not is_oras_py():
        print("[ERROR] oras-py backend not available. Install: pip install olot[oras-py]", file=sys.stderr)
        sys.exit(1)

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    insecure = args.plain_http

    work_dir = Path(tempfile.mkdtemp(prefix="olot-car-"))
    print(f"[olot] Work directory: {work_dir}")
    print(f"[olot] Pulling source image: {args.source}")

    try:
        oras_py_pull(args.source, work_dir, insecure=insecure, tls_verify=not insecure)
        print(f"[olot] Extracting /models to: {output}")
        extracted = crawl_ocilayout_blobs_to_extract(
            work_dir, output, tar_filter_dir=args.tar_filter_dir
        )
        print(f"[olot] SUCCESS: Extracted {len(extracted)} file(s):")
        for f in extracted:
            print(f"  - {f}")
    except Exception as e:
        print(f"[olot] ERROR: {e}", file=sys.stderr)
        logging.getLogger("olot").exception("Extract failed")
        sys.exit(1)
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(
        description="KServe ModelCar pack/extract helper (olot + oras-py backend)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable DEBUG logging")
    sub = parser.add_subparsers(dest="command", required=True)

    p_pack = sub.add_parser("pack", help="Pack model files into ModelCar image and push to registry")
    p_pack.add_argument("-b", "--base", required=True, help="Base image reference (e.g., quay.io/mmortari/hello-world-wait:latest)")
    p_pack.add_argument("-t", "--target", required=True, help="Target image reference (e.g., localhost:5000/my-model:v1)")
    p_pack.add_argument("-m", "--modelcard", help="Path to ModelCarD README.md")
    p_pack.add_argument("-r", "--root-dir", help="Root directory for preserving subdirectory structure")
    p_pack.add_argument("-l", "--label", action="append", help="Labels (key=value, repeatable)")
    p_pack.add_argument("-a", "--annotation", action="append", help="Annotations (key=value, repeatable)")
    p_pack.add_argument("--plain-http", action="store_true", default=True, help="Use plain HTTP (no TLS) for registry (default: True)")
    p_pack.add_argument("--no-plain-http", dest="plain_http", action="store_false", help="Use HTTPS/TLS for registry")
    p_pack.add_argument("files", nargs="+", help="Model files to pack")

    p_ext = sub.add_parser("extract", help="Extract /models from ModelCar image to local directory")
    p_ext.add_argument("-s", "--source", required=True, help="Source ModelCar image reference")
    p_ext.add_argument("-o", "--output", required=True, help="Output directory for extracted files")
    p_ext.add_argument("--tar-filter-dir", default="/models", help="Directory prefix to extract (default: /models)")
    p_ext.add_argument("--plain-http", action="store_true", default=True, help="Use plain HTTP (no TLS) for registry (default: True)")
    p_ext.add_argument("--no-plain-http", dest="plain_http", action="store_false", help="Use HTTPS/TLS for registry")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    else:
        logging.basicConfig(level=logging.WARNING)

    if args.command == "pack":
        cmd_pack(args)
    elif args.command == "extract":
        cmd_extract(args)


if __name__ == "__main__":
    main()
