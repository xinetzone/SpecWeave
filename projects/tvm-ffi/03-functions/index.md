# 函数与调用系统

> 分类编号：03-functions | 视角数量：15 篇

## 概述

本分类聚焦函数与调用系统，解析 Packed Function 调用约定、FunctionCell 结构、safe_call/cpp_call 双路径、全局函数注册表、Lambda 回调支持、参数传递与返回值约定、异常跨边界传播等。

## 概念文档

> 按视角编号排序，共 15 篇。

| 编号 | 标题 | 文件链接 |
|------|------|---------|
| 036 | Packed Function 约定 | [036-packed-function-convention.md](concepts/036-packed-function-convention.md) |
| 037 | FunctionCell 函数单元 | [037-function-cell.md](concepts/037-function-cell.md) |
| 038 | safe_call 与 cpp_call 双路径 | [038-safe-call-and-cpp-call.md](concepts/038-safe-call-and-cpp-call.md) |
| 039 | C 回调函数创建 | [039-c-callback-creation.md](concepts/039-c-callback-creation.md) |
| 040 | 全局函数注册表 | [040-global-function-registry.md](concepts/040-global-function-registry.md) |
| 041 | 函数一等公民 | [041-function-as-first-class-citizen.md](concepts/041-function-as-first-class-citizen.md) |
| 042 | Lambda 与回调 | [042-lambda-and-callbacks.md](concepts/042-lambda-and-callbacks.md) |
| 043 | 参数传递约定 | [043-argument-passing-convention.md](concepts/043-argument-passing-convention.md) |
| 044 | 返回值约定 | [044-return-value-convention.md](concepts/044-return-value-convention.md) |
| 045 | 异常跨越 FFI 边界 | [045-exception-crossing-ffi.md](concepts/045-exception-crossing-ffi.md) |
| 046 | TLS 错误传播 | [046-tls-error-propagation.md](concepts/046-tls-error-propagation.md) |
| 047 | cpp_call 快速路径 | [047-cpp-call-fast-path.md](concepts/047-cpp-call-fast-path.md) |
| 048 | 模块入口点约定 | [048-module-entry-point-convention.md](concepts/048-module-entry-point-convention.md) |
| 049 | __tvm_ffi_ 符号前缀 | [049-tvm-ffi-symbol-prefix.md](concepts/049-tvm-ffi-symbol-prefix.md) |
| 050 | 函数重载解析 | [050-function-overload-resolution.md](concepts/050-function-overload-resolution.md) |

## 参考资源

- [信源清单](references/sources.md) - 本分类相关源码路径与API清单
- [变更日志](log.md) - 文档变更历史记录
