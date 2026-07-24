# Tasks

- [x] Task 1: 创建目录结构
  - [x] 创建 `docker/standalone/pycaffe/` 目录
  - [x] 创建 `docker/standalone/pycaffe/scripts/` 子目录
- [x] Task 2: 编写独立多阶段 Dockerfile
  - [x] 阶段 0 (base-system): ubuntu:26.04 基础环境，apt 换源为阿里云镜像，安装 ca-certificates/curl/wget
  - [x] 阶段 1 (base-builder): 安装 C++ 编译工具链 + Caffe 系统依赖 + Python 3 + 科学计算包（numpy/scipy/matplotlib/scikit-image/h5py/networkx/pandas/pyyaml/pillow/six/Cython/protobuf/python-dateutil/python-gflags），创建 builder 用户，设置环境变量
  - [x] 阶段 2 (caffe-builder): 复制 caffex/ 源码，内联生成 Makefile.config（CPU_ONLY/BLAS/Python路径/Boost.Python探测/HDF5/C++14），执行 `make all && make pycaffe && make tools && make distribute`
  - [x] 阶段 3 (pycaffe-builder): 从 caffe-builder 复制编译产物，创建 libcaffe.so 符号链接，复制 python/pycaffe 源码，安装 build 工具，使用 scikit-build-core 构建 pycaffe wheel（参考 `docker/modules/pycaffe/Dockerfile` 的 cmake.define 参数）
  - [x] 阶段 4 (runtime): 合并 Caffe 编译产物 + pycaffe wheel 安装，复制验证脚本，执行 `verify-pycaffe.sh`，设置 HEALTHCHECK，配置 ENTRYPOINT/CMD
- [x] Task 3: 复制验证脚本
  - [x] 从 `docker/modules/pycaffe/scripts/verify-pycaffe.sh` 复制到 `docker/standalone/pycaffe/scripts/`
  - [x] 从 `docker/modules/pycaffe/scripts/verify-parity.sh` 复制到 `docker/standalone/pycaffe/scripts/`
- [x] Task 4: 创建 Makefile 构建入口
  - [x] 创建 `docker/standalone/pycaffe/Makefile`，支持 all / caffe-builder / clean 目标
  - [x] all 目标构建 runtime 镜像并运行验证
  - [x] clean 目标清理 Docker 镜像

# Task Dependencies

- Task 2 依赖 Task 1（目录结构先就绪）
- Task 3 依赖 Task 1（目录结构先就绪）
- Task 4 依赖 Task 2（Dockerfile 就绪后编写 Makefile）
- Task 2 和 Task 3 可并行执行