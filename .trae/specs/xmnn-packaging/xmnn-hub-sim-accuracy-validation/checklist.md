# Checklist

## 环境确认与基线
- [ ] WSL（Ubuntu-24.04）中 `docker` 可用（v29.6.1），Docker daemon 运行中
- [ ] `xmnn-dev:llvm22` 基础镜像存在
- [ ] `/mnt/d/spaces/SpecWeave` 源码可挂载，`xmtools`、`npu_tvm`、`npuusertools` 完整
- [ ] 记录既有基线镜像 `xmnn:1.2.1-new` 及其模型精度基线（若存在既有 result.csv/报告）

## Wheel 重打包
- [ ] `xmtools/dist/xmnn-*.whl` 生成
- [ ] wheel 8 项验证全部通过（import tvm/vta/xmnn、_libs、libtvm.so、tvm.build(llvm)、relay/std、.pth 引导）
- [ ] 构建过程无错误退出

## 运行时 Docker 镜像
- [ ] `xmnn:1.2.1-hub-sim` 镜像构建成功
- [ ] 镜像内 `verify_xmnn.py` 全部通过

## 模型枚举
- [ ] hub/caffe 与 hub/onnx 完整产物模型被枚举并生成模型名清单
- [ ] 不完整产物模型被列出

## 仿真 target 编译
- [ ] hub/caffe 与 hub/onnx 全部 config.toml 已备份
- [ ] compile.target 临时置为 sim_vta2.0、tune 置为 false
- [ ] 每个完整产物模型编译无错误（或已记录失败原因）
- [ ] 编译产物（network.xmnn / param.bin）生成
- [ ] 编译报告汇总完成

## 精度测试
- [ ] 每个编译成功模型执行精度测试
- [ ] 每个模型 `result.csv` 收集完成
- [ ] 精度对比表与 `build/xmnn-hub-sim-accuracy-report.md` 产出

## 恢复与清洁
- [ ] hub/caffe 与 hub/onnx config.toml 恢复为原始 target/tune
- [ ] `git status` 无明显无关改动（仅 build/ 产出物与 .trae/specs 新增）