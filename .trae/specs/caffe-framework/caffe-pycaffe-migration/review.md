---
version: 1.3
---

# Caffe PyCaffe 迁移检查清单

## 构建系统检查
- [x] pyproject.toml 存在且配置 scikit-build-core 为构建后端
- [x] CMakeLists.txt 存在且正确配置 Python 扩展编译
- [x] `[tool.scikit-build]` 配置包含 wheel.packages 和 wheel.install-dir
- [x] 构建时依赖声明完整（scikit-build-core、cmake、ninja、numpy）
- [x] CMake 配置能找到 Python3、Boost.Python、NumPy、protobuf
- [x] CPU_ONLY 编译定义已添加，排除 CUDA 依赖
- [x] Protobuf 生成头文件路径已配置（`${CONDA_PREFIX}/src`）
- [x] wheel.install-dir 设为 "" 解决 _caffe.so 嵌套路径问题

## C++ 扩展检查
- [x] `_caffe.cpp` 已从 caffex 迁移至 pycaffe/python/pycaffe/
- [x] `_caffe.cpp` 中的 include 路径正确（caffe/caffe.hpp 等）
- [x] `_caffe.cpp` 编译无错误（C++17 标准，CPU_ONLY 模式）
- [x] 编译产物 `_caffe.so` 正确生成并链接到 libcaffe.so
- [x] Python 3.13 兼容性验证通过（conda-forge boost-python 支持 cp313，cp314 暂不可用）
- [x] CAFFE_VERSION 宏正确定义为 1.0.0，`__version__` 属性正常返回

## Python 模块检查
- [x] 所有 Python 模块从 caffex 迁移至 pycaffe/python/pycaffe/（9 个文件 + proto/）
- [x] `__init__.py` 导入路径正确（包名为 pycaffe，相对导入）
- [x] `pycaffe.py` 中无 `six` 库依赖，使用 `zip_longest` 替代 `izip_longest`
- [x] `pycaffe.py` 中无 `izip_longest` try/except 兼容代码
- [x] 所有文件中的导入已更新为相对导入（`.pycaffe`、`._caffe`、`.proto`、`.io` 等）
- [x] `proto/` 目录包含 `caffe_pb2.py` 和 `__init__.py`

## 运行时依赖检查
- [x] pyproject.toml 中 `[project].dependencies` 声明完整（11 个运行时依赖）
- [x] 无 Python 2 独有依赖
- [x] 依赖版本与目标环境兼容

## Docker 多阶段构建检查
- [x] Dockerfile 包含 6 个阶段：base-system → base-builder → builder-dev → builder → pycaffe-builder → runtime
- [x] pycaffe-builder 阶段从 builder 复制 Caffe 编译产物并构建 wheel
- [x] libcaffe.so 符号链接在 pycaffe-builder 和 runtime 阶段均创建
- [x] runtime 阶段从 pycaffe-builder 复制 wheel 并通过 pip 安装
- [x] 构建脚本 `build-multistage.sh` 支持 --verify 和 --export 选项
- [x] Docker 镜像构建成功（上次会话已验证）
- [x] pycaffe wheel 安装成功，`_caffe.so` 动态库依赖正确解析（上次会话已验证）
- [x] Dockerfile 已集成 test_inference.py 和 lenet_deploy.prototxt

## 验证检查
- [x] `build.sh` 脚本可执行，生成 wheel 文件
- [x] `verify.py` 验证脚本存在且覆盖 9 项核心功能检查
- [x] `test_inference.py` 推理测试脚本存在，覆盖 11 项测试（导入→前向→反向→属性→io→net_spec→proto）
- [x] `lenet_deploy.prototxt` LeNet 部署配置存在（Input 层，无 Data 依赖）
- [x] `import pycaffe` 在目标环境成功（conda Python 3.13 Docker 镜像）
- [x] `pycaffe.__version__` 返回 "1.0.0"（CAFFE_VERSION 宏正确展开）
- [x] `pycaffe.Net` 和 `pycaffe.SGDSolver` 可实例化（test_inference.py 验证通过）
- [x] `pycaffe.set_mode_cpu()` 可调用（test_inference.py 验证通过）
- [x] 简单推理流程（MNIST LeNet）执行正确（前向/反向传播均通过）
- [x] 推理结果与预期一致（11/11 测试全部通过：输出形状正确、Softmax归一化、梯度非零）
- [x] protobuf 兼容性：通过 `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python` 解决 C++/Python protobuf 冲突
- [x] Docker 多阶段构建成功：pycaffe-builder-conda（wheel构建）→ runtime-conda（运行时镜像）

## 代码质量检查
- [x] 无 Python 2 兼容代码残留
- [x] 无硬编码绝对路径
- [x] 变更文件原子化（每个文件变更单一职责）
- [x] 所有导入使用相对路径，符合 Python 包规范

<!-- changelog -->
- 2026-07-22 | update | v1.3：Docker conda Python 3.13 镜像构建成功，11/11 推理测试全部通过；C++标准升级至C++17；protobuf冲突通过纯Python实现解决；CAFFE_VERSION宏正确定义；RPATH配置正确
- 2026-07-22 | update | v1.2：新增 test_inference.py 和 lenet_deploy.prototxt 文件；Dockerfile 集成测试脚本；Python 3.14 兼容性审查结论；更新 spec.md 至 v1.1 新增 Docker 集成和推理测试两个 Requirement