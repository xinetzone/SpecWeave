# 错误处理系统 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. Error 对象

### 源码路径

- `include/tvm/ffi/error.h`
- `src/ffi/error.cc`

### 关键 API/类型清单

- `ErrorObj`
- `Error`
- `ErrorKind`
- `ErrorBuilder`
- `Error::what`
- `Error::kind`
- `Error::message`
- `Error::traceback`
- `Error::cause`
- `Error::WithContext`
- `Error::Raise`
- `TVM_FFI_TRY`
- `TVM_FFI_CATCH`

### 相关事实编号

`F-202`, `F-203`, `F-204`, `F-205`, `F-206`, `F-207`, `F-208`, `F-209`, `F-210`, `F-211`, `F-212`, `F-213`, `F-283`

---

## 2. C ABI 错误接口

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFIGetLastError`
- `TVMFFISetLastError`
- `TVMFFICStringFree`
- `TVMFFIThrowableGetMessage`
- `TVMFFIThrowableGetKind`
- `TVMFFIThrowableGetTraceback`
- `TVMFFIThrowableGetCause`
- `TVMFFIThrowableGetExtraContext`
- `TVMFFIThrowableAppendContext`
- `TVMFFIThrowableToAny`
- `TVMFFICtxSetLastError`
- `TVMFFICtxGetLastError`

### 相关事实编号

`F-026`, `F-027`, `F-028`, `F-029`, `F-030`, `F-031`, `F-032`, `F-061`

---

## 3. Backtrace 栈回溯

### 源码路径

- `src/ffi/backtrace.cc`
- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFIBacktrace`（c_api.h:1464）
- `TVMFFIBacktraceUpdateMode`（c_api.h:414）
- `kTVMFFIBacktraceUpdateModeReplace` / `kTVMFFIBacktraceUpdateModeAppend`（c_api.h:418-419）

### 相关事实编号

`F-063`, `F-295`, `F-296`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
