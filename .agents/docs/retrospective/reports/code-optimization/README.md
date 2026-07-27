# 代码优化复盘报告索引

本目录存放代码优化/重构类任务的复盘报告。

| 报告 | 日期 | 核心内容 | 萃取模式 |
|------|------|---------|---------|
| [retrospective-caffe-ops-library-extraction-20260727](retrospective-caffe-ops-library-extraction-20260727/README.md) | 2026-07-27 | Caffe算子测试库提取与网络级测试集成：从TVM测试文件提取23个Caffe单算子+4个网络级端到端测试，原子化拆分为33个文件1557行，移除TVM依赖 | 跨框架测试用例提取模式、测试目录两级架构模式、预训练模型缓存下载模式 |
| [retrospective-caffe-slim-batch-inference-mnist-20260727](retrospective-caffe-slim-batch-inference-mnist-20260727/README.md) | 2026-07-27 | Caffe-Slim MNIST批量推理优化 | - |
| [retrospective-caffe-slim-inference-notebook-20260727](retrospective-caffe-slim-inference-notebook-20260727/README.md) | 2026-07-27 | Caffe-Slim推理Notebook开发 | - |
| [retrospective-caffe-slim-tvm-ffi-20260723](retrospective-caffe-slim-tvm-ffi-20260723/README.md) | 2026-07-23 | Caffe-Slim TVM FFI集成 | - |
| [retrospective-pycaffe-image-preprocessing-20260723](retrospective-pycaffe-image-preprocessing-20260723/README.md) | 2026-07-23 | PyCaffe图像预处理 | - |
| [retrospective-caffe-rmsnorm-transpose-removal-20260721](retrospective-caffe-rmsnorm-transpose-removal-20260721/README.md) | 2026-07-21 | Caffe Frontend RMSNorm冗余transpose移除：基于错误API假设引入2个冗余transpose，验证后移除，代码15行→6行 | API参考验证模式（L2）、TryPrepare判定准备合并模式（L2） |
