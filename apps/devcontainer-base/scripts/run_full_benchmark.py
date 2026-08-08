#!/usr/bin/env python3
"""Comprehensive benchmark: FP32/FP16/INT8-Dynamic/INT8-Static-QDQ/INT8-Static-QOperator across 4 model types."""
import json, time, tempfile, os, shutil
import numpy as np
import onnx, onnxsim
import onnxruntime as ort
from onnxruntime.quantization import (quantize_dynamic, quantize_static,
    CalibrationDataReader, QuantType, QuantFormat, CalibrationMethod)
import torch, torch.nn as nn

WARMUP, RUNS, THREADS = 50, 300, 4

class CalibReader(CalibrationDataReader):
    def __init__(self, name, shape, n=100):
        self.name = name
        self.data = [{name: np.random.randn(*shape).astype(np.float32)} for _ in range(n)]
        self.i = 0
    def get_next(self):
        if self.i >= len(self.data): return None
        d = self.data[self.i]; self.i += 1; return d
    def rewind(self): self.i = 0

def bench(sess, name, shape):
    inp_info = sess.get_inputs()[0]
    is_fp16 = 'float16' in str(inp_info.type)
    dtype = np.float16 if is_fp16 else np.float32
    def make_input():
        return np.random.randn(*shape).astype(dtype)
    for _ in range(WARMUP):
        sess.run(None, {name: make_input()})
    ts = []
    for _ in range(RUNS):
        x = make_input()
        t0 = time.perf_counter(); sess.run(None, {name: x}); ts.append(time.perf_counter()-t0)
    t = np.array(ts)*1000
    return {
        'avg_ms': float(np.mean(t)),'p50_ms': float(np.median(t)),
        'p95_ms': float(np.percentile(t,95)),'p99_ms': float(np.percentile(t,99)),
        'min_ms': float(np.min(t)),'std_ms': float(np.std(t)),
        'throughput_fps': float(1000.0/np.mean(t)*shape[0]),
    }

def make_sess(path, th=THREADS):
    so = ort.SessionOptions()
    so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    so.intra_op_num_threads = th; so.inter_op_num_threads = 1
    so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
    return ort.InferenceSession(path, sess_options=so, providers=['CPUExecutionProvider'])

def make_onnx(model, name, shape, out_path):
    dummy = torch.randn(*shape)
    torch.onnx.export(model, dummy, out_path, input_names=[name], output_names=['output'],
                      opset_version=18, do_constant_folding=True)
    m = onnx.load(out_path); ms, ok = onnxsim.simplify(m); assert ok
    onnx.save(ms, out_path); return out_path

def quant_fp16(src, dst):
    from onnxconverter_common import float16
    m = onnx.load(src); m16 = float16.convert_float_to_float16(m); onnx.save(m16, dst)

class TrWrap(nn.Module):
    def __init__(self, net):
        super().__init__(); self.net = net
    def forward(self, x):
        b = x.size(0); x = self.net[0](x); x = x.view(b, 16, -1)
        x = self.net[1](x); x = self.net[2](x); x = self.net[3](x)
        x = x.mean(dim=1); return self.net[4](x)

def test_model(name, model, shape, iname='input'):
    print(f'=== {name} ===', flush=True)
    td = tempfile.mkdtemp()
    fp32p = f'{td}/fp32.onnx'; make_onnx(model, iname, shape, fp32p)
    fp16p = f'{td}/fp16.onnx'; quant_fp16(fp32p, fp16p)
    dyn_p = f'{td}/dyn.onnx'; quantize_dynamic(fp32p, dyn_p, weight_type=QuantType.QInt8)
    qdq_p = f'{td}/qdq.onnx'
    cr = CalibReader(iname, shape); cr.rewind()
    quantize_static(fp32p, qdq_p, cr, quant_format=QuantFormat.QDQ, per_channel=True,
                    activation_type=QuantType.QInt8, weight_type=QuantType.QInt8,
                    calibrate_method=CalibrationMethod.MinMax)
    qop_p = f'{td}/qop.onnx'
    cr2 = CalibReader(iname, shape); cr2.rewind()
    quantize_static(fp32p, qop_p, cr2, quant_format=QuantFormat.QOperator, per_channel=True,
                    activation_type=QuantType.QUInt8, weight_type=QuantType.QInt8,
                    calibrate_method=CalibrationMethod.MinMax)
    r = {}
    for label, path in [('FP32',fp32p),('FP16',fp16p),('INT8_Dynamic',dyn_p),
                        ('INT8_Static_QDQ',qdq_p),('INT8_Static_QOperator',qop_p)]:
        try:
            s = make_sess(path); p = bench(s, iname, shape)
            p['size_kb'] = os.path.getsize(path)/1024
            # accuracy
            s32 = make_sess(fp32p)
            diffs = []
            inp_info = s.get_inputs()[0]
            is_fp16 = 'float16' in str(inp_info.type)
            for _ in range(50):
                x32 = np.random.randn(*shape).astype(np.float32)
                o32 = s32.run(None,{iname:x32})[0]
                xq = x32.astype(np.float16) if is_fp16 else x32
                oq = s.run(None,{iname:xq})[0]
                diffs.append(float(np.max(np.abs(o32.astype(np.float32) - oq.astype(np.float32)))))
            p['max_diff'] = float(np.max(diffs)); p['error'] = None
        except Exception as e:
            p = {'error': str(e), 'size_kb': os.path.getsize(path)/1024 if os.path.exists(path) else 0}
        r[label] = p
    fp32_avg = r['FP32'].get('avg_ms', 1.0); fp32_size = r['FP32']['size_kb']
    for k,v in r.items():
        if 'avg_ms' in v and v.get('error') is None:
            v['speedup'] = fp32_avg/v['avg_ms'] if k!='FP32' else 1.0
        else:
            v['speedup'] = 0.0
        v['size_ratio'] = v['size_kb']/fp32_size
    shutil.rmtree(td, ignore_errors=True)
    return r

if __name__ == '__main__':
    models = {
        'SmallMLP(128->10)': (nn.Sequential(nn.Linear(128,256),nn.ReLU(),nn.Linear(256,10)), (1,128)),
        'LargeMLP(1024->100)': (nn.Sequential(nn.Linear(1024,2048),nn.ReLU(),nn.Linear(2048,1024),nn.ReLU(),nn.Linear(1024,100)), (1,1024)),
        'ConvNet(CIFAR-10)': (nn.Sequential(nn.Conv2d(3,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(32,64,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Flatten(),nn.Linear(64*8*8,256),nn.ReLU(),nn.Linear(256,10)), (1,3,32,32)),
        'Transformer(3L-256d)': (TrWrap(nn.Sequential(nn.Linear(128,256),nn.TransformerEncoderLayer(d_model=256,nhead=4,dim_feedforward=512,dropout=0.0,batch_first=True),nn.TransformerEncoderLayer(d_model=256,nhead=4,dim_feedforward=512,dropout=0.0,batch_first=True),nn.TransformerEncoderLayer(d_model=256,nhead=4,dim_feedforward=512,dropout=0.0,batch_first=True),nn.Linear(256,10))), (1,16,128)),
    }
    results = {}
    for name, (model, shape) in models.items():
        model.eval()
        results[name] = test_model(name, model, shape)
    report = {
        'config': {'warmup':WARMUP,'runs':RUNS,'intra_threads':THREADS,
                   'ort_version':ort.__version__,'device':'x64_CPU_Intel_i9-14900K'},
        'results': results
    }
    out = '/tmp/benchmark-results.json'
    with open(out, 'w') as f: json.dump(report, f, indent=2)
    print(f'\nDONE. Results saved to {out}')
    for name, r in results.items():
        print(f'{name}:')
        for k,v in r.items():
            if v.get('error'):
                print(f'  {k:25s}: ERROR - {v["error"][:80]}')
            else:
                print(f'  {k:25s}: avg={v["avg_ms"]:.4f}ms  speedup={v["speedup"]:.2f}x  size_ratio={v["size_ratio"]:.3f}  max_diff={v.get("max_diff",-1):.6f}')
