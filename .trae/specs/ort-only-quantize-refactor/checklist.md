# ORT-Only 量化方案重构 - Verification Checklist

## Dockerfile 重构验证
- [ ] Dockerfile Stage 2 pip install 列表中不再包含 `neural-compressor`
- [ ] Dockerfile Stage 2 版本打印块中 NC 版本检查有容错逻辑（失败时显示 "not installed"）
- [ ] Dockerfile LABEL 中 quantization 字段准确反映工具链（onnxruntime 为核心）
- [ ] Dockerfile Stage 3 NCIMPORT 块使用 try/except 处理 ImportError，NC 缺失时不中断构建
- [ ] Dockerfile Stage 3 NCUNIT 块为条件执行（仅当 INC 可用时运行）
- [ ] Dockerfile Stage 3 新增 ORTREGRESSION 块运行回归测试，且为必过测试
- [ ] Dockerfile build-info 中 NEURAL_COMPRESSOR_VERSION 为条件字段
- [ ] Dockerfile 注释清晰说明 NC 为可选扩展及手动安装命令
- [ ] PACKAGES_INSTALLED 标签中 neural-compressor 标记为 optional

## verify-deployment.py 调整验证
- [ ] neural_compressor 从必选包列表移至可选包列表
- [ ] 可选包导入失败时状态为 SKIP（非 FAIL）
- [ ] test_neural_compressor_imports() 函数开头检查 INC 可用性，不可用时优雅跳过
- [ ] 文件头 docstring 更新说明 NC 为 optional
- [ ] 脚本在无 INC 环境中运行退出码为 0

## Shell 脚本调整验证
- [ ] verify-services.sh 中 NC 导入有 2>/dev/null 或 try/except 容错
- [ ] local-build.sh 中 NC 版本打印有容错逻辑
- [ ] variants/scripts/test-onnx-quantized.sh 中 test_neural_compressor() 不可导入时 skip 而非 fail
- [ ] variants/build.sh 中 NC 引用调整为可选（如有硬依赖）

## onnx_quantize_kit 包验证
- [ ] __init__.py 的 __all__ 导出列表无 INC 相关符号
- [ ] __init__.py docstring 明确说明基于 onnxruntime.quantization
- [ ] quantize.py 顶部注释说明仅使用 ORT API，不依赖 INC
- [ ] grep onnx_quantize_kit/ 目录无 import neural_compressor（注释除外）

## 回归测试脚本验证
- [ ] test_ort_quantization_regression.py 已创建在 scripts/ 目录
- [ ] 脚本中无任何 neural_compressor import
- [ ] 脚本覆盖 dynamic/static_qdq/static_qoperator/fp16/auto 五种策略
- [ ] 脚本至少测试 MLP + Transformer/CNN 两种模型类型
- [ ] 所有精度断言包含 cosine_sim 和 max_diff 阈值
- [ ] 脚本通过 python -m py_compile 语法检查
- [ ] 脚本可在仅安装 onnxruntime+onnx+numpy 的环境中运行

## 文档更新验证
- [ ] README.md 工具链概述明确 ORT 为唯一核心量化引擎
- [ ] README.md 预装包列表中 NC 标注为 optional/not pre-installed
- [ ] README.md INC 示例代码标注为"PyTorch场景手动安装后使用"
- [ ] README.md 包含"为什么不默认安装 INC"的简要说明
- [ ] ADVANCED-QUANTIZATION-GUIDE.md 中无将 INC 作为 ONNX 主要方案的描述
- [ ] 文档中安装命令示例不含 neural-compressor（可选安装段落除外）

## 全局依赖审计验证
- [ ] scripts/ 目录下 grep "import neural_compressor" 仅出现在 test_neural_compressor.py、try/except 块、注释中
- [ ] onnx_quantize_kit/ 目录零 INC import（注释除外）
- [ ] ci-requirements.txt 不包含 neural-compressor
- [ ] 所有核心入口脚本（onnx-quantize.py, batch_quantize.py, ci_quantization_gate.py）可在无 INC 环境下正常 import
- [ ] 所有修改过的 .py 文件通过 python -m py_compile

## 原子提交验证
- [ ] 所有相关变更已 staged
- [ ] Commit message 遵循 Conventional Commits（refactor(quantize): ...）
- [ ] git diff --cached 无意外变更
- [ ] 单次原子提交包含所有相关文件变更
