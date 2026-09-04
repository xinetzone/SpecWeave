# PyCaffe pyproject.toml Python 3.14+ 兼容性更新 - Verification Checklist

## 配置文件格式验证
- [x] pyproject.toml 可被 Python tomllib 成功解析，无语法错误
- [x] [build-system] 节完整：requires 和 build-backend 字段存在且格式正确
- [x] [project] 节完整：name、version、requires-python、dependencies 字段存在
- [x] [tool.scikit-build] 节配置正确
- [x] 所有版本约束字符串可被 packaging.requirements.Requirement 成功解析

## Python 版本声明验证
- [x] requires-python 字段值为 ">=3.14"
- [x] Python 版本分类器（classifiers）包含 "Programming Language :: Python :: 3.14"

## 构建系统依赖验证
- [x] scikit-build-core 版本下限 >= 0.10
- [x] setuptools-scm 版本约束兼容 Python 3.14（>=8.0）
- [x] ninja 存在于构建依赖中（>=1.11）
- [x] cmake 存在于构建依赖中（>=3.26）
- [x] numpy 不在 build-system.requires 中（仅为运行时依赖）

## 运行时依赖版本验证
- [x] numpy 版本下限 >= 2.3
- [x] scipy 版本下限 >= 1.14
- [x] scikit-image 版本下限 >= 0.22
- [x] matplotlib 版本下限 >= 3.8
- [x] protobuf 版本下限 >= 4.25
- [x] h5py 版本下限 >= 3.10
- [x] networkx 版本下限 >= 3.2
- [x] pillow 版本下限 >= 10.0
- [x] pyyaml 版本下限 >= 6.0
- [x] six 版本下限 >= 1.16.0
- [x] python-dateutil 版本下限 >= 2.8
- [x] typing-extensions 已添加到 dependencies 且版本下限 >= 4.5
- [x] 不存在与 Python 3.14 不兼容的上限约束（如 `<3.14`、`<3.0`）

## 可选依赖验证
- [x] test 组包含 pytest>=8.0、jupyter>=1.0、ipython>=8.18、notebook>=7.0
- [x] full 组包含 pycaffe[test]、pandas>=2.1、black>=24.0、isort>=5.13、mypy>=1.8、graphviz>=0.20
- [x] full 组保留原有依赖 python-gflags>=3.1、leveldb>=0.20
- [x] 可选依赖版本下限与 Python 3.14 兼容

## scikit-build 配置验证
- [x] wheel.py-api 为 "py3"（不阻止 Python 3.14+）
- [x] cmake.build-type 为 "Release"
- [x] cmake.install-dir 指向正确的包目录
- [x] minimum-version = "0.10" 已设置

## build.sh 更新验证
- [x] build.sh 第6行注释已更新为 "Python 3.14+"
- [x] build.sh 脚本语法正确

## 变更范围验证
- [x] 仅修改了 pyproject.toml 和 build.sh 两个文件
- [x] CMakeLists.txt、Dockerfile、Python 源码、C++ 源码均未修改
- [x] caffex/ 目录下文件未被修改
