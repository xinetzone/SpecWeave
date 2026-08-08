#!/usr/bin/env python3
"""Comprehensive benchmark: FP32/FP16/INT8-Dynamic/INT8-QDQ/INT8-QOperator on x64 CPU

Features:
- Structured logging with per-stage timing
- Memory usage tracking (if psutil available)
- CLI arguments for configuration
- Detailed per-precision breakdown
- JSON results export with full metadata
"""
import argparse
import json
import logging
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configure structured logging with timing support."""
    level = logging.DEBUG if verbose else logging.INFO
    logger = logging.getLogger("benchmark")
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = logging.Formatter(
            "[%(asctime)s] %(levelname)-7s | %(stage)-20s | %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


class StageTimer:
    """Context manager for timing code stages with logging."""
    def __init__(self, logger: logging.Logger, stage: str):
        self.logger = logger
        self.stage = stage
        self.t0 = 0.0
        self.elapsed = 0.0

    def __enter__(self):
        self.t0 = time.perf_counter()
        self.logger.debug("Starting stage", extra={"stage": self.stage})
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.t0
        self.logger.info(
            f"Completed in {self.elapsed*1000:.1f}ms",
            extra={"stage": self.stage},
        )


def log_mem(logger: logging.Logger, stage: str, note: str = ""):
    """Log memory usage if psutil is available (non-fatal if missing)."""
    try:
        import psutil
        proc = psutil.Process(os.getpid())
        mem_mb = proc.memory_info().rss / (1024 * 1024)
        logger.debug(f"RSS={mem_mb:.1f}MB {note}", extra={"stage": stage})
    except ImportError:
        pass


# ---------------------------------------------------------------------------
# Model definitions
# ---------------------------------------------------------------------------
import torch
import onnx
import onnxsim
import onnxruntime as ort
from onnxruntime.quantization import (
    quantize_dynamic, quantize_static, CalibrationDataReader,
    QuantType, QuantFormat, CalibrationMethod,
)

try:
    from onnxconverter_common import float16
except ImportError:
    float16 = None

SEP = "=" * 70
DASH = "-" * 70
WARMUP = 50
RUNS = 300
CALIB_SAMPLES = 100


class SmallMLP(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(128, 256), torch.nn.ReLU(),
            torch.nn.Linear(256, 256), torch.nn.ReLU(),
            torch.nn.Linear(256, 64), torch.nn.ReLU(),
            torch.nn.Linear(64, 10),
        )
    def forward(self, x): return self.net(x)


class LargeMLP(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.net = torch.nn.Sequential(
            torch.nn.Linear(1024, 2048), torch.nn.ReLU(),
            torch.nn.Linear(2048, 2048), torch.nn.ReLU(),
            torch.nn.Linear(2048, 1024), torch.nn.ReLU(),
            torch.nn.Linear(1024, 512), torch.nn.ReLU(),
            torch.nn.Linear(512, 100),
        )
    def forward(self, x): return self.net(x)


class ConvNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = torch.nn.Sequential(
            torch.nn.Conv2d(3, 32, 3, padding=1), torch.nn.ReLU(),
            torch.nn.Conv2d(32, 32, 3, padding=1), torch.nn.ReLU(),
            torch.nn.AdaptiveAvgPool2d(8),
        )
        self.fc = torch.nn.Linear(32*8*8, 10)
    def forward(self, x):
        x = self.conv(x)
        x = x.flatten(1)
        return self.fc(x)


class TransformerLike(torch.nn.Module):
    def __init__(self, d=256, heads=4):
        super().__init__()
        self.d = d
        self.qkv = torch.nn.Linear(d, d*3)
        self.proj = torch.nn.Linear(d, d)
        self.ffn = torch.nn.Sequential(
            torch.nn.Linear(d, d*4), torch.nn.ReLU(), torch.nn.Linear(d*4, d)
        )
        self.head = torch.nn.Linear(d, 10)
    def forward(self, x):
        B, S, D = x.shape
        qkv = self.qkv(x).reshape(B, S, 3, 4, D//4).permute(2,0,3,1,4)
        q, k, v = qkv[0], qkv[1], qkv[2]
        attn = torch.matmul(q, k.transpose(-2,-1)) / (D//4)**0.5
        attn = torch.softmax(attn, dim=-1)
        out = torch.matmul(attn, v).transpose(1,2).reshape(B, S, D)
        out = self.proj(out)
        out = self.ffn(out)
        return self.head(out[:, 0, :])


MODELS = [
    ('SmallMLP(128->10)', SmallMLP(), torch.randn(1, 128), (1,128), 'input'),
    ('LargeMLP(1024->100)', LargeMLP(), torch.randn(1, 1024), (1,1024), 'input'),
    ('ConvNet(3x32x32->10)', ConvNet(), torch.randn(1,3,32,32), (1,3,32,32), 'input'),
    ('Transformer(16x256->10)', TransformerLike(), torch.randn(1,16,256), (1,16,256), 'input'),
]


class CalibReader(CalibrationDataReader):
    def __init__(self, samples, input_name='input'):
        self.data = samples
        self.i = 0
        self.input_name = input_name
    def get_next(self):
        if self.i >= len(self.data): return None
        d = {self.input_name: self.data[self.i]}
        self.i += 1
        return d


def benchmark_session(
    sess: ort.InferenceSession,
    input_shape: Tuple,
    input_name: str,
    warmup: int = WARMUP,
    runs: int = RUNS,
    logger: logging.Logger = None,
) -> Dict[str, float]:
    """Benchmark an ORT session with detailed timing stats."""
    stage = "benchmark"
    # Warmup
    if logger:
        logger.info(f"Warmup: {warmup} iterations", extra={"stage": stage})
    inp = np.random.randn(*input_shape).astype(np.float32)
    with StageTimer(logger, f"{stage}.warmup") if logger else nullcontext():
        for _ in range(warmup):
            sess.run(None, {input_name: inp})
    log_mem(logger, stage, "after warmup")

    # Timed runs
    if logger:
        logger.info(f"Benchmark: {runs} timed iterations", extra={"stage": stage})
    times = []
    for _ in range(runs):
        inp = np.random.randn(*input_shape).astype(np.float32)
        t0 = time.perf_counter()
        sess.run(None, {input_name: inp})
        times.append(time.perf_counter() - t0)
    t = np.array(times) * 1000
    stats = {
        'avg_ms': float(np.mean(t)),
        'p50_ms': float(np.median(t)),
        'p95_ms': float(np.percentile(t, 95)),
        'p99_ms': float(np.percentile(t, 99)),
        'min_ms': float(np.min(t)),
        'max_ms': float(np.max(t)),
        'std_ms': float(np.std(t)),
    }
    if logger:
        logger.info(
            f"avg={stats['avg_ms']:.4f}ms p50={stats['p50_ms']:.4f}ms "
            f"p95={stats['p95_ms']:.4f}ms p99={stats['p99_ms']:.4f}ms",
            extra={"stage": stage},
        )
    return stats


class nullcontext:
    """Fallback context manager for when StageTimer is not used."""
    def __enter__(self): return self
    def __exit__(self, *args): pass


def get_sess_options(intra_threads: int = 4, logger: logging.Logger = None) -> ort.SessionOptions:
    """Build ORT SessionOptions with logging."""
    stage = "session-init"
    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    so.intra_op_num_threads = intra_threads
    so.inter_op_num_threads = 1
    so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    if logger:
        logger.info(
            f"graph_opt=ALL intra_threads={intra_threads} inter_threads=1 mode=SEQUENTIAL",
            extra={"stage": stage},
        )
    return so


def export_to_onnx(
    model: torch.nn.Module,
    dummy: torch.Tensor,
    path: str,
    input_name: str,
    logger: logging.Logger,
) -> None:
    """Export PyTorch model to ONNX with logging."""
    stage = "export"
    model.eval()
    with StageTimer(logger, f"{stage}.torch2onnx"):
        torch.onnx.export(
            model, dummy, path,
            input_names=[input_name], output_names=['output'],
            opset_version=18, do_constant_folding=True,
        )
    size_kb = os.path.getsize(path) / 1024
    logger.info(f"Exported ONNX: {size_kb:.1f}KB", extra={"stage": stage})
    log_mem(logger, stage, "after export")


def simplify_onnx(path: str, logger: logging.Logger) -> None:
    """Simplify ONNX model with onnxsim."""
    stage = "simplify"
    with StageTimer(logger, f"{stage}.onnxsim"):
        m = onnx.load(path)
        m_simp, ok = onnxsim.simplify(m)
        if not ok:
            logger.warning("onnxsim reported simplification issues", extra={"stage": stage})
        onnx.save(m_simp, path)
    size_kb = os.path.getsize(path) / 1024
    logger.info(f"Simplified ONNX: {size_kb:.1f}KB", extra={"stage": stage})


def convert_fp16(src: str, dst: str, logger: logging.Logger) -> None:
    """Convert FP32 ONNX to FP16."""
    stage = "convert-fp16"
    if float16 is None:
        raise RuntimeError("onnxconverter-common not installed; cannot convert to FP16")
    with StageTimer(logger, f"{stage}.float16"):
        m16 = float16.convert_float_to_float16(onnx.load(src), keep_io_types=True)
        onnx.save(m16, dst)
    size_kb = os.path.getsize(dst) / 1024
    logger.info(f"FP16 model: {size_kb:.1f}KB", extra={"stage": stage})


def quantize_dynamic_int8(src: str, dst: str, logger: logging.Logger) -> None:
    """Quantize to INT8 Dynamic (per-channel)."""
    stage = "quantize-dyn"
    with StageTimer(logger, f"{stage}.quantize_dynamic"):
        quantize_dynamic(src, dst, weight_type=QuantType.QInt8, per_channel=True)
    size_kb = os.path.getsize(dst) / 1024
    logger.info(f"INT8 Dynamic model: {size_kb:.1f}KB", extra={"stage": stage})


def quantize_static_qdq(
    src: str, dst: str, calib_data, input_name: str, logger: logging.Logger,
) -> None:
    """Quantize to INT8 Static QDQ format (recommended)."""
    stage = "quantize-qdq"
    reader = CalibReader(calib_data, input_name)
    with StageTimer(logger, f"{stage}.quantize_static_qdq"):
        quantize_static(
            src, dst, calibration_data_reader=reader,
            quant_format=QuantFormat.QDQ, per_channel=True,
            activation_type=QuantType.QInt8, weight_type=QuantType.QInt8,
            calibrate_method=CalibrationMethod.MinMax,
        )
    size_kb = os.path.getsize(dst) / 1024
    logger.info(f"INT8 Static QDQ model: {size_kb:.1f}KB", extra={"stage": stage})


def quantize_static_qop(
    src: str, dst: str, calib_data, input_name: str, logger: logging.Logger,
) -> None:
    """Quantize to INT8 Static QOperator format."""
    stage = "quantize-qop"
    reader = CalibReader(calib_data, input_name)
    with StageTimer(logger, f"{stage}.quantize_static_qop"):
        quantize_static(
            src, dst, calibration_data_reader=reader,
            quant_format=QuantFormat.QOperator, per_channel=True,
            activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8,
            calibrate_method=CalibrationMethod.MinMax,
        )
    size_kb = os.path.getsize(dst) / 1024
    logger.info(f"INT8 Static QOp model: {size_kb:.1f}KB", extra={"stage": stage})


def create_session(
    model_path: str, intra_threads: int, logger: logging.Logger,
) -> ort.InferenceSession:
    """Create ORT InferenceSession with logging."""
    stage = "session-init"
    with StageTimer(logger, f"{stage}.create_inference_session"):
        so = get_sess_options(intra_threads, logger)
        sess = ort.InferenceSession(model_path, sess_options=so, providers=['CPUExecutionProvider'])
    logger.info(
        f"Session created: providers={sess.get_providers()}",
        extra={"stage": stage},
    )
    return sess


# ---------------------------------------------------------------------------
# Main benchmark runner
# ---------------------------------------------------------------------------
def run_benchmark(args: argparse.Namespace) -> Dict[str, Any]:
    """Run full benchmark suite with structured logging."""
    logger = setup_logging(args.verbose)
    intra_threads = args.threads

    logger.info(SEP, extra={"stage": "init"})
    logger.info("COMPREHENSIVE BENCHMARK: FP32 / FP16 / INT8-Dynamic / INT8-Static-QDQ / INT8-Static-QOperator", extra={"stage": "init"})
    logger.info(
        f"ONNX Runtime: {ort.__version__} | PyTorch: {torch.__version__}",
        extra={"stage": "init"},
    )
    logger.info(
        f"Config: warmup={args.warmup}, runs={args.runs}, calib={args.calib}, "
        f"threads={intra_threads}, CPUExecutionProvider",
        extra={"stage": "init"},
    )
    logger.info(f"OMP_NUM_THREADS={os.environ.get('OMP_NUM_THREADS', 'unset')}", extra={"stage": "init"})
    logger.info(f"OPENBLAS_NUM_THREADS={os.environ.get('OPENBLAS_NUM_THREADS', 'unset')}", extra={"stage": "init"})
    logger.info(SEP, extra={"stage": "init"})
    log_mem(logger, "init", "startup")

    results: Dict[str, Any] = {}
    tmpdir = tempfile.mkdtemp(prefix="onnx-bench-")
    logger.info(f"Temp dir: {tmpdir}", extra={"stage": "init"})

    try:
        for model_name, model, dummy, inp_shape, inp_name in MODELS:
            model_stage = f"model:{model_name}"
            logger.info(f"\n{DASH}", extra={"stage": model_stage})
            logger.info(f"Model: {model_name} | input shape: {inp_shape}", extra={"stage": model_stage})
            logger.info(DASH, extra={"stage": model_stage})

            # 1. Export + simplify
            fp32_path = os.path.join(tmpdir, model_name + '_fp32.onnx')
            export_to_onnx(model, dummy, fp32_path, inp_name, logger)
            simplify_onnx(fp32_path, logger)

            # 2. Prepare calibration + test data
            with StageTimer(logger, f"{model_stage}.gen_calib_data"):
                calib_data = [np.random.randn(*inp_shape).astype(np.float32) for _ in range(args.calib)]
                test_inp = np.random.randn(*inp_shape).astype(np.float32)
            logger.info(f"Generated {args.calib} calibration samples", extra={"stage": model_stage})

            model_results: Dict[str, Any] = {'input_shape': list(inp_shape)}

            # --- FP32 baseline ---
            prec = "FP32"
            logger.info(f"--- {prec} baseline ---", extra={"stage": model_stage})
            sess_fp32 = create_session(fp32_path, intra_threads, logger)
            r = benchmark_session(sess_fp32, inp_shape, inp_name, args.warmup, args.runs, logger)
            r['size_kb'] = os.path.getsize(fp32_path) / 1024
            out_fp32 = sess_fp32.run(None, {inp_name: test_inp})[0]
            fp32_avg = r['avg_ms']
            logger.info(
                f"  FP32: avg={r['avg_ms']:.4f}ms size={r['size_kb']:.1f}KB",
                extra={"stage": model_stage},
            )
            model_results[prec] = r
            del sess_fp32
            log_mem(logger, model_stage, f"after {prec}")

            # --- FP16 ---
            prec = "FP16"
            logger.info(f"--- {prec} ---", extra={"stage": model_stage})
            fp16_path = os.path.join(tmpdir, model_name + '_fp16.onnx')
            convert_fp16(fp32_path, fp16_path, logger)
            sess = create_session(fp16_path, intra_threads, logger)
            r = benchmark_session(sess, inp_shape, inp_name, args.warmup, args.runs, logger)
            r['size_kb'] = os.path.getsize(fp16_path) / 1024
            r['max_diff'] = float(np.max(np.abs(out_fp32 - sess.run(None, {inp_name: test_inp})[0])))
            r['speedup'] = fp32_avg / r['avg_ms']
            r['size_ratio'] = r['size_kb'] / model_results['FP32']['size_kb']
            logger.info(
                f"  FP16: avg={r['avg_ms']:.4f}ms size={r['size_kb']:.1f}KB "
                f"diff={r['max_diff']:.6f} speedup={r['speedup']:.2f}x",
                extra={"stage": model_stage},
            )
            model_results[prec] = r
            del sess
            log_mem(logger, model_stage, f"after {prec}")

            # --- INT8 Dynamic ---
            prec = "INT8-Dyn"
            logger.info(f"--- {prec} ---", extra={"stage": model_stage})
            dyn_path = os.path.join(tmpdir, model_name + '_dyn.onnx')
            quantize_dynamic_int8(fp32_path, dyn_path, logger)
            sess = create_session(dyn_path, intra_threads, logger)
            r = benchmark_session(sess, inp_shape, inp_name, args.warmup, args.runs, logger)
            r['size_kb'] = os.path.getsize(dyn_path) / 1024
            r['max_diff'] = float(np.max(np.abs(out_fp32 - sess.run(None, {inp_name: test_inp})[0])))
            r['speedup'] = fp32_avg / r['avg_ms']
            r['size_ratio'] = r['size_kb'] / model_results['FP32']['size_kb']
            logger.info(
                f"  INT8 Dynamic: avg={r['avg_ms']:.4f}ms size={r['size_kb']:.1f}KB "
                f"diff={r['max_diff']:.6f} speedup={r['speedup']:.2f}x",
                extra={"stage": model_stage},
            )
            model_results[prec] = r
            del sess
            log_mem(logger, model_stage, f"after {prec}")

            # --- INT8 Static QDQ ---
            prec = "INT8-QDQ"
            logger.info(f"--- {prec} ---", extra={"stage": model_stage})
            qdq_path = os.path.join(tmpdir, model_name + '_qdq.onnx')
            quantize_static_qdq(fp32_path, qdq_path, calib_data, inp_name, logger)
            sess = create_session(qdq_path, intra_threads, logger)
            r = benchmark_session(sess, inp_shape, inp_name, args.warmup, args.runs, logger)
            r['size_kb'] = os.path.getsize(qdq_path) / 1024
            r['max_diff'] = float(np.max(np.abs(out_fp32 - sess.run(None, {inp_name: test_inp})[0])))
            r['speedup'] = fp32_avg / r['avg_ms']
            r['size_ratio'] = r['size_kb'] / model_results['FP32']['size_kb']
            logger.info(
                f"  INT8 Static QDQ: avg={r['avg_ms']:.4f}ms size={r['size_kb']:.1f}KB "
                f"diff={r['max_diff']:.6f} speedup={r['speedup']:.2f}x",
                extra={"stage": model_stage},
            )
            model_results['INT8_Static_QDQ'] = r
            del sess
            log_mem(logger, model_stage, f"after {prec}")

            # --- INT8 Static QOperator ---
            prec = "INT8-QOp"
            logger.info(f"--- {prec} ---", extra={"stage": model_stage})
            qop_path = os.path.join(tmpdir, model_name + '_qop.onnx')
            quantize_static_qop(fp32_path, qop_path, calib_data, inp_name, logger)
            sess = create_session(qop_path, intra_threads, logger)
            r = benchmark_session(sess, inp_shape, inp_name, args.warmup, args.runs, logger)
            r['size_kb'] = os.path.getsize(qop_path) / 1024
            r['max_diff'] = float(np.max(np.abs(out_fp32 - sess.run(None, {inp_name: test_inp})[0])))
            r['speedup'] = fp32_avg / r['avg_ms']
            r['size_ratio'] = r['size_kb'] / model_results['FP32']['size_kb']
            logger.info(
                f"  INT8 Static QOp: avg={r['avg_ms']:.4f}ms size={r['size_kb']:.1f}KB "
                f"diff={r['max_diff']:.6f} speedup={r['speedup']:.2f}x",
                extra={"stage": model_stage},
            )
            model_results['INT8_Static_QOperator'] = r
            del sess
            log_mem(logger, model_stage, f"after {prec}")

            # QDQ vs QOp comparison
            qdq_avg = model_results['INT8_Static_QDQ']['avg_ms']
            qop_avg = model_results['INT8_Static_QOperator']['avg_ms']
            qdq_vs_qop = qdq_avg / qop_avg
            winner = "QDQ" if qdq_avg < qop_avg else "QOperator"
            logger.info(
                f"  >> QDQ vs QOp ratio: {qdq_vs_qop:.3f}x (winner: {winner})",
                extra={"stage": model_stage},
            )
            results[model_name] = model_results
            log_mem(logger, model_stage, "model complete")

        # Save results
        out_path = args.output
        output_data = {
            'results': results,
            'config': {
                'warmup': args.warmup,
                'runs': args.runs,
                'calib_samples': args.calib,
                'intra_threads': intra_threads,
                'ort_version': ort.__version__,
                'torch_version': torch.__version__,
                'providers': ['CPUExecutionProvider'],
                'omp_num_threads': os.environ.get('OMP_NUM_THREADS'),
                'openblas_num_threads': os.environ.get('OPENBLAS_NUM_THREADS'),
            }
        }
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Results saved to {out_path}", extra={"stage": "save"})

        # Print summary table
        print(f'\n{SEP}')
        print('SUMMARY')
        print(SEP)
        print(f'{"Model":<28} {"FP32":>8} {"FP16":>8} {"INT8-Dyn":>8} {"INT8-QDQ":>9} {"INT8-QOp":>9} | {"Best Speedup":>12}')
        print('-' * 100)
        for name, data in results.items():
            fp32 = data['FP32']['avg_ms']
            speeds = {
                'FP16': data['FP16']['speedup'],
                'INT8-Dyn': data['INT8-Dyn']['speedup'],
                'INT8-QDQ': data['INT8_Static_QDQ']['speedup'],
                'INT8-QOp': data['INT8_Static_QOperator']['speedup'],
            }
            best = max(speeds.items(), key=lambda x: x[1])
            print(f'{name:<28} {fp32:>7.3f}m {data["FP16"]["avg_ms"]:>7.3f}m {data["INT8-Dyn"]["avg_ms"]:>7.3f}m '
                  f'{data["INT8_Static_QDQ"]["avg_ms"]:>8.3f}m {data["INT8_Static_QOperator"]["avg_ms"]:>8.3f}m | {best[0]:>9}: {best[1]:.2f}x')
        print(f'\nResults saved to {out_path}')
        return output_data

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
        logger.info(f"Cleaned up temp dir: {tmpdir}", extra={"stage": "cleanup"})


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="ONNX Quantization Benchmark (FP32/FP16/INT8 variants)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('-w', '--warmup', type=int, default=WARMUP, help='Warmup iterations')
    parser.add_argument('-r', '--runs', type=int, default=RUNS, help='Timed benchmark iterations')
    parser.add_argument('-c', '--calib', type=int, default=CALIB_SAMPLES, help='Calibration samples for static quantization')
    parser.add_argument('-t', '--threads', type=int, default=4, help='OR intra-op threads')
    parser.add_argument('-o', '--output', type=str, default=str(Path(tempfile.gettempdir()) / 'benchmark_results.json'), help='Results JSON output path')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable debug logging')
    return parser.parse_args()


if __name__ == '__main__':
    run_benchmark(parse_args())
