# Tasks

## 阶段 1：重打包 xmnn Wheel
- [ ] Task 1: 重新打包 xmnn wheel
  - [ ] Subtask 1.1: 在 WSL 中执行 `bash docker/dev-llvm22/build-and-test.sh --no-build`（复用已构建 `xmnn-dev:llvm22` 镜像，增量重建 xmnn Nuitka 模块以纳入新 `caffe_pb2.py`）
  - [ ] Subtask 1.2: 验证 `xmtools/dist/xmnn-*.whl` 生成（版本号、大小）
  - [ ] Subtask 1.3: 验证 wheel 8 项标准（import tvm/vta/xmnn、_libs、libtvm.so、tvm.build(llvm)、relay/std、.pth 引导）
  - [ ] Subtask 1.4: 验证 wheel 内 `xmnn` Nuitka `.so` 包含更新后的 `caffe_pb2`（Caffe 前端可解析 prototxt/caffemodel）
  - [ ] Subtask 1.5: 若构建失败，收集错误并回退修复后重试（不进入下游）

## 阶段 2：基于新 wheel 构建运行时 Docker 镜像
- [ ] Task 2: 构建运行时镜像 `xmnn:1.2.1-new`
  - [ ] Subtask 2.1: 确认 `xmtools/docker/runtime/miniconda.sh`/`build-runtime.sh` 存在
  - [ ] Subtask 2.2: 执行 `bash docker/runtime/build-runtime.sh -t xmnn:1.2.1-new`
  - [ ] Subtask 2.3: 验证镜像内 `verify_xmnn.py` 全部通过
  - [ ] Subtask 2.4: 验证镜像内 Caffe 前端 `caffe_pb2` 可正常解析

## 阶段 3：枚举并编译三目录下所有完整产物模型
- [ ] Task 3: 枚举并编译完整产物模型
  - [ ] Subtask 3.1: 编写/运行模型枚举与编译服务脚本（识别 config.toml + 模型 + dataset 完整）
  - [ ] Subtask 3.2: 对每个完整产物模型执行 `compile.py -n <model>`
  - [ ] Subtask 3.3: 验证编译产物（network.xmnn / param.bin）生成
  - [ ] Subtask 3.4: 重点覆盖 Caffe 前端模型（验证 caffe_pb2 更新）
  - [ ] Subtask 3.5: 汇总编译报告

## 阶段 4：对编译成功模型执行精度测试
- [ ] Task 4: 精度测试
  - [ ] Subtask 4.1: 对每个编译成功模型执行 `accuracy.py -n <model>`
  - [ ] Subtask 4.2: 收集每个模型的 `result.csv`
  - [ ] Subtask 4.3: 汇总为结构化指标

## 阶段 5：与基准对比分析并产出报告
- [ ] Task 5: 对比分析并产出报告
  - [ ] Subtask 5.1: 将新镜像精度指标与基线（`xmnn:1.2.1-alpha`）对比
  - [ ] Subtask 5.2: 生成精度对比表
  - [ ] Subtask 5.3: 产出编译报告 + 精度对比报告
  - [ ] Subtask 5.4: 判断 `caffe_pb2.py` 更新是否引入精度回归

# Task Dependencies
- [Task 2] 依赖 [Task 1]（镜像基于新 wheel）
- [Task 3] 依赖 [Task 2]（编译在新镜像中执行）
- [Task 4] 依赖 [Task 3]（先编译后精度测试）
- [Task 5] 依赖 [Task 4]（对比需先有精度指标）