#!/usr/bin/env python3
"""Comprehensive benchmark: FP32/FP16/INT8-Dynamic/INT8-QDQ/INT8-QOperator on x64 CPU"""
import json, time, os, shutil, tempfile
import numpy as np
import torch
import onnx
import onnxsim
import onnxruntime as ort
from onnxruntime.quantization import (
    quantize_dynamic, quantize_static, CalibrationDataReader,
    QuantType, QuantFormat, CalibrationMethod
)
from onnxconverter_common import float16

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

def benchmark_session(sess, input_shape, input_name, warmup=WARMUP, runs=RUNS):
    inp = np.random.randn(*input_shape).astype(np.float32)
    for _ in range(warmup):
        sess.run(None, {input_name: inp})
    times = []
    for _ in range(runs):
        inp = np.random.randn(*input_shape).astype(np.float32)
        t0 = time.perf_counter()
        sess.run(None, {input_name: inp})
        times.append(time.perf_counter() - t0)
    t = np.array(times) * 1000
    return {
        'avg_ms': float(np.mean(t)),
        'p50_ms': float(np.median(t)),
        'p95_ms': float(np.percentile(t, 95)),
        'p99_ms': float(np.percentile(t, 99)),
        'min_ms': float(np.min(t)),
        'std_ms': float(np.std(t)),
    }

def get_sess_options(intra_threads=4):
    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    so.intra_op_num_threads = intra_threads
    so.inter_op_num_threads = 1
    so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return so

print(SEP)
print('COMPREHENSIVE BENCHMARK: FP32 / FP16 / INT8-Dynamic / INT8-Static-QDQ / INT8-Static-QOperator')
print(f'ONNX Runtime: {ort.__version__} | PyTorch: {torch.__version__}')
print(f'Config: warmup={WARMUP}, runs={RUNS}, calib={CALIB_SAMPLES}, threads=4, CPUExecutionProvider')
print(SEP)

results = {}
tmpdir = tempfile.mkdtemp()

for model_name, model, dummy, inp_shape, inp_name in MODELS:
    print(f'\n{DASH}')
    print(f'Model: {model_name} | input shape: {inp_shape}')
    print(DASH)
    model.eval()

    fp32_path = os.path.join(tmpdir, model_name + '_fp32.onnx')
    torch.onnx.export(model, dummy, fp32_path,
                      input_names=[inp_name], output_names=['output'],
                      opset_version=18, do_constant_folding=True)
    m = onnx.load(fp32_path)
    m_simp, ok = onnxsim.simplify(m)
    assert ok
    onnx.save(m_simp, fp32_path)

    calib_data = [np.random.randn(*inp_shape).astype(np.float32) for _ in range(CALIB_SAMPLES)]
    test_inp = np.random.randn(*inp_shape).astype(np.float32)

    # FP32
    so = get_sess_options()
    sess_fp32 = ort.InferenceSession(fp32_path, sess_options=so, providers=['CPUExecutionProvider'])
    r = benchmark_session(sess_fp32, inp_shape, inp_name)
    r['size_kb'] = os.path.getsize(fp32_path) / 1024
    out_fp32 = sess_fp32.run(None, {inp_name: test_inp})[0]
    fp32_avg = r['avg_ms']
    print(f'  FP32:              avg={r["avg_ms"]:.4f}ms  p50={r["p50_ms"]:.4f}ms  p95={r["p95_ms"]:.4f}ms  size={r["size_kb"]:.1f}KB')
    fp32_r = r

    # FP16
    fp16_path = os.path.join(tmpdir, model_name + '_fp16.onnx')
    m16 = float16.convert_float_to_float16(onnx.load(fp32_path), keep_io_types=True)
    onnx.save(m16, fp16_path)
    so = get_sess_options()
    sess = ort.InferenceSession(fp16_path, sess_options=so, providers=['CPUExecutionProvider'])
    r = benchmark_session(sess, inp_shape, inp_name)
    r['size_kb'] = os.path.getsize(fp16_path) / 1024
    r['max_diff'] = float(np.max(np.abs(out_fp32 - sess.run(None, {inp_name: test_inp})[0])))
    r['speedup'] = fp32_avg / r['avg_ms']
    r['size_ratio'] = r['size_kb'] / fp32_r['size_kb']
    print(f'  FP16:              avg={r["avg_ms"]:.4f}ms  p50={r["p50_ms"]:.4f}ms  p95={r["p95_ms"]:.4f}ms  size={r["size_kb"]:.1f}KB  diff={r["max_diff"]:.6f}  speedup={r["speedup"]:.2f}x')
    fp16_r = r

    # INT8 Dynamic
    dyn_path = os.path.join(tmpdir, model_name + '_dyn.onnx')
    quantize_dynamic(fp32_path, dyn_path, weight_type=QuantType.QInt8, per_channel=True)
    so = get_sess_options()
    sess = ort.InferenceSession(dyn_path, sess_options=so, providers=['CPUExecutionProvider'])
    r = benchmark_session(sess, inp_shape, inp_name)
    r['size_kb'] = os.path.getsize(dyn_path) / 1024
    r['max_diff'] = float(np.max(np.abs(out_fp32 - sess.run(None, {inp_name: test_inp})[0])))
    r['speedup'] = fp32_avg / r['avg_ms']
    r['size_ratio'] = r['size_kb'] / fp32_r['size_kb']
    print(f'  INT8 Dynamic:      avg={r["avg_ms"]:.4f}ms  p50={r["p50_ms"]:.4f}ms  p95={r["p95_ms"]:.4f}ms  size={r["size_kb"]:.1f}KB  diff={r["max_diff"]:.6f}  speedup={r["speedup"]:.2f}x')
    dyn_r = r

    # INT8 Static QDQ (QInt8/QInt8 - recommended)
    qdq_path = os.path.join(tmpdir, model_name + '_qdq.onnx')
    reader = CalibReader(calib_data, inp_name)
    quantize_static(fp32_path, qdq_path, calibration_data_reader=reader,
                    quant_format=QuantFormat.QDQ, per_channel=True,
                    activation_type=QuantType.QInt8, weight_type=QuantType.QInt8,
                    calibrate_method=CalibrationMethod.MinMax)
    so = get_sess_options()
    sess = ort.InferenceSession(qdq_path, sess_options=so, providers=['CPUExecutionProvider'])
    r = benchmark_session(sess, inp_shape, inp_name)
    r['size_kb'] = os.path.getsize(qdq_path) / 1024
    r['max_diff'] = float(np.max(np.abs(out_fp32 - sess.run(None, {inp_name: test_inp})[0])))
    r['speedup'] = fp32_avg / r['avg_ms']
    r['size_ratio'] = r['size_kb'] / fp32_r['size_kb']
    print(f'  INT8 Static QDQ:   avg={r["avg_ms"]:.4f}ms  p50={r["p50_ms"]:.4f}ms  p95={r["p95_ms"]:.4f}ms  size={r["size_kb"]:.1f}KB  diff={r["max_diff"]:.6f}  speedup={r["speedup"]:.2f}x')
    qdq_r = r

    # INT8 Static QOperator (QUInt8 activations - better for QOperator)
    qop_path = os.path.join(tmpdir, model_name + '_qop.onnx')
    reader = CalibReader(calib_data, inp_name)
    quantize_static(fp32_path, qop_path, calibration_data_reader=reader,
                    quant_format=QuantFormat.QOperator, per_channel=True,
                    activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8,
                    calibrate_method=CalibrationMethod.MinMax)
    so = get_sess_options()
    sess = ort.InferenceSession(qop_path, sess_options=so, providers=['CPUExecutionProvider'])
    r = benchmark_session(sess, inp_shape, inp_name)
    r['size_kb'] = os.path.getsize(qop_path) / 1024
    r['max_diff'] = float(np.max(np.abs(out_fp32 - sess.run(None, {inp_name: test_inp})[0])))
    r['speedup'] = fp32_avg / r['avg_ms']
    r['size_ratio'] = r['size_kb'] / fp32_r['size_kb']
    print(f'  INT8 Static QOp:   avg={r["avg_ms"]:.4f}ms  p50={r["p50_ms"]:.4f}ms  p95={r["p95_ms"]:.4f}ms  size={r["size_kb"]:.1f}KB  diff={r["max_diff"]:.6f}  speedup={r["speedup"]:.2f}x')
    qop_r = r

    # QDQ vs QOp direct comparison
    qdq_vs_qop = qdq_r['avg_ms'] / qop_r['avg_ms']
    winner = "QDQ" if qdq_r['avg_ms'] < qop_r['avg_ms'] else "QOperator"
    print(f'  >> QDQ vs QOp ratio: {qdq_vs_qop:.3f}x (winner: {winner})')

    results[model_name] = {
        'input_shape': list(inp_shape),
        'FP32': fp32_r,
        'FP16': fp16_r,
        'INT8_Dynamic': dyn_r,
        'INT8_Static_QDQ': qdq_r,
        'INT8_Static_QOperator': qop_r,
    }

# Save
out_path = '/tmp/benchmark_results.json'
with open(out_path, 'w') as f:
    json.dump({
        'results': results,
        'config': {
            'warmup': WARMUP, 'runs': RUNS, 'calib_samples': CALIB_SAMPLES,
            'intra_threads': 4, 'ort_version': ort.__version__,
            'torch_version': torch.__version__,
            'providers': ['CPUExecutionProvider'],
        }
    }, f, indent=2)

print(f'\n{SEP}')
print(f'SUMMARY')
print(SEP)
print(f'{"Model":<28} {"FP32":>8} {"FP16":>8} {"INT8-Dyn":>8} {"INT8-QDQ":>9} {"INT8-QOp":>9} | {"Best Speedup":>12}')
print('-' * 100)
for name, data in results.items():
    fp32 = data['FP32']['avg_ms']
    speeds = {
        'FP16': data['FP16']['speedup'],
        'INT8-Dyn': data['INT8_Dynamic']['speedup'],
        'INT8-QDQ': data['INT8_Static_QDQ']['speedup'],
        'INT8-QOp': data['INT8_Static_QOperator']['speedup'],
    }
    best = max(speeds.items(), key=lambda x: x[1])
    print(f'{name:<28} {fp32:>7.3f}m {data["FP16"]["avg_ms"]:>7.3f}m {data["INT8_Dynamic"]["avg_ms"]:>7.3f}m '
          f'{data["INT8_Static_QDQ"]["avg_ms"]:>8.3f}m {data["INT8_Static_QOperator"]["avg_ms"]:>8.3f}m | {best[0]:>9}: {best[1]:.2f}x')
print(f'\nResults saved to {out_path}')
shutil.rmtree(tmpdir, ignore_errors=True)
