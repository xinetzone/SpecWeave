# 函数与调用系统 - 信源清单

> 本文件从 facts.md 提取与本分类相关的事实，按模块组织，包含源码路径和关键API清单。
> 信源先行是 source-code-to-okf-wiki 方法论的核心纪律。

## 源码根路径

- **tvm-ffi 根目录**: `d:\AI\.chaos\libs\ffi`
- **TVM 根目录**: `d:\AI\.chaos\libs\ffi`（tvm-ffi + tvm 共存）

---

## 1. Function 核心

### 源码路径

- `include/tvm/ffi/function.h`
- `src/ffi/function.cc`

### 关键 API/类型清单

- `Function`
- `Function::operator()`
- `Function::CallAny`
- `Function::CallPacked`
- `Function::FromPacked`（function.h:341）
- `Function::GetGlobal`（function.h:409）
- `Function::SetGlobal`（function.h:499）
- `Function::ListGlobalNames`

### 相关事实编号

`F-135`, `F-136`, `F-137`, `F-138`, `F-139`, `F-140`, `F-141`, `F-142`, `F-143`, `F-280`, `F-281`, `F-282`

---

## 2. PackedArgs / ReturnValue

### 源码路径

- `include/tvm/ffi/function.h`

### 关键 API/类型清单

- `PackedArgs`
- `PackedArgs::operator[]`
- `PackedArgs::size()`
- `ReturnValue`

### 相关事实编号

`F-144`, `F-145`, `F-146`, `F-147`, `F-148`

---

## 3. TypedFunction / 全局注册

### 源码路径

- `include/tvm/ffi/function.h`
- `include/tvm/ffi/reflection/registry.h`

### 关键 API/类型清单

- `TypedFunction<R(Args...)>`
- `Function::SetGlobal`（function.h:499）
- `Function::FromPacked`（function.h:341）
- `refl::GlobalDef`（include/tvm/ffi/reflection/registry.h）

### 相关事实编号

`F-149`, `F-150`, `F-151`, `F-152`

---

## 4. C ABI 函数接口

### 源码路径

- `include/tvm/ffi/c_api.h`

### 关键 API/类型清单

- `TVMFFISafeCallType`
- `TVMFFIFunction`
- `TVMFFIFunctionCreate`（c_api.h:719）
- `TVMFFIFunctionCall`（c_api.h:746）
- `TVMFFIFunctionGetGlobal`（c_api.h:728）
- `TVMFFIFunctionSetGlobal`（c_api.h:1390）

### 相关事实编号

`F-016`, `F-017`, `F-020`, `F-021`, `F-022`, `F-059`

---

## 5. TVM 运行时打包参数

### 源码路径

- `src/runtime/pack_args.h`

### 关键 API/类型清单

- `PackFuncVoidAddr`
- `PackFuncNonBufferArg`
- `PackFuncPackedArgAligned`
- `ArgUnion32`
- `ArgUnion64`
- `ArgConvertCode`
- `GetArgConvertCode`

### 相关事实编号

`F-361`, `F-362`, `F-363`, `F-364`, `F-365`, `F-366`, `F-367`, `F-368`

---

## 事实来源说明

所有事实编号引用自：
`d:\AI\.trae\specs\tvm-ffi-200-perspectives\supporting-analysis\facts.md`

每条事实包含源码文件路径与行号引用，仅陈述代码中可见内容，不含推测。

## 使用规范

1. 撰写概念文档时，必须引用本清单中的源码路径和事实编号
2. 新增 API 引用前，先在本清单中登记
3. 发现事实遗漏时，先补充 facts.md 再更新本清单
