# Checklist

## 环境确认与基线
- [ ] WSL（Ubuntu-24.04）中 `docker` 可用（v29.6.1），Docker daemon 运行中
- [ ] `xmnn-dev:llvm22` 基础镜像存在
- [ ] `xmtools`、`npu_tvm`、`npuusertools` 三个源码目录完整
- [ ] `npuusertools/xmnn/caffe_pb2.py` 为最新更新版本
- [ ] 记录基线镜像 `xmnn:1.2.1-alpha` 及其模型精度基线（若存在既有 result.csv/报告）

## Wheel 重打包
- [ ] `xmtools/dist/xmnn-*.whl` 生成
- [ ] wheel 8 项验证全部通过（import tvm/vta/xmnn、_libs、libtvm.so、tvm.build(llvm)、relay/std、.pth 引导）
- [ ] wheel 内 `xmnn` Nuitka `.so` 包含更新后的 `caffe_pb2` 定义（Caffe 前端可解析）
- [ ] 构建过程无错误退出

## 运行时 Docker 镜像
- [ ] `xmnn:1.2.1-new` 镜像构建成功
- [ ] 镜像内 `verify_xmnn.py` 全部通过
- [ ] 镜像内 Caffe 前端 `caffe_pb2` 可正常解析

## 模型编译
- [ ] 三目录下所有完整产物模型被枚举
- [ ] 每个完整产物模型编译无错误
- [ ] 编译产物（network.xmnn / param.bin）生成
- [ ] Caffe 前端模型被重点覆盖

## 精度测试
- [ ] 每个编译成功模型执行精度测试
- [ ] 每个模型 `result.csv` 收集完成
- [ ] 指标汇总为结构化数据

## 对比报告
- [ ] 新镜像精度指标与基线对比完成
- [ ] 精度对比表生成
- [ ] 编译报告 + 精度对比报告产出
- [ ] 判断 `caffe_pb2.py` 更新是否引入精度回归