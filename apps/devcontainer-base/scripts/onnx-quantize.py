#!/usr/bin/env python3
"""
onnx-quantize CLI — 本地开发一键量化工具入口脚本

用法:
  python onnx-quantize.py model.onnx                    # 自动量化
  python onnx-quantize.py model.onnx -o out.onnx        # 指定输出
  python onnx-quantize.py model.onnx --info             # 查看模型信息
  python onnx-quantize.py model.onnx --dry-run          # 预览推荐策略
  python onnx-quantize.py model.onnx --strategy fp16    # 强制FP16
  python onnx-quantize.py --help                        # 查看全部选项
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from onnx_quantize_kit.cli import main

if __name__ == "__main__":
    sys.exit(main())
