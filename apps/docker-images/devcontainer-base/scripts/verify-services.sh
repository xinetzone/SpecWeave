#!/bin/bash
echo "=== Devuser access test ==="
docker exec onnx-quantized-test su - devuser -c 'source /etc/profile.d/onnx-pytorch-init.sh && /opt/conda/bin/python -c "import torch,onnx,onnxruntime;print(\"devuser torch:\", torch.__version__);print(\"devuser onnx:\", onnx.__version__);print(\"devuser ort:\", onnxruntime.__version__)"'
echo ""
echo "=== Container IP and ports ==="
docker exec onnx-quantized-test hostname -I
echo ""
echo "=== Jupyter process check ==="
docker exec onnx-quantized-test bash -c "ps aux | grep -i jupyter | grep -v grep || echo 'Jupyter may be managed by supervisord'"
echo ""
echo "=== Supervisord status ==="
docker exec onnx-quantized-test bash -c "supervisorctl status 2>/dev/null || echo 'supervisorctl not available yet'"
echo ""
echo "=== All core package versions ==="
docker exec onnx-quantized-test /opt/conda/bin/python -c "
import torch, torchvision, onnx, onnxruntime, onnxsim, onnxoptimizer, onnxscript
print('PyTorch:', torch.__version__)
print('TorchVision:', torchvision.__version__)
print('ONNX:', onnx.__version__)
print('ONNX Runtime:', onnxruntime.__version__)
print('ONNX Simplifier:', onnxsim.__version__)
print('ONNX Optimizer:', onnxoptimizer.__version__)
print('ONNX Script:', onnxscript.__version__)
try:
    import neural_compressor
    print('Neural Compressor:', neural_compressor.__version__, '(optional)')
except ImportError:
    print('Neural Compressor: not installed (optional - pip install neural-compressor for PyTorch quantization)')
print('CUDA available:', torch.cuda.is_available())
"
