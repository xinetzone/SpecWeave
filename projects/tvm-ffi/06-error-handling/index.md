# 错误处理系统

> 分类编号：06-error-handling | 视角数量：10 篇

## 概述

本分类解析错误处理系统，包括 Error 对象设计、错误类型分类、栈回溯捕获、跨 FFI 边界回溯传播、错误因果链、额外错误上下文、TLS 错误状态管理等。

## 概念文档

> 按视角编号排序，共 10 篇。

| 编号 | 标题 | 文件链接 |
|------|------|---------|
| 076 | ErrorObj 对象设计 | [076-error-obj-design.md](concepts/076-error-obj-design.md) |
| 077 | Error 类与 std::exception 集成 | [077-error-class-exception-integration.md](concepts/077-error-class-exception-integration.md) |
| 078 | ErrorKind 错误类型分类 | [078-error-kind-classification.md](concepts/078-error-kind-classification.md) |
| 079 | TVMFFIBacktrace 栈回溯捕获 | [079-backtrace-capture.md](concepts/079-backtrace-capture.md) |
| 080 | 跨 FFI 边界回溯传播 | [080-cross-ffi-boundary-backtrace.md](concepts/080-cross-ffi-boundary-backtrace.md) |
| 081 | 错误因果链 cause_chain | [081-error-cause-chain.md](concepts/081-error-cause-chain.md) |
| 082 | 额外错误上下文 extra_context | [082-error-extra-context.md](concepts/082-error-extra-context.md) |
| 083 | TLS 错误状态 SafeCallContext | [083-tls-error-state.md](concepts/083-tls-error-state.md) |
| 084 | ErrorBuilder 与抛出宏 | [084-error-builder-throw-macros.md](concepts/084-error-builder-throw-macros.md) |
| 085 | Expected 无异常错误处理 | [085-expected-exception-free.md](concepts/085-expected-exception-free.md) |

## 参考资源

- [信源清单](references/sources.md) - 本分类相关源码路径与API清单
- [变更日志](log.md) - 文档变更历史记录
