#!/usr/bin/env python3
"""torch-dev GPU 专项深度压测脚本"""
import sys, time, gc, math, threading
import torch
import torch.nn as nn
import torch.nn.functional as F

PASS = 0
FAIL = 0

def _p(msg):
    global PASS
    PASS += 1
    print(f"  ✅ PASS: {msg}")

def _f(msg):
    global FAIL
    FAIL += 1
    print(f"  ❌ FAIL: {msg}")

print("=" * 70)
print("  torch-dev GPU 专项深度压测")
print("=" * 70)
print(f"  PyTorch: {torch.__version__}")
print(f"  CUDA: {torch.version.cuda}")
print(f"  cuDNN: {torch.backends.cudnn.version()}")
print(f"  Python: {sys.version.split()[0]}")
gil_status = "disabled (free-threading)" if hasattr(sys, "_is_gil_enabled") and not sys._is_gil_enabled() else "enabled"
print(f"  GIL: {gil_status}")
print()

device = torch.device("cuda:0")
props = torch.cuda.get_device_properties(0)
print(f"  GPU: {props.name}")
print(f"  Compute Capability: {props.major}.{props.minor}")
print(f"  VRAM: {props.total_memory/1024**3:.2f} GB")
print()

torch.backends.cudnn.benchmark = True

# ── Test 1: GPU Memory Info ──
print("── 1. GPU 显存信息 ──")
total_mem = props.total_memory
free_before = torch.cuda.mem_get_info(0)[0]
print(f"  总显存: {total_mem/1024**3:.2f} GB")
print(f"  空闲显存: {free_before/1024**3:.2f} GB")
gc.collect(); torch.cuda.empty_cache()
free_after_gc = torch.cuda.mem_get_info(0)[0]
print(f"  GC后空闲: {free_after_gc/1024**3:.2f} GB")
_p("GPU显存信息可查询")
print()

# ── Test 2: FP32 Large Matmul Performance ──
print("── 2. FP32 大矩阵乘法性能 ──")
for m, n in [(1024, 1024), (2048, 2048), (4096, 4096)]:
    a = torch.randn(m, n, device=device)
    b = torch.randn(n, m, device=device)
    torch.cuda.synchronize()
    t0 = time.perf_counter()
    for _ in range(10):
        c = a @ b
    torch.cuda.synchronize()
    t1 = time.perf_counter()
    flops = 2 * m * n * m * 10
    tflops = flops / (t1 - t0) / 1e12
    print(f"  {m}x{n} matmul x10: {(t1-t0)*1000:.1f}ms ({tflops:.2f} TFLOPS)")
    del a, b, c
gc.collect(); torch.cuda.empty_cache()
_p("FP32矩阵乘法执行正常")
print()

# ── Test 3: Mixed Precision (BF16/FP16) ──
print("── 3. 混合精度运算 (BF16/FP16) ──")
mp_ok = True
for dtype_name, dtype in [("BF16", torch.bfloat16), ("FP16", torch.float16)]:
    try:
        x_m = torch.randn(256, 256, device=device, dtype=dtype, requires_grad=True)
        w_m = torch.randn(256, 256, device=device, dtype=dtype, requires_grad=True)
        y_m = x_m @ w_m
        loss = y_m.float().sum()
        loss.backward()
        assert x_m.grad is not None and w_m.grad is not None
        print(f"  {dtype_name}: matmul+backward OK, dtype={y_m.dtype}, loss={loss.item():.4f}, grad_mean={x_m.grad.float().mean().item():.6f}")
    except Exception as e:
        print(f"  {dtype_name}: FAIL - {e}")
        mp_ok = False
gc.collect(); torch.cuda.empty_cache()
if mp_ok:
    _p("混合精度(BF16/FP16)运算正常")
else:
    _f("混合精度运算有失败")
print()

# ── Test 4: CPU vs GPU Performance ──
print("── 4. CPU vs GPU 性能对比 (4096x4096 matmul) ──")
sz = 4096
a_cpu = torch.randn(sz, sz)
b_cpu = torch.randn(sz, sz)
t0 = time.perf_counter()
c_cpu = a_cpu @ b_cpu
t_cpu = time.perf_counter() - t0

a_gpu = a_cpu.to(device)
b_gpu = b_cpu.to(device)
torch.cuda.synchronize()
t0 = time.perf_counter()
c_gpu = a_gpu @ b_gpu
torch.cuda.synchronize()
t_gpu = time.perf_counter() - t0

speedup = t_cpu / t_gpu
diff = (c_cpu - c_gpu.cpu()).abs().max().item()
print(f"  CPU: {t_cpu*1000:.1f}ms")
print(f"  GPU: {t_gpu*1000:.1f}ms")
print(f"  Speedup: {speedup:.1f}x")
print(f"  最大误差: {diff:.6f}")
if speedup > 5 and diff < 1e-2:
    _p(f"GPU比CPU快{speedup:.1f}x且结果一致(误差{diff:.6f})")
else:
    _f(f"性能对比异常: speedup={speedup:.1f}x, diff={diff:.6f}")
del a_cpu, b_cpu, c_cpu, a_gpu, b_gpu, c_gpu
gc.collect(); torch.cuda.empty_cache()
print()

# ── Test 5: Data Transfer Bandwidth ──
print("── 5. 数据传输带宽 (CPU<->GPU) ──")
sz = 100_000_000  # ~400MB
x_host = torch.randn(sz)
x_pinned = torch.randn(sz).pin_memory()

torch.cuda.synchronize()
t0 = time.perf_counter()
x_dev = x_host.to(device)
torch.cuda.synchronize()
t_regular = time.perf_counter() - t0

torch.cuda.synchronize()
t0 = time.perf_counter()
x_dev_pinned = x_pinned.to(device)
torch.cuda.synchronize()
t_pinned = time.perf_counter() - t0

torch.cuda.synchronize()
t0 = time.perf_counter()
x_back = x_dev.cpu()
torch.cuda.synchronize()
t_d2h = time.perf_counter() - t0

bytes_xfer = sz * 4
print(f"  H2D (pageable): {t_regular*1000:.1f}ms, {bytes_xfer/t_regular/1e9:.2f} GB/s")
print(f"  H2D (pinned):   {t_pinned*1000:.1f}ms, {bytes_xfer/t_pinned/1e9:.2f} GB/s")
print(f"  D2H:            {t_d2h*1000:.1f}ms, {bytes_xfer/t_d2h/1e9:.2f} GB/s")
_p("数据传输正常")
del x_host, x_pinned, x_dev, x_dev_pinned, x_back
gc.collect(); torch.cuda.empty_cache()
print()

# ── Test 6: CNN Forward+Backward ──
print("── 6. CNN 前向+反向传播 ──")
model = nn.Sequential(
    nn.Conv2d(3, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
    nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
    nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Linear(128, 10)
).to(device)
x = torch.randn(32, 3, 224, 224, device=device)
target = torch.randint(0, 10, (32,), device=device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

torch.cuda.synchronize()
t0 = time.perf_counter()
for _ in range(5):
    optimizer.zero_grad()
    out = model(x)
    loss = F.cross_entropy(out, target)
    loss.backward()
    optimizer.step()
torch.cuda.synchronize()
t1 = time.perf_counter()
print(f"  ConvNet (5 iters, batch=32, 224x224): {(t1-t0)*1000:.0f}ms, loss={loss.item():.4f}")
_p("CNN训练循环正常")
del model, x, target, optimizer
gc.collect(); torch.cuda.empty_cache()
print()

# ── Test 7: Memory Allocation (safe, up to 70% of free) ──
print("── 7. 显存分配/释放测试 ──")
free_info = torch.cuda.mem_get_info(0)
free_before_alloc = free_info[0]
target_alloc = int(free_before_alloc * 0.7)  # allocate up to 70% of free
block = 256 * 1024 * 1024  # 256MB blocks
tensors = []
allocated = 0
while allocated + block <= target_alloc:
    try:
        t = torch.empty(block // 4, dtype=torch.float32, device=device)
        tensors.append(t)
        allocated += block
    except RuntimeError:
        break
mid_free = torch.cuda.mem_get_info(0)[0]
print(f"  目标分配: {target_alloc/1024**3:.2f} GB")
print(f"  实际分配: {allocated/1024**3:.2f} GB ({len(tensors)} blocks)")
print(f"  分配后空闲: {mid_free/1024**3:.2f} GB")

# Write test: multiply in allocated memory
if tensors:
    tensors[0].fill_(1.0)
    tensors[0] = tensors[0] * 2.0
    val = tensors[0][0].item()
    print(f"  写入测试: fill(1.0)*2.0 => {val}")

del tensors
gc.collect(); torch.cuda.empty_cache()
free_after_free = torch.cuda.mem_get_info(0)[0]
recovered = (free_after_free - mid_free) / 1024**3
print(f"  释放后空闲: {free_after_free/1024**3:.2f} GB")
print(f"  回收显存: {recovered:.2f} GB")
if recovered > allocated / 1024**3 * 0.8:
    _p(f"显存分配/释放/回收正常(回收{recovered:.2f}GB)")
else:
    _f(f"显存回收不足: 分配{allocated/1024**3:.2f}GB, 仅回收{recovered:.2f}GB")
print()

# ── Test 8: CUDA Streams ──
print("── 8. CUDA 多流并发 ──")
streams = [torch.cuda.Stream() for _ in range(4)]
results = []
torch.cuda.synchronize()
t0 = time.perf_counter()
for i, s in enumerate(streams):
    with torch.cuda.stream(s):
        a = torch.randn(2048, 2048, device=device)
        b = torch.randn(2048, 2048, device=device)
        results.append(a @ b)
torch.cuda.synchronize()
t1 = time.perf_counter()
print(f"  4并发流(2048x2048 matmul): {(t1-t0)*1000:.1f}ms")
streams_ok = True
for i, r in enumerate(results):
    if r.shape == (2048, 2048) and torch.isfinite(r).all():
        pass
    else:
        streams_ok = False
        print(f"  Stream {i}: 异常!")
if streams_ok:
    _p("CUDA多流并发执行正常")
else:
    _f("CUDA多流并发有异常")
del results
gc.collect(); torch.cuda.empty_cache()
print()

# ── Test 9: Free-threading concurrency ──
print("── 9. Free-threading 并发CUDA测试 (4线程) ──")
results_t = []
errors_t = []

def worker(wid):
    try:
        results = []
        for _ in range(20):
            a = torch.randn(256, 256, device=device)
            b = torch.randn(256, 256, device=device)
            c = a @ b
            results.append(c.mean().item())
        torch.cuda.synchronize()
        results_t.append((wid, sum(results) / len(results)))
    except Exception as e:
        errors_t.append((wid, str(e)))

threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
torch.cuda.synchronize()
t0 = time.perf_counter()
for th in threads:
    th.start()
for th in threads:
    th.join()
torch.cuda.synchronize()
t1 = time.perf_counter()
print(f"  4线程并发CUDA: {(t1-t0)*1000:.1f}ms")
for wid, val in results_t:
    print(f"  Worker {wid}: mean={val:.6f}")
if errors_t:
    for wid, err in errors_t:
        print(f"  Worker {wid} ERROR: {err}")
    _f("Free-threading并发CUDA有错误")
else:
    _p("Free-threading并发CUDA运算正常")
gc.collect(); torch.cuda.empty_cache()
print()

# ── Test 10: TorchCompilation / torch.compile (if supported) ──
print("── 10. torch.compile 兼容性 ──")
try:
    model_simple = nn.Sequential(nn.Linear(256, 128), nn.ReLU(), nn.Linear(128, 10)).to(device)
    x_comp = torch.randn(16, 256, device=device)
    compiled = torch.compile(model_simple, mode="reduce-overhead")
    out_eager = model_simple(x_comp)
    out_compiled = compiled(x_comp)
    diff_comp = (out_eager - out_compiled).abs().max().item()
    print(f"  eager vs compiled max_diff: {diff_comp:.6f}")
    if diff_comp < 1e-4:
        _p("torch.compile正常工作")
    else:
        _f(f"torch.compile结果差异过大: {diff_comp}")
    del model_simple, x_comp, compiled, out_eager, out_compiled
except Exception as e:
    print(f"  torch.compile: SKIP - {e}")
gc.collect(); torch.cuda.empty_cache()
print()

# ── Final Memory Check ──
free_final = torch.cuda.mem_get_info(0)[0]
print("── 最终显存状态 ──")
print(f"  测试前空闲: {free_before/1024**3:.2f} GB")
print(f"  测试后空闲: {free_final/1024**3:.2f} GB")
leak = (free_before - free_final) / 1024**3
if leak < 0.5:
    print(f"  显存泄漏: ~{leak:.3f} GB (正常)")
else:
    print(f"  显存泄漏: ~{leak:.3f} GB (可能有问题)")
print()

# ── Summary ──
print("=" * 70)
total = PASS + FAIL
print(f"  测试总结: PASS {PASS}/{total}" + (f", FAIL {FAIL}" if FAIL > 0 else ""))
print("=" * 70)
if FAIL == 0:
    print("\n🎉 GPU 专项压测全部通过！")
else:
    print(f"\n⚠️  有 {FAIL} 项失败，请排查")
    sys.exit(1)
