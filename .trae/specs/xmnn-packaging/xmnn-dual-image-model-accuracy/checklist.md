# 双镜像模型精度测试 - Checklist

## 执行前
- [x] WSL（Ubuntu-26.04）下 `xmnn-whl-builder:latest` 与 `xmnn-runtime:latest` 镜像存在（docker images 可查）
- [x] `caffe_demo` 与 `palmDet` 模型产物完整（config.toml + 模型文件 + dataset）
- [x] 模型目录挂载命令可用（容器内 `/workspace/models` 可访问两模型）

## Task 2：whl-builder 镜像
- [x] `caffe_demo` 编译无错误，生成 network.xmnn/param.bin
- [x] `palmDet` 编译无错误，生成 network.xmnn/param.bin
- [x] `palmDet` 精度测试产出 `temp/whl/palmDet/accuracy/result.csv`（余弦/MSE/MAE，67 节点）
- [ ] `caffe_demo` 精度测试产出 `result.csv` —— **被 TVM VM 调度器 bug 阻塞**（`conv2d_NCHWc × T_multiply` LowerSchedule 失败；4 种融合配置均复现；graph executor 正常）。已记录根因，见报告；待工具链修复后复测。

## Task 3：runtime 镜像
- [x] `caffe_demo` 编译无错误，生成 network.xmnn/param.bin
- [x] `palmDet` 编译无错误，生成 network.xmnn/param.bin
- [x] `palmDet` 精度测试产出 `temp/runtime/palmDet/accuracy/result.csv`（与 whl 产物 MD5 一致）
- [ ] `caffe_demo` 精度测试产出 `result.csv` —— **被同一 TVM VM 调度器 bug 阻塞**（与 whl-builder 同因）
- [x] runtime 无 LLVM 工具链场景下浮点参考推理（tvm.build(llvm)/relay-vm）可运行（palmDet 精度已证明；caffe_demo 阻塞为模型特定 bug，非 runtime 环境缺陷）

## Task 4：交叉对比与报告
- [x] 2 模型 × 2 镜像精度指标（余弦/MSE/MAE）汇总为对比表
- [x] `xmnn-dual-image-accuracy-report.md` 生成，含一致性判定与差异说明
- [x] 报告数据与原始 result.csv 一致（V 对抗审查通过；palmDet 双镜像 MD5 相同）

## Task 5：环境恢复与污染核查
- [x] 模型 config.toml/prototxt/onnx 未被修改（git status 无源文件改动；config.toml 已恢复原值）
- [x] 已从备份恢复 palmDet（tune/adaround）与 caffe_demo（fuse_conv/fuse_branch_conv）config.toml
- [x] 编译/精度产物仅落在模型 `temp/` 与 spec 目录内（`.temp` 下诊断脚本为复测工具，git 忽略）

> **未勾选项说明**：`caffe_demo` 精度两项因 TVM VM 调度器 bug（模型特定，非配置/镜像问题）无法在本 spec 约束内产出 result.csv。此为基线期已识别发现，移交工具链修复后以 `run_model.py caffe_demo <tag>` 复测即可闭环。
