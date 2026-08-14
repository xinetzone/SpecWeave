#!/usr/bin/env python3
"""
QDQ vs QOperator 量化格式自动对比脚本

功能: 对任意ONNX模型自动进行QDQ和QOperator两种格式的静态INT8量化，
对比推理延迟(P50/P95/P99)、吞吐量、精度损失、模型大小，输出结构化报告。

用法:
  python compare_qdq_vs_qoperator.py --model model.onnx --input-shape 1,3,224,224
  python compare_qdq_vs_qoperator.py --model model.onnx --input-name input --calib-dir ./calib_data/
  python compare_qdq_vs_qoperator.py --model model.onnx --output report.json --warmup 100 --runs 1000

验证环境: ONNX Runtime 1.28.0, Python 3.14.6
"""
import argparse
import json
import os
import sys
import time
import tempfile
import shutil
from pathlib import Path

import numpy as np
import onnx
import onnxsim
import onnxruntime as ort
from onnxruntime.quantization import (
    quantize_static,
    CalibrationDataReader,
    QuantType,
    QuantFormat,
    CalibrationMethod,
)


class FileCalibrationReader(CalibrationDataReader):
    """从目录加载校准数据(numpy .npy文件)或生成随机数据"""
    def __init__(self, input_name: str, input_shape: tuple,
                 calib_dir: str = None, num_samples: int = 100,
                 preprocess_fn=None):
        self.input_name = input_name
        self.input_shape = input_shape
        self.num_samples = num_samples
        self.idx = 0

        if calib_dir and os.path.isdir(calib_dir):
            self.data = []
            npy_files = sorted(Path(calib_dir).glob("*.npy"))[:num_samples]
            if npy_files:
                for f in npy_files:
                    arr = np.load(str(f)).astype(np.float32)
                    if preprocess_fn:
                        arr = preprocess_fn(arr)
                    self.data.append({input_name: arr})
            else:
                print(f"[WARN] No .npy files found in {calib_dir}, using random data")
                self._gen_random()
        else:
            self._gen_random()

    def _gen_random(self):
        self.data = [
            {self.input_name: np.random.randn(*self.input_shape).astype(np.float32)}
            for _ in range(self.num_samples)
        ]

    def get_next(self):
        if self.idx >= len(self.data):
            return None
        d = self.data[self.idx]
        self.idx += 1
        return d

    def rewind(self):
        self.idx = 0


def benchmark_session(
    sess: ort.InferenceSession,
    input_name: str,
    input_shape: tuple,
    warmup: int = 100,
    runs: int = 500,
) -> dict:
    """基准测试单个Session的推理性能"""
    dummy = np.random.randn(*input_shape).astype(np.float32)
    for _ in range(warmup):
        sess.run(None, {input_name: dummy})

    times = []
    for _ in range(runs):
        inp = np.random.randn(*input_shape).astype(np.float32)
        t0 = time.perf_counter()
        sess.run(None, {input_name: inp})
        times.append(time.perf_counter() - t0)

    t = np.array(times) * 1000  # ms
    return {
        "avg_ms": float(np.mean(t)),
        "p50_ms": float(np.median(t)),
        "p95_ms": float(np.percentile(t, 95)),
        "p99_ms": float(np.percentile(t, 99)),
        "min_ms": float(np.min(t)),
        "max_ms": float(np.max(t)),
        "std_ms": float(np.std(t)),
        "throughput_fps": float(1000.0 / np.mean(t) * input_shape[0]),
    }


def measure_accuracy(
    sess_fp32: ort.InferenceSession,
    sess_quant: ort.InferenceSession,
    input_name: str,
    input_shape: tuple,
    num_tests: int = 100,
) -> dict:
    """测量量化模型相对FP32的精度损失"""
    max_diffs = []
    cos_sims = []
    for _ in range(num_tests):
        inp = np.random.randn(*input_shape).astype(np.float32)
        out_fp32 = sess_fp32.run(None, {input_name: inp})[0]
        out_q = sess_quant.run(None, {input_name: inp})[0]
        max_diffs.append(float(np.max(np.abs(out_fp32 - out_q))))
        fp32_flat = out_fp32.flatten()
        q_flat = out_q.flatten()
        cos_sim = float(np.dot(fp32_flat, q_flat) /
                        (np.linalg.norm(fp32_flat) * np.linalg.norm(q_flat) + 1e-10))
        cos_sims.append(cos_sim)

    return {
        "max_diff": float(np.max(max_diffs)),
        "mean_diff": float(np.mean(max_diffs)),
        "p95_diff": float(np.percentile(max_diffs, 95)),
        "cosine_similarity_mean": float(np.mean(cos_sims)),
        "cosine_similarity_min": float(np.min(cos_sims)),
    }


def quantize_and_benchmark(
    model_path: str,
    output_path: str,
    quant_format: QuantFormat,
    calib_reader: CalibrationDataReader,
    input_name: str,
    input_shape: tuple,
    per_channel: bool = True,
    activation_type: QuantType = QuantType.QInt8,
    weight_type: QuantType = QuantType.QInt8,
    calibrate_method: CalibrationMethod = CalibrationMethod.MinMax,
    intra_threads: int = 4,
    warmup: int = 100,
    runs: int = 500,
    sess_fp32=None,
) -> dict:
    """量化模型并执行性能/精度基准测试"""
    calib_reader.rewind()

    try:
        quantize_static(
            model_input=model_path,
            model_output=output_path,
            calibration_data_reader=calib_reader,
            quant_format=quant_format,
            per_channel=per_channel,
            activation_type=activation_type,
            weight_type=weight_type,
            calibrate_method=calibrate_method,
        )
    except Exception as e:
        return {"error": str(e), "success": False}

    size_kb = os.path.getsize(output_path) / 1024

    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    so.intra_op_num_threads = intra_threads
    so.inter_op_num_threads = 1
    so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

    sess = ort.InferenceSession(output_path, sess_options=so,
                                providers=["CPUExecutionProvider"])
    perf = benchmark_session(sess, input_name, input_shape, warmup, runs)
    perf["size_kb"] = size_kb

    if sess_fp32 is not None:
        acc = measure_accuracy(sess_fp32, sess, input_name, input_shape)
        perf["accuracy"] = acc

    perf["success"] = True
    return perf


def compare_qdq_vs_qoperator(args):
    """主对比流程"""
    print("=" * 70)
    print("QDQ vs QOperator 量化格式对比工具")
    print(f"模型: {args.model}")
    print(f"输入形状: {args.input_shape}")
    print(f"线程数: {args.threads}, warmup: {args.warmup}, runs: {args.runs}")
    print("=" * 70)

    # 加载并简化模型
    model = onnx.load(args.model)
    model_simp, check = onnxsim.simplify(model)
    if not check:
        print("[ERROR] Model simplification failed", file=sys.stderr)
        return 1

    tmpdir = tempfile.mkdtemp()
    simp_path = os.path.join(tmpdir, "model_simplified.onnx")
    onnx.save(model_simp, simp_path)

    # 获取输入信息
    input_shape = tuple(int(x) for x in args.input_shape.split(","))
    if args.input_name:
        input_name = args.input_name
    else:
        sess_tmp = ort.InferenceSession(simp_path, providers=["CPUExecutionProvider"])
        input_name = sess_tmp.get_inputs()[0].name
        del sess_tmp

    # FP32基准
    so_fp32 = ort.SessionOptions()
    so_fp32.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    so_fp32.intra_op_num_threads = args.threads
    so_fp32.inter_op_num_threads = 1
    sess_fp32 = ort.InferenceSession(simp_path, sess_options=so_fp32,
                                     providers=["CPUExecutionProvider"])

    print("\n[1/3] 测试 FP32 基准性能...")
    fp32_perf = benchmark_session(sess_fp32, input_name, input_shape, args.warmup, args.runs)
    fp32_perf["size_kb"] = os.path.getsize(simp_path) / 1024
    fp32_perf["success"] = True
    print(f"  FP32: avg={fp32_perf['avg_ms']:.4f}ms, "
          f"p50={fp32_perf['p50_ms']:.4f}ms, "
          f"p95={fp32_perf['p95_ms']:.4f}ms, "
          f"size={fp32_perf['size_kb']:.1f}KB")

    # 校准数据
    calib_reader = FileCalibrationReader(
        input_name=input_name,
        input_shape=input_shape,
        calib_dir=args.calib_dir,
        num_samples=args.calib_samples,
    )

    # QDQ格式
    print("\n[2/3] 测试 QDQ 格式 (QuantFormat.QDQ, QInt8/QInt8)...")
    qdq_path = os.path.join(tmpdir, "model_qdq.onnx")
    calib_reader.rewind()
    qdq_perf = quantize_and_benchmark(
        simp_path, qdq_path, QuantFormat.QDQ, calib_reader,
        input_name, input_shape,
        per_channel=True,
        activation_type=QuantType.QInt8,
        weight_type=QuantType.QInt8,
        calibrate_method=CalibrationMethod.MinMax,
        intra_threads=args.threads,
        warmup=args.warmup,
        runs=args.runs,
        sess_fp32=sess_fp32,
    )
    if qdq_perf.get("success"):
        acc = qdq_perf.get("accuracy", {})
        print(f"  QDQ:  avg={qdq_perf['avg_ms']:.4f}ms, "
              f"p50={qdq_perf['p50_ms']:.4f}ms, "
              f"p95={qdq_perf['p95_ms']:.4f}ms, "
              f"size={qdq_perf['size_kb']:.1f}KB, "
              f"speedup={fp32_perf['avg_ms']/qdq_perf['avg_ms']:.2f}x"
              f", max_diff={acc.get('max_diff', 'N/A')}")
    else:
        print(f"  QDQ: FAILED - {qdq_perf.get('error')}")

    # QOperator格式 - 分别测试两种激活类型组合
    print("\n[3/3] 测试 QOperator 格式...")
    results_qop = {}
    for act_type_name, act_type in [("QInt8/QInt8", QuantType.QInt8),
                                     ("QUInt8/QInt8", QuantType.QUInt8)]:
        qop_path = os.path.join(tmpdir, f"model_qop_{act_type_name.replace('/', '_')}.onnx")
        calib_reader.rewind()
        perf = quantize_and_benchmark(
            simp_path, qop_path, QuantFormat.QOperator, calib_reader,
            input_name, input_shape,
            per_channel=True,
            activation_type=act_type,
            weight_type=QuantType.QInt8,
            calibrate_method=CalibrationMethod.MinMax,
            intra_threads=args.threads,
            warmup=args.warmup,
            runs=args.runs,
            sess_fp32=sess_fp32,
        )
        results_qop[act_type_name] = perf
        if perf.get("success"):
            acc = perf.get("accuracy", {})
            print(f"  QOp ({act_type_name}): avg={perf['avg_ms']:.4f}ms, "
                  f"p50={perf['p50_ms']:.4f}ms, "
                  f"p95={perf['p95_ms']:.4f}ms, "
                  f"size={perf['size_kb']:.1f}KB, "
                  f"speedup={fp32_perf['avg_ms']/perf['avg_ms']:.2f}x"
                  f", max_diff={acc.get('max_diff', 'N/A')}")
        else:
            print(f"  QOp ({act_type_name}): FAILED - {perf.get('error')}")

    # 对比报告
    print("\n" + "=" * 70)
    print("对比报告")
    print("=" * 70)

    def fmt_row(name, perf, fp32_avg):
        if not perf.get("success"):
            return f"  {name:25s}: FAILED"
        sp = fp32_avg / perf["avg_ms"]
        acc = perf.get("accuracy", {})
        md = acc.get("max_diff", -1)
        return (f"  {name:25s}: avg={perf['avg_ms']:.4f}ms  "
                f"p50={perf['p50_ms']:.4f}ms  "
                f"p95={perf['p95_ms']:.4f}ms  "
                f"size={perf['size_kb']:.1f}KB  "
                f"speedup={sp:.2f}x  "
                f"max_diff={md:.6f}")

    print(fmt_row("FP32 (baseline)", fp32_perf, fp32_perf["avg_ms"]))
    print(fmt_row("QDQ (QInt8/QInt8)", qdq_perf, fp32_perf["avg_ms"]))
    for name, perf in results_qop.items():
        print(fmt_row(f"QOperator ({name})", perf, fp32_perf["avg_ms"]))

    # 判定winner
    all_quant = {"QDQ": qdq_perf}
    all_quant.update({f"QOp_{k.replace('/', '_')}": v for k, v in results_qop.items()})
    valid = {k: v for k, v in all_quant.items() if v.get("success")}
    if valid:
        winner = min(valid.items(), key=lambda x: x[1]["avg_ms"])
        print(f"\n  >>> 性能冠军: {winner[0]} (avg={winner[1]['avg_ms']:.4f}ms)")
        qdq_avg = qdq_perf.get("avg_ms", float("inf"))
        for name, perf in valid.items():
            if name != "QDQ" and perf.get("success"):
                ratio = qdq_avg / perf["avg_ms"]
                if ratio > 1:
                    # qdq_avg > qop_avg → QDQ is slower
                    print(f"      QDQ is {ratio*100-100:.1f}% SLOWER than {name}")
                else:
                    # qdq_avg < qop_avg → QDQ is faster
                    print(f"      QDQ is {(1/ratio)*100-100:.1f}% FASTER than {name}")

    # 输出JSON
    report = {
        "model": os.path.basename(args.model),
        "input_shape": list(input_shape),
        "input_name": input_name,
        "config": {
            "threads": args.threads,
            "warmup": args.warmup,
            "runs": args.runs,
            "calib_samples": args.calib_samples,
            "ort_version": ort.__version__,
        },
        "fp32": fp32_perf,
        "qdq_qint8_qint8": qdq_perf,
        "qoperator": results_qop,
        "winner": winner[0] if valid else None,
    }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n报告已保存至: {args.output}")

    # 清理
    shutil.rmtree(tmpdir, ignore_errors=True)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="QDQ vs QOperator 量化格式自动对比工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法（随机校准数据）
  python compare_qdq_vs_qoperator.py -m model.onnx -s 1,3,224,224

  # 指定输入名称和校准数据目录
  python compare_qdq_vs_qoperator.py -m model.onnx -s 1,3,224,224 -n input -d ./calib/

  # 完整参数
  python compare_qdq_vs_qoperator.py -m model.onnx -s 1,1024 -w 200 -r 1000 -t 8 -o report.json
        """
    )
    parser.add_argument("-m", "--model", required=True, help="ONNX模型路径")
    parser.add_argument("-s", "--input-shape", required=True,
                        help="输入形状, 逗号分隔 (如 1,3,224,224)")
    parser.add_argument("-n", "--input-name", default=None,
                        help="输入节点名称 (默认自动检测)")
    parser.add_argument("-d", "--calib-dir", default=None,
                        help="校准数据目录(.npy文件), 不指定则用随机数据")
    parser.add_argument("-c", "--calib-samples", type=int, default=100,
                        help="校准样本数 (默认100)")
    parser.add_argument("-w", "--warmup", type=int, default=100,
                        help="预热次数 (默认100)")
    parser.add_argument("-r", "--runs", type=int, default=500,
                        help="正式测量次数 (默认500)")
    parser.add_argument("-t", "--threads", type=int, default=4,
                        help="intra_op线程数 (默认4)")
    parser.add_argument("-o", "--output", default=None,
                        help="JSON报告输出路径")

    args = parser.parse_args()

    if not os.path.isfile(args.model):
        print(f"[ERROR] Model not found: {args.model}", file=sys.stderr)
        return 1

    return compare_qdq_vs_qoperator(args)


if __name__ == "__main__":
    sys.exit(main())
