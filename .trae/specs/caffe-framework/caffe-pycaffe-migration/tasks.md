---
version: 1.0
---

# Caffe PyCaffe 迁移任务列表

## [x] Task 1: 创建 pycaffe 目录结构和 pyproject.toml
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `pycaffe/` 下创建 `python/pycaffe/` 子目录
  - 创建 `pyproject.toml`，配置 scikit-build-core 构建后端
  - 参考 TVM-FFI 的 `examples/python_packaging/pyproject.toml` 模式
  - 声明构建时依赖（scikit-build-core>=0.10、cmake、ninja）
  - 声明运行时依赖（numpy、protobuf、pyyaml、Pillow、scipy、scikit-image、matplotlib、h5py、leveldb、networkx、pandas 等）
  - 配置 `[tool.scikit-build]`：wheel.packages、wheel.install-dir、cmake.build-type
  - 配置 `[tool.scikit-build.cmake.define]`：CMAKE_EXPORT_COMPILE_COMMANDS
- **Acceptance Criteria Addressed**: [AC-1]
- **Test Requirements**:
  - `programmatic` TR-1.1: `pyproject.toml` 语法正确，可被 pip 解析
  - `human-judgement` TR-1.2: 配置项与 TVM-FFI 参考模式一致

## [x] Task 2: 创建 CMakeLists.txt 构建文件
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 `pycaffe/CMakeLists.txt`
  - 使用 `find_package(Python REQUIRED COMPONENTS Interpreter Development NumPy)` 查找 Python
  - 使用 `find_package(Boost REQUIRED COMPONENTS python3)` 查找 Boost.Python
  - 使用 `find_package(Protobuf REQUIRED)` 查找 protobuf
  - 使用 `find_package(Caffe REQUIRED)` 或通过 `find_library` 查找 Caffe C++ 库
  - 使用 `Python_add_library(_caffe MODULE _caffe.cpp)` 编译扩展
  - 链接 Caffe 库和所有依赖
  - 设置 `CXX_STANDARD 14` 和 `PREFIX ""`、`OUTPUT_NAME "_caffe"`
  - 配置安装目标
- **Acceptance Criteria Addressed**: [AC-2]
- **Test Requirements**:
  - `programmatic` TR-2.1: CMake 配置阶段无错误
  - `human-judgement` TR-2.2: CMakeLists.txt 能找到所有必需依赖

## [x] Task 3: 迁移 _caffe.cpp C++ 绑定文件
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 从 `caffex/python/caffe/_caffe.cpp` 复制到 `pycaffe/python/pycaffe/_caffe.cpp`
  - 检查并修复 include 路径（确保能找到 caffe/caffe.hpp 等头文件）
  - 修复 `NPY_NO_DEPRECATED_API` 版本号（如需适配新版 NumPy）
  - 确保 `Dtype` 定义为 `float`（CPU-only）
  - 保留 Boost.Python 绑定代码不变
- **Acceptance Criteria Addressed**: [AC-2, AC-3]
- **Test Requirements**:
  - `programmatic` TR-3.1: `_caffe.cpp` 编译无错误
  - `human-judgement` TR-3.2: include 路径与 conda 环境兼容

## [x] Task 4: 迁移 Python 模块并清理 Python 2 代码
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 从 `caffex/python/caffe/` 复制以下文件到 `pycaffe/python/pycaffe/`：
    - `__init__.py`（修改包名为 pycaffe）
    - `pycaffe.py`（清理 Python 2 代码）
    - `classifier.py`
    - `detector.py`
    - `draw.py`
    - `io.py`
    - `net_spec.py`
    - `coord_map.py`
  - 清理 `pycaffe.py` 中的 Python 2 兼容代码：
    - 移除 `import six`，替换 `six.iteritems()` 为 `.items()`，`six.next()` 为 `next()`
    - 移除 `izip_longest`，使用 `itertools.zip_longest`
    - 移除 `from itertools import izip_longest` 的 try/except
  - 更新 `__init__.py` 的导入路径（从 `.pycaffe` 改为 `.pycaffe` 或调整相对导入）
  - 更新 `classifier.py`、`detector.py` 等文件中的 `import caffe` 为 `import pycaffe`
- **Acceptance Criteria Addressed**: [AC-3, AC-4]
- **Test Requirements**:
  - `programmatic` TR-4.1: `python -c "import pycaffe"` 语法检查通过（无 import 错误）
  - `programmatic` TR-4.2: 代码中无 `six` 导入
  - `human-judgement` TR-4.3: 所有文件中的 Python 2 兼容代码已清理

## [x] Task 5: 处理 protobuf 生成代码
- **Priority**: medium
- **Depends On**: Task 4
- **Description**:
  - 创建 `pycaffe/python/pycaffe/proto/__init__.py`
  - 从 caffex 编译产物中复制 `caffe_pb2.py` 到 `pycaffe/python/pycaffe/proto/`
  - 或在 CMakeLists.txt 中添加 protobuf 代码生成步骤
  - 确保 `from .proto.caffe_pb2 import TRAIN, TEST` 可用
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `programmatic` TR-5.1: `from pycaffe.proto.caffe_pb2 import TRAIN, TEST` 成功

## [x] Task 6: 编写构建和验证脚本
- **Priority**: medium
- **Depends On**: Task 3, Task 4, Task 5
- **Description**:
  - 创建 `pycaffe/build.sh`：一键构建 wheel 的脚本
  - 创建 `pycaffe/verify.py`：验证脚本，测试以下功能：
    - `import pycaffe` 成功
    - `pycaffe.Net`、`pycaffe.SGDSolver` 等类可用
    - `pycaffe.set_mode_cpu()` 可调用
    - `pycaffe.__version__` 可访问
    - 如有测试模型，运行一次简单推理
  - 脚本在 conda 环境中可执行
- **Acceptance Criteria Addressed**: [AC-5, AC-6]
- **Test Requirements**:
  - `programmatic` TR-6.1: `build.sh` 执行成功，生成 wheel 文件
  - `programmatic` TR-6.2: `verify.py` 所有检查项通过

## [x] Task 7: Docker 环境端到端验证
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 更新 Dockerfile（参考 `caffe-conda-python314-docker` spec），添加 pycaffe wheel 安装步骤
  - 在 Docker 容器内（conda 环境 + Python 3.14）执行：
    - `pip install pycaffe/dist/*.whl`
    - `python verify.py` 全量验证
    - 运行一个简单 Caffe 推理流程（如 MNIST LeNet）
  - 验证推理结果正确性
- **Acceptance Criteria Addressed**: [AC-5, AC-6, AC-7]
- **Test Requirements**:
  - `programmatic` TR-7.1: Docker 容器内 `import pycaffe` 成功
  - `programmatic` TR-7.2: 推理流程无错误
  - `programmatic` TR-7.3: 推理结果与预期一致

# Task Dependencies
- Task 2 depends on Task 1
- Task 3 depends on Task 2
- Task 4 can run in parallel with Task 2, 3
- Task 5 depends on Task 4
- Task 6 depends on Task 3, 4, 5
- Task 7 depends on Task 6