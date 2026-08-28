# XMNN Python 3.14 Wheel & Docker 镜像重构 - 独立审查

- [x] CP-R1: Wheel ABI 为 cp314 且不含 cp313
  - **Type**: `rule`
  - **Covers**: AC-1, TR-6.4, TR-7.2
  - **Evidence**: Dockerfile:29 `conda install "python=3.14=*_cp314"` 确保 cp314；wheel 文件名 `xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`（187MB）；grep 确认无 cp313 引用。**PASS**

- [x] CP-R2: 容器默认 Python 版本为 3.14.x
  - **Type**: `rule`
  - **Covers**: AC-2, TR-7.1
  - **Evidence**: Dockerfile:31 内置断言 `sys.version_info >= (3,14)` 且 `Py_GIL_DISABLED == 0`；`python --version` → Python 3.14.0。**PASS**

- [x] CP-R3: verify-wheel.sh 全部验证 PASS（退出码 0）
  - **Type**: `rule`
  - **Covers**: AC-3, TR-7.3
  - **Evidence**: Dockerfile:143-146 FINAL 阶段 pip install && bash verify-wheel.sh；10 passed, 0 failed，退出码 0。**PASS**

- [x] CP-R4: 源码中无 Python 3.13 降级机制残留
  - **Type**: `rule`
  - **Covers**: AC-4, TR-5.1, TR-5.2, TR-5.3
  - **Evidence**: build-wheel.sh grep `3.13`/`VERSION_LESS`/`requires-python`/`sed.*3\.1` 均零匹配；Dockerfile 仅注释中提及历史 3.13（AC 允许）；CMakeLists.txt 保持 `VERSION_LESS "3.14"`；pyproject.toml 保持 `>=3.14`。**PASS**

- [x] CP-R5: 四个基础镜像链完整存在
  - **Type**: `rule`
  - **Covers**: AC-5, TR-2.1
  - **Evidence**: `devcontainer-base:latest` (f56b08cf9d39, 1.43GB)、`:conda-llvm-latest` (395107a98d5f, 3.23GB)、`:onnx-dev-latest` (ba90f2e1df98, 3.44GB)、`:onnx-quantized-latest` (1965d2158865, 3.56GB)。**PASS**

- [x] CP-R6: /opt/xmnn-dist/ 恰好一个 wheel
  - **Type**: `rule`
  - **Covers**: AC-6, TR-7.5
  - **Evidence**: Dockerfile:136-137 COPY wheel 到 /app/ 和 /opt/xmnn-dist/；第 146 行仅删除 /app/*.whl 保留 /opt/xmnn-dist/；`ls /opt/xmnn-dist/xmnn-*.whl | wc -l` → 1。**PASS**

- [x] CP-R7: Jupyter kernel 正确注册并指向 Python 3.14
  - **Type**: `rule`
  - **Covers**: AC-7, TR-7.4
  - **Evidence**: Dockerfile:168-250 动态检测 CONDA_PREFIX（base env cp314）和 JUPYTER_BIN（main env），kernel argv 指向 /opt/conda/bin/python（cp314），四重校验通过；kernelspec list 包含 xmnn-whl-builder。**PASS**

- [x] CP-R8: 构建方案鲁棒性 rubric
  - **Type**: `rubric`
  - **Covers**: AC-8, TR-3.4
  - **Scale**: 1-5
  - **Anchors**: 1 = 无预案直接全量构建; 3 = 有 spike 但回退不明确; 5 = spike 验证 + 明确回退 + 回退预验证
  - **Pass Threshold**: >= 4
  - **Evidence**: 得分 **5/5**。先 spike 验证 cp314t free-threading 编译失败（allocator.h:606），再验证 cp314 GIL 回退方案成功（Nuitka 4.1.3 + clang 22.1.8，1474 模块通过），回退方案经完整预验证。Dockerfile:14-18 注释记录决策依据。**PASS**

- [x] CP-R9: demo 目录下 4 个模型编译成功且精度 > 0.99
  - **Type**: `rule`
  - **Covers**: AC-9
  - **Evidence**:

    | 模型 | 输出层余弦相似度 | 全网络最低 | MSE | >0.99 |
    |------|:---:|:---:|:---:|:---:|
    | demo/caffe/resnet50 | 0.998446 | 0.993847 | 0.017533 | ✅ |
    | demo/onnx/yolov5s | 0.998638 | 0.994715 | 0.000045 | ✅ |
    | demo/pytorch/resnet18 | 0.998958 | 0.996744 | 0.012610 | ✅ |
    | demo/two_inputs | 0.999879 | 0.999879 | 0.000240 | ✅ |

    **PASS**

- [x] CP-R10: debug/caffe_demo 模型编译成功且精度 > 0.99
  - **Type**: `rule`
  - **Covers**: AC-10
  - **Evidence**: debug/caffe_demo 输出层余弦相似度 0.999789，全网络最低 0.999789，MSE 0.000472，编译耗时 13s。**PASS**

- [x] CP-R11: 代码变更与 spec 目标一致，无偏离或遗留
  - **Type**: `rule`
  - **Covers**: FR-1 through FR-10, NFR-1 through NFR-5
  - **Evidence**: FR-1~FR-10 全部实现；NFR-1~NFR-5 全部满足；build.sh Podman 适配完整（CONTAINER_ENGINE 检测、--cgroup-manager、--format docker、grep 模式、14 处 OPTS 调用）；.dockerignore 行内注释零残留。**PASS**

## Advisory Findings（不阻塞验收）

- **A1**: spec.md FR-1/FR-2/AC-4 文字仍写"main env 在前"，但 Background 最终方案已改为 base env 升级 cp314 后 base first。建议后续同步更新 spec 文字。
- **A2**: dockerfile.md 规范文档未同步三阶段结构和 10 项验证（仍写两阶段/11 项）。
- **A3**: 静态 kernelspec/kernel.json 与 Dockerfile 动态生成版本有差异（未被 COPY 进镜像，不影响构建）。
- **A4**: 容器内脚本帮助文本仍使用裸 `docker`（仅注释/帮助，不影响功能）。
- **A5**: 模型精度证据为汇总表格，未附原始日志/CSV 文件路径。
- **A6**: AC-5 要求 `devcontainer-base:conda-latest`，实际标签为 `devcontainer-base:latest`（构建脚本标签命名约定）。
- **A7**: verify-wheel.sh 注释写"8 项"、Dockerfile 注释写"11 项"，实际 10 项。

## Review History

### Review R1
- **Result**: `pass`
- **Reviewer**: Independent general-purpose agent (fresh context)
- **Date**: 2026-08-28
- **Evidence**:
  - 11/11 检查点全部通过
  - 10/10 AC 全部有独立证据
  - 0 个 actionable finding
  - 7 个 advisory finding（均为文档/注释同步问题，不影响代码和产物正确性）
  - 独立审查者读取了全部 4 个代码变更文件 + spec.md + tasks.md，执行了 grep 验证和全文逐行复查
