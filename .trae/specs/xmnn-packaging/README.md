# xmnn-packaging — XMNN 打包与量化

XMNN 打包与量化：wheel 构建、Nuitka 打包、运行时镜像、模型精度验证 spec。

**Spec 数量**：40
**上级看板**：[返回全局执行看板](../README.md)

---

## &#128451; 主题说明

- **归属判定**：XMNN 打包与量化：wheel 构建、Nuitka 打包、运行时镜像、模型精度验证 spec
- **新增 Spec 流程**：先查重 → 创建三件套 → 全局看板由 docgen（C-6）自动刷新

*本看板由 Python 脚本于 2026-09-04 生成（C-2b），后续应由 docgen 自动化维护（C-6）。*

<!-- THEME_DASHBOARD_START -->

| # | Spec 名称 | 状态 | 三件套 |
|---|---|---|---|
| 1 | [add-onnx-pytorch-variant](add-onnx-pytorch-variant/spec.md) | ? 待启动 | ✓/✗ |
| 2 | [camera-power-automation-testing](camera-power-automation-testing/spec.md) | ? 待启动 | ✓/✗ |
| 3 | [chaos-ai-xmnn-releases](chaos-ai-xmnn-releases/spec.md) | ✓ 完成 | ✓/✗ |
| 4 | [chaos-ai-xmnn-whl-builder](chaos-ai-xmnn-whl-builder/spec.md) | ! 进行中 | ✓/✗ |
| 5 | [fix-xmnn-whl-data-dirs](fix-xmnn-whl-data-dirs/spec.md) | ✓ 完成 | ✓/✗ |
| 6 | [migrate-xmnn-builder-to-jupyter](migrate-xmnn-builder-to-jupyter/spec.md) | ✓ 完成 | ✓/✗ |
| 7 | [npu-ffi-optimization](npu-ffi-optimization/spec.md) | ✓ 完成 | ✓/✗ |
| 8 | [npu-ffi-vta](npu-ffi-vta/spec.md) | ✓ 完成 | ✓/✗ |
| 9 | [npu-tvm-nuitka-packaging](npu-tvm-nuitka-packaging/spec.md) | ✓ 完成 | ✓/✗ |
| 10 | [npuusertools-packaging-env](npuusertools-packaging-env/spec.md) | ✓ 完成 | ✓/✗ |
| 11 | [nuitka-scripts-migration](nuitka-scripts-migration/spec.md) | ✓ 完成 | ✓/✗ |
| 12 | [onnx-adaround-library](onnx-adaround-library/spec.md) | ✓ 完成 | ✓/✗ |
| 13 | [onnx-adaround-relocate](onnx-adaround-relocate/spec.md) | ✓ 完成 | ✓/✗ |
| 14 | [ort-only-quantize-refactor](ort-only-quantize-refactor/spec.md) | ✓ 完成 | ✓/✗ |
| 15 | [publish-xs-cli-pypi](publish-xs-cli-pypi/spec.md) | ! 进行中 | ✓/✗ |
| 16 | [vta-hw-doc-audit](vta-hw-doc-audit/spec.md) | ? 待启动 | ✓/✗ |
| 17 | [vta-hw-rewrite-18-docs](vta-hw-rewrite-18-docs/spec.md) | ✓ 完成 | ✓/✗ |
| 18 | [xmnn-client-directory](xmnn-client-directory/spec.md) | ? 待启动 | ✓/✗ |
| 19 | [xmnn-docker-runtime-image-wsl](xmnn-docker-runtime-image-wsl/spec.md) | ! 进行中 | ✓/✗ |
| 20 | [xmnn-dual-image-model-accuracy](xmnn-dual-image-model-accuracy/spec.md) | ! 进行中 | ✓/✗ |
| 21 | [xmnn-failure-models-analysis](xmnn-failure-models-analysis/spec.md) | ✓ 完成 | ✓/✗ |
| 22 | [xmnn-hub-sim-accuracy-validation](xmnn-hub-sim-accuracy-validation/spec.md) | ! 进行中 | ✓/✗ |
| 23 | [xmnn-nuitka-scikit-build-packaging](xmnn-nuitka-scikit-build-packaging/spec.md) | ? 待启动 | ✓/✗ |
| 24 | [xmnn-nuitka-whl](xmnn-nuitka-whl/spec.md) | ✓ 完成 | ✓/✗ |
| 25 | [xmnn-package-docker-release](xmnn-package-docker-release/spec.md) | ! 进行中 | ✓/✗ |
| 26 | [xmnn-project-refactor](xmnn-project-refactor/spec.md) | ✓ 完成 | ✓/✗ |
| 27 | [xmnn-py314-rebuild](xmnn-py314-rebuild/spec.md) | ? 待启动 | ✓✗✗ |
| 28 | [xmnn-pyproject-deps-audit](xmnn-pyproject-deps-audit/spec.md) | ✓ 完成 | ✓/✗ |
| 29 | [xmnn-repackage-docker-model-validation](xmnn-repackage-docker-model-validation/spec.md) | ? 待启动 | ✓/✗ |
| 30 | [xmnn-runtime-image](xmnn-runtime-image/spec.md) | ✓ 完成 | ✓/✗ |
| 31 | [xmnn-runtime-pytorch-model-validation](xmnn-runtime-pytorch-model-validation/spec.md) | ! 进行中 | ✓/✗ |
| 32 | [xmnn-runtime-repackage-cp314](xmnn-runtime-repackage-cp314/spec.md) | ? 待启动 | ✓/✗ |
| 33 | [xmnn-selfcontained-package](xmnn-selfcontained-package/spec.md) | ! 进行中 | ✓/✗ |
| 34 | [xmnn-whl-build-workflow-tutorial](xmnn-whl-build-workflow-tutorial/spec.md) | ✓ 完成 | ✓/✗ |
| 35 | [xmnn-whl-builder-jupyter-start](xmnn-whl-builder-jupyter-start/spec.md) | ✓ 完成 | ✓/✗ |
| 36 | [xmnn-whl-clean-rebuild](xmnn-whl-clean-rebuild/spec.md) | ! 进行中 | ✓/✗ |
| 37 | [xmnn-whl-docker-rebuild](xmnn-whl-docker-rebuild/spec.md) | ✓ 完成 | ✓/✗ |
| 38 | [xmtools-customer-distribution-docs](xmtools-customer-distribution-docs/spec.md) | ✓ 完成 | ✓/✗ |
| 39 | [xmtools-python314-requirement](xmtools-python314-requirement/spec.md) | ✓ 完成 | ✓/✗ |
| 40 | [xmtools-repackage-sim-accuracy-20260806](xmtools-repackage-sim-accuracy-20260806/spec.md) | ? 待启动 | ✓/✗ |

<!-- THEME_DASHBOARD_END -->
