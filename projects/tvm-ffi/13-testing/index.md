# 测试策略

> 分类编号：13-testing | 视角数量：10 篇

## 概述

本分类介绍测试策略，包括 C++ GoogleTest 套件、Python pytest 套件、各核心模块测试覆盖分析、CI/CD 流水线、跨平台测试、代码检查与格式化等。

## 概念文档

> 按视角编号排序。

| 视角 | 文档 | 核心主题 |
|------|------|---------|
| 161 | [C++ GoogleTest 套件](concepts/161-cpp-googletest-suite.md) | GoogleTest 框架、CMake 构建、ctest 执行、测试文件组织 |
| 162 | [Python pytest 套件](concepts/162-python-pytest-suite.md) | pytest 框架、Python 绑定测试、跨语言异常传播 |
| 163 | [test_any 覆盖分析](concepts/163-test-any-coverage.md) | Any/AnyView 类型转换、引用计数、哈希相等、TypeTraits |
| 164 | [test_container 覆盖](concepts/164-test-container-coverage.md) | Array/List/Map/Dict C++ 与 Python 测试、COW 语义、共享变更 |
| 165 | [test_dtype 覆盖](concepts/165-test-dtype-coverage.md) | DataType/Device DLPack 类型转换、字符串别名、框架互操作 |
| 166 | [test_error 覆盖](concepts/166-test-error-coverage.md) | 回溯捕获、CHECK 宏、因果链、C++→Python 异常映射 |
| 167 | [test_shape/tuple 覆盖](concepts/167-test-shape-tuple-variant-coverage.md) | Shape 内联存储、Tuple 类型安全、Variant 类型选择 |
| 168 | [CI/CD 流水线](concepts/168-ci-cd-pipeline.md) | GitHub Actions 架构、任务依赖、跳过机制、多平台矩阵 |
| 169 | [跨平台测试](concepts/169-cross-platform-testing.md) | x86_64/aarch64/ARM64/Windows 差异、自由线程 Python、ABI 稳定性 |
| 170 | [代码检查与格式化](concepts/170-code-check-formatting.md) | pre-commit hooks、clang-tidy、文件类型检查、ASF 头验证 |

## 参考资源

- [信源清单](references/sources.md) - 本分类相关源码路径与API清单
- [变更日志](log.md) - 文档变更历史记录
