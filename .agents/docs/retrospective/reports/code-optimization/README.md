# 代码优化复盘报告索引

本目录存放代码优化/重构类任务的**具体里程碑复盘报告**。

## 里程碑报告

| 报告 | 日期 | 核心内容 | 萃取模式 |
|------|------|---------|---------|
| [retrospective-split-zerocopy-cow-milestone-20260731](retrospective-split-zerocopy-cow-milestone-20260731/README.md) | 2026-07-31 | Split层零拷贝优化Phase 1+2完整里程碑：Phase 1 N=1零拷贝捷径（ShareData/ShareDiff、14个C++测试、ZEROCOPY路径）+ Phase 2 N≥2 COW机制（cpu_mutable_data/cpu_mutable_diff、const/non-const分离、19个C+++22个Python测试）+ 工程配套（OpenBLAS跨平台CMake检测、构建预检脚本、TypeTraits冲突修复），共萃取4个代码模式+1个方法论模式；配套文档：[insight-extraction.md](retrospective-split-zerocopy-cow-milestone-20260731/insight-extraction.md)（50事实+5洞察） | FFI-Intrusive-RefCount-ZeroCopy、Const-COW-Trigger、Platform-Aware-Dependency-Detect、Preflight-Checks-Script、Phased-Incremental-Optimization |
| [retrospective-caffe-slim-bvlc-logging-20260727](retrospective-caffe-slim-bvlc-logging-20260727/README.md) | 2026-07-27 | Caffe-Slim BVLC兼容层日志系统增强：C++ tvm-ffi类型注册冲突修复+Docker Python3.14/GCC14兼容性问题解决+Python核心路径8个关键位置日志埋点+Docker端到端验证 | 容器化AI服务结构化日志埋点模式（L1）、前沿编译器/解释器版本兼容性最小修复法（L2） |
| [retrospective-caffe-ops-library-extraction-20260727](retrospective-caffe-ops-library-extraction-20260727/README.md) | 2026-07-27 | Caffe算子测试库提取与网络级测试集成：从TVM测试文件提取23个Caffe单算子+4个网络级端到端测试，原子化拆分为33个文件1557行，移除TVM依赖 | 跨框架测试用例提取模式、测试目录两级架构模式、预训练模型缓存下载模式 |
| [retrospective-caffe-slim-batch-inference-mnist-20260727](retrospective-caffe-slim-batch-inference-mnist-20260727/README.md) | 2026-07-27 | Caffe-Slim MNIST批量推理优化 | - |
| [retrospective-caffe-slim-inference-notebook-20260727](retrospective-caffe-slim-inference-notebook-20260727/README.md) | 2026-07-27 | Caffe-Slim推理Notebook开发 | - |
| [retrospective-caffe-slim-bvlc-compat-20260727](retrospective-caffe-slim-bvlc-compat-20260727/README.md) | 2026-07-27 | Caffe-Slim BVLC PyCaffe API兼容层：C++8个tvm-ffi元数据接口+Python代理类/猴子补丁两层架构，支持net.blobs/net.forward()dict/net.layers/net.params零拷贝访问 | 可选API兼容层模式（L1）、零拷贝数据代理模式（L1） |
| [retrospective-caffe-slim-tvm-ffi-20260723](retrospective-caffe-slim-tvm-ffi-20260723/README.md) | 2026-07-23 | Caffe-Slim TVM FFI集成 | - |
| [retrospective-pycaffe-image-preprocessing-20260723](retrospective-pycaffe-image-preprocessing-20260723/README.md) | 2026-07-23 | PyCaffe图像预处理 | - |
| [retrospective-caffe-rmsnorm-transpose-removal-20260721](retrospective-caffe-rmsnorm-transpose-removal-20260721/README.md) | 2026-07-21 | Caffe Frontend RMSNorm冗余transpose移除：基于错误API假设引入2个冗余transpose，验证后移除，代码15行→6行 | API参考验证模式（L2）、TryPrepare判定准备合并模式（L2） |
