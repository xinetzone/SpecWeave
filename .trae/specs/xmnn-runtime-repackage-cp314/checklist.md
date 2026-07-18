# XMNN Runtime cp314 重新打包 - 验证清单

## 环境准备检查
- [ ] Docker Desktop 正在运行，`docker ps` 可正常返回
- [ ] `nuitka-gcc-llvm` 镜像存在（或可通过 `inv image-build` 成功构建）
- [ ] 容器内 Python 版本确认为 3.14.x
- [ ] npu_tvm、npuusertools、notebook 源码目录完整
- [ ] 日志目录 `notebook/.agents/logs/` 已创建
- [ ] 报告目录 `notebook/.agents/reports/` 已创建

## Nuitka 构建检查
- [ ] `inv build -f` 执行成功，退出码为 0
- [ ] `inv nuitka` 执行成功，退出码为 0
- [ ] Nuitka 构建日志中无 ERROR 级别输出
- [ ] Nuitka 构建日志中无 Python 异常/Exception 输出
- [ ] `tvm.cpython-314-*.so` 已生成且大小 > 10MB
- [ ] `vta.cpython-314-*.so` 已生成且大小 > 1MB
- [ ] `xmnn.cpython-314-*.so` 已生成且大小 > 1MB
- [ ] `xmnn-*.whl` wheel 包已生成且大小 > 50MB
- [ ] 构建日志完整保存到 `notebook/.agents/logs/nuitka-build-*.log`

## 验证容器与 wheel 安装检查
- [ ] 持久化验证容器 `xmnn-validation` 已启动并处于 running 状态
- [ ] wheel 在容器内安装成功（`pip install` 退出码 0）
- [ ] 容器内 `import tvm; import vta; import xmnn` 基础导入测试通过
- [ ] 容器内 `TVM_FFI` 环境变量值为 `ctypes`
- [ ] 容器内 Python 版本为 3.14.x
- [ ] 遵循了所有 17 条不可变约束（notebook/.agents/constraints.md）

## ONNX (YOLOv5s) 模型编译检查
- [ ] 旧的 `temp/yolov5s/` 编译产物已清理
- [ ] `python compile.py -n yolov5s` 执行成功，退出码为 0
- [ ] 编译日志中 ERROR 数量为 0
- [ ] 编译日志中未预期 WARNING 数量为 0（白名单外无警告）
- [ ] `network.xmnn` 编译产物存在且大小 > 100KB
- [ ] `param.bin` 参数文件存在且大小 > 1MB
- [ ] 编译过程无 Python 异常抛出
- [ ] 编译日志完整保存到 `notebook/.agents/logs/compile-yolov5s-*.log`

## Caffe (ResNet50) 模型编译检查
- [ ] 旧的 `temp/resnet50/` 编译产物已清理
- [ ] `python compile.py -n resnet50` 执行成功，退出码为 0
- [ ] 编译日志中 ERROR 数量为 0
- [ ] 编译日志中未预期 WARNING 数量为 0
- [ ] `network.xmnn` 编译产物存在且大小 > 100KB
- [ ] `param.bin` 参数文件存在且大小 > 1MB
- [ ] 编译过程无 Python 异常抛出
- [ ] 编译日志完整保存到 `notebook/.agents/logs/compile-resnet50-*.log`

## ONNX (YOLOv5s) 精度测试检查
- [ ] `python accuracy.py -n yolov5s` 执行成功，退出码为 0
- [ ] `result.csv` 精度结果文件已生成
- [ ] result.csv 包含所有内部节点和输出节点的指标
- [ ] 所有输出层节点（output-*）余弦相似度 ≥ 0.99
- [ ] 所有 conv2d/dense/batch_matmul 内部节点余弦相似度 ≥ 0.95
- [ ] 节点级输出文件（*-float.txt、*-xmnn.txt）已保存
- [ ] 精度日志完整保存到 `notebook/.agents/logs/accuracy-yolov5s-*.log`
- [ ] 未达标节点（如有）已在报告中明确列出并标注差异值

## Caffe (ResNet50) 精度测试检查
- [ ] `python accuracy.py -n resnet50` 执行成功，退出码为 0
- [ ] `result.csv` 精度结果文件已生成
- [ ] result.csv 包含所有内部节点和输出节点的指标
- [ ] 所有输出层节点余弦相似度 ≥ 0.99
- [ ] 所有 conv2d/dense/batch_matmul 内部节点余弦相似度 ≥ 0.95
- [ ] 节点级输出文件已保存
- [ ] 精度日志完整保存到 `notebook/.agents/logs/accuracy-resnet50-*.log`
- [ ] 未达标节点（如有）已在报告中明确列出并标注差异值

## Runtime 打包产物检查
- [ ] `xmnn-runtime-1.2.1-fix-cp314.tar.gz` 已生成到 `notebook/xmnn/dist/`
- [ ] tar.gz 文件大小 > 100MB
- [ ] tar.gz 结构验证通过：包含 `oci-layout`、`index.json`、`manifest.json`
- [ ] tar.gz 包含 `blobs/sha256/` 目录及 blob 文件
- [ ] 旧的 tar.gz 已备份为 `.bak` 文件
- [ ] 文件 SHA256 校验值已计算并记录

## 打包报告检查
- [ ] 报告文件已保存到 `notebook/.agents/reports/packaging-report-YYYYMMDD.md`
- [ ] 报告包含环境信息章节（Python/Nuitka/LLVM 版本、镜像 tag、构建时间）
- [ ] 报告包含 Nuitka 构建摘要（时长、产物大小、错误/警告统计）
- [ ] 报告包含 YOLOv5s 编译结果章节（错误/警告统计、产物大小）
- [ ] 报告包含 YOLOv5s 精度结果章节（Markdown 表格、最低相似度节点、阈值验证结论）
- [ ] 报告包含 ResNet50 编译结果章节（同格式）
- [ ] 报告包含 ResNet50 精度结果章节（同格式）
- [ ] 报告包含最终产物信息（文件名、大小、SHA256）
- [ ] 报告包含结论章节（通过/失败状态、已知问题、建议）
- [ ] 精度数值精确到小数点后 6 位
- [ ] 所有日志文件路径在报告中正确引用

## 最终验证与清理检查
- [ ] tar.gz 可成功通过 `docker load` 或 skopeo 重新导入
- [ ] 导入后的容器内 `import tvm/vta/xmnn` 基础测试通过
- [ ] 验证容器 `xmnn-validation` 已清理（停止并删除）
- [ ] 临时编译产物按策略保留或清理（日志保留、模型产物保留用于复现）
- [ ] 所有任务状态在 tasks.md 中标记为完成 [x]
- [ ] 本 checklist 所有项目标记为通过 [x]（或标记为 N/A 并说明原因）
