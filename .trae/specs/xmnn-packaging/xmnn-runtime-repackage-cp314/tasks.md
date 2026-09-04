# XMNN Runtime cp314 重新打包 - 实现计划

## [ ] Task 1: 环境预检与 Docker 镜像准备
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 检查 Docker Desktop 是否运行正常
  - 验证 `nuitka-gcc-llvm` 镜像是否存在，若不存在则执行 `inv image-build` 构建
  - 检查 npu_tvm、npuusertools、notebook 源码目录完整性
  - 创建日志和报告输出目录 `notebook/.agents/reports/` 和 `notebook/.agents/logs/`
  - 确认 Python 3.14 在容器内可用（`docker run --rm nuitka-gcc-llvm python --version`）
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: `docker ps` 返回正常容器列表，Docker daemon 可达
  - `programmatic` TR-1.2: `docker images nuitka-gcc-llvm` 返回非空结果
  - `programmatic` TR-1.3: 容器内 `python --version` 输出包含 "Python 3.14"
  - `programmatic` TR-1.4: 关键源码目录存在且非空（npu_tvm/CMakeLists.txt、npuusertools/compile.py、notebook/tasks.py）
- **Notes**: 如果 Docker 未启动需要提示用户启动 Docker Desktop

---

## [ ] Task 2: Nuitka 编译流水线执行（CMake + Nuitka）
- **Priority**: high
- **Depends On**: [Task 1]
- **Description**:
  - 在 notebook/ 目录下执行 `inv build -f`（强制 CMake 重建）
  - 执行 `inv nuitka` 完成 TVM/VTA/XMNN 的 Nuitka 编译和 wheel 打包
  - 将完整构建 stdout/stderr 日志保存到 `notebook/.agents/logs/nuitka-build-<timestamp>.log`
  - 记录构建开始/结束时间戳
  - 验证关键 .so 文件和 wheel 文件生成
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-2.1: `inv build` 退出码为 0，日志无 ERROR
  - `programmatic` TR-2.2: `inv nuitka` 退出码为 0，日志无 ERROR/EXCEPTION
  - `programmatic` TR-2.3: 存在 `xmnn/dist/tvm.cpython-314-*.so` 且文件大小 > 10MB
  - `programmatic` TR-2.4: 存在 `xmnn/dist/vta.cpython-314-*.so` 且文件大小 > 1MB
  - `programmatic` TR-2.5: 存在 `xmnn/dist/xmnn.cpython-314-*.so` 且文件大小 > 1MB
  - `programmatic` TR-2.6: 存在 `xmnn/dist/xmnn-*.whl` 且文件大小 > 50MB
  - `programmatic` TR-2.7: 构建日志文件已保存，大小 > 0
- **Notes**: 遵循 notebook/.agents/constraints.md 中的 17 条约束，特别是容器内执行要求

---

## [ ] Task 3: 启动验证容器并安装 wheel
- **Priority**: high
- **Depends On**: [Task 2]
- **Description**:
  - 基于 `nuitka-gcc-llvm` 启动一个名为 `xmnn-validation` 的持久化容器
  - 将 npuusertools 和 dist 目录挂载到容器内
  - 在容器内安装新编译的 wheel：`pip install /work/dist/xmnn-*.whl --force-reinstall`
  - 验证基础导入：`python -c "import tvm; import vta; import xmnn; print('All imports OK')"`
  - 验证 TVM_FFI 环境变量为 ctypes
  - 验证容器内 Python 版本为 3.14
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-3.1: 容器 `xmnn-validation` 处于 running 状态
  - `programmatic` TR-3.2: wheel 安装退出码为 0
  - `programmatic` TR-3.3: 基础导入测试输出 "All imports OK"
  - `programmatic` TR-3.4: `echo $TVM_FFI` 在容器内返回 "ctypes"
  - `programmatic` TR-3.5: `python --version` 在容器内返回 3.14.x
- **Notes**: 容器需保持运行以支持后续模型编译和精度测试步骤

---

## [ ] Task 4: ONNX (YOLOv5s) 模型编译验证
- **Priority**: high
- **Depends On**: [Task 3]
- **Description**:
  - 在验证容器内，切换到 npuusertools 工作目录
  - 清理之前的临时编译产物（`temp/yolov5s/`）
  - 执行模型编译：`python compile.py -n yolov5s`
  - 将编译日志保存到 `notebook/.agents/logs/compile-yolov5s-<timestamp>.log`
  - 分析日志：统计 ERROR、WARNING 数量
  - 验证编译产物：`temp/yolov5s/compile/network.xmnn` 和 `param.bin`
  - 建立 WARNING 白名单（收集已知无害警告作为基线）
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `programmatic` TR-4.1: compile.py 退出码为 0
  - `programmatic` TR-4.2: 编译日志中 ERROR 数量为 0
  - `programmatic` TR-4.3: 未预期 WARNING 数量为 0（白名单外的 WARNING 需人工确认）
  - `programmatic` TR-4.4: `network.xmnn` 文件存在且大小 > 100KB
  - `programmatic` TR-4.5: `param.bin` 文件存在且大小 > 1MB
  - `programmatic` TR-4.6: 日志文件已保存
- **Notes**: 若出现非白名单 WARNING，记录到报告并暂停评估是否需要修复

---

## [ ] Task 5: Caffe (ResNet50) 模型编译验证
- **Priority**: high
- **Depends On**: [Task 3]
- **Description**:
  - 在验证容器内执行 Caffe ResNet50 模型编译
  - 清理之前的临时编译产物（`temp/resnet50/`）
  - 执行模型编译：`python compile.py -n resnet50`
  - 将编译日志保存到 `notebook/.agents/logs/compile-resnet50-<timestamp>.log`
  - 分析日志：统计 ERROR、WARNING 数量
  - 验证编译产物：`temp/resnet50/compile/network.xmnn` 和 `param.bin`
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `programmatic` TR-5.1: compile.py 退出码为 0
  - `programmatic` TR-5.2: 编译日志中 ERROR 数量为 0
  - `programmatic` TR-5.3: 未预期 WARNING 数量为 0
  - `programmatic` TR-5.4: `network.xmnn` 文件存在且大小 > 100KB
  - `programmatic` TR-5.5: `param.bin` 文件存在且大小 > 1MB
  - `programmatic` TR-5.6: 日志文件已保存
- **Notes**: Caffe 前端依赖 protobuf，确保容器内 caffe 相关依赖可用

---

## [ ] Task 6: ONNX (YOLOv5s) 精度测试验证
- **Priority**: high
- **Depends On**: [Task 4]
- **Description**:
  - 在验证容器内执行 YOLOv5s 精度测试
  - 执行：`python accuracy.py -n yolov5s`
  - 将精度测试日志保存到 `notebook/.agents/logs/accuracy-yolov5s-<timestamp>.log`
  - 验证 `temp/yolov5s/accuracy/result.csv` 文件生成
  - 解析 result.csv，提取所有节点的余弦相似度、MSE、MAE
  - 验证输出层余弦相似度 ≥ 0.99
  - 验证所有内部 conv2d/dense/batch_matmul 节点余弦相似度 ≥ 0.95
  - 收集不达标节点信息（如有）
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `programmatic` TR-6.1: accuracy.py 退出码为 0
  - `programmatic` TR-6.2: result.csv 文件存在且包含所有节点指标
  - `programmatic` TR-6.3: 输出层节点（output-*）余弦相似度最小值 ≥ 0.99
  - `programmatic` TR-6.4: 所有 conv2d/dense/batch_matmul 节点余弦相似度最小值 ≥ 0.95
  - `programmatic` TR-6.5: 节点输出文本文件（*-float.txt、*-xmnn.txt）已保存
  - `programmatic` TR-6.6: 精度日志已保存
- **Notes**: 精度不达标时记录详细差异，但不自动修复——仅报告

---

## [ ] Task 7: Caffe (ResNet50) 精度测试验证
- **Priority**: high
- **Depends On**: [Task 5]
- **Description**:
  - 在验证容器内执行 ResNet50 精度测试
  - 执行：`python accuracy.py -n resnet50`
  - 将精度测试日志保存到 `notebook/.agents/logs/accuracy-resnet50-<timestamp>.log`
  - 验证 `temp/resnet50/accuracy/result.csv` 文件生成
  - 解析 result.csv，同 Task 6 的阈值验证标准
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `programmatic` TR-7.1: accuracy.py 退出码为 0
  - `programmatic` TR-7.2: result.csv 文件存在且包含所有节点指标
  - `programmatic` TR-7.3: 输出层节点余弦相似度最小值 ≥ 0.99
  - `programmatic` TR-7.4: 所有 conv2d/dense/batch_matmul 节点余弦相似度最小值 ≥ 0.95
  - `programmatic` TR-7.5: 节点输出文本文件已保存
  - `programmatic` TR-7.6: 精度日志已保存
- **Notes**: ResNet50 是分类模型，输出层精度要求同样严格

---

## [ ] Task 8: Runtime 镜像导出与 tar.gz 打包
- **Priority**: high
- **Depends On**: [Task 6, Task 7]
- **Description**:
  - 停止验证容器
  - 基于验证通过的环境构建 runtime 镜像（或从现有容器 commit）
  - 按照现有 OCI layout 格式导出镜像为 tar.gz
  - 使用 `skopeo copy` 或 `docker save` + OCI 转换工具生成 `xmnn-runtime-1.2.1-fix-cp314.tar.gz`
  - 如已有导出脚本则复用，否则手动按 OCI image-spec 格式打包
  - 计算最终产物的 SHA256 校验值
  - 备份旧的 tar.gz 为 `.bak` 后替换
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `programmatic` TR-8.1: tar.gz 文件存在于 `notebook/xmnn/dist/` 目录
  - `programmatic` TR-8.2: 文件大小 > 100MB
  - `programmatic` TR-8.3: `tar -tzf` 列出内容包含 `oci-layout`、`index.json`、`manifest.json`
  - `programmatic` TR-8.4: `blobs/sha256/` 目录下有 blob 文件
  - `programmatic` TR-8.5: SHA256 校验值已计算并记录
- **Notes**: 需要调查现有 runtime tar.gz 的具体导出方式（查看 notebook/tasks.py 是否有 export 命令）

---

## [ ] Task 9: 打包报告生成
- **Priority**: high
- **Depends On**: [Task 8]
- **Description**:
  - 汇总所有阶段日志和数据
  - 生成 Markdown 格式的打包报告，包含以下章节：
    1. 概述与环境信息（时间、Python/Nuitka/LLVM 版本、镜像信息）
    2. Nuitka 构建摘要（构建时长、关键产物大小、错误/警告统计）
    3. YOLOv5s (ONNX) 编译结果（错误/警告统计、产物大小、关键日志片段）
    4. YOLOv5s (ONNX) 精度结果（汇总表格、最低余弦相似度节点、阈值验证结论）
    5. ResNet50 (Caffe) 编译结果（同格式）
    6. ResNet50 (Caffe) 精度结果（同格式）
    7. 最终产物信息（文件名、大小、SHA256）
    8. 结论（通过/失败、已知问题、后续建议）
  - 报告保存到 `notebook/.agents/reports/packaging-report-YYYYMMDD.md`
  - 清理验证容器（`docker rm -f xmnn-validation`）
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 报告结构完整，包含上述所有章节
  - `programmatic` TR-9.2: 报告文件存在且大小 > 5KB
  - `human-judgement` TR-9.3: 精度数据以 Markdown 表格形式呈现，数值精确到 6 位小数
  - `human-judgement` TR-9.4: 错误/警告有明确统计数字，非模糊描述
  - `programmatic` TR-9.5: 验证容器已清理（`docker ps -a --filter name=xmnn-validation` 返回空）
- **Notes**: 报告模板可参考 notebook/.agents/postmortems/ 下的现有文档格式

---

## [ ] Task 10: 最终验证与清理
- **Priority**: medium
- **Depends On**: [Task 9]
- **Description**:
  - 验证 tar.gz 可通过 `docker load` 或 skopeo 重新导入
  - 简单 sanity check：导入后容器内可正确 import tvm/vta/xmnn
  - 确认所有日志文件已保存
  - 更新本 spec 中 Open Questions 的答案（如有发现）
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `programmatic` TR-10.1: tar.gz 可成功导入（使用 skopeo 或 docker load 测试）
  - `programmatic` TR-10.2: 导入后容器基础导入测试通过
  - `programmatic` TR-10.3: 所有日志文件路径在报告中正确引用
- **Notes**: 可复现性的全面重测不在此任务范围内，仅做导入 sanity check
