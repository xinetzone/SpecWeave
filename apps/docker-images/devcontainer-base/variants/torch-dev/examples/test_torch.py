#!/usr/bin/env python3
"""
torch-dev 容器 PyTorch + CUDA 综合验证脚本
可在容器内独立运行，也可通过 start-torch-dev.sh 一键启动后自动执行。

用法:
  python examples/test_torch.py           # 完整验证
  python examples/test_torch.py --quick   # 快速验证（跳过耗时算子测试）
  python examples/test_torch.py --cuda    # 强制 CUDA 测试（无 CUDA 时跳过）
"""
from __future__ import annotations

import sys
import argparse
import platform
import time
from typing import List, Tuple, Any

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"

PASS_COUNT = 0
FAIL_COUNT = 0
SKIP_COUNT = 0
ERRORS: List[str] = []


def _ok(msg: str) -> None:
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"  {GREEN}PASS{NC}: {msg}")


def _fail(msg: str) -> None:
    global FAIL_COUNT
    FAIL_COUNT += 1
    ERRORS.append(msg)
    print(f"  {RED}FAIL{NC}: {msg}")


def _skip(msg: str) -> None:
    global SKIP_COUNT
    SKIP_COUNT += 1
    print(f"  {YELLOW}SKIP{NC}: {msg}")


def _info(msg: str) -> None:
    print(f"  {CYAN}INFO{NC}: {msg}")


def _header(title: str) -> None:
    print(f"\n{BOLD}── {title} ──{NC}")


def check_python_env() -> bool:
    """检查 Python 版本与 free-threading 状态"""
    ok = True
    _header("Python 环境")

    pyver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"  Python版本: {pyver}")
    print(f"  平台: {platform.platform()}")
    print(f"  可执行文件: {sys.executable}")

    if sys.version_info[:2] == (3, 14):
        _ok(f"Python {pyver} 符合预期 (3.14.x)")
    else:
        _fail(f"Python 版本不符合预期: {pyver}，期望 3.14.x")
        ok = False

    gil_disabled = not sys._is_gil_enabled()
    if gil_disabled:
        _ok("free-threading 启用 (GIL 已禁用, cp314t)")
    else:
        _info("GIL 当前启用 (triton 导入时临时启用属于预期行为)")

    try:
        import sysconfig
        py_gil = sysconfig.get_config_var("Py_GIL_DISABLED")
        soabi = sysconfig.get_config_var("SOABI") or ""
        print(f"  构建配置: Py_GIL_DISABLED={py_gil}, SOABI={soabi}")
        if "cp314t" in soabi or py_gil == 1:
            _ok("二进制为 cp314t free-threading 构建")
        else:
            _fail(f"非 free-threading 构建: SOABI={soabi}")
            ok = False
    except Exception as e:
        _skip(f"sysconfig 检查失败: {e}")

    return ok


def check_torch_import() -> bool:
    """检查 torch / torchvision 导入与版本"""
    ok = True
    _header("PyTorch 导入与版本")

    try:
        import torch
        print(f"  torch 版本: {torch.__version__}")
        _ok(f"torch {torch.__version__} 导入成功")
    except ImportError as e:
        _fail(f"torch 导入失败: {e}")
        return False

    try:
        import torchvision
        print(f"  torchvision 版本: {torchvision.__version__}")
        _ok(f"torchvision {torchvision.__version__} 导入成功")
    except ImportError as e:
        _fail(f"torchvision 导入失败: {e}")
        ok = False

    try:
        import onnx
        import onnxruntime
        print(f"  onnx 版本: {onnx.__version__}")
        print(f"  onnxruntime 版本: {onnxruntime.__version__}")
        _ok(f"ONNX 栈继承正常 (onnx {onnx.__version__}, ort {onnxruntime.__version__})")
    except ImportError as e:
        _skip(f"ONNX 栈导入失败（非致命）: {e}")

    return ok


def check_cuda() -> Tuple[bool, Any]:
    """检查 CUDA 可用性，返回 (可用, device)"""
    _header("CUDA / GPU 检测")
    import torch

    cuda_available = torch.cuda.is_available()
    if cuda_available:
        dev_count = torch.cuda.device_count()
        print(f"  CUDA 可用: 是")
        print(f"  GPU 数量: {dev_count}")
        for i in range(dev_count):
            props = torch.cuda.get_device_properties(i)
            mem_gb = props.total_memory / (1024**3)
            print(f"  GPU[{i}]: {props.name}, {mem_gb:.1f} GB VRAM, CC {props.major}.{props.minor}")
        _ok(f"CUDA 可用，共 {dev_count} 个 GPU")
        device = torch.device("cuda:0")
    else:
        _skip("CUDA 不可用（容器无 GPU 或未配置 --gpus），使用 CPU")
        device = torch.device("cpu")

    try:
        import torch.backends.mkldnn
        print(f"  MKL-DNN (oneDNN) 可用: {torch.backends.mkldnn.is_available()}")
    except Exception:
        pass

    try:
        import torch.backends.openmp
        print(f"  OpenMP 可用: {torch.backends.openmp.is_available()}")
    except Exception:
        pass

    return cuda_available, device


def check_basic_ops(device: Any, quick: bool = False) -> bool:
    """基础算子冒烟测试"""
    ok = True
    _header("基础算子测试")
    import torch
    import torch.nn.functional as F

    torch.manual_seed(42)

    # matmul
    try:
        t0 = time.time()
        a = torch.randn(64, 128, device=device)
        b = torch.randn(128, 32, device=device)
        c = torch.matmul(a, b)
        dt = (time.time() - t0) * 1000
        assert c.shape == (64, 32), f"shape mismatch: {c.shape}"
        _ok(f"matmul: (64,128)@(128,32) -> (64,32) ({dt:.1f}ms, {device.type})")
    except Exception as e:
        _fail(f"matmul 失败: {e}")
        ok = False

    # conv2d
    try:
        t0 = time.time()
        x = torch.randn(2, 3, 32, 32, device=device)
        w = torch.randn(16, 3, 3, 3, device=device)
        out = F.conv2d(x, w, padding=1)
        dt = (time.time() - t0) * 1000
        assert out.shape == (2, 16, 32, 32), f"shape mismatch: {out.shape}"
        _ok(f"conv2d: (2,3,32,32) -> (2,16,32,32) ({dt:.1f}ms, {device.type})")
    except Exception as e:
        _fail(f"conv2d 失败: {e}")
        ok = False

    if quick:
        return ok

    # autograd
    try:
        x = torch.randn(8, 16, device=device, requires_grad=True)
        w = torch.randn(16, 4, device=device, requires_grad=True)
        y = x @ w
        loss = y.sum()
        loss.backward()
        assert x.grad is not None and w.grad is not None
        assert x.grad.shape == x.shape and w.grad.shape == w.shape
        _ok("autograd: 梯度计算正常，shape 匹配")
    except Exception as e:
        _fail(f"autograd 失败: {e}")
        ok = False

    # cross_entropy
    try:
        logits = torch.randn(8, 10, device=device)
        targets = torch.randint(0, 10, (8,), device=device)
        loss = F.cross_entropy(logits, targets)
        assert loss.dim() == 0 and loss.item() > 0
        _ok(f"cross_entropy: loss={loss.item():.4f}")
    except Exception as e:
        _fail(f"cross_entropy 失败: {e}")
        ok = False

    # MLP forward
    try:
        import torch.nn as nn
        model = nn.Sequential(nn.Linear(32, 64), nn.ReLU(), nn.Linear(64, 8)).to(device)
        out = model(torch.randn(4, 32, device=device))
        assert out.shape == (4, 8)
        _ok("MLP forward: Sequential(32->64->ReLU->8) -> (4,8)")
    except Exception as e:
        _fail(f"MLP forward 失败: {e}")
        ok = False

    return ok


def check_onnx_export(quick: bool = False) -> bool:
    """torch → ONNX 导出互操作测试"""
    if quick:
        return True
    _header("PyTorch → ONNX 互操作")
    try:
        import torch
        import torch.nn as nn
        import onnx
        import onnxruntime as ort
        import tempfile
        import os
        import numpy as np
    except ImportError as e:
        _skip(f"ONNX 互操作依赖缺失: {e}")
        return True

    try:
        torch.manual_seed(42)
        model = nn.Sequential(nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 8))
        model.eval()
        dummy = torch.randn(1, 32)

        with tempfile.TemporaryDirectory() as td:
            onnx_path = os.path.join(td, "model.onnx")
            torch.onnx.export(
                model, dummy, onnx_path,
                input_names=["input"], output_names=["output"],
                opset_version=18,
            )
            m = onnx.load(onnx_path)
            onnx.checker.check_model(m)
            sess = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
            out = sess.run(None, {"input": dummy.numpy()})[0]
            assert out.shape == (1, 8), f"Unexpected shape: {out.shape}"
            with torch.no_grad():
                torch_out = model(dummy).numpy()
            max_diff = float(np.max(np.abs(out - torch_out)))
            assert max_diff < 1e-5, f"Diff too large: {max_diff}"
            _ok(f"torch→ONNX 导出+ORT推理互操作正常 (max_diff={max_diff:.2e})")
            return True
    except Exception as e:
        _fail(f"ONNX 互操作失败: {e}")
        return False


def check_env_health() -> bool:
    """环境健康检查：PATH、关键环境变量、线程配置"""
    ok = True
    _header("环境健康")

    expected_python = "/opt/conda/envs/main/bin/python"
    if sys.executable == expected_python:
        _ok(f"Python 路径正确: {sys.executable}")
    else:
        _info(f"Python 路径: {sys.executable} (期望 {expected_python})")

    import os
    omp_threads = os.environ.get("OMP_NUM_THREADS", "<未设置>")
    kmp_ok = os.environ.get("KMP_DUPLICATE_LIB_OK", "<未设置>")
    print(f"  OMP_NUM_THREADS={omp_threads}, KMP_DUPLICATE_LIB_OK={kmp_ok}")

    # devuser 权限检查（非root时）
    if hasattr(os, "getuid"):
        uid = os.getuid()
        print(f"  当前 UID: {uid} ({'root' if uid == 0 else '非root用户'})")

    # onnxoptimizer 缺席检查（cp314t不兼容）
    try:
        import importlib.util as u
        if u.find_spec("onnxoptimizer") is None:
            _ok("onnxoptimizer 缺席（cp314t不兼容，预期行为）")
        else:
            _fail("onnxoptimizer 意外存在（cp314t不兼容）")
            ok = False
    except Exception:
        pass

    return ok


def print_summary() -> bool:
    """打印总结，返回是否全部通过"""
    total = PASS_COUNT + FAIL_COUNT + SKIP_COUNT
    print(f"\n{BOLD}{'='*60}{NC}")
    print(f"{BOLD}  测试总结{NC}")
    print(f"{'='*60}")
    print(f"  {GREEN}PASS:{NC} {PASS_COUNT}/{total}  ", end="")
    if FAIL_COUNT > 0:
        print(f"{RED}FAIL:{NC} {FAIL_COUNT}/{total}  ", end="")
    if SKIP_COUNT > 0:
        print(f"{YELLOW}SKIP:{NC} {SKIP_COUNT}/{total}", end="")
    print()
    print(f"{'='*60}")

    if ERRORS:
        print(f"\n{RED}失败项:{NC}")
        for e in ERRORS:
            print(f"  - {e}")

    if FAIL_COUNT == 0:
        print(f"\n{GREEN}{BOLD}✅ torch-dev 环境验证全部通过！{NC}")
        return True
    else:
        print(f"\n{RED}{BOLD}❌ 有 {FAIL_COUNT} 项测试失败{NC}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description="torch-dev PyTorch+CUDA 验证脚本")
    parser.add_argument("--quick", action="store_true", help="快速模式：跳过耗时算子测试")
    parser.add_argument("--cuda", action="store_true", help="强制 CUDA 测试")
    args = parser.parse_args()

    print(f"{BOLD}{CYAN}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║       torch-dev PyTorch + CUDA 综合验证脚本               ║")
    print("║       (cp314t free-threading, PyTorch + torchvision)     ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{NC}")

    all_ok = True

    try:
        all_ok &= check_python_env()
        all_ok &= check_torch_import()

        import torch
        cuda_avail, device = check_cuda()
        if args.cuda and not cuda_avail:
            _skip("--cuda 指定但 CUDA 不可用，回退到 CPU")
        all_ok &= check_basic_ops(device, quick=args.quick)
        all_ok &= check_onnx_export(quick=args.quick)
        all_ok &= check_env_health()
    except Exception as e:
        _fail(f"未预期异常: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        all_ok = False

    success = print_summary()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
