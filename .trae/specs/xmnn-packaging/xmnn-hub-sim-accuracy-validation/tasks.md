# Tasks

## 阶段 1：重新打包 xmnn Wheel
- [x] Task 1: 重新打包 xmnn wheel
  - [x] Subtask 1.1: 在 WSL（Ubuntu-24.04）中确认 `xmnn-dev:llvm22` 镜像存在、`/mnt/d/spaces/SpecWeave` 源码可挂载（Docker 29.6.1，镜像存在，源码可挂载）
  - [x] Subtask 1.2: 执行 `bash docker/dev-llvm22/build-and-test.sh --no-build` 增量重建 xmnn Nuitka 模块与 wheel（exit 0）
  - [x] Subtask 1.3: 验证 `xmtools/dist/xmnn-*.whl` 生成（`xmnn-1.2.1.dev0-cp314-cp314-linux_x86_64.whl`，181M）
  - [x] Subtask 1.4: 验证 wheel 9 项标准全通过（import tvm/vta/xmnn、_libs、libtvm.so、tvm.build(llvm)、relay/std、.pth 引导、xmnn data dirs）
  - [x] Subtask 1.5: 构建成功；已恢复 build 临时修改的 pyproject.toml 至原始状态

## 阶段 2：基于新 wheel 构建运行时 Docker 镜像
- [x] Task 2: 构建运行时镜像 `xmnn:1.2.1-hub-sim`
  - [x] Subtask 2.1: 确认 `xmtools/docker/runtime/miniconda.sh`/`build-runtime.sh` 存在
  - [x] Subtask 2.2: 执行 `bash docker/runtime/build-runtime.sh -t xmnn:1.2.1-hub-sim`（exit 0，镜像 4.37GB）
  - [x] Subtask 2.3: 验证镜像内 `verify_xmnn.py` 全部通过（import tvm/vta/xmnn、_libs、libtvm 加载、tvm.build）

## 阶段 3：枚举 hub/caffe 与 hub/onnx 完整产物模型
- [x] Task 3: 枚举完整产物模型
  - [x] Subtask 3.1: 编写/运行 hub 模型枚举服务脚本（`docker/runtime/enumerate_hub.py`，识别 config.toml + 模型文件 + dataset 完整，frontend 为 caffe/onnx）
  - [x] Subtask 3.2: 生成 `hub.caffe.<路径>` 与 `hub.onnx.<路径>` 模型名清单（60 个完整模型：30 caffe + 30 onnx，清单存 `build/hub_enum.txt`）
  - [x] Subtask 3.3: 列出不完整产物模型（`hub.onnx.car_model.track_all.test`：缺模型文件与 dataset）

## 阶段 4：仿真 target 下编译所有完整产物 hub 模型
- [x] Task 4: 仿真 target 编译
  - [x] Subtask 4.1: 备份 hub/caffe 与 hub/onnx 全部 config.toml 原始内容（30 caffe + 31 onnx → `build/hub_config_backup/`）
  - [x] Subtask 4.2: 批量 patch config.toml 为仿真 target（`compile.target="sim_vta2.0"`、`tune=false`），61 个全部生效
  - [x] Subtask 4.3: 修复 **caffe 假PASS bug**（`npuusertools/xmnn/compile_api.py` 第391行日志无条件访问 `model_file_path` 致 caffe 加载失败，改 `getattr` 兼容 caffemodel_file_path）；重新打包 wheel 并重建 `xmnn:1.2.1-hub-sim` 镜像
  - [x] Subtask 4.4: 用修复后镜像重跑全部 60 模型编译 → **PASS=49, FAIL=11**（日志 `build/compile_logs/`）
  - [x] Subtask 4.5: 验证 49 个 PASS 模型产物完整（network.xmnn + param.bin 全部存在）
  - [x] Subtask 4.6: 汇总失败清单与原因（量化失败/段错误 7、OOM 3、配置错误 1，见 compile-all-2.log）

## 阶段 5：仿真 target 下精度测试并汇总报告
- [ ] Task 5: 精度测试
  - [ ] Subtask 5.1: 对每个编译成功模型执行 `accuracy.py -n hub.<frontend>.<路径>`
  - [ ] Subtask 5.2: 收集每个模型的 `result.csv`（余弦相似度/MSE/MAE）
  - [ ] Subtask 5.3: 汇总为结构化精度对比表，产出 `build/xmnn-hub-sim-accuracy-report.md`

## 阶段 6：恢复 hub 模型原始 target
- [ ] Task 6: 恢复 config.toml
  - [ ] Subtask 6.1: 从备份恢复 hub/caffe 与 hub/onnx 全部 config.toml 原始 target/tune
  - [ ] Subtask 6.2: 验证 `git status` 无无关改动（仅 build/ 产出物与 .trae/specs 新增）

# Task Dependencies
- [Task 2] 依赖 [Task 1]（镜像基于新 wheel）
- [Task 3] 独立（可提前枚举）
- [Task 4] 依赖 [Task 2]（编译在新镜像中执行）与 [Task 3]（需模型清单）
- [Task 5] 依赖 [Task 4]（先编译后精度测试）
- [Task 6] 依赖 [Task 5]（测试结束后恢复）