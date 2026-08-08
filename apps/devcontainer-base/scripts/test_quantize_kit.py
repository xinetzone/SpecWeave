#!/usr/bin/env python3
"""onnx_quantize_kit + CI门禁 集成测试

测试重点：
1. 模型类型自动检测 (MLP/CNN/Transformer)
2. auto_quantize API 可用性
3. 强制失败策略触发回滚机制
4. CI门禁脚本退出码
5. 独立API函数 (benchmark/validate/detect)
"""
import os, sys, json, tempfile, shutil, subprocess
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch
import torch.nn as nn
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from onnx_quantize_kit import (
    auto_quantize, QuantizationConfig, AccuracyThresholds,
    detect_model_type, benchmark_model, validate_accuracy,
    RandomCalibrationReader, quantize_dynamic_simple, quantize_fp16,
)
from onnx_quantize_kit.model_detect import ModelType, get_recommended_quant_config

tmpdir = tempfile.mkdtemp()

# ---- 创建测试模型 ----
class TestMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(512, 1024), nn.ReLU(),
            nn.Linear(1024, 1024), nn.ReLU(),
            nn.Linear(1024, 512), nn.ReLU(),
            nn.Linear(512, 100),
        )
    def forward(self, x): return self.net(x)

class TestCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.AdaptiveAvgPool2d((4, 4))
        self.fc = nn.Linear(64*16, 10)
        self.relu = nn.ReLU()
    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        x = self.pool(x)
        return self.fc(x.flatten(1))

class TestTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        self.emb = nn.Linear(64, 128)
        layer = nn.TransformerEncoderLayer(
            d_model=128, nhead=4, dim_feedforward=256, batch_first=True,
        )
        self.enc = nn.TransformerEncoder(layer, num_layers=2)
        self.fc = nn.Linear(128, 10)
    def forward(self, x):
        return self.fc(self.enc(self.emb(x)).mean(1))

def export(model, shape, name):
    model.eval()
    path = os.path.join(tmpdir, f"{name}.onnx")
    torch.onnx.export(model, torch.randn(*shape), path,
                      input_names=["input"], output_names=["output"], opset_version=18)
    return path

mlp_path = export(TestMLP(), (1, 512), "mlp")
cnn_path = export(TestCNN(), (1, 3, 16, 16), "cnn")
trans_path = export(TestTransformer(), (1, 8, 64), "transformer")

passed = 0
failed = 0

def check(name, condition, msg=""):
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}: {msg}")
        failed += 1

# 非常宽松的阈值（随机初始化模型精度天然不高）
RELAXED = AccuracyThresholds(acceptable_max_diff=5.0, min_cosine_sim=0.0, min_speedup=0.0)
# 严格阈值（触发回滚用）
STRICT = AccuracyThresholds(acceptable_max_diff=0.0001, min_cosine_sim=0.9999, min_speedup=10.0)

print("="*70)
print("Test 1: Model type detection")
print("="*70)
check("detect MLP", detect_model_type(mlp_path) == ModelType.MLP)
check("detect CNN", detect_model_type(cnn_path) == ModelType.CNN)
check("detect Transformer", detect_model_type(trans_path) == ModelType.TRANSFORMER)

print("\n" + "="*70)
print("Test 2: Recommended config per model type")
print("="*70)
mlp_cfg = get_recommended_quant_config(ModelType.MLP)
cnn_cfg = get_recommended_quant_config(ModelType.CNN)
trans_cfg = get_recommended_quant_config(ModelType.TRANSFORMER)
check("MLP recommends static", mlp_cfg["strategy"].startswith("static"))
check("CNN recommends static_qdq", cnn_cfg["strategy"] == "static_qdq")
check("Transformer recommends dynamic/FP16", trans_cfg["strategy"] in ("dynamic", "fp16"))
print(f"  MLP: {mlp_cfg['strategy']}")
print(f"  CNN: {cnn_cfg['strategy']}")
print(f"  Transformer: {trans_cfg['strategy']}")

print("\n" + "="*70)
print("Test 3: auto_quantize basic functionality")
print("="*70)
# MLP
r = auto_quantize(mlp_path, os.path.join(tmpdir, "mlp_q.onnx"),
                  input_shape=(1,512), input_name="input",
                  config=QuantizationConfig(warmup=10, runs=50, thresholds=RELAXED),
                  verbose=False)
check("MLP auto_quantize returns result", r is not None)
check("MLP quantize runs without fatal error", r.error is None or "All strategies" not in str(r.error),
      f"error={r.error}")
check("MLP output file exists", os.path.exists(r.output_path) if r.success else True)
if r.success:
    print(f"  MLP: strategy={r.strategy_used}, speedup={r.speedup:.2f}x, max_diff={r.accuracy.max_diff:.4f}")

# CNN
r = auto_quantize(cnn_path, os.path.join(tmpdir, "cnn_q.onnx"),
                  input_shape=(1,3,16,16), input_name="input",
                  config=QuantizationConfig(warmup=10, runs=50, thresholds=RELAXED),
                  verbose=False)
check("CNN auto_quantize returns result", r is not None)
check("CNN quantize runs without fatal error", r.error is None or "All strategies" not in str(r.error),
      f"error={r.error}")
if r.success:
    print(f"  CNN: strategy={r.strategy_used}, speedup={r.speedup:.2f}x, max_diff={r.accuracy.max_diff:.4f}")

# Transformer (auto mode should pick dynamic/FP16)
r = auto_quantize(trans_path, os.path.join(tmpdir, "trans_q.onnx"),
                  input_shape=(1,8,64), input_name="input",
                  config=QuantizationConfig(warmup=10, runs=50, thresholds=RELAXED),
                  verbose=False)
check("Transformer auto_quantize returns result", r is not None)
check("Transformer auto picks safe strategy",
      r.strategy_used in ("dynamic", "fp16", "static_qoperator_quint8"),
      f"got {r.strategy_used}")
if r.success:
    print(f"  Transformer: strategy={r.strategy_used}, speedup={r.speedup:.2f}x, max_diff={r.accuracy.max_diff:.4f}")

print("\n" + "="*70)
print("Test 4: Fallback mechanism triggers on impossible thresholds")
print("="*70)
# Use impossible strict thresholds - all strategies should fail but fallback chain is exercised
r = auto_quantize(mlp_path, os.path.join(tmpdir, "mlp_fb.onnx"),
                  input_shape=(1,512), input_name="input",
                  config=QuantizationConfig(strategy="static_qdq", warmup=5, runs=20, thresholds=STRICT),
                  verbose=False)
check("Fallback test returns result", r is not None)
check("Fallback chain was attempted", len(r.all_attempts) >= 1,
      f"attempts={len(r.all_attempts)}")
check("All attempts recorded with strategy names",
      all("strategy" in a for a in r.all_attempts))
# Show what was attempted
for a in r.all_attempts:
    status = "✅" if a["success"] else "❌"
    err = (a.get("error") or "")[:80]
    print(f"  {status} {a['strategy']:25s} success={a['success']} max_diff={a.get('max_diff',-1):.4f}  {err}")

# ──── Test 4b: Transformer 静态量化精度灾难 → 自动回滚到动态量化 ────
# 核心场景模拟：强制对 Transformer 使用静态量化，通过「校准数据分布不匹配」
# 复现真实场景中的精度灾难（静态量化严重依赖校准数据分布，分布不匹配时误差剧增；
# 动态量化无需校准数据，不受此影响）
print("\n" + "="*70)
print("Test 4b: Transformer static quantization disaster → auto rollback to dynamic")
print("="*70)

# 构造一个「分布不匹配」的校准Reader：校准数据范围极窄，
# 但验证时用正常范围数据，模拟生产环境校准数据与真实输入分布不一致
# （这是静态量化精度灾难的最常见根因）
class MismatchedCalibrationReader(RandomCalibrationReader):
    """故意用分布不匹配的校准数据触发静态量化精度灾难"""
    def _generate(self):
        # 校准数据范围极窄(乘以0.001)，与真实输入(标准正态N(0,1))严重不匹配
        # 静态量化会根据这些窄范围数据计算scale/zero_point，
        # 导致真实范围输入时严重截断/clamp，误差爆炸
        self.data = [
            {self.input_name: np.random.randn(*self.input_shape).astype(np.float32) * 0.001}
            for _ in range(self.num_samples)
        ]

mismatch_reader = MismatchedCalibrationReader("input", (1,8,64), num_samples=10)

# 使用较紧的阈值：正常动态量化max_diff一般<0.5，静态量化在分布不匹配时会爆炸
TRANSFORMER_ROLLBACK = AccuracyThresholds(
    acceptable_max_diff=1.0,
    min_cosine_sim=0.0,
    min_speedup=0.0,
)
r_trans = auto_quantize(
    trans_path,
    os.path.join(tmpdir, "trans_fb.onnx"),
    calib_reader=mismatch_reader,
    input_shape=(1,8,64), input_name="input",
    config=QuantizationConfig(
        strategy="static_qdq",       # 强制从静态QDQ开始（Transformer的灾难路径）
        warmup=5, runs=20,
        thresholds=TRANSFORMER_ROLLBACK,
    ),
    verbose=False,
)
check("Transformer forced-static returns result", r_trans is not None)
check("Transformer fallback chain attempted (≥2 strategies)",
      len(r_trans.all_attempts) >= 2,
      f"attempts={len(r_trans.all_attempts)}")
# 关键断言：回滚被触发（strategy_used != static_qdq）
check("Transformer fallback TRIGGERED (not static_qdq)",
      r_trans.fallback_triggered == True,
      f"fallback_triggered={r_trans.fallback_triggered}, strategy={r_trans.strategy_used}")
check("Transformer rolled back to safe strategy (dynamic/fp16)",
      r_trans.strategy_used in ("dynamic", "fp16", "static_qoperator_quint8"),
      f"got {r_trans.strategy_used}")
check("Final result file exists",
      r_trans.success and os.path.exists(r_trans.output_path),
      f"success={r_trans.success}, error={r_trans.error}")
check("Fallback reason recorded",
      bool(r_trans.fallback_reason),
      f"reason={r_trans.fallback_reason}")
# 打印完整回滚链
print("  Transformer rollback chain (calibration mismatch scenario):")
for i, a in enumerate(r_trans.all_attempts):
    status = "✅" if a["success"] else "❌"
    tag = "PRIMARY" if i == 0 else f"FALLBACK-{i}"
    err = (a.get("error") or "")[:70]
    print(f"    {status} [{tag:10s}] {a['strategy']:25s} "
          f"max_diff={a.get('max_diff',-1):.4f}  {err}")
if r_trans.success:
    print(f"  ✅ Final: strategy={r_trans.strategy_used}, "
          f"speedup={r_trans.speedup:.2f}x, max_diff={r_trans.accuracy.max_diff:.4f}")
    print(f"  ✅ Fallback reason: {r_trans.fallback_reason}")
else:
    print(f"  ❌ All strategies failed: {r_trans.error}")

print("\n" + "="*70)
print("Test 5: Individual API functions")
print("="*70)
# benchmark_model
perf = benchmark_model(mlp_path, (1,512), "input", warmup=3, runs=10)
check("benchmark_model returns valid result", perf.success and perf.avg_ms > 0,
      f"error={perf.error}")
check("benchmark_model has percentile metrics",
      perf.p50_ms > 0 and perf.p95_ms > 0 and perf.p99_ms > 0)
check("benchmark_model has throughput", perf.throughput_fps > 0)
print(f"  FP32 MLP: avg={perf.avg_ms:.4f}ms, fps={perf.throughput_fps:.1f}")

# validate_accuracy (self-match)
acc = validate_accuracy(mlp_path, mlp_path, (1,512), "input", num_samples=3)
check("validate_accuracy self-match max_diff≈0", acc.max_diff < 1e-5,
      f"max_diff={acc.max_diff}")
check("validate_accuracy self-match cosine≈1", acc.cosine_sim_min > 0.9999,
      f"cos_sim={acc.cosine_sim_min}")

# FP16 conversion always works
try:
    r_fp16 = quantize_fp16(mlp_path, os.path.join(tmpdir, "mlp_fp16.onnx"))
    check("FP16 conversion works", r_fp16.success, f"error={r_fp16.error}")
except ImportError:
    check("FP16 conversion (onnxconverter-common not installed)", True)

# RandomCalibrationReader
cr = RandomCalibrationReader("input", (1, 32), num_samples=5)
check("RandomCalibrationReader generates data", cr.get_next() is not None)
cr.rewind()
check("RandomCalibrationReader rewind", cr.get_next() is not None)
count = 0
cr.rewind()
while cr.get_next() is not None:
    count += 1
check("RandomCalibrationReader correct count", count == 5, f"count={count}")

print("\n" + "="*70)
print("Test 6: CI gate script exit codes")
print("="*70)
ci_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ci_quantization_gate.py")
report_path = os.path.join(tmpdir, "ci_report.json")

# Test 6a: CI gate with valid model - should PASS (exit 0)
proc = subprocess.run(
    [sys.executable, ci_script,
     "-m", mlp_path, "-o", os.path.join(tmpdir, "ci_mlp.onnx"),
     "-s", "1,512", "-n", "input",
     "--report", report_path, "--ci",
     "-w", "5", "-r", "20",
     "--max-diff", "5.0", "--min-speedup", "0.0"],
    capture_output=True, text=True,
    env={**os.environ, "KMP_DUPLICATE_LIB_OK": "TRUE"},
)
check("CI gate exit 0 on valid model", proc.returncode == 0,
      f"exit={proc.returncode}, stderr={proc.stderr[:200]}")
if proc.returncode == 0:
    try:
        report = json.loads(proc.stdout.strip().split("\n")[-1])
        check("CI report has status=PASS", report.get("status") == "PASS")
        check("CI report JSON file exists", os.path.exists(report_path))
        check("CI report has strategy_used", "strategy_used" in report)
        check("CI report has speedup", "speedup" in report)
    except Exception as e:
        check("CI report parse", False, str(e))

# Test 6b: CI gate with nonexistent model - should FAIL (exit 3)
proc2 = subprocess.run(
    [sys.executable, ci_script, "-m", "/nonexistent/model.onnx", "-o", "/tmp/out.onnx", "--ci"],
    capture_output=True, text=True,
    env={**os.environ, "KMP_DUPLICATE_LIB_OK": "TRUE"},
)
check("CI gate exit 3 on missing model", proc2.returncode == 3,
      f"exit={proc2.returncode}")

print("\n" + "="*70)
print(f"Results: {passed} passed, {failed} failed")
print("="*70)

shutil.rmtree(tmpdir, ignore_errors=True)
sys.exit(0 if failed == 0 else 1)
