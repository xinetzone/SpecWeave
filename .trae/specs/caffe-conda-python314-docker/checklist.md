---
version: 1.0
---

# Caffe Conda Python 3.14 Docker 镜像 - Verification Checklist

## 目录与文件结构检查
- [x] Checkpoint 1: `d:\spaces\SpecWeave\external\chaos\caffe\docker\conda-cpu\` 目录已创建
- [x] Checkpoint 2: Dockerfile 文件存在于 conda-cpu/ 目录下
- [x] Checkpoint 3: 构建脚本 `build-docker.sh` 存在且有可执行权限
- [x] Checkpoint 4: 运行脚本 `run-docker.sh` 存在且有可执行权限
- [x] Checkpoint 5: 环境配置文件（environment.yml）存在

## Dockerfile 规范检查
- [ ] Checkpoint 6: Dockerfile 基于官方 conda 镜像（miniforge3 或 miniconda3）
- [ ] Checkpoint 7: Dockerfile 中创建名为 `caffe` 的 conda 环境
- [ ] Checkpoint 8: Dockerfile 中明确指定 Python 版本为 3.14
- [ ] Checkpoint 9: Dockerfile 安装了所有必要的系统依赖（BLAS, Boost, protobuf, glog, gflags, hdf5, leveldb, lmdb, OpenCV, snappy等）
- [ ] Checkpoint 10: Dockerfile 配置了正确的 Makefile.config（CPU_ONLY, Python路径）
- [ ] Checkpoint 11: Dockerfile 中设置了 CAFFE_ROOT, PYTHONPATH, PATH, LD_LIBRARY_PATH 环境变量
- [ ] Checkpoint 12: Dockerfile 中 WORKDIR 设置为 /workspace
- [ ] Checkpoint 13: 进行了镜像大小优化（清理apt缓存、conda/pip缓存）
- [ ] Checkpoint 14: 多阶段构建（如采用）正确复制了所有必要的运行时文件

## WSL2 构建验证
- [ ] Checkpoint 15: 在 WSL2 环境中 `docker build` 命令成功执行
- [ ] Checkpoint 16: 构建过程中无致命编译错误
- [ ] Checkpoint 17: 镜像构建完成，标签为 `caffe:conda-py314-cpu`

## 容器内功能验证
- [ ] Checkpoint 18: 容器内 `conda run -n caffe python --version` 输出 Python 3.14.x
- [ ] Checkpoint 19: 容器内 `conda run -n caffe python -c "import caffe; print('OK')"` 成功输出 OK
- [ ] Checkpoint 20: 容器内 `caffe --version` 命令正常执行并输出版本信息
- [ ] Checkpoint 21: 容器内 `pwd` 显示 /workspace
- [ ] Checkpoint 22: 容器内 `echo $CAFFE_ROOT` 指向正确的 Caffe 安装目录
- [ ] Checkpoint 23: 容器内 `echo $PYTHONPATH` 包含 PyCaffe 路径
- [ ] Checkpoint 24: 容器内 numpy 可正常导入（`import numpy as np; print(np.__version__)`）
- [ ] Checkpoint 25: 容器内 scipy 可正常导入（`import scipy; print(scipy.__version__)`）
- [ ] Checkpoint 26: 容器内 protobuf 可正常导入（`import google.protobuf`）

## 镜像特性验证
- [ ] Checkpoint 27: `docker images caffe:conda-py314-cpu` 显示镜像大小 ≤ 3GB
- [ ] Checkpoint 28: `docker run --rm -v $(pwd):/workspace caffe:conda-py314-cpu ls /workspace` 能正确列出挂载目录内容
- [ ] Checkpoint 29: `docker save -o caffe-conda-py314-cpu.tar caffe:conda-py314-cpu` 成功导出tar文件
- [ ] Checkpoint 30: 导出的tar文件可通过 `docker load -i` 重新导入（可选验证）

## 文档检查
- [ ] Checkpoint 31: README.md 使用说明文档存在
- [ ] Checkpoint 32: 文档包含构建命令说明
- [ ] Checkpoint 33: 文档包含运行命令说明
- [ ] Checkpoint 34: 文档记录了 Python 3.14 兼容性相关问题（如有）

## 对抗审查视角验证（V阶段 - 假设攻击）
- [ ] Checkpoint 35: 镜像在全新环境中拉取后能否直接运行（无缺失依赖）？
- [ ] Checkpoint 36: 挂载主机目录时文件权限是否正常（非root用户场景）？
- [ ] Checkpoint 37: conda环境是否正确激活（不需要手动conda activate）？
- [ ] Checkpoint 38: 是否有caffe命令找不到或库加载错误的情况？
- [ ] Checkpoint 39: 镜像中是否包含不必要的敏感信息或凭据？
- [ ] Checkpoint 40: 构建脚本是否能在干净的WSL2环境中重复执行（幂等性）？
