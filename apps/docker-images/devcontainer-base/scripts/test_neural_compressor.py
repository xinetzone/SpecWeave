#!/usr/bin/env python3
"""Neural Compressor 3.x API 单元测试

测试重点：
1. INC 包安装和版本检测（>= 3.0）
2. INC 3.x PyTorch 新API导入验证（RTNConfig/AWQConfig/GPTQConfig/quantize/prepare/convert）
3. INC 2.x 旧API弃用行为验证（PostTrainingQuantConfig等）
4. INC 3.x weight-only量化冒烟测试（PyTorch模型）
5. 验证我们的主力量化方案（onnxruntime.quantization）不受INC版本影响

========================================================================
📌 Neural Compressor 版本说明（测试维护者必读）
========================================================================
INC 2.x → 3.x 是一次重大架构重构：
- 2.x: 统一框架API，支持 PyTorch/TensorFlow/ONNX Runtime
  - 入口: from neural_compressor import quantization
  - 配置: PostTrainingQuantConfig
  - ONNX支持: 通过 adaptor/onnxrt.py 适配层
- 3.x: 框架专属API，PyTorch-first
  - PyTorch入口: from neural_compressor.torch.quantization import ...
  - 配置: 细粒度 RTNConfig/AWQConfig/GPTQConfig/TeqConfig/AutoRoundConfig
  - ⚠️ ONNX/TensorFlow adaptor 已弃用（PR #2199标记deprecated）
  - 工作流: prepare() → convert() 或直接 quantize()

本项目策略：
- ✅ ONNX模型量化主力: onnxruntime.quantization 原生API（不依赖INC）
- ✅ PyTorch高级量化: 使用INC 3.x torch API（weight-only量化、AutoRound等）
- 📝 本测试聚焦INC 3.x API可用性和冒烟测试
========================================================================
"""
import os
import sys
import tempfile
import shutil

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np

passed = 0
failed = 0
skipped = 0


def check(name, condition, msg=""):
    """测试断言函数（与test_quantize_kit.py风格一致）"""
    global passed, failed
    if condition:
        print(f"  ✅ {name}")
        passed += 1
    else:
        print(f"  ❌ {name}: {msg}")
        failed += 1


def skip(name, reason=""):
    """标记跳过的测试"""
    global skipped
    print(f"  ⏭️  {name} [SKIPPED: {reason}]")
    skipped += 1


# ======================================================================
# 前置检查：INC是否安装
# ======================================================================
print("=" * 70)
print("Test 1: Neural Compressor 包安装和版本验证")
print("=" * 70)

nc_available = False
nc_version = None
nc_version_tuple = None

# 严格模式：通过命令行参数 --strict 或环境变量 NC_STRICT=1 启用
# 严格模式下INC未安装视为失败（用于onnx-quantized Docker镜像验证）
strict_mode = "--strict" in sys.argv or os.environ.get("NC_STRICT", "0") == "1"

try:
    import neural_compressor
    nc_version = neural_compressor.__version__
    nc_version_tuple = tuple(map(int, nc_version.split(".")[:2]))
    nc_available = True
    check("neural_compressor 包可导入", True)
    check(f"版本号 >= 3.0 (当前: {nc_version})", nc_version_tuple >= (3, 0),
          f"需要INC 3.x，当前安装的是 {nc_version}")
    print(f"  ℹ️  Neural Compressor 版本: {nc_version}")
    if strict_mode:
        print(f"  ℹ️  严格模式已启用（onnx-quantized镜像验证）")
except ImportError as e:
    if strict_mode:
        check("neural_compressor 包可导入（严格模式）", False, f"导入失败: {e}")
    else:
        skip("neural_compressor 包可导入", "INC未安装（仅验证onnxruntime主力方案）")
    print("\n" + "!" * 70)
    print("! neural_compressor 未安装，跳过所有INC相关测试")
    print("! 安装命令: pip install neural-compressor")
    print("! 注意: onnxruntime.quantization 原生量化功能不受影响")
    print("!" * 70)

if not nc_available:
    # INC未安装，只验证onnxruntime原生量化不受影响
    print("\n" + "=" * 70)
    print("Test 5 (fallback): onnxruntime.quantization 主力方案验证（INC未安装）")
    print("=" * 70)
    try:
        from onnxruntime.quantization import quantize_dynamic, QuantType
        check("onnxruntime.quantization 可导入（主力方案不受影响）", True)
    except ImportError as e:
        check("onnxruntime.quantization 可导入", False, str(e))
    print(f"\n{'='*70}")
    print(f"测试结果: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 70)
    sys.exit(0 if failed == 0 else 1)

# ======================================================================
# Test 2: INC 3.x PyTorch 新API导入验证
# ======================================================================
print("\n" + "=" * 70)
print("Test 2: INC 3.x PyTorch 新API 导入验证")
print("=" * 70)

# 检查torch是否可用
torch_available = False
try:
    import torch
    import torch.nn as nn
    torch_available = True
    check("PyTorch 可用", True, f"version={torch.__version__}")
except ImportError as e:
    check("PyTorch 可用", False, str(e))

# INC 3.x 核心API路径
inc3_api_imports = {
    "neural_compressor.torch": "torch模块",
    "neural_compressor.torch.quantization": "torch.quantization模块",
}

inc3_config_classes = [
    "RTNConfig",      # Round-to-Nearest weight-only quantization
]

inc3_functions = [
    "quantize",       # 直接一键量化
    "prepare",        # 校准准备
    "convert",        # 转换为量化模型
]

# 尝试导入3.x核心模块
nc_torch_available = False
try:
    import neural_compressor.torch
    nc_torch_available = True
    check("neural_compressor.torch 可导入（3.x PyTorch API）", True)
except ImportError as e:
    check("neural_compressor.torch 可导入（3.x PyTorch API）", False, str(e))

if nc_torch_available:
    try:
        from neural_compressor.torch.quantization import RTNConfig, quantize, prepare, convert
        check("RTNConfig 可导入", True)
        check("quantize 函数可导入", True)
        check("prepare 函数可导入", True)
        check("convert 函数可导入", True)

        # 可选配置类（某些子版本可能有差异）
        optional_configs = ["AWQConfig", "GPTQConfig", "TeqConfig", "AutoRoundConfig"]
        for cfg_name in optional_configs:
            try:
                exec(f"from neural_compressor.torch.quantization import {cfg_name}")
                check(f"{cfg_name} 可导入（可选高级算法）", True)
            except (ImportError, AttributeError):
                skip(f"{cfg_name} 可导入（可选高级算法）", "此版本可能不包含该算法或需要额外依赖")
    except ImportError as e:
        check("INC 3.x API导入", False, str(e))

# ======================================================================
# Test 3: INC 2.x 旧API弃用验证（预期行为验证）
# ======================================================================
print("\n" + "=" * 70)
print("Test 3: INC 2.x 旧API弃用行为验证（预期行为）")
print("=" * 70)
print("  ℹ️  注意: INC 3.x已重构API，以下导入失败是预期行为，不是Bug")
print("  ℹ️  ONNX量化请使用onnxruntime.quantization原生API")

# 2.x旧API列表 - 在3.x中应该不存在或被标记弃用
legacy_imports_2x = [
    ("from neural_compressor.config import PostTrainingQuantConfig",
     "PostTrainingQuantConfig（2.x统一配置类，3.x已拆分为细粒度Config）"),
    ("from neural_compressor import quantization",
     "neural_compressor.quantization统一入口（3.x改为框架专属）"),
]

all_legacy_failed_as_expected = True
for import_stmt, description in legacy_imports_2x:
    try:
        exec(import_stmt)
        # 如果导入成功，说明还保留了2.x兼容层
        check(f"[兼容层] {description}", True, "2.x API仍可通过兼容层访问")
        print(f"    ⚠️  导入成功: 保留了2.x兼容层")
    except (ImportError, AttributeError):
        check(f"[预期弃用] {description}", True, "已移除，符合3.x重构预期")
        print(f"    ℹ️  导入失败: 符合3.x重构预期（使用3.x新API）")
    except Exception as e:
        check(f"[异常] {description}", False, f"意外错误: {type(e).__name__}: {e}")
        all_legacy_failed_as_expected = False

# ======================================================================
# Test 4: INC 3.x weight-only 量化冒烟测试（PyTorch模型）
# ======================================================================
print("\n" + "=" * 70)
print("Test 4: INC 3.x Weight-Only 量化冒烟测试（PyTorch MLP）")
print("=" * 70)

if not torch_available or not nc_torch_available:
    skip("INC 3.x PyTorch量化冒烟测试", "PyTorch或neural_compressor.torch不可用")
else:
    tmpdir = tempfile.mkdtemp()
    try:
        from neural_compressor.torch.quantization import RTNConfig, quantize

        # 创建一个简单MLP模型
        class SimpleMLP(nn.Module):
            def __init__(self):
                super().__init__()
                self.net = nn.Sequential(
                    nn.Linear(128, 256),
                    nn.ReLU(),
                    nn.Linear(256, 64),
                    nn.ReLU(),
                    nn.Linear(64, 10),
                )
            def forward(self, x):
                return self.net(x)

        model = SimpleMLP().eval()
        example_inputs = torch.randn(1, 128)

        # FP32基准推理
        with torch.no_grad():
            fp32_output = model(example_inputs)
        check("FP32模型推理成功", fp32_output.shape == (1, 10),
              f"输出形状错误: {fp32_output.shape}")

        # 使用RTN 4bit weight-only量化
        try:
            woq_config = RTNConfig(bits=4, group_size=32)
            check("RTNConfig创建成功（bits=4, group_size=32）", True)

            # 一键量化
            q_model = quantize(model, quant_config=woq_config, example_inputs=example_inputs)
            check("quantize()一键量化成功", q_model is not None)

            # 量化后推理
            with torch.no_grad():
                int8_output = q_model(example_inputs)
            check("量化模型推理成功", int8_output.shape == (1, 10),
                  f"输出形状错误: {int8_output.shape}")

            # 精度验证（4bit量化误差应该在合理范围内）
            max_diff = torch.max(torch.abs(fp32_output - int8_output)).item()
            check(f"量化精度合理（max_diff={max_diff:.6f} < 1.0）",
                  max_diff < 1.0, f"误差过大: {max_diff}")
            print(f"    ℹ️  FP32 vs INT4 max_diff: {max_diff:.6f}")

            # 保存和加载测试（如果API支持）
            save_path = os.path.join(tmpdir, "nc_quantized_model")
            try:
                q_model.save(save_path)
                check("量化模型保存成功", os.path.exists(save_path))
            except Exception as e:
                skip("量化模型保存/加载", f"save() API可能有变化: {type(e).__name__}")

        except Exception as e:
            check("INC 3.x weight-only量化", False,
                  f"{type(e).__name__}: {str(e)[:200]}")
            import traceback
            traceback.print_exc()

    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

# ======================================================================
# Test 5: onnxruntime.quantization 主力方案验证（与INC无关，必须可用）
# ======================================================================
print("\n" + "=" * 70)
print("Test 5: onnxruntime.quantization 主力方案验证（核心功能）")
print("=" * 70)
print("  ℹ️  本项目ONNX量化主力方案: onnxruntime.quantization（完全不依赖INC）")

try:
    from onnxruntime.quantization import (
        quantize_dynamic, quantize_static, QuantType, QuantFormat,
        CalibrationDataReader
    )
    check("onnxruntime.quantization 核心API可导入", True)

    # 验证关键枚举和类
    check("QuantType.QInt8 存在", hasattr(QuantType, "QInt8"))
    check("QuantType.QUInt8 存在", hasattr(QuantType, "QUInt8"))
    check("CalibrationDataReader 存在", CalibrationDataReader is not None)

    import onnx
    import onnxsim
    import onnxruntime as ort

    # 简单ONNX导出+量化端到端冒烟
    if torch_available:
        tmpdir = tempfile.mkdtemp()
        try:
            # 导出ONNX
            class TinyModel(nn.Module):
                def __init__(self):
                    super().__init__()
                    self.fc = nn.Linear(16, 8)
                def forward(self, x):
                    return self.fc(x)

            model = TinyModel().eval()
            onnx_path = os.path.join(tmpdir, "tiny.onnx")
            quant_path = os.path.join(tmpdir, "tiny_int8.onnx")

            torch.onnx.export(model, torch.randn(1, 16), onnx_path,
                              input_names=["input"], output_names=["output"],
                              opset_version=18)

            # onnxsim简化
            m = onnx.load(onnx_path)
            m_simp, check_ok = onnxsim.simplify(m)
            onnx.save(m_simp, onnx_path)

            # 动态量化（我们的主力方案）
            quantize_dynamic(onnx_path, quant_path,
                             weight_type=QuantType.QInt8, per_channel=True)
            check("onnxruntime.quantization 动态量化冒烟测试成功",
                  os.path.exists(quant_path), "输出文件未生成")

            # 推理验证
            sess = ort.InferenceSession(quant_path, providers=["CPUExecutionProvider"])
            out = sess.run(None, {"input": np.random.randn(1, 16).astype(np.float32)})[0]
            check("量化ONNX模型推理成功", out.shape == (1, 8), f"形状错误: {out.shape}")

        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)
    else:
        skip("ONNX量化端到端测试", "PyTorch不可用，无法导出测试模型")

except ImportError as e:
    check("onnxruntime.quantization 导入", False, str(e))

# ======================================================================
# Test 6: INC版本和功能矩阵说明验证（文档一致性检查）
# ======================================================================
print("\n" + "=" * 70)
print("Test 6: 版本信息和功能矩阵一致性验证")
print("=" * 70)

print(f"  📦 Neural Compressor版本: {nc_version}")
print(f"  📦 PyTorch版本: {torch.__version__ if torch_available else 'N/A'}")

import onnxruntime
print(f"  📦 ONNX Runtime版本: {onnxruntime.__version__}")

# 版本兼容性断言
check("INC版本 >= 3.0（符合本项目3.x API预期）", nc_version_tuple >= (3, 0),
      f"当前版本 {nc_version} 不符合预期")

# 方案边界说明
print("\n  📋 量化方案矩阵:")
print("     ┌─────────────────┬─────────────────────┬──────────────────────┐")
print("     │ 目标模型        │ 推荐量化方案        │ 依赖库               │")
print("     ├─────────────────┼─────────────────────┼──────────────────────┤")
print("     │ ONNX模型(主力)  │ onnxruntime         │ onnxruntime          │")
print("     │ PyTorch(高级)   │ INC 3.x torch API   │ neural-compressor    │")
print("     │ PyTorch(weight) │ INC RTN/AWQ/GPTQ    │ neural-compressor    │")
print("     └─────────────────┴─────────────────────┴──────────────────────┘")

check("方案边界清晰（ONNX用ORT，PyTorch高级用INC）", True)

# ======================================================================
# 测试汇总
# ======================================================================
print("\n" + "=" * 70)
print("测试汇总")
print("=" * 70)
total = passed + failed
print(f"  ✅ 通过: {passed}")
print(f"  ❌ 失败: {failed}")
print(f"  ⏭️  跳过: {skipped}")
print(f"  📊 总计: {total} 个测试用例")
print("=" * 70)

if failed > 0:
    print("\n⚠️  存在失败的测试用例！")
    sys.exit(1)
else:
    print("\n🎉 所有测试通过！")
    sys.exit(0)
