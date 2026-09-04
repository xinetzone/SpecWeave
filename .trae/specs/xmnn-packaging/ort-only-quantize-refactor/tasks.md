# ORT-Only 量化方案重构 - The Implementation Plan (Decomposed and Prioritized Task List)

## [x] Task 1: 重构 Dockerfile — 移除 neural-compressor 必装依赖，NC 检查降级为可选 ✅
- **Priority**: high
- **Depends On**: None
- **Status**: Completed (commit ac11e143)
- **Changes**: 移除neural-compressor和onnxruntime-tools必装依赖；NC版本打印改为条件检查；NCIMPORT/NCUNIT块改为try/except可选；PACKAGES_INSTALLED标记NC为optional；添加COPY scripts/持久化目录；新增ORTREG回归测试块
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-7

## [x] Task 2: 调整 verify-deployment.py — INC 从必选降级为可选 ✅
- **Priority**: high
- **Depends On**: None
- **Status**: Completed (commit ac11e143)
- **Changes**: 拆分required/optional包列表；新增SKIP状态（⏭️图标）和统计；test_neural_compressor_imports()开头检查ImportError直接SKIP+return；docstring更新；main()汇总添加skipped计数
- **Acceptance Criteria Addressed**: AC-3

## [x] Task 3: 调整 Shell 脚本中的 INC 版本检查 ✅
- **Priority**: medium
- **Depends On**: None
- **Status**: Completed (commit ac11e143)
- **Changes**: verify-services.sh改为try/except容错；local-build.sh快速验证块改为try/except；test-onnx-quantized.sh的test_neural_compressor()改为nc-skip→pass而非fail
- **Acceptance Criteria Addressed**: AC-3, NFR-5

## [x] Task 4: 更新 onnx_quantize_kit 包的 __init__.py docstring 和模块注释 ✅
- **Priority**: medium
- **Depends On**: None
- **Status**: Completed (commit ac11e143)
- **Changes**: __init__.py添加📌量化引擎说明块；quantize.py模块docstring添加ORT唯一引擎说明；全局审计确认包内零neural_compressor导入
- **Acceptance Criteria Addressed**: AC-5, AC-10

## [x] Task 5: 生成 ORT 量化回归测试脚本 test_ort_quantization_regression.py ✅
- **Priority**: high
- **Depends On**: Task 4
- **Status**: Completed (commit ac11e143)
- **Changes**: 创建962行回归测试脚本，覆盖G1-G11共11组测试（包导入/动态INT8/静态QDQ/QOperator/FP16/auto_quantize管线/精度验证/性能基准/模型检测/零NC硬依赖/CI阈值）
- **Acceptance Criteria Addressed**: AC-4

## [x] Task 6: 更新文档（README.md 和 ADVANCED-QUANTIZATION-GUIDE.md） ✅
- **Priority**: medium
- **Depends On**: Task 1
- **Status**: Completed (commit ac11e143)
- **Changes**: README.md 6处更新（描述/预装表格/验证状态/策略矩阵/安装说明/依赖列表）；ADVANCED-QUANTIZATION-GUIDE.md 2处更新（添加📌量化引擎说明+链接说明）；.env.example更新NC版本注释
- **Acceptance Criteria Addressed**: AC-7

## [x] Task 7: 集成回归测试到 Dockerfile 构建流程 ✅
- **Priority**: medium
- **Depends On**: Task 5, Task 1
- **Status**: Completed (commit ac11e143)
- **Changes**: 添加COPY scripts/到/opt/devcontainer-scripts/持久位置；Stage3中在ORTUNIT后NCUNIT前插入ORTREG块（cp到/tmp/scripts+运行回归测试+失败中断构建）
- **Acceptance Criteria Addressed**: AC-2, AC-4

## [x] Task 8: 全局验证 — 零 INC 硬依赖审计 ✅
- **Priority**: high
- **Depends On**: Task 1-7
- **Status**: Completed (commit ac11e143)
- **Changes**: grep审计确认onnx_quantize_kit/零NC导入；scripts/无顶层import neural_compressor；Dockerfile无pip install neural-compressor；所有Python文件py_compile通过
- **Acceptance Criteria Addressed**: AC-5, AC-6, NFR-5

## [x] Task 9: 原子提交 ✅
- **Priority**: high
- **Depends On**: Task 8
- **Status**: Completed (commit ac11e143)
- **Changes**: 14文件变更，+1435/-75行；commit ac11e143；遵循Conventional Commits规范；预提交检查全部通过
- **Acceptance Criteria Addressed**: AC-8
